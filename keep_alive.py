import schedule
import time
import threading
import requests
import os

def ping_keep_alive():
    try:
        # Using the JioSaavn API URL
        base_url = "https://jiosaavnapi-bok7.onrender.com"
        response = requests.get(f"{base_url}/keep-alive/")
        if response.status_code == 200:
            print(f"Keep alive ping successful: {response.json()['message']}")
        else:
            print(f"Keep alive ping failed with status code: {response.status_code}")
    except Exception as e:
        print(f"Error in keep alive ping: {str(e)}")

def run_scheduler():
    # Schedule the ping every 10 minutes
    schedule.every(10).minutes.do(ping_keep_alive)
    
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    print("Starting keep-alive service for JioSaavn API...")
    # Run the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Keep the main thread alive
    while True:
        time.sleep(1) 