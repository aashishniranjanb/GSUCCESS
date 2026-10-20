"use client";

import React, { useState } from "react";
import {
  Clock,
  Sparkle,
  CheckCircle,
  WarningCircle,
  ArrowRight,
  ShieldCheck,
  Bookmarks,
  ListNumbers,
  ArrowsClockwise
} from "@phosphor-icons/react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MockBlueprintItem, MockHistoryItem } from "@/lib/api/types";

interface MockSelectorProps {
  blueprints: MockBlueprintItem[];
  history: MockHistoryItem[];
  isLoading: boolean;
  onSelectBlueprint: (blueprintId: string) => Promise<void>;
  onOpenMiniMockBuilder?: () => void;
  onResumeExam: (examId: string) => Promise<void>;
  onViewResults: (examId: string) => Promise<void>;
}

export function MockSelector({
  blueprints,
  history,
  isLoading,
  onSelectBlueprint,
  onOpenMiniMockBuilder,
  onResumeExam,
  onViewResults,
}: MockSelectorProps) {
  const [selectedBlueprint, setSelectedBlueprint] = useState<string>("sprint_25");
  const [isStarting, setIsStarting] = useState(false);

  const activeBlueprint = blueprints.find((b) => b.id === selectedBlueprint) || blueprints[0];

  const handleStart = async () => {
    if (!activeBlueprint) return;
    if (activeBlueprint.id === "mini_mock" && onOpenMiniMockBuilder) {
      onOpenMiniMockBuilder();
      return;
    }
    setIsStarting(true);
    try {
      await onSelectBlueprint(activeBlueprint.id);
    } finally {
      setIsStarting(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header Banner */}
      <div className="border-b border-[var(--color-border-subtle)] pb-5">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--color-text-primary)]">
              Mock Exam Arena
            </h1>
            <p className="text-xs text-[var(--color-text-secondary)] mt-1 max-w-2xl leading-relaxed">
              Authoritative Computer-Based Test (CBT) simulations powered by the backend evaluation engine.
              Strict exposure windows, zero adaptive hints, and 4-quadrant diagnostic feedback.
            </p>
          </div>
          <div className="flex items-center gap-2 self-start sm:self-auto">
            {onOpenMiniMockBuilder && (
              <Button
                variant="primary"
                size="sm"
                onClick={onOpenMiniMockBuilder}
                className="font-mono text-xs gap-1.5 h-8 bg-[var(--color-accent)] font-semibold shadow-sm"
              >
                <Sparkle size={14} weight="bold" />
                Build Mini Mock
              </Button>
            )}
            <Badge variant="primary" className="font-mono text-[11px] gap-1">
              <ShieldCheck size={13} weight="bold" />
              Verified CBT
            </Badge>
          </div>
        </div>
      </div>

      {/* Blueprint Mode Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
            <ListNumbers size={16} weight="bold" className="text-[var(--color-accent)]" />
            Select Blueprint Mode
          </h2>
          <span className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
            Authoritative +4 / -1 Marking
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {blueprints.map((bp) => {
            const isSelected = selectedBlueprint === bp.id;
            const isOfficial = bp.exam_version === "OFFICIAL_EXAM_SIMULATION";

            return (
              <Card
                key={bp.id}
                onClick={() => setSelectedBlueprint(bp.id)}
                className={`cursor-pointer transition-all border ${
                  isSelected
                    ? "border-[var(--color-accent)] ring-1 ring-[var(--color-accent)]/30 bg-[var(--color-surface-raised)]"
                    : "border-[var(--color-border-subtle)] hover:border-[var(--color-border-focus)] bg-[var(--color-surface)]"
                }`}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <Badge
                      variant={isOfficial ? "primary" : "default"}
                      className="text-[10px] font-mono"
                    >
                      {isOfficial ? "NBEMS Simulation" : "Provisional Mock"}
                    </Badge>
                    <span className="text-xs font-mono text-[var(--color-text-tertiary)] flex items-center gap-1">
                      <Clock size={13} weight="bold" className="text-[var(--color-accent)]" />
                      {bp.duration_minutes}m
                    </span>
                  </div>
                  <CardTitle className="text-base font-semibold mt-2.5 text-[var(--color-text-primary)]">
                    {bp.title}
                  </CardTitle>
                  <CardDescription className="text-xs line-clamp-2">
                    {bp.description || `${bp.total_questions} Questions adhering to standardized syllabus distribution.`}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-0 text-xs font-mono text-[var(--color-text-secondary)] space-y-1">
                  <div className="flex justify-between border-t border-[var(--color-border-subtle)] pt-2.5">
                    <span>Questions:</span>
                    <span className="text-[var(--color-text-primary)] font-semibold">{bp.total_questions} Qs</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Max Marks:</span>
                    <span className="text-[var(--color-text-primary)] font-semibold">
                      {bp.total_questions * bp.marks_per_question} pts
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Negative Marking:</span>
                    <span className="text-[var(--color-status-error)] font-semibold">
                      -{bp.negative_marks} mark / wrong
                    </span>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Selected Mode Summary & Launch Banner */}
      {activeBlueprint && (
        <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/40 p-5">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase font-mono tracking-wider text-[var(--color-accent)]">
                  CBT Instructions & Constraints
                </span>
              </div>
              <h3 className="text-base font-bold text-[var(--color-text-primary)]">
                {activeBlueprint.title}
              </h3>
              <ul className="text-xs text-[var(--color-text-secondary)] space-y-1 max-w-2xl">
                <li className="flex items-center gap-2">
                  <CheckCircle size={14} weight="bold" className="text-emerald-400 shrink-0" />
                  <span>
                    Each correct answer awards <strong>+{activeBlueprint.marks_per_question} marks</strong>; incorrect deductions are <strong>-{activeBlueprint.negative_marks} mark</strong>.
                  </span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle size={14} weight="bold" className="text-emerald-400 shrink-0" />
                  <span>
                    Server-authoritative timer: exam expires strictly after <strong>{activeBlueprint.duration_minutes} minutes</strong>. Refreshing or closing tabs does not freeze server time.
                  </span>
                </li>
                <li className="flex items-center gap-2">
                  <WarningCircle size={14} weight="bold" className="text-amber-400 shrink-0" />
                  <span>
                    Answers are auto-persisted per question. Explanations and answer keys remain concealed until final submission.
                  </span>
                </li>
              </ul>
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <Button
                variant="primary"
                size="lg"
                onClick={handleStart}
                disabled={isStarting || isLoading}
                className="w-full sm:w-auto font-semibold gap-2"
              >
                {isStarting ? (
                  <>
                    <ArrowsClockwise size={16} className="animate-spin" />
                    Initializing CBT...
                  </>
                ) : (
                  <>
                    <Sparkle size={16} weight="bold" />
                    Start Mock Exam
                    <ArrowRight size={16} weight="bold" />
                  </>
                )}
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Session History & In-Progress Resumes */}
      {history.length > 0 && (
        <div className="space-y-4 pt-2">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
              <Bookmarks size={16} weight="bold" className="text-[var(--color-accent)]" />
              Recent Exam Sessions
            </h2>
            <span className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
              {history.length} logged sessions
            </span>
          </div>

          <div className="border border-[var(--color-border-subtle)] rounded-lg overflow-hidden bg-[var(--color-surface)]">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/60 text-[var(--color-text-secondary)]">
                    <th className="py-2.5 px-4 font-medium">Exam Title</th>
                    <th className="py-2.5 px-4 font-medium">Questions</th>
                    <th className="py-2.5 px-4 font-medium">Status</th>
                    <th className="py-2.5 px-4 font-medium">Score / Accuracy</th>
                    <th className="py-2.5 px-4 font-medium text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--color-border-subtle)]">
                  {history.map((item) => {
                    const isEvaluated = item.status === "EVALUATED";
                    const isLive = item.status === "IN_PROGRESS" || item.status === "STARTED" || item.status === "PAUSED" || item.status === "CREATED";

                    return (
                      <tr key={item.id} className="hover:bg-[var(--color-surface-raised)]/40 transition-colors">
                        <td className="py-3 px-4">
                          <span className="font-semibold text-[var(--color-text-primary)] block">
                            {item.title}
                          </span>
                          <span className="text-[10px] text-[var(--color-text-tertiary)]">
                            {new Date(item.created_at).toLocaleDateString(undefined, {
                              month: "short",
                              day: "numeric",
                              year: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-[var(--color-text-secondary)]">
                          {item.total_questions} Qs
                        </td>
                        <td className="py-3 px-4">
                          <Badge
                            variant={isEvaluated ? "default" : isLive ? "primary" : "warning"}
                            className="text-[10px]"
                          >
                            {item.status}
                          </Badge>
                        </td>
                        <td className="py-3 px-4">
                          {isEvaluated && item.score !== null ? (
                            <span className="text-[var(--color-text-primary)] font-semibold">
                              {item.score} pts ({item.accuracy_percent}%)
                            </span>
                          ) : (
                            <span className="text-[var(--color-text-tertiary)]">—</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-right">
                          {isLive ? (
                            <Button
                              size="sm"
                              variant="primary"
                              onClick={() => onResumeExam(item.id)}
                              className="text-[11px] h-7 px-2.5"
                            >
                              Resume CBT
                            </Button>
                          ) : isEvaluated ? (
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => onViewResults(item.id)}
                              className="text-[11px] h-7 px-2.5"
                            >
                              View Diagnostic
                            </Button>
                          ) : null}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
