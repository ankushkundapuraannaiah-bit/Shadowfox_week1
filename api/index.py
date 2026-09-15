"""
Vercel serverless function entry point.
Re-exports the FastAPI app from the backend package so Vercel's Python
runtime can discover and serve it via @vercel/python.
"""
import sys
import os

# Ensure the project root is on the path so `backend` package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.app import app  # noqa: F401 – Vercel imports 'app' from this module
