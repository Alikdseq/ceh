"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: React.ReactNode;
  count?: number;
}

export function Checkbox({ label, count, className, id, ...props }: CheckboxProps) {
  const autoId = React.useId();
  const inputId = id ?? autoId;
  return (
    <label
      htmlFor={inputId}
      className={cn(
        "flex cursor-pointer items-start gap-2 rounded-md py-1.5 text-sm leading-snug hover:bg-muted/60",
        props.disabled && "cursor-not-allowed opacity-50",
        className,
      )}
    >
      <input
        id={inputId}
        type="checkbox"
        className="mt-0.5 h-4 w-4 shrink-0 rounded border-input accent-[var(--color-brand-blue)]"
        {...props}
      />
      <span className="flex-1">
        {label}
        {count !== undefined && (
          <span className="ml-1 text-muted-foreground">({count})</span>
        )}
      </span>
    </label>
  );
}
