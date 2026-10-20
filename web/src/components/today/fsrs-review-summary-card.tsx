"use client";

import React from "react";
import Link from "next/link";
import {
  ArrowsCounterClockwise,
  ArrowRight,
  CheckCircle,
  Cards
} from "@phosphor-icons/react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface FsrsReviewSummaryCardProps {
  dueCount: number;
  isLoading: boolean;
}

export function FsrsReviewSummaryCard({ dueCount, isLoading }: FsrsReviewSummaryCardProps) {
  return (
    <Card className="interactive-card border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] relative overflow-hidden flex flex-col justify-between shadow-xs">
      {/* Subtle flashcard watermark */}
      <div
        className="absolute -right-3 -bottom-3 text-purple-400 opacity-[0.04] pointer-events-none select-none"
        aria-hidden="true"
      >
        <Cards size={110} weight="fill" />
      </div>

      <CardHeader className="p-3.5 sm:p-5 pb-1.5 sm:pb-2 relative z-10">
        <div className="flex items-center justify-between">
          <span className="text-[10px] sm:text-[11px] font-mono tracking-wider uppercase text-purple-400 flex items-center gap-1.5 font-semibold">
            <ArrowsCounterClockwise size={14} weight="bold" />
            Spaced Repetition
          </span>
          <Badge
            variant={dueCount > 0 ? "warning" : "default"}
            className="text-[9px] sm:text-[10px] py-0 px-1.5 font-mono"
          >
            {dueCount > 0 ? `${dueCount} Due` : "Up to date"}
          </Badge>
        </div>
        <CardTitle className="text-xs sm:text-sm font-semibold text-[var(--color-text-primary)] mt-0.5">
          Essential Review
        </CardTitle>
        <p className="text-[11px] sm:text-xs text-[var(--color-text-secondary)] mt-0.5">
          Revisit what you&apos;ve learned to strengthen recall.
        </p>
      </CardHeader>

      <CardContent className="p-3.5 sm:p-5 pt-0 sm:pt-0 space-y-2.5 relative z-10">
        {isLoading ? (
          <div className="space-y-2 py-1">
            <div className="h-7 w-16 bg-[var(--color-surface-raised)] rounded animate-pulse" />
            <div className="h-3 w-40 bg-[var(--color-surface-raised)] rounded animate-pulse" />
          </div>
        ) : (
          <>
            <div className="flex items-baseline gap-2">
              <span
                className={`text-2xl sm:text-3xl md:text-4xl font-extrabold font-mono tracking-tight ${
                  dueCount > 0 ? "text-purple-400" : "text-emerald-400"
                }`}
              >
                {dueCount}
              </span>
              <span className="text-[11px] sm:text-xs uppercase font-mono tracking-wider text-[var(--color-text-secondary)]">
                {dueCount === 1 ? "card due today" : "cards due today"}
              </span>
            </div>

            {dueCount > 0 ? (
              <p className="text-[10px] sm:text-[11px] text-[var(--color-text-secondary)] leading-tight">
                Interval decay indicates active review is needed to sustain long-term memory.
              </p>
            ) : (
              <p className="text-[10px] sm:text-[11px] text-[var(--color-text-secondary)] leading-tight flex items-center gap-1.5">
                <CheckCircle size={14} weight="bold" className="text-emerald-400 shrink-0" />
                All scheduled flashcards consolidated. Zero pending decay.
              </p>
            )}

            <div className="pt-0.5">
              <Link href="/review" className="block">
                <Button
                  size="sm"
                  variant={dueCount > 0 ? "primary" : "secondary"}
                  className="h-9 min-h-[44px] text-xs gap-1.5 font-mono w-full font-semibold rounded-lg shadow-2xs active:scale-[0.98]"
                >
                  <span>{dueCount > 0 ? "Start Review Session" : "Open Review Buffer"}</span>
                  <ArrowRight size={13} weight="bold" />
                </Button>
              </Link>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
