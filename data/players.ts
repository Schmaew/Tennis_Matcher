export interface Player {
  id: string;
  name: string;
  age: number;
  photo: string;
  photos: string[];
  skillLevel: string;
  bio: string;
  lookingFor: string[];
  playStyle: string[];
  groupSize: number;
  availability: { day: string; timeSlot: string }[];
  location: string;
  distance: number;
  isAvailableNow: boolean;
  endorsements: Endorsement[];
  matchesPlayed: number;
}

export interface Endorsement {
  id: string;
  fromPlayerId: string;
  fromPlayerName: string;
  fromPlayerPhoto: string;
  type: 'skill' | 'sportsmanship' | 'punctuality' | 'friendliness';
  comment: string;
  date: string;
}

export const CURRENT_USER: Player = {
  id: 'current',
  name: 'You',
  age: 28,
  photo: 'https://i.pravatar.cc/300?img=11',
  photos: ['https://i.pravatar.cc/300?img=11'],
  skillLevel: '3.5',
  bio: 'Weekend warrior looking for fun rallies!',
  lookingFor: ['Singles Partner', 'Doubles Partner'],
  playStyle: ['Casual/Social'],
  groupSize: 1,
  availability: [
    { day: 'Saturday', timeSlot: 'Morning' },
    { day: 'Sunday', timeSlot: 'Morning' },
    { day: 'Wednesday', timeSlot: 'Evening' },
  ],
  location: 'Downtown',
  distance: 0,
  isAvailableNow: true,
  endorsements: [],
  matchesPlayed: 12,
};

