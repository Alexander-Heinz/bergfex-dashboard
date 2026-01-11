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

export const getShredScoreColor = (score: number): string => {
  if (score >= 8) return 'text-emerald-500';
  if (score >= 6) return 'text-amber-500';
  return 'text-orange-500';
};

export const getShredScoreGradient = (score: number): string => {
  if (score >= 8) return 'from-emerald-500 to-teal-500';
  if (score >= 6) return 'from-amber-500 to-orange-500';
  return 'from-orange-500 to-red-500';
};
