# 🎾 Teaching Plan: Real-World Court Data & Party Finder Feature

**Project:** Tennis Matcher – React Native / Expo  
**Feature:** Fetch real nearby tennis courts from Google Places API and display them in the Party Finder (Matches) flow.  
**Audience:** Beginner–Intermediate mobile developer  
**Duration:** 5 sessions (~90 min each)

---

## Overview of What Was Built

| File | Purpose |
|---|---|
| `services/courtsService.ts` | Calls Google Places API, maps raw JSON → `Court` objects |
| `hooks/useCourts.ts` | Custom hook: asks location permission → fetches real courts → falls back to mock data |
| `app/(tabs)/courts.tsx` | Updated Courts screen: uses `useCourts`, shows loading spinner + error banner |
| `.env.example` | Documents how to configure the API key safely |
| `app.json` | Added `expo-location` plugin + iOS permission string |

---

## Session 1 – Understanding the Existing Codebase (Day 1)

### Goals
- Read and understand the project structure
- Know what mock data looks like vs real API data

### Tasks for Student
1. Open the app (`npx expo start`) and explore all 5 tabs.
2. Read `data/courts.ts` — identify every field in the `Court` interface.
3. Read `components/CourtCard.tsx` — trace how a `Court` object becomes UI.
4. Read `app/(tabs)/courts.tsx` (before the changes) — answer:
   - Where does the data come from?
   - What happens when you press a card?
5. Read `app/(tabs)/matches.tsx` — explain what a "Match" is and how it relates to courts.

### Questions to Discuss
- What is mock/fake data? Why do apps use it during development?
- What is a TypeScript `interface`? Why does `Court` have one?
- What does `FlatList` do? How is it different from `ScrollView`?

### Key Concept
> **Static data → API data** is the core pattern of this feature.  
> The `Court` interface stays the same. Only the *source* of the data changes.

---

## Session 2 – APIs & HTTP Requests (Day 2)

### Goals
- Understand what a REST API is
- Make a real HTTP request with `fetch`
- Understand JSON and how to map it

### Concepts to Teach

#### What is an API?
An API (Application Programming Interface) is a URL you can call to get data.  
Google Places returns a list of nearby places as JSON when you call:
```
GET https://maps.googleapis.com/maps/api/place/nearbysearch/json
    ?location=13.7563,100.5018
    &radius=5000
    &type=tennis_court
    &key=YOUR_KEY
```

#### What is JSON?
JavaScript Object Notation – a text format that looks like a JS object:
```json
{
  "name": "Bangkok Tennis Club",
  "vicinity": "123 Sukhumvit Rd",
  "geometry": { "location": { "lat": 13.75, "lng": 100.50 } },
  "rating": 4.2
}
```

#### The `fetch` API
```typescript
const response = await fetch(url);        // Make the HTTP request
const data = await response.json();       // Parse the JSON body
console.log(data.results);               // Array of places
```

### Hands-on Exercise
1. Open `services/courtsService.ts` and read through it.
2. Find the `mapPlaceToCourt` function. Answer:
   - What Google Places field becomes `court.name`?
   - What field becomes `court.latitude`?
   - What happens if a court has no photos?
3. Try changing `radiusMeters` default from `5000` to `10000`. What changes?

### Key Concept
> **Data mapping** – transforming one shape of data into another.  
> Google gives us `place.vicinity`; our app wants `court.address`.  
> The `mapPlaceToCourt` function is responsible for this translation.

---

## Session 3 – Location Services with expo-location (Day 3)

### Goals
- Understand why apps need location permission
- Request permission and get GPS coordinates
- Combine location + API call in one flow

### Concepts to Teach

#### Why Permission?
The OS protects user privacy. The app must *ask* before reading GPS.  
This is done with:
```typescript
const { status } = await Location.requestForegroundPermissionsAsync();
if (status !== 'granted') {
  // User said NO — handle gracefully
}
```

#### Getting Coordinates
```typescript
const position = await Location.getCurrentPositionAsync({});
console.log(position.coords.latitude);   // e.g. 13.7563
console.log(position.coords.longitude);  // e.g. 100.5018
```

#### The Full Flow (in `hooks/useCourts.ts`)
```
App starts
  → Ask for GPS permission
      ↓ granted                    ↓ denied
  Get coordinates              Show mock data + error message
      ↓
  Call Google Places API
      ↓ success                    ↓ fail
  Show real courts             Show mock data + error message
```

