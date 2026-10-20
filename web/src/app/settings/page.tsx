"use client";

import React, { useState, useEffect, useCallback } from "react";
import { fetchLearnerRewards, SettingsApiError } from "@/lib/api/settings";
import { LearnerRewardsResponse } from "@/lib/api/types";
import { SettingsWorkspace } from "@/components/settings/settings-workspace";
import { ErrorState, Skeleton } from "@/components/ui/states";

export default function SettingsPage() {
  const [rewards, setRewards] = useState<LearnerRewardsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const loadSettingsData = useCallback(async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetchLearnerRewards("student_01");
      setRewards(res);
    } catch (err: unknown) {
      const msg = err instanceof SettingsApiError ? err.message : "Failed to load learner settings.";
      setErrorMsg(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSettingsData();
  }, [loadSettingsData]);

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto py-6 animate-enter">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-4 w-96" />
        <div className="space-y-4 mt-6">
          <Skeleton className="h-40 rounded-lg" />
          <Skeleton className="h-48 rounded-lg" />
          <Skeleton className="h-44 rounded-lg" />
        </div>
      </div>
    );
  }

  if (errorMsg || !rewards) {
    return (
      <div className="max-w-md mx-auto py-12">
        <ErrorState
          title="Settings Unavailable"
          message={errorMsg || "Could not retrieve learner configuration."}
          onRetry={loadSettingsData}
        />
      </div>
    );
  }

  return <SettingsWorkspace initialRewards={rewards} onRefresh={loadSettingsData} />;
}
