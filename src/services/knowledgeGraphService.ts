import { KnowledgeGraphNode, KnowledgeGraphEdge } from "@/types";
import { MOCK_KNOWLEDGE_GRAPH_NODES, MOCK_KNOWLEDGE_GRAPH_EDGES } from "@/mocks/mockData";
import { mockDelay } from "./apiClient";

export const knowledgeGraphService = {
  async getGraphData(): Promise<{ nodes: KnowledgeGraphNode[]; edges: KnowledgeGraphEdge[] }> {
    return mockDelay(
      {
        nodes: [...MOCK_KNOWLEDGE_GRAPH_NODES],
        edges: [...MOCK_KNOWLEDGE_GRAPH_EDGES],
      },
      150
    );
  },

  async searchNodes(query: string, filterType?: string): Promise<KnowledgeGraphNode[]> {
    let result = [...MOCK_KNOWLEDGE_GRAPH_NODES];
    if (query) {
      result = result.filter((n) => n.label.toLowerCase().includes(query.toLowerCase()));
    }
    if (filterType && filterType !== "all") {
      result = result.filter((n) => n.type === filterType);
    }
    return mockDelay(result, 100);
  },
};
