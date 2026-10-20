import {
  DailySessionResponse,
  AttemptSubmissionRequest,
  AttemptFeedbackResponse,
} from "./types";

const getBaseUrl = (): string => {
  if (typeof window !== "undefined") {
    // Client-side: use configured env or fallback to same-origin / relative proxy or localhost:8000
    return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }
  return process.env.INTERNAL_API_URL || "http://127.0.0.1:8000";
};

export class StudyApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "StudyApiError";
    this.status = status;
  }
}

export async function fetchStudyToday(
  studentId: string = "student_01",
  minutes: number = 12,
  mode: string = "balanced"
): Promise<DailySessionResponse> {
  const url = `${getBaseUrl()}/api/study/today?student_id=${encodeURIComponent(
    studentId
  )}&minutes=${minutes}&mode=${encodeURIComponent(mode)}`;

  try {
    const res = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
      cache: "no-store",
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown server error");
      throw new StudyApiError(`Failed to fetch today session (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof StudyApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new StudyApiError(msg, 0);
  }
}

export async function submitStudyAttempt(
  submission: AttemptSubmissionRequest
): Promise<AttemptFeedbackResponse> {
  const url = `${getBaseUrl()}/api/study/attempt`;

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(submission),
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown submission error");
      throw new StudyApiError(`Failed to submit attempt (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof StudyApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new StudyApiError(msg, 0);
  }
}

export async function completeStudyMission(
  missionId: string
): Promise<{ status: string }> {
  const url = `${getBaseUrl()}/api/study/mission/${encodeURIComponent(missionId)}/complete`;

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json",
      },
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown completion error");
      throw new StudyApiError(`Failed to complete mission (${res.status}): ${errText}`, res.status);
    }

    return await res.json().catch(() => ({ status: "completed" }));
  } catch (err: unknown) {
    if (err instanceof StudyApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new StudyApiError(msg, 0);
  }
}
