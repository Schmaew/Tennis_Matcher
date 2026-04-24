import { useState, useEffect, useCallback } from 'react';
import * as Location from 'expo-location';
import { Court, COURTS } from '@/data/courts';
import { fetchNearbyCourts } from '@/services/courtsService';

interface UseCourtsResult {
  courts: Court[];
  loading: boolean;
  error: string | null;
  isRealData: boolean;
  reload: () => void;
}

/**
 * Custom hook that returns tennis courts.
 *
 * - If EXPO_PUBLIC_GOOGLE_PLACES_API_KEY is set, it requests the user's
 *   location and fetches real nearby courts from Google Places.
 * - If the key is missing, location is denied, or the API call fails,
 *   it falls back silently to the local mock data in data/courts.ts.
 */
export function useCourts(): UseCourtsResult {
  const [courts, setCourts] = useState<Court[]>(COURTS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isRealData, setIsRealData] = useState(false);

  const loadRealCourts = useCallback(async () => {
    const apiKey = process.env.EXPO_PUBLIC_GOOGLE_PLACES_API_KEY;

    if (!apiKey) {
      // No API key configured – use mock data silently
      setCourts(COURTS);
      setIsRealData(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 1. Ask for location permission
      const { status } = await Location.requestForegroundPermissionsAsync();

      if (status !== 'granted') {
        setError('Location permission denied. Showing sample courts.');
        setCourts(COURTS);
        setIsRealData(false);
        setLoading(false);
        return;
      }

      // 2. Get current GPS coordinates
      const position = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });

      // 3. Fetch real courts from Google Places
      const nearbyCourts = await fetchNearbyCourts(
        position.coords.latitude,
        position.coords.longitude
      );

      if (nearbyCourts.length === 0) {
        setError('No tennis courts found nearby. Showing sample courts.');
        setCourts(COURTS);
        setIsRealData(false);
      } else {
        setCourts(nearbyCourts);
        setIsRealData(true);
        setError(null);
      }
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : 'Unknown error occurred.';
      setError(`Could not load nearby courts: ${message}`);
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
