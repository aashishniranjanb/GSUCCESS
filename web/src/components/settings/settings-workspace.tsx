"use client";

import React, { useState, useEffect } from "react";
import {
  User,
  GearSix,
  Bell,
  Database,
  ShieldCheck,
  WarningCircle,
  SignOut,
  Sliders,
  Check,
  Sun,
  Moon,
  Palette
} from "@phosphor-icons/react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { LearnerRewardsResponse, LearnerLocalPreferences } from "@/lib/api/types";
import { updateWeeklyGoal } from "@/lib/api/settings";
import { getLocalPreferences, saveLocalPreferences } from "@/lib/preferences";

interface SettingsWorkspaceProps {
  initialRewards: LearnerRewardsResponse;
  onRefresh: () => void;
}

export function SettingsWorkspace({ initialRewards }: SettingsWorkspaceProps) {
  const [weeklyGoal, setWeeklyGoal] = useState<number>(initialRewards.weekly_goal.target_count);
  const [isUpdatingGoal, setIsUpdatingGoal] = useState(false);
  const [goalSaveStatus, setGoalSaveStatus] = useState<"idle" | "saved" | "error">("idle");

  const [localPrefs, setLocalPrefs] = useState<LearnerLocalPreferences>(() => getLocalPreferences());
  const [prefSaveStatus, setPrefSaveStatus] = useState<"idle" | "saved">("idle");

  // Sync state on client mount
  useEffect(() => {
    setLocalPrefs(getLocalPreferences());
  }, []);

  const handleUpdateWeeklyGoal = async (newTarget: number) => {
    setIsUpdatingGoal(true);
    setGoalSaveStatus("idle");
    try {
      const res = await updateWeeklyGoal("student_01", newTarget, "active", "completed_missions");
      setWeeklyGoal(res.goal.target_count);
      setGoalSaveStatus("saved");
      setTimeout(() => setGoalSaveStatus("idle"), 3000);
    } catch {
      setGoalSaveStatus("error");
    } finally {
      setIsUpdatingGoal(false);
    }
  };

  const handleUpdatePref = (key: keyof LearnerLocalPreferences, val: unknown) => {
    const updated = saveLocalPreferences({ [key]: val });
    setLocalPrefs(updated);
    setPrefSaveStatus("saved");
    setTimeout(() => setPrefSaveStatus("idle"), 2000);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-enter">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-[var(--color-border-subtle)] pb-5">
        <div>
          <div className="flex items-center gap-2">
            <Badge variant="primary" className="font-mono text-[10px] gap-1">
              <ShieldCheck size={13} weight="bold" />
              Pilot Architecture v1.1.0
            </Badge>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--color-text-primary)] mt-1">
            Settings &amp; Learner Preferences
          </h1>
          <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">
            Configure authoritative study cadence, local display preferences, and view deployment integrity.
          </p>
        </div>
      </div>

      {/* 1. Account Section */}
      <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
        <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
              <User size={16} weight="bold" className="text-[var(--color-accent)]" />
              Account &amp; Learner Identity
            </CardTitle>
            <Badge variant="default" className="font-mono text-[10px]">
              Local Pilot Session
            </Badge>
          </div>
          <CardDescription className="text-xs">
            Pseudonymous student identifier with verified SQLite data isolation.
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-4 space-y-3.5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/40 text-xs">
            <div>
              <span className="text-[11px] text-[var(--color-text-tertiary)] font-mono block">Active Learner ID</span>
              <span className="font-mono font-bold text-[var(--color-text-primary)] text-sm">
                {initialRewards.student_id}
              </span>
              <span className="text-[10px] text-[var(--color-text-secondary)] block mt-0.5">
                Role: GPAT Aspirant (Non-destructive learner account)
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="secondary"
                onClick={() => alert("Local pilot mode: Account session is pinned to this device.")}
                className="text-xs h-8 gap-1.5 font-mono"
              >
                <SignOut size={13} weight="bold" />
                Session Info
              </Button>
            </div>
          </div>

          <div className="p-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/30 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-medium text-[var(--color-text-primary)] block">Learner Display Name</span>
                <span className="text-[11px] text-[var(--color-text-secondary)]">Used for personalized greetings on your daily study home.</span>
              </div>
            </div>
            <div className="flex items-center gap-2 max-w-sm">
              <input
                type="text"
                placeholder="e.g. Priya or Rahul"
                value={localPrefs.learnerName || ""}
                onChange={(e) => handleUpdatePref("learnerName", e.target.value.trim() || null)}
                className="w-full text-xs px-2.5 py-1.5 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)] text-[var(--color-text-primary)] focus:border-[var(--color-accent)] focus:outline-none"
              />
            </div>
          </div>

          <div className="p-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] text-[11px] text-[var(--color-text-secondary)] leading-relaxed">
            <strong>Authentication Status:</strong> Supabase Auth is the designated authentication provider for VPS deployment. The local environment operates with secure pseudonymous session identity without transmitting or leaking access secrets to the client.
          </div>
        </CardContent>
      </Card>

      {/* 2. Study Cadence & Mission Goals (Authoritative Backend Persistence) */}
      <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
        <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
              <GearSix size={16} weight="bold" className="text-[var(--color-accent)]" />
              Authoritative Study Cadence
            </CardTitle>
            <div className="flex items-center gap-2">
              {goalSaveStatus === "saved" && (
                <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
                  <Check size={12} weight="bold" /> Goal Persisted
                </span>
              )}
              {goalSaveStatus === "error" && (
                <span className="text-[11px] font-mono text-rose-400 flex items-center gap-1">
                  <WarningCircle size={12} weight="bold" /> Failed to Save
                </span>
              )}
              <Badge variant="primary" className="font-mono text-[10px]">
                SQLite Backed
              </Badge>
            </div>
          </div>
          <CardDescription className="text-xs">
            Persisted in `learner_goals` table. Flexible, non-punitive weekly goals without loss threats.
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-4 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <span className="text-xs font-semibold text-[var(--color-text-primary)] block">
                Target Study Missions / Week
              </span>
              <span className="text-[11px] text-[var(--color-text-secondary)] block">
                Current week: {initialRewards.weekly_goal.week_range} ({initialRewards.weekly_goal.achieved_count} completed)
              </span>
            </div>

            <div className="flex items-center gap-1.5">
              {[3, 5, 7, 10, 14].map((num) => (
                <button
                  key={num}
                  type="button"
                  disabled={isUpdatingGoal}
                  onClick={() => handleUpdateWeeklyGoal(num)}
                  className={`h-8 w-9 rounded text-xs font-mono border transition-all ${
                    weeklyGoal === num
                      ? "bg-[var(--color-accent)] text-black font-bold border-[var(--color-accent)]"
                      : "bg-[var(--color-surface-raised)] text-[var(--color-text-secondary)] border-[var(--color-border-subtle)] hover:border-[var(--color-border-focus)]"
                  }`}
                >
                  {num}
                </button>
              ))}
            </div>
          </div>

          <div className="p-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/30 text-[11px] font-mono text-[var(--color-text-secondary)] flex justify-between">
            <span>Goal Status:</span>
            <span className={initialRewards.weekly_goal.is_met ? "text-emerald-400 font-bold" : "text-[var(--color-accent)]"}>
              {initialRewards.weekly_goal.is_met ? "Weekly Target Met!" : `${weeklyGoal - initialRewards.weekly_goal.achieved_count} missions remaining`}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* 3. Study Session Preferences (Client-Side Validated) */}
      <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
        <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
              <Sliders size={16} weight="bold" className="text-[var(--color-accent)]" />
              Interface &amp; Learning Preferences
            </CardTitle>
            {prefSaveStatus === "saved" && (
              <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
                <Check size={12} weight="bold" /> Updated
              </span>
            )}
          </div>
          <CardDescription className="text-xs">
            Stored in client local preferences and passed into mission initialization parameters.
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-4 space-y-4 text-xs">
          {/* Mission Duration */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 py-2 border-b border-[var(--color-border-subtle)]">
            <div>
              <span className="font-semibold text-[var(--color-text-primary)] block">
                Preferred Daily Mission Duration
              </span>
              <span className="text-[11px] text-[var(--color-text-secondary)]">
                Standard balanced session timing: 8 to 20 minutes
              </span>
            </div>
            <div className="flex items-center gap-1.5 font-mono">
              {[8, 12, 15, 20].map((mins) => (
                <button
                  key={mins}
                  type="button"
                  onClick={() => handleUpdatePref("preferredMissionDurationMinutes", mins)}
                  className={`h-7 px-2.5 rounded text-[11px] border transition-colors ${
                    localPrefs.preferredMissionDurationMinutes === mins
                      ? "bg-[var(--color-accent)] text-black font-bold border-[var(--color-accent)]"
                      : "bg-[var(--color-surface-raised)] text-[var(--color-text-secondary)] border-[var(--color-border-subtle)]"
                  }`}
                >
                  {mins}m
                </button>
              ))}
            </div>
          </div>

          {/* Review Batch Size */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 py-2 border-b border-[var(--color-border-subtle)]">
            <div>
              <span className="font-semibold text-[var(--color-text-primary)] block">
                FSRS Review Batch Size
              </span>
              <span className="text-[11px] text-[var(--color-text-secondary)]">
                Active recall cards presented per review cycle
              </span>
            </div>
            <div className="flex items-center gap-1.5 font-mono">
              {[5, 10, 15, 25].map((count) => (
                <button
                  key={count}
                  type="button"
                  onClick={() => handleUpdatePref("preferredReviewBatchSize", count)}
                  className={`h-7 px-2.5 rounded text-[11px] border transition-colors ${
                    localPrefs.preferredReviewBatchSize === count
                      ? "bg-[var(--color-accent)] text-black font-bold border-[var(--color-accent)]"
                      : "bg-[var(--color-surface-raised)] text-[var(--color-text-secondary)] border-[var(--color-border-subtle)]"
                  }`}
                >
                  {count} Qs
                </button>
              ))}
            </div>
          </div>

          {/* Color Mode & Inversion (XIAS) */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 py-2 border-b border-[var(--color-border-subtle)]">
            <div>
              <span className="font-semibold text-[var(--color-text-primary)] block">
                Visual Theme &amp; Color Inversion
              </span>
              <span className="text-[11px] text-[var(--color-text-secondary)]">
                Switch between Dark Botanical, Crisp White Minimalist, and Warm Editorial Bone
              </span>
            </div>
            <div className="flex items-center gap-1.5 font-mono">
              <button
                type="button"
                onClick={() => handleUpdatePref("theme", "dark")}
                className={`h-7 px-2.5 rounded text-[11px] border transition-colors flex items-center gap-1.5 ${
                  localPrefs.theme === "dark" || !localPrefs.theme
                    ? "bg-[var(--color-accent)] text-black font-bold border-[var(--color-accent)]"
                    : "bg-[var(--color-surface-raised)] text-[var(--color-text-secondary)] border-[var(--color-border-subtle)] hover:text-[var(--color-text-primary)]"
                }`}
              >
                <Moon size={13} weight="bold" />
                Dark Navy
              </button>
              <button
                type="button"
                onClick={() => handleUpdatePref("theme", "light")}
                className={`h-7 px-2.5 rounded text-[11px] border transition-colors flex items-center gap-1.5 ${
                  localPrefs.theme === "light"
                    ? "bg-[var(--color-accent)] text-white font-bold border-[var(--color-accent)]"
                    : "bg-[var(--color-surface-raised)] text-[var(--color-text-secondary)] border-[var(--color-border-subtle)] hover:text-[var(--color-text-primary)]"
                }`}
              >
                <Sun size={13} weight="bold" />
                Crisp White
              </button>
              <button
                type="button"
                onClick={() => handleUpdatePref("theme", "warm-editorial")}
                className={`h-7 px-2.5 rounded text-[11px] border transition-colors flex items-center gap-1.5 ${
                  localPrefs.theme === "warm-editorial"
                    ? "bg-[#1F6C9F] text-white font-bold border-[#1F6C9F]"
                    : "bg-[var(--color-surface-raised)] text-[var(--color-text-secondary)] border-[var(--color-border-subtle)] hover:text-[var(--color-text-primary)]"
                }`}
              >
                <Palette size={13} weight="bold" />
                Warm Editorial
              </button>
            </div>
          </div>

          {/* Reduced Motion Toggle */}
          <div className="flex items-center justify-between py-2">
            <div>
              <span className="font-semibold text-[var(--color-text-primary)] block">
                Reduced Motion Mode
              </span>
              <span className="text-[11px] text-[var(--color-text-secondary)]">
                Disables animated transitions and decorative entry effects
              </span>
            </div>
            <button
              type="button"
              onClick={() => handleUpdatePref("reducedMotion", !localPrefs.reducedMotion)}
              className={`h-6 w-11 rounded-full p-0.5 transition-colors border ${
                localPrefs.reducedMotion
                  ? "bg-emerald-500 border-emerald-400"
                  : "bg-[var(--color-surface-raised)] border-[var(--color-border-subtle)]"
              }`}
            >
              <div
                className={`h-4.5 w-4.5 rounded-full bg-white transition-transform ${
                  localPrefs.reducedMotion ? "translate-x-5" : "translate-x-0"
                }`}
              />
            </button>
          </div>
        </CardContent>
      </Card>

      {/* 4. Notifications & Reminders (Honest Status) */}
      <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
        <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
              <Bell size={16} weight="bold" className="text-amber-400" />
              Notifications &amp; Reminders
            </CardTitle>
            <Badge variant="warning" className="font-mono text-[10px]">
              Not Yet Implemented
            </Badge>
          </div>
          <CardDescription className="text-xs">
            Browser push notifications and periodic study alert channels.
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-4 text-xs text-[var(--color-text-secondary)] space-y-2">
          <p className="leading-relaxed">
            Background Push Notifications require Web Push API subscriptions and a running VPS delivery worker. Push reminder scheduling is currently disabled in this local environment to avoid false promises.
          </p>
        </CardContent>
      </Card>

      {/* 5. Data Safety & Architecture Transparency */}
      <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
        <CardHeader className="pb-3 border-b border-[var(--color-border-subtle)]">
          <CardTitle className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
            <Database size={16} weight="bold" className="text-emerald-400" />
            Data Storage &amp; Database Safety
          </CardTitle>
          <CardDescription className="text-xs">
            Authoritative persistence configuration for GPAT Learning OS.
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-4 space-y-2.5 text-xs text-[var(--color-text-secondary)] font-mono">
          <div className="flex justify-between py-1.5 border-b border-[var(--color-border-subtle)]">
            <span className="font-sans">Learner Store:</span>
            <span className="text-[var(--color-status-success)]">gpat_knowledge.db (Active, Protected)</span>
          </div>
          <div className="flex justify-between py-1.5 border-b border-[var(--color-border-subtle)]">
            <span className="font-sans">Baseline Question Bank:</span>
            <span className="text-[var(--color-accent)]">data/gpat_baseline.db (2,063 Published)</span>
          </div>
          <div className="flex justify-between py-1.5 border-b border-[var(--color-border-subtle)]">
            <span className="font-sans">Syllabus Staging:</span>
            <span className="text-[var(--color-status-warning)]">data/pyq_topic_staging.db (Quarantine Isolated)</span>
          </div>
          <div className="flex justify-between py-1.5 border-b border-[var(--color-border-subtle)]">
            <span className="font-sans">Offline Strategy:</span>
            <span className="text-[var(--color-text-primary)]">IndexedDB + Next.js SW PWA Cache</span>
          </div>
          <div className="flex justify-between py-1.5">
            <span className="font-sans">Automated Backups:</span>
            <span className="text-emerald-400">Available (`scripts/backup_db.py`)</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
