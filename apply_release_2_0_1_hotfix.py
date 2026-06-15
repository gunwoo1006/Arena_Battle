from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT
MAIN_SRC = ROOT / "main_release_2_0_1.py"
MAIN_DST = PROJECT / "main.py"
SOUNDS_SRC = ROOT / "sounds"
SOUNDS_DST = PROJECT / "sounds"

IMAGE_FILES = [
    "minjae.jpg",
    "jaemin.jpg",
    "sungmin.jpg",
    "jungwoo.png",
    "suin.jpg",
    "sunghyun.png",
    "gski.png",
    "gunwoo.jpg",
]

def main():
    if not MAIN_SRC.exists():
        print("[ERROR] main_release_2_0_1.py not found.")
        raise SystemExit(1)

    if MAIN_DST.exists():
        backup = PROJECT / "main_before_release_2_0_1.py"
        if not backup.exists():
            shutil.copy2(MAIN_DST, backup)
            print("[OK] Backup created:", backup.name)

    shutil.copy2(MAIN_SRC, MAIN_DST)
    print("[OK] main.py updated to release 2.0.1 hotfix version.")

    if SOUNDS_SRC.exists():
        SOUNDS_DST.mkdir(exist_ok=True)
        for src in SOUNDS_SRC.iterdir():
            if src.is_file():
                shutil.copy2(src, SOUNDS_DST / src.name)
        print("[OK] sounds folder updated.")

    missing = [name for name in IMAGE_FILES if not (PROJECT / name).exists()]
    if missing:
        print()
        print("[WARNING] These image files are not in this folder:")
        for name in missing:
            print(" -", name)
        print("If your local game folder has them, put this hotfix folder content in that same folder before building.")
    else:
        print("[OK] Character image files found.")

    print()
    print("[DONE] Release 2.0.1 hotfix applied.")
    print("Run with: python main.py")

if __name__ == "__main__":
    main()
