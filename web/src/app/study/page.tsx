"use client";

import React, { useEffect, useState, useMemo, useCallback } from "react";
import Link from "next/link";
import {
  fetchSyllabusTree,
  fetchTopicDetail,
} from "@/lib/api/syllabus";
import { fetchStudentProgress } from "@/lib/api/progress";
import {
  SyllabusTreeResponse,
  SyllabusTopicSummary,
  TopicDetailResponse,
  ProgressConceptItem,
  SyllabusExamGroup,
  SyllabusCurriculumSubject,
} from "@/lib/api/types";
import { Skeleton, ErrorState } from "@/components/ui/states";
import { Button } from "@/components/ui/button";
import {
  MagnifyingGlass,
  X,
  WifiSlash,
  WarningCircle,
  Sparkle,
  ArrowLeft,
  ArrowRight,
  Folder,
  CheckCircle,
  Circle,
  FileText,
  Target,
  Question,
  Cards,
  BookmarksSimple,
  CaretRight,
  BookmarkSimple,
  Warning,
  Flame,
} from "@phosphor-icons/react";
import { getSubjectTheme, ExamSubjectId } from "@/lib/colors";
import {
  SynapseIllustration,
  DissolutionIllustration,
} from "@/components/today/botanical-illustrations";
import {
  ChemistryMolecularIllustration,
  PharmacognosyFlowerIllustration,
  BiotechnologyDnaIllustration,
} from "@/components/study/subject-illustrations";

// Filter modes
type FilterMode = "all" | "high_yield" | "needs_review";

const CANONICAL_SUBJECTS: Array<{
  id: ExamSubjectId;
  name: string;
  description: string;
  fallbackTopics: number;
}> = [
  {
    id: "pharmacology",
    name: "Pharmacology",
    description: "Receptors, mechanisms & organ systems",
    fallbackTopics: 39,
  },
  {
    id: "pharmaceutics",
    name: "Pharmaceutics",
    description: "Formulation, dosage forms & delivery systems",
    fallbackTopics: 65,
  },
  {
    id: "pharmaceutical_chemistry",
    name: "Pharmaceutical Chemistry",
    description: "Medicinal chemistry & SAR",
    fallbackTopics: 58,
  },
  {
    id: "pharmacognosy",
    name: "Pharmacognosy",
    description: "Natural products & crude drugs",
    fallbackTopics: 27,
  },
  {
    id: "other_subjects",
    name: "Biotechnology & Allied",
    description: "Molecular biology, genetics & microbiology",
    fallbackTopics: 32,
  },
];

