"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  CalendarBlank,
  BookOpen,
  ClockCounterClockwise,
  ArrowsCounterClockwise,
  Exam,
  ChartLineUp,
  GearSix,
  Sun,
  Moon,
} from "@phosphor-icons/react";
import { cn } from "@/lib/utils";
import { getLocalPreferences, saveLocalPreferences } from "@/lib/preferences";

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ size?: number; weight?: "bold" | "regular"; className?: string }>;
}

const navItems: NavItem[] = [
  { name: "Today", href: "/today", icon: CalendarBlank },
  { name: "Study", href: "/study", icon: BookOpen },
  { name: "PYQs", href: "/pyqs", icon: ClockCounterClockwise },
  { name: "Review", href: "/review", icon: ArrowsCounterClockwise },
  { name: "Mocks", href: "/mocks", icon: Exam },
  { name: "Progress", href: "/progress", icon: ChartLineUp },
  { name: "Settings", href: "/settings", icon: GearSix },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [theme, setTheme] = React.useState<"dark" | "light" | "warm-editorial">("dark");

  React.useEffect(() => {
    const prefs = getLocalPreferences();
    if (prefs.theme) {
      setTheme(prefs.theme);
    }
  }, []);

  const toggleTheme = () => {
    // Cycle dark -> light -> warm-editorial -> dark
    const nextTheme: "dark" | "light" | "warm-editorial" =
      theme === "dark" ? "light" : theme === "light" ? "warm-editorial" : "dark";
    setTheme(nextTheme);
    saveLocalPreferences({ theme: nextTheme });
  };

  return (
    <div className="min-h-dvh bg-[var(--color-bg-base)] text-[var(--color-text-primary)] flex flex-col md:flex-row transition-colors duration-200">
      {/* Skip to content — accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 z-50 bg-[var(--color-accent)] text-[var(--color-bg-base)] font-semibold px-4 py-2 rounded-md text-sm"
      >
        Skip to main content
      </a>

      {/* Desktop sidebar — visible above 768px */}
      <aside
        className="hidden md:flex md:w-56 md:flex-col md:fixed md:inset-y-0 bg-[var(--color-surface-base)] border-r border-[var(--color-border-subtle)] z-30"
        aria-label="Primary navigation"
      >
        {/* Brand & Theme Quick Toggle */}
        <div className="flex h-14 items-center justify-between px-4 border-b border-[var(--color-border-subtle)]">
          <div className="flex items-center gap-2.5">
            <div className="h-7 w-7 rounded-md bg-[var(--color-accent)] flex items-center justify-center text-[var(--color-bg-base)] text-xs font-bold">
              G
            </div>
            <div>
              <span className="font-semibold text-sm tracking-tight text-[var(--color-text-primary)] block leading-none">
                GPAT 2027
              </span>
              <span className="text-[10px] text-[var(--color-text-tertiary)] tracking-wide uppercase block font-mono mt-0.5">
                Learning OS
              </span>
            </div>
          </div>
          <button
            type="button"
            onClick={toggleTheme}
            className="p-1.5 rounded-md text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface-raised)] transition-colors"
            title={`Current theme: ${theme}. Click to invert color mode.`}
            aria-label="Toggle theme color mode"
          >
            {theme === "dark" ? <Sun size={16} weight="bold" /> : <Moon size={16} weight="bold" />}
          </button>
        </div>

        {/* Navigation links */}
        <nav className="flex-1 px-3 py-3 space-y-0.5">
          {navItems.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href === "/today" && pathname === "/");
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors duration-150",
                  isActive
                    ? "bg-[var(--color-surface-raised)] text-[var(--color-text-primary)] font-medium"
                    : "text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-raised)] hover:text-[var(--color-text-primary)]"
                )}
                aria-current={isActive ? "page" : undefined}
              >
                <Icon
                  size={18}
                  weight={isActive ? "bold" : "regular"}
                  className={cn(
                    "shrink-0 transition-colors duration-150",
                    isActive
                      ? "text-[var(--color-accent)]"
                      : "text-[var(--color-text-tertiary)]"
                  )}
                />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Sidebar footer — organic reminder */}
        <div className="p-3 border-t border-[var(--color-border-subtle)] space-y-2">
          <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-500/20 text-xs">
            <div className="flex items-center gap-1.5 text-emerald-400 font-semibold mb-1">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>GPAT 2027 Aspirant</span>
            </div>
            <p className="text-[11px] text-[var(--color-text-secondary)] leading-relaxed">
              Small consistent steps create big results.
            </p>
          </div>
          <div className="px-2">
            <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">
              v1.1.0 — Pilot build
            </span>
          </div>
        </div>
      </aside>

      {/* Main content area */}
      <div className="flex-1 md:pl-56 flex flex-col min-h-dvh">
        {/* Mobile header — visible below 768px */}
        <header className="md:hidden flex h-13 items-center justify-between px-4 bg-[var(--color-surface-base)] border-b border-[var(--color-border-subtle)] sticky top-0 z-20">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded-md bg-[var(--color-accent)] flex items-center justify-center text-[var(--color-bg-base)] text-[10px] font-bold">
              G
            </div>
            <span className="font-semibold text-sm text-[var(--color-text-primary)]">
              GPAT 2027
            </span>
          </div>
          <div className="flex items-center gap-1">
            <Link
              href="/settings"
              className="p-2 rounded-md text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface-raised)] transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
              title="Settings & Profile"
              aria-label="Settings and Profile"
            >
              <GearSix size={18} weight="bold" />
            </Link>
            <button
              type="button"
              onClick={toggleTheme}
              className="p-2 rounded-md text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface-raised)] transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
              title={`Current theme: ${theme}. Click to invert color mode.`}
              aria-label="Toggle theme color mode"
            >
              {theme === "dark" ? <Sun size={18} weight="bold" /> : <Moon size={18} weight="bold" />}
            </button>
          </div>
        </header>

        {/* Page content viewport with generous bottom clearance for fixed mobile navigation */}
        <main
          id="main-content"
          tabIndex={-1}
          className="flex-1 px-3 sm:px-4 py-4 md:px-8 md:py-6 max-w-5xl w-full mx-auto pb-24 md:pb-8"
        >
          {children}
        </main>

        {/* Mobile bottom navigation — 5 primary destinations with >= 48px touch targets */}
        <nav
          className="md:hidden fixed bottom-0 inset-x-0 bg-[var(--color-surface-base)]/95 backdrop-blur-md border-t border-[var(--color-border-subtle)] z-30 flex items-center justify-around h-16 px-1 shadow-lg"
          aria-label="Mobile navigation"
          style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
        >
          {[
            { name: "Today", href: "/today", icon: CalendarBlank },
            { name: "Study", href: "/study", icon: BookOpen },
            { name: "PYQs", href: "/pyqs", icon: ClockCounterClockwise },
            { name: "Review", href: "/review", icon: ArrowsCounterClockwise },
            { name: "Progress", href: "/progress", icon: ChartLineUp },
          ].map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href === "/today" && pathname === "/");
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex flex-col items-center justify-center flex-1 h-full min-h-[48px] py-1 text-[11px] font-medium transition-colors duration-150 relative touch-manipulation",
                  isActive
                    ? "text-emerald-400 font-semibold"
                    : "text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)]"
                )}
                aria-current={isActive ? "page" : undefined}
              >
                <Icon
                  size={22}
                  weight={isActive ? "bold" : "regular"}
                  className="mb-0.5 transition-transform active:scale-90"
                />
                <span className="leading-tight">{item.name}</span>
                {isActive && (
                  <span className="absolute top-1 h-1 w-6 bg-emerald-400 rounded-full" />
                )}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
