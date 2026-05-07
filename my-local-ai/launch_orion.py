import subprocess
import webbrowser
import time
import os
import sys
import socket

def get_local_ip():
    """Get local network IP address."""
    try:
        # Connect to a public DNS to find local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def launch_orion():
    """Launch Orion OS and show network details."""
    
    orion_dir = r"C:\Users\outla\Documents\Orion's interface\my-local-ai"
    
    os.chdir(orion_dir)
    os.environ.setdefault("ORION_LLM_TIMEOUT", "12")
    
    # Start Flask server (hidden)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    
    print("\n" + "="*60)
    print("🧠 ORION OS STARTING")
    print("="*60)
    print("\n⏳ Initializing Orion...")
    
    subprocess.Popen(
        [sys.executable, "app.py"],
        startupinfo=startupinfo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    time.sleep(5)
    
    # Get IP address
    local_ip = get_local_ip()
    
    print("\n✓ Orion is running!")
    print("\n📱 PHONE ACCESS:")
    print(f"   Open browser on your phone and go to:")
    print(f"   http://{local_ip}:5000")
    print("\n💻 DESKTOP ACCESS:")
    print(f"   http://localhost:5000")
    print("\n" + "="*60)
    print("\nOrion Features:")
    print("  ✓ Persistent memory across restarts")
    print("  ✓ Auto-learn from conversations")
    print("  ✓ Web search capability")
    print("  ✓ Image generation")
    print("  ✓ Emotion detection")
    print("  ✓ Works on desktop & mobile")
    print("\n" + "="*60 + "\n")
    
    # Open on desktop
    webbrowser.open("http://localhost:5000")
    
    print("💡 TIP: Both devices must be on the same WiFi network")
    print("Press Ctrl+C to stop Orion\n")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Orion is shutting down...\n")

if __name__ == "__main__":
    try:
        launch_orion()
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")
