import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CivicMind AI — Grievance Intelligence & Resolution Prediction",
  description:
    "An intelligent civic platform that transforms citizen complaints into actionable insights through predictive AI, semantic intelligence and transparent decision support.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 antialiased font-sans text-slate-900">
        {children}
      </body>
    </html>
  );
}
