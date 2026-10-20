"use client";

import React, { useState } from "react";
import {
  ListChecks,
  Plus,
  Trash,
  CheckCircle,
  Circle,
  Clock,
  BookmarksSimple,
  MagnifyingGlass,
  ArrowUp,
  ArrowDown,
  Info,
  CalendarPlus,
} from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getSubjectTheme, ExamSubjectId } from "@/lib/colors";
import { SyllabusExamGroup, SyllabusTopicSummary } from "@/lib/api/types";

export interface StudyPlanItem {
  id: string;
  topicId: string;
  topicTitle: string;
  subjectId: string;
  estimatedMinutes: number;
  isCompleted: boolean;
  addedAt: string;
}

interface MyStudyPlanSectionProps {
  planItems: StudyPlanItem[];
  onTogglePlanItem: (id: string) => void;
  onRemovePlanItem: (id: string) => void;
  onAddPlanItem: (topicTitle: string, subjectId: string, durationMin: number, topicId?: string) => void;
  onReorderPlanItems?: (reordered: StudyPlanItem[]) => void;
  examGroups?: SyllabusExamGroup[];
}

export function MyStudyPlanSection({
  planItems,
  onTogglePlanItem,
  onRemovePlanItem,
  onAddPlanItem,
  onReorderPlanItems,
  examGroups = [],
}: MyStudyPlanSectionProps) {
  const [isAdding, setIsAdding] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSubject, setSelectedSubject] = useState<ExamSubjectId>("pharmacology");
  const [selectedTopic, setSelectedTopic] = useState<{ id: string; title: string } | null>(null);
  const [customTitle, setCustomTitle] = useState("");
  const [durationMin, setDurationMin] = useState(15);
  const [filterMode, setFilterMode] = useState<"all" | "planned" | "completed">("all");

  // Flatten syllabus topics for search and selection
  const allSyllabusTopics: Array<{ id: string; title: string; subjectId: ExamSubjectId }> = React.useMemo(() => {
    const list: Array<{ id: string; title: string; subjectId: ExamSubjectId }> = [];
    examGroups.forEach((group) => {
      const subjId = group.exam_subject_id as ExamSubjectId;
      group.curriculum_subjects?.forEach((curr) => {
        curr.topics?.forEach((t: SyllabusTopicSummary) => {
          list.push({
            id: t.topic_id,
            title: t.name,
            subjectId: subjId,
          });
        });
      });
    });
    return list;
  }, [examGroups]);

  // Filtered topics based on search query
  const searchResults = React.useMemo(() => {
    if (!searchQuery.trim()) return [];
    const q = searchQuery.toLowerCase();
    return allSyllabusTopics
      .filter((t) => t.title.toLowerCase().includes(q))
      .slice(0, 6);
  }, [allSyllabusTopics, searchQuery]);

  const handleSelectSearchResult = (topic: { id: string; title: string; subjectId: ExamSubjectId }) => {
    setSelectedTopic({ id: topic.id, title: topic.title });
    setSelectedSubject(topic.subjectId);
    setCustomTitle(topic.title);
    setSearchQuery("");
  };

  const handleAddSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const title = customTitle.trim() || selectedTopic?.title || "";
    if (!title) return;

    onAddPlanItem(title, selectedSubject, durationMin, selectedTopic?.id);

    // Reset form
    setCustomTitle("");
    setSelectedTopic(null);
    setSearchQuery("");
    setIsAdding(false);
  };

  const handleMoveUp = (index: number) => {
    if (index <= 0 || !onReorderPlanItems) return;
    const reordered = [...planItems];
    const temp = reordered[index - 1];
    reordered[index - 1] = reordered[index];
    reordered[index] = temp;
    onReorderPlanItems(reordered);
  };

  const handleMoveDown = (index: number) => {
    if (index >= planItems.length - 1 || !onReorderPlanItems) return;
    const reordered = [...planItems];
    const temp = reordered[index + 1];
    reordered[index + 1] = reordered[index];
    reordered[index] = temp;
    onReorderPlanItems(reordered);
  };

  // Filtered display list
  const displayedItems = planItems.filter((item) => {
    if (filterMode === "planned") return !item.isCompleted;
    if (filterMode === "completed") return item.isCompleted;
    return true;
  });

  const completedCount = planItems.filter((i) => i.isCompleted).length;
  const plannedCount = planItems.filter((i) => !i.isCompleted).length;
  const totalPlannedMinutes = planItems
    .filter((i) => !i.isCompleted)
    .reduce((acc, curr) => acc + (curr.estimatedMinutes || 15), 0);

  return (
    <section aria-labelledby="my-study-plan-heading" className="space-y-3">
      <div className="rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] shadow-2xs overflow-hidden">
        <div className="p-4 sm:p-5 pb-3 border-b border-[var(--color-border-subtle)]">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <div className="h-6 w-6 rounded-md bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                  <ListChecks size={15} weight="bold" />
                </div>
                <h2
                  id="my-study-plan-heading"
                  className="text-base sm:text-lg font-bold tracking-tight text-[var(--color-text-primary)]"
                >
                  My Study Plan
                </h2>
                <Badge variant="default" className="text-[10px] font-mono py-0 px-1.5">
                  Learner Queued
                </Badge>
              </div>
              <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">
                Organize your personal study queue. Recommendations suggest what the system predicts; you decide what to study.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="primary"
                onClick={() => setIsAdding(!isAdding)}
                className="interactive-cta h-8 text-xs px-3 gap-1.5 font-semibold"
                aria-expanded={isAdding}
              >
                <Plus size={13} weight="bold" />
                <span>Add a topic</span>
              </Button>
            </div>
          </div>

          {/* Quick status counters and filter chips */}
          {planItems.length > 0 && (
            <div className="flex flex-wrap items-center justify-between gap-2 pt-2 mt-1 border-t border-[var(--color-border-subtle)] text-[11px]">
              <div className="flex items-center gap-1.5 font-mono text-[var(--color-text-secondary)]">
                <span className="font-semibold text-[var(--color-text-primary)]">{plannedCount}</span> pending
                <span>•</span>
                <span className="font-semibold text-emerald-400">{completedCount}</span> completed
                <span>•</span>
                <span className="text-[var(--color-text-tertiary)] flex items-center gap-0.5">
                  <Clock size={11} /> ~{totalPlannedMinutes}m total
                </span>
              </div>

              {/* Segmented Filter */}
              <div className="flex items-center gap-1 bg-[var(--color-surface-raised)] p-0.5 rounded-md border border-[var(--color-border-subtle)] font-medium">
                <button
                  type="button"
                  onClick={() => setFilterMode("all")}
                  className={`px-2 py-0.5 rounded text-[10px] transition-colors ${
                    filterMode === "all"
                      ? "bg-[var(--color-surface-base)] text-[var(--color-text-primary)] font-semibold shadow-xs"
                      : "text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)]"
                  }`}
                >
                  All ({planItems.length})
                </button>
                <button
                  type="button"
                  onClick={() => setFilterMode("planned")}
                  className={`px-2 py-0.5 rounded text-[10px] transition-colors ${
                    filterMode === "planned"
                      ? "bg-[var(--color-surface-base)] text-[var(--color-text-primary)] font-semibold shadow-xs"
                      : "text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)]"
                  }`}
                >
                  Pending ({plannedCount})
                </button>
                <button
                  type="button"
                  onClick={() => setFilterMode("completed")}
                  className={`px-2 py-0.5 rounded text-[10px] transition-colors ${
                    filterMode === "completed"
                      ? "bg-[var(--color-surface-base)] text-[var(--color-text-primary)] font-semibold shadow-xs"
                      : "text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)]"
                  }`}
                >
                  Done ({completedCount})
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="p-4 sm:p-5 pt-3 space-y-3">
          {/* Add a topic drawer / form */}
          {isAdding && (
            <div className="p-3.5 rounded-xl border border-emerald-500/20 bg-[var(--color-surface-raised)]/60 space-y-3 animate-enter">
              <div className="flex items-center justify-between pb-1 border-b border-[var(--color-border-subtle)]">
                <span className="text-xs font-semibold text-[var(--color-text-primary)] flex items-center gap-1.5">
                  <CalendarPlus size={14} className="text-emerald-400" />
                  Plan a New Study Session
                </span>
                <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">
                  Persists on this device
                </span>
              </div>

              {/* Taxonomy Search */}
              <div className="space-y-1">
                <label className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-text-tertiary)] block">
                  Search Syllabus or Enter Topic
                </label>
                <div className="relative">
                  <MagnifyingGlass
                    size={14}
                    className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]"
                  />
                  <input
                    type="text"
                    placeholder="Search e.g. Bioavailability, Receptors, Autoclaving..."
                    value={searchQuery || customTitle}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      setCustomTitle(e.target.value);
                      if (selectedTopic) setSelectedTopic(null);
                    }}
                    className="w-full text-xs pl-8 pr-2.5 py-1.5 rounded-lg bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)] text-[var(--color-text-primary)] placeholder-[var(--color-text-tertiary)] focus:border-emerald-500 focus:outline-none"
                  />
                </div>

                {/* Instant Taxonomy Search Suggestions */}
                {searchResults.length > 0 && (
                  <div className="p-1 rounded-lg bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)] shadow-md space-y-0.5 mt-1">
                    <span className="text-[9px] font-mono text-[var(--color-text-tertiary)] px-2 py-0.5 block">
                      Matching syllabus topics:
                    </span>
                    {searchResults.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => handleSelectSearchResult(item)}
                        className="w-full text-left px-2 py-1 rounded text-xs hover:bg-[var(--color-surface-raised)] flex items-center justify-between transition-colors"
                      >
                        <span className="truncate text-[var(--color-text-primary)]">{item.title}</span>
                        <span className="text-[10px] font-mono capitalize text-[var(--color-text-tertiary)] shrink-0 ml-2">
                          {item.subjectId.replace(/_/g, " ")}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Subject & Planned Duration row */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div className="space-y-1">
                  <label className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-text-tertiary)] block">
                    Subject Classification
                  </label>
                  <select
                    value={selectedSubject}
                    onChange={(e) => setSelectedSubject(e.target.value as ExamSubjectId)}
                    className="w-full text-xs px-2.5 py-1.5 rounded-lg bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)] text-[var(--color-text-primary)] focus:border-emerald-500 focus:outline-none font-sans"
                  >
                    <option value="pharmacology">Pharmacology &amp; Allied Subjects</option>
                    <option value="pharmaceutics">Pharmaceutics &amp; Formulation</option>
                    <option value="pharmaceutical_chemistry">Pharmaceutical Chemistry</option>
                    <option value="pharmacognosy">Pharmacognosy &amp; Phytochemistry</option>
                    <option value="other_subjects">Biotechnology &amp; Allied</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-text-tertiary)] block">
                    Planned Session Duration
                  </label>
                  <div className="flex items-center gap-2">
                    {[10, 15, 20, 30].map((mins) => (
                      <button
                        key={mins}
                        type="button"
                        onClick={() => setDurationMin(mins)}
                        className={`flex-1 py-1.5 text-xs rounded-lg font-mono font-medium border transition-colors ${
                          durationMin === mins
                            ? "bg-emerald-500/15 border-emerald-500/40 text-emerald-400 font-bold"
                            : "bg-[var(--color-surface-base)] border-[var(--color-border-subtle)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
                        }`}
                      >
                        {mins}m
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-2 pt-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setIsAdding(false);
                    setCustomTitle("");
                    setSelectedTopic(null);
                    setSearchQuery("");
                  }}
                  className="h-7 text-xs"
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  variant="primary"
                  onClick={() => handleAddSubmit()}
                  disabled={!customTitle.trim()}
                  className="h-7 text-xs font-semibold px-3"
                >
                  Add to My Plan
                </Button>
              </div>
            </div>
          )}

          {/* Empty State */}
          {planItems.length === 0 ? (
            <div className="text-center py-8 px-4 rounded-xl border border-dashed border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/20 space-y-2.5">
              <div className="h-10 w-10 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto">
                <BookmarksSimple size={20} weight="duotone" />
              </div>
              <div className="space-y-1 max-w-sm mx-auto">
                <p className="text-xs font-medium text-[var(--color-text-primary)]">
                  Your plan starts here. Add a topic you want to study next.
                </p>
                <p className="text-[11px] text-[var(--color-text-secondary)]">
                  Planning gives structure to your day. Queued items remain saved on this device.
                </p>
              </div>
              <Button
                size="sm"
                variant="secondary"
                onClick={() => setIsAdding(true)}
                className="h-7 text-xs gap-1.5 font-medium"
              >
                <Plus size={12} weight="bold" />
                <span>Add a topic</span>
              </Button>
            </div>
          ) : displayedItems.length === 0 ? (
            <div className="text-center py-6 text-xs text-[var(--color-text-tertiary)]">
              No items match the selected filter ({filterMode}).
            </div>
          ) : (
            <ul className="space-y-2" aria-label="Learner study plan list">
              {displayedItems.map((item) => {
                const theme = getSubjectTheme(item.subjectId as ExamSubjectId);
                const originalIndex = planItems.findIndex((p) => p.id === item.id);

                return (
                  <li
                    key={item.id}
                    className={`interactive-card flex items-center justify-between p-2.5 sm:p-3 rounded-xl border text-xs group ${
                      item.isCompleted
                        ? "border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/20 opacity-60"
                        : "border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/40 hover:border-emerald-500/40 shadow-2xs"
                    }`}
                  >
                    {/* Left: Completion toggle + Title + Subject pill */}
                    <div className="flex items-center gap-2.5 min-w-0 pr-2">
                      <button
                        type="button"
                        onClick={() => onTogglePlanItem(item.id)}
                        className="text-[var(--color-text-tertiary)] hover:text-emerald-400 transition-colors shrink-0"
                        title={item.isCompleted ? "Mark incomplete" : "Mark as completed"}
                        aria-label={`Mark ${item.topicTitle} as ${item.isCompleted ? "incomplete" : "completed"}`}
                      >
                        {item.isCompleted ? (
                          <CheckCircle size={18} weight="fill" className="text-emerald-400" />
                        ) : (
                          <Circle size={18} weight="regular" />
                        )}
                      </button>

                      <div className="min-w-0">
                        <span
                          className={`font-medium block truncate ${
                            item.isCompleted
                              ? "line-through text-[var(--color-text-tertiary)]"
                              : "text-[var(--color-text-primary)]"
                          }`}
                        >
                          {item.topicTitle}
                        </span>

                        <div className="flex items-center gap-2 text-[10px] font-mono text-[var(--color-text-tertiary)] mt-0.5">
                          <span
                            className="font-semibold"
                            style={{ color: theme.accentText }}
                          >
                            {theme.shortName}
                          </span>
                          <span>•</span>
                          <span className="flex items-center gap-0.5">
                            <Clock size={10} />
                            ~{item.estimatedMinutes || 15}m
                          </span>
                          {item.isCompleted && (
                            <>
                              <span>•</span>
                              <span className="text-emerald-400 font-semibold">Done</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Right: Reorder + Delete actions */}
                    <div className="flex items-center gap-1 shrink-0">
                      {onReorderPlanItems && filterMode === "all" && (
                        <div className="flex items-center opacity-60 group-hover:opacity-100 transition-opacity">
                          <button
                            type="button"
                            onClick={() => handleMoveUp(originalIndex)}
                            disabled={originalIndex === 0}
                            className="p-1 rounded text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] disabled:opacity-20 transition-colors"
                            title="Move item up"
                            aria-label="Move item up"
                          >
                            <ArrowUp size={12} weight="bold" />
                          </button>
                          <button
                            type="button"
                            onClick={() => handleMoveDown(originalIndex)}
                            disabled={originalIndex === planItems.length - 1}
                            className="p-1 rounded text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] disabled:opacity-20 transition-colors"
                            title="Move item down"
                            aria-label="Move item down"
                          >
                            <ArrowDown size={12} weight="bold" />
                          </button>
                        </div>
                      )}

                      <button
                        type="button"
                        onClick={() => onRemovePlanItem(item.id)}
                        className="p-1 rounded text-[var(--color-text-tertiary)] hover:text-rose-400 transition-colors opacity-60 group-hover:opacity-100 ml-1"
                        title="Remove topic from plan"
                        aria-label={`Remove ${item.topicTitle} from plan`}
                      >
                        <Trash size={14} />
                      </button>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}

          {/* Sync & Integrity Transparency Notice */}
          <div className="flex items-center justify-between pt-2 border-t border-[var(--color-border-subtle)] text-[10px] font-mono text-[var(--color-text-tertiary)]">
            <span className="flex items-center gap-1">
              <Info size={12} />
              Saved locally on this device. Planning an item does not alter official mastery records.
            </span>
            <span className="hidden sm:inline">Storage: gpat_learner_study_plan_v1</span>
          </div>
        </div>
      </div>
    </section>
  );
}
