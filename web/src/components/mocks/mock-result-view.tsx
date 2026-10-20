"use client";

import React from "react";
import {
  Trophy,
  ChartBar,
  Clock,
  Target,
  ArrowCounterClockwise,
  ListDashes,
  Wrench,
  Info
} from "@phosphor-icons/react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MockEvaluationResult } from "@/lib/api/types";

interface MockResultViewProps {
  result: MockEvaluationResult;
  onRetake: () => void;
  onPracticeTopic?: (conceptId: string) => void;
}

export function MockResultView({ result, onRetake, onPracticeTopic }: MockResultViewProps) {
  const { summary, timing_analysis, concept_performance, identified_traps, recommended_repairs } = result;

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-enter">
      {/* Top Banner / Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[var(--color-border-subtle)] pb-5">
        <div>
          <div className="flex items-center gap-2">
            <Badge variant="primary" className="font-mono text-[10px]">
              Authoritative CBT Evaluation
            </Badge>
            {result.exam_id && (
              <span className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
                {result.exam_id}
              </span>
            )}
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--color-text-primary)] mt-1">
            Exam Diagnostic Report
          </h1>
          <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">
            4-Quadrant Cognitive Profiling & Concept Mastery Analysis
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="secondary"
            onClick={onRetake}
            className="text-xs gap-1.5 h-8 font-semibold"
          >
            <ArrowCounterClockwise size={14} weight="bold" />
            Back to Mock Arena
          </Button>
        </div>
      </div>

      {/* Summary Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
        <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)] p-4">
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-tertiary)]">
            <Trophy size={15} weight="bold" className="text-[var(--color-accent)]" />
            <span>Raw Score</span>
          </div>
          <div className="text-xl sm:text-2xl font-bold text-[var(--color-text-primary)] mt-1.5 font-mono">
            {summary.raw_score}
            <span className="text-xs text-[var(--color-text-tertiary)] font-normal ml-1">
              / {summary.max_possible_score}
            </span>
          </div>
          <div className="text-[11px] text-[var(--color-text-secondary)] mt-1 font-mono">
            {summary.score_percent}% weighted
          </div>
        </Card>

        <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)] p-4">
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-tertiary)]">
            <Target size={15} weight="bold" className="text-emerald-400" />
            <span>Accuracy</span>
          </div>
          <div className="text-xl sm:text-2xl font-bold text-emerald-400 mt-1.5 font-mono">
            {summary.accuracy_percent}%
          </div>
          <div className="text-[11px] text-[var(--color-text-secondary)] mt-1 font-mono">
            {summary.correct} correct of {summary.attempted} attempted
          </div>
        </Card>

        <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)] p-4">
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-tertiary)]">
            <ListDashes size={15} weight="bold" className="text-amber-400" />
            <span>Attempt Breakdown</span>
          </div>
          <div className="text-xs sm:text-sm font-bold text-[var(--color-text-primary)] mt-2 font-mono space-y-1">
            <div className="flex justify-between">
              <span className="text-emerald-400">Correct:</span>
              <span>{summary.correct}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-rose-400">Incorrect:</span>
              <span>{summary.incorrect}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[var(--color-text-tertiary)]">Unattempted:</span>
              <span>{summary.unattempted}</span>
            </div>
          </div>
        </Card>

        <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)] p-4">
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-tertiary)]">
            <Clock size={15} weight="bold" className="text-purple-400" />
            <span>Timing Pace</span>
          </div>
          <div className="text-xl sm:text-2xl font-bold text-[var(--color-text-primary)] mt-1.5 font-mono">
            {summary.avg_time_per_q_sec}s
            <span className="text-xs text-[var(--color-text-tertiary)] font-normal ml-1">/ q</span>
          </div>
          <div className="text-[11px] text-[var(--color-text-secondary)] mt-1 font-mono">
            Total {Math.round(summary.total_time_sec)}s recorded
          </div>
        </Card>
      </div>

      {/* 4-Quadrant Timing Analysis */}
      <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
        <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
              <ChartBar size={16} weight="bold" className="text-[var(--color-accent)]" />
              4-Quadrant Cognitive Retrieval Breakdown
            </CardTitle>
            <span className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
              Speed vs Correctness Matrix
            </span>
          </div>
        </CardHeader>
        <CardContent className="pt-4 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 font-mono text-xs">
            {/* Quadrant 1 */}
            <div className="p-3.5 rounded-lg border border-emerald-800/40 bg-emerald-950/20">
              <div className="flex justify-between items-center text-emerald-300 font-bold mb-1">
                <span>Fast & Correct (&lt;25s)</span>
                <span className="text-sm">{timing_analysis.quadrants.fast_correct} Qs</span>
              </div>
              <p className="text-[11px] text-emerald-200/70 font-sans leading-relaxed">
                Automated memory retrieval. High yield retention with immediate cognitive access.
              </p>
              <div className="mt-2 text-[10px] text-emerald-400 font-bold">
                {timing_analysis.interpretation.automated_retrieval_rate}% of attempts
              </div>
            </div>

            {/* Quadrant 2 */}
            <div className="p-3.5 rounded-lg border border-blue-800/40 bg-blue-950/20">
              <div className="flex justify-between items-center text-blue-300 font-bold mb-1">
                <span>Slow & Correct (&ge;25s)</span>
                <span className="text-sm">{timing_analysis.quadrants.slow_correct} Qs</span>
              </div>
              <p className="text-[11px] text-blue-200/70 font-sans leading-relaxed">
                Knowledge verified, but inefficient retrieval. Benefits from spaced flashcard drills.
              </p>
              <div className="mt-2 text-[10px] text-blue-400 font-bold">
                {timing_analysis.interpretation.inefficient_retrieval_rate}% of attempts
              </div>
            </div>

            {/* Quadrant 3 */}
            <div className="p-3.5 rounded-lg border border-amber-800/40 bg-amber-950/20">
              <div className="flex justify-between items-center text-amber-300 font-bold mb-1">
                <span>Fast & Incorrect (&lt;20s)</span>
                <span className="text-sm">{timing_analysis.quadrants.fast_incorrect} Qs</span>
              </div>
              <p className="text-[11px] text-amber-200/70 font-sans leading-relaxed">
                Careless errors or distractor traps. Needs careful stem reading and distractor verification.
              </p>
              <div className="mt-2 text-[10px] text-amber-400 font-bold">
                {timing_analysis.interpretation.careless_error_rate}% of attempts
              </div>
            </div>

            {/* Quadrant 4 */}
            <div className="p-3.5 rounded-lg border border-rose-800/40 bg-rose-950/20">
              <div className="flex justify-between items-center text-rose-300 font-bold mb-1">
                <span>Slow & Incorrect (&ge;20s)</span>
                <span className="text-sm">{timing_analysis.quadrants.slow_incorrect} Qs</span>
              </div>
              <p className="text-[11px] text-rose-200/70 font-sans leading-relaxed">
                Deep conceptual difficulty or factual misconception. Priority for repair study missions.
              </p>
              <div className="mt-2 text-[10px] text-rose-400 font-bold">
                {timing_analysis.interpretation.deep_struggle_rate}% of attempts
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recommended Repairs for Daily Scheduler */}
      {recommended_repairs && recommended_repairs.length > 0 && (
        <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
          <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
                <Wrench size={16} weight="bold" className="text-amber-400" />
                Recommended Adaptive Repairs
              </CardTitle>
              <span className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
                Fed to Daily Adaptive Engine
              </span>
            </div>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="space-y-2">
              {recommended_repairs.map((repair, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/40 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 text-xs"
                >
                  <div>
                    <span className="font-semibold text-[var(--color-text-primary)] block">
                      {repair.concept_name}
                    </span>
                    <span className="text-[11px] text-[var(--color-text-secondary)] mt-0.5">
                      {repair.reason}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={repair.recommended_mode === "repair" ? "warning" : "default"} className="font-mono text-[10px] uppercase">
                      {repair.recommended_mode} Mode
                    </Badge>
                    {onPracticeTopic && (
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => onPracticeTopic(repair.concept_id)}
                        className="text-[11px] h-7 px-2.5"
                      >
                        Study Topic
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Concept Performance Table */}
      {concept_performance && concept_performance.length > 0 && (
        <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
          <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
            <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)]">
              Concept Mastery Classification
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-[var(--color-border-subtle)] text-[var(--color-text-secondary)]">
                    <th className="py-2.5 px-3">Concept</th>
                    <th className="py-2.5 px-3">Tested</th>
                    <th className="py-2.5 px-3">Correct</th>
                    <th className="py-2.5 px-3">Accuracy</th>
                    <th className="py-2.5 px-3">Mastery Tier</th>
                  </tr>
                </thead>
                <tbody className="divide-y border-[var(--color-border-subtle)]">
                  {concept_performance.map((c) => {
                    const badgeVariant = c.tier === "STRONG" ? "success" : c.tier === "FRAGILE" ? "warning" : "error";
                    return (
                      <tr key={c.concept_id} className="hover:bg-[var(--color-surface-raised)]/30">
                        <td className="py-2.5 px-3 font-medium text-[var(--color-text-primary)] font-sans">
                          {c.name}
                        </td>
                        <td className="py-2.5 px-3 text-[var(--color-text-secondary)]">{c.total}</td>
                        <td className="py-2.5 px-3 text-emerald-400 font-bold">{c.correct}</td>
                        <td className="py-2.5 px-3 font-bold">{c.accuracy}%</td>
                        <td className="py-2.5 px-3">
                          <Badge variant={badgeVariant} className="text-[10px]">
                            {c.tier}
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

      {/* Distractor Traps Identified */}
      {identified_traps && identified_traps.length > 0 && (
        <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
          <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
                <Info size={16} weight="bold" className="text-rose-400" />
                Recurring Distractor Traps Caught
              </CardTitle>
              <span className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
                {identified_traps.length} Traps Logged
              </span>
            </div>
          </CardHeader>
          <CardContent className="pt-3">
            <div className="space-y-2.5">
              {identified_traps.map((trap, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg border border-rose-950/60 bg-rose-950/20 text-xs space-y-1"
                >
                  <div className="flex items-center justify-between font-mono text-[11px] text-[var(--color-text-tertiary)]">
                    <span className="text-rose-300 font-semibold">{trap.concept_name}</span>
                    <span>Q: {trap.question_id}</span>
                  </div>
                  <div className="text-[var(--color-text-secondary)] leading-relaxed">
                    <strong>Distractor Analysis:</strong> {trap.distractor_reason}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
