"""
CivicMind AI — Core Grievance Service & Lifecycle Implementation
Handles sequence-based tracking IDs, complete grievance CRUD, role-scoped filtering,
IDOR protection, officer assignments, resolution verification, appeals, and deterministic triage fallback.
"""

import uuid
from typing import Optional, List, Tuple
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, text
from sqlalchemy.orm import selectinload

from app.models.grievance import Grievance
from app.models.department import Department
from app.models.user import User
from app.models.evidence import GrievanceEvidence
from app.models.timeline import GrievanceTimeline
from app.models.resolution import ResolutionReport
from app.models.audit import AuditLog
from app.models.outbox import OutboxEvent
from app.schemas.grievance import (
    GrievanceCreateRequest,
    GrievanceResponse,
    GrievanceListResponse,
    EvidenceResponse,
    TimelineEventResponse,
    ResolutionReportResponse,
    GrievanceLocationSchema,
    TriagePreviewRequest,
    TriagePreviewResponse,
)
from app.services.lifecycle import LifecycleService


SLA_HOURS_BY_PRIORITY = {
    "critical": 48,
    "high": 72,
    "medium": 96,
    "low": 120,
}

DURATION_DAYS_BY_PRIORITY = {
    "critical": 1.5,
    "high": 2.5,
    "medium": 3.5,
    "low": 5.0,
}

DEPARTMENT_KEYWORD_RULES = [
    {
        "dept_id": "PWD-RDS",
        "dept_name": "Public Works Department (Roads)",
        "category": "Road Infrastructure",
        "subcategory": "Potholes & Road Damage",
        "keywords": ["pothole", "road", "tar", "asphalt", "crater", "footpath", "divider", "flyover", "bridge", "pavement"],
    },
    {
        "dept_id": "MC-SWM",
        "dept_name": "Municipal Solid Waste Management",
        "category": "Sanitation & Waste Management",
        "subcategory": "Garbage Dump Overflow",
        "keywords": ["garbage", "waste", "trash", "dump", "bin", "litter", "rubbish", "sweeping", "debris", "cleanliness"],
    },
    {
        "dept_id": "WSSB-OPS",
        "dept_name": "Water Supply & Sewerage Board",
        "category": "Water Supply & Drainage",
        "subcategory": "Pipeline Leakage & Contamination",
        "keywords": ["water", "sewage", "drain", "drainage", "pipe", "pipeline", "leak", "overflow", "drinking water", "tap", "gutter", "contamination"],
    },
]


