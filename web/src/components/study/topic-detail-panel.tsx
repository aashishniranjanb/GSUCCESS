"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  TopicDetailResponse,
} from "@/lib/api/types";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  BookOpen,
  Cards,
  FileText,
  Target,
  ArrowLeft,
  CheckCircle,
  Question,
  PlusCircle,
  Check,
  WarningCircle,
  Sparkle,
  Image as ImageIcon,
  RocketLaunch,
  ArrowsCounterClockwise,
  ArrowRight,
  ShieldCheck,
  Warning,
} from "@phosphor-icons/react/dist/ssr";
import {
  UniversalQuestionPlayer,
} from "./universal-question-player";
import { submitStudyAttempt } from "@/lib/api/study";
import { getSubjectTheme } from "@/lib/colors";

const STORAGE_PLAN_KEY = "gpat_learner_study_plan_v1";

interface StudyPlanItem {
  id: string;
  topicId: string;
  topicTitle: string;
  subjectId: string;
  estimatedMinutes: number;
  isCompleted: boolean;
  addedAt: string;
}

interface TopicDetailPanelProps {
  detail: TopicDetailResponse;
  masteryState?: "UNASSESSED" | "LEARNING" | "RETAINING" | "DEMONSTRATED_MASTERY" | "NEEDS_REPAIR";
  onBack?: () => void;
  onSelectTopic?: (topicId: string) => void;
}

type TabType = "overview" | "learn" | "practice" | "resources";

