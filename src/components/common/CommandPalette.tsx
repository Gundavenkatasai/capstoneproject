import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import {
  Search,
  LayoutDashboard,
  FileText,
  Copy,
  Radio,
  TrendingUp,
  BrainCircuit,
  Share2,
  CheckSquare,
  Sliders,
  Database,
  UserCheck,
  X,
} from "lucide-react";

interface CommandItem {
  id: string;
  title: string;
  category: "Navigation" | "AI Research" | "Role Switcher";
  icon: React.ComponentType<{ className?: string }>;
  action: () => void;
  badge?: string;
}

export function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const navigate = useNavigate();
  const { switchRole } = useAuthStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
      if (e.key === "Escape" && isOpen) {
        setIsOpen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  const commands: CommandItem[] = [
    {
      id: "admin-dash",
      title: "Admin Grievance Intelligence Command Center",
      category: "Navigation",
      icon: LayoutDashboard,
      action: () => navigate("/admin"),
    },
    {
      id: "admin-all",
      title: "All Grievances & Priority Queue",
      category: "Navigation",
      icon: FileText,
      action: () => navigate("/admin/grievances"),
    },
    {
      id: "admin-dup",
      title: "Duplicate Intelligence & Cluster Merge",
      category: "AI Research",
      icon: Copy,
      badge: "AI Semantic",
      action: () => navigate("/admin/duplicates"),
    },
    {
      id: "admin-radar",
      title: "Civic Issue Early-Warning Radar",
      category: "AI Research",
      icon: Radio,
      badge: "Spatial AI",
      action: () => navigate("/admin/early-warning"),
    },
    {
      id: "admin-pred",
      title: "Predictive Analytics & SLA Breach Forecaster",
      category: "AI Research",
      icon: TrendingUp,
      action: () => navigate("/admin/predictions"),
    },
    {
      id: "admin-xai",
      title: "Explainable AI (SHAP & Routing Attribution)",
      category: "AI Research",
      icon: BrainCircuit,
      badge: "XAI",
      action: () => navigate("/admin/explainability"),
    },
    {
      id: "admin-kg",
      title: "Civic Entity Knowledge Graph",
      category: "AI Research",
      icon: Share2,
      action: () => navigate("/admin/knowledge-graph"),
    },
    {
      id: "admin-verify",
      title: "Resolution Quality & Ground-Truth Verification",
      category: "Navigation",
      icon: CheckSquare,
      action: () => navigate("/admin/resolution-verification"),
    },
    {
      id: "admin-sim",
      title: "Counterfactual Workload Simulator",
      category: "AI Research",
      icon: Sliders,
      badge: "What-If",
      action: () => navigate("/admin/simulator"),
    },
    {
      id: "admin-models",
      title: "Model Performance & Benchmarks",
      category: "AI Research",
      icon: Database,
      action: () => navigate("/admin/models"),
    },
    {
      id: "role-citizen",
      title: "Switch to Citizen Experience (Submit & Track)",
      category: "Role Switcher",
      icon: UserCheck,
      action: () => {
        switchRole("citizen");
        navigate("/citizen/dashboard");
      },
    },
    {
      id: "role-officer",
      title: "Switch to Department Officer Experience",
      category: "Role Switcher",
      icon: UserCheck,
      action: () => {
        switchRole("officer");
        navigate("/officer/dashboard");
      },
    },
    {
      id: "role-admin",
      title: "Switch to Administrator Intelligence Experience",
      category: "Role Switcher",
      icon: UserCheck,
      action: () => {
        switchRole("admin");
        navigate("/admin");
      },
    },
  ];

  const filtered = query
    ? commands.filter((c) => c.title.toLowerCase().includes(query.toLowerCase()) || c.category.toLowerCase().includes(query.toLowerCase()))
    : commands;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-slate-900/40 backdrop-blur-xs">
      <div className="relative w-full max-w-xl bg-white rounded-lg shadow-elevated border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-100">
        <div className="flex items-center px-4 border-b border-slate-100">
          <Search className="w-4 h-4 text-slate-400 mr-3" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a command, module, or jump to route..."
            className="w-full py-3.5 text-sm bg-transparent border-0 focus:outline-none text-slate-900 placeholder:text-slate-400 font-medium"
          />
          <button
            onClick={() => setIsOpen(false)}
            className="p-1 rounded text-slate-400 hover:text-slate-600"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filtered.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-400">
              No matching modules or commands found.
            </div>
          ) : (
            filtered.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    item.action();
                    setIsOpen(false);
                  }}
                  className="w-full flex items-center justify-between px-3 py-2.5 rounded hover:bg-slate-50 text-left transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded bg-slate-100 group-hover:bg-blue-50 group-hover:text-blue-600 text-slate-600 flex items-center justify-center transition-colors">
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="text-xs font-semibold text-slate-800 block">
                        {item.title}
                      </span>
                      <span className="text-[10px] text-slate-400 uppercase font-mono">
                        {item.category}
                      </span>
                    </div>
                  </div>
                  {item.badge && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-50 text-blue-700 font-semibold border border-blue-200">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })
          )}
        </div>

        <div className="px-4 py-2 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400 font-mono">
          <span>Navigation Quick Switcher</span>
          <span>Press ESC to close</span>
        </div>
      </div>
    </div>
  );
}
