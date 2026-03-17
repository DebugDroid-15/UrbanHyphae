#!/usr/bin/env python3
"""Minimal web server that serves the dashboard - no Flask required"""

import http.server
import socketserver
import json
import threading
import time
from pathlib import Path

PORT = 5000
DASHBOARD_FILE = "/home/mushroom/mushroom_monitoring/dummy_dashboard.html"

class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        try:
            # API endpoint for sensors
            if self.path == "/api/sensors":
                response = {
                    "sensors": [
                        {"id": 1, "name": "NPK Sensor 1", "status": "online", "nitrogen": 120, "phosphorus": 45, "potassium": 180},
                        {"id": 2, "name": "NPK Sensor 2", "status": "online", "nitrogen": 115, "phosphorus": 42, "potassium": 175},
                        {"id": 3, "name": "NPK Sensor 3", "status": "online", "nitrogen": 125, "phosphorus": 48, "potassium": 185},
                        {"id": 4, "name": "NPK Sensor 4", "status": "online", "nitrogen": 110, "phosphorus": 40, "potassium": 170},
                    ]
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            # Serve dashboard HTML
            elif self.path == "/" or self.path == "/index.html":
                if Path(DASHBOARD_FILE).exists():
                    with open(DASHBOARD_FILE, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.send_header("Content-Length", len(content))
                    self.end_headers()
                    self.wfile.write(content)
                else:
                    self.send_response(404)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<h1>Dashboard file not found</h1>")
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode())
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

if __name__ == "__main__":
    try:
        with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
            print(f" * Running on http://0.0.0.0:{PORT}")
            print(f" * Press Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error: {e}")
