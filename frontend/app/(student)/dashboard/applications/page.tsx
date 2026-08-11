"use client";

import Link from "next/link";
import { ClipboardList } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { useDrives, useMyApplications } from "@/hooks/use-drives";
import type { ApplicationStatus } from "@/types/drive";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { dateStyle: "medium" });
}

function statusVariant(status: ApplicationStatus): "success" | "destructive" | "secondary" | "outline" {
  switch (status) {
    case "selected":
      return "success";
    case "shortlisted":
      return "outline";
    case "rejected":
      return "destructive";
    default:
      return "secondary";
  }
}

export default function ApplicationsPage() {
  const { data: applications, isLoading: applicationsLoading } = useMyApplications();
  const { data: drives, isLoading: drivesLoading } = useDrives();

  const isLoading = applicationsLoading || drivesLoading;
  const driveById = new Map((drives ?? []).map((d) => [d.id, d]));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold">My applications</h1>
        <p className="text-sm text-muted-foreground">Track the status of every drive you&apos;ve applied to.</p>
      </div>

      {isLoading ? (
        <Skeleton className="h-64 w-full" />
      ) : !applications || applications.length === 0 ? (
        <EmptyState
          icon={ClipboardList}
          title="No applications yet"
          description="Browse open drives and apply to see them tracked here."
        />
      ) : (
        <div className="space-y-3">
          {applications.map((app) => {
            const drive = driveById.get(app.drive_id);
            return (
              <Link key={app.id} href={`/dashboard/drives/${app.drive_id}`}>
                <Card className="transition-colors hover:border-primary">
                  <CardContent className="flex items-center justify-between gap-4 p-4">
                    <div>
                      <p className="font-medium">{drive?.job_title ?? "Drive"}</p>
                      <p className="text-sm text-muted-foreground">
                        {drive?.company.name ?? "—"} · Applied {formatDate(app.applied_at)}
                      </p>
                    </div>
                    <Badge variant={statusVariant(app.status)}>{app.status}</Badge>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
