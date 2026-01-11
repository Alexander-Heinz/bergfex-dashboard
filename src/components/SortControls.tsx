import { Button } from './ui/button';
import { cn } from '@/lib/utils';
import { Activity } from 'lucide-react';

export type SortOption = 
  | 'shredScore'
  | 'snowMountain' 
  | 'newSnow' 
  | 'slopesOpenKm' 
  | 'liftsOpen'
  | 'name';

interface SortControlsProps {
  currentSort: SortOption;
  onSortChange: (sort: SortOption) => void;
}

export const SortControls = ({ currentSort, onSortChange }: SortControlsProps) => {
  const options: { value: SortOption; label: string }[] = [
    { value: 'shredScore', label: 'Shred Score' },
    { value: 'newSnow', label: 'Neuschnee' },
    { value: 'snowMountain', label: 'Schneehöhe' },
    { value: 'slopesOpenKm', label: 'Pisten km' },
    { value: 'liftsOpen', label: 'Lifte' },
    { value: 'name', label: 'Name' },
  ];

  return (
    <div className="flex flex-col gap-2 w-full">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm font-medium text-muted-foreground mr-2">Sortieren nach:</span>
        {options.map((option) => (
          <Button
            key={option.value}
            variant={currentSort === option.value ? 'default' : 'outline'}
            size="sm"
            onClick={() => onSortChange(option.value)}
            className={cn(
              'transition-all duration-200',
              currentSort === option.value 
                ? 'bg-gradient-alpine text-primary-foreground shadow-lg hover:opacity-90' 
                : 'hover:bg-secondary'
            )}
          >
            {option.label}
          </Button>
        ))}
      </div>
      
      {currentSort === 'shredScore' && (
        <div className="text-xs text-muted-foreground bg-secondary/50 px-3 py-2 rounded-lg flex items-center gap-2 animate-in fade-in slide-in-from-top-1 border border-border/50">
          <Activity className="w-3.5 h-3.5 text-primary flex-shrink-0" />
          <span>
            Der <span className="font-semibold text-foreground">Shred Score (1-10)</span> zeigt dir die besten Bedingungen basierend auf Neuschnee, Schneehöhe, Pistenzustand und Lawinengefahr.
          </span>
        </div>
      )}
    </div>
  );
};
