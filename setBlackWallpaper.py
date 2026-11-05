import os
import sys
import ctypes
import winreg

def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_black_bitmap(file_path):
    """Generates a 1x1 pixel 24-bit black BMP file."""
    # BMP header for a 1x1 24-bit bitmap
    bmp_header = bytes([
        0x42, 0x4D, 0x3A, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x36, 0x00, 0x00, 0x00, 0x28, 0x00, 
        0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 
        0x00, 0x00, 0x01, 0x00, 0x18, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x13, 0x0b, 
        0x00, 0x00, 0x13, 0x0b, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00
    ])
    with open(file_path, "wb") as f:
        f.write(bmp_header)

def set_wallpaper(image_path):
    """Updates the Windows wallpaper via the SystemParametersInfo API."""
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    
    res = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 
        0, 
        image_path, 
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    return res != 0

def update_registry(image_path):
    """Updates registry keys for Wallpaper and WallpaperStyle (Admin level)."""
    # Key for current user desktop settings
    reg_path = r"Control Panel\Desktop"
    
    try:
        # Open registry key with write permissions
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "Wallpaper", 0, winreg.REG_SZ, image_path)
            winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "0") # 0 = Centered / Solid fill
            winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")
        print("[+] Registry updated successfully.")
    except Exception as e:
        print(f"[-] Error updating registry: {e}", file=sys.stderr)

def main():
    if not is_admin():
        print("[-] This script requires Administrator privileges. Please re-run as Administrator.")
        sys.exit(1)

    # Define path to save the generated solid black bitmap
    # Windows usually caches this safely in the user's local pictures or temp folder
    target_dir = os.path.join(os.environ.get("USERPROFILE", "C:\\"), "Pictures")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
    
    bmp_path = os.path.join(target_dir, "solid_black.bmp")

    print(f"[*] Generating black bitmap at: {bmp_path}")
    create_black_bitmap(bmp_path)

    print("[*] Updating Windows Registry...")
    update_registry(bmp_path)

    print("[*] Applying wallpaper change...")
    success = set_wallpaper(bmp_path)

    if success:
        print("[+] Wallpaper successfully changed to solid black.")
    else:
        print("[-] Failed to apply wallpaper via SystemParametersInfo API.", file=sys.stderr)

if __name__ == "__main__":
    main()