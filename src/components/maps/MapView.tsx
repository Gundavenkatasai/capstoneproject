"use client";

import React, { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { Hotspot, Grievance } from "@/types";
import { AlertCircle, MapPin } from "lucide-react";

interface MapViewProps {
  hotspots?: Hotspot[];
  grievances?: Grievance[];
  center?: [number, number];
  zoom?: number;
  onHotspotClick?: (hotspot: Hotspot) => void;
  onGrievanceClick?: (grievance: Grievance) => void;
  selectedId?: string;
  className?: string;
}

// Internal dynamic wrapper to avoid SSR Leaflet "window is not defined" issues
export function MapView({
  hotspots = [],
  grievances = [],
  center = [28.56, 77.16],
  zoom = 12,
  onHotspotClick,
  onGrievanceClick,
  selectedId,
  className = "h-[450px] w-full",
}: MapViewProps) {
  const [mounted, setMounted] = useState(false);
  const [activeTab, setActiveTab] = useState<"map" | "grid">("map");

  useEffect(() => {
    setMounted(true);
  }, []);

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "critical":
        return "#EF4444";
      case "high":
        return "#F59E0B";
      case "medium":
        return "#3B82F6";
      default:
        return "#10B981";
    }
  };

  if (!mounted) {
    return (
      <div className={`bg-slate-100 rounded-md border border-slate-200 flex flex-col items-center justify-center text-slate-400 p-6 ${className}`}>
        <MapPin className="w-8 h-8 text-slate-400 animate-bounce mb-2" />
        <span className="text-xs font-medium">Initializing Geographic Intelligence Layer...</span>
      </div>
    );
  }

  return (
    <div className={`relative rounded-md border border-slate-200 overflow-hidden bg-slate-900 ${className}`}>
      {/* Map Header Overlay */}
      <div className="absolute top-3 left-3 z-20 flex items-center gap-2 bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded border border-slate-700/80 text-white text-xs shadow-md">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
        <span className="font-semibold tracking-wide">Live Civic GIS Radar</span>
        <span className="text-slate-400 font-mono text-[10px]">({hotspots.length} Clusters Active)</span>
      </div>

      {/* Map Legend */}
      <div className="absolute bottom-3 left-3 z-20 bg-slate-900/90 backdrop-blur-md px-3 py-2 rounded border border-slate-700/80 text-white text-[11px] shadow-md flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500" />
          <span className="text-slate-300">Critical Hotspot</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
          <span className="text-slate-300">High Risk</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
          <span className="text-slate-300">Monitored</span>
        </div>
      </div>

      {/* Interactive SVG GIS Projection Canvas */}
      <div className="w-full h-full relative bg-[#0b132b] overflow-hidden">
        {/* Subtle coordinate grid lines */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:3.5rem_3.5rem] opacity-35" />

        {/* Metro Geographic Zone Overlays */}
        <svg className="w-full h-full absolute inset-0 pointer-events-auto" viewBox="0 0 800 500" preserveAspectRatio="none">
          {/* Arterial Road Network Vectors */}
          <path d="M 50,220 Q 300,200 450,250 T 780,280" fill="none" stroke="#1e3a8a" strokeWidth="4" strokeOpacity="0.4" />
          <path d="M 200,50 L 320,480" fill="none" stroke="#1e3a8a" strokeWidth="3" strokeOpacity="0.3" />
          <path d="M 120,400 Q 400,320 700,420" fill="none" stroke="#1e3a8a" strokeWidth="2.5" strokeOpacity="0.3" />
          <path d="M 450,50 Q 520,250 600,480" fill="none" stroke="#1e3a8a" strokeWidth="3" strokeOpacity="0.3" />

          {/* Render Hotspot Radiation Radii & Centroids */}
          {hotspots.map((h, idx) => {
            // Project lat/lng to 800x500 viewport
            // Delhi bounds: lat 28.50 to 28.66, lng 77.05 to 77.30
            const x = Math.min(750, Math.max(60, ((h.lng - 77.04) / 0.28) * 700 + 50));
            const y = Math.min(450, Math.max(50, 480 - ((h.lat - 28.5) / 0.17) * 420));
            const isSelected = selectedId === h.id;
            const color = getRiskColor(h.riskLevel);

            return (
              <g
                key={h.id}
                className="cursor-pointer transition-transform duration-200 hover:scale-105"
                onClick={() => onHotspotClick?.(h)}
              >
                {/* Radiation circle */}
                <circle
                  cx={x}
                  cy={y}
                  r={isSelected ? 48 : 34}
                  fill={color}
                  fillOpacity={isSelected ? 0.35 : 0.18}
                  stroke={color}
                  strokeWidth={isSelected ? 2.5 : 1.5}
                  strokeDasharray={isSelected ? "4 2" : "none"}
                >
                  <animate
                    attributeName="r"
                    values={isSelected ? "44;52;44" : "30;36;30"}
                    dur="3s"
                    repeatCount="indefinite"
                  />
                </circle>

                {/* Hotspot Center Beacon */}
                <circle cx={x} cy={y} r="8" fill={color} stroke="#ffffff" strokeWidth="2" />

                {/* Label Pin Badge */}
                <rect
                  x={x - 45}
                  y={y - 32}
                  width="90"
                  height="20"
                  rx="4"
                  fill="#0f172a"
                  stroke={isSelected ? "#60a5fa" : "#334155"}
                  strokeWidth="1.2"
                />
                <text
                  x={x}
                  y={y - 18}
                  textAnchor="middle"
                  fill="#ffffff"
                  fontSize="10"
                  fontWeight="600"
                  fontFamily="monospace"
                >
                  {h.ward.split(" ")[0]} ({h.complaintCount})
                </text>
              </g>
            );
          })}

          {/* Render individual grievance markers if present */}
          {grievances.map((g) => {
            const gx = Math.min(760, Math.max(50, ((g.location.lng - 77.04) / 0.28) * 700 + 50));
            const gy = Math.min(460, Math.max(40, 480 - ((g.location.lat - 28.5) / 0.17) * 420));
            const isSelected = selectedId === g.id;

            return (
              <g
                key={g.id}
                className="cursor-pointer"
                onClick={() => onGrievanceClick?.(g)}
              >
                <circle
                  cx={gx}
                  cy={gy}
                  r={isSelected ? 6 : 4}
                  fill={isSelected ? "#60a5fa" : "#94a3b8"}
                  stroke="#ffffff"
                  strokeWidth="1.5"
                />
              </g>
            );
          })}
        </svg>

        {/* Hotspot Floating Tooltip in bottom right */}
        {selectedId && (
          <div className="absolute top-3 right-3 z-20 max-w-xs bg-slate-900/95 backdrop-blur-md p-3.5 rounded border border-blue-500/50 text-white text-xs shadow-elevated">
            <span className="text-[10px] uppercase font-mono text-blue-400 block mb-1">
              Active Zone Inspection
            </span>
            <p className="font-semibold text-slate-100">
              {hotspots.find((h) => h.id === selectedId)?.title || "Selected Hotspot"}
            </p>
            <p className="text-slate-300 text-[11px] mt-1 leading-snug">
              {hotspots.find((h) => h.id === selectedId)?.summary}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