### Hands-on Exercise
1. Open `hooks/useCourts.ts` and trace the full flow of `loadRealCourts`.
2. Answer: What does `useCallback` do? Why is it used here?
3. Answer: Why does the hook start with `setCourts(COURTS)` in state?  
   *(Hint: what does the user see before the API call finishes?)*
4. Add a `console.log` inside `loadRealCourts` to print the coordinates before the API call. Verify it works.

### Key Concept
> **Graceful degradation** – always show *something* useful even when an API fails.  
> The hook never shows a blank screen; it falls back to mock courts with an info message.

---

## Session 4 – Custom Hooks & State Management (Day 4)

### Goals
- Understand React custom hooks
- Understand `useState`, `useEffect`, `useCallback`
- See how a hook connects a screen to a service

### Concepts to Teach

#### What is a Custom Hook?
A function that starts with `use` and can call other React hooks:
```typescript
// Before: screen manages everything itself (messy)
export default function CourtsScreen() {
  const [courts, setCourts] = useState(COURTS);
  const [loading, setLoading] = useState(false);
  // ... 30 lines of fetch logic mixed with UI ...
}

// After: logic is extracted into a hook (clean)
export default function CourtsScreen() {
  const { courts, loading, error, reload } = useCourts();
  // Screen only cares about display
}
```

#### The Three Key Hooks Used
| Hook | Purpose |
|---|---|
| `useState` | Stores courts, loading flag, error message, isRealData flag |
| `useEffect` | Runs `loadRealCourts` automatically when the component mounts |
| `useCallback` | Prevents `loadRealCourts` from being recreated on every render |

### Hands-on Exercise
1. Draw a diagram showing:  
   `CourtsScreen` → calls → `useCourts` → calls → `fetchNearbyCourts` → calls → Google Places API
2. Add a new state field `courtsCount: number` to `useCourts` that tracks how many courts were returned.
3. Display that count in `courts.tsx` as: *"Showing 8 courts near you"*

### Key Concept
> **Separation of concerns** – the screen handles display, the hook handles logic, the service handles networking.  
> Each file has one job.

---

## Session 5 – Environment Variables, API Keys & Going Live (Day 5)

### Goals
- Understand what an API key is and why it must be kept secret
- Set up a real Google Places API key
- Test the full flow end-to-end on a real device

### Concepts to Teach

#### What is an API Key?
A secret string that proves your app is allowed to use a paid service.  
Google charges per request. If someone steals your key, they run up your bill.

#### How Expo Handles Secrets
```
.env file  →  EXPO_PUBLIC_*  →  bundled into app (visible to users)
           →  non-EXPO_PUBLIC  →  only available at build time (safer)
```
> ⚠️ For production, put secret keys in a **backend server**, not the app.  
> For learning purposes, `EXPO_PUBLIC_` is acceptable.

#### Setting Up the Key (Step-by-Step)
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
3. Create a project → Enable **Places API** → Create an **API Key**
4. Paste the key into `.env`:
   ```
   EXPO_PUBLIC_GOOGLE_PLACES_API_KEY=AIzaSy...
   ```
5. Restart the Expo dev server:
   ```bash
   npx expo start --clear
   ```
6. Open the **Courts** tab on your phone → grant location → see real courts!

### Hands-on Exercise
1. Set up the API key and test on a real device or emulator.
2. Open Google Cloud Console → check the **Quotas** page. How many requests did you make?
3. Discussion: If this were a real app with 10,000 users, what would happen to the API costs?  
   What is a better architecture? *(Answer: backend proxy server)*

### Key Concept
> **Security first** – the `.env` file is already in `.gitignore`.  
> **Never** hardcode `AIzaSy...` directly in your source code.  
> Always use environment variables, always document them in `.env.example`.

---

## Bonus Challenges (For Fast Learners)

### Challenge 1 – Distance Badge
Show how far each court is from the user in the `CourtCard`.  
Hint: use the Haversine formula to calculate distance from two lat/lng pairs.

### Challenge 2 – Filter by Distance
Add a slider to the Courts screen to filter courts by radius (1 km, 5 km, 10 km).  
Update `useCourts` to accept a `radiusKm` parameter.

### Challenge 3 – Create Party at Real Court
When a user presses "Create Match" in `matches.tsx`, show a list of real nearby courts (from `useCourts`) to pick from.  
Save the selected `place_id` as the `courtId` in the new match.

### Challenge 4 – Cache Courts
Store the court results in `AsyncStorage` so the app shows them instantly next time without a loading spinner.  
Expire the cache after 10 minutes.

### Challenge 5 – Map View
Replace the "Map view coming soon" placeholder in `courts.tsx` with a real map using `react-native-maps`.  
Drop a pin for each court returned by `useCourts`.

