"use client";

import { useRouter } from "next/navigation";
import { Award, BarChart3, LayoutDashboard, ListChecks } from "lucide-react";
import { useEffect } from "react";

import { DashboardShell, initialsFrom, type DashboardNavItem } from "@/components/shared/dashboard-shell";
import { useAuth } from "@/providers/auth-provider";

const NAV_ITEMS: DashboardNavItem[] = [
  { href: "/admin/dashboard", label: "Overview", icon: LayoutDashboard, exact: true },
  { href: "/admin/dashboard/questions", label: "Question bank", icon: ListChecks },
  { href: "/admin/dashboard/assessments", label: "Assessments", icon: Award },
  { href: "/admin/dashboard/analytics", label: "Analytics", icon: BarChart3 },
];

/**
 * middleware.ts already redirects unauthenticated/wrong-role requests away
 * from /admin before this even renders — this is a client-side backstop,
 * same reasoning as the student/TPO layout guards.
 */
export default function AdminDashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && (!user || user.role !== "admin")) {
      router.replace("/login");
    }
  }, [isLoading, user, router]);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  if (isLoading || !user || user.role !== "admin") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-sm text-muted-foreground">Loading your dashboard…</div>
      </div>
    );
  }

  return (
    <DashboardShell
      navItems={NAV_ITEMS}
      displayName={user.email}
      initials={initialsFrom(undefined, user.email)}
      onLogout={handleLogout}
    >
      {children}
    </DashboardShell>
  );
}
