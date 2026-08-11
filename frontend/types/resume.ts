export interface ParsedResumeData {
  name: string | null;
  email: string | null;
  phone: string | null;
  education: Record<string, unknown>[];
  experience: Record<string, unknown>[];
  projects: Record<string, unknown>[];
  skills: string[];
  certifications: string[];
  achievements: string[];
  languages: string[];
}

export interface ResumeSummary {
  id: string;
  version: number;
  original_filename: string;
  uploaded_at: string;
  is_active: boolean;
}

export interface ResumeUploadResponse extends ResumeSummary {
  file_size_bytes: number;
}

export interface ResumeDetail extends ResumeSummary {
  parsed: ParsedResumeData | null;
  skill_set: string[];
  experience_years: number | null;
}
