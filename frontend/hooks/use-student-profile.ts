import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { StudentProfile, StudentProfileUpdate } from "@/types/student";

const STUDENT_PROFILE_KEY = ["student-profile", "me"] as const;

export function useStudentProfile() {
  return useQuery({
    queryKey: STUDENT_PROFILE_KEY,
    queryFn: async () => {
      const { data } = await apiClient.get<StudentProfile>("/students/me");
      return data;
    },
  });
}

export function useUpdateStudentProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: StudentProfileUpdate) => {
      const { data } = await apiClient.put<StudentProfile>("/students/me", payload);
      return data;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(STUDENT_PROFILE_KEY, data);
    },
  });
}
