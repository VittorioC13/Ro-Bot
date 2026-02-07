"""
One-command setup script for Robotics Daily Report
Installs dependencies and initializes database
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"✗ Failed: {description}")
        return False
    print(f"✓ Success: {description}")
    return True

def main():
    print("\n" + "="*60)
    print("Robotics Daily Report - Setup")
    print("="*60)

    # Step 1: Install dependencies
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies"
    ):
        return False

    # Step 2: Initialize database
    if not run_command(
        f"{sys.executable} database/init_sqlite.py",
        "Initializing SQLite database"
    ):
        return False

    # Success message
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run scraper: python scrapers/scraper_manager.py")
    print("2. Start server: python api/index.py")
    print("3. Open browser: http://localhost:5000")
    print("\n" + "="*60)

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
