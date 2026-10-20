import React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium select-none",
  {
    variants: {
      variant: {
        default:
          "bg-[var(--color-surface-raised)] text-[var(--color-text-secondary)]",
        primary:
          "bg-[rgb(96_165_250/0.12)] text-[var(--color-accent)]",
        success:
          "bg-[rgb(134_239_172/0.12)] text-[var(--color-status-success)]",
        warning:
          "bg-[rgb(252_211_77/0.12)] text-[var(--color-status-warning)]",
        error:
          "bg-[rgb(252_165_165/0.12)] text-[var(--color-status-error)]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
