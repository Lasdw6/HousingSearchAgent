# Real-Time Agent Progress Updates

The housing search system now includes real-time progress updates that show exactly what the intelligent agent is doing during the search process.

## 🚀 Features

### Backend (FastAPI + WebSocket)

- **WebSocket endpoint**: `/ws/search-progress` for real-time communication
- **Progress-enabled search**: `/api/v1/search-with-progress` endpoint
- **Real agent progress**: Shows actual search steps, not simulated progress
- **Multiple progress types**: initialization, searching, processing, completion, errors

### Frontend (Next.js + WebSocket)

- **Real-time progress display**: Live updates as the agent works
- **Progress bar**: Visual representation of search completion
- **Progress log**: Detailed step-by-step log of agent actions
- **Color-coded messages**: Different colors for different message types
- **Auto-scrolling log**: Shows the most recent progress updates

## 🏃‍♂️ How to Run

### 1. Start the Backend Server

```bash
cd backend
python run_server.py
```

The server will start on `http://localhost:8000` with:

- API endpoints: `http://localhost:8000/api/v1/`
- WebSocket: `ws://localhost:8000/ws/search-progress`
- API docs: `http://localhost:8000/docs`

### 2. Start the Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🔍 How It Works

### 1. User Initiates Search

- User fills out search form and clicks "Search Listings"
- Frontend connects to WebSocket endpoint
- Frontend sends search request to `/api/v1/search-with-progress`

### 2. Agent Progress Updates

The intelligent agent sends real-time updates for:

- **Initialization** (0-10%): Setting up search strategy
- **Searching** (15-75%): Searching each source (Kijiji, Reddit, Facebook, Google, UW Off-Campus)
- **Processing** (80-95%): Filtering and scoring results
- **Completion** (100%): Final results ready

### 3. Real-Time Display

- **Progress bar**: Shows current completion percentage
- **Live log**: Shows each step as it happens
- **Source status**: Shows which sources found listings
- **Error handling**: Shows any issues that occur

## 📊 Progress Message Types

| Type              | Icon | Color | Description                  |
| ----------------- | ---- | ----- | ---------------------------- |
| `init`            | ℹ️   | Gray  | Initial setup                |
| `strategy`        | 🧠   | Blue  | Strategy selection           |
| `searching`       | 🔍   | Blue  | Currently searching a source |
| `source_complete` | ✓    | Blue  | Source search completed      |
| `source_error`    | ❌   | Red   | Source search failed         |
| `processing`      | ⚙️   | Blue  | Processing results           |
| `complete`        | ✅   | Green | Search completed             |
| `error`           | ❌   | Red   | General error                |

## 🎯 Example Progress Flow

```
🤖 Intelligent Agent Progress
[████████████████████████████████████████] 100%

ℹ️ Initializing intelligent search agent...
🧠 Using broad search strategy
🔍 Searching Kijiji...
✓ Kijiji: Found 2 listings
🔍 Searching Reddit...
✓ Reddit: Found 1 listings
🔍 Searching Facebook...
✗ Facebook: No listings found
🔍 Searching Google...
✓ Google: Found 3 listings
🔍 Searching UW Off-Campus...
✓ UW Off-Campus: Found 1 listings
⚙️ Processing 7 total listings...
✅ Search completed! Found 7 listings
```

## 🔧 Technical Details

### Backend Architecture

- **FastAPI**: Main web framework
- **WebSocket**: Real-time communication
- **Agent Callbacks**: Progress callback system
- **Broadcasting**: Sends updates to all connected clients

### Frontend Architecture

- **WebSocket Client**: Connects to backend WebSocket
- **State Management**: React state for progress tracking
- **Real-time Updates**: Live UI updates as messages arrive
- **Progress Visualization**: Progress bar and log display

### Message Format

```typescript
interface ProgressMessage {
  type: "progress" | "error" | "connection" | "complete";
  message: string;
  step?: string;
  progress?: number;
  current_source?: string;
  results_count?: number;
}
```

## 🐛 Troubleshooting

### WebSocket Connection Issues

- Ensure backend is running on port 8000
- Check browser console for WebSocket errors
- Verify CORS settings in backend

### Progress Not Showing

- Check browser console for JavaScript errors
- Verify WebSocket connection is established
- Check backend logs for agent progress messages

### Search Not Starting

- Ensure all required fields are filled
- Check backend logs for API errors
- Verify frontend is connecting to correct backend URL

## 🚀 Future Enhancements

- **Progress persistence**: Save progress for long-running searches
- **Search cancellation**: Allow users to cancel ongoing searches
- **Progress notifications**: Browser notifications for search completion
- **Search history**: Track and display previous search progress
- **Performance metrics**: Show search speed and efficiency stats
