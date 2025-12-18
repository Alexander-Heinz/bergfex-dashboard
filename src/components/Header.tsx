import { Mountain, Snowflake } from 'lucide-react';

export const Header = () => {
  return (
    <header className="relative overflow-hidden bg-gradient-alpine text-primary-foreground">
      {/* Decorative snowflakes */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(12)].map((_, i) => (
          <Snowflake
            key={i}
            className="absolute text-primary-foreground/10 animate-snowfall"
            style={{
              left: `${Math.random() * 100}%`,
              top: `-20px`,
              animationDuration: `${8 + Math.random() * 8}s`,
              animationDelay: `${Math.random() * 5}s`,
              width: `${12 + Math.random() * 16}px`,
              height: `${12 + Math.random() * 16}px`,
            }}
          />
        ))}
      </div>

      <div className="container mx-auto px-4 py-8 relative z-10">
        <div className="flex items-center justify-center gap-4">
          <div className="p-3 rounded-2xl bg-primary-foreground/10 backdrop-blur-sm">
            <Mountain className="w-10 h-10" />
          </div>
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
              Alpen Schnee Radar
            </h1>
            <p className="text-primary-foreground/80 mt-1 text-sm md:text-base">
              Live Schneebericht für Skigebiete in Deutschland & Österreich
            </p>
          </div>
        </div>
      </div>

      {/* Mountain silhouette */}
      <svg
        className="absolute bottom-0 left-0 right-0 w-full h-12 text-background"
        viewBox="0 0 1440 48"
        preserveAspectRatio="none"
      >
        <path
          fill="currentColor"
          d="M0,48 L0,24 Q180,0 360,24 T720,12 T1080,20 T1440,16 L1440,48 Z"
        />
      </svg>
    </header>
  );
};
