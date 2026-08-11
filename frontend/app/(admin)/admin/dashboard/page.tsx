"use client";

import Link from "next/link";
import { Award, ListChecks, PlusCircle, Tags } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { StatCard } from "@/components/shared/stat-card";
import { useAssessments } from "@/hooks/use-assessments";
import { useCategories, useQuestions } from "@/hooks/use-admin-questions";

export default function AdminOverviewPage() {
  const { data: categories, isLoading: categoriesLoading } = useCategories();
  const { data: questions, isLoading: questionsLoading } = useQuestions();
  const { data: assessments, isLoading: assessmentsLoading } = useAssessments();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold">Admin dashboard</h1>
          <p className="text-sm text-muted-foreground">Manage the question bank and adaptive assessments.</p>
        </div>
        <div className="flex gap-2">
          <Button asChild variant="secondary">
            <Link href="/admin/dashboard/questions/new">
              <PlusCircle className="mr-2 h-4 w-4" />
              New question
            </Link>
          </Button>
          <Button asChild>
            <Link href="/admin/dashboard/assessments/new">
              <PlusCircle className="mr-2 h-4 w-4" />
              New assessment
            </Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard
          label="Categories"
          value={categoriesLoading ? <Skeleton className="h-7 w-10" /> : (categories?.length ?? 0)}
          icon={Tags}
        />
        <StatCard
          label="Questions"
          value={questionsLoading ? <Skeleton className="h-7 w-10" /> : (questions?.length ?? 0)}
          icon={ListChecks}
        />
        <StatCard
          label="Assessments"
          value={assessmentsLoading ? <Skeleton className="h-7 w-10" /> : (assessments?.length ?? 0)}
          icon={Award}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Question bank</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-muted-foreground">
              Add questions individually or bulk-import a JSON array. Categories organize questions and drive which
              pool an assessment draws from.
            </p>
            <Button asChild size="sm" variant="secondary">
              <Link href="/admin/dashboard/questions">Manage question bank</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Assessments</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-muted-foreground">
              An assessment draws from one or more categories, adapting difficulty as a student answers.
            </p>
            <Button asChild size="sm" variant="secondary">
              <Link href="/admin/dashboard/assessments">Manage assessments</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
