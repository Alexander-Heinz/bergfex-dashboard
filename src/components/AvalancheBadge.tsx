import { AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AvalancheBadgeProps {
  level: number;
  text: string;
  compact?: boolean;
}

export const AvalancheBadge = ({ level, text, compact = false }: AvalancheBadgeProps) => {
  const getStyles = () => {
    switch (level) {
      case 1:
        return 'bg-avalanche-low/15 text-avalanche-low border-avalanche-low/30';
      case 2:
        return 'bg-avalanche-moderate/15 text-avalanche-moderate border-avalanche-moderate/30';
      case 3:
        return 'bg-avalanche-considerable/15 text-avalanche-considerable border-avalanche-considerable/30';
      case 4:
        return 'bg-avalanche-high/15 text-avalanche-high border-avalanche-high/30';
      case 5:
        return 'bg-avalanche-extreme/15 text-avalanche-extreme border-avalanche-extreme/30';
      default:
        return 'bg-muted text-muted-foreground border-muted';
    }
  };

  if (level === 0 || text === "-") {
    return (
      <div className={cn('inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border bg-muted/10 text-muted-foreground border-muted/30')}>
        <span className="text-xs font-medium">Keine Lawinen-Info</span>
      </div>
    );
  }

  if (compact) {
    return (
      <span
        className={cn(
          'inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold border',
          getStyles()
        )}
      >
        {level}
      </span>
    );
  }

  return (
    <div className={cn('inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border', getStyles())}>
      <AlertTriangle className="w-4 h-4" />
      <span className="text-xs font-medium hidden sm:inline">Lawinenwarnstufe</span>
      <span className="text-xs font-medium sm:hidden">LWS</span>
      <span className="font-bold">{level}</span>
      <span className="text-sm opacity-80 border-l border-current/20 pl-2">{text}</span>
    </div>
  );
};
