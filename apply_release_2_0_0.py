from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT
MAIN_SRC = ROOT / "main_release_2_0_0.py"
MAIN_DST = PROJECT / "main.py"
SOUNDS_SRC = ROOT / "sounds"
SOUNDS_DST = PROJECT / "sounds"

def main():
    if not MAIN_SRC.exists():
        print("[ERROR] main_release_2_0_0.py not found.")
        raise SystemExit(1)

    if MAIN_DST.exists():
        backup = PROJECT / "main_before_release_2_0_0.py"
        if not backup.exists():
            shutil.copy2(MAIN_DST, backup)
            print("[OK] Backup created:", backup.name)

    shutil.copy2(MAIN_SRC, MAIN_DST)
    print("[OK] main.py updated to release 2.0.0 version.")

    if SOUNDS_SRC.exists():
        SOUNDS_DST.mkdir(exist_ok=True)
        for src in SOUNDS_SRC.iterdir():
            if src.is_file():
                shutil.copy2(src, SOUNDS_DST / src.name)
        print("[OK] sounds folder updated.")

    print()
    print("[DONE] Release 2.0.0 applied.")
    print("Run with: python main.py")

if __name__ == "__main__":
    main()
