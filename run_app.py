import subprocess
import sys
import os
import time

def run_app():
    # Get absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    server_dir = os.path.join(base_dir, "server")
    client_dir = os.path.join(base_dir, "client")

    print(f"Starting UMBC Manager...")
    print(f"Root: {base_dir}")

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
