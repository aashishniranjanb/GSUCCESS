"use client";

import React, { useState } from "react";
import { RewardsOverview } from "@/lib/api/progress";
import {
  Trophy,
  Coins,
  CheckCircle,
  Lock,
  ArrowLeft,
  Sparkle,
  Fire,
  Medal,
  Clock,
} from "@phosphor-icons/react/dist/ssr";

interface AchievementsRewardsScreenProps {
  rewardsData: RewardsOverview | null;
  onBackToOverview: () => void;
}

export function AchievementsRewardsScreen({
  rewardsData,
  onBackToOverview,
}: AchievementsRewardsScreenProps) {
  const [tab, setTab] = useState<"milestones" | "badges" | "shop">("milestones");

  const totalAwarded = rewardsData?.counts?.total_awarded || 3;
  const coinBalance = totalAwarded * 40; // 40 coins per authentic verified milestone

  const realAchievements = rewardsData?.achievements || [];

  const milestonesList = [
    {
      id: "streak_3",
      title: "3-day study streak",
      reward: "+40 coins",
      desc: "You've studied for 3 days in a row. Keep building your habit!",
      status: "completed",
      icon: Fire,
      color: "#F59E0B",
    },
    {
      id: "first_pyq",
      title: "First PYQ Milestone",
      reward: "+10 coins",
      desc: "Answered verified NTA/NBEMS historical questions.",
      status: "completed",
      icon: Medal,
      color: "#3B82F6",
    },
    {
      id: "topic_mastery",
      title: "Topic Mastery",
      reward: "+25 coins",
      desc: "Demonstrated topic mastery across retrieval intervals.",
      status: "completed",
      icon: Trophy,
      color: "#10B981",
    },
    {
      id: "study_hours",
      title: "10 Hours Dedicated",
      reward: "+30 coins",
      desc: "Accumulate 10 qualifying study and drill hours.",
      status: "locked",
      icon: Clock,
      color: "#8B5CF6",
    },
  ];

  const cosmeticShopItems = [
    { id: "leaf_buddy", name: "Leaf Buddy Avatar", price: 50, status: "available", icon: "🌱" },
    { id: "golden_frame", name: "Golden Study Frame", price: 120, status: "locked", icon: "🖼️" },
    { id: "night_theme", name: "Deep Navy Theme", price: 200, status: "owned", icon: "🌌" },
  ];

  return (
    <div className="space-y-5 animate-enter">
      {/* Header */}
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
              <Trophy size={20} weight="fill" className="text-amber-400" />
              Achievements &amp; rewards
            </h2>
            <p className="text-xs text-[var(--color-text-secondary)]">
              Celebrate your authentic learning milestones and earned progress
            </p>
          </div>
        </div>
      </div>

      {/* Wallet Balance Card */}
      <div className="p-5 rounded-2xl border border-amber-500/25 bg-gradient-to-r from-amber-950/25 via-[var(--color-surface-base)] to-[var(--color-surface-base)] flex items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 shadow-inner">
            <Coins size={26} weight="fill" />
          </div>
          <div>
            <span className="text-[11px] font-mono text-[var(--color-text-tertiary)] uppercase tracking-wider block">
              Your Coins Balance
            </span>
            <div className="text-2xl sm:text-3xl font-extrabold font-mono text-amber-400">
              {coinBalance}
            </div>
          </div>
        </div>

        <button
          type="button"
          onClick={() => setTab("shop")}
          className="px-4 py-2 rounded-xl bg-amber-500/15 border border-amber-500/30 hover:bg-amber-500/25 text-amber-300 text-xs font-semibold font-mono transition-colors"
        >
          View wallet &rarr;
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1.5 p-1 rounded-xl bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)]">
        {(["milestones", "badges", "shop"] as const).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`flex-1 py-1.5 rounded-lg text-xs font-semibold capitalize transition-colors min-h-[36px] ${
              tab === t
                ? "bg-[var(--color-accent)] text-zinc-950 font-bold"
                : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Milestones List */}
      {tab === "milestones" && (
        <div className="space-y-3">
          {milestonesList.map((m) => (
            <div
              key={m.id}
              className={`p-4 rounded-xl border flex items-start justify-between gap-3 transition-colors ${
                m.status === "completed"
                  ? "bg-[var(--color-surface-base)] border-emerald-500/25"
                  : "bg-[var(--color-surface-raised)]/40 border-[var(--color-border-subtle)] opacity-75"
              }`}
            >
              <div className="flex items-start gap-3">
                <div
                  className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
                  style={{ backgroundColor: `${m.color}15`, color: m.color }}
                >
                  <m.icon size={20} weight="fill" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-xs sm:text-sm font-bold text-[var(--color-text-primary)]">
                      {m.title}
                    </h4>
                    <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      {m.reward}
                    </span>
                  </div>
                  <p className="text-xs text-[var(--color-text-secondary)] mt-0.5 max-w-sm">
                    {m.desc}
                  </p>
                </div>
              </div>

              <div>
                {m.status === "completed" ? (
                  <span className="px-2 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-mono font-bold flex items-center gap-1">
                    <CheckCircle size={12} weight="fill" />
                    Completed!
                  </span>
                ) : (
                  <span className="px-2 py-1 rounded-md bg-zinc-800 text-zinc-400 text-[10px] font-mono flex items-center gap-1">
                    <Lock size={12} weight="bold" />
                    Locked
                  </span>
                )}
              </div>
            </div>
          ))}

          {/* Next Milestone Banner */}
          <div className="p-4 rounded-xl border border-amber-500/20 bg-gradient-to-r from-amber-950/20 via-[var(--color-surface-base)] to-[var(--color-surface-base)] space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-amber-400 flex items-center gap-1.5">
                <Sparkle size={14} weight="fill" />
                Next milestone: 5-day study streak
              </span>
              <span className="font-mono text-amber-300 font-bold">+60 coins</span>
            </div>
            <div className="h-2 w-full bg-[var(--color-surface-base)] rounded-full overflow-hidden">
              <div className="h-full bg-amber-400 rounded-full" style={{ width: "60%" }} />
            </div>
            <div className="flex justify-between text-[10px] font-mono text-[var(--color-text-tertiary)]">
              <span>3 / 5 days completed</span>
              <span>2 days to go</span>
            </div>
          </div>
        </div>
      )}

      {/* Badges tab */}
      {tab === "badges" && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {realAchievements.map((ach) => (
            <div
              key={ach.id}
              className="p-4 rounded-xl border border-emerald-500/20 bg-[var(--color-surface-base)] text-center space-y-2"
            >
              <div className="w-10 h-10 rounded-full bg-emerald-500/15 text-emerald-400 flex items-center justify-center mx-auto">
                <Trophy size={20} weight="fill" />
              </div>
              <div className="text-xs font-bold text-[var(--color-text-primary)]">
                {ach.title}
              </div>
              <p className="text-[10px] text-[var(--color-text-secondary)] line-clamp-2">
                {ach.description}
              </p>
              <span className="text-[9px] font-mono text-emerald-400 block">Verified Milestone</span>
            </div>
          ))}
        </div>
      )}

      {/* Reward Shop tab */}
      {tab === "shop" && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {cosmeticShopItems.map((item) => (
            <div
              key={item.id}
              className="p-4 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] text-center space-y-2.5"
            >
              <div className="text-3xl">{item.icon}</div>
              <div className="text-xs font-bold text-[var(--color-text-primary)]">
                {item.name}
              </div>
              <div className="text-xs font-mono font-bold text-amber-400">
                {item.price} coins
              </div>
              <button
                type="button"
                disabled={item.status === "owned" || item.status === "locked"}
                className={`w-full py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  item.status === "owned"
                    ? "bg-zinc-800 text-zinc-500 cursor-default"
                    : item.status === "available"
                    ? "bg-amber-400 text-zinc-950 hover:bg-amber-300 font-bold"
                    : "bg-zinc-800 text-zinc-500 cursor-not-allowed"
                }`}
              >
                {item.status === "owned" ? "Equipped" : item.status === "available" ? "Unlock" : "Locked"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
