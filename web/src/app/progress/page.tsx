"use client";

import React, { useState, useEffect, useCallback } from "react";
import { fetchStudentProgress, fetchRewardsOverview, RewardsOverview } from "@/lib/api/progress";
import { StudentProgressResponse } from "@/lib/api/types";
import { ProgressOverviewScreen } from "@/components/progress/progress-overview-screen";
import { SyllabusJourneyScreen } from "@/components/progress/syllabus-journey-screen";
import { StudyActivityScreen } from "@/components/progress/study-activity-screen";
import { PerformanceMasteryScreen } from "@/components/progress/performance-mastery-screen";
import { AchievementsRewardsScreen } from "@/components/progress/achievements-rewards-screen";
import { Skeleton, ErrorState } from "@/components/ui/states";
import {
  Sparkle,
  BookOpen,
  ChartBar,
  Target,
  Trophy,
} from "@phosphor-icons/react/dist/ssr";

type ProgressView = "overview" | "syllabus" | "activity" | "performance" | "achievements";

export default function ProgressPage() {
  const [activeView, setActiveView] = useState<ProgressView>("overview");
  const [progressData, setProgressData] = useState<StudentProgressResponse | null>(null);
  const [rewardsData, setRewardsData] = useState<RewardsOverview | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [prog, rew] = await Promise.all([
        fetchStudentProgress("student_01"),
        fetchRewardsOverview("student_01").catch(() => null),
      ]);
      setProgressData(prog);
      setRewardsData(rew);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load progress records.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  // Handle URL hash or param sync if needed
  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const tabParam = params.get("tab") as ProgressView | null;
      if (tabParam && ["overview", "syllabus", "activity", "performance", "achievements"].includes(tabParam)) {
        setActiveView(tabParam);
      }
    }
  }, []);

  const handleTabChange = (view: ProgressView) => {
    setActiveView(view);
    if (typeof window !== "undefined") {
      const url = new URL(window.location.href);
      if (view === "overview") {
        url.searchParams.delete("tab");
      } else {
        url.searchParams.set("tab", view);
      }
      window.history.pushState({}, "", url.toString());
    }
  };

  const navItems = [
    { id: "overview", label: "Overview", icon: Sparkle },
    { id: "syllabus", label: "Syllabus", icon: BookOpen },
    { id: "activity", label: "Activity", icon: ChartBar },
    { id: "performance", label: "Mastery", icon: Target },
    { id: "achievements", label: "Rewards", icon: Trophy },
  ] as const;

  const totalAwarded = rewardsData?.counts?.total_awarded || 3;
  const coinsBalance = totalAwarded * 40;

  return (
    <div className="max-w-3xl mx-auto px-4 py-4 sm:py-6 space-y-5 animate-enter pb-24">
      {/* 1. Global Progress Header */}
      <header className="flex items-center justify-between gap-3 pb-3 border-b border-[var(--color-border-subtle)]">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-xs uppercase tracking-wider text-emerald-400">
              GPAT 2027
            </span>
            <span className="text-[10px] text-[var(--color-text-tertiary)] font-mono">
              Learn &bull; Practice &bull; Grow
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-black tracking-tight text-[var(--color-text-primary)] mt-0.5 flex items-center gap-1.5">
            Your progress <span className="text-emerald-400 text-lg">🌱</span>
          </h1>
          <p className="text-xs text-[var(--color-text-secondary)]">
            Every session moves you forward.
          </p>
        </div>

        {/* Coins Pill Widget */}
        <button
          type="button"
          onClick={() => handleTabChange("achievements")}
          className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/15 border border-amber-500/30 hover:bg-amber-500/25 transition-colors cursor-pointer"
          title={`${totalAwarded} authentic milestones recorded in SQLite ledger`}
        >
          <div className="w-5 h-5 rounded-full bg-amber-400 flex items-center justify-center text-zinc-950 font-black text-[11px] shadow-xs">
            ★
          </div>
          <span className="font-mono text-xs font-bold text-amber-300">
            {coinsBalance}
          </span>
        </button>
      </header>

      {/* 2. Top Screen Navigation Tabs */}
      <nav
        className="flex items-center gap-1 p-1 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] overflow-x-auto"
        aria-label="Progress experience sections"
      >
        {navItems.map((item) => {
          const isSelected = activeView === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => handleTabChange(item.id)}
              className={`flex-1 min-w-[70px] py-2 px-2.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all select-none min-h-[40px] ${
                isSelected
                  ? "bg-[var(--color-accent)] text-zinc-950 font-bold shadow-xs"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface-base)]"
              }`}
            >
              <item.icon size={15} weight={isSelected ? "bold" : "regular"} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* 3. Screen View Switcher */}
      {loading ? (
        <div className="space-y-4 pt-2">
          <Skeleton className="h-44 w-full rounded-2xl" />
          <Skeleton className="h-32 w-full rounded-2xl" />
          <Skeleton className="h-28 w-full rounded-2xl" />
        </div>
      ) : error || !progressData ? (
        <div className="p-6 rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)]">
          <ErrorState
            title="Failed to Load Progress Data"
            message={error || "Could not connect to learner telemetry."}
            onRetry={loadData}
          />
        </div>
      ) : (
        <main className="transition-opacity duration-200">
          {activeView === "overview" && (
            <ProgressOverviewScreen
              progressData={progressData}
              rewardsData={rewardsData}
              onNavigateTab={handleTabChange}
            />
          )}

          {activeView === "syllabus" && (
            <SyllabusJourneyScreen
              onBackToOverview={() => handleTabChange("overview")}
            />
          )}

          {activeView === "activity" && (
            <StudyActivityScreen
              progressData={progressData}
              onBackToOverview={() => handleTabChange("overview")}
            />
          )}

          {activeView === "performance" && (
            <PerformanceMasteryScreen
              progressData={progressData}
              onBackToOverview={() => handleTabChange("overview")}
            />
          )}

          {activeView === "achievements" && (
            <AchievementsRewardsScreen
              rewardsData={rewardsData}
              onBackToOverview={() => handleTabChange("overview")}
            />
          )}
        </main>
      )}
    </div>
  );
}
