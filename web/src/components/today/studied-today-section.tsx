"use client";

import React from "react";
import {
  ClockCounterClockwise,
  CheckCircle,
  XCircle,
  HourglassMedium,
  ShieldCheck,
} from "@phosphor-icons/react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export interface StudiedActivityItem {
  id: string;
  type: "mission_answered" | "review_card" | "mock_question";
  title: string;
  isCorrect?: boolean;
  timeSpentSec?: number;
  timestamp: string;
}

interface StudiedTodaySectionProps {
  activities: StudiedActivityItem[];
  isLoading: boolean;
}

export function StudiedTodaySection({ activities, isLoading }: StudiedTodaySectionProps) {
  const correctCount = activities.filter((a) => a.isCorrect === true).length;
  const evaluatedCount = activities.filter((a) => a.isCorrect !== undefined).length;
  const accuracy = evaluatedCount > 0 ? Math.round((correctCount / evaluatedCount) * 100) : null;

  // Pattern B/C requirement: max 3 recent events on the home page without modifying/deleting historical records
  const recentActivities = activities.slice(0, 3);
  const remainingCount = Math.max(0, activities.length - 3);

  return (
    <Card className="interactive-card border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] flex flex-col justify-between shadow-xs">
      <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ClockCounterClockwise size={16} weight="bold" className="text-[var(--color-status-success)]" />
            <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)]">
              Studied Today
            </CardTitle>
          </div>
          <Badge variant="default" className="text-[10px] font-mono py-0 px-1.5 flex items-center gap-1">
            <ShieldCheck size={12} weight="bold" /> Persisted History
          </Badge>
        </div>
        <p className="text-xs text-[var(--color-text-secondary)]">
          Real learning events recorded in SQLite today. Showing {activities.length > 0 ? `the latest ${recentActivities.length} of ${activities.length}` : "0"} verified completions.
        </p>
      </CardHeader>

      <CardContent className="space-y-3 pt-3">
        {isLoading ? (
          <div className="space-y-2 py-4">
            <div className="h-4 w-3/4 bg-[var(--color-surface-raised)] rounded animate-pulse" />
            <div className="h-4 w-1/2 bg-[var(--color-surface-raised)] rounded animate-pulse" />
          </div>
        ) : activities.length === 0 ? (
          <div className="text-center py-7 text-xs text-[var(--color-text-tertiary)] space-y-1.5">
            <HourglassMedium size={24} className="mx-auto text-[var(--color-text-tertiary)]" />
            <p className="text-[var(--color-text-secondary)] font-medium">No learning activities logged today yet.</p>
            <p className="text-[11px]">Start today&apos;s Daily Mission or Essential Review above to begin your active study record.</p>
          </div>
        ) : (
          <div className="space-y-3">
            <ul className="space-y-2" aria-label="Recent learning activities today">
              {recentActivities.map((act) => {
                const formattedTime = new Date(act.timestamp).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                });

                return (
                  <li
                    key={act.id}
                    className="flex items-center justify-between p-2.5 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/40 text-xs"
                  >
                    <div className="flex items-center gap-2 min-w-0 pr-2">
                      {act.isCorrect === true && (
                        <CheckCircle size={16} weight="fill" className="text-[var(--color-status-success)] shrink-0" />
                      )}
                      {act.isCorrect === false && (
                        <XCircle size={16} weight="fill" className="text-[var(--color-status-error)] shrink-0" />
                      )}
                      {act.isCorrect === undefined && (
                        <CheckCircle size={16} weight="bold" className="text-[var(--color-accent)] shrink-0" />
                      )}

                      <div className="min-w-0">
                        <span className="text-[var(--color-text-primary)] font-medium block truncate">
                          {act.title}
                        </span>
                        <div className="flex items-center gap-2 text-[10px] font-mono text-[var(--color-text-tertiary)]">
                          <span>{formattedTime}</span>
                          {act.timeSpentSec !== undefined && <span>{act.timeSpentSec}s response</span>}
                        </div>
                      </div>
                    </div>

                    <Badge variant="default" className="text-[10px] font-mono py-0 shrink-0">
                      Logged
                    </Badge>
                  </li>
                );
              })}
            </ul>

            {/* Action footer: summary metrics + link to full history on /progress */}
            <div className="pt-2 border-t border-[var(--color-border-subtle)] flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[11px] font-mono text-[var(--color-text-secondary)]">
              <div className="flex items-center gap-2">
                <span>{activities.length} total today</span>
                {accuracy !== null && (
                  <>
                    <span>•</span>
                    <span className={accuracy >= 70 ? "text-[var(--color-status-success)]" : "text-[var(--color-accent)]"}>
                      Accuracy: {accuracy}%
                    </span>
                  </>
                )}
                {remainingCount > 0 && (
                  <span className="text-[var(--color-text-tertiary)]">
                    (+{remainingCount} more)
                  </span>
                )}
              </div>

              <a
                href="/progress"
                className="text-xs text-[var(--color-accent)] hover:underline inline-flex items-center gap-1 font-sans font-medium"
              >
                <span>View all activity</span>
                <span aria-hidden="true">&rarr;</span>
              </a>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
