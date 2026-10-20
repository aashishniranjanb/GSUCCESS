import {
  MockBlueprintsResponse,
  MockCreateResponse,
  CreateMockOptions,
  MiniMockCoverageResponse,
  MockExamSession,
  MockEvaluationResult,
  MockHistoryItem,
} from "./types";

const getBaseUrl = (): string => {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }
  return process.env.INTERNAL_API_URL || "http://127.0.0.1:8000";
};

export class MockApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "MockApiError";
    this.status = status;
  }
}

/**
 * Fetch available blueprints from backend authoritative configuration.
 */
export async function fetchMockBlueprints(): Promise<MockBlueprintsResponse> {
  const url = `${getBaseUrl()}/api/mock/blueprints`;
  try {
    const res = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown server error");
      throw new MockApiError(`Failed to fetch mock blueprints (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof MockApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new MockApiError(msg, 0);
  }
}

/**
 * Create a new mock exam session with controlled blueprint constraints.
 * Supports string blueprintName or full CreateMockOptions for personalized mini mocks.
 */
export async function createMockExam(
  blueprintOrOptions: string | CreateMockOptions = "sprint_25",
  userId: string = "student_01"
): Promise<MockCreateResponse> {
  const url = `${getBaseUrl()}/api/mock/create`;
  const payload =
    typeof blueprintOrOptions === "string"
      ? {
          user_id: userId,
          blueprint_name: blueprintOrOptions,
        }
      : {
          user_id: blueprintOrOptions.userId || userId,
          blueprint_name: blueprintOrOptions.blueprintName || "mini_mock",
          custom_title: blueprintOrOptions.customTitle,
          question_count: blueprintOrOptions.questionCount,
          duration_minutes: blueprintOrOptions.durationMinutes,
          topic_ids: blueprintOrOptions.topicIds,
          subject_ids: blueprintOrOptions.subjectIds,
        };

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown server error");
      throw new MockApiError(`Failed to create mock exam (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof MockApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new MockApiError(msg, 0);
  }
}

/**
 * Start the exam timer on server and transition status to IN_PROGRESS.
 */
export async function startMockExam(
  examId: string,
  userId: string = "student_01"
): Promise<{ exam_id: string; status: string; started_at: string; remaining_seconds: number }> {
  const url = `${getBaseUrl()}/api/mock/${encodeURIComponent(examId)}/start?user_id=${encodeURIComponent(userId)}`;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { Accept: "application/json" },
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown server error");
      throw new MockApiError(`Failed to start mock exam (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof MockApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new MockApiError(msg, 0);
  }
}

/**
 * Retrieve full mock session state (questions, answers, server-authoritative timer).
 */
export async function fetchMockExam(
  examId: string,
  userId: string = "student_01"
): Promise<MockExamSession> {
  const url = `${getBaseUrl()}/api/mock/${encodeURIComponent(examId)}?user_id=${encodeURIComponent(userId)}`;
  try {
    const res = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown server error");
      throw new MockApiError(`Failed to fetch mock exam (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof MockApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new MockApiError(msg, 0);
  }
}

/**
 * Record an answer for a specific question in the mock exam session.
 */
export async function recordMockAnswer(
  examId: string,
  questionId: string,
  selectedOption: number | null,
  timeSpentMs: number = 0,
  confidence: number = 3,
  userId: string = "student_01"
): Promise<{ exam_id: string; question_id: string; status: string; answered_at: string }> {
  const url = `${getBaseUrl()}/api/mock/${encodeURIComponent(examId)}/answer`;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        user_id: userId,
        question_id: questionId,
        selected_option: selectedOption,
        time_spent_ms: timeSpentMs,
        confidence,
      }),
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown server error");
      throw new MockApiError(`Failed to record mock answer (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof MockApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new MockApiError(msg, 0);
  }
}

/**
 * Pause the mock exam session.
 */
export async function pauseMockExam(
  examId: string,
  userId: string = "student_01"
): Promise<{ exam_id: string; status: string; elapsed_seconds: number }> {
  const url = `${getBaseUrl()}/api/mock/${encodeURIComponent(examId)}/pause?user_id=${encodeURIComponent(userId)}`;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { Accept: "application/json" },
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown server error");
      throw new MockApiError(`Failed to pause mock exam (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof MockApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new MockApiError(msg, 0);
  }
}

/**
 * Authoritatively submit mock exam session for final scoring and 4-quadrant evaluation.
 */
export async function submitMockExam(
  examId: string,
  userId: string = "student_01"
): Promise<MockEvaluationResult> {
  const url = `${getBaseUrl()}/api/mock/${encodeURIComponent(examId)}/submit?user_id=${encodeURIComponent(userId)}`;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { Accept: "application/json" },
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown server error");
      throw new MockApiError(`Failed to submit mock exam (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof MockApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new MockApiError(msg, 0);
  }
}

/**
 * Retrieve past mock exam history for student.
 */
export async function fetchMockHistory(
  userId: string = "student_01"
): Promise<{ history: MockHistoryItem[] }> {
  const url = `${getBaseUrl()}/api/mock/history?user_id=${encodeURIComponent(userId)}`;
  try {
    const res = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown server error");
      throw new MockApiError(`Failed to fetch mock history (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof MockApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new MockApiError(msg, 0);
  }
}

/**
 * Fetch coverage analysis and eligible question counts for personalized mini mock.
 */
export async function fetchMiniMockCoverage(
  topicIds?: string[],
  subjectIds?: string[],
  requestedCount: number = 10
): Promise<MiniMockCoverageResponse> {
  const url = `${getBaseUrl()}/api/mock/mini-mock-coverage`;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        topic_ids: topicIds,
        subject_ids: subjectIds,
        requested_count: requestedCount,
      }),
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown server error");
      throw new MockApiError(`Failed to fetch mini mock coverage (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof MockApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new MockApiError(msg, 0);
  }
}
