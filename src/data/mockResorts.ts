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
}

export const mockResorts: SkiResort[] = [
  {
    id: '1',
    name: 'St. Anton am Arlberg',
    region: 'Tirol',
    country: 'AT',
    status: 'Geöffnet',
    snowValley: 45,
    snowMountain: 185,
    newSnow: 25,
    snowCondition: 'Pulver',
    lastSnowfall: '17.12.',
    avalancheWarning: 3,
    avalancheText: 'Erheblich',
    liftsOpen: 82,
    liftsTotal: 88,
    slopesOpenKm: 285,
    slopesTotalKm: 305,
    slopesOpen: 142,
    slopesTotal: 150,
    slopeCondition: 'Sehr gut',
    lastUpdate: '2024-12-18 08:30:00',
    altitude: { min: 1304, max: 2811 },
    url: 'https://www.bergfex.at/st-anton-am-arlberg/',
  },
  {
    id: '2',
    name: 'Kitzbühel',
    region: 'Tirol',
    country: 'AT',
    status: 'Geöffnet',
    snowValley: 30,
    snowMountain: 120,
    newSnow: 10,
    snowCondition: 'Griffig',
    lastSnowfall: '16.12.',
    avalancheWarning: 2,
    avalancheText: 'Mäßig',
    liftsOpen: 51,
    liftsTotal: 57,
    slopesOpenKm: 165,
    slopesTotalKm: 188,
    slopesOpen: 78,
    slopesTotal: 85,
    slopeCondition: 'Gut',
    lastUpdate: '2024-12-18 07:45:00',
    altitude: { min: 800, max: 2000 },
    url: 'https://www.bergfex.at/kitzbuehel/',
  },
  {
    id: '3',
    name: 'Sölden',
    region: 'Tirol',
    country: 'AT',
    status: 'Geöffnet',
    snowValley: 55,
    snowMountain: 210,
    newSnow: 35,
    snowCondition: 'Pulver',
    lastSnowfall: '17.12.',
    avalancheWarning: 3,
    avalancheText: 'Erheblich',
    liftsOpen: 31,
    liftsTotal: 34,
    slopesOpenKm: 138,
    slopesTotalKm: 144,
    slopesOpen: 68,
    slopesTotal: 71,
    slopeCondition: 'Sehr gut',
    lastUpdate: '2024-12-18 08:00:00',
    altitude: { min: 1350, max: 3340 },
    url: 'https://www.bergfex.at/soelden/',
  },
  {
    id: '4',
    name: 'Ischgl',
    region: 'Tirol',
    country: 'AT',
    status: 'Geöffnet',
    snowValley: 40,
    snowMountain: 165,
    newSnow: 20,
    snowCondition: 'Pulver',
    lastSnowfall: '17.12.',
    avalancheWarning: 2,
    avalancheText: 'Mäßig',
    liftsOpen: 41,
    liftsTotal: 45,
    slopesOpenKm: 225,
    slopesTotalKm: 239,
    slopesOpen: 112,
    slopesTotal: 118,
    slopeCondition: 'Sehr gut',
    lastUpdate: '2024-12-18 08:15:00',
    altitude: { min: 1400, max: 2872 },
    url: 'https://www.bergfex.at/ischgl/',
  },
  {
    id: '5',
    name: 'Oberstdorf-Kleinwalsertal',
    region: 'Bayern / Vorarlberg',
    country: 'DE',
    status: 'Geöffnet',
    snowValley: 25,
    snowMountain: 95,
    newSnow: 15,
    snowCondition: 'Griffig',
    lastSnowfall: '16.12.',
    avalancheWarning: 2,
    avalancheText: 'Mäßig',
    liftsOpen: 42,
    liftsTotal: 48,
    slopesOpenKm: 115,
    slopesTotalKm: 130,
    slopesOpen: 58,
    slopesTotal: 65,
    slopeCondition: 'Gut',
    lastUpdate: '2024-12-18 07:30:00',
    altitude: { min: 828, max: 2224 },
    url: 'https://www.bergfex.at/oberstdorf-kleinwalsertal/',
  },
  {
    id: '6',
    name: 'Garmisch-Partenkirchen',
    region: 'Bayern',
    country: 'DE',
    status: 'Teilweise geöffnet',
    snowValley: 15,
    snowMountain: 85,
    newSnow: 5,
    snowCondition: 'Kunstschnee',
    lastSnowfall: '15.12.',
    avalancheWarning: 1,
    avalancheText: 'Gering',
    liftsOpen: 28,
    liftsTotal: 38,
    slopesOpenKm: 35,
    slopesTotalKm: 60,
    slopesOpen: 22,
    slopesTotal: 35,
    slopeCondition: 'Mäßig',
    lastUpdate: '2024-12-18 08:00:00',
    altitude: { min: 708, max: 2720 },
    url: 'https://www.bergfex.at/garmisch-partenkirchen/',
  },
  {
    id: '7',
    name: 'Zell am See - Kaprun',
    region: 'Salzburg',
    country: 'AT',
    status: 'Geöffnet',
    snowValley: 35,
    snowMountain: 195,
    newSnow: 30,
    snowCondition: 'Pulver',
    lastSnowfall: '17.12.',
    avalancheWarning: 3,
    avalancheText: 'Erheblich',
    liftsOpen: 52,
    liftsTotal: 54,
    slopesOpenKm: 118,
    slopesTotalKm: 138,
    slopesOpen: 62,
    slopesTotal: 68,
    slopeCondition: 'Sehr gut',
    lastUpdate: '2024-12-18 08:20:00',
    altitude: { min: 757, max: 3029 },
    url: 'https://www.bergfex.at/zell-am-see-kaprun/',
  },
  {
    id: '8',
    name: 'Mayrhofen',
    region: 'Tirol',
    country: 'AT',
    status: 'Geöffnet',
    snowValley: 20,
    snowMountain: 140,
    newSnow: 18,
    snowCondition: 'Firn',
    lastSnowfall: '16.12.',
    avalancheWarning: 2,
    avalancheText: 'Mäßig',
    liftsOpen: 55,
    liftsTotal: 58,
    slopesOpenKm: 128,
    slopesTotalKm: 142,
    slopesOpen: 64,
    slopesTotal: 70,
    slopeCondition: 'Gut',
    lastUpdate: '2024-12-18 07:50:00',
    altitude: { min: 630, max: 2500 },
    url: 'https://www.bergfex.at/mayrhofen/',
  },
  {
    id: '9',
    name: 'Lech Zürs',
    region: 'Vorarlberg',
    country: 'AT',
    status: 'Geöffnet',
    snowValley: 50,
    snowMountain: 175,
    newSnow: 28,
    snowCondition: 'Pulver',
    lastSnowfall: '17.12.',
    avalancheWarning: 3,
    avalancheText: 'Erheblich',
    liftsOpen: 85,
    liftsTotal: 88,
    slopesOpenKm: 295,
    slopesTotalKm: 305,
    slopesOpen: 145,
    slopesTotal: 150,
    slopeCondition: 'Sehr gut',
    lastUpdate: '2024-12-18 08:25:00',
    altitude: { min: 1450, max: 2811 },
    url: 'https://www.bergfex.at/lech-zuers/',
  },
  {
    id: '10',
    name: 'Stubaier Gletscher',
    region: 'Tirol',
    country: 'AT',
    status: 'Geöffnet',
    snowValley: 0,
    snowMountain: 245,
    newSnow: 40,
    snowCondition: 'Pulver',
    lastSnowfall: '17.12.',
    avalancheWarning: 2,
    avalancheText: 'Mäßig',
    liftsOpen: 22,
    liftsTotal: 24,
    slopesOpenKm: 58,
    slopesTotalKm: 65,
    slopesOpen: 32,
    slopesTotal: 35,
    slopeCondition: 'Sehr gut',
    lastUpdate: '2024-12-18 08:10:00',
    altitude: { min: 1750, max: 3210 },
    url: 'https://www.bergfex.at/stubaier-gletscher/',
  },
];

export const getAvalancheColor = (level: number): string => {
  switch (level) {
    case 1: return 'avalanche-low';
    case 2: return 'avalanche-moderate';
    case 3: return 'avalanche-considerable';
    case 4: return 'avalanche-high';
    case 5: return 'avalanche-extreme';
    default: return 'muted';
  }
};

export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'Geöffnet': return 'status-open';
    case 'Geschlossen': return 'status-closed';
    case 'Teilweise geöffnet': return 'status-partial';
    default: return 'muted';
  }
};

export const getSnowConditionIcon = (condition: string): string => {
  switch (condition) {
    case 'Pulver': return '❄️';
    case 'Firn': return '🌤️';
    case 'Sulz': return '💧';
    case 'Kunstschnee': return '🎿';
    case 'Griffig': return '✨';
    case 'Hart': return '🧊';
    default: return '❄️';
  }
};
