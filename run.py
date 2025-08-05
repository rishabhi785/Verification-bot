#!/usr/bin/env python3
"""
Production runner for the Flask application
"""
import os
from app import app, setup_telegram_webhook

if __name__ == '__main__':
    # Setup webhook on startup
    setup_telegram_webhook()
    
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Set to False for production
    )