import pygame
import random
import math
import os
import sys

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# === SOUND PATCH V5 START ===
# V5: V3 고전 격투게임 BGM 복구 + 캐릭터별 스킬 효과음 + 우측 상단 사운드 옵션.
# 사운드 파일이 없어도 게임은 멈추지 않고 조용히 실행됩니다.
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = resource_path("sounds")

def resource_path(relative_path):
    """Return a usable path for local run and PyInstaller exe run."""
    if relative_path is None:
        return None

    # Already absolute path.
    if os.path.isabs(relative_path):
        return relative_path

    # PyInstaller --onefile extracts bundled files to sys._MEIPASS.
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        bundled_path = os.path.join(bundle_dir, relative_path)
        if os.path.exists(bundled_path):
            return bundled_path

    return os.path.join(BASE_DIR, relative_path)

SOUND_SETTINGS_FILE = os.path.join(BASE_DIR, "arena_sound_settings.json")

SOUND_ENABLED = True
SFX_ENABLED = True
BGM_ENABLED = True
SFX_VOLUME = 0.78
BGM_VOLUME = 0.18
SOUND_PANEL_OPEN = False
SOUNDS = {}

SOUND_FILES = {
    "hit": "hit.wav",
    "body_hit": "body_hit.wav",
    "dodge": "dodge.wav",
    "button": "button.wav",

    "laser": "laser.wav",
    "trickster": "trickster.wav",
    "land": "land.wav",

    "aura": "aura.wav",
    "jaemin_awaken": "jaemin_awaken.wav",
    "jaemin_global": "jaemin_global.wav",
    "explosion": "explosion.wav",

    "slash": "slash.wav",
    "moon_slash": "moon_slash.wav",

    "cow_moo": "cow_moo.wav",
    "cow_herd": "cow_herd.wav",

    "suin_grasp": "suin_grasp.wav",
    "suin_demon": "suin_demon.wav",
    "suin_burst": "suin_burst.wav",

    "gunshot": "gunshot.wav",
    "heal": "heal.wav",
    "item": "item.wav",

    "stew_throw": "stew_throw.wav",
    "stew_land": "stew_land.wav",
    "stew_ult": "stew_ult.wav",

    "geonwoo_charge": "geonwoo_charge.wav",
    "geonwoo_boom": "geonwoo_boom.wav",
}

SOUND_VOLUMES = {
    "hit": 0.30,
    "body_hit": 0.22,
    "dodge": 0.22,
    "button": 0.20,

    "laser": 0.30,
    "trickster": 0.28,
    "land": 0.34,

    "aura": 0.16,
    "jaemin_awaken": 0.40,
    "jaemin_global": 0.40,
    "explosion": 0.34,

    "slash": 0.28,
    "moon_slash": 0.46,

    "cow_moo": 0.42,
    "cow_herd": 0.44,

    "suin_grasp": 0.30,
    "suin_demon": 0.38,
    "suin_burst": 0.42,

    "gunshot": 0.26,
    "heal": 0.28,
    "item": 0.24,

    "stew_throw": 0.23,
    "stew_land": 0.34,
    "stew_ult": 0.38,

    "geonwoo_charge": 0.42,
    "geonwoo_boom": 0.62,
}


def clamp_sound_value(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def load_sound_settings():
    global BGM_ENABLED, SFX_ENABLED, BGM_VOLUME, SFX_VOLUME

    try:
        if not os.path.exists(SOUND_SETTINGS_FILE):
            return

        with open(SOUND_SETTINGS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        BGM_ENABLED = bool(data.get("bgm_enabled", BGM_ENABLED))
        SFX_ENABLED = bool(data.get("sfx_enabled", SFX_ENABLED))
        BGM_VOLUME = clamp_sound_value(float(data.get("bgm_volume", BGM_VOLUME)))
        SFX_VOLUME = clamp_sound_value(float(data.get("sfx_volume", SFX_VOLUME)))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        pass


def save_sound_settings():
    data = {
        "bgm_enabled": BGM_ENABLED,
        "sfx_enabled": SFX_ENABLED,
        "bgm_volume": BGM_VOLUME,
        "sfx_volume": SFX_VOLUME,
    }

    try:
        with open(SOUND_SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError:
        pass


def load_game_sounds():
    global SOUND_ENABLED, SOUNDS

    load_sound_settings()

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
            sound.set_volume(SOUND_VOLUMES.get(key, 0.30) * SFX_VOLUME)
            SOUNDS[key] = sound
        except pygame.error:
            SOUNDS[key] = None


def play_sound(name, volume=None):
    if not SOUND_ENABLED or not SFX_ENABLED:
        return

    sound = SOUNDS.get(name)

    if sound is None:
        return

    base_volume = SOUND_VOLUMES.get(name, 0.30) if volume is None else volume
    final_volume = clamp_sound_value(base_volume * SFX_VOLUME)

    try:
        sound.set_volume(final_volume)
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
        pygame.mixer.music.set_volume(BGM_VOLUME if BGM_ENABLED else 0.0)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass


def apply_bgm_volume():
    if not SOUND_ENABLED:
        return

    try:
        pygame.mixer.music.set_volume(BGM_VOLUME if BGM_ENABLED else 0.0)
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
# === SOUND PATCH V5 END ===

WIDTH, HEIGHT = 1050, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arena Battle")

clock = pygame.time.Clock()

font = pygame.font.SysFont("malgungothic", 38)
small_font = pygame.font.SysFont("malgungothic", 23)
tiny_font = pygame.font.SysFont("malgungothic", 18)
mini_font = pygame.font.SysFont("malgungothic", 15)


# === SOUND OPTIONS UI V5 START ===
def get_sound_option_rects():
    return {
        "button": pygame.Rect(WIDTH - 152, 12, 136, 34),
        "panel": pygame.Rect(WIDTH - 292, 52, 276, 166),
        "bgm_toggle": pygame.Rect(WIDTH - 274, 96, 58, 28),
        "bgm_minus": pygame.Rect(WIDTH - 202, 96, 34, 28),
        "bgm_plus": pygame.Rect(WIDTH - 162, 96, 34, 28),
        "sfx_toggle": pygame.Rect(WIDTH - 274, 146, 58, 28),
        "sfx_minus": pygame.Rect(WIDTH - 202, 146, 34, 28),
        "sfx_plus": pygame.Rect(WIDTH - 162, 146, 34, 28),
    }


def draw_sound_option_button(rect, text, font_obj, bg_color, text_color=(245, 245, 245)):
    pygame.draw.rect(screen, bg_color, rect, border_radius=8)
    pygame.draw.rect(screen, (225, 225, 235), rect, 1, border_radius=8)

    image = font_obj.render(text, True, text_color)
    screen.blit(image, image.get_rect(center=rect.center))


def handle_sound_options_event(event):
    global SOUND_PANEL_OPEN, BGM_ENABLED, SFX_ENABLED, BGM_VOLUME, SFX_VOLUME

    if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
        return False

    rects = get_sound_option_rects()

    if rects["button"].collidepoint(event.pos):
        SOUND_PANEL_OPEN = not SOUND_PANEL_OPEN
        play_sound("button", 0.22)
        return True

    if not SOUND_PANEL_OPEN:
        return False

    if not rects["panel"].collidepoint(event.pos):
        return False

    changed = False

    if rects["bgm_toggle"].collidepoint(event.pos):
        BGM_ENABLED = not BGM_ENABLED
        changed = True
    elif rects["sfx_toggle"].collidepoint(event.pos):
        SFX_ENABLED = not SFX_ENABLED
        changed = True
    elif rects["bgm_minus"].collidepoint(event.pos):
        BGM_VOLUME = clamp_sound_value(round(BGM_VOLUME - 0.05, 2))
        changed = True
    elif rects["bgm_plus"].collidepoint(event.pos):
        BGM_VOLUME = clamp_sound_value(round(BGM_VOLUME + 0.05, 2))
        BGM_ENABLED = True
        changed = True
    elif rects["sfx_minus"].collidepoint(event.pos):
        SFX_VOLUME = clamp_sound_value(round(SFX_VOLUME - 0.05, 2))
        changed = True
    elif rects["sfx_plus"].collidepoint(event.pos):
        SFX_VOLUME = clamp_sound_value(round(SFX_VOLUME + 0.05, 2))
        SFX_ENABLED = True
        changed = True

    if changed:
        apply_bgm_volume()
        save_sound_settings()
        play_sound("button", 0.16)
        return True

    return True


def draw_sound_options_ui():
    rects = get_sound_option_rects()

    draw_sound_option_button(
        rects["button"],
        "SOUND",
        mini_font,
        (56, 56, 66) if SOUND_PANEL_OPEN else (42, 42, 50),
        (255, 230, 90) if SOUND_PANEL_OPEN else (235, 235, 235),
    )

    if not SOUND_PANEL_OPEN:
        return

    panel = rects["panel"]
    panel_surface = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
    panel_surface.fill((22, 22, 30, 232))
    screen.blit(panel_surface, panel.topleft)

    pygame.draw.rect(screen, (240, 240, 250), panel, 2, border_radius=12)

    title = tiny_font.render("사운드 설정", True, (255, 255, 255))
    screen.blit(title, (panel.x + 16, panel.y + 13))

    bgm_label = mini_font.render(f"BGM  {int(BGM_VOLUME * 100)}%", True, (235, 235, 235))
    sfx_label = mini_font.render(f"SFX  {int(SFX_VOLUME * 100)}%", True, (235, 235, 235))

    screen.blit(bgm_label, (panel.x + 18, panel.y + 48))
    screen.blit(sfx_label, (panel.x + 18, panel.y + 98))

    draw_sound_option_button(
        rects["bgm_toggle"],
        "ON" if BGM_ENABLED else "OFF",
        mini_font,
        (55, 125, 70) if BGM_ENABLED else (125, 55, 55),
    )
    draw_sound_option_button(rects["bgm_minus"], "-", mini_font, (62, 62, 72))
    draw_sound_option_button(rects["bgm_plus"], "+", mini_font, (62, 62, 72))

    draw_sound_option_button(
        rects["sfx_toggle"],
        "ON" if SFX_ENABLED else "OFF",
        mini_font,
        (55, 125, 70) if SFX_ENABLED else (125, 55, 55),
    )
    draw_sound_option_button(rects["sfx_minus"], "-", mini_font, (62, 62, 72))
    draw_sound_option_button(rects["sfx_plus"], "+", mini_font, (62, 62, 72))

    guide = mini_font.render("우측 상단에서 언제든 조절", True, (175, 175, 185))
    screen.blit(guide, (panel.x + 18, panel.bottom - 28))
# === SOUND OPTIONS UI V5 END ===

arena = pygame.Rect(80, 140, 740, 500)

CHARACTER_ORDER = ["beminje", "jaemin", "sungmin", "jungwoo", "suin", "iinrok2", "gyeongsik", "geonwoo"]
ASURA_CHARACTER_ORDER = [key for key in CHARACTER_ORDER if key != "geonwoo"]

CHARACTERS = {
    "beminje": {
        "name": "민재",
        "image": "minjae.jpg",
        "desc": "탕치기와 재간둥이의 콤보는 막강합니다.",
    },
    "jaemin": {
        "name": "재민",
        "image": "jaemin.jpg",
        "desc": "23년도의 재림.",
    },
    "sungmin": {
        "name": "성민",
        "image": "sungmin.jpg",
        "desc": "세계제일의 검사가 되는 그날까지.",
    },
    "jungwoo": {
        "name": "정우",
        "image": "jungwoo.png",
        "desc": "소의 친구.",
    },
    "suin": {
        "name": "수인",
        "image": "suin.jpg",
        "desc": "스웨인을 모티브로 만들어졌습니다.",
    },
    "iinrok2": {
        "name": "이인록2",
        "image": "sunghyun.png",
        "desc": "숙련된 배틀그라운드 유저입니다.",
    },
    "gyeongsik": {
        "name": "경식",
        "image": "gski.png",
        "desc": "해물찜을 던져 화상을 입힙니다.",
    },
    "geonwoo": {
        "name": "건우",
        "image": "gunwoo.jpg",
        "desc": "넣지 않는걸 추천합니다....",
    },
}


CHARACTER_SKILL_GUIDES = {
    "beminje": [
        "습관성 거짓말: 짧은 간격으로 탕을 칩니다.",
        "재간둥이: 일정 시간 공중으로 뛰어올라 피해를 받지 않는다.",
        "착지 충격: 재간둥이 종료 시 주변 적에게 약한 피해를 준다.",
    ],
    "jaemin": [
        "오오라: 주변으로 퍼지는 원형 오오라를 만들어 피해를 준다.",
        "각성재민: 20초마다 잠시 각성해 오오라 쿨타임이 매우 짧아진다.",
        "맵 오오라: 일정 주기마다 경기장 전체에 강한 광역 피해를 준다.",
    ],
    "sungmin": [
        "조준 참격: 상대를 조준한 뒤 짧고 빠른 검격을 날린다.",
        "달빛가르기: 맵 전체를 가르는 긴 검기를 발사한다.",
        "검 장착: 캐릭터가 이동 방향으로 검을 들고 움직인다.",
    ],
    "jungwoo": [
        "소 돌진: 오른쪽에서 왼쪽으로 소가 튀어나와 적을 들이받는다.",
        "소떼 돌진: 여러 마리의 소가 한꺼번에 맵을 가로지른다.",
        "정우 보호: 자신이 부른 소 공격에는 정우가 피해를 받지 않는다.",
    ],
    "suin": [
        "까마귀 손아귀: 적 위치에 장판을 예고한 뒤 피해와 끌어당김을 준다.",
        "악마화: 일정 시간 주변 적에게 지속 피해를 주고 수인이 회복한다.",
        "악마화 폭발: 변신 종료 시 주변 적에게 폭발 피해를 준다.",
    ],
    "iinrok2": [
        "총 발사: 일정 주기마다 가장 가까운 적을 향해 총알을 발사한다.",
        "배그 회복 아이템: 에너지드링크, 붕대, 구급상자 중 하나를 확률로 사용한다.",
        "회복량: 에너지드링크 < 붕대 < 구급상자 순서로 회복량이 크다.",
    ],
    "gyeongsik": [
        "해물찜 투척: 적에게 해물찜을 던져 착지 지점에 열기 장판을 남긴다.",
        "열기 장판: 원형 범위 안의 적에게 지속 피해를 준다.",
        "해물찜 폭격: 맵 전체 랜덤 위치에 해물찜을 여러 개 떨어뜨린다.",
    ],
    "geonwoo": [
        "아수라장에선 등장하지 않습니다.",
        "종말을 일으킵니다."
    ],
}

TEAM_INFOS = [
    {"label": "BLUE", "color": (0, 120, 255)},
    {"label": "RED", "color": (255, 80, 80)},
    {"label": "GREEN", "color": (70, 210, 120)},
    {"label": "PURPLE", "color": (180, 110, 255)},
    {"label": "ORANGE", "color": (255, 150, 55)},
    {"label": "CYAN", "color": (80, 220, 230)},
    {"label": "YELLOW", "color": (235, 220, 70)},
    {"label": "PINK", "color": (255, 120, 190)},
]

BLUE_LASER_COOLDOWN = 3000
MINJE_TRICKSTER_COOLDOWN = 8500
MINJE_TRICKSTER_DURATION = 1250
MINJE_TRICKSTER_LAND_DAMAGE = 10

JAEMIN_AURA_COOLDOWN = 2300
JAEMIN_AWAKENED_AURA_COOLDOWN = 320
JAEMIN_GLOBAL_AURA_COOLDOWN = 30000
JAEMIN_AWAKEN_INTERVAL = 20000
JAEMIN_AWAKEN_DURATION = 5000

SUNGMIN_SLASH_COOLDOWN = 750
SUNGMIN_MOON_SLASH_COOLDOWN = 20000

JUNGWOO_COW_COOLDOWN = 5200
JUNGWOO_COW_ULT_COOLDOWN = 25000

SUIN_GRASP_COOLDOWN = 4300
SUIN_GRASP_WARNING = 650
SUIN_GRASP_FIRE_TIME = 420
SUIN_GRASP_RADIUS = 76
SUIN_GRASP_DAMAGE = 14
SUIN_DEMON_COOLDOWN = 24500
SUIN_DEMON_DURATION = 5600
SUIN_DEMON_RADIUS = 165
SUIN_DEMON_TICK_INTERVAL = 820
SUIN_DEMON_TICK_DAMAGE = 7
SUIN_DEMON_HEAL = 4
SUIN_DEMON_BURST_DAMAGE = 18

IINROK2_SHOT_COOLDOWN = 1800
IINROK2_BULLET_SPEED = 17.0
IINROK2_BULLET_DAMAGE = 11
IINROK2_ITEM_COOLDOWN = 9000
IINROK2_ITEM_TABLE = [
    {"name": "에너지드링크", "heal": 7, "weight": 45, "color": (80, 210, 255)},
    {"name": "붕대", "heal": 14, "weight": 38, "color": (235, 235, 210)},
    {"name": "구급상자", "heal": 32, "weight": 17, "color": (255, 85, 85)},
]

GYEONGSIK_STEW_COOLDOWN = 4300
GYEONGSIK_STEW_ULT_COOLDOWN = 26000
GYEONGSIK_STEW_THROW_TIME = 720
GYEONGSIK_STEW_DAMAGE = 10
GYEONGSIK_HEAT_RADIUS = 72
GYEONGSIK_HEAT_DURATION = 4200
GYEONGSIK_HEAT_TICK_INTERVAL = 650
GYEONGSIK_HEAT_DAMAGE = 5
GYEONGSIK_ULT_STEW_COUNT = 12

GEONWOO_EXECUTE_DELAY = 10000
GEONWOO_ANNIHILATION_FREEZE_TIME = 2600
GEONWOO_ANNIHILATION_FLASH_TIME = 900

particles = []
screen_shake = 0.0


def set_arena_for_count(player_count):
    global arena

    if player_count == 2:
        arena = pygame.Rect(115, 180, 670, 410)
    elif player_count == 3:
        arena = pygame.Rect(70, 155, 760, 470)
    elif player_count == 4:
        arena = pygame.Rect(45, 150, 810, 500)
    else:
        # 아수라장 모드: 모든 캐릭터가 들어가므로 가장 큰 전용 경기장을 사용한다.
        arena = pygame.Rect(25, 150, 850, 525)


def load_circle_image(path, diameter):
    if path is None:
        return None

    path = resource_path(path)

    if not os.path.exists(path):
        return None

    try:
        image = pygame.image.load(path).convert_alpha()
    except pygame.error:
        return None

    image = pygame.transform.smoothscale(image, (diameter, diameter))

    mask = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.circle(
        mask,
        (255, 255, 255, 255),
        (diameter // 2, diameter // 2),
        diameter // 2,
    )

    circle_image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    circle_image.blit(image, (0, 0))
    circle_image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return circle_image


def random_velocity(character_key):
    angle = random.uniform(0, math.pi * 2)

    if character_key == "sungmin":
        speed = random.uniform(4.0, 6.2)
    elif character_key == "jungwoo":
        speed = random.uniform(2.9, 5.2)
    elif character_key == "suin":
        speed = random.uniform(3.0, 5.3)
    elif character_key == "iinrok2":
        speed = random.uniform(3.1, 5.6)
    elif character_key == "gyeongsik":
        speed = random.uniform(2.7, 5.1)
    elif character_key == "geonwoo":
        speed = random.uniform(2.6, 4.8)
    else:
        speed = random.uniform(2.8, 5.0)

    return math.cos(angle) * speed, math.sin(angle) * speed


class Fighter:
    def __init__(self, fighter_id, x, y, team_info, character_key):
        self.fighter_id = fighter_id
        self.team_label = team_info["label"]
        self.x = x
        self.y = y
        self.radius = 25
        self.color = team_info["color"]

        self.character_key = character_key
        self.base_name = CHARACTERS[character_key]["name"]
        self.name = self.base_name

        self.vx, self.vy = random_velocity(character_key)
        self.next_random_turn_time = random.randint(500, 1300)

        if self.character_key == "geonwoo":
            self.hp = 200
            self.max_hp = 200
        else:
            self.hp = 100
            self.max_hp = 100

        self.damage_dealt = 0

        self.damage_flash_until = 0
        self.dodge_flash_until = 0
        self.trail = []

        self.last_laser_time = 0
        self.last_trickster_time = 0
        self.trickster_start_time = 0
        self.is_trickster = False
        self.trickster_landed = False

        self.last_aura_time = 0
        self.last_global_aura_time = 0
        self.last_slash_time = 0
        self.last_moon_slash_time = 0
        self.last_cow_time = 0
        self.last_cow_ult_time = 0
        self.last_suin_grasp_time = 0
        self.last_suin_demon_time = 0
        self.last_iinrok2_shot_time = 0
        self.last_iinrok2_item_time = 0
        self.last_gyeongsik_stew_time = 0
        self.last_gyeongsik_ult_time = 0
        self.geonwoo_execute_ready_time = 0
        self.geonwoo_execute_done = False
        self.is_demon = False
        self.demon_start_time = 0
        self.last_demon_tick_time = 0
        self.demon_burst_done = False

        self.is_awakened = False
        self.awaken_start_time = 0
        self.next_awaken_time = 0

        image_path = CHARACTERS[character_key]["image"]
        self.image = load_circle_image(image_path, self.radius * 2)

    def reset_skill_times(self, current_time):
        self.last_laser_time = current_time
        self.last_trickster_time = current_time
        self.trickster_start_time = 0
        self.is_trickster = False
        self.trickster_landed = False

        self.last_aura_time = current_time
        self.last_global_aura_time = current_time
        self.last_slash_time = current_time
        self.last_moon_slash_time = current_time
        self.last_cow_time = current_time
        self.last_cow_ult_time = current_time
        self.last_suin_grasp_time = current_time
        self.last_suin_demon_time = current_time
        self.last_iinrok2_shot_time = current_time
        self.last_iinrok2_item_time = current_time
        self.last_gyeongsik_stew_time = current_time
        self.last_gyeongsik_ult_time = current_time
        self.geonwoo_execute_ready_time = current_time + GEONWOO_EXECUTE_DELAY
        self.geonwoo_execute_done = False
        self.is_demon = False
        self.demon_start_time = 0
        self.last_demon_tick_time = current_time
        self.demon_burst_done = False
        self.damage_dealt = 0

        self.is_awakened = False
        self.awaken_start_time = 0
        self.next_awaken_time = current_time + JAEMIN_AWAKEN_INTERVAL

        if self.character_key == "jaemin":
            self.name = "재민"
        else:
            self.name = self.base_name

    def is_alive(self):
        return self.hp > 0

    def is_invincible(self, current_time):
        if not self.is_trickster:
            return False

        return current_time - self.trickster_start_time < MINJE_TRICKSTER_DURATION

    def get_direction(self):
        length = math.sqrt(self.vx * self.vx + self.vy * self.vy)

        if length == 0:
            return 1, 0

        return self.vx / length, self.vy / length

    def random_turn(self):
        current_angle = math.atan2(self.vy, self.vx)
        current_speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)

        current_angle += random.uniform(-0.7, 0.7)
        current_speed *= random.uniform(0.85, 1.15)

        if self.character_key == "sungmin":
            current_speed = max(3.8, min(current_speed, 6.4))
        elif self.character_key == "beminje" and self.is_trickster:
            current_speed = max(5.2, min(current_speed + 0.5, 7.2))
        else:
            current_speed = max(2.5, min(current_speed, 5.4))

        self.vx = math.cos(current_angle) * current_speed
        self.vy = math.sin(current_angle) * current_speed

    def move(self, current_time):
        if not self.is_alive():
            return

        if current_time >= self.next_random_turn_time:
            self.random_turn()
            self.next_random_turn_time = current_time + random.randint(600, 1500)

        self.trail.append((self.x, self.y, current_time))
        self.trail = [
            trail
            for trail in self.trail
            if current_time - trail[2] <= 320
        ]

        if len(self.trail) > 12:
            self.trail = self.trail[-12:]

        speed_bonus = 1.35 if self.is_trickster else 1.0
        self.x += self.vx * speed_bonus
        self.y += self.vy * speed_bonus

        if self.x - self.radius <= arena.left:
            self.x = arena.left + self.radius
            self.vx *= -1
            self.random_turn()

        if self.x + self.radius >= arena.right:
            self.x = arena.right - self.radius
            self.vx *= -1
            self.random_turn()

        if self.y - self.radius <= arena.top:
            self.y = arena.top + self.radius
            self.vy *= -1
            self.random_turn()

        if self.y + self.radius >= arena.bottom:
            self.y = arena.bottom - self.radius
            self.vy *= -1
            self.random_turn()

    def draw_trail(self, current_time):
        for trail_x, trail_y, trail_time in self.trail:
            age = current_time - trail_time
            alpha = max(0, 80 - int(age * 0.24))

            if alpha <= 0:
                continue

            trail_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)

            pygame.draw.circle(
                trail_surface,
                (self.color[0], self.color[1], self.color[2], alpha),
                (self.radius, self.radius),
                self.radius,
            )

            screen.blit(
                trail_surface,
                (int(trail_x - self.radius), int(trail_y - self.radius)),
            )

    def draw_sword(self):
        if self.character_key != "sungmin":
            return

        dx, dy = self.get_direction()

        base_x = self.x + dx * 8
        base_y = self.y + dy * 8

        tip_x = self.x + dx * 58
        tip_y = self.y + dy * 58

        side_x = -dy
        side_y = dx

        pygame.draw.line(
            screen,
            (230, 230, 230),
            (int(base_x), int(base_y)),
            (int(tip_x), int(tip_y)),
            6,
        )

        pygame.draw.line(
            screen,
            (255, 255, 255),
            (int(base_x), int(base_y)),
            (int(tip_x), int(tip_y)),
            2,
        )

        pygame.draw.line(
            screen,
            (120, 80, 40),
            (int(base_x + side_x * 12), int(base_y + side_y * 12)),
            (int(base_x - side_x * 12), int(base_y - side_y * 12)),
            4,
        )

    def draw_trickster_effect(self, current_time):
        if not self.is_trickster:
            return

        elapsed = current_time - self.trickster_start_time
        ratio = max(0, min(1, elapsed / MINJE_TRICKSTER_DURATION))
        lift = math.sin(ratio * math.pi) * 38
        pulse = math.sin(current_time / 80) * 4

        shadow = pygame.Surface((70, 28), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 90), (0, 0, 70, 28))
        screen.blit(shadow, (int(self.x - 35), int(self.y + 22)))

        pygame.draw.circle(
            screen,
            (80, 240, 255),
            (int(self.x), int(self.y - lift)),
            int(self.radius + 14 + pulse),
            3,
        )
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (int(self.x), int(self.y - lift)),
            int(self.radius + 23 - pulse),
            2,
        )

    def draw(self, current_time):
        if not self.is_alive():
            return

        self.draw_trail(current_time)
        draw_y = self.y

        if self.is_trickster:
            elapsed = current_time - self.trickster_start_time
            ratio = max(0, min(1, elapsed / MINJE_TRICKSTER_DURATION))
            draw_y -= math.sin(ratio * math.pi) * 38
            self.draw_trickster_effect(current_time)

        if self.image is not None:
            screen.blit(
                self.image,
                (int(self.x - self.radius), int(draw_y - self.radius)),
            )
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (int(self.x), int(draw_y)),
                self.radius,
                2,
            )
        else:
            pygame.draw.circle(
                screen,
                self.color,
                (int(self.x), int(draw_y)),
                self.radius,
            )
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (int(self.x), int(draw_y)),
                self.radius,
                2,
            )

        if self.character_key == "suin" and self.is_demon:
            draw_suin_demon_effect(self, current_time)

        if current_time < self.damage_flash_until:
            flash = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                flash,
                (255, 40, 40, 110),
                (self.radius, self.radius),
                self.radius,
            )
            screen.blit(
                flash,
                (int(self.x - self.radius), int(draw_y - self.radius)),
            )

        if current_time < self.dodge_flash_until:
            pygame.draw.circle(
                screen,
                (120, 250, 255),
                (int(self.x), int(draw_y)),
                self.radius + 12,
                4,
            )

        self.draw_sword()

    def take_damage(self, damage, current_time):
        if not self.is_alive():
            return 0

        if self.is_invincible(current_time):
            self.dodge_flash_until = current_time + 360
            create_hit_particles(
                self.x,
                self.y,
                current_time,
                (90, 240, 255),
                14,
                4,
            )
            add_screen_shake(1.8)
            return 0

        actual_damage = min(self.hp, damage)
        self.hp -= actual_damage

        if self.hp < 0:
            self.hp = 0

        self.damage_flash_until = current_time + 260

        create_hit_particles(self.x, self.y, current_time)
        add_screen_shake(3.5)
        return actual_damage

    def heal(self, amount):
        if not self.is_alive():
            return 0

        before = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before


