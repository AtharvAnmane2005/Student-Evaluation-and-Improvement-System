"use client";

import { useRouter } from "next/navigation";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { QuestionForm } from "@/components/shared/question-form";
import { useToast } from "@/hooks/use-toast";
import { useCategories, useCreateQuestion } from "@/hooks/use-admin-questions";
import type { QuestionCreateRequest } from "@/types/question";

export default function NewQuestionPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { data: categories, isLoading } = useCategories();
  const createQuestion = useCreateQuestion();

  const handleSubmit = async (payload: QuestionCreateRequest) => {
    try {
      await createQuestion.mutateAsync(payload);
      toast({ title: "Question created" });
      router.push("/admin/dashboard/questions");
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Couldn't create the question. Please try again.";
      toast({ title: "Creation failed", description: detail, variant: "destructive" });
    }
  };

  return (
    <div className="max-w-2xl">
      <h1 className="mb-1 font-display text-2xl font-semibold">New question</h1>
      <p className="mb-6 text-sm text-muted-foreground">Marks are assigned automatically based on difficulty.</p>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Question details</CardTitle>
          {(!categories || categories.length === 0) && !isLoading && (
            <CardDescription className="text-warning">
              No categories exist yet — create one from the question bank page first.
            </CardDescription>
          )}
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-64 w-full" />
          ) : (
            <QuestionForm
              categories={categories ?? []}
              onSubmit={handleSubmit}
              submitLabel="Create question"
              isSubmitting={createQuestion.isPending}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
