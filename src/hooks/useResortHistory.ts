import { useState, useEffect } from 'react';
import { SkiResort } from '@/types/resort';

export interface ResortHistoryPoint {
  date: string;
  timestamp: string;
  snowMountain: number;
  snowValley: number;
  newSnow: number;
  shredScore: number | null;
  scoreFreshness: number | null;
  scoreBaseSnow: number | null;
  scoreTerrain: number | null;
  scoreConditions: number | null;
  scoreAvalanchePenalty: number | null;
  liftsOpen: number;
  liftsTotal: number;
  slopesOpen: number;
  slopesTotal: number;
}

export const useResortHistory = (resortId: string, isOpen: boolean) => {
  const [data, setData] = useState<ResortHistoryPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen || data.length > 0) return;

    const fetchHistory = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/resorts/${resortId}/history`);
        if (!response.ok) {
          throw new Error('Failed to fetch history');
        }
        const historyData = await response.json();
        setData(historyData);
      } catch (err) {
        console.error(err);
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [resortId, isOpen, data.length]);

  return { data, loading, error };
};
