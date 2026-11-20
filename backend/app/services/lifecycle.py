"""
CivicMind AI — Grievance Lifecycle State Machine & Transition Engine
Enforces strict lifecycle rules, role authorization, timeline recording, and audit trails.
"""

from typing import Optional, Dict, Set, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.models.grievance import Grievance
from app.models.timeline import GrievanceTimeline
from app.models.audit import AuditLog
from app.models.user import User
from app.models.outbox import OutboxEvent


# Valid lifecycle state transitions: from_status -> set of allowed to_statuses
ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
    "submitted": {"analyzed", "assigned", "in_progress"},
    "analyzed": {"assigned", "in_progress", "escalated"},
    "assigned": {"in_progress", "assigned", "escalated"},
    "in_progress": {"resolution_submitted", "escalated", "assigned"},
    "resolution_submitted": {"citizen_verified", "closed", "reopened"},
    "citizen_verified": {"closed", "reopened"},
    "closed": {"reopened"},
    "escalated": {"assigned", "in_progress", "closed"},
    "reopened": {"assigned", "in_progress", "escalated"},
}

# Role permissions per target status
ROLE_TARGET_STATUS_RULES: Dict[str, Set[str]] = {
    "citizen": {"citizen_verified", "closed", "reopened"},
    "officer": {"assigned", "in_progress", "resolution_submitted", "escalated"},
    "admin": {
        "submitted",
        "analyzed",
        "assigned",
        "in_progress",
        "resolution_submitted",
        "citizen_verified",
        "closed",
        "escalated",
        "reopened",
    },
}

STATUS_TITLES: Dict[str, str] = {
    "submitted": "Grievance Registered",
    "analyzed": "AI Intelligence Analysis Completed",
    "assigned": "Department & Officer Assigned",
    "in_progress": "Investigation & Field Work In Progress",
    "resolution_submitted": "Resolution Report Submitted by Officer",
    "citizen_verified": "Resolution Verified and Approved by Citizen",
    "closed": "Grievance Formally Closed",
    "escalated": "Escalated for Executive Review",
    "reopened": "Grievance Reopened for Further Remediation",
}


class LifecycleService:
    @staticmethod
    def validate_transition(
        current_status: str,
        target_status: str,
        user: User,
        is_citizen_owner: bool = False,
    ) -> None:
        """
        Validate whether the given status transition is valid and authorized for the user.
        Raises HTTP 400 or 403 on violation.
        """
        if current_status == target_status:
            return

        valid_targets = ALLOWED_TRANSITIONS.get(current_status, set())
        if target_status not in valid_targets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid lifecycle transition from '{current_status}' to '{target_status}'. "
                f"Allowed target states: {sorted(list(valid_targets)) if valid_targets else 'None'}",
            )

        # Role-based transition authorization
        allowed_for_role = ROLE_TARGET_STATUS_RULES.get(user.role, set())
        if target_status not in allowed_for_role and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User with role '{user.role}' is not authorized to transition grievance to '{target_status}'.",
            )

        # Citizen can only transition their own grievance
        if user.role == "citizen" and not is_citizen_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Citizens can only verify or appeal grievances they personally submitted.",
            )

    @staticmethod
    async def record_transition(
        session: AsyncSession,
        grievance: Grievance,
        target_status: str,
        actor: User,
        title: Optional[str] = None,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        ip_address: str = "127.0.0.1",
    ) -> GrievanceTimeline:
        """
        Atomically update grievance status, record immutable timeline event, and persist audit log.
        """
        old_status = grievance.status
        grievance.status = target_status
        grievance.updated_at = datetime.now(timezone.utc)

        if target_status == "resolution_submitted" and not grievance.actual_resolution_date:
            grievance.actual_resolution_date = datetime.now(timezone.utc)

        event_title = title or STATUS_TITLES.get(target_status, f"Status changed to {target_status}")
        event_desc = description or f"Status transitioned from '{old_status}' to '{target_status}'."

        timeline_event = GrievanceTimeline(
            grievance_id=grievance.id,
            status=target_status,
            title=event_title,
            description=event_desc,
            actor_name=actor.full_name,
            actor_role=actor.role.capitalize(),
            notes=notes,
        )
        session.add(timeline_event)

        audit = AuditLog(
            action="GRIEVANCE_STATUS_TRANSITION",
            entity_type="grievance",
            entity_id=grievance.id,
            performed_by=f"{actor.full_name} ({actor.email})",
            user_role=actor.role,
            details=f"Status transitioned from '{old_status}' to '{target_status}'. Notes: {notes or 'N/A'}",
            ip_address=ip_address,
        )
        session.add(audit)

        # Enqueue transactional outbox event atomically
        outbox = OutboxEvent(
            event_type="grievance.status_changed",
            aggregate_type="grievance",
            aggregate_id=grievance.id,
            payload={
                "grievance_id": grievance.id,
                "tracking_id": grievance.id,
                "title": grievance.title,
                "old_status": old_status,
                "new_status": target_status,
                "actor_name": actor.full_name,
                "actor_role": actor.role,
                "notes": notes or event_desc,
            },
            correlation_id=f"grv-status-{grievance.id}-{target_status}",
        )
        session.add(outbox)

        return timeline_event
