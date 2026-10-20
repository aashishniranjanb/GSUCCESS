"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  BookOpen,
  CheckCircle,
  Clock,
  Circle,
  CaretDown,
  CaretRight,
  ArrowRight,
  ArrowLeft,
  Plant,
  Flask,
  Atom,
  Drop,
  Dna,
} from "@phosphor-icons/react/dist/ssr";

interface SyllabusJourneyScreenProps {
  onBackToOverview: () => void;
}

interface TopicItem {
  id: string;
  name: string;
  status: "completed" | "in_progress" | "not_started";
  attempts: number;
  accuracy: number;
}

interface UnitItem {
  id: string;
  name: string;
  completedTopics: number;
  totalTopics: number;
  topics: TopicItem[];
}

interface SubjectJourney {
  id: string;
  name: string;
  color: string;
  icon: React.ElementType;
  completedTopics: number;
  totalTopics: number;
  units: UnitItem[];
}

export function SyllabusJourneyScreen({
  onBackToOverview,
}: SyllabusJourneyScreenProps) {
  const [filterView, setFilterView] = useState<"all" | "in_progress" | "completed">("all");
  const [expandedSubject, setExpandedSubject] = useState<string | null>("pharmacology");
  const [expandedUnit, setExpandedUnit] = useState<string | null>("pharm_ans");

  // Real canonical subject hierarchy
  const subjects: SubjectJourney[] = [
    {
      id: "pharmacology",
      name: "Pharmacology & Allied Subjects",
      color: "#10B981", // emerald
      icon: Plant,
      completedTopics: 34,
      totalTopics: 50,
      units: [
        {
          id: "pharm_ans",
          name: "Unit 1: Autonomic Nervous System",
          completedTopics: 8,
          totalTopics: 12,
          topics: [
            { id: "col_agonists", name: "Cholinergic Agonists & Esters", status: "completed", attempts: 6, accuracy: 83 },
            { id: "anti_musc", name: "Antimuscarinic Agents & Atropine", status: "completed", attempts: 4, accuracy: 100 },
            { id: "adren_receptors", name: "Adrenergic Receptor Subtypes", status: "in_progress", attempts: 3, accuracy: 67 },
            { id: "ganglion_block", name: "Ganglionic Blockers & Neuromuscular Junction", status: "not_started", attempts: 0, accuracy: 0 },
          ],
        },
        {
          id: "pharm_cvs",
          name: "Unit 2: Cardiovascular Pharmacology",
          completedTopics: 6,
          totalTopics: 10,
          topics: [
            { id: "anti_arrhythmics", name: "Vaughan Williams Antiarrhythmics", status: "completed", attempts: 5, accuracy: 80 },
            { id: "ace_inhibitors", name: "RAAS Inhibitors & ARBs", status: "in_progress", attempts: 2, accuracy: 50 },
            { id: "lipid_lowering", name: "Statins & PCSK9 Inhibitors", status: "not_started", attempts: 0, accuracy: 0 },
          ],
        },
      ],
    },
    {
      id: "pharmaceutics",
      name: "Pharmaceutics & Biopharmaceutics",
      color: "#3B82F6", // blue
      icon: Flask,
      completedTopics: 28,
      totalTopics: 50,
      units: [
        {
          id: "cets_formulation",
          name: "Unit 1: Tablets & Solid Dosage Forms",
          completedTopics: 7,
          totalTopics: 12,
          topics: [
            { id: "tab_defects", name: "Tablet Compression & Coating Defects", status: "completed", attempts: 4, accuracy: 100 },
            { id: "dissolution", name: "USP Dissolution Apparatus & Kinetics", status: "in_progress", attempts: 3, accuracy: 66 },
          ],
        },
      ],
    },
    {
      id: "pharm_chem",
      name: "Pharmaceutical Chemistry",
      color: "#F59E0B", // amber
      icon: Atom,
      completedTopics: 21,
      totalTopics: 50,
      units: [
        {
          id: "chem_sar",
          name: "Unit 1: Structure-Activity Relationships",
          completedTopics: 5,
          totalTopics: 15,
          topics: [
            { id: "sar_beta_lactam", name: "Beta-Lactam Ring Stability & SAR", status: "in_progress", attempts: 3, accuracy: 67 },
          ],
        },
      ],
    },
    {
      id: "pharmacognosy",
      name: "Pharmacognosy & Phytochemistry",
      color: "#8B5CF6", // purple
      icon: Drop,
      completedTopics: 19,
      totalTopics: 50,
      units: [
        {
          id: "phytochem_alkaloids",
          name: "Unit 1: Plant Alkaloids & Extraction",
          completedTopics: 4,
          totalTopics: 10,
          topics: [
            { id: "alkaloid_tests", name: "Dragendorff & Mayer Reagent Chemistry", status: "completed", attempts: 2, accuracy: 100 },
          ],
        },
      ],
    },
    {
      id: "biotech",
      name: "Biotechnology & Allied",
      color: "#06B6D4", // cyan
      icon: Dna,
      completedTopics: 24,
      totalTopics: 50,
      units: [
        {
          id: "r_dna",
          name: "Unit 1: Recombinant DNA Technology",
          completedTopics: 6,
          totalTopics: 10,
          topics: [
            { id: "pcr_mechanisms", name: "Taq Polymerase & PCR Cycles", status: "completed", attempts: 3, accuracy: 100 },
          ],
        },
      ],
    },
  ];

  const totalAllTopics = 166;
  const completedAll = 42;
  const inProgressAll = 68;
  const notStartedAll = 56;
  const overallPercent = Math.round((completedAll / totalAllTopics) * 100);

  return (
    <div className="space-y-5 animate-enter">
      {/* Header with Back Button */}
      <div className="flex items-center justify-between pb-2 border-b border-[var(--color-border-subtle)]">
        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={onBackToOverview}
            className="p-1.5 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:border-[var(--color-border-focus)] transition-colors"
            aria-label="Back to overview"
          >
            <ArrowLeft size={16} weight="bold" />
          </button>
          <div>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] flex items-center gap-2">
              <BookOpen size={20} weight="fill" className="text-emerald-400" />
              Syllabus journey
            </h2>
            <p className="text-xs text-[var(--color-text-secondary)]">
              Track your preparation across all canonical subjects
            </p>
          </div>
        </div>
      </div>

      {/* Overview Ring & Counts Card */}
      <div className="p-5 rounded-2xl border border-emerald-500/20 bg-gradient-to-br from-[#0c1c1f] via-[var(--color-surface-base)] to-[var(--color-surface-base)]">
        <div className="grid grid-cols-1 sm:grid-cols-12 gap-5 items-center">
          <div className="sm:col-span-4 flex items-center justify-center">
            <div className="relative w-28 h-28 flex items-center justify-center">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  className="stroke-[var(--color-surface-raised)]"
                  strokeWidth="8"
                  fill="transparent"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  className="stroke-cyan-400"
                  strokeWidth="8"
                  strokeDasharray={251.2}
                  strokeDashoffset={251.2 * (1 - 0.25)}
                  strokeLinecap="round"
                  fill="transparent"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span className="text-xl font-bold font-mono text-[var(--color-text-primary)]">
                  {overallPercent}%
                </span>
                <span className="text-[9px] uppercase tracking-wider text-[var(--color-text-tertiary)] font-medium">
                  covered
                </span>
              </div>
            </div>
          </div>

          <div className="sm:col-span-8 grid grid-cols-3 gap-2.5">
            <div className="p-3 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-center">
              <span className="w-2 h-2 rounded-full bg-cyan-400 inline-block mb-1" />
              <div className="text-lg font-bold font-mono text-cyan-400">{completedAll}</div>
              <div className="text-[10px] text-[var(--color-text-secondary)] font-medium">Completed</div>
            </div>

            <div className="p-3 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-center">
              <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block mb-1" />
              <div className="text-lg font-bold font-mono text-emerald-400">{inProgressAll}</div>
              <div className="text-[10px] text-[var(--color-text-secondary)] font-medium">In progress</div>
            </div>

            <div className="p-3 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-center">
              <span className="w-2 h-2 rounded-full bg-zinc-500 inline-block mb-1" />
              <div className="text-lg font-bold font-mono text-zinc-400">{notStartedAll}</div>
              <div className="text-[10px] text-[var(--color-text-secondary)] font-medium">Not started</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-1.5 p-1 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)]">
        {(["all", "in_progress", "completed"] as const).map((mode) => (
          <button
            key={mode}
            type="button"
            onClick={() => setFilterView(mode)}
            className={`flex-1 py-1.5 rounded-lg text-xs font-semibold capitalize transition-colors min-h-[36px] ${
              filterView === mode
                ? "bg-[var(--color-accent)] text-zinc-950 font-bold"
                : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
            }`}
          >
            {mode.replace("_", " ")}
          </button>
        ))}
      </div>

      {/* Expandable Subjects & Units Accordion */}
      <div className="space-y-3">
        {subjects.map((subj) => {
          const isSubjectOpen = expandedSubject === subj.id;
          const percent = Math.round((subj.completedTopics / subj.totalTopics) * 100);

          return (
            <div
              key={subj.id}
              className="rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] overflow-hidden transition-all shadow-xs"
            >
              {/* Subject Bar */}
              <button
                type="button"
                onClick={() => setExpandedSubject(isSubjectOpen ? null : subj.id)}
                className="w-full p-4 flex items-center justify-between text-left hover:bg-[var(--color-surface-raised)]/40 transition-colors"
                aria-expanded={isSubjectOpen}
              >
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                    style={{ backgroundColor: `${subj.color}15`, color: subj.color }}
                  >
                    <subj.icon size={18} weight="bold" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between text-xs sm:text-sm font-semibold text-[var(--color-text-primary)] mb-1">
                      <span className="truncate">{subj.name}</span>
                      <span className="font-mono text-xs font-bold" style={{ color: subj.color }}>
                        {percent}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-[var(--color-text-tertiary)] font-mono">
                      <span>{subj.completedTopics}/{subj.totalTopics} topics</span>
                    </div>
                  </div>
                </div>

                <div className="ml-3 text-[var(--color-text-tertiary)] shrink-0">
                  {isSubjectOpen ? <CaretDown size={16} weight="bold" /> : <CaretRight size={16} weight="bold" />}
                </div>
              </button>

              {/* Units & Topics (Nested Accordion) */}
              {isSubjectOpen && (
                <div className="p-4 pt-0 border-t border-[var(--color-border-subtle)] space-y-3 bg-[var(--color-surface-raised)]/30 animate-enter">
                  {subj.units.map((unit) => {
                    const isUnitOpen = expandedUnit === unit.id;

                    return (
                      <div
                        key={unit.id}
                        className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] overflow-hidden"
                      >
                        <button
                          type="button"
                          onClick={() => setExpandedUnit(isUnitOpen ? null : unit.id)}
                          className="w-full p-3 flex items-center justify-between text-left hover:bg-[var(--color-surface-raised)]/60 text-xs font-semibold text-[var(--color-text-primary)]"
                          aria-expanded={isUnitOpen}
                        >
                          <span>{unit.name}</span>
                          <div className="flex items-center gap-2 text-[11px] font-mono text-[var(--color-text-tertiary)]">
                            <span>{unit.completedTopics}/{unit.totalTopics} topics</span>
                            {isUnitOpen ? <CaretDown size={14} weight="bold" /> : <CaretRight size={14} weight="bold" />}
                          </div>
                        </button>

                        {isUnitOpen && (
                          <div className="p-3 pt-0 space-y-2 border-t border-[var(--color-border-subtle)]">
                            {unit.topics.map((top) => (
                              <div
                                key={top.id}
                                className="flex items-center justify-between gap-3 p-2.5 rounded-lg bg-[var(--color-surface-raised)]/50 border border-[var(--color-border-subtle)] text-xs"
                              >
                                <div className="flex items-center gap-2 min-w-0">
                                  {top.status === "completed" ? (
                                    <CheckCircle size={15} weight="fill" className="text-emerald-400 shrink-0" />
                                  ) : top.status === "in_progress" ? (
                                    <Clock size={15} weight="fill" className="text-amber-400 shrink-0" />
                                  ) : (
                                    <Circle size={15} weight="regular" className="text-zinc-500 shrink-0" />
                                  )}
                                  <span className="truncate text-[var(--color-text-primary)] font-medium">
                                    {top.name}
                                  </span>
                                </div>

                                <div className="flex items-center gap-2 shrink-0">
                                  {top.attempts > 0 && (
                                    <span className="font-mono text-[10px] text-[var(--color-text-secondary)]">
                                      {top.accuracy}% acc
                                    </span>
                                  )}
                                  <Link
                                    href={`/study?topic=${top.id}`}
                                    className="p-1 rounded text-cyan-400 hover:text-cyan-300 font-semibold"
                                  >
                                    <ArrowRight size={14} weight="bold" />
                                  </Link>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
