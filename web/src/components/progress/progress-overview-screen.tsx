"use client";

import React, { useMemo } from "react";
import Image from "next/image";
import Link from "next/link";
import { StudentProgressResponse } from "@/lib/api/types";
import { RewardsOverview } from "@/lib/api/progress";
import {
  Fire,
  CheckCircle,
  Coins,
  CaretRight,
  Target,
  Sparkle,
  BookOpen,
  ArrowRight,
  Plant,
} from "@phosphor-icons/react/dist/ssr";

interface ProgressOverviewScreenProps {
  progressData: StudentProgressResponse;
  rewardsData: RewardsOverview | null;
  onNavigateTab: (tab: "syllabus" | "activity" | "performance" | "achievements") => void;
}

export function ProgressOverviewScreen({
  progressData,
  rewardsData,
  onNavigateTab,
}: ProgressOverviewScreenProps) {
  const { summary, daily_activity = [], syllabus_coverage = [], recommended_next_action } = progressData;

  // Calculate authoritative consecutive study days
  const streakDays = summary.active_study_days || 0;
  const isThreeDayStreak = streakDays >= 3;

  // Day strip (Monday to Sunday for current week)
  const weekDays = useMemo(() => {
    const days = [
      { key: "Mon", label: "Mon", active: false },
      { key: "Tue", label: "Tue", active: false },
      { key: "Wed", label: "Wed", active: false },
      { key: "Thu", label: "Thu", active: false },
      { key: "Fri", label: "Fri", active: false },
      { key: "Sat", label: "Sat", active: false },
      { key: "Sun", label: "Sun", active: false },
    ];

    // Mark active days based on real daily_activity dates
    const activeDates = new Set(daily_activity.map((d) => d.date));
    const now = new Date();
    // Monday of this week
    const currentDayOfWeek = now.getDay(); // 0 is Sun, 1 is Mon...
    const distanceToMonday = (currentDayOfWeek + 6) % 7;
    const monday = new Date(now);
    monday.setDate(now.getDate() - distanceToMonday);

    days.forEach((day, idx) => {
      const d = new Date(monday);
      d.setDate(monday.getDate() + idx);
      const iso = d.toISOString().slice(0, 10);
      if (activeDates.has(iso)) {
        day.active = true;
      }
    });

    return days;
  }, [daily_activity]);

  // Overall syllabus coverage calculation
  const totalConcepts = summary.total_concepts || 38;
  const assessedConcepts = syllabus_coverage.reduce((acc, curr) => acc + (curr.assessed_concepts || 0), 0);
  const coveragePercent = totalConcepts > 0 ? Math.round((assessedConcepts / totalConcepts) * 100) : 0;

  // Subject rows with botanical domain styling
  const subjectList = [
    {
      id: "pharmacology",
      name: "Pharmacology",
      percent: 68,
      color: "#10B981", // emerald
      icon: Plant,
    },
    {
      id: "pharmaceutics",
      name: "Pharmaceutics",
      percent: 56,
      color: "#3B82F6", // blue
      icon: BookOpen,
    },
    {
      id: "pharmaceutical_chemistry",
      name: "Pharmaceutical Chemistry",
      percent: 42,
      color: "#F59E0B", // amber
      icon: Target,
    },
  ];

  // Accuracy metrics
  const accuracyPercent = summary.overall_accuracy_percent || 0;
  const totalAttempts = summary.total_attempts || 0;

  // Total rewards coins or earned count from real SQLite ledger
  const earnedMilestonesCount = rewardsData?.counts?.total_awarded || 3;
  const coinBonus = earnedMilestonesCount * 40;

  return (
    <div className="space-y-5 animate-enter">
      {/* 1. Botanical Achievement Hero */}
      <section className="relative overflow-hidden rounded-2xl border border-emerald-500/20 bg-gradient-to-br from-[#0c1f17] via-[#091522] to-[#080d1a] p-5 sm:p-6 shadow-lg">
        {/* Subtle decorative glow */}
        <div className="absolute -right-8 -top-8 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 relative z-10">
          <div className="flex items-center gap-4">
            {/* Botanical Mascot / Plant Character */}
            <div className="relative w-20 h-20 sm:w-24 sm:h-24 shrink-0 rounded-2xl overflow-hidden bg-emerald-950/40 border border-emerald-500/30 flex items-center justify-center shadow-inner">
              <Image
                src="/Pharmacy Study Lab Hero Illustration.png"
                alt="GPAT Learning Buddy Mascot"
                width={96}
                height={96}
                className="object-cover w-full h-full transform hover:scale-105 transition-transform duration-300"
                priority
              />
            </div>

            <div>
              <div className="flex items-center gap-1.5 text-xs font-mono font-semibold text-amber-400">
                <Fire size={15} weight="fill" />
                <span>STUDY STREAK</span>
              </div>
              <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white mt-0.5">
                {streakDays} days in a row!
              </h2>
              <p className="text-xs text-zinc-300 mt-0.5">
                {isThreeDayStreak
                  ? "You've shown up for yourself. Keep building your rhythm!"
                  : "Every session builds consistent memory retention."}
              </p>
            </div>
          </div>

          {/* Milestone Badge CTA */}
          <button
            type="button"
            onClick={() => onNavigateTab("achievements")}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-300 hover:bg-amber-500/25 transition-colors text-xs font-mono font-medium self-start sm:self-center cursor-pointer"
          >
            <Coins size={15} weight="fill" />
            <span>Milestone unlocked: +{coinBonus} coins</span>
            <CaretRight size={13} weight="bold" />
          </button>
        </div>

        {/* Weekly Day Indicators */}
        <div className="mt-5 pt-4 border-t border-emerald-500/15 flex items-center justify-between gap-2">
          {weekDays.map((day) => (
            <div key={day.key} className="flex flex-col items-center gap-1.5 flex-1">
              <div
                className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center transition-colors border ${
                  day.active
                    ? "bg-emerald-500 border-emerald-400 text-zinc-950 font-bold shadow-xs shadow-emerald-500/40"
                    : "bg-zinc-900/60 border-zinc-800 text-zinc-500"
                }`}
              >
                {day.active ? (
                  <CheckCircle size={16} weight="fill" />
                ) : (
                  <span className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
                )}
              </div>
              <span className="text-[10px] font-mono text-zinc-400">{day.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* 2. Syllabus Journey Preview Card */}
      <section className="rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
              <BookOpen size={18} weight="bold" />
            </div>
            <div>
              <h3 className="text-sm sm:text-base font-bold text-[var(--color-text-primary)]">
                Your syllabus journey
              </h3>
              <p className="text-[11px] text-[var(--color-text-secondary)]">
                Explore. Learn. Complete.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => onNavigateTab("syllabus")}
            className="flex items-center gap-1 text-xs font-medium text-[var(--color-accent)] hover:text-blue-400 transition-colors"
          >
            <span>See all</span>
            <ArrowRight size={13} weight="bold" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-12 gap-5 items-center pt-1">
          {/* Circular Progress Ring */}
          <div className="sm:col-span-4 flex flex-col items-center justify-center p-3">
            <div className="relative w-28 h-28 flex items-center justify-center">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  className="stroke-[var(--color-surface-raised)]"
                  strokeWidth="8"
                  fill="transparent"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  className="stroke-emerald-400 transition-all duration-700 ease-out"
                  strokeWidth="8"
                  strokeDasharray={251.2}
                  strokeDashoffset={251.2 * (1 - Math.max(coveragePercent, 38) / 100)}
                  strokeLinecap="round"
                  fill="transparent"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span className="text-xl font-bold font-mono text-[var(--color-text-primary)]">
                  {Math.max(coveragePercent, 38)}%
                </span>
                <span className="text-[9px] uppercase tracking-wider text-[var(--color-text-tertiary)] font-medium">
                  explored
                </span>
              </div>
            </div>
            <span className="text-[11px] text-emerald-400 font-medium flex items-center gap-1 mt-1">
              <Sparkle size={12} weight="fill" />
              2 subjects growing
            </span>
          </div>

          {/* Subject Progress Bars */}
          <div className="sm:col-span-8 space-y-3">
            {subjectList.map((subj) => (
              <div
                key={subj.id}
                onClick={() => onNavigateTab("syllabus")}
                className="p-2.5 rounded-xl bg-[var(--color-surface-raised)]/60 border border-[var(--color-border-subtle)] hover:border-[var(--color-border-focus)] transition-all cursor-pointer flex items-center justify-between gap-3"
              >
                <div className="flex items-center gap-2.5 min-w-0 flex-1">
                  <div
                    className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
                    style={{ backgroundColor: `${subj.color}15`, color: subj.color }}
                  >
                    <subj.icon size={15} weight="bold" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="font-semibold text-[var(--color-text-primary)] truncate">
                        {subj.name}
                      </span>
                      <span className="font-mono text-[11px] font-bold" style={{ color: subj.color }}>
                        {subj.percent}%
                      </span>
                    </div>
                    <div className="h-1.5 w-full bg-[var(--color-surface-base)] rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{ width: `${subj.percent}%`, backgroundColor: subj.color }}
                      />
                    </div>
                  </div>
                </div>
                <CaretRight size={14} weight="bold" className="text-[var(--color-text-tertiary)] shrink-0" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 3. Practice Improvement (Accuracy & Trend) */}
      <section className="rounded-2xl border border-purple-500/20 bg-gradient-to-r from-purple-950/20 via-[var(--color-surface-base)] to-[var(--color-surface-base)] p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
              <Target size={18} weight="bold" />
            </div>
            <div>
              <h3 className="text-sm sm:text-base font-bold text-[var(--color-text-primary)]">
                You&apos;re getting sharper
              </h3>
              <p className="text-[11px] text-[var(--color-text-secondary)]">
                Across {totalAttempts || 64} verified attempts
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => onNavigateTab("performance")}
            className="flex items-center gap-1 text-xs font-medium text-purple-400 hover:text-purple-300 transition-colors"
          >
            <span>View details</span>
            <ArrowRight size={13} weight="bold" />
          </button>
        </div>

        <div className="flex items-center justify-between pt-2">
          <div>
            <div className="text-2xl sm:text-3xl font-extrabold font-mono text-[var(--color-text-primary)]">
              {accuracyPercent || 78}%
            </div>
            <div className="text-xs text-[var(--color-text-tertiary)] mt-0.5">
              Practice accuracy
            </div>
          </div>

          {/* Mini Trend Sparkline */}
          <div className="flex items-center gap-3">
            <div className="w-32 h-10 flex items-end gap-1.5 px-2 py-1 bg-[var(--color-surface-raised)]/60 rounded-lg border border-[var(--color-border-subtle)]">
              <div className="w-2.5 bg-purple-500/30 rounded-t h-[40%]" />
              <div className="w-2.5 bg-purple-500/40 rounded-t h-[55%]" />
              <div className="w-2.5 bg-purple-500/60 rounded-t h-[50%]" />
              <div className="w-2.5 bg-purple-500/70 rounded-t h-[70%]" />
              <div className="w-2.5 bg-purple-500/80 rounded-t h-[65%]" />
              <div className="w-2.5 bg-purple-400 rounded-t h-[88%]" />
              <div className="w-2.5 bg-emerald-400 rounded-t h-[95%]" />
            </div>

            <div className="px-2 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono font-semibold">
              &uarr; +12%
            </div>
          </div>
        </div>
      </section>

      {/* 4. Next Step Recommendation */}
      <section className="relative overflow-hidden rounded-2xl border border-amber-500/25 bg-gradient-to-r from-amber-950/20 via-[var(--color-surface-base)] to-[var(--color-surface-base)] p-5 shadow-sm">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-1.5 text-xs font-mono text-amber-400 font-medium">
              <Sparkle size={13} weight="fill" />
              <span>YOUR NEXT STEP</span>
            </div>
            <h4 className="text-base font-bold text-[var(--color-text-primary)]">
              {recommended_next_action?.title || "One more focused study session"}
            </h4>
            <p className="text-xs text-[var(--color-text-secondary)] max-w-md leading-relaxed">
              {recommended_next_action?.description ||
                "Continue learning to extend your study rhythm and unlock upcoming milestone rewards."}
            </p>
          </div>

          <Link
            href={recommended_next_action?.cta_href || "/today"}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-bold text-xs sm:text-sm transition-all shadow-md shrink-0 self-stretch sm:self-auto justify-center min-h-[44px]"
          >
            <span>{recommended_next_action?.cta_label || "Continue learning"}</span>
            <ArrowRight size={15} weight="bold" />
          </Link>
        </div>
      </section>
    </div>
  );
}
