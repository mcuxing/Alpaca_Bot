import time
import subprocess
import os
from datetime import datetime
import pytz

def run_trading_bot():
    print(f"\n--- Starting Trading Bot Execution: {datetime.now()} ---")
    try:
        # Run main.py using the same python interpreter
        result = subprocess.run(["python3", "main.py"], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
    except Exception as e:
        print(f"Failed to run bot: {e}")

def is_trading_time():
    """
    Checks if it is time to run the bot.
    Target: Market Open (9:30 AM EST) + 5 minutes buffer = 9:35 AM EST.
    Runs only on weekdays (Mon-Fri).
    """
    ny_tz = pytz.timezone('America/New_York')
    now_ny = datetime.now(ny_tz)
    
    # Check if weekday (0=Mon, 4=Fri)
    if now_ny.weekday() > 4:
        return False
        
    # Check time window (e.g., 9:35 AM - 9:36 AM)
    # This simple logic assumes the script loop runs frequently enough
    if now_ny.hour == 9 and now_ny.minute == 35:
        return True
        
    return False

def main():
    print("Scheduler started. Waiting for trading time (09:35 EST)...")
    print("Press Ctrl+C to stop.")
    
    # Track if we already ran today to avoid multiple executions in the same minute
    last_run_date = None
    
    while True:
        ny_tz = pytz.timezone('America/New_York')
        now_ny = datetime.now(ny_tz)
        current_date = now_ny.date()
        
        # Check if trading time and haven't ran today
        if is_trading_time() and last_run_date != current_date:
            run_trading_bot()
            last_run_date = current_date
            print("Execution complete. Waiting for next day...")
            
        # Sleep for 30 seconds
        time.sleep(30)

if __name__ == "__main__":
    main()
