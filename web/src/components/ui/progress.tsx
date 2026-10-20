import React from "react";
import { cn } from "@/lib/utils";

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number;
  max?: number;
  variant?: "primary" | "success" | "warning" | "error";
  label?: string;
}

export function Progress({
  value = 0,
  max = 100,
  variant = "primary",
  label,
  className,
  ...props
}: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const variantColors: Record<string, string> = {
    primary: "bg-[var(--color-accent)]",
    success: "bg-[var(--color-status-success)]",
    warning: "bg-[var(--color-status-warning)]",
    error: "bg-[var(--color-status-error)]",
  };

  return (
    <div
      role="progressbar"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={max}
      aria-label={label}
      className={cn(
        "relative h-1 w-full overflow-hidden rounded-sm bg-[var(--color-surface-raised)]",
        className
      )}
      {...props}
    >
      <div
        className={cn(
          "h-full transition-all duration-500 ease-out rounded-sm",
          variantColors[variant]
        )}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}
