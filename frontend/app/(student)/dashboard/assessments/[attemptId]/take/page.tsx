"use client";

import { useParams, useRouter } from "next/navigation";
import { AlertTriangle, Clock } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { useReportViolation, useSubmitAnswer } from "@/hooks/use-assessments";
import { clearAttemptState, loadAttemptState, saveAttemptState, type AttemptState } from "@/lib/attempt-storage";

const VIOLATION_THROTTLE_MS = 3000;

function formatTime(totalSec: number): string {
  const m = Math.floor(totalSec / 60);
  const s = totalSec % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export default function TakeAssessmentPage() {
  const params = useParams<{ attemptId: string }>();
  const attemptId = params.attemptId;
  const router = useRouter();
  const { toast } = useToast();

  const [attempt, setAttempt] = useState<AttemptState | null>(null);
  const [selectedOption, setSelectedOption] = useState<string>("");
  const [freeTextResponse, setFreeTextResponse] = useState<string>("");
  const [secondsLeft, setSecondsLeft] = useState<number>(0);
  const [violationBanner, setViolationBanner] = useState<string | null>(null);
  const [autoSubmittedDialogOpen, setAutoSubmittedDialogOpen] = useState(false);

  const questionStartRef = useRef<number>(Date.now());
  const lastViolationAtRef = useRef<Record<string, number>>({});
  const submittedRef = useRef(false); // guards against double-submit races (timer + auto-submit)

  const submitAnswer = useSubmitAnswer();
  const reportViolation = useReportViolation();

  // ---- Load attempt state (from sessionStorage, set by the "Start" action) ----
  useEffect(() => {
    const stored = loadAttemptState(attemptId);
    if (!stored) {
      // Direct navigation with no active attempt in this browser session — nothing to resume.
      toast({
        title: "No active attempt found",
        description: "Start a new assessment attempt from the assessments page.",
        variant: "destructive",
      });
      router.replace("/dashboard/assessments");
      return;
    }
    setAttempt(stored);
    setSecondsLeft(Math.max(0, stored.timeLimitSec - Math.floor((Date.now() - stored.startedAtMs) / 1000)));
    questionStartRef.current = Date.now();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attemptId]);

  const finishAttempt = useCallback(
    (reason: "completed" | "auto_submitted") => {
      if (submittedRef.current) return;
      submittedRef.current = true;
      clearAttemptState(attemptId);
      if (document.fullscreenElement) {
        document.exitFullscreen().catch(() => undefined);
      }
      if (reason === "auto_submitted") {
        setAutoSubmittedDialogOpen(true);
      } else {
        router.replace(`/dashboard/assessments/results/${attemptId}`);
      }
    },
    [attemptId, router]
  );

  const reportViolationThrottled = useCallback(
    (type: string, metadata?: Record<string, unknown>) => {
      if (!attempt || submittedRef.current) return;
      const now = Date.now();
      const last = lastViolationAtRef.current[type] ?? 0;
      if (now - last < VIOLATION_THROTTLE_MS) return;
      lastViolationAtRef.current[type] = now;

      reportViolation.mutate(
        { attemptId, sessionToken: attempt.sessionToken, type, metadata },
        {
          onSuccess: (result) => {
            setAttempt((prev) => (prev ? { ...prev, violationCount: result.violation_count } : prev));
            if (result.attempt_status === "submitted" || result.auto_submitted) {
              finishAttempt("auto_submitted");
              return;
            }
            setViolationBanner(
              `Violation recorded (${result.violation_count}/${result.max_violations}): ${type.replace(/_/g, " ")}`
            );
          },
        }
      );
    },
    [attempt, attemptId, finishAttempt, reportViolation]
  );

  // ---- Fullscreen enforcement ----
  useEffect(() => {
    if (!attempt) return;
    if (attempt.antiCheatConfig.require_fullscreen && !document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {
        reportViolationThrottled("fullscreen_denied");
      });
    }

    const onFullscreenChange = () => {
      if (attempt.antiCheatConfig.require_fullscreen && !document.fullscreenElement && !submittedRef.current) {
        reportViolationThrottled("fullscreen_exit");
      }
    };
    document.addEventListener("fullscreenchange", onFullscreenChange);
    return () => document.removeEventListener("fullscreenchange", onFullscreenChange);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attempt?.antiCheatConfig.require_fullscreen]);

  // ---- Tab-switch / visibility detection ----
  useEffect(() => {
    if (!attempt) return;
    const onVisibilityChange = () => {
      if (document.hidden) {
        reportViolationThrottled("tab_switch");
      }
    };
    document.addEventListener("visibilitychange", onVisibilityChange);
    return () => document.removeEventListener("visibilitychange", onVisibilityChange);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attempt]);

  // ---- Copy/paste blocking ----
  useEffect(() => {
    if (!attempt) return;
    const block = (e: ClipboardEvent) => {
      e.preventDefault();
      reportViolationThrottled("copy_paste_attempt");
    };
    document.addEventListener("copy", block);
    document.addEventListener("paste", block);
    document.addEventListener("cut", block);
    return () => {
      document.removeEventListener("copy", block);
      document.removeEventListener("paste", block);
      document.removeEventListener("cut", block);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attempt]);

  // ---- Countdown timer ----
  // This is a UX convenience only — server-side timer enforcement (per
  // Phase 11) is the actual source of truth; a client clock can't be
  // trusted, but the answer/violation endpoints will reject or auto-submit
  // regardless of what happens here.
  useEffect(() => {
    if (!attempt || submittedRef.current) return;
    const interval = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          reportViolationThrottled("time_expired");
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attempt]);

  const handleSubmitAnswer = async () => {
    if (!attempt?.currentQuestion) return;
    const question = attempt.currentQuestion;
    const response = question.type === "mcq" ? selectedOption : freeTextResponse;
    if (!response.trim()) {
      toast({ title: "Answer required", description: "Please provide a response before continuing." });
      return;
    }

    const timeTakenSec = (Date.now() - questionStartRef.current) / 1000;

    try {
      const result = await submitAnswer.mutateAsync({
        attemptId,
        sessionToken: attempt.sessionToken,
        questionId: question.id,
        response,
        timeTakenSec,
      });

      setSelectedOption("");
      setFreeTextResponse("");
      questionStartRef.current = Date.now();

      if (result.attempt_status === "submitted" || !result.next_question) {
        finishAttempt("completed");
        return;
      }

      const updated: AttemptState = { ...attempt, currentQuestion: result.next_question };
      setAttempt(updated);
      saveAttemptState(attemptId, updated);
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Couldn't submit your answer. Please try again.";
      toast({ title: "Submission failed", description: detail, variant: "destructive" });
    }
  };

  if (!attempt) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center text-sm text-muted-foreground">
        Loading assessment…
      </div>
    );
  }

  const question = attempt.currentQuestion;

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="flex items-center justify-between">
        <Badge variant="outline" className="capitalize">
          {question?.difficulty ?? "—"}
        </Badge>
        <div className="flex items-center gap-1.5 text-sm font-medium">
          <Clock className="h-4 w-4" />
          {formatTime(secondsLeft)}
        </div>
      </div>

      {violationBanner && (
        <div className="flex items-center gap-2 rounded-md border border-destructive bg-secondary px-3 py-2 text-sm text-destructive">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          {violationBanner}
        </div>
      )}

      {!question ? (
        <Card>
          <CardContent className="p-8 text-center text-sm text-muted-foreground">
            No more questions — wrapping up your attempt…
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-normal leading-relaxed">{question.text}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {question.type === "mcq" ? (
              <div className="space-y-2">
                {question.options.map((option, i) => (
                  <button
                    key={i}
                    onClick={() => setSelectedOption(option)}
                    className={`w-full rounded-md border px-4 py-2.5 text-left text-sm transition-colors ${
                      selectedOption === option
                        ? "border-primary bg-secondary"
                        : "border-border hover:bg-secondary/50"
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            ) : (
              <Textarea
                rows={question.type === "coding" ? 10 : 6}
                value={freeTextResponse}
                onChange={(e) => setFreeTextResponse(e.target.value)}
                placeholder={question.type === "coding" ? "Write your code here…" : "Write your answer here…"}
                className={question.type === "coding" ? "font-mono" : undefined}
              />
            )}

            <Button onClick={handleSubmitAnswer} disabled={submitAnswer.isPending} className="w-full">
              {submitAnswer.isPending ? "Submitting…" : "Submit & continue"}
            </Button>
          </CardContent>
        </Card>
      )}

      <Dialog open={autoSubmittedDialogOpen} onOpenChange={setAutoSubmittedDialogOpen}>
        <DialogContent onInteractOutside={(e) => e.preventDefault()}>
          <DialogHeader>
            <DialogTitle>Attempt auto-submitted</DialogTitle>
            <DialogDescription>
              Too many anti-cheat violations were detected, so this attempt was submitted automatically with your
              answers so far.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button onClick={() => router.replace(`/dashboard/assessments/results/${attemptId}`)}>
              View results
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
