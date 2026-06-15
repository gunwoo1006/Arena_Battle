from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "main.py"
NEW_MAIN = ROOT / "main_gameplay_v6.py"
BACKUP = ROOT / "main_before_gameplay_patch_v6.py"

if not MAIN.exists():
    print("[ERROR] main.py was not found. Put these files in the same folder as main.py.")
    raise SystemExit(1)

if not NEW_MAIN.exists():
    print("[ERROR] main_gameplay_v6.py was not found.")
    raise SystemExit(1)

if not BACKUP.exists():
    shutil.copy2(MAIN, BACKUP)
    print("[OK] Backup created:", BACKUP.name)
else:
    print("[OK] Backup already exists:", BACKUP.name)

shutil.copy2(NEW_MAIN, MAIN)
print("[DONE] Gameplay Patch V6 applied.")
print("Run the game with: python main.py")
