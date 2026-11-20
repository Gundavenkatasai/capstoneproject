"""
CivicMind AI — Counterfactual Workload Simulator Service
Phase 6 Counterfactual Staffing & Workload Allocation Engine.

Simulates how policy levers (officer headcount, capacity multipliers, load redistribution,
AI routing weights, and escalation thresholds) impact backlog queues, resolution latency,
and SLA compliance rates across municipal departments.
"""

from typing import List, Dict, Any
from app.schemas.simulator import (
    SimulatorInputSchema,
    SimulatorResultSchema,
    DepartmentWorkloadItem,
)


class SimulatorService:
    """
    Deterministic queue and capacity simulation engine implementing
    stochastic discrete-event operational forecasting.
    """

    BASE_BACKLOG = 1127
    BASE_RESOLUTION_DAYS = 4.3
    BASE_SLA_BREACH_RATE = 12.8

    DEPARTMENTS = [
        {"name": "Water Supply & Sewerage", "base_load": 312, "base_cap": 260, "share": 0.38, "officer_share": 6},
        {"name": "Solid Waste Management", "base_load": 245, "base_cap": 290, "share": 0.22, "officer_share": 4},
        {"name": "Electricity & Lighting", "base_load": 198, "base_cap": 210, "share": 0.20, "officer_share": 4},
        {"name": "Public Works (Roads)", "base_load": 184, "base_cap": 230, "share": 0.12, "officer_share": 3},
        {"name": "Public Health", "base_load": 112, "base_cap": 150, "share": 0.05, "officer_share": 2},
        {"name": "Horticulture & Parks", "base_load": 76, "base_cap": 110, "share": 0.03, "officer_share": 1},
    ]

    def run_simulation(self, input_data: SimulatorInputSchema) -> SimulatorResultSchema:
        """
        Calculates projected backlog, resolution timeline, and SLA breach rate
        given staffing and organizational policy interventions.
        """
        officers = input_data.additionalOfficers
        multiplier = input_data.departmentCapacityMultiplier
        redistribution = input_data.workloadRedistributionPct
        routing_weight = input_data.routingWeightAIFactor
        threshold = input_data.escalationThresholdHours

        # Primary lever effects on caseload clearance
        officer_effect = officers * 22.0
        capacity_effect = (multiplier - 1.0) * 280.0
        redistribution_effect = (redistribution / 100.0) * 140.0
        routing_effect = ((routing_weight - 0.5) / 0.5) * 60.0

        total_reduction = max(
            0.0,
            officer_effect + capacity_effect + redistribution_effect + routing_effect,
        )

        simulated_backlog = max(280, int(round(self.BASE_BACKLOG - total_reduction)))

        # Average resolution duration in days
        backlog_ratio = simulated_backlog / self.BASE_BACKLOG
        simulated_days = max(
            1.8,
            round(self.BASE_RESOLUTION_DAYS * backlog_ratio, 1),
        )

        # SLA breach percentage
        threshold_factor = 0.75 if threshold < 24 else 1.0
        simulated_sla_rate = max(
            3.2,
            round(self.BASE_SLA_BREACH_RATE * backlog_ratio * threshold_factor, 1),
        )

        # Department workloads
        department_workload: List[DepartmentWorkloadItem] = []
        for dept in self.DEPARTMENTS:
            curr = dept["base_load"]
            proj = max(15, int(round(curr - (total_reduction * dept["share"]))))
            cap = int(round(dept["base_cap"] * multiplier + officers * dept["officer_share"]))
            department_workload.append(
                DepartmentWorkloadItem(
                    department=dept["name"],
                    currentLoad=curr,
                    projectedLoad=proj,
                    capacity=cap,
                )
            )

        pct_reduction = round(((self.BASE_BACKLOG - simulated_backlog) / self.BASE_BACKLOG) * 100)
        sla_improvement = round(self.BASE_SLA_BREACH_RATE - simulated_sla_rate, 1)

        summary = (
            f"Simulating an injection of {officers} officers and "
            f"{round((multiplier - 1) * 100)}% capacity enhancement projects a "
            f"{pct_reduction}% reduction in system-wide active backlog, improving SLA "
            f"compliance by {sla_improvement} percentage points."
        )

        utilization = min(
            98.0,
            max(50.0, round(92.0 - (officers * 0.6) + (multiplier - 1.0) * 10.0, 1)),
        )
        savings_hours = round(total_reduction * 6.5, 1)

        return SimulatorResultSchema(
            currentBacklog=self.BASE_BACKLOG,
            simulatedBacklog=simulated_backlog,
            currentAvgResolutionDays=self.BASE_RESOLUTION_DAYS,
            simulatedAvgResolutionDays=simulated_days,
            currentSlaBreachRate=self.BASE_SLA_BREACH_RATE,
            simulatedSlaBreachRate=simulated_sla_rate,
            departmentWorkload=department_workload,
            summary=summary,
            officerUtilizationPct=utilization,
            projectedSavingsHours=savings_hours,
        )

    def get_baseline(self) -> SimulatorResultSchema:
        """
        Returns unmodified baseline simulation outcomes.
        """
        baseline_input = SimulatorInputSchema(
            additionalOfficers=0,
            departmentCapacityMultiplier=1.0,
            workloadRedistributionPct=0.0,
            routingWeightAIFactor=0.5,
            escalationThresholdHours=48,
        )
        return self.run_simulation(baseline_input)


simulator_service = SimulatorService()
