from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import logging
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .api.search import router as search_router
from .models import SearchRequest
from .scrapers.agent import search_with_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Housing Search API",
    description="Intelligent agent-based housing search for UW students",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the search router
app.include_router(search_router, prefix="/api/v1")

# Store active WebSocket connections
active_connections: List[WebSocket] = []

async def broadcast_progress(message: Dict):
    """Broadcast progress message to all connected clients"""
    if active_connections:
        await asyncio.gather(
            *[connection.send_text(json.dumps(message)) for connection in active_connections]
        )

@app.websocket("/ws/search-progress")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time search progress updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_text(json.dumps({
            "type": "connection",
            "message": "Connected to search progress stream"
        }))
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("WebSocket client disconnected")

@app.post("/api/v1/search-with-progress")
async def search_with_progress(request: SearchRequest):
    """Search with real-time progress updates via WebSocket"""
    try:
        # Convert to dict for agent
        params = request.dict()
        
        # Send initial progress message
        await broadcast_progress({
            "type": "progress",
            "message": "Starting intelligent housing search...",
            "step": "init",
            "progress": 0
        })
        
        # Use intelligent agent for search with progress updates
        results = await search_with_agent_with_progress(params)
        
        # Send completion message
        await broadcast_progress({
            "type": "complete",
            "message": f"Search completed! Found {len(results)} listings",
            "step": "complete",
            "progress": 100,
            "results_count": len(results)
        })
        
        return JSONResponse({
            "success": True,
            "results": results,
            "total_found": len(results)
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        await broadcast_progress({
            "type": "error",
            "message": f"Search failed: {str(e)}",
            "step": "error"
        })
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Search failed"}
        )

async def search_with_agent_with_progress(params: Dict):
    """Modified agent search that sends progress updates"""
    try:
        # Send initial progress message
        await broadcast_progress({
            "type": "progress",
            "message": "Initializing intelligent search agent...",
            "step": "start",
            "progress": 5
        })
        
        # Create progress callback function
        async def progress_callback(message: Dict):
            await broadcast_progress(message)
        
        # Use Google Playwright scraper with progress updates for better performance
        from .scrapers.google_playwright import search_google_playwright
        
        # Send progress message
        await broadcast_progress({
            "type": "progress",
            "message": "Starting Google Playwright search with deep search...",
            "step": "playwright_start",
            "progress": 10
        })
        
        # Perform the search with progress updates
        search_result = await search_google_playwright(params, enable_deep_search=True, progress_callback=progress_callback)
        results = search_result.get('listings', [])
        
        # Send final completion message
        await broadcast_progress({
            "type": "complete",
            "message": f"Search completed! Found {len(results)} listings",
            "step": "complete",
            "progress": 100,
            "results_count": len(results)
        })
        
        return results
        
    except Exception as e:
        logger.error(f"Agent search error: {e}")
        await broadcast_progress({
            "type": "error",
            "message": f"Agent search failed: {str(e)}",
            "step": "error"
        })
        return []

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Housing Search API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/v1/search",
            "search_with_progress": "/api/v1/search-with-progress",
            "websocket": "/ws/search-progress"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "active_connections": len(active_connections)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 