"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import type { CategoryResponse, QuestionAdminResponse, QuestionCreateRequest } from "@/types/question";

const questionSchema = z
  .object({
    category_id: z.string().min(1, "Select a category."),
    difficulty: z.enum(["easy", "medium", "hard"]),
    type: z.enum(["mcq", "coding", "descriptive"]),
    text: z.string().min(1, "Question text is required."),
    options: z.string().optional(),
    correct_answer: z.string().optional(),
    skill_tags: z.string().optional(),
    company_tags: z.string().optional(),
  })
  .superRefine((values, ctx) => {
    const options = splitLines(values.options);
    if (values.type === "mcq") {
      if (options.length < 2) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["options"], message: "MCQ needs at least 2 options (one per line)." });
      }
      if (!values.correct_answer?.trim()) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["correct_answer"], message: "MCQ requires a correct answer." });
      } else if (!options.includes(values.correct_answer.trim())) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["correct_answer"],
          message: "Correct answer must exactly match one of the options.",
        });
      }
    }
    if (values.type === "coding" && !values.correct_answer?.trim()) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["correct_answer"],
        message: "Coding questions need an expected-output correct answer.",
      });
    }
  });

type QuestionFormValues = z.infer<typeof questionSchema>;

function splitLines(value: string | undefined): string[] {
  if (!value) return [];
  return value
    .split("\n")
    .map((v) => v.trim())
    .filter(Boolean);
}

function splitCsv(value: string | undefined): string[] {
  if (!value) return [];
  return value
    .split(",")
    .map((v) => v.trim())
    .filter(Boolean);
}

export function QuestionForm({
  categories,
  initialValues,
  onSubmit,
  submitLabel = "Save",
  isSubmitting = false,
}: {
  categories: CategoryResponse[];
  initialValues?: QuestionAdminResponse;
  onSubmit: (payload: QuestionCreateRequest) => Promise<void> | void;
  submitLabel?: string;
  isSubmitting?: boolean;
}) {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors },
  } = useForm<QuestionFormValues>({
    resolver: zodResolver(questionSchema),
    defaultValues: { type: "mcq", difficulty: "medium" },
  });

  useEffect(() => {
    if (!initialValues) return;
    reset({
      category_id: initialValues.category_id,
      difficulty: initialValues.difficulty,
      type: initialValues.type,
      text: initialValues.text,
      options: initialValues.options.join("\n"),
      correct_answer: initialValues.correct_answer ?? "",
      skill_tags: initialValues.skill_tags.join(", "),
      company_tags: initialValues.company_tags.join(", "),
    });
  }, [initialValues, reset]);

  const questionType = watch("type");

  const submit = handleSubmit(async (values) => {
    await onSubmit({
      category_id: values.category_id,
      difficulty: values.difficulty,
      type: values.type,
      text: values.text,
      options: values.type === "mcq" ? splitLines(values.options) : [],
      correct_answer: values.type === "descriptive" ? undefined : values.correct_answer?.trim() || undefined,
      skill_tags: splitCsv(values.skill_tags),
      company_tags: splitCsv(values.company_tags),
    });
  });

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="category_id">Category</Label>
          <Select value={watch("category_id")} onValueChange={(v) => setValue("category_id", v, { shouldValidate: true })}>
            <SelectTrigger id="category_id">
              <SelectValue placeholder="Select a category" />
            </SelectTrigger>
            <SelectContent>
              {categories.map((c) => (
                <SelectItem key={c.id} value={c.id}>
                  {c.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.category_id && <p className="text-sm text-destructive">{errors.category_id.message}</p>}
        </div>
        <div className="space-y-2">
          <Label htmlFor="difficulty">Difficulty</Label>
          <Select value={watch("difficulty")} onValueChange={(v) => setValue("difficulty", v as QuestionFormValues["difficulty"])}>
            <SelectTrigger id="difficulty">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="easy">Easy</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="hard">Hard</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="type">Question type</Label>
        <Select value={watch("type")} onValueChange={(v) => setValue("type", v as QuestionFormValues["type"])}>
          <SelectTrigger id="type">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="mcq">MCQ</SelectItem>
            <SelectItem value="coding">Coding</SelectItem>
            <SelectItem value="descriptive">Descriptive</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="text">Question text</Label>
        <Textarea id="text" rows={3} {...register("text")} />
        {errors.text && <p className="text-sm text-destructive">{errors.text.message}</p>}
      </div>

      {questionType === "mcq" && (
        <div className="space-y-2">
          <Label htmlFor="options">Options (one per line)</Label>
          <Textarea id="options" rows={4} {...register("options")} />
          {errors.options && <p className="text-sm text-destructive">{errors.options.message}</p>}
        </div>
      )}

      {questionType !== "descriptive" && (
        <div className="space-y-2">
          <Label htmlFor="correct_answer">
            {questionType === "mcq" ? "Correct answer (must match an option exactly)" : "Expected output"}
          </Label>
          <Input id="correct_answer" {...register("correct_answer")} />
          {errors.correct_answer && <p className="text-sm text-destructive">{errors.correct_answer.message}</p>}
        </div>
      )}

      <div className="space-y-2">
        <Label htmlFor="skill_tags">Skill tags (comma-separated)</Label>
        <Input id="skill_tags" placeholder="python, algorithms" {...register("skill_tags")} />
      </div>
      <div className="space-y-2">
        <Label htmlFor="company_tags">Company tags (comma-separated, optional)</Label>
        <Input id="company_tags" {...register("company_tags")} />
      </div>

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Saving…" : submitLabel}
      </Button>
    </form>
  );
}
