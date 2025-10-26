#!/usr/bin/env python3
"""
Run the Housing Search API server
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting Housing Search API Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws/search-progress")
    print("📚 API docs: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",  # Use import string for reload mode
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    ) 