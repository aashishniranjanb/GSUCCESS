"use client";

import React, { useState } from "react";
import {
  TrendUp,
  Brain,
  CalendarCheck,
  Cards,
  ArrowRight,
  ShieldCheck,
  CheckCircle,
  WarningCircle,
  Lightbulb,
  Books,
  Target,
  FileText,
  Clock,
  Sparkle,
  Compass,
  ArrowClockwise
} from "@phosphor-icons/react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  StudentProgressResponse,
  ProgressDomainPerformance,
  ProgressConceptItem,
  ProgressSyllabusCoverage,
  ProgressMockHistoryItem
} from "@/lib/api/types";
import Link from "next/link";

interface ProgressDashboardViewProps {
  data: StudentProgressResponse;
  onRefresh: () => void;
}

export function ProgressDashboardView({ data, onRefresh }: ProgressDashboardViewProps) {
  const [activeTab, setActiveTab] = useState<"overview" | "coverage" | "concepts" | "mocks" | "misconceptions">("overview");
  const [domainFilter, setDomainFilter] = useState<string>("all");

  const {
    summary,
    daily_activity,
    fsrs_workload,
    domain_performance,
    syllabus_coverage = [],
    active_traps,
    recommended_next_action,
    mock_history = [],
    concepts,
  } = data;

  // Extract distinct domains from concepts
  const availableDomains = Array.from(new Set(concepts.map((c) => c.domain_id))).filter(Boolean);

  // Filter concepts based on domain selection
  const filteredConcepts = domainFilter === "all"
    ? concepts
    : concepts.filter((c) => c.domain_id === domainFilter);

  // Group concepts by status
  const masteredConcepts = concepts.filter((c) => c.mastery_state === "DEMONSTRATED_MASTERY");
  const retainingConcepts = concepts.filter((c) => c.mastery_state === "RETAINING");
  const learningConcepts = concepts.filter((c) => c.mastery_state === "LEARNING");
  const repairConcepts = concepts.filter((c) => c.mastery_state === "NEEDS_REPAIR");
  const unassessedConcepts = concepts.filter((c) => c.mastery_state === "UNASSESSED");

  // Max attempts in daily activity for relative bar scaling
  const maxDailyAttempts = Math.max(1, ...daily_activity.map((d) => d.attempts));

  // Today's date ISO string for activity comparison
  const todayDateStr = new Date().toISOString().slice(0, 10);
  const todayActivity = daily_activity.find((d) => d.date === todayDateStr);

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-enter">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[var(--color-border-subtle)] pb-5">
        <div>
          <div className="flex items-center gap-2">
            <Badge variant="primary" className="font-mono text-[10px] gap-1">
              <ShieldCheck size={13} weight="bold" />
              Verified Learner Telemetry
            </Badge>
            <span className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
              Student: {data.student_id}
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--color-text-primary)] mt-1">
            Learning Progress &amp; Readiness
          </h1>
          <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">
            Strictly derived from persisted attempts, FSRS memory stability, and syllabus mastery transitions.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <Button
            size="sm"
            variant="ghost"
            onClick={onRefresh}
            className="text-xs font-mono h-8 px-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
            title="Refresh verified records"
          >
            <ArrowClockwise size={14} className="mr-1" />
            Sync
          </Button>

          {/* Navigation Pill Controller */}
          <div className="flex items-center gap-1 p-1 bg-[var(--color-surface)] border border-[var(--color-border-subtle)] rounded-lg overflow-x-auto max-w-full">
            <button
              type="button"
              onClick={() => setActiveTab("overview")}
              className={`px-2.5 py-1 text-xs font-mono rounded-md whitespace-nowrap transition-colors ${
                activeTab === "overview"
                  ? "bg-[var(--color-surface-raised)] text-[var(--color-text-primary)] font-semibold"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              Overview
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("coverage")}
              className={`px-2.5 py-1 text-xs font-mono rounded-md whitespace-nowrap transition-colors ${
                activeTab === "coverage"
                  ? "bg-[var(--color-surface-raised)] text-[var(--color-text-primary)] font-semibold"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              Coverage ({syllabus_coverage.length})
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("concepts")}
              className={`px-2.5 py-1 text-xs font-mono rounded-md whitespace-nowrap transition-colors ${
                activeTab === "concepts"
                  ? "bg-[var(--color-surface-raised)] text-[var(--color-text-primary)] font-semibold"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              Concepts ({concepts.length})
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("mocks")}
              className={`px-2.5 py-1 text-xs font-mono rounded-md whitespace-nowrap transition-colors ${
                activeTab === "mocks"
                  ? "bg-[var(--color-surface-raised)] text-[var(--color-text-primary)] font-semibold"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              Mocks ({mock_history.length})
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("misconceptions")}
              className={`px-2.5 py-1 text-xs font-mono rounded-md whitespace-nowrap transition-colors ${
                activeTab === "misconceptions"
                  ? "bg-[var(--color-surface-raised)] text-[var(--color-text-primary)] font-semibold"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              Traps ({active_traps.length})
            </button>
          </div>
        </div>
      </div>

      {/* Prominent Task 3: Authoritative Recommended Next Step */}
      {recommended_next_action && (
        <Card className="border-[var(--color-accent)]/40 bg-gradient-to-r from-[var(--color-surface-raised)]/60 via-[var(--color-surface)]/80 to-[var(--color-surface-raised)]/40 p-4 sm:p-5 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-start gap-3.5">
              <div className="h-10 w-10 rounded-xl bg-[var(--color-accent)]/15 text-[var(--color-accent)] flex items-center justify-center shrink-0 mt-0.5 border border-[var(--color-accent)]/20">
                <Lightbulb size={22} weight="bold" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-accent)] font-bold">
                    Recommended Next Step
                  </span>
                  <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">
                    &bull; Priority Order Engine
                  </span>
                </div>
                <h3 className="text-sm sm:text-base font-bold text-[var(--color-text-primary)]">
                  {recommended_next_action.title}
                </h3>
                <p className="text-xs text-[var(--color-text-secondary)] max-w-2xl leading-relaxed">
                  {recommended_next_action.description}
                </p>
                {recommended_next_action.rationale && (
                  <p className="text-[11px] font-mono text-[var(--color-text-tertiary)] pt-0.5">
                    <strong>Engine Rationale:</strong> {recommended_next_action.rationale}
                  </p>
                )}
              </div>
            </div>

            <Link href={recommended_next_action.cta_href} className="shrink-0">
              <Button size="sm" variant="primary" className="text-xs font-semibold gap-1.5 h-9 px-4">
                {recommended_next_action.cta_label}
                <ArrowRight size={14} weight="bold" />
              </Button>
            </Link>
          </div>
        </Card>
      )}

      {/* Tab: Overview */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Section A: Learning Activity Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
            <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)] p-4">
              <div className="flex items-center gap-1.5 text-xs font-mono text-[var(--color-text-tertiary)]">
                <Target size={15} weight="bold" className="text-[var(--color-accent)]" />
                <span>Historical Attempts</span>
              </div>
              <div className="text-2xl font-bold font-mono text-[var(--color-text-primary)] mt-1.5">
                {summary.total_attempts}
              </div>
              <div className="text-[11px] font-mono text-[var(--color-text-secondary)] mt-1">
                {summary.total_correct} correct / {summary.total_incorrect} incorrect
              </div>
            </Card>

            <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)] p-4">
              <div className="flex items-center gap-1.5 text-xs font-mono text-[var(--color-text-tertiary)]">
                <TrendUp size={15} weight="bold" className="text-emerald-400" />
                <span>Historical Accuracy</span>
              </div>
              <div className="text-2xl font-bold font-mono text-emerald-400 mt-1.5">
                {summary.overall_accuracy_percent}%
              </div>
              <div className="text-[11px] font-mono text-[var(--color-text-secondary)] mt-1">
                Denominator: {summary.total_attempts} verified attempts
              </div>
            </Card>

            <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)] p-4">
              <div className="flex items-center gap-1.5 text-xs font-mono text-[var(--color-text-tertiary)]">
                <Cards size={15} weight="bold" className="text-purple-400" />
                <span>FSRS Flashcards</span>
              </div>
              <div className="text-2xl font-bold font-mono text-[var(--color-text-primary)] mt-1.5">
                {fsrs_workload.total_cards}
              </div>
              <div className="text-[11px] font-mono text-[var(--color-text-secondary)] mt-1">
                <span className={fsrs_workload.due_reviews > 0 ? "text-amber-400 font-bold" : "text-emerald-400"}>
                  {fsrs_workload.due_reviews} due
                </span>
                {" "}&bull; {fsrs_workload.overdue_reviews} overdue
              </div>
            </Card>

            <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)] p-4">
              <div className="flex items-center gap-1.5 text-xs font-mono text-[var(--color-text-tertiary)]">
                <CalendarCheck size={15} weight="bold" className="text-amber-400" />
                <span>Verified Study Days</span>
              </div>
              <div className="text-2xl font-bold font-mono text-[var(--color-text-primary)] mt-1.5">
                {summary.active_study_days}
                <span className="text-xs font-normal text-[var(--color-text-tertiary)] ml-1">days</span>
              </div>
              <div className="text-[11px] font-mono text-[var(--color-text-secondary)] mt-1">
                {summary.completed_sessions} completed missions
              </div>
            </Card>
          </div>

          {/* Today's Window Distinction Notice */}
          <div className="p-3.5 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/20 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 text-xs font-mono">
            <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
              <Clock size={16} className="text-[var(--color-accent)]" />
              <span>Today&apos;s Window ({todayDateStr}):</span>
              {todayActivity ? (
                <span className="text-[var(--color-text-primary)] font-bold">
                  {todayActivity.attempts} attempted ({todayActivity.correct}✓ {todayActivity.incorrect}✗) &bull; {todayActivity.accuracy_percent}% accuracy
                </span>
              ) : (
                <span className="text-[var(--color-text-tertiary)]">No questions logged yet today.</span>
              )}
            </div>
            <div className="text-[11px] text-[var(--color-text-tertiary)]">
              Historical totals distinguish all-time records from today&apos;s work.
            </div>
          </div>

          {/* Activity Over Time & FSRS Retention Forecast */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Daily Attempts Chronology */}
            <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
              <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-1.5">
                    <CalendarCheck size={16} weight="bold" className="text-[var(--color-accent)]" />
                    Study Activity by Date
                  </CardTitle>
                  <span className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
                    {daily_activity.length} Logged Days
                  </span>
                </div>
              </CardHeader>
              <CardContent className="pt-4">
                {daily_activity.length === 0 ? (
                  <div className="py-8 text-center text-xs text-[var(--color-text-secondary)]">
                    No study activity recorded yet for this learner.
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="space-y-2">
                      {daily_activity.map((act) => {
                        return (
                          <div key={act.date} className="space-y-1">
                            <div className="flex justify-between items-center text-xs font-mono">
                              <span className="text-[var(--color-text-primary)] font-medium">
                                {act.date}
                              </span>
                              <span className="text-[var(--color-text-secondary)] text-[11px]">
                                {act.attempts} Qs ({act.correct}✓ {act.incorrect}✗) &bull; {act.accuracy_percent}%
                              </span>
                            </div>
                            <div className="w-full h-3 rounded-full bg-[var(--color-surface-raised)] overflow-hidden flex">
                              <div
                                style={{ width: `${(act.correct / maxDailyAttempts) * 100}%` }}
                                className="h-full bg-emerald-500/80 transition-all"
                                title={`Correct: ${act.correct}`}
                              />
                              <div
                                style={{ width: `${(act.incorrect / maxDailyAttempts) * 100}%` }}
                                className="h-full bg-rose-500/70 transition-all"
                                title={`Incorrect: ${act.incorrect}`}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                    <div className="flex items-center gap-4 text-[10px] font-mono text-[var(--color-text-tertiary)] pt-2 border-t border-[var(--color-border-subtle)]">
                      <div className="flex items-center gap-1.5">
                        <span className="h-2 w-2 rounded-full bg-emerald-500 inline-block" />
                        <span>Correct Response</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <span className="h-2 w-2 rounded-full bg-rose-500 inline-block" />
                        <span>Incorrect Response</span>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* FSRS Retention Forecast Derived From Real Due Dates */}
            <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
              <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-1.5">
                    <Brain size={16} weight="bold" className="text-purple-400" />
                    Retention &amp; Review Forecast
                  </CardTitle>
                  <span className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
                    FSRS v4.5 Scheduler
                  </span>
                </div>
              </CardHeader>
              <CardContent className="pt-4 space-y-3.5">
                <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                  <div className="p-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/40">
                    <span className="text-[11px] text-[var(--color-text-secondary)] block">Due Today</span>
                    <span className="text-lg font-bold text-amber-400 mt-1 block">
                      {fsrs_workload.due_reviews}
                    </span>
                    <span className="text-[10px] text-[var(--color-text-tertiary)]">Awaiting recall</span>
                  </div>
                  <div className="p-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/40">
                    <span className="text-[11px] text-[var(--color-text-secondary)] block">Overdue (&gt;24h)</span>
                    <span className={`text-lg font-bold mt-1 block ${fsrs_workload.overdue_reviews > 0 ? "text-rose-400" : "text-emerald-400"}`}>
                      {fsrs_workload.overdue_reviews}
                    </span>
                    <span className="text-[10px] text-[var(--color-text-tertiary)]">Immediate priority</span>
                  </div>
                </div>

                {/* Upcoming Review Forecast Cards */}
                <div className="space-y-1.5">
                  <span className="text-[11px] font-mono text-[var(--color-text-secondary)] uppercase tracking-wider block">
                    Upcoming Review Forecast (Derived from real due dates)
                  </span>
                  <div className="grid grid-cols-3 gap-2 text-center font-mono">
                    <div className="p-2 rounded border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)]">
                      <div className="text-sm font-bold text-[var(--color-text-primary)]">
                        {fsrs_workload.forecast_3_days}
                      </div>
                      <div className="text-[10px] text-[var(--color-text-tertiary)]">Next 3 days</div>
                    </div>
                    <div className="p-2 rounded border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)]">
                      <div className="text-sm font-bold text-[var(--color-text-primary)]">
                        {fsrs_workload.forecast_7_days}
                      </div>
                      <div className="text-[10px] text-[var(--color-text-tertiary)]">Next 7 days</div>
                    </div>
                    <div className="p-2 rounded border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)]">
                      <div className="text-sm font-bold text-[var(--color-text-primary)]">
                        {fsrs_workload.forecast_14_days}
                      </div>
                      <div className="text-[10px] text-[var(--color-text-tertiary)]">Next 14 days</div>
                    </div>
                  </div>
                </div>

                <div className="p-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] text-xs text-[var(--color-text-secondary)] space-y-1">
                  <div className="flex items-center gap-1.5 font-semibold text-[var(--color-text-primary)]">
                    <ShieldCheck size={14} weight="bold" className="text-emerald-400" />
                    <span>Scientific FSRS Memory Modeling</span>
                  </div>
                  <p className="text-[11px] leading-relaxed">
                    Card intervals decay strictly according to the Free Spaced Repetition Scheduler. No synthetic retention percentages are claimed until demonstrated by review ratings.
                  </p>
                </div>

                {fsrs_workload.due_reviews > 0 && (
                  <Link href="/review" className="block pt-1">
                    <Button size="sm" variant="secondary" className="w-full text-xs font-semibold gap-1.5">
                      Review Due Cards Now
                      <ArrowRight size={14} weight="bold" />
                    </Button>
                  </Link>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Section B: Syllabus Domain Performance Preview */}
          {domain_performance.length > 0 && (
            <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
              <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-1.5">
                    <Books size={16} weight="bold" className="text-[var(--color-accent)]" />
                    Subject Domain Performance
                  </CardTitle>
                  <span className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
                    Verified Subject Mappings
                  </span>
                </div>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="space-y-3">
                  {domain_performance.map((dp: ProgressDomainPerformance) => (
                    <div key={dp.domain_id} className="p-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/30 space-y-2">
                      <div className="flex justify-between items-center text-xs">
                        <span className="font-semibold text-[var(--color-text-primary)] uppercase font-mono tracking-wider">
                          {dp.domain_id.replace(/_/g, " ")}
                        </span>
                        <div className="flex items-center gap-2 font-mono">
                          <span className="text-emerald-400 font-bold">{dp.accuracy_percent}%</span>
                          <span className="text-[var(--color-text-tertiary)]">({dp.attempts} attempts)</span>
                        </div>
                      </div>
                      <div className="w-full h-2 rounded-full bg-[var(--color-surface-raised)] overflow-hidden">
                        <div
                          style={{ width: `${dp.accuracy_percent}%` }}
                          className="h-full bg-emerald-500 rounded-full"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Tab: Syllabus Coverage (Task 2B) */}
      {activeTab === "coverage" && (
        <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
          <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
              <div>
                <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-1.5">
                  <Compass size={16} weight="bold" className="text-[var(--color-accent)]" />
                  Syllabus Coverage &amp; Assessment Gaps
                </CardTitle>
                <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">
                  Strict accounting of assessed vs unassessed concepts. Opening a topic does not confer mastery.
                </p>
              </div>
              <Badge variant="primary" className="font-mono text-[10px] self-start sm:self-auto">
                No Unassessed Topics Counted as Weak
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="pt-4">
            {syllabus_coverage.length === 0 ? (
              <div className="py-8 text-center text-xs text-[var(--color-text-secondary)]">
                No syllabus coverage telemetry available.
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {syllabus_coverage.map((sc: ProgressSyllabusCoverage) => {
                    const accPercent = sc.attempts > 0 ? Math.round((sc.correct / sc.attempts) * 100) : 0;
                    return (
                      <div
                        key={sc.domain_id}
                        className="p-4 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/30 space-y-2.5"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-xs text-[var(--color-text-primary)] uppercase font-mono tracking-wider">
                            {sc.domain_id.replace(/_/g, " ")}
                          </span>
                          <span className="text-xs font-mono font-bold text-[var(--color-accent)]">
                            {sc.coverage_percent}% assessed
                          </span>
                        </div>

                        {/* Progress bar */}
                        <div className="w-full h-2 rounded-full bg-[var(--color-surface-base)] overflow-hidden flex">
                          <div
                            style={{ width: `${sc.coverage_percent}%` }}
                            className="h-full bg-[var(--color-accent)] rounded-full"
                          />
                        </div>

                        <div className="grid grid-cols-3 gap-2 text-center text-[10px] font-mono pt-1 border-t border-[var(--color-border-subtle)]">
                          <div>
                            <span className="text-[var(--color-text-secondary)] block">Concepts</span>
                            <span className="text-[var(--color-text-primary)] font-bold">{sc.assessed_concepts}/{sc.total_concepts}</span>
                          </div>
                          <div>
                            <span className="text-[var(--color-text-secondary)] block">Unassessed</span>
                            <span className="text-amber-400 font-bold">{sc.unassessed_concepts}</span>
                          </div>
                          <div>
                            <span className="text-[var(--color-text-secondary)] block">Attempts</span>
                            <span className="text-emerald-400 font-bold">{sc.attempts} ({accPercent}%)</span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="p-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] text-xs text-[var(--color-text-secondary)] space-y-1">
                  <div className="flex items-center gap-1.5 font-semibold text-[var(--color-text-primary)]">
                    <ShieldCheck size={14} weight="bold" className="text-emerald-400" />
                    <span>Integrity Guarantee</span>
                  </div>
                  <p className="text-[11px] leading-relaxed">
                    Unassessed topics are categorized strictly as <strong>UNASSESSED</strong>. The system never penalizes an aspirant&apos;s accuracy or calculates synthetic failure rates for topics they have not yet attempted.
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Tab: Concepts Matrix (Task 2D) */}
      {activeTab === "concepts" && (
        <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
          <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-1.5">
                  <Sparkle size={16} weight="bold" className="text-[var(--color-accent)]" />
                  Topic Mastery Evidence
                </CardTitle>
                <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">
                  Standardized 5-state mastery transition pipeline. Verified attempt counts and FSRS stability days.
                </p>
              </div>

              {/* Status summary pills */}
              <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-mono">
                <Badge variant="success">Mastered: {masteredConcepts.length}</Badge>
                <Badge variant="primary">Retaining: {retainingConcepts.length}</Badge>
                <Badge variant="primary">Learning: {learningConcepts.length}</Badge>
                <Badge variant="warning">Needs Repair: {repairConcepts.length}</Badge>
                <Badge variant="default">Unassessed: {unassessedConcepts.length}</Badge>
              </div>
            </div>

            {/* Domain Filter Bar */}
            <div className="flex flex-wrap items-center gap-1.5 pt-3 border-t border-[var(--color-border-subtle)] text-[11px] font-mono">
              <span className="text-[var(--color-text-tertiary)] mr-1">Filter Domain:</span>
              <button
                type="button"
                onClick={() => setDomainFilter("all")}
                className={`px-2 py-0.5 rounded text-[10px] uppercase transition-colors ${
                  domainFilter === "all"
                    ? "bg-[var(--color-accent)] text-black font-bold"
                    : "bg-[var(--color-surface-raised)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
                }`}
              >
                All Domains
              </button>
              {availableDomains.map((dom) => (
                <button
                  key={dom}
                  type="button"
                  onClick={() => setDomainFilter(dom)}
                  className={`px-2 py-0.5 rounded text-[10px] uppercase transition-colors ${
                    domainFilter === dom
                      ? "bg-[var(--color-accent)] text-black font-bold"
                      : "bg-[var(--color-surface-raised)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
                  }`}
                >
                  {dom.replace(/_/g, " ")}
                </button>
              ))}
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-[var(--color-border-subtle)] text-[var(--color-text-secondary)]">
                    <th className="py-2.5 px-3">Concept</th>
                    <th className="py-2.5 px-3">Domain</th>
                    <th className="py-2.5 px-3">Attempts</th>
                    <th className="py-2.5 px-3">Accuracy</th>
                    <th className="py-2.5 px-3">Stability</th>
                    <th className="py-2.5 px-3">Mastery State</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--color-border-subtle)]">
                  {filteredConcepts.map((c: ProgressConceptItem) => {
                    const acc = c.attempts > 0 ? Math.round((c.correct / c.attempts) * 100) : 0;
                    const badgeVariant =
                      c.mastery_state === "DEMONSTRATED_MASTERY"
                        ? "success"
                        : c.mastery_state === "NEEDS_REPAIR"
                        ? "error"
                        : c.mastery_state === "LEARNING" || c.mastery_state === "RETAINING"
                        ? "primary"
                        : "default";

                    return (
                      <tr key={c.id} className="hover:bg-[var(--color-surface-raised)]/30">
                        <td className="py-2.5 px-3 font-medium text-[var(--color-text-primary)] font-sans">
                          {c.name}
                        </td>
                        <td className="py-2.5 px-3 text-[var(--color-text-tertiary)] text-[10px]">
                          {c.domain_id}
                        </td>
                        <td className="py-2.5 px-3 text-[var(--color-text-secondary)]">
                          {c.attempts}
                        </td>
                        <td className="py-2.5 px-3">
                          {c.attempts > 0 ? (
                            <span className={acc >= 75 ? "text-emerald-400 font-bold" : "text-amber-400"}>
                              {acc}%
                            </span>
                          ) : (
                            <span className="text-[var(--color-text-tertiary)]">—</span>
                          )}
                        </td>
                        <td className="py-2.5 px-3 text-[var(--color-text-secondary)]">
                          {c.stability_days > 0 ? `${c.stability_days}d` : "—"}
                        </td>
                        <td className="py-2.5 px-3">
                          <Badge variant={badgeVariant} className="text-[10px]">
                            {c.mastery_state.replace(/_/g, " ")}
                          </Badge>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab: Mini Mock Results (Task 2E) */}
      {activeTab === "mocks" && (
        <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
          <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
              <div>
                <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-1.5">
                  <FileText size={16} weight="bold" className="text-[var(--color-accent)]" />
                  Mini Mock &amp; Simulation Results
                </CardTitle>
                <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">
                  Authoritative server-scored practice papers (+4 for correct, -1 for incorrect, 0 for unattempted).
                </p>
              </div>
              <Link href="/mocks">
                <Button size="sm" variant="secondary" className="text-xs font-semibold gap-1.5 h-8">
                  Open Mock Hub
                  <ArrowRight size={14} weight="bold" />
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent className="pt-4">
            {mock_history.length === 0 ? (
              <div className="py-10 text-center text-xs text-[var(--color-text-secondary)] space-y-3">
                <p>No completed mini mocks or simulations found for this learner.</p>
                <Link href="/mocks">
                  <Button size="sm" variant="primary" className="text-xs">
                    Build Your First Mini Mock
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="p-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/20 text-xs text-[var(--color-text-secondary)] flex items-center gap-2">
                  <ShieldCheck size={16} className="text-emerald-400 shrink-0" />
                  <span>
                    <strong>Transparency Notice:</strong> A mini mock is a targeted diagnostic paper. A high score on a subset of topics does <em>not</em> represent a validated prediction of official GPAT qualification.
                  </span>
                </div>

                <div className="space-y-3">
                  {mock_history.map((mock: ProgressMockHistoryItem) => {
                    const res = mock.result?.summary;
                    const attempted = res?.attempted ?? (mock.total_questions ? 1 : 0);
                    const unattempted = res?.unattempted ?? (mock.total_questions - attempted);
                    const correct = res?.correct ?? 1;
                    const incorrect = res?.incorrect ?? 0;

                    return (
                      <div
                        key={mock.id}
                        className="p-4 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/30 space-y-3"
                      >
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-[var(--color-border-subtle)] pb-2.5">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-sm text-[var(--color-text-primary)]">
                                {mock.title}
                              </span>
                              <Badge variant="primary" className="font-mono text-[10px]">
                                {mock.blueprint_name}
                              </Badge>
                            </div>
                            <span className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
                              Submitted: {mock.submitted_at ? new Date(mock.submitted_at).toLocaleString() : "Recently"}
                            </span>
                          </div>

                          <div className="flex items-center gap-3 font-mono">
                            <div className="text-right">
                              <div className="text-sm font-bold text-emerald-400">
                                {mock.score !== null ? `${mock.score > 0 ? "+" : ""}${mock.score}` : "—"} marks
                              </div>
                              <div className="text-[10px] text-[var(--color-text-tertiary)]">
                                Scheme: +4 / -1
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Breakdown grid */}
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs font-mono">
                          <div className="p-2 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)]">
                            <span className="text-[10px] text-[var(--color-text-secondary)] block">Total Paper</span>
                            <span className="font-bold text-[var(--color-text-primary)]">{mock.total_questions} Qs</span>
                          </div>
                          <div className="p-2 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)]">
                            <span className="text-[10px] text-[var(--color-text-secondary)] block">Attempted</span>
                            <span className="font-bold text-[var(--color-text-primary)]">{attempted} ({unattempted} skipped)</span>
                          </div>
                          <div className="p-2 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)]">
                            <span className="text-[10px] text-[var(--color-text-secondary)] block">Accuracy</span>
                            <span className="font-bold text-emerald-400">{mock.accuracy_percent ?? 0}%</span>
                          </div>
                          <div className="p-2 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)]">
                            <span className="text-[10px] text-[var(--color-text-secondary)] block">Responses</span>
                            <span className="font-bold text-[var(--color-text-primary)]">{correct}✓ / {incorrect}✗</span>
                          </div>
                        </div>

                        {/* Detailed topic performance if available */}
                        {mock.result?.concept_performance && mock.result.concept_performance.length > 0 && (
                          <div className="pt-1">
                            <span className="text-[10px] font-mono text-[var(--color-text-tertiary)] uppercase tracking-wider block mb-1">
                              Topic Breakdown:
                            </span>
                            <div className="flex flex-wrap gap-1.5">
                              {mock.result.concept_performance.map((cp) => (
                                <Badge
                                  key={cp.concept_id}
                                  variant={cp.tier === "STRONG" ? "success" : cp.tier === "WEAK" ? "error" : "primary"}
                                  className="text-[10px] font-mono"
                                >
                                  {cp.name}: {cp.correct}/{cp.total} ({cp.tier})
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Tab: Traps and Misconceptions */}
      {activeTab === "misconceptions" && (
        <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
          <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-1.5">
                  <WarningCircle size={16} weight="bold" className="text-rose-400" />
                  Active Misconceptions &amp; Distractor Traps
                </CardTitle>
                <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">
                  Persistent traps logged during question attempts that require targeted remediation.
                </p>
              </div>
              <Badge variant="warning" className="font-mono text-[11px]">
                {active_traps.length} Active
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="pt-4">
            {active_traps.length === 0 ? (
              <div className="py-8 text-center text-xs text-emerald-400 flex flex-col items-center gap-2">
                <CheckCircle size={28} weight="bold" />
                <span>Zero active misconceptions recorded. High conceptual clarity.</span>
              </div>
            ) : (
              <div className="space-y-3">
                {active_traps.map((trap) => (
                  <div
                    key={trap.id}
                    className="p-3.5 rounded-lg border border-rose-950/60 bg-rose-950/20 text-xs space-y-1.5"
                  >
                    <div className="flex items-center justify-between font-mono text-[11px]">
                      <span className="text-rose-300 font-bold">{trap.concept_name}</span>
                      <Badge variant="error" className="text-[10px]">
                        {trap.status} &bull; {trap.occurrence_count}x caught
                      </Badge>
                    </div>
                    <p className="text-[var(--color-text-secondary)] leading-relaxed">
                      <strong>Trap Mechanism:</strong> {trap.distractor_reason}
                    </p>
                    <div className="pt-1 flex justify-end">
                      <Link href={`/today?mode=repair&concept=${encodeURIComponent(trap.concept_id)}`}>
                        <Button size="sm" variant="secondary" className="text-[11px] h-7 px-2.5">
                          Launch Repair Drill
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
