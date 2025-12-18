import { cn } from '@/lib/utils';

interface StatusBadgeProps {
  status: 'Geöffnet' | 'Geschlossen' | 'Teilweise geöffnet';
}

export const StatusBadge = ({ status }: StatusBadgeProps) => {
  const getStyles = () => {
    switch (status) {
      case 'Geöffnet':
        return 'bg-status-open/15 text-status-open border-status-open/30';
      case 'Geschlossen':
        return 'bg-status-closed/15 text-status-closed border-status-closed/30';
      case 'Teilweise geöffnet':
        return 'bg-status-partial/15 text-status-partial border-status-partial/30';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border',
        getStyles()
      )}
    >
      <span
        className={cn(
          'w-1.5 h-1.5 rounded-full mr-1.5',
          status === 'Geöffnet' && 'bg-status-open animate-pulse',
          status === 'Geschlossen' && 'bg-status-closed',
          status === 'Teilweise geöffnet' && 'bg-status-partial'
        )}
      />
      {status}
    </span>
  );
};
