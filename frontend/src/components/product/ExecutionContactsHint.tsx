import { executionLabel } from "@/lib/utils";

interface ExecutionContactsHintProps {
  productType?: string;
  executions?: string[];
  selectedExecution?: string | null;
  className?: string;
}

type ExecutionHint = {
  code: string;
  text: string;
};

function buildExecutionHints(codes: string[]): ExecutionHint[] {
  const hints: ExecutionHint[] = [];
  const execSet = new Set(codes.filter(Boolean));

  if (execSet.has("B")) {
    hints.push({
      code: "B",
      text: "Исполнение Б — силовые контакты из меди",
    });
  }
  if (execSet.has("BS")) {
    hints.push({
      code: "BS",
      text: "Исполнение БС — силовые контакты из серебряного сплава (повышенная стойкость к дуговой эрозии)",
    });
  }
  if (execSet.has("S")) {
    hints.push({
      code: "S",
      text: `Исполнение ${executionLabel("S")} — силовые контакты из серебра`,
    });
  }
  if (execSet.has("NONE")) {
    hints.push({
      code: "NONE",
      text: `Исполнение ${executionLabel("NONE")} — силовые контакты из меди`,
    });
  }

  return hints;
}

/** Material notes for contact executions (KT/KTP, VPK, ЭУ and other product types). */
export function ExecutionContactsHint({
  executions = [],
  selectedExecution = null,
  className = "",
}: ExecutionContactsHintProps) {
  const allHints = buildExecutionHints(executions);
  if (!allHints.length) {
    return null;
  }

  const visibleHints = selectedExecution
    ? allHints.filter((hint) => hint.code === selectedExecution)
    : allHints;

  if (!visibleHints.length) {
    return null;
  }

  return (
    <p className={`text-xs leading-relaxed text-muted-foreground ${className}`.trim()}>
      {visibleHints.map((hint, index) => (
        <span key={hint.code}>
          {index > 0 && "; "}
          <span className="font-medium text-foreground">{hint.text}</span>
        </span>
      ))}
      .
    </p>
  );
}
