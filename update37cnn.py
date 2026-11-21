import os
import shutil
import subprocess
import tkinter as tk
from tkinter import scrolledtext, simpledialog


class SlaxUpgraderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Slax Linux Upgradable Package Explorer (2-Pane)")
        self.root.geometry("920x560")
        self.root.minsize(760, 460)

        # Main container using PanedWindow for dual vertical panes
        self.paned_window = tk.PanedWindow(
            root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=4
        )
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- LEFT WINDOW: Messages, Logs & Inputs ---
        self.left_frame = tk.Frame(self.paned_window, padx=10, pady=10)
        self.paned_window.add(self.left_frame, width=460)

        self.lbl_left = tk.Label(
            self.left_frame, text="Console & Controls", font=("Arial", 11, "bold")
        )
        self.lbl_left.pack(anchor="w", pady=(0, 5))

        self.console_log = scrolledtext.ScrolledText(
            self.left_frame,
            wrap=tk.WORD,
            font=("Courier", 10),
            bg="#1e1e1e",
            fg="#00ff00",
        )
        self.console_log.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.console_log.tag_config("cyan", foreground="#00ffff")
        self.console_log.tag_config("yellow", foreground="#ffff00")
        self.console_log.config(state=tk.DISABLED)

        # Input Frame at the bottom of the left pane
        self.input_frame = tk.Frame(self.left_frame)
        self.input_frame.pack(fill=tk.X, pady=5)

        self.lbl_prompt = tk.Label(
            self.input_frame, text="Enter Letter (A-Z):", font=("Arial", 10, "bold")
        )
        self.lbl_prompt.pack(anchor="w", pady=2)

        self.entry_input = tk.Entry(self.input_frame, font=("Arial", 11))
        self.entry_input.pack(fill=tk.X, pady=2)
        self.entry_input.bind("<Return>", self.handle_user_input)
        self.entry_input.focus_set()

        # --- RIGHT WINDOW: Upgradable Packages List ---
        self.right_frame = tk.Frame(self.paned_window, padx=10, pady=10)
        self.paned_window.add(self.right_frame, width=460)

        self.lbl_right = tk.Label(
            self.right_frame,
            text="Upgradable Packages (Right Pane)",
            font=("Arial", 11, "bold"),
        )
        self.lbl_right.pack(anchor="w", pady=(0, 5))

        self.listbox_frame = tk.Frame(self.right_frame)
        self.listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.scrollbar = tk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL)
        self.pkg_listbox = tk.Listbox(
            self.listbox_frame,
            font=("Courier", 11, "bold"),
            selectbackground="cyan",
            selectforeground="black",
            yscrollcommand=self.scrollbar.set,
            exportselection=False,
        )
        self.scrollbar.config(command=self.pkg_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.pkg_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # State management for workflow
        self.step = "GET_LETTER"
        self.busy = False
        self.current_letter = ""
        self.filter_choice = "1"
        self.matched_packages = []

        # Initial startup message
        self.log_message("=== SLAX LINUX UPGRADABLE PACKAGE EXPLORER ===")
        self.log_message("System ready. Tip: Run 'sudo apt-get update' first if needed.")
        self.log_message(
            "Please enter an alphabetical letter (A-Z) in the input box below to search for upgradable packages:\n"
        )

    def log_message(self, message, tag=None):
        """Appends text to the left console log window, optionally styled with a tag."""
        self.console_log.config(state=tk.NORMAL)
        if tag:
            self.console_log.insert(tk.END, message + "\n", tag)
        else:
            self.console_log.insert(tk.END, message + "\n")
        self.console_log.see(tk.END)
        self.console_log.config(state=tk.DISABLED)

    def log_upgrading(self, pkg_name):
        """Logs '[+] Upgrading <pkg>...' with the word 'Upgrading' colored cyan."""
        self.console_log.config(state=tk.NORMAL)
        self.console_log.insert(tk.END, "[+] ")
        self.console_log.insert(tk.END, "Upgrading", "cyan")
        self.console_log.insert(tk.END, f" {pkg_name}...\n")
        self.console_log.see(tk.END)
        self.console_log.config(state=tk.DISABLED)

    def set_input_enabled(self, enabled):
        """Enables or disables the user input entry widget."""
        self.busy = not enabled
        state = tk.NORMAL if enabled else tk.DISABLED
        self.entry_input.config(state=state)
        if enabled:
            self.entry_input.focus_set()

    def reset_to_letter_prompt(self):
        """Resets workflow back to waiting for a letter."""
        self.pkg_listbox.delete(0, tk.END)
        self.log_message("\n----------------------------------------")
        self.log_message("Enter another letter to search (or type 'quit' to exit):")
        self.lbl_prompt.config(text="Enter Letter (A-Z):")
        self.step = "GET_LETTER"
        self.set_input_enabled(True)

    def fetch_upgradable(self, letter, short_name_filter=False):
        """Fetches upgradable packages via apt-get simulation without shell=True."""
        if not shutil.which("apt-get"):
            self.log_message("❌ 'apt-get' was not found on this system.")
            return []

        try:
            result = subprocess.run(
                ["apt-get", "-s", "upgrade"],
                text=True,
                capture_output=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            self.log_message("❌ Timed out while checking upgradable packages.")
            return []
        except OSError as exc:
            self.log_message(f"❌ Failed to run 'apt-get': {exc}")
            return []

        if result.returncode != 0:
            err_msg = result.stderr.strip() or "Unknown apt-get error"
            self.log_message(f"⚠️ 'apt-get -s upgrade' error: {err_msg}")
            return []

        packages = []
        for line in result.stdout.splitlines():
            if line.startswith("Inst "):
                parts = line.split()
                if len(parts) > 1:
                    pkg_name = parts[1].split(":")[0]
                    packages.append(pkg_name)

        unique_packages = sorted(set(packages))
        letter = letter.lower()

        if short_name_filter:
            return [
                pkg
                for pkg in unique_packages
                if pkg.lower().startswith(letter) and len(pkg) in (2, 3)
            ]
        return [pkg for pkg in unique_packages if pkg.lower().startswith(letter)]

    def perform_upgrade(self, selected_pkg):
        """Upgrades a single package safely from the GUI."""
        if not shutil.which("apt-get"):
            self.log_message("❌ 'apt-get' was not found on this system.")
            return False

        cmd = ["apt-get", "install", "-y", "--only-upgrade", selected_pkg]
        stdin_data = None

        if hasattr(os, "geteuid") and os.geteuid() == 0:
            pass
        elif shutil.which("sudo"):
            sudo_pwd = simpledialog.askstring(
                "Sudo Authentication",
                f"Enter sudo password to upgrade '{selected_pkg}':",
                show="*",
                parent=self.root,
            )
            if sudo_pwd is None:
                self.log_message("⚠️ Upgrade cancelled by user.")
                return False
            cmd = ["sudo", "-S"] + cmd
            stdin_data = f"{sudo_pwd}\n"
        else:
            self.log_message(
                "⚠️ 'sudo' not found; attempting direct 'apt-get' (requires root)."
            )

        self.log_upgrading(selected_pkg)
        self.root.update_idletasks()

        try:
            upgrade_res = subprocess.run(
                cmd,
                input=stdin_data,
                text=True,
                capture_output=True,
            )
        except OSError as exc:
            self.log_message(f"❌ Error running upgrade command: {exc}")
            return False

        if upgrade_res.returncode == 0:
            self.log_message(
                f"[✔] Package '{selected_pkg}' upgraded successfully!",
                tag="yellow",
            )
            return True

        err_detail = upgrade_res.stderr.strip() or upgrade_res.stdout.strip()
        self.log_message(f"❌ Upgrade failed for '{selected_pkg}'.")
        if err_detail:
            tail_lines = "\n".join(err_detail.splitlines()[-6:])
            self.log_message(tail_lines)
        return False

    def handle_user_input(self, event=None):
        if self.busy:
            return

        user_val = self.entry_input.get().strip()
        self.entry_input.delete(0, tk.END)

        if user_val.lower() == "quit":
            self.log_message("Exiting program. Goodbye!")
            self.set_input_enabled(False)
            self.root.after(800, self.root.destroy)
            return

        if self.step == "GET_LETTER":
            if len(user_val) == 1 and user_val.isalpha():
                self.current_letter = user_val.lower()
                self.log_message(f"> Selected letter: '{self.current_letter.upper()}'")
                self.log_message("Choose listing mode:")
                self.log_message("  [1] All packages starting with this letter")
                self.log_message(
                    "  [2] Only packages whose name is 2 or 3 characters long"
                )
                self.lbl_prompt.config(text="Enter choice (1 or 2):")
                self.step = "GET_FILTER_CHOICE"
            else:
                self.log_message(
                    "⚠️ Please enter a single valid alphabetical letter (A-Z)."
                )

        elif self.step == "GET_FILTER_CHOICE":
            if user_val in ["1", "2"]:
                self.filter_choice = user_val
                short_name_filter = self.filter_choice == "2"
                filter_desc = (
                    " (Name length = 2 or 3 characters)" if short_name_filter else ""
                )

                self.log_message(f"\n> Selected choice: {user_val}")
                self.set_input_enabled(False)

                # Create "Loading data..." Popup Window
                loading_win = tk.Toplevel(self.root)
                loading_win.title("Please Wait")
                loading_win.geometry("260x120")
                loading_win.transient(self.root)
                loading_win.grab_set()

                x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - 130
                y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 60
                loading_win.geometry(f"+{x}+{y}")

                tk.Label(
                    loading_win,
                    text="Loading data...",
                    font=("Arial", 12, "bold"),
                    fg="#333333",
                    padx=20,
                    pady=30,
                ).pack(expand=True)
                loading_win.update()

                def finish_loading():
                    try:
                        self.matched_packages = self.fetch_upgradable(
                            self.current_letter,
                            short_name_filter=short_name_filter,
                        )
                    finally:
                        if loading_win.winfo_exists():
                            loading_win.grab_release()
                            loading_win.destroy()
                    self.render_packages(filter_desc)

                self.root.after(1500, finish_loading)
            else:
                self.log_message("⚠️ Invalid choice. Please enter 1 or 2.")

        elif self.step == "GET_PACKAGE_SELECTION":
            max_selectable = min(len(self.matched_packages), 18)
            try:
                choice_num = int(user_val)
                if 1 <= choice_num <= max_selectable:
                    idx = choice_num - 1
                    selected_pkg = self.matched_packages[idx]

                    # Highlight selection in right-hand listbox
                    self.pkg_listbox.selection_clear(0, tk.END)
                    self.pkg_listbox.selection_set(idx)
                    self.pkg_listbox.see(idx)

                    self.log_message(
                        f"\n> Selected package for upgrade: {selected_pkg}"
                    )
                    self.set_input_enabled(False)
                    self.perform_upgrade(selected_pkg)
                    self.reset_to_letter_prompt()
                else:
                    self.log_message(
                        f"⚠️ Invalid number. Choose between 1 and {max_selectable}."
                    )
            except ValueError:
                self.log_message("⚠️ Invalid input. Please enter a valid number.")

    def render_packages(self, filter_desc):
        self.log_message(
            f"\n> Fetching upgradable packages starting with '{self.current_letter.upper()}'{filter_desc}..."
        )
        self.pkg_listbox.delete(0, tk.END)

        if not self.matched_packages:
            self.log_message("❌ No upgradable packages found.")
            self.reset_to_letter_prompt()
            return

        self.log_message(
            f"✔ Found {len(self.matched_packages)} packages. Displaying in right window."
        )

        display_packages = self.matched_packages[:18]
        for idx, pkg in enumerate(display_packages, start=1):
            self.pkg_listbox.insert(tk.END, f"[{idx}] {pkg}")

        if len(self.matched_packages) > 18:
            self.log_message(
                f"⚠️ Warning: {len(self.matched_packages)} total packages found. "
                f"Only the first 18 are displayed. Another run is recommended afterwards!"
            )

        self.log_message(
            "\nEnter the number of the package you want to upgrade from the right pane:"
        )
        self.lbl_prompt.config(text="Enter package number to upgrade:")
        self.step = "GET_PACKAGE_SELECTION"
        self.set_input_enabled(True)


def main():
    root = tk.Tk()
    SlaxUpgraderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()