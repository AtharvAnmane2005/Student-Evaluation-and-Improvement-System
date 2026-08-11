import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { DriveMatchScore, RankedApplicant, RecommendedDrive } from "@/types/matching";

/**
 * All three hooks treat a 503 (MatchingUnavailableError — model artifacts
 * not present in this deployment, see artifacts/README.md) as "no data"
 * rather than a hard error, so pages can render a normal empty/unavailable
 * state instead of an error boundary. Everything else in the app works
 * fine without the matching models present; these hooks shouldn't make it
 * look broken.
 */
function isMatchingUnavailable(error: unknown): boolean {
  return (error as any)?.response?.status === 503;
}

export function useDriveMatchScore(driveId: string) {
  return useQuery({
    queryKey: ["matching", "drive-score", driveId],
    queryFn: async () => {
      const { data } = await apiClient.get<DriveMatchScore>(`/matching/drives/${driveId}/score`);
      return data;
    },
    enabled: Boolean(driveId),
    retry: (failureCount, error) => !isMatchingUnavailable(error) && failureCount < 2,
  });
}

export function useRecommendedDrives(limit = 5) {
  return useQuery({
    queryKey: ["matching", "recommended-drives", limit],
    queryFn: async () => {
      const { data } = await apiClient.get<RecommendedDrive[]>("/matching/recommended-drives", { params: { limit } });
      return data;
    },
    retry: (failureCount, error) => !isMatchingUnavailable(error) && failureCount < 2,
  });
}

export function useRankedApplicants(driveId: string) {
  return useQuery({
    queryKey: ["matching", "ranked-applicants", driveId],
    queryFn: async () => {
      const { data } = await apiClient.get<RankedApplicant[]>(`/matching/drives/${driveId}/ranked-applicants`);
      return data;
    },
    enabled: Boolean(driveId),
    retry: (failureCount, error) => !isMatchingUnavailable(error) && failureCount < 2,
  });
}
