import importlib.metadata
import pkgutil


def get_libraries_starting_with(letter):
  letter = letter.lower()

  # 1. Check third-party packages installed via pip
  print(
      f"\n[1] Third-Party Packages (Installed via pip) starting with '{letter.upper()}':"
      "\n"
      + "-" * 60
  )
  try:
    installed_dists = [
        d.metadata["Name"] for d in importlib.metadata.distributions()
    ]
    matched_packages = sorted(
        [p for p in installed_dists if p.lower().startswith(letter)]
    )

    if matched_packages:
      for pkg in matched_packages:
        try:
          version = importlib.metadata.version(pkg)
          print(f"  • {pkg} (Version: {version})")
        except Exception:
          print(f"  • {pkg}")
    else:
      print(
          f"  No third-party pip packages starting with '{letter.upper()}'"
          " found."
      )
  except Exception as e:
    print(f"  Could not retrieve pip packages: {e}")

  # 2. Check all importable modules (Standard library + site-packages)
  print(
      f"\n[2] All Importable Modules & Libraries starting with"
      f" '{letter.upper()}':\n" + "-" * 60
  )
  matched_modules = sorted(
      set(
          name
          for _, name, _ in pkgutil.iter_modules()
          if name.lower().startswith(letter)
      )
  )

  if matched_modules:
    for mod in matched_modules:
      print(f"  • {mod}")
    print(f"\nTotal importable modules found: {len(matched_modules)}")
  else:
    print(
        f"  No importable modules starting with '{letter.upper()}' found."
    )


def main():
  print("=" * 60)
  print(" PYTHON LIBRARY EXPLORER BY LETTER")
  print("=" * 60)

  # Step 1: Automatically display libraries starting with 'z'
  print("\n>>> Step 1: Listing libraries starting with 'Z'")
  get_libraries_starting_with("z")

  print("\n" + "=" * 60)

  # Step 2: Ask the user for another letter and display its libraries
  while True:
    user_input = input(
        "\nEnter a letter of the alphabet to list its libraries (or type 'quit'"
        " to exit): "
    ).strip()

    if user_input.lower() == "quit":
      print("Exiting program. Goodbye!")
      break

    if len(user_input) == 1 and user_input.isalpha():
      print(f"\n>>> Step 2: Listing libraries starting with '{user_input.upper()}'")
      get_libraries_starting_with(user_input)
      print("\n" + "=" * 60)
    else:
      print("⚠️ Please enter a single valid alphabetical letter (A-Z).")


if __name__ == "__main__":
  main()