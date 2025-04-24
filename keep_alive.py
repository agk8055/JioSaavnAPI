import schedule
import time
import threading

def print_keep_alive():
    print(f"Keep alive - Service is running at {time.strftime('%Y-%m-%d %H:%M:%S')}")

def run_scheduler():
    # Schedule the message to print every 10 minutes
    schedule.every(10).minutes.do(print_keep_alive)
    
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    print("Starting keep-alive service...")
    # Run the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Keep the main thread alive
    while True:
        time.sleep(1) 