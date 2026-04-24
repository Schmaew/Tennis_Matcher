import { Court } from '@/data/courts';

const API_KEY = process.env.EXPO_PUBLIC_GOOGLE_PLACES_API_KEY ?? '';
const BASE_URL = 'https://maps.googleapis.com/maps/api/place';

// Shape of a single result from Google Places Nearby Search
interface PlacesResult {
  place_id: string;
  name: string;
  vicinity: string;
  geometry: { location: { lat: number; lng: number } };
  rating?: number;
  user_ratings_total?: number;
  photos?: { photo_reference: string }[];
}

interface PlacesResponse {
  status: string;
  results: PlacesResult[];
  error_message?: string;
}

function buildPhotoUrl(photoReference: string): string {
  return `${BASE_URL}/photo?maxwidth=400&photoreference=${photoReference}&key=${API_KEY}`;
}

function mapPlaceToCourt(place: PlacesResult): Court {
  const fallbackPhoto =
    'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=400';
  const photos =
    place.photos?.map((p) => buildPhotoUrl(p.photo_reference)) ?? [];

  return {
    id: place.place_id,
    name: place.name,
    address: place.vicinity,
    photo: photos[0] ?? fallbackPhoto,
    photos: photos.length > 0 ? photos : [fallbackPhoto],
    latitude: place.geometry.location.lat,
    longitude: place.geometry.location.lng,
    courtFee: 0,
    feeUnit: 'contact for pricing',
    numberOfCourts: 1,
    surface: 'Hard Court',
    openingHours: [],
    amenities: [],
    rules: [],
    rating: place.rating ?? 0,
    reviewCount: place.user_ratings_total ?? 0,
    phone: '',
    website: '',
    description: 'Real nearby tennis court. Tap to see more on Google Maps.',
    isFavorite: false,
  };
}

/**
 * Fetches tennis courts near the given coordinates using Google Places Nearby Search.
 * Requires EXPO_PUBLIC_GOOGLE_PLACES_API_KEY to be set in your .env file.
 *
 * @param latitude  - User's current latitude
 * @param longitude - User's current longitude
 * @param radiusMeters - Search radius in metres (default: 5000 = 5 km)
 */
export async function fetchNearbyCourts(
  latitude: number,
  longitude: number,
  radiusMeters = 5000
): Promise<Court[]> {
  if (!API_KEY) {
    throw new Error('EXPO_PUBLIC_GOOGLE_PLACES_API_KEY is not set.');
  }

  const url =
    `${BASE_URL}/nearbysearch/json` +
    `?location=${latitude},${longitude}` +
    `&radius=${radiusMeters}` +
    `&type=tennis_court` +
    `&key=${API_KEY}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}`);
  }

  const data: PlacesResponse = await response.json();

  if (data.status !== 'OK' && data.status !== 'ZERO_RESULTS') {
    throw new Error(data.error_message ?? `Places API error: ${data.status}`);
  }

  return data.results.map(mapPlaceToCourt);
}
