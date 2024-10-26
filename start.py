import subprocess
import time
import webbrowser
import os

def main():
    # Start Docker containers
    print("Starting Weather Monitoring System...")
    subprocess.run(["docker-compose", "up", "-d", "--build"])
    
    # Wait for services to be ready
    print("Waiting for services to start...")
    time.sleep(10)  # Wait 10 seconds for services to initialize
    
    # Open browser
    print("Opening application in browser...")
    webbrowser.open('http://localhost:8000')
    
    # Keep containers running
    print("\nApplication is running!")
    print("Access the dashboard at: http://localhost:8000")
    print("Press Ctrl+C to stop the application")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        subprocess.run(["docker-compose", "down"])
        print("Application stopped.")

if __name__ == "__main__":
    main()