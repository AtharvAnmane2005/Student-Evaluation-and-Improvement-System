"use client";

import { useParams } from "next/navigation";
import { Building2, Calendar, MapPin } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { MatchScoreCard } from "@/components/shared/match-score-card";
import { useToast } from "@/hooks/use-toast";
import { useApplyToDrive, useDriveDetail, useMyApplications } from "@/hooks/use-drives";
import { useDriveMatchScore } from "@/hooks/use-matching";
import { useStudentProfile } from "@/hooks/use-student-profile";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { dateStyle: "medium" });
}

export default function DriveDetailPage() {
  const params = useParams<{ id: string }>();
  const driveId = params.id;

  const { data: drive, isLoading } = useDriveDetail(driveId);
  const { data: profile } = useStudentProfile();
  const { data: applications } = useMyApplications();
  const applyToDrive = useApplyToDrive();
  const { toast } = useToast();

  const {
    data: matchScore,
    isLoading: matchLoading,
    error: matchError,
  } = useDriveMatchScore(driveId);
  const matchUnavailable = (matchError as any)?.response?.status === 503;

  const existingApplication = applications?.find((a) => a.drive_id === driveId);
  const closed = drive ? drive.status === "closed" || new Date(drive.deadline).getTime() < Date.now() : false;

  const eligibilityIssues: string[] = [];
  if (drive && profile) {
    if (drive.eligibility.min_cgpa !== null && (profile.cgpa === null || profile.cgpa < drive.eligibility.min_cgpa)) {
      eligibilityIssues.push(`Requires minimum CGPA of ${drive.eligibility.min_cgpa}.`);
    }
    if (
      drive.eligibility.departments.length > 0 &&
      (!profile.department || !drive.eligibility.departments.includes(profile.department))
    ) {
      eligibilityIssues.push(`Open to: ${drive.eligibility.departments.join(", ")}.`);
    }
    if (
      drive.eligibility.batch_years.length > 0 &&
      (!profile.batch_year || !drive.eligibility.batch_years.includes(profile.batch_year))
    ) {
      eligibilityIssues.push(`Open to batch years: ${drive.eligibility.batch_years.join(", ")}.`);
    }
  }

  const handleApply = async () => {
    try {
      await applyToDrive.mutateAsync(driveId);
      toast({ title: "Application submitted", description: "You'll be notified of any status updates." });
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Couldn't submit your application. Please try again.";
      toast({ title: "Application failed", description: detail, variant: "destructive" });
    }
  };

  if (isLoading || !drive) {
    return (
      <div className="max-w-3xl space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <div className="mb-2 flex items-center gap-2">
          <Badge variant={closed ? "secondary" : "success"}>{closed ? "Closed" : "Open"}</Badge>
          {existingApplication && <Badge variant="outline">Application: {existingApplication.status}</Badge>}
        </div>
        <h1 className="font-display text-2xl font-semibold">{drive.job_title}</h1>
        <div className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <Building2 className="h-4 w-4" /> {drive.company.name}
          </span>
          {drive.location && (
            <span className="flex items-center gap-1.5">
              <MapPin className="h-4 w-4" /> {drive.location}
            </span>
          )}
          <span className="flex items-center gap-1.5">
            <Calendar className="h-4 w-4" /> Apply by {formatDate(drive.deadline)}
          </span>
        </div>
      </div>

      <MatchScoreCard score={matchScore} isLoading={matchLoading} isUnavailable={matchUnavailable} />

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Job description</CardTitle>
          {drive.package && <CardDescription>Package: {drive.package}</CardDescription>}
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <p className="whitespace-pre-line text-muted-foreground">{drive.description || drive.jd_text}</p>

          {drive.required_skills.length > 0 && (
            <div>
              <p className="mb-1.5 font-medium">Required skills</p>
              <div className="flex flex-wrap gap-1.5">
                {drive.required_skills.map((skill) => (
                  <Badge key={skill} variant="outline">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {drive.selection_process.length > 0 && (
            <div>
              <p className="mb-1.5 font-medium">Selection process</p>
              <ol className="list-inside list-decimal space-y-0.5 text-muted-foreground">
                {drive.selection_process.map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ol>
            </div>
          )}

          <div>
            <p className="mb-1.5 font-medium">Eligibility</p>
            <ul className="space-y-0.5 text-muted-foreground">
              <li>Minimum CGPA: {drive.eligibility.min_cgpa ?? "No minimum"}</li>
              <li>Departments: {drive.eligibility.departments.length > 0 ? drive.eligibility.departments.join(", ") : "All"}</li>
              <li>Batch years: {drive.eligibility.batch_years.length > 0 ? drive.eligibility.batch_years.join(", ") : "All"}</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="flex flex-col gap-3 p-6">
          {existingApplication ? (
            <p className="text-sm">
              You applied on {formatDate(existingApplication.applied_at)} — current status:{" "}
              <span className="font-medium">{existingApplication.status}</span>
            </p>
          ) : (
            <>
              {eligibilityIssues.length > 0 && (
                <div className="rounded-md border border-warning bg-secondary p-3 text-sm">
                  <p className="mb-1 font-medium text-warning">Before you apply:</p>
                  <ul className="list-inside list-disc">
                    {eligibilityIssues.map((issue, i) => (
                      <li key={i}>{issue}</li>
                    ))}
                  </ul>
                </div>
              )}
              <Button onClick={handleApply} disabled={closed || applyToDrive.isPending} className="w-fit">
                {applyToDrive.isPending ? "Applying…" : closed ? "Applications closed" : "Apply now"}
              </Button>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
