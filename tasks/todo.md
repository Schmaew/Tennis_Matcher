# Tennis Matcher - Mobile App Plan

## Overview
A React Native (Expo SDK 54) mobile app for amateur tennis players to find partners, share court costs, and organize games in their area. Frontend-only with mocked data.

---

## Implementation Phases

### Phase 1: Project Setup
- [x] Initialize Expo project with SDK 54
- [x] Set up Expo Router with tab navigation
- [x] Create folder structure
- [x] Add mock data files (players, courts, matches, messages)
- [x] Create constants (Colors, skillLevels, amenities)
- [x] Create AuthContext with mock login

### Phase 2: Reusable Components
- [x] PlayerCard — photo, name, skill badge, distance, availability, play style, message button
- [x] CourtCard — photo, name, address, fee, surface, rating, amenity icons
- [x] MatchCard — court, date/time, type badge, skill range, spots, cost, player avatars
- [x] SkillBadge — NTRP level with color coding
- [x] EndorsementBadge — type icon + count
- [x] CostSplitter — interactive per-person cost calculator

### Phase 3: Tab Screens
- [x] Tab layout (5 tabs: Discover, Courts, Matches, Messages, Profile)
- [x] Home/Discovery screen — player feed with filters and available-now toggle
- [x] Courts screen — court list with map view toggle
- [x] Matches screen — match feed with Open/My Matches/Full filter
- [x] Messages screen — conversation list with unread badges
- [x] Profile screen — full profile with stats, tags, edit/logout

### Phase 4: Detail Screens
- [x] Player detail — full profile, endorsements, send message
- [x] Court detail — photos, fees, cost splitter, hours, amenities, rules, contact
- [x] Match detail — players, spots, cost breakdown, join button
- [x] Chat screen — message bubbles, quick invite template, send

### Phase 5: Navigation & State
- [x] Auth context + auto-login
- [x] Root layout with AuthProvider
- [x] Stack screens for all detail routes
- [x] Deep linking (player → profile → message, court → detail, match → detail)

---

## Review

### What was built
A complete frontend React Native mobile app with **17 routes**, **6 reusable components**, **4 mock data files**, **3 constant files**, and **1 context provider**. All screens compile and bundle successfully.

### Architecture
- **5 tab screens**: Discover, Courts, Matches, Messages, Profile
- **4 detail screens**: Player, Court, Match, Chat (stack navigation)
- **File-based routing** via Expo Router
- **Mock data** in TypeScript files with full type definitions
- **Dark/light mode** support throughout
- **Green theme** (tennis-appropriate color scheme)

### Key Features Implemented
- Player discovery with skill/availability filters
- Court directory with fees, amenities, rules, hours
- Interactive cost-splitting calculator
- Match organizer (browse open matches, join)
- Private messaging with chat bubbles
- Player endorsements (skill, sportsmanship, punctuality, friendliness)
- NTRP skill level badges with color coding
- Profile with bio, availability, play style, stats

### Files Created/Modified
| Category | Files |
|----------|-------|
| Tab Screens | 5 (index, courts, matches, messages, profile) |
| Detail Screens | 4 (player/[id], court/[id], match/[id], chat/[id]) |
| Components | 6 (PlayerCard, CourtCard, MatchCard, SkillBadge, EndorsementBadge, CostSplitter) |
| Data | 4 (players, courts, matches, messages) |
| Constants | 3 (Colors, skillLevels, amenities) |
| Contexts | 1 (AuthContext) |
| Layouts | 2 (root _layout, tabs _layout) |
| **Total** | **25 files** |
