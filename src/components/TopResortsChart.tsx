import { SkiResort } from '@/data/mockResorts';
import { Card } from './ui/card';
import { Trophy, Snowflake } from 'lucide-react';

interface TopResortsChartProps {
  resorts: SkiResort[];
}

export const TopResortsChart = ({ resorts }: TopResortsChartProps) => {
  const topBySnow = [...resorts]
    .sort((a, b) => b.snowMountain - a.snowMountain)
    .slice(0, 5);

  const maxSnow = topBySnow[0]?.snowMountain || 1;

  return (
    <Card className="p-5 bg-card border-border shadow-card">
      <div className="flex items-center gap-2 mb-5">
        <div className="p-2 rounded-lg bg-alpine-sky/10">
          <Trophy className="w-5 h-5 text-alpine-sky" />
        </div>
        <h3 className="font-bold text-foreground">Top 5 Schneehöhe Berg</h3>
      </div>

      <div className="space-y-3">
        {topBySnow.map((resort, index) => (
          <div key={resort.id} className="group">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className={`
                  w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold
                  ${index === 0 ? 'bg-alpine-amber text-accent-foreground' : 
                    index === 1 ? 'bg-secondary text-secondary-foreground' : 
                    index === 2 ? 'bg-alpine-sunset/20 text-alpine-sunset' : 
                    'bg-muted text-muted-foreground'}
                `}>
                  {index + 1}
                </span>
                <span className="text-sm font-medium text-foreground truncate max-w-[150px]">
                  {resort.name}
                </span>
              </div>
              <div className="flex items-center gap-1 text-sm font-bold text-foreground">
                <Snowflake className="w-3.5 h-3.5 text-alpine-sky" />
                {resort.snowMountain} cm
              </div>
            </div>
            <div className="h-2 bg-secondary rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-alpine-sky to-snow-powder rounded-full transition-all duration-700 ease-out"
                style={{ width: `${(resort.snowMountain / maxSnow) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
