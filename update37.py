import shutil
import subprocess
import sys

# ANSI escape codes for coloring
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def get_upgradable_packages_matching(letter, short_name_filter=False):
    """Fetches upgradable packages via apt-get simulation, filtered by letter and optional 2- or 3-char length."""
    if not shutil.which("apt-get"):
        print(" 'apt-get' was not found on this system.", file=sys.stderr)
        return []

    letter = letter.lower()

    try:
        result = subprocess.run(
            ["apt-get", "-s", "upgrade"],
            text=True,
            capture_output=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        print(" Timed out while checking upgradable packages.", file=sys.stderr)
        return []
    except OSError as exc:
        print(f" Failed to run 'apt-get': {exc}", file=sys.stderr)
        return []

    if result.returncode != 0:
        err_msg = result.stderr.strip() or "Unknown apt-get error"
        print(f" 'apt-get -s upgrade' returned an error:\n{err_msg}", file=sys.stderr)
        return []

    packages = []
    for line in result.stdout.splitlines():
        if line.startswith("Inst "):
            parts = line.split()
            if len(parts) > 1:
                pkg_name = parts[1].split(":")[0]  # Strip :arch suffix if present
                packages.append(pkg_name)

    unique_packages = sorted(set(packages))

    if short_name_filter:
        return [
            pkg
            for pkg in unique_packages
            if pkg.lower().startswith(letter) and len(pkg) in (2, 3)
        ]
    return [pkg for pkg in unique_packages if pkg.lower().startswith(letter)]


def upgrade_package(pkg_name):
    """Upgrades a single package using sudo (if needed) and apt-get."""
    if not shutil.which("apt-get"):
        print(" 'apt-get' was not found on this system.", file=sys.stderr)
        return False

    cmd = ["apt-get", "install", "-y", "--only-upgrade", pkg_name]

    # If already running as root (UID 0), no need for sudo
    if hasattr(sys, "getuid") and sys.getuid() == 0:
        pass
    elif shutil.which("sudo"):
        auth = subprocess.run(["sudo", "-v"])
        if auth.returncode != 0:
            print(" Sudo authentication failed or was cancelled.", file=sys.stderr)
            return False
        cmd = ["sudo"] + cmd
    else:
        print(
            " 'sudo' not found; attempting direct 'apt-get' (requires root privileges).",
            file=sys.stderr,
        )

    print(f"\n[+] Upgrading selected package: {BOLD}{pkg_name}{RESET}...")
    try:
        upgrade_result = subprocess.run(cmd, text=True)
    except OSError as exc:
        print(f" Error launching upgrade command: {exc}", file=sys.stderr)
        return False

    return upgrade_result.returncode == 0


def main():
    print("=" * 60)
    print(" SLAX LINUX UPGRADABLE PACKAGE EXPLORER & UPGRADER ")
    print("=" * 60)
    print("Tip: Run 'sudo apt-get update' beforehand to refresh package lists.")

    while True:
        try:
            user_input = input(
                "\nEnter a letter of the alphabet to check upgradable packages (or type 'quit' to exit): "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting program. Goodbye!")
            break

        if user_input.lower() == "quit":
            print("Exiting program. Goodbye!")
            break

        if len(user_input) == 1 and user_input.isalpha():
            print(f"\nSelected letter: '{user_input.upper()}'")
            try:
                filter_choice = input(
                    "Choose listing mode:\n"
                    f"  [{CYAN}1{RESET}] All upgradable packages starting with this letter\n"
                    f"  [{CYAN}2{RESET}] Only upgradable packages whose name is 2 or 3 characters long\n"
                    "Enter your choice (1 or 2): "
                ).strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting program. Goodbye!")
                break

            if filter_choice not in ["1", "2"]:
                print(" Invalid choice. Please select 1 or 2.")
                continue

            short_name_filter = filter_choice == "2"
            filter_desc = (
                " (Name length = 2 or 3 characters)" if short_name_filter else ""
            )

            print(
                f"\n>>> Fetching upgradable packages starting with '{user_input.upper()}'{filter_desc}..."
            )
            matched_packages = get_upgradable_packages_matching(
                user_input, short_name_filter=short_name_filter
            )

            if not matched_packages:
                print(
                    f"  No upgradable packages starting with '{user_input.upper()}'{filter_desc} found."
                )
                print("-" * 60)
                continue

            print(f"\nUpgradable packages found ({len(matched_packages)}):")

            if len(matched_packages) > 9:
                display_packages = matched_packages[:18]
                left_col = display_packages[:9]
                right_col = display_packages[9:18]

                for i in range(max(len(left_col), len(right_col))):
                    left_str = f"[{i + 1}] {left_col[i]}"
                    right_str = f"[{i + 10}] {right_col[i]}" if i < len(right_col) else ""
                    print(f"  {CYAN}{left_str:<35} {right_str}{RESET}")

                if len(matched_packages) > 18:
                    print(
                        f"\n {CYAN}Warning: There are {len(matched_packages)} total packages. "
                        f"Only the first 18 are displayed. Another run is recommended after upgrading these!{RESET}"
                    )
            else:
                for idx, pkg in enumerate(matched_packages, start=1):
                    print(f"  {CYAN}[{idx}] {pkg}{RESET}")

            print("-" * 60)

            max_selectable = (
                min(len(matched_packages), 18)
                if len(matched_packages) > 9
                else len(matched_packages)
            )

            try:
                choice = input(
                    f"{CYAN}Enter the number of the package to upgrade (1-{max_selectable}) or press Enter to skip: {RESET}"
                ).strip()
            except (EOFError, KeyboardInterrupt):
                print("\nSkipping upgrade.")
                print("=" * 60)
                continue

            if not choice:
                print("Skipping upgrade.")
                print("=" * 60)
                continue

            try:
                choice_num = int(choice)
                if 1 <= choice_num <= max_selectable:
                    selected_pkg = matched_packages[choice_num - 1]
                    if upgrade_package(selected_pkg):
                        print(f"\n{CYAN}[✔] Successfully upgraded '{selected_pkg}'!{RESET}")
                    else:
                        print(
                            f"\n Error occurred while upgrading '{selected_pkg}'.",
                            file=sys.stderr,
                        )
                else:
                    print(
                        f" Invalid selection number. Please choose between 1 and {max_selectable}."
                    )
            except ValueError:
                print(" Invalid input. Please enter a valid number.")

            print("=" * 60)
        else:
            print(" Please enter a single valid alphabetical letter (A-Z).")


if __name__ == "__main__":
    main()