export default function StudyPage() {
  const [treeData, setTreeData] = useState<SyllabusTreeResponse | null>(null);
  const [progressConcepts, setProgressConcepts] = useState<Record<string, ProgressConceptItem>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isOffline, setIsOffline] = useState<boolean>(false);

  // 4 Navigation Levels in the Flow:
  // 1: Syllabus Explorer (Landing) -> selectedSubjectId = null, selectedUnitId = null, selectedTopicId = null
  // 2: Subject Overview           -> selectedSubjectId != null, selectedUnitId = null, selectedTopicId = null
  // 3: Unit View (Topic List)     -> selectedSubjectId != null, selectedUnitId != null, selectedTopicId = null
  // 4: Topic Detail               -> selectedTopicId != null
  const [selectedSubjectId, setSelectedSubjectId] = useState<string | null>(null);
  const [selectedUnitId, setSelectedUnitId] = useState<string | null>(null);
  const [selectedTopicId, setSelectedTopicId] = useState<string | null>(null);

  // Search & Filter state
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [filterMode, setFilterMode] = useState<FilterMode>("all");

  // Topic detail state
  const [topicDetail, setTopicDetail] = useState<TopicDetailResponse | null>(null);
  const [topicLoading, setTopicLoading] = useState<boolean>(false);
  const [topicError, setTopicError] = useState<string | null>(null);

  // Topic Detail Tab
  const [topicTab, setTopicTab] = useState<"learn" | "practice" | "pyqs" | "notes">("learn");

  // Study Plan bookmark persistence
  const [isInPlan, setIsInPlan] = useState<boolean>(false);

  // Parse URL search params on mount & window popstate (browser back/forward support)
  const syncFromUrl = useCallback(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    const topicParam = params.get("topic");
    const unitParam = params.get("unit");
    const examParam = params.get("exam_subject");

    if (topicParam) {
      setSelectedTopicId(topicParam);
    } else {
      setSelectedTopicId(null);
    }

    if (unitParam) {
      setSelectedUnitId(unitParam);
    } else {
      setSelectedUnitId(null);
    }

    if (examParam) {
      setSelectedSubjectId(examParam);
    } else if (!topicParam) {
      setSelectedSubjectId(null);
    }
  }, []);

  useEffect(() => {
    syncFromUrl();
    window.addEventListener("popstate", syncFromUrl);
    return () => window.removeEventListener("popstate", syncFromUrl);
  }, [syncFromUrl]);

  // Sync URL when state changes
  const updateUrl = useCallback((subject: string | null, unit: string | null, topic: string | null) => {
    if (typeof window !== "undefined") {
      const url = new URL(window.location.href);
      if (topic) {
        url.searchParams.set("topic", topic);
        if (subject) url.searchParams.set("exam_subject", subject);
        if (unit) url.searchParams.set("unit", unit);
      } else if (unit) {
        url.searchParams.set("unit", unit);
        if (subject) url.searchParams.set("exam_subject", subject);
        url.searchParams.delete("topic");
      } else if (subject) {
        url.searchParams.set("exam_subject", subject);
        url.searchParams.delete("unit");
        url.searchParams.delete("topic");
      } else {
        url.searchParams.delete("topic");
        url.searchParams.delete("unit");
        url.searchParams.delete("exam_subject");
      }
      window.history.pushState({}, "", url.toString());
    }
  }, []);

  // Level transitions
  const handleSelectSubject = (subjId: string) => {
    setSelectedSubjectId(subjId);
    setSelectedUnitId(null);
    setSelectedTopicId(null);
    updateUrl(subjId, null, null);
  };

  const handleSelectUnit = (unitId: string) => {
    setSelectedUnitId(unitId);
    setSelectedTopicId(null);
    updateUrl(selectedSubjectId, unitId, null);
  };

  const handleSelectTopic = (topicId: string) => {
    setSelectedTopicId(topicId);
    updateUrl(selectedSubjectId, selectedUnitId, topicId);
  };

  // Back transitions
  const handleBackToSubjects = () => {
    setSelectedSubjectId(null);
    setSelectedUnitId(null);
    setSelectedTopicId(null);
    updateUrl(null, null, null);
  };

  const handleBackToUnits = () => {
    setSelectedUnitId(null);
    setSelectedTopicId(null);
    updateUrl(selectedSubjectId, null, null);
  };

  const handleBackToTopicList = () => {
    setSelectedTopicId(null);
    updateUrl(selectedSubjectId, selectedUnitId, null);
  };

  // Network monitoring
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

  // Fetch syllabus tree and student progress
  const loadTree = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [treeRes, progressRes] = await Promise.allSettled([
        fetchSyllabusTree(),
        fetchStudentProgress("student_01"),
      ]);

      if (treeRes.status === "fulfilled") {
        setTreeData(treeRes.value);
      } else {
        throw treeRes.reason;
      }

      if (progressRes.status === "fulfilled") {
        const conceptMap: Record<string, ProgressConceptItem> = {};
        for (const c of progressRes.value.concepts) {
          conceptMap[c.id] = c;
        }
        setProgressConcepts(conceptMap);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load syllabus taxonomy.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadTree();
  }, [loadTree]);

  // Fetch topic details when selected
  useEffect(() => {
    if (!selectedTopicId) {
      setTopicDetail(null);
      return;
    }

    let isMounted = true;
    setTopicLoading(true);
    setTopicError(null);

    fetchTopicDetail(selectedTopicId)
      .then((res) => {
        if (isMounted) setTopicDetail(res);
      })
      .catch((err: unknown) => {
        if (isMounted) {
          const msg = err instanceof Error ? err.message : "Failed to load topic assets.";
          setTopicError(msg);
        }
      })
      .finally(() => {
        if (isMounted) setTopicLoading(false);
      });

    // Check study plan
    try {
      const saved = localStorage.getItem("gpat_learner_study_plan_v1");
      if (saved) {
        const items = JSON.parse(saved);
        setIsInPlan(items.some((i: { topicId: string }) => i.topicId === selectedTopicId));
      }
    } catch {
      // ignore
    }

    return () => {
      isMounted = false;
    };
  }, [selectedTopicId]);

  // Toggle study plan for active topic
  const handleTogglePlan = () => {
    if (!selectedTopicId || !topicDetail) return;
    try {
      const saved = localStorage.getItem("gpat_learner_study_plan_v1");
      const items = saved ? JSON.parse(saved) : [];
      if (isInPlan) {
        const filtered = items.filter((i: { topicId: string }) => i.topicId !== selectedTopicId);
        localStorage.setItem("gpat_learner_study_plan_v1", JSON.stringify(filtered));
        setIsInPlan(false);
      } else {
        items.push({
          id: `plan_${Date.now()}`,
          topicId: selectedTopicId,
          topicTitle: topicDetail.topic.name,
          subjectId: topicDetail.topic.subject_id || "pharmacology",
          estimatedMinutes: 15,
          isCompleted: false,
          addedAt: new Date().toISOString(),
        });
        localStorage.setItem("gpat_learner_study_plan_v1", JSON.stringify(items));
        setIsInPlan(true);
      }
    } catch {
      // ignore
    }
  };

  // Topic filter logic based on genuine data
  const matchesTopicFilter = useCallback(
    (topic: SyllabusTopicSummary) => {
      const progress = progressConcepts[topic.topic_id];

      if (filterMode === "high_yield") {
        const isImportant = progress && progress.importance_score >= 8;
        const hasQuestions = topic.question_count > 0;
        return isImportant || hasQuestions;
      }

      if (filterMode === "needs_review") {
        const isNeedsRepair = progress?.mastery_state === "NEEDS_REPAIR";
        const isUnverified = topic.is_verified === false;
        return isNeedsRepair || isUnverified;
      }

      return true;
    },
    [filterMode, progressConcepts]
  );

  // Search results
  const searchResults = useMemo(() => {
    if (!treeData) return [];
    const query = searchQuery.trim().toLowerCase();
    if (!query) return null;

    const matchedTopics: Array<{
      topic: SyllabusTopicSummary;
      examSubjectId: string;
      examSubjectName: string;
      curriculumId: string;
      curriculumName: string;
    }> = [];

    treeData.tree.forEach((exam) => {
      exam.curriculum_subjects.forEach((curr) => {
        curr.topics.forEach((t) => {
          const textToMatch = `${exam.name} ${curr.name} ${t.name}`.toLowerCase();
          if (textToMatch.includes(query) && matchesTopicFilter(t)) {
            matchedTopics.push({
              topic: t,
              examSubjectId: exam.exam_subject_id,
              examSubjectName: exam.name,
              curriculumId: curr.curriculum_subject_id,
              curriculumName: curr.name,
            });
          }
        });
      });
    });

    return matchedTopics;
  }, [treeData, searchQuery, matchesTopicFilter]);

  // Active Subject Group (Screen 2 & Screen 3 context)
  const currentExamGroup: SyllabusExamGroup | undefined = useMemo(() => {
    if (!treeData || !selectedSubjectId) return undefined;
    return treeData.tree.find(
      (g) => g.exam_subject_id.toLowerCase() === selectedSubjectId.toLowerCase()
    );
  }, [treeData, selectedSubjectId]);

  // Active Unit (Screen 3 context)
  const currentUnit: SyllabusCurriculumSubject | undefined = useMemo(() => {
    if (!currentExamGroup || !selectedUnitId) return undefined;
    return currentExamGroup.curriculum_subjects.find(
      (c) => c.curriculum_subject_id === selectedUnitId
    );
  }, [currentExamGroup, selectedUnitId]);

  // Illustration selector
  const getSubjectIllustration = (subjId: string, className = "w-full h-full") => {
    switch (subjId) {
      case "pharmacology":
        return <SynapseIllustration className={className} />;
      case "pharmaceutics":
        return <DissolutionIllustration className={className} />;
      case "pharmaceutical_chemistry":
        return <ChemistryMolecularIllustration className={className} />;
      case "pharmacognosy":
        return <PharmacognosyFlowerIllustration className={className} />;
      case "other_subjects":
      default:
        return <BiotechnologyDnaIllustration className={className} />;
    }
  };

  // --- Render Loading State ---
  if (loading) {
    return (
      <div className="space-y-6 max-w-5xl mx-auto py-2 animate-enter">
        <div className="space-y-2">
          <Skeleton className="h-8 w-60" />
          <Skeleton className="h-4 w-80" />
        </div>
        <div className="h-11 w-full rounded-xl bg-[var(--color-surface-raised)] animate-pulse" />
        <div className="space-y-3">
          <Skeleton className="h-32 rounded-2xl" />
          <Skeleton className="h-32 rounded-2xl" />
          <Skeleton className="h-32 rounded-2xl" />
        </div>
      </div>
    );
  }

  // --- Render Error State ---
  if (error && !treeData) {
    return (
      <div className="space-y-6 max-w-xl mx-auto py-12 animate-enter">
        <ErrorState
          title="Syllabus Explorer Unavailable"
          message={error}
          onRetry={loadTree}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto py-1 animate-enter pb-8">
      {/* Offline Alert */}
      {isOffline && (
        <div
          role="status"
          className="p-3 rounded-lg bg-[rgb(252_211_77/0.1)] border border-[var(--color-status-warning)]/30 text-xs text-[var(--color-status-warning)] flex items-center gap-2"
        >
          <WifiSlash size={16} weight="bold" />
          <span>Offline mode: Browsing cached syllabus structure.</span>
        </div>
      )}

      {/* =========================================================================
          SCREEN 4: TOPIC DETAIL (Matching Reference B Phone 4)
          ========================================================================= */}
      {selectedTopicId ? (
        <div className="space-y-4 animate-enter">
          {/* Top Bar Navigation & Actions */}
          <div className="flex items-center justify-between pb-2 border-b border-[var(--color-border-subtle)]">
            <button
              type="button"
              onClick={selectedUnitId ? handleBackToTopicList : selectedSubjectId ? handleBackToUnits : handleBackToSubjects}
              className="inline-flex items-center gap-2 text-xs font-semibold text-[var(--color-accent)] hover:underline min-h-[44px] px-2 -ml-2 rounded-lg"
              aria-label="Back to topic list"
            >
              <ArrowLeft size={16} weight="bold" />
              <span>
                {selectedUnitId ? currentUnit?.name || "Unit Topics" : selectedSubjectId ? "Subject Overview" : "All Subjects"}
              </span>
            </button>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleTogglePlan}
                className={`p-2 rounded-lg text-xs flex items-center gap-1.5 transition-colors min-h-[40px] px-2.5 font-medium border ${
                  isInPlan
                    ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
                    : "bg-[var(--color-surface-base)] text-[var(--color-text-secondary)] border-[var(--color-border-subtle)] hover:text-[var(--color-text-primary)]"
                }`}
                title={isInPlan ? "Saved in study plan" : "Bookmark to study plan"}
                aria-label="Bookmark to study plan"
              >
                <BookmarkSimple size={16} weight={isInPlan ? "fill" : "bold"} />
                <span className="text-[11px] font-mono">{isInPlan ? "In Plan" : "Plan"}</span>
              </button>
            </div>
          </div>

          {topicLoading ? (
            <div className="p-8 space-y-4 rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)]">
              <Skeleton className="h-6 w-32" />
              <Skeleton className="h-8 w-3/4" />
              <Skeleton className="h-36 w-full" />
            </div>
          ) : topicError ? (
            <ErrorState
              title="Failed to Load Topic Detail"
              message={topicError}
              onRetry={() => {
                if (selectedTopicId) setSelectedTopicId(selectedTopicId);
              }}
            />
          ) : topicDetail ? (
            <div className="space-y-5 animate-enter">
              {/* Topic Hero Card with Graphic */}
              {(() => {
                const subjTheme = getSubjectTheme(topicDetail.topic.subject_id);

                return (
                  <div
                    className="p-5 sm:p-6 rounded-2xl border bg-[var(--color-surface-base)] relative overflow-hidden"
                    style={{
                      borderColor: subjTheme.borderHover,
                      boxShadow: `0 8px 24px -6px rgba(0, 0, 0, 0.35), 0 0 20px -2px ${subjTheme.glowColor}`,
                    }}
                  >
                    {/* Ambient Glow & Illustration Watermark */}
                    <div
                      className="absolute right-0 top-1/2 -translate-y-1/2 w-44 h-44 opacity-20 pointer-events-none"
                      aria-hidden="true"
                    >
                      {getSubjectIllustration(topicDetail.topic.subject_id || "pharmacology")}
                    </div>

                    <div className="relative z-10 space-y-2 max-w-xl">
                      <div className="flex flex-wrap items-center gap-2">
                        <span
                          className="text-[10px] font-mono font-bold tracking-wider uppercase px-2 py-0.5 rounded"
                          style={{
                            backgroundColor: subjTheme.badgeBg,
                            color: subjTheme.accentText,
                            border: `1px solid ${subjTheme.badgeBorder}`,
                          }}
                        >
                          {topicDetail.topic.exam_subject_name || subjTheme.shortName}
                        </span>
                        {topicDetail.topic.curriculum_name && (
                          <span className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
                            &bull; {topicDetail.topic.curriculum_name}
                          </span>
                        )}
                        {progressConcepts[selectedTopicId]?.mastery_state === "NEEDS_REPAIR" && (
                          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-red-950/60 text-red-400 border border-red-500/30 flex items-center gap-1">
                            <WarningCircle size={12} weight="bold" /> Needs Repair
                          </span>
                        )}
                      </div>

                      <h1 className="text-xl sm:text-2xl font-extrabold text-[var(--color-text-primary)] leading-tight">
                        {topicDetail.topic.name}
                      </h1>

                      {/* Editorial notice if unverified */}
                      {topicDetail.topic.verification_status !== "VERIFIED" && (
                        <div className="pt-1 flex items-center gap-1.5 text-[11px] font-mono text-amber-400">
                          <Warning size={13} weight="bold" />
                          <span>Topic in baseline review. Verified questions and excerpts linked below.</span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })()}

              {/* 4 Navigation Tabs: Learn, Practice, PYQs, Notes (Reference B Phone 4) */}
              <div className="flex items-center gap-2 border-b border-[var(--color-border-subtle)] pb-1 overflow-x-auto">
                {[
                  { id: "learn", label: "Learn", count: topicDetail.chunk_count + topicDetail.objective_count },
                  { id: "practice", label: "Practice", count: topicDetail.question_count },
                  { id: "pyqs", label: "PYQs", count: topicDetail.questions?.filter((q) => q.pyq_year).length || 0 },
                  { id: "notes", label: "Notes & Flashcards", count: topicDetail.flashcard_count },
                ].map((t) => {
                  const isActive = topicTab === t.id;
                  return (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setTopicTab(t.id as typeof topicTab)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all shrink-0 flex items-center gap-1.5 min-h-[38px] ${
                        isActive
                          ? "bg-[var(--color-surface-raised)] text-emerald-400 border border-emerald-500/30 shadow-xs"
                          : "text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)]"
                      }`}
                    >
                      <span>{t.label}</span>
                      {t.count > 0 && (
                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)]">
                          {t.count}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>

              {/* TAB 1: LEARN (Quick Summary & Study Notes) */}
              {topicTab === "learn" && (
                <div className="space-y-4">
                  {/* Quick Summary Card (Reference B Phone 4) */}
                  <div className="p-4 sm:p-5 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] space-y-2">
                    <div className="flex items-center gap-2 text-amber-400 text-xs font-semibold">
                      <Sparkle size={16} weight="fill" />
                      <span>Quick Summary</span>
                    </div>
                    {topicDetail.content_chunks.length > 0 ? (
                      <p className="text-xs sm:text-sm text-[var(--color-text-secondary)] leading-relaxed">
                        {topicDetail.content_chunks[0].content}
                      </p>
                    ) : topicDetail.learning_objectives.length > 0 ? (
                      <p className="text-xs sm:text-sm text-[var(--color-text-secondary)] leading-relaxed">
                        {topicDetail.learning_objectives[0].objective_statement}
                      </p>
                    ) : (
                      <p className="text-xs text-[var(--color-text-tertiary)] italic">
                        Essential syllabus topic for GPAT examination. In-depth theory excerpts are currently mapped to official textbook chapters.
                      </p>
                    )}
                  </div>

                  {/* Learning Objectives List */}
                  {topicDetail.learning_objectives.length > 0 && (
                    <div className="space-y-2">
                      <span className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase font-mono px-1">
                        Learning Objectives
                      </span>
                      <div className="space-y-2">
                        {topicDetail.learning_objectives.map((lo, idx) => (
                          <div
                            key={lo.objective_id || idx}
                            className="p-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/40 text-xs space-y-1"
                          >
                            <div className="flex items-center gap-2">
                              <span className="px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-400 font-mono text-[10px] font-bold">
                                {lo.bloom_level || "Core Principle"}
                              </span>
                              <span className="font-semibold text-[var(--color-text-primary)]">
                                {lo.objective_statement}
                              </span>
                            </div>
                            {lo.clinical_pearl && (
                              <p className="text-[11px] text-[var(--color-text-secondary)] pl-2 border-l border-emerald-500/40">
                                <strong>Exam Pearl:</strong> {lo.clinical_pearl}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Primary Action Button: Start Practice */}
                  <div className="pt-2">
                    <Link href={`/today?mode=repair&topic=${encodeURIComponent(selectedTopicId)}`}>
                      <Button
                        size="md"
                        variant="primary"
                        className="interactive-cta w-full h-12 min-h-[48px] rounded-xl text-sm font-semibold gap-2 shadow-sm"
                      >
                        <Target size={18} weight="bold" />
                        <span>Start Practice ({topicDetail.question_count || "Concept Drill"})</span>
                        <ArrowRight size={16} weight="bold" />
                      </Button>
                    </Link>
                  </div>
                </div>
              )}

              {/* TAB 2: PRACTICE QUESTIONS */}
              {topicTab === "practice" && (
                <div className="space-y-3">
                  {topicDetail.questions.length === 0 ? (
                    <div className="p-8 text-center text-xs text-[var(--color-text-tertiary)] border border-dashed border-[var(--color-border-subtle)] rounded-xl space-y-2">
                      <Question size={24} className="mx-auto text-[var(--color-text-tertiary)]" />
                      <p className="text-[var(--color-text-secondary)] font-medium">Practice questions staging in progress.</p>
                      <p className="text-[11px]">Questions for this topic are currently undergoing editorial alignment.</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {topicDetail.questions.map((q, idx) => (
                        <div
                          key={q.id || idx}
                          className="p-4 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] space-y-2.5"
                        >
                          <div className="flex items-center justify-between text-[11px] font-mono text-[var(--color-text-tertiary)]">
                            <span className="font-semibold text-[var(--color-text-secondary)]">Question #{idx + 1}</span>
                            {q.pyq_year && (
                              <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 font-bold border border-blue-500/20">
                                GPAT {q.pyq_year}
                              </span>
                            )}
                          </div>
                          <p className="text-xs sm:text-sm text-[var(--color-text-primary)] font-medium">
                            {q.question_text}
                          </p>
                          {q.options && (
                            <ul className="space-y-1.5 pt-1">
                              {q.options.map((opt, oIdx) => (
                                <li
                                  key={oIdx}
                                  className="p-2 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/50 text-xs text-[var(--color-text-secondary)]"
                                >
                                  <span className="font-mono font-bold mr-2 text-[var(--color-text-primary)]">
                                    {String.fromCharCode(65 + oIdx)}.
                                  </span>
                                  {opt}
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* TAB 3: PYQS */}
              {topicTab === "pyqs" && (
                <div className="space-y-3">
                  {topicDetail.questions.filter((q) => q.pyq_year).length === 0 ? (
                    <div className="p-8 text-center text-xs text-[var(--color-text-tertiary)] border border-dashed border-[var(--color-border-subtle)] rounded-xl space-y-2">
                      <BookmarksSimple size={24} className="mx-auto text-[var(--color-text-tertiary)]" />
                      <p className="text-[var(--color-text-secondary)] font-medium">No verified past year questions directly linked.</p>
                      <p className="text-[11px]">Explore the PYQ Explorer route for complete past examination papers.</p>
                      <Link href="/pyqs">
                        <Button size="sm" variant="secondary" className="mt-2 text-xs">
                          Open PYQ Explorer &rarr;
                        </Button>
                      </Link>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {topicDetail.questions
                        .filter((q) => q.pyq_year)
                        .map((q, idx) => (
                          <div
                            key={q.id || idx}
                            className="p-4 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] space-y-2"
                          >
                            <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 font-bold border border-blue-500/20 text-[10px] font-mono">
                              GPAT {q.pyq_year}
                            </span>
                            <p className="text-xs sm:text-sm text-[var(--color-text-primary)] font-medium">
                              {q.question_text}
                            </p>
                          </div>
                        ))}
                    </div>
                  )}
                </div>
              )}

              {/* TAB 4: NOTES & FLASHCARDS */}
              {topicTab === "notes" && (
                <div className="space-y-3">
                  {topicDetail.flashcards.length === 0 ? (
                    <div className="p-8 text-center text-xs text-[var(--color-text-tertiary)] border border-dashed border-[var(--color-border-subtle)] rounded-xl space-y-2">
                      <Cards size={24} className="mx-auto text-[var(--color-text-tertiary)]" />
                      <p className="text-[var(--color-text-secondary)] font-medium">No spaced repetition flashcards for this topic yet.</p>
                      <p className="text-[11px]">Flashcards are automatically consolidated after answering practice questions.</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {topicDetail.flashcards.map((fc, idx) => (
                        <div
                          key={fc.card_id || idx}
                          className="p-4 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] space-y-2"
                        >
                          <div className="flex items-center gap-1.5 text-[11px] font-mono text-purple-400 font-semibold">
                            <Cards size={14} weight="bold" />
                            <span>Flashcard #{idx + 1}</span>
                          </div>
                          <div className="text-xs font-semibold text-[var(--color-text-primary)]">
                            Q: {fc.front}
                          </div>
                          <div className="text-xs text-emerald-400 font-medium pl-2 border-l-2 border-emerald-500/40">
                            A: {fc.back}
                          </div>
                          {fc.explanation && (
                            <p className="text-[11px] text-[var(--color-text-tertiary)] pt-1 border-t border-[var(--color-border-subtle)]">
                              {fc.explanation}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : null}
        </div>
      ) : selectedSubjectId && currentExamGroup && selectedUnitId && currentUnit ? (
        /* =========================================================================
           SCREEN 3: UNIT VIEW / TOPIC LIST (Matching Reference B Phone 3)
           ========================================================================= */
        (() => {
          const theme = getSubjectTheme(currentExamGroup.exam_subject_id);
          const courseTopics = currentUnit.topics.filter(matchesTopicFilter);

          return (
            <div className="space-y-5 animate-enter">
              {/* Back to Subject Overview */}
              <div className="flex items-center justify-between pb-2 border-b border-[var(--color-border-subtle)]">
                <button
                  type="button"
                  onClick={handleBackToUnits}
                  className="inline-flex items-center gap-2 text-xs font-semibold text-[var(--color-accent)] hover:underline min-h-[44px] px-2 -ml-2 rounded-lg"
                  aria-label="Back to Subject Overview"
                >
                  <ArrowLeft size={16} weight="bold" />
                  <span>{currentExamGroup.name}</span>
                </button>

                <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-tertiary)]">
                  <span>{currentUnit.topics.length} topics</span>
                </div>
              </div>

              {/* Unit Header Title */}
              <div>
                <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-emerald-400 block">
                  {currentExamGroup.name} &bull; {currentUnit.pci_course_code ? `PCI ${currentUnit.pci_course_code}` : "Course Module"}
                </span>
                <h1 className="text-xl sm:text-2xl font-extrabold text-[var(--color-text-primary)]">
                  {currentUnit.name}
                </h1>
                <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">
                  Showing {courseTopics.length} of {currentUnit.topics.length} syllabus topics
                </p>
              </div>

              {/* Filter Chips inside Unit (All Topics / High-yield / Needs Review) */}
              <div
                className="flex items-center gap-2 overflow-x-auto pb-1 text-xs -mx-1 px-1 scroll-smooth"
                role="radiogroup"
                aria-label="Unit topic filters"
              >
                {[
                  { id: "all" as FilterMode, label: "All Topics" },
                  { id: "high_yield" as FilterMode, label: "High-yield" },
                  { id: "needs_review" as FilterMode, label: "Needs Review" },
                ].map((f) => {
                  const isActive = filterMode === f.id;
                  return (
                    <button
                      key={f.id}
                      type="button"
                      role="radio"
                      aria-checked={isActive}
                      onClick={() => setFilterMode(f.id)}
                      className={`px-3.5 py-1.5 rounded-full text-xs font-mono font-medium transition-all min-h-[38px] shrink-0 touch-manipulation ${
                        isActive
                          ? "bg-emerald-500 text-slate-950 font-bold shadow-2xs"
                          : "bg-[var(--color-surface-base)] text-[var(--color-text-secondary)] border border-[var(--color-border-subtle)] hover:border-emerald-500/40 hover:text-[var(--color-text-primary)]"
                      }`}
                    >
                      {f.label}
                    </button>
                  );
                })}
              </div>

              {/* Topic Rows List (Reference B Phone 3) */}
              <div className="space-y-2">
                {courseTopics.length === 0 ? (
                  <div className="p-8 text-center text-xs text-[var(--color-text-tertiary)] border border-dashed border-[var(--color-border-subtle)] rounded-xl space-y-1">
                    <p className="text-[var(--color-text-secondary)] font-medium">No topics found for &quot;{filterMode}&quot; filter.</p>
                    <p>Switch to &quot;All Topics&quot; to browse all available units.</p>
                  </div>
                ) : (
                  courseTopics.map((top: SyllabusTopicSummary) => {
                    const progress = progressConcepts[top.topic_id];
                    const isNeedsRepair = progress?.mastery_state === "NEEDS_REPAIR";
                    const isMastered = progress?.mastery_state === "DEMONSTRATED_MASTERY";

                    return (
                      <button
                        key={top.topic_id}
                        type="button"
                        onClick={() => handleSelectTopic(top.topic_id)}
                        className="interactive-card w-full p-3.5 sm:p-4 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] hover:border-emerald-500/40 hover:bg-[var(--color-surface-raised)]/60 text-left transition-all min-h-[52px] flex items-center justify-between group shadow-2xs"
                        aria-label={`Open topic ${top.name}`}
                      >
                        <div className="flex items-center gap-3 min-w-0 pr-3">
                          <FileText
                            size={18}
                            weight="bold"
                            style={{ color: theme.accentText }}
                            className="shrink-0"
                          />

                          <div className="min-w-0">
                            <span className="text-xs sm:text-sm font-semibold text-[var(--color-text-primary)] group-hover:text-emerald-400 transition-colors block truncate">
                              {top.name}
                            </span>
                            <div className="flex items-center gap-2 text-[10px] font-mono text-[var(--color-text-tertiary)] mt-0.5">
                              {isNeedsRepair && (
                                <span className="text-red-400 font-semibold flex items-center gap-0.5">
                                  <WarningCircle size={11} weight="bold" /> Needs Repair
                                </span>
                              )}
                              {isMastered && (
                                <span className="text-emerald-400 font-semibold flex items-center gap-0.5">
                                  <Sparkle size={11} weight="fill" /> Mastered
                                </span>
                              )}
                              {top.question_count > 0 && (
                                <span>{top.question_count} practice questions</span>
                              )}
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          {isMastered ? (
                            <CheckCircle size={18} weight="fill" className="text-emerald-400 shrink-0" />
                          ) : (
                            <Circle size={18} weight="regular" className="text-[var(--color-text-tertiary)] shrink-0" />
                          )}
                          <ArrowRight
                            size={14}
                            className="text-[var(--color-text-tertiary)] group-hover:text-emerald-400 group-hover:translate-x-0.5 transition-all"
                          />
                        </div>
                      </button>
                    );
                  })
                )}
              </div>
            </div>
          );
        })()
      ) : selectedSubjectId && currentExamGroup ? (
        /* =========================================================================
           SCREEN 2: SUBJECT OVERVIEW (Matching Reference B Phone 2)
           ========================================================================= */
        (() => {
          const theme = getSubjectTheme(currentExamGroup.exam_subject_id);
          const Icon = theme.icon;

          return (
            <div className="space-y-5 animate-enter">
              {/* Back to Syllabus Explorer */}
              <div className="flex items-center justify-between pb-2 border-b border-[var(--color-border-subtle)]">
                <button
                  type="button"
                  onClick={handleBackToSubjects}
                  className="inline-flex items-center gap-2 text-xs font-semibold text-[var(--color-accent)] hover:underline min-h-[44px] px-2 -ml-2 rounded-lg"
                  aria-label="Back to Syllabus Explorer"
                >
                  <ArrowLeft size={16} weight="bold" />
                  <span>Syllabus Explorer</span>
                </button>

                <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-tertiary)]">
                  <span>{currentExamGroup.total_topics} total topics</span>
                </div>
              </div>

              {/* Subject Hero Header with Visual & Key Metrics (Reference B Phone 2) */}
              <div
                className="p-5 sm:p-6 rounded-2xl border bg-[var(--color-surface-base)] relative overflow-hidden"
                style={{
                  borderColor: theme.borderHover,
                  boxShadow: `0 8px 24px -6px rgba(0, 0, 0, 0.35), 0 0 20px -2px ${theme.glowColor}`,
                }}
              >
                {/* Illustration Watermark */}
                <div
                  className="absolute right-0 top-1/2 -translate-y-1/2 w-48 h-48 opacity-25 pointer-events-none"
                  aria-hidden="true"
                >
                  {getSubjectIllustration(currentExamGroup.exam_subject_id)}
                </div>

                <div className="relative z-10 space-y-3 max-w-lg">
                  <div
                    className="h-11 w-11 rounded-xl flex items-center justify-center shrink-0"
                    style={{
                      backgroundColor: theme.badgeBg,
                      color: theme.accentText,
                      border: `1px solid ${theme.badgeBorder}`,
                    }}
                  >
                    <Icon size={24} weight="bold" />
                  </div>

                  <div>
                    <h1 className="text-xl sm:text-2xl font-extrabold text-[var(--color-text-primary)]">
                      {currentExamGroup.name}
                    </h1>
                    <p className="text-xs sm:text-sm text-[var(--color-text-secondary)] mt-1 leading-relaxed">
                      Core examination area. Tap any unit below to browse structured syllabus topics and practice resources.
                    </p>
                  </div>

                  {/* 3 Overview Stat Badges (Reference B Phone 2) */}
                  <div className="flex flex-wrap items-center gap-2.5 pt-2 text-xs font-mono">
                    <div className="px-3 py-1.5 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] flex items-center gap-2">
                      <FileText size={15} weight="bold" className="text-emerald-400" />
                      <div>
                        <span className="font-bold text-[var(--color-text-primary)]">{currentExamGroup.total_topics}</span>
                        <span className="text-[10px] text-[var(--color-text-secondary)] ml-1">Topics</span>
                      </div>
                    </div>

                    <div className="px-3 py-1.5 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] flex items-center gap-2">
                      <Folder size={15} weight="bold" className="text-blue-400" />
                      <div>
                        <span className="font-bold text-[var(--color-text-primary)]">{currentExamGroup.curriculum_subjects.length}</span>
                        <span className="text-[10px] text-[var(--color-text-secondary)] ml-1">Units</span>
                      </div>
                    </div>

                    <div className="px-3 py-1.5 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] flex items-center gap-2">
                      <Flame size={15} weight="fill" className="text-amber-400" />
                      <div>
                        <span className="font-bold text-[var(--color-text-primary)]">High-yield</span>
                        <span className="text-[10px] text-[var(--color-text-secondary)] ml-1">Focus</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Units List (Reference B Phone 2) */}
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs font-mono text-[var(--color-text-secondary)] px-1">
                  <span className="uppercase tracking-wider font-semibold">
                    Curriculum Units ({currentExamGroup.curriculum_subjects.length})
                  </span>
                  <span>Select a unit to view topics &rarr;</span>
                </div>

                <div className="space-y-2">
                  {currentExamGroup.curriculum_subjects.map((curr, idx) => (
                    <button
                      key={curr.curriculum_subject_id}
                      type="button"
                      onClick={() => handleSelectUnit(curr.curriculum_subject_id)}
                      className="interactive-card w-full p-4 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] hover:border-emerald-500/40 hover:bg-[var(--color-surface-raised)]/60 text-left transition-all min-h-[56px] flex items-center justify-between group shadow-2xs"
                      aria-label={`Open unit ${curr.name}`}
                    >
                      <div className="flex items-center gap-3.5 min-w-0 pr-3">
                        <div
                          className="h-8 w-8 rounded-lg flex items-center justify-center shrink-0 font-mono text-xs font-bold"
                          style={{
                            backgroundColor: theme.badgeBg,
                            color: theme.accentText,
                          }}
                        >
                          {idx + 1}
                        </div>

                        <div className="min-w-0">
                          <span className="text-xs sm:text-sm font-semibold text-[var(--color-text-primary)] group-hover:text-emerald-400 transition-colors block truncate">
                            {curr.name}
                          </span>
                          <span className="text-[10px] font-mono text-[var(--color-text-tertiary)] block mt-0.5">
                            {curr.topics.length} topics &bull; {curr.pci_course_code ? `PCI ${curr.pci_course_code}` : "Course Module"}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        <span className="text-xs font-mono font-medium text-[var(--color-text-secondary)] group-hover:text-emerald-400 transition-colors">
                          {curr.topics.length} topics
                        </span>
                        <CaretRight
                          size={14}
                          weight="bold"
                          className="text-[var(--color-text-tertiary)] group-hover:text-emerald-400 group-hover:translate-x-0.5 transition-all"
                        />
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          );
        })()
      ) : (
        /* =========================================================================
           SCREEN 1: SYLLABUS EXPLORER (Matching Reference A)
           ========================================================================= */
        <div className="space-y-5 animate-enter">
          {/* Header (Reference A) */}
          <div className="flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-3 pb-2 border-b border-[var(--color-border-subtle)]">
            <div>
              <h1 className="text-xl sm:text-2xl font-extrabold tracking-tight text-[var(--color-text-primary)]">
                Explore your <span className="text-emerald-400 underline decoration-emerald-500/30 underline-offset-4">syllabus</span> 🌿
              </h1>
              <p className="text-xs sm:text-sm text-[var(--color-text-secondary)] mt-0.5">
                Find your next topic to master.
              </p>
            </div>

            <Link
              href="/today"
              className="inline-flex items-center gap-1.5 text-xs font-medium text-[var(--color-accent)] hover:underline min-h-[44px] py-1"
            >
              <span>Back to Today</span>
              <ArrowRight size={13} weight="bold" />
            </Link>
          </div>

          {/* Search Input (Reference A) */}
          <div className="relative">
            <MagnifyingGlass
              size={18}
              weight="bold"
              className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)] pointer-events-none"
            />
            <input
              type="text"
              placeholder="Search subjects, units or topics"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-10 py-3 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] text-xs sm:text-sm text-[var(--color-text-primary)] placeholder-[var(--color-text-tertiary)] focus:outline-none focus:border-emerald-500/80 focus:ring-1 focus:ring-emerald-500/30 transition-all shadow-2xs min-h-[48px]"
              aria-label="Search syllabus topics"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] p-1.5 rounded-full hover:bg-[var(--color-surface-raised)] min-h-[36px] min-w-[36px] flex items-center justify-center"
                aria-label="Clear search input"
              >
                <X size={15} weight="bold" />
              </button>
            )}
          </div>

          {/* Filter Chips (Reference A: All subjects, High-yield, Needs review) */}
          <div
            className="flex items-center gap-2 overflow-x-auto pb-1 text-xs -mx-1 px-1 scroll-smooth"
            role="radiogroup"
            aria-label="Syllabus view filters"
          >
            {[
              { id: "all" as FilterMode, label: "All subjects" },
              { id: "high_yield" as FilterMode, label: "High-yield" },
              { id: "needs_review" as FilterMode, label: "Needs review" },
            ].map((f) => {
              const isActive = filterMode === f.id;
              return (
                <button
                  key={f.id}
                  type="button"
                  role="radio"
                  aria-checked={isActive}
                  onClick={() => setFilterMode(f.id)}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-mono font-medium transition-all min-h-[38px] shrink-0 touch-manipulation ${
                    isActive
                      ? "bg-emerald-500 text-slate-950 font-bold shadow-2xs"
                      : "bg-[var(--color-surface-base)] text-[var(--color-text-secondary)] border border-[var(--color-border-subtle)] hover:border-emerald-500/40 hover:text-[var(--color-text-primary)]"
                  }`}
                >
                  {f.label}
                </button>
              );
            })}
          </div>

          {/* Search Results Dropdown / Panel if query is typed */}
          {searchResults !== null ? (
            <div className="space-y-3 pt-1">
              <div className="flex items-center justify-between text-xs font-mono text-[var(--color-text-secondary)] px-1">
                <span>{searchResults.length} search results for &ldquo;{searchQuery}&rdquo;</span>
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  className="text-emerald-400 hover:underline"
                >
                  Clear search
                </button>
              </div>

              {searchResults.length === 0 ? (
                <div className="p-8 text-center text-xs text-[var(--color-text-tertiary)] border border-dashed border-[var(--color-border-subtle)] rounded-xl space-y-1">
                  <p className="text-[var(--color-text-secondary)] font-medium">No syllabus topics found.</p>
                  <p>Try searching for pharmacology, receptors, formulations, or chemistry keywords.</p>
                </div>
              ) : (
                <ul className="space-y-2" aria-label="Search results list">
                  {searchResults.map(({ topic, examSubjectId, examSubjectName, curriculumId, curriculumName }) => {
                    const theme = getSubjectTheme(examSubjectId);

                    return (
                      <li key={topic.topic_id}>
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedSubjectId(examSubjectId);
                            setSelectedUnitId(curriculumId);
                            handleSelectTopic(topic.topic_id);
                          }}
                          className="w-full p-3 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] hover:border-emerald-500/40 hover:bg-[var(--color-surface-raised)]/60 text-left transition-all min-h-[48px] flex items-center justify-between group shadow-2xs"
                        >
                          <div className="min-w-0 pr-3">
                            <span className="text-xs sm:text-sm font-semibold text-[var(--color-text-primary)] group-hover:text-emerald-400 block truncate">
                              {topic.name}
                            </span>
                            <div className="flex items-center gap-1.5 text-[10px] font-mono text-[var(--color-text-tertiary)] mt-0.5">
                              <span style={{ color: theme.accentText }}>{examSubjectName}</span>
                              <span>&bull;</span>
                              <span className="truncate">{curriculumName}</span>
                            </div>
                          </div>

                          <ArrowRight
                            size={14}
                            className="text-[var(--color-text-tertiary)] group-hover:text-emerald-400 group-hover:translate-x-0.5 transition-all shrink-0"
                          />
                        </button>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          ) : (
            /* Five Subject Cards (Matching Reference A on mobile, responsive grid on tablet/desktop) */
            <div className="space-y-3.5 md:space-y-0 md:grid md:grid-cols-2 md:gap-4 pt-1">
              {CANONICAL_SUBJECTS.map((subj) => {
                const theme = getSubjectTheme(subj.id);
                const Icon = theme.icon;

                const realGroup = treeData?.tree.find(
                  (g) => g.exam_subject_id.toLowerCase() === subj.id.toLowerCase()
                );
                const topicCount = realGroup ? realGroup.total_topics : subj.fallbackTopics;

                return (
                  <button
                    key={subj.id}
                    type="button"
                    onClick={() => handleSelectSubject(subj.id)}
                    style={
                      {
                        "--card-accent-border": theme.borderHover,
                        "--card-glow": theme.glowColor,
                      } as React.CSSProperties
                    }
                    className="discovery-card w-full p-4 sm:p-5 text-left border border-[var(--color-border-subtle)]/70 hover:border-transparent group touch-manipulation min-h-[140px] cursor-pointer overflow-hidden relative"
                    aria-label={`Explore ${subj.name} syllabus`}
                  >
                    {/* Background Illustration Artwork on the Right (Reference A) */}
                    <div
                      className="absolute right-8 top-1/2 -translate-y-1/2 w-36 h-36 opacity-25 group-hover:opacity-40 transition-opacity pointer-events-none"
                      aria-hidden="true"
                    >
                      {getSubjectIllustration(subj.id)}
                    </div>

                    <div className="relative z-10 flex flex-col justify-between h-full">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-3.5 min-w-0 pr-10">
                          {/* Subject Icon in Rounded Badge */}
                          <div
                            className="h-11 w-11 rounded-xl flex items-center justify-center shrink-0 transition-transform group-hover:scale-105"
                            style={{
                              backgroundColor: theme.badgeBg,
                              color: theme.accentText,
                              border: `1px solid ${theme.badgeBorder}`,
                            }}
                          >
                            <Icon size={22} weight="bold" />
                          </div>

                          <div className="min-w-0">
                            <h2 className="text-base sm:text-lg font-bold text-[var(--color-text-primary)] group-hover:text-emerald-400 transition-colors leading-snug">
                              {subj.name}
                            </h2>
                            <p className="text-xs text-[var(--color-text-secondary)] mt-0.5 leading-relaxed line-clamp-2">
                              {subj.description}
                            </p>
                            <div className="flex items-center gap-1.5 text-[11px] font-mono text-[var(--color-text-tertiary)] mt-1.5">
                              <FileText size={13} />
                              <span>{topicCount} topics</span>
                            </div>
                          </div>
                        </div>

                        {/* Round Circular Arrow Button (Reference A) */}
                        <div className="h-9 w-9 rounded-full bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] flex items-center justify-center text-[var(--color-text-secondary)] group-hover:text-emerald-400 group-hover:bg-emerald-500/10 group-hover:border-emerald-500/30 transition-all shrink-0">
                          <CaretRight size={15} weight="bold" />
                        </div>
                      </div>

                      {/* Bottom CTA Action Bar (Reference A) */}
                      <div className="pt-3 mt-3 border-t border-[var(--color-border-subtle)]/60 flex items-center justify-between text-xs font-semibold text-emerald-400">
                        <span>Explore topics</span>
                        <ArrowRight
                          size={14}
                          weight="bold"
                          className="group-hover:translate-x-1 transition-transform"
                        />
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}

          {/* Footnote */}
          <div className="p-3 rounded-xl border border-[var(--color-border-subtle)]/70 bg-[var(--color-surface-raised)]/30 text-[11px] text-[var(--color-text-tertiary)] flex items-start gap-2 font-mono">
            <p>
              Canonical syllabus covers 221 topics across 19 PCI courses and 5 NBEMS examination groups.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
