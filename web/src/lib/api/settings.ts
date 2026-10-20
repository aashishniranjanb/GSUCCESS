import { LearnerRewardsResponse, WeeklyStudyGoal } from "./types";

const getBaseUrl = (): string => {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }
  return process.env.INTERNAL_API_URL || "http://127.0.0.1:8000";
};

export class SettingsApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "SettingsApiError";
    this.status = status;
  }
}

/**
 * Fetch authoritative weekly study goal and rewards for the student.
 */
export async function fetchLearnerRewards(
  studentId: string = "student_01"
): Promise<LearnerRewardsResponse> {
  const url = `${getBaseUrl()}/api/rewards?student_id=${encodeURIComponent(studentId)}`;
  try {
    const res = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown server error");
      throw new SettingsApiError(`Failed to fetch rewards (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof SettingsApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new SettingsApiError(msg, 0);
  }
}

/**
 * Update the student's weekly study goal with authoritative persistence in SQLite.
 */
export async function updateWeeklyGoal(
  studentId: string = "student_01",
  targetCount: number = 5,
  status: string = "active",
  goalType: string = "completed_missions"
): Promise<{ status: string; goal: WeeklyStudyGoal }> {
  const url = `${getBaseUrl()}/api/rewards/goal`;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        student_id: studentId,
        target_count: targetCount,
        status,
        goal_type: goalType,
      }),
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown server error");
      throw new SettingsApiError(`Failed to update weekly goal (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof SettingsApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new SettingsApiError(msg, 0);
  }
}
