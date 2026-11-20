import { Hotspot } from "@/types";
import { MOCK_HOTSPOTS } from "@/mocks/mockData";
import { mockDelay, USE_MOCK, apiClient } from "./apiClient";

let localHotspots: Hotspot[] = [...MOCK_HOTSPOTS];

export const earlyWarningService = {
  async getHotspots(category?: string, riskLevel?: string): Promise<Hotspot[]> {
    if (!USE_MOCK) {
      try {
        const res = await apiClient.get<Hotspot[]>("/early-warning/hotspots", {
          params: { category, riskLevel },
        });
        return res.data;
      } catch (e) {
        console.warn("Falling back to local hotspots", e);
      }
    }

    let result = [...localHotspots];
    if (category && category !== "all") {
      result = result.filter((h) => h.category.toLowerCase().includes(category.toLowerCase()));
    }
    if (riskLevel && riskLevel !== "all") {
      result = result.filter((h) => h.riskLevel === riskLevel);
    }
    return mockDelay(result, 150);
  },

  async getById(id: string): Promise<Hotspot | null> {
    if (!USE_MOCK) {
      try {
        const res = await apiClient.get<Hotspot>(`/early-warning/hotspots/${id}`);
        return res.data;
      } catch (e) {
        console.warn("Falling back to local hotspot", e);
      }
    }
    const item = localHotspots.find((h) => h.id === id) || null;
    return mockDelay(item, 100);
  },

  async acknowledgeHotspot(id: string, notes?: string): Promise<Hotspot | null> {
    if (!USE_MOCK) {
      try {
        const res = await apiClient.post<Hotspot>(`/early-warning/hotspots/${id}/acknowledge`, {
          notes: notes || "Emergency inspection dispatched by Apex Control",
        });
        return res.data;
      } catch (e) {
        console.warn("Falling back to local acknowledge", e);
      }
    }
    const item = localHotspots.find((h) => h.id === id);
    if (!item) return null;
    item.recommendedAction = `${item.recommendedAction} (Acknowledged: ${notes || "Action team assigned"})`;
    return mockDelay({ ...item }, 200);
  },
};
