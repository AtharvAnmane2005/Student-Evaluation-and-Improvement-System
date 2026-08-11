export type DifficultyLevel = "easy" | "medium" | "hard";
export type QuestionType = "mcq" | "coding" | "descriptive";
export type AttemptStatus = "in_progress" | "submitted";

export interface AntiCheatConfig {
  max_violations?: number;
  require_fullscreen?: boolean;
  [key: string]: unknown;
}

export interface AssessmentCreateRequest {
  title: string;
  category_ids: string[];
  question_pool_size: number;
  time_limit_sec: number;
  max_violations: number;
  require_fullscreen: boolean;
}

export interface AssessmentResponse {
  id: string;
  title: string;
  category_ids: string[];
  question_pool_size: number;
  time_limit_sec: number;
  anti_cheat_config: AntiCheatConfig;
}

export interface QuestionStudentView {
  id: string;
  difficulty: DifficultyLevel;
  type: QuestionType;
  text: string;
  options: string[];
  marks: number;
}

export interface StartAttemptResponse {
  attempt_id: string;
  session_token: string;
  time_limit_sec: number;
  anti_cheat_config: AntiCheatConfig;
  next_question: QuestionStudentView | null;
}

export interface SubmitAnswerResponse {
  is_correct: boolean | null;
  marks_awarded: number;
  next_question: QuestionStudentView | null;
  attempt_status: AttemptStatus;
}

export interface ViolationReportResponse {
  violation_count: number;
  max_violations: number;
  attempt_status: AttemptStatus;
  auto_submitted: boolean;
}

export interface AttemptResultResponse {
  attempt_id: string;
  status: AttemptStatus;
  total_marks: number;
  max_possible_marks: number;
  questions_answered: number;
  started_at: string;
  submitted_at: string | null;
}

export interface KnowledgeStateResponse {
  skill_tag: string;
  mastery_pct: number;
  confidence: number;
  attempts_count: number;
}
