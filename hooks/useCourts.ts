import { useState, useEffect, useCallback } from 'react';
import { Court, COURTS } from '@/data/courts';
import { fetchCourtsFromSupabase } from '@/services/courtsSupabaseService';

interface UseCourtsResult {
  courts: Court[];
  loading: boolean;
  error: string | null;
  isRealData: boolean;
  reload: () => void;
}

/**
 * Returns tennis courts from Supabase. Falls back to mock data
 * if Supabase env vars are missing or the query fails.
 */
export function useCourts(): UseCourtsResult {
  const [courts, setCourts] = useState<Court[]>(COURTS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isRealData, setIsRealData] = useState(false);

  const loadRealCourts = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const realCourts = await fetchCourtsFromSupabase();

      if (realCourts.length === 0) {
        setError('No courts found in database. Showing sample courts.');
        setCourts(COURTS);
        setIsRealData(false);
      } else {
        setCourts(realCourts);
        setIsRealData(true);
      }
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : 'Unknown error occurred.';
      setError(`Could not load courts: ${message}`);
      setCourts(COURTS);
      setIsRealData(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadRealCourts();
  }, [loadRealCourts]);

  return {
    courts,
    loading,
    error,
    isRealData,
    reload: loadRealCourts,
  };
}
