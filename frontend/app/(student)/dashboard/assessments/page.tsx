"use client";

import { useRouter } from "next/navigation";
import { Award, Clock, ListChecks } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { useToast } from "@/hooks/use-toast";
import { useAssessments, useKnowledgeStates, useStartAssessment } from "@/hooks/use-assessments";
import { saveAttemptState } from "@/lib/attempt-storage";
import { fingerprintHash } from "@/lib/fingerprint";

function formatMinutes(sec: number): string {
  const minutes = Math.round(sec / 60);
  return `${minutes} min`;
}

export default function AssessmentsPage() {
  const { data: assessments, isLoading: assessmentsLoading } = useAssessments();
  const { data: knowledgeStates, isLoading: knowledgeLoading } = useKnowledgeStates();
  const startAssessment = useStartAssessment();
  const router = useRouter();
  const { toast } = useToast();
  const [startingId, setStartingId] = useState<string | null>(null);

  const handleStart = async (assessmentId: string) => {
    setStartingId(assessmentId);
    try {
      const result = await startAssessment.mutateAsync({
        assessmentId,
        fingerprintHash: fingerprintHash(),
      });
      saveAttemptState(result.attempt_id, {
        sessionToken: result.session_token,
        timeLimitSec: result.time_limit_sec,
        antiCheatConfig: result.anti_cheat_config,
        currentQuestion: result.next_question,
        startedAtMs: Date.now(),
        violationCount: 0,
      });
      router.push(`/dashboard/assessments/${result.attempt_id}/take`);
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Couldn't start this assessment. Please try again.";
      toast({ title: "Couldn't start assessment", description: detail, variant: "destructive" });
    } finally {
      setStartingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold">Assessments</h1>
        <p className="text-sm text-muted-foreground">
          Adaptive skill assessments — difficulty adjusts to your answers as you go.
        </p>
      </div>

      {assessmentsLoading ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-40 w-full" />
          ))}
        </div>
      ) : !assessments || assessments.length === 0 ? (
        <EmptyState
          icon={ListChecks}
          title="No assessments available"
          description="Your TPO or admin hasn't published any assessments yet."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {assessments.map((assessment) => (
            <Card key={assessment.id}>
              <CardHeader>
                <CardTitle className="text-base">{assessment.title}</CardTitle>
                <CardDescription className="flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" /> {formatMinutes(assessment.time_limit_sec)}
                  </span>
                  <span>{assessment.question_pool_size} questions</span>
                </CardDescription>
              </CardHeader>
              <CardContent>
                {assessment.anti_cheat_config.require_fullscreen && (
                  <p className="mb-3 text-xs text-muted-foreground">
                    Runs in fullscreen mode with tab-switch and copy/paste monitoring.
                  </p>
                )}
                <Button onClick={() => handleStart(assessment.id)} disabled={startingId === assessment.id}>
                  {startingId === assessment.id ? "Starting…" : "Start assessment"}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Award className="h-4 w-4" /> Skill mastery
          </CardTitle>
          <CardDescription>Built from an exponential moving average across your attempts.</CardDescription>
        </CardHeader>
        <CardContent>
          {knowledgeLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : !knowledgeStates || knowledgeStates.length === 0 ? (
            <p className="text-sm text-muted-foreground">No attempts yet — start an assessment above.</p>
          ) : (
            <div className="space-y-3">
              {knowledgeStates.map((state) => (
                <div key={state.skill_tag} className="flex items-center gap-3">
                  <Badge variant="outline" className="w-32 shrink-0 justify-center truncate">
                    {state.skill_tag}
                  </Badge>
                  <Progress value={state.mastery_pct} className="flex-1" />
                  <span className="w-12 shrink-0 text-right text-sm text-muted-foreground">
                    {Math.round(state.mastery_pct)}%
                  </span>
                  <span className="w-20 shrink-0 text-right text-xs text-muted-foreground">
                    {state.attempts_count} attempts
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
