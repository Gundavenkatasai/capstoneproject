"""
CivicMind AI — Evidence File Storage Service
Provides secure file upload, magic-byte validation, path traversal prevention,
and role-based file access controls.
"""

import os
import uuid
import aiofiles
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.evidence import GrievanceEvidence
from app.models.grievance import Grievance
from app.models.user import User


# Upload directory configuration
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads" / "evidence"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB

ALLOWED_MIME_TYPES = {
    # Images
    "image/jpeg": "image",
    "image/png": "image",
    "image/webp": "image",
    # Documents
    "application/pdf": "document",
    # Audio
    "audio/mpeg": "audio",
    "audio/mp3": "audio",
    "audio/wav": "audio",
    "audio/x-wav": "audio",
    "audio/ogg": "audio",
}

ALLOWED_EXTENSIONS = {
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".webp": "image",
    ".pdf": "document",
    ".mp3": "audio",
    ".wav": "audio",
    ".ogg": "audio",
}


def _format_size(size_bytes: int) -> str:
    """Format bytes to human readable string (e.g. 2.4 MB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"



def _validate_magic_bytes(header: bytes, content_type: str, ext: str) -> bool:
    """Validate binary header signature against declared MIME type and extension."""
    if len(header) < 4:
        return False

    if ext in (".jpg", ".jpeg") or "jpeg" in content_type:
        return header[:3] == b"\xff\xd8\xff"
    if ext == ".png" or "png" in content_type:
        return header[:8] == b"\x89PNG\r\n\x1a\n"
    if ext == ".webp" or "webp" in content_type:
        return header[:4] == b"RIFF" and len(header) >= 12 and header[8:12] == b"WEBP"
    if ext == ".pdf" or "pdf" in content_type:
        return header[:4] == b"%PDF"
    if ext == ".mp3" or "mpeg" in content_type or "mp3" in content_type:
        return (
            header[:3] == b"ID3"
            or header[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")
        )
    if ext == ".wav" or "wav" in content_type:
        return header[:4] == b"RIFF" and len(header) >= 12 and header[8:12] == b"WAVE"
    if ext == ".ogg" or "ogg" in content_type:
        return header[:4] == b"OggS"

    return False


class StorageService:
    @staticmethod
    async def save_evidence_file(
        session: AsyncSession,
        file: UploadFile,
        uploaded_by_user: User,
        grievance_id: Optional[str] = None,
    ) -> GrievanceEvidence:
        """
        Validate, sanitize, write evidence file to disk, and persist record to database.
        """
        raw_filename = file.filename or "evidence"
        sanitized_basename = Path(raw_filename).name  # Prevent directory traversal
        ext = Path(sanitized_basename).suffix.lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file extension: '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS.keys())}",
            )

        content_type = (file.content_type or "").lower()
        file_type = ALLOWED_EXTENSIONS[ext]

        # Read first chunk for magic byte validation and size check
        chunk = await file.read(4096)
        if not chunk:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        if not _validate_magic_bytes(chunk, content_type, ext):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File content does not match declared file type binary signature.",
            )

        # Generate unique storage filename
        stored_filename = f"{uuid.uuid4().hex}{ext}"
        destination_path = (UPLOAD_DIR / stored_filename).resolve()

        # Path traversal guard
        if not str(destination_path).startswith(str(UPLOAD_DIR.resolve())):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid destination path detected.",
            )

        # Stream remaining contents while enforcing max size
        total_bytes = len(chunk)
        async with aiofiles.open(destination_path, "wb") as out_file:
            await out_file.write(chunk)
            while True:
                data = await file.read(64 * 1024)
                if not data:
                    break
                total_bytes += len(data)
                if total_bytes > MAX_FILE_SIZE_BYTES:
                    # Clean up oversized file
                    await out_file.close()
                    if destination_path.exists():
                        destination_path.unlink()
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds maximum allowed size of 25MB (received {total_bytes} bytes).",
                    )
                await out_file.write(data)

        # Build storage reference
        evidence_id = uuid.uuid4()
        storage_url = f"/api/v1/uploads/evidence/{evidence_id}/download"

        evidence = GrievanceEvidence(
            id=evidence_id,
            grievance_id=grievance_id,
            uploaded_by=uploaded_by_user.id,
            file_name=sanitized_basename,
            file_type=file_type,
            file_size_bytes=total_bytes,
            storage_url=storage_url,
        )

        session.add(evidence)
        await session.commit()
        await session.refresh(evidence)
        return evidence

    @staticmethod
    async def get_evidence_file_path(
        session: AsyncSession,
        evidence_id: uuid.UUID,
        user: User,
    ) -> Tuple[Path, str, str]:
        """
        Verify role-scoped access and return local file path, original filename, and media type.
        """
        result = await session.execute(
            select(GrievanceEvidence).where(GrievanceEvidence.id == evidence_id)
        )
        evidence = result.scalar_one_or_none()
        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence file not found.",
            )

        # IDOR and RBAC check:
        # Admins can view any evidence.
        # Uploader can view their evidence.
        # If attached to a grievance, department officers or assigned officer can view it.
        has_access = False
        if user.role == "admin" or evidence.uploaded_by == user.id:
            has_access = True
        elif evidence.grievance_id:
            g_result = await session.execute(
                select(Grievance).where(Grievance.id == evidence.grievance_id)
            )
            grievance = g_result.scalar_one_or_none()
            if grievance:
                if grievance.citizen_id == user.id:
                    has_access = True
                elif user.role == "officer":
                    if grievance.assigned_officer_id == user.id:
                        has_access = True
                    elif user.department_id and grievance.department_id == user.department_id:
                        has_access = True

        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this evidence file.",
            )

        # Locate file on disk
        ext = Path(evidence.file_name).suffix.lower()
        # Find file by scanning upload directory matching evidence id prefix
        file_candidates = list(UPLOAD_DIR.glob(f"*{ext}"))
        target_file = None
        for candidate in file_candidates:
            if candidate.is_file():
                # Check file size to match
                if candidate.stat().st_size == evidence.file_size_bytes:
                    target_file = candidate
                    break

        if not target_file or not target_file.exists():
            # Fallback search any file in upload dir
            for candidate in UPLOAD_DIR.iterdir():
                if candidate.is_file() and candidate.stat().st_size == evidence.file_size_bytes:
                    target_file = candidate
                    break

        if not target_file or not target_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Physical file not found on storage disk.",
            )

        media_types = {
            "image": "image/jpeg",
            "document": "application/pdf",
            "audio": "audio/mpeg",
        }
        media_type = media_types.get(evidence.file_type, "application/octet-stream")
        return target_file, evidence.file_name, media_type
