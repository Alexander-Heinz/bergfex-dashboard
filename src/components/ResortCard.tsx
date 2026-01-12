import { SkiResort } from '@/types/resort';
import { getSnowConditionIcon, getShredScoreColor } from '@/utils/resortUtils';
import { StatusBadge } from './StatusBadge';
import { AvalancheBadge } from './AvalancheBadge';
import { SnowDepthGauge } from './SnowDepthGauge';
import { ProgressRing } from './ProgressRing';
import { 
  Mountain, 
  Snowflake, 
  Clock, 
  MapPin,
  TrendingUp,
  Activity
} from 'lucide-react';
import { Card } from './ui/card';
import { useState } from 'react';
import { useResortHistory } from '@/hooks/useResortHistory';
import { ResortHistoryChart } from './ResortHistoryChart';

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

  const score = resort.shredScore ? resort.shredScore.toFixed(1) : null;
  const [showHistory, setShowHistory] = useState(false);
  const { data: historyData, loading: historyLoading, error: historyError } = useResortHistory(resort.id, showHistory);

  return (
    <Card className="group relative overflow-visible bg-card border-border shadow-card hover:shadow-card-hover transition-all duration-300 hover:-translate-y-1">
      {/* Shred Score Badge */}
      {score && (
        <div className="absolute top-3 right-3 z-20 group/score cursor-help">
          <div className={`w-14 h-14 rounded-full border-4 bg-background flex flex-col items-center justify-center shadow-lg ${getShredScoreColor(resort.shredScore || 0)} border-current transition-transform group-hover/score:scale-105`}>
            <span className="text-xl font-black leading-none tracking-tighter">{score}</span>
            <span className="text-[7px] font-bold uppercase tracking-wide opacity-80">Score</span>
          </div>
          <span className="absolute -bottom-4 left-1/2 -translate-x-1/2 text-[8px] text-muted-foreground opacity-0 group-hover/score:opacity-100 transition-opacity whitespace-nowrap">Hover für Details</span>
          
          {/* Detailed Score Tooltip */}
          <div className="invisible group-hover/score:visible absolute right-0 top-16 w-60 p-3 bg-popover text-popover-foreground rounded-xl shadow-2xl border border-border z-50 text-xs animate-in fade-in zoom-in-95 duration-200">
            <h5 className="font-bold text-sm border-b border-border/50 pb-2 mb-2 flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <span>Shred Score Details</span>
                <Activity className="w-3 h-3" />
              </div>
              <span className="text-[10px] font-normal text-muted-foreground leading-tight">
                Dein Faktor für perfekte Tage: Neuschnee, Unterlage, Größe & Lawinenwarnstufe.
              </span>
            </h5>
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Freshness (Neuschnee):</span>
                <span className="font-medium bg-secondary px-1.5 py-0.5 rounded">{resort.scoreFreshness?.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Base (Unterlage):</span>
                <span className="font-medium bg-secondary px-1.5 py-0.5 rounded">{resort.scoreBaseSnow?.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Terrain (Größe):</span>
                <span className="font-medium bg-secondary px-1.5 py-0.5 rounded">{resort.scoreTerrain?.toFixed(2)}</span>
              </div>
              <div className="h-px bg-border/50 my-1" />
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Lawinen-Faktor:</span>
                <span className={resort.scoreAvalanchePenalty && resort.scoreAvalanchePenalty < 1 ? "text-destructive font-bold" : "text-emerald-500 font-bold"}>
                  x{resort.scoreAvalanchePenalty?.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground mr-2">Schnee-Faktor:</span>
                <span className="font-bold">x{resort.scoreSnowFactor?.toFixed(2) ?? resort.scoreCondition?.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground mr-2">Pisten-Faktor:</span>
                <span className="font-bold">x{resort.scoreSlopeFactor?.toFixed(2) ?? '-'}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="p-5 pb-3 border-b border-border">
        <div className="flex items-start gap-3">
          {/* Rank Badge Inline */}
          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-secondary/80 flex items-center justify-center text-muted-foreground font-bold text-lg border border-border/50">
            #{rank}
          </div>
          
          <div className="flex-1 min-w-0 pt-0.5">
            <h3 className="font-bold text-lg text-foreground truncate pr-12 leading-tight">{resort.name}</h3>
            <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
              <MapPin className="w-3.5 h-3.5" />
              <span className="truncate">{resort.region}</span>
              <span className="text-xs px-1.5 py-0.5 rounded bg-secondary font-medium flex-shrink-0">
                {resort.country}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center justify-between mt-3">
          <StatusBadge status={resort.status} />
          <span className="text-xs text-muted-foreground">
            Pistenzustand: <span className="text-foreground font-medium">{resort.slopeCondition}</span>
          </span>
        </div>
      </div>

      {/* Snow Section or History */}
      <div className="p-5 border-b border-border bg-gradient-frost min-h-[220px]">
        {!showHistory ? (
          <>
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
          </>
        ) : (
          <div className="flex flex-col h-full animate-in fade-in duration-300">
             <h4 className="font-semibold text-sm text-foreground flex items-center gap-2 mb-2">
                <Activity className="w-4 h-4 text-emerald-500" />
                Saison-Verlauf
              </h4>
             <ResortHistoryChart data={historyData} loading={historyLoading} error={historyError} />
          </div>
        )}
      </div>

      {/* Stats Grid - Only show if not in history mode, or show different stats? 
          Let's hide it in history mode to save space/clean look, or keep it.
          Let's keep it but maybe it looks crowded with the chart if the chart is tall.
          The chart is set to h-[250px], and the snow section had min-h.
          Let's conditionally render Stats Grid only in non-history mode for now.
      */}
      {!showHistory && (
        <div className="p-5 border-b border-border">
          <div className="flex justify-around items-center">
            {(resort.status === 'Geöffnet' || resort.status === 'Teilweise geöffnet') && (resort.liftsOpen === 0 || resort.liftsOpen === null) ? (
               <div className="flex flex-col items-center justify-center h-[72px] w-[72px] text-center">
                 <span className="text-xs text-muted-foreground font-medium">Lifte</span>
                 <span className="text-[10px] leading-tight text-muted-foreground">Keine<br/>Meldung</span>
              </div>
            ) : (
              <ProgressRing
                value={resort.liftsOpen}
                max={resort.liftsTotal}
                label="Lifte"
                size={72}
              />
            )}

            {(resort.status === 'Geöffnet' || resort.status === 'Teilweise geöffnet') && (resort.slopesOpenKm === 0 || resort.slopesOpenKm === null) ? (
              <div className="flex flex-col items-center justify-center h-[72px] w-[72px] text-center">
                 <span className="text-xs text-muted-foreground font-medium">Pisten</span>
                 <span className="text-[10px] leading-tight text-muted-foreground">Keine<br/>Meldung</span>
              </div>
            ) : (
              <ProgressRing
                value={resort.slopesOpenKm}
                max={resort.slopesTotalKm}
                label="km"
                size={72}
              />
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="p-4 flex items-center justify-between bg-secondary/30">
        <div className="flex flex-col gap-1">
          <AvalancheBadge level={resort.avalancheWarning} text={resort.avalancheText} />
          <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
            <Clock className="w-3 h-3" />
            {formatDate(resort.lastUpdate)}
          </div>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
                showHistory 
                ? 'bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20' 
                : 'bg-secondary hover:bg-secondary/80 text-foreground'
            }`}
          >
            {showHistory ? (
              <>
                <Snowflake className="w-3.5 h-3.5" />
                Aktuell
              </>
            ) : (
              <>
                <Activity className="w-3.5 h-3.5" />
                Verlauf
              </>
            )}
          </button>
          
          <a 
            href={resort.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="px-3 py-1.5 rounded-lg bg-primary/10 hover:bg-primary/20 text-primary text-xs font-semibold transition-colors flex items-center gap-1.5"
            title="Auf Bergfex öffnen"
          >
            Bergfex
            <TrendingUp className="w-3.5 h-3.5 rotate-45" />
          </a>
        </div>
      </div>
    </Card>
  );
};
