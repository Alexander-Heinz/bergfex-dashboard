import { SkiResort } from '@/data/mockResorts';
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
}

export const DashboardStats = ({ resorts }: DashboardStatsProps) => {
  const openResorts = resorts.filter(r => r.status === 'Geöffnet').length;
  const totalResorts = resorts.length;
  const avgSnowMountain = Math.round(
    resorts.reduce((acc, r) => acc + r.snowMountain, 0) / resorts.length
  );
  const totalNewSnow = resorts.reduce((acc, r) => acc + r.newSnow, 0);
  const totalOpenKm = resorts.reduce((acc, r) => acc + r.slopesOpenKm, 0).toFixed(1);

  const stats = [
    {
      label: 'Geöffnete Gebiete',
      value: `${openResorts}/${totalResorts}`,
      icon: CheckCircle2,
      color: 'text-status-open',
      bgColor: 'bg-status-open/10',
    },
    {
      label: 'Ø Schneehöhe Berg',
      value: `${avgSnowMountain} cm`,
      icon: Mountain,
      color: 'text-alpine-sky',
      bgColor: 'bg-alpine-sky/10',
    },
    {
      label: 'Neuschnee gesamt',
      value: `${totalNewSnow} cm`,
      icon: Snowflake,
      color: 'text-snow-fresh',
      bgColor: 'bg-snow-fresh/10',
    },
    {
      label: 'Offene Pistenkilometer',
      value: `${totalOpenKm} km`,
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
