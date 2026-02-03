# Setup Guide - Andhra Pradesh Government Dashboard

## Quick Start

### 1. Install Dependencies

```bash
cd dashboard
npm install
```

### 2. Configure Environment

Create `.env.local` file in the `dashboard` directory:

```env
# n8n Webhook Base URL
NEXT_PUBLIC_N8N_BASE_URL=http://localhost:5678/webhook

# Google Maps API Key (required for district map)
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

**Important:** Replace `your_google_maps_api_key_here` with your actual Google Maps API key.

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 4. Login

1. Select a district from the dropdown
2. Click "Login"
3. You'll be redirected to the dashboard

## n8n Webhook Endpoints Required

The dashboard expects these endpoints to be available at your n8n base URL:

### Messages
- `GET /messages-recent?district={slug}` 
  - Returns: Array of message objects
  - Example: `http://localhost:5678/webhook/messages-recent?district=srikakulam`

### Calendar
- `GET /calendar-today?district={slug}`
  - Returns: Array of today's calendar events
- `GET /calendar?district={slug}&start={iso}&end={iso}`
  - Returns: Array of calendar events in date range

### Departments
- `GET /departments?district={slug}`
  - Returns: Array of department objects with message counts and pending tasks

### District Stats
- `GET /district-stats?district={slug}`
  - Returns: District statistics object

### Filtered Messages
- `GET /messages-recent?district={slug}&department={name}`
  - Returns: Messages filtered by department

## Expected Response Formats

### Message Object
```json
{
  "id": "msg-123",
  "summary": "Message summary text",
  "from": "Citizen Name or Officer Name",
  "forwardedDepartment": "Health",
  "timestamp": "2024-01-15T10:30:00Z",
  "priority": "high" | "medium" | "low",
  "department": "Health"
}
```

### Calendar Event Object
```json
{
  "id": "event-123",
  "title": "Meeting Title",
  "start": "2024-01-15T10:00:00Z",
  "end": "2024-01-15T11:00:00Z",
  "location": "Conference Room A",
  "department": "Health",
  "attendees": ["Collector", "DRO", "JC"],
  "description": "Meeting description"
}
```

### Department Object
```json
{
  "id": "dept-123",
  "name": "Health Department",
  "messageCount": 15,
  "pendingTasks": 3
}
```

## Google Maps Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Maps JavaScript API"
4. Create API key
5. Add API key to `.env.local` as `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`

**Note:** For production, restrict the API key to your domain.

## District GeoJSON Data

The district map requires GeoJSON boundary data. Currently using placeholder coordinates. To add real boundaries:

1. Obtain GeoJSON for each district
2. Store in a database or static files
3. Update `DistrictMap.tsx` to fetch from n8n or API endpoint

Example endpoint:
- `GET /district-boundary?district={slug}`
- Returns: GeoJSON FeatureCollection

## Troubleshooting

### "n8n API error" messages
- Verify n8n is running
- Check `NEXT_PUBLIC_N8N_BASE_URL` in `.env.local`
- Test endpoints with curl or Postman

### Google Maps not loading
- Verify API key is set in `.env.local`
- Check browser console for API errors
- Ensure Maps JavaScript API is enabled

### Voice Assistant not working
- Use Chrome or Edge (best Web Speech API support)
- Grant microphone permissions when prompted
- Check browser console for errors

### District login not persisting
- Check browser console for errors
- Verify sessionStorage is enabled
- Clear browser cache and try again

## Production Build

```bash
npm run build
npm start
```

The application will be available at `http://localhost:3000` (or your configured port).

## Project Structure

```
dashboard/
├── app/                    # Next.js App Router pages
│   ├── login/             # District login
│   ├── home/              # Dashboard home
│   ├── messages/          # Messages page
│   ├── calendar/          # Calendar page
│   └── departments/        # Departments page
├── components/            # React components
├── lib/                   # Utilities and clients
├── store/                 # Zustand state stores
├── public/                # Static assets
└── types/                 # TypeScript type definitions
```

## Support

For issues or questions, check:
1. Browser console for errors
2. Network tab for API call failures
3. n8n workflow logs
4. Next.js build output
