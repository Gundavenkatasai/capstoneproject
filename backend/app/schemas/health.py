"""
CivicMind AI — Health Check Pydantic Schemas
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ComponentStatus(BaseModel):
    status: str = Field(..., description="Component state: 'healthy', 'degraded', or 'unhealthy'")
    reachable: bool = Field(..., description="Whether the network connection was established")
    message: str = Field(..., description="Status summary or diagnostic message")
    latency_ms: Optional[float] = Field(None, description="Check execution duration in milliseconds")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class SystemHealthResponse(BaseModel):
    status: str = Field(..., description="'healthy', 'degraded', or 'unhealthy'")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Operating environment: development, staging, production")
    database: ComponentStatus
    redis: ComponentStatus
    pgvector: ComponentStatus


class SingleComponentHealthResponse(BaseModel):
    service: str
    status: str
    reachable: bool
    message: str
    latency_ms: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
