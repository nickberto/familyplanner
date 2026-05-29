"""
WSGI entry point for the application.
"""
import os
from familyplanner.app import create_app

# Load environment
os.environ.setdefault("ENV", "development")

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
