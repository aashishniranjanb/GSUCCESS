"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Clock, Sparkle, Eye } from "@phosphor-icons/react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getSubjectTheme, ExamSubjectId } from "@/lib/colors";
import { SynapseIllustration, DissolutionIllustration } from "./botanical-illustrations";

export interface StudyRecommendationOption {
  optionKey: "A" | "B";
  subjectId: ExamSubjectId;
  subjectName: string;
  topicTitle: string;
  unitTitle?: string;
  estimatedMinutes: number;
  whyRecommended: string;
  targetQuestionCount: number;
  tags?: string[];
  dueCardsCount?: number;
  misconceptionsCount?: number;
  topicId?: string;
  mode?: "balanced" | "repair";
}

interface TwoStudyChoicesSectionProps {
  optionA: StudyRecommendationOption;
  optionB: StudyRecommendationOption;
  isStarting: boolean;
  onSelectOption: (optionKey: "A" | "B") => void;
}

export function TwoStudyChoicesSection({
  optionA,
  optionB,
  isStarting,
  onSelectOption,
}: TwoStudyChoicesSectionProps) {
  const themeA = getSubjectTheme(optionA.subjectId);
  const themeB = getSubjectTheme(optionB.subjectId);

  const IconA = themeA.icon;
  const IconB = themeB.icon;

  return (
    <section className="space-y-4" aria-labelledby="choose-focus-heading">
      <div className="flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-1 pb-1">
        <div className="flex items-center gap-2">
          <div className="h-6 w-6 rounded-md bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
            <Sparkle size={15} weight="fill" />
          </div>
          <div>
            <h2 id="choose-focus-heading" className="text-base sm:text-lg font-bold tracking-tight text-[var(--color-text-primary)]">
              Personalized Focus
            </h2>
            <p className="text-xs text-[var(--color-text-secondary)]">
              Two balanced study options selected by syllabus weightage and your learning history.
            </p>
          </div>
        </div>
        <span className="text-[11px] font-mono text-[var(--color-text-tertiary)] flex items-center gap-1.5">
          <Clock size={13} /> ~12 minutes per session
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* OPTION A CARD - Pattern C: Discovery Card */}
        <Card
          className="interactive-card border border-[var(--color-border-subtle)] rounded-xl bg-[var(--color-surface-base)] relative overflow-hidden flex flex-col justify-between hover:border-emerald-500/40 shadow-2xs group transition-all"
        >
          {/* Subtle accent edge */}
          <div className="absolute top-0 left-0 right-0 h-1 bg-emerald-500/80" aria-hidden="true" />

          {/* Subtle Synapse illustration watermark */}
          <div
            className="absolute right-0 top-1/2 -translate-y-1/2 w-32 h-32 opacity-10 group-hover:opacity-20 transition-opacity pointer-events-none"
            aria-hidden="true"
          >
            <SynapseIllustration className="w-full h-full" />
          </div>

          <CardHeader className="space-y-2 pb-2 pt-4 relative z-10">
            <div className="flex items-center justify-between">
              <span className="inline-flex items-center gap-1.5 text-[11px] font-mono font-bold tracking-wider uppercase text-emerald-400">
                <IconA size={14} weight="bold" />
                <span>Pharmacology</span>
              </span>

              <div className="flex items-center gap-1 text-[11px] font-mono text-[var(--color-text-secondary)]">
                <Clock size={12} />
                <span>~{optionA.estimatedMinutes} min</span>
              </div>
            </div>

            <CardTitle className="text-base sm:text-lg font-bold text-[var(--color-text-primary)] leading-snug">
              {optionA.topicTitle}
            </CardTitle>

            <CardDescription className="text-xs text-[var(--color-text-secondary)] leading-relaxed line-clamp-2">
              {optionA.whyRecommended}
            </CardDescription>

            {/* Single concise context chip */}
            <div className="flex items-center gap-1.5 pt-0.5 text-[10px] font-mono text-[var(--color-text-tertiary)]">
              <span className="px-1.5 py-0.5 rounded bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)]">
                Active Recall
              </span>
              <span>•</span>
              <span>{optionA.targetQuestionCount} questions</span>
            </div>
          </CardHeader>

          <CardContent className="pt-2 relative z-10">
            <div className="flex items-center gap-2 pt-2 border-t border-[var(--color-border-subtle)]">
              <Button
                onClick={() => onSelectOption("A")}
                disabled={isStarting}
                size="sm"
                variant="primary"
                className="flex-1 gap-1.5 text-xs font-semibold h-8 min-h-[40px] rounded-lg shadow-2xs"
              >
                <span>{isStarting ? "Starting..." : "Start Mission"}</span>
                <ArrowRight size={13} weight="bold" />
              </Button>
              {optionA.topicId && (
                <Link href={`/study?topic=${encodeURIComponent(optionA.topicId)}`}>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-xs h-8 min-h-[40px] px-2.5 text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] gap-1 font-mono"
                  >
                    <Eye size={13} />
                    <span>Details</span>
                  </Button>
                </Link>
              )}
            </div>
          </CardContent>
        </Card>

        {/* OPTION B CARD - Pattern C: Discovery Card */}
        <Card
          className="interactive-card border border-[var(--color-border-subtle)] rounded-xl bg-[var(--color-surface-base)] relative overflow-hidden flex flex-col justify-between hover:border-blue-500/40 shadow-2xs group transition-all"
        >
          {/* Subtle accent edge */}
          <div className="absolute top-0 left-0 right-0 h-1 bg-blue-500/80" aria-hidden="true" />

          {/* Subtle Dissolution illustration watermark */}
          <div
            className="absolute right-0 top-1/2 -translate-y-1/2 w-32 h-32 opacity-10 group-hover:opacity-20 transition-opacity pointer-events-none"
            aria-hidden="true"
          >
            <DissolutionIllustration className="w-full h-full" />
          </div>

          <CardHeader className="space-y-2 pb-2 pt-4 relative z-10">
            <div className="flex items-center justify-between">
              <span className="inline-flex items-center gap-1.5 text-[11px] font-mono font-bold tracking-wider uppercase text-blue-400">
                <IconB size={14} weight="bold" />
                <span>Pharmaceutics</span>
              </span>

              <div className="flex items-center gap-1 text-[11px] font-mono text-[var(--color-text-secondary)]">
                <Clock size={12} />
                <span>~{optionB.estimatedMinutes} min</span>
              </div>
            </div>

            <CardTitle className="text-base sm:text-lg font-bold text-[var(--color-text-primary)] leading-snug">
              {optionB.topicTitle}
            </CardTitle>

            <CardDescription className="text-xs text-[var(--color-text-secondary)] leading-relaxed line-clamp-2">
              {optionB.whyRecommended}
            </CardDescription>

            {/* Single concise context chip */}
            <div className="flex items-center gap-1.5 pt-0.5 text-[10px] font-mono text-[var(--color-text-tertiary)]">
              <span className="px-1.5 py-0.5 rounded bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)]">
                Formulation Core
              </span>
              <span>•</span>
              <span>{optionB.targetQuestionCount} questions</span>
            </div>
          </CardHeader>

          <CardContent className="pt-2 relative z-10">
            <div className="flex items-center gap-2 pt-2 border-t border-[var(--color-border-subtle)]">
              <Button
                onClick={() => onSelectOption("B")}
                disabled={isStarting}
                size="sm"
                variant="secondary"
                className="flex-1 gap-1.5 text-xs font-semibold h-8 min-h-[40px] rounded-lg shadow-2xs"
              >
                <span>{isStarting ? "Starting..." : "Start Mission"}</span>
                <ArrowRight size={13} weight="bold" />
              </Button>
              {optionB.topicId && (
                <Link href={`/study?topic=${encodeURIComponent(optionB.topicId)}`}>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-xs h-8 min-h-[40px] px-2.5 text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] gap-1 font-mono"
                  >
                    <Eye size={13} />
                    <span>Details</span>
                  </Button>
                </Link>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
