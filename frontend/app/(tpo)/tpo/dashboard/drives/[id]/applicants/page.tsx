"use client";

import { useParams } from "next/navigation";
import { ChevronDown, ChevronUp, Download, Sparkles, Users } from "lucide-react";
import { useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { useToast } from "@/hooks/use-toast";
import { useStudentKnowledgeStates } from "@/hooks/use-assessments";
import { useRankedApplicants } from "@/hooks/use-matching";
import { downloadResumeFile } from "@/hooks/use-resumes";
import { useDriveApplicants, useUpdateApplicationStatus } from "@/hooks/use-tpo-drives";
import type { ApplicationStatus } from "@/types/drive";
import type { RankedApplicant } from "@/types/matching";

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

function ApplicantMastery({ studentId }: { studentId: string }) {
  const { data: states, isLoading } = useStudentKnowledgeStates(studentId);

  if (isLoading) return <Skeleton className="h-16 w-full" />;
  if (!states || states.length === 0) {
    return <p className="text-sm text-muted-foreground">No assessment attempts yet.</p>;
  }
  return (
    <div className="space-y-2">
      {states.map((s) => (
        <div key={s.skill_tag} className="flex items-center gap-3">
          <Badge variant="outline" className="w-28 shrink-0 justify-center truncate">
            {s.skill_tag}
          </Badge>
          <Progress value={s.mastery_pct} className="flex-1" />
          <span className="w-10 shrink-0 text-right text-sm text-muted-foreground">
            {Math.round(s.mastery_pct)}%
          </span>
        </div>
      ))}
    </div>
  );
}

export default function DriveApplicantsPage() {
  const params = useParams<{ id: string }>();
  const driveId = params.id;
  const { data: applicants, isLoading } = useDriveApplicants(driveId);
  const { data: rankedApplicants, error: rankedError } = useRankedApplicants(driveId);
  const matchUnavailable = (rankedError as any)?.response?.status === 503;
  const updateStatus = useUpdateApplicationStatus(driveId);
  const { toast } = useToast();
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [sortByMatch, setSortByMatch] = useState(false);

  const scoresByApplicationId = useMemo(() => {
    const map = new Map<string, RankedApplicant>();
    rankedApplicants?.forEach((r) => map.set(r.application_id, r));
    return map;
  }, [rankedApplicants]);

  const sortedApplicants = useMemo(() => {
    if (!applicants) return applicants;
    if (!sortByMatch) return applicants;
    return [...applicants].sort((a, b) => {
      const scoreA = scoresByApplicationId.get(a.id)?.final_score ?? -1;
      const scoreB = scoresByApplicationId.get(b.id)?.final_score ?? -1;
      return scoreB - scoreA;
    });
  }, [applicants, sortByMatch, scoresByApplicationId]);

  const handleStatusChange = async (applicationId: string, status: ApplicationStatus) => {
    try {
      await updateStatus.mutateAsync({ applicationId, status });
      toast({ title: "Status updated" });
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Couldn't update the status.";
      toast({ title: "Update failed", description: detail, variant: "destructive" });
    }
  };

  const handleDownload = async (resumeId: string, filename: string) => {
    try {
      await downloadResumeFile(resumeId, filename);
    } catch {
      toast({ title: "Download failed", variant: "destructive" });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold">Applicants</h1>
        <p className="text-sm text-muted-foreground">Review candidates and update their status.</p>
      </div>

      {isLoading ? (
        <Skeleton className="h-64 w-full" />
      ) : !applicants || applicants.length === 0 ? (
        <EmptyState icon={Users} title="No applicants yet" description="Applications will appear here as students apply." />
      ) : (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-base">{applicants.length} applicant(s)</CardTitle>
            {!matchUnavailable && rankedApplicants && rankedApplicants.length > 0 && (
              <Button size="sm" variant={sortByMatch ? "default" : "outline"} onClick={() => setSortByMatch((v) => !v)}>
                <Sparkles className="mr-1.5 h-3.5 w-3.5" />
                {sortByMatch ? "Sorted by match" : "Sort by match"}
              </Button>
            )}
          </CardHeader>
          <CardContent className="space-y-2">
            {sortedApplicants!.map((applicant) => {
              const expanded = expandedId === applicant.id;
              const matchScore = scoresByApplicationId.get(applicant.id);
              return (
                <div key={applicant.id} className="rounded-md border border-border">
                  <div className="flex flex-wrap items-center justify-between gap-3 p-4">
                    <button
                      onClick={() => setExpandedId(expanded ? null : applicant.id)}
                      className="flex items-center gap-2 text-left"
                    >
                      {expanded ? (
                        <ChevronUp className="h-4 w-4 text-muted-foreground" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-muted-foreground" />
                      )}
                      <div>
                        <p className="font-medium">{applicant.student_name}</p>
                        <p className="text-sm text-muted-foreground">
                          {applicant.student_department ?? "—"} · CGPA {applicant.student_cgpa ?? "—"} · Applied{" "}
                          {formatDate(applicant.applied_at)}
                        </p>
                      </div>
                    </button>

                    <div className="flex items-center gap-2">
                      {matchScore && <Badge variant="outline">{Math.round(matchScore.final_score * 100)}% match</Badge>}
                      <Badge variant={statusVariant(applicant.status)}>{applicant.status}</Badge>
                      {applicant.resume_filename && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDownload(applicant.resume_id, applicant.resume_filename!)}
                        >
                          <Download className="mr-1.5 h-3.5 w-3.5" />
                          Resume
                        </Button>
                      )}
                      <Select
                        value={applicant.status}
                        onValueChange={(value) => handleStatusChange(applicant.id, value as ApplicationStatus)}
                      >
                        <SelectTrigger className="w-36">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="applied">Applied</SelectItem>
                          <SelectItem value="shortlisted">Shortlisted</SelectItem>
                          <SelectItem value="rejected">Rejected</SelectItem>
                          <SelectItem value="selected">Selected</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {expanded && (
                    <div className="border-t border-border bg-secondary p-4 space-y-4">
                      {matchScore && (
                        <div>
                          <p className="mb-2 text-sm font-medium">Match breakdown ({Math.round(matchScore.final_score * 100)}%)</p>
                          <div className="flex flex-wrap gap-1.5">
                            {matchScore.matched_skills.map((skill) => (
                              <Badge key={skill} variant="success">
                                {skill}
                              </Badge>
                            ))}
                            {matchScore.missing_skills.map((skill) => (
                              <Badge key={skill} variant="outline">
                                {skill}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      <div>
                        <p className="mb-2 text-sm font-medium">Skill mastery</p>
                        <ApplicantMastery studentId={applicant.student_id} />
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
