import { LearnerLocalPreferences } from "./api/types";

const PREFERENCES_STORAGE_KEY = "gpat_learning_os_preferences";

export const DEFAULT_PREFERENCES: LearnerLocalPreferences = {
  preferredMissionDurationMinutes: 12,
  preferredReviewBatchSize: 10,
  reducedMotion: false,
  theme: "dark",
  notificationsEnabled: false,
  reminderTime: null,
  targetExamDate: "2027-02-02",
  targetExamLabel: "GPAT 2027 Learner Target (Unconfirmed)",
  learnerName: null,
};

export function getLocalPreferences(): LearnerLocalPreferences {
  if (typeof window === "undefined") {
    return DEFAULT_PREFERENCES;
  }
  try {
    const raw = localStorage.getItem(PREFERENCES_STORAGE_KEY);
    if (!raw) return DEFAULT_PREFERENCES;
    return { ...DEFAULT_PREFERENCES, ...JSON.parse(raw) };
  } catch {
    return DEFAULT_PREFERENCES;
  }
}

export function applyTheme(theme: "dark" | "light" | "warm-editorial"): void {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  root.setAttribute("data-theme", theme);
  if (theme === "light" || theme === "warm-editorial") {
    root.classList.remove("dark");
    root.classList.add("light");
  } else {
    root.classList.remove("light");
    root.classList.add("dark");
  }
}

export function saveLocalPreferences(prefs: Partial<LearnerLocalPreferences>): LearnerLocalPreferences {
  const current = getLocalPreferences();
  const updated = { ...current, ...prefs };
  if (typeof window !== "undefined") {
    try {
      localStorage.setItem(PREFERENCES_STORAGE_KEY, JSON.stringify(updated));
      if (prefs.theme) {
        applyTheme(prefs.theme);
      }
    } catch {
      // quota or private browsing silently handled
    }
  }
  return updated;
}
