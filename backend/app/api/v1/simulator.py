"""
CivicMind AI — Counterfactual Workload Simulator API Router
Phase 6 Counterfactual Staffing & Policy Simulator.

Provides endpoints for running what-if policy scenarios and evaluating baseline
workload metrics across municipal departments.
"""

from fastapi import APIRouter
from app.schemas.simulator import (
    SimulatorInputSchema,
    SimulatorResultSchema,
)
from app.services.simulator_service import simulator_service

router = APIRouter(prefix="/simulator", tags=["Counterfactual Workload Simulator"])


@router.post(
    "/run",
    response_model=SimulatorResultSchema,
    summary="Run Counterfactual Simulation",
    description="Simulates the effect of officer staffing, capacity multipliers, and AI routing weights on backlogs and SLA compliance.",
)
async def run_simulation(
    input_data: SimulatorInputSchema,
) -> SimulatorResultSchema:
    return simulator_service.run_simulation(input_data)


@router.get(
    "/baseline",
    response_model=SimulatorResultSchema,
    summary="Get Baseline Simulation Metrics",
    description="Returns unmodified municipal workload and SLA baseline numbers.",
)
async def get_baseline() -> SimulatorResultSchema:
    return simulator_service.get_baseline()
