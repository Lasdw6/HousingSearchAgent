# 🏠 Waterloo Student Housing Search Agent (MVP)

A fast, no-fluff search tool that helps University of Waterloo students find relevant housing listings from platforms like Facebook, Kijiji, and Reddit — without digging through spammy or outdated posts.

This MVP focuses on delivering 10 high-quality listings in real time, filtered by user preferences, with zero storage and no login required.

## 💡 Key Features (MVP)

### ✅ Structured Search Form (Next.js)

- Predefined filters:
  - Gender preference (Any / Male-only / Female-only)
  - Price range (min & max)
  - Term / Move-in (e.g., Fall 2025)
  - Location (e.g., Columbia, Lester, Keats)
  - Furnished (yes/no)
  - Lease type (Private room / Shared room / Entire unit)
- Simple and fast UI
- Submits search query to the backend

### ✅ Backend Search Agent (FastAPI)

- Accepts structured user input via API
- Performs real-time search across multiple platforms
- Uses asynchronous scraping/searching with timeout fallback
- Platforms for MVP:
  - Kijiji (search URL scraping)
  - Reddit (r/uwaterloo) (search via API or scrape)
  - (Optional) Facebook Group/Marketplace (only if Playwright is working)
- Filters listings by:
  - Price range
  - Furnishing
  - Gender-specific keywords
  - Location relevance (heuristic or keyword-based)
- Returns up to 10 best matches based on score

### ✅ Results Page (Next.js)

- Displays matching listings as clean cards:
  - Title
  - Price
  - Location
  - Source (e.g., "Kijiji")
  - Link to original listing
- Shows loading state while scraping
- If fewer than 10 listings, shows message like:
  "Only 6 listings found matching your search. Try adjusting your filters!"

## ⚙️ Tech Stack

| Part       | Stack                                                    |
| ---------- | -------------------------------------------------------- |
| Frontend   | Next.js (TypeScript) + TailwindCSS                       |
| Backend    | FastAPI (Python 3.11+) with async support                |
| Scraping   | httpx, selectolax / BeautifulSoup, Playwright (optional) |
| Deployment | Vercel (frontend) + Railway / Render (backend)           |

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- Git

### Quick Start (Windows)

```powershell
# Run the development startup script
.\start-dev.ps1
```

### Manual Installation

1. Clone the repository

```bash
git clone <repository-url>
cd waterloo-housing-search
```

2. Set up the backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
# OR source venv/bin/activate  # On Unix/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

3. Set up the frontend

```bash
cd frontend
npm install
npm run dev
```

4. Open your browser to `http://localhost:3000`

## 📁 Project Structure

```
waterloo-housing-search/
├── frontend/           # Next.js frontend application
│   ├── src/
│   │   ├── app/       # App router pages
│   │   ├── components/ # React components
│   │   └── lib/       # Utilities and API calls
│   ├── public/        # Static assets
│   ├── vercel.json    # Vercel deployment config
│   └── package.json   # Frontend dependencies
├── backend/           # FastAPI backend application
│   ├── app/
│   │   ├── api/       # API endpoints
│   │   ├── scrapers/  # Scraping modules
│   │   └── models/    # Data models
│   ├── main.py        # FastAPI app entry point
│   ├── requirements.txt # Backend dependencies
│   ├── railway.json   # Railway deployment config
│   ├── Dockerfile     # Docker configuration
│   └── .dockerignore  # Docker ignore file
├── start-dev.ps1      # Development startup script
└── README.md          # This file
```

## 🔧 Development

### Backend Development

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## 🌐 API Endpoints

- `POST /api/search` - Search for housing listings
- `GET /api/health` - Health check endpoint

### Search Request Format

```json
{
  "gender": "Any",
  "price_min": 400,
  "price_max": 1500,
  "term": "Fall 2025",
  "location": "Columbia",
  "furnished": true,
  "lease_type": "Private room"
}
```

## 🚀 Deployment

### Frontend (Vercel)

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Set environment variable: `NEXT_PUBLIC_API_URL` to your backend URL
4. Deploy!

### Backend (Railway)

1. Push your code to GitHub
2. Connect your repository to Railway
3. Railway will automatically detect the Python app and deploy
4. Update your frontend's `NEXT_PUBLIC_API_URL` with the Railway URL

### Alternative Backend Deployment (Render)

1. Push your code to GitHub
2. Create a new Web Service on Render
3. Connect your repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 🔍 How It Works

1. **User Input**: Students fill out the search form with their preferences
2. **Async Scraping**: Backend simultaneously searches Kijiji and Reddit
3. **Smart Filtering**: Listings are filtered based on user criteria
4. **Scoring System**: Results are scored and ranked by relevance
5. **Clean Results**: Top 10 matches are displayed with direct links

## 🛡️ Error Handling

- **Timeout Protection**: 45-second timeout for scraping operations
- **Graceful Degradation**: If one platform fails, others continue working
- **User-Friendly Errors**: Clear error messages for different failure scenarios
- **Health Checks**: Backend health endpoint for monitoring

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ⚠️ Legal Notice

This tool is for educational purposes. Please respect the terms of service of the platforms being scraped (Kijiji, Reddit). Consider implementing rate limiting and respecting robots.txt in production use.
