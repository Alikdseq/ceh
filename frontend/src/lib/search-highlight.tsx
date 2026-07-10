import type { ReactNode } from "react";

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/** Highlight matched query tokens in text (FR-SRH-03). */
export function highlightMatch(text: string, query: string): ReactNode {
  const trimmed = query.trim();
  if (!trimmed) return text;

  const tokens = trimmed.split(/\s+/).filter(Boolean);
  if (!tokens.length) return text;

  const pattern = new RegExp(`(${tokens.map(escapeRegExp).join("|")})`, "gi");
  const parts = text.split(pattern);

  return parts.map((part, index) =>
    tokens.some((token) => part.toLowerCase() === token.toLowerCase()) ? (
      <mark key={index} className="rounded-sm bg-accent/30 px-0.5 font-medium text-foreground">
        {part}
      </mark>
    ) : (
      part
    ),
  );
}
