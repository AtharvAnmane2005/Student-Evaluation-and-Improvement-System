"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { CheckCircle2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { useAttemptResults } from "@/hooks/use-assessments";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

export default function AssessmentResultsPage() {
  const params = useParams<{ attemptId: string }>();
  const { data: result, isLoading } = useAttemptResults(params.attemptId);

  if (isLoading || !result) {
    return (
      <div className="mx-auto max-w-xl">
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  const pct = result.max_possible_marks > 0 ? Math.round((result.total_marks / result.max_possible_marks) * 100) : 0;

  return (
    <div className="mx-auto max-w-xl space-y-4">
      <Card>
        <CardHeader className="items-center text-center">
          <CheckCircle2 className="mb-2 h-10 w-10 text-success" />
          <CardTitle>Attempt {result.status === "submitted" ? "submitted" : "in progress"}</CardTitle>
          <CardDescription>Started {formatDate(result.started_at)}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="mb-1 flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Score</span>
              <span className="font-medium">
                {result.total_marks} / {result.max_possible_marks} ({pct}%)
              </span>
            </div>
            <Progress value={pct} />
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Questions answered</p>
              <p className="font-medium">{result.questions_answered}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Submitted</p>
              <p className="font-medium">{result.submitted_at ? formatDate(result.submitted_at) : "—"}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-center gap-3">
        <Button asChild variant="secondary">
          <Link href="/dashboard/assessments">Back to assessments</Link>
        </Button>
        <Button asChild>
          <Link href="/dashboard">Go to dashboard</Link>
        </Button>
      </div>
    </div>
  );
}
