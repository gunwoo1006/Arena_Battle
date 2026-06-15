#!/usr/bin/env python3
"""
Arena_Battle sound patcher

사용법:
1) 이 파일과 sounds 폴더를 Arena_Battle 프로젝트 폴더(main.py 있는 곳)에 넣기
2) 터미널에서 실행:
   python apply_sound_patch.py
   또는
   py apply_sound_patch.py
3) 생성/수정된 main.py 실행:
   python main.py

실행하면 기존 main.py는 main_before_sound.py 로 백업됩니다.
"""

from pathlib import Path
import re
import shutil

MAIN_FILE = Path("main.py")
BACKUP_FILE = Path("main_before_sound.py")
PATCH_MARK = "# === SOUND PATCH START ==="

SOUND_BLOCK = """
# === SOUND PATCH START ===
# 사운드 파일은 main.py와 같은 위치의 sounds 폴더에 넣으면 됩니다.
# 파일이 없어도 게임은 멈추지 않고 조용히 실행됩니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(BASE_DIR, "sounds")
SOUND_ENABLED = True
SOUNDS = {}

SOUND_FILES = {
    "hit": "hit.wav",
    "dodge": "dodge.wav",
    "laser": "laser.wav",
    "slash": "slash.wav",
    "moon_slash": "moon_slash.wav",
    "explosion": "explosion.wav",
    "geonwoo_boom": "geonwoo_boom.wav",
    "heal": "heal.wav",
    "button": "button.wav",
}


def load_game_sounds():
    global SOUND_ENABLED, SOUNDS
    if not SOUND_ENABLED:
        return
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
    except pygame.error:
        SOUND_ENABLED = False
        return

    for key, filename in SOUND_FILES.items():
        path = os.path.join(SOUND_DIR, filename)
        if not os.path.exists(path):
            SOUNDS[key] = None
            continue
        try:
            SOUNDS[key] = pygame.mixer.Sound(path)
        except pygame.error:
            SOUNDS[key] = None


def play_sound(name, volume=None):
    if not SOUND_ENABLED:
        return
    sound = SOUNDS.get(name)
    if sound is None:
        return
    if volume is not None:
        sound.set_volume(volume)
    try:
        sound.play()
    except pygame.error:
        pass


def start_bgm():
    if not SOUND_ENABLED:
        return
    bgm_path = os.path.join(SOUND_DIR, "bgm.wav")
    if not os.path.exists(bgm_path):
        return
    try:
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.set_volume(0.18)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass


def stop_bgm():
    if SOUND_ENABLED:
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass

load_game_sounds()
start_bgm()
# === SOUND PATCH END ===
"""


def fail(message):
    print("[실패]", message)
    raise SystemExit(1)


def insert_after_first(text, marker, insert_text):
    idx = text.find(marker)
    if idx == -1:
        return text, False
    idx += len(marker)
    return text[:idx] + insert_text + text[idx:], True


def patch_class_fire_sound(text, class_name, sound_name):
    start = text.find(f"class {class_name}:")
    if start == -1:
        return text, False
    next_class = text.find("\nclass ", start + 1)
    if next_class == -1:
        next_class = len(text)
    before, segment, after = text[:start], text[start:next_class], text[next_class:]

    pattern = re.compile(
        r'(?P<indent>^[ \t]+)self\.phase = "fire"(?P<trail>[ \t]*\n)(?P<blank>[ \t]*\n)?(?P=indent)if not self\.locked:',
        re.MULTILINE,
    )

    def repl(m):
        indent = m.group('indent')
        trail = m.group('trail')
        blank = m.group('blank') or ''
        return (
            f'{indent}self.phase = "fire"{trail}'
            f'{blank}'
            f'{indent}if not self.announced:\n'
            f'{indent}    play_sound("{sound_name}")\n'
            f'{indent}    self.announced = True\n'
            f'{blank}'
            f'{indent}if not self.locked:'
        )

    new_segment, count = pattern.subn(repl, segment, count=1)
    return before + new_segment + after, count > 0


