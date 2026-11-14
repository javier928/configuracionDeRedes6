import platform
import subprocess
import sys
import socket
import ctypes

def is_admin():
    """Check if the script is running with Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_powershell(command):
    """Execute a PowerShell command and return exit code, stdout, and stderr."""
    process = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
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
    # 1. Check if running on Windows and verify Administrator privileges
    if platform.system() != "Windows":
        print("[-] Error: This script must be run on a Windows machine or Windows Server.")
        sys.exit(1)
        
    if not is_admin():
        print("[-] Error: Administrator privileges are required.")
        print("    Please right-click your terminal/command prompt and select 'Run as administrator'.")
        sys.exit(1)
        
    print("[+] Environment check passed: Running on Windows with Administrator rights.")

    # 2. Activate or enable the OpenSSH Server capability
    print("[*] Enabling OpenSSH Server capability...")
    code, out, err = run_powershell("Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0")
    if code != 0 and "already installed" not in err.lower() and "already installed" not in out.lower():
        print(f"[*] Note during capability setup: {out.strip() or err.strip()}")
    else:
        print("[+] OpenSSH Server capability is enabled.")

    # 3. Start the service
    print("[*] Starting the sshd service...")
    code, out, err = run_powershell("Start-Service sshd")
    if code != 0:
        print(f"[-] Warning starting service: {err.strip()}")
    else:
        print("[+] sshd service started successfully.")

    # 4. Set-Service -Name sshd -StartupType Automatic
    print("[*] Configuring sshd startup type to Automatic...")
    code, out, err = run_powershell("Set-Service -Name sshd -StartupType Automatic")
    if code != 0:
        print(f"[-] Error setting startup type: {err.strip()}")
    else:
        print("[+] Service startup type successfully set to Automatic.")

    # 5. Verify and inform the user the service is running ok
    code, out, err = run_powershell("(Get-Service sshd).Status")
    status = out.strip()
    print(f"[+] Service Status Check: OpenSSH Server is currently -> {status}")

    # 6. Inform the user the IP of the server
    server_ip = get_local_ip()
    print(f"[+] Server Local IP Address: {server_ip}")

    # 7. Inform the user with the ready-to-use pscp command
    print("\n" + "="*70)
    print("FILE TRANSFER INSTRUCTIONS (SCP):")
    print("Run the following command from your other PC to send your file:")
    print(f'scp "C:\\path\\to\\your\\file.zip" username@{server_ip}:C:\\Path\\To\\Destination\\')
    print("="*70)

if __name__ == "__main__":
    main()