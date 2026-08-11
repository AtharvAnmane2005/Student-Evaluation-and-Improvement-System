import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { AdminAnalytics, TpoAnalytics } from "@/types/analytics";

export function useTpoAnalytics() {
  return useQuery({
    queryKey: ["analytics", "tpo"],
    queryFn: async () => {
      const { data } = await apiClient.get<TpoAnalytics>("/analytics/tpo");
      return data;
    },
  });
}

export function useAdminAnalytics() {
  return useQuery({
    queryKey: ["analytics", "admin"],
    queryFn: async () => {
      const { data } = await apiClient.get<AdminAnalytics>("/analytics/admin");
      return data;
    },
  });
}
