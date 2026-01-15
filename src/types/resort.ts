export interface SkiResort {
  id: string;
  name: string;
  region: string;
  country: string;
  status: 'Geöffnet' | 'Geschlossen' | 'Teilweise geöffnet';
  snowValley: number;
  snowMountain: number;
  newSnow: number;
  snowCondition: string;
  lastSnowfall: string;
  avalancheWarning: number;
  avalancheText: string;
  liftsOpen: number;
  liftsTotal: number;
  slopesOpenKm: number;
  slopesTotalKm: number;
  slopesOpen: number;
  slopesTotal: number;
  slopeCondition: string;
  lastUpdate: string;
  altitude: {
    min: number;
    max: number;
  };
  url: string;
  latitude?: number;
  longitude?: number;
  // Shred Score
  shredScore?: number;
  scoreFreshness?: number;
  scoreBaseSnow?: number;
  scoreTerrain?: number;
  scoreSnowFactor?: number;
  scoreSlopeFactor?: number;
  scoreCondition?: number;
  scoreAvalanchePenalty?: number;
}
