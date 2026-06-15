#!/usr/bin/env python3
"""
Arena_Battle sound patcher V3

사용법:
1) 이 파일과 sounds 폴더를 Arena_Battle 프로젝트 폴더(main.py 있는 곳)에 넣기
2) 터미널에서 실행:
   python apply_sound_patch_v3.py
   또는
   py apply_sound_patch_v3.py
3) 생성/수정된 main.py 실행:
   python main.py

이미 예전 사운드 패치를 적용한 상태라면 BGM/효과음 볼륨만 V3 기준으로 낮춰줍니다.
기존 main.py는 처음 적용할 때 main_before_sound.py 로 백업됩니다.
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

SOUND_VOLUMES = {
    "hit": 0.34,
    "dodge": 0.24,
    "laser": 0.30,
    "slash": 0.30,
    "moon_slash": 0.36,
    "explosion": 0.42,
    "geonwoo_boom": 0.52,
    "heal": 0.30,
    "button": 0.22,
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
            sound = pygame.mixer.Sound(path)
            sound.set_volume(SOUND_VOLUMES.get(key, 0.30))
            SOUNDS[key] = sound
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


def tune_existing_sound_patch(text):
    # 예전 패치가 이미 들어간 경우, 코드 구조는 건드리지 않고 볼륨만 낮춘다.
    text = re.sub(r'pygame\.mixer\.music\.set_volume\([0-9.]+\)', 'pygame.mixer.music.set_volume(0.18)', text)
    replacements = {
        'play_sound("dodge", 0.45)': 'play_sound("dodge", 0.24)',
        'play_sound("hit", 0.55)': 'play_sound("hit", 0.34)',
        'play_sound("geonwoo_boom", 0.9)': 'play_sound("geonwoo_boom", 0.52)',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # SOUND_VOLUMES가 없는 구버전 사운드 블록이면 기본 볼륨 딕셔너리를 추가한다.
    if 'SOUND_VOLUMES = {' not in text and 'SOUND_FILES = {' in text:
        text = text.replace(
            'SOUND_FILES = {\n    "hit": "hit.wav",\n    "dodge": "dodge.wav",\n    "laser": "laser.wav",\n    "slash": "slash.wav",\n    "moon_slash": "moon_slash.wav",\n    "explosion": "explosion.wav",\n    "geonwoo_boom": "geonwoo_boom.wav",\n    "heal": "heal.wav",\n    "button": "button.wav",\n}\n',
            'SOUND_FILES = {\n    "hit": "hit.wav",\n    "dodge": "dodge.wav",\n    "laser": "laser.wav",\n    "slash": "slash.wav",\n    "moon_slash": "moon_slash.wav",\n    "explosion": "explosion.wav",\n    "geonwoo_boom": "geonwoo_boom.wav",\n    "heal": "heal.wav",\n    "button": "button.wav",\n}\n\nSOUND_VOLUMES = {\n    "hit": 0.34,\n    "dodge": 0.24,\n    "laser": 0.30,\n    "slash": 0.30,\n    "moon_slash": 0.36,\n    "explosion": 0.42,\n    "geonwoo_boom": 0.52,\n    "heal": 0.30,\n    "button": 0.22,\n}\n'
        )
        text = text.replace(
            'SOUNDS[key] = pygame.mixer.Sound(path)',
            'sound = pygame.mixer.Sound(path)\n            sound.set_volume(SOUND_VOLUMES.get(key, 0.30))\n            SOUNDS[key] = sound'
        )
    return text


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
        fail("현재 폴더에 main.py가 없습니다. apply_sound_patch_v3.py를 main.py와 같은 폴더로 옮겨주세요.")

    text = MAIN_FILE.read_text(encoding="utf-8")

    if PATCH_MARK in text:
        text = tune_existing_sound_patch(text)
        MAIN_FILE.write_text(text, encoding="utf-8", newline="\n")
        print("완료: 이미 적용된 사운드 패치를 V3 볼륨 기준으로 조정했습니다.")
        print("sounds 폴더도 V3 버전으로 교체해 주세요.")
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
        "add_screen_shake(1.8)\n  play_sound(\"dodge\")\n\n  return 0",
        1,
    )
    text = text.replace(
        "create_hit_particles(self.x, self.y, current_time)\n\n  add_screen_shake(3.5)",
        "create_hit_particles(self.x, self.y, current_time)\n  play_sound(\"hit\")\n\n  add_screen_shake(3.5)",
        1,
    )

    text, _ = patch_class_fire_sound(text, "BlueLaser", "laser")
    text, _ = patch_class_fire_sound(text, "SwordSlash", "slash")
    text, _ = patch_simple_phase_sound(text, "MoonSlash", "moon_slash")
    text, _ = patch_simple_phase_sound(text, "GlobalAura", "explosion")

    text = re.sub(
        r'(?m)^(?P<indent>[ \t]+)([^\n]*\.geonwoo_execute_done\s*=\s*True[ \t]*)$',
        r'\g<indent>\2\n\g<indent>play_sound("geonwoo_boom")',
        text,
        count=1,
    )

    MAIN_FILE.write_text(text, encoding="utf-8", newline="\n")
    print("완료: main.py에 V3 사운드 기능을 추가했습니다.")
    print("사운드 파일 위치: sounds/ 폴더")
    print("원본 백업: main_before_sound.py")


if __name__ == "__main__":
    main()
