import { DuplicateCluster, Grievance } from "@/types";
import { MOCK_DUPLICATE_CLUSTERS, MOCK_GRIEVANCES } from "@/mocks/mockData";
import { mockDelay, USE_MOCK, apiClient } from "./apiClient";

let localClusters: DuplicateCluster[] = [...MOCK_DUPLICATE_CLUSTERS];

export const duplicateService = {
  async getClusters(): Promise<DuplicateCluster[]> {
    if (!USE_MOCK) {
      try {
        const res = await apiClient.get<DuplicateCluster[]>("/duplicates");
        return res.data;
      } catch (e) {
        console.warn("Falling back to local duplicate clusters", e);
      }
    }
    return mockDelay([...localClusters], 150);
  },

  async getClusterById(id: string): Promise<DuplicateCluster | null> {
    const cluster = localClusters.find((c) => c.id === id) || null;
    return mockDelay(cluster, 100);
  },

  async approveMerge(clusterId: string, masterId: string): Promise<DuplicateCluster | null> {
    const cluster = localClusters.find((c) => c.id === clusterId);
    if (!cluster) return null;

    cluster.status = "merged";
    cluster.masterGrievanceId = masterId;
    return mockDelay({ ...cluster }, 250);
  },

  async rejectDuplicate(clusterId: string, reason?: string): Promise<DuplicateCluster | null> {
    const cluster = localClusters.find((c) => c.id === clusterId);
    if (!cluster) return null;

    cluster.status = "rejected";
    return mockDelay({ ...cluster }, 200);
  },

  async markAsRelated(clusterId: string): Promise<DuplicateCluster | null> {
    const cluster = localClusters.find((c) => c.id === clusterId);
    if (!cluster) return null;

    cluster.status = "split";
    return mockDelay({ ...cluster }, 200);
  },

  async getClusterGrievances(cluster: DuplicateCluster): Promise<Grievance[]> {
    const list = MOCK_GRIEVANCES.filter((g) => cluster.grievanceIds.includes(g.id));
    return mockDelay(list, 100);
  },

  async searchSemanticDuplicates(params: {
    grievance_id?: string;
    title?: string;
    description?: string;
    latitude?: number;
    longitude?: number;
    category?: string;
  }) {
    if (!USE_MOCK) {
      try {
        const res = await apiClient.post("/ai/duplicates", params);
        return res.data;
      } catch (e) {
        console.warn("Falling back to local duplicate search", e);
      }
    }
    return mockDelay(
      {
        matches: [],
        total_found: 0,
        search_vector_dimension: 768,
      },
      150
    );
  },
};
