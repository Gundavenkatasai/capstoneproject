import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, ShieldCheck, Sparkles } from "lucide-react";

export function PublicHeader() {
  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-subtle">
            CM
          </div>
          <div>
            <span className="font-bold text-base tracking-tight text-slate-900">
              CivicMind AI
            </span>
            <span className="text-[10px] text-blue-600 font-mono block -mt-1 font-medium">
              Grievance Intelligence Platform
            </span>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-6 text-xs font-semibold text-slate-600">
          <a href="#about" className="hover:text-blue-600 transition-colors">
            Architecture
          </a>
          <a href="#how-it-works" className="hover:text-blue-600 transition-colors">
            AI Pipeline
          </a>
          <a href="#capabilities" className="hover:text-blue-600 transition-colors">
            Capabilities
          </a>
          <a href="#predictive" className="hover:text-blue-600 transition-colors">
            Predictive Models
          </a>
          <a href="#transparency" className="hover:text-blue-600 transition-colors">
            Safety & XAI
          </a>
        </nav>

        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="text-xs font-semibold text-slate-700 hover:text-slate-900 px-3 py-1.5 rounded hover:bg-slate-100 transition-colors"
          >
            Sign In
          </Link>
          <Link
            to="/citizen/submit"
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-subtle transition-colors"
          >
            File Grievance
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </header>
  );
}

export function PublicFooter() {
  return (
    <footer className="bg-navy-950 text-slate-400 border-t border-slate-800 text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded bg-blue-600 text-white flex items-center justify-center font-bold text-xs">
                CM
              </div>
              <span className="font-bold text-sm text-white">CivicMind AI</span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed">
              AI-Powered Citizen Grievance Intelligence and Resolution Prediction Platform. Advanced decision support for public administration.
            </p>
            <div className="text-[11px] text-slate-500 font-mono">
              Research Prototype & Demonstration Platform. Not an official government agency endorsement.
            </div>
          </div>

          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-3 font-mono">
              Platform Portals
            </h4>
            <ul className="space-y-2">
              <li>
                <Link to="/citizen/dashboard" className="hover:text-white transition-colors">
                  Citizen Services Portal
                </Link>
              </li>
              <li>
                <Link to="/officer/dashboard" className="hover:text-white transition-colors">
                  Department Officer Workspace
                </Link>
              </li>
              <li>
                <Link to="/admin" className="hover:text-white transition-colors">
                  Apex Intelligence Command Center
                </Link>
              </li>
              <li>
                <Link to="/citizen/submit" className="hover:text-white transition-colors">
                  AI Complaint Submission Wizard
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-3 font-mono">
              AI Modules
            </h4>
            <ul className="space-y-2">
              <li>
                <Link to="/admin/early-warning" className="hover:text-white transition-colors">
                  Civic Early-Warning Radar
                </Link>
              </li>
              <li>
                <Link to="/admin/duplicates" className="hover:text-white transition-colors">
                  Duplicate Intelligence Center
                </Link>
              </li>
              <li>
                <Link to="/admin/predictions" className="hover:text-white transition-colors">
                  SLA Risk & Resolution Predictor
                </Link>
              </li>
              <li>
                <Link to="/admin/explainability" className="hover:text-white transition-colors">
                  Explainable AI (SHAP & Trace)
                </Link>
              </li>
              <li>
                <Link to="/admin/knowledge-graph" className="hover:text-white transition-colors">
                  Civic Entity Knowledge Graph
                </Link>
              </li>
              <li>
                <Link to="/admin/simulator" className="hover:text-white transition-colors">
                  Counterfactual Workload Simulator
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-3 font-mono">
              Research & Compliance
            </h4>
            <ul className="space-y-2">
              <li>
                <Link to="/admin/models" className="hover:text-white transition-colors">
                  Model Performance & Benchmarks
                </Link>
              </li>
              <li>
                <Link to="/admin/datasets" className="hover:text-white transition-colors">
                  Dataset Explorer & Augmentation
                </Link>
              </li>
              <li>
                <Link to="/admin/audit-logs" className="hover:text-white transition-colors">
                  Audit Logs & Traceability
                </Link>
              </li>
              <li>
                <span className="text-slate-500">ISO 27001 & OpenGov Standards</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-slate-500">
          <p>© 2026 CivicMind AI Research Initiative. All rights reserved.</p>
          <div className="flex items-center gap-4">
            <span className="inline-flex items-center gap-1 text-slate-400">
              <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
              Explainable AI Governance
            </span>
            <span>•</span>
            <span className="text-slate-400">Deterministic Demonstration Engine</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
