"use client";

import { useEffect, useId, useRef, useState } from "react";
import { Check, ChevronDown } from "lucide-react";

import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

export interface FilterDropdownOption {
  value: string;
  label: string;
}

interface FilterDropdownProps {
  label: string;
  value: string;
  placeholder: string;
  options: FilterDropdownOption[];
  onChange: (value: string) => void;
  /** Desktop sidebar: open on hover. Mobile sheet: tap toggle. */
  mode: "hover" | "tap";
}

export function FilterDropdown({
  label,
  value,
  placeholder,
  options,
  onChange,
  mode,
}: FilterDropdownProps) {
  const listId = useId();
  const rootRef = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const selectedLabel = options.find((o) => o.value === value)?.label ?? placeholder;

  function clearCloseTimer() {
    if (closeTimer.current) {
      clearTimeout(closeTimer.current);
      closeTimer.current = null;
    }
  }

  function scheduleClose() {
    clearCloseTimer();
    closeTimer.current = setTimeout(() => setOpen(false), 120);
  }

  function handleOpen() {
    clearCloseTimer();
    setOpen(true);
  }

  function handleSelect(next: string) {
    onChange(next);
    setOpen(false);
  }

  function handleTriggerClick() {
    if (mode === "tap") {
      setOpen((prev) => !prev);
    }
  }

  useEffect(() => {
    if (mode !== "tap" || !open) return;
    function onPointerDown(e: PointerEvent) {
      if (!rootRef.current?.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [mode, open]);

  useEffect(() => () => clearCloseTimer(), []);

  return (
    <div
      ref={rootRef}
      className="relative space-y-2"
      onMouseEnter={mode === "hover" ? handleOpen : undefined}
      onMouseLeave={mode === "hover" ? scheduleClose : undefined}
    >
      <Label id={`${listId}-label`}>{label}</Label>
      <button
        type="button"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-labelledby={`${listId}-label`}
        aria-controls={listId}
        onClick={handleTriggerClick}
        onKeyDown={(e) => {
          if (e.key === "Escape") {
            setOpen(false);
            return;
          }
          if (mode === "hover" && (e.key === "Enter" || e.key === " ")) {
            e.preventDefault();
            setOpen((prev) => !prev);
          }
        }}
        className={cn(
          "flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm",
          "ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        )}
      >
        <span className="truncate text-left">{selectedLabel}</span>
        <ChevronDown
          className={cn("h-4 w-4 shrink-0 opacity-50 transition-transform duration-150", open && "rotate-180")}
          aria-hidden
        />
      </button>

      <ul
        id={listId}
        role="listbox"
        aria-labelledby={`${listId}-label`}
        className={cn(
          "absolute left-0 right-0 top-full z-50 mt-1 max-h-60 overflow-y-auto rounded-md border bg-popover p-1 text-popover-foreground shadow-md",
          "origin-top transition-[opacity,transform] duration-150 ease-out",
          open
            ? "pointer-events-auto scale-100 opacity-100"
            : "pointer-events-none scale-[0.98] opacity-0",
        )}
        onMouseEnter={mode === "hover" ? clearCloseTimer : undefined}
        onMouseLeave={mode === "hover" ? scheduleClose : undefined}
      >
        {options.map((option) => {
          const isSelected = option.value === value;
          return (
            <li key={option.value} role="none">
              <button
                type="button"
                role="option"
                aria-selected={isSelected}
                onClick={() => handleSelect(option.value)}
                className={cn(
                  "relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none",
                  "hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground",
                  isSelected && "bg-accent/60",
                )}
              >
                {isSelected && (
                  <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
                    <Check className="h-4 w-4" />
                  </span>
                )}
                {option.label}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
