export interface ApplicationStatusBreakdown {
  applied: number;
  shortlisted: number;
  rejected: number;
  selected: number;
}

export interface DriveFunnel {
  drive_id: string;
  job_title: string;
  company_name: string;
  status: string;
  total_applications: number;
  breakdown: ApplicationStatusBreakdown;
}

export interface TpoAnalytics {
  total_drives: number;
  open_drives: number;
  closed_drives: number;
  total_applications: number;
  breakdown: ApplicationStatusBreakdown;
  selection_rate_pct: number;
  drives: DriveFunnel[];
}

export interface SkillMasteryOverview {
  skill_tag: string;
  avg_mastery_pct: number;
  student_count: number;
}

export interface AdminAnalytics {
  total_students: number;
  total_tpos: number;
  total_drives: number;
  open_drives: number;
  closed_drives: number;
  total_applications: number;
  application_breakdown: ApplicationStatusBreakdown;
  placed_students: number;
  placement_rate_pct: number;
  total_categories: number;
  total_questions: number;
  total_assessments: number;
  total_attempts: number;
  submitted_attempts: number;
  average_score_pct: number;
  skill_mastery_overview: SkillMasteryOverview[];
}
