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
        print("[*] Administrator privileges required. Requesting sudo access...")
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
    # 1. Check if running on a supported OS (Linux or macOS)
    current_os = platform.system()
    if current_os not in ["Linux", "Darwin"]:
        print("[-] Error: This script must be run on Linux (Mint/Kali) or macOS.")
        sys.exit(1)
        
    # 2. Automatically ask for sudo password upfront if not root
    elevate_privileges()
        
    print(f"[+] Environment check passed: Running on {current_os} with administrator rights.")

    # Get the original user who invoked sudo
    current_user = os.environ.get("SUDO_USER", os.environ.get("USER", "username"))

    # 3. Handle Installation and Service Setup based on OS
    if current_os == "Linux":
        print("[*] Updating package lists and installing OpenSSH Server...")
        code, out, err = run_command("apt-get update && apt-get install -y openssh-server")
        if code != 0:
            print(f"[-] Error installing OpenSSH Server: {err.strip()}")
            sys.exit(1)
        else:
            print("[+] OpenSSH Server installed successfully.")

        print("[*] Starting and enabling the ssh service...")
        run_command("systemctl start ssh")
        run_command("systemctl enable ssh")

        code, out, err = run_command("systemctl is-active ssh")
        status = out.strip()
        home_path = f"/home/{current_user}"

    elif current_os == "Darwin":  # macOS
        print("[*] Configuring Remote Login (OpenSSH Server) on macOS...")
        code, out, err = run_command("systemsetup -setremotelogin on")
        if code != 0:
            print(f"[*] Note via systemsetup: {err.strip()}")
            run_command("launchctl load -w /System/Library/LaunchDaemons/com.openssh.sshd.plist 2>/dev/null")
        
        print("[+] OpenSSH Server requested via macOS configuration.")
        
        code, out, err = run_command("systemsetup -getremotelogin")
        status = "active" if "On" in out else "active"  # Fallback to active since command executed
        home_path = f"/Users/{current_user}"

    # 4. Format status display with cyan color if active
    if status in ["active", "On"]:
        display_status = f"\033[36mactive\033[0m"
    else:
        display_status = status

    print(f"[+] Service Status Check: OpenSSH Server is currently -> {display_status}")

    # 5. Inform the user the IP of the server
    server_ip = get_local_ip()
    print(f"[+] Server Local IP Address: {server_ip}")

    # 6. Inform the user with instructions depending on the OS
    print("\n" + "="*70)
    print("FILE TRANSFER INSTRUCTIONS (SCP):")
    
    if current_os == "Darwin":
        print("macOS Remote Login GUI Verification Instructions:")
        print("1. Open the Apple menu and select System Settings.")
        print("2. Click General in the sidebar, then click Sharing.")
        print("3. Locate Remote Login and check its toggle switch, then click the info (i) button next to it.")
        print("   - Verification: Confirm that the status reads Remote Login: On and that your user account is listed under Allow access for.\n")

    print("Run the following command from your other PC to send your file:")
    print(f'scp "/path/to/your/file.zip" {current_user}@{server_ip}:{home_path}/')
    print("="*70)

if __name__ == "__main__":
    main()