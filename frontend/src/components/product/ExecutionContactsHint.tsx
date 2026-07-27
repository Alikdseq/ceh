interface ExecutionContactsHintProps {
  productType?: string;
  executions?: string[];
  className?: string;
}

/** Brief note: B = copper, BS = silver alloy main contacts (KT/KTP). */
export function ExecutionContactsHint({
  productType,
  executions = [],
  className = "",
}: ExecutionContactsHintProps) {
  if (productType !== "KT" && productType !== "KTP") {
    return null;
  }

  const execSet = new Set(executions.filter(Boolean));
  const showsB = execSet.has("B");
  const showsBs = execSet.has("BS");
  if (!showsB && !showsBs) {
    return null;
  }

  return (
    <p className={`text-xs leading-relaxed text-muted-foreground ${className}`.trim()}>
      {showsB && (
        <>
          Исполнение <span className="font-medium text-foreground">Б</span> — силовые контакты из{" "}
          <span className="font-medium text-foreground">меди</span>
        </>
      )}
      {showsB && showsBs && "; "}
      {showsBs && (
        <>
          исполнение <span className="font-medium text-foreground">БС</span> — силовые контакты из{" "}
          <span className="font-medium text-foreground">серебряного сплава</span> (повышенная
          стойкость к дуговой эрозии)
        </>
      )}
      .
    </p>
  );
}
