import importlib.metadata
import pkgutil


def main():
  print("=" * 60)
  print(" SEARCHING FOR PYTHON LIBRARIES STARTING WITH 'Z'")
  print("=" * 60)

  # 1. Check third-party packages installed via pip
  print(
      "\n[1] Third-Party Packages (Installed via pip) starting with 'z':"
      "\n"
      + "-" * 60
  )
  try:
    installed_dists = [d.metadata["Name"] for d in importlib.metadata.distributions()]
    z_packages = sorted([p for p in installed_dists if p.lower().startswith("z")])

    if z_packages:
      for pkg in z_packages:
        try:
          version = importlib.metadata.version(pkg)
          print(f"  • {pkg} (Version: {version})")
        except Exception:
          print(f"  • {pkg}")
    else:
      print("  No third-party pip packages starting with 'z' found.")
  except Exception as e:
    print(f"  Could not retrieve pip packages: {e}")

  # 2. Check all importable modules (Standard library + site-packages)
  print(
      "\n[2] All Importable Modules & Libraries starting with 'z':"
      "\n"
      + "-" * 60
  )
  z_modules = sorted(
      set(name for _, name, _ in pkgutil.iter_modules() if name.lower().startswith("z"))
  )

  if z_modules:
    for mod in z_modules:
      print(f"  • {mod}")
    print(f"\nTotal importable modules found: {len(z_modules)}")
  else:
    print("  No importable modules starting with 'z' found.")

  print("=" * 60)


if __name__ == "__main__":
  main()