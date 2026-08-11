import type { DifficultyLevel, QuestionType } from "@/types/assessment";

export interface CategoryResponse {
  id: string;
  name: string;
  parent_category_id: string | null;
}

export interface CategoryCreateRequest {
  name: string;
  parent_category_id?: string;
}

export interface QuestionAdminResponse {
  id: string;
  category_id: string;
  skill_tags: string[];
  difficulty: DifficultyLevel;
  type: QuestionType;
  text: string;
  options: string[];
  correct_answer: string | null;
  marks: number;
  company_tags: string[];
}

export interface QuestionCreateRequest {
  category_id: string;
  skill_tags: string[];
  difficulty: DifficultyLevel;
  type: QuestionType;
  text: string;
  options: string[];
  correct_answer?: string;
  company_tags: string[];
}

export interface QuestionUpdateRequest {
  category_id?: string;
  skill_tags?: string[];
  difficulty?: DifficultyLevel;
  type?: QuestionType;
  text?: string;
  options?: string[];
  correct_answer?: string;
  company_tags?: string[];
}
