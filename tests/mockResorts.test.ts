import { describe, it, expect } from 'vitest';
import { 
  mockResorts, 
  getAvalancheColor, 
  getStatusColor, 
  getSnowConditionIcon,
  SkiResort 
} from '../src/data/mockResorts';

describe('mockResorts data', () => {
  it('contains resort data', () => {
    expect(mockResorts.length).toBeGreaterThan(0);
  });

  it('each resort has required fields', () => {
    mockResorts.forEach((resort: SkiResort) => {
      expect(resort.id).toBeDefined();
      expect(resort.name).toBeDefined();
      expect(resort.region).toBeDefined();
      expect(resort.country).toMatch(/^(AT|DE)$/);
      expect(resort.status).toBeDefined();
      expect(typeof resort.snowValley).toBe('number');
      expect(typeof resort.snowMountain).toBe('number');
      expect(typeof resort.liftsOpen).toBe('number');
      expect(typeof resort.liftsTotal).toBe('number');
      expect(resort.avalancheWarning).toBeGreaterThanOrEqual(1);
      expect(resort.avalancheWarning).toBeLessThanOrEqual(5);
    });
  });

  it('liftsOpen does not exceed liftsTotal', () => {
    mockResorts.forEach((resort: SkiResort) => {
      expect(resort.liftsOpen).toBeLessThanOrEqual(resort.liftsTotal);
    });
  });

  it('slopesOpen does not exceed slopesTotal', () => {
    mockResorts.forEach((resort: SkiResort) => {
      expect(resort.slopesOpen).toBeLessThanOrEqual(resort.slopesTotal);
      expect(resort.slopesOpenKm).toBeLessThanOrEqual(resort.slopesTotalKm);
    });
  });
});

describe('getAvalancheColor', () => {
  it('returns correct color for each level', () => {
    expect(getAvalancheColor(1)).toBe('avalanche-low');
    expect(getAvalancheColor(2)).toBe('avalanche-moderate');
    expect(getAvalancheColor(3)).toBe('avalanche-considerable');
    expect(getAvalancheColor(4)).toBe('avalanche-high');
    expect(getAvalancheColor(5)).toBe('avalanche-extreme');
  });

  it('returns muted for unknown levels', () => {
    expect(getAvalancheColor(0)).toBe('muted');
    expect(getAvalancheColor(6)).toBe('muted');
  });
});

describe('getStatusColor', () => {
  it('returns correct color for each status', () => {
    expect(getStatusColor('Geöffnet')).toBe('status-open');
    expect(getStatusColor('Geschlossen')).toBe('status-closed');
    expect(getStatusColor('Teilweise geöffnet')).toBe('status-partial');
  });

  it('returns muted for unknown status', () => {
    expect(getStatusColor('unknown')).toBe('muted');
  });
});

describe('getSnowConditionIcon', () => {
  it('returns correct icon for each condition', () => {
    expect(getSnowConditionIcon('Pulver')).toBe('❄️');
    expect(getSnowConditionIcon('Firn')).toBe('🌤️');
    expect(getSnowConditionIcon('Sulz')).toBe('💧');
    expect(getSnowConditionIcon('Kunstschnee')).toBe('🎿');
    expect(getSnowConditionIcon('Griffig')).toBe('✨');
    expect(getSnowConditionIcon('Hart')).toBe('🧊');
  });

  it('returns default icon for unknown condition', () => {
    expect(getSnowConditionIcon('unknown')).toBe('❄️');
  });
});
