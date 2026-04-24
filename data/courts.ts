export interface Court {
  id: string;
  name: string;
  address: string;
  photo: string;
  photos: string[];
  latitude: number;
  longitude: number;
  courtFee: number;
  feeUnit: string;
  numberOfCourts: number;
  surface: string;
  openingHours: { day: string; open: string; close: string }[];
  amenities: string[];
  rules: string[];
  rating: number;
  reviewCount: number;
  phone: string;
  website: string;
  description: string;
  isFavorite: boolean;
}

export const COURTS: Court[] = [
  {
    id: '1',
    name: 'Greenwood Tennis Center',
    address: '123 Park Avenue, Downtown',
    photo: 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=400',
    photos: [
      'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=400',
      'https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?w=400',
    ],
    latitude: 37.7749,
    longitude: -122.4194,
    courtFee: 40,
    feeUnit: 'per hour',
    numberOfCourts: 8,
    surface: 'Hard Court',
    openingHours: [
      { day: 'Monday - Friday', open: '6:00 AM', close: '10:00 PM' },
      { day: 'Saturday', open: '7:00 AM', close: '9:00 PM' },
      { day: 'Sunday', open: '7:00 AM', close: '8:00 PM' },
    ],
    amenities: ['toilets', 'showers', 'snackBar', 'parking', 'proShop', 'lighting', 'waterFountain', 'lockers'],
    rules: [
      'Proper tennis attire required',
      'Non-marking shoes only',
      'Maximum 2-hour booking per session',
      'Cancel at least 24 hours in advance for refund',
      'No food or drinks on courts (water only)',
      'Guests must check in at front desk',
    ],
    rating: 4.5,
    reviewCount: 128,
    phone: '(555) 123-4567',
    website: 'https://greenwoodtennis.com',
    description: 'Premier tennis facility with 8 well-maintained hard courts. Full amenities including pro shop, locker rooms, and a snack bar. Great for all levels.',
    isFavorite: false,
  },
  {
    id: '2',
    name: 'Riverside Public Courts',
    address: '456 River Road, Westside',
    photo: 'https://images.unsplash.com/photo-1551773188-d63e5d26426e?w=400',
    photos: [
      'https://images.unsplash.com/photo-1551773188-d63e5d26426e?w=400',
    ],
    latitude: 37.7849,
    longitude: -122.4094,
    courtFee: 0,
    feeUnit: 'free',
    numberOfCourts: 4,
    surface: 'Hard Court',
    openingHours: [
      { day: 'Monday - Sunday', open: '6:00 AM', close: 'Sunset' },
    ],
    amenities: ['toilets', 'parking', 'waterFountain'],
    rules: [
      'First come, first served',
      'Limit play to 1 hour when others are waiting',
      'No reservations — walk-up only',
      'Clean up after yourself',
    ],
    rating: 3.8,
    reviewCount: 64,
    phone: '(555) 234-5678',
    website: '',
    description: 'Free public courts along the river. Great for casual play. Courts can get busy on weekends — arrive early!',
    isFavorite: true,
  },
  {
    id: '3',
    name: 'Elite Tennis Academy',
    address: '789 Champion Blvd, Northside',
    photo: 'https://images.unsplash.com/photo-1530915534534-9d16e720c045?w=400',
    photos: [
      'https://images.unsplash.com/photo-1530915534534-9d16e720c045?w=400',
    ],
    latitude: 37.7949,
    longitude: -122.4294,
    courtFee: 60,
    feeUnit: 'per hour',
    numberOfCourts: 12,
    surface: 'Clay',
    openingHours: [
      { day: 'Monday - Friday', open: '5:30 AM', close: '11:00 PM' },
      { day: 'Saturday - Sunday', open: '6:00 AM', close: '10:00 PM' },
    ],
    amenities: ['toilets', 'showers', 'snackBar', 'parking', 'proShop', 'lighting', 'waterFountain', 'lockers'],
    rules: [
      'Membership or day pass required',
      'Clay court shoes recommended',
      'Water the courts after use',
      'Maximum 1.5-hour booking during peak hours',
      'Coaching sessions must be booked through front desk',
      'No outside coaching allowed',
    ],
    rating: 4.8,
    reviewCount: 256,
    phone: '(555) 345-6789',
    website: 'https://elitetennis.com',
    description: '12 beautifully maintained clay courts. Home to the city\'s top junior and adult programs. Premium facility with full amenities.',
    isFavorite: false,
  },
  {
    id: '4',
    name: 'Community Park Courts',
    address: '321 Oak Street, Eastside',
    photo: 'https://images.unsplash.com/photo-1599586120429-48281b6f0ece?w=400',
    photos: [
      'https://images.unsplash.com/photo-1599586120429-48281b6f0ece?w=400',
    ],
    latitude: 37.7649,
    longitude: -122.3994,
    courtFee: 15,
    feeUnit: 'per hour',
    numberOfCourts: 6,
    surface: 'Hard Court',
    openingHours: [
      { day: 'Monday - Friday', open: '7:00 AM', close: '9:00 PM' },
      { day: 'Saturday - Sunday', open: '7:00 AM', close: '7:00 PM' },
    ],
    amenities: ['toilets', 'parking', 'lighting', 'waterFountain'],
    rules: [
      'Book online or call ahead',
      'Non-marking shoes required',
      '2-hour maximum during weekends',
      'No glass containers',
    ],
    rating: 4.1,
    reviewCount: 89,
    phone: '(555) 456-7890',
    website: 'https://communitypark.org/tennis',
    description: 'Affordable community courts in a beautiful park setting. Recently resurfaced with LED lighting for evening play.',
    isFavorite: false,
  },
  {
    id: '5',
    name: 'Sunset Tennis Club',
    address: '567 Hilltop Drive, Southside',
    photo: 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400',
    photos: [
      'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400',
    ],
    latitude: 37.7549,
    longitude: -122.4394,
    courtFee: 35,
    feeUnit: 'per hour',
    numberOfCourts: 5,
    surface: 'Artificial Grass',
    openingHours: [
      { day: 'Monday - Friday', open: '6:30 AM', close: '9:30 PM' },
      { day: 'Saturday', open: '7:00 AM', close: '8:00 PM' },
      { day: 'Sunday', open: '8:00 AM', close: '6:00 PM' },
    ],
    amenities: ['toilets', 'showers', 'parking', 'lighting', 'lockers'],
    rules: [
      'Members get priority booking',
      'Guest fee: $10 per visit',
      'Proper tennis attire required',
      'No coaching without permission',
    ],
    rating: 4.3,
    reviewCount: 72,
    phone: '(555) 567-8901',
    website: 'https://sunsettennisclub.com',
    description: 'Boutique tennis club with 5 artificial grass courts. Beautiful views and a friendly community atmosphere.',
    isFavorite: true,
  },
];
