#!/usr/bin/env python3
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or use default 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app with debug enabled for development
    app.run(host='0.0.0.0', port=port, debug=True)