import { SkiResort } from '@/data/mockResorts';
import { Card } from './ui/card';
import { AlertTriangle } from 'lucide-react';

interface AvalancheOverviewProps {
  resorts: SkiResort[];
  globalDistribution?: Record<string, number>;
}

export const AvalancheOverview = ({ resorts, globalDistribution }: AvalancheOverviewProps) => {
  const avalancheCounts = globalDistribution || resorts.reduce((acc, resort) => {
    acc[resort.avalancheWarning] = (acc[resort.avalancheWarning] || 0) + 1;
    return acc;
  }, {} as Record<number, number>);

  const levels = [
    { level: 1, label: 'Gering', color: 'bg-avalanche-low' },
    { level: 2, label: 'Mäßig', color: 'bg-avalanche-moderate' },
    { level: 3, label: 'Erheblich', color: 'bg-avalanche-considerable' },
    { level: 4, label: 'Groß', color: 'bg-avalanche-high' },
    { level: 5, label: 'Sehr groß', color: 'bg-avalanche-extreme' },
  ];

  const total = levels.reduce((sum, { level }) => sum + (avalancheCounts[level] || 0), 0);

  return (
    <Card className="p-5 bg-card border-border shadow-card">
      <div className="flex items-center gap-2 mb-5">
        <div className="p-2 rounded-lg bg-avalanche-moderate/10">
          <AlertTriangle className="w-5 h-5 text-avalanche-moderate" />
        </div>
        <h3 className="font-bold text-foreground">Lawinenwarnstufen</h3>
      </div>

      <div className="flex h-6 rounded-full overflow-hidden mb-4">
        {levels.map(({ level, color }) => {
          const count = avalancheCounts[level] || 0;
          const width = (count / total) * 100;
          if (width === 0) return null;
          return (
            <div
              key={level}
              className={`${color} transition-all duration-500`}
              style={{ width: `${width}%` }}
            />
          );
        })}
      </div>

      <div className="grid grid-cols-5 gap-2">
        {levels.map(({ level, label, color }) => {
          const count = avalancheCounts[level] || 0;
          return (
            <div key={level} className="text-center">
              <div className={`w-4 h-4 rounded-full ${color} mx-auto mb-1`} />
              <p className="text-xs font-bold text-foreground">{count}</p>
              <p className="text-[10px] text-muted-foreground leading-tight">{label}</p>
            </div>
          );
        })}
      </div>
    </Card>
  );
};
