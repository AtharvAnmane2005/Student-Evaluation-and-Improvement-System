"use client";

import { Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import type { MatchScoreBreakdown } from "@/types/matching";

export function MatchScoreCard({
  score,
  isLoading,
  isUnavailable,
}: {
  score: MatchScoreBreakdown | undefined;
  isLoading: boolean;
  isUnavailable: boolean;
}) {
  // Matching is a bonus feature layered on top of everything else — if the
  // model artifacts aren't provisioned in this deployment (see
  // app/ml/matching/artifacts/README.md), quietly show nothing rather than
  // an error or a permanent loading spinner.
  if (isUnavailable) return null;

  if (isLoading || !score) {
    return <Skeleton className="h-40 w-full" />;
  }

  const pct = Math.round(score.final_score * 100);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Sparkles className="h-4 w-4" /> Match score
        </CardTitle>
        <CardDescription>How well your active resume fits this role.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="mb-1 flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Overall match</span>
            <span className="font-semibold">{pct}%</span>
          </div>
          <Progress value={pct} />
        </div>

        <div className="grid grid-cols-3 gap-3 text-center text-xs">
          <div>
            <p className="text-muted-foreground">Semantic fit</p>
            <p className="font-medium">{Math.round(score.semantic_score * 100)}%</p>
          </div>
          <div>
            <p className="text-muted-foreground">Skills</p>
            <p className="font-medium">{Math.round(score.skills_score * 100)}%</p>
          </div>
          <div>
            <p className="text-muted-foreground">Experience</p>
            <p className="font-medium">{Math.round(score.experience_score * 100)}%</p>
          </div>
        </div>

        {score.matched_skills.length > 0 && (
          <div>
            <p className="mb-1.5 text-xs font-medium text-muted-foreground">Matched skills</p>
            <div className="flex flex-wrap gap-1.5">
              {score.matched_skills.map((skill) => (
                <Badge key={skill} variant="success">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {score.missing_skills.length > 0 && (
          <div>
            <p className="mb-1.5 text-xs font-medium text-muted-foreground">Skills to highlight or build</p>
            <div className="flex flex-wrap gap-1.5">
              {score.missing_skills.map((skill) => (
                <Badge key={skill} variant="outline">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
