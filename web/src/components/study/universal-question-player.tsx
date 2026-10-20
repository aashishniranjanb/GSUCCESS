"use client";

import React, { useState, useEffect, useRef } from "react";
import { AttemptFeedbackResponse } from "@/lib/api/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  CheckCircle,
  XCircle,
  Lightbulb,
  ArrowRight,
  ArrowLeft,
  Clock,
  BookOpen,
  Image as ImageIcon,
  ShieldCheck,
  WarningCircle,
  Sparkle,
} from "@phosphor-icons/react/dist/ssr";

export interface UniversalQuestionItem {
  id: string;
  concept_id?: string;
  concept_name?: string;
  topic_name?: string;
  question_text: string;
  options: string[];
  difficulty?: number;
  candidate_type?: string;
  provenance?: string;
  verification_status?: string;
  answer_status?: string;
  pyq_year?: number | null;
  cognitive_level?: string;
  media_url?: string | null;
  media_alt?: string | null;
  media_caption?: string | null;
  cue?: string | null;
  explanation?: string | null;
  source_page?: number | null;
  distractor_reasons?: Record<string, string> | null;
  // If previously answered in session
  previously_answered?: boolean;
  previous_is_correct?: boolean;
  previous_selected_option?: number | null;
}

export interface UniversalQuestionPlayerProps {
  question: UniversalQuestionItem;
  currentIndex: number;
  totalQuestions: number;
  sessionModeTag?: string; // e.g., "Daily Mission", "PYQ Practice", "Topic Drill"
  studentId?: string;
  onSubmitAnswer?: (
    questionId: string,
    selectedOption: number,
    responseTimeSec: number,
    confidence: number
  ) => Promise<AttemptFeedbackResponse>;
  // For local or self-contained grading when standalone (e.g., browse-only mode)
  localCorrectOption?: number | null;
  onNext?: () => void;
  onPrevious?: () => void;
  isLast?: boolean;
  onBackToList?: () => void;
}

const CONFIDENCE_LEVELS = [
  { value: 1, label: "Guess / Unsure", badge: "Guess (1/5)" },
  { value: 2, label: "Low Confidence", badge: "Low (2/5)" },
  { value: 3, label: "Moderate", badge: "Moderate (3/5)" },
  { value: 4, label: "Confident", badge: "Confident (4/5)" },
  { value: 5, label: "Certain", badge: "Certain (5/5)" },
];

