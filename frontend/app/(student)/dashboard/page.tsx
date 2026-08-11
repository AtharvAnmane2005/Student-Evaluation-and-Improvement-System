"use client";

import Link from "next/link";
import { Award, Briefcase, ClipboardList, FileText, TrendingUp } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { StatCard } from "@/components/shared/stat-card";
import { useMyApplications } from "@/hooks/use-drives";
import { useResumeHistory } from "@/hooks/use-resumes";
import { useKnowledgeStates } from "@/hooks/use-assessments";
import { useStudentProfile } from "@/hooks/use-student-profile";

export default function StudentOverviewPage() {
  const { data: profile, isLoading: profileLoading } = useStudentProfile();
  const { data: resumes, isLoading: resumesLoading } = useResumeHistory();
  const { data: applications, isLoading: applicationsLoading } = useMyApplications();
  const { data: knowledgeStates, isLoading: knowledgeLoading } = useKnowledgeStates();

  const activeResume = resumes?.find((r) => r.is_active) ?? null;
  const shortlistedCount = applications?.filter((a) => a.status === "shortlisted" || a.status === "selected").length ?? 0;
  const avgMastery =
    knowledgeStates && knowledgeStates.length > 0
      ? Math.round(knowledgeStates.reduce((sum, k) => sum + k.mastery_pct, 0) / knowledgeStates.length)
      : null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold">
          Welcome back{profile?.name ? `, ${profile.name.trim().split(/\s+/)[0] ?? profile.name}` : ""}
        </h1>
        <p className="text-sm text-muted-foreground">Here&apos;s where your placement prep stands today.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Resume status"
          value={resumesLoading ? <Skeleton className="h-7 w-16" /> : activeResume ? "Uploaded" : "Not uploaded"}
          icon={FileText}
        />
        <StatCard
          label="Applications"
          value={applicationsLoading ? <Skeleton className="h-7 w-10" /> : (applications?.length ?? 0)}
          icon={Briefcase}
        />
        <StatCard
          label="Shortlisted / selected"
          value={applicationsLoading ? <Skeleton className="h-7 w-10" /> : shortlistedCount}
          icon={ClipboardList}
        />
        <StatCard
          label="Avg. skill mastery"
          value={knowledgeLoading ? <Skeleton className="h-7 w-14" /> : avgMastery !== null ? `${avgMastery}%` : "—"}
          icon={TrendingUp}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Profile completeness</CardTitle>
            <CardDescription>A fuller profile helps TPOs and drive eligibility checks.</CardDescription>
          </CardHeader>
          <CardContent>
            {profileLoading || !profile ? (
              <Skeleton className="h-4 w-full" />
            ) : (
              <>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{profile.profile_completeness_pct}% complete</span>
                </div>
                <Progress value={profile.profile_completeness_pct} />
                {profile.profile_completeness_pct < 100 && (
                  <Button asChild size="sm" variant="secondary" className="mt-4">
                    <Link href="/dashboard/profile">Complete your profile</Link>
                  </Button>
                )}
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Resume</CardTitle>
            <CardDescription>
              {activeResume
                ? `Active version: ${activeResume.original_filename}`
                : "No resume on file yet — upload one to start applying to drives."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild size="sm">
              <Link href="/dashboard/resume">{activeResume ? "Manage resume" : "Upload resume"}</Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Award className="h-4 w-4" /> Knowledge tracing snapshot
          </CardTitle>
          <CardDescription>Mastery estimates from your adaptive assessment attempts.</CardDescription>
        </CardHeader>
        <CardContent>
          {knowledgeLoading ? (
            <Skeleton className="h-16 w-full" />
          ) : !knowledgeStates || knowledgeStates.length === 0 ? (
            <div className="text-sm text-muted-foreground">
              No assessments taken yet.{" "}
              <Link href="/dashboard/assessments" className="text-primary underline underline-offset-2">
                Take one
              </Link>{" "}
              to start building your skill profile.
            </div>
          ) : (
            <div className="space-y-3">
              {knowledgeStates.slice(0, 5).map((state) => (
                <div key={state.skill_tag} className="flex items-center gap-3">
                  <Badge variant="outline" className="w-28 shrink-0 justify-center truncate">
                    {state.skill_tag}
                  </Badge>
                  <Progress value={state.mastery_pct} className="flex-1" />
                  <span className="w-10 shrink-0 text-right text-sm text-muted-foreground">
                    {Math.round(state.mastery_pct)}%
                  </span>
                </div>
              ))}
              {knowledgeStates.length > 5 && (
                <Link href="/dashboard/assessments" className="inline-block text-sm text-primary underline underline-offset-2">
                  View all {knowledgeStates.length} skills
                </Link>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
