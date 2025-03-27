#!/usr/bin/env python3
"""
Run script for the Hybrid Clinical Genomics Database API.

This script provides a convenient way to start the FastAPI application.
It imports the app from app.api and runs it with Uvicorn.
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get port from environment variable or use default
PORT = int(os.getenv("API_PORT", "8000"))
HOST = os.getenv("API_HOST", "0.0.0.0")
RELOAD = os.getenv("API_RELOAD", "False").lower() == "true"


def main():
    """Run the FastAPI application."""
    # Add the current directory to the path so we can import app modules
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Import the app here to avoid circular imports
    print(f"Starting Hybrid Clinical Genomics Database API on {HOST}:{PORT}")
    print(f"Swagger UI available at http://localhost:{PORT}/docs")
    
    uvicorn.run(
        "app.api:app",
        host=HOST,
        port=PORT,
        reload=RELOAD
    )


if __name__ == "__main__":
    main() 