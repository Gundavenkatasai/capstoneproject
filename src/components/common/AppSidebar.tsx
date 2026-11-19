"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";
import { UserRole } from "@/types";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  FileText,
  AlertTriangle,
  Copy,
  Radio,
  TrendingUp,
  BrainCircuit,
  Share2,
  CheckSquare,
  Users,
  Sliders,
  Database,
  FlaskConical,
  ScrollText,
  Settings,
  PlusCircle,
  Clock,
  Shield,
  Award,
  User,
  ChevronDown,
  Sparkles,
  ExternalLink,
} from "lucide-react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

export function AppSidebar({ className }: { className?: string }) {
  const pathname = usePathname();
  const { user, role, switchRole } = useAuthStore();

  const adminSections: NavSection[] = [
    {
      title: "OVERVIEW",
      items: [
        { label: "Intelligence Dashboard", href: "/admin", icon: LayoutDashboard },
        { label: "Live Monitoring", href: "/admin#live", icon: Radio, badge: "Live" },
      ],
    },
    {
      title: "GRIEVANCE MANAGEMENT",
      items: [
        { label: "All Grievances", href: "/admin/grievances", icon: FileText },
        { label: "Priority Queue", href: "/admin/grievances?filter=priority", icon: AlertTriangle },
        { label: "Duplicate Intelligence", href: "/admin/duplicates", icon: Copy, badge: "AI" },
        { label: "Escalations", href: "/admin/grievances?status=escalated", icon: AlertTriangle },
        { label: "Resolution Verification", href: "/admin/resolution-verification", icon: CheckSquare },
      ],
    },
    {
      title: "AI INTELLIGENCE",
      items: [
        { label: "Classification Intelligence", href: "/admin/models", icon: BrainCircuit },
        { label: "Predictive Analytics", href: "/admin/predictions", icon: TrendingUp },
        { label: "Civic Early-Warning Radar", href: "/admin/early-warning", icon: Radio, badge: "GIS" },
        { label: "Knowledge Graph", href: "/admin/knowledge-graph", icon: Share2 },
        { label: "Explainable AI (SHAP)", href: "/admin/explainability", icon: Sparkles },
      ],
    },
    {
      title: "OPERATIONS",
      items: [
        { label: "Workload Management", href: "/admin/workload", icon: Users },
        { label: "Workload Simulator", href: "/admin/simulator", icon: Sliders, badge: "Sim" },
      ],
    },
    {
      title: "RESEARCH & SYSTEM",
      items: [
        { label: "Model Performance", href: "/admin/models", icon: Database },
        { label: "Dataset Explorer", href: "/admin/datasets", icon: Database },
        { label: "Experiment Results", href: "/admin/experiments", icon: FlaskConical },
        { label: "Audit Logs", href: "/admin/audit-logs", icon: ScrollText },
        { label: "System Settings", href: "/admin/settings", icon: Settings },
      ],
    },
  ];

  const officerSections: NavSection[] = [
    {
      title: "MY DUTY OPERATIONS",
      items: [
        { label: "Officer Dashboard", href: "/officer/dashboard", icon: LayoutDashboard },
        { label: "Assigned Grievances", href: "/officer/assigned", icon: FileText, badge: "Active" },
        { label: "Escalation Queue", href: "/officer/escalations", icon: AlertTriangle },
        { label: "Performance & SLA", href: "/officer/performance", icon: Award },
        { label: "Duty Ward & Profile", href: "/officer/profile", icon: User },
      ],
    },
  ];

  const citizenSections: NavSection[] = [
    {
      title: "CITIZEN SERVICES",
      items: [
        { label: "Citizen Dashboard", href: "/citizen/dashboard", icon: LayoutDashboard },
        { label: "Submit Grievance", href: "/citizen/submit", icon: PlusCircle, badge: "AI Assist" },
        { label: "My Grievances", href: "/citizen/grievances", icon: FileText },
        { label: "Appeals & Reviews", href: "/citizen/appeals", icon: CheckSquare },
        { label: "Profile & History", href: "/citizen/profile", icon: User },
      ],
    },
  ];

  const currentSections =
    role === "admin"
      ? adminSections
      : role === "officer"
      ? officerSections
      : citizenSections;

  return (
    <aside
      className={cn(
        "w-64 bg-navy-950 text-slate-300 flex flex-col flex-shrink-0 h-screen sticky top-0 border-r border-slate-800 select-none z-30",
        className
      )}
    >
      {/* Brand Header */}
      <div className="h-16 px-5 border-b border-slate-800/80 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white font-bold text-sm shadow-subtle">
            CM
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-sm tracking-tight text-white group-hover:text-blue-300 transition-colors">
                CivicMind AI
              </span>
              <span className="text-[10px] font-mono px-1 py-0.2 rounded bg-blue-900/60 text-blue-300 border border-blue-700/50">
                PRO
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono tracking-wider">
              {role.toUpperCase()} PORTAL
            </p>
          </div>
        </Link>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {currentSections.map((section, sIdx) => (
          <div key={sIdx}>
            <h3 className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2 font-mono">
              {section.title}
            </h3>
            <div className="space-y-0.5">
              {section.items.map((item, iIdx) => {
                const Icon = item.icon;
                const isActive =
                  pathname === item.href ||
                  (item.href !== "/admin" &&
                    item.href !== "/officer/dashboard" &&
                    item.href !== "/citizen/dashboard" &&
                    pathname.startsWith(item.href.split("?")[0]));

                return (
                  <Link
                    key={iIdx}
                    href={item.href}
                    className={cn(
                      "flex items-center justify-between px-3 py-2 rounded text-xs font-medium transition-all group",
                      isActive
                        ? "bg-blue-600 text-white shadow-subtle"
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/80"
                    )}
                  >
                    <div className="flex items-center gap-2.5 truncate">
                      <Icon
                        className={cn(
                          "w-4 h-4 flex-shrink-0 transition-colors",
                          isActive
                            ? "text-white"
                            : "text-slate-500 group-hover:text-slate-300"
                        )}
                      />
                      <span className="truncate">{item.label}</span>
                    </div>

                    {item.badge && (
                      <span
                        className={cn(
                          "text-[9px] font-mono font-semibold px-1.5 py-0.5 rounded",
                          isActive
                            ? "bg-blue-700 text-white"
                            : "bg-slate-800 text-slate-300 border border-slate-700/70"
                        )}
                      >
                        {item.badge}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Role Switcher Demo Bar at bottom */}
      <div className="p-3 border-t border-slate-800 bg-navy-900/60">
        <div className="text-[10px] uppercase font-mono text-slate-400 mb-2 flex items-center justify-between">
          <span>Role Switcher (Demo)</span>
          <span className="text-emerald-400 font-bold">● Active</span>
        </div>
        <div className="grid grid-cols-3 gap-1">
          {(["citizen", "officer", "admin"] as UserRole[]).map((r) => (
            <button
              key={r}
              onClick={() => switchRole(r)}
              className={cn(
                "py-1.5 px-2 rounded text-[10px] font-semibold uppercase tracking-wider transition-colors",
                role === r
                  ? "bg-blue-600 text-white shadow-xs"
                  : "bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-800"
              )}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* User Footer Card */}
      <div className="p-3 border-t border-slate-800/80 bg-navy-950 flex items-center justify-between">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 overflow-hidden flex-shrink-0">
            {user?.avatar ? (
              <img src={user.avatar} alt={user.name} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-xs font-bold text-white">
                {user?.name?.charAt(0) || "U"}
              </div>
            )}
          </div>
          <div className="min-w-0">
            <p className="text-xs font-semibold text-white truncate">{user?.name}</p>
            <p className="text-[10px] text-slate-400 truncate">{user?.ward || user?.department}</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
