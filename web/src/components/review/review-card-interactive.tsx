"use client";

import React, { useState, useEffect, useRef } from "react";
import { ReviewQueueCard, FSRSRating, ReviewRatingResponse } from "@/lib/api/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Eye,
  CheckCircle,
  Lightbulb,
  Clock,
  BookOpen,
} from "@phosphor-icons/react/dist/ssr";

interface ReviewCardInteractiveProps {
  card: ReviewQueueCard;
  currentIndex: number;
  totalCards: number;
  onSubmitRating: (rating: FSRSRating, responseTimeSec: number) => Promise<ReviewRatingResponse>;
}

export function ReviewCardInteractive({
  card,
  currentIndex,
  totalCards,
  onSubmitRating,
}: ReviewCardInteractiveProps) {
  const [isRevealed, setIsRevealed] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [elapsedSec, setElapsedSec] = useState<number>(0);
  const startTimeRef = useRef<number>(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize per-card timer
  useEffect(() => {
    setIsRevealed(false);
    setError(null);
    setElapsedSec(0);
    startTimeRef.current = Date.now();
    const currentStart = startTimeRef.current;

    timerRef.current = setInterval(() => {
      setElapsedSec(Math.floor((Date.now() - currentStart) / 1000));
    }, 1000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [card.card_id]);

  const handleReveal = () => {
    setIsRevealed(true);
  };

  const handleRating = async (rating: FSRSRating) => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    setError(null);

    const responseTime = Math.max(1, (Date.now() - (startTimeRef.current || Date.now())) / 1000);

    try {
      if (timerRef.current) clearInterval(timerRef.current);
      await onSubmitRating(rating, responseTime);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to record rating. Check connection.";
      setError(msg);
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] relative overflow-hidden transition-all duration-200 max-w-2xl mx-auto">
      <CardHeader className="space-y-3 pb-4 border-b border-[var(--color-border-subtle)]">
        {/* Meta Bar */}
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-medium text-[var(--color-accent)]">
              Card {currentIndex + 1} of {totalCards}
            </span>
            <span className="text-xs text-[var(--color-text-tertiary)]">&bull;</span>
            <span className="text-xs font-mono text-[var(--color-text-secondary)]">
              Stability: {card.stability_days}d
            </span>
          </div>

          <div className="flex items-center gap-1.5 text-xs font-mono text-[var(--color-text-secondary)]">
            <Clock size={13} weight="bold" />
            <span>{elapsedSec}s</span>
          </div>
        </div>

        {/* Concept Label */}
        {card.concept_name && (
          <div className="text-xs font-medium text-[var(--color-text-tertiary)] flex items-center gap-1">
            <BookOpen size={13} weight="bold" />
            <span>{card.concept_name}</span>
          </div>
        )}

        {/* Card Front: Recall Prompt */}
        <div className="space-y-1 pt-1">
          <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-text-tertiary)] block">
            Recall Prompt (Question Front)
          </span>
          <CardTitle className="text-base sm:text-lg font-semibold text-[var(--color-text-primary)] leading-relaxed">
            {card.question_text}
          </CardTitle>
        </div>
      </CardHeader>

      <CardContent className="space-y-6 pt-5">
        {/* Options Prompt Context */}
        {card.options.length > 0 && !isRevealed && (
          <div className="space-y-2">
            <span className="text-[11px] font-mono text-[var(--color-text-tertiary)] block">
              Options Context:
            </span>
            <div className="space-y-1.5">
              {card.options.map((opt, idx) => (
                <div
                  key={idx}
                  className="p-2.5 rounded-md bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)]/70 text-xs text-[var(--color-text-secondary)]"
                >
                  <span className="font-mono text-[11px] text-[var(--color-text-tertiary)] mr-2">
                    {String.fromCharCode(65 + idx)}.
                  </span>
                  {opt}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Card Back: Revealed Answer & Explanation */}
        {isRevealed && (
          <div className="space-y-4 animate-enter">
            {/* Correct Answer Display */}
            {card.options.length > 0 && (
              <div className="p-3.5 rounded-lg border border-[var(--color-status-success)]/40 bg-[rgb(134_239_172/0.08)]">
                <span className="text-[11px] font-mono uppercase text-[var(--color-status-success)] font-semibold flex items-center gap-1.5 mb-1">
                  <CheckCircle size={14} weight="bold" />
                  Correct Answer (Option {String.fromCharCode(65 + card.correct_option)})
                </span>
                <p className="text-xs sm:text-sm font-medium text-[var(--color-text-primary)] leading-relaxed">
                  {card.options[card.correct_option]}
                </p>
              </div>
            )}

            {/* Scientific Explanation */}
            {card.explanation && (
              <div className="p-3.5 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] space-y-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-text-tertiary)] block">
                  Authoritative Scientific Rationale
                </span>
                <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed whitespace-pre-line">
                  {card.explanation}
                </p>
              </div>
            )}

            {/* Memory Recall Cue */}
            {card.cue && (
              <div className="p-3 rounded-lg bg-[rgb(252_211_77/0.08)] border border-[var(--color-status-warning)]/30 flex items-start gap-2 text-xs text-[var(--color-status-warning)]">
                <Lightbulb size={16} weight="bold" className="shrink-0 mt-0.5" />
                <span>
                  <strong>Recall Cue:</strong> {card.cue}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Error notice */}
        {error && (
          <div
            role="alert"
            className="p-3 rounded-md bg-[rgb(252_165_165/0.1)] border border-[var(--color-status-error)]/30 text-xs text-[var(--color-status-error)]"
          >
            {error}
          </div>
        )}

        {/* Action Controls */}
        {!isRevealed ? (
          <div className="pt-2 flex justify-center">
            <Button
              onClick={handleReveal}
              size="lg"
              className="gap-2 text-sm font-semibold w-full sm:w-auto px-8"
            >
              <Eye size={16} weight="bold" />
              Reveal Answer
            </Button>
          </div>
        ) : (
          /* FSRS Rating Buttons */
          <div className="space-y-3 pt-2">
            <div className="text-center text-xs text-[var(--color-text-tertiary)] font-mono">
              Rate your active recall difficulty to update FSRS memory stability:
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              <Button
                variant="secondary"
                onClick={() => handleRating("Again")}
                disabled={isSubmitting}
                className="flex flex-col items-center justify-center h-14 border-[var(--color-status-error)]/40 hover:bg-[rgb(252_165_165/0.1)] text-xs"
              >
                <span className="font-bold text-[var(--color-status-error)]">Again</span>
                <span className="text-[10px] text-[var(--color-text-tertiary)] font-mono">&lt; 10 mins</span>
              </Button>

              <Button
                variant="secondary"
                onClick={() => handleRating("Hard")}
                disabled={isSubmitting}
                className="flex flex-col items-center justify-center h-14 border-[var(--color-status-warning)]/40 hover:bg-[rgb(252_211_77/0.1)] text-xs"
              >
                <span className="font-bold text-[var(--color-status-warning)]">Hard</span>
                <span className="text-[10px] text-[var(--color-text-tertiary)] font-mono">Short interval</span>
              </Button>

              <Button
                variant="secondary"
                onClick={() => handleRating("Good")}
                disabled={isSubmitting}
                className="flex flex-col items-center justify-center h-14 border-[var(--color-accent)]/40 hover:bg-[rgb(96_165_250/0.1)] text-xs"
              >
                <span className="font-bold text-[var(--color-accent)]">Good</span>
                <span className="text-[10px] text-[var(--color-text-tertiary)] font-mono">Standard FSRS</span>
              </Button>

              <Button
                variant="secondary"
                onClick={() => handleRating("Easy")}
                disabled={isSubmitting}
                className="flex flex-col items-center justify-center h-14 border-[var(--color-status-success)]/40 hover:bg-[rgb(134_239_172/0.1)] text-xs"
              >
                <span className="font-bold text-[var(--color-status-success)]">Easy</span>
                <span className="text-[10px] text-[var(--color-text-tertiary)] font-mono">Extended</span>
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
