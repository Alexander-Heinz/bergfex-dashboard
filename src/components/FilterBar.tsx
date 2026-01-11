
import { Input } from './ui/input';
import { SortControls, SortOption } from './SortControls';
import { Search, MapPin, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

// Country display names
const COUNTRY_NAMES: Record<string, string> = {
  'AT': 'Österreich',
  'CH': 'Schweiz',
  'DE': 'Deutschland',
  'IT': 'Italien',
  'FR': 'Frankreich',
  'SI': 'Slowenien',
  'CZ': 'Tschechien',
  'PL': 'Polen',
  'SK': 'Slowakei',
};

interface FilterBarProps {
  sortBy: SortOption;
  onSortChange: (sort: SortOption) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  openOnly: boolean;
  onOpenOnlyChange: (open: boolean) => void;
  // New props for location filtering
  selectedCountry: string;
  onCountryChange: (country: string) => void;
  selectedRegion: string;
  onRegionChange: (region: string) => void;
  availableCountries: string[];
  availableRegions: Record<string, string[]>;
}

export const FilterBar = ({
  sortBy,
  onSortChange,
  searchQuery,
  onSearchChange,
  openOnly,
  onOpenOnlyChange,
  selectedCountry,
  onCountryChange,
  selectedRegion,
  onRegionChange,
  availableCountries,
  availableRegions,
}: FilterBarProps) => {
  const regions = selectedCountry ? availableRegions[selectedCountry] || [] : [];

  return (
    <div className="flex flex-col gap-4 bg-card/50 p-4 rounded-xl border border-border/50">
      {/* Top row: Search, Location, Open Only */}
      <div className="flex flex-col lg:flex-row gap-3 w-full">
        {/* Search */}
        <div className="relative flex-1 lg:max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Skigebiet suchen..."
            className="pl-9 bg-background/50 border-input/50 focus:bg-background transition-all"
          />
        </div>

        {/* Location Filters */}
        <div className="flex gap-2 flex-wrap">
          {/* Country Select */}
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
            <select
              value={selectedCountry}
              onChange={(e) => onCountryChange(e.target.value)}
              className={cn(
                "appearance-none pl-9 pr-8 py-2 rounded-lg border text-sm font-medium transition-all cursor-pointer min-w-[140px]",
                selectedCountry 
                  ? "bg-alpine-sky/10 border-alpine-sky/30 text-foreground" 
                  : "bg-background/50 border-input/50 text-muted-foreground hover:border-input"
              )}
            >
              <option value="">Alle Länder</option>
              {availableCountries.map((c) => (
                <option key={c} value={c}>{COUNTRY_NAMES[c] || c}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
          </div>

          {/* Region Select */}
          <div className="relative">
            <select
              value={selectedRegion}
              onChange={(e) => onRegionChange(e.target.value)}
              disabled={!selectedCountry || regions.length === 0}
              className={cn(
                "appearance-none pl-4 pr-8 py-2 rounded-lg border text-sm font-medium transition-all cursor-pointer min-w-[160px]",
                selectedRegion 
                  ? "bg-alpine-sky/10 border-alpine-sky/30 text-foreground" 
                  : "bg-background/50 border-input/50 text-muted-foreground hover:border-input",
                (!selectedCountry || regions.length === 0) && "opacity-50 cursor-not-allowed"
              )}
            >
              <option value="">Alle Regionen</option>
              {regions.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
          </div>
        </div>

        {/* Open Only Toggle */}
        <button
          onClick={() => onOpenOnlyChange(!openOnly)}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-lg border transition-all text-sm font-medium whitespace-nowrap",
            openOnly 
              ? "bg-emerald-600 border-emerald-600 text-white" 
              : "bg-background/50 border-input/50 text-muted-foreground hover:border-input hover:text-foreground"
          )}
        >
          <div className={cn(
            "w-4 h-4 rounded border-2 flex items-center justify-center transition-all",
            openOnly 
              ? "bg-white border-white" 
              : "border-current"
          )}>
            {openOnly && (
              <svg className="w-3 h-3 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            )}
          </div>
          Nur Geöffnete
        </button>
      </div>

      {/* Bottom row: Sort Controls */}
      <SortControls currentSort={sortBy} onSortChange={onSortChange} />
    </div>
  );
};
