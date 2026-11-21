import React from "react";
import { Link } from "react-router-dom";
import { useNotificationStore } from "@/stores/notificationStore";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { formatRelativeTime } from "@/lib/utils";
import { Bell, Check, Trash2, ExternalLink, AlertCircle, AlertTriangle, CheckCircle2, Info } from "lucide-react";

export default function CitizenNotificationsPage() {
  const { notifications, markAsRead, markAllAsRead, removeNotification } =
    useNotificationStore();

  const getIcon = (type: string) => {
    switch (type) {
      case "critical":
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case "warning":
        return <AlertTriangle className="w-4 h-4 text-amber-500" />;
      case "success":
        return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;
      default:
        return <Info className="w-4 h-4 text-blue-500" />;
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title="Notifications & Updates"
        subtitle="Real-time alerts, AI classification reports, and official resolution notices regarding your civic filings."
        breadcrumbs={[
          { label: "Citizen Portal", href: "/citizen/dashboard" },
          { label: "Notifications", active: true },
        ]}
        actions={
          <button
            onClick={markAllAsRead}
            className="px-3 py-1.5 text-xs font-semibold bg-white border border-slate-200 rounded hover:bg-slate-50 text-slate-700 transition-colors"
          >
            Mark All as Read
          </button>
        }
      />

      <div className="bg-white rounded-lg border border-slate-200 shadow-subtle divide-y divide-slate-100 overflow-hidden">
        {notifications.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-400">
            You have no notifications at this time.
          </div>
        ) : (
          notifications.map((n) => (
            <div
              key={n.id}
              className={`p-4 flex items-start justify-between gap-4 transition-colors ${
                !n.read ? "bg-blue-50/20" : "hover:bg-slate-50/80"
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="mt-0.5">{getIcon(n.type)}</div>
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-xs font-bold text-slate-900">{n.title}</h4>
                    {!n.read && (
                      <span className="w-2 h-2 rounded-full bg-blue-600 inline-block" />
                    )}
                  </div>
                  <p className="text-xs text-slate-600 mt-0.5 leading-relaxed">{n.message}</p>
                  <span className="text-[10px] text-slate-400 font-mono mt-1.5 block">
                    {formatRelativeTime(n.timestamp)}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2 flex-shrink-0">
                {n.link && (
                  <Link
                    to={n.link}
                    onClick={() => markAsRead(n.id)}
                    className="p-1.5 rounded hover:bg-slate-100 text-blue-600"
                    title="View related record"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </Link>
                )}
                {!n.read && (
                  <button
                    onClick={() => markAsRead(n.id)}
                    className="p-1.5 rounded hover:bg-slate-100 text-slate-500"
                    title="Mark read"
                  >
                    <Check className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => removeNotification(n.id)}
                  className="p-1.5 rounded hover:bg-slate-100 text-slate-400 hover:text-red-600"
                  title="Delete"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
