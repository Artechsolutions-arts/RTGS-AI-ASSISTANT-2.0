# Andhra Pradesh Government Dashboard

Production-ready government portal dashboard built with Next.js, TypeScript, and Tailwind CSS.

## Features

- ✅ District-based authentication (26 districts)
- ✅ Real-time data from n8n webhooks (NO mock data)
- ✅ Google Maps integration with district boundaries
- ✅ Voice Assistant (Web Speech API) - English & Telugu
- ✅ AI Chatbot for dashboard queries
- ✅ Messages, Calendar, and Departments pages
- ✅ Government-grade UI matching srikakulam.ap.gov.in

## Technology Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **Maps:** Google Maps API
- **Voice:** Web Speech API
- **Data Source:** n8n Webhooks only

## Setup Instructions

### 1. Install Dependencies

```bash
cd dashboard
npm install
```

### 2. Configure Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_N8N_BASE_URL=http://localhost:5678/webhook
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 4. Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
dashboard/
├── app/
│   ├── login/          # District login page
│   ├── home/           # Home dashboard (map + activity)
│   ├── messages/       # Messages page
│   ├── calendar/       # Calendar page
│   ├── departments/    # Departments page
│   ├── layout.tsx      # Root layout
│   └── globals.css     # Global styles
├── components/
│   ├── Header.tsx      # Navigation header
│   ├── DistrictMap.tsx # Google Maps district map
│   ├── MessagesPanel.tsx
│   ├── CalendarPanel.tsx
│   ├── VoiceToggle.tsx # Voice assistant toggle
│   └── Chatbot.tsx     # AI chatbot panel
├── lib/
│   ├── n8nClient.ts    # n8n API client (NO mock data)
│   └── auth.ts         # District authentication
└── store/
    ├── districtStore.ts # District state (Zustand)
    └── voiceStore.ts   # Voice assistant state
```

## n8n API Endpoints Required

The dashboard expects these n8n webhook endpoints:

- `GET /messages-recent?district={slug}` - Recent messages
- `GET /calendar-today?district={slug}` - Today's calendar events
- `GET /calendar?district={slug}&start={iso}&end={iso}` - Calendar by date range
- `GET /departments?district={slug}` - Department list
- `GET /district-stats?district={slug}` - District statistics
- `GET /messages-recent?district={slug}&department={name}` - Messages by department

**All endpoints MUST return real data - NO mock responses.**

## District Authentication

1. User selects district from dropdown on login page
2. District context stored in sessionStorage
3. All API calls include district context
4. Dashboard shows only data for logged-in district

## Voice Assistant

- Toggle switch in header
- State persists in localStorage
- Auto-activates when enabled
- Supports English and Telugu
- Uses Web Speech API

## Chatbot

- Floating button (bottom-right)
- Answers queries about:
  - Today's meetings
  - Recent messages
  - Department information
- All responses based on n8n data only

## Google Maps

- Requires API key in `.env.local`
- Shows district boundary overlay
- Mandal boundaries visible
- Government-style map styling

## Important Notes

⚠️ **NO MOCK DATA** - All data must come from n8n APIs
⚠️ **District-scoped** - All data filtered by logged-in district
⚠️ **Production-ready** - Built for government use, not a demo

## License

Government of Andhra Pradesh - Internal Use Only
