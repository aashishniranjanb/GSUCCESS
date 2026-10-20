import { StudentProgressResponse } from "./types";

const getBaseUrl = (): string => {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }
  return process.env.INTERNAL_API_URL || "http://127.0.0.1:8000";
};

export class ProgressApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ProgressApiError";
    this.status = status;
  }
}

export interface RewardsOverview {
  student_id: string;
  weekly_goal: {
    goal_type: string;
    target_count: number;
    achieved_count: number;
    is_met: boolean;
    status: string;
    week_range: string;
    iso_week: string;
  };
  counts: {
    mission_completed: number;
    delayed_recall: number;
    misconception_repaired: number;
    topic_mastery: number;
    personal_best: number;
    total_awarded: number;
  };
  achievements: Array<{
    id: string;
    achievement_type: string;
    title: string;
    description: string;
    evidence_type: string;
    evidence_id: string;
    metadata: Record<string, unknown>;
    awarded_at: string;
  }>;
}

/**
 * Fetch authoritative learner progress, activity history, and FSRS workload from backend.
 */
export async function fetchStudentProgress(
  studentId: string = "student_01"
): Promise<StudentProgressResponse> {
  const url = `${getBaseUrl()}/api/progress?student_id=${encodeURIComponent(studentId)}`;
  try {
    const res = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown server error");
      throw new ProgressApiError(`Failed to fetch student progress (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof ProgressApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new ProgressApiError(msg, 0);
  }
}

/**
 * Fetch authoritative rewards, weekly goals, and milestone achievements from SQLite ledger.
 */
export async function fetchRewardsOverview(
  studentId: string = "student_01"
): Promise<RewardsOverview> {
  const url = `${getBaseUrl()}/api/rewards?student_id=${encodeURIComponent(studentId)}`;
  try {
    const res = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown server error");
      throw new ProgressApiError(`Failed to fetch rewards (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof ProgressApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new ProgressApiError(msg, 0);
  }
}
