
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  ComposedChart
} from 'recharts';
import { ResortHistoryPoint } from '@/hooks/useResortHistory';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';
import { useState } from 'react';

interface ResortHistoryChartProps {
  data: ResortHistoryPoint[];
  loading: boolean;
  error: string | null;
}

type ViewMode = 'snow' | 'score' | 'lifts' | 'slopes';

const VIEW_CONFIG: Record<ViewMode, { label: string; dataKey: string; unit: string; color: string; gradientId: string }> = {
  snow: { label: 'Schnee', dataKey: 'snowMountain', unit: 'cm', color: '#0ea5e9', gradientId: 'colorSnow' },
  score: { label: 'Score', dataKey: 'shredScore', unit: '', color: '#10b981', gradientId: 'colorScore' },
  lifts: { label: 'Lifte', dataKey: 'liftsOpen', unit: '', color: '#f59e0b', gradientId: 'colorLifts' },
  slopes: { label: 'Pisten', dataKey: 'slopesOpen', unit: 'km', color: '#6366f1', gradientId: 'colorSlopes' },
};

export const ResortHistoryChart = ({ data, loading, error }: ResortHistoryChartProps) => {
  const [viewMode, setViewMode] = useState<ViewMode>('snow');

  if (loading) {
    return (
      <div className="h-[200px] w-full flex items-center justify-center bg-secondary/20 rounded-lg animate-pulse">
        <span className="text-muted-foreground text-sm">Lade Historie...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-[200px] w-full flex items-center justify-center bg-destructive/10 rounded-lg">
        <span className="text-destructive text-sm">Fehler beim Laden der Daten</span>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="h-[200px] w-full flex items-center justify-center bg-secondary/20 rounded-lg">
        <span className="text-muted-foreground text-sm">Keine historischen Daten verfügbar</span>
      </div>
    );
  }

  const formatDate = (dateStr: string) => {
    try {
      return format(new Date(dateStr), 'dd.MM', { locale: de });
    } catch {
      return dateStr;
    }
  };

  const config = VIEW_CONFIG[viewMode];

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const entry = payload[0];
      return (
        <div className="bg-popover border border-border p-2 rounded-lg shadow-lg text-xs">
          <p className="font-bold mb-1">{format(new Date(entry.payload.timestamp), 'dd.MM.yyyy HH:mm')}</p>
          <div className="flex items-center gap-2" style={{ color: config.color }}>
            <span className="font-medium">{config.label}:</span>
            <span>{entry.value?.toFixed(1)} {config.unit}</span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-[220px] flex flex-col">
      {/* Toggle Controls */}
      <div className="flex justify-center gap-1 mb-2 flex-wrap">
        {(Object.keys(VIEW_CONFIG) as ViewMode[]).map((mode) => (
          <button
            key={mode}
            onClick={() => setViewMode(mode)}
            className={`px-2 py-1 text-[10px] rounded transition-colors ${
              viewMode === mode 
              ? 'bg-primary text-primary-foreground font-medium' 
              : 'bg-secondary text-muted-foreground hover:bg-secondary/80'
            }`}
          >
            {VIEW_CONFIG[mode].label}
          </button>
        ))}
      </div>

      <div className="flex-1 min-h-[160px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id={config.gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={config.color} stopOpacity={0.3}/>
                <stop offset="95%" stopColor={config.color} stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.5} />
            <XAxis 
              dataKey="timestamp" 
              tickFormatter={formatDate}
              stroke="hsl(var(--muted-foreground))"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              minTickGap={30}
            />
            <YAxis 
              stroke="hsl(var(--muted-foreground))"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              domain={viewMode === 'score' ? [0, 10] : [0, 'auto']}
              tickFormatter={(v) => `${v}${config.unit ? ` ${config.unit}` : ''}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey={config.dataKey}
              stroke={config.color}
              fillOpacity={1}
              fill={`url(#${config.gradientId})`}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
