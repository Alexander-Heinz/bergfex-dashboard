import { SkiResort, getSnowConditionIcon } from '@/data/mockResorts';
import { StatusBadge } from './StatusBadge';
import { AvalancheBadge } from './AvalancheBadge';
import { SnowDepthGauge } from './SnowDepthGauge';
import { ProgressRing } from './ProgressRing';
import { 
  Mountain, 
  Snowflake, 
  Clock, 
  MapPin,
  TrendingUp
} from 'lucide-react';
import { Card } from './ui/card';

interface ResortCardProps {
  resort: SkiResort;
  rank: number;
}

export const ResortCard = ({ resort, rank }: ResortCardProps) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Card className="group relative overflow-hidden bg-card border-border shadow-card hover:shadow-card-hover transition-all duration-300 hover:-translate-y-1">
      {/* Rank Badge */}
      <div className="absolute top-4 right-4 w-10 h-10 rounded-full bg-gradient-alpine flex items-center justify-center text-primary-foreground font-bold text-lg shadow-lg">
        {rank}
      </div>

      {/* Header */}
      <div className="p-5 pb-3 border-b border-border">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-xl bg-gradient-alpine text-primary-foreground">
            <Mountain className="w-5 h-5" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-lg text-foreground truncate pr-12">{resort.name}</h3>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <MapPin className="w-3.5 h-3.5" />
              <span>{resort.region}</span>
              <span className="text-xs px-1.5 py-0.5 rounded bg-secondary font-medium">
                {resort.country}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center justify-between mt-3">
          <StatusBadge status={resort.status} />
          <span className="text-xs text-muted-foreground">
            {resort.altitude.min}m - {resort.altitude.max}m
          </span>
        </div>
      </div>

      {/* Snow Section */}
      <div className="p-5 border-b border-border bg-gradient-frost">
        <div className="flex items-center justify-between mb-4">
          <h4 className="font-semibold text-sm text-foreground flex items-center gap-2">
            <Snowflake className="w-4 h-4 text-alpine-sky" />
            Schneehöhen
          </h4>
          {resort.newSnow > 0 && (
            <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-snow-fresh/20 text-snow-fresh text-xs font-semibold">
              <TrendingUp className="w-3 h-3" />
              +{resort.newSnow} cm Neuschnee
            </div>
          )}
        </div>
        <SnowDepthGauge valley={resort.snowValley} mountain={resort.snowMountain} />
        <div className="flex items-center justify-center gap-4 mt-4 text-sm">
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <span>{getSnowConditionIcon(resort.snowCondition)}</span>
            <span className="font-medium text-foreground">{resort.snowCondition}</span>
          </span>
          <span className="text-muted-foreground">•</span>
          <span className="text-muted-foreground">
            Letzter Schneefall: <span className="font-medium text-foreground">{resort.lastSnowfall}</span>
          </span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="p-5 border-b border-border">
        <div className="flex justify-around">
          <ProgressRing
            value={resort.liftsOpen}
            max={resort.liftsTotal}
            label="Lifte"
            size={72}
          />
          <ProgressRing
            value={resort.slopesOpen}
            max={resort.slopesTotal}
            label="Pisten"
            size={72}
          />
          <ProgressRing
            value={resort.slopesOpenKm}
            max={resort.slopesTotalKm}
            label="km"
            size={72}
          />
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 flex items-center justify-between bg-secondary/30">
        <AvalancheBadge level={resort.avalancheWarning} text={resort.avalancheText} />
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Clock className="w-3.5 h-3.5" />
          {formatDate(resort.lastUpdate)}
        </div>
      </div>
    </Card>
  );
};
