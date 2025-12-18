import { SkiResort } from '@/data/mockResorts';
import { Card } from './ui/card';
import { CloudSnow } from 'lucide-react';

interface NewSnowChartProps {
  resorts: SkiResort[];
}

export const NewSnowChart = ({ resorts }: NewSnowChartProps) => {
  const resortsWithNewSnow = [...resorts]
    .filter(r => r.newSnow > 0)
    .sort((a, b) => b.newSnow - a.newSnow)
    .slice(0, 5);

  const maxNewSnow = resortsWithNewSnow[0]?.newSnow || 1;

  return (
    <Card className="p-5 bg-card border-border shadow-card">
      <div className="flex items-center gap-2 mb-5">
        <div className="p-2 rounded-lg bg-snow-fresh/10">
          <CloudSnow className="w-5 h-5 text-snow-fresh" />
        </div>
        <h3 className="font-bold text-foreground">Frischer Neuschnee</h3>
      </div>

      <div className="space-y-3">
        {resortsWithNewSnow.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">
            Momentan kein Neuschnee gemeldet
          </p>
        ) : (
          resortsWithNewSnow.map((resort, index) => (
            <div key={resort.id} className="group">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-foreground truncate max-w-[180px]">
                  {resort.name}
                </span>
                <span className="text-sm font-bold text-snow-fresh">
                  +{resort.newSnow} cm
                </span>
              </div>
              <div className="h-2 bg-secondary rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-snow-fresh to-alpine-sky rounded-full transition-all duration-700 ease-out"
                  style={{ width: `${(resort.newSnow / maxNewSnow) * 100}%` }}
                />
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  );
};