export const PLAYERS: Player[] = [
  {
    id: '1',
    name: 'Sarah Chen',
    age: 26,
    photo: 'https://i.pravatar.cc/300?img=1',
    photos: ['https://i.pravatar.cc/300?img=1', 'https://i.pravatar.cc/300?img=21'],
    skillLevel: '3.5',
    bio: 'Love playing doubles on weekends! Been playing for 3 years. Always looking for fun rallies and good vibes on the court.',
    lookingFor: ['Doubles Partner', 'Group/Social Play'],
    playStyle: ['Casual/Social', 'Hitting Partner'],
    groupSize: 2,
    availability: [
      { day: 'Saturday', timeSlot: 'Morning' },
      { day: 'Sunday', timeSlot: 'Afternoon' },
    ],
    location: 'Westside',
    distance: 2.3,
    isAvailableNow: true,
    endorsements: [
      { id: 'e1', fromPlayerId: '2', fromPlayerName: 'Mike Johnson', fromPlayerPhoto: 'https://i.pravatar.cc/300?img=3', type: 'friendliness', comment: 'Super fun to play with!', date: '2026-03-15' },
      { id: 'e2', fromPlayerId: '3', fromPlayerName: 'Lisa Park', fromPlayerPhoto: 'https://i.pravatar.cc/300?img=5', type: 'sportsmanship', comment: 'Great sportsmanship, always positive', date: '2026-03-20' },
    ],
    matchesPlayed: 24,
  },
  {
    id: '2',
    name: 'Mike Johnson',
    age: 34,
    photo: 'https://i.pravatar.cc/300?img=3',
    photos: ['https://i.pravatar.cc/300?img=3'],
    skillLevel: '4.0',
    bio: 'Competitive player looking for challenging matches. Played college tennis. Happy to help beginners too!',
    lookingFor: ['Singles Partner', 'Hitting Partner'],
    playStyle: ['Competitive', 'Hitting Partner'],
    groupSize: 1,
    availability: [
      { day: 'Monday', timeSlot: 'Evening' },
      { day: 'Wednesday', timeSlot: 'Evening' },
      { day: 'Friday', timeSlot: 'Evening' },
    ],
    location: 'Midtown',
    distance: 1.5,
    isAvailableNow: false,
    endorsements: [
      { id: 'e3', fromPlayerId: '1', fromPlayerName: 'Sarah Chen', fromPlayerPhoto: 'https://i.pravatar.cc/300?img=1', type: 'skill', comment: 'Amazing backhand, really pushes you to play better', date: '2026-03-10' },
    ],
    matchesPlayed: 45,
  },
  {
    id: '3',
    name: 'Lisa Park',
    age: 29,
    photo: 'https://i.pravatar.cc/300?img=5',
    photos: ['https://i.pravatar.cc/300?img=5', 'https://i.pravatar.cc/300?img=25'],
    skillLevel: '3.0',
    bio: 'Getting back into tennis after a few years off. Looking for patient hitting partners and social groups.',
    lookingFor: ['Hitting Partner', 'Group/Social Play'],
    playStyle: ['Casual/Social', 'Drill Partner'],
    groupSize: 1,
    availability: [
      { day: 'Tuesday', timeSlot: 'Morning' },
      { day: 'Thursday', timeSlot: 'Morning' },
      { day: 'Saturday', timeSlot: 'Afternoon' },
    ],
    location: 'Eastside',
    distance: 3.1,
    isAvailableNow: true,
    endorsements: [
      { id: 'e4', fromPlayerId: '1', fromPlayerName: 'Sarah Chen', fromPlayerPhoto: 'https://i.pravatar.cc/300?img=1', type: 'punctuality', comment: 'Always on time and ready to play', date: '2026-04-01' },
    ],
    matchesPlayed: 8,
  },
  {
    id: '4',
    name: 'James Wilson',
    age: 42,
    photo: 'https://i.pravatar.cc/300?img=7',
    photos: ['https://i.pravatar.cc/300?img=7'],
    skillLevel: '4.5',
    bio: 'Former club champion, now playing for fun. I organize weekly doubles sessions — join us!',
    lookingFor: ['Doubles Partner', 'Group/Social Play', 'Tournament Partner'],
    playStyle: ['Competitive', 'League Play'],
    groupSize: 4,
    availability: [
      { day: 'Wednesday', timeSlot: 'Evening' },
      { day: 'Saturday', timeSlot: 'Morning' },
      { day: 'Sunday', timeSlot: 'Morning' },
    ],
    location: 'Northside',
    distance: 4.2,
    isAvailableNow: false,
    endorsements: [
      { id: 'e5', fromPlayerId: '2', fromPlayerName: 'Mike Johnson', fromPlayerPhoto: 'https://i.pravatar.cc/300?img=3', type: 'skill', comment: 'Incredible serve and volley game', date: '2026-02-28' },
      { id: 'e6', fromPlayerId: '5', fromPlayerName: 'Emma Davis', fromPlayerPhoto: 'https://i.pravatar.cc/300?img=9', type: 'friendliness', comment: 'Organizes the best group sessions!', date: '2026-03-25' },
    ],
    matchesPlayed: 67,
  },
  {
    id: '5',
    name: 'Emma Davis',
    age: 31,
    photo: 'https://i.pravatar.cc/300?img=9',
    photos: ['https://i.pravatar.cc/300?img=9', 'https://i.pravatar.cc/300?img=29'],
    skillLevel: '3.5',
    bio: 'Tennis is my therapy! Looking for regular hitting partners around my level. Love a good rally.',
    lookingFor: ['Singles Partner', 'Hitting Partner'],
    playStyle: ['Casual/Social', 'Hitting Partner'],
    groupSize: 1,
    availability: [
      { day: 'Monday', timeSlot: 'Morning' },
      { day: 'Wednesday', timeSlot: 'Morning' },
      { day: 'Friday', timeSlot: 'Morning' },
    ],
    location: 'Southside',
    distance: 2.8,
    isAvailableNow: true,
    endorsements: [],
    matchesPlayed: 18,
  },
  {
    id: '6',
    name: 'David Kim',
    age: 25,
    photo: 'https://i.pravatar.cc/300?img=12',
    photos: ['https://i.pravatar.cc/300?img=12'],
    skillLevel: '2.5',
    bio: 'New to tennis, eager to learn! Signed up for lessons and looking for beginner-friendly partners.',
    lookingFor: ['Hitting Partner', 'Lessons/Coaching'],
    playStyle: ['Casual/Social', 'Drill Partner'],
    groupSize: 1,
    availability: [
      { day: 'Saturday', timeSlot: 'Afternoon' },
      { day: 'Sunday', timeSlot: 'Afternoon' },
    ],
    location: 'Downtown',
    distance: 0.8,
    isAvailableNow: false,
    endorsements: [],
    matchesPlayed: 3,
  },
  {
    id: '7',
    name: 'Rachel Torres',
    age: 37,
    photo: 'https://i.pravatar.cc/300?img=16',
    photos: ['https://i.pravatar.cc/300?img=16'],
    skillLevel: '4.0',
    bio: 'USTA league player looking for doubles partners and practice matches. Serious about improving!',
    lookingFor: ['Doubles Partner', 'Tournament Partner', 'Hitting Partner'],
    playStyle: ['Competitive', 'League Play'],
    groupSize: 2,
    availability: [
      { day: 'Tuesday', timeSlot: 'Evening' },
      { day: 'Thursday', timeSlot: 'Evening' },
      { day: 'Saturday', timeSlot: 'Morning' },
    ],
    location: 'Westside',
    distance: 3.5,
    isAvailableNow: true,
    endorsements: [
      { id: 'e7', fromPlayerId: '4', fromPlayerName: 'James Wilson', fromPlayerPhoto: 'https://i.pravatar.cc/300?img=7', type: 'sportsmanship', comment: 'Tough competitor but always fair', date: '2026-03-18' },
    ],
    matchesPlayed: 52,
  },
];
