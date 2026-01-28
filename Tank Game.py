# main.py

import os
import sys
import math
import json
import random
import time
import struct
import traceback
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Set

import pygame
from pygame.math import Vector2

# =========================================================
# SETTINGS / CONSTANTS
# =========================================================
WIDTH, HEIGHT = 1100, 650
TITLE = "Tank Game v1.7.3"
FPS_CAP = 144

RECOIL_MULT = 1.0 # Default = 1       (Recoil multiplier)
                  # Off = 0
SAVE_PATH = "save.json"
LEADERBOARD_LIMIT = 10

COINS_SCORE_DIV = 50
COINS_PER_WAVE = 4

ARENA_W, ARENA_H = 3000, 3000
BG_GRID_SIZE = 90

DAILY_WHEEL_COOLDOWN = 24 * 60 * 60
DAILY_WHEEL_FALLBACK_TANK_COINS = 100
DAILY_WHEEL_FALLBACK_META_COINS = 50
DAILY_WHEEL_FALLBACK_WINDSCREEN_COINS = 150
DAILY_WHEEL_REWARDS = [
    {"id": "coins_50", "label": "50 COINS", "short": "50", "weight": 18, "kind": "coins", "amount": 50},
    {"id": "coins_100", "label": "100 COINS", "short": "100", "weight": 14, "kind": "coins", "amount": 100},
    {"id": "coins_20", "label": "20 COINS", "short": "20", "weight": 20, "kind": "coins", "amount": 20},
    {"id": "random_tank", "label": "RANDOM TANK", "short": "TANK", "weight": 10, "kind": "tank"},
    {"id": "coins_10", "label": "10 COINS", "short": "10", "weight": 22, "kind": "coins", "amount": 10},
    {"id": "random_meta", "label": "META UPGRADE", "short": "META", "weight": 10, "kind": "meta"},
    {"id": "windscreen", "label": "WINDSCREEN WIPER", "short": "WIPER", "weight": 1, "kind": "windscreen"},
    {"id": "coins_300", "label": "300 COINS", "short": "300", "weight": 5, "kind": "coins", "amount": 300},
]
DAILY_WHEEL_META_UPGRADES = [
    {"id": "meta_damage", "name": "Damage +5%", "max": 10},
    {"id": "meta_move", "name": "Move Speed +5%", "max": 10},
    {"id": "meta_hp", "name": "Max HP +1", "max": 5},
    {"id": "meta_xp", "name": "XP Gain +5%", "max": 10},
    {"id": "meta_dash", "name": "Dash Cooldown -5%", "max": 10},
    {"id": "meta_armor", "name": "Damage Resistance +10%", "max": 10},
    {"id": "meta_bulletspeed", "name": "Bullet Speed +5%", "max": 10},
]

OBSTACLE_COUNT = 22
OBSTACLE_MIN = (80, 60)
OBSTACLE_MAX = (220, 180)

# Colors
C_BG = (8, 10, 16)
C_GRID = (15, 20, 35)
C_PANEL = (14, 16, 24)
C_PANEL_2 = (20, 24, 38)
C_TEXT = (230, 240, 255)
C_TEXT_DIM = (160, 175, 205)
C_ACCENT = (80, 245, 210)
C_ACCENT_2 = (255, 70, 170)
C_WARN = (255, 210, 80)
C_OK = (120, 255, 160)

C_PLAYER = (90, 255, 220)      # Cyan
C_PLAYER_ALT = (120, 180, 255)
C_CHASER = (255, 80, 150)      # Pink
C_RANGED = (120, 190, 255)     # Light Blue
C_TANK = (255, 190, 80)        # Orange/Yellow
C_SPRINTER = (160, 255, 120)   # Lime Green
C_DASHER = (210, 160, 255)     # Purple

C_BOSS = (255, 85, 95)         # Red
C_BOSS_EDGE = (255, 190, 210)
C_ELITE_OUTLINE = (255, 235, 120)

C_BULLET = (240, 240, 255)
C_EBULLET = (255, 120, 90)
C_XP = (120, 255, 160)
C_HEALTH = (255, 90, 110)
C_WALL = (26, 28, 42)
C_WALL_EDGE = (70, 80, 120)
C_COIN = (255, 220, 120)

# Cosmetic palette
C_OUTLINE_NEON = (120, 255, 210)
C_OUTLINE_EMBER = (255, 170, 90)
C_OUTLINE_STEEL = (180, 200, 230)
C_BULLET_MINT = (120, 255, 210)
C_BULLET_VIOLET = (200, 140, 255)
C_BULLET_GOLD = (255, 215, 120)
C_TRAIL_SPARK = (255, 200, 140)
C_TRAIL_ION = (120, 200, 255)
C_EXPLOSION_PLASMA = (120, 200, 255)
C_EXPLOSION_MAGMA = (255, 140, 90)

PLAYER_RADIUS = 16
ENEMY_RADIUS_CHASER = 14
ENEMY_RADIUS_RANGED = 15
ENEMY_RADIUS_TANK = 20
ENEMY_RADIUS_SPRINTER = 11
ENEMY_RADIUS_DASHER = 16
ENEMY_RADIUS_KNIGHT = 24

BULLET_RADIUS_PLAYER = 4
BULLET_RADIUS_ENEMY = 4

PLAYER_ACCEL = 2100.0
PLAYER_FRICTION = 10.5
PLAYER_MAX_SPEED_BASE = 360.0

PLAYER_MAX_HP_BASE = 7
PLAYER_IFRAMES = 0.70

DASH_SPEED = 1000.0
DASH_TIME_BASE = 0.16
DASH_COOLDOWN_BASE = 1.15

WAVE_TIME_BASE = 15 # Originally 18, now 15    (Wave time)

# Difficulty ramping: reduced by ~30% (slower) by increasing the ramp time
DIFFICULTY_RAMP_TIME = 400.0 # 400s to reach "hard" instead of 180s

CHASER_SPEED_BASE, CHASER_SPEED_HARD = 140.0, 300.0
RANGED_SPEED_BASE, RANGED_SPEED_HARD = 110.0, 240.0
TANK_SPEED_BASE, TANK_SPEED_HARD = 75.0, 160.0
SPRINTER_SPEED_BASE, SPRINTER_SPEED_HARD = 175.0, 360.0
DASHER_SPEED_BASE, DASHER_SPEED_HARD = 115.0, 255.0
KNIGHT_SPEED_BASE, KNIGHT_SPEED_HARD = 45.0, 90.0

SPAWN_RATE_BASE = 1.35
SPAWN_RATE_HARD = 0.9
SPAWN_RATE_WAVE_BONUS = 0.008

ENEMY_HP_BASE_MUL = 1.0
ENEMY_HP_HARD_MUL = 1.3

ENEMY_CAP_BASE = 7
ENEMY_CAP_HARD = 20

RANGED_MAX_SHOOT_DIST = 520.0
RANGED_SHOOT_IF_ONSCREEN_MARGIN = 60
RANGED_LOS_ENABLED = True

RANGED_BULLET_SPEED_BASE = 470.0
RANGED_BULLET_LIFETIME = 1.55
RANGED_DAMAGE_BASE = 1
RANGED_DAMAGE_HARD = 2

RANGED_COOLDOWN_MIN = 1.10
RANGED_COOLDOWN_MAX = 1.55

XP_ORB_VALUE_BASE = 12
XP_ORB_RADIUS = 8
HEALTH_PACK_AMOUNT = 1
HEALTH_PACK_RADIUS = 10

PICKUP_ATTRACT_FORCE = 900.0
PICKUP_ATTRACT_DIST_BASE = 190.0

POWERUP_SPAWN_MIN = 20.0
POWERUP_SPAWN_MAX = 34.0
POWERUP_MAX_ON_MAP = 2
POWERUP_RADIUS = 12

POWERUP_DURATION_DAMAGE = 10.0
POWERUP_DURATION_RAPID = 8.0
POWERUP_DURATION_SPEED = 10.0
POWERUP_DURATION_SHIELD = 6.0

UI_PAD = 16

UPGRADE_BOX_PADDING = 18
UPGRADE_LINE_SPACING = 6
UPGRADE_RIGHT_LABEL_WIDTH = 160

HIT_PARTICLE_COUNT = 10
PARTICLE_LIFE = 0.35
SHAKE_HIT = 10.0
SHAKE_DECAY = 24.0

PLAYER_ENEMY_MIN_DIST_EPS = 1.0
PLAYER_ENEMY_PUSH_STRENGTH = 1.0
ENEMY_SEPARATION_CELL = 120
ENEMY_SEPARATION_SOFT = 1.15
ENEMY_SEPARATION_FORCE = 2.2

AUDIO_ENABLED_DEFAULT = True

# Boss rules
BOSS_EVERY_WAVES = 10
BOSS_GRACE_AFTER_DEATH = 3  # seconds where normal spawning is paused after boss dies

# Late-game modifiers
LATE_GAME_START_WAVE = 20
MID_LATE_START_WAVE = 25
LATE_LATE_START_WAVE = 35
MODIFIER_WAVE_MIN = 2
MODIFIER_WAVE_MAX = 3
MODIFIER_MIN_STACK = 2
MODIFIER_MAX_STACK = 3

# =========================================================
# STORY MODE CONFIG
# =========================================================
LEVELS = [
    {
        "id": 1,
        "name": "Outskirts Run",
        "objective": "Survive 35 seconds.",
        "win": {"type": "survive", "seconds": 35},
        "arena_size": (2400, 2400),
        "obstacles": {"count": 14, "min": (90, 70), "max": (200, 160)},
        "spawn": {"interval": 1.25, "cap": 8},
        "enemy_weights": {"chaser": 0.7, "sprinter": 0.3},
        "special": {},
        "difficulty": 0.25,
    },
    {
        "id": 2,
        "name": "Lockdown Lanes",
        "objective": "Eliminate 25 enemies. (Pistol-only)",
        "win": {"type": "kills", "count": 25},
        "arena_size": (2000, 1300),
        "obstacles": {"count": 26, "min": (80, 80), "max": (220, 180)},
        "spawn": {"interval": 1.1, "cap": 10},
        "enemy_weights": {"chaser": 0.55, "ranged": 0.25, "sprinter": 0.2},
        "special": {"forced_weapon": "pistol"},
        "difficulty": 0.175,
    },
    {
        "id": 3,
        "name": "Nightglass",
        "objective": "Survive 45 seconds in the dark.",
        "win": {"type": "survive", "seconds": 45},
        "arena_size": (2300, 2300),
        "obstacles": {"count": 18, "min": (90, 70), "max": (210, 170)},
        "spawn": {"interval": 1.05, "cap": 11},
        "enemy_weights": {"chaser": 0.4, "ranged": 0.4, "sprinter": 0.2},
        "special": {"visibility_radius": 260},
        "difficulty": 0.21,
    },
    {
        "id": 4,
        "name": "Beacon Hold",
        "objective": "Defend the beacon for 30 seconds.",
        "win": {"type": "defend", "seconds": 30, "radius": 150},
        "arena_size": (2200, 2000),
        "obstacles": {"count": 20, "min": (90, 70), "max": (200, 150)},
        "spawn": {"interval": 1.05, "cap": 12},
        "enemy_weights": {"chaser": 0.55, "tank": 0.25, "sprinter": 0.2},
        "special": {"objective_point": "center", "beacon_hp": 25},
        "difficulty": 0.25,
    },
    {
        "id": 5,
        "name": "Static Fields",
        "objective": "Reach 50 kills while avoiding hazard zones.",
        "win": {"type": "kills", "count": 50},
        "arena_size": (2500, 2100),
        "obstacles": {"count": 16, "min": (100, 80), "max": (240, 190)},
        "spawn": {"interval": 0.95, "cap": 13},
        "enemy_weights": {"chaser": 0.35, "ranged": 0.35, "sprinter": 0.15, "dasher": 0.15},
        "special": {
            "hazard_count": 4,
            "hazard_sizes": [(320, 520), (320, 360)],
            "hazard_dps": [1.0, 1.2],
        },
        "difficulty": 0.3,
    },
    {
        "id": 6,
        "name": "Overclocked Core",
        "objective": "Defeat the Overlord.",
        "win": {"type": "boss", "spawn_after": 0},
        "arena_size": (2200, 2200),
        "obstacles": {"count": 10, "min": (120, 90), "max": (220, 180)},
        "spawn": {"interval": 1.4, "cap": 6},
        "enemy_weights": {"chaser": 0.4, "ranged": 0.4, "tank": 0.2},
        "special": {},
        "difficulty": 0.7,
    },
]


