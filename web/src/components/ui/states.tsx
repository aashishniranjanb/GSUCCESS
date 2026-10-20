import React from "react";
import { Warning, ArrowCounterClockwise, MagnifyingGlass } from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({
  title,
  description,
  icon,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      <div className="h-10 w-10 rounded-lg bg-[var(--color-surface-raised)] flex items-center justify-center text-[var(--color-text-tertiary)] mb-4">
        {icon || <MagnifyingGlass size={20} weight="bold" />}
      </div>
      <h4 className="text-sm font-semibold text-[var(--color-text-primary)]">
        {title}
      </h4>
      <p className="text-xs text-[var(--color-text-secondary)] max-w-xs mt-1.5 leading-relaxed">
        {description}
      </p>
      {actionLabel && onAction && (
        <Button variant="secondary" size="sm" onClick={onAction} className="mt-5">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = "Connection failed",
  message,
  onRetry,
}: ErrorStateProps) {
  return (
    <div
      role="alert"
      className="flex flex-col items-center justify-center py-12 px-6 text-center rounded-lg border border-[var(--color-status-error)]/20 bg-[var(--color-status-error)]/5"
    >
      <div className="h-10 w-10 rounded-lg bg-[var(--color-status-error)]/10 flex items-center justify-center text-[var(--color-status-error)] mb-3">
        <Warning size={20} weight="bold" />
      </div>
      <h4 className="text-sm font-semibold text-[var(--color-status-error)]">
        {title}
      </h4>
      <p className="text-xs text-[var(--color-text-secondary)] max-w-xs mt-1 leading-relaxed">
        {message}
      </p>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry} className="mt-4 gap-1.5">
          <ArrowCounterClockwise size={14} weight="bold" />
          Retry
        </Button>
      )}
    </div>
  );
}

/* Skeleton loader for data fetching states */
export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={`animate-pulse rounded-md bg-[var(--color-surface-raised)] ${className ?? ""}`}
      aria-hidden="true"
    />
  );
}
