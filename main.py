#!/usr/bin/env python3
"""Launcher — runs the Streamlit healthcare chatbot."""
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    app_file = Path(__file__).parent / "app.py"
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_file),
         "--server.headless", "true"],
        check=True,
    )
