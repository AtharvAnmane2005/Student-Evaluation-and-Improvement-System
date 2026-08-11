import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { ResumeDetail, ResumeSummary, ResumeUploadResponse } from "@/types/resume";

const RESUME_HISTORY_KEY = ["resumes", "history"] as const;
const RESUME_DETAIL_KEY = (id: string) => ["resumes", id] as const;

export function useResumeHistory() {
  return useQuery({
    queryKey: RESUME_HISTORY_KEY,
    queryFn: async () => {
      const { data } = await apiClient.get<ResumeSummary[]>("/resumes/history");
      return data;
    },
  });
}

export function useResumeDetail(resumeId: string | null) {
  return useQuery({
    queryKey: resumeId ? RESUME_DETAIL_KEY(resumeId) : ["resumes", "none"],
    queryFn: async () => {
      const { data } = await apiClient.get<ResumeDetail>(`/resumes/${resumeId}`);
      return data;
    },
    enabled: Boolean(resumeId),
  });
}

export function useUploadResume() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await apiClient.post<ResumeUploadResponse>("/resumes", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: RESUME_HISTORY_KEY });
      queryClient.invalidateQueries({ queryKey: ["student-profile", "me"] });
    },
  });
}

export function useReparseResume() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (resumeId: string) => {
      const { data } = await apiClient.post<ResumeDetail>(`/resumes/${resumeId}/reparse`);
      return data;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(RESUME_DETAIL_KEY(data.id), data);
      queryClient.invalidateQueries({ queryKey: RESUME_HISTORY_KEY });
    },
  });
}

/**
 * The download endpoint requires the Authorization header (it's gated by
 * get_current_user, same as everything else) — a plain <a href> navigation
 * never attaches that header, only apiClient's axios interceptor does. So
 * this fetches the PDF as a blob and triggers a client-side save instead
 * of linking straight to the backend URL.
 */
export async function downloadResumeFile(resumeId: string, filename: string): Promise<void> {
  const response = await apiClient.get(`/resumes/${resumeId}/download`, { responseType: "blob" });
  const blobUrl = URL.createObjectURL(response.data as Blob);
  const link = document.createElement("a");
  link.href = blobUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(blobUrl);
}
