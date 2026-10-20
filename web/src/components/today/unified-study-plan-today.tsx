"use client";

import React, { useState } from "react";
import {
  ListChecks,
  Plus,
  Trash,
  CheckCircle,
  Circle,
  Check,
  Clock,
  BookmarksSimple
} from "@phosphor-icons/react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StudyPlanItem } from "./study-planning-section";
import { StudiedActivityItem } from "./studied-today-section";

interface UnifiedStudyPlanTodayProps {
  planItems: StudyPlanItem[];
  onTogglePlanItem: (id: string) => void;
  onRemovePlanItem: (id: string) => void;
  onAddPlanItem: (topicTitle: string, subjectId: string, durationMin: number) => void;
  completedActivities: StudiedActivityItem[];
}

export function UnifiedStudyPlanToday({
  planItems,
  onTogglePlanItem,
  onRemovePlanItem,
  onAddPlanItem,
  completedActivities,
}: UnifiedStudyPlanTodayProps) {
  const [activeTab, setActiveTab] = useState<"studied" | "plan">("studied");
  const [isAdding, setIsAdding] = useState(false);
  const [topicName, setTopicName] = useState("");
  const [subjectId, setSubjectId] = useState("pharmacology");
  const [duration, setDuration] = useState(15);

  const handleAdd = () => {
    if (!topicName.trim()) return;
    onAddPlanItem(topicName.trim(), subjectId, duration);
    setTopicName("");
    setIsAdding(false);
  };

  return (
    <Card className="border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] relative overflow-hidden flex flex-col justify-between shadow-sm">
      <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono tracking-wider uppercase text-[var(--color-accent)] font-semibold flex items-center gap-1.5">
                <ListChecks size={15} weight="bold" />
                Today&apos;s Plan
              </span>
            </div>
            <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">
              Review completed study activity and manage your queued topics.
            </p>
          </div>

          {/* Segmented Controller */}
          <div className="flex items-center gap-1.5 p-1 bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] rounded-lg self-start sm:self-auto">
            <button
              type="button"
              onClick={() => setActiveTab("studied")}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-all ${
                activeTab === "studied"
                  ? "bg-[var(--color-surface-base)] text-[var(--color-text-primary)] font-semibold shadow-xs"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              <Check size={12} weight="bold" className="text-emerald-400" />
              <span>Studied ({completedActivities.length})</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("plan")}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-all ${
                activeTab === "plan"
                  ? "bg-[var(--color-surface-base)] text-[var(--color-text-primary)] font-semibold shadow-xs"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              <Plus size={12} weight="bold" className="text-blue-400" />
              <span>Plan next ({planItems.length})</span>
            </button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-3">
        {/* STUDIED TAB */}
        {activeTab === "studied" && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-[var(--color-text-secondary)] border-b border-[var(--color-border-subtle)] pb-2">
              <span>Verified learning events logged today</span>
              <span className="font-mono text-[11px] text-[var(--color-text-tertiary)]">
                {completedActivities.length} items logged
              </span>
            </div>

            {completedActivities.length === 0 ? (
              <div className="text-center py-8 text-xs text-[var(--color-text-secondary)] space-y-2">
                <p>No learning activity recorded yet today.</p>
                <p className="text-[11px] text-[var(--color-text-tertiary)]">
                  Completed daily mission tasks or review questions will appear here automatically.
                </p>
              </div>
            ) : (
              <ul className="space-y-2" aria-label="Completed activities today">
                {completedActivities.map((act) => {
                  const formattedTime = new Date(act.timestamp).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  });

                  return (
                    <li
                      key={act.id}
                      className="flex items-center justify-between p-2.5 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/30 text-xs"
                    >
                      <div className="flex items-center gap-2.5 min-w-0 pr-2">
                        <CheckCircle size={16} weight="fill" className="text-emerald-400 shrink-0" />
                        <div className="min-w-0">
                          <span className="text-[var(--color-text-primary)] font-medium block truncate">
                            {act.title}
                          </span>
                          <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">
                            {formattedTime} {act.timeSpentSec ? `• ${act.timeSpentSec}s response` : ""}
                          </span>
                        </div>
                      </div>

                      <Badge variant="default" className="text-[10px] font-mono py-0 shrink-0">
                        Recorded
                      </Badge>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        )}

        {/* PLAN NEXT TAB */}
        {activeTab === "plan" && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-[var(--color-text-secondary)] border-b border-[var(--color-border-subtle)] pb-2">
              <span className="flex items-center gap-1.5">
                <BookmarksSimple size={14} />
                <span>Personal study queue (saved on this device)</span>
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsAdding(!isAdding)}
                className="h-7 text-xs gap-1 font-mono text-[var(--color-accent)] hover:text-white"
              >
                <Plus size={12} weight="bold" />
                <span>Add topic</span>
              </Button>
            </div>

            {/* Custom Item Form */}
            {isAdding && (
              <div className="p-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/50 space-y-2.5 animate-enter">
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-mono text-[var(--color-text-tertiary)]">
                    Topic title
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Sterilization methods & autoclaving cycles"
                    value={topicName}
                    onChange={(e) => setTopicName(e.target.value)}
                    className="w-full text-xs px-2.5 py-1.5 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)] text-[var(--color-text-primary)] focus:border-[var(--color-accent)] focus:outline-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div className="space-y-1">
                    <label className="text-[10px] uppercase font-mono text-[var(--color-text-tertiary)]">
                      Subject
                    </label>
                    <select
                      value={subjectId}
                      onChange={(e) => setSubjectId(e.target.value)}
                      className="w-full text-xs px-2 py-1.5 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)] text-[var(--color-text-primary)] focus:border-[var(--color-accent)] focus:outline-none"
                    >
                      <option value="pharmacology">Pharmacology</option>
                      <option value="pharmaceutics">Pharmaceutics</option>
                      <option value="pharmaceutical_chemistry">Pharm Chemistry</option>
                      <option value="pharmacognosy">Pharmacognosy</option>
                      <option value="other_subjects">Other Subjects</option>
                    </select>
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] uppercase font-mono text-[var(--color-text-tertiary)]">
                      Target duration
                    </label>
                    <select
                      value={duration}
                      onChange={(e) => setDuration(parseInt(e.target.value, 10))}
                      className="w-full text-xs px-2 py-1.5 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)] text-[var(--color-text-primary)] focus:border-[var(--color-accent)] focus:outline-none font-mono"
                    >
                      <option value={10}>10 min</option>
                      <option value={15}>15 min</option>
                      <option value={20}>20 min</option>
                      <option value={30}>30 min</option>
                    </select>
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setIsAdding(false);
                      setTopicName("");
                    }}
                    className="h-7 text-xs"
                  >
                    Cancel
                  </Button>
                  <Button size="sm" onClick={handleAdd} className="h-7 text-xs font-semibold">
                    Add to Queue
                  </Button>
                </div>
              </div>
            )}

            {/* List of planned items */}
            {planItems.length === 0 ? (
              <div className="text-center py-7 text-xs text-[var(--color-text-secondary)]">
                No topics queued in your study plan. Click &quot;Add topic&quot; above to organize your session.
              </div>
            ) : (
              <ul className="space-y-2" aria-label="Queued study items">
                {planItems.map((item) => (
                  <li
                    key={item.id}
                    className={`flex items-center justify-between p-2.5 rounded-lg border transition-all text-xs ${
                      item.isCompleted
                        ? "border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/20 opacity-60"
                        : "border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/30 hover:border-[var(--color-border-focus)]"
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0 pr-2">
                      <button
                        type="button"
                        onClick={() => onTogglePlanItem(item.id)}
                        className="text-[var(--color-text-tertiary)] hover:text-emerald-400 transition-colors shrink-0"
                        title={item.isCompleted ? "Mark incomplete" : "Mark completed"}
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
                        <div className="flex items-center gap-2 text-[10px] font-mono text-[var(--color-text-tertiary)]">
                          <span className="capitalize">{item.subjectId.replace(/_/g, " ")}</span>
                          <span>•</span>
                          <span className="flex items-center gap-0.5">
                            <Clock size={10} />
                            ~{item.estimatedMinutes}m
                          </span>
                        </div>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => onRemovePlanItem(item.id)}
                      className="text-[var(--color-text-tertiary)] hover:text-[var(--color-status-error)] transition-colors p-1"
                      title="Remove from queue"
                    >
                      <Trash size={14} />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
