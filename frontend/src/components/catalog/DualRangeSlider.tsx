"use client";

import { cn } from "@/lib/utils";

interface DualRangeSliderProps {
  min: number;
  max: number;
  value: [number, number];
  onChange: (value: [number, number]) => void;
  step?: number;
  unit?: string;
  className?: string;
}

export function DualRangeSlider({
  min,
  max,
  value,
  onChange,
  step = 1,
  unit = "",
  className,
}: DualRangeSliderProps) {
  const [lo, hi] = value;

  function setLo(next: number) {
    onChange([Math.min(next, hi), hi]);
  }

  function setHi(next: number) {
    onChange([lo, Math.max(next, lo)]);
  }

  if (min >= max) {
    return (
      <p className="text-sm text-muted-foreground">
        {min}
        {unit}
      </p>
    );
  }

  return (
    <div className={cn("space-y-3", className)}>
      <div className="relative h-6">
        <div className="absolute top-1/2 h-1.5 w-full -translate-y-1/2 rounded-full bg-muted" />
        <div
          className="absolute top-1/2 h-1.5 -translate-y-1/2 rounded-full bg-primary/70"
          style={{
            left: `${((lo - min) / (max - min)) * 100}%`,
            right: `${100 - ((hi - min) / (max - min)) * 100}%`,
          }}
        />
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={lo}
          onChange={(e) => setLo(Number(e.target.value))}
          className="pointer-events-auto absolute inset-0 z-20 h-full w-full cursor-pointer appearance-none bg-transparent [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-primary [&::-webkit-slider-thumb]:bg-background"
          aria-label="Минимальное значение"
        />
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={hi}
          onChange={(e) => setHi(Number(e.target.value))}
          className="pointer-events-auto absolute inset-0 z-30 h-full w-full cursor-pointer appearance-none bg-transparent [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-primary [&::-webkit-slider-thumb]:bg-background"
          aria-label="Максимальное значение"
        />
      </div>
      <p className="text-center text-sm font-medium tabular-nums">
        {lo}
        {unit} — {hi}
        {unit}
      </p>
    </div>
  );
}
