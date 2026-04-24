export interface Message {
  id: string;
  senderId: string;
  text: string;
  timestamp: string;
  read: boolean;
}

export interface Conversation {
  id: string;
  playerId: string;
  playerName: string;
  playerPhoto: string;
  lastMessage: string;
  lastMessageTime: string;
  unreadCount: number;
  messages: Message[];
}

export const CONVERSATIONS: Conversation[] = [
  {
    id: 'c1',
    playerId: '1',
    playerName: 'Sarah Chen',
    playerPhoto: 'https://i.pravatar.cc/300?img=1',
    lastMessage: 'Sounds great! See you Saturday at 9!',
    lastMessageTime: '2026-04-09T18:30:00',
    unreadCount: 1,
    messages: [
      { id: 'm1', senderId: 'current', text: 'Hey Sarah! Want to play doubles this Saturday?', timestamp: '2026-04-09T14:00:00', read: true },
      { id: 'm2', senderId: '1', text: 'Hi! That sounds fun! Which court were you thinking?', timestamp: '2026-04-09T14:15:00', read: true },
      { id: 'm3', senderId: 'current', text: 'How about Greenwood at 9am? We can split the court fee.', timestamp: '2026-04-09T14:20:00', read: true },
      { id: 'm4', senderId: '1', text: 'Perfect! $20 each for 2 hours. I\'ll bring an extra racket.', timestamp: '2026-04-09T15:00:00', read: true },
      { id: 'm5', senderId: 'current', text: 'Awesome, do you have a 4th player?', timestamp: '2026-04-09T18:00:00', read: true },
      { id: 'm6', senderId: '1', text: 'Sounds great! See you Saturday at 9!', timestamp: '2026-04-09T18:30:00', read: false },
    ],
  },
  {
    id: 'c2',
    playerId: '2',
    playerName: 'Mike Johnson',
    playerPhoto: 'https://i.pravatar.cc/300?img=3',
    lastMessage: 'Good match today! Your backhand has really improved.',
    lastMessageTime: '2026-04-08T20:00:00',
    unreadCount: 0,
    messages: [
      { id: 'm7', senderId: '2', text: 'Hey! Up for a singles match this week?', timestamp: '2026-04-07T10:00:00', read: true },
      { id: 'm8', senderId: 'current', text: 'Sure! How about Wednesday evening?', timestamp: '2026-04-07T10:30:00', read: true },
      { id: 'm9', senderId: '2', text: 'Wednesday works. Community Park at 6pm?', timestamp: '2026-04-07T11:00:00', read: true },
      { id: 'm10', senderId: 'current', text: 'See you there!', timestamp: '2026-04-07T11:05:00', read: true },
      { id: 'm11', senderId: '2', text: 'Good match today! Your backhand has really improved.', timestamp: '2026-04-08T20:00:00', read: true },
    ],
  },
  {
    id: 'c3',
    playerId: '4',
    playerName: 'James Wilson',
    playerPhoto: 'https://i.pravatar.cc/300?img=7',
    lastMessage: 'We have 5 so far. Room for 3 more!',
    lastMessageTime: '2026-04-09T12:00:00',
    unreadCount: 2,
    messages: [
      { id: 'm12', senderId: '4', text: 'Hey! Want to join our Saturday social doubles?', timestamp: '2026-04-09T09:00:00', read: true },
      { id: 'm13', senderId: 'current', text: 'Sounds fun! When and where?', timestamp: '2026-04-09T09:30:00', read: true },
      { id: 'm14', senderId: '4', text: 'Riverside Courts, 10am. Free courts so no cost!', timestamp: '2026-04-09T10:00:00', read: false },
      { id: 'm15', senderId: '4', text: 'We have 5 so far. Room for 3 more!', timestamp: '2026-04-09T12:00:00', read: false },
    ],
  },
];
