import React, { useEffect, useState } from "react";
import { knowledgeGraphService } from "@/services/knowledgeGraphService";
import { KnowledgeGraphNode, KnowledgeGraphEdge } from "@/types";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { SearchInput } from "@/components/common/SearchInput";
import { LoadingSkeleton } from "@/components/common/EmptyState";
import {
  Share2,
  Building,
  Layers,
  Wrench,
  MapPin,
  FileCheck,
  User,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Info,
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function KnowledgeGraphPage() {
  const [nodes, setNodes] = useState<KnowledgeGraphNode[]>([]);
  const [edges, setEdges] = useState<KnowledgeGraphEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<KnowledgeGraphNode | null>(null);
  const [typeFilter, setTypeFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [zoomLevel, setZoomLevel] = useState(1);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await knowledgeGraphService.getGraphData();
      setNodes(data.nodes);
      setEdges(data.edges);
      if (data.nodes.length > 0) setSelectedNode(data.nodes[0]);
      setLoading(false);
    }
    load();
  }, []);

  const filteredNodes = nodes.filter((n) => {
    const matchesSearch = n.label.toLowerCase().includes(search.toLowerCase());
    const matchesType = typeFilter === "all" || n.type === typeFilter;
    return matchesSearch && matchesType;
  });

  const getNodeColor = (type: string) => {
    switch (type) {
      case "department":
        return { bg: "bg-blue-600", text: "text-white", border: "border-blue-700" };
      case "category":
        return { bg: "bg-emerald-600", text: "text-white", border: "border-emerald-700" };
      case "asset":
        return { bg: "bg-red-500", text: "text-white", border: "border-red-600" };
      case "jurisdiction":
        return { bg: "bg-purple-600", text: "text-white", border: "border-purple-700" };
      case "procedure":
        return { bg: "bg-indigo-600", text: "text-white", border: "border-indigo-700" };
      case "officer":
        return { bg: "bg-amber-600", text: "text-white", border: "border-amber-700" };
      default:
        return { bg: "bg-slate-700", text: "text-white", border: "border-slate-800" };
    }
  };

  // Connected edges for selected node
  const connectedEdges = edges.filter(
    (e) => e.source === selectedNode?.id || e.target === selectedNode?.id
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Civic Entity Knowledge Graph"
        subtitle="Graph database ontology connecting departments, infrastructure assets, standard operating procedures, and ward jurisdictions."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Knowledge Graph", active: true },
        ]}
        badge="Neo4j / RDF Triple Store"
      />

      {/* Filter and Zoom Controls */}
      <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-subtle flex flex-col md:flex-row items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          <SearchInput
            value={search}
            onChange={setSearch}
            placeholder="Search entity node..."
            className="w-full md:w-64"
          />

          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-slate-500 font-medium">Filter Type:</span>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-2.5 py-1.5 border border-slate-200 rounded text-slate-800 font-medium bg-white"
            >
              <option value="all">All Entity Types ({nodes.length})</option>
              <option value="department">Departments</option>
              <option value="category">Categories</option>
              <option value="asset">Physical Assets</option>
              <option value="jurisdiction">Jurisdictions</option>
              <option value="procedure">SOP Procedures</option>
              <option value="officer">Duty Officers</option>
            </select>
          </div>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-1 bg-slate-50 p-1 rounded border border-slate-200">
          <button
            onClick={() => setZoomLevel((z) => Math.max(0.6, z - 0.2))}
            className="p-1 rounded hover:bg-slate-200 text-slate-600"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="font-mono text-xs text-slate-600 px-2">
            {Math.round(zoomLevel * 100)}%
          </span>
          <button
            onClick={() => setZoomLevel((z) => Math.min(1.8, z + 0.2))}
            className="p-1 rounded hover:bg-slate-200 text-slate-600"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={() => setZoomLevel(1)}
            className="p-1 rounded hover:bg-slate-200 text-slate-600"
            title="Reset Zoom"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {loading ? (
        <LoadingSkeleton count={3} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Main Interactive Graph Canvas (8 cols) */}
          <div className="lg:col-span-8 bg-[#0b132b] rounded-lg border border-slate-800 p-4 relative h-[520px] overflow-hidden flex flex-col justify-between shadow-card">
            {/* Graph Legend Overlay */}
            <div className="absolute top-3 left-3 z-10 flex flex-wrap gap-2 text-[10px] font-mono text-white bg-slate-900/80 p-2 rounded border border-slate-700 backdrop-blur-xs">
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-600" /> Dept
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-600" /> Category
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500" /> Asset
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-purple-600" /> Jurisdiction
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-600" /> Procedure
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-600" /> Officer
              </span>
            </div>

            {/* Interactive SVG Graph Network */}
            <div className="w-full h-full relative overflow-hidden flex items-center justify-center">
              <svg
                className="w-full h-full transition-transform duration-200"
                style={{ transform: `scale(${zoomLevel})` }}
                viewBox="0 0 700 460"
              >
                {/* Graph Edges / Relationship Connectors */}
                {edges.map((edge) => {
                  const sIdx = nodes.findIndex((n) => n.id === edge.source);
                  const tIdx = nodes.findIndex((n) => n.id === edge.target);
                  if (sIdx === -1 || tIdx === -1) return null;

                  // Circular layout positioning coordinates
                  const total = nodes.length;
                  const getCoords = (idx: number) => {
                    const angle = (idx / total) * 2 * Math.PI;
                    const radius = 175;
                    return {
                      x: 350 + radius * Math.cos(angle),
                      y: 230 + radius * Math.sin(angle),
                    };
                  };

                  const s = getCoords(sIdx);
                  const t = getCoords(tIdx);

                  const isConnected =
                    selectedNode?.id === edge.source || selectedNode?.id === edge.target;

                  return (
                    <g key={edge.id}>
                      <line
                        x1={s.x}
                        y1={s.y}
                        x2={t.x}
                        y2={t.y}
                        stroke={isConnected ? "#60a5fa" : "#334155"}
                        strokeWidth={isConnected ? 2.5 : 1}
                        strokeDasharray={isConnected ? "none" : "2 2"}
                      />
                      {isConnected && (
                        <text
                          x={(s.x + t.x) / 2}
                          y={(s.y + t.y) / 2 - 4}
                          fill="#93c5fd"
                          fontSize="9"
                          fontFamily="monospace"
                          textAnchor="middle"
                        >
                          {edge.label}
                        </text>
                      )}
                    </g>
                  );
                })}

                {/* Graph Nodes */}
                {nodes.map((node, idx) => {
                  const angle = (idx / nodes.length) * 2 * Math.PI;
                  const radius = 175;
                  const x = 350 + radius * Math.cos(angle);
                  const y = 230 + radius * Math.sin(angle);
                  const isSelected = selectedNode?.id === node.id;
                  const isFiltered = filteredNodes.some((fn) => fn.id === node.id);

                  return (
                    <g
                      key={node.id}
                      className={cn(
                        "cursor-pointer transition-all duration-200",
                        !isFiltered && "opacity-25"
                      )}
                      onClick={() => setSelectedNode(node)}
                    >
                      <circle
                        cx={x}
                        cy={y}
                        r={isSelected ? 16 : 11}
                        fill={node.color || "#3b82f6"}
                        stroke="#ffffff"
                        strokeWidth={isSelected ? 3 : 1.5}
                        className="transition-all"
                      />
                      <text
                        x={x}
                        y={y + (isSelected ? 26 : 22)}
                        textAnchor="middle"
                        fill={isSelected ? "#ffffff" : "#94a3b8"}
                        fontSize={isSelected ? "11" : "9"}
                        fontWeight={isSelected ? "bold" : "normal"}
                        fontFamily="monospace"
                      >
                        {node.label.length > 16 ? node.label.slice(0, 14) + ".." : node.label}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>

            <div className="text-[10px] text-slate-400 font-mono flex items-center justify-between border-t border-slate-800 pt-2 z-10">
              <span>Nodes: {nodes.length} | Relationships: {edges.length}</span>
              <span>Click any node to inspect ontology relationships</span>
            </div>
          </div>

          {/* Right Rail: Node Details & Connected Edges (4 cols) */}
          <div className="lg:col-span-4 bg-white rounded-lg border border-slate-200 p-5 shadow-subtle space-y-4">
            {selectedNode ? (
              <>
                <div className="pb-3 border-b border-slate-100">
                  <span className="text-[10px] font-mono uppercase font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                    Entity: {selectedNode.type}
                  </span>
                  <h3 className="text-base font-bold text-slate-900 mt-2">
                    {selectedNode.label}
                  </h3>
                  <span className="text-xs text-slate-400 font-mono">ID: {selectedNode.id}</span>
                </div>

                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 font-mono mb-2">
                    Active Graph Relations ({connectedEdges.length})
                  </h4>
                  <div className="space-y-2">
                    {connectedEdges.map((e) => {
                      const isSource = e.source === selectedNode.id;
                      const otherNodeId = isSource ? e.target : e.source;
                      const otherNode = nodes.find((n) => n.id === otherNodeId);

                      return (
                        <div
                          key={e.id}
                          className="p-2.5 rounded bg-slate-50 border border-slate-200 text-xs flex items-center justify-between"
                        >
                          <div>
                            <span className="text-slate-400 font-mono text-[10px] uppercase">
                              {isSource ? `→ ${e.label} →` : `← ${e.label} ←`}
                            </span>
                            <p className="font-semibold text-slate-800">{otherNode?.label}</p>
                          </div>
                          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white border border-slate-200 text-slate-600">
                            {otherNode?.type}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="p-3 bg-blue-50 rounded border border-blue-200 text-xs text-blue-900">
                  <span className="font-bold block mb-1">Ontology Use in Auto-Dispatch:</span>
                  <p className="text-blue-800 text-[11px] leading-relaxed">
                    When complaints mention "{selectedNode.label}", the classifier traverses these relational edges to identify responsible engineering divisions and emergency SOP protocols.
                  </p>
                </div>
              </>
            ) : (
              <div className="p-8 text-center text-xs text-slate-400">
                Select any node on the graph to inspect entity relations.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
