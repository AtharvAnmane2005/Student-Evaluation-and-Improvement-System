import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type {
  CategoryCreateRequest,
  CategoryResponse,
  QuestionAdminResponse,
  QuestionCreateRequest,
  QuestionUpdateRequest,
} from "@/types/question";

const CATEGORIES_KEY = ["admin", "categories"] as const;
const QUESTIONS_KEY = (categoryId?: string, difficulty?: string) =>
  ["admin", "questions", categoryId ?? "all", difficulty ?? "all"] as const;

export function useCategories() {
  return useQuery({
    queryKey: CATEGORIES_KEY,
    queryFn: async () => {
      const { data } = await apiClient.get<CategoryResponse[]>("/questions/categories");
      return data;
    },
  });
}

export function useCreateCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CategoryCreateRequest) => {
      const { data } = await apiClient.post<CategoryResponse>("/questions/categories", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CATEGORIES_KEY });
    },
  });
}

export function useQuestions(categoryId?: string, difficulty?: string) {
  return useQuery({
    queryKey: QUESTIONS_KEY(categoryId, difficulty),
    queryFn: async () => {
      const { data } = await apiClient.get<QuestionAdminResponse[]>("/questions", {
        params: { category_id: categoryId || undefined, difficulty: difficulty || undefined },
      });
      return data;
    },
  });
}

function invalidateAllQuestionLists(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.invalidateQueries({ queryKey: ["admin", "questions"] });
}

export function useCreateQuestion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: QuestionCreateRequest) => {
      const { data } = await apiClient.post<QuestionAdminResponse>("/questions", payload);
      return data;
    },
    onSuccess: () => invalidateAllQuestionLists(queryClient),
  });
}

export function useUpdateQuestion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: QuestionUpdateRequest }) => {
      const { data } = await apiClient.put<QuestionAdminResponse>(`/questions/${id}`, payload);
      return data;
    },
    onSuccess: () => invalidateAllQuestionLists(queryClient),
  });
}

export function useDeleteQuestion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/questions/${id}`);
      return id;
    },
    onSuccess: () => invalidateAllQuestionLists(queryClient),
  });
}

export function useImportQuestions() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: QuestionCreateRequest[]) => {
      const { data } = await apiClient.post<QuestionAdminResponse[]>("/questions/import", payload);
      return data;
    },
    onSuccess: () => invalidateAllQuestionLists(queryClient),
  });
}

export async function exportQuestions(categoryId?: string, difficulty?: string): Promise<QuestionAdminResponse[]> {
  const { data } = await apiClient.get<QuestionAdminResponse[]>("/questions/export", {
    params: { category_id: categoryId || undefined, difficulty: difficulty || undefined },
  });
  return data;
}
