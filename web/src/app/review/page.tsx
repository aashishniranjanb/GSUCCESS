"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import {
  fetchReviewQueue,
  submitReviewRating,
} from "@/lib/api/review";
import {
  ReviewQueueCard,
  FSRSRating,
  ReviewRatingResponse,
} from "@/lib/api/types";
import { ReviewCardInteractive } from "@/components/review/review-card-interactive";
import { Card, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton, ErrorState, EmptyState } from "@/components/ui/states";
import {
  ArrowsCounterClockwise,
  CheckCircle,
  Brain,
  WifiSlash,
} from "@phosphor-icons/react/dist/ssr";

const STUDENT_ID = "student_01";

export default function ReviewPage() {
  const [cards, setCards] = useState<ReviewQueueCard[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isOffline, setIsOffline] = useState<boolean>(false);
  const [sessionCompleted, setSessionCompleted] = useState<boolean>(false);
  const [completedCount, setCompletedCount] = useState<number>(0);

  // Offline network listener
  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  // Fetch actual due review queue from backend
  const loadQueue = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchReviewQueue(STUDENT_ID);
      setCards(res.review_items);
      setCurrentIndex(0);
      setSessionCompleted(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load due review queue.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadQueue();
  }, [loadQueue]);

  // Handle rating submission to FastAPI
  const handleRatingSubmit = async (
    rating: FSRSRating,
    responseTimeSec: number
  ): Promise<ReviewRatingResponse> => {
    const currentCard = cards[currentIndex];

    const res = await submitReviewRating({
      student_id: STUDENT_ID,
      card_id: currentCard.card_id,
      question_id: currentCard.question_id,
      rating: rating,
      response_time_sec: responseTimeSec,
    });

    setCompletedCount((prev) => prev + 1);

    // Progress to next card or complete
    if (currentIndex + 1 < cards.length) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      setSessionCompleted(true);
    }

    return res;
  };

  // Loading View
  if (loading) {
    return (
      <div className="space-y-6 animate-enter max-w-2xl mx-auto">
        <div className="space-y-2">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-72" />
        </div>
        <Card className="p-6 space-y-4">
          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-28 w-full" />
        </Card>
      </div>
    );
  }

  // Error View
  if (error && cards.length === 0) {
    return (
      <div className="space-y-6 animate-enter max-w-2xl mx-auto">
        <ErrorState
          title="Review Queue Unavailable"
          message={error}
          onRetry={loadQueue}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-enter">
      {/* Offline Alert */}
      {isOffline && (
        <div
          role="status"
          className="p-3 rounded-md bg-[rgb(252_211_77/0.1)] border border-[var(--color-status-warning)]/30 text-xs text-[var(--color-status-warning)] flex items-center gap-2 max-w-2xl mx-auto"
        >
          <WifiSlash size={16} weight="bold" />
          <span>Offline mode: FSRS reviews require a server connection to guarantee memory scheduling.</span>
        </div>
      )}

      {/* Header Context */}
      <div className="flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-2 pb-4 border-b border-[var(--color-border-subtle)]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--color-text-primary)]">
            FSRS Active Recall Review
          </h1>
          <p className="text-xs text-[var(--color-text-secondary)] mt-1">
            Free Spaced Repetition Scheduler v4 &bull; Retrievability decay intervals
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="primary" className="font-mono text-[11px]">
            {cards.length} Cards Due
          </Badge>
        </div>
      </div>

      {/* Session Completed State */}
      {sessionCompleted ? (
        <Card className="border border-[var(--color-status-success)]/40 bg-[rgb(134_239_172/0.05)] text-center py-12 px-6 max-w-2xl mx-auto">
          <div className="h-12 w-12 rounded-full bg-[rgb(134_239_172/0.15)] flex items-center justify-center text-[var(--color-status-success)] mx-auto mb-4">
            <CheckCircle size={28} weight="bold" />
          </div>
          <CardTitle className="text-xl font-bold text-[var(--color-text-primary)]">
            Review Queue Clean
          </CardTitle>
          <CardDescription className="max-w-md mx-auto mt-2 text-xs sm:text-sm">
            All scheduled FSRS memory cards have been reviewed. Stability and difficulty matrices
            have been updated in your learner database (`gpat_knowledge.db`).
          </CardDescription>

          <div className="mt-6 flex justify-center gap-4 text-xs font-mono">
            <div className="p-3 rounded-md bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)]">
              <span className="text-[var(--color-text-secondary)] block">Cards Reviewed</span>
              <span className="text-base font-bold text-[var(--color-text-primary)]">
                {completedCount}
              </span>
            </div>
            <div className="p-3 rounded-md bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)]">
              <span className="text-[var(--color-text-secondary)] block">Due Remaining</span>
              <span className="text-base font-bold text-[var(--color-status-success)]">0</span>
            </div>
          </div>

          <div className="mt-6 flex justify-center gap-3">
            <Button onClick={loadQueue} variant="secondary" size="sm" className="gap-1.5 text-xs">
              <ArrowsCounterClockwise size={14} weight="bold" />
              Check for Due Cards
            </Button>
            <Link href="/progress">
              <Button size="sm" className="text-xs">
                Inspect Memory Retention
              </Button>
            </Link>
          </div>
        </Card>
      ) : cards.length === 0 ? (
        /* Empty Due Queue State */
        <EmptyState
          title="No Cards Due for Review"
          description="Your active recall queue is currently clear. New reviews will be scheduled automatically based on your FSRS forgetting curves."
          icon={<Brain size={24} weight="bold" />}
          actionLabel="Refresh Queue"
          onAction={loadQueue}
        />
      ) : (
        /* Active Card Review Workspace */
        <div className="py-2">
          <ReviewCardInteractive
            card={cards[currentIndex]}
            currentIndex={currentIndex}
            totalCards={cards.length}
            onSubmitRating={handleRatingSubmit}
          />
        </div>
      )}
    </div>
  );
}
