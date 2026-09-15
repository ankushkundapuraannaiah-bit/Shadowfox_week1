"""
CogniStudy AI - Application Launcher
Starts the FastAPI backend and launches the web dashboard in the browser.
"""
import sys
import time
import webbrowser
import threading
import uvicorn
from backend import config


def open_browser(url: str):
    """Opens browser after server initialization."""
    time.sleep(1.2)
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main():
    url = f"http://{config.HOST}:{config.PORT}"

    print("=" * 68)
    print("  CogniStudy AI -- Intelligent Academic Utility Suite")
    print("=" * 68)
    print(f"  Server URL   : {url}")
    print(f"  Swagger Docs : {url}/docs")
    print(f"  Live Model   : {config.DEFAULT_GEMINI_MODEL}")
    print(f"  API Key Set  : {'YES (Live LLM Active)' if config.GEMINI_API_KEY else 'NO (Simulation Demo Mode Ready)'}")
    print("=" * 68)
    print("  Opening student dashboard in your browser...")
    print("  Press CTRL+C in this terminal to stop the application.\n")

    # Launch browser in a daemon thread
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    # Start Uvicorn ASGI server
    uvicorn.run(
        "backend.app:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )


if __name__ == "__main__":
    main()
