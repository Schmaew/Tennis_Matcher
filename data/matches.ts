export interface Match {
  id: string;
  courtId: string;
  courtName: string;
  organizerId: string;
  organizerName: string;
  organizerPhoto: string;
  date: string;
  time: string;
  duration: number;
  type: 'singles' | 'doubles' | 'group';
  skillRange: string;
  spotsTotal: number;
  spotsFilled: number;
  players: { id: string; name: string; photo: string }[];
  costPerPerson: number;
  totalCost: number;
  description: string;
  status: 'open' | 'full' | 'completed';
}

export const MATCHES: Match[] = [
  {
    id: '1',
    courtId: '1',
    courtName: 'Greenwood Tennis Center',
    organizerId: '1',
    organizerName: 'Sarah Chen',
    organizerPhoto: 'https://i.pravatar.cc/300?img=1',
    date: '2026-04-12',
    time: '9:00 AM',
    duration: 2,
    type: 'doubles',
    skillRange: '3.0 - 4.0',
    spotsTotal: 4,
    spotsFilled: 2,
    players: [
      { id: '1', name: 'Sarah Chen', photo: 'https://i.pravatar.cc/300?img=1' },
      { id: '5', name: 'Emma Davis', photo: 'https://i.pravatar.cc/300?img=9' },
    ],
    costPerPerson: 20,
    totalCost: 80,
    description: 'Friendly doubles match! All levels welcome within range. We\'ll rotate partners each set.',
    status: 'open',
  },
  {
    id: '2',
    courtId: '4',
    courtName: 'Community Park Courts',
    organizerId: '2',
    organizerName: 'Mike Johnson',
    organizerPhoto: 'https://i.pravatar.cc/300?img=3',
    date: '2026-04-13',
    time: '6:00 PM',
    duration: 1.5,
    type: 'singles',
    skillRange: '3.5 - 4.5',
    spotsTotal: 2,
    spotsFilled: 1,
    players: [
      { id: '2', name: 'Mike Johnson', photo: 'https://i.pravatar.cc/300?img=3' },
    ],
    costPerPerson: 11.25,
    totalCost: 22.50,
    description: 'Looking for a competitive singles match. Best of 3 sets. Let\'s get a good workout in!',
    status: 'open',
  },
  {
    id: '3',
    courtId: '2',
    courtName: 'Riverside Public Courts',
    organizerId: '4',
    organizerName: 'James Wilson',
    organizerPhoto: 'https://i.pravatar.cc/300?img=7',
    date: '2026-04-12',
    time: '10:00 AM',
    duration: 2,
    type: 'group',
    skillRange: '3.0 - 5.0',
    spotsTotal: 8,
    spotsFilled: 5,
    players: [
      { id: '4', name: 'James Wilson', photo: 'https://i.pravatar.cc/300?img=7' },
      { id: '1', name: 'Sarah Chen', photo: 'https://i.pravatar.cc/300?img=1' },
      { id: '7', name: 'Rachel Torres', photo: 'https://i.pravatar.cc/300?img=16' },
      { id: '5', name: 'Emma Davis', photo: 'https://i.pravatar.cc/300?img=9' },
      { id: '3', name: 'Lisa Park', photo: 'https://i.pravatar.cc/300?img=5' },
    ],
    costPerPerson: 0,
    totalCost: 0,
    description: 'Weekly Saturday social tennis! We rotate partners and play doubles. Everyone welcome. Free courts!',
    status: 'open',
  },
  {
    id: '4',
    courtId: '3',
    courtName: 'Elite Tennis Academy',
    organizerId: '7',
    organizerName: 'Rachel Torres',
    organizerPhoto: 'https://i.pravatar.cc/300?img=16',
    date: '2026-04-15',
    time: '7:00 PM',
    duration: 1.5,
    type: 'doubles',
    skillRange: '4.0 - 5.0',
    spotsTotal: 4,
    spotsFilled: 4,
    players: [
      { id: '7', name: 'Rachel Torres', photo: 'https://i.pravatar.cc/300?img=16' },
      { id: '2', name: 'Mike Johnson', photo: 'https://i.pravatar.cc/300?img=3' },
      { id: '4', name: 'James Wilson', photo: 'https://i.pravatar.cc/300?img=7' },
      { id: '1', name: 'Sarah Chen', photo: 'https://i.pravatar.cc/300?img=1' },
    ],
    costPerPerson: 22.50,
    totalCost: 90,
    description: 'Competitive doubles practice. USTA league prep.',
    status: 'full',
  },
  {
    id: '5',
    courtId: '5',
    courtName: 'Sunset Tennis Club',
    organizerId: '3',
    organizerName: 'Lisa Park',
    organizerPhoto: 'https://i.pravatar.cc/300?img=5',
    date: '2026-04-14',
    time: '9:00 AM',
    duration: 1,
    type: 'singles',
    skillRange: '2.5 - 3.5',
    spotsTotal: 2,
    spotsFilled: 1,
    players: [
      { id: '3', name: 'Lisa Park', photo: 'https://i.pravatar.cc/300?img=5' },
    ],
    costPerPerson: 17.50,
    totalCost: 35,
    description: 'Casual hitting session. Let\'s work on our groundstrokes!',
    status: 'open',
  },
];