# =========================================================
# HELPERS
# =========================================================
def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(t: float) -> float:
    t = clamp(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def weighted_choice(weights: Dict[str, float]) -> str:
    total = sum(max(0.0, v) for v in weights.values())
    if total <= 0:
        return random.choice(list(weights.keys()))
    r = random.uniform(0.0, total)
    upto = 0.0
    for k, v in weights.items():
        w = max(0.0, v)
        upto += w
        if r <= upto:
            return k
    return list(weights.keys())[-1]


def draw_text(surf, font, text, pos, color=C_TEXT, center=False, shadow=True):
    img = font.render(text, True, color)
    r = img.get_rect()
    if center:
        r.center = pos
    else:
        r.topleft = pos
    if shadow:
        sh = font.render(text, True, (0, 0, 0))
        sh_r = sh.get_rect(center=r.center) if center else sh.get_rect(topleft=(r.x + 2, r.y + 2))
        surf.blit(sh, sh_r)
    surf.blit(img, r)
    return r


def clamp_text(font, text, max_width):
    if font.size(text)[0] <= max_width:
        return text
    ellipsis = "..."
    ellipsis_w = font.size(ellipsis)[0]
    if ellipsis_w >= max_width:
        return ellipsis
    trimmed = text
    target_w = max_width - ellipsis_w
    while trimmed and font.size(trimmed)[0] > target_w:
        trimmed = trimmed[:-1]
    return f"{trimmed}{ellipsis}"


def circle_outline(surf, color, pos, radius, width=2):
    pygame.draw.circle(surf, color, (int(pos[0]), int(pos[1])), int(radius), int(width))


def load_optional_sound(path: str):
    try:
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
    except Exception:
        pass
    return None


def generate_tone_sound(freq=440.0, duration=0.08, volume=0.25, sample_rate=44100):
    try:
        if not pygame.mixer.get_init():
            return None
        n = int(sample_rate * duration)
        buf = bytearray()
        amp = int(32767 * volume)
        two_pi = 2.0 * math.pi
        for i in range(n):
            t = i / sample_rate
            s = int(math.sin(two_pi * freq * t) * amp)
            buf += struct.pack("<h", s)
        return pygame.mixer.Sound(buffer=bytes(buf))
    except Exception:
        return None


def rect_centered_text(surf, font, text, rect: pygame.Rect, color, shadow=True):
    img = font.render(text, True, color)
    r = img.get_rect()
    r.center = rect.center
    if shadow:
        sh = font.render(text, True, (0, 0, 0))
        sh_r = sh.get_rect(center=(r.centerx + 2, r.centery + 2))
        surf.blit(sh, sh_r)
    surf.blit(img, r)


def clamp_to_screen_edge(pt: Vector2, margin: int = 10) -> Vector2:
    return Vector2(clamp(pt.x, margin, WIDTH - margin), clamp(pt.y, margin, HEIGHT - margin))


# =========================================================
# SAVE
# =========================================================
class SaveManager:
    def __init__(self, path: str):
        self.path = path
        self.coins: int = 0
        self.shop_levels: Dict[str, int] = {}
        self.weapon_unlocks: Dict[str, bool] = {}
        self.selected_weapon: str = "pistol"
        self.cosmetic_outline_alt: bool = False
        self.bundles_purchased: Dict[str, bool] = {}
        self.cosmetics_unlocked: Dict[str, bool] = {}
        self.cosmetics_equipped: Dict[str, str] = {}
        self.daily_challenges: Dict[str, object] = {}
        self.weekly_challenges: Dict[str, object] = {}
        self.weapon_mastery: Dict[str, Dict[str, int]] = {}
        self.settings: Dict[str, bool] = {"audio": True, "shake": True}
        self.leaderboard: List[Dict[str, int]] = []
        self.story_unlocked_level: int = 1
        self.story_last_level: int = 1
        self.last_spin_timestamp: int = 0
        self.load()

    def defaults(self):
        self.coins = 0
        self.shop_levels = {
            "meta_damage": 0,
            "meta_move": 0,
            "meta_hp": 0,
            "meta_xp": 0,
            "meta_dash": 0,
            "meta_armor": 0,
            "meta_bulletspeed": 0,
        }
        # NOTE: weapon ids are synced against WEAPONS later (future-proof)
        self.weapon_unlocks = {"pistol": True}
        self.selected_weapon = "pistol"
        self.cosmetic_outline_alt = False
        self.bundles_purchased = {}
        self.cosmetics_unlocked = {}
        self.cosmetics_equipped = {}
        self.daily_challenges = {}
        self.weekly_challenges = {}
        self.weapon_mastery = {}
        self.settings = {"audio": True, "shake": True}
        self.leaderboard = []
        self.story_unlocked_level = 1
        self.story_last_level = 1
        self.last_spin_timestamp = 0

    def ensure_weapons(self, weapon_ids: List[str]) -> bool:
        """Future-proof: ensure save file contains keys for every weapon in WEAPONS."""
        changed = False
        if "pistol" not in self.weapon_unlocks:
            self.weapon_unlocks["pistol"] = True
            changed = True

        for wid in weapon_ids:
            if wid not in self.weapon_unlocks:
                self.weapon_unlocks[wid] = (wid == "pistol")
                changed = True

        # If selected weapon isn't unlocked, fallback.
        if not self.weapon_unlocks.get(self.selected_weapon, False):
            self.selected_weapon = "pistol"
            changed = True

        return changed

    def ensure_cosmetics(self, cosmetics: List["CosmeticDef"]) -> bool:
        changed = False
        if not self.cosmetics_equipped:
            self.cosmetics_equipped = dict(DEFAULT_COSMETICS)
            changed = True
        for category, cid in DEFAULT_COSMETICS.items():
            if category not in self.cosmetics_equipped:
                self.cosmetics_equipped[category] = cid
                changed = True

        for cosmetic in cosmetics:
            if cosmetic.id not in self.cosmetics_unlocked:
                self.cosmetics_unlocked[cosmetic.id] = bool(cosmetic.default)
                changed = True

        for category, default_id in DEFAULT_COSMETICS.items():
            equipped_id = self.cosmetics_equipped.get(category, default_id)
            if equipped_id not in self.cosmetics_unlocked:
                self.cosmetics_equipped[category] = default_id
                equipped_id = default_id
                changed = True
            if not self.cosmetics_unlocked.get(equipped_id, False):
                self.cosmetics_unlocked[equipped_id] = True
                changed = True

        if self.cosmetic_outline_alt:
            if "outline_neon" in self.cosmetics_unlocked:
                if not self.cosmetics_unlocked.get("outline_neon"):
                    self.cosmetics_unlocked["outline_neon"] = True
                    changed = True
                self.cosmetics_equipped["outline"] = "outline_neon"
                changed = True

        return changed

    def ensure_mastery(self, weapon_ids: List[str]) -> bool:
        changed = False
        for wid in weapon_ids:
            _, entry_changed = self.ensure_mastery_entry(wid)
            if entry_changed:
                changed = True
        return changed

    def ensure_mastery_entry(self, weapon_id: str) -> Tuple[Dict[str, int], bool]:
        changed = False
        if weapon_id not in self.weapon_mastery or not isinstance(self.weapon_mastery.get(weapon_id), dict):
            self.weapon_mastery[weapon_id] = {}
            changed = True
        stats = self.weapon_mastery[weapon_id]
        if "level" not in stats:
            stats["level"] = 0
            changed = True
        if "hits" not in stats:
            stats["hits"] = 0
            changed = True
        if "total_kills" not in stats:
            stats["total_kills"] = int(stats.get("kills", 0))
            changed = True
        if "total_wins" not in stats:
            stats["total_wins"] = int(stats.get("games", 0))
            changed = True
        if "level_kills" not in stats:
            stats["level_kills"] = 0
            changed = True
        if "level_wins" not in stats:
            stats["level_wins"] = 0
            changed = True
        req_level = min(int(stats.get("level", 0)) + 1, MAX_MASTERY_LEVEL)
        req_kills, req_wins = mastery_requirements(req_level)
        if "req_kills" not in stats:
            stats["req_kills"] = req_kills
            changed = True
        if "req_wins" not in stats:
            stats["req_wins"] = req_wins
            changed = True
        return stats, changed

    def load(self):
        self.defaults()
        try:
            if not os.path.exists(self.path):
                return
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.coins = int(data.get("coins", 0))
            self.shop_levels = dict(data.get("shop_levels", self.shop_levels))
            self.weapon_unlocks = dict(data.get("weapon_unlocks", self.weapon_unlocks))
            self.selected_weapon = str(data.get("selected_weapon", self.selected_weapon))
            self.cosmetic_outline_alt = bool(data.get("cosmetic_outline_alt", False))
            self.bundles_purchased = dict(data.get("bundles_purchased", {}))
            self.cosmetics_unlocked = dict(data.get("cosmetics_unlocked", {}))
            self.cosmetics_equipped = dict(data.get("cosmetics_equipped", {}))
            self.daily_challenges = dict(data.get("daily_challenges", {}))
            self.weekly_challenges = dict(data.get("weekly_challenges", {}))
            self.weapon_mastery = dict(data.get("weapon_mastery", {}))
            self.settings = dict(data.get("settings", self.settings))
            self.leaderboard = list(data.get("leaderboard", []))
            self.story_unlocked_level = int(data.get("story_unlocked_level", 1))
            self.story_last_level = int(data.get("story_last_level", self.story_unlocked_level))
            spin_ts = data.get("last_spin_timestamp", data.get("last_daily_spin_ts", 0))
            self.last_spin_timestamp = int(spin_ts)

            for k in ["meta_damage", "meta_move", "meta_hp", "meta_xp", "meta_dash", "meta_armor", "meta_bulletspeed"]:
                if k not in self.shop_levels:
                    self.shop_levels[k] = 0

            if "audio" not in self.settings:
                self.settings["audio"] = True
            if "shake" not in self.settings:
                self.settings["shake"] = True

            if self.story_unlocked_level < 1:
                self.story_unlocked_level = 1
            if self.story_last_level < 1:
                self.story_last_level = self.story_unlocked_level
            max_story = max(1, len(LEVELS))
            if self.story_unlocked_level > max_story:
                self.story_unlocked_level = max_story
            if self.last_spin_timestamp < 0:
                self.last_spin_timestamp = 0
            if self.story_last_level > max_story:
                self.story_last_level = self.story_unlocked_level

            if "pistol" not in self.weapon_unlocks:
                self.weapon_unlocks["pistol"] = True

            if not self.weapon_unlocks.get(self.selected_weapon, False):
                self.selected_weapon = "pistol"

            if not isinstance(self.bundles_purchased, dict):
                self.bundles_purchased = {}
            if not isinstance(self.cosmetics_unlocked, dict):
                self.cosmetics_unlocked = {}
            if not isinstance(self.cosmetics_equipped, dict):
                self.cosmetics_equipped = {}
            if not isinstance(self.daily_challenges, dict):
                self.daily_challenges = {}
            if not isinstance(self.weekly_challenges, dict):
                self.weekly_challenges = {}
            if not isinstance(self.weapon_mastery, dict):
                self.weapon_mastery = {}

            self.leaderboard = [
                e for e in self.leaderboard
                if isinstance(e, dict)
                and "score" in e
                and "time" in e
                and "wave" in e
                and "level" in e
            ]
            self.leaderboard.sort(key=lambda e: (e["score"], e["wave"], e["time"]), reverse=True)
            self.leaderboard = self.leaderboard[:LEADERBOARD_LIMIT]
        except Exception:
            self.defaults()

    def save(self):
        try:
            data = {
                "coins": int(self.coins),
                "shop_levels": self.shop_levels,
                "weapon_unlocks": self.weapon_unlocks,
                "selected_weapon": self.selected_weapon,
                "cosmetic_outline_alt": bool(self.cosmetic_outline_alt),
                "bundles_purchased": self.bundles_purchased,
                "cosmetics_unlocked": self.cosmetics_unlocked,
                "cosmetics_equipped": self.cosmetics_equipped,
                "daily_challenges": self.daily_challenges,
                "weekly_challenges": self.weekly_challenges,
                "weapon_mastery": self.weapon_mastery,
                "settings": self.settings,
                "leaderboard": self.leaderboard,
                "story_unlocked_level": int(self.story_unlocked_level),
                "story_last_level": int(self.story_last_level),
                "last_spin_timestamp": int(self.last_spin_timestamp),
            }
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def add_leaderboard_entry(self, score: int, time_s: int, wave: int, level: int):
        entry = {
            "score": int(score),
            "time": int(time_s),
            "wave": int(wave),
            "level": int(level),
        }
        self.leaderboard.append(entry)
        self.leaderboard = [
            e for e in self.leaderboard
            if isinstance(e, dict)
            and "score" in e
            and "time" in e
            and "wave" in e
            and "level" in e
        ]
        self.leaderboard.sort(key=lambda e: (e["score"], e["wave"], e["time"]), reverse=True)
        self.leaderboard = self.leaderboard[:LEADERBOARD_LIMIT]


# =========================================================
# UI COMPONENTS
# =========================================================
class Button:
    def __init__(self, rect: pygame.Rect, text: str, callback, hotkey=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.hotkey = hotkey
        self.hover = False
        self.pulse = 0.0
        self.enabled = True

    def update(self, dt, mouse_pos, mouse_down, events):
        self.hover = self.enabled and self.rect.collidepoint(mouse_pos)
        self.pulse = (self.pulse + dt * 3.0) % (math.tau)

        clicked = False
        if self.hover and mouse_down:
            clicked = True

        for e in events:
            if e.type == pygame.KEYDOWN and self.hotkey and e.key == self.hotkey:
                clicked = True

        if clicked and self.enabled:
            self.callback()

    def draw(self, surf, font, alpha=255):
        base = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        bg = (*C_PANEL_2, alpha) if self.enabled else (*C_PANEL_2, int(alpha * 0.55))
        edge = (*C_ACCENT, alpha) if self.hover else (*C_WALL_EDGE, alpha)

        base.fill(bg)
        pygame.draw.rect(base, edge, base.get_rect(), 2, border_radius=10)

        strip_col = (*C_ACCENT_2, int(alpha * (0.55 if self.hover else 0.22)))
        pygame.draw.rect(base, strip_col, pygame.Rect(0, 0, 8, self.rect.height), border_radius=10)

        if self.hover:
            glow = int(26 + 18 * math.sin(self.pulse))
            pygame.draw.rect(base, (*C_ACCENT, min(alpha, glow)), base.get_rect(), 6, border_radius=12)

        surf.blit(base, self.rect.topleft)

        txt_col = C_TEXT if self.enabled else (120, 130, 155)
        draw_text(surf, font, self.text, self.rect.center, txt_col, center=True, shadow=True)


class TabButton:
    """Small tab-like button for Shop navigation."""
    def __init__(self, rect: pygame.Rect, text: str, on_click, tab_id: str):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.on_click = on_click
        self.tab_id = tab_id
        self.hover = False

    def update(self, mouse_pos, mouse_down):
        self.hover = self.rect.collidepoint(mouse_pos)
        if self.hover and mouse_down:
            self.on_click(self.tab_id)

    def draw(self, surf, font, active=False):
        bg = (*C_PANEL_2, 245) if active else (*C_PANEL, 220)
        edge = C_ACCENT if active else (C_WALL_EDGE if not self.hover else C_ACCENT)
        pygame.draw.rect(surf, bg, self.rect, border_radius=12)
        pygame.draw.rect(surf, edge, self.rect, 2, border_radius=12)
        rect_centered_text(surf, font, self.text, self.rect, C_TEXT if active else C_TEXT_DIM, shadow=False)


# =========================================================
# EFFECTS
# =========================================================
class Particle:
    def __init__(self, pos: Vector2, vel: Vector2, color: Tuple[int, int, int], life=PARTICLE_LIFE, radius=2):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.color = color
        self.life = life
        self.life_max = life
        self.radius = radius

    def update(self, dt):
        self.life -= dt
        self.pos += self.vel * dt
        self.vel *= (1.0 - min(dt * 4.5, 0.35))

    def draw(self, surf, cam):
        if self.life <= 0:
            return
        t = clamp(self.life / self.life_max, 0, 1)
        a = int(220 * t)
        rr = max(1, int(self.radius * (0.7 + 0.6 * t)))
        pygame.draw.circle(surf, (*self.color, a), (int(self.pos.x - cam.x), int(self.pos.y - cam.y)), rr)


class FloatingText:
    def __init__(self, pos: Vector2, text: str, color=C_WARN, life=0.65):
        self.pos = Vector2(pos)
        self.text = text
        self.color = color
        self.life = life
        self.life_max = life
        self.vel = Vector2(random.uniform(-30, 30), random.uniform(-90, -55))

    def update(self, dt):
        self.life -= dt
        self.pos += self.vel * dt
        self.vel.y -= 55 * dt

    def draw(self, surf, cam, font):
        if self.life <= 0:
            return
        t = clamp(self.life / self.life_max, 0, 1)
        a = int(255 * t)
        img = font.render(self.text, True, self.color)
        img.set_alpha(a)
        surf.blit(img, (self.pos.x - cam.x, self.pos.y - cam.y))


# =========================================================
# PROJECTILES / PICKUPS
# =========================================================
class Projectile:
    def __init__(
        self,
        pos: Vector2,
        vel: Vector2,
        damage: int,
        owner: str,
        color,
        radius=4,
        lifetime=1.0,
        pierce=0,
        splash_radius=0.0,  # for rocket
    ):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.damage = damage
        self.owner = owner
        self.color = color
        self.radius = radius
        self.life = lifetime
        self.pierce = pierce
        self.hit_set = set()
        self.splash_radius = splash_radius

    def update(self, dt):
        self.life -= dt
        self.pos += self.vel * dt

    def draw(self, surf, cam):
        p = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surf, self.color, p, self.radius)
        circle_outline(surf, self.color, p, self.radius + 3, 1)

    def alive(self):
        return self.life > 0


class Pickup:
    def __init__(self, pos: Vector2, kind: str, value: int = 0, power_type: str = ""):
        self.pos = Vector2(pos)
        self.kind = kind  # "xp" | "health" | "power"
        self.value = value
        self.power_type = power_type
        self.vel = Vector2(0, 0)

    def radius(self):
        if self.kind == "xp":
            return XP_ORB_RADIUS
        if self.kind == "health":
            return HEALTH_PACK_RADIUS
        return POWERUP_RADIUS

    def draw(self, surf, cam, t_seconds: float):
        screen_p = Vector2(self.pos.x - cam.x, self.pos.y - cam.y)
        p = (int(screen_p.x), int(screen_p.y))
        pulse = 1.0 + 0.10 * math.sin(t_seconds * 5.0 + (self.pos.x + self.pos.y) * 0.01)

        if self.kind == "xp":
            r = int(XP_ORB_RADIUS * pulse)
            pygame.draw.circle(surf, C_XP, p, r)
            circle_outline(surf, (60, 220, 140), p, r + 3, 2)
        elif self.kind == "health":
            r = int(HEALTH_PACK_RADIUS * pulse)
            pygame.draw.circle(surf, C_HEALTH, p, r)
            circle_outline(surf, (255, 160, 190), p, r + 3, 2)
            pygame.draw.rect(surf, (255, 240, 245), pygame.Rect(p[0] - 2, p[1] - 7, 4, 14))
            pygame.draw.rect(surf, (255, 240, 245), pygame.Rect(p[0] - 7, p[1] - 2, 14, 4))
        else:
            col = {
                "damage_boost": (255, 120, 220),
                "rapid_fire": (120, 255, 240),
                "speed_boost": (140, 255, 160),
                "shield": (200, 200, 255),
            }.get(self.power_type, (255, 255, 255))
            r = int(POWERUP_RADIUS * pulse)
            pts = [(p[0], p[1] - r), (p[0] + r, p[1]), (p[0], p[1] + r), (p[0] - r, p[1])]
            pygame.draw.polygon(surf, col, pts)
            pygame.draw.polygon(surf, (20, 20, 30), pts, 2)


# =========================================================
# WEAPONS (Tanks)
# =========================================================
@dataclass
class WeaponDef:
    id: str
    name: str
    desc: str
    base_damage: int
    fire_cd: float
    bullet_speed: float
    bullet_life: float
    bullets_per_shot: int = 1
    spread_deg: float = 0.0
    bullet_radius: int = BULLET_RADIUS_PLAYER
    recoil: float = 30.0
    burst_count: int = 0
    burst_gap: float = 0.06
    splash_radius: float = 0.0   # rocket
    chain: int = 0               # tesla: number of extra chains
    chain_range: float = 0.0     # tesla chain range
    chain_damage_mult: float = 0.65
    base_pierce: int = 0         # weapon provides pierce baseline


WEAPONS: Dict[str, WeaponDef] = {
    "pistol": WeaponDef(
        id="pistol",
        name="Pistol",
        desc="Reliable default tank",
        base_damage=14,
        fire_cd=0.16,
        bullet_speed=880.0,
        bullet_life=1.0,
        bullets_per_shot=1,
        spread_deg=0.0,
        bullet_radius=4,
        recoil=21.0,
    ),
    "cannon": WeaponDef(
        id="cannon",
        name="Cannon",
        desc="Slow fire, heavy hits",
        base_damage=22,
        fire_cd=0.44,
        bullet_speed=780.0,
        bullet_life=1.15,
        bullet_radius=5,
        recoil=52.0,
    ),
    "minigun": WeaponDef(
        id="minigun",
        name="Minigun",
        desc="Fast fire, lower damage",
        base_damage=7,
        fire_cd=0.070,
        bullet_speed=920.0,
        bullet_life=0.95,
        spread_deg=6.0,
        bullet_radius=3,
        recoil=18.0,
    ),
    "burst": WeaponDef(
        id="burst",
        name="Burst Rifle",
        desc="3-shot burst, controlled",
        base_damage=12,
        fire_cd=0.26,
        bullet_speed=930.0,
        bullet_life=1.05,
        spread_deg=2.5,
        bullet_radius=4,
        recoil=21.0,
        burst_count=3,
        burst_gap=0.06,
    ),
    "shotgun": WeaponDef(
        id="shotgun",
        name="Shotgun",
        desc="Wide spread, close-range shred",
        base_damage=9,
        fire_cd=0.55,
        bullet_speed=760.0,
        bullet_life=0.70,
        bullets_per_shot=5,
        spread_deg=20.0,
        bullet_radius=3,
        recoil=60.0,
    ),
    "rocket": WeaponDef(
        id="rocket",
        name="Rocket",
        desc="Explosive splash damage",
        base_damage=30, # Originally 28
        fire_cd=0.85,   # Originally 0.7
        bullet_speed=680.0,
        bullet_life=1.25,
        bullet_radius=5,
        recoil=80.0,
        splash_radius=95.0,
    ),
    "tesla": WeaponDef(
        id="tesla",
        name="Tesla",
        desc="Chain lightning",
        base_damage=9, # Originally 13
        fire_cd=0.21,
        bullet_speed=920.0,
        bullet_life=0.85,
        bullet_radius=4,
        recoil=21.0,
        chain=2,
        chain_range=150.0,
    ),
    "sniper": WeaponDef(
        id="sniper",
        name="Sniper",
        desc="Slow shots, massive damage",
        base_damage=50,
        fire_cd=0.78,
        bullet_speed=1500.0, # Originally 1450
        bullet_life=1.55,
        bullet_radius=3,     # Originally 4
        recoil=10.0,
        base_pierce=1,
    ),
     "flamethrower": WeaponDef(
        id="flamethrower",
        name="Flamethrower",
        desc="Constant damage to melt enemies",
        base_damage=1,
        fire_cd=0.05,        # 0.05
        bullet_speed=520,    # 520
        bullet_life=0.45,    # 0.45
        bullets_per_shot=6,  # 6
        spread_deg=18,       # 18
        bullet_radius=1,
        recoil=10,           #10
    ),
    "omni_pistol": WeaponDef(
        id="omni_pistol",
        name="Omni Pistol",
        desc="Fires in 16 directions",
        base_damage=9,     # lower than pistol because 16 bullets per shot
        fire_cd=0.14,       # slightly faster than pistol (0.16)
        bullet_speed=860.0,
        bullet_life=1.05,
        bullets_per_shot=1, # special-cased in spawn_player_shot
        bullet_radius=4,
        recoil=18.0,
    ),
     "windscreen_wiper": WeaponDef(
        id="windscreen_wiper",
        name="Windscreen Wiper",
        desc="Wipes the map clean...",
        base_damage=1,
        fire_cd=0.05,        # 0.05
        bullet_speed=600,    # 520
        bullet_life=2,       # 0.45
        bullets_per_shot=50, # 50
        spread_deg=80,       # 80
        bullet_radius=1,
        recoil=10,
        chain_damage_mult=0.65
    ),
    "electricity": WeaponDef(
        id="electricity",
        name="Electricity",
        desc="Chains many enemies",
        base_damage=7,
        fire_cd=0.27,
        bullet_speed=920.0,
        bullet_life=0.85,
        bullet_radius=4,
        recoil=23.0,
        chain=6,
        chain_range=200.0,
        chain_damage_mult=0.85
    ),
    "tank": WeaponDef(
        id="tank",
        name="Tank",
        desc="Insane damage but very slow",
        base_damage=56, # Originally 52
        fire_cd=1.5,    # Originally 1.65
        bullet_speed=350.0,
        bullet_life=1,
        bullet_radius=7,
        recoil=150.0,
        splash_radius=150,
    ),
        "final_boss": WeaponDef(
        id="final_boss",
        name="Final Boss",
        desc="Final Boss",
        base_damage=150,
        fire_cd=4,       
        bullet_speed=250.0,
        bullet_life=0.7,
        bullet_radius=10,
        recoil=300,
        splash_radius=300,
    ),
}


# =========================================================
# LATE-GAME MODIFIERS
# =========================================================
@dataclass(frozen=True)
class ModifierDef:
    id: str
    name: str
    desc: str
    tiers: Tuple[str, ...]
    weight: float = 1.0


LATE_GAME_MODIFIERS = [
    ModifierDef(
        id="enemy_accel",
        name="Adrenaline Rush",
        desc="Enemies accelerate the longer they stay alive.",
        tiers=("early",),
        weight=1.0,
    ),
    ModifierDef(
        id="spawn_uneven",
        name="Pressure Spikes",
        desc="Enemy spawns favor uneven hot zones.",
        tiers=("early",),
        weight=1.0,
    ),
    ModifierDef(
        id="knight_enemy",
        name="Knight Arrival",
        desc="Knight enemies enter the fray.",
        tiers=("early",),
        weight=0.9,
    ),
    ModifierDef(
        id="resist_over_time",
        name="Adaptive Plating",
        desc="Enemies gain slight resistance over time.",
        tiers=("early",),
        weight=0.95,
    ),
    ModifierDef(
        id="turning_speed",
        name="Rapid Turns",
        desc="Enemies turn faster and adjust quickly.",
        tiers=("early",),
        weight=0.95,
    ),
    ModifierDef(
        id="spawn_bursts",
        name="Burst Spawns",
        desc="Delayed spawn bursts replace smooth spawns.",
        tiers=("early",),
        weight=0.9,
    ),
    ModifierDef(
        id="elite_spawn",
        name="Elite Scouts",
        desc="Elite enemies spawn across the map.",
        tiers=("mid",),
        weight=1.0,
    ),
    ModifierDef(
        id="tight_clusters",
        name="Tight Formations",
        desc="Enemy waves spawn in tighter clusters.",
        tiers=("mid",),
        weight=1.0,
    ),
    ModifierDef(
        id="double_ranged",
        name="Twin Salvos",
        desc="Ranged enemies fire 2 bullets per shot.",
        tiers=("mid",),
        weight=1.0,
    ),
    ModifierDef(
        id="knight_frequent",
        name="Knight Vanguard",
        desc="Knight enemies spawn more frequently.",
        tiers=("mid",),
        weight=0.9,
    ),
    ModifierDef(
        id="enemy_dashes",
        name="Sudden Dashes",
        desc="Enemies occasionally dash short distances.",
        tiers=("mid",),
        weight=1.0,
    ),
    ModifierDef(
        id="death_explosions",
        name="Death Blasts",
        desc="Enemies explode shortly after death.",
        tiers=("late",),
        weight=1.0,
    ),
    ModifierDef(
        id="curving_shots",
        name="Homing Fire",
        desc="Enemy projectiles curve toward the player.",
        tiers=("late",),
        weight=0.95,
    ),
    ModifierDef(
        id="enemy_regen",
        name="Regeneration Field",
        desc="Nearby enemies heal each other rapidly.",
        tiers=("late",),
        weight=0.9,
    ),
    ModifierDef(
        id="elite_frenzy",
        name="Elite Surge",
        desc="Elite enemies spawn much more frequently.",
        tiers=("late",),
        weight=1.0,
    ),
    ModifierDef(
        id="overlord_waves",
        name="Overlord Cycle",
        desc="Overlord battle every 3 waves.",
        tiers=("late",),
        weight=0.9,
    ),
    ModifierDef(
        id="revive_once",
        name="Second Wind",
        desc="Enemies revive once with reduced HP.",
        tiers=("late",),
        weight=0.95,
    ),
    ModifierDef(
        id="speed_ramp",
        name="Overdrive",
        desc="Global enemy speed ramps during the wave.",
        tiers=("late",),
        weight=1.0,
    ),
]


# =========================================================
# ENEMIES
# =========================================================
class EnemyBase:
    def __init__(self, pos: Vector2, hp: float, speed: float, radius: int, color):
        self.pos = Vector2(pos)
        self.vel = Vector2(0, 0)
        self.hp = hp
        self.hp_max = hp
        self.base_speed = speed
        self.speed = speed
        self.radius = radius
        self.color = color
        self.damage_contact = 1
        self.score_value = 10
        self.hit_flash = 0.0
        self.age = 0.0
        self.elite = False
        self.revives_remaining = 0
        self.revive_hp_ratio = 0.45
        self.extra_dash_cd = 0.0
        self.extra_dash_timer = 0.0
        self.extra_dash_dir = Vector2(1, 0)
        self.last_hit_weapon_id: Optional[str] = None
        self.last_hit_by_player: bool = False

    def update(self, dt, game):
        raise NotImplementedError

    def apply_separation(self, dt, neighbors: List["EnemyBase"]):
        push = Vector2(0, 0)
        for other in neighbors:
            if other is self:
                continue
            d = self.pos - other.pos
            dist = d.length()
            min_dist = self.radius + other.radius
            if 0.001 < dist < min_dist * ENEMY_SEPARATION_SOFT:
                push += d.normalize() * (min_dist - dist) * ENEMY_SEPARATION_FORCE
        if push.length_squared() > 0:
            self.vel += push * dt * 8.0

    def take_damage(self, dmg: int, knock_dir: Vector2, knockback: float, weapon_id: Optional[str] = None, from_player: bool = False):
        self.hp -= dmg
        self.vel += knock_dir * (knockback / max(1.0, self.radius))
        self.hit_flash = 0.12
        if from_player:
            self.last_hit_by_player = True
            self.last_hit_weapon_id = weapon_id

    def alive(self):
        return self.hp > 0

    def draw(self, surf, cam):
        p = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        col = (255, 255, 255) if self.hit_flash > 0 else self.color
        pygame.draw.circle(surf, col, p, self.radius)
        circle_outline(surf, (25, 25, 35), p, self.radius + 3, 2)
        if self.elite:
            circle_outline(surf, C_ELITE_OUTLINE, p, self.radius + 6, 2)

        # hp bar (small)
        w = self.radius * 2
        h = 5
        x = p[0] - w // 2
        y = p[1] - self.radius - 12
        frac = clamp(self.hp / max(1.0, self.hp_max), 0, 1)
        pygame.draw.rect(surf, (10, 10, 12), pygame.Rect(x, y, w, h))
        pygame.draw.rect(surf, (90, 255, 210), pygame.Rect(x, y, int(w * frac), h))


class Chaser(EnemyBase):
    def __init__(self, pos, hp, speed):
        super().__init__(pos, hp, speed, radius=ENEMY_RADIUS_CHASER, color=C_CHASER)
        self.damage_contact = 1
        self.score_value = 12

    def update(self, dt, game):
        target = game.enemy_target_pos()
        d = target - self.pos
        if d.length_squared() > 1:
            desired = d.normalize() * self.speed
            self.vel = self.vel.lerp(desired, 1 - math.exp(-dt * 6.5 * game.enemy_turn_speed_mult()))
        self.pos += self.vel * dt
        game.resolve_circle_walls(self, damping=0.2)


class Ranged(EnemyBase):
    def __init__(self, pos, hp, speed):
        super().__init__(pos, hp, speed, radius=ENEMY_RADIUS_RANGED, color=C_RANGED)
        self.damage_contact = 1
        self.score_value = 16
        self.shoot_cd = random.uniform(0.9, 1.3)

    def update(self, dt, game):
        self.shoot_cd -= dt
        target = game.enemy_target_pos()
        d = target - self.pos
        dist = d.length()

        # keep distance
        if dist > 430:
            if dist > 1:
                desired = d.normalize() * self.speed
                self.vel = self.vel.lerp(desired, 1 - math.exp(-dt * 5.0 * game.enemy_turn_speed_mult()))
        elif dist < 270:
            if dist > 1:
                desired = (-d).normalize() * (self.speed * 0.95)
                self.vel = self.vel.lerp(desired, 1 - math.exp(-dt * 7.0 * game.enemy_turn_speed_mult()))
        else:
            self.vel *= (1.0 - min(dt * 6.5 * game.enemy_turn_speed_mult(), 0.25))

        self.pos += self.vel * dt
        game.resolve_circle_walls(self, damping=0.2)

        if self.shoot_cd <= 0 and dist <= RANGED_MAX_SHOOT_DIST:
            if game.is_world_pos_onscreen(self.pos, margin=RANGED_SHOOT_IF_ONSCREEN_MARGIN):
                if (not RANGED_LOS_ENABLED) or game.has_line_of_sight(self.pos, target):
                    if dist > 1:
                        dirn = d.normalize()
                        spd = RANGED_BULLET_SPEED_BASE + 60.0 * game.diff_eased
                        dmg = int(round(lerp(RANGED_DAMAGE_BASE, RANGED_DAMAGE_HARD, game.diff_eased)))
                        shots = 2 if game.is_modifier_active("double_ranged") else 1
                        spread = 10.0 if shots > 1 else 0.0
                        for i in range(shots):
                            ang = 0.0 if shots == 1 else lerp(-spread * 0.5, spread * 0.5, i / (shots - 1))
                            vel = dirn.rotate(ang) * spd
                            b = Projectile(
                                self.pos + dirn * (self.radius + 6),
                                vel,
                                damage=dmg,
                                owner="enemy",
                                color=C_EBULLET,
                                radius=BULLET_RADIUS_ENEMY,
                                lifetime=RANGED_BULLET_LIFETIME,
                            )
                            game.enemy_projectiles.append(b)
                        game.audio_play("enemy_shoot")
                    self.shoot_cd = random.uniform(RANGED_COOLDOWN_MIN, RANGED_COOLDOWN_MAX)


class Tank(EnemyBase):
    def __init__(self, pos, hp, speed):
        super().__init__(pos, hp, speed, radius=ENEMY_RADIUS_TANK, color=C_TANK)
        self.damage_contact = 2
        self.score_value = 24

    def update(self, dt, game):
        target = game.enemy_target_pos()
        d = target - self.pos
        if d.length_squared() > 1:
            desired = d.normalize() * self.speed
            self.vel = self.vel.lerp(desired, 1 - math.exp(-dt * 4.0 * game.enemy_turn_speed_mult()))
        self.pos += self.vel * dt
        game.resolve_circle_walls(self, damping=0.15)


class Knight(EnemyBase):
    def __init__(self, pos, hp, speed):
        super().__init__(pos, hp, speed, radius=ENEMY_RADIUS_KNIGHT, color=(210, 190, 140))
        self.damage_contact = 3
        self.score_value = 38

    def update(self, dt, game):
        target = game.enemy_target_pos()
        d = target - self.pos
        if d.length_squared() > 1:
            desired = d.normalize() * self.speed
            self.vel = self.vel.lerp(desired, 1 - math.exp(-dt * 3.2 * game.enemy_turn_speed_mult()))
        self.pos += self.vel * dt
        game.resolve_circle_walls(self, damping=0.12)


class Sprinter(EnemyBase):
    def __init__(self, pos, hp, speed):
        super().__init__(pos, hp, speed, radius=ENEMY_RADIUS_SPRINTER, color=C_SPRINTER)
        self.damage_contact = 1
        self.score_value = 10

    def update(self, dt, game):
        target = game.enemy_target_pos()
        d = target - self.pos
        if d.length_squared() > 1:
            desired = d.normalize() * self.speed
            self.vel = self.vel.lerp(desired, 1 - math.exp(-dt * 9.0 * game.enemy_turn_speed_mult()))
        self.pos += self.vel * dt
        game.resolve_circle_walls(self, damping=0.25)


class Dasher(EnemyBase):
    def __init__(self, pos, hp, speed):
        super().__init__(pos, hp, speed, radius=ENEMY_RADIUS_DASHER, color=C_DASHER)
        self.damage_contact = 2
        self.score_value = 20
        self.dash_cd = random.uniform(2.2, 3.0)
        self.dash_time = 0.0

    def update(self, dt, game):
        self.dash_cd -= dt
        self.dash_time = max(0.0, self.dash_time - dt)

        target = game.enemy_target_pos()
        d = target - self.pos
        dist2 = d.length_squared()

        if self.dash_time > 0:
            if dist2 > 1:
                steer = d.normalize()
                self.vel = self.vel.lerp(steer * (self.speed * 2.6), 1 - math.exp(-dt * 10.0 * game.enemy_turn_speed_mult()))
        else:
            if dist2 > 1:
                desired = d.normalize() * self.speed
                self.vel = self.vel.lerp(desired, 1 - math.exp(-dt * 6.0 * game.enemy_turn_speed_mult()))

            if self.dash_cd <= 0 and dist2 < (620 * 620):
                self.dash_time = 0.22
                self.dash_cd = lerp(3.0, 2.0, game.diff_eased) + random.uniform(-0.15, 0.15)

        self.pos += self.vel * dt
        game.resolve_circle_walls(self, damping=0.18)

    def draw(self, surf, cam):
        super().draw(surf, cam)
        if self.dash_cd < 0.55:
            p = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
            circle_outline(surf, (230, 200, 255), p, self.radius + 10, 2)


class Boss(EnemyBase):
    """Big slow boss. Spawns every N waves. No normal spawns while alive."""
    MIN_SHOOT_CD = 0.75
    ENRAGED_ATTACK_SPEED_MULT = 0.8
    ENRAGED_MOVE_SPEED_MULT = 1.2
    ENRAGED_DASH_SPEED_MULT = 1.3
    ENRAGED_DASH_WINDUP = 0.8
    ENRAGED_VOLLEY_BONUS = 1
    ENRAGED_ROCKET_REACTION_REDUCTION = 0.3
    ENRAGED_ROCKET_RADIUS_MULT = 1.7
    SKY_SLAM_COOLDOWN_RANGE = (10.0, 13.0)
    SKY_SLAM_TAKEOFF_TIME = 0.7
    SKY_SLAM_HOVER_TIME = 3.0
    SKY_SLAM_RECOVERY_TIME = 0.5
    SKY_SLAM_MARKER_DELAY = 0.5
    SKY_SLAM_DAMAGE = 3
    SKY_SLAM_SCALE_MIN = 0.2
    SKY_SLAM_BUFFER_EXTRA = 0.6

    def __init__(self, pos, hp, speed, wave_index: int):
        super().__init__(pos, hp, speed, radius=36, color=C_BOSS)
        self.damage_contact = 1
        self.base_damage_contact = 1
        self.score_value = 300 + wave_index * 25
        self.wave_index = wave_index
        self.base_shoot_cd = 1.4
        self.shoot_cd = self.base_shoot_cd
        self.shoot_cd_base = self.base_shoot_cd
        self.base_volley = 3
        self.volley = self.base_volley
        self.volley_spread = 12.0
        self.bullet_speed = 270.0
        self.bullet_damage = 1 + max(0, (wave_index // 10) - 1) * 2 # Boss damage
        self.bullet_life = 1.5
        self.enraged = False
        self.base_speed = speed
        # Story boss specials (Level 6 only).
        self.base_dash_speed = 920.0
        self.dash_distance = 420.0
        self.base_dash_windup = 1.3
        self.dash_cd = random.uniform(4.0, 6.0)
        self.dash_windup = 0.0
        self.dash_timer = 0.0
        self.dash_dir = Vector2(0, 0)
        self.dash_target = Vector2(self.pos)
        self.dash_hit = False
        self.rocket_cd = random.uniform(5.0, 7.0)
        self.base_rocket_telegraph = 0.7
        self.base_rocket_fall = 0.35
        self.base_rocket_reaction = self.base_rocket_telegraph + self.base_rocket_fall
        self.base_rocket_radius = 90.0
        self.sky_slam_cd = random.uniform(*self.SKY_SLAM_COOLDOWN_RANGE)
        self.sky_slam_active = False
        self.sky_slam_phase = "idle"
        self.sky_slam_timer = 0.0
        self.sky_slam_recovery = 0.0
        self.sky_slam_scale = 1.0
        self.sky_slam_marker_pos = Vector2(self.pos)
        self.sky_slam_marker_radius = 180.0
        self.sky_slam_buffer: List[Dict[str, object]] = []
        self.sky_slam_impact_timer = 0.0
        self.sky_slam_impact_total = 0.45
        self.sky_slam_impact_pos = Vector2(self.pos)

    def take_damage(self, dmg: int, knock_dir: Vector2, knockback: float, weapon_id: Optional[str] = None, from_player: bool = False):
        # Boss has knockback resistance
        if self.sky_slam_active and self.sky_slam_phase in ("takeoff", "hover"):
            return
        super().take_damage(dmg, knock_dir, knockback * 0.35, weapon_id=weapon_id, from_player=from_player)

    def update(self, dt, game):
        # Enrage at low HP
        if (not self.enraged) and self.hp < self.hp_max * 0.35:
            self.enraged = True

        enraged_mult = 1.0 if not self.enraged else self.ENRAGED_ATTACK_SPEED_MULT
        self.shoot_cd_base = max(self.MIN_SHOOT_CD, self.base_shoot_cd * enraged_mult)
        self.volley = self.base_volley + (self.ENRAGED_VOLLEY_BONUS if self.enraged else 0)
        self.speed = self.base_speed * (self.ENRAGED_MOVE_SPEED_MULT if self.enraged else 1.0)
        dash_speed = self.base_dash_speed * (self.ENRAGED_DASH_SPEED_MULT if self.enraged else 1.0)
        dash_windup_time = self.ENRAGED_DASH_WINDUP if self.enraged else self.base_dash_windup
        reaction_reduction = self.ENRAGED_ROCKET_REACTION_REDUCTION if self.enraged else 0.0
        rocket_reaction = max(0.0, self.base_rocket_reaction - reaction_reduction)
        rocket_radius = self.base_rocket_radius * (self.ENRAGED_ROCKET_RADIUS_MULT if self.enraged else 1.0)
        rocket_telegraph = max(0.0, rocket_reaction - self.base_rocket_fall)

        if self.sky_slam_active:
            self._update_sky_slam(dt, game)
            return

        if self.enraged and game.boss_specials_active():
            self.sky_slam_cd = max(0.0, self.sky_slam_cd - dt)
            if self.sky_slam_cd <= 0 and self.dash_windup <= 0 and self.dash_timer <= 0:
                self._start_sky_slam(game)
                return

        self.shoot_cd -= dt

        if game.boss_specials_active():
            # Dash attack: visible wind-up, then lunge toward the player.
            dash_duration = self.dash_distance / dash_speed
            self.dash_cd -= dt
            if self.dash_windup > 0:
                self.dash_windup -= dt
                # Hold position during the wind-up so the telegraph is clear.
                self.vel *= 0
                if self.dash_windup <= 0:
                    self.dash_timer = dash_duration
                    self.dash_hit = False
                    # Begin the dash immediately after wind-up using any leftover time slice.
                    dash_dt = -self.dash_windup
                    if dash_dt > 0:
                        step = min(dash_dt, self.dash_timer)
                        self.pos += self.dash_dir * dash_speed * step
                        game.resolve_circle_walls(self, damping=0.12)
                        if not self.dash_hit:
                            rr = (self.radius + PLAYER_RADIUS) ** 2
                            if (game.player.pos - self.pos).length_squared() <= rr:
                                self.dash_hit = True
                                game.damage_player(2)
                                knock = (game.player.pos - self.pos)
                                if knock.length_squared() > 0.001:
                                    game.player.vel += knock.normalize() * 420
                        self.dash_timer -= step
            elif self.dash_timer > 0:
                step = min(dt, self.dash_timer)
                self.pos += self.dash_dir * dash_speed * step
                game.resolve_circle_walls(self, damping=0.12)
                if not self.dash_hit:
                    rr = (self.radius + PLAYER_RADIUS) ** 2
                    if (game.player.pos - self.pos).length_squared() <= rr:
                        self.dash_hit = True
                        game.damage_player(2)
                        knock = (game.player.pos - self.pos)
                        if knock.length_squared() > 0.001:
                            game.player.vel += knock.normalize() * 420
                self.dash_timer -= step
            elif self.dash_cd <= 0:
                self.dash_cd = random.uniform(4.0, 6.0)
                # Dash timing: lock direction and target, then wait briefly before moving.
                self.dash_windup = dash_windup_time
                d = game.player.pos - self.pos
                self.dash_dir = d.normalize() if d.length_squared() > 0.001 else Vector2(1, 0)
                self.dash_target = self.pos + self.dash_dir * self.dash_distance

            # Rocket strike: mark ground, then drop and explode.
            self.rocket_cd -= dt
            if self.rocket_cd <= 0:
                self.rocket_cd = random.uniform(5.0, 7.0)
                jitter = Vector2(random.uniform(-120, 120), random.uniform(-120, 120))
                game.spawn_boss_rocket_strike(
                    game.player.pos + jitter,
                    telegraph_time=rocket_telegraph,
                    fall_time=self.base_rocket_fall,
                    radius=rocket_radius,
                )
            if self.dash_windup > 0 or self.dash_timer > 0:
                return

        # Slow pursuit
        d = game.player.pos - self.pos
        if d.length_squared() > 1:
            desired = d.normalize() * self.speed
            self.vel = self.vel.lerp(desired, 1 - math.exp(-dt * 3.2))
        self.pos += self.vel * dt
        game.resolve_circle_walls(self, damping=0.12)

        # Shoot if on screen-ish and has LOS
        dist = d.length()
        if self.shoot_cd <= 0 and dist < 820:
            if game.is_world_pos_onscreen(self.pos, margin=120):
                if (not RANGED_LOS_ENABLED) or game.has_line_of_sight(self.pos, game.player.pos):
                    if dist > 1:
                        base_dir = d.normalize()
                        # fire a small volley spread
                        if self.volley <= 1:
                            angles = [0.0]
                        else:
                            angles = []
                            for i in range(self.volley):
                                t = i / (self.volley - 1)
                                angles.append(lerp(-self.volley_spread * 0.5, self.volley_spread * 0.5, t))

                        spd = self.bullet_speed + 90.0 * game.diff_eased + (30.0 if self.enraged else 0.0)
                        dmg = int(self.bullet_damage + 2 * game.diff_eased)

                        for ang in angles:
                            dirn = base_dir.rotate(ang)
                            b = Projectile(
                                self.pos + dirn * (self.radius + 8),
                                dirn * spd,
                                damage=dmg,
                                owner="enemy",
                                color=C_EBULLET,
                                radius=5,
                                lifetime=self.bullet_life,
                            )
                            game.enemy_projectiles.append(b)

                        game.audio_play("enemy_shoot")
            self.shoot_cd = self.shoot_cd_base + random.uniform(-0.12, 0.18)

    def draw(self, surf, cam):
        if self.sky_slam_phase == "hover":
            self._draw_sky_slam_marker(surf, cam)
        if self.sky_slam_impact_timer > 0:
            self._draw_sky_slam_impact(surf, cam)

        draw_radius = max(1, int(self.radius * self.sky_slam_scale))
        p = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        col = (255, 255, 255) if self.hit_flash > 0 else self.color
        pygame.draw.circle(surf, col, p, draw_radius)
        circle_outline(surf, C_BOSS_EDGE, p, draw_radius + 5, 3)
        circle_outline(surf, (25, 25, 35), p, draw_radius + 10, 2)
        if self.dash_windup > 0 and not self.sky_slam_active:
            # Telegraph the dash with a line toward the target.
            t = (int(self.dash_target.x - cam.x), int(self.dash_target.y - cam.y))
            pygame.draw.line(surf, (255, 150, 110), p, t, 3)
            circle_outline(surf, (255, 180, 140), p, draw_radius + 14, 2)

        # tiny hp bar over head
        w = draw_radius * 2 + 30
        h = 7
        x = p[0] - w // 2
        y = p[1] - draw_radius - 16
        frac = clamp(self.hp / max(1.0, self.hp_max), 0, 1)
        pygame.draw.rect(surf, (10, 10, 12), pygame.Rect(x, y, w, h))
        pygame.draw.rect(surf, (255, 120, 140), pygame.Rect(x, y, int(w * frac), h))

    def _start_sky_slam(self, game):
        # Enraged-only special: briefly take off, track the player, then slam down.
        self.sky_slam_active = True
        self.sky_slam_phase = "takeoff"
        self.sky_slam_timer = self.SKY_SLAM_TAKEOFF_TIME
        self.sky_slam_recovery = 0.0
        self.sky_slam_scale = 1.0
        self.sky_slam_buffer.clear()
        self.sky_slam_marker_pos = Vector2(game.player.pos)
        self.damage_contact = 0
        self.vel *= 0
        self.dash_windup = 0.0
        self.dash_timer = 0.0
        self.shoot_cd = self.shoot_cd_base

    def _update_sky_slam(self, dt, game):
        self.vel *= 0
        self._record_sky_slam_target(dt, game)
        if self.sky_slam_phase == "takeoff":
            self.sky_slam_timer -= dt
            progress = clamp(1.0 - (self.sky_slam_timer / self.SKY_SLAM_TAKEOFF_TIME), 0.0, 1.0)
            self.sky_slam_scale = lerp(1.0, self.SKY_SLAM_SCALE_MIN, progress)
            if self.sky_slam_timer <= 0:
                self.sky_slam_phase = "hover"
                self.sky_slam_timer = self.SKY_SLAM_HOVER_TIME
        elif self.sky_slam_phase == "hover":
            self.sky_slam_timer -= dt
            self.sky_slam_marker_pos = Vector2(self._get_delayed_sky_slam_target())
            self.sky_slam_scale = self.SKY_SLAM_SCALE_MIN
            if self.sky_slam_timer <= 0:
                self._slam_down(game)
        elif self.sky_slam_phase == "impact":
            self.sky_slam_impact_timer = max(0.0, self.sky_slam_impact_timer - dt)
            self.sky_slam_recovery = max(0.0, self.sky_slam_recovery - dt)
            if self.sky_slam_recovery <= 0:
                self._end_sky_slam()

    def _slam_down(self, game):
        self.sky_slam_phase = "impact"
        self.sky_slam_scale = 1.0
        self.pos = Vector2(self.sky_slam_marker_pos)
        self.damage_contact = self.base_damage_contact
        self.sky_slam_recovery = self.SKY_SLAM_RECOVERY_TIME
        self.sky_slam_impact_timer = self.sky_slam_impact_total
        self.sky_slam_impact_pos = Vector2(self.sky_slam_marker_pos)
        d2 = (game.player.pos - self.sky_slam_marker_pos).length_squared()
        if d2 <= self.sky_slam_marker_radius ** 2:
            game.damage_player(self.SKY_SLAM_DAMAGE)
        game.shake = max(game.shake, 16.0)

    def _end_sky_slam(self):
        self.sky_slam_active = False
        self.sky_slam_phase = "idle"
        self.sky_slam_scale = 1.0
        self.sky_slam_cd = random.uniform(*self.SKY_SLAM_COOLDOWN_RANGE)

    def _record_sky_slam_target(self, dt, game):
        self.sky_slam_buffer.append({"pos": Vector2(game.player.pos), "age": 0.0})
        for entry in self.sky_slam_buffer:
            entry["age"] = float(entry["age"]) + dt
        trim_after = self.SKY_SLAM_MARKER_DELAY + self.SKY_SLAM_BUFFER_EXTRA
        while self.sky_slam_buffer and float(self.sky_slam_buffer[0]["age"]) > trim_after:
            self.sky_slam_buffer.pop(0)

    def _get_delayed_sky_slam_target(self) -> Vector2:
        target = None
        for entry in self.sky_slam_buffer:
            if float(entry["age"]) >= self.SKY_SLAM_MARKER_DELAY:
                target = entry["pos"]
                break
        if target is None and self.sky_slam_buffer:
            target = self.sky_slam_buffer[0]["pos"]
        return Vector2(target) if target is not None else Vector2(self.pos)

    def _draw_sky_slam_marker(self, surf, cam):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pos = self.sky_slam_marker_pos
        screen = (int(pos.x - cam.x), int(pos.y - cam.y))
        radius = int(self.sky_slam_marker_radius)
        pygame.draw.circle(overlay, (255, 120, 140, 60), screen, radius)
        pygame.draw.circle(overlay, (255, 170, 190, 200), screen, radius, 3)
        pygame.draw.line(overlay, (255, 170, 190, 220), (screen[0] - radius, screen[1]), (screen[0] + radius, screen[1]), 3)
        pygame.draw.line(overlay, (255, 170, 190, 220), (screen[0], screen[1] - radius), (screen[0], screen[1] + radius), 3)
        surf.blit(overlay, (0, 0))

    def _draw_sky_slam_impact(self, surf, cam):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        progress = clamp(1.0 - (self.sky_slam_impact_timer / self.sky_slam_impact_total), 0.0, 1.0)
        radius = int(self.sky_slam_marker_radius * (0.7 + 0.6 * progress))
        alpha = int(200 * (1.0 - progress))
        pos = self.sky_slam_impact_pos
        screen = (int(pos.x - cam.x), int(pos.y - cam.y))
        pygame.draw.circle(overlay, (255, 220, 230, alpha), screen, max(1, radius), 4)
        pygame.draw.circle(overlay, (255, 180, 200, int(alpha * 0.6)), screen, max(1, int(radius * 0.6)), 2)
        surf.blit(overlay, (0, 0))


# =========================================================
# UPGRADES (Level-up)
# =========================================================
@dataclass
class UpgradeDef:
    id: str
    name: str
    desc: str
    tag: str


UPGRADES = [
    UpgradeDef("damage", "Overcharged Rounds", "Deal more damage per shot.", "DMG"),
    UpgradeDef("fire_rate", "Rapid Trigger", "Shoot faster.", "FR"),
    UpgradeDef("bullet_speed", "Rail Assist", "Bullets travel faster.", "BSPD"),
    UpgradeDef("max_hp", "Reinforced Core", "Increase max HP by 1.", "HP"),
    UpgradeDef("move_speed", "Neon Strides", "Move faster.", "MOVE"),
    UpgradeDef("dash_cd", "Reflex Coil", "Dash cooldown reduced.", "CD"),
    UpgradeDef("piercing", "Phase Ammo", "Bullets pierce +1 enemy.", "PIERCE"),
    UpgradeDef("crit", "Lucky Circuitry", "Increase crit chance.", "CRIT"),
    UpgradeDef("dash_len", "Momentum Surge", "Dash lasts slightly longer.", "DASH"),
    UpgradeDef("heal", "Emergency Patch", "Instantly heal 3 HP.", "HEAL"),
    UpgradeDef("xp_gain", "Data Magnet", "Gain more XP from orbs.", "XP"),
    UpgradeDef("magnet", "Orb Magnet", "Pickups pull in from farther away.", "MAG"),
]


# =========================================================
# SHOP
# =========================================================
@dataclass
class ShopItemDef:
    id: str
    name: str
    desc: str
    max_level: int
    base_cost: int
    cost_mult: float
    kind: str = "meta"  # meta / weapon / cosmetic / settings
    weapon_id: str = ""


SHOP_ITEMS = [
    # META
    ShopItemDef("meta_damage", "+5% Base Damage", "Permanent: increases starting damage.", 10, 40, 1.35, "meta"),
    ShopItemDef("meta_move", "+5% Move Speed", "Permanent: increases starting speed.", 10, 40, 1.35, "meta"),
    ShopItemDef("meta_hp", "+1 Max HP", "Permanent: increases starting max HP.", 5, 80, 1.50, "meta"),
    ShopItemDef("meta_xp", "+5% XP Gain", "Permanent: gain more XP from orbs.", 10, 35, 1.35, "meta"),
    ShopItemDef("meta_dash", "-5% Dash Cooldown", "Permanent: dash comes back faster.", 10, 45, 1.35, "meta"),
    ShopItemDef("armor", "+10% Damage Resistance", "Permanent: take less damage.", 10, 45, 1.35, "meta"),
    ShopItemDef("meta_bulletspeed", "+5% Bullet Speed", "Permanent: faster bullets.", 10, 30, 1.35, "meta"),

    # WEAPONS (unlocks)
    ShopItemDef("unlock_cannon", "Unlock: Cannon", "Slow fire, heavy hits", 1, 110, 1.0, "weapon", weapon_id="cannon"),
    ShopItemDef("unlock_minigun", "Unlock: Minigun", "Fast fire, lower damage", 1, 150, 1.0, "weapon", weapon_id="minigun"),
    ShopItemDef("unlock_burst", "Unlock: Burst Rifle", "3-shot bursts", 1, 120, 1.0, "weapon", weapon_id="burst"),
    ShopItemDef("unlock_shotgun", "Unlock: Shotgun", "Wide spread close-range", 1, 200, 1.0, "weapon", weapon_id="shotgun"),
    ShopItemDef("unlock_tesla", "Unlock: Tesla", "Chains targets", 1, 230, 1.0, "weapon", weapon_id="tesla"),
    ShopItemDef("unlock_rocket", "Unlock: Rocket", "Splash damage explosives", 1, 260, 1.0, "weapon", weapon_id="rocket"),

    # NEW
    ShopItemDef("unlock_sniper", "Unlock: Sniper", "Slow shots, massive damage", 1, 200, 1.0, "weapon", weapon_id="sniper"),
    ShopItemDef("unlock_flamethrower", "Unlock: Flamethrower", "Constant damage to melt enemies", 1, 300, 1.0, "weapon", weapon_id="flamethrower"),
    ShopItemDef("unlock_omni_pistol", "Unlock: Omni Pistol", "Fires in 16 directions", 1, 500, 1.0, "weapon", weapon_id="omni_pistol"),
    ShopItemDef("unlock_electricity", "Unlock: Electricity", "Chains many enemies", 1, 400, 1.0, "weapon", weapon_id="electricity"),
    ShopItemDef("unlock_windscreen_wiper", "Unlock: Windscreen Wiper", "Wipes the map clean...", 1, math.inf, 1.0, "weapon", weapon_id="windscreen"),
    ShopItemDef("unlock_tank", "Unlock: Tank", "Insane damage but very slow", 1, 390, 1.0, "weapon", weapon_id="tank"),
    ShopItemDef("unlock_final_boss", "Unlock: Final Boss", "Final Boss", 1, 1000, 1.0, "weapon", weapon_id="final_boss"),

]

SHOP_ITEMS_BY_ID = {item.id: item for item in SHOP_ITEMS}
SHOP_ITEMS_BY_WEAPON = {item.weapon_id: item for item in SHOP_ITEMS if item.kind == "weapon"}


@dataclass
class CosmeticDef:
    id: str
    name: str
    desc: str
    category: str  # outline / bullet / trail / explosion
    cost: int
    color: Tuple[int, int, int]
    default: bool = False
    bundle_only: bool = False


DEFAULT_COSMETICS = {
    "outline": "outline_standard",
    "bullet": "bullet_standard",
    "trail": "trail_none",
    "explosion": "explosion_ember",
}

BUNDLE_ONLY_COSMETIC_VALUE = 150

COSMETICS = [
    CosmeticDef("outline_standard", "Standard Outline", "Clean default trim.", "outline", 0, C_ACCENT, default=True),
    CosmeticDef("outline_neon", "Neon Outline", "Bright cyan glow.", "outline", 120, C_OUTLINE_NEON),
    CosmeticDef("outline_ember", "Ember Outline", "Warm orange trim.", "outline", 140, C_OUTLINE_EMBER),
    CosmeticDef("outline_steel", "Steel Outline", "Cold metallic edge.", "outline", 0, C_OUTLINE_STEEL, bundle_only=True),
    CosmeticDef("bullet_standard", "Standard Rounds", "Classic bright shots.", "bullet", 0, C_BULLET, default=True),
    CosmeticDef("bullet_mint", "Mint Rounds", "Fresh neon bullets.", "bullet", 110, C_BULLET_MINT),
    CosmeticDef("bullet_violet", "Violet Rounds", "Electric violet shots.", "bullet", 130, C_BULLET_VIOLET),
    CosmeticDef("bullet_gold", "Gold Rounds", "Lux gilded shots.", "bullet", 0, C_BULLET_GOLD, bundle_only=True),
    CosmeticDef("trail_none", "No Trail", "Pure, clean movement.", "trail", 0, C_TEXT_DIM, default=True),
    CosmeticDef("trail_spark", "Spark Trail", "Short warm sparks.", "trail", 120, C_TRAIL_SPARK),
    CosmeticDef("trail_ion", "Ion Trail", "Cool ion streak.", "trail", 150, C_TRAIL_ION),
    CosmeticDef("explosion_ember", "Ember Burst", "Standard explosion flare.", "explosion", 0, C_WARN, default=True),
    CosmeticDef("explosion_plasma", "Plasma Burst", "Bright cyan burst.", "explosion", 170, C_EXPLOSION_PLASMA),
    CosmeticDef("explosion_magma", "Magma Burst", "Heavy orange blast.", "explosion", 0, C_EXPLOSION_MAGMA, bundle_only=True),
]

COSMETICS_BY_ID = {cosmetic.id: cosmetic for cosmetic in COSMETICS}


@dataclass
class BundleDef:
    id: str
    name: str
    desc: str
    weapons: List[str]
    meta: List[str]
    cosmetics: List[str]
    discount: float


BUNDLES = [
    BundleDef(
        "starter_arsenal",
        "Starter Arsenal",
        "A discounted mix of core firepower and extra durability.",
        weapons=["cannon", "burst"],
        meta=["meta_hp"],
        cosmetics=[],
        discount=0.15,
    ),
    BundleDef(
        "speed_demon",
        "Speed Demon",
        "A fast-paced bundle built for mobility and rapid fire.",
        weapons=["minigun"],
        meta=["meta_move", "meta_dash"],
        cosmetics=["bullet_mint"],
        discount=0.18,
    ),
    BundleDef(
        "heavy_metal",
        "Heavy Metal",
        "High-impact gear paired with rugged upgrades and exclusive cosmetics.",
        weapons=["tank"],
        meta=["armor"],
        cosmetics=["outline_steel", "explosion_magma"],
        discount=0.22,
    ),
    BundleDef(
        "arc_surge",
        "Arc Surge",
        "A shocking bundle of experimental firepower and charged visuals.",
        weapons=["tesla", "electricity"],
        meta=["meta_bulletspeed"],
        cosmetics=["bullet_violet", "trail_ion"],
        discount=0.20,
    ),
]


MAX_MASTERY_LEVEL = 5


def mastery_requirements(level: int) -> Tuple[int, int]:
    kills_needed = int(30 * (level ** 2))
    games_needed = int(5 + (level - 1) * 7)
    return kills_needed, games_needed


# =========================================================
# PLAYER
# =========================================================
class Player:
    def __init__(self, pos: Vector2, weapon_id: str = "pistol"):
        self.pos = Vector2(pos)
        self.vel = Vector2(0, 0)
        self.aim_dir = Vector2(1, 0)

        self.weapon_id = weapon_id
        self.weapon = WEAPONS.get(weapon_id, WEAPONS["pistol"])

        self.damage_mult = 1.0
        self.fire_rate_mult = 1.0
        self.bullet_speed_mult = 1.0
        self.bullet_life_add = 0.0
        self.move_speed_add = 0.0
        self.piercing = 0
        self.crit_chance = 0.05
        self.crit_mult = 1.75
        self.dash_time_bonus = 0.0
        self.knockback_mult = 1.0
        self.magnet_bonus = 0.0

        self.max_hp = PLAYER_MAX_HP_BASE
        self.hp = self.max_hp
        self.iframes = 0.0

        self.shoot_timer = 0.0
        self.trigger_held = False
        self.burst_remaining = 0
        self.burst_gap_timer = 0.0
        self.auto_fire = False

        self.dash_timer = 0.0
        self.dash_cd_timer = 0.0
        self.dash_dir = Vector2(0, 0)

        self.level = 1
        self.xp = 0
        self.xp_to_next = 60

        self.score = 0

        self.effects: Dict[str, float] = {
            "damage_boost": 0.0,
            "rapid_fire": 0.0,
            "speed_boost": 0.0,
            "shield": 0.0,
        }

        self.meta_damage_mul = 1.0
        self.meta_move_mul = 1.0
        self.meta_xp_mul = 1.0
        self.meta_dash_mul = 1.0
        self.meta_armor_mul = 1.0
        self.meta_bulletspd_mul = 1.0
        self.outline_color = C_ACCENT

    def set_weapon(self, weapon_id: str):
        self.weapon_id = weapon_id
        self.weapon = WEAPONS.get(weapon_id, WEAPONS["pistol"])
        self.burst_remaining = 0
        self.burst_gap_timer = 0.0
        self.shoot_timer = min(self.shoot_timer, 0.1)

    def invulnerable(self):
        return self.iframes > 0 or self.is_dashing() or self.effects["shield"] > 0

    def is_dashing(self):
        return self.dash_timer > 0

    def apply_powerup(self, ptype: str):
        if ptype == "damage_boost":
            self.effects["damage_boost"] = max(self.effects["damage_boost"], POWERUP_DURATION_DAMAGE)
        elif ptype == "rapid_fire":
            self.effects["rapid_fire"] = max(self.effects["rapid_fire"], POWERUP_DURATION_RAPID)
        elif ptype == "speed_boost":
            self.effects["speed_boost"] = max(self.effects["speed_boost"], POWERUP_DURATION_SPEED)
        elif ptype == "shield":
            self.effects["shield"] = max(self.effects["shield"], POWERUP_DURATION_SHIELD)

    def gain_xp(self, amount: int):
        self.xp += int(round(amount * self.meta_xp_mul))

    def try_level_up(self):
        leveled = False
        for _ in range(16):
            if self.xp < self.xp_to_next:
                break
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(self.xp_to_next * 1.18 + 18)
            leveled = True
        return leveled

    def apply_upgrade(self, up_id: str):
        if up_id == "damage":
            self.damage_mult *= 1.12
        elif up_id == "fire_rate":
            self.fire_rate_mult *= 1.12
        elif up_id == "bullet_speed":
            self.bullet_speed_mult *= 1.10
        elif up_id == "max_hp":
            self.max_hp += 1
            self.hp = min(self.max_hp, self.hp + 1)
        elif up_id == "move_speed":
            self.move_speed_add += 20
        elif up_id == "dash_cd":
            self.meta_dash_mul *= 0.92
            self.meta_dash_mul = max(0.55, self.meta_dash_mul)
        elif up_id == "piercing":
            self.piercing += 1
        elif up_id == "crit":
            self.crit_chance = min(0.30, self.crit_chance + 0.04)
        elif up_id == "dash_len":
            self.dash_time_bonus = min(0.12, self.dash_time_bonus + 0.03)
        elif up_id == "heal":
            self.hp = min(self.max_hp, self.hp + 3)
        elif up_id == "xp_gain":
            self.meta_xp_mul = min(2.0, self.meta_xp_mul * 1.10)
        elif up_id == "xp_push":
            self.meta_xp_mul = min(2.0, self.meta_xp_mul * 1.06)
            self.knockback_mult = min(2.0, self.knockback_mult * 1.10)
        elif up_id == "knockback":
            self.knockback_mult = min(2.0, self.knockback_mult * 1.18)
        elif up_id == "magnet":
            self.magnet_bonus = min(120.0, self.magnet_bonus + 35.0)

    def get_damage(self) -> int:
        dmg = self.weapon.base_damage
        dmg = int(round(dmg * self.damage_mult * self.meta_damage_mul))
        if self.effects["damage_boost"] > 0:
            dmg = int(dmg * 1.5)
        return max(1, dmg)

    def get_fire_cooldown(self) -> float:
        cd = self.weapon.fire_cd / max(0.1, self.fire_rate_mult)
        if self.effects["rapid_fire"] > 0:
            cd *= 0.58
        return max(0.045, cd)

    def get_bullet_speed(self) -> float:
        return self.weapon.bullet_speed * self.bullet_speed_mult * self.meta_bulletspd_mul

    def get_bullet_lifetime(self) -> float:
        return max(0.25, self.weapon.bullet_life + self.bullet_life_add)

    def get_move_speed(self) -> float:
        sp = (PLAYER_MAX_SPEED_BASE + self.move_speed_add) * self.meta_move_mul
        if self.effects["speed_boost"] > 0:
            sp *= 1.25
        return sp

    def get_dash_time(self) -> float:
        return DASH_TIME_BASE + self.dash_time_bonus

    def get_dash_cooldown(self) -> float:
        return max(0.35, DASH_COOLDOWN_BASE * self.meta_dash_mul)

    def update(self, dt, game, input_move: Vector2, mouse_world: Vector2, mouse_buttons, keys):
        d = mouse_world - self.pos
        if d.length_squared() > 0.001:
            self.aim_dir = d.normalize()

        self.shoot_timer = max(0.0, self.shoot_timer - dt)
        self.iframes = max(0.0, self.iframes - dt)
        self.dash_cd_timer = max(0.0, self.dash_cd_timer - dt)
        self.dash_timer = max(0.0, self.dash_timer - dt)
        self.burst_gap_timer = max(0.0, self.burst_gap_timer - dt)
        for k in list(self.effects.keys()):
            self.effects[k] = max(0.0, self.effects[k] - dt)

        if keys[pygame.K_SPACE] and self.dash_cd_timer <= 0 and not self.is_dashing():
            dirn = input_move if input_move.length_squared() > 0.01 else self.aim_dir
            self.dash_dir = dirn.normalize() if dirn.length_squared() > 0.01 else Vector2(1, 0)
            self.dash_timer = self.get_dash_time()
            self.dash_cd_timer = self.get_dash_cooldown()
            game.audio_play("dash")

        if self.is_dashing():
            self.vel = self.dash_dir * DASH_SPEED
        else:
            if input_move.length_squared() > 0.001:
                wish = input_move.normalize() * self.get_move_speed()
                self.vel += (wish - self.vel) * (1 - math.exp(-dt * (PLAYER_ACCEL / 500.0)))
            self.vel *= (1.0 - min(dt * PLAYER_FRICTION, 0.65))
            max_sp = self.get_move_speed()
            if self.vel.length() > max_sp:
                self.vel.scale_to_length(max_sp)

        self.pos += self.vel * dt
        arena = game.arena_rect
        self.pos.x = clamp(self.pos.x, arena.left + PLAYER_RADIUS, arena.right - PLAYER_RADIUS)
        self.pos.y = clamp(self.pos.y, arena.top + PLAYER_RADIUS, arena.bottom - PLAYER_RADIUS)

        game.resolve_player_walls()

        self.trigger_held = mouse_buttons[0] or self.auto_fire

        if self.burst_remaining > 0:
            if self.burst_gap_timer <= 0:
                self.burst_remaining -= 1
                self.burst_gap_timer = self.weapon.burst_gap
                game.spawn_player_shot(self)
        else:
            if self.trigger_held and self.shoot_timer <= 0:
                self.shoot_timer = self.get_fire_cooldown()
                if self.weapon.burst_count > 0:
                    game.spawn_player_shot(self)
                    self.burst_remaining = self.weapon.burst_count - 1
                    self.burst_gap_timer = self.weapon.burst_gap
                else:
                    game.spawn_player_shot(self)

    def draw(self, surf, cam):
        flashing = self.invulnerable() and (int(time.time() * 24) % 2 == 0)
        col = (30, 30, 30) if flashing else C_PLAYER

        p = Vector2(self.pos.x - cam.x, self.pos.y - cam.y)
        pygame.draw.circle(surf, col, (int(p.x), int(p.y)), PLAYER_RADIUS)

        circle_outline(surf, self.outline_color, (int(p.x), int(p.y)), PLAYER_RADIUS + 4, 2)

        tip = p + self.aim_dir * (PLAYER_RADIUS + 10)
        left = p + self.aim_dir.rotate(140) * 10
        right = p + self.aim_dir.rotate(-140) * 10
        pygame.draw.polygon(surf, C_PLAYER_ALT, [(int(tip.x), int(tip.y)), (int(left.x), int(left.y)), (int(right.x), int(right.y))])

        if self.effects["shield"] > 0:
            circle_outline(surf, (200, 200, 255), (int(p.x), int(p.y)), PLAYER_RADIUS + 10, 2)

        if self.is_dashing():
            circle_outline(surf, C_ACCENT_2, (int(p.x), int(p.y)), PLAYER_RADIUS + 8, 2)


# =========================================================
# GAME CORE
# =========================================================
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_big = pygame.font.Font(None, 64)
        self.font_med = pygame.font.Font(None, 34)
        self.font_ui = pygame.font.Font(None, 26)
        self.font_small = pygame.font.Font(None, 20)
        self.font_tiny = pygame.font.Font(None, 18)

        self.font_shop_title = pygame.font.Font(None, 42)
        self.font_shop_item = pygame.font.Font(None, 28)
        self.font_shop_desc = pygame.font.Font(None, 22)
        self.font_shop_small = pygame.font.Font(None, 20)

        self.save = SaveManager(SAVE_PATH)
        # Future-proof: ensure save knows about every WEAPONS key (so new weapons never "vanish")
        if self.save.ensure_weapons(list(WEAPONS.keys())):
            self.save.save()
        if self.save.ensure_cosmetics(COSMETICS):
            self.save.save()
        if self.save.ensure_mastery(list(WEAPONS.keys())):
            self.save.save()

        # Audio
        self.audio_enabled = AUDIO_ENABLED_DEFAULT and bool(self.save.settings.get("audio", True))
        self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {
            "shoot": None,
            "hit": None,
            "levelup": None,
            "enemy_shoot": None,
            "dash": None,
            "powerup": None,
            "buy": None,
        }
        self._init_audio()

        # State
        self.state = "menu"  # menu, daily_wheel, weapons, shop, settings, controls, leaderboard, challenges, playing, paused, levelup, gameover
        self.running = True

        # Mode
        self.mode = "endless"  # endless / story

        # Story mode
        self.story_level_index = 1
        self.story_config: Optional[Dict[str, object]] = None
        self.story_start_time = 0.0
        self.story_elapsed = 0.0
        self.story_kills = 0
        self.story_defend_progress = 0.0
        self.story_defend_required = 0.0
        self.story_defend_radius = 0.0
        self.story_defend_point: Optional[Vector2] = None
        self.story_objective_text = ""
        self.story_boss_spawned = False
        self.story_boss_defeated = False
        self.story_visibility_radius: Optional[int] = None
        self.story_hazard_zones: List[Dict[str, object]] = []
        self.story_hazard_accum = 0.0
        self.story_level_complete_stats: Dict[str, int] = {}
        self.story_forced_weapon: Optional[str] = None
        self.story_beacon_pos: Optional[Vector2] = None
        self.story_beacon_hp: Optional[int] = None
        self.story_beacon_max: int = 0
        self.story_beacon_radius: int = 18
        self.story_beacon_iframes = 0.0
        self.boss_rocket_strikes: List[Dict[str, object]] = []
        self.minimap_obstacle_cache: List[Tuple[float, float, float, float]] = []
        self.daily_wheel_angle = 0.0
        self.daily_wheel_spinning = False
        self.daily_wheel_spin_time = 0.0
        self.daily_wheel_spin_duration = 0.0
        self.daily_wheel_spin_start = 0.0
        self.daily_wheel_spin_delta = 0.0
        self.daily_wheel_selected_reward: Optional[Dict[str, object]] = None
        self.daily_wheel_message = ""
        self.daily_wheel_message_timer = 0.0

        self.arena_rect = pygame.Rect(0, 0, ARENA_W, ARENA_H)

        # Camera
        self.cam = Vector2(0, 0)
        self.shake = 0.0
        self.shake_vec = Vector2(0, 0)

        # Entities
        self.player = Player(Vector2(self.arena_rect.centerx, self.arena_rect.centery), weapon_id=self.save.selected_weapon)
        self.player.outline_color = self.get_outline_color()
        self.projectiles: List[Projectile] = []
        self.enemy_projectiles: List[Projectile] = []
        self.enemies: List[EnemyBase] = []
        self.pickups: List[Pickup] = []
        self.particles: List[Particle] = []
        self.float_texts: List[FloatingText] = []

        # Boss state
        self.in_boss_fight = False
        self.boss_alive = False
        self.boss_banner_timer = 0.0
        self.boss_grace_timer = 0.0
        self.run_bonus_coins = 0  # banked during run; added on gameover

        # World
        self.obstacles: List[pygame.Rect] = []
        self._generate_obstacles()

        # Run metrics
        self.start_time = time.time()
        self.survival_time = 0.0
        self.wave = 1
        self.wave_timer = WAVE_TIME_BASE
        self.spawn_timer = 0.0
        self.spawn_interval = SPAWN_RATE_BASE
        self.spawn_burst_remaining = 0
        self.spawn_burst_timer = 0.0
        self.spawn_cluster_anchor = None
        self.spawn_cluster_timer = 0.0
        self.spawn_bias_angle = 0.0
        self.spawn_burst_remaining = 0
        self.spawn_burst_timer = 0.0
        self.spawn_cluster_anchor = None
        self.spawn_cluster_timer = 0.0
        self.spawn_bias_angle = 0.0
        self.spawn_burst_remaining = 0
        self.spawn_burst_timer = 0.0
        self.spawn_cluster_anchor: Optional[Vector2] = None
        self.spawn_cluster_timer = 0.0
        self.spawn_bias_angle = 0.0

        # Difficulty
        self.difficulty = 0.0
        self.diff_eased = 0.0

        # Late-game modifiers
        self.active_modifiers: List[ModifierDef] = []
        self.active_modifier_ids: Set[str] = set()
        self.modifier_last_ids: Set[str] = set()
        self.modifier_cycle_end_wave = LATE_GAME_START_WAVE
        self.pending_enemy_explosions: List[Dict[str, object]] = []

        # Powerup spawn timer
        self.powerup_timer = random.uniform(POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX)

        # UI
        self.menu_buttons: List[Button] = []
        self.menu_challenges_btn: Optional[Button] = None
        self.menu_daily_wheel_btn: Optional[Button] = None
        self.shop_back_btn: Optional[Button] = None
        self.weapon_back_btn: Optional[Button] = None
        self.leaderboard_back_btn: Optional[Button] = None
        self.settings_back_btn: Optional[Button] = None
        self.challenges_back_btn: Optional[Button] = None
        self.story_back_btn: Optional[Button] = None
        self.story_continue_btn: Optional[Button] = None
        self.story_level_buttons: List[Button] = []
        self.story_complete_next_btn: Optional[Button] = None
        self.story_complete_menu_btn: Optional[Button] = None
        self.story_fail_buttons: List[Button] = []
        self.daily_wheel_back_btn: Optional[Button] = None
        self.daily_wheel_spin_btn: Optional[Button] = None
        self.challenges_view = "daily"
        self.challenge_tabs: List[TabButton] = []
        self.pause_buttons: List[Button] = []
        self.gameover_buttons: List[Button] = []

        # Shop tabs/pages
        self.shop_tab = "meta"      # meta / weapons / cosmetics / bundles
        self.shop_page = 0
        self.shop_tabs: List[TabButton] = []
        self.shop_next_btn: Optional[Button] = None
        self.shop_prev_btn: Optional[Button] = None
        self.cosmetics_category = "outline"
        self.cosmetic_tabs: List[TabButton] = []

        # Weapons screen pagination
        self.weapon_page = 0
        self.weapon_next_btn: Optional[Button] = None
        self.weapon_prev_btn: Optional[Button] = None
        self.weapon_notice_text = ""
        self.weapon_notice_timer = 0.0
        self.weapons_view = "weapons"
        self.weapon_tabs: List[TabButton] = []
        self.mastery_error_logged = False

        self.progress_dirty = False
        self.progress_dirty_timer = 0.0
        self.trail_timer = 0.0
        self.counted_game = False

        self.last_run_coins_earned = 0
        self.coins_awarded_this_gameover = False
        self.leaderboard_recorded = False

        self.refresh_challenges()

        self._build_menus()

    # ---------------- Audio ----------------
    def _init_audio(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
        except Exception:
            self.audio_enabled = False
            return

        self.sounds["shoot"] = load_optional_sound("shoot.wav") or generate_tone_sound(740, 0.05, 0.22)
        self.sounds["hit"] = load_optional_sound("hit.wav") or generate_tone_sound(190, 0.06, 0.25)
        self.sounds["levelup"] = load_optional_sound("levelup.wav") or generate_tone_sound(980, 0.12, 0.25)
        self.sounds["enemy_shoot"] = load_optional_sound("enemy_shoot.wav") or generate_tone_sound(420, 0.07, 0.20)
        self.sounds["dash"] = load_optional_sound("dash.wav") or generate_tone_sound(330, 0.08, 0.22)
        self.sounds["powerup"] = load_optional_sound("powerup.wav") or generate_tone_sound(620, 0.10, 0.23)
        self.sounds["buy"] = load_optional_sound("buy.wav") or generate_tone_sound(840, 0.08, 0.22)

    def audio_play(self, name: str):
        if not self.audio_enabled:
            return
        s = self.sounds.get(name)
        if s:
            try:
                s.play()
            except Exception:
                pass

    # ---------------- World ----------------
    def _generate_obstacles(self):
        self.obstacles.clear()
        safe = pygame.Rect(int(self.arena_rect.centerx - 260), int(self.arena_rect.centery - 200), 520, 400)

        for _ in range(OBSTACLE_COUNT):
            w = random.randint(OBSTACLE_MIN[0], OBSTACLE_MAX[0])
            h = random.randint(OBSTACLE_MIN[1], OBSTACLE_MAX[1])
            x = random.randint(self.arena_rect.left + 80, self.arena_rect.right - w - 80)
            y = random.randint(self.arena_rect.top + 80, self.arena_rect.bottom - h - 80)
            r = pygame.Rect(x, y, w, h)
            if r.colliderect(safe):
                continue
            ok = True
            for o in self.obstacles:
                if r.inflate(40, 40).colliderect(o):
                    ok = False
                    break
            if ok:
                self.obstacles.append(r)
        self._cache_minimap_obstacles()

    def _generate_story_obstacles(self, config: Dict[str, object]):
        self.obstacles.clear()
        obstacle_cfg = config.get("obstacles", {})
        count = int(obstacle_cfg.get("count", OBSTACLE_COUNT))
        min_size = obstacle_cfg.get("min", OBSTACLE_MIN)
        max_size = obstacle_cfg.get("max", OBSTACLE_MAX)
        safe = pygame.Rect(int(self.arena_rect.centerx - 260), int(self.arena_rect.centery - 200), 520, 400)

        for _ in range(count):
            w = random.randint(min_size[0], max_size[0])
            h = random.randint(min_size[1], max_size[1])
            x = random.randint(self.arena_rect.left + 80, self.arena_rect.right - w - 80)
            y = random.randint(self.arena_rect.top + 80, self.arena_rect.bottom - h - 80)
            r = pygame.Rect(x, y, w, h)
            if r.colliderect(safe):
                continue
            ok = True
            for o in self.obstacles:
                if r.inflate(40, 40).colliderect(o):
                    ok = False
                    break
            if ok:
                self.obstacles.append(r)
        self._cache_minimap_obstacles()

    def _cache_minimap_obstacles(self):
        """Cache normalized obstacle rects for minimap rendering."""
        self.minimap_obstacle_cache = []
        arena = self.arena_rect
        if arena.width <= 0 or arena.height <= 0:
            return
        for r in self.obstacles:
            fx = (r.x - arena.left) / arena.width
            fy = (r.y - arena.top) / arena.height
            fw = r.w / arena.width
            fh = r.h / arena.height
            self.minimap_obstacle_cache.append((fx, fy, fw, fh))

    # ---------------- UI build ----------------
    def _build_menus(self):
        cx = WIDTH // 2
        bw, bh = 340, 56
        top = 240
        gap = 58

        self.menu_buttons = [
            Button(pygame.Rect(cx - bw // 2, top + gap * 0, bw, bh), "Start Run", self.start_run),
            Button(pygame.Rect(cx - bw // 2, top + gap * 1, bw, bh), "Story Mode", self.open_story_menu),
            Button(pygame.Rect(cx - bw // 2, top + gap * 2, bw, bh), "Weapons", self.open_weapons_screen),
            Button(pygame.Rect(cx - bw // 2, top + gap * 3, bw, bh), "Shop", self.open_shop),
            Button(pygame.Rect(cx - bw // 2, top + gap * 4, bw, bh), "Settings", self.open_settings),
            Button(pygame.Rect(cx - bw // 2, top + gap * 5, bw, bh), "Leaderboard", self.open_leaderboard),
        ]
        self.menu_quit_btn = Button(
            pygame.Rect(20, 18, 54, 48),
            "X",
            self.quit_game
        )
        self.menu_challenges_btn = Button(
            pygame.Rect(WIDTH - 170, 20, 150, 40),
            "Challenges",
            lambda: self.set_state("challenges")
        )
        wheel_size = 72
        wheel_x = WIDTH - wheel_size - 30
        wheel_y = top + gap * 1 - 6
        self.menu_daily_wheel_btn = Button(
            pygame.Rect(wheel_x, wheel_y, wheel_size, wheel_size),
            "",
            self.open_daily_wheel
        )

        self.weapon_back_btn = Button(pygame.Rect(40, HEIGHT - 80, 220, 52), "Back", lambda: self.set_state("menu"))
        self.shop_back_btn = Button(pygame.Rect(40, HEIGHT - 80, 220, 52), "Back", lambda: self.set_state("menu"))
        self.leaderboard_back_btn = Button(pygame.Rect(40, HEIGHT - 80, 220, 52), "Back", lambda: self.set_state("menu"))
        self.settings_back_btn = Button(pygame.Rect(40, HEIGHT - 80, 220, 52), "Back", lambda: self.set_state("menu"))
        self.challenges_back_btn = Button(pygame.Rect(40, HEIGHT - 80, 220, 52), "Back", lambda: self.set_state("menu"))
        self.story_back_btn = Button(pygame.Rect(40, HEIGHT - 80, 220, 52), "Back", lambda: self.set_state("menu"))
        self.story_continue_btn = Button(pygame.Rect(WIDTH - 260, HEIGHT - 80, 220, 52), "Continue", self.start_story_continue)
        self.daily_wheel_back_btn = Button(pygame.Rect(40, HEIGHT - 80, 220, 52), "Back", lambda: self.set_state("menu"))
        self.daily_wheel_spin_btn = Button(pygame.Rect(WIDTH // 2 - 120, HEIGHT - 140, 240, 56), "Spin", self.spin_daily_wheel)

        self.story_level_buttons = []
        story_cols = 2
        story_bw, story_bh = 380, 56
        story_gap_x = 30
        story_gap_y = 18
        total_w = story_cols * story_bw + (story_cols - 1) * story_gap_x
        start_x = WIDTH // 2 - total_w // 2
        start_y = 220
        for idx, level in enumerate(LEVELS):
            col = idx % story_cols
            row = idx // story_cols
            rect = pygame.Rect(
                start_x + col * (story_bw + story_gap_x),
                start_y + row * (story_bh + story_gap_y),
                story_bw,
                story_bh,
            )
            btn = Button(rect, f"Level {idx + 1}: {level['name']}", callback=lambda i=idx + 1: self.start_story_level(i))
            self.story_level_buttons.append(btn)

        self.story_complete_next_btn = Button(pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 + 120, 340, 56),
                                              "Next Level", self.start_next_story_level)
        self.story_complete_menu_btn = Button(pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 + 190, 340, 56),
                                              "Back to Menu", lambda: self.set_state("menu"))

        # Weapons pagination buttons (bottom-right)
        self.weapon_prev_btn = Button(pygame.Rect(WIDTH - 300, HEIGHT - 80, 120, 52), "Prev", lambda: self.change_weapon_page(-1))
        self.weapon_next_btn = Button(pygame.Rect(WIDTH - 170, HEIGHT - 80, 120, 52), "Next", lambda: self.change_weapon_page(+1))

        py = HEIGHT // 2 - 30
        self.pause_buttons = [
            Button(pygame.Rect(cx - bw // 2, py, bw, bh), "Resume", lambda: self.set_state("playing")),
            Button(pygame.Rect(cx - bw // 2, py + 70, bw, bh), "Restart", self.start_run),
            Button(pygame.Rect(cx - bw // 2, py + 140, bw, bh), "Quit to Menu", lambda: self.set_state("menu")),
        ]

        self.gameover_buttons = [
            Button(pygame.Rect(cx - bw // 2, py + 60, bw, bh), "Restart (R)", self.start_run, hotkey=pygame.K_r),
            Button(pygame.Rect(cx - bw // 2, py + 130, bw, bh), "Menu", lambda: self.set_state("menu")),
        ]
        self.story_fail_buttons = [
            Button(pygame.Rect(cx - bw // 2, py + 60, bw, bh), "Retry (R)", self.retry_story_level, hotkey=pygame.K_r),
            Button(pygame.Rect(cx - bw // 2, py + 130, bw, bh), "Menu", lambda: self.set_state("menu")),
        ]

        # Shop tabs
        tab_y = 120
        tab_w = 170
        tab_h = 44
        tab_gap = 12
        start_x = (WIDTH - (tab_w * 4 + tab_gap * 3)) // 2

        def set_tab(tid: str):
            self.shop_tab = tid
            self.shop_page = 0
            if tid == "cosmetics":
                self.cosmetics_category = "outline"

        self.shop_tabs = [
            TabButton(pygame.Rect(start_x + (tab_w + tab_gap) * 0, tab_y, tab_w, tab_h), "META", set_tab, "meta"),
            TabButton(pygame.Rect(start_x + (tab_w + tab_gap) * 1, tab_y, tab_w, tab_h), "WEAPONS", set_tab, "weapons"),
            TabButton(pygame.Rect(start_x + (tab_w + tab_gap) * 2, tab_y, tab_w, tab_h), "COSMETICS", set_tab, "cosmetics"),
            TabButton(pygame.Rect(start_x + (tab_w + tab_gap) * 3, tab_y, tab_w, tab_h), "BUNDLES", set_tab, "bundles"),
        ]

        self.shop_prev_btn = Button(pygame.Rect(WIDTH - 300, HEIGHT - 80, 120, 52), "Prev", lambda: self.change_shop_page(-1))
        self.shop_next_btn = Button(pygame.Rect(WIDTH - 170, HEIGHT - 80, 120, 52), "Next", lambda: self.change_shop_page(+1))

        # Cosmetics tabs
        ctab_y = 170
        ctab_w = 160
        ctab_h = 36
        ctab_gap = 12
        ctab_start_x = (WIDTH - (ctab_w * 4 + ctab_gap * 3)) // 2

        def set_cosmetic_category(category: str):
            self.cosmetics_category = category
            self.shop_page = 0

        self.cosmetic_tabs = [
            TabButton(pygame.Rect(ctab_start_x + (ctab_w + ctab_gap) * 0, ctab_y, ctab_w, ctab_h), "OUTLINE", set_cosmetic_category, "outline"),
            TabButton(pygame.Rect(ctab_start_x + (ctab_w + ctab_gap) * 1, ctab_y, ctab_w, ctab_h), "BULLETS", set_cosmetic_category, "bullet"),
            TabButton(pygame.Rect(ctab_start_x + (ctab_w + ctab_gap) * 2, ctab_y, ctab_w, ctab_h), "TRAILS", set_cosmetic_category, "trail"),
            TabButton(pygame.Rect(ctab_start_x + (ctab_w + ctab_gap) * 3, ctab_y, ctab_w, ctab_h), "EXPLOSION", set_cosmetic_category, "explosion"),
        ]

        # Weapons tabs
        wtab_y = 108
        wtab_w = 190
        wtab_h = 40
        wtab_gap = 14
        wtab_start_x = (WIDTH - (wtab_w * 2 + wtab_gap)) // 2
        def set_weapon_view(view: str):
            self.weapons_view = view
            self.weapon_page = 0
        self.weapon_tabs = [
            TabButton(pygame.Rect(wtab_start_x, wtab_y, wtab_w, wtab_h), "WEAPONS", set_weapon_view, "weapons"),
            TabButton(pygame.Rect(wtab_start_x + wtab_w + wtab_gap, wtab_y, wtab_w, wtab_h), "MASTERY", set_weapon_view, "mastery"),
        ]

        # Challenges tabs
        ctab_y = 168
        ctab_w = 200
        ctab_h = 40
        ctab_gap = 14
        ctab_start_x = (WIDTH - (ctab_w * 2 + ctab_gap)) // 2

        def set_challenges_view(view: str):
            self.challenges_view = view

        self.challenge_tabs = [
            TabButton(pygame.Rect(ctab_start_x, ctab_y, ctab_w, ctab_h), "DAILY", set_challenges_view, "daily"),
            TabButton(pygame.Rect(ctab_start_x + ctab_w + ctab_gap, ctab_y, ctab_w, ctab_h), "WEEKLY", set_challenges_view, "weekly"),
        ]

    def set_state(self, st: str):
        self.state = st

    def quit_game(self):
        self.running = False

    # ---------------- Shop helpers ----------------
    def _shop_items_for_tab(self) -> List[ShopItemDef]:
        if self.shop_tab == "meta":
            return [it for it in SHOP_ITEMS if it.kind == "meta"]
        if self.shop_tab == "weapons":
            return [it for it in SHOP_ITEMS if it.kind == "weapon"]
        return []

    def _shop_rows_per_page(self, box: pygame.Rect) -> int:
        row_h = 72
        gap = 12
        step = row_h + gap
        usable = max(1, box.h - 24)
        return max(1, usable // step)

    # ---------------- Shop logic ----------------
    def open_shop(self):
        self.shop_tab = "meta"
        self.shop_page = 0
        if self.save.ensure_cosmetics(COSMETICS):
            self.save.save()
        self.set_state("shop")

    def open_settings(self):
        self.set_state("settings")

    def open_leaderboard(self):
        self.set_state("leaderboard")

    def open_challenges(self):
        self.challenges_view = "daily"
        self.set_state("challenges")

    def open_daily_wheel(self):
        self.daily_wheel_message = ""
        self.daily_wheel_message_timer = 0.0
        self.set_state("daily_wheel")

    # ---------------- Story Mode ----------------
    def open_story_menu(self):
        self.set_state("story_menu")

    def story_levels_count(self) -> int:
        return len(LEVELS)

    def get_unlocked_story_level(self) -> int:
        return max(1, min(int(self.save.story_unlocked_level), self.story_levels_count()))

    def get_story_continue_level(self) -> int:
        unlocked = self.get_unlocked_story_level()
        last = max(1, min(int(self.save.story_last_level), self.story_levels_count()))
        return last if last <= unlocked else unlocked

    def start_story_continue(self):
        self.start_story_level(self.get_story_continue_level())

    def start_next_story_level(self):
        if self.story_level_index < self.story_levels_count():
            self.start_story_level(self.story_level_index + 1)
        else:
            self.set_state("menu")

    def retry_story_level(self):
        self.start_story_level(self.story_level_index)

    def start_story_level(self, level_index: int):
        level_index = max(1, min(level_index, self.story_levels_count()))
        config = LEVELS[level_index - 1]
        self.mode = "story"
        self.story_level_index = level_index
        self.story_config = config
        self.set_state("playing")

        size = config.get("arena_size", (ARENA_W, ARENA_H))
        self.arena_rect = pygame.Rect(
            (ARENA_W - size[0]) // 2,
            (ARENA_H - size[1]) // 2,
            size[0],
            size[1],
        )

        self.save.ensure_weapons(list(WEAPONS.keys()))
        forced_weapon = config.get("special", {}).get("forced_weapon")
        self.story_forced_weapon = forced_weapon
        weapon_id = forced_weapon or self.save.selected_weapon
        if not self.save.weapon_unlocks.get(weapon_id, False):
            weapon_id = "pistol"

        self.player = Player(Vector2(self.arena_rect.centerx, self.arena_rect.centery), weapon_id=weapon_id)
        self.apply_meta_upgrades_to_player()
        self.player.outline_color = self.get_outline_color()
        self.counted_game = False

        self.projectiles.clear()
        self.enemy_projectiles.clear()
        self.enemies.clear()
        self.pickups.clear()
        self.particles.clear()
        self.float_texts.clear()

        self._generate_story_obstacles(config)

        self.start_time = time.time()
        self.survival_time = 0.0
        self.wave = 1
        self.wave_timer = WAVE_TIME_BASE
        self.spawn_timer = 0.0
        self.spawn_interval = float(config.get("spawn", {}).get("interval", SPAWN_RATE_BASE))
        self.spawn_burst_remaining = 0
        self.spawn_burst_timer = 0.0
        self.spawn_cluster_anchor = None
        self.spawn_cluster_timer = 0.0
        self.spawn_bias_angle = 0.0

        self.difficulty = float(config.get("difficulty", 0.35))
        self.diff_eased = self.difficulty

        self.shake = 0.0
        self.powerup_timer = random.uniform(POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX)

        self.last_run_coins_earned = 0
        self.coins_awarded_this_gameover = False
        self.run_bonus_coins = 0
        self.leaderboard_recorded = False

        self.daily_wheel_angle = 0.0
        self.daily_wheel_spinning = False
        self.daily_wheel_spin_time = 0.0
        self.daily_wheel_spin_duration = 0.0
        self.daily_wheel_spin_start = 0.0
        self.daily_wheel_spin_delta = 0.0
        self.daily_wheel_selected_reward: Optional[Dict[str, object]] = None
        self.daily_wheel_message = ""
        self.daily_wheel_message_timer = 0.0

        self.in_boss_fight = False
        self.boss_alive = False
        self.boss_banner_timer = 0.0
        self.boss_grace_timer = 0.0

        self.active_modifiers = []
        self.active_modifier_ids = set()
        self.modifier_last_ids = set()
        self.modifier_cycle_end_wave = LATE_GAME_START_WAVE
        self.pending_enemy_explosions = []

        self.active_modifiers = []
        self.active_modifier_ids = set()
        self.modifier_last_ids = set()
        self.modifier_cycle_end_wave = LATE_GAME_START_WAVE
        self.pending_enemy_explosions = []

        self.active_modifiers = []
        self.active_modifier_ids = set()
        self.modifier_last_ids = set()
        self.modifier_cycle_end_wave = LATE_GAME_START_WAVE
        self.pending_enemy_explosions = []

        self.story_start_time = time.time()
        self.story_elapsed = 0.0
        self.story_kills = 0
        self.story_defend_progress = 0.0
        win_cfg = config.get("win", {})
        self.story_defend_required = float(win_cfg.get("seconds", 0)) if win_cfg.get("type") == "defend" else 0.0
        self.story_defend_radius = float(win_cfg.get("radius", 0)) if win_cfg.get("type") == "defend" else 0.0
        self.story_objective_text = str(config.get("objective", ""))
        self.story_boss_spawned = False
        self.story_boss_defeated = False
        self.story_visibility_radius = config.get("special", {}).get("visibility_radius")
        self.story_hazard_zones = []
        self.story_hazard_accum = 0.0
        self.story_beacon_pos = None
        self.story_beacon_hp = None
        self.story_beacon_max = 0
        self.story_beacon_radius = int(config.get("special", {}).get("beacon_radius", 18))
        self.story_beacon_iframes = 0.0
        self.boss_rocket_strikes = []

        objective_point = config.get("special", {}).get("objective_point")
        if objective_point == "center":
            self.story_defend_point = Vector2(self.arena_rect.centerx, self.arena_rect.centery)
        else:
            self.story_defend_point = None

        beacon_hp = config.get("special", {}).get("beacon_hp")
        if beacon_hp and self.story_defend_point:
            # Story level beacon: enemies target this instead of the player.
            self.story_beacon_pos = Vector2(self.story_defend_point)
            self.story_beacon_hp = int(beacon_hp)
            self.story_beacon_max = int(beacon_hp)

        hazard_count = int(config.get("special", {}).get("hazard_count", 0))
        hazard_sizes = list(config.get("special", {}).get("hazard_sizes", []))
        hazard_dps = list(config.get("special", {}).get("hazard_dps", []))
        if hazard_count > 0 and hazard_sizes:
            # Randomize hazard zones each Level 5 start; avoid obstacles/overlap.
            max_attempts = 80
            for _ in range(hazard_count):
                size = random.choice(hazard_sizes)
                w, h = int(size[0]), int(size[1])
                placed = False
                for _ in range(max_attempts):
                    x = random.randint(self.arena_rect.left, self.arena_rect.right - w)
                    y = random.randint(self.arena_rect.top, self.arena_rect.bottom - h)
                    rect_abs = pygame.Rect(x, y, w, h)
                    if any(rect_abs.colliderect(obs) for obs in self.obstacles):
                        continue
                    if any(rect_abs.colliderect(hz["rect"]) for hz in self.story_hazard_zones):
                        continue
                    dps = float(random.choice(hazard_dps)) if hazard_dps else 1.0
                    self.story_hazard_zones.append({"rect": rect_abs, "dps": dps})
                    placed = True
                    break
                if not placed:
                    break

        self.save.story_last_level = level_index
        self.save.save()

    def unlock_next_story_level(self):
        unlocked = self.get_unlocked_story_level()
        if self.story_level_index >= unlocked and self.story_level_index < self.story_levels_count():
            self.save.story_unlocked_level = self.story_level_index + 1
        if self.story_level_index >= self.story_levels_count():
            self.save.story_unlocked_level = self.story_levels_count()
        self.save.story_last_level = min(self.story_level_index + 1, self.story_levels_count())
        self.save.save()

    def story_objective_progress_text(self) -> str:
        if not self.story_config:
            return ""
        win_cfg = self.story_config.get("win", {})
        win_type = win_cfg.get("type")
        if win_type == "survive":
            seconds = int(win_cfg.get("seconds", 0))
            return f"{self.story_objective_text} ({int(min(self.story_elapsed, seconds))}/{seconds}s)"
        if win_type == "kills":
            count = int(win_cfg.get("count", 0))
            return f"{self.story_objective_text} ({min(self.story_kills, count)}/{count})"
        if win_type == "defend":
            required = int(self.story_defend_required)
            current = int(min(self.story_defend_progress, self.story_defend_required))
            return f"{self.story_objective_text} ({current}/{required}s)"
        if win_type == "boss":
            return self.story_objective_text
        return self.story_objective_text

    def beacon_active(self) -> bool:
        return self.mode == "story" and self.story_beacon_pos is not None and self.story_beacon_hp is not None

    def enemy_target_pos(self) -> Vector2:
        if self.beacon_active():
            return Vector2(self.story_beacon_pos)
        return Vector2(self.player.pos)

    def boss_specials_active(self) -> bool:
        return self.mode == "story" and self.story_level_index == 6

    def modifier_phase(self) -> Optional[str]:
        if self.mode != "endless":
            return None
        if self.wave >= LATE_LATE_START_WAVE:
            return "late"
        if self.wave >= MID_LATE_START_WAVE:
            return "mid"
        if self.wave >= LATE_GAME_START_WAVE:
            return "early"
        return None

    def is_modifier_active(self, modifier_id: str) -> bool:
        return modifier_id in self.active_modifier_ids

    def enemy_turn_speed_mult(self) -> float:
        return 1.25 if self.is_modifier_active("turning_speed") else 1.0

    def modifier_waves_remaining(self) -> int:
        if not self.active_modifiers:
            return 0
        return max(0, self.modifier_cycle_end_wave - self.wave)

    def _modifier_candidates(self, phase: str) -> List[ModifierDef]:
        if phase == "early":
            tiers = {"early"}
        elif phase == "mid":
            tiers = {"early", "mid"}
        else:
            tiers = {"early", "mid", "late"}
        return [m for m in LATE_GAME_MODIFIERS if any(t in tiers for t in m.tiers)]

    def _modifier_phase_weight(self, modifier: ModifierDef, phase: str) -> float:
        if phase == "early":
            return 1.0
        if phase == "mid":
            return 1.25 if "mid" in modifier.tiers else 1.0
        if "late" in modifier.tiers:
            return 1.4
        if "mid" in modifier.tiers:
            return 1.2
        return 1.0

    def _pick_modifiers(self, phase: str, avoid: Set[str]) -> List[ModifierDef]:
        candidates = self._modifier_candidates(phase)
        chosen: List[ModifierDef] = []
        count = 1
        if phase == "late":
            count = random.randint(MODIFIER_MIN_STACK, MODIFIER_MAX_STACK)
        for _ in range(count):
            pool = [m for m in candidates if m.id not in avoid and m.id not in {c.id for c in chosen}]
            if not pool:
                pool = [m for m in candidates if m.id not in {c.id for c in chosen}]
            weights = {m.id: m.weight * self._modifier_phase_weight(m, phase) for m in pool}
            pick_id = weighted_choice(weights)
            pick = next(m for m in pool if m.id == pick_id)
            chosen.append(pick)
        return chosen

    def advance_late_game_modifiers(self):
        phase = self.modifier_phase()
        if phase is None:
            self.active_modifiers = []
            self.active_modifier_ids = set()
            return
        if self.active_modifiers and self.wave < self.modifier_cycle_end_wave:
            return
        cycle_len = random.randint(MODIFIER_WAVE_MIN, MODIFIER_WAVE_MAX)
        self.modifier_cycle_end_wave = self.wave + cycle_len
        new_mods = self._pick_modifiers(phase, self.modifier_last_ids)
        self.active_modifiers = new_mods
        self.active_modifier_ids = {m.id for m in new_mods}
        self.modifier_last_ids = {m.id for m in new_mods}
        self.spawn_bias_angle = random.uniform(0, math.tau)
        self.spawn_cluster_anchor = None
        self.spawn_cluster_timer = 0.0
        self.spawn_burst_remaining = 0
        self.spawn_burst_timer = 0.0
        if self.is_modifier_active("enemy_dashes"):
            for e in self.enemies:
                if not isinstance(e, (Boss, Dasher)):
                    e.extra_dash_cd = random.uniform(0.6, 2.4)
        if self.is_modifier_active("revive_once"):
            for e in self.enemies:
                if not isinstance(e, Boss):
                    e.revives_remaining = max(e.revives_remaining, 1)

    def enemy_speed_multiplier(self, enemy: EnemyBase) -> float:
        if isinstance(enemy, Boss):
            return 1.0
        mult = 1.0
        if self.is_modifier_active("enemy_accel"):
            mult *= 1.0 + min(0.6, enemy.age * 0.02)
        if self.is_modifier_active("speed_ramp"):
            wave_progress = 1.0 - clamp(self.wave_timer / max(0.1, WAVE_TIME_BASE), 0.0, 1.0)
            mult *= 1.0 + 0.45 * wave_progress
        return mult

    def enemy_damage_multiplier(self, enemy: EnemyBase) -> float:
        if isinstance(enemy, Boss) or not self.is_modifier_active("resist_over_time"):
            return 1.0
        resistance = min(0.25, enemy.age * 0.01)
        return 1.0 - resistance

    def apply_enemy_damage(self, enemy: EnemyBase, damage: int, knock_dir: Vector2, knockback: float, weapon_id: Optional[str] = None):
        scaled = max(1, int(round(damage * self.enemy_damage_multiplier(enemy))))
        enemy.take_damage(scaled, knock_dir, knockback, weapon_id=weapon_id, from_player=True)
        return scaled

    def damage_beacon(self, amount: int):
        if not self.beacon_active():
            return
        if self.story_beacon_iframes > 0:
            return
        self.story_beacon_hp = max(0, int(self.story_beacon_hp) - int(amount))
        self.story_beacon_iframes = 0.55  # brief grace so it doesn't melt instantly

    def spawn_boss_rocket_strike(self, pos: Vector2, telegraph_time: float = 0.7, fall_time: float = 0.35, radius: float = 90.0):
        # Boss special: telegraphed rocket strike.
        self.boss_rocket_strikes.append({
            "pos": Vector2(pos),
            "state": "telegraph",
            "timer": telegraph_time,
            "telegraph_time": telegraph_time,
            "fall_time": fall_time,
            "radius": radius,
        })

    def update_boss_rocket_strikes(self, dt: float):
        if not self.boss_rocket_strikes:
            return
        for strike in list(self.boss_rocket_strikes):
            strike["timer"] -= dt
            if strike["state"] == "telegraph" and strike["timer"] <= 0:
                strike["state"] = "fall"
                strike["timer"] = float(strike.get("fall_time", 0.35))
                strike["fall_total"] = strike["timer"]
            elif strike["state"] == "fall" and strike["timer"] <= 0:
                strike["state"] = "explode"
                strike["timer"] = 0.22
                # Apply damage once on explosion.
                d2 = (self.player.pos - strike["pos"]).length_squared()
                rad = float(strike["radius"])
                if d2 <= rad * rad:
                    self.damage_player(2)
                    knock = (self.player.pos - strike["pos"])
                    if knock.length_squared() > 0.001:
                        self.player.vel += knock.normalize() * 360
            elif strike["state"] == "explode" and strike["timer"] <= 0:
                self.boss_rocket_strikes.remove(strike)

    def draw_boss_rocket_strikes(self):
        if not self.boss_rocket_strikes:
            return
        cam = self.cam + self.shake_vec
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for strike in self.boss_rocket_strikes:
            pos = strike["pos"]
            screen = (int(pos.x - cam.x), int(pos.y - cam.y))
            radius = int(strike["radius"])
            if strike["state"] == "telegraph":
                pygame.draw.circle(overlay, (255, 90, 110, 70), screen, radius, 0)
                pygame.draw.circle(overlay, (255, 120, 140, 170), screen, radius, 2)
            elif strike["state"] == "fall":
                fall_total = float(strike.get("fall_total", 0.35))
                time_left = max(0.0, float(strike["timer"]))
                imminent = clamp(1.0 - (time_left / fall_total), 0.0, 1.0)
                pulse_t = pygame.time.get_ticks() / 1000.0
                pulse = 0.5 + 0.5 * math.sin(pulse_t * 10.0 + imminent * 3.0)
                pulse_alpha = int(120 + 100 * pulse * (0.4 + 0.6 * imminent))
                pulse_radius = int(radius + 8 + 12 * pulse * (0.4 + 0.6 * imminent))
                top = (screen[0], screen[1] - 120)
                pygame.draw.line(overlay, (255, 130, 150, 200), top, screen, 4)
                pygame.draw.polygon(overlay, (255, 130, 150, 220),
                                    [(screen[0] - 10, screen[1] - 10),
                                     (screen[0] + 10, screen[1] - 10),
                                     (screen[0], screen[1] + 12)])
                pygame.draw.circle(overlay, (255, 120, 140, 200), screen, radius + 6, 3)
                pygame.draw.circle(overlay, (255, 150, 170, pulse_alpha), screen, pulse_radius, 4)
            else:
                pygame.draw.circle(overlay, (255, 120, 140, 140), screen, radius, 0)
                pygame.draw.circle(overlay, (255, 160, 180, 220), screen, radius, 2)
        self.screen.blit(overlay, (0, 0))

    # ---------------- Cosmetics ----------------
    def get_cosmetic(self, cosmetic_id: str) -> Optional[CosmeticDef]:
        return COSMETICS_BY_ID.get(cosmetic_id)

    def get_equipped_cosmetic(self, category: str) -> CosmeticDef:
        cosmetic_id = self.save.cosmetics_equipped.get(category)
        cosmetic = self.get_cosmetic(cosmetic_id) if cosmetic_id else None
        if cosmetic:
            return cosmetic
        fallback_id = DEFAULT_COSMETICS[category]
        return COSMETICS_BY_ID[fallback_id]

    def get_outline_color(self) -> Tuple[int, int, int]:
        return self.get_equipped_cosmetic("outline").color

    def get_bullet_color(self) -> Tuple[int, int, int]:
        return self.get_equipped_cosmetic("bullet").color

    def get_trail_cosmetic(self) -> CosmeticDef:
        return self.get_equipped_cosmetic("trail")

    def get_explosion_color(self) -> Tuple[int, int, int]:
        return self.get_equipped_cosmetic("explosion").color

    def buy_cosmetic(self, cosmetic: CosmeticDef):
        if cosmetic.bundle_only:
            return
        if self.save.cosmetics_unlocked.get(cosmetic.id, False):
            return
        if self.save.coins < cosmetic.cost:
            return
        self.save.coins -= cosmetic.cost
        self.save.cosmetics_unlocked[cosmetic.id] = True
        self.save.cosmetics_equipped[cosmetic.category] = cosmetic.id
        self.save.save()
        self.audio_play("buy")

    def equip_cosmetic(self, cosmetic: CosmeticDef):
        if not self.save.cosmetics_unlocked.get(cosmetic.id, False):
            return
        self.save.cosmetics_equipped[cosmetic.category] = cosmetic.id
        self.save.save()
        self.audio_play("buy")

    def unequip_cosmetic(self, category: str):
        default_id = DEFAULT_COSMETICS.get(category)
        if not default_id:
            return
        self.save.cosmetics_equipped[category] = default_id
        self.save.cosmetics_unlocked[default_id] = True
        self.save.save()
        self.audio_play("buy")

    # ---------------- Bundles ----------------
    def resolve_bundle_items(self, bundle: BundleDef) -> Tuple[List[str], List[str], List[str]]:
        available_weapons = [
            wid for wid in WEAPONS.keys() if not self.save.weapon_unlocks.get(wid, False)
        ]
        resolved_weapons: List[str] = []
        remaining_pool = [wid for wid in available_weapons if wid not in bundle.weapons]
        for wid in bundle.weapons:
            if not self.save.weapon_unlocks.get(wid, False):
                if wid not in resolved_weapons:
                    resolved_weapons.append(wid)
                if wid in remaining_pool:
                    remaining_pool.remove(wid)
                continue
            replacement = remaining_pool.pop(0) if remaining_pool else None
            if replacement:
                resolved_weapons.append(replacement)
        return resolved_weapons, list(bundle.meta), list(bundle.cosmetics)

    def cosmetic_bundle_value(self, cosmetic: CosmeticDef) -> int:
        if cosmetic.cost > 0:
            return cosmetic.cost
        if cosmetic.bundle_only:
            return BUNDLE_ONLY_COSMETIC_VALUE
        return 0

    def bundle_base_value(self, bundle: BundleDef) -> int:
        total = 0
        weapons, meta, cosmetics = self.resolve_bundle_items(bundle)
        for wid in weapons:
            item = SHOP_ITEMS_BY_WEAPON.get(wid)
            if item:
                total += item.base_cost
        for mid in meta:
            item = SHOP_ITEMS_BY_ID.get(mid)
            if item:
                total += item.base_cost
        for cid in cosmetics:
            cosmetic = COSMETICS_BY_ID.get(cid)
            if cosmetic:
                total += self.cosmetic_bundle_value(cosmetic)
        return total

    def bundle_owned_value(self, bundle: BundleDef) -> int:
        owned = 0
        weapons, meta, cosmetics = self.resolve_bundle_items(bundle)
        for wid in weapons:
            if self.save.weapon_unlocks.get(wid, False):
                item = SHOP_ITEMS_BY_WEAPON.get(wid)
                if item:
                    owned += item.base_cost
        for mid in meta:
            if int(self.save.shop_levels.get(mid, 0)) > 0:
                item = SHOP_ITEMS_BY_ID.get(mid)
                if item:
                    owned += item.base_cost
        for cid in cosmetics:
            if self.save.cosmetics_unlocked.get(cid, False):
                cosmetic = COSMETICS_BY_ID.get(cid)
                if cosmetic:
                    owned += self.cosmetic_bundle_value(cosmetic)
        return owned

    def bundle_price(self, bundle: BundleDef) -> int:
        base_value = self.bundle_base_value(bundle)
        owned_value = self.bundle_owned_value(bundle)
        remaining = max(0, base_value - owned_value)
        return int(remaining * (1.0 - bundle.discount))

    def bundle_is_owned(self, bundle: BundleDef) -> bool:
        if self.save.bundles_purchased.get(bundle.id, False):
            return True
        base_value = self.bundle_base_value(bundle)
        if base_value <= 0:
            return True
        return self.bundle_owned_value(bundle) >= base_value

    def buy_bundle(self, bundle: BundleDef):
        if self.bundle_is_owned(bundle):
            return
        cost = self.bundle_price(bundle)
        if cost <= 0 or self.save.coins < cost:
            return
        self.save.coins -= cost
        weapons, meta, cosmetics = self.resolve_bundle_items(bundle)
        for wid in weapons:
            self.save.weapon_unlocks[wid] = True
        for mid in meta:
            item = SHOP_ITEMS_BY_ID.get(mid)
            if not item:
                continue
            current = int(self.save.shop_levels.get(mid, 0))
            self.save.shop_levels[mid] = min(item.max_level, current + 1)
        for cid in cosmetics:
            self.save.cosmetics_unlocked[cid] = True
        self.save.bundles_purchased[bundle.id] = True
        self.save.save()
        self.audio_play("buy")

    # ---------------- Challenges ----------------
    def _daily_key(self) -> str:
        return time.strftime("%Y-%j", time.localtime())

    def _weekly_key(self) -> str:
        return time.strftime("%Y-%V", time.localtime())

    def refresh_challenges(self):
        daily_key = self._daily_key()
        weekly_key = self._weekly_key()
        changed = False
        if self.save.daily_challenges.get("key") != daily_key:
            self.save.daily_challenges = {
                "key": daily_key,
                "generated_at": int(time.time()),
                "items": self._generate_daily_challenges(daily_key),
            }
            changed = True
        if self.save.weekly_challenges.get("key") != weekly_key:
            self.save.weekly_challenges = {
                "key": weekly_key,
                "generated_at": int(time.time()),
                "items": self._generate_weekly_challenges(weekly_key),
            }
            changed = True
        if changed:
            self.save.save()

    def _generate_daily_challenges(self, key: str) -> List[Dict[str, object]]:
        rng = random.Random(key)
        weapon_ids = list(WEAPONS.keys())
        candidates = [
            {"id": "daily_kills", "name": "Clear the Field", "desc": "Defeat 60 enemies.", "target": 60, "reward": 20, "metric": "kills"},
            {"id": "daily_waves", "name": "Hold the Line", "desc": "Survive 9 waves.", "target": 9, "reward": 10, "metric": "waves"},
            {"id": "daily_run", "name": "Warm-Up Run", "desc": "Complete 2 runs.", "target": 2, "reward": 5, "metric": "runs"},
        ]
        weapon_pick = rng.choice(weapon_ids)
        weapon_name = WEAPONS[weapon_pick].name
        candidates.append({
            "id": f"daily_weapon_{weapon_pick}",
            "name": f"Weapon Focus: {weapon_name}",
            "desc": f"Defeat 38 enemies using {weapon_name}.",
            "target": 38,
            "reward": 25,
            "metric": "weapon_kills",
            "weapon_id": weapon_pick,
        })
        count = rng.randint(1, 3)
        picks = rng.sample(candidates, count)
        return [
            {
                **c,
                "progress": 0,
                "claimed": False,
            }
            for c in picks
        ]

    def _generate_weekly_challenges(self, key: str) -> List[Dict[str, object]]:
        rng = random.Random(key)
        candidates = [
            {"id": "weekly_boss", "name": "Boss Hunter", "desc": "Defeat 5 bosses.", "target": 5, "reward": 110, "metric": "boss_kills"},
            {"id": "weekly_damage", "name": "Heavy Damage", "desc": "Deal 13500 total damage.", "target": 13500, "reward": 100, "metric": "damage"},
            {"id": "weekly_wave", "name": "Deep Run", "desc": "Reach wave 30.", "target": 30, "reward": 120, "metric": "high_wave"},
            {"id": "weekly_runs", "name": "Weekend Warrior", "desc": "Complete 12 runs.", "target": 12, "reward": 70, "metric": "runs"},
        ]
        count = rng.randint(1, 2)
        picks = rng.sample(candidates, count)
        return [
            {
                **c,
                "progress": 0,
                "claimed": False,
            }
            for c in picks
        ]

    def update_challenges(self, metric: str, amount: int, weapon_id: Optional[str] = None, absolute: bool = False):
        changed = False
        for bucket in (self.save.daily_challenges.get("items", []), self.save.weekly_challenges.get("items", [])):
            for item in bucket:
                if item.get("metric") != metric:
                    continue
                if metric == "weapon_kills" and item.get("weapon_id") != weapon_id:
                    continue
                if absolute:
                    item["progress"] = max(int(item.get("progress", 0)), int(amount))
                else:
                    item["progress"] = int(item.get("progress", 0)) + int(amount)
                if not item.get("claimed") and item["progress"] >= int(item.get("target", 0)):
                    item["claimed"] = True
                    reward = int(item.get("reward", 0))
                    self.save.coins += reward
                    self.float_texts.append(FloatingText(self.player.pos + Vector2(0, -34), f"+{reward} COINS", C_COIN, life=1.0))
                changed = True
        if changed:
            self.progress_dirty = True

    def time_until_reset(self, kind: str) -> str:
        now = time.time()
        if kind == "daily":
            tomorrow = time.localtime(now + 86400)
            reset = time.mktime((tomorrow.tm_year, tomorrow.tm_mon, tomorrow.tm_mday, 0, 0, 0, 0, 0, -1))
        else:
            now_local = time.localtime(now)
            days_ahead = (7 - now_local.tm_wday) % 7
            if days_ahead == 0:
                days_ahead = 7
            next_week = time.localtime(now + days_ahead * 86400)
            reset = time.mktime((next_week.tm_year, next_week.tm_mon, next_week.tm_mday, 0, 0, 0, 0, 0, -1))
        remaining = max(0, int(reset - now))
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        return f"{hours}h {minutes}m"

    # ---------------- Mastery ----------------
    def update_mastery(self, weapon_id: str, hits: int = 0, kills: int = 0, wins: int = 0):
        if weapon_id not in WEAPONS:
            return
        stats, changed = self.save.ensure_mastery_entry(weapon_id)
        if changed:
            self.save.save()
        stats["hits"] = int(stats.get("hits", 0)) + hits
        stats["total_kills"] = int(stats.get("total_kills", 0)) + kills
        stats["total_wins"] = int(stats.get("total_wins", 0)) + wins

        if stats.get("level", 0) < MAX_MASTERY_LEVEL:
            stats["level_kills"] = int(stats.get("level_kills", 0)) + kills
            stats["level_wins"] = int(stats.get("level_wins", 0)) + wins

        leveled = False
        level = int(stats.get("level", 0))
        if level < MAX_MASTERY_LEVEL:
            req_kills, req_wins = mastery_requirements(level + 1)
            stats["req_kills"] = req_kills
            stats["req_wins"] = req_wins
            if stats["level_kills"] >= req_kills and stats["level_wins"] >= req_wins:
                stats["level"] = level + 1
                stats["level_kills"] = 0
                stats["level_wins"] = 0
                leveled = True
                if stats["level"] < MAX_MASTERY_LEVEL:
                    next_req_kills, next_req_wins = mastery_requirements(stats["level"] + 1)
                    stats["req_kills"] = next_req_kills
                    stats["req_wins"] = next_req_wins
        if leveled:
            self.float_texts.append(FloatingText(self.player.pos + Vector2(0, -50), f"{WEAPONS[weapon_id].name} Mastery +1", C_ACCENT))
        self.progress_dirty = True

    def change_shop_page(self, delta: int):
        self.shop_page = max(0, self.shop_page + delta)

    def shop_cost(self, item: ShopItemDef) -> int:
        lvl = int(self.save.shop_levels.get(item.id, 0))
        if item.kind == "weapon":
            return item.base_cost
        cost = item.base_cost * (item.cost_mult ** lvl)
        return int(round(cost))

    def is_maxed(self, item: ShopItemDef) -> bool:
        if item.kind == "weapon":
            wid = item.weapon_id
            return bool(self.save.weapon_unlocks.get(wid, False))
        lvl = int(self.save.shop_levels.get(item.id, 0))
        return lvl >= item.max_level

    def can_buy(self, item: ShopItemDef) -> bool:
        if self.is_maxed(item):
            return False
        return self.save.coins >= self.shop_cost(item)

    def buy_item(self, item: ShopItemDef):
        if not self.can_buy(item):
            return
        cost = self.shop_cost(item)
        self.save.coins -= cost

        if item.kind == "weapon":
            wid = item.weapon_id
            # Ensure key exists even if weapon list changed
            if wid not in self.save.weapon_unlocks:
                self.save.weapon_unlocks[wid] = False
            self.save.weapon_unlocks[wid] = True
        else:
            self.save.shop_levels[item.id] = int(self.save.shop_levels.get(item.id, 0)) + 1

        # Re-sync after purchases in case an update added weapons
        self.save.ensure_weapons(list(WEAPONS.keys()))
        self.save.save()
        self.audio_play("buy")

    def toggle_setting(self, key: str):
        self.save.settings[key] = not bool(self.save.settings.get(key, True))
        self.save.save()
        if key == "audio":
            self.audio_enabled = bool(self.save.settings.get("audio", True))
        self.audio_play("buy")

    def reset_settings(self):
        self.save.settings["audio"] = True
        self.save.settings["shake"] = True
        self.audio_enabled = AUDIO_ENABLED_DEFAULT and bool(self.save.settings.get("audio", True))
        self.save.save()
        self.audio_play("buy")

    def reset_cosmetics(self):
        self.save.cosmetics_equipped = dict(DEFAULT_COSMETICS)
        for cid in DEFAULT_COSMETICS.values():
            self.save.cosmetics_unlocked[cid] = True
        self.save.save()
        self.audio_play("buy")

    # ---------------- Daily Wheel ----------------
    def daily_wheel_remaining(self) -> float:
        now = time.time()
        last_spin = float(self.save.last_spin_timestamp or 0)
        return max(0.0, (last_spin + DAILY_WHEEL_COOLDOWN) - now)

    def daily_wheel_available(self) -> bool:
        return self.daily_wheel_remaining() <= 0.0

    def format_cooldown(self, seconds: float) -> str:
        seconds = max(0, int(seconds))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        if minutes > 0:
            return f"{minutes}m {secs}s"
        return f"{secs}s"

    def pick_daily_wheel_reward(self) -> Dict[str, object]:
        total = sum(entry["weight"] for entry in DAILY_WHEEL_REWARDS)
        roll = random.uniform(0, total)
        acc = 0.0
        for entry in DAILY_WHEEL_REWARDS:
            acc += entry["weight"]
            if roll <= acc:
                return entry
        return DAILY_WHEEL_REWARDS[-1]

    def spin_daily_wheel(self):
        if self.daily_wheel_spinning or not self.daily_wheel_available():
            return
        reward = self.pick_daily_wheel_reward()
        self.daily_wheel_selected_reward = reward
        slice_angle = math.tau / len(DAILY_WHEEL_REWARDS)
        reward_index = DAILY_WHEEL_REWARDS.index(reward)
        slice_center = reward_index * slice_angle + slice_angle / 2
        desired = -math.pi / 2 - slice_center
        start = self.daily_wheel_angle
        delta = (desired - start) % (math.tau)
        delta += math.tau * random.randint(3, 5)
        self.daily_wheel_spin_start = start
        self.daily_wheel_spin_delta = delta
        self.daily_wheel_spin_time = 0.0
        self.daily_wheel_spin_duration = 3.2
        self.daily_wheel_spinning = True
        self.daily_wheel_message = ""
        self.daily_wheel_message_timer = 0.0

    def apply_daily_wheel_reward(self, reward: Dict[str, object]):
        message = ""
        kind = reward.get("kind")
        if kind == "coins":
            amount = int(reward.get("amount", 0))
            self.save.coins += amount
            message = f"+{amount} COINS"
        elif kind == "tank":
            available = [wid for wid in WEAPONS.keys() if not self.save.weapon_unlocks.get(wid, False)]
            if available:
                wid = random.choice(available)
                self.save.weapon_unlocks[wid] = True
                message = f"Unlocked: {WEAPONS[wid].name}"
            else:
                self.save.coins += DAILY_WHEEL_FALLBACK_TANK_COINS
                message = f"All tanks owned → +{DAILY_WHEEL_FALLBACK_TANK_COINS} COINS"
        elif kind == "windscreen":
            wid = "windscreen"
            if not self.save.weapon_unlocks.get(wid, False):
                self.save.weapon_unlocks[wid] = True
                message = f"Unlocked: {WEAPONS[wid].name}"
            else:
                self.save.coins += DAILY_WHEEL_FALLBACK_WINDSCREEN_COINS
                message = f"Windscreen owned → +{DAILY_WHEEL_FALLBACK_WINDSCREEN_COINS} COINS"
        elif kind == "meta":
            candidates = [
                entry for entry in DAILY_WHEEL_META_UPGRADES
                if int(self.save.shop_levels.get(entry["id"], 0)) < int(entry["max"])
            ]
            if candidates:
                picked = random.choice(candidates)
                self.save.shop_levels[picked["id"]] = int(self.save.shop_levels.get(picked["id"], 0)) + 1
                message = f"Meta Upgrade: {picked['name']}"
            else:
                self.save.coins += DAILY_WHEEL_FALLBACK_META_COINS
                message = f"Meta maxed → +{DAILY_WHEEL_FALLBACK_META_COINS} COINS"
        self.save.ensure_weapons(list(WEAPONS.keys()))
        self.save.last_spin_timestamp = int(time.time())
        self.save.save()
        self.audio_play("levelup")
        self.daily_wheel_message = message
        self.daily_wheel_message_timer = 3.6

    def update_daily_wheel(self, dt: float):
        if self.daily_wheel_spinning:
            self.daily_wheel_spin_time += dt
            t = min(1.0, self.daily_wheel_spin_time / max(0.001, self.daily_wheel_spin_duration))
            eased = 1 - (1 - t) ** 3
            self.daily_wheel_angle = self.daily_wheel_spin_start + self.daily_wheel_spin_delta * eased
            if t >= 1.0:
                self.daily_wheel_spinning = False
                if self.daily_wheel_selected_reward:
                    self.apply_daily_wheel_reward(self.daily_wheel_selected_reward)
                self.daily_wheel_selected_reward = None
        if self.daily_wheel_message_timer > 0:
            self.daily_wheel_message_timer = max(0.0, self.daily_wheel_message_timer - dt)

    # ---------------- Weapons screen ----------------
    def open_weapons_screen(self):
        # Ensure weapons list is always synced before showing (future updates safety)
        if self.save.ensure_weapons(list(WEAPONS.keys())):
            self.save.save()
        if self.save.ensure_mastery(list(WEAPONS.keys())):
            self.save.save()
        self.weapon_page = 0
        self.weapon_notice_text = ""
        self.weapon_notice_timer = 0.0
        self.weapons_view = "weapons"
        self.mastery_error_logged = False
        self.set_state("weapons")

    def change_weapon_page(self, delta: int):
        self.weapon_page = max(0, self.weapon_page + delta)

    # ---------------- Meta application ----------------
    def apply_meta_upgrades_to_player(self):
        dmg_lvl = int(self.save.shop_levels.get("meta_damage", 0))
        mov_lvl = int(self.save.shop_levels.get("meta_move", 0))
        hp_lvl = int(self.save.shop_levels.get("meta_hp", 0))
        xp_lvl = int(self.save.shop_levels.get("meta_xp", 0))
        dash_lvl = int(self.save.shop_levels.get("meta_dash", 0))
        armor_lvl = int(self.save.shop_levels.get("meta_armor", 0))
        bsp_lvl = int(self.save.shop_levels.get("meta_bulletspeed", 0))

        self.player.meta_damage_mul = 1.0 + 0.05 * dmg_lvl
        self.player.meta_move_mul = 1.0 + 0.05 * mov_lvl
        self.player.meta_xp_mul = 1.0 + 0.05 * xp_lvl
        self.player.meta_dash_mul = max(0.55, 1.0 - 0.05 * dash_lvl)
        self.player.meta_armor_mul = max(0.70, 1.0 - 0.05 * armor_lvl)
        self.player.meta_bulletspd_mul = 1.0 + 0.05 * bsp_lvl

        if hp_lvl > 0:
            self.player.max_hp += hp_lvl
            self.player.hp += hp_lvl

        self.player.outline_color = self.get_outline_color()

    # ---------------- Run reset ----------------
    def start_run(self):
        self.mode = "endless"
        self.set_state("playing")
        self.arena_rect = pygame.Rect(0, 0, ARENA_W, ARENA_H)
        self.story_config = None
        self.story_visibility_radius = None
        self.story_hazard_zones = []
        self.story_defend_point = None
        self.story_forced_weapon = None
        self.story_beacon_pos = None
        self.story_beacon_hp = None
        self.story_beacon_max = 0
        self.story_beacon_iframes = 0.0
        self.boss_rocket_strikes = []

        # Always ensure weapon keys are synced before starting
        self.save.ensure_weapons(list(WEAPONS.keys()))
        weapon_id = self.save.selected_weapon if self.save.weapon_unlocks.get(self.save.selected_weapon, False) else "pistol"

        self.player = Player(Vector2(self.arena_rect.centerx, self.arena_rect.centery), weapon_id=weapon_id)
        self.apply_meta_upgrades_to_player()
        self.counted_game = False

        self.projectiles.clear()
        self.enemy_projectiles.clear()
        self.enemies.clear()
        self.pickups.clear()
        self.particles.clear()
        self.float_texts.clear()

        self._generate_obstacles()

        self.start_time = time.time()
        self.survival_time = 0.0
        self.wave = 1
        self.wave_timer = WAVE_TIME_BASE
        self.spawn_timer = 0.0
        self.spawn_interval = SPAWN_RATE_BASE

        self.difficulty = 0.0
        self.diff_eased = 0.0

        self.shake = 0.0
        self.powerup_timer = random.uniform(POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX)

        self.last_run_coins_earned = 0
        self.coins_awarded_this_gameover = False
        self.run_bonus_coins = 0
        self.leaderboard_recorded = False

        self.in_boss_fight = False
        self.boss_alive = False
        self.boss_banner_timer = 0.0
        self.boss_grace_timer = 0.0

    # ---------------- Difficulty / caps ----------------
    def update_difficulty(self):
        self.difficulty = clamp(self.survival_time / DIFFICULTY_RAMP_TIME, 0.0, 1.0)
        self.diff_eased = smoothstep(self.difficulty)

    def current_enemy_cap(self) -> int:
        return int(round(lerp(ENEMY_CAP_BASE, ENEMY_CAP_HARD, self.diff_eased)))

    def update_enemy_projectiles(self, dt: float):
        for b in self.enemy_projectiles:
            if self.is_modifier_active("curving_shots"):
                target = self.enemy_target_pos()
                d = target - b.pos
                if d.length_squared() > 1:
                    desired = d.normalize() * max(80.0, b.vel.length())
                    b.vel = b.vel.lerp(desired, 1 - math.exp(-dt * 1.25))
            b.update(dt)

    def update_enemy_explosions(self, dt: float):
        if not self.pending_enemy_explosions:
            return
        remaining: List[Dict[str, object]] = []
        for exp in self.pending_enemy_explosions:
            exp["timer"] = float(exp["timer"]) - dt
            if exp["timer"] > 0:
                remaining.append(exp)
                continue
            pos = Vector2(exp["pos"])
            radius = float(exp["radius"])
            dmg = int(exp["damage"])
            if (self.player.pos - pos).length_squared() <= (radius + PLAYER_RADIUS) ** 2:
                self.damage_player(dmg)
            self._spawn_hit_particles(pos, self.get_explosion_color())
            self.shake = max(self.shake, 6.0)
        self.pending_enemy_explosions = remaining

    # ---------------- Visibility / LOS ----------------
    def is_world_pos_onscreen(self, world_pos: Vector2, margin: int = 0) -> bool:
        cam = self.cam + self.shake_vec
        x = world_pos.x - cam.x
        y = world_pos.y - cam.y
        return (-margin <= x <= WIDTH + margin) and (-margin <= y <= HEIGHT + margin)

    def has_line_of_sight(self, a: Vector2, b: Vector2) -> bool:
        ax, ay = int(a.x), int(a.y)
        bx, by = int(b.x), int(b.y)
        for r in self.obstacles:
            if r.clipline(ax, ay, bx, by):
                return False
        return True

    # ---------------- Collisions ----------------
    def resolve_player_walls(self):
        for r in self.obstacles:
            self._resolve_circle_rect(self.player.pos, PLAYER_RADIUS, r)

    def resolve_circle_walls(self, enemy: EnemyBase, damping=0.25):
        before = Vector2(enemy.pos)
        for r in self.obstacles:
            self._resolve_circle_rect(enemy.pos, enemy.radius, r)
        moved = enemy.pos - before
        if moved.length_squared() > 0:
            enemy.vel *= (1.0 - damping)

    def _resolve_circle_rect(self, cpos: Vector2, radius: float, rect: pygame.Rect):
        closest_x = clamp(cpos.x, rect.left, rect.right)
        closest_y = clamp(cpos.y, rect.top, rect.bottom)
        closest = Vector2(closest_x, closest_y)
        d = cpos - closest
        dist2 = d.length_squared()

        if dist2 < radius * radius:
            dist = math.sqrt(dist2) if dist2 > 1e-6 else 0.0
            if dist == 0.0:
                dx_left = abs(cpos.x - rect.left)
                dx_right = abs(rect.right - cpos.x)
                dy_top = abs(cpos.y - rect.top)
                dy_bottom = abs(rect.bottom - cpos.y)
                m = min(dx_left, dx_right, dy_top, dy_bottom)
                if m == dx_left:
                    cpos.x = rect.left - radius
                elif m == dx_right:
                    cpos.x = rect.right + radius
                elif m == dy_top:
                    cpos.y = rect.top - radius
                else:
                    cpos.y = rect.bottom + radius
            else:
                push = d / dist * (radius - dist)
                cpos += push

        arena = self.arena_rect
        cpos.x = clamp(cpos.x, arena.left + radius, arena.right - radius)
        cpos.y = clamp(cpos.y, arena.top + radius, arena.bottom - radius)

    def bullet_hits_wall(self, bullet: Projectile) -> bool:
        p = bullet.pos
        for r in self.obstacles:
            if r.collidepoint(p.x, p.y):
                return True
        return False

    def resolve_enemy_player_overlap(self, enemy: EnemyBase):
        p = self.player.pos
        d = enemy.pos - p
        min_dist = PLAYER_RADIUS + enemy.radius - PLAYER_ENEMY_MIN_DIST_EPS
        dist2 = d.length_squared()

        if dist2 < (min_dist * min_dist):
            if dist2 < 1e-8:
                ang = ((int(enemy.pos.x) * 73856093) ^ (int(enemy.pos.y) * 19349663)) % 360
                n = Vector2(1, 0).rotate(ang)
                dist = 0.0
            else:
                dist = math.sqrt(dist2)
                n = d / dist

            penetration = (min_dist - dist) if dist > 0 else min_dist
            enemy.pos += n * penetration * PLAYER_ENEMY_PUSH_STRENGTH

            into = enemy.vel.dot(n)
            if into < 0:
                enemy.vel -= n * into * 0.85

            dd = enemy.pos - p
            if dd.length_squared() < (min_dist * min_dist):
                enemy.pos = p + (dd.normalize() if dd.length_squared() > 1e-8 else n) * min_dist

            arena = self.arena_rect
            enemy.pos.x = clamp(enemy.pos.x, arena.left + enemy.radius, arena.right - enemy.radius)
            enemy.pos.y = clamp(enemy.pos.y, arena.top + enemy.radius, arena.bottom - enemy.radius)

    # ---------------- Shooting + special weapon mechanics ----------------
    def spawn_player_shot(self, player: Player):
        w = player.weapon
        dmg = player.get_damage()
        bspd = player.get_bullet_speed()
        life = player.get_bullet_lifetime()

        is_crit = False
        if player.crit_chance > 0 and random.random() < player.crit_chance:
            dmg = int(dmg * player.crit_mult)
            is_crit = True

        base_dir = Vector2(player.aim_dir)
        if base_dir.length_squared() < 1e-6:
            base_dir = Vector2(1, 0)

        # recoil
        player.vel -= base_dir * w.recoil * RECOIL_MULT

        # angles / firing pattern
        if player.weapon_id == "omni_pistol":
            # 8-way shots: forward, back, left, right, diagonals (aim-relative)
            angles = [
            0, 22.5, 45, 67.5,
            90, 112.5, 135, 157.5,
            180, -157.5, -135, -112.5,
            -90, -67.5, -45, -22.5
    ]
        else:
            # normal spread system
            n = w.bullets_per_shot
            spread = w.spread_deg
            if n <= 1 or spread <= 0.0:
                angles = [0.0]
            else:
                angles = []
                for i in range(n):
                    t = 0.0 if n == 1 else (i / (n - 1))
                    angles.append(lerp(-spread * 0.5, spread * 0.5, t))

        base_col = self.get_bullet_color()
        for ang in angles:
            dirn = base_dir.rotate(ang)
            vel = dirn * bspd
            col = base_col if not is_crit else (255, 240, 120)
            splash = w.splash_radius if w.splash_radius > 0 else 0.0
            pierce_total = max(0, player.piercing + int(getattr(w, "base_pierce", 0)))
            b = Projectile(
                player.pos + dirn * (PLAYER_RADIUS + 7),
                vel,
                dmg,
                owner="player",
                color=col,
                radius=w.bullet_radius,
                lifetime=life,
                pierce=pierce_total,
                splash_radius=splash
            )
            self.projectiles.append(b)

        self.audio_play("shoot")

    def tesla_chain(self, start_enemy: EnemyBase, base_damage: int, chains: int, chain_range: float):
        hit = {id(start_enemy)}
        current = start_enemy
        for _ in range(chains):
            best = None
            best_d2 = (chain_range * chain_range)
            for e in self.enemies:
                if id(e) in hit or not e.alive():
                    continue
                d2 = (e.pos - current.pos).length_squared()
                if d2 < best_d2:
                    best_d2 = d2
                    best = e
            if best is None:
                break

            hit.add(id(best))
            dscale = getattr(self.player.weapon, "chain_damage_mult", 0.65)
            scale = getattr(self.player.weapon, "chain_damage_mult", 0.65)
            dmg = max(3, int(base_damage * scale))
            dirn = (best.pos - current.pos)
            if dirn.length_squared() > 0.001:
                dirn = dirn.normalize()
            else:
                dirn = Vector2(1, 0)
            actual = self.apply_enemy_damage(best, dmg, dirn, 70.0, weapon_id=self.player.weapon_id)
            self.update_mastery(self.player.weapon_id, hits=1)
            self.update_challenges("damage", actual)
            self.float_texts.append(FloatingText(best.pos + Vector2(0, -10), str(actual), C_ACCENT))
            self._spawn_hit_particles(best.pos, (200, 220, 255))
            current = best

    # ---------------- Spawning ----------------
    def valid_pickup_spawn(self, pos: Vector2, min_player_dist: float = 120.0) -> bool:
        if (pos - self.player.pos).length() < min_player_dist:
            return False
        for r in self.obstacles:
            if r.inflate(22, 22).collidepoint(pos.x, pos.y):
                return False
        return True

    def random_arena_spawn(self, min_player_dist: float = 220.0, attempts: int = 40) -> Vector2:
        arena = self.arena_rect
        pos = Vector2(arena.center)
        for _ in range(attempts):
            pos = Vector2(
                random.uniform(arena.left + 60, arena.right - 60),
                random.uniform(arena.top + 60, arena.bottom - 60),
            )
            if (pos - self.player.pos).length() < min_player_dist:
                continue
            if any(r.inflate(40, 40).collidepoint(pos.x, pos.y) for r in self.obstacles):
                continue
            return pos
        return pos

    def pick_enemy_kind(self) -> str:
        if self.wave < 2:
            weights = {"chaser": 1.0}
        elif self.wave < 4:
            weights = {"chaser": 0.8, "sprinter": 0.2}
        elif self.wave < 7:
            weights = {"chaser": 0.55, "ranged": 0.25, "sprinter": 0.2}
        elif self.wave < 11:
            weights = {"chaser": 0.45, "ranged": 0.27, "tank": 0.14, "sprinter": 0.14}
        else:
            weights = {"chaser": 0.38, "ranged": 0.24, "dasher": 0.16, "tank": 0.12, "sprinter": 0.1}

        if self.is_modifier_active("knight_enemy"):
            weights["knight"] = weights.get("knight", 0.0) + 0.08
        if self.is_modifier_active("knight_frequent"):
            weights["knight"] = weights.get("knight", 0.0) + 0.18
        return weighted_choice(weights)

    def spawn_enemy(self, kind: str):
        player = self.player
        margin = 260
        dist = max(WIDTH, HEIGHT) * 0.65 + margin
        use_bias = self.is_modifier_active("spawn_uneven")
        if use_bias and random.random() < 0.7:
            ang = random.gauss(self.spawn_bias_angle, 0.45)
        else:
            ang = random.uniform(0, math.tau)
        spawn = player.pos + Vector2(math.cos(ang), math.sin(ang)) * dist

        arena = self.arena_rect
        spawn.x = clamp(spawn.x, arena.left + 60, arena.right - 60)
        spawn.y = clamp(spawn.y, arena.top + 60, arena.bottom - 60)

        attempts = 14
        while attempts > 0:
            if any(r.inflate(40, 40).collidepoint(spawn.x, spawn.y) for r in self.obstacles):
                ang = random.uniform(0, math.tau)
                spawn = player.pos + Vector2(math.cos(ang), math.sin(ang)) * dist
                spawn.x = clamp(spawn.x, arena.left + 60, arena.right - 60)
                spawn.y = clamp(spawn.y, arena.top + 60, arena.bottom - 60)
                attempts -= 1
            else:
                break

        hp_mul = lerp(ENEMY_HP_BASE_MUL, ENEMY_HP_HARD_MUL, self.diff_eased)
        elite_chance = 0.0
        if self.is_modifier_active("elite_frenzy"):
            elite_chance = 0.22
        elif self.is_modifier_active("elite_spawn"):
            elite_chance = 0.12
        is_elite = self.mode == "endless" and self.wave >= MID_LATE_START_WAVE and random.random() < elite_chance
        if is_elite:
            spawn = self.random_arena_spawn(min_player_dist=240.0)

        if kind == "chaser":
            spd = lerp(CHASER_SPEED_BASE, CHASER_SPEED_HARD, self.diff_eased)
            e = Chaser(spawn, hp=42 * hp_mul, speed=spd)
        elif kind == "ranged":
            spd = lerp(RANGED_SPEED_BASE, RANGED_SPEED_HARD, self.diff_eased)
            e = Ranged(spawn, hp=58 * hp_mul, speed=spd)
        elif kind == "tank":
            spd = lerp(TANK_SPEED_BASE, TANK_SPEED_HARD, self.diff_eased)
            e = Tank(spawn, hp=125 * hp_mul, speed=spd)
        elif kind == "knight":
            spd = lerp(KNIGHT_SPEED_BASE, KNIGHT_SPEED_HARD, self.diff_eased)
            e = Knight(spawn, hp=375 * hp_mul, speed=spd)
        elif kind == "sprinter":
            spd = lerp(SPRINTER_SPEED_BASE, SPRINTER_SPEED_HARD, self.diff_eased)
            e = Sprinter(spawn, hp=28 * hp_mul, speed=spd)
        else:
            spd = lerp(DASHER_SPEED_BASE, DASHER_SPEED_HARD, self.diff_eased)
            e = Dasher(spawn, hp=72 * hp_mul, speed=spd)

        if self.is_modifier_active("tight_clusters") and not is_elite:
            if self.spawn_cluster_timer <= 0 or self.spawn_cluster_anchor is None:
                self.spawn_cluster_anchor = Vector2(spawn)
                self.spawn_cluster_timer = random.uniform(1.4, 2.6)
            jitter = Vector2(random.uniform(-85, 85), random.uniform(-85, 85))
            e.pos = self.spawn_cluster_anchor + jitter
            arena = self.arena_rect
            e.pos.x = clamp(e.pos.x, arena.left + 60, arena.right - 60)
            e.pos.y = clamp(e.pos.y, arena.top + 60, arena.bottom - 60)
            if any(r.inflate(40, 40).collidepoint(e.pos.x, e.pos.y) for r in self.obstacles):
                e.pos = self.random_arena_spawn(min_player_dist=120.0)

        if is_elite:
            e.elite = True
            e.hp *= 1.25
            e.hp_max *= 1.25
            e.base_speed *= 1.08
            e.speed = e.base_speed
            e.score_value = int(e.score_value * 1.45)

        if self.is_modifier_active("revive_once"):
            e.revives_remaining = 1

        if self.is_modifier_active("enemy_dashes"):
            e.extra_dash_cd = random.uniform(1.8, 3.2)

        self.enemies.append(e)

    def spawn_boss(self):
        # clear field
        self.enemies.clear()
        self.enemy_projectiles.clear()

        dist = 620
        ang = random.uniform(0, math.tau)
        pos = self.player.pos + Vector2(math.cos(ang), math.sin(ang)) * dist
        arena = self.arena_rect
        pos.x = clamp(pos.x, arena.left + 120, arena.right - 120)
        pos.y = clamp(pos.y, arena.top + 120, arena.bottom - 120)

        tries = 24
        while tries > 0 and any(r.inflate(60, 60).collidepoint(pos.x, pos.y) for r in self.obstacles):
            ang = random.uniform(0, math.tau)
            pos = self.player.pos + Vector2(math.cos(ang), math.sin(ang)) * dist
            pos.x = clamp(pos.x, arena.left + 120, arena.right - 120)
            pos.y = clamp(pos.y, arena.top + 120, arena.bottom - 120)
            tries -= 1

        stage = max(1, self.wave // BOSS_EVERY_WAVES)
        base_hp = 1200.0
        wave_mul = 1.0 + 0.85 * (stage - 1)
        diff_mul = 1.0 + 0.65 * self.diff_eased
        hp = base_hp * wave_mul * diff_mul

        speed = 72.0 + 22.0 * self.diff_eased
        boss = Boss(pos, hp=hp, speed=speed, wave_index=self.wave)
        self.enemies.append(boss)

        self.in_boss_fight = True
        self.boss_alive = True
        self.boss_banner_timer = 2.3
        self.shake = max(self.shake, 10.0)
        self.float_texts.append(FloatingText(self.player.pos + Vector2(-10, -40), "BOSS!", C_ACCENT_2, life=1.0))

    def on_boss_killed(self, boss: Boss):
        center = Vector2(boss.pos)
        self.player.score += boss.score_value
        self.update_challenges("boss_kills", 1)
        self.update_challenges("kills", 1)
        if boss.last_hit_by_player and boss.last_hit_weapon_id:
            self.update_mastery(boss.last_hit_weapon_id, kills=1)
            self.update_challenges("weapon_kills", 1, weapon_id=boss.last_hit_weapon_id)

        stage = max(1, self.wave // BOSS_EVERY_WAVES)
        bonus = 10 + 4 * (stage - 1)
        self.run_bonus_coins += bonus
        self.float_texts.append(FloatingText(self.player.pos + Vector2(0, -54), f"+{bonus} COINS (BANKED)", C_COIN, life=1.0))

        xp_each = int(XP_ORB_VALUE_BASE * (3.0 + 1.0 * self.diff_eased))
        for _ in range(18):
            ang = random.uniform(0, math.tau)
            rad = random.uniform(10, 120)
            p = center + Vector2(math.cos(ang), math.sin(ang)) * rad
            arena = self.arena_rect
            p.x = clamp(p.x, arena.left + 40, arena.right - 40)
            p.y = clamp(p.y, arena.top + 40, arena.bottom - 40)
            self.pickups.append(Pickup(p, "xp", xp_each))

        for _ in range(2):
            p = center + Vector2(random.uniform(-60, 60), random.uniform(-60, 60))
            self.pickups.append(Pickup(p, "health", HEALTH_PACK_AMOUNT + 1))

        ptype = random.choice(["damage_boost", "rapid_fire", "speed_boost", "shield"])
        self.pickups.append(Pickup(center + Vector2(0, -20), "power", 0, ptype))

        self._spawn_hit_particles(center, self.get_explosion_color())
        self.shake = max(self.shake, 12.0)

        self.in_boss_fight = False
        self.boss_alive = False
        self.boss_grace_timer = BOSS_GRACE_AFTER_DEATH

    def drop_pickups(self, pos: Vector2):
        xp = XP_ORB_VALUE_BASE + int(self.diff_eased * 6)
        self.pickups.append(Pickup(pos, "xp", xp))

        health_chance = 0.09 + 0.07 * self.diff_eased
        if random.random() < health_chance:
            self.pickups.append(Pickup(pos + Vector2(random.uniform(-10, 10), random.uniform(-10, 10)),
                                       "health", HEALTH_PACK_AMOUNT))

    def try_spawn_powerup(self, dt):
        self.powerup_timer -= dt
        if self.powerup_timer > 0:
            return
        self.powerup_timer = random.uniform(POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX)

        powerups_on_map = sum(1 for p in self.pickups if p.kind == "power")
        if powerups_on_map >= POWERUP_MAX_ON_MAP:
            return

        attempts = 40
        while attempts > 0:
            arena = self.arena_rect
            pos = Vector2(random.uniform(arena.left + 80, arena.right - 80), random.uniform(arena.top + 80, arena.bottom - 80))
            if not self.valid_pickup_spawn(pos, min_player_dist=260.0):
                attempts -= 1
                continue
            ptype = random.choice(["damage_boost", "rapid_fire", "speed_boost", "shield"])
            self.pickups.append(Pickup(pos, "power", 0, ptype))
            break

    # ---------------- Coins on run end ----------------
    def award_coins_if_needed(self):
        if self.coins_awarded_this_gameover:
            return
        waves_cleared = max(0, self.wave - 1)
        coins_earned = (self.player.score // COINS_SCORE_DIV) + (waves_cleared * COINS_PER_WAVE) + int(self.run_bonus_coins)
        coins_earned = max(0, int(coins_earned))
        self.last_run_coins_earned = coins_earned
        self.save.coins += coins_earned
        self.save.save()
        self.coins_awarded_this_gameover = True

    def record_leaderboard_if_needed(self):
        if self.leaderboard_recorded:
            return
        self.save.add_leaderboard_entry(
            score=self.player.score,
            time_s=int(self.survival_time),
            wave=self.wave,
            level=self.player.level,
        )
        self.update_challenges("runs", 1)
        self.save.save()
        self.leaderboard_recorded = True

    # ---------------- Events ----------------
    def handle_events(self):
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                self.running = False

            if e.type == pygame.KEYDOWN:
                if self.state in ("controls", "weapons", "shop", "settings", "leaderboard", "challenges", "story_menu", "story_complete", "daily_wheel"):
                    if e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                        self.set_state("menu")

                if self.state == "playing":
                    if e.key == pygame.K_ESCAPE:
                        self.set_state("paused")

                    if e.key == pygame.K_f:
                        self.player.auto_fire = not self.player.auto_fire

                elif self.state == "paused":
                    if e.key == pygame.K_ESCAPE:
                        self.set_state("playing")

                elif self.state == "gameover":
                    if e.key == pygame.K_r:
                        if self.mode == "story":
                            self.retry_story_level()
                        else:
                            self.start_run()
                    if e.key == pygame.K_ESCAPE:
                        self.set_state("menu")

                elif self.state == "menu":
                    if e.key == pygame.K_ESCAPE:
                        self.running = False

        return events

    # ---------------- Camera ----------------
    def update_camera(self, dt):
        target = self.player.pos - Vector2(WIDTH / 2, HEIGHT / 2)
        self.cam = self.cam.lerp(target, 1 - math.exp(-dt * 8.5))

        do_shake = bool(self.save.settings.get("shake", True))
        self.shake = max(0.0, self.shake - dt * SHAKE_DECAY)
        if do_shake and self.shake > 0:
            self.shake_vec = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * self.shake
        else:
            self.shake_vec = Vector2(0, 0)

        arena = self.arena_rect
        self.cam.x = clamp(self.cam.x, arena.left, max(arena.left, arena.right - WIDTH))
        self.cam.y = clamp(self.cam.y, arena.top, max(arena.top, arena.bottom - HEIGHT))

    # ---------------- Updates (Playing) ----------------
    def update_playing(self, dt, events):
        if self.mode == "story":
            self.update_story_playing(dt, events)
            return

        self.refresh_challenges()
        self.survival_time = time.time() - self.start_time
        self.update_difficulty()
        if self.wave >= LATE_GAME_START_WAVE:
            self.advance_late_game_modifiers()

        self.boss_grace_timer = max(0.0, self.boss_grace_timer - dt)
        self.boss_banner_timer = max(0.0, self.boss_banner_timer - dt)

        self.try_spawn_powerup(dt)
        self.update_enemy_explosions(dt)

        if not self.in_boss_fight:
            self.wave_timer -= dt
            if self.wave_timer <= 0:
                self.wave += 1
                self.wave_timer = WAVE_TIME_BASE
                self.update_challenges("waves", 1)
                self.update_challenges("high_wave", self.wave, absolute=True)
                self.advance_late_game_modifiers()

                if self.wave == 3 and not self.counted_game:
                    self.update_mastery(self.player.weapon_id, wins=1)
                    self.counted_game = True

                if self.wave % BOSS_EVERY_WAVES == 0 or (self.is_modifier_active("overlord_waves") and self.wave % 3 == 0):
                    self.spawn_boss()

        can_spawn_normals = (not self.in_boss_fight) and (self.boss_grace_timer <= 0.0)

        base = lerp(SPAWN_RATE_BASE, SPAWN_RATE_HARD, self.diff_eased)
        self.spawn_interval = max(0.42, base - SPAWN_RATE_WAVE_BONUS * max(0, self.wave - 1))

        cap_now = self.current_enemy_cap()

        self.spawn_timer -= dt
        self.spawn_cluster_timer = max(0.0, self.spawn_cluster_timer - dt)
        if self.is_modifier_active("spawn_bursts"):
            if self.spawn_burst_remaining > 0:
                self.spawn_burst_timer -= dt
                while self.spawn_burst_remaining > 0 and self.spawn_burst_timer <= 0:
                    self.spawn_burst_timer += 0.12
                    if can_spawn_normals and len(self.enemies) < cap_now:
                        self.spawn_enemy(self.pick_enemy_kind())
                    self.spawn_burst_remaining -= 1
            if self.spawn_timer <= 0:
                self.spawn_timer = self.spawn_interval * random.uniform(1.2, 1.7)
                self.spawn_burst_remaining = random.randint(3, 6)
                self.spawn_burst_timer = 0.0
        elif self.spawn_timer <= 0:
            self.spawn_timer = self.spawn_interval
            if can_spawn_normals and len(self.enemies) < cap_now:
                self.spawn_enemy(self.pick_enemy_kind())

        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed(3)

        move = Vector2(0, 0)
        if keys[pygame.K_w]:
            move.y -= 1
        if keys[pygame.K_s]:
            move.y += 1
        if keys[pygame.K_a]:
            move.x -= 1
        if keys[pygame.K_d]:
            move.x += 1

        mouse_world = Vector2(mx, my) + self.cam + self.shake_vec
        self.player.update(dt, self, move, mouse_world, mouse_buttons, keys)

        trail = self.get_trail_cosmetic()
        if trail.id != "trail_none" and self.player.vel.length_squared() > 4.0:
            self.trail_timer -= dt
            if self.trail_timer <= 0:
                jitter = Vector2(random.uniform(-6, 6), random.uniform(-6, 6))
                self.particles.append(Particle(self.player.pos + jitter, -self.player.vel * 0.1, trail.color, life=0.25, radius=2))
                self.trail_timer = 0.05 if trail.id == "trail_spark" else 0.04

        pickup_dist = PICKUP_ATTRACT_DIST_BASE + self.player.magnet_bonus
        for p in self.pickups:
            d = self.player.pos - p.pos
            dist = d.length()
            if dist < pickup_dist and dist > 1e-6:
                p.vel += d.normalize() * PICKUP_ATTRACT_FORCE * dt
            p.vel *= (1.0 - min(dt * 6.0, 0.5))
            p.pos += p.vel * dt

        self.pickups = [p for p in self.pickups if not self._handle_pickup_collect(p)]

        for b in self.projectiles:
            b.update(dt)
        self.update_enemy_projectiles(dt)

        arena = self.arena_rect
        self.projectiles = [
            b for b in self.projectiles
            if b.alive()
            and arena.left <= b.pos.x <= arena.right
            and arena.top <= b.pos.y <= arena.bottom
            and not self.bullet_hits_wall(b)
        ]
        self.enemy_projectiles = [
            b for b in self.enemy_projectiles
            if b.alive()
            and arena.left <= b.pos.x <= arena.right
            and arena.top <= b.pos.y <= arena.bottom
            and not self.bullet_hits_wall(b)
        ]

        cell = ENEMY_SEPARATION_CELL
        buckets: Dict[Tuple[int, int], List[EnemyBase]] = {}
        for e in self.enemies:
            key = (int(e.pos.x // cell), int(e.pos.y // cell))
            buckets.setdefault(key, []).append(e)

        for e in self.enemies:
            e.hit_flash = max(0.0, e.hit_flash - dt)
            key = (int(e.pos.x // cell), int(e.pos.y // cell))
            neighbors: List[EnemyBase] = []
            for ox in (-1, 0, 1):
                for oy in (-1, 0, 1):
                    neighbors.extend(buckets.get((key[0] + ox, key[1] + oy), []))
            e.apply_separation(dt, neighbors)
            e.age += dt
            e.speed = e.base_speed * self.enemy_speed_multiplier(e)
            e.update(dt, self)
            if self.is_modifier_active("enemy_dashes") and not isinstance(e, (Boss, Dasher)):
                e.extra_dash_cd = max(0.0, e.extra_dash_cd - dt)
                if e.extra_dash_timer > 0:
                    step = min(dt, e.extra_dash_timer)
                    e.pos += e.extra_dash_dir * e.base_speed * 2.8 * step
                    e.extra_dash_timer -= step
                    self.resolve_circle_walls(e, damping=0.2)
                elif e.extra_dash_cd <= 0:
                    d = self.enemy_target_pos() - e.pos
                    if d.length_squared() > 1:
                        e.extra_dash_dir = d.normalize()
                        e.extra_dash_timer = 0.12
                        e.extra_dash_cd = random.uniform(2.0, 3.6)
            if self.is_modifier_active("enemy_regen") and not isinstance(e, Boss):
                has_neighbor = any(
                    (n is not e) and (n.pos - e.pos).length_squared() < 170 * 170 for n in neighbors
                )
                if has_neighbor:
                    e.hp = min(e.hp_max, e.hp + e.hp_max * 0.05 * dt)
            self.resolve_enemy_player_overlap(e)

        self._handle_bullet_enemy_collisions()
        self._handle_enemy_bullet_player_collisions()
        self._handle_enemy_contact_player()

        alive = []
        for e in self.enemies:
            if e.alive():
                alive.append(e)
            else:
                if isinstance(e, Boss):
                    self.on_boss_killed(e)
                else:
                    if self.is_modifier_active("revive_once") and e.revives_remaining > 0:
                        e.revives_remaining -= 1
                        e.hp = max(1.0, e.hp_max * e.revive_hp_ratio)
                        e.hit_flash = 0.2
                        alive.append(e)
                        continue
                    if self.is_modifier_active("death_explosions"):
                        self.pending_enemy_explosions.append({
                            "pos": Vector2(e.pos),
                            "timer": 0.35,
                            "radius": 120.0,
                            "damage": 2,
                        })
                    self.player.score += e.score_value
                    if e.last_hit_by_player and e.last_hit_weapon_id:
                        self.update_mastery(e.last_hit_weapon_id, kills=1)
                        self.update_challenges("kills", 1)
                        self.update_challenges("weapon_kills", 1, weapon_id=e.last_hit_weapon_id)
                    self.drop_pickups(Vector2(e.pos))
        self.enemies = alive

        for pt in self.particles:
            pt.update(dt)
        self.particles = [pt for pt in self.particles if pt.life > 0]

        for ft in self.float_texts:
            ft.update(dt)
        self.float_texts = [ft for ft in self.float_texts if ft.life > 0]

        if self.progress_dirty:
            self.progress_dirty_timer += dt
            if self.progress_dirty_timer >= 2.0:
                self.save.save()
                self.progress_dirty = False
                self.progress_dirty_timer = 0.0

        if self.player.try_level_up():
            self.audio_play("levelup")
            self.open_levelup()

        if self.player.hp <= 0:
            self.player.hp = 0
            self.set_state("gameover")

    def update_story_playing(self, dt, events):
        self.refresh_challenges()
        self.story_elapsed = time.time() - self.story_start_time
        self.survival_time = self.story_elapsed
        self.story_beacon_iframes = max(0.0, self.story_beacon_iframes - dt)

        self.boss_grace_timer = max(0.0, self.boss_grace_timer - dt)
        self.boss_banner_timer = max(0.0, self.boss_banner_timer - dt)

        self.try_spawn_powerup(dt)
        self.update_boss_rocket_strikes(dt)

        spawn_cfg = self.story_config.get("spawn", {}) if self.story_config else {}
        self.spawn_interval = float(spawn_cfg.get("interval", SPAWN_RATE_BASE))
        cap_now = int(spawn_cfg.get("cap", ENEMY_CAP_BASE))

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = self.spawn_interval
            if len(self.enemies) < cap_now and not self.in_boss_fight:
                weights = self.story_config.get("enemy_weights", {}) if self.story_config else {}
                if weights:
                    kind = weighted_choice(weights)
                else:
                    kind = "chaser"
                self.spawn_enemy(kind)

        win_cfg = self.story_config.get("win", {}) if self.story_config else {}
        if win_cfg.get("type") == "boss":
            spawn_after = float(win_cfg.get("spawn_after", 6))
            if not self.story_boss_spawned and self.story_elapsed >= spawn_after:
                self.spawn_boss()
                self.story_boss_spawned = True

        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed(3)

        move = Vector2(0, 0)
        if keys[pygame.K_w]:
            move.y -= 1
        if keys[pygame.K_s]:
            move.y += 1
        if keys[pygame.K_a]:
            move.x -= 1
        if keys[pygame.K_d]:
            move.x += 1

        mouse_world = Vector2(mx, my) + self.cam + self.shake_vec
        self.player.update(dt, self, move, mouse_world, mouse_buttons, keys)

        trail = self.get_trail_cosmetic()
        if trail.id != "trail_none" and self.player.vel.length_squared() > 4.0:
            self.trail_timer -= dt
            if self.trail_timer <= 0:
                jitter = Vector2(random.uniform(-6, 6), random.uniform(-6, 6))
                self.particles.append(Particle(self.player.pos + jitter, -self.player.vel * 0.1, trail.color, life=0.25, radius=2))
                self.trail_timer = 0.05 if trail.id == "trail_spark" else 0.04

        pickup_dist = PICKUP_ATTRACT_DIST_BASE + self.player.magnet_bonus
        for p in self.pickups:
            d = self.player.pos - p.pos
            dist = d.length()
            if dist < pickup_dist and dist > 1e-6:
                p.vel += d.normalize() * PICKUP_ATTRACT_FORCE * dt
            p.vel *= (1.0 - min(dt * 6.0, 0.5))
            p.pos += p.vel * dt

        self.pickups = [p for p in self.pickups if not self._handle_pickup_collect(p)]

        for b in self.projectiles:
            b.update(dt)
        self.update_enemy_projectiles(dt)

        arena = self.arena_rect
        self.projectiles = [
            b for b in self.projectiles
            if b.alive()
            and arena.left <= b.pos.x <= arena.right
            and arena.top <= b.pos.y <= arena.bottom
            and not self.bullet_hits_wall(b)
        ]
        self.enemy_projectiles = [
            b for b in self.enemy_projectiles
            if b.alive()
            and arena.left <= b.pos.x <= arena.right
            and arena.top <= b.pos.y <= arena.bottom
            and not self.bullet_hits_wall(b)
        ]

        cell = ENEMY_SEPARATION_CELL
        buckets: Dict[Tuple[int, int], List[EnemyBase]] = {}
        for e in self.enemies:
            key = (int(e.pos.x // cell), int(e.pos.y // cell))
            buckets.setdefault(key, []).append(e)

        for e in self.enemies:
            e.hit_flash = max(0.0, e.hit_flash - dt)
            key = (int(e.pos.x // cell), int(e.pos.y // cell))
            neighbors: List[EnemyBase] = []
            for ox in (-1, 0, 1):
                for oy in (-1, 0, 1):
                    neighbors.extend(buckets.get((key[0] + ox, key[1] + oy), []))
            e.apply_separation(dt, neighbors)
            e.update(dt, self)
            self.resolve_enemy_player_overlap(e)

        self._handle_bullet_enemy_collisions()
        if self.beacon_active():
            self._handle_enemy_bullet_beacon_collisions()
            self._handle_enemy_contact_beacon()
        else:
            self._handle_enemy_bullet_player_collisions()
            self._handle_enemy_contact_player()

        alive = []
        for e in self.enemies:
            if e.alive():
                alive.append(e)
            else:
                if isinstance(e, Boss):
                    self.on_boss_killed(e)
                    if win_cfg.get("type") == "boss":
                        self.story_boss_defeated = True
                else:
                    self.player.score += e.score_value
                    self.story_kills += 1
                    if e.last_hit_by_player and e.last_hit_weapon_id:
                        self.update_mastery(e.last_hit_weapon_id, kills=1)
                        self.update_challenges("kills", 1)
                        self.update_challenges("weapon_kills", 1, weapon_id=e.last_hit_weapon_id)
                    self.drop_pickups(Vector2(e.pos))
        self.enemies = alive

        for pt in self.particles:
            pt.update(dt)
        self.particles = [pt for pt in self.particles if pt.life > 0]

        for ft in self.float_texts:
            ft.update(dt)
        self.float_texts = [ft for ft in self.float_texts if ft.life > 0]

        if self.progress_dirty:
            self.progress_dirty_timer += dt
            if self.progress_dirty_timer >= 2.0:
                self.save.save()
                self.progress_dirty = False
                self.progress_dirty_timer = 0.0

        if self.player.try_level_up():
            self.audio_play("levelup")
            self.open_levelup()

        if self.story_defend_point and self.story_defend_radius > 0:
            dist2 = (self.player.pos - self.story_defend_point).length_squared()
            if dist2 <= self.story_defend_radius * self.story_defend_radius:
                self.story_defend_progress += dt

        if self.story_hazard_zones:
            in_hazard = 0.0
            for hz in self.story_hazard_zones:
                rect = hz["rect"]
                if rect.collidepoint(self.player.pos.x, self.player.pos.y):
                    in_hazard += float(hz.get("dps", 1.0))
            if in_hazard > 0:
                self.story_hazard_accum += in_hazard * dt
                dmg = int(self.story_hazard_accum)
                if dmg > 0:
                    self.story_hazard_accum -= dmg
                    self.damage_player(dmg)

        if self.player.hp <= 0:
            self.player.hp = 0
            self.set_state("gameover")
            return
        if self.beacon_active() and self.story_beacon_hp is not None and self.story_beacon_hp <= 0:
            self.set_state("gameover")
            return

        if win_cfg:
            win_type = win_cfg.get("type")
            complete = False
            if win_type == "survive":
                complete = self.story_elapsed >= float(win_cfg.get("seconds", 0))
            elif win_type == "kills":
                complete = self.story_kills >= int(win_cfg.get("count", 0))
            elif win_type == "defend":
                complete = self.story_defend_progress >= self.story_defend_required
            elif win_type == "boss":
                complete = self.story_boss_spawned and self.story_boss_defeated and not self.boss_alive

            if complete:
                self.story_level_complete_stats = {
                    "time": int(self.story_elapsed),
                    "kills": int(self.story_kills),
                    "score": int(self.player.score),
                    "level": int(self.player.level),
                }
                self.unlock_next_story_level()
                self.set_state("story_complete")

    # ---------------- Level up screen ----------------
    def open_levelup(self):
        self.set_state("levelup")
        self.level_choices = random.sample(UPGRADES, 3)

        cx = WIDTH // 2
        bw, bh = 720, 94
        top = HEIGHT // 2 - 170
        self.level_cards = []
        for i, up in enumerate(self.level_choices):
            rect = pygame.Rect(cx - bw // 2, top + i * (bh + 18), bw, bh)
            self.level_cards.append((rect, up))

    # ---------------- Pickup collect ----------------
    def _handle_pickup_collect(self, p: Pickup) -> bool:
        if (self.player.pos - p.pos).length_squared() <= (PLAYER_RADIUS + p.radius()) ** 2:
            if p.kind == "xp":
                self.player.gain_xp(p.value)
            elif p.kind == "health":
                self.player.hp = min(self.player.max_hp, self.player.hp + p.value)
            else:
                self.player.apply_powerup(p.power_type)
                self.audio_play("powerup")
                self.float_texts.append(FloatingText(self.player.pos + Vector2(0, -26),
                                                     p.power_type.replace("_", " ").upper(), C_ACCENT))
            return True
        return False

    # ---------------- Combat collisions ----------------
    def _rocket_explode(self, b: Projectile):
        if b.splash_radius <= 0:
            return
        center = Vector2(b.pos)
        rad2 = b.splash_radius * b.splash_radius
        for e in self.enemies:
            if not e.alive():
                continue
            d2 = (e.pos - center).length_squared()
            if d2 <= rad2:
                t = 1.0 - math.sqrt(max(0.0, d2)) / max(1.0, b.splash_radius)
                dmg = max(2, int(b.damage * (0.55 + 0.45 * t)))
                knock_dir = (e.pos - center)
                if knock_dir.length_squared() > 0.001:
                    knock_dir = knock_dir.normalize()
                else:
                    knock_dir = Vector2(1, 0)
                actual = self.apply_enemy_damage(e, dmg, knock_dir, 110.0, weapon_id=self.player.weapon_id)
                self.update_mastery(self.player.weapon_id, hits=1)
                self.update_challenges("damage", actual)
                self.float_texts.append(FloatingText(e.pos + Vector2(0, -10), str(actual), C_WARN))
        self._spawn_hit_particles(center, self.get_explosion_color())
        self.shake = max(self.shake, 6.0)

    def _handle_bullet_enemy_collisions(self):
        for b in list(self.projectiles):
            if b.owner != "player":
                continue
            for e in self.enemies:
                if id(e) in b.hit_set:
                    continue
                rr = (e.radius + b.radius) ** 2
                if (e.pos - b.pos).length_squared() <= rr:
                    b.hit_set.add(id(e))

                    knock_dir = (e.pos - b.pos)
                    if knock_dir.length_squared() > 0.001:
                        knock_dir = knock_dir.normalize()
                    else:
                        knock_dir = Vector2(1, 0).rotate(random.uniform(0, 360))

                    base_knock = 95.0
                    weapon_knock = {
                        "cannon": 1.55,
                        "minigun": 0.75,
                        "shotgun": 1.30,
                        "rocket": 1.60,
                        "sniper": 1.15,
                        "sawblade": 0.55,
                    }.get(self.player.weapon_id, 1.0)

                    knockback = base_knock * weapon_knock * self.player.knockback_mult
                    actual = self.apply_enemy_damage(e, b.damage, knock_dir, knockback, weapon_id=self.player.weapon_id)
                    self.update_mastery(self.player.weapon_id, hits=1)
                    self.update_challenges("damage", actual)
                    self.float_texts.append(FloatingText(e.pos + Vector2(random.uniform(-6, 6), -10),
                                                         str(actual), C_WARN))
                    self.audio_play("hit")
                    self._spawn_hit_particles(e.pos, C_ACCENT_2)

                    # Chain lightning for any weapon that defines it (tesla, electricity, etc.)
                    w = self.player.weapon
                    if getattr(w, "chain", 0) > 0 and getattr(w, "chain_range", 0.0) > 0:
                        self.tesla_chain(e, base_damage=actual, chains=w.chain, chain_range=w.chain_range)


                    # --- Pierce should apply BEFORE splash kills the bullet ---
                    if b.pierce > 0:
                        b.pierce -= 1
                        # IMPORTANT: while piercing, do NOT explode (otherwise rockets/tank become insane)
                    else:
                        # no pierce left -> now explode (if it has splash) and end the bullet
                        if b.splash_radius > 0:
                            self._rocket_explode(b)
                        b.life = 0
                    break
    def _handle_enemy_bullet_player_collisions(self):
        if self.player.invulnerable():
            return
        for b in list(self.enemy_projectiles):
            rr = (PLAYER_RADIUS + b.radius) ** 2
            if (self.player.pos - b.pos).length_squared() <= rr:
                b.life = 0
                self.damage_player(b.damage)
                break

    def _handle_enemy_bullet_beacon_collisions(self):
        if not self.beacon_active():
            return
        for b in list(self.enemy_projectiles):
            rr = (self.story_beacon_radius + b.radius) ** 2
            if (self.story_beacon_pos - b.pos).length_squared() <= rr:
                b.life = 0
                self.damage_beacon(b.damage)
                break

    def _handle_enemy_contact_player(self):
        if self.player.invulnerable():
            return
        for e in self.enemies:
            rr = (PLAYER_RADIUS + e.radius) ** 2
            if (self.player.pos - e.pos).length_squared() <= rr:
                self.damage_player(e.damage_contact)
                d = (self.player.pos - e.pos)
                if d.length_squared() > 0.001:
                    self.player.vel += d.normalize() * 220
                break

    def _handle_enemy_contact_beacon(self):
        if not self.beacon_active():
            return
        for e in self.enemies:
            rr = (self.story_beacon_radius + e.radius) ** 2
            if (self.story_beacon_pos - e.pos).length_squared() <= rr:
                self.damage_beacon(e.damage_contact)
                break

    def damage_player(self, amount: int):
        if self.player.invulnerable():
            return
        dmg = int(math.ceil(amount * self.player.meta_armor_mul))
        dmg = max(1, dmg)
        self.player.hp -= dmg
        self.player.iframes = PLAYER_IFRAMES
        self.shake = max(self.shake, SHAKE_HIT)
        self._spawn_hit_particles(self.player.pos, C_HEALTH)
        self.audio_play("hit")

    def _spawn_hit_particles(self, pos: Vector2, color):
        for _ in range(HIT_PARTICLE_COUNT):
            ang = random.uniform(0, math.tau)
            sp = random.uniform(120, 320)
            vel = Vector2(math.cos(ang), math.sin(ang)) * sp
            self.particles.append(Particle(pos, vel, color, life=PARTICLE_LIFE, radius=random.randint(1, 3)))

    # =========================================================
    # DRAWING
    # =========================================================
    def draw_background(self):
        self.screen.fill(C_BG)
        cam = self.cam + self.shake_vec
        start_x = int(cam.x // BG_GRID_SIZE) * BG_GRID_SIZE
        start_y = int(cam.y // BG_GRID_SIZE) * BG_GRID_SIZE

        for x in range(start_x, int(cam.x) + WIDTH + BG_GRID_SIZE, BG_GRID_SIZE):
            sx = x - cam.x
            pygame.draw.line(self.screen, C_GRID, (sx, 0), (sx, HEIGHT), 1)

        for y in range(start_y, int(cam.y) + HEIGHT + BG_GRID_SIZE, BG_GRID_SIZE):
            sy = y - cam.y
            pygame.draw.line(self.screen, C_GRID, (0, sy), (WIDTH, sy), 1)

        border = pygame.Rect(self.arena_rect.left - cam.x, self.arena_rect.top - cam.y,
                             self.arena_rect.width, self.arena_rect.height)
        pygame.draw.rect(self.screen, (25, 30, 50), border, 4)
        pygame.draw.rect(self.screen, (70, 245, 210), border, 1)

    def draw_obstacles(self):
        cam = self.cam + self.shake_vec
        for r in self.obstacles:
            rr = pygame.Rect(r.x - cam.x, r.y - cam.y, r.w, r.h)
            pygame.draw.rect(self.screen, C_WALL, rr, border_radius=10)
            pygame.draw.rect(self.screen, C_WALL_EDGE, rr, 2, border_radius=10)

    def draw_story_objects(self):
        if self.mode != "story":
            return
        cam = self.cam + self.shake_vec
        if self.story_hazard_zones:
            for hz in self.story_hazard_zones:
                rect = hz["rect"]
                rr = pygame.Rect(rect.x - cam.x, rect.y - cam.y, rect.w, rect.h)
                overlay = pygame.Surface((rr.w, rr.h), pygame.SRCALPHA)
                overlay.fill((255, 80, 120, 60))
                self.screen.blit(overlay, rr.topleft)
                pygame.draw.rect(self.screen, (255, 120, 160), rr, 2, border_radius=10)

        if self.story_defend_point and self.story_defend_radius > 0:
            center = (int(self.story_defend_point.x - cam.x), int(self.story_defend_point.y - cam.y))
            radius = int(self.story_defend_radius)
            pygame.draw.circle(self.screen, (120, 255, 210, 70), center, radius, 0)
            pygame.draw.circle(self.screen, C_ACCENT, center, radius, 2)
            pygame.draw.circle(self.screen, C_ACCENT_2, center, 10, 0)
            if self.beacon_active():
                # Beacon icon + HP bar for Level 4 defense.
                beacon_center = (int(self.story_beacon_pos.x - cam.x), int(self.story_beacon_pos.y - cam.y))
                pygame.draw.circle(self.screen, (255, 220, 140), beacon_center, self.story_beacon_radius)
                circle_outline(self.screen, (120, 80, 40), beacon_center, self.story_beacon_radius + 4, 2)
                bar_w = 80
                bar_h = 8
                bar_x = beacon_center[0] - bar_w // 2
                bar_y = beacon_center[1] - self.story_beacon_radius - 18
                frac = clamp(self.story_beacon_hp / max(1, self.story_beacon_max), 0, 1)
                pygame.draw.rect(self.screen, (10, 10, 12), pygame.Rect(bar_x, bar_y, bar_w, bar_h))
                pygame.draw.rect(self.screen, (255, 120, 140), pygame.Rect(bar_x, bar_y, int(bar_w * frac), bar_h))

        self.draw_boss_rocket_strikes()

    def draw_pickup_indicators(self, t_seconds: float):
        cam = self.cam + self.shake_vec

        # where the line "comes from" on screen (player)
        origin = Vector2(self.player.pos.x - cam.x, self.player.pos.y - cam.y)

        # pull markers inward so they don't clip
        inset = 22
        left = inset
        right = WIDTH - inset
        top = inset
        bottom = HEIGHT - inset

        def ray_to_screen_edge(o: Vector2, dirn: Vector2) -> Optional[Vector2]:
            """Return intersection point of ray o + t*dirn with inset screen rect."""
            t_candidates = []

            if abs(dirn.x) > 1e-8:
                t = (left - o.x) / dirn.x
                y = o.y + dirn.y * t
                if t > 0 and top <= y <= bottom:
                    t_candidates.append(t)

                t = (right - o.x) / dirn.x
                y = o.y + dirn.y * t
                if t > 0 and top <= y <= bottom:
                    t_candidates.append(t)

            if abs(dirn.y) > 1e-8:
                t = (top - o.y) / dirn.y
                x = o.x + dirn.x * t
                if t > 0 and left <= x <= right:
                    t_candidates.append(t)

                t = (bottom - o.y) / dirn.y
                x = o.x + dirn.x * t
                if t > 0 and left <= x <= right:
                    t_candidates.append(t)

            if not t_candidates:
                return None

            t_edge = min(t_candidates)
            p = o + dirn * t_edge
            p.x = clamp(p.x, left, right)
            p.y = clamp(p.y, top, bottom)
            return p

        # transparent overlay so arrows aren't loud
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for p in self.pickups:
            # only track POWERUPS (rapid fire / damage / etc)
            if p.kind != "power":
                continue

            screen = Vector2(p.pos.x - cam.x, p.pos.y - cam.y)

            # if it's on-screen, don't show an indicator
            if (-10 <= screen.x <= WIDTH + 10) and (-10 <= screen.y <= HEIGHT + 10):
                continue

            d = screen - origin
            if d.length_squared() < 1e-6:
                continue
            dirn = d.normalize()

            edge = ray_to_screen_edge(origin, dirn)
            if edge is None:
                continue

            # little pulsing + color by type
            col = {
                "damage_boost": (255, 120, 220),
                "rapid_fire": (120, 255, 240),
                "speed_boost": (140, 255, 160),
                "shield": (200, 200, 255),
            }.get(p.power_type, (220, 210, 255))

            pulse = 0.5 + 0.5 * math.sin(t_seconds * 6.0 + (p.pos.x + p.pos.y) * 0.003)
            a = int(90 + 70 * pulse)  # subtle

            tip = edge
            back = tip - dirn * 18
            perp = Vector2(-dirn.y, dirn.x)

            left_pt = back + perp * 8
            right_pt = back - perp * 8

            # draw arrow
            pygame.draw.polygon(
                overlay,
                (*col, a),
                [(int(tip.x), int(tip.y)),
                 (int(left_pt.x), int(left_pt.y)),
                 (int(right_pt.x), int(right_pt.y))]
            )

            # small ring for clarity
            pygame.draw.circle(overlay, (*col, int(a * 0.75)), (int(tip.x), int(tip.y)), 12, 2)

        self.screen.blit(overlay, (0, 0))


    def draw_entities(self):
        cam = self.cam + self.shake_vec
        tsec = time.time()

        for p in self.pickups:
            p.draw(self.screen, cam, tsec)

        for pt in self.particles:
            pt.draw(self.screen, cam)

        for b in self.projectiles:
            b.draw(self.screen, cam)
        for b in self.enemy_projectiles:
            b.draw(self.screen, cam)

        visibility_radius = self.story_visibility_radius if self.mode == "story" else None
        if visibility_radius:
            # Level 3: hide enemies completely outside the vision circle.
            rad2 = visibility_radius * visibility_radius
            for e in self.enemies:
                if (e.pos - self.player.pos).length_squared() > rad2:
                    continue
                e.draw(self.screen, cam)
        else:
            for e in self.enemies:
                e.draw(self.screen, cam)

        for ft in self.float_texts:
            ft.draw(self.screen, cam, self.font_small)

        self.player.draw(self.screen, cam)
        self.draw_pickup_indicators(tsec)

    def _get_boss(self) -> Optional[Boss]:
        for e in self.enemies:
            if isinstance(e, Boss) and e.alive():
                return e
        return None

    def draw_minimap(self, map_rect: pygame.Rect):
        pygame.draw.rect(self.screen, (*C_PANEL_2, 230), map_rect, border_radius=8)
        pygame.draw.rect(self.screen, (*C_WALL_EDGE, 200), map_rect, 2, border_radius=8)

        arena = self.arena_rect
        if arena.width <= 0 or arena.height <= 0:
            return

        inner = map_rect.inflate(-4, -4)

        def world_to_minimap(pos: Vector2) -> Tuple[int, int]:
            # World -> minimap transform (cached world bounds, clamped to map rect).
            mx = map_rect.left + (pos.x - arena.left) / arena.width * map_rect.w
            my = map_rect.top + (pos.y - arena.top) / arena.height * map_rect.h
            mx = clamp(mx, inner.left, inner.right)
            my = clamp(my, inner.top, inner.bottom)
            return int(mx), int(my)

        for fx, fy, fw, fh in self.minimap_obstacle_cache:
            rx = map_rect.left + fx * map_rect.w
            ry = map_rect.top + fy * map_rect.h
            rw = max(2, fw * map_rect.w)
            rh = max(2, fh * map_rect.h)
            rect = pygame.Rect(int(rx), int(ry), int(rw), int(rh))
            pygame.draw.rect(self.screen, (40, 46, 70), rect, border_radius=3)

        if self.mode == "story" and self.story_hazard_zones:
            for hz in self.story_hazard_zones:
                rect = hz["rect"]
                rx = map_rect.left + (rect.x - arena.left) / arena.width * map_rect.w
                ry = map_rect.top + (rect.y - arena.top) / arena.height * map_rect.h
                rw = max(2, rect.w / arena.width * map_rect.w)
                rh = max(2, rect.h / arena.height * map_rect.h)
                hrect = pygame.Rect(int(rx), int(ry), int(rw), int(rh))
                pygame.draw.rect(self.screen, (200, 90, 120), hrect, 1, border_radius=2)

        for e in self.enemies:
            ex, ey = world_to_minimap(e.pos)
            pygame.draw.circle(self.screen, (255, 150, 190), (ex, ey), 2)

        if self.beacon_active():
            bx, by = world_to_minimap(self.story_beacon_pos)
            pygame.draw.circle(self.screen, (255, 220, 140), (bx, by), 3)
            pygame.draw.circle(self.screen, (120, 80, 40), (bx, by), 4, 1)

        px, py = world_to_minimap(self.player.pos)
        pygame.draw.circle(self.screen, C_PLAYER, (px, py), 3)
        pygame.draw.circle(self.screen, (20, 30, 40), (px, py), 4, 1)

    def draw_hud(self):
        x = UI_PAD
        y = UI_PAD

        panel = pygame.Rect(x - 10, y - 10, 420, 130)
        pygame.draw.rect(self.screen, (*C_PANEL, 220), panel, border_radius=12)
        pygame.draw.rect(self.screen, (*C_WALL_EDGE, 200), panel, 2, border_radius=12)

        label_w = 64
        circle_start_x = x + label_w
        line1_y = y + 2
        line2_y = y + 38

        show_beacon_hp = self.mode == "story" and self.story_level_index == 4 and self.beacon_active()
        if show_beacon_hp:
            draw_text(self.screen, self.font_ui, "BEACON", (x, line1_y), C_TEXT)
            bar_w = 260
            bar_h = 16
            bx = circle_start_x
            by = line1_y + 6
            pygame.draw.rect(self.screen, (10, 10, 12), pygame.Rect(bx, by, bar_w, bar_h), border_radius=6)
            frac = clamp(self.story_beacon_hp / max(1, self.story_beacon_max), 0, 1)
            pygame.draw.rect(self.screen, (255, 180, 120), pygame.Rect(bx, by, int(bar_w * frac), bar_h), border_radius=6)
            pygame.draw.rect(self.screen, (255, 200, 150), pygame.Rect(bx, by, bar_w, bar_h), 2, border_radius=6)
            beacon_value = f"{int(self.story_beacon_hp)}/{int(self.story_beacon_max)}"
            draw_text(self.screen, self.font_tiny, beacon_value, (bx + bar_w + 8, by - 1), C_TEXT_DIM, shadow=False)
        else:
            draw_text(self.screen, self.font_ui, "HP", (x, line1_y), C_TEXT)
            hp = int(self.player.hp)
            mhp = int(self.player.max_hp)

            r = 7
            gap = 6
            max_per_row = 12
            cx0 = circle_start_x + r
            cy0 = line1_y + 10

            for i in range(mhp):
                row = i // max_per_row
                col = i % max_per_row
                px = cx0 + col * (r * 2 + gap)
                py = cy0 + row * (r * 2 + 6)

                filled = i < hp
                if filled:
                    pygame.draw.circle(self.screen, C_HEALTH, (px, py), r)
                circle_outline(self.screen, (255, 160, 190), (px, py), r + 2, 2)

        draw_text(self.screen, self.font_ui, f"LVL {self.player.level}", (x, line2_y), C_TEXT)
        bx2 = circle_start_x
        by2 = line2_y + 2
        bar_w = 260
        bar_h = 16
        pygame.draw.rect(self.screen, (10, 10, 12), pygame.Rect(bx2, by2, bar_w, bar_h), border_radius=6)
        frac2 = self.player.xp / max(1, self.player.xp_to_next)
        pygame.draw.rect(self.screen, C_XP, pygame.Rect(bx2, by2, int(bar_w * clamp(frac2, 0, 1)), bar_h), border_radius=6)
        pygame.draw.rect(self.screen, (60, 200, 120), pygame.Rect(bx2, by2, bar_w, bar_h), 2, border_radius=6)

        draw_text(self.screen, self.font_small, f"{self.player.weapon.name}", (x, y + 92), C_ACCENT, shadow=False)

        sx = WIDTH - UI_PAD - 300
        sy = UI_PAD
        panel2 = pygame.Rect(sx - 10, sy - 10, 310, 130)
        pygame.draw.rect(self.screen, (*C_PANEL, 220), panel2, border_radius=12)
        pygame.draw.rect(self.screen, (*C_WALL_EDGE, 200), panel2, 2, border_radius=12)

        map_size = 96
        map_pad = 12
        map_rect = pygame.Rect(panel2.right - map_size - map_pad, panel2.y + map_pad, map_size, map_size)
        text_x = panel2.x + 14
        text_y = panel2.y + 10

        draw_text(self.screen, self.font_ui, f"Score: {self.player.score}", (text_x, text_y), C_TEXT)
        draw_text(self.screen, self.font_ui, f"Wave: {self.wave}", (text_x, text_y + 28), C_TEXT)
        draw_text(self.screen, self.font_ui, f"Time: {int(self.survival_time)}s", (text_x, text_y + 56), C_TEXT)
        draw_text(self.screen, self.font_ui, f"Coins: {self.save.coins}", (text_x, text_y + 84), C_COIN)

        self.draw_minimap(map_rect)

        if self.mode == "endless" and self.active_modifiers:
            remaining = self.modifier_waves_remaining()
            mod_panel_w = 310
            line_h = 18
            mod_panel_h = 36 + line_h * len(self.active_modifiers)
            mod_x = panel2.x
            mod_y = panel2.bottom + 10
            mod_panel = pygame.Rect(mod_x, mod_y, mod_panel_w, mod_panel_h)
            pygame.draw.rect(self.screen, (*C_PANEL, 215), mod_panel, border_radius=12)
            pygame.draw.rect(self.screen, (*C_WALL_EDGE, 200), mod_panel, 2, border_radius=12)
            header = f"Modifiers ({remaining}w)"
            draw_text(self.screen, self.font_small, header, (mod_panel.x + 12, mod_panel.y + 8), C_TEXT, shadow=False)
            for idx, mod in enumerate(self.active_modifiers):
                label = clamp_text(self.font_small, mod.name, mod_panel.w - 26)
                draw_text(self.screen, self.font_small, f"• {label}",
                          (mod_panel.x + 12, mod_panel.y + 26 + idx * line_h), C_TEXT_DIM, shadow=False)

        if self.mode == "story":
            story_w = 620
            base_story_h = 46
            padding = 10
            story_x = WIDTH // 2 - story_w // 2
            top_hud_bottom = max(panel.bottom, panel2.bottom)
            available = HEIGHT - top_hud_bottom - 12
            story_h = min(base_story_h, max(40, available - padding))
            if available < story_h + padding:
                padding = max(8, available - story_h)
            story_y = top_hud_bottom + padding
            story_panel = pygame.Rect(story_x, story_y, story_w, story_h)
            pygame.draw.rect(self.screen, (*C_PANEL, 215), story_panel, border_radius=12)
            pygame.draw.rect(self.screen, (*C_WALL_EDGE, 200), story_panel, 2, border_radius=12)
            level_label = f"STORY LEVEL {self.story_level_index}: {self.story_config.get('name', '') if self.story_config else ''}"
            obj_label = self.story_objective_progress_text()
            level_y = story_panel.y + 6
            obj_y = story_panel.y + story_panel.h - 22
            draw_text(self.screen, self.font_small, level_label, (story_panel.centerx, level_y),
                      C_ACCENT, center=True, shadow=False)
            draw_text(self.screen, self.font_small, obj_label, (story_panel.centerx, obj_y),
                      C_TEXT, center=True, shadow=False)

        boss = self._get_boss()
        if boss is not None:
            w = 520
            h = 18
            bx = WIDTH // 2 - w // 2
            by = 18
            pygame.draw.rect(self.screen, (*C_PANEL, 220), pygame.Rect(bx - 10, by - 10, w + 20, h + 34), border_radius=12)
            pygame.draw.rect(self.screen, (*C_WALL_EDGE, 200), pygame.Rect(bx - 10, by - 10, w + 20, h + 34), 2, border_radius=12)

            draw_text(self.screen, self.font_small, "BOSS", (WIDTH // 2, by - 2), C_ACCENT_2, center=True, shadow=False)

            frac = clamp(boss.hp / max(1.0, boss.hp_max), 0, 1)
            pygame.draw.rect(self.screen, (10, 10, 12), pygame.Rect(bx, by + 16, w, h), border_radius=8)
            pygame.draw.rect(self.screen, (255, 120, 140), pygame.Rect(bx, by + 16, int(w * frac), h), border_radius=8)
            pygame.draw.rect(self.screen, (255, 190, 210), pygame.Rect(bx, by + 16, w, h), 2, border_radius=8)

            if self.boss_banner_timer > 0:
                draw_text(self.screen, self.font_med, "BOSS FIGHT!", (WIDTH // 2, 86), C_ACCENT_2, center=True)

    def draw_boss_tracker(self):
        """Off-screen tracker: a subtle transparent line from the PLAYER toward the boss.
        Only draws when the boss is off-screen. Endpoint is true screen-edge intersection.
        """
        boss = self._get_boss()
        if boss is None:
            return

        cam = self.cam + self.shake_vec

        # Boss + player in screen space
        boss_s = Vector2(boss.pos.x - cam.x, boss.pos.y - cam.y)
        player_s = Vector2(self.player.pos.x - cam.x, self.player.pos.y - cam.y)

        # Only draw when boss is off-screen
        off_margin = 40
        if (-off_margin <= boss_s.x <= WIDTH + off_margin) and (-off_margin <= boss_s.y <= HEIGHT + off_margin):
            return

        d = boss_s - player_s
        if d.length_squared() < 1e-6:
            return
        dirn = d.normalize()

        # --- Find intersection of ray (player_s -> dirn) with screen rect, minus an inset margin ---
        inset = 26  # pull endpoint inside screen so label always fits
        left = inset
        right = WIDTH - inset
        top = inset
        bottom = HEIGHT - inset

        t_candidates = []

        # Vertical sides
        if abs(dirn.x) > 1e-8:
            t = (left - player_s.x) / dirn.x
            y = player_s.y + dirn.y * t
            if t > 0 and top <= y <= bottom:
                t_candidates.append(t)

            t = (right - player_s.x) / dirn.x
            y = player_s.y + dirn.y * t
            if t > 0 and top <= y <= bottom:
                t_candidates.append(t)

        # Horizontal sides
        if abs(dirn.y) > 1e-8:
            t = (top - player_s.y) / dirn.y
            x = player_s.x + dirn.x * t
            if t > 0 and left <= x <= right:
                t_candidates.append(t)

            t = (bottom - player_s.y) / dirn.y
            x = player_s.x + dirn.x * t
            if t > 0 and left <= x <= right:
                t_candidates.append(t)

        if not t_candidates:
            return

        t_edge = min(t_candidates)
        edge = player_s + dirn * t_edge

        # Nudge the whole marker up a few pixels so the distance text is always visible
        nudge_up = 10
        edge.y -= nudge_up

        # Final clamp (just in case)
        edge.x = clamp(edge.x, left, right)
        edge.y = clamp(edge.y, top, bottom)

        # --- Draw on a transparent overlay so it’s visible but not loud ---
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        # Softer, semi-transparent line
        LINE_COL = (*C_ACCENT_2, 95)     # low alpha so it’s not distracting
        OUTLINE_COL = (0, 0, 0, 70)      # faint outline for readability

        p1 = (int(player_s.x), int(player_s.y))
        p2 = (int(edge.x), int(edge.y))

        pygame.draw.line(overlay, OUTLINE_COL, p1, p2, 6)
        pygame.draw.line(overlay, LINE_COL, p1, p2, 3)

        # Small end-cap so you can see where it’s pointing
        pygame.draw.circle(overlay, OUTLINE_COL, p2, 9, 3)
        pygame.draw.circle(overlay, LINE_COL, p2, 9, 2)

        self.screen.blit(overlay, (0, 0))

        # Distance label: ABOVE the endpoint (so it never gets cut off at bottom)
        dist = (boss.pos - self.player.pos).length()
        draw_text(
            self.screen,
            self.font_tiny,
            f"{int(dist)}",
            (p2[0], p2[1] - 16),
            C_TEXT,
            center=True,
            shadow=False
        )

    def draw_overlay_dim(self, alpha=170):
        o = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        o.fill((0, 0, 0, alpha))
        self.screen.blit(o, (0, 0))

    def draw_story_visibility(self):
        if self.mode != "story" or not self.story_visibility_radius:
            return
        cam = self.cam + self.shake_vec
        radius = int(self.story_visibility_radius)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 255))
        center = (int(self.player.pos.x - cam.x), int(self.player.pos.y - cam.y))
        pygame.draw.circle(overlay, (0, 0, 0, 0), center, radius)
        pygame.draw.circle(overlay, (0, 0, 0, 0), center, int(radius * 0.6))
        self.screen.blit(overlay, (0, 0))
        
    # =========================================================
    # SCREENS
    # =========================================================
    def draw_menu(self, events):
        self.screen.fill(C_BG)
        cx = WIDTH // 2
        t = time.time()
        self.refresh_challenges()

        draw_text(self.screen, self.font_big, "TANK GAME SURVIVAL", (cx, 92), C_TEXT, center=True)
        draw_text(self.screen, self.font_ui, "survive • upgrade • progress • unlock tanks", (cx, 128), C_TEXT_DIM, center=True, shadow=False)
        pygame.draw.line(self.screen, C_ACCENT, (cx - 360, 148), (cx + 360, 148), 2)
        pygame.draw.line(self.screen, C_ACCENT_2, (cx - 310, 154), (cx + 310, 154), 2)

        panel_w = 760
        panel = pygame.Rect(cx - panel_w // 2, 168, panel_w, 76)
        pygame.draw.rect(self.screen, (*C_PANEL, 230), panel, border_radius=16)
        pygame.draw.rect(self.screen, (*C_WALL_EDGE, 220), panel, 2, border_radius=16)

        wdef = WEAPONS.get(self.save.selected_weapon, WEAPONS["pistol"])
        draw_text(self.screen, self.font_ui, f"Coins: {self.save.coins}", (panel.x + 18, panel.y + 16), C_COIN, shadow=False)
        draw_text(self.screen, self.font_ui, f"Selected: {wdef.name}", (panel.x + 18, panel.y + 44), C_ACCENT, shadow=False)
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)
        for b in self.menu_buttons:
            b.update(1 / 60, mouse_pos, mouse_down, events)
            b.draw(self.screen, self.font_med)

        if self.menu_challenges_btn:
            self.menu_challenges_btn.update(1 / 60, mouse_pos, mouse_down, events)
            self.menu_challenges_btn.draw(self.screen, self.font_small)

        # Top-left X quit button
        self.menu_quit_btn.update(1 / 60, mouse_pos, mouse_down, events)
        self.menu_quit_btn.draw(self.screen, self.font_med)

        if self.menu_daily_wheel_btn:
            self.menu_daily_wheel_btn.update(1 / 60, mouse_pos, mouse_down, events)
            self.menu_daily_wheel_btn.draw(self.screen, self.font_med)
            self.draw_wheel_icon(self.menu_daily_wheel_btn.rect, self.menu_daily_wheel_btn.hover)
            draw_text(self.screen, self.font_tiny, "Daily", (self.menu_daily_wheel_btn.rect.centerx,
                                                            self.menu_daily_wheel_btn.rect.bottom + 14),
                      C_TEXT_DIM, center=True, shadow=False)


        controls1 = "WASD to move • Mouse to aim • Hold LMB to shoot"
        controls2 = "Space to dash • F to toggle auto-fire • ESC to pause"
        draw_text(self.screen, self.font_small, controls1, (cx, HEIGHT - 44), C_TEXT_DIM, center=True, shadow=False)
        draw_text(self.screen, self.font_small, controls2, (cx, HEIGHT - 24), C_TEXT_DIM, center=True, shadow=False)

        pygame.draw.circle(self.screen, (*C_ACCENT, 255), (int(cx + math.sin(t * 1.3) * 320), 156), 3)
        pygame.draw.circle(self.screen, (*C_ACCENT_2, 255), (int(cx + math.cos(t * 1.1) * 300), 156), 3)

    def draw_wheel_icon(self, rect: pygame.Rect, hover=False):
        center = rect.center
        radius = rect.width // 2 - 12
        icon_col = C_ACCENT if hover else C_TEXT_DIM
        pygame.draw.circle(self.screen, icon_col, center, radius, 2)
        for i in range(8):
            ang = math.tau * (i / 8) - math.pi / 2
            end = (center[0] + math.cos(ang) * radius, center[1] + math.sin(ang) * radius)
            pygame.draw.line(self.screen, icon_col, center, end, 1)
        stand = pygame.Rect(0, 0, 16, 8)
        stand.center = (center[0], center[1] + radius + 8)
        pygame.draw.rect(self.screen, icon_col, stand, border_radius=3)

    def draw_daily_wheel(self, events, dt):
        self.screen.fill(C_BG)
        cx = WIDTH // 2
        draw_text(self.screen, self.font_big, "DAILY WHEEL", (cx, 92), C_TEXT, center=True)
        draw_text(self.screen, self.font_ui, "Spin once every 24 hours for a reward", (cx, 128),
                  C_TEXT_DIM, center=True, shadow=False)

        wheel_center = (cx, HEIGHT // 2 - 10)
        wheel_radius = 170
        slice_angle = math.tau / len(DAILY_WHEEL_REWARDS)
        slice_colors = [C_PANEL_2, C_PANEL, (28, 34, 50), (22, 28, 42)]

        for i, reward in enumerate(DAILY_WHEEL_REWARDS):
            start = self.daily_wheel_angle + i * slice_angle
            end = start + slice_angle
            points = [wheel_center]
            steps = 10
            for s in range(steps + 1):
                ang = start + (end - start) * (s / steps)
                px = wheel_center[0] + math.cos(ang) * wheel_radius
                py = wheel_center[1] + math.sin(ang) * wheel_radius
                points.append((px, py))
            pygame.draw.polygon(self.screen, slice_colors[i % len(slice_colors)], points)
            pygame.draw.polygon(self.screen, (*C_WALL_EDGE, 200), points, 1)

            mid = start + slice_angle / 2
            label_pos = (
                wheel_center[0] + math.cos(mid) * (wheel_radius * 0.62),
                wheel_center[1] + math.sin(mid) * (wheel_radius * 0.62),
            )
            draw_text(self.screen, self.font_tiny, reward["short"], label_pos, C_TEXT, center=True, shadow=False)

        pygame.draw.circle(self.screen, (*C_WALL_EDGE, 210), wheel_center, wheel_radius, 3)
        pygame.draw.circle(self.screen, (*C_PANEL, 200), wheel_center, 8)

        pointer_y = wheel_center[1] - wheel_radius + 12
        pointer = [
            (wheel_center[0], pointer_y),
            (wheel_center[0] - 12, pointer_y - 18),
            (wheel_center[0] + 12, pointer_y - 18),
        ]
        pygame.draw.polygon(self.screen, C_ACCENT_2, pointer)

        remaining = self.daily_wheel_remaining()
        available = remaining <= 0.0
        status_text = "Ready to spin!" if available else f"Available in {self.format_cooldown(remaining)}"
        draw_text(self.screen, self.font_small, status_text, (cx, wheel_center[1] + wheel_radius + 36),
                  C_TEXT_DIM if not available else C_ACCENT, center=True, shadow=False)

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)

        if self.daily_wheel_spin_btn:
            self.daily_wheel_spin_btn.enabled = available and not self.daily_wheel_spinning
            self.daily_wheel_spin_btn.update(dt, mouse_pos, mouse_down, events)
            self.daily_wheel_spin_btn.draw(self.screen, self.font_med)

        if self.daily_wheel_back_btn:
            self.daily_wheel_back_btn.update(dt, mouse_pos, mouse_down, events)
            self.daily_wheel_back_btn.draw(self.screen, self.font_med)

        if self.daily_wheel_message_timer > 0:
            msg_box = pygame.Rect(cx - 260, wheel_center[1] + wheel_radius + 60, 520, 48)
            pygame.draw.rect(self.screen, (*C_PANEL, 230), msg_box, border_radius=12)
            pygame.draw.rect(self.screen, (*C_WALL_EDGE, 210), msg_box, 2, border_radius=12)
            draw_text(self.screen, self.font_small, self.daily_wheel_message, msg_box.center, C_TEXT, center=True)

    def draw_story_menu(self, events):
        self.screen.fill(C_BG)
        cx = WIDTH // 2

        draw_text(self.screen, self.font_big, "STORY MODE", (cx, 92), C_TEXT, center=True)
        draw_text(self.screen, self.font_ui, "Complete levels to unlock the next", (cx, 128),
                  C_TEXT_DIM, center=True, shadow=False)

        box = pygame.Rect(90, 170, WIDTH - 180, HEIGHT - 280)
        pygame.draw.rect(self.screen, (*C_PANEL, 235), box, border_radius=16)
        pygame.draw.rect(self.screen, (*C_WALL_EDGE, 220), box, 2, border_radius=16)

        unlocked = self.get_unlocked_story_level()
        hovered_level = None

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)

        for idx, btn in enumerate(self.story_level_buttons, start=1):
            level_cfg = LEVELS[idx - 1]
            btn.enabled = idx <= unlocked
            label = f"Level {idx}: {level_cfg['name']}"
            if not btn.enabled:
                label = f"Level {idx}: Locked"
            btn.text = label
            btn.update(1 / 60, mouse_pos, mouse_down, events)
            btn.draw(self.screen, self.font_small if btn.enabled else self.font_small)
            if btn.hover:
                hovered_level = level_cfg

        info_box = pygame.Rect(box.x + 22, box.bottom - 78, box.w - 44, 58)
        pygame.draw.rect(self.screen, (*C_PANEL_2, 240), info_box, border_radius=12)
        pygame.draw.rect(self.screen, (*C_WALL_EDGE, 200), info_box, 2, border_radius=12)
        info = hovered_level["objective"] if hovered_level else "Hover a level to preview the objective."
        draw_text(self.screen, self.font_small, info, (info_box.centerx, info_box.centery),
                  C_TEXT_DIM if hovered_level is None else C_TEXT, center=True, shadow=False)

        self.story_continue_btn.enabled = unlocked >= 1
        self.story_continue_btn.update(1 / 60, mouse_pos, mouse_down, events)
        self.story_continue_btn.draw(self.screen, self.font_med)

        if self.story_back_btn:
            self.story_back_btn.update(1 / 60, mouse_pos, mouse_down, events)
            self.story_back_btn.draw(self.screen, self.font_med)

    def draw_story_complete(self, events):
        self.award_coins_if_needed()
        self.draw_background()
        self.draw_obstacles()
        self.draw_story_objects()
        self.draw_entities()
        self.draw_story_visibility()
        self.draw_hud()

        self.draw_overlay_dim(200)
        draw_text(self.screen, self.font_big, "LEVEL COMPLETE", (WIDTH // 2, 120), C_OK, center=True)

        stats = self.story_level_complete_stats or {}
        lines = [
            f"Level: {self.story_level_index}",
            f"Score: {stats.get('score', 0)}",
            f"Kills: {stats.get('kills', 0)}",
            f"Time: {stats.get('time', 0)}s",
            f"Coins Earned: +{self.last_run_coins_earned}",
        ]
        y = 190
        for line in lines:
            draw_text(self.screen, self.font_med, line, (WIDTH // 2, y), C_TEXT, center=True)
            y += 34

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)

        has_next = self.story_level_index < self.story_levels_count()
        self.story_complete_next_btn.enabled = has_next
        self.story_complete_next_btn.update(1 / 60, mouse_pos, mouse_down, events)
        self.story_complete_next_btn.draw(self.screen, self.font_med)

        self.story_complete_menu_btn.update(1 / 60, mouse_pos, mouse_down, events)
        self.story_complete_menu_btn.draw(self.screen, self.font_med)

    def draw_settings(self, events):
        self.screen.fill(C_BG)
        cx = WIDTH // 2

        draw_text(self.screen, self.font_big, "SETTINGS", (cx, 92), C_TEXT, center=True)
        draw_text(self.screen, self.font_ui, "Customize your run feel", (cx, 128), C_TEXT_DIM, center=True, shadow=False)

        box = pygame.Rect(140, 175, WIDTH - 280, HEIGHT - 275)
        pygame.draw.rect(self.screen, (*C_PANEL, 235), box, border_radius=16)
        pygame.draw.rect(self.screen, (*C_WALL_EDGE, 220), box, 2, border_radius=16)

        opt_w = 220
        opt_h = 46
        opt_y = box.y + 26
        opt_gap = 16
        opt_x = box.x + 16

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)

        def draw_option(label, value_on, on_click, x):
            rect = pygame.Rect(x, opt_y, opt_w, opt_h)
            pygame.draw.rect(self.screen, (*C_PANEL_2, 245), rect, border_radius=12)
            pygame.draw.rect(self.screen, (*C_WALL_EDGE, 200), rect, 2, border_radius=12)
            draw_text(self.screen, self.font_shop_small, label, (rect.x + 14, rect.y + 12), C_TEXT, shadow=False)
            badge = pygame.Rect(rect.right - 60, rect.y + 8, 48, 28)
            pygame.draw.rect(self.screen, (*C_OK, 220) if value_on else (*C_TEXT_DIM, 160), badge, border_radius=8)
            pygame.draw.rect(self.screen, C_WALL_EDGE, badge, 2, border_radius=8)
            rect_centered_text(self.screen, self.font_tiny, "ON" if value_on else "OFF", badge,
                               (10, 20, 20) if value_on else (25, 25, 32), shadow=False)
            if rect.collidepoint(mouse_pos) and mouse_down:
                on_click()

        draw_option("Screen Shake", bool(self.save.settings.get("shake", True)), lambda: self.toggle_setting("shake"), opt_x)
        draw_option("Audio", bool(self.save.settings.get("audio", True)), lambda: self.toggle_setting("audio"), opt_x + opt_w + opt_gap)

        reset_y = opt_y + opt_h + 50
        draw_text(self.screen, self.font_shop_item, "RESET", (box.x + 16, reset_y), C_TEXT, shadow=False)

        reset_btn_y = reset_y + 34
        reset_w = 240
        reset_h = 46
        reset_gap = 16
        reset_x = box.x + 16

        reset_settings_btn = Button(pygame.Rect(reset_x, reset_btn_y, reset_w, reset_h), "Defaults", self.reset_settings)
        reset_cosmetics_btn = Button(pygame.Rect(reset_x + reset_w + reset_gap, reset_btn_y, reset_w, reset_h), "Reset Cosmetics", self.reset_cosmetics)

        for btn in (reset_settings_btn, reset_cosmetics_btn):
            btn.update(1 / 60, mouse_pos, mouse_down, events)
            btn.draw(self.screen, self.font_shop_small)

        if self.settings_back_btn:
            self.settings_back_btn.update(1 / 60, mouse_pos, mouse_down, events)
            self.settings_back_btn.draw(self.screen, self.font_med)

    def draw_controls(self):
        self.screen.fill(C_BG)
        draw_text(self.screen, self.font_big, "CONTROLS", (WIDTH // 2, 100), C_TEXT, center=True)
        lines = [
            "WASD — Move",
            "Mouse — Aim",
            "LMB — Shoot (hold = auto-fire)",
            "Space — Dash (invulnerable, cooldown)",
            "ESC — Pause / Back",
        ]
        y = 190
        for ln in lines:
            draw_text(self.screen, self.font_med, ln, (WIDTH // 2, y), C_TEXT, center=True)
            y += 42
        draw_text(self.screen, self.font_ui, "Press ESC / Backspace to return", (WIDTH // 2, HEIGHT - 60), C_TEXT_DIM, center=True, shadow=False)

    def draw_leaderboard(self, events):
        self.screen.fill(C_BG)
        cx = WIDTH // 2

        draw_text(self.screen, self.font_big, "LEADERBOARD", (cx, 92), C_TEXT, center=True)
        draw_text(self.screen, self.font_ui, "Top runs by score", (cx, 128), C_TEXT_DIM, center=True, shadow=False)

        box = pygame.Rect(140, 170, WIDTH - 280, HEIGHT - 280)
        pygame.draw.rect(self.screen, (*C_PANEL, 235), box, border_radius=16)
        pygame.draw.rect(self.screen, (*C_WALL_EDGE, 220), box, 2, border_radius=16)

        header = pygame.Rect(box.x + 10, box.y + 12, box.w - 20, 44)
        pygame.draw.rect(self.screen, (*C_PANEL_2, 240), header, border_radius=12)
        pygame.draw.rect(self.screen, (*C_WALL_EDGE, 200), header, 2, border_radius=12)

        col_rank = header.x + 16
        col_score = header.x + 110
        col_time = header.x + 300
        col_wave = header.x + 470
        col_level = header.right - 110

        header_y = header.y + 12
        draw_text(self.screen, self.font_ui, "RANK", (col_rank, header_y), C_TEXT_DIM, shadow=False)
        draw_text(self.screen, self.font_ui, "SCORE", (col_score, header_y), C_TEXT_DIM, shadow=False)
        draw_text(self.screen, self.font_ui, "TIME", (col_time, header_y), C_TEXT_DIM, shadow=False)
        draw_text(self.screen, self.font_ui, "WAVE", (col_wave, header_y), C_TEXT_DIM, shadow=False)
        draw_text(self.screen, self.font_ui, "LEVEL", (col_level, header_y), C_TEXT_DIM, shadow=False)

        entries = list(self.save.leaderboard)
        if not entries:
            draw_text(self.screen, self.font_med, "No runs yet — play a game to set a score!", (cx, box.centery), C_TEXT_DIM, center=True, shadow=False)
        else:
            row_y = header.bottom + 12
            row_gap = 10
            row_h = 40
            for idx, entry in enumerate(entries, start=1):
                row = pygame.Rect(box.x + 10, row_y, box.w - 20, row_h)
                row_color = (*C_PANEL_2, 220) if idx % 2 == 0 else (*C_PANEL_2, 180)
                pygame.draw.rect(self.screen, row_color, row, border_radius=10)
                pygame.draw.rect(self.screen, (*C_WALL_EDGE, 150), row, 1, border_radius=10)

                badge = pygame.Rect(row.x + 8, row.y + 8, 48, row_h - 16)
                badge_color = (*C_PANEL, 220)
                pygame.draw.rect(self.screen, badge_color, badge, border_radius=8)
                pygame.draw.rect(self.screen, (*C_WALL_EDGE, 190), badge, 2, border_radius=8)
                rect_centered_text(self.screen, self.font_small, f"{idx}", badge, (255, 255, 255), shadow=False)

                draw_text(self.screen, self.font_ui, f"{entry['score']}", (col_score, row.y + 12), C_TEXT, shadow=False)
                draw_text(self.screen, self.font_ui, f"{entry['time']}s", (col_time, row.y + 12), C_TEXT, shadow=False)
                draw_text(self.screen, self.font_ui, f"{entry['wave']}", (col_wave, row.y + 12), C_TEXT, shadow=False)
                draw_text(self.screen, self.font_ui, f"{entry['level']}", (col_level, row.y + 12), C_TEXT, shadow=False)
                row_y += row_h + row_gap

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)
        if self.leaderboard_back_btn:
            self.leaderboard_back_btn.update(1 / 60, mouse_pos, mouse_down, events)
            self.leaderboard_back_btn.draw(self.screen, self.font_med)

    def draw_challenges(self, events):
        self.screen.fill(C_BG)
        self.refresh_challenges()
        cx = WIDTH // 2

        title_y = 92
        subtitle_y = 128
        tab_y = subtitle_y + 32
        tab_gap = 18

        draw_text(self.screen, self.font_big, "CHALLENGES", (cx, title_y), C_TEXT, center=True)
        subtitle = "Daily goals reset automatically" if self.challenges_view == "daily" else "Weekly goals reset automatically"
        draw_text(self.screen, self.font_ui, subtitle, (cx, subtitle_y), C_TEXT_DIM, center=True, shadow=False)

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)

        tab_h = self.challenge_tabs[0].rect.height if self.challenge_tabs else 0
        for tab in self.challenge_tabs:
            tab.rect.y = tab_y
            tab.update(mouse_pos, mouse_down)
            tab.draw(self.screen, self.font_shop_item, active=(tab.tab_id == self.challenges_view))

        box_y = tab_y + tab_h + tab_gap
        box_bottom = HEIGHT - 110
        box = pygame.Rect(120, box_y, WIDTH - 240, box_bottom - box_y)
        pygame.draw.rect(self.screen, (*C_PANEL, 235), box, border_radius=16)
        pygame.draw.rect(self.screen, (*C_WALL_EDGE, 220), box, 2, border_radius=16)

        list_rect = pygame.Rect(box.x + 16, box.y + 32, box.w - 32, box.h - 48)
        reset_label = f"Resets in {self.time_until_reset(self.challenges_view)}"
        header = "DAILY" if self.challenges_view == "daily" else "WEEKLY"
        draw_text(self.screen, self.font_shop_item, f"{header}  •  {reset_label}", (list_rect.x, box.y + 10), C_TEXT, shadow=False)

        def draw_list(items, rect):
            if not items:
                draw_text(self.screen, self.font_small, "No challenges available.", (rect.centerx, rect.centery), C_TEXT_DIM, center=True, shadow=False)
                return
            row_h = 64
            gap = 10
            y = rect.y + 8
            for item in items:
                row = pygame.Rect(rect.x, y, rect.w, row_h)
                y += row_h + gap
                pygame.draw.rect(self.screen, (*C_PANEL_2, 245), row, border_radius=12)
                pygame.draw.rect(self.screen, (*C_WALL_EDGE, 200), row, 2, border_radius=12)

                progress = int(item.get("progress", 0))
                target = int(item.get("target", 1))
                claimed = bool(item.get("claimed", False))

                draw_text(self.screen, self.font_shop_item, item.get("name", "Challenge"), (row.x + 12, row.y + 8), C_TEXT, shadow=False)
                draw_text(self.screen, self.font_shop_desc, item.get("desc", ""), (row.x + 12, row.y + 34), C_TEXT_DIM, shadow=False)

                progress_txt = f"{min(progress, target)}/{target}"
                reward_txt = f"{int(item.get('reward', 0))} coins"
                progress_w = self.font_shop_small.size(progress_txt)[0]
                reward_w = self.font_shop_small.size(reward_txt)[0]
                info_gap = 10
                status_x = row.right - 120
                group_w = progress_w + info_gap + reward_w
                group_x = max(row.x + row.w * 0.5, status_x - 16 - group_w)
                info_y = row.y + 18
                draw_text(self.screen, self.font_shop_small, progress_txt, (group_x, info_y), C_TEXT_DIM, shadow=False)
                draw_text(self.screen, self.font_shop_small, reward_txt, (group_x + progress_w + info_gap, info_y), C_COIN, shadow=False)

                status = "CLAIMED" if claimed else ("COMPLETE" if progress >= target else "IN PROGRESS")
                status_col = C_OK if claimed else (C_ACCENT if progress >= target else C_TEXT_DIM)
                draw_text(self.screen, self.font_shop_small, status, (status_x, row.y + 24), status_col, shadow=False)

                bar_w = 220
                bar_h = 8
                bar_x = row.right - bar_w - 18
                bar_y = row.y + row.h - 16
                pygame.draw.rect(self.screen, (10, 10, 12), pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=6)
                fill_w = int(bar_w * clamp(progress / max(1, target), 0, 1))
                pygame.draw.rect(self.screen, C_ACCENT, pygame.Rect(bar_x, bar_y, fill_w, bar_h), border_radius=6)

        items = list(self.save.daily_challenges.get("items", [])) if self.challenges_view == "daily" else list(self.save.weekly_challenges.get("items", []))
        draw_list(items, list_rect)

        if self.challenges_back_btn:
            self.challenges_back_btn.update(1 / 60, mouse_pos, mouse_down, events)
            self.challenges_back_btn.draw(self.screen, self.font_med)

    def draw_weapon_mastery(self, box: pygame.Rect, mouse_pos, mouse_down, events) -> int:
        cols = 2
        rows = 3
        gap_x = 12
        gap_y = 14
        pad = 16

        usable_w = box.w - pad * 2
        usable_h = box.h - pad * 2
        card_w = (usable_w - gap_x * (cols - 1)) // cols
        card_h = (usable_h - gap_y * (rows - 1)) // rows

        cards_per_page = cols * rows
        weapon_ids = list(WEAPONS.keys())
        total_pages = max(1, math.ceil(len(weapon_ids) / cards_per_page))
        self.weapon_page = int(clamp(self.weapon_page, 0, total_pages - 1))

        start = self.weapon_page * cards_per_page
        end = start + cards_per_page
        page_ids = weapon_ids[start:end]

        self.weapon_prev_btn.enabled = self.weapon_page > 0
        self.weapon_next_btn.enabled = (self.weapon_page + 1) < total_pages

        start_x = box.x + pad
        start_y = box.y + pad

        for i, wid in enumerate(page_ids):
            c = i % cols
            r = i // cols
            rect = pygame.Rect(
                start_x + c * (card_w + gap_x),
                start_y + r * (card_h + gap_y),
                card_w,
                card_h
            )

            stats, changed = self.save.ensure_mastery_entry(wid)
            if changed:
                self.save.save()
            level = int(stats.get("level", 0))
            level_kills = int(stats.get("level_kills", 0))
            level_wins = int(stats.get("level_wins", 0))
            total_kills = int(stats.get("total_kills", stats.get("kills", 0)))
            total_wins = int(stats.get("total_wins", stats.get("games", 0)))
            req_level = min(level + 1, MAX_MASTERY_LEVEL)
            req_kills = int(stats.get("req_kills", mastery_requirements(req_level)[0]))
            req_wins = int(stats.get("req_wins", mastery_requirements(req_level)[1]))

            pygame.draw.rect(self.screen, (*C_PANEL_2, 245), rect, border_radius=14)
            pygame.draw.rect(self.screen, C_WALL_EDGE, rect, 2, border_radius=14)

            wdef = WEAPONS[wid]
            max_text_w = rect.w - 28
            mastery_label = clamp_text(self.font_shop_small, f"Mastery Lv. {level}", max_text_w)
            mastery_w = self.font_shop_small.size(mastery_label)[0]
            header_gap = 12
            header_y = rect.y + 12
            mastery_x = rect.right - 14 - mastery_w
            weapon_max_w = max_text_w - mastery_w - header_gap
            weapon_name = clamp_text(self.font_shop_item, wdef.name, max(60, weapon_max_w))
            mastery_y = header_y + (self.font_shop_item.get_height() - self.font_shop_small.get_height()) // 2
            draw_text(self.screen, self.font_shop_item, weapon_name, (rect.x + 14, header_y), C_TEXT, shadow=False)
            draw_text(self.screen, self.font_shop_small, mastery_label, (mastery_x, mastery_y), C_ACCENT, shadow=False)

            stats_lines = [
                f"Kills: {min(level_kills, req_kills)} / {req_kills}",
                f"Wins: {min(level_wins, req_wins)} / {req_wins}",
            ]
            stats_y = rect.y + 44
            stats_gap = self.font_tiny.get_height() + 14
            for line in stats_lines:
                clamped_line = clamp_text(self.font_tiny, line, max_text_w)
                draw_text(self.screen, self.font_tiny, clamped_line, (rect.x + 14, stats_y), C_TEXT_DIM, shadow=False)
                stats_y += stats_gap

            bar_w = rect.w - 28
            bar_h = 10
            bar_x = rect.x + 14
            bar_y = rect.y + rect.h - 54

            if level >= MAX_MASTERY_LEVEL:
                pygame.draw.rect(self.screen, (10, 10, 12), pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=6)
                pygame.draw.rect(self.screen, C_OK, pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=6)
            else:
                kill_frac = clamp(level_kills / max(1, req_kills), 0, 1)
                game_frac = clamp(level_wins / max(1, req_wins), 0, 1)

                pygame.draw.rect(self.screen, (10, 10, 12), pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=6)
                pygame.draw.rect(self.screen, C_ACCENT, pygame.Rect(bar_x, bar_y, int(bar_w * kill_frac), bar_h), border_radius=6)

                bar_y2 = bar_y + 31
                pygame.draw.rect(self.screen, (10, 10, 12), pygame.Rect(bar_x, bar_y2, bar_w, bar_h), border_radius=6)
                pygame.draw.rect(self.screen, C_ACCENT_2, pygame.Rect(bar_x, bar_y2, int(bar_w * game_frac), bar_h), border_radius=6)

        return total_pages
    def draw_weapons(self, events):
        self.screen.fill(C_BG)
        cx = WIDTH // 2

        # countdown any hint toast
        self.weapon_notice_timer = max(0.0, self.weapon_notice_timer - (1 / 60))

        draw_text(self.screen, self.font_shop_title, "WEAPONS", (cx, 62), C_TEXT, center=True)
        subtitle = "Pick an unlocked troop (buy more in Shop → WEAPONS)." if self.weapons_view == "weapons" else "Mastery tracks each weapon's usage and progression over time."
        draw_text(self.screen, self.font_ui, subtitle,
                  (cx, 94), C_TEXT_DIM, center=True, shadow=False)

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)

        for tab in self.weapon_tabs:
            tab.update(mouse_pos, mouse_down)
            tab.draw(self.screen, self.font_shop_item, active=(tab.tab_id == self.weapons_view))

        box = pygame.Rect(70, 160, WIDTH - 140, HEIGHT - 255)
        pygame.draw.rect(self.screen, (*C_PANEL, 235), box, border_radius=16)
        pygame.draw.rect(self.screen, (*C_WALL_EDGE, 220), box, 2, border_radius=16)

        if self.weapons_view == "mastery":
            try:
                total_pages = self.draw_weapon_mastery(box, mouse_pos, mouse_down, events)
            except Exception:
                if not self.mastery_error_logged:
                    print("Mastery tab error:")
                    traceback.print_exc()
                    self.mastery_error_logged = True
                total_pages = 1
                draw_text(self.screen, self.font_med, "Mastery data unavailable.", (cx, box.centery), C_TEXT_DIM, center=True, shadow=False)
        else:
            cols = 3
            rows = 3  # ✅ force 3 rows => 9 cards per page

            gap_x = 10
            gap_y = 12
            pad = 14

            # Compute card sizes so 3x3 fits perfectly in the box
            usable_w = box.w - pad * 2
            usable_h = box.h - pad * 2

            card_w = (usable_w - gap_x * (cols - 1)) // cols
            card_h = (usable_h - gap_y * (rows - 1)) // rows

            cards_per_page = cols * rows

            weapon_ids = list(WEAPONS.keys())  # insertion order; new weapons auto included
            total_pages = max(1, math.ceil(len(weapon_ids) / cards_per_page))
            self.weapon_page = int(clamp(self.weapon_page, 0, total_pages - 1))

            start = self.weapon_page * cards_per_page
            end = start + cards_per_page
            page_ids = weapon_ids[start:end]

            # enable/disable buttons
            self.weapon_prev_btn.enabled = self.weapon_page > 0
            self.weapon_next_btn.enabled = (self.weapon_page + 1) < total_pages

            start_x = box.x + pad
            start_y = box.y + pad

            for i, wid in enumerate(page_ids):
                c = i % cols
                r = i // cols
                rect = pygame.Rect(
                    start_x + c * (card_w + gap_x),
                    start_y + r * (card_h + gap_y),
                    card_w,
                    card_h
                )

                wdef = WEAPONS[wid]
                unlocked = bool(self.save.weapon_unlocks.get(wid, False))
                equipped = (self.save.selected_weapon == wid) and unlocked

                hover = rect.collidepoint(mouse_pos)
                if hover and mouse_down:
                    if unlocked:
                        self.save.selected_weapon = wid
                        self.save.save()
                        self.audio_play("buy")
                    else:
                        self.weapon_notice_text = "LOCKED — buy it in SHOP → WEAPONS"
                        self.weapon_notice_timer = 1.2
                        self.audio_play("hit")

                bg = (*C_PANEL_2, 245) if unlocked else (*C_PANEL_2, 190)
                edge = C_ACCENT if hover else C_WALL_EDGE
                pygame.draw.rect(self.screen, bg, rect, border_radius=14)
                pygame.draw.rect(self.screen, edge, rect, 2, border_radius=14)

                title_col = C_TEXT if unlocked else C_TEXT_DIM
                draw_text(self.screen, self.font_shop_item, wdef.name, (rect.x + 14, rect.y + 12), title_col, shadow=False)
                draw_text(self.screen, self.font_shop_desc, wdef.desc, (rect.x + 14, rect.y + 40), C_TEXT_DIM, shadow=False)

                extra = ""
                if wdef.splash_radius > 0:
                    extra += " SPLASH"
                if wdef.chain > 0:
                    extra += " CHAIN"
                if getattr(wdef, "base_pierce", 0) > 0:
                    extra += f" PIERCE+{wdef.base_pierce}"

                stats = f"DMG {wdef.base_damage}  CD {wdef.fire_cd:.2f}s{extra}"
                draw_text(self.screen, self.font_shop_small, stats, (rect.x + 14, rect.y + 74), C_ACCENT if unlocked else C_TEXT_DIM, shadow=False)

                badge = pygame.Rect(rect.right - 110, rect.y + 10, 96, 28)
                if equipped:
                    pygame.draw.rect(self.screen, (*C_OK, 230), badge, border_radius=10)
                    pygame.draw.rect(self.screen, C_WALL_EDGE, badge, 2, border_radius=10)
                    rect_centered_text(self.screen, self.font_shop_small, "EQUIPPED", badge, (10, 20, 20), shadow=False)
                elif not unlocked:
                    pygame.draw.rect(self.screen, (*C_TEXT_DIM, 180), badge, border_radius=10)
                    pygame.draw.rect(self.screen, C_WALL_EDGE, badge, 2, border_radius=10)
                    rect_centered_text(self.screen, self.font_shop_small, "LOCKED", badge, (25, 25, 32), shadow=False)

        # Back + pagination buttons
        self.weapon_back_btn.update(1 / 60, mouse_pos, mouse_down, events)
        self.weapon_back_btn.draw(self.screen, self.font_med)

        self.weapon_prev_btn.update(1 / 60, mouse_pos, mouse_down, events)
        self.weapon_next_btn.update(1 / 60, mouse_pos, mouse_down, events)
        self.weapon_prev_btn.draw(self.screen, self.font_med)
        self.weapon_next_btn.draw(self.screen, self.font_med)

        page_txt = f"Page {self.weapon_page + 1}/{total_pages}"
        mid_x = (self.weapon_prev_btn.rect.centerx + self.weapon_next_btn.rect.centerx) // 2
        below_y = self.weapon_prev_btn.rect.bottom + 10
        draw_text(self.screen, self.font_tiny, page_txt, (mid_x, below_y), C_TEXT_DIM, center=True, shadow=False)

        if self.weapon_notice_timer > 0 and self.weapon_notice_text:
            draw_text(self.screen, self.font_small, self.weapon_notice_text, (cx, HEIGHT - 118), C_WARN, center=True, shadow=True)

    def draw_shop(self, events):
        self.screen.fill(C_BG)
        cx = WIDTH // 2
        draw_text(self.screen, self.font_shop_title, "SHOP", (cx, 62), C_TEXT, center=True)
        draw_text(self.screen, self.font_ui, f"Coins: {self.save.coins}", (cx, 92), C_COIN, center=True)

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)

        for tab in self.shop_tabs:
            tab.update(mouse_pos, mouse_down)
            tab.draw(self.screen, self.font_shop_item, active=(tab.tab_id == self.shop_tab))

        box = pygame.Rect(70, 175, WIDTH - 140, HEIGHT - 270)
        if self.shop_tab != "cosmetics":
            pygame.draw.rect(self.screen, (*C_PANEL, 235), box, border_radius=16)
            pygame.draw.rect(self.screen, (*C_WALL_EDGE, 220), box, 2, border_radius=16)

        if self.shop_tab == "cosmetics":
            for tab in self.cosmetic_tabs:
                tab.update(mouse_pos, mouse_down)
                tab.draw(self.screen, self.font_shop_desc, active=(tab.tab_id == self.cosmetics_category))

            controls_top = min(self.shop_prev_btn.rect.top, self.shop_back_btn.rect.top)
            list_top = 220
            list_bottom = controls_top - 12
            cosmetic_box = pygame.Rect(70, list_top, WIDTH - 140, list_bottom - list_top)
            pygame.draw.rect(self.screen, (*C_PANEL, 235), cosmetic_box, border_radius=16)
            pygame.draw.rect(self.screen, (*C_WALL_EDGE, 220), cosmetic_box, 2, border_radius=16)

            cosmetics = [c for c in COSMETICS if c.category == self.cosmetics_category]
            rows_per_page = 4
            total_pages = max(1, math.ceil(len(cosmetics) / rows_per_page))
            self.shop_page = clamp(self.shop_page, 0, total_pages - 1)

            start = self.shop_page * rows_per_page
            end = start + rows_per_page
            page_items = cosmetics[start:end]

            has_prev = self.shop_page > 0
            has_next = (self.shop_page + 1) < total_pages
            self.shop_prev_btn.enabled = has_prev
            self.shop_next_btn.enabled = has_next

            x0 = cosmetic_box.x + 18
            y = cosmetic_box.y + 14

            row_h = 70
            gap = 12
            row_w = cosmetic_box.w - 36

            for cosmetic in page_items:
                row = pygame.Rect(x0, y, row_w, row_h)
                y += (row_h + gap)

                pygame.draw.rect(self.screen, (*C_PANEL_2, 245), row, border_radius=12)
                pygame.draw.rect(self.screen, (*C_WALL_EDGE, 200), row, 2, border_radius=12)

                unlocked = bool(self.save.cosmetics_unlocked.get(cosmetic.id, False))
                equipped = self.save.cosmetics_equipped.get(cosmetic.category) == cosmetic.id
                status = "Owned" if unlocked else ("Bundle Exclusive" if cosmetic.bundle_only else "Locked")
                cost_txt = "--" if unlocked or cosmetic.bundle_only else f"{cosmetic.cost} coins"
                cat_txt = cosmetic.category.upper()

                draw_text(self.screen, self.font_shop_item, f"{cosmetic.name}  •  {cat_txt}", (row.x + 14, row.y + 10), C_TEXT, shadow=False)
                draw_text(self.screen, self.font_shop_desc, cosmetic.desc, (row.x + 14, row.y + 38), C_TEXT_DIM, shadow=False)
                draw_text(self.screen, self.font_shop_small, status, (row.right - 310, row.y + 14),
                          C_OK if unlocked else C_TEXT_DIM, shadow=False)
                draw_text(self.screen, self.font_shop_small, cost_txt, (row.right - 310, row.y + 38), C_COIN, shadow=False)

                action_rect = pygame.Rect(row.right - 120, row.y + 16, 100, 38)
                if equipped:
                    pygame.draw.rect(self.screen, (*C_OK, 220), action_rect, border_radius=10)
                    pygame.draw.rect(self.screen, C_WALL_EDGE, action_rect, 2, border_radius=10)
                    rect_centered_text(self.screen, self.font_shop_small, "EQUIPPED", action_rect, (10, 20, 20), shadow=False)
                else:
                    label = "Equip" if unlocked else ("Bundle" if cosmetic.bundle_only else "Buy")
                    btn = Button(action_rect, label, callback=lambda c=cosmetic: self.equip_cosmetic(c) if self.save.cosmetics_unlocked.get(c.id, False) else self.buy_cosmetic(c))
                    btn.enabled = unlocked or (not cosmetic.bundle_only and self.save.coins >= cosmetic.cost)
                    btn.update(1 / 60, mouse_pos, mouse_down, events)
                    btn.draw(self.screen, self.font_shop_small)

            self.shop_back_btn.update(1 / 60, mouse_pos, mouse_down, events)
            self.shop_back_btn.draw(self.screen, self.font_med)

            self.shop_prev_btn.update(1 / 60, mouse_pos, mouse_down, events)
            self.shop_next_btn.update(1 / 60, mouse_pos, mouse_down, events)
            self.shop_prev_btn.draw(self.screen, self.font_med)
            self.shop_next_btn.draw(self.screen, self.font_med)

            page_txt = f"Page {self.shop_page + 1}/{total_pages}"
            mid_x = (self.shop_prev_btn.rect.centerx + self.shop_next_btn.rect.centerx) // 2
            below_y = self.shop_prev_btn.rect.bottom + 10
            draw_text(self.screen, self.font_tiny, page_txt, (mid_x, below_y), C_TEXT_DIM, center=True, shadow=False)
            return

        if self.shop_tab == "bundles":
            items = BUNDLES
            rows_per_page = self._shop_rows_per_page(box)
            total_pages = max(1, math.ceil(len(items) / max(1, rows_per_page)))
            self.shop_page = clamp(self.shop_page, 0, total_pages - 1)

            start = self.shop_page * rows_per_page
            end = start + rows_per_page
            page_items = items[start:end]

            has_prev = self.shop_page > 0
            has_next = (self.shop_page + 1) < total_pages
            self.shop_prev_btn.enabled = has_prev
            self.shop_next_btn.enabled = has_next

            x0 = box.x + 18
            y = box.y + 14

            row_h = 80
            gap = 8
            row_w = box.w - 36

            for bundle in page_items:
                row = pygame.Rect(x0, y, row_w, row_h)
                y += (row_h + gap)

                pygame.draw.rect(self.screen, (*C_PANEL_2, 245), row, border_radius=12)
                pygame.draw.rect(self.screen, (*C_WALL_EDGE, 200), row, 2, border_radius=12)

                weapons, meta, cosmetics = self.resolve_bundle_items(bundle)
                owned = self.bundle_is_owned(bundle)
                cost = self.bundle_price(bundle)
                includes = []
                includes += [WEAPONS[w].name for w in weapons if w in WEAPONS]
                includes += [SHOP_ITEMS_BY_ID[m].name for m in meta if m in SHOP_ITEMS_BY_ID]
                includes += [COSMETICS_BY_ID[c].name for c in cosmetics if c in COSMETICS_BY_ID]
                includes_txt = ", ".join(includes) if includes else "No bundle items available"

                draw_text(self.screen, self.font_shop_item, bundle.name, (row.x + 14, row.y + 10), C_TEXT, shadow=False)
                draw_text(self.screen, self.font_shop_desc, bundle.desc, (row.x + 14, row.y + 38), C_TEXT_DIM, shadow=False)
                draw_text(self.screen, self.font_shop_small, includes_txt, (row.x + 14, row.y + 62), C_TEXT_DIM, shadow=False)

                status_txt = "OWNED" if owned else f"{int(bundle.discount * 100)}% off"
                draw_text(self.screen, self.font_shop_small, status_txt, (row.right - 310, row.y + 16),
                          C_OK if owned else C_TEXT_DIM, shadow=False)
                cost_txt = "OWNED" if owned else f"{cost} coins"
                draw_text(self.screen, self.font_shop_small, cost_txt, (row.right - 310, row.y + 44), C_COIN, shadow=False)

                buy_rect = pygame.Rect(row.right - 110, row.y + 22, 92, 40)
                btn = Button(buy_rect, "Buy", callback=lambda b=bundle: self.buy_bundle(b))
                btn.enabled = (not owned) and (self.save.coins >= cost) and cost > 0
                btn.update(1 / 60, mouse_pos, mouse_down, events)
                btn.draw(self.screen, self.font_shop_small)

            self.shop_back_btn.update(1 / 60, mouse_pos, mouse_down, events)
            self.shop_back_btn.draw(self.screen, self.font_med)

            self.shop_prev_btn.update(1 / 60, mouse_pos, mouse_down, events)
            self.shop_next_btn.update(1 / 60, mouse_pos, mouse_down, events)
            self.shop_prev_btn.draw(self.screen, self.font_med)
            self.shop_next_btn.draw(self.screen, self.font_med)

            page_txt = f"Page {self.shop_page + 1}/{total_pages}"
            mid_x = (self.shop_prev_btn.rect.centerx + self.shop_next_btn.rect.centerx) // 2
            below_y = self.shop_prev_btn.rect.bottom + 10
            draw_text(self.screen, self.font_tiny, page_txt, (mid_x, below_y), C_TEXT_DIM, center=True, shadow=False)
            return

        items = self._shop_items_for_tab()

        rows_per_page = self._shop_rows_per_page(box)
        total_pages = max(1, math.ceil(len(items) / max(1, rows_per_page)))
        self.shop_page = clamp(self.shop_page, 0, total_pages - 1)

        start = self.shop_page * rows_per_page
        end = start + rows_per_page
        page_items = items[start:end]

        has_prev = self.shop_page > 0
        has_next = (self.shop_page + 1) < total_pages
        self.shop_prev_btn.enabled = has_prev
        self.shop_next_btn.enabled = has_next

        x0 = box.x + 18
        y = box.y + 14

        row_h = 72
        gap = 12
        row_w = box.w - 36

        for item in page_items:
            row = pygame.Rect(x0, y, row_w, row_h)
            y += (row_h + gap)

            pygame.draw.rect(self.screen, (*C_PANEL_2, 245), row, border_radius=12)
            pygame.draw.rect(self.screen, (*C_WALL_EDGE, 200), row, 2, border_radius=12)

            maxed = self.is_maxed(item)
            cost = self.shop_cost(item)

            if item.kind == "weapon":
                unlocked = bool(self.save.weapon_unlocks.get(item.weapon_id, False))
                lvl_txt = "Unlocked" if unlocked else "Locked"
                lvl_col = C_OK if unlocked else C_TEXT_DIM
                cost_txt = "MAX" if maxed else f"{cost} coins"
            else:
                lvl = int(self.save.shop_levels.get(item.id, 0))
                lvl_txt = f"Level {lvl}/{item.max_level}"
                lvl_col = C_TEXT_DIM
                cost_txt = "MAX" if maxed else f"{cost} coins"

            draw_text(self.screen, self.font_shop_item, item.name, (row.x + 14, row.y + 10), C_TEXT, shadow=False)
            draw_text(self.screen, self.font_shop_desc, item.desc, (row.x + 14, row.y + 38), C_TEXT_DIM, shadow=False)
            draw_text(self.screen, self.font_shop_small, lvl_txt, (row.right - 310, row.y + 14), lvl_col, shadow=False)
            draw_text(self.screen, self.font_shop_small, cost_txt, (row.right - 310, row.y + 38), C_COIN, shadow=False)

            buy_rect = pygame.Rect(row.right - 110, row.y + 16, 92, 40)
            btn = Button(buy_rect, "Buy", callback=lambda it=item: self.buy_item(it))
            btn.enabled = self.can_buy(item)
            btn.update(1 / 60, mouse_pos, mouse_down, events)
            btn.draw(self.screen, self.font_shop_small)

        self.shop_back_btn.update(1 / 60, mouse_pos, mouse_down, events)
        self.shop_back_btn.draw(self.screen, self.font_med)

        self.shop_prev_btn.update(1 / 60, mouse_pos, mouse_down, events)
        self.shop_next_btn.update(1 / 60, mouse_pos, mouse_down, events)
        self.shop_prev_btn.draw(self.screen, self.font_med)
        self.shop_next_btn.draw(self.screen, self.font_med)

        page_txt = f"Page {self.shop_page + 1}/{total_pages}"
        mid_x = (self.shop_prev_btn.rect.centerx + self.shop_next_btn.rect.centerx) // 2
        below_y = self.shop_prev_btn.rect.bottom + 10
        draw_text(self.screen, self.font_tiny, page_txt, (mid_x, below_y), C_TEXT_DIM, center=True, shadow=False)

    def draw_paused(self, events):
        self.draw_background()
        self.draw_obstacles()
        self.draw_story_objects()
        self.draw_entities()
        self.draw_story_visibility()
        self.draw_hud()
        self.draw_overlay_dim(175)
        draw_text(self.screen, self.font_big, "PAUSED", (WIDTH // 2, 170), C_TEXT, center=True)

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)
        for b in self.pause_buttons:
            b.update(1 / 60, mouse_pos, mouse_down, events)
            b.draw(self.screen, self.font_med)

    def draw_levelup(self, events):
        self.draw_background()
        self.draw_obstacles()
        self.draw_story_objects()
        self.draw_entities()
        self.draw_story_visibility()
        self.draw_hud()

        self.draw_overlay_dim(190)
        draw_text(self.screen, self.font_big, "LEVEL UP!", (WIDTH // 2, 105), C_ACCENT, center=True)
        draw_text(self.screen, self.font_ui, "Pick an upgrade", (WIDTH // 2, 150), C_TEXT_DIM, center=True, shadow=False)

        box = pygame.Rect(WIDTH // 2 - 380, HEIGHT // 2 - 190, 760, 410)
        pygame.draw.rect(self.screen, (*C_PANEL, 235), box, border_radius=16)
        pygame.draw.rect(self.screen, (*C_WALL_EDGE, 220), box, 2, border_radius=16)

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)

        for rect, up in self.level_cards:
            hover = rect.collidepoint(mouse_pos)
            bg = (*C_PANEL_2, 245)
            edge = C_ACCENT if hover else C_WALL_EDGE
            pygame.draw.rect(self.screen, bg, rect, border_radius=14)
            pygame.draw.rect(self.screen, edge, rect, 2, border_radius=14)

            tag_area = pygame.Rect(rect.right - 170, rect.y + 16, 140, rect.h - 32)
            pygame.draw.rect(self.screen, (*C_PANEL, 230), tag_area, border_radius=12)
            pygame.draw.rect(self.screen, (*C_WALL_EDGE, 210), tag_area, 2, border_radius=12)
            rect_centered_text(self.screen, self.font_shop_small, up.tag, tag_area, C_ACCENT, shadow=False)

            draw_text(self.screen, self.font_shop_item, up.name, (rect.x + 18, rect.y + 16), C_TEXT, shadow=False)
            draw_text(self.screen, self.font_shop_desc, up.desc, (rect.x + 18, rect.y + 46), C_TEXT_DIM, shadow=False)

            if hover and mouse_down:
                self.player.apply_upgrade(up.id)
                self.audio_play("levelup")
                self.set_state("playing")

    def draw_gameover(self, events):
        self.draw_background()
        self.draw_obstacles()
        self.draw_story_objects()
        self.draw_entities()
        self.draw_story_visibility()
        self.draw_hud()

        self.draw_overlay_dim(205)
        title = "LEVEL FAILED" if self.mode == "story" else "GAME OVER"
        title_color = C_WARN if self.mode == "story" else C_ACCENT_2
        draw_text(self.screen, self.font_big, title, (WIDTH // 2, 145), title_color, center=True)

        if self.mode == "story":
            stats = [
                f"Level: {self.story_level_index}",
                f"Score: {self.player.score}",
                f"Kills: {self.story_kills}",
                f"Time: {int(self.story_elapsed)}s",
            ]
        else:
            self.award_coins_if_needed()
            self.record_leaderboard_if_needed()
            stats = [
                f"Score: {self.player.score}",
                f"Time: {int(self.survival_time)}s",
                f"Wave: {self.wave}",
                f"Level: {self.player.level}",
                f"Boss Coins Banked: +{self.run_bonus_coins}",
                f"Coins Earned: +{self.last_run_coins_earned}",
            ]
        y = 205
        for s in stats:
            draw_text(self.screen, self.font_med, s, (WIDTH // 2, y), C_TEXT, center=True)
            y += 34

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)
        buttons = self.story_fail_buttons if self.mode == "story" else self.gameover_buttons
        for b in buttons:
            b.update(1 / 60, mouse_pos, mouse_down, events)
            b.draw(self.screen, self.font_med)

        helper_text = "Press R to retry" if self.mode == "story" else "Press R to restart"
        draw_text(self.screen, self.font_small, helper_text, (WIDTH // 2, HEIGHT - 26), C_TEXT_DIM, center=True, shadow=False)
        

    # =========================================================
    # MAIN LOOP
    # =========================================================
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS_CAP) / 1000.0
            dt = clamp(dt, 0.0, 1 / 30)

            events = self.handle_events()

            if self.state == "playing":
                self.update_playing(dt, events)
                self.update_camera(dt)
                self.draw_background()
                self.draw_obstacles()
                self.draw_story_objects()
                self.draw_entities()
                self.draw_story_visibility()
                self.draw_hud()
                
                self.draw_boss_tracker()


                # --- Auto-fire indicator (in-game) ---
                if getattr(self.player, "auto_fire", False):
                    badge_w, badge_h = 130, 28
                    bx = WIDTH - badge_w - 16
                    by = HEIGHT - badge_h - 16  # bottom-right

                    badge = pygame.Rect(bx, by, badge_w, badge_h)

                    pygame.draw.rect(self.screen, (*C_OK, 230), badge, border_radius=12)
                    pygame.draw.rect(self.screen, (*C_WALL_EDGE, 220), badge, 2, border_radius=12)
                    draw_text(self.screen, self.font_small, "AUTO FIRE", badge.center,
                              (20, 30, 20), center=True, shadow=False)

            elif self.state == "menu":
                self.draw_menu(events)

            elif self.state == "daily_wheel":
                self.update_daily_wheel(dt)
                self.draw_daily_wheel(events, dt)

            elif self.state == "story_menu":
                self.draw_story_menu(events)

            elif self.state == "weapons":
                self.draw_weapons(events)

            elif self.state == "shop":
                self.draw_shop(events)

            elif self.state == "settings":
                self.draw_settings(events)

            elif self.state == "controls":
                self.draw_controls()

            elif self.state == "leaderboard":
                self.draw_leaderboard(events)

            elif self.state == "challenges":
                self.draw_challenges(events)

            elif self.state == "paused":
                self.update_camera(dt)
                self.draw_paused(events)

            elif self.state == "levelup":
                self.update_camera(dt)
                self.draw_levelup(events)

            elif self.state == "story_complete":
                self.update_camera(dt)
                self.draw_story_complete(events)

            elif self.state == "gameover":
                self.update_camera(dt)
                self.draw_gameover(events)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":
    Game().run()

