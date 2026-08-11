"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { ApplicationStatusBreakdown } from "@/types/analytics";

const STATUS_COLORS: Record<string, string> = {
  Applied: "#94a3b8",
  Shortlisted: "#3b82f6",
  Rejected: "#ef4444",
  Selected: "#22c55e",
};

export function StatusBreakdownChart({ breakdown }: { breakdown: ApplicationStatusBreakdown }) {
  const data = [
    { name: "Applied", count: breakdown.applied },
    { name: "Shortlisted", count: breakdown.shortlisted },
    { name: "Rejected", count: breakdown.rejected },
    { name: "Selected", count: breakdown.selected },
  ];

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
        <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
        <Tooltip />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {data.map((entry) => (
            <Cell key={entry.name} fill={STATUS_COLORS[entry.name]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
