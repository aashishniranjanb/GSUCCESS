import {
  SyllabusTreeResponse,
  TopicDetailResponse,
} from "./types";
import { StudyApiError } from "./study";

const getBaseUrl = (): string => {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }
  return process.env.INTERNAL_API_URL || "http://127.0.0.1:8000";
};

export async function fetchSyllabusTree(): Promise<SyllabusTreeResponse> {
  const url = `${getBaseUrl()}/api/syllabus/tree`;

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
      throw new StudyApiError(`Failed to fetch syllabus tree (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof StudyApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new StudyApiError(msg, 0);
  }
}

export async function fetchTopicDetail(topicId: string): Promise<TopicDetailResponse> {
  const url = `${getBaseUrl()}/api/syllabus/topic/${encodeURIComponent(topicId)}`;

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
      throw new StudyApiError(`Failed to fetch topic detail (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof StudyApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new StudyApiError(msg, 0);
  }
}
