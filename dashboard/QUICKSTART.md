# Quick Start Guide

## 1. Install Dependencies

```bash
npm install
```

## 2. Create Environment File

Create `.env.local`:

```env
NEXT_PUBLIC_N8N_BASE_URL=http://localhost:5678/webhook
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_key_here
```

## 3. Start Development Server

```bash
npm run dev
```

## 4. Access Dashboard

Open [http://localhost:3000](http://localhost:3000)

## 5. Login

- Select a district from dropdown
- Click "Login"
- Dashboard loads with district-specific data

## Features Available

✅ **Home Page** - District map + recent messages + calendar  
✅ **Messages Page** - All messages with filters  
✅ **Calendar Page** - Monthly calendar view  
✅ **Departments Page** - Department overview  
✅ **Voice Assistant** - Toggle in header (English/Telugu)  
✅ **Chatbot** - Floating button (bottom-right)  

## Important Notes

⚠️ **All data comes from n8n** - No mock data  
⚠️ **District-scoped** - Only shows data for logged-in district  
⚠️ **Google Maps required** - For district map visualization  

See `SETUP.md` for detailed configuration.
