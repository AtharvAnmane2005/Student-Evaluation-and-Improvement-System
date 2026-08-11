export type DriveStatus = "open" | "closed";
export type ApplicationStatus = "applied" | "shortlisted" | "rejected" | "selected";

export interface EligibilityCriteria {
  min_cgpa: number | null;
  departments: string[];
  batch_years: number[];
}

export interface CompanySummary {
  id: string;
  name: string;
  description: string | null;
  website: string | null;
  industry: string | null;
}

export interface DriveSummary {
  id: string;
  company: CompanySummary;
  job_title: string;
  package: string | null;
  location: string | null;
  deadline: string;
  status: DriveStatus;
  required_skills: string[];
}

export interface DriveDetail extends DriveSummary {
  description: string;
  jd_text: string;
  eligibility: EligibilityCriteria;
  selection_process: string[];
  experience_required_years: number;
  created_at: string;
}

export interface ApplicationResponse {
  id: string;
  drive_id: string;
  student_id: string;
  resume_id: string;
  status: ApplicationStatus;
  applied_at: string;
}

export interface ApplicationDetail extends ApplicationResponse {
  student_name: string;
  student_department: string | null;
  student_cgpa: number | null;
  resume_filename: string | null;
}

export interface DriveCreateRequest {
  company_name: string;
  company_description?: string;
  company_website?: string;
  company_industry?: string;
  job_title: string;
  description: string;
  jd_text: string;
  required_skills: string[];
  experience_required_years?: number;
  package?: string;
  location?: string;
  eligibility: EligibilityCriteria;
  deadline: string;
  selection_process: string[];
}

export interface DriveUpdateRequest {
  job_title?: string;
  description?: string;
  jd_text?: string;
  required_skills?: string[];
  experience_required_years?: number;
  package?: string;
  location?: string;
  eligibility?: EligibilityCriteria;
  deadline?: string;
  selection_process?: string[];
  status?: DriveStatus;
}
