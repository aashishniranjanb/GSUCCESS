"use client";

import React, { useState } from "react";
import {
  Calendar,
  Gear,
  Check,
  WarningCircle,
  Plant,
  Info
} from "@phosphor-icons/react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface ExamCountdownCardProps {
  targetDate: string | null;
  targetLabel?: string | null;
  onUpdateTargetDate: (newDate: string | null, label?: string | null) => void;
}

export function ExamCountdownCard({
  targetDate,
  targetLabel,
  onUpdateTargetDate,
}: ExamCountdownCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [inputDate, setInputDate] = useState(targetDate || "2027-02-02");
  const [inputLabel, setInputLabel] = useState(targetLabel || "GPAT 2027 Target");
  const [validationError, setValidationError] = useState<string | null>(null);

  // Timezone-safe UTC midnight calculation
  const calculateDaysRemaining = (isoDateStr: string | null): number | null => {
    if (!isoDateStr) return null;
    try {
      const parts = isoDateStr.split("-");
      if (parts.length !== 3) return null;
      const targetYear = parseInt(parts[0], 10);
      const targetMonth = parseInt(parts[1], 10) - 1;
      const targetDay = parseInt(parts[2], 10);

      const targetUtc = Date.UTC(targetYear, targetMonth, targetDay);
      const now = new Date();
      const todayUtc = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());

      const diffMs = targetUtc - todayUtc;
      return Math.ceil(diffMs / (1000 * 60 * 60 * 24));
    } catch {
      return null;
    }
  };

  const daysRemaining = calculateDaysRemaining(targetDate);

  const handleSave = () => {
    setValidationError(null);
    if (!inputDate) {
      onUpdateTargetDate(null, null);
      setIsEditing(false);
      return;
    }

    const calculated = calculateDaysRemaining(inputDate);
    if (calculated === null || isNaN(calculated)) {
      setValidationError("Please enter a valid date in YYYY-MM-DD format.");
      return;
    }

    if (calculated < 0) {
      setValidationError("Target date is in the past. Select a future date.");
      return;
    }

    onUpdateTargetDate(inputDate, inputLabel.trim() || "GPAT 2027 Target");
    setIsEditing(false);
  };

  return (
    <Card className="interactive-card border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] relative overflow-hidden flex flex-col justify-between shadow-xs">
      {/* Subtle organic watermark */}
      <div
        className="absolute -right-3 -bottom-3 text-[var(--color-accent)] opacity-[0.04] pointer-events-none select-none"
        aria-hidden="true"
      >
        <Plant size={110} weight="fill" />
      </div>

      <CardHeader className="p-3.5 sm:p-5 pb-1.5 sm:pb-2 relative z-10">
        <div className="flex items-center justify-between">
          <span className="text-[10px] sm:text-[11px] font-mono tracking-wider uppercase text-[var(--color-accent)] flex items-center gap-1.5 font-semibold">
            <Calendar size={14} weight="bold" />
            Exam Horizon
          </span>
          <button
            type="button"
            onClick={() => {
              setInputDate(targetDate || "2027-02-02");
              setInputLabel(targetLabel || "GPAT 2027 Target");
              setValidationError(null);
              setIsEditing(!isEditing);
            }}
            className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] transition-colors p-1.5 rounded hover:bg-[var(--color-surface-raised)] min-h-[36px] min-w-[36px] flex items-center justify-center"
            title="Configure target date"
            aria-label="Configure target exam date"
          >
            <Gear size={15} weight="bold" />
          </button>
        </div>
        <CardTitle className="text-xs sm:text-sm font-semibold text-[var(--color-text-primary)] truncate mt-0.5">
          {targetLabel || "GPAT 2027 Target"}
        </CardTitle>
      </CardHeader>

      <CardContent className="p-3.5 sm:p-5 pt-0 sm:pt-0 space-y-2.5 relative z-10">
        {isEditing ? (
          <div className="space-y-2 pt-1 animate-enter">
            <div>
              <label className="text-[10px] uppercase font-mono text-[var(--color-text-tertiary)] block mb-1">
                Target Date (YYYY-MM-DD)
              </label>
              <input
                type="date"
                value={inputDate}
                onChange={(e) => setInputDate(e.target.value)}
                className="w-full text-xs font-mono px-2.5 py-1.5 rounded bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-[var(--color-text-primary)] focus:border-[var(--color-accent)] focus:outline-none"
              />
            </div>
            <div>
              <label className="text-[10px] uppercase font-mono text-[var(--color-text-tertiary)] block mb-1">
                Milestone Description
              </label>
              <input
                type="text"
                placeholder="e.g. 2 Feb 2027 Target"
                value={inputLabel}
                onChange={(e) => setInputLabel(e.target.value)}
                className="w-full text-xs px-2.5 py-1.5 rounded bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-[var(--color-text-primary)] focus:border-[var(--color-accent)] focus:outline-none"
              />
            </div>

            {validationError && (
              <p className="text-[11px] text-[var(--color-status-error)] flex items-center gap-1 font-mono">
                <WarningCircle size={13} weight="bold" /> {validationError}
              </p>
            )}

            <div className="flex items-center gap-2 pt-1">
              <Button size="sm" onClick={handleSave} className="h-7 text-xs px-2.5 gap-1">
                <Check size={13} weight="bold" /> Save
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  setIsEditing(false);
                  setValidationError(null);
                }}
                className="h-7 text-xs px-2"
              >
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl sm:text-3xl md:text-4xl font-extrabold font-mono tracking-tight text-[var(--color-text-primary)]">
                {daysRemaining !== null ? daysRemaining : "—"}
              </span>
              <span className="text-[11px] sm:text-xs uppercase font-mono tracking-wider text-[var(--color-text-secondary)]">
                days remaining
              </span>
            </div>

            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs font-mono text-[var(--color-text-secondary)]">
                <span className="text-[10px] sm:text-[11px]">
                  Target: {targetDate || "2027-02-02"}
                </span>
                <Badge variant="default" className="text-[9px] sm:text-[10px] py-0 px-1.5">
                  Learner Target
                </Badge>
              </div>

              <p className="text-[10px] sm:text-[11px] text-[var(--color-text-tertiary)] leading-tight flex items-start gap-1">
                <Info size={12} className="shrink-0 mt-0.5" />
                <span>Configurable milestone. NBEMS has not gazetted official 2027 dates.</span>
              </p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
