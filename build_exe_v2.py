from __future__ import annotations

import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "main.py"
APP_NAME = "Arena_Battle"

# Folders commonly used by pygame projects.
ASSET_DIRS = [
    "sounds",
    "sound",
    "assets",
    "asset",
    "images",
    "image",
    "imgs",
    "sprites",
    "sprite",
    "fonts",
    "font",
    "data",
    "resources",
    "resource",
]

# Root-level files that may be loaded by the game.
ASSET_EXTS = {
    ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp",
    ".wav", ".mp3", ".ogg", ".flac",
    ".ttf", ".otf",
    ".json", ".txt", ".csv",
}


def fail(message: str) -> None:
    print(f"[ERROR] {message}")
    raise SystemExit(1)


def clean_previous_build() -> None:
    for name in ["build", "dist", "release"]:
        path = ROOT / name
        if path.exists():
            shutil.rmtree(path)

    spec = ROOT / f"{APP_NAME}.spec"
    if spec.exists():
        spec.unlink()


def create_runtime_hook() -> Path:
    hook = ROOT / "_arena_runtime_hook.py"
    hook.write_text(
        """
import os
import sys

# PyInstaller extracts bundled data to sys._MEIPASS.
# Moving the working directory there lets existing relative paths like
# sounds/bgm.wav or images/player.png keep working without editing main.py.
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    os.chdir(sys._MEIPASS)
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return hook


def collect_add_data_args() -> list[str]:
    args: list[str] = []

    # Add asset folders.
    for folder in ASSET_DIRS:
        src = ROOT / folder
        if src.exists() and src.is_dir():
            args.extend(["--add-data", f"{src}{os.pathsep}{folder}"])

    # Add root-level asset files.
    for file in ROOT.iterdir():
        if file.is_file() and file.suffix.lower() in ASSET_EXTS:
            args.extend(["--add-data", f"{file}{os.pathsep}."])

    return args


def build_exe() -> None:
    if not MAIN.exists():
        fail("main.py was not found. Put this script in the same folder as main.py.")

    clean_previous_build()
    hook = create_runtime_hook()
    add_data_args = collect_add_data_args()

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        APP_NAME,
        "--runtime-hook",
        str(hook),
        *add_data_args,
        str(MAIN),
    ]

    print("[INFO] Running PyInstaller...")
    print("[INFO] This can take a few minutes.")
    result = subprocess.run(command, cwd=ROOT)

    try:
        hook.unlink()
    except FileNotFoundError:
        pass

    if result.returncode != 0:
        fail("PyInstaller failed.")

    exe = ROOT / "dist" / f"{APP_NAME}.exe"
    if not exe.exists():
        fail("EXE was not created.")

    release = ROOT / "release"
    release.mkdir(exist_ok=True)

    readme = release / "README_FOR_FRIENDS.txt"
    readme.write_text(
        """Arena Battle 실행 방법

1. 압축을 푼다.
2. Arena_Battle.exe를 더블클릭한다.
3. Windows 보안 경고가 뜨면 '추가 정보' -> '실행'을 누른다.

주의:
- exe 파일만 빼서 옮겨도 되지만, 압축 파일 그대로 보내는 것을 추천합니다.
- 실행이 안 되면 Windows 보안 프로그램이 막았을 가능성이 있습니다.
""",
        encoding="utf-8",
    )

    shutil.copy2(exe, release / exe.name)

    zip_path = release / "Arena_Battle_for_friends.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(release / exe.name, exe.name)
        zf.write(readme, readme.name)

    print()
    print("[SUCCESS] Build complete!")
    print(f"[SUCCESS] Friend ZIP: {zip_path}")


if __name__ == "__main__":
    build_exe()
