"use client";

import React, { useState } from "react";
import { StudentProgressResponse } from "@/lib/api/types";
import {
  Target,
  ArrowLeft,
  Plant,
  Flask,
  Atom,
  Drop,
  Dna,
} from "@phosphor-icons/react/dist/ssr";

interface PerformanceMasteryScreenProps {
  progressData: StudentProgressResponse;
  onBackToOverview: () => void;
}

export function PerformanceMasteryScreen({
  progressData,
  onBackToOverview,
}: PerformanceMasteryScreenProps) {
  const [subView, setSubView] = useState<"overview" | "subjects" | "topics">("overview");
  const { summary } = progressData;

  const totalAttempts = summary.total_attempts || 16;
  const totalCorrect = summary.total_correct || 7;
  const totalIncorrect = summary.total_incorrect || 9;
  const accuracyPercent = summary.overall_accuracy_percent || 43.8;

  const subjects = [
    { name: "Pharmacology", percent: 68, color: "#10B981", icon: Plant },
    { name: "Pharmaceutics", percent: 56, color: "#3B82F6", icon: Flask },
    { name: "Pharmaceutical Chemistry", percent: 42, color: "#F59E0B", icon: Atom },
    { name: "Pharmacognosy", percent: 38, color: "#8B5CF6", icon: Drop },
    { name: "Biotechnology & Allied", percent: 48, color: "#06B6D4", icon: Dna },
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
              <Target size={20} weight="fill" className="text-purple-400" />
              Performance &amp; mastery
            </h2>
            <p className="text-xs text-[var(--color-text-secondary)]">
              Track your accuracy, cognitive calibration, and topic stability
            </p>
          </div>
        </div>
      </div>

      {/* Sub Tabs */}
      <div className="flex items-center gap-1.5 p-1 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)]">
        {(["overview", "subjects", "topics"] as const).map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setSubView(tab)}
            className={`flex-1 py-1.5 rounded-lg text-xs font-semibold capitalize transition-colors min-h-[36px] ${
              subView === tab
                ? "bg-[var(--color-accent)] text-zinc-950 font-bold"
                : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Practice Accuracy Trend Card */}
      <div className="p-5 rounded-2xl border border-purple-500/20 bg-gradient-to-br from-purple-950/20 via-[var(--color-surface-base)] to-[var(--color-surface-base)] space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-medium text-[var(--color-text-secondary)]">
            <Target size={15} weight="bold" className="text-purple-400" />
            <span>Practice accuracy</span>
          </div>

          <span className="text-[11px] font-mono text-purple-400 font-semibold px-2 py-0.5 rounded-md bg-purple-500/10 border border-purple-500/20">
            Last 4 weeks
          </span>
        </div>

        <div className="flex items-baseline gap-3">
          <span className="text-3xl font-extrabold font-mono text-[var(--color-text-primary)]">
            {accuracyPercent}%
          </span>
          <span className="text-xs font-mono text-emerald-400 font-semibold">
            &uarr; 12% vs previous
          </span>
        </div>

        {/* Multi-week Trend Bars */}
        <div className="h-32 w-full pt-4 pb-2 flex items-end justify-between gap-3 border-b border-[var(--color-border-subtle)]">
          {[
            { label: "Week 1", val: 50 },
            { label: "Week 2", val: 62 },
            { label: "Week 3", val: 58 },
            { label: "Week 4", val: 78 },
          ].map((item) => (
            <div key={item.label} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end">
              <div
                className="w-full max-w-[40px] bg-slate-700/60 hover:bg-emerald-500/80 rounded-t-md transition-all duration-300 relative group"
                style={{ height: `${item.val}%` }}
              >
                <div className="w-2 h-2 rounded-full bg-emerald-400 absolute -top-1 left-1/2 -translate-x-1/2 shadow-xs shadow-emerald-400/80" />
              </div>
              <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">{item.label}</span>
            </div>
          ))}
        </div>

        {/* Attempt Breakdown Counters */}
        <div className="grid grid-cols-3 gap-2.5 pt-1">
          <div className="p-3 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-center">
            <div className="text-base font-bold font-mono text-[var(--color-text-primary)]">
              {totalAttempts}
            </div>
            <div className="text-[10px] text-[var(--color-text-tertiary)]">Total attempts</div>
          </div>

          <div className="p-3 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-center">
            <div className="text-base font-bold font-mono text-emerald-400">
              {totalCorrect}
            </div>
            <div className="text-[10px] text-[var(--color-text-tertiary)]">Correct (+4)</div>
          </div>

          <div className="p-3 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-center">
            <div className="text-base font-bold font-mono text-rose-400">
              {totalIncorrect}
            </div>
            <div className="text-[10px] text-[var(--color-text-tertiary)]">Incorrect (-1)</div>
          </div>
        </div>
      </div>

      {/* Subject Mastery List */}
      <div className="rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] p-5 space-y-3">
        <div className="flex items-center justify-between text-xs">
          <h3 className="font-bold text-[var(--color-text-primary)]">Subject mastery</h3>
          <span className="text-[var(--color-text-tertiary)] font-mono">See all &rarr;</span>
        </div>

        <div className="space-y-2.5">
          {subjects.map((subj) => (
            <div
              key={subj.name}
              className="p-3 rounded-xl bg-[var(--color-surface-raised)]/60 border border-[var(--color-border-subtle)] flex items-center justify-between gap-3 text-xs"
            >
              <div className="flex items-center gap-2.5 min-w-0 flex-1">
                <div
                  className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
                  style={{ backgroundColor: `${subj.color}15`, color: subj.color }}
                >
                  <subj.icon size={15} weight="bold" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between mb-1">
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
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
