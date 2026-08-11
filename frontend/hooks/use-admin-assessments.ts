import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { AssessmentCreateRequest, AssessmentResponse } from "@/types/assessment";

export function useCreateAssessment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: AssessmentCreateRequest) => {
      const { data } = await apiClient.post<AssessmentResponse>("/assessments", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["assessments"] });
    },
  });
}
