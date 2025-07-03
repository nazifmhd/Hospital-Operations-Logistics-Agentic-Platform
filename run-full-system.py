#!/usr/bin/env python3
"""
Full System Startup Script
Starts both backend and frontend servers for the Hospital Operations Platform
"""

import subprocess
import sys
import time
import os
import signal
import threading
from pathlib import Path

class SystemRunner:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True
        
    def start_backend(self):
        """Start the FastAPI backend server"""
        print("🚀 Starting backend server...")
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "src.main:app", 
                "--reload", 
                "--host", "0.0.0.0", 
                "--port", "8000"
            ], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            universal_newlines=True,
            bufsize=1
            )
            
            # Monitor backend output in a separate thread
            def monitor_backend():
                for line in iter(self.backend_process.stdout.readline, ''):
                    if self.running:
                        print(f"[BACKEND] {line.strip()}")
                    else:
                        break
            
            backend_thread = threading.Thread(target=monitor_backend, daemon=True)
            backend_thread.start()
            
            print("✅ Backend server starting on http://localhost:8000")
            time.sleep(3)  # Give backend time to start
            return True
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the Vite frontend server"""
        print("🚀 Starting frontend server...")
        
        frontend_path = Path("frontend")
        if not frontend_path.exists():
            print("❌ Frontend directory not found")
            return False
        
        try:
            # Change to frontend directory and start
            self.frontend_process = subprocess.Popen([
                "npm", "run", "dev"
            ], 
            cwd=frontend_path,
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            universal_newlines=True,
            bufsize=1,
            shell=True  # Required for Windows
            )
            
            # Monitor frontend output in a separate thread
            def monitor_frontend():
                for line in iter(self.frontend_process.stdout.readline, ''):
                    if self.running:
                        print(f"[FRONTEND] {line.strip()}")
                    else:
                        break
            
            frontend_thread = threading.Thread(target=monitor_frontend, daemon=True)
            frontend_thread.start()
            
            print("✅ Frontend server starting on http://localhost:3000")
            time.sleep(3)  # Give frontend time to start
            return True
            
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def check_health(self):
        """Check if both servers are healthy"""
        try:
            import requests
            
            # Check backend health
            backend_response = requests.get("http://localhost:8000/health", timeout=5)
            backend_healthy = backend_response.status_code == 200
            
            # Check frontend (just check if it responds)
            frontend_response = requests.get("http://localhost:3000", timeout=5)
            frontend_healthy = frontend_response.status_code == 200
            
            return backend_healthy, frontend_healthy
            
        except Exception as e:
            print(f"Health check failed: {e}")
            return False, False
    
    def stop_servers(self):
        """Stop both servers gracefully"""
        print("\n🛑 Stopping servers...")
        self.running = False
        
        if self.backend_process:
            print("Stopping backend server...")
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            except Exception as e:
                print(f"Error stopping backend: {e}")
        
        if self.frontend_process:
            print("Stopping frontend server...")
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            except Exception as e:
                print(f"Error stopping frontend: {e}")
        
        print("✅ All servers stopped")
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signal"""
        print(f"\nReceived signal {signum}")
        self.stop_servers()
        sys.exit(0)
    
    def run(self):
        """Main run loop"""
        # Register signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🏥 Hospital Operations Platform - Full System Startup")
        print("=" * 60)
        
        # Start backend
        if not self.start_backend():
            print("❌ Failed to start backend. Exiting.")
            return False
        
        # Start frontend
        if not self.start_frontend():
            print("❌ Failed to start frontend. Backend is still running.")
            print("You can access the API at: http://localhost:8000/docs")
            # Don't exit, keep backend running
        
        # Wait a bit more for full startup
        print("\n⏳ Waiting for servers to fully initialize...")
        time.sleep(5)
        
        # Check health
        print("\n🔍 Checking server health...")
        backend_healthy, frontend_healthy = self.check_health()
        
        print("\n📋 System Status:")
        print(f"Backend (API):  {'✅ HEALTHY' if backend_healthy else '❌ UNHEALTHY'}")
        print(f"Frontend (UI):  {'✅ HEALTHY' if frontend_healthy else '❌ UNHEALTHY'}")
        
        if backend_healthy:
            print(f"\n🌐 Access Points:")
            print(f"• API Documentation: http://localhost:8000/docs")
            print(f"• API Health Check:  http://localhost:8000/health")
            if frontend_healthy:
                print(f"• Web Interface:     http://localhost:3000")
        
        print(f"\n💡 Tips:")
        print(f"• Press Ctrl+C to stop all servers")
        print(f"• Backend logs are prefixed with [BACKEND]")
        print(f"• Frontend logs are prefixed with [FRONTEND]")
        print(f"• API endpoints are available at /api/v1/...")
        
        print(f"\n🏥 Hospital Operations Platform is now running!")
        print(f"=" * 60)
        
        # Keep running until interrupted
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_servers()
        
        return True

def main():
    """Main entry point"""
    runner = SystemRunner()
    
    try:
        success = runner.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