def _format_size(size_bytes: int) -> str:
    """Format bytes to human readable string (e.g. 2.4 MB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def _map_to_response(g: Grievance) -> GrievanceResponse:
    """Maps a SQLAlchemy Grievance entity to the unified GrievanceResponse schema."""
    evidence_items = [
        EvidenceResponse(
            id=str(e.id),
            type=e.file_type,
            url=e.storage_url,
            name=e.file_name,
            size=_format_size(e.file_size_bytes),
            file_name=e.file_name,
            fileName=e.file_name,
            file_type=e.file_type,
            fileType=e.file_type,
            file_size_bytes=e.file_size_bytes,
            fileSizeBytes=e.file_size_bytes,
            storage_url=e.storage_url,
            storageUrl=e.storage_url,
            created_at=e.created_at,
            createdAt=e.created_at,
        )
        for e in (g.evidence or [])
    ]

    timeline_items = [
        TimelineEventResponse(
            id=str(t.id),
            status=t.status,
            title=t.title,
            description=t.description,
            timestamp=t.created_at,
            actor=t.actor_name,
            actorRole=t.actor_role,
            actor_name=t.actor_name,
            actor_role=t.actor_role,
            notes=t.notes,
            created_at=t.created_at,
            createdAt=t.created_at,
        )
        for t in (g.timeline or [])
    ]

    resolution_rep = None
    if g.resolution_report:
        r = g.resolution_report
        resolution_rep = ResolutionReportResponse(
            report_text=r.report_text,
            reportText=r.report_text,
            text=r.report_text,
            resolved_at=r.resolved_at,
            resolvedAt=r.resolved_at,
            officer_evidence_urls=r.officer_evidence_urls or [],
            officerEvidence=r.officer_evidence_urls or [],
            citizen_rating=r.citizen_rating,
            citizenFeedbackRating=r.citizen_rating,
            citizen_comment=r.citizen_comment,
            citizenFeedbackComment=r.citizen_comment,
            ai_verification_confidence=float(r.ai_verification_confidence or 0.95),
            aiVerificationConfidence=float(r.ai_verification_confidence or 0.95),
            verified_by_admin=r.verified_by_admin,
            verifiedByAdmin=r.verified_by_admin,
        )

    citizen_name = g.citizen.full_name if g.citizen else "Citizen"
    citizen_phone = g.citizen.phone_number if g.citizen else None
    dept_name = g.department.name if g.department else g.department_id
    officer_name = g.assigned_officer.full_name if g.assigned_officer else None

    return GrievanceResponse(
        id=g.id,
        title=g.title,
        description=g.description,
        citizen_id=str(g.citizen_id),
        citizenId=str(g.citizen_id),
        citizen_name=citizen_name,
        citizenName=citizen_name,
        citizen_phone=citizen_phone,
        citizenPhone=citizen_phone,
        category=g.category,
        subcategory=g.subcategory,
        department_id=g.department_id,
        departmentId=g.department_id,
        department_name=dept_name,
        departmentName=dept_name,
        assigned_officer_id=str(g.assigned_officer_id) if g.assigned_officer_id else None,
        assignedOfficerId=str(g.assigned_officer_id) if g.assigned_officer_id else None,
        assigned_officer_name=officer_name,
        assignedOfficerName=officer_name,
        location=GrievanceLocationSchema(
            address=g.address,
            ward=g.ward,
            zone=g.zone,
            lat=g.latitude,
            lng=g.longitude,
        ),
        priority=g.priority,  # type: ignore[arg-type]
        status=g.status,  # type: ignore[arg-type]
        ai_confidence=float(g.ai_confidence or 0.90),
        aiConfidence=float(g.ai_confidence or 0.90),
        submitted_at=g.submitted_at,
        submittedAt=g.submitted_at,
        updated_at=g.updated_at,
        updatedAt=g.updated_at,
        expected_resolution_date=g.expected_resolution_date,
        expectedResolutionDate=g.expected_resolution_date,
        actual_resolution_date=g.actual_resolution_date,
        actualResolutionDate=g.actual_resolution_date,
        sla_deadline=g.sla_deadline,
        slaDeadline=g.sla_deadline,
        sla_breached=g.sla_breached,
        slaBreached=g.sla_breached,
        sla_breach_risk=g.sla_breach_risk,  # type: ignore[arg-type]
        slaBreachRisk=g.sla_breach_risk,  # type: ignore[arg-type]
        duplicate_probability=float(g.duplicate_probability or 0.0),
        duplicateProbability=float(g.duplicate_probability or 0.0),
        duplicate_cluster_id=str(g.duplicate_cluster_id) if g.duplicate_cluster_id else None,
        duplicateClusterId=str(g.duplicate_cluster_id) if g.duplicate_cluster_id else None,
        is_anonymous=g.is_anonymous,
        isAnonymous=g.is_anonymous,
        language=g.language,
        predicted_duration_days=float(g.predicted_duration_days or 3.0),
        predictedDurationDays=float(g.predicted_duration_days or 3.0),
        evidence=evidence_items,
        timeline=timeline_items,
        resolution_report=resolution_rep,
        resolutionReport=resolution_rep,
    )


class GrievanceService:
    @staticmethod
    async def generate_tracking_id(session: AsyncSession) -> str:
        """Atomically generate collision-safe GRV-YYYY-XXXXX sequence ID."""
        now_year = datetime.now(timezone.utc).year
        result = await session.execute(text("SELECT nextval('grievance_tracking_seq');"))
        seq_num = result.scalar()
        return f"GRV-{now_year}-{seq_num}"

    @staticmethod
    async def create_grievance(
        session: AsyncSession,
        payload: GrievanceCreateRequest,
        current_user: User,
        ip_address: str = "127.0.0.1",
    ) -> GrievanceResponse:
        """
        Create a new grievance, assign sequence tracking ID, calculate SLA, attach uploaded evidence,
        and generate initial timeline and audit log entries.
        """
        tracking_id = await GrievanceService.generate_tracking_id(session)
        now = datetime.now(timezone.utc)

        # Priority & SLA calculation
        priority = payload.priority or "medium"
        sla_hours = SLA_HOURS_BY_PRIORITY.get(priority, 96)
        sla_deadline = now + timedelta(hours=sla_hours)
        predicted_days = DURATION_DAYS_BY_PRIORITY.get(priority, 3.5)
        expected_resolution_date = now + timedelta(days=predicted_days)

        # Department resolution: fallback to municipal rule-based classification if not specified
        dept_id = payload.department_id
        if not dept_id:
            # Check default from keyword rules
            matched_rule = None
            text_corpus = f"{payload.title} {payload.description}".lower()
            for rule in DEPARTMENT_KEYWORD_RULES:
                if any(kw in text_corpus for kw in rule["keywords"]):
                    matched_rule = rule
                    break
            dept_id = matched_rule["dept_id"] if matched_rule else "PWD-RDS"

        # Validate department exists
        dept_check = await session.execute(
            select(Department).where(Department.id == dept_id)
        )
        dept = dept_check.scalar_one_or_none()
        if not dept:
            # Fallback to first available department
            first_dept = await session.execute(select(Department).limit(1))
            dept = first_dept.scalar_one_or_none()
            if not dept:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No municipal departments configured in the database.",
                )
            dept_id = dept.id

        grievance = Grievance(
            id=tracking_id,
            title=payload.title,
            description=payload.description,
            citizen_id=current_user.id,
            department_id=dept_id,
            category=payload.category,
            subcategory=payload.subcategory or "General Civic Issue",
            priority=priority,
            status="submitted",
            address=payload.address,
            ward=payload.ward,
            zone=payload.zone,
            latitude=payload.latitude,
            longitude=payload.longitude,
            ai_confidence=0.920,
            is_anonymous=payload.is_anonymous,
            language=payload.language or "en",
            predicted_duration_days=predicted_days,
            expected_resolution_date=expected_resolution_date,
            sla_deadline=sla_deadline,
            sla_breached=False,
            sla_breach_risk="low",
            duplicate_probability=0.000,
        )
        session.add(grievance)
        await session.flush()

        # Associate pre-uploaded evidence files
        if payload.evidence_file_ids:
            for ev_id in payload.evidence_file_ids:
                ev_res = await session.execute(
                    select(GrievanceEvidence).where(
                        GrievanceEvidence.id == ev_id,
                        GrievanceEvidence.uploaded_by == current_user.id,
                    )
                )
                ev = ev_res.scalar_one_or_none()
                if ev:
                    ev.grievance_id = tracking_id

        # Insert initial timeline record
        timeline_event = GrievanceTimeline(
            grievance_id=tracking_id,
            status="submitted",
            title="Grievance Registered",
            description=f"Complaint registered by citizen with tracking ID {tracking_id}.",
            actor_name=current_user.full_name,
            actor_role="Citizen",
            notes=f"Reported issue in ward {payload.ward}, zone {payload.zone}.",
        )
        session.add(timeline_event)

        # Insert audit log
        audit = AuditLog(
            action="GRIEVANCE_REGISTERED",
            entity_type="grievance",
            entity_id=tracking_id,
            performed_by=f"{current_user.full_name} ({current_user.email})",
            user_role=current_user.role,
            details=f"Grievance created with priority {priority} for department {dept_id}.",
            ip_address=ip_address,
        )
        session.add(audit)

        # Enqueue transactional outbox event
        outbox = OutboxEvent(
            event_type="grievance.created",
            aggregate_type="grievance",
            aggregate_id=tracking_id,
            payload={
                "grievance_id": tracking_id,
                "tracking_id": tracking_id,
                "title": grievance.title,
                "department_id": dept_id,
                "priority": priority,
                "citizen_id": str(current_user.id),
                "citizen_email": current_user.email,
                "citizen_phone": current_user.phone_number,
                "notes": f"New grievance registered in ward {payload.ward}, zone {payload.zone}.",
            },
            correlation_id=f"grv-create-{tracking_id}",
        )
        session.add(outbox)

        await session.commit()
        return await GrievanceService.get_grievance_by_id(session, tracking_id, current_user)

    @staticmethod
    async def get_grievance_by_id(
        session: AsyncSession,
        grievance_id: str,
        current_user: User,
    ) -> GrievanceResponse:
        """
        Fetch grievance details with strict IDOR access control:
        - Citizens can only view their own grievances.
        - Officers can view grievances in their department or assigned to them.
        - Admins can view any grievance.
        """
        stmt = (
            select(Grievance)
            .where(Grievance.id == grievance_id)
            .options(
                selectinload(Grievance.citizen),
                selectinload(Grievance.department),
                selectinload(Grievance.assigned_officer),
                selectinload(Grievance.evidence),
                selectinload(Grievance.timeline),
                selectinload(Grievance.resolution_report),
            )
        )
        result = await session.execute(stmt)
        grievance = result.scalar_one_or_none()
        if not grievance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grievance with tracking ID '{grievance_id}' not found.",
            )

        # IDOR Authorization Enforcement
        if current_user.role == "citizen":
            if grievance.citizen_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. You do not have permission to view grievances submitted by other citizens.",
                )
        elif current_user.role == "officer":
            # Officers can view grievances in their department or explicitly assigned to them
            if (
                grievance.assigned_officer_id != current_user.id
                and current_user.department_id
                and grievance.department_id != current_user.department_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. Grievance belongs to a different department jurisdiction.",
                )

        return _map_to_response(grievance)

    @staticmethod
    async def list_grievances(
        session: AsyncSession,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None,
        priority_filter: Optional[str] = None,
        department_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        ward_filter: Optional[str] = None,
        search: Optional[str] = None,
        assigned_to_me: bool = False,
    ) -> GrievanceListResponse:
        """
        Role-scoped filtered and paginated list of grievances.
        """
        page = max(1, page)
        page_size = min(max(1, page_size), 100)
        offset = (page - 1) * page_size

        stmt = select(Grievance).options(
            selectinload(Grievance.citizen),
            selectinload(Grievance.department),
            selectinload(Grievance.assigned_officer),
            selectinload(Grievance.evidence),
            selectinload(Grievance.timeline),
            selectinload(Grievance.resolution_report),
        )
        count_stmt = select(func.count(Grievance.id))

        # Role-based scoping
        if current_user.role == "citizen":
            stmt = stmt.where(Grievance.citizen_id == current_user.id)
            count_stmt = count_stmt.where(Grievance.citizen_id == current_user.id)
        elif current_user.role == "officer":
            if assigned_to_me:
                stmt = stmt.where(Grievance.assigned_officer_id == current_user.id)
                count_stmt = count_stmt.where(Grievance.assigned_officer_id == current_user.id)
            elif current_user.department_id:
                # Officer sees department grievances + their own assignments
                stmt = stmt.where(
                    or_(
                        Grievance.department_id == current_user.department_id,
                        Grievance.assigned_officer_id == current_user.id,
                    )
                )
                count_stmt = count_stmt.where(
                    or_(
                        Grievance.department_id == current_user.department_id,
                        Grievance.assigned_officer_id == current_user.id,
                    )
                )

        # Filters
        if status_filter and status_filter != "all":
            stmt = stmt.where(Grievance.status == status_filter)
            count_stmt = count_stmt.where(Grievance.status == status_filter)
        if priority_filter and priority_filter != "all":
            stmt = stmt.where(Grievance.priority == priority_filter)
            count_stmt = count_stmt.where(Grievance.priority == priority_filter)
        if department_filter and department_filter != "all":
            stmt = stmt.where(Grievance.department_id == department_filter)
            count_stmt = count_stmt.where(Grievance.department_id == department_filter)
        if category_filter and category_filter != "all":
            stmt = stmt.where(Grievance.category.ilike(f"%{category_filter}%"))
            count_stmt = count_stmt.where(Grievance.category.ilike(f"%{category_filter}%"))
        if ward_filter and ward_filter != "all":
            stmt = stmt.where(Grievance.ward == ward_filter)
            count_stmt = count_stmt.where(Grievance.ward == ward_filter)

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Grievance.id.ilike(search_pattern),
                    Grievance.title.ilike(search_pattern),
                    Grievance.description.ilike(search_pattern),
                    Grievance.address.ilike(search_pattern),
                )
            )
            count_stmt = count_stmt.where(
                or_(
                    Grievance.id.ilike(search_pattern),
                    Grievance.title.ilike(search_pattern),
                    Grievance.description.ilike(search_pattern),
                    Grievance.address.ilike(search_pattern),
                )
            )

        # Count total
        total_res = await session.execute(count_stmt)
        total = total_res.scalar() or 0

        # Order by submitted_at desc
        stmt = stmt.order_by(Grievance.submitted_at.desc()).offset(offset).limit(page_size)
        items_res = await session.execute(stmt)
        items = items_res.scalars().all()

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        return GrievanceListResponse(
            items=[_map_to_response(g) for g in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    async def transition_status(
        session: AsyncSession,
        grievance_id: str,
        target_status: str,
        notes: Optional[str],
        current_user: User,
        ip_address: str = "127.0.0.1",
    ) -> GrievanceResponse:
        """
        Validate and apply a lifecycle state transition.
        """
        stmt = select(Grievance).where(Grievance.id == grievance_id)
        result = await session.execute(stmt)
        grievance = result.scalar_one_or_none()
        if not grievance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grievance '{grievance_id}' not found.",
            )

        # Check officer department jurisdiction
        if current_user.role == "officer":
            if (
                grievance.assigned_officer_id != current_user.id
                and current_user.department_id
                and grievance.department_id != current_user.department_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Officers can only update grievances in their assigned department.",
                )

        is_owner = grievance.citizen_id == current_user.id
        LifecycleService.validate_transition(
            current_status=grievance.status,
            target_status=target_status,
            user=current_user,
            is_citizen_owner=is_owner,
        )

        await LifecycleService.record_transition(
            session=session,
            grievance=grievance,
            target_status=target_status,
            actor=current_user,
            notes=notes,
            ip_address=ip_address,
        )
        await session.commit()
        return await GrievanceService.get_grievance_by_id(session, grievance_id, current_user)

    @staticmethod
    async def submit_resolution(
        session: AsyncSession,
        grievance_id: str,
        report_text: str,
        officer_evidence_urls: List[str],
        current_user: User,
        ip_address: str = "127.0.0.1",
    ) -> GrievanceResponse:
        """
        Officer submits resolution report and moves status to resolution_submitted.
        """
        if current_user.role not in ("officer", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only municipal officers and administrators can submit grievance resolutions.",
            )

        stmt = select(Grievance).where(Grievance.id == grievance_id)
        result = await session.execute(stmt)
        grievance = result.scalar_one_or_none()
        if not grievance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grievance '{grievance_id}' not found.",
            )

        # Officer department check
        if current_user.role == "officer":
            if (
                grievance.assigned_officer_id != current_user.id
                and current_user.department_id
                and grievance.department_id != current_user.department_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Officers can only resolve grievances assigned to their department.",
                )

        # Must be in_progress or assigned to submit resolution
        if grievance.status not in ("in_progress", "assigned", "reopened"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot submit resolution for grievance in '{grievance.status}' status. Must be 'in_progress'.",
            )

        # Check existing resolution report
        existing_rep = await session.execute(
            select(ResolutionReport).where(ResolutionReport.grievance_id == grievance_id)
        )
        report = existing_rep.scalar_one_or_none()
        if report:
            # Update existing report if reopened
            report.report_text = report_text
            report.officer_id = current_user.id
            report.resolved_at = datetime.now(timezone.utc)
            report.officer_evidence_urls = officer_evidence_urls
        else:
            report = ResolutionReport(
                grievance_id=grievance_id,
                officer_id=current_user.id,
                report_text=report_text,
                officer_evidence_urls=officer_evidence_urls,
                ai_verification_confidence=0.965,
                verified_by_admin=False,
            )
            session.add(report)

        # Transition status to resolution_submitted
        await LifecycleService.record_transition(
            session=session,
            grievance=grievance,
            target_status="resolution_submitted",
            actor=current_user,
            title="Resolution Report Submitted",
            description=f"Field resolution report submitted: {report_text[:120]}...",
            ip_address=ip_address,
        )

        await session.commit()
        return await GrievanceService.get_grievance_by_id(session, grievance_id, current_user)

    @staticmethod
    async def verify_resolution(
        session: AsyncSession,
        grievance_id: str,
        rating: int,
        comment: Optional[str],
        action: str,
        current_user: User,
        ip_address: str = "127.0.0.1",
    ) -> GrievanceResponse:
        """
        Citizen verifies or rejects resolution. Accept transitions to citizen_verified; Reject transitions to reopened.
        """
        stmt = (
            select(Grievance)
            .where(Grievance.id == grievance_id)
            .options(selectinload(Grievance.resolution_report))
        )
        result = await session.execute(stmt)
        grievance = result.scalar_one_or_none()
        if not grievance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grievance '{grievance_id}' not found.",
            )

        if current_user.role == "citizen" and grievance.citizen_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Citizens can only verify resolutions for their own complaints.",
            )

        if grievance.status != "resolution_submitted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot verify resolution when grievance is in '{grievance.status}' status. Expected 'resolution_submitted'.",
            )

        # Update resolution feedback
        if grievance.resolution_report:
            grievance.resolution_report.citizen_rating = rating
            grievance.resolution_report.citizen_comment = comment

        if action == "accept":
            target_status = "citizen_verified"
            title = "Resolution Accepted by Citizen"
            desc = f"Citizen verified and rated resolution {rating}/5 stars. Feedback: {comment or 'Satisfied'}"
        else:
            target_status = "reopened"
            title = "Resolution Rejected by Citizen — Grievance Reopened"
            desc = f"Citizen was not satisfied with the resolution (Rating: {rating}/5). Grievance has been reopened for remediation. Reason: {comment or 'Unresolved issue'}"

        await LifecycleService.record_transition(
            session=session,
            grievance=grievance,
            target_status=target_status,
            actor=current_user,
            title=title,
            description=desc,
            notes=comment,
            ip_address=ip_address,
        )

        await session.commit()
        return await GrievanceService.get_grievance_by_id(session, grievance_id, current_user)

    @staticmethod
    async def submit_appeal(
        session: AsyncSession,
        grievance_id: str,
        reason: str,
        evidence_file_ids: List[uuid.UUID],
        current_user: User,
        ip_address: str = "127.0.0.1",
    ) -> GrievanceResponse:
        """
        Citizen appeals a closed or citizen-verified grievance, transitioning it to reopened.
        """
        stmt = select(Grievance).where(Grievance.id == grievance_id)
        result = await session.execute(stmt)
        grievance = result.scalar_one_or_none()
        if not grievance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grievance '{grievance_id}' not found.",
            )

        if current_user.role == "citizen" and grievance.citizen_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot file an appeal for another citizen's grievance.",
            )

        if grievance.status not in ("closed", "citizen_verified", "resolution_submitted"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Grievance in status '{grievance.status}' is not eligible for appeal. Must be closed or verified.",
            )

        # Attach any appeal evidence
        if evidence_file_ids:
            for ev_id in evidence_file_ids:
                ev_res = await session.execute(
                    select(GrievanceEvidence).where(
                        GrievanceEvidence.id == ev_id,
                        GrievanceEvidence.uploaded_by == current_user.id,
                    )
                )
                ev = ev_res.scalar_one_or_none()
                if ev:
                    ev.grievance_id = grievance_id

        await LifecycleService.record_transition(
            session=session,
            grievance=grievance,
            target_status="reopened",
            actor=current_user,
            title="Citizen Appeal Filed",
            description=f"Formal appeal lodged by citizen: {reason}",
            notes=reason,
            ip_address=ip_address,
        )

        await session.commit()
        return await GrievanceService.get_grievance_by_id(session, grievance_id, current_user)

    @staticmethod
    async def reassign_grievance(
        session: AsyncSession,
        grievance_id: str,
        department_id: Optional[str],
        officer_id: Optional[uuid.UUID],
        reason: Optional[str],
        current_user: User,
        ip_address: str = "127.0.0.1",
    ) -> GrievanceResponse:
        """
        Reassign grievance to a different department or designated officer.
        """
        if current_user.role not in ("officer", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only municipal officers and administrators can reassign grievances.",
            )

        stmt = select(Grievance).where(Grievance.id == grievance_id)
        result = await session.execute(stmt)
        grievance = result.scalar_one_or_none()
        if not grievance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grievance '{grievance_id}' not found.",
            )

        details_parts = []
        if department_id and department_id != grievance.department_id:
            dept_res = await session.execute(select(Department).where(Department.id == department_id))
            dept = dept_res.scalar_one_or_none()
            if not dept:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Department '{department_id}' does not exist.",
                )
            details_parts.append(f"Department transferred from {grievance.department_id} to {department_id}")
            grievance.department_id = department_id

        if officer_id and officer_id != grievance.assigned_officer_id:
            officer_res = await session.execute(select(User).where(User.id == officer_id, User.role == "officer"))
            officer = officer_res.scalar_one_or_none()
            if not officer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Officer with ID '{officer_id}' not found.",
                )
            details_parts.append(f"Assigned officer set to {officer.full_name}")
            grievance.assigned_officer_id = officer_id

        if grievance.status in ("submitted", "analyzed"):
            grievance.status = "assigned"

        change_summary = "; ".join(details_parts) if details_parts else "Assignment details updated"
        timeline_event = GrievanceTimeline(
            grievance_id=grievance.id,
            status=grievance.status,
            title="Grievance Reassigned",
            description=f"{change_summary}. Reason: {reason or 'Administrative reallocation'}",
            actor_name=current_user.full_name,
            actor_role=current_user.role.capitalize(),
            notes=reason,
        )
        session.add(timeline_event)

        audit = AuditLog(
            action="GRIEVANCE_REASSIGNED",
            entity_type="grievance",
            entity_id=grievance.id,
            performed_by=f"{current_user.full_name} ({current_user.email})",
            user_role=current_user.role,
            details=f"{change_summary}. Reason: {reason or 'N/A'}",
            ip_address=ip_address,
        )
        session.add(audit)

        await session.commit()
        return await GrievanceService.get_grievance_by_id(session, grievance_id, current_user)

    @staticmethod
    def triage_preview(payload: TriagePreviewRequest) -> TriagePreviewResponse:
        """
        Deterministic municipal rule-based triage preview fallback.
        Explicitly marked as rule-based fallback until ML models (Phase 5) are active.
        """
        corpus = f"{payload.title} {payload.description}".lower()
        matched_rule = None
        matched_keywords = []

        for rule in DEPARTMENT_KEYWORD_RULES:
            found = [kw for kw in rule["keywords"] if kw in corpus]
            if found:
                if not matched_rule or len(found) > len(matched_keywords):
                    matched_rule = rule
                    matched_keywords = found

        if not matched_rule:
            matched_rule = DEPARTMENT_KEYWORD_RULES[0]

        # Calculate heuristic priority based on urgency keywords
        urgency_keywords = ["emergency", "danger", "burst", "severe", "fatal", "spark", "fire", "immediate", "hazard"]
        if any(w in corpus for w in urgency_keywords):
            prio = "critical"
            dur = 1.5
            conf = 0.940
        elif any(w in corpus for w in ["overflow", "blocked", "broken", "major", "stagnant"]):
            prio = "high"
            dur = 2.5
            conf = 0.910
        else:
            prio = "medium"
            dur = 3.5
            conf = 0.880

        return TriagePreviewResponse(
            predicted_category=matched_rule["category"],
            predictedCategory=matched_rule["category"],
            predicted_subcategory=matched_rule["subcategory"],
            predictedSubcategory=matched_rule["subcategory"],
            suggested_department_id=matched_rule["dept_id"],
            suggestedDepartmentId=matched_rule["dept_id"],
            suggested_department_name=matched_rule["dept_name"],
            suggestedDepartmentName=matched_rule["dept_name"],
            priority=prio,  # type: ignore[arg-type]
            confidence=conf,
            predicted_duration_days=dur,
            predictedDurationDays=dur,
            is_mock_fallback=True,
            isMockFallback=True,
            keywords_matched=matched_keywords,
            keywordsMatched=matched_keywords,
        )
