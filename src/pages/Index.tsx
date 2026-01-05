import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { SkiResort } from '@/data/mockResorts';

interface ResortResponse {
  totalCount: number;
  openCount: number;
  resorts: SkiResort[];
}
import { Header } from '@/components/Header';
import { DashboardStats } from '@/components/DashboardStats';
import { ResortCard } from '@/components/ResortCard';
import { SortControls, SortOption } from '@/components/SortControls';
import { TopResortsChart } from '@/components/TopResortsChart';
import { NewSnowChart } from '@/components/NewSnowChart';
import { AvalancheOverview } from '@/components/AvalancheOverview';

const Index = () => {
  const [sortBy, setSortBy] = useState<SortOption>('snowMountain');

  const { data, isLoading, error } = useQuery({
    queryKey: ['resorts'],
    queryFn: async () => {
      const response = await fetch('/api/resorts');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json() as Promise<ResortResponse>;
    },
  });

  const resorts = data?.resorts || [];
  const totalCount = data?.totalCount || 0;
  const openCount = data?.openCount || 0;

  const sortedResorts = useMemo(() => {
    const sorted = [...resorts].sort((a, b) => {
      switch (sortBy) {
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
    return sorted;
  }, [sortBy, resorts]);

  if (isLoading) return <div className="flex justify-center p-8">Loading...</div>;
  if (error) return <div className="text-red-500 p-8">Error loading data: {(error as Error).message}</div>;

  const latestDate = resorts.length > 0 
    ? resorts.reduce((max, r) => r.lastUpdate > max ? r.lastUpdate : max, resorts[0].lastUpdate)
    : new Date().toISOString();

  return (
    <div className="min-h-screen bg-background">
      <Header resortCount={openCount} latestDate={latestDate} />

      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Stats Overview */}
        <section className="animate-fade-in">
          <DashboardStats 
            resorts={resorts} 
            totalResortsCount={totalCount}
            openResortsCount={openCount}
          />
        </section>

        {/* Charts Row */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in" style={{ animationDelay: '100ms' }}>
          <TopResortsChart resorts={resorts} />
          <NewSnowChart resorts={resorts} />
          <AvalancheOverview resorts={resorts} />
        </section>

        {/* Resort Cards */}
        <section className="animate-fade-in" style={{ animationDelay: '200ms' }}>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
            <h2 className="text-2xl font-bold text-foreground">Alle Skigebiete (zeige {resorts.length} von {totalCount})</h2>
            <SortControls currentSort={sortBy} onSortChange={setSortBy} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {sortedResorts.map((resort, index) => (
              <div
                key={resort.id}
                className="animate-fade-in"
                style={{ animationDelay: `${300 + index * 50}ms` }}
              >
                <ResortCard resort={resort} rank={index + 1} />
              </div>
            ))}
          </div>
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
