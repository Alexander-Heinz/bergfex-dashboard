import { Mountain, TreePine } from 'lucide-react';

interface SnowDepthGaugeProps {
  valley: number;
  mountain: number;
  maxHeight?: number;
}

export const SnowDepthGauge = ({ valley, mountain, maxHeight = 300 }: SnowDepthGaugeProps) => {
  const valleyPercent = Math.min((valley / maxHeight) * 100, 100);
  const mountainPercent = Math.min((mountain / maxHeight) * 100, 100);

  return (
    <div className="flex items-end justify-center gap-6 h-32">
      {/* Valley */}
      <div className="flex flex-col items-center gap-2">
        <span className="text-lg font-bold text-foreground">{valley} cm</span>
        <div className="relative w-12 h-20 bg-secondary rounded-t-lg overflow-hidden border border-border">
          <div
            className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-alpine-sky to-snow-powder transition-all duration-700 ease-out"
            style={{ height: `${valleyPercent}%` }}
          />
          <div className="absolute inset-0 flex items-center justify-center">
            <TreePine className="w-5 h-5 text-status-open opacity-60" />
          </div>
        </div>
        <span className="text-xs text-muted-foreground font-medium">Tal</span>
      </div>

      {/* Mountain */}
      <div className="flex flex-col items-center gap-2">
        <span className="text-lg font-bold text-foreground">{mountain} cm</span>
        <div className="relative w-12 h-20 bg-secondary rounded-t-lg overflow-hidden border border-border">
          <div
            className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-alpine-sky to-snow-powder transition-all duration-700 ease-out"
            style={{ height: `${mountainPercent}%` }}
          />
          <div className="absolute inset-0 flex items-center justify-center">
            <Mountain className="w-5 h-5 text-primary opacity-60" />
          </div>
        </div>
        <span className="text-xs text-muted-foreground font-medium">Berg</span>
      </div>
    </div>
  );
};
