import os
import sys
from pathlib import Path

# Add project root directory to Python path
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import FastAPI ASGI application
from src.api.main import app

# Vercel serverless function entrypoint
# The ASGI 'app' object is detected and served by @vercel/python
