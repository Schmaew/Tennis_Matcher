import { Court } from '@/data/courts';
import { supabase } from './supabaseClient';

interface CourtRow {
  id: number;
  province: string | null;
  name_en: string | null;
  name_th: string | null;
  location: string | null;
  google_maps_url: string | null;
  phone: string | null;
  line_id: string | null;
  facebook: string | null;
  gmaps_verified_url: string | null;
  stars: number | null;
  reviews: number | null;
  lat: number | null;
  lng: number | null;
}

const FALLBACK_PHOTO =
  'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=400';

function mapRowToCourt(row: CourtRow): Court {
  const name = row.name_en || row.name_th || 'Unknown Court';
  const address = [row.location, row.province].filter(Boolean).join(', ');

  return {
    id: String(row.id),
    name,
    address: address || 'Thailand',
    photo: FALLBACK_PHOTO,
    photos: [FALLBACK_PHOTO],
    latitude: row.lat ?? 0,
    longitude: row.lng ?? 0,
    courtFee: 0,
    feeUnit: 'contact for pricing',
    numberOfCourts: 1,
    surface: 'Hard Court',
    openingHours: [],
    amenities: [],
    rules: [],
    rating: row.stars ?? 0,
    reviewCount: row.reviews ?? 0,
    phone: row.phone ?? '',
    website: row.gmaps_verified_url ?? row.google_maps_url ?? '',
    description:
      'Tennis court in Thailand. Tap to see contact info and map link.',
    isFavorite: false,
  };
}

export async function fetchCourtsFromSupabase(): Promise<Court[]> {
  if (!supabase) {
    throw new Error(
      'Supabase env vars not set. Add EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY to .env.'
    );
  }

  const { data, error } = await supabase
    .from('courts')
    .select(
      'id, province, name_en, name_th, location, google_maps_url, phone, line_id, facebook, gmaps_verified_url, stars, reviews, lat, lng'
    )
    .order('stars', { ascending: false, nullsFirst: false })
    .limit(100);

  if (error) {
    throw new Error(error.message);
  }

  return (data ?? []).map(mapRowToCourt);
}
