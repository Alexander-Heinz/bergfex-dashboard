import { useState, useMemo, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { SkiResort } from '@/types/resort';
import { SortOption } from '@/components/SortControls';

interface ResortResponse {
  totalCount: number;
  openCount: number;
  avgSnowMountain: number;
  totalNewSnow: number;
  totalOpenKm: number;
  resorts: SkiResort[];
  topSnowResorts: SkiResort[];
  topNewSnowResorts: SkiResort[];
  avalancheDistribution: Record<string, number>;
  // Global stats (unfiltered)
  globalTotalCount: number;
  globalOpenCount: number;
  globalAvgSnowMountain: number;
  globalTotalNewSnow: number;
  globalTotalOpenKm: number;
  // Available filter options
  availableCountries: string[];
  availableRegions: Record<string, string[]>;
}
import { Header } from '@/components/Header';
import { DashboardStats } from '@/components/DashboardStats';
import { ResortCard } from '@/components/ResortCard';
import { FilterBar } from '@/components/FilterBar';
import { TopResortsChart } from '@/components/TopResortsChart';
import { NewSnowChart } from '@/components/NewSnowChart';
import { AvalancheOverview } from '@/components/AvalancheOverview';

const Index = () => {
  const [sortBy, setSortBy] = useState<SortOption>('shredScore');
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [showOpenOnly, setShowOpenOnly] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [selectedRegion, setSelectedRegion] = useState<string>('');
  const [limit, setLimit] = useState(50);

  // No debounce needed for client-side filtering of <1000 items
  // const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');

  // Reset region when country changes
  useEffect(() => {
    setSelectedRegion('');
  }, [selectedCountry]);

  // Fetch ALL data once
  const { data, isLoading, error } = useQuery({
    queryKey: ['resorts'], // Static key, fetches once (and on re-focus etc)
    queryFn: async () => {
      const response = await fetch('/api/resorts');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json() as Promise<ResortResponse>;
    },
  });

  const allResorts = data?.resorts || [];
  
  // Available filter options from backend (or could be derived client side, but backend sends them)
  const availableCountries = data?.availableCountries || [];
  const availableRegions = data?.availableRegions || {};

  // Client-side Filtering & Sorting
  const processedResorts = useMemo(() => {
    let result = [...allResorts];

    // 1. Search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(r => r.name.toLowerCase().includes(query));
    }

    // 2. Open Only
    if (showOpenOnly) {
      result = result.filter(r => r.status === 'Geöffnet' || r.status === 'Teilweise geöffnet');
    }

    // 3. Country
    if (selectedCountry) {
      result = result.filter(r => r.country === selectedCountry);
    }

    // 4. Region
    if (selectedRegion) {
      result = result.filter(r => r.region === selectedRegion);
    }

    // 5. Sorting
    result.sort((a, b) => {
      switch (sortBy) {
        case 'shredScore':
          return (b.shredScore || 0) - (a.shredScore || 0);
        case 'snowMountain':
          return b.snowMountain - a.snowMountain;
        case 'newSnow':
          return b.newSnow - a.newSnow;
        case 'slopesOpenKm':
          return b.slopesOpenKm - a.slopesOpenKm;
        case 'liftsOpen':
          return b.liftsOpen - a.liftsOpen;
        case 'name':
          return a.name.localeCompare(b.name, 'de');
        default:
          return 0;
      }
    });

    return result;
  }, [allResorts, searchQuery, showOpenOnly, selectedCountry, selectedRegion, sortBy]);

  // Pagination / Limit
  const visibleResorts = processedResorts.slice(0, limit);
  // Total matches after filters (before pagination)
  const totalFilteredCount = processedResorts.length;

  // Global stats come directly from backend response (pre-calculated on full dataset)
  // or we could calculate them here if we wanted strictly client-side, 
  // but backend response has "global..." fields which is perfect.

  if (isLoading) return <div className="flex justify-center p-8">Loading data...</div>;
  if (error) return <div className="text-red-500 p-8">Error loading data: {(error as Error).message}</div>;

  const latestDate = allResorts.length > 0 
    ? allResorts.reduce((max, r) => r.lastUpdate > max ? r.lastUpdate : max, allResorts[0].lastUpdate)
    : new Date().toISOString();

  return (
    <div className="min-h-screen bg-background">
      <Header resortCount={data?.globalOpenCount || 0} latestDate={latestDate} />

      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Stats Overview - uses global stats */}
        <section className="animate-fade-in">
          <DashboardStats 
            resorts={allResorts} 
            totalResortsCount={data?.globalTotalCount || 0}
            openResortsCount={data?.globalOpenCount || 0}
            avgSnowMountain={data?.globalAvgSnowMountain || 0}
            totalNewSnow={data?.globalTotalNewSnow || 0}
            totalOpenKm={data?.globalTotalOpenKm || 0}
          />
        </section>

        {/* Charts Row - uses global top resorts */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in" style={{ animationDelay: '100ms' }}>
          <TopResortsChart resorts={data?.topSnowResorts || []} />
          <NewSnowChart resorts={data?.topNewSnowResorts || []} />
          <AvalancheOverview resorts={allResorts} globalDistribution={data?.avalancheDistribution} />
        </section>

        {/* Resort Cards */}
        <section className="animate-fade-in" style={{ animationDelay: '200ms' }}>
          <div className="flex flex-col gap-6 mb-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-foreground">
                Alle Skigebiete 
                <span className="text-muted-foreground text-lg font-normal ml-2">
                  (zeige {visibleResorts.length} von {totalFilteredCount} {totalFilteredCount !== data?.globalTotalCount ? `gefiltert aus ${data?.globalTotalCount}` : ''})
                </span>
              </h2>
            </div>
            
            <FilterBar
              sortBy={sortBy}
              onSortChange={setSortBy}
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery} // Direct update for real-time
              openOnly={showOpenOnly}
              onOpenOnlyChange={setShowOpenOnly}
              selectedCountry={selectedCountry}
              onCountryChange={setSelectedCountry}
              selectedRegion={selectedRegion}
              onRegionChange={setSelectedRegion}
              availableCountries={availableCountries}
              availableRegions={availableRegions}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {visibleResorts.map((resort, index) => (
              <div
                key={resort.id}
                className="animate-fade-in"
                style={{ animationDelay: `${300 + index * 50}ms` }}
              >
                <ResortCard resort={resort} rank={index + 1} />
              </div>
            ))}
          </div>



          {visibleResorts.length < totalFilteredCount && (
            <div className="flex justify-center mt-12">
               <button 
                 onClick={() => setLimit(prev => prev + 50)}
                 className="px-6 py-3 rounded-full bg-primary text-primary-foreground font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all"
               >
                 Mehr anzeigen
               </button>
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-secondary/30 py-6 mt-12">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>Datenquelle: BigQuery (Live Data)</p>
          <p className="mt-1">Stand: {new Date().toLocaleDateString()}</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
