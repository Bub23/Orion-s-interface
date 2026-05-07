#!/usr/bin/env python3
"""
Sound Savage AI - Startup script
Initializes database and runs the Flask server
"""

import os
import sys
from database.schema import init_db

print("""
╔══════════════════════════════════════════╗
║   SOUND SAVAGE AI - WAR ROOM ONLINE      ║
║   Content Engine v1.0                    ║
╚══════════════════════════════════════════╝
""")

# Initialize database
print("[*] Initializing database...")
os.makedirs("database", exist_ok=True)
init_db()

# Run Flask server
print("[*] Starting Flask server on http://localhost:5000")
print("[*] Dashboard: http://localhost:5000/dashboard")
print("[*] API Docs: http://localhost:5000/api/")

from api.routes import app

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
