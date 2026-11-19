"""
CivicMind AI — Evidence Upload & Download API Endpoints
"""

import uuid
from fastapi import APIRouter, Depends, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.grievance import EvidenceResponse
from app.services.storage_service import StorageService, _format_size


router = APIRouter(prefix="/uploads", tags=["Multimedia Evidence Storage"])


@router.post(
    "/evidence",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Grievance Evidence File",
    description="Validates MIME types (JPEG, PNG, WebP, PDF, MP3, WAV, OGG), inspects magic-byte signatures, enforces a 25MB ceiling, and sanitizes filenames before storing locally.",
)
async def upload_evidence(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EvidenceResponse:
    evidence = await StorageService.save_evidence_file(
        session=db,
        file=file,
        uploaded_by_user=current_user,
    )
    return EvidenceResponse(
        id=str(evidence.id),
        type=evidence.file_type,
        url=evidence.storage_url,
        name=evidence.file_name,
        size=_format_size(evidence.file_size_bytes),
        file_name=evidence.file_name,
        fileName=evidence.file_name,
        file_type=evidence.file_type,
        fileType=evidence.file_type,
        file_size_bytes=evidence.file_size_bytes,
        fileSizeBytes=evidence.file_size_bytes,
        storage_url=evidence.storage_url,
        storageUrl=evidence.storage_url,
        created_at=evidence.created_at,
        createdAt=evidence.created_at,
    )


@router.get(
    "/evidence/{id}/download",
    summary="Download Evidence File",
    description="Streams stored evidence file with role-based access verification and IDOR prevention.",
)
async def download_evidence(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    file_path, original_filename, media_type = await StorageService.get_evidence_file_path(
        session=db,
        evidence_id=id,
        user=current_user,
    )
    return FileResponse(
        path=str(file_path),
        filename=original_filename,
        media_type=media_type,
    )
