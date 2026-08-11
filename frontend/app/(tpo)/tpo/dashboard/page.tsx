"use client";

import Link from "next/link";
import { Briefcase, PlusCircle, Users } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { StatCard } from "@/components/shared/stat-card";
import { useMyDrives } from "@/hooks/use-tpo-drives";

function formatDeadline(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { dateStyle: "medium" });
}

export default function TpoOverviewPage() {
  const { data: drives, isLoading } = useMyDrives();

  const openCount = drives?.filter((d) => d.status === "open").length ?? 0;
  const closedCount = drives?.filter((d) => d.status === "closed").length ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold">TPO dashboard</h1>
          <p className="text-sm text-muted-foreground">Manage your placement drives and review applicants.</p>
        </div>
        <Button asChild>
          <Link href="/tpo/dashboard/drives/new">
            <PlusCircle className="mr-2 h-4 w-4" />
            New drive
          </Link>
        </Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard
          label="Total drives"
          value={isLoading ? <Skeleton className="h-7 w-10" /> : (drives?.length ?? 0)}
          icon={Briefcase}
        />
        <StatCard label="Open" value={isLoading ? <Skeleton className="h-7 w-10" /> : openCount} icon={Briefcase} />
        <StatCard label="Closed" value={isLoading ? <Skeleton className="h-7 w-10" /> : closedCount} icon={Users} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Recent drives</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-40 w-full" />
          ) : !drives || drives.length === 0 ? (
            <EmptyState
              icon={Briefcase}
              title="No drives yet"
              description="Create your first placement drive to start accepting applications."
              action={
                <Button asChild size="sm">
                  <Link href="/tpo/dashboard/drives/new">Create a drive</Link>
                </Button>
              }
            />
          ) : (
            <div className="space-y-2">
              {drives.slice(0, 5).map((drive) => (
                <Link key={drive.id} href={`/tpo/dashboard/drives/${drive.id}`}>
                  <div className="flex items-center justify-between rounded-md border border-border px-4 py-3 text-sm transition-colors hover:border-primary">
                    <div>
                      <p className="font-medium">{drive.job_title}</p>
                      <p className="text-muted-foreground">
                        {drive.company.name} · Apply by {formatDeadline(drive.deadline)}
                      </p>
                    </div>
                    <Badge variant={drive.status === "open" ? "success" : "secondary"}>{drive.status}</Badge>
                  </div>
                </Link>
              ))}
              {drives.length > 5 && (
                <Link href="/tpo/dashboard/drives" className="inline-block text-sm text-primary underline underline-offset-2">
                  View all {drives.length} drives
                </Link>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
