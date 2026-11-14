import platform
import subprocess
import sys
import socket
import os

def is_root():
    """Check if the script is running with root (administrator) privileges."""
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False

def elevate_privileges():
    """Re-run the script with sudo if not already running as root."""
    if not is_root():
        print("[*] Root privileges required. Requesting sudo access...")
        # Re-execute the script with sudo, preserving python interpreter and arguments
        script_path = os.path.abspath(sys.argv[0])
        try:
            os.execvp("sudo", ["sudo", sys.executable, script_path] + sys.argv[1:])
        except Exception as e:
            print(f"[-] Error elevating privileges: {e}")
            sys.exit(1)

def run_command(command):
    """Execute a shell command and return exit code, stdout, and stderr."""
    process = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    return process.returncode, process.stdout, process.stderr

def get_local_ip():
    """Retrieve the primary local IPv4 address of the server."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return socket.gethostbyname(socket.gethostname())

def main():
    # 1. Check if running on Linux
    if platform.system() != "Linux":
        print("[-] Error: This script must be run on a Linux machine (e.g., Linux Mint or Kali Linux).")
        sys.exit(1)
        
    # 2. Automatically ask for sudo password upfront if not root
    elevate_privileges()
        
    print("[+] Environment check passed: Running with root rights.")

    # 3. Update package list and install OpenSSH Server
    print("[*] Updating package lists and installing OpenSSH Server...")
    code, out, err = run_command("apt-get update && apt-get install -y openssh-server")
    if code != 0:
        print(f"[-] Error installing OpenSSH Server: {err.strip()}")
        sys.exit(1)
    else:
        print("[+] OpenSSH Server installed successfully.")

    # 4. Start the SSH service
    print("[*] Starting the ssh service...")
    code, out, err = run_command("systemctl start ssh")
    if code != 0:
        print(f"[-] Warning starting service: {err.strip()}")
    else:
        print("[+] ssh service started successfully.")

    # 5. Enable the SSH service to start automatically on boot
    print("[*] Configuring ssh startup type to Automatic (enabled)...")
    code, out, err = run_command("systemctl enable ssh")
    if code != 0:
        print(f"[-] Error enabling service: {err.strip()}")
    else:
        print("[+] Service startup type successfully enabled.")

    # 6. Verify and inform the user the service is running ok
    code, out, err = run_command("systemctl is-active ssh")
    status = out.strip()
    print(f"[+] Service Status Check: OpenSSH Server is currently -> {status}")

    # 7. Inform the user the IP of the server
    server_ip = get_local_ip()
    print(f"[+] Server Local IP Address: {server_ip}")

    # Get the original user who invoked sudo (if available) for the example path
    current_user = os.environ.get("SUDO_USER", os.environ.get("USER", "username"))

    # 8. Inform the user with the ready-to-use scp command
    print("\n" + "="*70)
    print("FILE TRANSFER INSTRUCTIONS (SCP):")
    print("Run the following command from your other PC to send your file:")
    print(f'scp "/path/to/your/file.zip" {current_user}@{server_ip}:/home/{current_user}/')
    print("="*70)

if __name__ == "__main__":
    main()