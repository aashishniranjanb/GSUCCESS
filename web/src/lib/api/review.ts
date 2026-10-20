import {
  ReviewQueueResponse,
  ReviewRatingRequest,
  ReviewRatingResponse,
} from "./types";
import { StudyApiError } from "./study";

const getBaseUrl = (): string => {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }
  return process.env.INTERNAL_API_URL || "http://127.0.0.1:8000";
};

export async function fetchReviewQueue(
  studentId: string = "student_01"
): Promise<ReviewQueueResponse> {
  const url = `${getBaseUrl()}/api/study/review-queue?student_id=${encodeURIComponent(studentId)}`;

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
      throw new StudyApiError(`Failed to fetch review queue (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof StudyApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new StudyApiError(msg, 0);
  }
}

export async function submitReviewRating(
  request: ReviewRatingRequest
): Promise<ReviewRatingResponse> {
  const url = `${getBaseUrl()}/api/study/review-rating`;

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown rating submission error");
      throw new StudyApiError(`Failed to submit review rating (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof StudyApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new StudyApiError(msg, 0);
  }
}
