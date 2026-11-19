import { mockDelay, USE_MOCK, apiClient } from "./apiClient";

export interface SlaBreachRiskItem {
  grievanceId: string;
  title: string;
  department: string;
  breachProbability: number;
  riskTier: "critical" | "high" | "medium" | "low";
  hoursRemaining: number;
  contributingFactors: string[];
  recommendedAction: string;
}

export interface DepartmentForecast {
  department: string;
  currentActive: number;
  projectedIncoming7d: number;
  projectedResolved7d: number;
  netBacklogChange: number;
  capacityUtilizationPct: number;
  riskLevel: "safe" | "strained" | "overloaded";
}

export const predictionService = {
  async getSlaBreachQueue(): Promise<SlaBreachRiskItem[]> {
    const items: SlaBreachRiskItem[] = [
      {
        grievanceId: "GRV-2026-8939",
        title: "12 consecutive streetlights non-functional on Sector Road",
        department: "Urban Electricity & Street Lighting",
        breachProbability: 0.94,
        riskTier: "critical",
        hoursRemaining: -14, // breached
        contributingFactors: [
          "Specialized underground cable splice equipment required",
          "Department backlog elevated by 18% over historical mean",
          "Assigned officer currently handling 19 concurrent cases",
        ],
        recommendedAction: "Authorize emergency overtime crew or divert standby contractor team.",
      },
      {
        grievanceId: "GRV-2026-8936",
        title: "Dangerous high-tension cable sagging across residential lane",
        department: "Urban Electricity & Street Lighting",
        breachProbability: 0.91,
        riskTier: "critical",
        hoursRemaining: -42, // breached
        contributingFactors: [
          "11kV power isolation shutdown permit pending",
          "Traffic police escort required for hydraulic crane deployment",
        ],
        recommendedAction: "Escalate to Chief Electrical Inspector for immediate expedited clearance.",
      },
      {
        grievanceId: "GRV-2026-8941",
        title: "Major water pipeline rupture causing localized flooding",
        department: "Water Supply & Sewerage Board",
        breachProbability: 0.68,
        riskTier: "high",
        hoursRemaining: 24,
        contributingFactors: [
          "Heavy earth excavation required under main roadway",
          "Inter-departmental coordination needed with PWD for road cutting",
        ],
        recommendedAction: "Fast-track joint excavation permit and provide additional backhoe unit.",
      },
      {
        grievanceId: "GRV-2026-8935",
        title: "Sewage backflow into residential ground floor toilets",
        department: "Water Supply & Sewerage Board",
        breachProbability: 0.52,
        riskTier: "medium",
        hoursRemaining: 31,
        contributingFactors: ["Vehicle RJ-04 Super-Sucker transit time during peak traffic hours"],
        recommendedAction: "Confirm evening clearing shift to complete suction desilting.",
      },
      {
        grievanceId: "GRV-2026-8942",
        title: "Severe deep pothole causing two-wheeler accidents at night",
        department: "Public Works Department (PWD)",
        breachProbability: 0.35,
        riskTier: "low",
        hoursRemaining: 58,
        contributingFactors: ["Weather conditions dry and road mix batch plant operating normally"],
        recommendedAction: "Maintain scheduled patching queue for night window.",
      },
    ];

    return mockDelay(items, 150);
  },

  async getDepartmentForecast(): Promise<DepartmentForecast[]> {
    const list: DepartmentForecast[] = [
      {
        department: "Water Supply & Sewerage Board",
        currentActive: 312,
        projectedIncoming7d: 140,
        projectedResolved7d: 110,
        netBacklogChange: 30,
        capacityUtilizationPct: 118,
        riskLevel: "overloaded",
      },
      {
        department: "Urban Electricity & Street Lighting",
        currentActive: 198,
        projectedIncoming7d: 85,
        projectedResolved7d: 80,
        netBacklogChange: 5,
        capacityUtilizationPct: 94,
        riskLevel: "strained",
      },
      {
        department: "Public Works Department (PWD)",
        currentActive: 184,
        projectedIncoming7d: 90,
        projectedResolved7d: 105,
        netBacklogChange: -15,
        capacityUtilizationPct: 78,
        riskLevel: "safe",
      },
      {
        department: "Solid Waste Management",
        currentActive: 245,
        projectedIncoming7d: 160,
        projectedResolved7d: 175,
        netBacklogChange: -15,
        capacityUtilizationPct: 82,
        riskLevel: "safe",
      },
      {
        department: "Public Health & Vector Control",
        currentActive: 112,
        projectedIncoming7d: 40,
        projectedResolved7d: 45,
        netBacklogChange: -5,
        capacityUtilizationPct: 72,
        riskLevel: "safe",
      },
      {
        department: "Horticulture & Public Parks",
        currentActive: 76,
        projectedIncoming7d: 25,
        projectedResolved7d: 28,
        netBacklogChange: -3,
        capacityUtilizationPct: 65,
        riskLevel: "safe",
      },
    ];

    return mockDelay(list, 150);
  },

  async getResolutionTimeAccuracy() {
    return mockDelay(
      [
        { category: "Solid Waste", actualAvgDays: 2.1, predictedAvgDays: 2.0, accuracyPct: 95.2 },
        { category: "Public Health", actualAvgDays: 3.0, predictedAvgDays: 2.9, accuracyPct: 96.6 },
        { category: "Electricity", actualAvgDays: 3.5, predictedAvgDays: 3.8, accuracyPct: 91.4 },
        { category: "Roads (PWD)", actualAvgDays: 4.2, predictedAvgDays: 4.0, accuracyPct: 95.2 },
        { category: "Parks", actualAvgDays: 5.4, predictedAvgDays: 5.1, accuracyPct: 94.4 },
        { category: "Water Supply", actualAvgDays: 6.8, predictedAvgDays: 6.2, accuracyPct: 91.1 },
      ],
      150
    );
  },
};
