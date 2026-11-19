"use client";

import React from "react";
import Link from "next/link";
import { PublicHeader, PublicFooter } from "@/components/layout/PublicHeader";
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  BrainCircuit,
  Radio,
  Copy,
  TrendingUp,
  Share2,
  Users,
  CheckCircle2,
  Lock,
  BarChart3,
  Layers,
  MapPin,
  Clock,
  ChevronRight,
  Sliders,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      <PublicHeader />

      {/* HERO SECTION */}
      <section className="relative pt-16 pb-20 md:pt-24 md:pb-28 overflow-hidden bg-gradient-to-b from-white via-slate-50 to-slate-100/70 border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200/80 text-blue-700 text-xs font-semibold mb-6 shadow-subtle">
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              <span>Next-Generation Civic Intelligence & Decision Support</span>
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 leading-tight">
              Smarter Grievance Management.{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                Better Public Services.
              </span>
            </h1>

            <p className="mt-6 text-base sm:text-lg text-slate-600 leading-relaxed max-w-2xl mx-auto">
              An intelligent civic platform that transforms citizen complaints into actionable insights through predictive AI, semantic intelligence and transparent decision support.
            </p>

            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3.5">
              <Link
                href="/citizen/submit"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm shadow-card transition-all"
              >
                Submit a Grievance
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/admin"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded bg-white hover:bg-slate-50 border border-slate-200 text-slate-800 font-semibold text-sm shadow-subtle transition-all"
              >
                Explore Intelligence Command
              </Link>
            </div>

            <div className="mt-4 text-[11px] text-slate-400 font-mono">
              ★ Capstone Research Project & Live Demonstration Prototype
            </div>
          </div>

          {/* SOPHISTICATED DASHBOARD PREVIEW */}
          <div className="relative mx-auto max-w-5xl rounded-lg shadow-2xl border border-slate-300/80 bg-white overflow-hidden">
            {/* Window title bar */}
            <div className="bg-slate-900 px-4 py-2.5 flex items-center justify-between border-b border-slate-800 text-xs">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-red-500/80 inline-block" />
                <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block" />
                <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block" />
                <span className="ml-2 font-mono text-slate-400 text-[11px]">
                  CivicMind Apex Intelligence Command Center — [Live Feed]
                </span>
              </div>
              <div className="flex items-center gap-3 text-slate-400 font-mono text-[10px]">
                <span className="text-emerald-400 font-bold">● ENGINE ONLINE</span>
                <span>DEBERTA-V4.2</span>
              </div>
            </div>

            {/* Dashboard Content Mock */}
            <div className="p-6 bg-slate-50">
              {/* Mini KPI row */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5 mb-5">
                <div className="bg-white p-3.5 rounded border border-slate-200/80 shadow-xs">
                  <span className="text-[10px] font-mono uppercase text-slate-400 block">Total Active</span>
                  <span className="text-xl font-bold text-slate-900">1,127</span>
                  <span className="text-[10px] text-emerald-600 font-medium">↓ 14% vs avg</span>
                </div>
                <div className="bg-white p-3.5 rounded border border-slate-200/80 shadow-xs">
                  <span className="text-[10px] font-mono uppercase text-slate-400 block">Semantic Duplicates</span>
                  <span className="text-xl font-bold text-blue-600">342 (30.3%)</span>
                  <span className="text-[10px] text-blue-600 font-medium">48 Clusters Active</span>
                </div>
                <div className="bg-white p-3.5 rounded border border-slate-200/80 shadow-xs">
                  <span className="text-[10px] font-mono uppercase text-slate-400 block">Predicted SLA Breaches</span>
                  <span className="text-xl font-bold text-red-600">18 Flagged</span>
                  <span className="text-[10px] text-red-600 font-medium">Auto-Escalated</span>
                </div>
                <div className="bg-white p-3.5 rounded border border-slate-200/80 shadow-xs">
                  <span className="text-[10px] font-mono uppercase text-slate-400 block">Mean Resolution Time</span>
                  <span className="text-xl font-bold text-slate-900">3.4 Days</span>
                  <span className="text-[10px] text-slate-500 font-medium">SLA Target: 5.0d</span>
                </div>
              </div>

              {/* Mini Map + Cluster Feed row */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2 bg-[#0b132b] rounded border border-slate-800 p-4 text-white relative h-56 flex flex-col justify-between overflow-hidden">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold flex items-center gap-1.5 text-blue-300">
                      <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
                      Spatial Risk Radar & Cluster Centroids
                    </span>
                    <span className="text-[10px] font-mono bg-blue-900/60 text-blue-200 px-2 py-0.5 rounded border border-blue-700/50">
                      Zone 4 Hotspot Active
                    </span>
                  </div>

                  {/* SVG radar animation */}
                  <div className="relative flex-1 flex items-center justify-center my-2">
                    <div className="absolute w-28 h-28 rounded-full border border-blue-500/30 animate-ping" />
                    <div className="absolute w-20 h-20 rounded-full border border-red-500/40 bg-red-500/10" />
                    <div className="w-3 h-3 rounded-full bg-red-500 shadow-lg ring-4 ring-red-400/30" />
                    <div className="absolute bottom-2 right-4 text-right">
                      <p className="text-[11px] font-bold text-red-400">Ward 14 Feeder Line Burst</p>
                      <p className="text-[10px] text-slate-400 font-mono">18 Complaints • Risk: 92/100</p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono border-t border-slate-800 pt-2">
                    <span>GPS: 28.5244° N, 77.1558° E</span>
                    <span>WSSB Emergency Protocol Active</span>
                  </div>
                </div>

                <div className="bg-white rounded border border-slate-200/80 p-3.5 flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block mb-2 font-semibold">
                      Latest AI Classification
                    </span>
                    <h4 className="text-xs font-bold text-slate-900 leading-snug">
                      GRV-2026-8941: Feeder Line Rupture
                    </h4>
                    <p className="text-[11px] text-slate-500 mt-1 line-clamp-2">
                      Drinking water pipeline burst undermining pedestrian walkway...
                    </p>
                    <div className="mt-2.5 space-y-1.5 text-[11px]">
                      <div className="flex justify-between text-slate-600">
                        <span>Confidence:</span>
                        <span className="font-mono font-bold text-emerald-600">96.4%</span>
                      </div>
                      <div className="flex justify-between text-slate-600">
                        <span>Recommended Dept:</span>
                        <span className="font-semibold text-slate-800">WSSB</span>
                      </div>
                      <div className="flex justify-between text-slate-600">
                        <span>Duplicate Match:</span>
                        <span className="font-mono text-amber-600 font-bold">88% (Cluster #01)</span>
                      </div>
                    </div>
                  </div>

                  <Link
                    href="/admin/grievances/GRV-2026-8941"
                    className="mt-3 block text-center text-xs py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold rounded border border-blue-200 transition-colors"
                  >
                    Inspect Full AI Trace →
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* THREE APPLICATION EXPERIENCES */}
      <section className="py-16 bg-white border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-xs font-bold uppercase tracking-wider text-blue-600 font-mono mb-2">
              Role-Based Architecture
            </h2>
            <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
              Three Dedicated Operational Portals
            </h3>
            <p className="mt-3 text-sm text-slate-600">
              Tailored workspaces for citizens, department engineers, and apex municipal leaders.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Citizen Portal */}
            <div className="rounded-lg border border-slate-200/90 p-6 bg-slate-50/50 hover:shadow-card transition-all flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-md bg-blue-50 text-blue-600 border border-blue-200 flex items-center justify-center font-bold mb-4">
                  <Users className="w-5 h-5" />
                </div>
                <h4 className="text-base font-bold text-slate-900 mb-2">Citizen Portal</h4>
                <p className="text-xs text-slate-600 leading-relaxed mb-4">
                  Transparent, multi-step complaint filing with voice transcription, photo evidence upload, multilingual input (English, Hindi, Hinglish), live AI confidence review, duplicate alerts, and end-to-end lifecycle tracking.
                </p>
                <ul className="space-y-2 text-xs text-slate-600 mb-6 font-medium">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    AI Instant Category & SLA Prediction
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    Duplicate Warning & One-Click Upvoting
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    Direct Feedback & Citizen Verification
                  </li>
                </ul>
              </div>
              <Link
                href="/citizen/dashboard"
                className="inline-flex items-center justify-between text-xs font-bold text-blue-600 hover:text-blue-800 pt-3 border-t border-slate-200"
              >
                Access Citizen Workspace <ChevronRight className="w-4 h-4" />
              </Link>
            </div>

            {/* Officer Portal */}
            <div className="rounded-lg border border-slate-200/90 p-6 bg-slate-50/50 hover:shadow-card transition-all flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-md bg-amber-50 text-amber-700 border border-amber-200 flex items-center justify-center font-bold mb-4">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h4 className="text-base font-bold text-slate-900 mb-2">Department Officer Workspace</h4>
                <p className="text-xs text-slate-600 leading-relaxed mb-4">
                  Streamlined field and desk interface for engineers and sanitary inspectors. Intelligent workload triage, SLA countdown clocks, proof-of-work photo uploads, internal case notes, and assignment management.
                </p>
                <ul className="space-y-2 text-xs text-slate-600 mb-6 font-medium">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    Real-time SLA Countdown Clocks
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    Geofenced Ward Case Queue
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    Resolution Report Submission with Photo Proof
                  </li>
                </ul>
              </div>
              <Link
                href="/officer/dashboard"
                className="inline-flex items-center justify-between text-xs font-bold text-amber-700 hover:text-amber-900 pt-3 border-t border-slate-200"
              >
                Access Officer Workspace <ChevronRight className="w-4 h-4" />
              </Link>
            </div>

            {/* Administrator Intelligence */}
            <div className="rounded-lg border border-blue-200/90 p-6 bg-blue-50/30 hover:shadow-card transition-all flex flex-col justify-between ring-1 ring-blue-500/20">
              <div>
                <div className="w-10 h-10 rounded-md bg-blue-600 text-white flex items-center justify-center font-bold mb-4 shadow-subtle">
                  <BrainCircuit className="w-5 h-5" />
                </div>
                <h4 className="text-base font-bold text-slate-900 mb-2">Apex Intelligence Command</h4>
                <p className="text-xs text-slate-600 leading-relaxed mb-4">
                  Executive decision-support platform featuring GIS Early-Warning Radar, Cross-Encoder Duplicate Consolidation, Counterfactual Workload Simulator, SHAP Explainability, and Civic Knowledge Graph.
                </p>
                <ul className="space-y-2 text-xs text-slate-600 mb-6 font-medium">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />
                    Civic Issue Early-Warning Radar
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />
                    Counterfactual Workload Simulator
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />
                    Explainable AI (SHAP Feature Importance)
                  </li>
                </ul>
              </div>
              <Link
                href="/admin"
                className="inline-flex items-center justify-between text-xs font-bold text-blue-700 hover:text-blue-900 pt-3 border-t border-blue-200"
              >
                Access Intelligence Command <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* HOW AI GRIEVANCE INTELLIGENCE WORKS */}
      <section id="how-it-works" className="py-16 bg-slate-50 border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-xs font-bold uppercase tracking-wider text-blue-600 font-mono mb-2">
              End-to-End Pipeline
            </h2>
            <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
              How CivicMind AI Processes Grievances
            </h3>
            <p className="mt-3 text-sm text-slate-600">
              Five automated intelligence stages from ingestion to ground-truth verification.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="bg-white p-4 rounded-md border border-slate-200 shadow-xs">
              <span className="text-xs font-bold text-blue-600 font-mono block mb-2">01. INGESTION</span>
              <h4 className="text-sm font-bold text-slate-900 mb-1">Multilingual NLP</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Accepts voice, text, and images in English, Hindi, and Hinglish with zero information loss.
              </p>
            </div>

            <div className="bg-white p-4 rounded-md border border-slate-200 shadow-xs">
              <span className="text-xs font-bold text-blue-600 font-mono block mb-2">02. TRIAGE</span>
              <h4 className="text-sm font-bold text-slate-900 mb-1">Semantic Routing</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                DeBERTa-based classifier matches keywords & semantic context to target department with 94.8% accuracy.
              </p>
            </div>

            <div className="bg-white p-4 rounded-md border border-slate-200 shadow-xs">
              <span className="text-xs font-bold text-blue-600 font-mono block mb-2">03. DEDUPLICATION</span>
              <h4 className="text-sm font-bold text-slate-900 mb-1">Spatial & Text Radar</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Cross-Encoder compares complaint embeddings + GPS proximity to cluster duplicate reports.
              </p>
            </div>

            <div className="bg-white p-4 rounded-md border border-slate-200 shadow-xs">
              <span className="text-xs font-bold text-blue-600 font-mono block mb-2">04. PREDICTION</span>
              <h4 className="text-sm font-bold text-slate-900 mb-1">SLA Risk Forecasting</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Gradient boosted regressors project resolution duration and flag SLA breach risks before they happen.
              </p>
            </div>

            <div className="bg-white p-4 rounded-md border border-slate-200 shadow-xs">
              <span className="text-xs font-bold text-blue-600 font-mono block mb-2">05. VERIFICATION</span>
              <h4 className="text-sm font-bold text-slate-900 mb-1">Ground-Truth Audit</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Computer vision & citizen confirmation ensure complaints aren't prematurely closed without real action.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CORE CAPABILITIES GRID */}
      <section id="capabilities" className="py-16 bg-white border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-xs font-bold uppercase tracking-wider text-blue-600 font-mono mb-2">
              Intelligence Modules
            </h2>
            <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
              Enterprise Civic Intelligence Engine
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="p-5 rounded-md border border-slate-200 bg-slate-50/50">
              <div className="w-8 h-8 rounded bg-blue-100 text-blue-700 flex items-center justify-center mb-3">
                <Radio className="w-4 h-4" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 mb-1">Civic Issue Early-Warning Radar</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Geographic clustering identifies micro-hotspots (e.g. water pipeline bursts, recurring electrical faults) before systemic collapse occurs.
              </p>
            </div>

            <div className="p-5 rounded-md border border-slate-200 bg-slate-50/50">
              <div className="w-8 h-8 rounded bg-indigo-100 text-indigo-700 flex items-center justify-center mb-3">
                <Copy className="w-4 h-4" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 mb-1">Duplicate Intelligence Center</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Side-by-side complaint comparison with semantic similarity scores, GPS distance, and administrator merge approvals.
              </p>
            </div>

            <div className="p-5 rounded-md border border-slate-200 bg-slate-50/50">
              <div className="w-8 h-8 rounded bg-teal-100 text-teal-700 flex items-center justify-center mb-3">
                <TrendingUp className="w-4 h-4" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 mb-1">Predictive Analytics & SLA Forecaster</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Machine learning models forecast resolution duration, capacity bottlenecks, and SLA breach probabilities for proactive reallocation.
              </p>
            </div>

            <div className="p-5 rounded-md border border-slate-200 bg-slate-50/50">
              <div className="w-8 h-8 rounded bg-purple-100 text-purple-700 flex items-center justify-center mb-3">
                <Sparkles className="w-4 h-4" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 mb-1">Explainable AI (SHAP Attributions)</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Every categorization decision provides full transparency with lexical feature weights, sentiment traces, and decision audit logs.
              </p>
            </div>

            <div className="p-5 rounded-md border border-slate-200 bg-slate-50/50">
              <div className="w-8 h-8 rounded bg-sky-100 text-sky-700 flex items-center justify-center mb-3">
                <Share2 className="w-4 h-4" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 mb-1">Civic Entity Knowledge Graph</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Interactive relationship visualization linking departments, complaint categories, assets (valves, roads, transformers), and officers.
              </p>
            </div>

            <div className="p-5 rounded-md border border-slate-200 bg-slate-50/50">
              <div className="w-8 h-8 rounded bg-amber-100 text-amber-700 flex items-center justify-center mb-3">
                <Sliders className="w-4 h-4" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 mb-1">Counterfactual Workload Simulator</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                "What-if" scenario modeling to test adding officers, rebalancing department quotas, and testing SLA threshold adjustments before policy changes.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* STATISTICS */}
      <section className="py-14 bg-navy-950 text-white border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-3xl sm:text-4xl font-extrabold text-blue-400 font-mono">
                94.8%
              </div>
              <div className="text-xs text-slate-400 mt-1 uppercase tracking-wider font-semibold">
                Classification Accuracy
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Macro F1: 0.939</div>
            </div>

            <div>
              <div className="text-3xl sm:text-4xl font-extrabold text-emerald-400 font-mono">
                92.4%
              </div>
              <div className="text-xs text-slate-400 mt-1 uppercase tracking-wider font-semibold">
                Duplicate Precision@K
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Cross-Encoder SBERT</div>
            </div>

            <div>
              <div className="text-3xl sm:text-4xl font-extrabold text-amber-400 font-mono">
                0.68 Days
              </div>
              <div className="text-xs text-slate-400 mt-1 uppercase tracking-wider font-semibold">
                Mean Absolute Error (MAE)
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">SLA Duration Regressor</div>
            </div>

            <div>
              <div className="text-3xl sm:text-4xl font-extrabold text-purple-400 font-mono">
                142.5K
              </div>
              <div className="text-xs text-slate-400 mt-1 uppercase tracking-wider font-semibold">
                Research Benchmark Records
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Multilingual Public Corpus</div>
            </div>
          </div>
        </div>
      </section>

      {/* TRANSPARENCY & ETHICAL AI BANNER */}
      <section id="transparency" className="py-16 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-slate-50 rounded-lg border border-slate-200 p-8 flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="space-y-2 max-w-2xl">
              <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                <ShieldCheck className="w-3.5 h-3.5" />
                Ethical AI & Transparent Governance
              </div>
              <h3 className="text-xl font-bold text-slate-900">
                Decision Support, Not Opaque Automation
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                CivicMind AI adheres to human-in-the-loop principles. All merge operations, reassignments, and closures require human officer or administrator verification. No citizen complaints are automatically dismissed or merged without human review.
              </p>
            </div>

            <div className="flex gap-3">
              <Link
                href="/admin/explainability"
                className="px-4 py-2 bg-white hover:bg-slate-100 border border-slate-200 text-slate-800 text-xs font-semibold rounded shadow-subtle transition-colors"
              >
                Inspect XAI Engine
              </Link>
              <Link
                href="/login"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded shadow-subtle transition-colors"
              >
                Try Demo Accounts
              </Link>
            </div>
          </div>
        </div>
      </section>

      <PublicFooter />
    </div>
  );
}
