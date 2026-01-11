import { SkiResort } from '@/types/resort';
import { 
  Mountain, 
  Snowflake, 
  TrendingUp, 
  CheckCircle2,
  MapPin
} from 'lucide-react';
import { Card } from './ui/card';

interface DashboardStatsProps {
  resorts: SkiResort[];
  totalResortsCount?: number;
  openResortsCount?: number;
  avgSnowMountain?: number;
  totalNewSnow?: number;
  totalOpenKm?: number;
}

export const DashboardStats = ({ 
  resorts, 
  totalResortsCount, 
  openResortsCount,
  avgSnowMountain,
  totalNewSnow,
  totalOpenKm 
}: DashboardStatsProps) => {
  // Use passed counts/stats if available (calculated from full DB dataset), 
  // otherwise fallback to list length (legacy behavior)
  const displayOpenCount = openResortsCount ?? resorts.filter(r => r.status === 'Geöffnet').length;
  const displayTotalCount = totalResortsCount ?? resorts.length;

  const displayAvgSnow = avgSnowMountain ?? (resorts.length > 0 ? Math.round(
    resorts.reduce((acc, r) => acc + r.snowMountain, 0) / resorts.length
  ) : 0);
  
  const displayTotalNewSnow = totalNewSnow ?? resorts.reduce((acc, r) => acc + r.newSnow, 0);
  const displayTotalOpenKm = totalOpenKm?.toFixed(1) ?? resorts.reduce((acc, r) => acc + r.slopesOpenKm, 0).toFixed(1);

  const stats = [
    {
      label: 'Geöffnete Gebiete',
      value: `${displayOpenCount}/${displayTotalCount}`,
      icon: CheckCircle2,
      color: 'text-status-open',
      bgColor: 'bg-status-open/10',
    },
    {
      label: 'Ø Schneehöhe Berg',
      value: `${displayAvgSnow} cm`,
      icon: Mountain,
      color: 'text-alpine-sky',
      bgColor: 'bg-alpine-sky/10',
    },
    {
      label: 'Neuschnee gesamt',
      value: `${displayTotalNewSnow} cm`,
      icon: Snowflake,
      color: 'text-snow-fresh',
      bgColor: 'bg-snow-fresh/10',
    },
    {
      label: 'Offene Pistenkilometer',
      value: `${displayTotalOpenKm} km`,
      icon: TrendingUp,
      color: 'text-alpine-amber',
      bgColor: 'bg-alpine-amber/10',
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <Card
          key={stat.label}
          className="p-4 bg-card border-border shadow-card hover:shadow-card-hover transition-all duration-300"
          style={{ animationDelay: `${index * 100}ms` }}
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground font-medium">{stat.label}</p>
              <p className="text-2xl font-bold text-foreground mt-1">{stat.value}</p>
            </div>
            <div className={`p-2.5 rounded-xl ${stat.bgColor}`}>
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
};
