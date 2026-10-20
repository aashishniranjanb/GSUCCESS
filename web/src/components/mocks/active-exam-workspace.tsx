"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  Clock,
  CheckCircle,
  BookmarkSimple,
  WarningCircle,
  ArrowLeft,
  ArrowRight,
  ArrowsClockwise,
  ListNumbers,
  Check,
  Pause,
  Play,
  X
} from "@phosphor-icons/react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MockExamSession, MockQuestionItem } from "@/lib/api/types";
import { recordMockAnswer, pauseMockExam, startMockExam } from "@/lib/api/mocks";

interface ActiveExamWorkspaceProps {
  initialSession: MockExamSession;
  onFinishExam: (examId: string) => Promise<void>;
  onExitExam: () => void;
}

export function ActiveExamWorkspace({
  initialSession,
  onFinishExam,
  onExitExam,
}: ActiveExamWorkspaceProps) {
  const [session, setSession] = useState<MockExamSession>(initialSession);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [markedForReview, setMarkedForReview] = useState<Set<number>>(new Set());
  const [remainingSec, setRemainingSec] = useState<number>(initialSession.remaining_seconds);
  const [isPaused, setIsPaused] = useState<boolean>(initialSession.status === "PAUSED");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [showConfirmModal, setShowConfirmModal] = useState<boolean>(false);
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [networkError, setNetworkError] = useState<string | null>(null);

  const questionStartTimeRef = useRef<number>(0);

  useEffect(() => {
    questionStartTimeRef.current = typeof performance !== "undefined" ? performance.now() : 0;
  }, []);

  const questions: MockQuestionItem[] = session.questions;
  const currentQuestion = questions[currentIndex];

  const handleAutoSubmit = useCallback(async () => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
      await onFinishExam(session.exam_id);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Auto-submission failed";
      setNetworkError(msg);
      setIsSubmitting(false);
    }
  }, [isSubmitting, onFinishExam, session.exam_id]);

  // Server-authoritative timer countdown with 1s tick
  useEffect(() => {
    if (isPaused || remainingSec <= 0) return;

    const interval = setInterval(() => {
      setRemainingSec((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          handleAutoSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isPaused, remainingSec, handleAutoSubmit]);

  // Format timer HH:MM:SS
  const formatTime = (totalSec: number) => {
    const hrs = Math.floor(totalSec / 3600);
    const mins = Math.floor((totalSec % 3600) / 60);
    const secs = totalSec % 60;
    if (hrs > 0) {
      return `${hrs.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    }
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  // Option selection
  const handleSelectOption = useCallback(async (optionIdx: number) => {
    if (!currentQuestion) return;

    // Toggle or select option
    const newSelected = currentQuestion.selected_option === optionIdx ? null : optionIdx;
    const now = typeof performance !== "undefined" ? performance.now() : 0;
    const timeSpentMs = questionStartTimeRef.current > 0 ? now - questionStartTimeRef.current : 0;

    // Optimistically update question state
    setSession((prev) => {
      const updated = [...prev.questions];
      updated[currentIndex] = {
        ...updated[currentIndex],
        selected_option: newSelected,
      };
      return { ...prev, questions: updated };
    });

    // Save to backend immediately
    setSaveStatus("saving");
    setNetworkError(null);
    try {
      await recordMockAnswer(
        session.exam_id,
        currentQuestion.question_id,
        newSelected,
        timeSpentMs,
        3
      );
      setSaveStatus("saved");
    } catch (err: unknown) {
      setSaveStatus("error");
      const msg = err instanceof Error ? err.message : "Failed to record answer to server.";
      setNetworkError(msg);
    }
  }, [currentQuestion, currentIndex, session.exam_id]);

  // Toggle Mark for Review
  const toggleMarkForReview = (idx: number) => {
    setMarkedForReview((prev) => {
      const updated = new Set(prev);
      if (updated.has(idx)) {
        updated.delete(idx);
      } else {
        updated.add(idx);
      }
      return updated;
    });
  };

  // Navigation handlers
  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
      questionStartTimeRef.current = typeof performance !== "undefined" ? performance.now() : 0;
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
      questionStartTimeRef.current = typeof performance !== "undefined" ? performance.now() : 0;
    }
  };

  const handleJumpTo = useCallback((idx: number) => {
    setCurrentIndex(idx);
    questionStartTimeRef.current = typeof performance !== "undefined" ? performance.now() : 0;
  }, []);

  // Pause / Resume toggle
  const handleTogglePause = async () => {
    if (isPaused) {
      try {
        const res = await startMockExam(session.exam_id);
        setRemainingSec(res.remaining_seconds);
        setIsPaused(false);
      } catch (err: unknown) {
        setNetworkError(err instanceof Error ? err.message : "Failed to resume exam");
      }
    } else {
      try {
        await pauseMockExam(session.exam_id);
        setIsPaused(true);
      } catch (err: unknown) {
        setNetworkError(err instanceof Error ? err.message : "Failed to pause exam");
      }
    }
  };

  // Final submission action
  const handleConfirmSubmit = async () => {
    setShowConfirmModal(false);
    setIsSubmitting(true);
    setNetworkError(null);
    try {
      await onFinishExam(session.exam_id);
    } catch (err: unknown) {
      setIsSubmitting(false);
      setNetworkError(err instanceof Error ? err.message : "Submission failed. Please retry.");
    }
  };

  // Calculate count metrics for palette
  const answeredCount = questions.filter((q) => q.selected_option !== null).length;
  const markedCount = markedForReview.size;
  const unansweredCount = questions.length - answeredCount;

  return (
    <div className="space-y-4 max-w-6xl mx-auto">
      {/* Top Authoritative Exam Status Bar */}
      <div className="sticky top-0 z-20 bg-[var(--color-surface)]/95 backdrop-blur-md border border-[var(--color-border-subtle)] rounded-lg p-3 sm:p-4 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Button
              size="sm"
              variant="secondary"
              onClick={onExitExam}
              className="text-xs h-8 px-2.5"
              title="Return to mock selector"
            >
              <ArrowLeft size={14} weight="bold" />
              Exit
            </Button>
            <div>
              <h2 className="text-xs sm:text-sm font-bold text-[var(--color-text-primary)] truncate max-w-xs sm:max-w-md">
                {session.title}
              </h2>
              <div className="flex items-center gap-2 mt-0.5 text-[11px] font-mono text-[var(--color-text-secondary)]">
                <span>Q {currentIndex + 1} of {questions.length}</span>
                <span>&bull;</span>
                <span>+{session.marks_per_question} / -{session.negative_marks}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Save indicator */}
            <div className="hidden sm:flex items-center gap-1.5 text-[11px] font-mono">
              {saveStatus === "saving" && (
                <span className="text-amber-400 flex items-center gap-1">
                  <ArrowsClockwise size={12} className="animate-spin" /> Saving...
                </span>
              )}
              {saveStatus === "saved" && (
                <span className="text-emerald-400 flex items-center gap-1">
                  <Check size={12} weight="bold" /> Synced
                </span>
              )}
              {saveStatus === "error" && (
                <span className="text-[var(--color-status-error)] flex items-center gap-1">
                  <WarningCircle size={12} weight="bold" /> Save Error
                </span>
              )}
            </div>

            {/* Pause / Resume Button */}
            <Button
              size="sm"
              variant="secondary"
              onClick={handleTogglePause}
              className="text-xs h-8 px-2.5 font-mono"
            >
              {isPaused ? (
                <>
                  <Play size={13} weight="bold" className="text-emerald-400" />
                  Resume
                </>
              ) : (
                <>
                  <Pause size={13} weight="bold" />
                  Pause
                </>
              )}
            </Button>

            {/* Authoritative Server Countdown Timer */}
            <div
              className={`flex items-center gap-1.5 px-3 py-1 rounded-md font-mono text-xs sm:text-sm font-bold border ${
                remainingSec < 300
                  ? "bg-rose-950/40 border-rose-800/60 text-rose-300 animate-pulse"
                  : "bg-[var(--color-surface-raised)] border-[var(--color-border-subtle)] text-[var(--color-text-primary)]"
              }`}
            >
              <Clock size={16} weight="bold" className="text-[var(--color-accent)]" />
              <span>{formatTime(remainingSec)}</span>
            </div>

            {/* Final Submission Button */}
            <Button
              size="sm"
              variant="primary"
              onClick={() => setShowConfirmModal(true)}
              disabled={isSubmitting}
              className="text-xs h-8 px-3 font-semibold"
            >
              {isSubmitting ? (
                <>
                  <ArrowsClockwise size={14} className="animate-spin" />
                  Scoring...
                </>
              ) : (
                "Finish Exam"
              )}
            </Button>
          </div>
        </div>

        {networkError && (
          <div className="mt-2 text-xs text-[var(--color-status-error)] flex items-center gap-1.5 bg-rose-950/20 px-3 py-1.5 rounded border border-rose-900/30">
            <WarningCircle size={14} weight="bold" className="shrink-0" />
            <span>{networkError}</span>
          </div>
        )}
      </div>

      {/* Paused Overlay Notice */}
      {isPaused && (
        <div className="p-4 rounded-lg bg-amber-950/20 border border-amber-800/40 text-amber-200 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Pause size={18} weight="bold" className="text-amber-400 shrink-0" />
            <span>
              Exam timer is paused. Questions and options are locked until you resume.
            </span>
          </div>
          <Button size="sm" variant="primary" onClick={handleTogglePause} className="text-xs h-7">
            Resume CBT
          </Button>
        </div>
      )}

      {/* Main Two-Column Layout: Question Area + Question Palette */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 items-start">
        {/* Left Column: Question Details & Interactive Option Choices (3 cols) */}
        <div className="lg:col-span-3 space-y-4">
          <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
            <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <Badge variant="default" className="font-mono text-[11px]">
                    Question #{currentIndex + 1}
                  </Badge>
                  <span className="text-xs text-[var(--color-text-tertiary)] font-mono">
                    ID: {currentQuestion.question_id}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <Badge variant="default" className="text-[10px] font-mono">
                    {currentQuestion.domain_id}
                  </Badge>
                  <Button
                    size="sm"
                    variant={markedForReview.has(currentIndex) ? "primary" : "secondary"}
                    onClick={() => toggleMarkForReview(currentIndex)}
                    className="text-xs h-7 px-2.5 gap-1.5"
                  >
                    <BookmarkSimple
                      size={14}
                      weight={markedForReview.has(currentIndex) ? "fill" : "bold"}
                    />
                    {markedForReview.has(currentIndex) ? "Marked" : "Mark Review"}
                  </Button>
                </div>
              </div>

              <div className="pt-3">
                <span className="text-xs font-mono text-[var(--color-accent)] block mb-1">
                  Concept: {currentQuestion.concept_name}
                </span>
                <CardTitle className="text-sm sm:text-base font-normal leading-relaxed text-[var(--color-text-primary)]">
                  {currentQuestion.question_text}
                </CardTitle>
              </div>
            </CardHeader>

            <CardContent className="pt-4 space-y-2.5">
              <div className="text-xs font-mono text-[var(--color-text-secondary)] pb-1">
                Select one correct answer:
              </div>

              <div className="space-y-2">
                {currentQuestion.options.map((optionText, optIdx) => {
                  const isSelected = currentQuestion.selected_option === optIdx;

                  return (
                    <button
                      key={optIdx}
                      type="button"
                      disabled={isPaused || isSubmitting}
                      onClick={() => handleSelectOption(optIdx)}
                      className={`w-full text-left p-3.5 rounded-lg border text-xs sm:text-sm transition-all flex items-start gap-3 ${
                        isSelected
                          ? "border-[var(--color-accent)] bg-[var(--color-accent)]/10 text-[var(--color-text-primary)] ring-1 ring-[var(--color-accent)]/40 font-medium"
                          : "border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/40 text-[var(--color-text-secondary)] hover:border-[var(--color-border-focus)] hover:text-[var(--color-text-primary)]"
                      } ${isPaused ? "opacity-50 cursor-not-allowed" : ""}`}
                    >
                      <span
                        className={`h-5 w-5 rounded-full flex items-center justify-center font-mono text-xs shrink-0 transition-colors ${
                          isSelected
                            ? "bg-[var(--color-accent)] text-black font-bold"
                            : "border border-[var(--color-border-subtle)] text-[var(--color-text-tertiary)]"
                        }`}
                      >
                        {String.fromCharCode(65 + optIdx)}
                      </span>
                      <span className="leading-relaxed pt-0.5">{optionText}</span>
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Stepper Navigation Controls */}
          <div className="flex items-center justify-between pt-1">
            <Button
              size="sm"
              variant="secondary"
              onClick={handlePrev}
              disabled={currentIndex === 0 || isPaused}
              className="gap-1.5 text-xs h-9 px-4"
            >
              <ArrowLeft size={14} weight="bold" />
              Previous
            </Button>

            <div className="text-xs font-mono text-[var(--color-text-tertiary)]">
              {currentIndex + 1} / {questions.length}
            </div>

            <Button
              size="sm"
              variant="secondary"
              onClick={handleNext}
              disabled={currentIndex === questions.length - 1 || isPaused}
              className="gap-1.5 text-xs h-9 px-4"
            >
              Next
              <ArrowRight size={14} weight="bold" />
            </Button>
          </div>
        </div>

        {/* Right Column: Question Navigation Palette (1 col) */}
        <div className="lg:col-span-1 space-y-3">
          <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
            <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
              <div className="flex items-center justify-between">
                <CardTitle className="text-xs font-semibold text-[var(--color-text-primary)] flex items-center gap-1.5">
                  <ListNumbers size={15} weight="bold" className="text-[var(--color-accent)]" />
                  Question Palette
                </CardTitle>
                <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">
                  {questions.length} Total
                </span>
              </div>

              {/* Status Legend */}
              <div className="grid grid-cols-2 gap-1.5 pt-2 text-[10px] font-mono text-[var(--color-text-secondary)]">
                <div className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded bg-emerald-500/80 inline-block" />
                  <span>Answered ({answeredCount})</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded bg-amber-500/80 inline-block" />
                  <span>Marked ({markedCount})</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] inline-block" />
                  <span>Unanswered ({unansweredCount})</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded border border-[var(--color-accent)] inline-block" />
                  <span>Current</span>
                </div>
              </div>
            </CardHeader>

            <CardContent className="pt-3">
              <div className="grid grid-cols-5 gap-1.5 max-h-[380px] overflow-y-auto pr-1">
                {questions.map((q, idx) => {
                  const isCurrent = idx === currentIndex;
                  const isAnswered = q.selected_option !== null;
                  const isMarked = markedForReview.has(idx);

                  let bgStyle = "bg-[var(--color-surface-raised)] text-[var(--color-text-secondary)] border-[var(--color-border-subtle)]";
                  if (isMarked) {
                    bgStyle = "bg-amber-950/60 text-amber-300 border-amber-600/50 font-bold";
                  } else if (isAnswered) {
                    bgStyle = "bg-emerald-950/60 text-emerald-300 border-emerald-600/50 font-bold";
                  }

                  if (isCurrent) {
                    bgStyle += " ring-2 ring-[var(--color-accent)] border-[var(--color-accent)] text-white";
                  }

                  return (
                    <button
                      key={idx}
                      type="button"
                      disabled={isPaused}
                      onClick={() => handleJumpTo(idx)}
                      className={`h-8 rounded text-xs font-mono border transition-all flex items-center justify-center ${bgStyle} ${
                        isPaused ? "opacity-50 cursor-not-allowed" : "hover:brightness-125"
                      }`}
                    >
                      {idx + 1}
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <Card className="max-w-md w-full border-[var(--color-border-subtle)] bg-[var(--color-surface)] shadow-2xl animate-enter">
            <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base font-bold text-[var(--color-text-primary)] flex items-center gap-2">
                  <CheckCircle size={18} weight="bold" className="text-[var(--color-accent)]" />
                  Submit Examination?
                </CardTitle>
                <button
                  type="button"
                  onClick={() => setShowConfirmModal(false)}
                  className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)]"
                >
                  <X size={18} weight="bold" />
                </button>
              </div>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
                You are about to submit your exam. Once submitted, your answers will be authoritatively graded and the 4-quadrant diagnostic analysis will be generated.
              </p>

              <div className="p-3 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-xs font-mono space-y-1.5">
                <div className="flex justify-between">
                  <span>Answered Questions:</span>
                  <span className="text-emerald-400 font-bold">{answeredCount}</span>
                </div>
                <div className="flex justify-between">
                  <span>Marked for Review:</span>
                  <span className="text-amber-400 font-bold">{markedCount}</span>
                </div>
                <div className="flex justify-between">
                  <span>Unanswered Questions:</span>
                  <span className="text-rose-400 font-bold">{unansweredCount}</span>
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => setShowConfirmModal(false)}
                  className="text-xs"
                >
                  Return to Exam
                </Button>
                <Button
                  size="sm"
                  variant="primary"
                  onClick={handleConfirmSubmit}
                  className="text-xs font-semibold"
                >
                  Confirm & Submit
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
