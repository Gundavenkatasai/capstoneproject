"""
CivicMind AI — Counterfactual Workload Simulator Schemas
Pydantic v2 validation contracts for Phase 6 staffing and capacity simulation.
Supports dual camelCase & snake_case representation for Next.js frontend binding.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, AliasChoices


class SimulatorInputSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    additionalOfficers: int = Field(
        0,
        ge=0,
        le=100,
        validation_alias=AliasChoices("additionalOfficers", "additional_officers"),
    )
    departmentCapacityMultiplier: float = Field(
        1.0,
        ge=0.5,
        le=3.0,
        validation_alias=AliasChoices(
            "departmentCapacityMultiplier", "department_capacity_multiplier"
        ),
    )
    workloadRedistributionPct: float = Field(
        0.0,
        ge=0.0,
        le=100.0,
        validation_alias=AliasChoices(
            "workloadRedistributionPct", "workload_redistribution_pct"
        ),
    )
    routingWeightAIFactor: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices(
            "routingWeightAIFactor", "routing_weight_ai_factor"
        ),
    )
    escalationThresholdHours: int = Field(
        48,
        ge=6,
        le=168,
        validation_alias=AliasChoices(
            "escalationThresholdHours", "escalation_threshold_hours"
        ),
    )


class DepartmentWorkloadItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    department: str
    currentLoad: int = Field(
        ..., validation_alias=AliasChoices("currentLoad", "current_load")
    )
    projectedLoad: int = Field(
        ..., validation_alias=AliasChoices("projectedLoad", "projected_load")
    )
    capacity: int


class SimulatorResultSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    currentBacklog: int = Field(
        ..., validation_alias=AliasChoices("currentBacklog", "current_backlog")
    )
    simulatedBacklog: int = Field(
        ..., validation_alias=AliasChoices("simulatedBacklog", "simulated_backlog")
    )
    currentAvgResolutionDays: float = Field(
        ...,
        validation_alias=AliasChoices(
            "currentAvgResolutionDays", "current_avg_resolution_days"
        ),
    )
    simulatedAvgResolutionDays: float = Field(
        ...,
        validation_alias=AliasChoices(
            "simulatedAvgResolutionDays", "simulated_avg_resolution_days"
        ),
    )
    currentSlaBreachRate: float = Field(
        ...,
        validation_alias=AliasChoices(
            "currentSlaBreachRate", "current_sla_breach_rate"
        ),
    )
    simulatedSlaBreachRate: float = Field(
        ...,
        validation_alias=AliasChoices(
            "simulatedSlaBreachRate", "simulated_sla_breach_rate"
        ),
    )
    departmentWorkload: List[DepartmentWorkloadItem] = Field(
        default_factory=list,
        validation_alias=AliasChoices("departmentWorkload", "department_workload"),
    )
    summary: str
    officerUtilizationPct: float = Field(
        85.0,
        validation_alias=AliasChoices(
            "officerUtilizationPct", "officer_utilization_pct"
        ),
    )
    projectedSavingsHours: float = Field(
        0.0,
        validation_alias=AliasChoices(
            "projectedSavingsHours", "projected_savings_hours"
        ),
    )
