import { Mountain, MapPin, Thermometer } from 'lucide-react';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';

interface HeaderProps {
  resortCount: number;
  latestDate: string;
}

export const Header = ({ resortCount, latestDate }: HeaderProps) => {
  const formattedDate = latestDate 
    ? format(new Date(latestDate), 'MMMM yyyy', { locale: de })
    : format(new Date(), 'MMMM yyyy', { locale: de });

  return (
    <header className="relative overflow-hidden bg-gradient-alpine min-h-[200px] md:min-h-[240px]">
      {/* Background layers for depth */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-alpine-deep/40" />
      
      {/* Subtle grid pattern overlay */}
      <div 
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, white 1px, transparent 0)`,
          backgroundSize: '24px 24px'
        }}
      />

      {/* Content */}
      <div className="container mx-auto px-4 pt-8 pb-20 md:pt-10 md:pb-24 relative z-10">
        <div className="flex flex-col items-center text-center">
          {/* Logo/Icon */}
          <div className="relative mb-4">
            <div className="absolute inset-0 bg-primary-foreground/20 blur-xl rounded-full scale-150" />
            <div className="relative p-4 rounded-2xl bg-primary-foreground/10 backdrop-blur-sm border border-primary-foreground/20">
              <Mountain className="w-10 h-10 md:w-12 md:h-12 text-primary-foreground" />
            </div>
          </div>

          {/* Title */}
          <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-primary-foreground drop-shadow-lg">
            Alpen Schnee Radar
          </h1>
          
          {/* Subtitle */}
          <p className="text-primary-foreground/90 mt-2 text-sm md:text-lg font-medium max-w-md">
            Live Schneebericht für Skigebiete in den Alpen
          </p>

          {/* Quick stats pills */}
          <div className="flex flex-wrap items-center justify-center gap-3 mt-5">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-primary-foreground/10 backdrop-blur-sm border border-primary-foreground/20 text-primary-foreground text-xs md:text-sm">
              <MapPin className="w-3.5 h-3.5" />
              <span>{resortCount} Skigebiete</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-primary-foreground/10 backdrop-blur-sm border border-primary-foreground/20 text-primary-foreground text-xs md:text-sm">
              <Thermometer className="w-3.5 h-3.5" />
              <span>Aktuell: {formattedDate}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Mountain silhouette layers - creates depth */}
      <div className="absolute bottom-0 left-0 right-0 pointer-events-none">
        {/* Back mountain layer - lighter */}
        <svg
          className="absolute bottom-8 left-0 right-0 w-full h-24 md:h-32 text-primary-foreground/5"
          viewBox="0 0 1440 120"
          preserveAspectRatio="none"
        >
          <path
            fill="currentColor"
            d="M0,120 L0,80 Q120,20 240,60 T480,30 T720,50 T960,25 T1200,55 T1440,40 L1440,120 Z"
          />
        </svg>

        {/* Middle mountain layer */}
        <svg
          className="absolute bottom-4 left-0 right-0 w-full h-20 md:h-28 text-primary-foreground/8"
          viewBox="0 0 1440 100"
          preserveAspectRatio="none"
        >
          <path
            fill="currentColor"
            d="M0,100 L0,70 L180,30 L320,65 L480,15 L600,50 L780,10 L900,45 L1080,20 L1200,55 L1320,25 L1440,50 L1440,100 Z"
          />
        </svg>

        {/* Front mountain silhouette - darker, more defined */}
        <svg
          className="relative w-full h-16 md:h-20 text-background"
          viewBox="0 0 1440 80"
          preserveAspectRatio="none"
        >
          <path
            fill="currentColor"
            d="M0,80 L0,50 L100,35 L200,55 L350,15 L450,40 L550,20 L700,45 L850,10 L950,35 L1100,18 L1200,42 L1300,25 L1440,45 L1440,80 Z"
          />
          {/* Snow caps on peaks */}
          <path
            fill="currentColor"
            fillOpacity="0.95"
            d="M340,20 L350,15 L360,20 L355,22 L345,22 Z M840,15 L850,10 L860,15 L855,17 L845,17 Z M1090,23 L1100,18 L1110,23 L1105,25 L1095,25 Z"
          />
        </svg>
      </div>

      {/* Decorative elements */}
      <div className="absolute top-6 left-8 w-2 h-2 rounded-full bg-primary-foreground/30 animate-pulse" />
      <div className="absolute top-12 left-16 w-1.5 h-1.5 rounded-full bg-primary-foreground/20 animate-pulse" style={{ animationDelay: '0.5s' }} />
      <div className="absolute top-8 right-12 w-2 h-2 rounded-full bg-primary-foreground/25 animate-pulse" style={{ animationDelay: '1s' }} />
      <div className="absolute top-16 right-20 w-1 h-1 rounded-full bg-primary-foreground/20 animate-pulse" style={{ animationDelay: '1.5s' }} />
    </header>
  );
};