class BlueLaser:
    def __init__(self, caster, target, start_time):
        self.caster = caster
        self.target = target
        self.start_time = start_time

        self.aim_time = 900
        self.lock_time = 500
        self.fire_time = 180

        self.damage = 22
        self.width = 16

        self.locked = False
        self.hit = False
        self.alive = True
        self.phase = "aim"

        self.origin = None
        self.end = None
        self.lock_target = None
        self.announced = False

    def lock_aim(self):
        dx = self.target.x - self.caster.x
        dy = self.target.y - self.caster.y

        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            dx, dy = 1, 0
            length = 1

        dx /= length
        dy /= length

        start_x = self.caster.x + dx * self.caster.radius
        start_y = self.caster.y + dy * self.caster.radius

        end_x, end_y = get_ray_end(start_x, start_y, dx, dy)

        self.origin = (start_x, start_y)
        self.end = (end_x, end_y)
        self.lock_target = (self.target.x, self.target.y)
        self.locked = True

    def update(self, current_time):
        if not self.caster.is_alive() or not self.target.is_alive():
            self.alive = False
            return

        elapsed = current_time - self.start_time

        if elapsed < self.aim_time:
            self.phase = "aim"
        elif elapsed < self.aim_time + self.lock_time:
            self.phase = "lock"
            if not self.locked:
                self.lock_aim()
        elif elapsed < self.aim_time + self.lock_time + self.fire_time:
            self.phase = "fire"
            if not self.announced:
                play_sound("laser")
                self.announced = True
            if not self.locked:
                self.lock_aim()
        else:
            self.alive = False

    def draw(self):
        if not self.alive:
            return

        if self.phase == "aim":
            pygame.draw.line(
                screen,
                (255, 230, 80),
                (int(self.caster.x), int(self.caster.y)),
                (int(self.target.x), int(self.target.y)),
                2,
            )
            pygame.draw.circle(
                screen,
                (255, 230, 80),
                (int(self.target.x), int(self.target.y)),
                self.target.radius + 13,
                2,
            )
        elif self.phase == "lock" and self.origin is not None:
            pygame.draw.line(
                screen,
                (255, 120, 40),
                (int(self.origin[0]), int(self.origin[1])),
                (int(self.end[0]), int(self.end[1])),
                4,
            )
            pygame.draw.circle(
                screen,
                (255, 120, 40),
                (int(self.lock_target[0]), int(self.lock_target[1])),
                38,
                2,
            )
        elif self.phase == "fire" and self.origin is not None:
            draw_glow_line(self.origin, self.end, (60, 220, 255), self.width + 30, 70)
            pygame.draw.line(
                screen,
                (60, 220, 255),
                (int(self.origin[0]), int(self.origin[1])),
                (int(self.end[0]), int(self.end[1])),
                self.width,
            )
            pygame.draw.line(
                screen,
                (240, 255, 255),
                (int(self.origin[0]), int(self.origin[1])),
                (int(self.end[0]), int(self.end[1])),
                5,
            )


