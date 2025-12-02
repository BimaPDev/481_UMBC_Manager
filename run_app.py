import subprocess
import sys
import os
import time

def free_port(port):
    """
    Checks if a port is in use and kills the process holding it.
    """
    print(f"   Checking port {port}...")
    try:
        if os.name == 'nt': # Windows
            # Find PID
            result = subprocess.run(
                ["netstat", "-ano"], 
                capture_output=True, text=True
            )
            lines = result.stdout.splitlines()
            pid = None
            for line in lines:
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    pid = parts[-1]
                    break
            
            if pid:
                print(f"   ⚠️ Port {port} is in use by PID {pid}. Killing...")
                subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                print(f"   ✅ Port {port} freed.")
            else:
                print(f"   ✅ Port {port} is free.")

        else: # Linux/MacOS
            # Using lsof to find PID
            try:
                result = subprocess.run(
                    ["lsof", "-t", "-i", f":{port}"],
                    capture_output=True, text=True
                )
                pids = result.stdout.strip().split()
                if pids:
                    print(f"   ⚠️ Port {port} is in use by PID(s) {', '.join(pids)}. Killing...")
                    for pid in pids:
                        subprocess.run(["kill", "-9", pid])
                    print(f"   ✅ Port {port} freed.")
                else:
                    print(f"   ✅ Port {port} is free.")
            except FileNotFoundError:
                # lsof might not be installed
                pass

    except Exception as e:
        print(f"   ❌ Error checking/freeing port {port}: {e}")

def run_app():
    # Get absolute paths

    base_dir = os.path.dirname(os.path.abspath(__file__))
    server_dir = os.path.join(base_dir, "server")
    client_dir = os.path.join(base_dir, "client")

    print(f"Starting UMBC Manager...")
    print(f"Root: {base_dir}")

    # --- DEPENDENCY CHECK & INSTALL ---
    print("\n🔍 Checking dependencies...")

    # 1. Server Dependencies
    requirements_file = os.path.join(server_dir, "requirements.txt")
    if os.path.exists(requirements_file):
        print("   Checking server dependencies...")
        try:
            # Check if packages are installed by trying to import them or just run pip install
            # Running pip install is safer and usually fast if already satisfied
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=server_dir)
            print("   ✅ Server dependencies satisfied.")
        except subprocess.CalledProcessError:
            print("   ❌ Failed to install server dependencies.")
            input("Press Enter to continue anyway (or Ctrl+C to exit)...")
    else:
        print("   ⚠️ No requirements.txt found for server.")

    # 2. Client Dependencies
    node_modules_dir = os.path.join(client_dir, "node_modules")
    npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"
    
    if not os.path.exists(node_modules_dir):
        print("   ⚠️ Client node_modules not found. Installing...")
        try:
            subprocess.check_call([npm_cmd, "install"], cwd=client_dir)
            print("   ✅ Client dependencies installed.")
        except subprocess.CalledProcessError:
            print("   ❌ Failed to install client dependencies.")
            input("Press Enter to continue anyway (or Ctrl+C to exit)...")
    else:
        print("   ✅ Client node_modules found.")
    
    print("--------------------------------------------------")

    # --- PORT CLEANUP ---
    print("\n🧹 Ensuring ports are free...")
    free_port(8000)
    free_port(5173)
    print("--------------------------------------------------")

    processes = []

    try:
        # 1. Start Backend
        print("\n🚀 Starting Backend Server (Port 8000)...")
        backend = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=server_dir,
            shell=False  # Better for signal handling if possible, but might need shell=True on Windows for some envs
        )
        processes.append(backend)

        # 2. Start Frontend
        print("🚀 Starting Frontend Client (Port 5173)...")
        # Use 'npm.cmd' on Windows, 'npm' otherwise
        npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"
        
        frontend = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=client_dir,
            shell=False 
        )
        processes.append(frontend)

        print("\n✅ App is running!")
        print("Backend API: http://localhost:8000")
        print("Frontend UI: http://localhost:5173")
        print("\nPress Ctrl+C to stop everything.\n")

        # Keep main script alive
        while True:
            time.sleep(1)
            if backend.poll() is not None:
                print("❌ Backend process ended unexpectedly.")
                break
            if frontend.poll() is not None:
                print("❌ Frontend process ended unexpectedly.")
                break

    except KeyboardInterrupt:
        print("\n🛑 Stopping app...")
    finally:
        print("Terminating processes...")
        for p in processes:
            if p.poll() is None:
                # On Windows, terminate() might not kill the whole tree if shell=True was used,
                # but with shell=False it should be okay for direct executables.
                # For npm, it spawns node.
                if os.name == 'nt':
                    # Force kill tree to ensure node.exe dies
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
                else:
                    p.terminate()
        print("Goodbye!")

if __name__ == "__main__":
    run_app()
