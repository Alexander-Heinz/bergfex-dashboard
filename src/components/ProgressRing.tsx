interface ProgressRingProps {
  value: number;
  max: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
  unit?: string;
}

export const ProgressRing = ({
  value,
  max,
  size = 80,
  strokeWidth = 6,
  label,
  unit,
}: ProgressRingProps) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const percent = max > 0 ? (value / max) * 100 : 0;
  const offset = circumference - (percent / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="hsl(var(--secondary))"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="hsl(var(--alpine-sky))"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-lg font-bold text-foreground">{value}</span>
          {max && <span className="text-xs text-muted-foreground">/{max}</span>}
        </div>
      </div>
      {label && (
        <span className="text-xs text-muted-foreground font-medium">
          {label} {unit && `(${unit})`}
        </span>
      )}
    </div>
  );
};
