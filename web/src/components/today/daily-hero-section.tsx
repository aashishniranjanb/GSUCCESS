"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import { Play, ArrowRight, CheckCircle } from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";

interface DailyHeroSectionProps {
  headline?: string;
  supportingText?: string;
  estimatedMinutes?: number;
  isCompleted?: boolean;
  isMissionInProgress?: boolean;
  answeredCount?: number;
  totalQuestions?: number;
  onStartMission: () => void;
  learnerName?: string | null;
}

export function DailyHeroSection({
  headline,
  supportingText,
  estimatedMinutes = 12,
  isCompleted = false,
  isMissionInProgress = false,
  answeredCount = 0,
  totalQuestions = 8,
  onStartMission,
  learnerName,
}: DailyHeroSectionProps) {
  // Client-safe time-aware greeting
  const [greeting, setGreeting] = useState<string>("Good day");
  const [hasMounted, setHasMounted] = useState<boolean>(false);
  const [imageError, setImageError] = useState<boolean>(false);

  // Compute greeting with resolved first name
  const resolvedFirstName = learnerName ? learnerName.trim().split(" ")[0] : null;

  useEffect(() => {
    setHasMounted(true);

    const calculateGreeting = (): string => {
      const hour = new Date().getHours();
      let timeOfDay = "Good morning";
      if (hour >= 12 && hour < 17) {
        timeOfDay = "Good afternoon";
      } else if (hour >= 17 && hour < 22) {
        timeOfDay = "Good evening";
      } else if (hour >= 22 || hour < 5) {
        timeOfDay = "Welcome back";
      }

      if (resolvedFirstName) {
        return `${timeOfDay}, ${resolvedFirstName}`;
      }
      return `${timeOfDay}`;
    };

    setGreeting(calculateGreeting());

    // Update greeting if window regains focus or visibility
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        setGreeting(calculateGreeting());
      }
    };

    window.addEventListener("focus", handleVisibilityChange);
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      window.removeEventListener("focus", handleVisibilityChange);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [resolvedFirstName]);

  return (
    <section
      aria-label="Personalized Study Hero"
      className="p-4 sm:p-6 md:p-8 rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] shadow-sm relative overflow-hidden"
    >
      {/* Dark navy and emerald background ambient glow */}
      <div
        className="absolute -right-20 -top-20 w-80 sm:w-96 h-80 sm:h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"
        aria-hidden="true"
      />
      <div
        className="absolute -left-20 -bottom-20 w-72 sm:w-80 h-72 sm:h-80 bg-blue-500/5 rounded-full blur-3xl pointer-events-none"
        aria-hidden="true"
      />

      <div className="grid grid-cols-1 md:grid-cols-12 gap-4 sm:gap-6 md:gap-8 items-center relative z-10">
        {/* Left column: Text & CTA — positioned first on mobile for immediate visibility */}
        <div className="md:col-span-7 flex flex-col justify-center space-y-2.5 sm:space-y-4">
          {/* Time-aware greeting badge: "Good morning, {firstName}" */}
          {hasMounted && greeting ? (
            <div className="flex items-center gap-2">
              <span className="text-[11px] sm:text-xs md:text-sm font-semibold tracking-wide text-emerald-400 font-mono px-2 py-0.5 sm:px-2.5 sm:py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20">
                {greeting}
              </span>
            </div>
          ) : (
            <div className="h-5 sm:h-6 w-32 sm:w-36 rounded-md bg-emerald-500/5 animate-pulse" />
          )}

          {/* Headline: "Today, let's make progress." */}
          <div>
            <h1 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-extrabold tracking-tight text-[var(--color-text-primary)] leading-tight">
              Today, let&apos;s make{" "}
              <span className="text-emerald-400 underline decoration-emerald-500/30 underline-offset-4">
                progress
              </span>
              .
            </h1>
          </div>

          {/* Supporting text: “One focused session at a time.” */}
          <p className="text-xs sm:text-sm md:text-base text-[var(--color-text-secondary)] leading-relaxed max-w-md font-medium">
            {supportingText || "One focused session at a time."}
          </p>

          {/* Session Duration & Task Preview Chips (Phase 3 requirements) */}
          <div className="flex flex-wrap items-center gap-2 pt-0.5 font-mono text-[11px] text-[var(--color-text-secondary)]">
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)]">
              ⏱️ ~{estimatedMinutes || 12} mins
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)]">
              📋 {totalQuestions || 8} verified practice questions
            </span>
            {headline && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-sans truncate max-w-[200px]">
                🎯 {headline}
              </span>
            )}
          </div>

          {/* Primary CTA: “Start Daily Mission” */}
          <div className="pt-1 flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 sm:gap-3">
            <Button
              size="md"
              variant="primary"
              onClick={onStartMission}
              className="interactive-cta h-11 sm:h-12 min-h-[48px] px-5 sm:px-6 text-xs sm:text-sm font-semibold gap-2 shadow-sm rounded-xl cursor-pointer hover:shadow-md focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:ring-offset-2"
              aria-label={
                isCompleted
                  ? "Retake Daily Mission"
                  : isMissionInProgress
                  ? `Resume Daily Mission (${answeredCount} of ${totalQuestions} questions completed)`
                  : "Start Daily Mission"
              }
            >
              {isCompleted ? (
                <>
                  <CheckCircle size={18} weight="bold" />
                  <span>Retake Daily Mission</span>
                </>
              ) : isMissionInProgress ? (
                <>
                  <Play size={18} weight="bold" />
                  <span>Resume Daily Mission ({answeredCount}/{totalQuestions})</span>
                  <ArrowRight size={16} weight="bold" />
                </>
              ) : (
                <>
                  <Play size={18} weight="bold" />
                  <span>Start Daily Mission</span>
                  <ArrowRight size={16} weight="bold" />
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Right column: Generated Pharmacy Study Lab Hero Illustration — compact height with intentional face crop */}
        <div className="md:col-span-5 flex items-center justify-center">
          <div className="w-full max-w-[340px] md:max-w-[420px] relative h-36 sm:h-44 md:h-52 rounded-xl overflow-hidden border border-[var(--color-border-subtle)]/70 bg-[var(--color-surface-raised)]/40 shadow-inner group">
            {!imageError ? (
              <Image
                src="/images/pharmacy-hero-illustration.png"
                alt=""
                aria-hidden="true"
                fill
                priority
                sizes="(max-width: 640px) 340px, (max-width: 768px) 360px, (max-width: 1024px) 320px, 420px"
                className="object-cover object-top sm:object-center transition-transform duration-500 group-hover:scale-[1.02]"
                onError={() => setImageError(true)}
              />
            ) : (
              <div
                className="w-full h-full flex flex-col items-center justify-center p-4 text-center bg-emerald-950/20 text-emerald-400 text-xs font-mono space-y-1.5"
                aria-hidden="true"
              >
                <span className="text-2xl">🌿</span>
                <span className="font-semibold text-xs sm:text-sm">GPAT Pharmacy Learning Lab</span>
                <span className="text-[10px] text-[var(--color-text-secondary)]">Focused study &amp; active recall</span>
              </div>
            )}
            {/* Subtle soft gradient scrim */}
            <div
              className="absolute inset-0 bg-gradient-to-t from-[var(--color-surface-base)]/50 via-transparent to-transparent pointer-events-none"
              aria-hidden="true"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
