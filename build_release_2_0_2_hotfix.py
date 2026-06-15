from __future__ import annotations

import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_NAME = "Arena_Battle_2_0_2"
ENTRY = ROOT / "main.py"

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

ASSET_EXTS = {
    ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp",
    ".wav", ".mp3", ".ogg", ".flac",
    ".ttf", ".otf",
    ".json", ".txt", ".csv",
}

CHARACTER_IMAGE_FILES = [
    "minjae.jpg",
    "jaemin.jpg",
    "sungmin.jpg",
    "jungwoo.png",
    "suin.jpg",
    "sunghyun.png",
    "gski.png",
    "gunwoo.jpg",
]

def fail(message: str) -> None:
    print("[ERROR]", message)
    raise SystemExit(1)

def ensure_main() -> None:
    if ENTRY.exists():
        return
    release_main = ROOT / "main_release_2_0_2.py"
    if release_main.exists():
        shutil.copy2(release_main, ENTRY)
        print("[OK] main.py created from main_release_2_0_2.py")
        return
    fail("main.py was not found.")

def clean_previous_build() -> None:
    for name in ["build", "dist", "release"]:
        path = ROOT / name
        if path.exists():
            shutil.rmtree(path)
    spec = ROOT / f"{APP_NAME}.spec"
    if spec.exists():
        spec.unlink()

def create_runtime_hook() -> Path:
    hook = ROOT / "_arena_runtime_hook_2_0_2.py"
    hook.write_text(
        """
import os
import sys

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    os.chdir(sys._MEIPASS)
""".strip() + "\n",
        encoding="utf-8",
    )
    return hook

def collect_add_data_args() -> list[str]:
    args: list[str] = []
    added_sources = set()

    for folder in ASSET_DIRS:
        src = ROOT / folder
        if src.exists() and src.is_dir():
            args.extend(["--add-data", f"{src}{os.pathsep}{folder}"])
            added_sources.add(str(src.resolve()))

    for file in ROOT.iterdir():
        if file.is_file() and file.suffix.lower() in ASSET_EXTS:
            args.extend(["--add-data", f"{file}{os.pathsep}."])
            added_sources.add(str(file.resolve()))

    missing_images = []
    for name in CHARACTER_IMAGE_FILES:
        file = ROOT / name
        if file.exists() and file.is_file():
            if str(file.resolve()) not in added_sources:
                args.extend(["--add-data", f"{file}{os.pathsep}."])
                added_sources.add(str(file.resolve()))
        else:
            missing_images.append(name)

    if missing_images:
        print()
        print("[WARNING] Some character images are missing from this build folder:")
        for name in missing_images:
            print(" -", name)
        print("[WARNING] Put the image files next to main.py before building if you want them in the exe.")
        print()

    return args

def build() -> None:
    ensure_main()
    clean_previous_build()

    hook = create_runtime_hook()

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
        *collect_add_data_args(),
        str(ENTRY),
    ]

    print("[1/3] Building exe with PyInstaller...")
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
        """Arena Battle 2.0.2 실행 방법

1. 압축을 풉니다.
2. Arena_Battle_2_0_2.exe를 더블클릭합니다.
3. Windows 보안 경고가 뜨면 '추가 정보' -> '실행'을 누릅니다.

2.0.2 Hotfix:
- 2.0.1에서 resource_path 순서 오류로 exe가 실행되지 않던 문제를 수정했습니다.
- 배포 exe에서 캐릭터 사진이 사라지던 문제 수정도 유지했습니다.

조작:
- 게임 종료 화면에서 R: 같은 캐릭터로 즉시 재시작
- 게임 종료 화면에서 M: 메인화면으로 돌아가기
- Q 또는 ESC: 종료
""",
        encoding="utf-8",
    )

    shutil.copy2(exe, release / exe.name)

    zip_path = release / "Arena_Battle_release_2.0.2_for_friends.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(release / exe.name, exe.name)
        zf.write(readme, readme.name)

    print()
    print("[SUCCESS] Release build complete!")
    print("[SUCCESS] Send this file to friends:")
    print(" ", zip_path)

if __name__ == "__main__":
    build()