def patch_simple_phase_sound(text, class_name, sound_name):
    start = text.find(f"class {class_name}:")
    if start == -1:
        return text, False
    next_class = text.find("\nclass ", start + 1)
    if next_class == -1:
        next_class = len(text)
    before, segment, after = text[:start], text[start:next_class], text[next_class:]

    if "self.announced = False" not in segment:
        segment = re.sub(
            r'(?m)^(?P<indent>[ \t]+)self\.phase = "warning"[ \t]*$',
            r'\g<indent>self.phase = "warning"\n\g<indent>self.announced = False',
            segment,
            count=1,
        )
        segment = re.sub(
            r'(?m)^(?P<indent>[ \t]+)self\.phase = "charge"[ \t]*$',
            r'\g<indent>self.phase = "charge"\n\g<indent>self.announced = False',
            segment,
            count=1,
        )

    pattern = re.compile(r'(?m)^(?P<indent>[ \t]+)self\.phase = "fire"[ \t]*$')
    done = False

    def repl(m):
        nonlocal done
        if done:
            return m.group(0)
        done = True
        indent = m.group('indent')
        return (
            f'{indent}self.phase = "fire"\n'
            f'{indent}if not self.announced:\n'
            f'{indent}    play_sound("{sound_name}")\n'
            f'{indent}    self.announced = True'
        )

    new_segment = pattern.sub(repl, segment, count=1)
    return before + new_segment + after, done


def main():
    if not MAIN_FILE.exists():
        fail("현재 폴더에 main.py가 없습니다. apply_sound_patch.py를 main.py와 같은 폴더로 옮겨주세요.")

    text = MAIN_FILE.read_text(encoding="utf-8")
    if PATCH_MARK in text:
        print("이미 사운드 패치가 적용되어 있습니다.")
        return

    if not BACKUP_FILE.exists():
        shutil.copy2(MAIN_FILE, BACKUP_FILE)
        print("백업 생성: main_before_sound.py")

    if "pygame.mixer.pre_init" not in text:
        text, changed = re.subn(
            r'(?m)^pygame\.init\(\)[ \t]*$',
            'pygame.mixer.pre_init(44100, -16, 2, 512)\npygame.init()',
            text,
            count=1,
        )
        if not changed:
            fail("pygame.init() 위치를 찾지 못했습니다.")

    text, ok = insert_after_first(text, "pygame.init()\n", SOUND_BLOCK)
    if not ok:
        fail("pygame.init() 뒤에 사운드 코드를 삽입하지 못했습니다.")

    text = text.replace(
        "add_screen_shake(1.8)\n\n  return 0",
        "add_screen_shake(1.8)\n  play_sound(\"dodge\", 0.45)\n\n  return 0",
        1,
    )
    text = text.replace(
        "create_hit_particles(self.x, self.y, current_time)\n\n  add_screen_shake(3.5)",
        "create_hit_particles(self.x, self.y, current_time)\n  play_sound(\"hit\", 0.55)\n\n  add_screen_shake(3.5)",
        1,
    )

    text, _ = patch_class_fire_sound(text, "BlueLaser", "laser")
    text, _ = patch_class_fire_sound(text, "SwordSlash", "slash")
    text, _ = patch_simple_phase_sound(text, "MoonSlash", "moon_slash")
    text, _ = patch_simple_phase_sound(text, "GlobalAura", "explosion")

    text = re.sub(
        r'(?m)^(?P<indent>[ \t]+)([^\n]*\.geonwoo_execute_done\s*=\s*True[ \t]*)$',
        r'\g<indent>\2\n\g<indent>play_sound("geonwoo_boom", 0.9)',
        text,
        count=1,
    )

    MAIN_FILE.write_text(text, encoding="utf-8", newline="\n")
    print("완료: main.py에 사운드 기능을 추가했습니다.")
    print("사운드 파일 위치: sounds/ 폴더")
    print("원본 백업: main_before_sound.py")


if __name__ == "__main__":
    main()
