from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "main.py"
PATCHED_MAIN = ROOT / "main_sound_v5.py"
SOUNDS = ROOT / "sounds"
BACKUP = ROOT / "main_before_sound_patch_v5.py"


def fail(message: str) -> None:
    print("[ERROR]", message)
    raise SystemExit(1)


def copy_sounds() -> None:
    if not SOUNDS.exists():
        fail("sounds folder was not found.")

    dst = ROOT / "sounds"
    dst.mkdir(exist_ok=True)

    # same folder, but keep this for consistency if the script is moved with sounds
    for src in SOUNDS.iterdir():
        if src.is_file():
            shutil.copy2(src, dst / src.name)

    print("[OK] sounds folder ready")


def replace_main() -> None:
    if not PATCHED_MAIN.exists():
        fail("main_sound_v5.py was not found.")
    if not MAIN.exists():
        fail("main.py was not found. Put this patch in the same folder as main.py.")

    if not BACKUP.exists():
        shutil.copy2(MAIN, BACKUP)
        print("[OK] backup created:", BACKUP.name)
    else:
        print("[OK] backup already exists:", BACKUP.name)

    shutil.copy2(PATCHED_MAIN, MAIN)
    print("[OK] main.py replaced with V5")


def main() -> None:
    copy_sounds()
    replace_main()
    print()
    print("[DONE] Sound Patch V5 applied.")
    print("Run the game with: python main.py")
    print("In game, use the SOUND button at the top-right.")


if __name__ == "__main__":
    main()