---

## Session 6 – ngrok + Webhooks for LINE Bot (Day 6)

### Goals
- Understand what a webhook is and why it needs ngrok
- Run a local server that receives HTTP POST from LINE
- Expose local server to the internet with ngrok

### Concepts to Teach

#### What is a Webhook?
A webhook is an HTTP endpoint that an external service calls when something happens.  
LINE sends user messages to your server via webhook:
```
LINE Platform → HTTP POST → http://your-server.com/webhook
```

#### Why Do We Need ngrok?
- Your laptop runs on `localhost:5000` — not reachable from the internet
- ngrok creates a public URL that tunnels to your local machine
- LINE can now reach your server while you're developing

#### How ngrok Works (1 minute demo)
```bash
# Terminal 1: run your server
python server.py  # runs at http://localhost:5000

# Terminal 2: expose it publicly
ngrok http 5000
# → https://abc123.ngrok.io forwards to localhost:5000
```

#### The Full Flow
```
User sends message on LINE
  → LINE servers receive it
  → LINE calls your webhook URL (ngrok)
  → Your Flask server receives POST at /webhook
  → Your code parses message, queries database, builds reply
  → Your server sends reply back to LINE Messaging API
  → User sees reply in LINE app
```

### Hands-on Exercise
1. Read `lineofficial/server.py` — find the Flask route that handles the webhook.
2. Read `lineofficial/intent.py` — how does it detect sport type and province?
3. Read `lineofficial/reply.py` — what is a Flex Message and why use it?
4. Run the bot locally:
   ```bash
   cd lineofficial
   python server.py
   ```
5. In another terminal, expose it:
   ```bash
   ngrok http 5000
   ```
6. Copy the ngrok URL and paste it into LINE Console → Webhook URL → Verify
7. Test by sending a message to your LINE bot!

### Key Concept
> **Webhooks + ngrok = real-time integration**  
> Webhooks let external services push data to you.  
> ngrok makes your local machine reachable during development.

---

## Bonus Challenges (For Fast Learners)

### Challenge 6 – Add More Sports
The bot currently supports tennis and badminton. Add support for:
- Basketball (`สนามบาสเกตบอล`)
- Swimming (`สระว่ายน้ำ`)
- Football (`สนามฟุตบอล`)

### Challenge 7 – Persistent User State
Store the last sport the user searched for. If they send just a province name next time, assume the same sport.

### Challenge 8 – Location-based Search
If the user sends "สนามใกล้ฉัน" (courts near me), use their LINE profile location (if they shared it) to query the database by lat/lng.

### Challenge 9 – Rich Replies with Photos
Add court photos to the Flex Message carousel. Use the `photo` field from the database.

### Challenge 10 – Deploy the Bot
Deploy the Flask server to a real host (Railway, Render, or Heroku) so you don't need ngrok in production.

---

## Architecture Summary

```
┌─────────────────────────────────────────────┐
│               courts.tsx (UI)               │
│  Uses: useCourts() hook                     │
│  Shows: loading spinner, error banner,      │
│         list of CourtCard components        │
└────────────────┬────────────────────────────┘
                 │ calls
┌────────────────▼────────────────────────────┐
│          hooks/useCourts.ts (Logic)         │
│  Manages: loading, error, courts state      │
│  Calls: expo-location + courtsService       │
│  Fallback: mock data from data/courts.ts    │
└────────────────┬────────────────────────────┘
                 │ calls
┌────────────────▼────────────────────────────┐
│      services/courtsService.ts (Network)    │
│  Calls: Google Places Nearby Search API     │
│  Maps:  PlacesResult → Court interface      │
└────────────────┬────────────────────────────┘
                 │ HTTP GET
┌────────────────▼────────────────────────────┐
│         Google Places API (External)        │
│  Returns: real tennis courts near user      │
└─────────────────────────────────────────────┘
```

---

## Key Vocabulary Reference

| Term | Definition |
|---|---|
| API | A URL you call to get or send data |
| REST API | API that uses HTTP methods (GET, POST, etc.) |
| JSON | Text format for structured data |
| API Key | Secret token that authenticates your API requests |
| `fetch` | Built-in JS function to make HTTP requests |
| `async/await` | Syntax for handling asynchronous operations |
| Custom Hook | A reusable function that encapsulates React state/effects |
| Graceful degradation | Showing useful fallback content when something fails |
| Environment variable | Config value stored outside your code (in `.env`) |
| GPS / Location | Device coordinates (latitude, longitude) |
