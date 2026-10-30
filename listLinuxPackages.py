import subprocess


def get_packages_starting_with(letter):
  letter = letter.lower()
  print(
      f"\n[Installed Linux Packages starting with '{letter.upper()}']:"
      "\n"
      + "-" * 60
  )

  try:
    # Use dpkg-query to fetch all installed package names cleanly
    result = subprocess.run(
        ["dpkg-query", "-f", "${Package}\n", "-W"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )

    # Split the output into a list of package names
    all_packages = result.stdout.splitlines()
    matched_packages = sorted(
        [pkg for pkg in all_packages if pkg.lower().startswith(letter)]
    )

    if matched_packages:
      for pkg in matched_packages:
        print(f"  • {pkg}")
      print(f"\nTotal packages found: {len(matched_packages)}")
    else:
      print(
          f"  No installed Linux packages starting with '{letter.upper()}'"
          " found."
      )

  except FileNotFoundError:
    print(
        "❌ Error: 'dpkg-query' was not found. This script requires a"
        " Debian/Ubuntu-based Linux system (or WSL)."
    )
  except subprocess.CalledProcessError as e:
    print(f"❌ Error querying system packages: {e}")


def main():
  print("=" * 60)
  print(" LINUX SYSTEM PACKAGE EXPLORER BY LETTER (APT/DPKG)")
  print("=" * 60)

  # Step 1: Automatically display packages starting with 'z'
  print("\n>>> Step 1: Listing Linux packages starting with 'Z'")
  get_packages_starting_with("z")

  print("\n" + "=" * 60)

  # Step 2: Ask the user for another letter and display its packages
  while True:
    user_input = input(
        "\nEnter a letter of the alphabet to list its Linux packages (or type"
        " 'quit' to exit): "
    ).strip()

    if user_input.lower() == "quit":
      print("Exiting program. Goodbye!")
      break

    if len(user_input) == 1 and user_input.isalpha():
      print(
          f"\n>>> Step 2: Listing Linux packages starting with"
          f" '{user_input.upper()}'"
      )
      get_packages_starting_with(user_input)
      print("\n" + "=" * 60)
    else:
      print("⚠️ Please enter a single valid alphabetical letter (A-Z).")


if __name__ == "__main__":
  main()