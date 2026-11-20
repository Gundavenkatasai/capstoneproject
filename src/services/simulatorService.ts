import { SimulatorInput, SimulatorResult } from "@/types";
import { mockDelay, USE_MOCK, apiClient } from "./apiClient";

export const simulatorService = {
  async runSimulation(input: SimulatorInput): Promise<SimulatorResult> {
    if (!USE_MOCK) {
      try {
        const res = await apiClient.post<SimulatorResult>("/simulator/run", input);
        return res.data;
      } catch (e) {
        console.warn("Falling back to local simulation engine", e);
      }
    }

    const baseBacklog = 1127;
    const baseResolutionDays = 4.3;
    const baseSlaBreachRate = 12.8;

    // Simulation formulas based on input levers:
    // Adding officers reduces backlog and SLA breaches
    const officerEffect = input.additionalOfficers * 22;
    // Capacity multiplier improves throughput
    const capacityEffect = (input.departmentCapacityMultiplier - 1.0) * 280;
    // Redistribution flattens bottleneck departments
    const redistributionEffect = (input.workloadRedistributionPct / 100) * 140;
    // AI routing accuracy reduces misrouting bounce-backs
    const routingEffect = ((input.routingWeightAIFactor - 0.5) / 0.5) * 60;

    const totalReduction = Math.max(0, officerEffect + capacityEffect + redistributionEffect + routingEffect);
    const simulatedBacklog = Math.max(280, Math.round(baseBacklog - totalReduction));

    const simulatedDays = Math.max(
      1.8,
      Number((baseResolutionDays * (simulatedBacklog / baseBacklog)).toFixed(1))
    );

    const thresholdFactor = input.escalationThresholdHours < 24 ? 0.75 : 1.0;
    const simulatedSlaRate = Math.max(
      3.2,
      Number((baseSlaBreachRate * (simulatedBacklog / baseBacklog) * thresholdFactor).toFixed(1))
    );

    const departmentWorkload = [
      {
        department: "Water Supply & Sewerage",
        currentLoad: 312,
        projectedLoad: Math.round(312 - (totalReduction * 0.38)),
        capacity: Math.round(260 * input.departmentCapacityMultiplier + input.additionalOfficers * 6),
      },
      {
        department: "Solid Waste Management",
        currentLoad: 245,
        projectedLoad: Math.round(245 - (totalReduction * 0.22)),
        capacity: Math.round(290 * input.departmentCapacityMultiplier + input.additionalOfficers * 4),
      },
      {
        department: "Electricity & Lighting",
        currentLoad: 198,
        projectedLoad: Math.round(198 - (totalReduction * 0.2)),
        capacity: Math.round(210 * input.departmentCapacityMultiplier + input.additionalOfficers * 4),
      },
      {
        department: "Public Works (Roads)",
        currentLoad: 184,
        projectedLoad: Math.round(184 - (totalReduction * 0.12)),
        capacity: Math.round(230 * input.departmentCapacityMultiplier + input.additionalOfficers * 3),
      },
      {
        department: "Public Health",
        currentLoad: 112,
        projectedLoad: Math.round(112 - (totalReduction * 0.05)),
        capacity: Math.round(150 * input.departmentCapacityMultiplier + input.additionalOfficers * 2),
      },
      {
        department: "Horticulture & Parks",
        currentLoad: 76,
        projectedLoad: Math.round(76 - (totalReduction * 0.03)),
        capacity: Math.round(110 * input.departmentCapacityMultiplier + input.additionalOfficers * 1),
      },
    ];

    const summary = `Simulating an injection of ${input.additionalOfficers} officers and ${Math.round(
      (input.departmentCapacityMultiplier - 1) * 100
    )}% capacity enhancement projects a ${Math.round(
      ((baseBacklog - simulatedBacklog) / baseBacklog) * 100
    )}% reduction in system-wide active backlog, improving SLA compliance by ${(baseSlaBreachRate - simulatedSlaRate).toFixed(1)} percentage points.`;

    return mockDelay(
      {
        currentBacklog: baseBacklog,
        simulatedBacklog,
        currentAvgResolutionDays: baseResolutionDays,
        simulatedAvgResolutionDays: simulatedDays,
        currentSlaBreachRate: baseSlaBreachRate,
        simulatedSlaBreachRate: simulatedSlaRate,
        departmentWorkload,
        summary,
      },
      300
    );
  },
};