class Aura:
    def __init__(self, caster, start_time):
        self.caster = caster
        self.x = caster.x
        self.y = caster.y
        self.start_time = start_time
        self.duration = 700
        self.max_radius = 130
        self.damage = 16
        self.hit_targets = set()
        self.alive = True

    def update(self, current_time):
        elapsed = current_time - self.start_time

        if elapsed >= self.duration:
            self.alive = False
            return self.max_radius

        ratio = elapsed / self.duration
        return int(self.max_radius * ratio)

    def draw(self, current_time):
        radius = self.update(current_time)

        if self.alive:
            draw_glow_circle((self.x, self.y), radius, (255, 80, 80), 13, 55)
            pygame.draw.circle(screen, (255, 80, 80), (int(self.x), int(self.y)), radius, 5)
            pygame.draw.circle(
                screen,
                (255, 160, 100),
                (int(self.x), int(self.y)),
                max(1, radius // 2),
                3,
            )


class GlobalAura:
    def __init__(self, caster, start_time):
        self.caster = caster
        self.start_time = start_time
        self.charge_time = 1200
        self.fire_time = 700

        self.damage = 25
        self.hit_targets = set()
        self.alive = True
        self.phase = "charge"
        self.announced = False

    def update(self, current_time):
        elapsed = current_time - self.start_time

        if elapsed < self.charge_time:
            self.phase = "charge"
        elif elapsed < self.charge_time + self.fire_time:
            self.phase = "fire"
            if not self.announced:
                play_sound("explosion")
                self.announced = True
        else:
            self.alive = False

    def draw(self, current_time):
        self.update(current_time)

        if self.phase == "charge":
            warning_text = small_font.render(
                f"{self.caster.name} 맵 전체 오오라 준비중!",
                True,
                (255, 80, 80),
            )
            screen.blit(warning_text, (WIDTH // 2 - 165, arena.top + 20))
            pygame.draw.rect(screen, (255, 60, 60), arena, 6)
        elif self.phase == "fire":
            overlay = pygame.Surface((arena.width, arena.height), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 75))
            screen.blit(overlay, (arena.left, arena.top))

            center_x = arena.centerx
            center_y = arena.centery

            pygame.draw.circle(screen, (255, 80, 80), (center_x, center_y), 120, 5)
            pygame.draw.circle(screen, (255, 130, 80), (center_x, center_y), 230, 5)
            pygame.draw.circle(screen, (255, 180, 100), (center_x, center_y), 340, 5)


class SwordSlash:
    def __init__(self, caster, target, start_time):
        self.caster = caster
        self.target = target
        self.start_time = start_time

        self.aim_time = 320
        self.lock_time = 220
        self.fire_time = 180

        self.damage = 13
        self.range = 115
        self.width = 36

        self.phase = "aim"
        self.locked = False
        self.hit = False
        self.alive = True
        self.announced = False

        self.origin = None
        self.end = None
        self.dx = 1
        self.dy = 0
        self.lock_target = None

    def lock_aim(self):
        dx = self.target.x - self.caster.x
        dy = self.target.y - self.caster.y

        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            dx, dy = self.caster.get_direction()
            length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            dx, dy = 1, 0
            length = 1

        self.dx = dx / length
        self.dy = dy / length

        start_x = self.caster.x + self.dx * self.caster.radius
        start_y = self.caster.y + self.dy * self.caster.radius

        end_x = start_x + self.dx * self.range
        end_y = start_y + self.dy * self.range

        self.origin = (start_x, start_y)
        self.end = (end_x, end_y)
        self.lock_target = (self.target.x, self.target.y)
        self.locked = True

    def update(self, current_time):
        if not self.caster.is_alive() or not self.target.is_alive():
            self.alive = False
            return

        elapsed = current_time - self.start_time

        if elapsed < self.aim_time:
            self.phase = "aim"
        elif elapsed < self.aim_time + self.lock_time:
            self.phase = "lock"
            if not self.locked:
                self.lock_aim()
        elif elapsed < self.aim_time + self.lock_time + self.fire_time:
            self.phase = "fire"
            if not self.announced:
                play_sound("slash")
                self.announced = True
            if not self.locked:
                self.lock_aim()
        else:
            self.alive = False

    def draw(self):
        if not self.alive:
            return

        if self.phase == "aim":
            pygame.draw.line(
                screen,
                (180, 230, 255),
                (int(self.caster.x), int(self.caster.y)),
                (int(self.target.x), int(self.target.y)),
                2,
            )
            pygame.draw.circle(
                screen,
                (180, 230, 255),
                (int(self.target.x), int(self.target.y)),
                self.target.radius + 12,
                2,
            )
            pygame.draw.line(
                screen,
                (180, 230, 255),
                (int(self.target.x - 14), int(self.target.y)),
                (int(self.target.x + 14), int(self.target.y)),
                2,
            )
            pygame.draw.line(
                screen,
                (180, 230, 255),
                (int(self.target.x), int(self.target.y - 14)),
                (int(self.target.x), int(self.target.y + 14)),
                2,
            )
        elif self.phase == "lock" and self.origin is not None:
            pygame.draw.line(
                screen,
                (120, 180, 255),
                (int(self.origin[0]), int(self.origin[1])),
                (int(self.end[0]), int(self.end[1])),
                5,
            )
            pygame.draw.circle(
                screen,
                (120, 180, 255),
                (int(self.lock_target[0]), int(self.lock_target[1])),
                36,
                2,
            )
        elif self.phase == "fire" and self.origin is not None:
            draw_glow_line(self.origin, self.end, (120, 210, 255), self.width + 26, 75)

            ox, oy = self.origin
            ex, ey = self.end
            side_x = -self.dy
            side_y = self.dx

            pygame.draw.line(screen, (120, 210, 255), (int(ox), int(oy)), (int(ex), int(ey)), self.width)
            pygame.draw.line(screen, (255, 255, 255), (int(ox), int(oy)), (int(ex), int(ey)), 8)

            for offset in [-22, 22]:
                pygame.draw.line(
                    screen,
                    (180, 240, 255),
                    (int(ox + side_x * offset), int(oy + side_y * offset)),
                    (int(ex - side_x * offset * 0.3), int(ey - side_y * offset * 0.3)),
                    4,
                )


class MoonSlash:
    def __init__(self, caster, start_time):
        self.caster = caster
        self.start_time = start_time
        self.warning_time = 1000
        self.fire_time = 520

        self.damage = 28
        self.width = 34
        self.hit_targets = set()
        self.alive = True
        self.phase = "warning"
        self.announced = False

        dx, dy = caster.get_direction()
        self.angle = math.atan2(dy, dx)
        self.start_point, self.end_point = line_through_arena(self.angle)

    def update(self, current_time):
        elapsed = current_time - self.start_time

        if elapsed < self.warning_time:
            self.phase = "warning"
        elif elapsed < self.warning_time + self.fire_time:
            self.phase = "fire"
            if not self.announced:
                play_sound("moon_slash")
                self.announced = True
        else:
            self.alive = False

    def draw(self):
        sx, sy = self.start_point
        ex, ey = self.end_point

        if self.phase == "warning":
            text = small_font.render("성민 달빛가르기 준비중!", True, (180, 230, 255))
            screen.blit(text, (WIDTH // 2 - 130, arena.top + 45))
            pygame.draw.line(screen, (120, 160, 255), (int(sx), int(sy)), (int(ex), int(ey)), 4)
        elif self.phase == "fire":
            draw_glow_line(self.start_point, self.end_point, (130, 210, 255), self.width + 34, 80)
            pygame.draw.line(screen, (130, 210, 255), (int(sx), int(sy)), (int(ex), int(ey)), self.width)
            pygame.draw.line(screen, (255, 255, 255), (int(sx), int(sy)), (int(ex), int(ey)), 8)


class CowCharge:
    def __init__(self, caster, start_time, y, is_ultimate=False, lane_index=0):
        self.caster = caster
        self.start_time = start_time
        self.y = y
        self.is_ultimate = is_ultimate
        self.lane_index = lane_index

        self.warning_time = 680 if not is_ultimate else 900
        self.x = arena.right + 95 + lane_index * 35
        self.width = 92 if not is_ultimate else 106
        self.height = 48 if not is_ultimate else 54
        self.speed = 12.5 if not is_ultimate else 15.5
        self.damage = 17 if not is_ultimate else 24

        self.hit_targets = set()
        self.phase = "warning"
        self.alive = True

    def update(self, current_time):
        elapsed = current_time - self.start_time

        if elapsed < self.warning_time:
            self.phase = "warning"
            return

        self.phase = "charge"
        self.x -= self.speed

        if self.x + self.width < arena.left - 80:
            self.alive = False

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height / 2),
            int(self.width),
            int(self.height),
        )

    def draw_cow_body(self):
        rect = self.get_rect()
        body_color = (185, 120, 65) if not self.is_ultimate else (230, 180, 90)
        dark = (70, 45, 35)
        horn = (240, 240, 210)

        pygame.draw.ellipse(screen, body_color, rect)
        pygame.draw.ellipse(screen, dark, (rect.x + 18, rect.y + 8, 22, 16))
        pygame.draw.ellipse(screen, dark, (rect.x + 48, rect.y + 22, 26, 15))

        head = pygame.Rect(rect.x - 23, rect.y + 8, 38, 34)
        pygame.draw.ellipse(screen, body_color, head)
        pygame.draw.polygon(
            screen,
            horn,
            [(head.x + 4, head.y + 7), (head.x - 15, head.y - 5), (head.x + 9, head.y + 16)],
        )
        pygame.draw.polygon(
            screen,
            horn,
            [(head.x + 5, head.y + 27), (head.x - 15, head.y + 40), (head.x + 10, head.y + 20)],
        )

        pygame.draw.circle(screen, (0, 0, 0), (head.x + 9, head.y + 13), 3)
        pygame.draw.rect(screen, dark, (rect.x + 18, rect.bottom - 7, 9, 18))
        pygame.draw.rect(screen, dark, (rect.x + 57, rect.bottom - 7, 9, 18))

        if self.is_ultimate:
            draw_glow_line((arena.right, self.y), (arena.left, self.y), (255, 210, 90), 46, 35)

    def draw(self):
        if self.phase == "warning":
            color = (230, 190, 85) if self.is_ultimate else (210, 145, 70)
            pygame.draw.line(screen, color, (arena.right, int(self.y)), (arena.left, int(self.y)), 3)

            label = "정우 소떼 돌진 준비중!" if self.is_ultimate else "소 돌진!"
            text = tiny_font.render(label, True, color)
            screen.blit(text, (arena.right - 210, int(self.y - 34)))
        elif self.phase == "charge":
            self.draw_cow_body()


class RavenGrasp:
    def __init__(self, caster, target, start_time):
        self.caster = caster
        self.start_time = start_time
        self.warning_time = SUIN_GRASP_WARNING
        self.fire_time = SUIN_GRASP_FIRE_TIME
        self.radius = SUIN_GRASP_RADIUS
        self.damage = SUIN_GRASP_DAMAGE
        self.hit_targets = set()
        self.alive = True
        self.phase = "warning"
        self.x = target.x
        self.y = target.y

    def update(self, current_time):
        elapsed = current_time - self.start_time

        if elapsed < self.warning_time:
            self.phase = "warning"
        elif elapsed < self.warning_time + self.fire_time:
            self.phase = "fire"
        else:
            self.alive = False

    def draw(self, current_time):
        pulse = math.sin(current_time / 85) * 5

        if self.phase == "warning":
            pygame.draw.circle(
                screen,
                (130, 40, 70),
                (int(self.x), int(self.y)),
                int(self.radius + pulse),
                3,
            )
            pygame.draw.circle(
                screen,
                (210, 70, 120),
                (int(self.x), int(self.y)),
                9,
                2,
            )

            for angle in [0, math.pi * 0.5, math.pi, math.pi * 1.5]:
                sx = self.x + math.cos(angle) * (self.radius + 12)
                sy = self.y + math.sin(angle) * (self.radius + 12)
                ex = self.x + math.cos(angle) * (self.radius - 12)
                ey = self.y + math.sin(angle) * (self.radius - 12)
                pygame.draw.line(screen, (210, 70, 120), (int(sx), int(sy)), (int(ex), int(ey)), 2)

        elif self.phase == "fire":
            draw_glow_circle((self.x, self.y), self.radius + 22, (150, 40, 75), 28, 70)
            pygame.draw.circle(screen, (130, 35, 70), (int(self.x), int(self.y)), self.radius, 6)
            pygame.draw.circle(screen, (255, 180, 210), (int(self.x), int(self.y)), max(10, self.radius // 3), 3)

            for i in range(10):
                angle = current_time / 180 + i * math.pi * 2 / 10
                sx = self.x + math.cos(angle) * 18
                sy = self.y + math.sin(angle) * 18
                ex = self.x + math.cos(angle) * (self.radius + 8)
                ey = self.y + math.sin(angle) * (self.radius + 8)
                pygame.draw.line(screen, (70, 10, 35), (int(sx), int(sy)), (int(ex), int(ey)), 3)



class GunShot:
    def __init__(self, caster, target, start_time):
        self.caster = caster
        self.start_time = start_time
        self.x = caster.x
        self.y = caster.y
        self.damage = IINROK2_BULLET_DAMAGE
        self.radius = 6
        self.alive = True
        self.hit_targets = set()

        dx = target.x - caster.x
        dy = target.y - caster.y
        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            dx, dy = caster.get_direction()
            length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            dx, dy = 1, 0
            length = 1

        self.dx = dx / length
        self.dy = dy / length
        self.vx = self.dx * IINROK2_BULLET_SPEED
        self.vy = self.dy * IINROK2_BULLET_SPEED
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 7:
            self.trail = self.trail[-7:]

        self.x += self.vx
        self.y += self.vy

        if (
            self.x < arena.left - 80
            or self.x > arena.right + 80
            or self.y < arena.top - 80
            or self.y > arena.bottom + 80
        ):
            self.alive = False

    def draw(self):
        for index, point in enumerate(self.trail):
            alpha = 35 + index * 18
            trail = pygame.Surface((18, 18), pygame.SRCALPHA)
            pygame.draw.circle(trail, (255, 220, 90, alpha), (9, 9), max(2, index + 2))
            screen.blit(trail, (int(point[0] - 9), int(point[1] - 9)))

        pygame.draw.circle(screen, (255, 225, 90), (int(self.x), int(self.y)), self.radius + 3)
        pygame.draw.circle(screen, (255, 255, 245), (int(self.x), int(self.y)), self.radius)


class SeafoodStew:
    def __init__(self, caster, target_x, target_y, start_time, is_ultimate=False):
        self.caster = caster
        self.start_time = start_time
        self.target_x = target_x
        self.target_y = target_y
        self.start_x = caster.x
        self.start_y = caster.y
        self.is_ultimate = is_ultimate
        self.throw_time = GYEONGSIK_STEW_THROW_TIME + random.randint(-90, 130)
        self.damage = GYEONGSIK_STEW_DAMAGE + (4 if is_ultimate else 0)
        self.radius = 18 if not is_ultimate else 22
        self.alive = True
        self.landed = False

    def get_position(self, current_time):
        elapsed = current_time - self.start_time
        ratio = max(0, min(1, elapsed / self.throw_time))
        arc_height = 92 if not self.is_ultimate else 120
        x = self.start_x + (self.target_x - self.start_x) * ratio
        y = self.start_y + (self.target_y - self.start_y) * ratio - math.sin(ratio * math.pi) * arc_height
        return x, y, ratio

    def update(self, current_time):
        if current_time < self.start_time:
            return False

        _, _, ratio = self.get_position(current_time)

        if ratio >= 1 and not self.landed:
            self.landed = True
            self.alive = False
            return True

        return False

    def draw(self, current_time):
        if current_time < self.start_time:
            return

        x, y, ratio = self.get_position(current_time)
        shadow_size = int(12 + ratio * 34)
        shadow = pygame.Surface((shadow_size * 2, shadow_size), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 75), (0, 0, shadow_size * 2, shadow_size))
        screen.blit(shadow, (int(self.target_x - shadow_size), int(self.target_y - shadow_size / 2)))

        pygame.draw.circle(screen, (180, 60, 30), (int(x), int(y)), self.radius + 4)
        pygame.draw.circle(screen, (255, 110, 55), (int(x), int(y)), self.radius)
        pygame.draw.circle(screen, (255, 210, 130), (int(x - 5), int(y - 4)), max(4, self.radius // 3))
        pygame.draw.circle(screen, (230, 230, 170), (int(x + 6), int(y + 3)), max(3, self.radius // 4))


class HeatZone:
    def __init__(self, caster, x, y, start_time, is_ultimate=False):
        self.caster = caster
        self.x = x
        self.y = y
        self.start_time = start_time
        self.duration = GYEONGSIK_HEAT_DURATION + (900 if is_ultimate else 0)
        self.radius = GYEONGSIK_HEAT_RADIUS + (18 if is_ultimate else 0)
        self.damage = GYEONGSIK_HEAT_DAMAGE + (1 if is_ultimate else 0)
        self.tick_interval = GYEONGSIK_HEAT_TICK_INTERVAL
        self.last_tick_by_target = {}
        self.alive = True
        self.is_ultimate = is_ultimate

    def update(self, current_time):
        if current_time - self.start_time >= self.duration:
            self.alive = False

    def draw(self, current_time):
        elapsed = current_time - self.start_time
        ratio = max(0, min(1, elapsed / self.duration))
        pulse = math.sin(current_time / 110) * 5
        alpha = int(90 * (1 - ratio)) + 35
        color = (255, 105, 45) if not self.is_ultimate else (255, 165, 65)

        zone = pygame.Surface((int(self.radius * 2 + 30), int(self.radius * 2 + 30)), pygame.SRCALPHA)
        center = (zone.get_width() // 2, zone.get_height() // 2)
        pygame.draw.circle(zone, (color[0], color[1], color[2], alpha), center, int(self.radius + pulse))
        pygame.draw.circle(zone, (120, 35, 20, 115), center, int(self.radius * 0.72 + pulse), 4)
        screen.blit(zone, (int(self.x - center[0]), int(self.y - center[1])))

        for i in range(6):
            angle = current_time / 260 + i * math.pi * 2 / 6
            fx = self.x + math.cos(angle) * (self.radius * 0.45)
            fy = self.y + math.sin(angle) * (self.radius * 0.45)
            pygame.draw.circle(screen, (255, 190, 85), (int(fx), int(fy)), 4)

class TextEffect:
    def __init__(self, text, x, y, start_time, color=(255, 255, 255)):
        self.text = text
        self.x = x
        self.y = y
        self.start_time = start_time
        self.duration = 650
        self.color = color
        self.alive = True

    def draw(self, current_time):
        elapsed = current_time - self.start_time

        if elapsed >= self.duration:
            self.alive = False
            return

        offset_y = elapsed // 15
        img = small_font.render(self.text, True, self.color)
        screen.blit(img, (self.x, self.y - offset_y))


class Particle:
    def __init__(self, x, y, vx, vy, color, size, life):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.96
        self.vy *= 0.96
        self.vy += 0.05
        self.size *= 0.97
        self.life -= 1

        if self.life <= 0 or self.size <= 0.3:
            self.alive = False

    def draw(self):
        alpha = int(255 * (self.life / self.max_life))
        alpha = max(0, min(255, alpha))

        diameter = max(2, int(self.size * 2))
        particle_surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

        pygame.draw.circle(
            particle_surface,
            (self.color[0], self.color[1], self.color[2], alpha),
            (diameter // 2, diameter // 2),
            diameter // 2,
        )

        screen.blit(
            particle_surface,
            (int(self.x - diameter // 2), int(self.y - diameter // 2)),
        )


def add_screen_shake(power):
    global screen_shake
    screen_shake = max(screen_shake, power)


def create_hit_particles(x, y, current_time, color=(255, 70, 70), amount=18, power=5):
    for _ in range(amount):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1.2, power)

        particles.append(
            Particle(
                x,
                y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                color,
                random.uniform(2.5, 6.0),
                random.randint(18, 34),
            )
        )


def draw_glow_line(start, end, color, width, alpha=80):
    glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.line(
        glow_surface,
        (color[0], color[1], color[2], alpha),
        (int(start[0]), int(start[1])),
        (int(end[0]), int(end[1])),
        width,
    )
    screen.blit(glow_surface, (0, 0))


def draw_glow_circle(center, radius, color, width, alpha=75):
    glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(
        glow_surface,
        (color[0], color[1], color[2], alpha),
        (int(center[0]), int(center[1])),
        int(radius),
        width,
    )
    screen.blit(glow_surface, (0, 0))




def draw_suin_demon_effect(ball, current_time):
    elapsed = current_time - ball.demon_start_time
    ratio = max(0, min(1, elapsed / SUIN_DEMON_DURATION))
    pulse = math.sin(current_time / 95) * 7
    radius = int(SUIN_DEMON_RADIUS * (0.78 + 0.22 * ratio) + pulse)

    draw_glow_circle((ball.x, ball.y), radius, (120, 30, 70), 15, 45)
    pygame.draw.circle(screen, (110, 25, 65), (int(ball.x), int(ball.y)), radius, 3)

    wing_left = [
        (ball.x - 18, ball.y - 10),
        (ball.x - 80 - pulse, ball.y - 45),
        (ball.x - 55, ball.y + 12),
    ]
    wing_right = [
        (ball.x + 18, ball.y - 10),
        (ball.x + 80 + pulse, ball.y - 45),
        (ball.x + 55, ball.y + 12),
    ]
    pygame.draw.polygon(screen, (45, 8, 24), [(int(x), int(y)) for x, y in wing_left])
    pygame.draw.polygon(screen, (45, 8, 24), [(int(x), int(y)) for x, y in wing_right])
    pygame.draw.polygon(screen, (160, 35, 80), [(int(x), int(y)) for x, y in wing_left], 2)
    pygame.draw.polygon(screen, (160, 35, 80), [(int(x), int(y)) for x, y in wing_right], 2)


def draw_damage_graph(fighters):
    panel_x = arena.right + 18
    panel_y = arena.top
    panel_w = WIDTH - panel_x - 15
    panel_h = min(arena.height, 58 + len(fighters) * 36)

    if panel_w < 135:
        panel_x = WIDTH - 160
        panel_w = 145

    pygame.draw.rect(screen, (27, 27, 33), (panel_x, panel_y, panel_w, panel_h), border_radius=12)
    pygame.draw.rect(screen, (210, 210, 220), (panel_x, panel_y, panel_w, panel_h), 2, border_radius=12)

    title = tiny_font.render("입힌 데미지", True, (255, 255, 255))
    screen.blit(title, (panel_x + 12, panel_y + 10))

    max_damage = max([fighter.damage_dealt for fighter in fighters] + [1])
    bar_area_w = panel_w - 24
    start_y = panel_y + 42
    gap = 34 if len(fighters) >= 6 else 43

    for index, fighter in enumerate(fighters):
        y = start_y + index * gap

        if y + 28 > panel_y + panel_h:
            break

        label = f"{fighter.team_label} {fighter.name}"
        if len(label) > 13:
            label = label[:12] + "…"

        label_img = mini_font.render(label, True, fighter.color if fighter.is_alive() else (150, 150, 150))
        screen.blit(label_img, (panel_x + 12, y))

        bar_y = y + 16
        ratio = fighter.damage_dealt / max_damage if max_damage > 0 else 0
        pygame.draw.rect(screen, (52, 52, 58), (panel_x + 12, bar_y, bar_area_w, 11))
        pygame.draw.rect(screen, fighter.color, (panel_x + 12, bar_y, int(bar_area_w * ratio), 11))
        pygame.draw.rect(screen, (230, 230, 230), (panel_x + 12, bar_y, bar_area_w, 11), 1)

        value_img = mini_font.render(str(fighter.damage_dealt), True, (245, 245, 245))
        screen.blit(value_img, (panel_x + panel_w - value_img.get_width() - 12, y))

def draw_center_text(text, y, font_obj, color):
    image = font_obj.render(text, True, color)
    rect = image.get_rect(center=(WIDTH // 2, y))
    screen.blit(image, rect)


def draw_game_over_screen(winner, fighters=None, game_state=None):
    rankings = []
    if fighters is not None and game_state is not None:
        rankings = get_final_rankings(fighters, game_state)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 185))
    screen.blit(overlay, (0, 0))

    if rankings:
        panel_h = min(520, 285 + len(rankings) * 25)
    else:
        panel_h = 320

    panel = pygame.Rect(WIDTH // 2 - 285, HEIGHT // 2 - panel_h // 2, 570, panel_h)
    pygame.draw.rect(screen, (28, 28, 34), panel, border_radius=18)
    pygame.draw.rect(screen, (255, 255, 255), panel, 3, border_radius=18)

    draw_center_text("게임 종료", panel.y + 55, font, (255, 255, 255))
    draw_center_text(winner, panel.y + 100, small_font if rankings else font, (255, 230, 90))

    if rankings:
        draw_final_rankings(fighters, game_state, panel)
        guide_y = panel.bottom - 72
    else:
        guide_y = HEIGHT // 2 + 30

    draw_center_text("R : 같은 캐릭터로 즉시 재시작", guide_y, small_font, (210, 230, 255))
    draw_center_text("M : 메인화면 / Q 또는 ESC : 게임 종료", guide_y + 40, small_font, (255, 190, 190))

    if not rankings:
        draw_center_text("캐릭터를 바꾸고 싶으면 M으로 메인화면에 돌아갈 수 있습니다.", HEIGHT // 2 + 115, tiny_font, (220, 220, 220))


def get_ray_end(x, y, dx, dy):
    candidates = []

    if dx > 0:
        candidates.append((arena.right - x) / dx)
    elif dx < 0:
        candidates.append((arena.left - x) / dx)

    if dy > 0:
        candidates.append((arena.bottom - y) / dy)
    elif dy < 0:
        candidates.append((arena.top - y) / dy)

    positive_candidates = [t for t in candidates if t > 0]

    if not positive_candidates:
        return x, y

    t = min(positive_candidates)

    return x + dx * t, y + dy * t


def line_through_arena(angle):
    cx = arena.centerx
    cy = arena.centery

    dx = math.cos(angle)
    dy = math.sin(angle)

    points = []

    if abs(dx) > 0.0001:
        for x in [arena.left, arena.right]:
            t = (x - cx) / dx
            y = cy + t * dy

            if arena.top <= y <= arena.bottom:
                points.append((x, y))

    if abs(dy) > 0.0001:
        for y in [arena.top, arena.bottom]:
            t = (y - cy) / dy
            x = cx + t * dx

            if arena.left <= x <= arena.right:
                points.append((x, y))

    unique_points = []

    for point in points:
        duplicate = False

        for saved in unique_points:
            if abs(point[0] - saved[0]) < 1 and abs(point[1] - saved[1]) < 1:
                duplicate = True

        if not duplicate:
            unique_points.append(point)

    if len(unique_points) >= 2:
        return unique_points[0], unique_points[1]

    return (arena.left, cy), (arena.right, cy)


def point_line_distance(px, py, start, end):
    x1, y1 = start
    x2, y2 = end

    line_dx = x2 - x1
    line_dy = y2 - y1
    line_len_sq = line_dx * line_dx + line_dy * line_dy

    if line_len_sq == 0:
        return 99999

    t = ((px - x1) * line_dx + (py - y1) * line_dy) / line_len_sq
    t = max(0, min(1, t))

    closest_x = x1 + t * line_dx
    closest_y = y1 + t * line_dy

    dx = px - closest_x
    dy = py - closest_y

    return math.sqrt(dx * dx + dy * dy)


def distance(ball1, ball2):
    dx = ball1.x - ball2.x
    dy = ball1.y - ball2.y

    return math.sqrt(dx * dx + dy * dy)


def check_collision(ball1, ball2):
    return distance(ball1, ball2) < ball1.radius + ball2.radius


def handle_collision(ball1, ball2):
    ball1.vx, ball2.vx = ball2.vx, ball1.vx
    ball1.vy, ball2.vy = ball2.vy, ball1.vy

    ball1.random_turn()
    ball2.random_turn()

    dx = ball1.x - ball2.x
    dy = ball1.y - ball2.y
    dist = math.sqrt(dx * dx + dy * dy)

    if dist == 0:
        return

    overlap = ball1.radius + ball2.radius - dist

    move_x = dx / dist * overlap / 2
    move_y = dy / dist * overlap / 2

    ball1.x += move_x
    ball1.y += move_y
    ball2.x -= move_x
    ball2.y -= move_y


def laser_hits_ball(laser, ball):
    if laser.origin is None or laser.end is None:
        return False

    dist = point_line_distance(ball.x, ball.y, laser.origin, laser.end)
    return dist <= ball.radius + laser.width / 2


def slash_hits_ball(slash, ball):
    if slash.origin is None or slash.end is None:
        return False

    dist = point_line_distance(ball.x, ball.y, slash.origin, slash.end)
    return dist <= ball.radius + slash.width / 2


def moon_slash_hits_ball(moon_slash, ball):
    dist = point_line_distance(ball.x, ball.y, moon_slash.start_point, moon_slash.end_point)
    return dist <= ball.radius + moon_slash.width / 2


def circle_rect_collision(ball, rect):
    closest_x = max(rect.left, min(ball.x, rect.right))
    closest_y = max(rect.top, min(ball.y, rect.bottom))

    dx = ball.x - closest_x
    dy = ball.y - closest_y

    return dx * dx + dy * dy <= ball.radius * ball.radius


def draw_awaken_aura(ball, current_time):
    pulse = math.sin(current_time / 120) * 4

    radius1 = int(ball.radius + 8 + pulse)
    radius2 = int(ball.radius + 15 - pulse)

    pygame.draw.circle(screen, (255, 230, 60), (int(ball.x), int(ball.y)), radius1, 3)
    pygame.draw.circle(screen, (255, 200, 30), (int(ball.x), int(ball.y)), radius2, 2)


def get_ready_ratio(last_time, cooldown, current_time):
    return min(1, max(0, (current_time - last_time) / cooldown))


def draw_mini_skill_bar(x, y, width, label, ratio, color):
    ratio = max(0, min(1, ratio))
    pygame.draw.rect(screen, (50, 50, 55), (x, y, width, 8))
    pygame.draw.rect(screen, color, (x, y, int(width * ratio), 8))
    pygame.draw.rect(screen, (210, 210, 210), (x, y, width, 8), 1)

    label_img = mini_font.render(label, True, (235, 235, 235))
    screen.blit(label_img, (x, y - 15))


def get_skill_infos(ball, current_time):
    if ball.character_key == "beminje":
        return [
            ("레이저", get_ready_ratio(ball.last_laser_time, BLUE_LASER_COOLDOWN, current_time), (60, 220, 255)),
            ("재간", get_ready_ratio(ball.last_trickster_time, MINJE_TRICKSTER_COOLDOWN, current_time), (90, 240, 255)),
        ]

    if ball.character_key == "jaemin":
        aura_cooldown = JAEMIN_AWAKENED_AURA_COOLDOWN if ball.is_awakened else JAEMIN_AURA_COOLDOWN
        awaken_ratio = 1.0

        if ball.is_awakened:
            awaken_ratio = 1 - min(1, (current_time - ball.awaken_start_time) / JAEMIN_AWAKEN_DURATION)
        else:
            awaken_ratio = 1 - min(1, max(0, ball.next_awaken_time - current_time) / JAEMIN_AWAKEN_INTERVAL)

        return [
            ("오라", get_ready_ratio(ball.last_aura_time, aura_cooldown, current_time), (255, 90, 90)),
            ("맵", get_ready_ratio(ball.last_global_aura_time, JAEMIN_GLOBAL_AURA_COOLDOWN, current_time), (255, 160, 80)),
            ("각성", awaken_ratio, (255, 220, 60)),
        ]

    if ball.character_key == "sungmin":
        return [
            ("참격", get_ready_ratio(ball.last_slash_time, SUNGMIN_SLASH_COOLDOWN, current_time), (180, 230, 255)),
            ("달빛", get_ready_ratio(ball.last_moon_slash_time, SUNGMIN_MOON_SLASH_COOLDOWN, current_time), (120, 160, 255)),
        ]

    if ball.character_key == "jungwoo":
        return [
            ("소", get_ready_ratio(ball.last_cow_time, JUNGWOO_COW_COOLDOWN, current_time), (210, 145, 70)),
            ("소떼", get_ready_ratio(ball.last_cow_ult_time, JUNGWOO_COW_ULT_COOLDOWN, current_time), (255, 210, 90)),
        ]

    if ball.character_key == "suin":
        demon_ratio = get_ready_ratio(ball.last_suin_demon_time, SUIN_DEMON_COOLDOWN, current_time)
        if ball.is_demon:
            demon_ratio = 1 - min(1, (current_time - ball.demon_start_time) / SUIN_DEMON_DURATION)

        return [
            ("손아귀", get_ready_ratio(ball.last_suin_grasp_time, SUIN_GRASP_COOLDOWN, current_time), (190, 70, 130)),
            ("악마", demon_ratio, (120, 35, 80)),
        ]

    if ball.character_key == "iinrok2":
        return [
            ("사격", get_ready_ratio(ball.last_iinrok2_shot_time, IINROK2_SHOT_COOLDOWN, current_time), (255, 225, 90)),
            ("회복", get_ready_ratio(ball.last_iinrok2_item_time, IINROK2_ITEM_COOLDOWN, current_time), (100, 220, 180)),
        ]

    if ball.character_key == "gyeongsik":
        return [
            ("해물", get_ready_ratio(ball.last_gyeongsik_stew_time, GYEONGSIK_STEW_COOLDOWN, current_time), (255, 125, 60)),
            ("폭찜", get_ready_ratio(ball.last_gyeongsik_ult_time, GYEONGSIK_STEW_ULT_COOLDOWN, current_time), (255, 175, 75)),
        ]

    if ball.character_key == "geonwoo":
        if ball.geonwoo_execute_done:
            execute_ratio = 1.0
        else:
            start_time = ball.geonwoo_execute_ready_time - GEONWOO_EXECUTE_DELAY
            execute_ratio = min(1, max(0, (current_time - start_time) / GEONWOO_EXECUTE_DELAY))

        return [
            ("말살", execute_ratio, (120, 255, 120)),
        ]

    return []


def draw_compact_status_panels(fighters, current_time):
    count = len(fighters)
    margin = 10
    available_width = min(WIDTH, arena.right + 8)

    if count <= 4:
        panels_per_row = count
        panel_height = 92
        row_gap = 0
    else:
        # 아수라장 모드에서는 상단 UI가 겹치지 않도록 2줄 초소형 패널로 표시한다.
        panels_per_row = 4
        panel_height = 58
        row_gap = 6

    panel_width = (available_width - margin * 2 - 8 * (panels_per_row - 1)) // panels_per_row

    for index, ball in enumerate(fighters):
        row = index // panels_per_row
        col = index % panels_per_row
        x = margin + col * (panel_width + 8)
        y = 14 + row * (panel_height + row_gap)
        bg = (31, 31, 36) if ball.is_alive() else (25, 25, 25)

        pygame.draw.rect(screen, bg, (x, y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(screen, ball.color, (x, y, panel_width, panel_height), 2, border_radius=10)

        name = f"{ball.team_label} {ball.name}"
        if not ball.is_alive():
            name += " OUT"
        if count > 4 and len(name) > 15:
            name = name[:14] + "…"

        name_img = mini_font.render(name, True, (255, 255, 255))
        screen.blit(name_img, (x + 8, y + 6))

        hp_ratio = ball.hp / ball.max_hp
        hp_width = panel_width - 16
        hp_y = y + 25 if count <= 4 else y + 24
        pygame.draw.rect(screen, (55, 55, 55), (x + 8, hp_y, hp_width, 10))
        pygame.draw.rect(screen, ball.color, (x + 8, hp_y, int(hp_width * hp_ratio), 10))
        pygame.draw.rect(screen, (235, 235, 235), (x + 8, hp_y, hp_width, 10), 1)

        hp_text = mini_font.render(f"HP {ball.hp}/{ball.max_hp}", True, (245, 245, 245))
        if count <= 4:
            screen.blit(hp_text, (x + 10, y + 40))
        else:
            screen.blit(hp_text, (x + panel_width - hp_text.get_width() - 8, y + 6))

        skills = get_skill_infos(ball, current_time)
        if skills:
            skill_gap = 5
            skill_width = (hp_width - skill_gap * (len(skills) - 1)) // len(skills)
            skill_y = y + 75 if count <= 4 else y + 47

            for skill_index, skill in enumerate(skills):
                label, ratio, color = skill
                sx = x + 8 + skill_index * (skill_width + skill_gap)

                if count <= 4:
                    draw_mini_skill_bar(sx, skill_y, skill_width, label, ratio, color)
                else:
                    pygame.draw.rect(screen, (50, 50, 55), (sx, skill_y, skill_width, 7))
                    pygame.draw.rect(screen, color, (sx, skill_y, int(skill_width * max(0, min(1, ratio))), 7))
                    pygame.draw.rect(screen, (190, 190, 190), (sx, skill_y, skill_width, 7), 1)

def update_jaemin_awaken(ball, current_time, text_effects):
    if ball.character_key != "jaemin" or not ball.is_alive():
        return

    if not ball.is_awakened and current_time >= ball.next_awaken_time:
        ball.is_awakened = True
        ball.awaken_start_time = current_time
        ball.name = "각성재민"
        ball.last_aura_time = current_time - JAEMIN_AWAKENED_AURA_COOLDOWN
        text_effects.append(TextEffect("각성!", ball.x - 35, ball.y - 60, current_time, (255, 230, 80)))
        play_sound("jaemin_awaken")
        create_hit_particles(ball.x, ball.y, current_time, (255, 230, 80), 32, 7)

    if ball.is_awakened and current_time - ball.awaken_start_time >= JAEMIN_AWAKEN_DURATION:
        ball.is_awakened = False
        ball.name = "재민"
        ball.next_awaken_time = current_time + JAEMIN_AWAKEN_INTERVAL
        ball.last_aura_time = current_time
        text_effects.append(TextEffect("각성 해제", ball.x - 60, ball.y - 60, current_time))


def update_minje_trickster(ball, current_time, fighters, text_effects):
    if ball.character_key != "beminje" or not ball.is_alive():
        return

    if not ball.is_trickster and current_time - ball.last_trickster_time >= MINJE_TRICKSTER_COOLDOWN:
        ball.is_trickster = True
        ball.trickster_start_time = current_time
        ball.last_trickster_time = current_time
        ball.trickster_landed = False
        ball.random_turn()
        text_effects.append(TextEffect("재간둥이!", ball.x - 55, ball.y - 65, current_time, (90, 240, 255)))
        play_sound("trickster")
        create_hit_particles(ball.x, ball.y, current_time, (90, 240, 255), 28, 6)
        add_screen_shake(3)

    if ball.is_trickster and current_time - ball.trickster_start_time >= MINJE_TRICKSTER_DURATION:
        ball.is_trickster = False

        if not ball.trickster_landed:
            ball.trickster_landed = True
            play_sound("land")
            create_hit_particles(ball.x, ball.y, current_time, (90, 240, 255), 36, 7)
            draw_landing_damage(ball, fighters, current_time, text_effects)
            add_screen_shake(5)


def draw_landing_damage(ball, fighters, current_time, text_effects):
    for target in fighters:
        if target == ball or not target.is_alive():
            continue

        dx = ball.x - target.x
        dy = ball.y - target.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist <= 95 + target.radius:
            damaged = target.take_damage(MINJE_TRICKSTER_LAND_DAMAGE, current_time)

            if damaged:
                ball.damage_dealt += damaged
                text_effects.append(TextEffect("착지!", target.x - 35, target.y - 55, current_time, (90, 240, 255)))


def get_nearest_target(caster, fighters):
    targets = [fighter for fighter in fighters if fighter != caster and fighter.is_alive()]

    if not targets:
        return None

    targets.sort(key=lambda target: distance(caster, target))
    return targets[0]


def get_random_cow_y():
    return random.randint(arena.top + 45, arena.bottom - 45)


def get_ultimate_cow_lanes():
    lane_count = 6
    gap = arena.height / (lane_count + 1)
    return [arena.top + gap * (index + 1) for index in range(lane_count)]


def get_random_arena_point(margin=55):
    return (
        random.randint(arena.left + margin, arena.right - margin),
        random.randint(arena.top + margin, arena.bottom - margin),
    )


def choose_iinrok2_item():
    total = sum(item["weight"] for item in IINROK2_ITEM_TABLE)
    pick = random.randint(1, total)
    acc = 0

    for item in IINROK2_ITEM_TABLE:
        acc += item["weight"]
        if pick <= acc:
            return item

    return IINROK2_ITEM_TABLE[0]


def get_gyeongsik_ultimate_points():
    points = []

    for _ in range(GYEONGSIK_ULT_STEW_COUNT):
        points.append(get_random_arena_point(45))

    return points


def use_character_skills(
    caster,
    fighters,
    current_time,
    lasers,
    auras,
    global_auras,
    slashes,
    moon_slashes,
    cow_charges,
    raven_grasps,
    gunshots,
    seafood_stews,
    text_effects,
):
    if not caster.is_alive():
        return

    target = get_nearest_target(caster, fighters)

    if target is None:
        return

    if caster.character_key == "beminje":
        already_using_laser = any(laser.caster == caster for laser in lasers)

        if current_time - caster.last_laser_time >= BLUE_LASER_COOLDOWN and not already_using_laser:
            caster.last_laser_time = current_time
            lasers.append(BlueLaser(caster, target, current_time))

    elif caster.character_key == "jaemin":
        aura_cooldown = JAEMIN_AWAKENED_AURA_COOLDOWN if caster.is_awakened else JAEMIN_AURA_COOLDOWN

        if current_time - caster.last_aura_time >= aura_cooldown:
            caster.last_aura_time = current_time
            auras.append(Aura(caster, current_time))
            play_sound("aura", 0.08 if caster.is_awakened else 0.16)

        already_using_global = any(global_aura.caster == caster for global_aura in global_auras)

        if (
            current_time - caster.last_global_aura_time >= JAEMIN_GLOBAL_AURA_COOLDOWN
            and not already_using_global
        ):
            caster.last_global_aura_time = current_time
            global_auras.append(GlobalAura(caster, current_time))
            play_sound("jaemin_global")
            text_effects.append(TextEffect("맵 오오라!", caster.x - 55, caster.y - 60, current_time, (255, 130, 80)))

    elif caster.character_key == "sungmin":
        already_using_slash = any(slash.caster == caster for slash in slashes)

        if current_time - caster.last_slash_time >= SUNGMIN_SLASH_COOLDOWN and not already_using_slash:
            caster.last_slash_time = current_time
            slashes.append(SwordSlash(caster, target, current_time))

        already_using_moon = any(moon.caster == caster for moon in moon_slashes)

        if (
            current_time - caster.last_moon_slash_time >= SUNGMIN_MOON_SLASH_COOLDOWN
            and not already_using_moon
        ):
            caster.last_moon_slash_time = current_time
            moon_slashes.append(MoonSlash(caster, current_time))
            text_effects.append(TextEffect("달빛가르기!", caster.x - 80, caster.y - 60, current_time, (180, 230, 255)))

    elif caster.character_key == "jungwoo":
        already_using_cow = any(cow.caster == caster and not cow.is_ultimate for cow in cow_charges)

        if current_time - caster.last_cow_time >= JUNGWOO_COW_COOLDOWN and not already_using_cow:
            caster.last_cow_time = current_time
            cow_charges.append(CowCharge(caster, current_time, get_random_cow_y()))
            play_sound("cow_moo")
            text_effects.append(TextEffect("소 돌진!", caster.x - 50, caster.y - 60, current_time, (230, 180, 90)))

        already_using_ult = any(cow.caster == caster and cow.is_ultimate for cow in cow_charges)

        if current_time - caster.last_cow_ult_time >= JUNGWOO_COW_ULT_COOLDOWN and not already_using_ult:
            caster.last_cow_ult_time = current_time
            play_sound("cow_herd")

            for lane_index, lane_y in enumerate(get_ultimate_cow_lanes()):
                cow_charges.append(
                    CowCharge(
                        caster,
                        current_time + lane_index * 120,
                        lane_y,
                        True,
                        lane_index,
                    )
                )

            text_effects.append(TextEffect("소떼 돌진!", caster.x - 70, caster.y - 60, current_time, (255, 220, 90)))
            add_screen_shake(6)

    elif caster.character_key == "suin":
        already_using_grasp = any(grasp.caster == caster for grasp in raven_grasps)

        if current_time - caster.last_suin_grasp_time >= SUIN_GRASP_COOLDOWN and not already_using_grasp:
            caster.last_suin_grasp_time = current_time
            raven_grasps.append(RavenGrasp(caster, target, current_time))
            play_sound("suin_grasp")
            text_effects.append(TextEffect("까마귀 손아귀!", caster.x - 78, caster.y - 60, current_time, (210, 80, 140)))

        if current_time - caster.last_suin_demon_time >= SUIN_DEMON_COOLDOWN and not caster.is_demon:
            caster.last_suin_demon_time = current_time
            caster.is_demon = True
            caster.demon_start_time = current_time
            caster.last_demon_tick_time = current_time
            caster.demon_burst_done = False
            text_effects.append(TextEffect("악마화!", caster.x - 50, caster.y - 65, current_time, (190, 60, 120)))
            play_sound("suin_demon")
            create_hit_particles(caster.x, caster.y, current_time, (160, 45, 95), 46, 8)
            add_screen_shake(6)

    elif caster.character_key == "iinrok2":
        if current_time - caster.last_iinrok2_shot_time >= IINROK2_SHOT_COOLDOWN:
            caster.last_iinrok2_shot_time = current_time
            gunshots.append(GunShot(caster, target, current_time))
            play_sound("gunshot")
            text_effects.append(TextEffect("탕!", caster.x - 20, caster.y - 58, current_time, (255, 225, 90)))

        if current_time - caster.last_iinrok2_item_time >= IINROK2_ITEM_COOLDOWN:
            caster.last_iinrok2_item_time = current_time
            item = choose_iinrok2_item()
            healed = caster.heal(item["heal"])
            play_sound("item")
            text = f"{item['name']} +{healed}"
            text_effects.append(TextEffect(text, caster.x - 65, caster.y - 65, current_time, item["color"]))
            create_hit_particles(caster.x, caster.y, current_time, item["color"], 18 + healed // 2, 4)

    elif caster.character_key == "gyeongsik":
        already_throwing = any(stew.caster == caster and not stew.is_ultimate for stew in seafood_stews)

        if current_time - caster.last_gyeongsik_stew_time >= GYEONGSIK_STEW_COOLDOWN and not already_throwing:
            caster.last_gyeongsik_stew_time = current_time
            seafood_stews.append(SeafoodStew(caster, target.x, target.y, current_time))
            play_sound("stew_throw")
            text_effects.append(TextEffect("해물찜!", caster.x - 45, caster.y - 60, current_time, (255, 130, 70)))

        already_ulting = any(stew.caster == caster and stew.is_ultimate for stew in seafood_stews)

        if current_time - caster.last_gyeongsik_ult_time >= GYEONGSIK_STEW_ULT_COOLDOWN and not already_ulting:
            caster.last_gyeongsik_ult_time = current_time
            play_sound("stew_ult")

            for index, point in enumerate(get_gyeongsik_ultimate_points()):
                seafood_stews.append(
                    SeafoodStew(
                        caster,
                        point[0],
                        point[1],
                        current_time + index * 135,
                        True,
                    )
                )

            text_effects.append(TextEffect("해물찜 폭격!", caster.x - 80, caster.y - 65, current_time, (255, 170, 80)))
            add_screen_shake(6)


def draw_selection_card(x, y, w, h, title, character_key, color, selected=False):
    bg = (55, 55, 62) if selected else (43, 43, 48)
    pygame.draw.rect(screen, bg, (x, y, w, h), border_radius=14)
    pygame.draw.rect(screen, color, (x, y, w, h), 4 if selected else 2, border_radius=14)

    title_img = tiny_font.render(title, True, color)
    screen.blit(title_img, (x + 15, y + 12))

    name = CHARACTERS[character_key]["name"]
    desc = CHARACTERS[character_key]["desc"]

    name_img = small_font.render(name, True, (255, 255, 255))
    screen.blit(name_img, (x + 15, y + 42))

    desc_img = mini_font.render(desc, True, (220, 220, 220))
    screen.blit(desc_img, (x + 15, y + 77))

    image = load_circle_image(CHARACTERS[character_key]["image"], 70)
    cx = x + w // 2
    cy = y + h - 52

    if image is not None:
        screen.blit(image, (cx - 35, cy - 35))
    else:
        pygame.draw.circle(screen, color, (cx, cy), 35)
        pygame.draw.circle(screen, (255, 255, 255), (cx, cy), 35, 2)

    if character_key == "sungmin":
        pygame.draw.line(screen, (230, 230, 230), (cx - 2, cy), (cx + 48, cy - 30), 6)
        pygame.draw.line(screen, (255, 255, 255), (cx - 2, cy), (cx + 48, cy - 30), 2)

    if character_key == "jungwoo":
        pygame.draw.ellipse(screen, (170, 110, 65), (cx + 30, cy + 12, 42, 22))
        pygame.draw.circle(screen, (170, 110, 65), (cx + 28, cy + 21), 12)
        pygame.draw.polygon(screen, (240, 240, 210), [(cx + 20, cy + 14), (cx + 5, cy + 4), (cx + 23, cy + 22)])

    if character_key == "suin":
        pygame.draw.circle(screen, (85, 20, 50), (cx, cy), 42, 3)
        pygame.draw.arc(screen, (180, 50, 105), (cx - 55, cy - 48, 110, 96), math.pi * 0.15, math.pi * 0.85, 4)
        pygame.draw.arc(screen, (180, 50, 105), (cx - 55, cy - 48, 110, 96), math.pi * 1.15, math.pi * 1.85, 4)

    if character_key == "iinrok2":
        pygame.draw.line(screen, (65, 65, 65), (cx - 42, cy + 4), (cx + 42, cy - 16), 8)
        pygame.draw.line(screen, (230, 230, 210), (cx + 8, cy - 8), (cx + 58, cy - 25), 3)
        pygame.draw.rect(screen, (90, 70, 45), (cx - 15, cy + 5, 22, 20), border_radius=4)

    if character_key == "gyeongsik":
        pygame.draw.circle(screen, (180, 60, 30), (cx + 38, cy - 16), 18)
        pygame.draw.circle(screen, (255, 115, 55), (cx + 38, cy - 16), 13)
        pygame.draw.circle(screen, (255, 210, 120), (cx + 32, cy - 20), 4)
        pygame.draw.arc(screen, (255, 135, 70), (cx + 10, cy - 48, 56, 54), 0.2, 2.6, 3)

    if character_key == "geonwoo":
        pygame.draw.rect(screen, (30, 30, 35), (cx - 38, cy - 30, 76, 50), border_radius=8)
        pygame.draw.rect(screen, (120, 255, 120), (cx - 38, cy - 30, 76, 50), 3, border_radius=8)
        code_img = mini_font.render("DEV", True, (120, 255, 120))
        screen.blit(code_img, code_img.get_rect(center=(cx, cy - 5)))
        pygame.draw.line(screen, (120, 255, 120), (cx - 28, cy + 28), (cx + 28, cy + 28), 3)


def draw_menu_button(rect, text, selected, color=(255, 230, 90)):
    bg = (60, 60, 68) if selected else (40, 40, 47)
    border = color if selected else (115, 115, 125)

    pygame.draw.rect(screen, bg, rect, border_radius=16)
    pygame.draw.rect(screen, border, rect, 4 if selected else 2, border_radius=16)

    img = small_font.render(text, True, color if selected else (235, 235, 235))
    screen.blit(img, img.get_rect(center=rect.center))


EXTREME_MODE = "asura"

ASURA_INCLUDE_GEONWOO_DEFAULT = False


def get_asura_character_order(include_geonwoo=False):
    if include_geonwoo:
        return CHARACTER_ORDER[:]

    return [key for key in CHARACTER_ORDER if key != "geonwoo"]


def get_asura_checkbox_rect(option_rect):
    return pygame.Rect(option_rect.x + 18, option_rect.bottom - 40, 22, 22)


def draw_asura_geonwoo_checkbox(option_rect, include_geonwoo, selected):
    checkbox_rect = get_asura_checkbox_rect(option_rect)
    box_color = (120, 255, 120) if include_geonwoo else (185, 185, 190)
    label_color = (220, 255, 220) if include_geonwoo else (210, 210, 215)

    pygame.draw.rect(screen, (28, 28, 34), checkbox_rect, border_radius=5)
    pygame.draw.rect(screen, box_color, checkbox_rect, 2, border_radius=5)

    if include_geonwoo:
        pygame.draw.line(
            screen,
            (120, 255, 120),
            (checkbox_rect.x + 5, checkbox_rect.centery),
            (checkbox_rect.x + 10, checkbox_rect.bottom - 6),
            3,
        )
        pygame.draw.line(
            screen,
            (120, 255, 120),
            (checkbox_rect.x + 10, checkbox_rect.bottom - 6),
            (checkbox_rect.right - 5, checkbox_rect.y + 5),
            3,
        )

    label = "건우 포함" if include_geonwoo else "건우 제외"
    if selected:
        label += "  [G]"

    label_img = mini_font.render(label, True, label_color)
    screen.blit(label_img, (checkbox_rect.right + 8, checkbox_rect.y + 1))




def creator_screen():
    back_rect = pygame.Rect(WIDTH // 2 - 130, 580, 260, 58)

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if handle_sound_options_event(event):
                continue
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_RETURN]:
                    return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return

        screen.fill((16, 16, 22))
        draw_center_text("제작자 확인", 85, font, (255, 255, 255))
        draw_center_text("이 게임의 기획과 구현 기록", 135, tiny_font, (190, 190, 205))

        panel = pygame.Rect(WIDTH // 2 - 330, 180, 660, 350)
        pygame.draw.rect(screen, (32, 32, 40), panel, border_radius=20)
        pygame.draw.rect(screen, (255, 230, 90), panel, 3, border_radius=20)

        role_lines = [
            ("아이디어", "김건우"),
            ("코드 구현", "김건우"),
            ("게임 구현", "김건우"),
            ("그래픽 디자인", "김건우"),
        ]

        y = 230
        for role, name in role_lines:
            role_img = small_font.render(role, True, (170, 210, 255))
            name_img = small_font.render(name, True, (255, 255, 255))
            screen.blit(role_img, (WIDTH // 2 - 220, y))
            screen.blit(name_img, (WIDTH // 2 + 65, y))
            y += 54

        draw_center_text("모든 건 김건우가 했지만...", 475, small_font, (255, 230, 90))
        draw_center_text("Enter / ESC / 클릭으로 메인화면 복귀", 540, tiny_font, (180, 180, 190))

        draw_menu_button(back_rect, "메인화면으로", back_rect.collidepoint(mouse_pos), (255, 230, 90))
        draw_sound_options_ui()
        pygame.display.flip()


def character_info_screen():
    selected = 0
    back_rect = pygame.Rect(WIDTH - 185, 615, 145, 48)

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        list_rects = []

        for idx, character_key in enumerate(CHARACTER_ORDER):
            list_rects.append(pygame.Rect(55, 145 + idx * 66, 250, 54))

        for event in pygame.event.get():
            if handle_sound_options_event(event):
                continue
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEMOTION:
                for idx, rect in enumerate(list_rects):
                    if rect.collidepoint(event.pos):
                        selected = idx

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return

                for idx, rect in enumerate(list_rects):
                    if rect.collidepoint(event.pos):
                        selected = idx

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                    return
                if event.key in [pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a]:
                    selected = (selected - 1) % len(CHARACTER_ORDER)
                if event.key in [pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d, pygame.K_TAB]:
                    selected = (selected + 1) % len(CHARACTER_ORDER)
                if event.key == pygame.K_RETURN:
                    return

        screen.fill((16, 16, 22))
        draw_center_text("캐릭터 소개", 65, font, (255, 255, 255))
        draw_center_text("방향키 / A,D / 마우스로 캐릭터를 골라 스킬을 확인하세요", 110, tiny_font, (190, 190, 205))

        for idx, rect in enumerate(list_rects):
            key = CHARACTER_ORDER[idx]
            character = CHARACTERS[key]
            is_selected = idx == selected
            color = TEAM_INFOS[idx % len(TEAM_INFOS)]["color"]
            bg = (56, 56, 66) if is_selected else (36, 36, 44)
            border = color if is_selected else (100, 100, 112)

            pygame.draw.rect(screen, bg, rect, border_radius=12)
            pygame.draw.rect(screen, border, rect, 3 if is_selected else 1, border_radius=12)

            name_img = small_font.render(character["name"], True, color if is_selected else (230, 230, 235))
            screen.blit(name_img, (rect.x + 18, rect.y + 13))

        detail = pygame.Rect(345, 145, 650, 445)
        pygame.draw.rect(screen, (31, 31, 39), detail, border_radius=18)
        pygame.draw.rect(screen, (230, 230, 240), detail, 2, border_radius=18)

        selected_key = CHARACTER_ORDER[selected]
        character = CHARACTERS[selected_key]
        color = TEAM_INFOS[selected % len(TEAM_INFOS)]["color"]

        title_img = font.render(character["name"], True, color)
        screen.blit(title_img, (detail.x + 35, detail.y + 28))

        image = load_circle_image(character["image"], 130)
        if image is not None:
            screen.blit(image, (detail.right - 185, detail.y + 35))
        else:
            pygame.draw.circle(screen, color, (detail.right - 120, detail.y + 100), 65)
            pygame.draw.circle(screen, (255, 255, 255), (detail.right - 120, detail.y + 100), 65, 3)

        desc_img = small_font.render(character["desc"], True, (225, 225, 230))
        screen.blit(desc_img, (detail.x + 35, detail.y + 92))

        skill_title = small_font.render("보유 스킬", True, (255, 230, 90))
        screen.blit(skill_title, (detail.x + 35, detail.y + 155))

        skill_lines = CHARACTER_SKILL_GUIDES.get(selected_key, [character["desc"]])
        y = detail.y + 200
        for idx, line in enumerate(skill_lines, start=1):
            number_img = tiny_font.render(f"{idx}.", True, color)
            line_img = tiny_font.render(line, True, (240, 240, 245))
            screen.blit(number_img, (detail.x + 45, y))
            screen.blit(line_img, (detail.x + 78, y))
            y += 38

        guide_lines = [
            "이미지 파일은 파이썬 파일과 같은 폴더에 두면 자동 적용됩니다.",
            "Enter / ESC / 뒤로가기 버튼으로 메인화면으로 돌아갑니다.",
        ]
        y = detail.bottom - 70
        for line in guide_lines:
            guide_img = mini_font.render(line, True, (170, 170, 180))
            screen.blit(guide_img, (detail.x + 35, y))
            y += 24

        draw_menu_button(back_rect, "뒤로", back_rect.collidepoint(mouse_pos), (255, 230, 90))
        draw_sound_options_ui()
        pygame.display.flip()


def main_menu():
    selected = 0
    buttons = [
        ("게임 시작", "start"),
        ("제작자 확인", "credits"),
        ("캐릭터 소개", "characters"),
        ("게임 종료", "quit"),
    ]

    while True:
        clock.tick(60)
        button_rects = []
        start_y = 285

        for idx in range(len(buttons)):
            button_rects.append(pygame.Rect(WIDTH // 2 - 170, start_y + idx * 74, 340, 58))

        for event in pygame.event.get():
            if handle_sound_options_event(event):
                continue
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEMOTION:
                for idx, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        selected = idx

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        action = buttons[idx][1]

                        if action == "start":
                            return action
                        if action == "credits":
                            creator_screen()
                        if action == "characters":
                            character_info_screen()
                        if action == "quit":
                            pygame.quit()
                            raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    selected = (selected - 1) % len(buttons)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    selected = (selected + 1) % len(buttons)
                elif event.key == pygame.K_RETURN:
                    action = buttons[selected][1]

                    if action == "start":
                        return action
                    if action == "credits":
                        creator_screen()
                    if action == "characters":
                        character_info_screen()
                    if action == "quit":
                        pygame.quit()
                        raise SystemExit
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit

        screen.fill((16, 16, 22))

        draw_center_text("ARENA BATTLE", 105, font, (255, 255, 255))
        draw_center_text("캐릭터 난투 자동 전투", 160, small_font, (220, 220, 230))
        draw_center_text("방향키 또는 W/S로 이동, Enter 또는 마우스 클릭으로 선택", 215, tiny_font, (170, 170, 180))

        for idx, (label, _) in enumerate(buttons):
            draw_menu_button(button_rects[idx], label, selected == idx)

        guide = tiny_font.render("게임 시작 후 전투 인원 선택창에서 아수라장 모드도 고를 수 있습니다.", True, (180, 180, 190))
        screen.blit(guide, guide.get_rect(center=(WIDTH // 2, 620)))

        draw_sound_options_ui()
        pygame.display.flip()

def mode_screen():
    selected_mode = 2
    asura_include_geonwoo = ASURA_INCLUDE_GEONWOO_DEFAULT

    options = [
        (2, "1대1", "작은 경기장"),
        (3, "1대1대1", "확장 경기장"),
        (4, "1대1대1대1", "최대 경기장"),
        (EXTREME_MODE, "아수라장", "모든 캐릭터 / 초대형"),
    ]

    while True:
        clock.tick(60)
        option_w = 215
        option_gap = 18
        start_x = (WIDTH - (option_w * len(options) + option_gap * (len(options) - 1))) // 2
        option_rects = []

        for idx, option in enumerate(options):
            rect = pygame.Rect(start_x + idx * (option_w + option_gap), 250, option_w, 170)
            option_rects.append(rect)

        asura_index = [item[0] for item in options].index(EXTREME_MODE)
        asura_rect = option_rects[asura_index]
        asura_checkbox_rect = get_asura_checkbox_rect(asura_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEMOTION:
                for idx, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        selected_mode = options[idx][0]

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if asura_checkbox_rect.collidepoint(event.pos):
                    selected_mode = EXTREME_MODE
                    asura_include_geonwoo = not asura_include_geonwoo
                    play_sound("button")
                    continue

                for idx, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        selected_mode = options[idx][0]
                        return selected_mode, asura_include_geonwoo

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_2:
                    selected_mode = 2
                elif event.key == pygame.K_3:
                    selected_mode = 3
                elif event.key == pygame.K_4:
                    selected_mode = 4
                elif event.key in [pygame.K_a, pygame.K_5]:
                    selected_mode = EXTREME_MODE
                elif event.key == pygame.K_g and selected_mode == EXTREME_MODE:
                    asura_include_geonwoo = not asura_include_geonwoo
                    play_sound("button")
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    current_index = [item[0] for item in options].index(selected_mode)
                    selected_mode = options[(current_index - 1) % len(options)][0]
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    current_index = [item[0] for item in options].index(selected_mode)
                    selected_mode = options[(current_index + 1) % len(options)][0]
                elif event.key == pygame.K_RETURN:
                    return selected_mode, asura_include_geonwoo
                elif event.key == pygame.K_ESCAPE:
                    return None

        screen.fill((18, 18, 22))
        draw_center_text("전투 인원 선택", 90, font, (255, 255, 255))
        draw_center_text("2 / 3 / 4 또는 A: 아수라장", 155, small_font, (220, 220, 220))
        draw_center_text("아수라장 선택 후 G 또는 체크박스: 건우 포함/제외", 190, tiny_font, (190, 220, 190))
        draw_center_text("Enter: 선택 완료 / ESC: 메인화면", 590, small_font, (255, 255, 255))

        for idx, option in enumerate(options):
            mode_value, label, size_text = option
            rect = option_rects[idx]
            selected = mode_value == selected_mode
            color = (255, 230, 90) if selected else (120, 120, 130)
            bg = (52, 52, 60) if selected else (42, 42, 48)

            pygame.draw.rect(screen, bg, rect, border_radius=16)
            pygame.draw.rect(screen, color, rect, 4 if selected else 2, border_radius=16)

            label_img = small_font.render(label, True, color)
            screen.blit(label_img, label_img.get_rect(center=(rect.centerx, rect.centery - 33)))

            text_img = tiny_font.render(size_text, True, (230, 230, 230))
            screen.blit(text_img, text_img.get_rect(center=(rect.centerx, rect.centery + 5)))

            if mode_value == EXTREME_MODE:
                count = len(get_asura_character_order(asura_include_geonwoo))
                count_img = mini_font.render(f"{count}명 투입", True, (255, 190, 120))
                screen.blit(count_img, count_img.get_rect(center=(rect.centerx, rect.centery + 33)))
                draw_asura_geonwoo_checkbox(rect, asura_include_geonwoo, selected)

        pygame.display.flip()


def get_selection_positions(player_count):
    if player_count == 2:
        return [(95, 210), (505, 210)], 300, 250

    if player_count == 3:
        return [(40, 230), (315, 230), (590, 230)], 260, 235

    return [(85, 170), (505, 170), (85, 410), (505, 410)], 310, 205


def selection_screen(player_count):
    indices = [index % len(CHARACTER_ORDER) for index in range(player_count)]
    selected_slot = 0

    def make_card_rects():
        positions, card_w, card_h = get_selection_positions(player_count)
        return [
            pygame.Rect(x, y, card_w, card_h)
            for x, y in positions
        ], positions, card_w, card_h

    def get_arrow_rects(card_rect):
        left_rect = pygame.Rect(card_rect.x + 16, card_rect.centery - 23, 42, 46)
        right_rect = pygame.Rect(card_rect.right - 58, card_rect.centery - 23, 42, 46)
        return left_rect, right_rect

    def draw_arrow_button(rect, text, hover):
        bg = (65, 65, 74) if hover else (44, 44, 52)
        border = (255, 230, 90) if hover else (130, 130, 142)
        pygame.draw.rect(screen, bg, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 2, border_radius=10)
        img = small_font.render(text, True, border)
        screen.blit(img, img.get_rect(center=rect.center))

    start_rect = pygame.Rect(WIDTH // 2 - 135, 637, 270, 44)

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        card_rects, positions, card_w, card_h = make_card_rects()

        for event in pygame.event.get():
            if handle_sound_options_event(event):
                continue
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEMOTION:
                for slot, rect in enumerate(card_rects):
                    if rect.collidepoint(event.pos):
                        selected_slot = slot

            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    indices[selected_slot] = (indices[selected_slot] - 1) % len(CHARACTER_ORDER)
                    play_sound("button")
                elif event.y < 0:
                    indices[selected_slot] = (indices[selected_slot] + 1) % len(CHARACTER_ORDER)
                    play_sound("button")

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_rect.collidepoint(event.pos):
                    play_sound("button")
                    return [CHARACTER_ORDER[index] for index in indices]

                for slot, rect in enumerate(card_rects):
                    left_rect, right_rect = get_arrow_rects(rect)

                    if left_rect.collidepoint(event.pos):
                        selected_slot = slot
                        indices[selected_slot] = (indices[selected_slot] - 1) % len(CHARACTER_ORDER)
                        play_sound("button")
                        break

                    if right_rect.collidepoint(event.pos):
                        selected_slot = slot
                        indices[selected_slot] = (indices[selected_slot] + 1) % len(CHARACTER_ORDER)
                        play_sound("button")
                        break

                    if rect.collidepoint(event.pos):
                        selected_slot = slot
                        play_sound("button")
                        break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None

                if event.key == pygame.K_TAB:
                    selected_slot = (selected_slot + 1) % player_count

                if event.key in [pygame.K_1, pygame.K_KP1] and player_count >= 1:
                    selected_slot = 0
                if event.key in [pygame.K_2, pygame.K_KP2] and player_count >= 2:
                    selected_slot = 1
                if event.key in [pygame.K_3, pygame.K_KP3] and player_count >= 3:
                    selected_slot = 2
                if event.key in [pygame.K_4, pygame.K_KP4] and player_count >= 4:
                    selected_slot = 3

                if event.key in [pygame.K_a, pygame.K_LEFT]:
                    indices[selected_slot] = (indices[selected_slot] - 1) % len(CHARACTER_ORDER)

                if event.key in [pygame.K_d, pygame.K_RIGHT]:
                    indices[selected_slot] = (indices[selected_slot] + 1) % len(CHARACTER_ORDER)

                if event.key == pygame.K_RETURN:
                    return [CHARACTER_ORDER[index] for index in indices]

        screen.fill((18, 18, 22))

        title = font.render("출전 캐릭터 선택", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - 140, 55))

        mode_text = "1대1" if player_count == 2 else "1대1대1" if player_count == 3 else "1대1대1대1"
        guide1 = small_font.render(f"현재 모드: {mode_text}", True, (255, 230, 90))
        guide2 = tiny_font.render("마우스: 카드 선택 / ◀ ▶ 클릭 또는 휠: 캐릭터 변경 / 키보드도 사용 가능", True, (220, 220, 220))
        guide3 = mini_font.render("Enter 또는 경기 시작 버튼: 시작 / ESC: 인원 선택으로 돌아가기", True, (230, 230, 235))

        screen.blit(guide1, (70, 110))
        screen.blit(guide2, (70, 145))
        screen.blit(guide3, (WIDTH // 2 - 240, 615))

        for slot in range(player_count):
            x, y = positions[slot]
            rect = card_rects[slot]
            team = TEAM_INFOS[slot]
            title_text = f"{slot + 1}. {team['label']}"

            draw_selection_card(
                x,
                y,
                card_w,
                card_h,
                title_text,
                CHARACTER_ORDER[indices[slot]],
                team["color"],
                selected_slot == slot,
            )

            left_rect, right_rect = get_arrow_rects(rect)
            draw_arrow_button(left_rect, "◀", left_rect.collidepoint(mouse_pos))
            draw_arrow_button(right_rect, "▶", right_rect.collidepoint(mouse_pos))

            if rect.collidepoint(mouse_pos):
                hover_tip = mini_font.render("클릭: 이 슬롯 선택", True, (235, 235, 245))
                screen.blit(hover_tip, hover_tip.get_rect(center=(rect.centerx, rect.bottom - 20)))

        draw_menu_button(start_rect, "경기 시작", start_rect.collidepoint(mouse_pos), (255, 230, 90))

        draw_sound_options_ui()
        pygame.display.flip()




def create_match(character_keys):
    current_time = pygame.time.get_ticks()
    player_count = len(character_keys)
    set_arena_for_count(player_count)

    if player_count == 2:
        positions = [
            (arena.left + 150, arena.centery),
            (arena.right - 150, arena.centery),
        ]
    elif player_count == 3:
        positions = [
            (arena.centerx, arena.top + 80),
            (arena.left + 120, arena.bottom - 85),
            (arena.right - 120, arena.bottom - 85),
        ]
    elif player_count == 4:
        positions = [
            (arena.left + 110, arena.top + 85),
            (arena.right - 110, arena.top + 85),
            (arena.left + 110, arena.bottom - 85),
            (arena.right - 110, arena.bottom - 85),
        ]
    else:
        # 아수라장 모드: 전원을 원형으로 배치해 시작부터 한쪽에 몰리지 않게 한다.
        positions = []
        center_x = arena.centerx
        center_y = arena.centery
        radius_x = arena.width / 2 - 90
        radius_y = arena.height / 2 - 80

        for index in range(player_count):
            angle = -math.pi / 2 + math.pi * 2 * index / player_count
            positions.append((center_x + math.cos(angle) * radius_x, center_y + math.sin(angle) * radius_y))

    fighters = []

    for index, character_key in enumerate(character_keys):
        x, y = positions[index]
        team_info = TEAM_INFOS[index % len(TEAM_INFOS)]
        fighter = Fighter(index, x, y, team_info, character_key)
        fighter.reset_skill_times(current_time)
        fighters.append(fighter)

    return fighters


def reset_match_lists():
    return {
        "lasers": [],
        "auras": [],
        "global_auras": [],
        "slashes": [],
        "moon_slashes": [],
        "cow_charges": [],
        "raven_grasps": [],
        "gunshots": [],
        "seafood_stews": [],
        "heat_zones": [],
        "text_effects": [],
        "body_hit_times": {},
        "geonwoo_annihilation": None,
        "death_order": [],
    }


def choose_mode_and_characters():
    while True:
        main_menu()

        while True:
            mode_result = mode_screen()

            if mode_result is None:
                break

            selected_mode, asura_include_geonwoo = mode_result

            if selected_mode == EXTREME_MODE:
                return get_asura_character_order(asura_include_geonwoo)

            selected_keys = selection_screen(selected_mode)

            if selected_keys is not None:
                return selected_keys


def apply_body_collisions(fighters, current_time, body_hit_times):
    alive_fighters = [fighter for fighter in fighters if fighter.is_alive()]

    for i in range(len(alive_fighters)):
        for j in range(i + 1, len(alive_fighters)):
            first = alive_fighters[i]
            second = alive_fighters[j]

            if check_collision(first, second):
                handle_collision(first, second)

                pair_key = tuple(sorted([first.fighter_id, second.fighter_id]))
                last_hit_time = body_hit_times.get(pair_key, 0)

                if current_time - last_hit_time >= 500:
                    play_sound("body_hit")
                    first_dealt = second.take_damage(4, current_time)
                    second_dealt = first.take_damage(4, current_time)
                    first.damage_dealt += first_dealt
                    second.damage_dealt += second_dealt
                    body_hit_times[pair_key] = current_time


def update_lasers(lasers, current_time, text_effects):
    for laser in lasers:
        laser.update(current_time)

        if laser.phase == "fire" and laser.origin is not None and not laser.announced:
            text_effects.append(
                TextEffect("탕!", laser.origin[0] - 20, laser.origin[1] - 55, current_time, (120, 230, 255))
            )
            laser.announced = True

        if laser.phase == "fire" and not laser.hit:
            if laser.target.is_alive() and laser_hits_ball(laser, laser.target):
                damaged = laser.target.take_damage(laser.damage, current_time)

                if damaged:
                    laser.caster.damage_dealt += damaged
                    create_hit_particles(laser.target.x, laser.target.y, current_time, (60, 220, 255), 24, 7)
                    add_screen_shake(7)
                else:
                    text_effects.append(TextEffect("회피!", laser.target.x - 35, laser.target.y - 55, current_time, (90, 240, 255)))

                laser.hit = True

    return [laser for laser in lasers if laser.alive]


def update_auras(auras, fighters, current_time):
    for aura in auras:
        radius = aura.update(current_time)

        for target in fighters:
            if target == aura.caster or not target.is_alive() or target.fighter_id in aura.hit_targets:
                continue

            dx = aura.x - target.x
            dy = aura.y - target.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < radius + target.radius:
                damaged = target.take_damage(aura.damage, current_time)

                if damaged:
                    aura.caster.damage_dealt += damaged
                    create_hit_particles(target.x, target.y, current_time, (255, 130, 80), 26, 6)
                    add_screen_shake(6)

                aura.hit_targets.add(target.fighter_id)

    return [aura for aura in auras if aura.alive]


def update_global_auras(global_auras, fighters, current_time):
    for global_aura in global_auras:
        global_aura.update(current_time)

        if global_aura.phase != "fire":
            continue

        for target in fighters:
            if target == global_aura.caster or not target.is_alive() or target.fighter_id in global_aura.hit_targets:
                continue

            damaged = target.take_damage(global_aura.damage, current_time)

            if damaged:
                global_aura.caster.damage_dealt += damaged
                create_hit_particles(target.x, target.y, current_time, (255, 80, 80), 42, 8)
                add_screen_shake(10)

            global_aura.hit_targets.add(target.fighter_id)

    return [global_aura for global_aura in global_auras if global_aura.alive]


def update_slashes(slashes, current_time, text_effects):
    for slash in slashes:
        slash.update(current_time)

        if slash.phase == "fire" and slash.origin is not None and not slash.announced:
            text_effects.append(
                TextEffect("참격!", slash.origin[0] - 35, slash.origin[1] - 55, current_time, (180, 230, 255))
            )
            slash.announced = True

        if slash.phase == "fire" and not slash.hit:
            if slash.target.is_alive() and slash_hits_ball(slash, slash.target):
                damaged = slash.target.take_damage(slash.damage, current_time)

                if damaged:
                    slash.caster.damage_dealt += damaged
                    create_hit_particles(slash.target.x, slash.target.y, current_time, (180, 230, 255), 26, 7)
                    add_screen_shake(7)
                else:
                    text_effects.append(TextEffect("회피!", slash.target.x - 35, slash.target.y - 55, current_time, (90, 240, 255)))

                slash.hit = True

    return [slash for slash in slashes if slash.alive]


def update_moon_slashes(moon_slashes, fighters, current_time, text_effects):
    for moon_slash in moon_slashes:
        moon_slash.update(current_time)

        if moon_slash.phase != "fire":
            continue

        for target in fighters:
            if target == moon_slash.caster or not target.is_alive() or target.fighter_id in moon_slash.hit_targets:
                continue

            if moon_slash_hits_ball(moon_slash, target):
                damaged = target.take_damage(moon_slash.damage, current_time)

                if damaged:
                    moon_slash.caster.damage_dealt += damaged
                    create_hit_particles(target.x, target.y, current_time, (170, 220, 255), 48, 9)
                    add_screen_shake(11)
                else:
                    text_effects.append(TextEffect("회피!", target.x - 35, target.y - 55, current_time, (90, 240, 255)))

                moon_slash.hit_targets.add(target.fighter_id)

    return [moon for moon in moon_slashes if moon.alive]


def update_cow_charges(cow_charges, fighters, current_time, text_effects):
    for cow in cow_charges:
        cow.update(current_time)

        if cow.phase != "charge":
            continue

        rect = cow.get_rect()

        for target in fighters:
            if target == cow.caster or not target.is_alive() or target.fighter_id in cow.hit_targets:
                continue

            if circle_rect_collision(target, rect):
                damaged = target.take_damage(cow.damage, current_time)

                if damaged:
                    cow.caster.damage_dealt += damaged
                    color = (255, 210, 90) if cow.is_ultimate else (210, 145, 70)
                    create_hit_particles(target.x, target.y, current_time, color, 34 if cow.is_ultimate else 24, 8)
                    add_screen_shake(9 if cow.is_ultimate else 6)
                else:
                    text_effects.append(TextEffect("회피!", target.x - 35, target.y - 55, current_time, (90, 240, 255)))

                cow.hit_targets.add(target.fighter_id)

    return [cow for cow in cow_charges if cow.alive]




def update_raven_grasps(raven_grasps, fighters, current_time, text_effects):
    for grasp in raven_grasps:
        grasp.update(current_time)

        if grasp.phase != "fire":
            continue

        for target in fighters:
            if target == grasp.caster or not target.is_alive() or target.fighter_id in grasp.hit_targets:
                continue

            dx = target.x - grasp.x
            dy = target.y - grasp.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist <= grasp.radius + target.radius:
                dealt = target.take_damage(grasp.damage, current_time)

                if dealt:
                    grasp.caster.damage_dealt += dealt
                    create_hit_particles(target.x, target.y, current_time, (190, 70, 130), 30, 7)
                    add_screen_shake(7)

                    pull_dx = grasp.caster.x - target.x
                    pull_dy = grasp.caster.y - target.y
                    pull_len = math.sqrt(pull_dx * pull_dx + pull_dy * pull_dy)

                    if pull_len > 0:
                        target.x += pull_dx / pull_len * 26
                        target.y += pull_dy / pull_len * 26
                        target.x = max(arena.left + target.radius, min(arena.right - target.radius, target.x))
                        target.y = max(arena.top + target.radius, min(arena.bottom - target.radius, target.y))
                else:
                    text_effects.append(TextEffect("회피!", target.x - 35, target.y - 55, current_time, (90, 240, 255)))

                grasp.hit_targets.add(target.fighter_id)

    return [grasp for grasp in raven_grasps if grasp.alive]


def update_suin_demon(ball, fighters, current_time, text_effects):
    if ball.character_key != "suin" or not ball.is_alive() or not ball.is_demon:
        return

    elapsed = current_time - ball.demon_start_time

    if current_time - ball.last_demon_tick_time >= SUIN_DEMON_TICK_INTERVAL:
        ball.last_demon_tick_time = current_time

        for target in fighters:
            if target == ball or not target.is_alive():
                continue

            dx = ball.x - target.x
            dy = ball.y - target.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist <= SUIN_DEMON_RADIUS + target.radius:
                dealt = target.take_damage(SUIN_DEMON_TICK_DAMAGE, current_time)

                if dealt:
                    ball.damage_dealt += dealt
                    healed = ball.heal(SUIN_DEMON_HEAL)
                    create_hit_particles(target.x, target.y, current_time, (150, 45, 95), 18, 5)
                    create_hit_particles(ball.x, ball.y, current_time, (100, 20, 60), 10 + healed, 3)
                    text_effects.append(TextEffect("흡수", target.x - 28, target.y - 50, current_time, (210, 80, 140)))

    if elapsed >= SUIN_DEMON_DURATION and not ball.demon_burst_done:
        ball.demon_burst_done = True
        ball.is_demon = False
        text_effects.append(TextEffect("악마 폭발!", ball.x - 70, ball.y - 70, current_time, (220, 70, 130)))
        play_sound("suin_burst")
        create_hit_particles(ball.x, ball.y, current_time, (190, 50, 110), 58, 9)
        add_screen_shake(10)

        for target in fighters:
            if target == ball or not target.is_alive():
                continue

            dx = ball.x - target.x
            dy = ball.y - target.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist <= SUIN_DEMON_RADIUS + 35 + target.radius:
                dealt = target.take_damage(SUIN_DEMON_BURST_DAMAGE, current_time)

                if dealt:
                    ball.damage_dealt += dealt



def update_geonwoo_execute(ball, fighters, current_time, game_state):
    if ball.character_key != "geonwoo" or not ball.is_alive() or ball.geonwoo_execute_done:
        return

    if game_state.get("geonwoo_annihilation") is not None:
        return

    if current_time < ball.geonwoo_execute_ready_time:
        return

    ball.geonwoo_execute_done = True
    play_sound("geonwoo_charge")
    game_state["geonwoo_annihilation"] = {
        "caster": ball,
        "start_time": current_time,
        "explode_time": current_time + GEONWOO_ANNIHILATION_FREEZE_TIME,
        "end_time": current_time + GEONWOO_ANNIHILATION_FREEZE_TIME + GEONWOO_ANNIHILATION_FLASH_TIME,
        "exploded": False,
    }

    game_state["text_effects"].append(
        TextEffect("개발자 권한 로딩...", ball.x - 115, ball.y - 80, current_time, (120, 255, 120))
    )
    create_hit_particles(ball.x, ball.y, current_time, (120, 255, 120), 90, 9)
    add_screen_shake(10)


def update_geonwoo_annihilation(game_state, fighters, current_time):
    effect = game_state.get("geonwoo_annihilation")

    if effect is None:
        return False

    caster = effect["caster"]

    if not effect["exploded"] and current_time >= effect["explode_time"]:
        effect["exploded"] = True
        play_sound("geonwoo_boom")
        game_state["text_effects"].append(
            TextEffect("EXECUTE: 말살", arena.centerx - 85, arena.centery - 35, current_time, (120, 255, 120))
        )
        add_screen_shake(30)

        for target in fighters:
            if target == caster or not target.is_alive():
                continue

            dealt = target.hp
            target.hp = 0
            target.damage_flash_until = current_time + 700
            caster.damage_dealt += dealt

            create_hit_particles(target.x, target.y, current_time, (120, 255, 120), 95, 14)
            create_hit_particles(target.x, target.y, current_time, (255, 255, 255), 38, 10)
            game_state["text_effects"].append(
                TextEffect("펑!", target.x - 25, target.y - 65, current_time, (190, 255, 190))
            )

        create_hit_particles(caster.x, caster.y, current_time, (120, 255, 120), 120, 13)

    if current_time >= effect["end_time"]:
        game_state["geonwoo_annihilation"] = None
        return False

    return True


def draw_geonwoo_annihilation_effect(effect, fighters, current_time):
    if effect is None:
        return

    caster = effect["caster"]
    start_time = effect["start_time"]
    explode_time = effect["explode_time"]
    end_time = effect["end_time"]

    if current_time < explode_time:
        ratio = max(0, min(1, (current_time - start_time) / GEONWOO_ANNIHILATION_FREEZE_TIME))
        overlay_alpha = int(95 + ratio * 65)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 20, 8, overlay_alpha))
        screen.blit(overlay, (0, 0))

        pulse = math.sin(current_time / 80) * 6
        system_text = font.render("SYSTEM FREEZE", True, (120, 255, 120))
        screen.blit(system_text, (WIDTH // 2 - 150, arena.top + 25))

        percent_text = small_font.render(f"말살 준비중... {int(ratio * 100)}%", True, (210, 255, 210))
        screen.blit(percent_text, (WIDTH // 2 - 115, arena.top + 72))

        draw_glow_circle((caster.x, caster.y), 72 + ratio * 78 + pulse, (120, 255, 120), 8, 105)
        draw_glow_circle((caster.x, caster.y), 38 + ratio * 28 - pulse, (255, 255, 255), 4, 90)

        for target in fighters:
            if target == caster or not target.is_alive():
                continue

            draw_glow_line((caster.x, caster.y), (target.x, target.y), (120, 255, 120), 3, 50)
            lock_radius = int(target.radius + 18 + math.sin(current_time / 65) * 4)
            draw_glow_circle((target.x, target.y), lock_radius, (120, 255, 120), 4, 100)
            pygame.draw.line(
                screen,
                (120, 255, 120),
                (int(target.x - lock_radius - 7), int(target.y)),
                (int(target.x + lock_radius + 7), int(target.y)),
                2,
            )
            pygame.draw.line(
                screen,
                (120, 255, 120),
                (int(target.x), int(target.y - lock_radius - 7)),
                (int(target.x), int(target.y + lock_radius + 7)),
                2,
            )

        for _ in range(8):
            block_w = random.randint(35, 110)
            block_h = random.randint(3, 10)
            block_x = random.randint(arena.left, max(arena.left, arena.right - block_w))
            block_y = random.randint(arena.top, arena.bottom)
            glitch = pygame.Surface((block_w, block_h), pygame.SRCALPHA)
            glitch.fill((120, 255, 120, random.randint(35, 90)))
            screen.blit(glitch, (block_x, block_y))

    else:
        ratio = max(0, min(1, (current_time - explode_time) / GEONWOO_ANNIHILATION_FLASH_TIME))
        flash_alpha = int(230 * (1 - ratio))
        flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        flash.fill((210, 255, 210, flash_alpha))
        screen.blit(flash, (0, 0))

        boom_text = font.render("말살 완료", True, (120, 255, 120))
        screen.blit(boom_text, (WIDTH // 2 - 105, arena.top + 35))

        for target in fighters:
            if target == caster:
                continue

            radius = int(30 + ratio * 170)
            alpha = int(155 * (1 - ratio))
            draw_glow_circle((target.x, target.y), radius, (120, 255, 120), 10, alpha)
            draw_glow_circle((target.x, target.y), max(1, radius // 2), (255, 255, 255), 5, alpha)


def update_gunshots(gunshots, fighters, current_time, text_effects):
    for shot in gunshots:
        shot.update()

        for target in fighters:
            if target == shot.caster or not target.is_alive() or target.fighter_id in shot.hit_targets:
                continue

            dx = shot.x - target.x
            dy = shot.y - target.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist <= shot.radius + target.radius:
                dealt = target.take_damage(shot.damage, current_time)

                if dealt:
                    shot.caster.damage_dealt += dealt
                    create_hit_particles(target.x, target.y, current_time, (255, 220, 90), 16, 6)
                    add_screen_shake(4)
                else:
                    text_effects.append(TextEffect("회피!", target.x - 35, target.y - 55, current_time, (90, 240, 255)))

                shot.hit_targets.add(target.fighter_id)
                shot.alive = False
                break

    return [shot for shot in gunshots if shot.alive]


def update_seafood_stews(seafood_stews, heat_zones, current_time, text_effects):
    for stew in seafood_stews:
        landed = stew.update(current_time)

        if landed:
            heat_zones.append(
                HeatZone(
                    stew.caster,
                    stew.target_x,
                    stew.target_y,
                    current_time,
                    stew.is_ultimate,
                )
            )
            text_effects.append(TextEffect("뜨거워!", stew.target_x - 40, stew.target_y - 38, current_time, (255, 150, 75)))
            play_sound("stew_land", 0.38 if stew.is_ultimate else 0.30)
            create_hit_particles(stew.target_x, stew.target_y, current_time, (255, 125, 55), 32 if not stew.is_ultimate else 44, 7)
            add_screen_shake(5 if not stew.is_ultimate else 8)

    return [stew for stew in seafood_stews if stew.alive]


def update_heat_zones(heat_zones, fighters, current_time, text_effects):
    for zone in heat_zones:
        zone.update(current_time)

        if not zone.alive:
            continue

        for target in fighters:
            if target == zone.caster or not target.is_alive():
                continue

            dx = target.x - zone.x
            dy = target.y - zone.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist > zone.radius + target.radius:
                continue

            last_tick = zone.last_tick_by_target.get(target.fighter_id, 0)

            if current_time - last_tick >= zone.tick_interval:
                zone.last_tick_by_target[target.fighter_id] = current_time
                dealt = target.take_damage(zone.damage, current_time)

                if dealt:
                    zone.caster.damage_dealt += dealt
                    create_hit_particles(target.x, target.y, current_time, (255, 110, 55), 12, 4)
                else:
                    text_effects.append(TextEffect("회피!", target.x - 35, target.y - 55, current_time, (90, 240, 255)))

    return [zone for zone in heat_zones if zone.alive]


def update_death_ranking(fighters, game_state, current_time):
    if len(fighters) <= 2:
        return

    death_order = game_state.setdefault("death_order", [])

    for fighter in fighters:
        if fighter.is_alive() or fighter.fighter_id in death_order:
            continue

        death_order.append(fighter.fighter_id)
        rank_from_bottom = len(fighters) - len(death_order) + 1
        game_state["text_effects"].append(
            TextEffect(
                f"{fighter.name} {rank_from_bottom}위 확정",
                fighter.x - 55,
                fighter.y - 78,
                current_time,
                (255, 210, 120),
            )
        )


def get_final_rankings(fighters, game_state):
    if len(fighters) <= 2:
        return []

    fighter_by_id = {fighter.fighter_id: fighter for fighter in fighters}
    death_order = list(game_state.get("death_order", []))
    rankings = []

    alive_fighters = [fighter for fighter in fighters if fighter.is_alive()]
    for fighter in alive_fighters:
        rankings.append(fighter)

    for fighter_id in reversed(death_order):
        fighter = fighter_by_id.get(fighter_id)
        if fighter is not None and fighter not in rankings:
            rankings.append(fighter)

    for fighter in fighters:
        if fighter not in rankings:
            rankings.append(fighter)

    return list(enumerate(rankings, start=1))


def draw_final_rankings(fighters, game_state, panel):
    rankings = get_final_rankings(fighters, game_state)

    if not rankings:
        return

    title_img = small_font.render("최종 순위", True, (255, 230, 90))
    screen.blit(title_img, title_img.get_rect(center=(panel.centerx, panel.y + 118)))

    row_h = 26 if len(rankings) <= 6 else 23
    start_y = panel.y + 146
    row_w = 390
    row_x = panel.centerx - row_w // 2

    for rank, fighter in rankings:
        y = start_y + (rank - 1) * row_h
        row_rect = pygame.Rect(row_x, y, row_w, row_h - 3)
        bg = (48, 48, 56) if rank % 2 == 1 else (39, 39, 47)
        pygame.draw.rect(screen, bg, row_rect, border_radius=7)
        pygame.draw.rect(screen, fighter.color, row_rect, 1, border_radius=7)

        suffix = "WIN" if rank == 1 else "OUT"
        if rank == len(rankings):
            suffix = "꼴등"

        line = f"{rank}위  {fighter.team_label} {fighter.name}  /  데미지 {fighter.damage_dealt}  /  {suffix}"
        text_img = mini_font.render(line, True, (245, 245, 245))
        screen.blit(text_img, (row_rect.x + 12, row_rect.y + 3))

def get_winner_text(fighters):
    alive = [fighter for fighter in fighters if fighter.is_alive()]

    if len(alive) == 1:
        winner = alive[0]
        return f"{winner.team_label} {winner.name} WIN!"

    return "DRAW!"


def draw_dead_markers(fighters):
    for fighter in fighters:
        if fighter.is_alive():
            continue

        pygame.draw.circle(screen, (70, 70, 70), (int(fighter.x), int(fighter.y)), fighter.radius)
        pygame.draw.line(
            screen,
            (230, 230, 230),
            (int(fighter.x - 16), int(fighter.y - 16)),
            (int(fighter.x + 16), int(fighter.y + 16)),
            4,
        )
        pygame.draw.line(
            screen,
            (230, 230, 230),
            (int(fighter.x + 16), int(fighter.y - 16)),
            (int(fighter.x - 16), int(fighter.y + 16)),
            4,
        )


def apply_screen_shake():
    global screen_shake

    if screen_shake <= 0:
        return

    shake_amount = int(screen_shake)
    shake_x = random.randint(-shake_amount, shake_amount)
    shake_y = random.randint(-shake_amount, shake_amount)

    frame = screen.copy()
    screen.fill((20, 20, 20))
    screen.blit(frame, (shake_x, shake_y))

    screen_shake *= 0.86

    if screen_shake < 0.4:
        screen_shake = 0


last_selected_keys = []


def start_new_game(selected_keys=None):
    global particles, screen_shake, last_selected_keys

    particles = []
    screen_shake = 0.0

    if selected_keys is None:
        selected_keys = choose_mode_and_characters()

    last_selected_keys = selected_keys[:]
    fighters = create_match(selected_keys)
    state = reset_match_lists()
    return fighters, state


fighters, game_state = start_new_game()

running = True
game_over = False
winner = ""

while running:
    clock.tick(60)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if handle_sound_options_event(event):
            continue
        if event.type == pygame.QUIT:
            running = False

        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # 즉시 재시작: 메인화면/선택창으로 돌아가지 않고 방금 고른 캐릭터 그대로 새 경기 시작
                fighters, game_state = start_new_game(last_selected_keys)
                game_over = False
                winner = ""

            if event.key == pygame.K_m:
                # 캐릭터나 모드를 바꾸고 싶을 때만 메인화면으로 돌아가기
                fighters, game_state = start_new_game()
                game_over = False
                winner = ""

            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                running = False

    if not game_over:
        annihilation_active = game_state.get("geonwoo_annihilation") is not None

        if annihilation_active:
            update_geonwoo_annihilation(game_state, fighters, current_time)
        else:
            for fighter in fighters:
                fighter.move(current_time)
                update_jaemin_awaken(fighter, current_time, game_state["text_effects"])
                update_minje_trickster(fighter, current_time, fighters, game_state["text_effects"])
                update_suin_demon(fighter, fighters, current_time, game_state["text_effects"])
                update_geonwoo_execute(fighter, fighters, current_time, game_state)

                if game_state.get("geonwoo_annihilation") is not None:
                    break

        if not annihilation_active and game_state.get("geonwoo_annihilation") is None:
            apply_body_collisions(fighters, current_time, game_state["body_hit_times"])

            for fighter in fighters:
                use_character_skills(
                    fighter,
                    fighters,
                    current_time,
                    game_state["lasers"],
                    game_state["auras"],
                    game_state["global_auras"],
                    game_state["slashes"],
                    game_state["moon_slashes"],
                    game_state["cow_charges"],
                    game_state["raven_grasps"],
                    game_state["gunshots"],
                    game_state["seafood_stews"],
                    game_state["text_effects"],
                )

            game_state["lasers"] = update_lasers(game_state["lasers"], current_time, game_state["text_effects"])
            game_state["auras"] = update_auras(game_state["auras"], fighters, current_time)
            game_state["global_auras"] = update_global_auras(game_state["global_auras"], fighters, current_time)
            game_state["slashes"] = update_slashes(game_state["slashes"], current_time, game_state["text_effects"])
            game_state["moon_slashes"] = update_moon_slashes(
                game_state["moon_slashes"],
                fighters,
                current_time,
                game_state["text_effects"],
            )
            game_state["cow_charges"] = update_cow_charges(
                game_state["cow_charges"],
                fighters,
                current_time,
                game_state["text_effects"],
            )
            game_state["raven_grasps"] = update_raven_grasps(
                game_state["raven_grasps"],
                fighters,
                current_time,
                game_state["text_effects"],
            )
            game_state["gunshots"] = update_gunshots(
                game_state["gunshots"],
                fighters,
                current_time,
                game_state["text_effects"],
            )
            game_state["seafood_stews"] = update_seafood_stews(
                game_state["seafood_stews"],
                game_state["heat_zones"],
                current_time,
                game_state["text_effects"],
            )
            game_state["heat_zones"] = update_heat_zones(
                game_state["heat_zones"],
                fighters,
                current_time,
                game_state["text_effects"],
            )

        update_death_ranking(fighters, game_state, current_time)

        if game_state.get("geonwoo_annihilation") is None:
            alive_count = len([fighter for fighter in fighters if fighter.is_alive()])

            if alive_count <= 1:
                game_over = True
                winner = get_winner_text(fighters)

    screen.fill((20, 20, 20))

    draw_compact_status_panels(fighters, current_time)
    pygame.draw.rect(screen, (220, 220, 220), arena, 4)
    draw_damage_graph(fighters)

    for heat_zone in game_state["heat_zones"]:
        heat_zone.draw(current_time)

    for global_aura in game_state["global_auras"]:
        global_aura.draw(current_time)

    for cow in game_state["cow_charges"]:
        cow.draw()

    for grasp in game_state["raven_grasps"]:
        grasp.draw(current_time)

    for stew in game_state["seafood_stews"]:
        stew.draw(current_time)

    for shot in game_state["gunshots"]:
        shot.draw()

    for moon_slash in game_state["moon_slashes"]:
        moon_slash.draw()

    for laser in game_state["lasers"]:
        laser.draw()

    for aura in game_state["auras"]:
        aura.draw(current_time)

    for slash in game_state["slashes"]:
        slash.draw()

    for fighter in fighters:
        if fighter.character_key == "jaemin" and fighter.is_awakened and fighter.is_alive():
            draw_awaken_aura(fighter, current_time)

    for fighter in fighters:
        fighter.draw(current_time)

    draw_geonwoo_annihilation_effect(game_state.get("geonwoo_annihilation"), fighters, current_time)

    draw_dead_markers(fighters)

    for particle in particles:
        particle.update()
        particle.draw()

    particles = [particle for particle in particles if particle.alive]

    for text in game_state["text_effects"]:
        text.draw(current_time)

    game_state["text_effects"] = [text for text in game_state["text_effects"] if text.alive]

    if game_over:
        draw_game_over_screen(winner, fighters, game_state)

    apply_screen_shake()
    draw_sound_options_ui()
    pygame.display.flip()

pygame.quit()
