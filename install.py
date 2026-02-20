#!/usr/bin/env python3
"""Installation script for CivicSpend."""
import subprocess
import sys
from pathlib import Path


def main():
    """Run installation steps."""
    print("🚀 Installing CivicSpend...")
    print()
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Error: Python 3.11+ required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    print("✅ Python version OK")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            check=True
        )
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create directories
    print("📁 Creating directories...")
    dirs = ["data", "models", "config"]
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
        print(f"   ✅ {d}/")
    
    # Initialize database
    print("🗄️  Initializing database...")
    try:
        subprocess.run(
            [sys.executable, "-m", "civicspend.cli.main", "init"],
            check=True
        )
        print("✅ Database initialized")
    except subprocess.CalledProcessError:
        print("⚠️  Database initialization skipped (may already exist)")
    
    print()
    print("✨ Installation complete!")
    print()
    print("Next steps:")
    print("  1. Run: civicspend ingest --state MN --start-date 2022-01-01 --end-date 2024-01-31")
    print("  2. See: docs/QUICKSTART.md for full guide")
    print()


if __name__ == "__main__":
    main()
