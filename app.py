#!/usr/bin/env python3
"""
Bike-Dream Motorcycle Database Application
Entry Point for Production Deployment

This is the main entry point for the Bike-Dream application.
It imports and runs the FastAPI server with proper production configuration.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "api"))

def create_app():
    """
    Create and configure the FastAPI application.
    This function imports the server from the api module.
    """
    try:
        from api.server import app
        return app
    except ImportError as e:
        print(f"Error importing server: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)

def main():
    """
    Main function to run the application.
    Used for both development and production.
    """
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8001))
    debug = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    
    # Create the FastAPI app
    app = create_app()
    
    if debug:
        print("🚀 Starting Bike-Dream in DEBUG mode...")
        print(f"📍 Server will be available at: http://{host}:{port}")
        print("🔄 Auto-reload enabled for development")
    else:
        print("🚀 Starting Bike-Dream in PRODUCTION mode...")
        print(f"📍 Server running on: http://{host}:{port}")
    
    # Run the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=debug,
        access_log=True,
        log_level="info" if not debug else "debug"
    )

if __name__ == "__main__":
    main()