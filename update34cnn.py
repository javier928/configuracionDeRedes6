import getpass
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext

class KaliUpgraderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kali Linux Upgradable Package Explorer (NC Style)")
        self.root.geometry("900x550")
        self.root.minsize(750, 450)

        # Main container using PanedWindow for dual vertical panes
        self.paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=4)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- LEFT WINDOW: Messages, Logs & Inputs ---
        self.left_frame = tk.Frame(self.paned_window, padx=10, pady=10)
        self.paned_window.add(self.left_frame, width=450)

        self.lbl_left = tk.Label(self.left_frame, text="Console & Controls", font=("Arial", 11, "bold"))
        self.lbl_left.pack(anchor="w", pady=(0, 5))

        # Scrolled text widget for logs and messages
        self.console_log = scrolledtext.ScrolledText(self.left_frame, wrap=tk.WORD, font=("Courier", 10), bg="#1e1e1e", fg="#00ff00")
        self.console_log.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.console_log.config(state=tk.DISABLED)

        # Input Frame at the bottom of the left pane
        self.input_frame = tk.Frame(self.left_frame)
        self.input_frame.pack(fill=tk.X, pady=5)

        self.lbl_prompt = tk.Label(self.input_frame, text="Enter Letter (A-Z):", font=("Arial", 10, "bold"))
        self.lbl_prompt.pack(anchor="w", pady=2)

        self.entry_input = tk.Entry(self.input_frame, font=("Arial", 11))
        self.entry_input.pack(fill=tk.X, pady=2)
        self.entry_input.bind("<Return>", self.handle_user_input)
        self.entry_input.focus_set()

        # --- RIGHT WINDOW: Upgradable Packages List ---
        self.right_frame = tk.Frame(self.paned_window, padx=10, pady=10)
        self.paned_window.add(self.right_frame, width=450)

        self.lbl_right = tk.Label(self.right_frame, text="Upgradable Packages (Right Pane)", font=("Arial", 11, "bold"))
        self.lbl_right.pack(anchor="w", pady=(0, 5))

        # Listbox for packages with Cyan selection
        self.listbox_frame = tk.Frame(self.right_frame)
        self.listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.scrollbar = tk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL)
        self.pkg_listbox = tk.Listbox(
            self.listbox_frame,
            font=("Courier", 11, "bold"),
            selectbackground="cyan",
            selectforeground="black",
            yscrollcommand=self.scrollbar.set,
            exportselection=False
        )
        self.scrollbar.config(command=self.pkg_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.pkg_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # State management for workflow
        self.step = "GET_LETTER"
        self.current_letter = ""
        self.filter_choice = "1"
        self.matched_packages = []

        # Initial startup message
        self.log_message("=== KALI LINUX UPGRADABLE PACKAGE EXPLORER ===")
        self.log_message("System ready.")
        self.log_message("Please enter an alphabetical letter (A-Z) in the input box below to search for upgradable packages:\n")

    def log_message(self, message):
        """Appends text to the left console log window."""
        self.console_log.config(state=tk.NORMAL)
        self.console_log.insert(tk.END, message + "\n")
        self.console_log.see(tk.END)
        self.console_log.config(state=tk.DISABLED)

    def run_command(self, cmd):
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        return result.stdout

    def fetch_upgradable(self, letter, length_filter=False):
        output = self.run_command("apt-get -s upgrade")
        packages = []
        for line in output.splitlines():
            if line.startswith("Inst "):
                parts = line.split()
                if len(parts) > 1:
                    pkg_raw = parts[1]
                    pkg_name = pkg_raw.split(":")[0]
                    packages.append(pkg_name)
        unique_packages = sorted(list(set(packages)))

        if length_filter:
            matched = [pkg for pkg in unique_packages if pkg.lower().startswith(letter) and len(pkg) == 3]
        else:
            matched = [pkg for pkg in unique_packages if pkg.lower().startswith(letter)]
        return matched

    def handle_user_input(self, event=None):
        user_val = self.entry_input.get().strip()
        self.entry_input.delete(0, tk.END)

        if user_val.lower() == "quit":
            self.log_message("Exiting program. Goodbye!")
            self.root.after(1000, self.root.destroy)
            return

        if self.step == "GET_LETTER":
            if len(user_val) == 1 and user_val.isalpha():
                self.current_letter = user_val.lower()
                self.log_message(f"> Selected letter: '{self.current_letter.upper()}'")
                self.log_message("Choose listing mode:")
                self.log_message("  [1] All packages starting with this letter")
                self.log_message("  [2] Only packages with name length = 3")
                self.lbl_prompt.config(text="Enter choice (1 or 2):")
                self.step = "GET_FILTER_CHOICE"
            else:
                self.log_message("⚠️ Please enter a single valid alphabetical letter (A-Z).")

        elif self.step == "GET_FILTER_CHOICE":
            if user_val in ["1", "2"]:
                self.filter_choice = user_val
                length_filter = (self.filter_choice == "2")
                filter_desc = " (Name length = 3)" if length_filter else ""
                
                self.log_message(f"\n> Selected choice: {user_val}")
                
                # --- Create "Loading data..." Popup Window for 3 seconds ---
                loading_win = tk.Toplevel(self.root)
                loading_win.title("Please Wait")
                loading_win.geometry("260x120")
                loading_win.transient(self.root)
                loading_win.grab_set()  # Block interaction with main window while loading
                
                # Center popup relative to main window
                x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - 130
                y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 60
                loading_win.geometry(f"+{x}+{y}")
                
                tk.Label(loading_win, text="Loading data...", font=("Arial", 12, "bold"), fg="#333333", padx=20, pady=30).pack(expand=True)
                loading_win.update()

                # Function to execute after 3 seconds timeout
                def finish_loading():
                    # Fetch packages data
                    self.matched_packages = self.fetch_upgradable(self.current_letter, length_filter=length_filter)
                    
                    # Destroy loading popup
                    loading_win.destroy()
                    
                    # Render package results
                    self.render_packages(length_filter, filter_desc)

                # Wait 3000 milliseconds (3 seconds)
                self.root.after(3000, finish_loading)
                
            else:
                self.log_message("⚠️ Invalid choice. Please enter 1 or 2.")

        elif self.step == "GET_PACKAGE_SELECTION":
            max_selectable = min(len(self.matched_packages), 18)
            try:
                choice_num = int(user_val)
                if 1 <= choice_num <= max_selectable:
                    selected_pkg = self.matched_packages[choice_num - 1]
                    self.log_message(f"\n> Selected package for upgrade: {selected_pkg}")
                    self.log_message("Please enter your sudo password in the prompt window...")
                    
                    # Prompt for sudo password
                    sudo_pwd = getpass.getpass("Enter sudo password: ")
                    
                    self.log_message(f"[+] Upgrading {selected_pkg}...")
                    upgrade_res = subprocess.run(
                        ["sudo", "-S", "apt-get", "install", "-y", "--only-upgrade", selected_pkg],
                        input=f"{sudo_pwd}\n",
                        text=True,
                        capture_output=True
                    )

                    if upgrade_res.returncode == 0:
                        self.log_message(f"[✔] Successfully upgraded '{selected_pkg}'!")
                    else:
                        self.log_message(f"❌ Upgrade failed. Check password or logs.")

                    self.log_message("\n----------------------------------------")
                    self.log_message("Enter another letter to search (or type 'quit' to exit):")
                    self.pkg_listbox.delete(0, tk.END)
                    self.lbl_prompt.config(text="Enter Letter (A-Z):")
                    self.step = "GET_LETTER"
                else:
                    self.log_message(f"⚠️ Invalid number. Choose between 1 and {max_selectable}.")
            except ValueError:
                self.log_message("⚠️ Invalid input. Please enter a valid number.")

    def render_packages(self, length_filter, filter_desc):
        self.log_message(f"\n> Fetching upgradable packages starting with '{self.current_letter.upper()}'{filter_desc}...")
        
        # Clear right pane listbox
        self.pkg_listbox.delete(0, tk.END)

        if not self.matched_packages:
            self.log_message(f"❌ No upgradable packages found.")
            self.log_message("\nEnter another letter to search (or type 'quit' to exit):")
            self.lbl_prompt.config(text="Enter Letter (A-Z):")
            self.step = "GET_LETTER"
            return

        self.log_message(f"✔ Found {len(self.matched_packages)} packages. Displaying in right window.")

        # Display up to 18 packages in the right pane
        display_packages = self.matched_packages[:18]
        for idx, pkg in enumerate(display_packages, start=1):
            self.pkg_listbox.insert(tk.END, f"[{idx}] {pkg}")

        if len(self.matched_packages) > 18:
            self.log_message(f"⚠️ Warning: {len(self.matched_packages)} total packages found. Only the first 18 are displayed. Another run is recommended afterwards!")

        self.log_message("\nEnter the number of the package you want to upgrade from the right pane:")
        self.lbl_prompt.config(text="Enter package number to upgrade:")
        self.step = "GET_PACKAGE_SELECTION"


def main():
    root = tk.Tk()
    app = KaliUpgraderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()