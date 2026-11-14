import getpass
import subprocess
import sys

# ANSI escape codes for coloring
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def run_command(cmd):
    """Runs a read-only command and returns output text."""
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    return result.stdout


def get_upgradable_packages_matching(letter, length_filter=False):
    """Fetches upgradable packages, filters by letter and optional 3-character length."""
    letter = letter.lower()

    # Simulate upgrade to capture packages ready for update (does not require sudo)
    output = run_command("apt-get -s upgrade")
    packages = []

    for line in output.splitlines():
        if line.startswith("Inst "):
            parts = line.split()
            if len(parts) > 1:
                pkg_raw = parts[1]
                pkg_name = pkg_raw.split(":")[0]  # Strip architecture suffix if present
                packages.append(pkg_name)

    unique_packages = sorted(list(set(packages)))

    # Apply filters
    if length_filter:
        matched = [
            pkg
            for pkg in unique_packages
            if pkg.lower().startswith(letter) and len(pkg) == 3
        ]
    else:
        matched = [
            pkg for pkg in unique_packages if pkg.lower().startswith(letter)
        ]

    return matched


def main():
    print("=" * 60)
    print(" KALI LINUX UPGRADABLE PACKAGE EXPLORER & UPGRADER ")
    print("=" * 60)

    while True:
        user_input = input(
            "\nEnter a letter of the alphabet to check upgradable packages (or type 'quit' to exit): "
        ).strip()

        if user_input.lower() == "quit":
            print("Exiting program. Goodbye!")
            break

        if len(user_input) == 1 and user_input.isalpha():
            print(f"\nSelected letter: '{user_input.upper()}'")
            filter_choice = input(
                "Choose listing mode:\n"
                "  [1] All upgradable packages starting with this letter\n"
                "  [2] Only upgradable packages whose name contains exactly 3 characters\n"
                "Enter your choice (1 or 2): "
            ).strip()

            if filter_choice not in ["1", "2"]:
                print("⚠️ Invalid choice. Please select 1 or 2.")
                continue

            length_filter = filter_choice == "2"
            filter_desc = " (Name length = 3 characters)" if length_filter else ""

            print(
                f"\n>>> Fetching upgradable packages starting with '{user_input.upper()}'{filter_desc}..."
            )
            matched_packages = get_upgradable_packages_matching(
                user_input, length_filter=length_filter
            )

            if not matched_packages:
                print(
                    f"  No upgradable packages starting with '{user_input.upper()}'{filter_desc} found."
                )
                print("-" * 60)
                continue

            print(f"\nUpgradable packages found ({len(matched_packages)}):")

            # Conditional layout: if > 9 packages, display up to 18 in two columns
            if len(matched_packages) > 9:
                display_packages = matched_packages[:18]
                left_col = display_packages[:9]
                right_col = display_packages[9:18]

                for i in range(max(len(left_col), len(right_col))):
                    left_idx = i + 1
                    left_str = f"[{left_idx}] {left_col[i]}"
                    
                    right_str = ""
                    if i < len(right_col):
                        right_idx = i + 10
                        right_str = f"[{right_idx}] {right_col[i]}"

                    print(f"  {CYAN}{left_str:<35} {right_str}{RESET}")

                if len(matched_packages) > 18:
                    print(
                        f"\n⚠️ {CYAN}Warning: There are {len(matched_packages)} total packages. "
                        f"Only the first 18 are displayed. Another run is recommended after upgrading these!{RESET}"
                    )
            else:
                # Single column for 9 or fewer packages
                for idx, pkg in enumerate(matched_packages, start=1):
                    print(f"  {CYAN}[{idx}] {pkg}{RESET}")

            print("-" * 60)

            # Determine the maximum selectable option based on what is displayed
            max_selectable = min(len(matched_packages), 18) if len(matched_packages) > 9 else len(matched_packages)

            # Ask the user which package number they want to upgrade
            choice = input(
                f"Enter the number of the package to upgrade (1-{max_selectable}) or press Enter to skip: "
            ).strip()

            if not choice:
                print("Skipping upgrade.")
                print("=" * 60)
                continue

            try:
                choice_num = int(choice)
                if 1 <= choice_num <= max_selectable:
                    selected_pkg = matched_packages[choice_num - 1]
                    
                    # Prompt securely for the sudo password
                    sudo_password = getpass.getpass(
                        f"Enter sudo password to upgrade '{selected_pkg}': "
                    )
                    
                    print(f"\n[+] Upgrading selected package: {selected_pkg}...")

                    # Pass the password via stdin to sudo -S
                    upgrade_result = subprocess.run(
                        ["sudo", "-S", "apt-get", "install", "-y", "--only-upgrade", selected_pkg],
                        input=f"{sudo_password}\n",
                        text=True,
                    )

                    if upgrade_result.returncode == 0:
                        print(f"\n{CYAN}[✔] Successfully upgraded '{selected_pkg}'!{RESET}")
                    else:
                        print(
                            "\n❌ Error occurred during package upgrade (check if the password was correct).",
                            file=sys.stderr,
                        )
                else:
                    print(f"⚠️ Invalid selection number. Please choose between 1 and {max_selectable}.")
            except ValueError:
                print("⚠️ Invalid input. Please enter a valid number.")

            print("=" * 60)
        else:
            print("⚠️ Please enter a single valid alphabetical letter (A-Z).")


if __name__ == "__main__":
    main()