export function UniversalQuestionPlayer({
  question,
  currentIndex,
  totalQuestions,
  sessionModeTag = "Study Session",
  onSubmitAnswer,
  localCorrectOption,
  onNext,
  onPrevious,
  isLast = false,
  onBackToList,
}: UniversalQuestionPlayerProps) {
  const [selectedOption, setSelectedOption] = useState<number | null>(
    question.previously_answered && question.previous_selected_option !== undefined
      ? question.previous_selected_option
      : null
  );
  const [confidence, setConfidence] = useState<number>(3);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<AttemptFeedbackResponse | null>(null);
  const [localSubmitted, setLocalSubmitted] = useState<boolean>(
    Boolean(question.previously_answered)
  );
  const [error, setError] = useState<string | null>(null);
  const [elapsedSec, setElapsedSec] = useState<number>(0);

  const startTimeRef = useRef<number>(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize and run timer per question
  useEffect(() => {
    startTimeRef.current = Date.now();
    const currentStart = startTimeRef.current;
    setElapsedSec(0);
    setError(null);

    // If item was already answered prior to mount
    if (question.previously_answered) {
      setLocalSubmitted(true);
      setSelectedOption(
        question.previous_selected_option !== undefined
          ? question.previous_selected_option
          : null
      );
    } else {
      setSelectedOption(null);
      setLocalSubmitted(false);
      setFeedback(null);
    }

    timerRef.current = setInterval(() => {
      setElapsedSec(Math.floor((Date.now() - currentStart) / 1000));
    }, 1000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [question.id, question.previously_answered, question.previous_selected_option]);

  const isResolved = localSubmitted || feedback !== null;

  const handleOptionSelect = (optIndex: number) => {
    if (isResolved || isSubmitting) return;
    setSelectedOption(optIndex);
  };

  const handleSubmit = async () => {
    if (selectedOption === null || isSubmitting || isResolved) return;
    setIsSubmitting(true);
    setError(null);

    const responseTimeSec = Math.max(
      1,
      (Date.now() - (startTimeRef.current || Date.now())) / 1000
    );

    if (timerRef.current) clearInterval(timerRef.current);

    if (onSubmitAnswer) {
      try {
        const res = await onSubmitAnswer(
          question.id,
          selectedOption,
          responseTimeSec,
          confidence
        );
        setFeedback(res);
        setLocalSubmitted(true);
      } catch (err: unknown) {
        const msg =
          err instanceof Error
            ? err.message
            : "Failed to submit attempt. Check network connection.";
        setError(msg);
      } finally {
        setIsSubmitting(false);
      }
    } else {
      // Local self-contained submission mode (e.g., PYQ browser)
      setLocalSubmitted(true);
      setIsSubmitting(false);
    }
  };

  const handleNextClick = () => {
    setSelectedOption(null);
    setFeedback(null);
    setLocalSubmitted(false);
    setError(null);
    setElapsedSec(0);
    if (onNext) onNext();
  };

  // Determine correct option and status
  const effectiveCorrectOption = feedback
    ? feedback.correct_option
    : localCorrectOption !== undefined && localCorrectOption !== null
    ? localCorrectOption
    : null;

  const isCorrect =
    feedback !== null
      ? feedback.is_correct
      : question.previously_answered && question.previous_is_correct !== undefined
      ? question.previous_is_correct
      : effectiveCorrectOption !== null && selectedOption !== null
      ? selectedOption === effectiveCorrectOption
      : false;

  const distractorReason =
    feedback?.distractor_reason ||
    (selectedOption !== null && question.distractor_reasons
      ? question.distractor_reasons[selectedOption.toString()]
      : null);

  const isAnswerKeyVerified =
    question.answer_status === "VERIFIED" ||
    question.verification_status === "VERIFIED";

  // Provenance label
  const provenanceLabel =
    question.provenance ||
    (question.pyq_year ? `GPAT ${question.pyq_year} Official` : "Baseline Question Bank");

  return (
    <Card className="border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] relative overflow-hidden transition-all duration-200 shadow-sm">
      <CardHeader className="space-y-3 pb-4 border-b border-[var(--color-border-subtle)]">
        {/* Navigation & Session Meta Bar */}
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            {onBackToList && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onBackToList}
                className="gap-1 text-xs -ml-2 text-[var(--color-text-secondary)]"
              >
                <ArrowLeft size={14} weight="bold" />
                Back
              </Button>
            )}
            <Badge variant="primary" className="font-mono text-[10px]">
              {sessionModeTag}
            </Badge>
            <span className="text-xs font-mono font-medium text-[var(--color-accent)]">
              Q{currentIndex + 1} of {totalQuestions}
            </span>
          </div>

          <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-secondary)]">
            {question.difficulty && (
              <Badge variant="default" className="text-[10px] font-mono">
                Diff {question.difficulty}/5
              </Badge>
            )}
            <div className="flex items-center gap-1">
              <Clock size={13} weight="bold" />
              <span>{elapsedSec}s</span>
            </div>
          </div>
        </div>

        {/* Concept / Topic Attribution */}
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
          <div className="flex items-center gap-1.5 text-[var(--color-text-secondary)]">
            <BookOpen size={14} weight="bold" className="text-[var(--color-accent)] shrink-0" />
            <span className="font-medium text-[var(--color-text-primary)]">
              {question.concept_name || question.topic_name || "Pharmaceutical Sciences"}
            </span>
          </div>

          <div className="flex items-center gap-1.5 font-mono text-[10px]">
            {question.candidate_type && (
              <Badge variant="default" className="uppercase text-[9px]">
                {question.candidate_type.replace(/_/g, " ")}
              </Badge>
            )}
            <Badge
              variant={isAnswerKeyVerified ? "success" : "default"}
              className="text-[9px]"
            >
              {isAnswerKeyVerified ? "Official Key Verified" : "Standard Key"}
            </Badge>
          </div>
        </div>

        {/* Question Text */}
        <CardTitle className="text-base sm:text-lg font-semibold text-[var(--color-text-primary)] leading-relaxed pt-1">
          {question.question_text}
        </CardTitle>

        {/* Multimodal Scientific Media / Structure / Diagram */}
        {question.media_url && (
          <div className="mt-3 p-3 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] space-y-2">
            <div className="flex items-center gap-1.5 text-xs font-mono text-[var(--color-text-tertiary)]">
              <ImageIcon size={14} weight="bold" className="text-[var(--color-accent)]" />
              <span>Scientific Diagram / Structure</span>
            </div>
            <div className="flex justify-center p-2 rounded-lg bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)] overflow-hidden">
              {/* Image with fallback styling and alt text */}
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={
                  question.media_url.startsWith("http")
                    ? question.media_url
                    : `/media/${question.media_url.replace(/^\/?(media\/)?/, "")}`
                }
                alt={question.media_alt || "Chemical structure or scientific graph for question"}
                className="max-h-72 object-contain rounded transition-transform duration-200 hover:scale-[1.02]"
                loading="eager"
              />
            </div>
            {question.media_caption && (
              <p className="text-xs text-[var(--color-text-secondary)] italic text-center">
                {question.media_caption}
              </p>
            )}
          </div>
        )}
      </CardHeader>

      <CardContent className="space-y-5 pt-4">
        {/* Answer Options Radios */}
        <fieldset className="space-y-2.5" disabled={isSubmitting || isResolved}>
          <legend className="sr-only">Select the correct answer option</legend>

          {question.options.map((optText, optIdx) => {
            const isSelected = selectedOption === optIdx;
            const isCorrectOption =
              isResolved && effectiveCorrectOption !== null
                ? optIdx === effectiveCorrectOption
                : isResolved && isCorrect && isSelected;
            const isIncorrectSelection =
              isResolved && isSelected && !isCorrect;

            let optionStyle =
              "border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/60 text-[var(--color-text-primary)] hover:border-[var(--color-border-focus)]";

            if (isResolved) {
              if (isCorrectOption) {
                optionStyle =
                  "border-[var(--color-status-success)] bg-[rgb(134_239_172/0.1)] text-[var(--color-text-primary)] font-medium";
              } else if (isIncorrectSelection) {
                optionStyle =
                  "border-[var(--color-status-error)] bg-[rgb(252_165_165/0.1)] text-[var(--color-text-primary)]";
              } else {
                optionStyle =
                  "border-[var(--color-border-subtle)] opacity-50 bg-[var(--color-surface-base)]";
              }
            } else if (isSelected) {
              optionStyle =
                "border-[var(--color-accent)] bg-[rgb(96_165_250/0.1)] text-[var(--color-text-primary)] font-medium ring-1 ring-[var(--color-accent)]";
            }

            return (
              <label
                key={optIdx}
                className={`flex items-start gap-3 p-3.5 rounded-lg border cursor-pointer transition-colors duration-150 select-none ${optionStyle}`}
              >
                <input
                  type="radio"
                  name={`question-${question.id}`}
                  checked={isSelected}
                  onChange={() => handleOptionSelect(optIdx)}
                  disabled={isResolved || isSubmitting}
                  className="mt-0.5 h-4 w-4 text-[var(--color-accent)] focus:ring-[var(--color-accent)] cursor-pointer"
                />
                <span className="text-xs sm:text-sm leading-relaxed flex-1">
                  <span className="font-mono text-xs text-[var(--color-text-secondary)] mr-2 font-semibold">
                    {String.fromCharCode(65 + optIdx)}.
                  </span>
                  {optText}
                </span>
                {isResolved && isCorrectOption && (
                  <CheckCircle
                    size={18}
                    weight="bold"
                    className="text-[var(--color-status-success)] shrink-0 mt-0.5"
                    aria-label="Official correct answer"
                  />
                )}
                {isResolved && isIncorrectSelection && (
                  <XCircle
                    size={18}
                    weight="bold"
                    className="text-[var(--color-status-error)] shrink-0 mt-0.5"
                    aria-label="Incorrect selection"
                  />
                )}
              </label>
            );
          })}
        </fieldset>

        {/* Confidence Calibration Selector (Active before submission) */}
        {!isResolved && (
          <div className="p-3 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-medium text-[var(--color-text-secondary)] flex items-center gap-1">
                <Sparkle size={13} weight="bold" className="text-[var(--color-accent)]" />
                Confidence Rating (FSRS Calibration):
              </span>
              <span className="font-mono text-xs text-[var(--color-accent)] font-semibold">
                {CONFIDENCE_LEVELS[confidence - 1]?.label}
              </span>
            </div>
            <div className="grid grid-cols-5 gap-1.5">
              {CONFIDENCE_LEVELS.map((lvl) => (
                <button
                  key={lvl.value}
                  type="button"
                  onClick={() => setConfidence(lvl.value)}
                  disabled={isSubmitting}
                  className={`py-1.5 px-1 rounded text-center text-xs font-mono transition-colors border ${
                    confidence === lvl.value
                      ? "border-[var(--color-accent)] bg-[rgb(96_165_250/0.15)] text-[var(--color-accent)] font-bold shadow-sm"
                      : "border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] text-[var(--color-text-secondary)] hover:border-[var(--color-border-focus)]"
                  }`}
                >
                  {lvl.value}
                </button>
              ))}
            </div>
            <p className="text-[10px] text-[var(--color-text-tertiary)] italic">
              Your confidence score adjusts spaced-repetition memory intervals and identifies overconfidence traps.
            </p>
          </div>
        )}

        {/* Error notification */}
        {error && (
          <div
            role="alert"
            className="p-3 rounded-md bg-[rgb(252_165_165/0.1)] border border-[var(--color-status-error)]/30 text-xs text-[var(--color-status-error)] flex items-center gap-2"
          >
            <WarningCircle size={15} weight="bold" className="shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Action Button: Check / Confirm Answer */}
        {!isResolved ? (
          <div className="flex justify-between items-center pt-2">
            <div>
              {onPrevious && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={onPrevious}
                  disabled={currentIndex === 0 || isSubmitting}
                  className="gap-1 text-xs"
                >
                  <ArrowLeft size={14} weight="bold" />
                  Previous
                </Button>
              )}
            </div>

            <Button
              onClick={handleSubmit}
              disabled={selectedOption === null || isSubmitting}
              className="gap-2 text-sm font-semibold px-5"
            >
              {isSubmitting ? "Verifying..." : "Confirm & Submit"}
            </Button>
          </div>
        ) : (
          /* Evidence & Provenance Post-Submission Feedback Panel */
          <div className="space-y-4 pt-2 animate-enter">
            <div
              className={`p-4 rounded-lg border ${
                isCorrect
                  ? "bg-[rgb(134_239_172/0.08)] border-[var(--color-status-success)]/30"
                  : "bg-[rgb(252_165_165/0.08)] border-[var(--color-status-error)]/30"
              }`}
            >
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2.5">
                <div className="flex items-center gap-2">
                  {isCorrect ? (
                    <>
                      <CheckCircle
                        size={18}
                        weight="bold"
                        className="text-[var(--color-status-success)]"
                      />
                      <span className="text-sm font-semibold text-[var(--color-status-success)]">
                        Correct Answer
                        {effectiveCorrectOption !== null &&
                          ` • Option ${String.fromCharCode(65 + effectiveCorrectOption)}`}
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
                        Incorrect Choice
                        {effectiveCorrectOption !== null &&
                          ` • Official Key: Option ${String.fromCharCode(65 + effectiveCorrectOption)}`}
                      </span>
                    </>
                  )}
                </div>

                <div className="flex items-center gap-2 font-mono text-[10px]">
                  {feedback?.fsrs_rating && (
                    <Badge variant="default">
                      FSRS: {feedback.fsrs_rating}
                    </Badge>
                  )}
                  {feedback?.calibration_category && (
                    <Badge variant="default" className="uppercase">
                      {feedback.calibration_category.replace(/_/g, " ")}
                    </Badge>
                  )}
                  <span className="flex items-center gap-1 text-[var(--color-text-secondary)]">
                    <ShieldCheck size={13} weight="bold" className="text-[var(--color-accent)]" />
                    {provenanceLabel}
                  </span>
                </div>
              </div>

              {/* Distractor Misconception (if student selected a wrong trap choice) */}
              {distractorReason && (
                <div className="p-2.5 mb-3 rounded bg-[var(--color-surface-base)] border border-[var(--color-status-error)]/20 text-xs text-[var(--color-status-error)] font-medium">
                  <strong>Misconception Rationale:</strong> {distractorReason}
                </div>
              )}

              {/* Full Scientific Explanation */}
              {(feedback?.explanation || question.explanation) ? (
                <div className="space-y-1">
                  <span className="text-[11px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider block">
                    Conceptual Evidence &amp; Explanation
                  </span>
                  <p className="text-xs sm:text-sm text-[var(--color-text-primary)] leading-relaxed">
                    {feedback?.explanation || question.explanation}
                  </p>
                </div>
              ) : (
                <div className="text-xs text-[var(--color-text-tertiary)] italic flex items-center gap-1">
                  <WarningCircle size={14} weight="bold" />
                  Official answer verified from source key. Conceptual explanation is being indexed in knowledge baseline.
                </div>
              )}

              {/* Source Page Citation */}
              {(feedback?.source_page || question.source_page) && (
                <div className="mt-2 text-[11px] font-mono text-[var(--color-text-tertiary)]">
                  Citing Baseline Reference Page: {feedback?.source_page || question.source_page}
                </div>
              )}

              {/* Memory Recall Cue */}
              {(feedback?.cue || question.cue) && (
                <div className="mt-3 pt-3 border-t border-[var(--color-border-subtle)] flex items-start gap-2 text-xs text-[var(--color-text-secondary)]">
                  <Lightbulb
                    size={16}
                    weight="bold"
                    className="text-[var(--color-status-warning)] shrink-0 mt-0.5"
                  />
                  <span>
                    <strong className="text-[var(--color-text-primary)]">Recall Cue:</strong>{" "}
                    {feedback?.cue || question.cue}
                  </span>
                </div>
              )}
            </div>

            {/* Navigation Buttons */}
            <div className="flex justify-between items-center pt-1">
              <div>
                {onPrevious && (
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={onPrevious}
                    disabled={currentIndex === 0}
                    className="gap-1 text-xs"
                  >
                    <ArrowLeft size={14} weight="bold" />
                    Previous
                  </Button>
                )}
              </div>

              {onNext && (
                <Button onClick={handleNextClick} className="gap-2 text-sm font-semibold px-5 ml-auto">
                  <span>{isLast ? "Complete Session" : "Next Question"}</span>
                  <ArrowRight size={15} weight="bold" />
                </Button>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
