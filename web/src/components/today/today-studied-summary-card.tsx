"use client";

import React from "react";
import Link from "next/link";
import { CheckCircle, ChartLineUp, ArrowRight } from "@phosphor-icons/react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface TodayStudiedSummaryCardProps {
  completedCount: number;
  totalAttempts: number;
  accuracyPercent: number;
  isLoading: boolean;
}

export function TodayStudiedSummaryCard({
  completedCount,
  totalAttempts,
  accuracyPercent,
  isLoading,
}: TodayStudiedSummaryCardProps) {
  return (
    <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] flex flex-col justify-between">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-mono tracking-wider uppercase text-[var(--color-text-tertiary)] flex items-center gap-1.5">
            <CheckCircle size={14} weight="bold" className="text-[var(--color-status-success)]" />
            Studied Today
          </span>
          <Badge variant="default" className="text-[10px] py-0 px-1.5 font-mono">
            Persisted
          </Badge>
        </div>
        <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)]">
          Activity Evidence
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-3 pt-0">
        {isLoading ? (
          <div className="space-y-2 py-1">
            <div className="h-8 w-16 bg-[var(--color-surface-raised)] rounded animate-pulse" />
            <div className="h-3 w-40 bg-[var(--color-surface-raised)] rounded animate-pulse" />
          </div>
        ) : (
          <>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl sm:text-4xl font-extrabold font-mono tracking-tight text-[var(--color-text-primary)]">
                {completedCount}
              </span>
              <span className="text-xs uppercase font-mono tracking-wider text-[var(--color-text-secondary)]">
                {completedCount === 1 ? "task logged today" : "tasks logged today"}
              </span>
            </div>

            <div className="flex items-center justify-between text-[11px] font-mono text-[var(--color-text-secondary)] py-0.5">
              <span>Attempts: {totalAttempts} questions</span>
              <span className={accuracyPercent >= 70 ? "text-[var(--color-status-success)]" : "text-[var(--color-text-primary)]"}>
                Accuracy: {totalAttempts > 0 ? `${accuracyPercent}%` : "—"}
              </span>
            </div>

            <Link href="/progress" className="block pt-1">
              <Button
                size="sm"
                variant="secondary"
                className="h-8 text-xs gap-1.5 font-mono w-full"
              >
                <ChartLineUp size={13} weight="bold" />
                <span>View Learning Analytics</span>
                <ArrowRight size={13} weight="bold" />
              </Button>
            </Link>
          </>
        )}
      </CardContent>
    </Card>
  );
}