export function TopicDetailPanel({ detail, masteryState, onBack }: TopicDetailPanelProps) {
  const [activeTab, setActiveTab] = useState<TabType>("overview");
  const [isInPlan, setIsInPlan] = useState<boolean>(false);
  const [planFeedback, setPlanFeedback] = useState<string | null>(null);
  const [activeQuestionIndex, setActiveQuestionIndex] = useState<number | null>(null);
  const { topic } = detail;

  const subjectTheme = getSubjectTheme(topic.subject_id || topic.curriculum_subject_id);
  const isVerified = topic.verification_status === "VERIFIED";

  // Check if current topic is in study plan
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_PLAN_KEY);
      if (raw) {
        const items: StudyPlanItem[] = JSON.parse(raw);
        setIsInPlan(items.some((item) => item.topicId === topic.topic_id));
      } else {
        setIsInPlan(false);
      }
    } catch {
      setIsInPlan(false);
    }
  }, [topic.topic_id]);

  const handleToggleStudyPlan = () => {
    try {
      const raw = localStorage.getItem(STORAGE_PLAN_KEY);
      let items: StudyPlanItem[] = raw ? JSON.parse(raw) : [];

      if (isInPlan) {
        items = items.filter((item) => item.topicId !== topic.topic_id);
        localStorage.setItem(STORAGE_PLAN_KEY, JSON.stringify(items));
        setIsInPlan(false);
        setPlanFeedback("Removed from Today's Study Plan");
      } else {
        const newItem: StudyPlanItem = {
          id: `plan_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
          topicId: topic.topic_id,
          topicTitle: topic.name,
          subjectId: topic.subject_id || "pharmacology",
          estimatedMinutes: 20,
          isCompleted: false,
          addedAt: new Date().toISOString(),
        };
        items.push(newItem);
        localStorage.setItem(STORAGE_PLAN_KEY, JSON.stringify(items));
        setIsInPlan(true);
        setPlanFeedback("Added to Today's Study Plan");
      }

      setTimeout(() => setPlanFeedback(null), 3000);
    } catch {
      setPlanFeedback("Failed to update study plan");
    }
  };

  const getStatusBadge = () => {
    if (!masteryState || masteryState === "UNASSESSED") {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-slate-800/80 text-slate-300 border border-slate-700/60">
          Unassessed
        </span>
      );
    }
    if (masteryState === "NEEDS_REPAIR") {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-red-950/60 text-red-300 border border-red-500/40">
          <WarningCircle size={12} weight="bold" className="text-red-400" />
          Needs Repair
        </span>
      );
    }
    if (masteryState === "DEMONSTRATED_MASTERY") {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-emerald-950/60 text-emerald-300 border border-emerald-500/40">
          <Sparkle size={12} weight="fill" className="text-emerald-400" />
          Mastered
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-blue-950/60 text-blue-300 border border-blue-500/40">
        In Progress
      </span>
    );
  };

  const mediaList = detail.media || [];
  const sourcesList = detail.sources || [];

  return (
    <Card className="border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)]">
      <CardHeader className="space-y-3 pb-4 border-b border-[var(--color-border-subtle)]">
        {onBack && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onBack}
            className="md:hidden self-start gap-1.5 text-xs -ml-2 text-[var(--color-text-secondary)]"
          >
            <ArrowLeft size={14} weight="bold" />
            Back to Topics
          </Button>
        )}

        {/* 5-Tier Canonical Placement Badge */}
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap items-center gap-1.5 text-xs">
            <span
              className="font-mono font-semibold px-2 py-0.5 rounded"
              style={{
                backgroundColor: subjectTheme.badgeBg,
                borderColor: subjectTheme.badgeBorder,
                color: subjectTheme.badgeText,
                borderWidth: "1px",
              }}
            >
              {topic.exam_subject_name || subjectTheme.shortName}
            </span>
            <span className="text-[var(--color-text-tertiary)]">&rsaquo;</span>
            <span className="font-mono text-[var(--color-text-secondary)]">
              {topic.curriculum_name || topic.curriculum_subject_id}
            </span>
            {topic.unit_title && (
              <>
                <span className="text-[var(--color-text-tertiary)]">&rsaquo;</span>
                <span className="font-mono text-[var(--color-text-tertiary)] text-[11px]">
                  {topic.unit_number ? `Unit ${topic.unit_number}: ` : ""}{topic.unit_title}
                </span>
              </>
            )}
          </div>

          <div className="flex items-center gap-2">
            {getStatusBadge()}
            <Badge
              variant={isVerified ? "success" : "default"}
              className="text-[10px] font-mono uppercase"
            >
              {isVerified ? (
                <span className="flex items-center gap-1">
                  <CheckCircle size={12} weight="bold" />
                  Verified
                </span>
              ) : (
                <span className="flex items-center gap-1 text-[var(--color-status-warning)]">
                  <Warning size={11} weight="bold" />
                  Needs Mapping Review
                </span>
              )}
            </Badge>
          </div>
        </div>

        {/* Title & Primary Action */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pt-1">
          <CardTitle className="text-lg sm:text-xl font-bold text-[var(--color-text-primary)]">
            {topic.name}
          </CardTitle>

          <Button
            type="button"
            variant={isInPlan ? "primary" : "secondary"}
            size="sm"
            onClick={handleToggleStudyPlan}
            className={`shrink-0 text-xs h-8 gap-1.5 ${
              isInPlan
                ? "bg-[rgba(74,222,128,0.15)] text-[#86EFAC] border border-[rgba(74,222,128,0.3)] hover:bg-[rgba(74,222,128,0.25)]"
                : "border-[var(--color-border-subtle)] hover:bg-[var(--color-surface-raised)]"
            }`}
          >
            {isInPlan ? (
              <>
                <Check size={14} weight="bold" />
                <span>In Study Plan</span>
              </>
            ) : (
              <>
                <PlusCircle size={14} weight="bold" />
                <span>Add to Study Plan</span>
              </>
            )}
          </Button>
        </div>

        {planFeedback && (
          <div className="p-2 rounded bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-[11px] text-[var(--color-accent)] animate-enter">
            {planFeedback}
          </div>
        )}

        {/* Stable ID, Course Code, and Verification Notice */}
        <CardDescription className="text-xs text-[var(--color-text-secondary)] flex flex-wrap gap-x-4 gap-y-1 font-mono">
          <span>Topic ID: {topic.topic_id}</span>
          {topic.pci_course_code && <span>PCI Course: {topic.pci_course_code}</span>}
          {topic.semester_recommended && (
            <span>Semester: {topic.semester_recommended}</span>
          )}
        </CardDescription>

        {/* Editorial Notice Banner if Unverified */}
        {!isVerified && (
          <div className="p-2.5 rounded bg-amber-950/20 border border-amber-600/30 text-[11px] text-amber-300 flex items-start gap-2">
            <Warning size={14} weight="bold" className="shrink-0 mt-0.5 text-amber-400" />
            <span>
              <strong>Editorial Notice:</strong> This topic is derived from baseline syllabus trackers. Official NBEMS alignment and question-level mapping are currently in staging review.
            </span>
          </div>
        )}

        {/* Tab Selection */}
        <div className="flex items-center gap-1.5 pt-2 border-t border-[var(--color-border-subtle)] overflow-x-auto">
          <Button
            variant={activeTab === "overview" ? "primary" : "ghost"}
            size="sm"
            onClick={() => setActiveTab("overview")}
            className="gap-1.5 text-xs h-8"
          >
            <Target size={14} weight="bold" />
            <span>Overview</span>
          </Button>

          <Button
            variant={activeTab === "learn" ? "primary" : "ghost"}
            size="sm"
            onClick={() => setActiveTab("learn")}
            className="gap-1.5 text-xs h-8"
          >
            <FileText size={14} weight="bold" />
            <span>Learn ({detail.chunk_count + detail.objective_count})</span>
          </Button>

          <Button
            variant={activeTab === "practice" ? "primary" : "ghost"}
            size="sm"
            onClick={() => setActiveTab("practice")}
            className="gap-1.5 text-xs h-8"
          >
            <Question size={14} weight="bold" />
            <span>Practice ({detail.question_count})</span>
          </Button>

          <Button
            variant={activeTab === "resources" ? "primary" : "ghost"}
            size="sm"
            onClick={() => setActiveTab("resources")}
            className="gap-1.5 text-xs h-8"
          >
            <BookOpen size={14} weight="bold" />
            <span>Resources ({detail.flashcard_count + mediaList.length + sourcesList.length})</span>
          </Button>
        </div>
      </CardHeader>

      <CardContent className="pt-4">
        {/* ========================================================================= */}
        {/* TAB 1: OVERVIEW & STUDY ACTIONS                                           */}
        {/* ========================================================================= */}
        {activeTab === "overview" && (
          <div className="space-y-4">
            {/* Quick Action Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="p-3.5 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] flex flex-col justify-between space-y-2">
                <div>
                  <div className="flex items-center gap-2 text-xs font-semibold text-[var(--color-text-primary)]">
                    <RocketLaunch size={15} weight="bold" className="text-[var(--color-accent)]" />
                    <span>Daily Study Session</span>
                  </div>
                  <p className="text-[11px] text-[var(--color-text-secondary)] mt-1">
                    Start today&apos;s adaptive mission incorporating high-yield concepts and due recalls.
                  </p>
                </div>
                <Link href="/today" className="w-full">
                  <Button variant="primary" size="sm" className="w-full text-xs h-8 justify-between mt-1">
                    <span>Open Today Mission</span>
                    <ArrowRight size={13} weight="bold" />
                  </Button>
                </Link>
              </div>

              <div className="p-3.5 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] flex flex-col justify-between space-y-2">
                <div>
                  <div className="flex items-center gap-2 text-xs font-semibold text-[var(--color-text-primary)]">
                    <ArrowsCounterClockwise size={15} weight="bold" className="text-[#86EFAC]" />
                    <span>Spaced Review Queue</span>
                  </div>
                  <p className="text-[11px] text-[var(--color-text-secondary)] mt-1">
                    Review active recall flashcards scheduled via FSRS stability model.
                  </p>
                </div>
                <Link href="/review" className="w-full">
                  <Button variant="secondary" size="sm" className="w-full text-xs h-8 justify-between mt-1 border-[var(--color-border-subtle)]">
                    <span>Review Due Cards</span>
                    <ArrowRight size={13} weight="bold" />
                  </Button>
                </Link>
              </div>
            </div>

            {/* Topic Asset Inventory Breakdown */}
            <div className="p-3.5 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] space-y-2.5">
              <div className="text-xs font-semibold text-[var(--color-text-primary)]">
                Available Content Inventory
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
                <div className="p-2 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)]">
                  <span className="text-[10px] text-[var(--color-text-tertiary)] block">Text Excerpts</span>
                  <span className="text-sm font-bold text-[var(--color-text-primary)]">{detail.chunk_count}</span>
                </div>
                <div className="p-2 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)]">
                  <span className="text-[10px] text-[var(--color-text-tertiary)] block">Questions</span>
                  <span className="text-sm font-bold text-[var(--color-text-primary)]">{detail.question_count}</span>
                </div>
                <div className="p-2 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)]">
                  <span className="text-[10px] text-[var(--color-text-tertiary)] block">Objectives (LO)</span>
                  <span className="text-sm font-bold text-[var(--color-text-primary)]">{detail.objective_count}</span>
                </div>
                <div className="p-2 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)]">
                  <span className="text-[10px] text-[var(--color-text-tertiary)] block">Flashcards</span>
                  <span className="text-sm font-bold text-[var(--color-text-primary)]">{detail.flashcard_count}</span>
                </div>
              </div>
            </div>

            {/* Level 5 Learning Objectives Preview if available */}
            {detail.learning_objectives.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-semibold text-[var(--color-text-secondary)] font-mono uppercase">
                  Core Competencies &amp; Objectives
                </div>
                <div className="space-y-2">
                  {detail.learning_objectives.map((obj) => (
                    <div
                      key={obj.objective_id}
                      className="p-3 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-xs space-y-1.5"
                    >
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="font-mono text-[var(--color-text-tertiary)]">{obj.code || "LO"}</span>
                        {obj.bloom_level && (
                          <Badge variant="default" className="text-[10px] font-mono">
                            Bloom: {obj.bloom_level}
                          </Badge>
                        )}
                      </div>
                      <p className="text-[var(--color-text-primary)]">{obj.objective_statement}</p>
                      {obj.clinical_pearl && (
                        <div className="p-2 rounded bg-[rgba(96,165,250,0.08)] border border-[var(--color-accent)]/20 text-[11px] text-[var(--color-accent)]">
                          <strong>Clinical Pearl:</strong> {obj.clinical_pearl}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 2: LEARN (Textbook Excerpts, Notes & Detailed Objectives)              */}
        {/* ========================================================================= */}
        {activeTab === "learn" && (
          <div className="space-y-3">
            {detail.content_chunks.length === 0 && detail.learning_objectives.length === 0 ? (
              <div className="p-6 text-center text-xs text-[var(--color-text-tertiary)] border border-dashed border-[var(--color-border-subtle)] rounded-lg">
                No indexed textbook excerpts or learning objectives currently linked to this topic in the baseline knowledge graph.
              </div>
            ) : (
              <>
                {/* Reference Chunks */}
                {detail.content_chunks.map((chk) => (
                  <div
                    key={chk.chunk_id}
                    className="p-3.5 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between text-[11px] text-[var(--color-text-tertiary)] font-mono">
                      <span className="flex items-center gap-1.5">
                        <BookOpen size={13} weight="bold" className="text-[var(--color-accent)]" />
                        {chk.source_id}
                      </span>
                      {chk.page_or_range && <span>Page: {chk.page_or_range}</span>}
                    </div>
                    {chk.heading_path && (
                      <div className="font-semibold text-[var(--color-text-primary)]">
                        {chk.heading_path}
                      </div>
                    )}
                    <p className="text-[var(--color-text-secondary)] leading-relaxed whitespace-pre-line">
                      {chk.content}
                    </p>
                  </div>
                ))}

                {/* Learning Objectives as Reference */}
                {detail.learning_objectives.map((obj) => (
                  <div
                    key={obj.objective_id}
                    className="p-3.5 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between text-[11px] font-mono text-[var(--color-text-secondary)]">
                      <span>{obj.code || "Objective"}</span>
                      {obj.bloom_level && <Badge variant="default" className="text-[10px]">{obj.bloom_level}</Badge>}
                    </div>
                    <p className="text-[var(--color-text-primary)] leading-relaxed">{obj.objective_statement}</p>
                    {obj.key_formula_or_rule && (
                      <div className="p-2 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)] font-mono text-[11px] text-[var(--color-text-secondary)]">
                        <strong>Rule/Formula:</strong> {obj.key_formula_or_rule}
                      </div>
                    )}
                  </div>
                ))}
              </>
            )}
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 3: PRACTICE (Verified PYQs & Practice MCQs)                           */}
        {/* ========================================================================= */}
        {activeTab === "practice" && (
          <div className="space-y-4">
            {detail.questions.length === 0 ? (
              <div className="p-6 text-center text-xs text-[var(--color-text-tertiary)] border border-dashed border-[var(--color-border-subtle)] rounded-lg space-y-2">
                <p>No baseline questions currently linked to this topic identifier.</p>
                <Link href="/pyqs">
                  <Button variant="secondary" size="sm" className="text-xs h-7 border-[var(--color-border-subtle)]">
                    Browse All PYQs by Exam Year
                  </Button>
                </Link>
              </div>
            ) : activeQuestionIndex !== null && detail.questions[activeQuestionIndex] ? (
              /* Inline Universal Question Player Session */
              <div className="space-y-3">
                <UniversalQuestionPlayer
                  question={{
                    id: detail.questions[activeQuestionIndex].id,
                    concept_id: topic.topic_id,
                    concept_name: topic.name,
                    topic_name: topic.name,
                    question_text: detail.questions[activeQuestionIndex].question_text,
                    options: detail.questions[activeQuestionIndex].options || [],
                    difficulty: detail.questions[activeQuestionIndex].difficulty,
                    pyq_year: detail.questions[activeQuestionIndex].pyq_year,
                    cognitive_level: detail.questions[activeQuestionIndex].cognitive_level,
                    verification_status: detail.questions[activeQuestionIndex].verification_status,
                    media_url: detail.questions[activeQuestionIndex].media_url,
                    media_alt: detail.questions[activeQuestionIndex].media_alt,
                    media_caption: detail.questions[activeQuestionIndex].media_caption,
                    cue: detail.questions[activeQuestionIndex].cue,
                    explanation: detail.questions[activeQuestionIndex].explanation,
                    source_page: detail.questions[activeQuestionIndex].source_page,
                    distractor_reasons: detail.questions[activeQuestionIndex].distractor_reasons,
                    provenance: detail.questions[activeQuestionIndex].provenance,
                  }}
                  currentIndex={activeQuestionIndex}
                  totalQuestions={detail.questions.length}
                  sessionModeTag={`${topic.name} Drill`}
                  studentId="student_01"
                  localCorrectOption={detail.questions[activeQuestionIndex].correct_option}
                  onSubmitAnswer={async (qId, selectedOpt, responseTime, conf) => {
                    return await submitStudyAttempt({
                      student_id: "student_01",
                      question_id: qId,
                      selected_option: selectedOpt,
                      response_time_sec: responseTime,
                      confidence: conf,
                    });
                  }}
                  onPrevious={
                    activeQuestionIndex > 0
                      ? () => setActiveQuestionIndex(activeQuestionIndex - 1)
                      : undefined
                  }
                  onNext={
                    activeQuestionIndex < detail.questions.length - 1
                      ? () => setActiveQuestionIndex(activeQuestionIndex + 1)
                      : () => setActiveQuestionIndex(null)
                  }
                  isLast={activeQuestionIndex === detail.questions.length - 1}
                  onBackToList={() => setActiveQuestionIndex(null)}
                />
              </div>
            ) : (
              /* Question List View */
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs pb-1 border-b border-[var(--color-border-subtle)]">
                  <span className="font-semibold text-[var(--color-text-secondary)] font-mono uppercase">
                    Practice Items ({detail.questions.length})
                  </span>
                  <Button
                    size="sm"
                    variant="primary"
                    onClick={() => setActiveQuestionIndex(0)}
                    className="text-xs h-7 gap-1 font-mono"
                  >
                    <RocketLaunch size={13} weight="bold" />
                    Start Topic Drill
                  </Button>
                </div>

                {detail.questions.map((q, qIdx) => (
                  <div
                    key={q.id}
                    className="p-3.5 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] hover:border-[var(--color-border-focus)] transition-colors space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-[11px] text-[var(--color-accent)] font-semibold">
                        {q.pyq_year ? `GPAT ${q.pyq_year} PYQ` : `Practice Item ${qIdx + 1}`}
                      </span>
                      <div className="flex items-center gap-1.5">
                        {q.cognitive_level && (
                          <Badge variant="default" className="text-[10px] font-mono">
                            {q.cognitive_level}
                          </Badge>
                        )}
                        <Badge variant="default" className="text-[10px] font-mono">
                          {q.verification_status || "Baseline"}
                        </Badge>
                      </div>
                    </div>
                    <p className="font-medium text-[var(--color-text-primary)] leading-relaxed">
                      {q.question_text}
                    </p>
                    <div className="pt-2 flex items-center justify-between text-[11px] font-mono text-[var(--color-text-tertiary)] border-t border-[var(--color-border-subtle)]">
                      <span>QID: {q.id}</span>
                      <button
                        type="button"
                        onClick={() => setActiveQuestionIndex(qIdx)}
                        className="text-[var(--color-accent)] hover:underline font-semibold flex items-center gap-1"
                      >
                        Practice this question &rarr;
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 4: RESOURCES (Flashcards, Media Figures, and Canonical Sources)       */}
        {/* ========================================================================= */}
        {activeTab === "resources" && (
          <div className="space-y-4">
            {/* Scientific Figures & Chemical Structures */}
            {mediaList.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-semibold text-[var(--color-text-secondary)] font-mono uppercase flex items-center gap-1.5">
                  <ImageIcon size={14} weight="bold" className="text-[var(--color-accent)]" />
                  <span>Scientific Figures &amp; Chemical Structures ({mediaList.length})</span>
                </div>
                <div className="space-y-3">
                  {mediaList.map((m) => (
                    <div
                      key={m.media_id}
                      className="p-3.5 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] space-y-2 text-xs"
                    >
                      <div className="flex items-center justify-between text-[11px] font-mono text-[var(--color-text-tertiary)]">
                        <span className="text-[var(--color-accent)] font-semibold">{m.media_type}</span>
                        <span>Source: {m.source_id} {m.page_number ? `• Page ${m.page_number}` : ""}</span>
                      </div>
                      {m.caption && (
                        <div className="font-semibold text-[var(--color-text-primary)]">
                          {m.caption}
                        </div>
                      )}
                      {m.alt_text && (
                        <p className="text-[11px] text-[var(--color-text-secondary)] italic">
                          {m.alt_text}
                        </p>
                      )}
                      <div className="text-[10px] font-mono text-[var(--color-text-tertiary)]">
                        Path: {m.relative_file_path} • Rights: {m.rights_status || "FAIR_USE_EDUCATIONAL"}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Flashcards */}
            <div className="space-y-2">
              <div className="text-xs font-semibold text-[var(--color-text-secondary)] font-mono uppercase flex items-center gap-1.5">
                <Cards size={14} weight="bold" className="text-[#86EFAC]" />
                <span>Active Recall Flashcards ({detail.flashcard_count})</span>
              </div>
              {detail.flashcards.length === 0 ? (
                <div className="p-4 text-center text-xs text-[var(--color-text-tertiary)] border border-dashed border-[var(--color-border-subtle)] rounded-lg">
                  No active recall cards mapped for this topic.
                </div>
              ) : (
                detail.flashcards.map((fc) => (
                  <div
                    key={fc.card_id}
                    className="p-3.5 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] space-y-2 text-xs"
                  >
                    <div className="font-semibold text-[var(--color-text-primary)]">
                      Q: {fc.front}
                    </div>
                    <div className="text-[var(--color-status-success)] font-medium pt-1 border-t border-[var(--color-border-subtle)]">
                      A: {fc.back}
                    </div>
                    {fc.explanation && (
                      <p className="text-[11px] text-[var(--color-text-secondary)]">
                        {fc.explanation}
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>

            {/* Registered Canonical Sources */}
            {sourcesList.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-semibold text-[var(--color-text-secondary)] font-mono uppercase flex items-center gap-1.5">
                  <ShieldCheck size={14} weight="bold" className="text-[var(--color-accent)]" />
                  <span>Canonical Content Sources</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
                  {sourcesList.map((s) => (
                    <div
                      key={s.source_id}
                      className="p-2.5 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)] space-y-1"
                    >
                      <div className="font-semibold text-[var(--color-text-primary)] truncate">
                        {s.title}
                      </div>
                      <div className="text-[10px] text-[var(--color-text-tertiary)] flex justify-between">
                        <span>{s.source_id}</span>
                        <span className="uppercase">{s.authority_category}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
