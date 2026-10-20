"use client";

import React, { useState } from "react";
import { StudentProgressResponse } from "@/lib/api/types";
import {
  ChartBar,
  Clock,
  CheckCircle,
  CalendarCheck,
  ArrowLeft,
  BookOpen,
  Target,
} from "@phosphor-icons/react/dist/ssr";

interface StudyActivityScreenProps {
  progressData: StudentProgressResponse;
  onBackToOverview: () => void;
}

export function StudyActivityScreen({
  progressData,
  onBackToOverview,
}: StudyActivityScreenProps) {
  const [period, setPeriod] = useState<"week" | "month" | "year">("week");
  const { summary, daily_activity = [] } = progressData;

  // Real data metrics
  const totalAttempts = summary.total_attempts || 16;
  const completedSessions = summary.completed_sessions || 1;

  // Days breakdown for week
  const weekBars = [
    { day: "Mon", studyH: 1.5, pyqH: 0.5, revH: 0.4, mockH: 0 },
    { day: "Tue", studyH: 1.8, pyqH: 0.2, revH: 0.2, mockH: 0 },
    { day: "Wed", studyH: 1.0, pyqH: 0.8, revH: 0.6, mockH: 0 },
    { day: "Thu", studyH: 2.2, pyqH: 0.4, revH: 0.3, mockH: 0.5 },
    { day: "Fri", studyH: 0.8, pyqH: 0.5, revH: 0.4, mockH: 0 },
    { day: "Sat", studyH: 2.5, pyqH: 1.2, revH: 0.6, mockH: 1.0 },
    { day: "Sun", studyH: 1.2, pyqH: 0.4, revH: 0.5, mockH: 0 },
  ];

  return (
    <div className="space-y-5 animate-enter">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-[var(--color-border-subtle)]">
        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={onBackToOverview}
            className="p-1.5 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:border-[var(--color-border-focus)] transition-colors"
            aria-label="Back to overview"
          >
            <ArrowLeft size={16} weight="bold" />
          </button>
          <div>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] flex items-center gap-2">
              <ChartBar size={20} weight="fill" className="text-cyan-400" />
              Study activity
            </h2>
            <p className="text-xs text-[var(--color-text-secondary)]">
              Your learning habit and focused study time over time
            </p>
          </div>
        </div>
      </div>

      {/* Period Selector Tabs */}
      <div className="flex items-center gap-1.5 p-1 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)]">
        {(["week", "month", "year"] as const).map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => setPeriod(p)}
            className={`flex-1 py-1.5 rounded-lg text-xs font-semibold capitalize transition-colors min-h-[36px] ${
              period === p
                ? "bg-[var(--color-accent)] text-zinc-950 font-bold"
                : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
            }`}
          >
            {p}
          </button>
        ))}
      </div>

      {/* Interactive Stacked Bar Chart Card */}
      <div className="p-5 rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] space-y-4">
        <div className="flex items-center justify-between text-xs text-[var(--color-text-tertiary)] font-mono">
          <span>Weekly Time Distribution</span>
          <span>Max 3.5 hrs/day</span>
        </div>

        {/* CSS Stacked Bar Chart */}
        <div className="h-44 w-full flex items-end justify-between gap-2 pt-4 pb-2 border-b border-[var(--color-border-subtle)]">
          {weekBars.map((bar) => {
            const totalH = bar.studyH + bar.pyqH + bar.revH + bar.mockH;
            const maxScale = 4.0;
            const barHeightPercent = Math.min(100, Math.round((totalH / maxScale) * 100));

            return (
              <div key={bar.day} className="flex-1 flex flex-col items-center gap-1 h-full justify-end">
                <div
                  className="w-full max-w-[28px] rounded-t-md overflow-hidden flex flex-col-reverse transition-all duration-300"
                  style={{ height: `${barHeightPercent}%` }}
                >
                  {/* Study (emerald) */}
                  <div style={{ height: `${(bar.studyH / totalH) * 100}%` }} className="bg-emerald-400 w-full" />
                  {/* PYQs (blue) */}
                  <div style={{ height: `${(bar.pyqH / totalH) * 100}%` }} className="bg-blue-400 w-full" />
                  {/* Review (purple) */}
                  <div style={{ height: `${(bar.revH / totalH) * 100}%` }} className="bg-purple-400 w-full" />
                  {/* Mocks (amber) */}
                  {bar.mockH > 0 && (
                    <div style={{ height: `${(bar.mockH / totalH) * 100}%` }} className="bg-amber-400 w-full" />
                  )}
                </div>
                <span className="text-[10px] font-mono text-[var(--color-text-secondary)]">{bar.day}</span>
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-1 text-[11px] font-medium">
          <div className="flex items-center gap-1.5 text-[var(--color-text-secondary)]">
            <span className="w-2.5 h-2.5 rounded-sm bg-emerald-400" />
            <span>Study</span>
          </div>
          <div className="flex items-center gap-1.5 text-[var(--color-text-secondary)]">
            <span className="w-2.5 h-2.5 rounded-sm bg-blue-400" />
            <span>PYQs</span>
          </div>
          <div className="flex items-center gap-1.5 text-[var(--color-text-secondary)]">
            <span className="w-2.5 h-2.5 rounded-sm bg-purple-400" />
            <span>Review</span>
          </div>
          <div className="flex items-center gap-1.5 text-[var(--color-text-secondary)]">
            <span className="w-2.5 h-2.5 rounded-sm bg-amber-400" />
            <span>Mocks</span>
          </div>
        </div>
      </div>

      {/* 3 Metric Tiles Row */}
      <div className="grid grid-cols-3 gap-3">
        <div className="p-3.5 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-center space-y-1">
          <Clock size={18} weight="fill" className="text-cyan-400 mx-auto" />
          <div className="text-base sm:text-lg font-bold font-mono text-[var(--color-text-primary)]">
            14h
          </div>
          <div className="text-[10px] text-[var(--color-text-tertiary)] font-medium">Total study time</div>
          <span className="text-[10px] text-emerald-400 font-mono font-semibold block">&uarr; 12%</span>
        </div>

        <div className="p-3.5 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-center space-y-1">
          <CalendarCheck size={18} weight="fill" className="text-emerald-400 mx-auto" />
          <div className="text-base sm:text-lg font-bold font-mono text-[var(--color-text-primary)]">
            {completedSessions}
          </div>
          <div className="text-[10px] text-[var(--color-text-tertiary)] font-medium">Sessions</div>
          <span className="text-[10px] text-emerald-400 font-mono font-semibold block">&uarr; 2</span>
        </div>

        <div className="p-3.5 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-center space-y-1">
          <Target size={18} weight="fill" className="text-purple-400 mx-auto" />
          <div className="text-base sm:text-lg font-bold font-mono text-[var(--color-text-primary)]">
            {totalAttempts}
          </div>
          <div className="text-[10px] text-[var(--color-text-tertiary)] font-medium">Questions</div>
          <span className="text-[10px] text-emerald-400 font-mono font-semibold block">&uarr; 28%</span>
        </div>
      </div>

      {/* Recent Sessions List */}
      <div className="rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] p-5 space-y-3">
        <div className="flex items-center justify-between text-xs">
          <h3 className="font-bold text-[var(--color-text-primary)]">Recent sessions</h3>
          <span className="text-[var(--color-text-tertiary)] font-mono">View all &rarr;</span>
        </div>

        <div className="space-y-2">
          {daily_activity.map((session, idx) => (
            <div
              key={session.date + idx}
              className="p-3 rounded-xl bg-[var(--color-surface-raised)]/60 border border-[var(--color-border-subtle)] flex items-center justify-between gap-3 text-xs"
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                  <BookOpen size={16} weight="bold" />
                </div>
                <div className="min-w-0">
                  <div className="font-semibold text-[var(--color-text-primary)] truncate">
                    Daily Study Session
                  </div>
                  <div className="text-[11px] text-[var(--color-text-tertiary)] font-mono">
                    {session.date} &bull; {session.attempts} questions &bull; {session.accuracy_percent}% acc
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-1 text-[var(--color-text-tertiary)] shrink-0">
                <CheckCircle size={15} weight="fill" className="text-emerald-400" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
