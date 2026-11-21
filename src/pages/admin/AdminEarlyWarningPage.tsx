import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { earlyWarningService } from "@/services/earlyWarningService";
import { Hotspot } from "@/types";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { MapView } from "@/components/maps/MapView";
import { ChartCard } from "@/components/common/ChartCard";
import { FilterDropdown } from "@/components/common/SearchInput";
import { LoadingSkeleton } from "@/components/common/EmptyState";
import { formatDate } from "@/lib/utils";
import {
  Radio,
  AlertTriangle,
  TrendingUp,
  MapPin,
  ShieldCheck,
  CheckCircle2,
  Wrench,
  Clock,
  Sparkles,
  ArrowRight,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { cn } from "@/lib/utils";

export default function CivicEarlyWarningRadarPage() {
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [selectedHotspot, setSelectedHotspot] = useState<Hotspot | null>(null);
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [riskFilter, setRiskFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await earlyWarningService.getHotspots(categoryFilter, riskFilter);
      setHotspots(data);
      if (data.length > 0 && !selectedHotspot) {
        setSelectedHotspot(data[0]);
      }
      setLoading(false);
    }
    load();
  }, [categoryFilter, riskFilter]);

  const handleAcknowledge = async () => {
    if (!selectedHotspot) return;
    const updated = await earlyWarningService.acknowledgeHotspot(
      selectedHotspot.id,
      "Emergency inspection dispatched by Apex Control"
    );
    if (updated) {
      setSelectedHotspot(updated);
      setActionNotice(`Intervention team dispatched for ${updated.title}`);
      setTimeout(() => setActionNotice(null), 4000);
    }
  };

  const velocityChartData = selectedHotspot?.historicalVelocity
    ? selectedHotspot.historicalVelocity.map((count, idx) => ({
        day: `Day ${idx + 1}`,
        complaints: count,
      }))
    : [
        { day: "Day 1", complaints: 2 },
        { day: "Day 2", complaints: 4 },
        { day: "Day 3", complaints: 7 },
        { day: "Day 4", complaints: 11 },
        { day: "Day 5", complaints: 18 },
      ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Civic Issue Early-Warning Radar"
        subtitle="Autonomous spatial density modeling that detects emerging infrastructural failures and municipal service anomalies before citizen escalations multiply."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Civic Early-Warning Radar", active: true },
        ]}
        badge="Spatial AI v3.8"
      />

      {actionNotice && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-md font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          {actionNotice}
        </div>
      )}

      {/* Filter and Simulator Notice */}
      <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-subtle flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <FilterDropdown
            label="Category"
            value={categoryFilter}
            onChange={setCategoryFilter}
            options={[
              { label: "All Categories", value: "all" },
              { label: "Water & Sewerage", value: "water" },
              { label: "Roads (PWD)", value: "roads" },
              { label: "Solid Waste", value: "waste" },
              { label: "Electricity", value: "electricity" },
              { label: "Public Health", value: "health" },
            ]}
          />
          <FilterDropdown
            label="Risk Level"
            value={riskFilter}
            onChange={setRiskFilter}
            options={[
              { label: "All Risk Tiers", value: "all" },
              { label: "Critical", value: "critical" },
              { label: "High", value: "high" },
              { label: "Medium", value: "medium" },
            ]}
          />
        </div>

        <span className="text-[11px] font-mono text-slate-400 bg-slate-50 px-2 py-1 rounded border border-slate-200">
          ★ Simulated demonstration GIS feeds calibrated to metro coordinates
        </span>
      </div>

      {loading ? (
        <LoadingSkeleton count={3} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Main Map Canvas (7 cols) */}
          <div className="lg:col-span-7 space-y-4">
            <div className="bg-white rounded-lg border border-slate-200 p-2 shadow-subtle">
              <MapView
                hotspots={hotspots}
                selectedId={selectedHotspot?.id}
                onHotspotClick={(h) => setSelectedHotspot(h)}
                className="h-[460px] w-full"
              />
            </div>

            {/* Hotspots Quick Switcher */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              {hotspots.map((h) => {
                const isSelected = selectedHotspot?.id === h.id;
                return (
                  <button
                    key={h.id}
                    onClick={() => setSelectedHotspot(h)}
                    className={cn(
                      "p-3 rounded border text-left text-xs transition-all shadow-subtle",
                      isSelected
                        ? "bg-white border-blue-500 ring-2 ring-blue-100 font-semibold"
                        : "bg-white border-slate-200 hover:bg-slate-50 text-slate-700"
                    )}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono text-[10px] text-slate-500">{h.ward.split(" ")[0]}</span>
                      <span
                        className={cn(
                          "px-1.5 py-0.2 rounded text-[9px] font-bold uppercase",
                          h.riskLevel === "critical"
                            ? "bg-red-50 text-red-700"
                            : h.riskLevel === "high"
                            ? "bg-amber-50 text-amber-700"
                            : "bg-blue-50 text-blue-700"
                        )}
                      >
                        {h.riskLevel}
                      </span>
                    </div>
                    <p className="font-bold text-slate-900 truncate">{h.title}</p>
                    <p className="text-[11px] text-slate-400 mt-0.5">{h.complaintCount} incidents</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right Inspection & Alert Panel (5 cols) */}
          <div className="lg:col-span-5 space-y-4">
            {selectedHotspot && (
              <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-subtle space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <span className="text-[10px] uppercase font-mono font-bold tracking-wider text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                    Hotspot Dossier: {selectedHotspot.id}
                  </span>
                  <span
                    className={cn(
                      "text-xs font-mono font-bold px-2 py-0.5 rounded border uppercase",
                      selectedHotspot.riskLevel === "critical"
                        ? "bg-red-50 text-red-700 border-red-200"
                        : "bg-amber-50 text-amber-700 border-amber-200"
                    )}
                  >
                    Risk Score: {selectedHotspot.riskScore}/100
                  </span>
                </div>

                <div>
                  <h3 className="text-base font-bold text-slate-900 leading-snug">
                    {selectedHotspot.title}
                  </h3>
                  <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                    {selectedHotspot.summary}
                  </p>
                </div>

                {/* Key Metrics Grid */}
                <div className="grid grid-cols-2 gap-3 text-xs bg-slate-50 p-3.5 rounded border border-slate-200/80">
                  <div>
                    <span className="text-slate-400 font-mono text-[10px] uppercase block">Related Reports</span>
                    <span className="font-bold text-slate-900 mt-0.5 block">
                      {selectedHotspot.complaintCount} Complaints
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 font-mono text-[10px] uppercase block">Jurisdiction</span>
                    <span className="font-bold text-slate-900 mt-0.5 block">
                      {selectedHotspot.zone} ({selectedHotspot.ward})
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 font-mono text-[10px] uppercase block">Trend Velocity</span>
                    <span className="font-bold text-red-600 mt-0.5 block capitalize">
                      ↑ {selectedHotspot.trend} (+240% / 48h)
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 font-mono text-[10px] uppercase block">Radiation Radius</span>
                    <span className="font-bold text-slate-900 mt-0.5 block font-mono">
                      ~{selectedHotspot.radiusMeters}m
                    </span>
                  </div>
                </div>

                {/* Recommended Operational Action */}
                <div className="p-3.5 bg-amber-50/80 rounded border border-amber-200/80 text-xs text-amber-900 space-y-1">
                  <span className="font-bold block">Recommended Executive Action:</span>
                  <p className="text-amber-800 leading-relaxed">
                    {selectedHotspot.recommendedAction}
                  </p>
                </div>

                {/* Historical Velocity Mini-Chart */}
                <div>
                  <span className="text-xs font-bold text-slate-700 block mb-2 font-mono uppercase">
                    Incident Inundation Velocity (Last 6 Time Slices)
                  </span>
                  <div className="h-36 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={velocityChartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis dataKey="day" stroke="#64748b" fontSize={10} />
                        <YAxis stroke="#64748b" fontSize={10} />
                        <Tooltip />
                        <Line
                          type="monotone"
                          dataKey="complaints"
                          name="Complaints"
                          stroke="#ef4444"
                          strokeWidth={2.5}
                          dot={{ r: 4 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                  <Link
                    to={`/admin/grievances?ward=${encodeURIComponent(selectedHotspot.ward)}`}
                    className="text-xs text-blue-600 hover:text-blue-800 font-semibold"
                  >
                    View All {selectedHotspot.complaintCount} Cases →
                  </Link>

                  <button
                    onClick={handleAcknowledge}
                    className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold shadow-subtle transition-colors"
                  >
                    Dispatch Inspection Task Force
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
