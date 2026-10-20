"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  ListChecks,
  Plus,
  Trash,
  CheckCircle,
  Circle,
  Clock,
  BookmarksSimple,
  ShieldCheck,
} from "@phosphor-icons/react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getSubjectTheme } from "@/lib/colors";

export interface StudyPlanItem {
  id: string;
  topicId: string;
  topicTitle: string;
  subjectId: string;
  estimatedMinutes: number;
  isCompleted: boolean;
  addedAt: string;
}

const STORAGE_PLAN_KEY = "gpat_learner_study_plan_v1";

export function StudyPlanningSection() {
  const [planItems, setPlanItems] = useState<StudyPlanItem[]>([]);
  const [isAddingCustom, setIsAddingCustom] = useState(false);
  const [customTopic, setCustomTopic] = useState("");
  const [customSubject, setCustomSubject] = useState("pharmacology");
  const [customMins, setCustomMins] = useState(15);

  // Load from local storage
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_PLAN_KEY);
      if (raw) {
        setPlanItems(JSON.parse(raw));
      } else {
        // Curated evidence-grounded initial draft (Optionally empty or starter)
        const starter: StudyPlanItem[] = [
          {
            id: "plan_init_01",
            topicId: "pharmacology__ans__pd_antagonism",
            topicTitle: "Pharmacology: Receptor Antagonism & Competitive Kinetics",
            subjectId: "pharmacology",
            estimatedMinutes: 15,
            isCompleted: false,
            addedAt: new Date().toISOString(),
          },
          {
            id: "plan_init_02",
            topicId: "pharmaceutics__pharmaceutics__pharmaceuticals_and_dosage_forms",
            topicTitle: "Pharmaceutics: Dissolution Testing & BCS Classification",
            subjectId: "pharmaceutics",
            estimatedMinutes: 20,
            isCompleted: false,
            addedAt: new Date().toISOString(),
          },
        ];
        setPlanItems(starter);
        localStorage.setItem(STORAGE_PLAN_KEY, JSON.stringify(starter));
      }
    } catch {
      // fallback
    }
  }, []);

  const saveItems = (items: StudyPlanItem[]) => {
    setPlanItems(items);
    try {
      localStorage.setItem(STORAGE_PLAN_KEY, JSON.stringify(items));
    } catch {
      // storage quota
    }
  };

  const toggleComplete = (id: string) => {
    const updated = planItems.map((item) =>
      item.id === id ? { ...item, isCompleted: !item.isCompleted } : item
    );
    saveItems(updated);
  };

  const removeItem = (id: string) => {
    const updated = planItems.filter((item) => item.id !== id);
    saveItems(updated);
  };

  const handleAdd = () => {
    if (!customTopic.trim()) return;
    const newItem: StudyPlanItem = {
      id: `plan_${Date.now()}`,
      topicId: customTopic.trim().toLowerCase().replace(/\s+/g, "_"),
      topicTitle: customTopic.trim(),
      subjectId: customSubject,
      estimatedMinutes: customMins,
      isCompleted: false,
      addedAt: new Date().toISOString(),
    };
    saveItems([...planItems, newItem]);
    setCustomTopic("");
    setIsAddingCustom(false);
  };

  const totalPlannedMins = planItems.reduce((acc, curr) => acc + curr.estimatedMinutes, 0);
  const completedCount = planItems.filter((i) => i.isCompleted).length;

  return (
    <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] flex flex-col justify-between">
      <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ListChecks size={16} weight="bold" className="text-[var(--color-accent)]" />
            <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)]">
              Plan to Study
            </CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono text-[var(--color-text-tertiary)] flex items-center gap-1">
              <ShieldCheck size={12} weight="bold" /> Local Draft
            </span>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setIsAddingCustom(!isAddingCustom)}
              className="h-7 text-xs px-2 gap-1 text-[var(--color-accent)]"
            >
              <Plus size={13} weight="bold" /> Add Topic
            </Button>
          </div>
        </div>
        <p className="text-xs text-[var(--color-text-secondary)]">
          Queue topics for upcoming sessions. Selecting or planning topics never modifies your official study records until lessons and attempts are completed.
        </p>
      </CardHeader>

      <CardContent className="space-y-3 pt-3">
        {isAddingCustom && (
          <div className="p-3 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] space-y-2.5 animate-enter">
            <div>
              <label className="text-[10px] uppercase font-mono text-[var(--color-text-tertiary)] block mb-1">
                Topic Name
              </label>
              <input
                type="text"
                placeholder="e.g. Bioavailability & First-pass Metabolism"
                value={customTopic}
                onChange={(e) => setCustomTopic(e.target.value)}
                className="w-full text-xs px-2.5 py-1.5 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)] text-[var(--color-text-primary)] focus:border-[var(--color-accent)] focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <label className="text-[10px] uppercase font-mono text-[var(--color-text-tertiary)] block mb-1">
                  Subject
                </label>
                <select
                  value={customSubject}
                  onChange={(e) => setCustomSubject(e.target.value)}
                  className="w-full text-xs px-2 py-1.5 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)] text-[var(--color-text-primary)] focus:border-[var(--color-accent)] focus:outline-none font-mono"
                >
                  <option value="pharmacology">Pharmacology</option>
                  <option value="pharmaceutics">Pharmaceutics</option>
                  <option value="pharmaceutical_chemistry">Pharm Chemistry</option>
                  <option value="pharmacognosy">Pharmacognosy</option>
                  <option value="other_subjects">Other B.Pharm</option>
                </select>
              </div>

              <div>
                <label className="text-[10px] uppercase font-mono text-[var(--color-text-tertiary)] block mb-1">
                  Est. Minutes
                </label>
                <input
                  type="number"
                  min={5}
                  max={60}
                  value={customMins}
                  onChange={(e) => setCustomMins(parseInt(e.target.value, 10) || 15)}
                  className="w-full text-xs px-2 py-1.5 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)] text-[var(--color-text-primary)] focus:border-[var(--color-accent)] focus:outline-none font-mono"
                />
              </div>
            </div>

            <div className="flex items-center gap-2 pt-1">
              <Button size="sm" onClick={handleAdd} className="h-7 text-xs px-2.5">
                Add to Plan
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setIsAddingCustom(false)}
                className="h-7 text-xs px-2 text-[var(--color-text-secondary)]"
              >
                Cancel
              </Button>
            </div>
          </div>
        )}

        {planItems.length === 0 ? (
          <div className="text-center py-6 text-xs text-[var(--color-text-tertiary)] space-y-1">
            <BookmarksSimple size={24} className="mx-auto text-[var(--color-text-tertiary)]" />
            <p>No upcoming study topics planned yet.</p>
            <p className="text-[11px]">Browse the Syllabus Explorer below to queue topics.</p>
          </div>
        ) : (
          <ul className="space-y-2" aria-label="Planned study topics">
            {planItems.map((item) => {
              const theme = getSubjectTheme(item.subjectId);
              return (
                <li
                  key={item.id}
                  className="flex items-center justify-between p-2.5 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/40 hover:bg-[var(--color-surface-raised)] transition-colors group"
                >
                  <div className="flex items-center gap-2.5 min-w-0 pr-2">
                    <button
                      type="button"
                      onClick={() => toggleComplete(item.id)}
                      className="text-[var(--color-text-tertiary)] hover:text-[var(--color-status-success)] transition-colors shrink-0"
                      aria-label={`Mark ${item.topicTitle} as completed in plan`}
                    >
                      {item.isCompleted ? (
                        <CheckCircle size={18} weight="fill" className="text-[var(--color-status-success)]" />
                      ) : (
                        <Circle size={18} />
                      )}
                    </button>

                    <div className="min-w-0">
                      <span
                        className={`text-xs block truncate ${
                          item.isCompleted
                            ? "line-through text-[var(--color-text-tertiary)]"
                            : "text-[var(--color-text-primary)] font-medium"
                        }`}
                      >
                        {item.topicTitle}
                      </span>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span
                          className="text-[10px] font-mono font-semibold"
                          style={{ color: theme.accentText }}
                        >
                          {theme.shortName}
                        </span>
                        <span className="text-[10px] font-mono text-[var(--color-text-tertiary)] flex items-center gap-1">
                          <Clock size={11} /> {item.estimatedMinutes}m
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-1 shrink-0">
                    <Link href={`/study?topic=${encodeURIComponent(item.topicId)}`}>
                      <Button variant="ghost" size="sm" className="h-7 text-[11px] px-2 text-[var(--color-text-secondary)]">
                        Study
                      </Button>
                    </Link>
                    <button
                      type="button"
                      onClick={() => removeItem(item.id)}
                      className="text-[var(--color-text-tertiary)] hover:text-[var(--color-status-error)] transition-colors p-1"
                      title="Remove from plan"
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

        <div className="flex items-center justify-between pt-2 border-t border-[var(--color-border-subtle)] text-[11px] font-mono text-[var(--color-text-tertiary)]">
          <span>
            {completedCount} of {planItems.length} completed
          </span>
          <span>Total Planned: {totalPlannedMins} mins</span>
        </div>
      </CardContent>
    </Card>
  );
}
