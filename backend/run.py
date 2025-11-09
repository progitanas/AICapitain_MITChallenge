#!/usr/bin/env python
"""
Script de lancement du système AI Captain
Maritime Route Optimization Engine - Full Backend
"""
import os
import sys
import argparse
import uvicorn
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def main():
    parser = argparse.ArgumentParser(
        description="AI Captain - Maritime Route Optimization Backend"
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='API host (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='API port (default: 8000)'
    )
    
    parser.add_argument(
        '--reload',
        action='store_true',
        help='Enable auto-reload on code changes'
    )
    
    parser.add_argument(
        '--log-level',
        default='info',
        choices=['critical', 'error', 'warning', 'info', 'debug'],
        help='Logging level (default: info)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of worker processes (default: 1)'
    )
    
    args = parser.parse_args()
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║         AI CAPTAIN - Maritime Route Optimization                ║
    ║            Moteur d'Optimisation d'Itinéraire Maritime         ║
    ║                     Backend - Full IA/ML                        ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    print(f"🚀 Starting server...")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Reload: {args.reload}")
    print(f"   Log Level: {args.log_level}")
    print(f"   Workers: {args.workers}")
    
    print(f"\n📍 API Documentation:")
    print(f"   Swagger UI: http://{args.host}:{args.port}/api/v1/docs")
    print(f"   ReDoc: http://{args.host}:{args.port}/api/v1/redoc")
    print(f"   Health: http://{args.host}:{args.port}/health")
    
    print(f"\n📊 Quick Test Endpoints:")
    print(f"   GET  /api/v1/system/status")
    print(f"   POST /api/v1/route/optimize")
    print(f"   GET  /api/v1/route/alternatives")
    print(f"   POST /api/v1/forecast/congestion")
    
    print(f"\n⏳ Initializing components...")
    
    try:
        uvicorn.run(
            "api.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            workers=args.workers,
        )
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped gracefully")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
