#!/usr/bin/env python3
"""
Simple startup script for Hospital Operations Platform API only
This starts just the REST API without the agent orchestrator for testing
"""

import uvicorn
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

if __name__ == "__main__":
    print("🏥 Starting Hospital Operations Platform (API Only Mode)")
    print("=" * 60)
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
