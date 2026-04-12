#!/usr/bin/env python
"""
SheSecure - Women's Safety Application
Simple startup script for running the Flask app
"""

import os
import sys
from app import app, initialize_app_data

if __name__ == "__main__":
    print("=" * 60)
    print("SheSecure - Women's Safety Application")
    print("=" * 60)
    print("\nInitializing database and loading data...")
    
    try:
        initialize_app_data()
        print("\n✓ Database initialized successfully!")
        print("\n" + "=" * 60)
        print("Starting SheSecure Server...")
        print("=" * 60)
        print("\n🔗 Access the application at:")
        print("   http://localhost:5000")
        print("\n📝 You can also access from other devices on your network:")
        print("   http://YOUR_COMPUTER_IP:5000")
        print("\n💡 First time? Create an account using the signup page!")
        print("\nPress Ctrl+C to stop the server.")
        print("=" * 60 + "\n")
        
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"\n❌ Error starting the app: {str(e)}")
        sys.exit(1)
