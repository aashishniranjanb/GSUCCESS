"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight } from "@phosphor-icons/react";
import { getSubjectTheme } from "@/lib/colors";
import { SyllabusExamGroup } from "@/lib/api/types";

interface SyllabusSubjectExplorerPreviewProps {
  examGroups: SyllabusExamGroup[];
}

export function SyllabusSubjectExplorerPreview({
  examGroups,
}: SyllabusSubjectExplorerPreviewProps) {
  // Canonical 5 subjects with genuine topic counts
  const SUBJECT_ITEMS = [
    {
      id: "pharmacology",
      name: "Pharmacology",
      subtext: "Receptors, mechanisms & organ systems",
      fallbackTopics: 39,
    },
    {
      id: "pharmaceutics",
      name: "Pharmaceutics",
      subtext: "Formulations, biopharmaceutics & QA",
      fallbackTopics: 65,
    },
    {
      id: "pharmaceutical_chemistry",
      name: "Pharmaceutical Chemistry",
      subtext: "Medicinal chemistry, SAR & analysis",
      fallbackTopics: 58,
    },
    {
      id: "pharmacognosy",
      name: "Pharmacognosy",
      subtext: "Natural products, phytochemistry & crude drugs",
      fallbackTopics: 27,
    },
    {
      id: "other_subjects",
      name: "Biotechnology & Allied",
      subtext: "Molecular biology, jurisprudence & microbiology",
      fallbackTopics: 32,
    },
  ];

  return (
    <section className="space-y-3" aria-labelledby="syllabus-preview-heading">
      <div className="flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-1 pb-1">
        <div>
          <h2
            id="syllabus-preview-heading"
            className="text-base sm:text-lg font-bold tracking-tight text-[var(--color-text-primary)]"
          >
            Explore by Subject
          </h2>
          <p className="text-xs text-[var(--color-text-secondary)]">
            Navigate the complete GPAT syllabus by examination discipline.
          </p>
        </div>
        <Link
          href="/study"
          className="text-xs text-[var(--color-accent)] hover:underline flex items-center gap-1 font-mono shrink-0"
        >
          <span>View Syllabus Explorer</span>
          <ArrowRight size={13} weight="bold" />
        </Link>
      </div>

      {/* Horizontally scrollable on mobile (Swiggy/Duolingo style) and grid on desktop */}
      <div className="flex sm:grid sm:grid-cols-2 lg:grid-cols-5 gap-3 overflow-x-auto pb-2 sm:pb-0 pt-0.5 -mx-3 px-3 sm:mx-0 sm:px-0 snap-x snap-mandatory scroll-smooth focus:outline-none">
        {SUBJECT_ITEMS.map((item) => {
          const theme = getSubjectTheme(item.id);
          const Icon = theme.icon;

          // Find live counts from real backend tree if loaded
          const realGroup = examGroups.find((g) => g.exam_subject_id === item.id);
          const topicCount = realGroup ? realGroup.total_topics : item.fallbackTopics;

          return (
            <Link
              key={item.id}
              href={`/study?exam_subject=${encodeURIComponent(item.id)}`}
              className="block group shrink-0 w-[240px] sm:w-auto snap-start touch-manipulation"
            >
              <div className="interactive-card p-3.5 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] hover:border-emerald-500/50 h-full flex flex-col justify-between shadow-xs">
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div
                      className="h-8 w-8 rounded-lg flex items-center justify-center shrink-0"
                      style={{
                        backgroundColor: theme.badgeBg,
                        color: theme.accentText,
                      }}
                    >
                      <Icon size={18} weight="bold" />
                    </div>
                    <ArrowRight
                      size={14}
                      className="text-[var(--color-text-tertiary)] group-hover:text-emerald-400 group-hover:translate-x-0.5 transition-all mt-1"
                    />
                  </div>

                  <h3 className="font-bold text-xs sm:text-sm text-[var(--color-text-primary)] group-hover:text-emerald-400 transition-colors">
                    {item.name}
                  </h3>
                  <p className="text-[11px] text-[var(--color-text-secondary)] mt-1 leading-snug line-clamp-2">
                    {item.subtext}
                  </p>
                </div>

                <div className="pt-2.5 mt-2.5 border-t border-[var(--color-border-subtle)] flex items-center justify-between text-[10px] font-mono text-[var(--color-text-tertiary)]">
                  <span className="font-semibold text-[var(--color-text-secondary)]">{topicCount} topics</span>
                  <span className="text-[var(--color-text-tertiary)] group-hover:text-emerald-400 transition-colors font-sans">
                    Browse &rarr;
                  </span>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
