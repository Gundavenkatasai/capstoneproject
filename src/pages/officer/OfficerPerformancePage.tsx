import React from "react";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { MetricCard } from "@/components/common/MetricCard";
import { ChartCard } from "@/components/common/ChartCard";
import { Award, Clock, CheckCircle2, TrendingUp, Star } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";

export default function OfficerPerformancePage() {
  const weeklyData = [
    { day: "Mon", resolved: 6, incoming: 5 },
    { day: "Tue", resolved: 8, incoming: 7 },
    { day: "Wed", resolved: 10, incoming: 8 },
    { day: "Thu", resolved: 7, incoming: 6 },
    { day: "Fri", resolved: 9, incoming: 7 },
    { day: "Sat", resolved: 4, incoming: 3 },
    { day: "Sun", resolved: 2, incoming: 2 },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Officer Performance & SLA Metrics"
        subtitle="Operational resolution analytics, citizen satisfaction ratings, and compliance KPIs."
        breadcrumbs={[
          { label: "Officer Portal", href: "/officer/dashboard" },
          { label: "Performance & SLA", active: true },
        ]}
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Citizen Satisfaction"
          value="4.8 / 5.0"
          subtitle="Based on 48 verified reviews"
          icon={Star}
          badge="Top 5% Officers"
        />
        <MetricCard
          title="SLA Compliance Rate"
          value="94.2%"
          change="+2.4%"
          changeType="increase"
          isPositive={true}
          subtitle="Threshold target: 90%"
          icon={CheckCircle2}
        />
        <MetricCard
          title="Avg Resolution Speed"
          value="42 Hours"
          change="-4.5h"
          changeType="decrease"
          isPositive={true}
          subtitle="Department benchmark: 48h"
          icon={Clock}
        />
        <MetricCard
          title="Resolved This Month"
          value="38 Cases"
          subtitle="Public Works Division"
          icon={Award}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard
          title="Weekly Case Throughput"
          subtitle="Cases resolved vs incoming dispatch over the past 7 days"
        >
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip />
                <Bar dataKey="incoming" name="Incoming" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="resolved" name="Resolved" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard
          title="Historical Resolution Time Trend"
          subtitle="Mean resolution hours per month across 2026"
        >
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={[
                  { month: "Jun", hours: 56 },
                  { month: "Jul", hours: 52 },
                  { month: "Aug", hours: 48 },
                  { month: "Sep", hours: 45 },
                  { month: "Oct", hours: 44 },
                  { month: "Nov", hours: 42 },
                ]}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="hours"
                  name="Avg Hours"
                  stroke="#10b981"
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>
    </div>
  );
}
