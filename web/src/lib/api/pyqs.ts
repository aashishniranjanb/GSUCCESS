import {
  PYQYearItem,
  PYQListResponse,
  PYQDetailItem,
} from "./types";
import { StudyApiError } from "./study";

const getBaseUrl = (): string => {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }
  return process.env.INTERNAL_API_URL || "http://127.0.0.1:8000";
};

export async function fetchPYQYears(): Promise<PYQYearItem[]> {
  const url = `${getBaseUrl()}/api/pyqs/years`;

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
      throw new StudyApiError(`Failed to fetch PYQ years (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof StudyApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new StudyApiError(msg, 0);
  }
}

export async function fetchPYQList(
  year?: number | null,
  subjectId?: string | null,
  search?: string | null,
  page: number = 1,
  pageSize: number = 50
): Promise<PYQListResponse> {
  const params = new URLSearchParams();
  if (year !== undefined && year !== null) params.append("year", year.toString());
  if (subjectId) params.append("subject_id", subjectId);
  if (search && search.trim()) params.append("search", search.trim());
  params.append("page", page.toString());
  params.append("page_size", pageSize.toString());

  const url = `${getBaseUrl()}/api/pyqs/list?${params.toString()}`;

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
      throw new StudyApiError(`Failed to fetch PYQ list (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof StudyApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new StudyApiError(msg, 0);
  }
}

export async function fetchPYQDetail(questionId: string): Promise<PYQDetailItem> {
  const url = `${getBaseUrl()}/api/pyqs/${encodeURIComponent(questionId)}`;

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
      throw new StudyApiError(`Failed to fetch PYQ detail (${res.status}): ${errText}`, res.status);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof StudyApiError) throw err;
    const msg = err instanceof Error ? err.message : "Network unreachable / offline";
    throw new StudyApiError(msg, 0);
  }
}
