import { Button } from './ui/button';
import { cn } from '@/lib/utils';

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
  );
};
