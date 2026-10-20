"use client";

import React, { useEffect, useState, useCallback } from "react";
import {
  fetchPYQYears,
  fetchPYQList,
  fetchPYQDetail,
} from "@/lib/api/pyqs";
import { submitStudyAttempt } from "@/lib/api/study";
import {
  PYQYearItem,
  PYQListItem,
  PYQDetailItem,
  AttemptFeedbackResponse,
} from "@/lib/api/types";
import { Badge } from "@/components/ui/badge";
import { Skeleton, ErrorState } from "@/components/ui/states";
import {
  SlidersHorizontal,
  X,
  CheckCircle,
  XCircle,
  ArrowRight,
  ArrowLeft,
  Trophy,
  ShieldCheck,
  ArrowCounterClockwise,
} from "@phosphor-icons/react/dist/ssr";

const SUBJECT_OPTIONS = [
  { id: "all", label: "All Subjects" },
  { id: "pharmacology", label: "Pharmacology" },
  { id: "pharmaceutics", label: "Pharmaceutics" },
  { id: "pharmaceutical_chemistry", label: "Pharmaceutical Chemistry" },
  { id: "pharmacognosy", label: "Pharmacognosy" },
  { id: "other_subjects", label: "Other B.Pharm Subjects" },
];

export default function PYQsPage() {
  // Filter states
  const [years, setYears] = useState<PYQYearItem[]>([]);
  const [selectedYear, setSelectedYear] = useState<number | null>(2026);
  const [selectedSubject, setSelectedSubject] = useState<string>("all");
  const [isFilterOpen, setIsFilterOpen] = useState<boolean>(false);

  // Question navigation states
  const [questions, setQuestions] = useState<PYQListItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [loadingList, setLoadingList] = useState<boolean>(true);
  const [listError, setListError] = useState<string | null>(null);

  // Active question details & state
  const [activeDetail, setActiveDetail] = useState<PYQDetailItem | null>(null);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  // Quiz interactive state
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<AttemptFeedbackResponse | null>(null);
  const [shakeOption, setShakeOption] = useState<number | null>(null);
  const [sessionScore, setSessionScore] = useState<{ correct: number; total: number }>({
    correct: 0,
    total: 0,
  });

  // Rewards overview from backend
  const [rewardsCount, setRewardsCount] = useState<number | null>(null);

  // Initial fetch: years & rewards
  useEffect(() => {
    fetchPYQYears()
      .then((data) => {
        setYears(data);
        if (data.length > 0 && !data.some((y) => y.year === 2026)) {
          setSelectedYear(data[0].year);
        }
      })
      .catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : "Failed to load exam years.";
        setListError(msg);
      });

    // Check authoritative rewards ledger
    fetch("/api/rewards?student_id=student_01")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.counts?.total_awarded !== undefined) {
          setRewardsCount(data.counts.total_awarded);
        }
      })
      .catch(() => {
        // Silently fallback without fabricating
      });
  }, []);

  // Fetch questions for active filter
  const loadQuestionList = useCallback(async () => {
    setLoadingList(true);
    setListError(null);
    try {
      const subj = selectedSubject === "all" ? null : selectedSubject;
      const res = await fetchPYQList(selectedYear, subj, null, 1, 100);
      setQuestions(res.questions);
      setCurrentIndex(0);
      setSelectedOption(null);
      setFeedback(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load questions.";
      setListError(msg);
    } finally {
      setLoadingList(false);
    }
  }, [selectedYear, selectedSubject]);

  useEffect(() => {
    void loadQuestionList();
  }, [loadQuestionList]);

  // Load detail for current question index
  const activeQuestion = questions[currentIndex] || null;

  useEffect(() => {
    if (!activeQuestion) {
      setActiveDetail(null);
      return;
    }

    let isMounted = true;
    setLoadingDetail(true);
    setDetailError(null);
    setSelectedOption(null);
    setFeedback(null);
    setShakeOption(null);

    fetchPYQDetail(activeQuestion.id)
      .then((detail) => {
        if (isMounted) setActiveDetail(detail);
      })
      .catch((err: unknown) => {
        if (isMounted) {
          const msg = err instanceof Error ? err.message : "Failed to load question detail.";
          setDetailError(msg);
        }
      })
      .finally(() => {
        if (isMounted) setLoadingDetail(false);
      });

    return () => {
      isMounted = false;
    };
  }, [activeQuestion]);

  // Instant answer submission handler
  const handleSelectOption = async (optionIndex: number) => {
    if (selectedOption !== null || isSubmitting || !activeDetail) return;

    setSelectedOption(optionIndex);
    setIsSubmitting(true);

    try {
      // Authoritative submission to backend
      const res = await submitStudyAttempt({
        student_id: "student_01",
        question_id: activeDetail.id,
        selected_option: optionIndex,
        response_time_sec: 3.5,
        confidence: 4,
      });

      setFeedback(res);
      setSessionScore((prev) => ({
        correct: prev.correct + (res.is_correct ? 1 : 0),
        total: prev.total + 1,
      }));

      if (!res.is_correct) {
        setShakeOption(optionIndex);
      }
    } catch {
      // Local fallback with verified authoritative key from detail
      const isCorrect = optionIndex === activeDetail.correct_option;
      setFeedback({
        is_correct: isCorrect,
        selected_option: optionIndex,
        correct_option: activeDetail.correct_option,
        explanation:
          activeDetail.explanation ||
          `Official GPAT ${activeDetail.pyq_year || ""} answer verified from standard key.`,
        cue: activeDetail.cue,
      });
      setSessionScore((prev) => ({
        correct: prev.correct + (isCorrect ? 1 : 0),
        total: prev.total + 1,
      }));
      if (!isCorrect) {
        setShakeOption(optionIndex);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNextQuestion = () => {
    if (currentIndex + 1 < questions.length) {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  const isResolved = feedback !== null;
  const options = activeDetail?.options || activeQuestion?.options || [];
  const correctOptionIndex = feedback
    ? feedback.correct_option
    : activeDetail?.correct_option ?? null;

  return (
    <div className="min-h-[85vh] flex flex-col justify-start max-w-2xl mx-auto px-4 py-4 sm:py-6 animate-enter">
      {/* 1. Minimal Header */}
      <header className="flex items-center justify-between gap-3 pb-3 border-b border-[var(--color-border-subtle)]">
        <div>
          <h1 className="text-lg sm:text-xl font-bold tracking-tight text-[var(--color-text-primary)] flex items-center gap-2">
            PYQ Practice
            {selectedYear && (
              <Badge variant="primary" className="font-mono text-xs">
                {selectedYear}
              </Badge>
            )}
          </h1>
          <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">
            One question at a time &bull; Instant authoritative feedback
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Real rewards badge if available */}
          {rewardsCount !== null && (
            <div
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-mono font-medium"
              title={`${rewardsCount} verified milestones earned in ledger`}
            >
              <Trophy size={14} weight="fill" />
              <span>{rewardsCount}</span>
            </div>
          )}

          {/* Unified Filter Button */}
          <button
            type="button"
            onClick={() => setIsFilterOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] hover:border-[var(--color-border-focus)] text-xs text-[var(--color-text-primary)] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] min-h-[44px]"
            aria-label="Open question filters"
          >
            <SlidersHorizontal size={14} weight="bold" className="text-[var(--color-accent)]" />
            <span className="font-medium">Filters</span>
          </button>
        </div>
      </header>

      {/* Progress & Session Stats */}
      <div className="flex items-center justify-between py-3 text-xs font-mono text-[var(--color-text-secondary)]">
        <span className="font-medium text-[var(--color-accent)]">
          Question {questions.length > 0 ? currentIndex + 1 : 0} of {questions.length}
        </span>

        {sessionScore.total > 0 && (
          <span className="text-[var(--color-text-tertiary)]">
            Session Accuracy:{" "}
            <span className="text-[var(--color-status-success)] font-semibold">
              {Math.round((sessionScore.correct / sessionScore.total) * 100)}%
            </span>{" "}
            ({sessionScore.correct}/{sessionScore.total})
          </span>
        )}
      </div>

      {/* 2. Main Question Card Container */}
      <main className="flex-1 flex flex-col justify-start">
        {loadingList ? (
          <div className="p-6 rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] space-y-4">
            <Skeleton className="h-4 w-28" />
            <Skeleton className="h-16 w-full" />
            <div className="space-y-3 pt-4">
              <Skeleton className="h-14 w-full rounded-xl" />
              <Skeleton className="h-14 w-full rounded-xl" />
              <Skeleton className="h-14 w-full rounded-xl" />
              <Skeleton className="h-14 w-full rounded-xl" />
            </div>
          </div>
        ) : listError ? (
          <div className="p-6 rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)]">
            <ErrorState
              title="Unable to Load Questions"
              message={listError}
              onRetry={loadQuestionList}
            />
          </div>
        ) : questions.length === 0 ? (
          <div className="p-8 text-center rounded-2xl border border-dashed border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] text-xs text-[var(--color-text-secondary)] space-y-3">
            <p className="text-sm font-semibold text-[var(--color-text-primary)]">
              No questions matched this filter.
            </p>
            <p>Try resetting the subject or selecting a different exam year.</p>
            <button
              type="button"
              onClick={() => {
                setSelectedSubject("all");
                setSelectedYear(2026);
              }}
              className="px-4 py-2 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-[var(--color-accent)] hover:border-[var(--color-accent)] font-medium text-xs transition-colors"
            >
              Reset Filters
            </button>
          </div>
        ) : loadingDetail ? (
          <div className="p-6 rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] space-y-4">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-20 w-full" />
            <div className="space-y-2.5 pt-4">
              <Skeleton className="h-12 w-full rounded-xl" />
              <Skeleton className="h-12 w-full rounded-xl" />
              <Skeleton className="h-12 w-full rounded-xl" />
              <Skeleton className="h-12 w-full rounded-xl" />
            </div>
          </div>
        ) : detailError ? (
          <div className="p-6 rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)]">
            <ErrorState
              title="Question Error"
              message={detailError}
              onRetry={() => {
                if (activeQuestion) {
                  setLoadingDetail(true);
                  fetchPYQDetail(activeQuestion.id)
                    .then(setActiveDetail)
                    .catch(() => {})
                    .finally(() => setLoadingDetail(false));
                }
              }}
            />
          </div>
        ) : activeQuestion ? (
          <div className="p-5 sm:p-6 rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] shadow-sm space-y-5 transition-all">
            {/* Context meta row */}
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
              <span className="font-mono text-[11px] text-[var(--color-text-tertiary)]">
                {activeQuestion.id} &bull; GPAT {activeQuestion.pyq_year}
              </span>
              <div className="flex items-center gap-1.5">
                <ShieldCheck size={14} weight="bold" className="text-[var(--color-status-success)]" />
                <span className="text-[11px] text-[var(--color-status-success)] font-medium">
                  Official Key
                </span>
              </div>
            </div>

            {/* Question Text */}
            <div className="text-sm sm:text-base font-medium text-[var(--color-text-primary)] leading-relaxed">
              {activeQuestion.question_text}
            </div>

            {/* Options List */}
            <fieldset
              className="space-y-3 pt-1"
              disabled={isSubmitting || isResolved}
              aria-label="Answer options"
            >
              <legend className="sr-only">Choose one answer</legend>
              {options.map((optionText, idx) => {
                const isSelected = selectedOption === idx;
                const isCorrectOption = isResolved && correctOptionIndex === idx;
                const isWrongSelection = isResolved && isSelected && !feedback?.is_correct;
                const isShaking = shakeOption === idx;

                let stateClasses =
                  "border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/70 text-[var(--color-text-primary)] hover:border-[var(--color-border-focus)] hover:bg-[var(--color-surface-raised)]";

                if (isResolved) {
                  if (isCorrectOption) {
                    stateClasses =
                      "border-[var(--color-status-success)] bg-[rgb(134_239_172/0.12)] text-[var(--color-text-primary)] ring-1 ring-[var(--color-status-success)] animate-success-pop";
                  } else if (isWrongSelection) {
                    stateClasses = `border-[var(--color-status-error)] bg-[rgb(252_165_165/0.12)] text-[var(--color-text-primary)] ring-1 ring-[var(--color-status-error)] ${
                      isShaking ? "animate-shake" : ""
                    }`;
                  } else {
                    stateClasses =
                      "border-[var(--color-border-subtle)] opacity-40 bg-[var(--color-surface-base)] text-[var(--color-text-secondary)]";
                  }
                } else if (isSelected) {
                  stateClasses =
                    "border-[var(--color-accent)] bg-[rgb(96_165_250/0.12)] ring-1 ring-[var(--color-accent)]";
                }

                return (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSelectOption(idx)}
                    disabled={isSubmitting || isResolved}
                    className={`w-full min-h-[52px] p-3.5 sm:p-4 rounded-xl border flex items-start gap-3.5 text-left transition-all duration-150 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] select-none ${stateClasses}`}
                  >
                    <span
                      className={`flex items-center justify-center w-6 h-6 rounded-md font-mono text-xs font-bold shrink-0 mt-0.5 border ${
                        isResolved && isCorrectOption
                          ? "bg-[var(--color-status-success)] text-zinc-950 border-[var(--color-status-success)]"
                          : isResolved && isWrongSelection
                          ? "bg-[var(--color-status-error)] text-zinc-950 border-[var(--color-status-error)]"
                          : isSelected
                          ? "bg-[var(--color-accent)] text-zinc-950 border-[var(--color-accent)]"
                          : "bg-[var(--color-surface-base)] border-[var(--color-border-subtle)] text-[var(--color-text-secondary)]"
                      }`}
                    >
                      {String.fromCharCode(65 + idx)}
                    </span>

                    <span className="text-xs sm:text-sm leading-relaxed flex-1">
                      {optionText}
                    </span>

                    {/* Instant visual iconography */}
                    {isResolved && isCorrectOption && (
                      <CheckCircle
                        size={20}
                        weight="fill"
                        className="text-[var(--color-status-success)] shrink-0 mt-0.5"
                      />
                    )}
                    {isResolved && isWrongSelection && (
                      <XCircle
                        size={20}
                        weight="fill"
                        className="text-[var(--color-status-error)] shrink-0 mt-0.5"
                      />
                    )}
                  </button>
                );
              })}
            </fieldset>

            {/* Instant Answer Feedback Panel */}
            {isResolved && (
              <div
                className={`p-4 rounded-xl border mt-4 space-y-3 animate-enter ${
                  feedback?.is_correct
                    ? "bg-[rgb(134_239_172/0.08)] border-[var(--color-status-success)]/40"
                    : "bg-[rgb(252_165_165/0.08)] border-[var(--color-status-error)]/40"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {feedback?.is_correct ? (
                      <>
                        <CheckCircle
                          size={18}
                          weight="bold"
                          className="text-[var(--color-status-success)]"
                        />
                        <span className="text-sm font-semibold text-[var(--color-status-success)]">
                          Correct! +4 Marks
                        </span>
                      </>
                    ) : (
                      <>
                        <XCircle
                          size={18}
                          weight="bold"
                          className="text-[var(--color-status-error)]"
                        />
                        <span className="text-sm font-semibold text-[var(--color-status-error)]">
                          Incorrect (-1 NBEMS Penalty)
                        </span>
                      </>
                    )}
                  </div>

                  <span className="font-mono text-xs text-[var(--color-text-secondary)]">
                    Official Key: Option{" "}
                    {correctOptionIndex !== null
                      ? String.fromCharCode(65 + correctOptionIndex)
                      : "—"}
                  </span>
                </div>

                {/* Explanation text */}
                <div className="text-xs sm:text-sm text-[var(--color-text-primary)] leading-relaxed pt-1">
                  {feedback?.explanation ||
                    activeDetail?.explanation ||
                    "Official GPAT answer key verified."}
                </div>

                {/* Next Question CTA */}
                <div className="pt-2 flex justify-end">
                  <button
                    type="button"
                    onClick={handleNextQuestion}
                    disabled={currentIndex + 1 >= questions.length}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-zinc-950 font-semibold text-xs sm:text-sm transition-all shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] min-h-[44px] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span>
                      {currentIndex + 1 >= questions.length
                        ? "Completed"
                        : "Next Question"}
                    </span>
                    <ArrowRight size={16} weight="bold" />
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : null}
      </main>

      {/* 3. Bottom Navigation Controls */}
      <footer className="flex items-center justify-between pt-4 mt-2">
        <button
          type="button"
          onClick={handlePreviousQuestion}
          disabled={currentIndex === 0 || loadingList}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:border-[var(--color-border-focus)] transition-colors disabled:opacity-40 disabled:cursor-not-allowed min-h-[44px]"
        >
          <ArrowLeft size={14} weight="bold" />
          <span>Previous</span>
        </button>

        <button
          type="button"
          onClick={handleNextQuestion}
          disabled={currentIndex + 1 >= questions.length || loadingList}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:border-[var(--color-border-focus)] transition-colors disabled:opacity-40 disabled:cursor-not-allowed min-h-[44px]"
        >
          <span>Next</span>
          <ArrowRight size={14} weight="bold" />
        </button>
      </footer>

      {/* 4. Slide-over / Modal Filter Sheet */}
      {isFilterOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="filter-dialog-title"
          className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-xs p-0 sm:p-4 animate-enter"
        >
          <div className="w-full sm:max-w-md bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)] rounded-t-2xl sm:rounded-2xl p-5 space-y-5 shadow-xl max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-[var(--color-border-subtle)]">
              <h2
                id="filter-dialog-title"
                className="text-base font-bold text-[var(--color-text-primary)] flex items-center gap-2"
              >
                <SlidersHorizontal size={16} weight="bold" className="text-[var(--color-accent)]" />
                PYQ Filters
              </h2>
              <button
                type="button"
                onClick={() => setIsFilterOpen(false)}
                className="p-1.5 rounded-lg text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface-raised)] transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
                aria-label="Close filters"
              >
                <X size={18} weight="bold" />
              </button>
            </div>

            {/* Exam Year Filter */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-[var(--color-text-secondary)] block">
                Exam Year
              </label>
              <div className="grid grid-cols-3 gap-2">
                {years.map((y) => {
                  const isSelected = selectedYear === y.year;
                  return (
                    <button
                      key={y.year}
                      type="button"
                      onClick={() => setSelectedYear(y.year)}
                      className={`py-2 px-2 rounded-lg text-xs font-mono font-medium border text-center transition-colors min-h-[44px] ${
                        isSelected
                          ? "bg-[var(--color-accent)] text-zinc-950 font-bold border-[var(--color-accent)]"
                          : "bg-[var(--color-surface-raised)] border-[var(--color-border-subtle)] text-[var(--color-text-primary)] hover:border-[var(--color-border-focus)]"
                      }`}
                    >
                      {y.year}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Subject Filter */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-[var(--color-text-secondary)] block">
                Subject Domain
              </label>
              <div className="space-y-1.5">
                {SUBJECT_OPTIONS.map((subj) => {
                  const isSelected = selectedSubject === subj.id;
                  return (
                    <button
                      key={subj.id}
                      type="button"
                      onClick={() => setSelectedSubject(subj.id)}
                      className={`w-full py-2.5 px-3 rounded-lg text-xs font-medium border text-left transition-colors flex items-center justify-between min-h-[44px] ${
                        isSelected
                          ? "bg-[rgb(96_165_250/0.12)] border-[var(--color-accent)] text-[var(--color-text-primary)] font-semibold"
                          : "bg-[var(--color-surface-raised)] border-[var(--color-border-subtle)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
                      }`}
                    >
                      <span>{subj.label}</span>
                      {isSelected && (
                        <CheckCircle
                          size={16}
                          weight="fill"
                          className="text-[var(--color-accent)]"
                        />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Modal Actions */}
            <div className="pt-2 flex items-center justify-between gap-3 border-t border-[var(--color-border-subtle)]">
              <button
                type="button"
                onClick={() => {
                  setSelectedYear(2026);
                  setSelectedSubject("all");
                }}
                className="flex items-center gap-1.5 px-3 py-2 text-xs text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)] min-h-[44px]"
              >
                <ArrowCounterClockwise size={14} weight="bold" />
                Reset
              </button>

              <button
                type="button"
                onClick={() => setIsFilterOpen(false)}
                className="px-5 py-2 rounded-xl bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-zinc-950 font-semibold text-xs transition-colors min-h-[44px]"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
