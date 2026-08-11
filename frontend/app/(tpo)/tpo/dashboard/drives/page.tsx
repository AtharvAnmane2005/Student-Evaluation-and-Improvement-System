"use client";

import Link from "next/link";
import { Briefcase, PlusCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { useMyDrives } from "@/hooks/use-tpo-drives";

function formatDeadline(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { dateStyle: "medium" });
}

export default function TpoDrivesPage() {
  const { data: drives, isLoading } = useMyDrives();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold">My drives</h1>
          <p className="text-sm text-muted-foreground">All placement drives you&apos;ve created.</p>
        </div>
        <Button asChild>
          <Link href="/tpo/dashboard/drives/new">
            <PlusCircle className="mr-2 h-4 w-4" />
            New drive
          </Link>
        </Button>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full" />
          ))}
        </div>
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
        <div className="grid gap-4 sm:grid-cols-2">
          {drives.map((drive) => (
            <Link key={drive.id} href={`/tpo/dashboard/drives/${drive.id}`}>
              <Card className="h-full transition-colors hover:border-primary">
                <CardHeader>
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-base">{drive.job_title}</CardTitle>
                    <Badge variant={drive.status === "open" ? "success" : "secondary"}>{drive.status}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{drive.company.name}</p>
                </CardHeader>
                <CardContent className="space-y-1 text-sm text-muted-foreground">
                  {drive.location && <div>{drive.location}</div>}
                  {drive.package && <div>Package: {drive.package}</div>}
                  <div>Deadline: {formatDeadline(drive.deadline)}</div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
