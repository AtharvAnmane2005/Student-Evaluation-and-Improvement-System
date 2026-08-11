import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type {
  ApplicationDetail,
  ApplicationStatus,
  DriveCreateRequest,
  DriveDetail,
  DriveSummary,
  DriveUpdateRequest,
} from "@/types/drive";

const MY_DRIVES_KEY = ["drives", "mine"] as const;
const DRIVE_DETAIL_KEY = (id: string) => ["drives", id] as const;
const DRIVE_APPLICANTS_KEY = (driveId: string) => ["drives", driveId, "applications"] as const;

export function useMyDrives() {
  return useQuery({
    queryKey: MY_DRIVES_KEY,
    queryFn: async () => {
      const { data } = await apiClient.get<DriveSummary[]>("/drives/mine", { params: { limit: 100 } });
      return data;
    },
  });
}

export function useCreateDrive() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: DriveCreateRequest) => {
      const { data } = await apiClient.post<DriveDetail>("/drives", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: MY_DRIVES_KEY });
    },
  });
}

export function useUpdateDrive(driveId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: DriveUpdateRequest) => {
      const { data } = await apiClient.put<DriveDetail>(`/drives/${driveId}`, payload);
      return data;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(DRIVE_DETAIL_KEY(driveId), data);
      queryClient.invalidateQueries({ queryKey: MY_DRIVES_KEY });
    },
  });
}

export function useDeleteDrive() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (driveId: string) => {
      await apiClient.delete(`/drives/${driveId}`);
      return driveId;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: MY_DRIVES_KEY });
    },
  });
}

export function useDriveApplicants(driveId: string) {
  return useQuery({
    queryKey: DRIVE_APPLICANTS_KEY(driveId),
    queryFn: async () => {
      const { data } = await apiClient.get<ApplicationDetail[]>(`/drives/${driveId}/applications`);
      return data;
    },
    enabled: Boolean(driveId),
  });
}

export function useUpdateApplicationStatus(driveId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ applicationId, status }: { applicationId: string; status: ApplicationStatus }) => {
      const { data } = await apiClient.patch<ApplicationDetail>(
        `/drives/${driveId}/applications/${applicationId}`,
        { status }
      );
      return data;
    },
    onSuccess: (updated) => {
      queryClient.setQueryData<ApplicationDetail[]>(DRIVE_APPLICANTS_KEY(driveId), (prev) =>
        prev ? prev.map((a) => (a.id === updated.id ? updated : a)) : prev
      );
    },
  });
}
