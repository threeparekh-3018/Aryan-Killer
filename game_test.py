# codex edit

import pygame
import random
import math
import json
import os

pygame.init()

WIDTH, HEIGHT = 1100, 760
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aryan Killer")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MINT = (191, 219, 255)
RED = (220, 50, 50)
GREEN = (50, 180, 90)
BLUE = (70, 120, 255)
GOLD = (240, 200, 60)
GRAY = (80, 80, 80)
DARK_BLUE = (20, 40, 120)
CYAN = (120, 255, 255)
PURPLE = (160, 70, 220)
ROYAL_BLUE = (65, 105, 225)
LIME_GREEN = (120, 255, 80)
CHARCOAL = (54, 69, 79)
CRIMSON = (220, 20, 60)
ORANGE = (255, 140, 0)
YELLOW = (240, 220, 60)
MAGENTA = (255, 70, 190)
DEEP_VIOLET = (110, 70, 200)
TEAL = (40, 180, 180)
SILVER = (190, 190, 210)

SAVE_FILE = "stats.json"
ASSET_PATH = r"C:\Harsh Parekh\New folder"
POWERUP_DURATION = 10000
POWERUP_SPAWN_DELAY = 12000
POWERUP_DECAY_TIME = 20000
COIN_SPAWN_DELAY = 10000
BOSS_MINION_DELAY = 2000
BOSS_WALL_DELAY = 6000
BOSS_CENTER_RADIUS = 240
BOSS_ORBIT_JITTER = 45
BOSS_ORBIT_CHANGE_DELAY = 1800
BARREL_SPAWN_DELAY = 15000
SHOCKWAVE_COOLDOWN = 8000
MINE_RADIUS = 85
MINE_DAMAGE = 4
BARREL_RADIUS = 140
FREEZE_DURATION = 2200
BARRIER_DURATION = 5000
BARRIER_COOLDOWN = 15000
BARRIER_RADIUS = 110
SAPPER_WALL_DELAY = 3500
MAGNET_RADIUS = 180
PROTECTOR_RADIUS = 170
MEDIC_HEAL_RADIUS = 160
MEDIC_HEAL_DELAY = 2000
SMASHER_TRIGGER_DISTANCE = 170
SMASHER_OVERLAY_DURATION = 3000
SMASHER_FIELD_DURATION = 3000
SMASHER_FIELD_RADIUS = 180
CHARGER_IDLE_DELAY = 1800
CHARGER_SCREAM_DELAY = 900
INNER_ZONE_X_MIN = WIDTH * 0.1
INNER_ZONE_X_MAX = WIDTH * 0.9
INNER_ZONE_Y_MIN = HEIGHT * 0.1
INNER_ZONE_Y_MAX = HEIGHT * 0.9
MINIBOSS_SPAWN_CHANCE = 15
MINIBOSS_HEALTH = 10
MINIBOSS_TIMER_DELAY = 3000
PRISM_SHIELD_DELAY = 5000
PRISM_SHIELD_DURATION = 3000
PRISM_RADIUS = 170
SINGULARITY_DURATION = 5000
SINGULARITY_RADIUS = 170
STROBE_TELEPORT_DELAY = 3000
INVERTER_TRIGGER_LEVEL = 150
INVERTER_INVERT_DURATION = 10000


class PowerUp:
    COLORS = {
        "shield": BLUE,
        "double_damage": RED,
        "extra_life": GREEN
    }

    LABELS = {
        "shield": "Shield",
        "double_damage": "Double Damage",
        "extra_life": "Extra Life"
    }

    SHORT = {
        "shield": "S",
        "double_damage": "D",
        "extra_life": "L"
    }

    def __init__(self, powerup_type, pos):
        self.type = powerup_type
        self.pos = [int(pos[0]), int(pos[1])]
        self.size = 24
        self.spawn_time = pygame.time.get_ticks()

    def get_rect(self):
        return pygame.Rect(
            self.pos[0] - self.size // 2,
            self.pos[1] - self.size // 2,
            self.size,
            self.size
        )

    def draw(self, surface, font_obj):
        rect = self.get_rect()
        pygame.draw.rect(surface, self.COLORS[self.type], rect, border_radius=6)
        pygame.draw.rect(surface, BLACK, rect, 2, border_radius=6)
        letter = font_obj.render(self.SHORT[self.type], True, BLACK)
        surface.blit(letter, (rect.centerx - letter.get_width() // 2, rect.centery - letter.get_height() // 2))


class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(int(x), int(y), int(width), int(height))

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect, border_radius=4)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=4)


class Minion:
    def __init__(self, pos):
        self.pos = [int(pos[0]), int(pos[1])]
        self.type = "minion"
        self.hp = 2
        self.max_hp = 2
        self.speed = 2.6

    def to_enemy(self):
        return {
            "pos": self.pos[:],
            "type": self.type,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "speed": self.speed
        }


class Boss:
    def __init__(self, pos):
        self.pos = [float(pos[0]), float(pos[1])]
        self.type = "boss"
        self.hp = 15
        self.max_hp = 15
        self.speed = 0.4
        self.minion_timer = 0
        self.wall_timer = 0
        self.orbit_angle = random.uniform(0, math.tau)
        self.orbit_radius = BOSS_CENTER_RADIUS + random.randint(-BOSS_ORBIT_JITTER, BOSS_ORBIT_JITTER)
        self.orbit_timer = 0

    def to_enemy(self):
        return {
            "pos": [self.pos[0], self.pos[1]],
            "type": self.type,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "speed": self.speed,
            "boss_entity": self
        }

    def spawn_minion(self):
        angle = random.uniform(0, math.tau)
        radius = random.randint(80, 130)
        x = self.pos[0] + math.cos(angle) * radius
        y = self.pos[1] + math.sin(angle) * radius
        x = max(30, min(WIDTH - 30, int(x)))
        y = max(30, min(HEIGHT - 30, int(y)))
        return Minion([x, y]).to_enemy()

    def spawn_wall(self):
        center_x = WIDTH // 2
        center_y = HEIGHT // 2
        dx = self.pos[0] - center_x
        dy = self.pos[1] - center_y

        # Make the wall face the center: the wall's normal points inward.
        vertical = abs(dx) >= abs(dy)
        width = 24 if vertical else 90
        height = 90 if vertical else 24
        angle = random.uniform(0, math.tau)
        radius = random.randint(90, 150)
        x = self.pos[0] + math.cos(angle) * radius - width / 2
        y = self.pos[1] + math.sin(angle) * radius - height / 2
        x = max(10, min(WIDTH - width - 10, int(x)))
        y = max(10, min(HEIGHT - height - 10, int(y)))
        return Wall(x, y, width, height)


class Coin:
    def __init__(self, pos):
        self.pos = [int(pos[0]), int(pos[1])]
        self.size = 18
        self.spawn_time = pygame.time.get_ticks()

    def get_rect(self):
        return pygame.Rect(
            self.pos[0] - self.size // 2,
            self.pos[1] - self.size // 2,
            self.size,
            self.size
        )

    def draw(self, surface, font_obj):
        pygame.draw.circle(surface, GOLD, self.pos, self.size // 2)
        pygame.draw.circle(surface, BLACK, self.pos, self.size // 2, 2)
        letter = font_obj.render("C", True, BLACK)
        surface.blit(letter, (self.pos[0] - letter.get_width() // 2, self.pos[1] - letter.get_height() // 2))


class Mine:
    def __init__(self, pos):
        self.pos = [int(pos[0]), int(pos[1])]
        self.radius = MINE_RADIUS
        self.damage = MINE_DAMAGE

    def draw(self, surface):
        pygame.draw.circle(surface, RED, self.pos, 10)
        pygame.draw.circle(surface, BLACK, self.pos, 10, 2)
        pygame.draw.circle(surface, BLACK, self.pos, 3)


class Barrel:
    def __init__(self, pos):
        self.pos = [int(pos[0]), int(pos[1])]
        self.radius = BARREL_RADIUS
        self.rect = pygame.Rect(self.pos[0] - 18, self.pos[1] - 24, 36, 48)

    def draw(self, surface):
        pygame.draw.rect(surface, (170, 40, 30), self.rect, border_radius=6)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=6)
        pygame.draw.line(surface, BLACK, (self.rect.left, self.rect.top + 12), (self.rect.right, self.rect.top + 12), 2)
        pygame.draw.line(surface, BLACK, (self.rect.left, self.rect.bottom - 12), (self.rect.right, self.rect.bottom - 12), 2)


ENEMY_LEGEND = [
    ("Sapper", PURPLE),
    ("Magnet", ROYAL_BLUE),
    ("Protector", GOLD),
    ("Medic", LIME_GREEN),
    ("Smasher", CHARCOAL),
    ("Charger", CRIMSON),
    ("Splitter", ORANGE),
    ("Shielder", CYAN),
    ("Zig-Zagger", YELLOW),
    ("Multiplier", MAGENTA),
    ("Singularity", DARK_BLUE),
    ("Strobe", SILVER),
    ("Prism", TEAL),
    ("Inverter", RED),
]

MINIBOSS_TYPES = {"multiplier", "singularity", "strobe", "prism", "inverter"}

LABORATORY_MODE_ENABLED = True
LAB_PANEL_WIDTH = 250
LAB_SHOOTER_POS = [120, HEIGHT // 2]
LAB_GRID_COLOR = (210, 220, 230)
LAB_BUTTON_HEIGHT = 28


# ---------- SAVE ----------
def load_stats():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {"high_score": 0, "games_played": 0}


def save_stats(stats):
    with open(SAVE_FILE, "w") as f:
        json.dump(stats, f)


stats = load_stats()

# ---------- IMAGES ----------
face_img = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSET_PATH, "face.png")), (60, 60)
)

enemy_img = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSET_PATH, "face2.png")), (40, 40)
)

boss_img = pygame.transform.scale(enemy_img, (100, 100))

gun_img_original = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSET_PATH, "gun.png")), (60, 30)
)

life_img = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSET_PATH, "lives.png")), (30, 30)
)

avk_img_original = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSET_PATH, "avk.png")), (200, 200)
)

wts_img_original = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSET_PATH, "wts.png")), (200, 200)
)

# ---------- FONTS ----------
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 64)
small_font = pygame.font.SysFont(None, 24)

# ---------- QUESTIONS ----------
questions = [
    {"q": "lim x->0 (sinx/x)?", "a": "1"},
    {"q": "sin^2x + cos^2x?", "a": "1"},
    {"q": "tan45?", "a": "1"},
    {"q": "lim x->inf (1/x)?", "a": "0"},
]


# ---------- GAME ----------
def reset_game():
    return {
        "player_pos": [WIDTH // 2, HEIGHT // 2],
        "lives": 3,
        "player_lives": 3,
        "score": 0,
        "enemies": [],
        "bullets": [],
        "walls": [],
        "powerups": [],
        "coins": [],
        "mines": [],
        "barrels": [],
        "smasher_overlays": [],
        "smasher_fields": [],
        "black_holes": [],
        "spawn_timer": 0,
        "powerup_timer": 0,
        "coin_timer": 0,
        "barrel_timer": 0,
        "auto_mode": False,
        "auto_timer": 0,
        "fast_forward": False,
        "game_over": False,
        "boss_spawned": False,
        "boss_intro_done": False,
        "level100_done": False,
        "miniboss_level_checked": 0,
        "inverter_spawned": False,
        "mine_count": 3,
        "coin_count": 0,
        "shockwave_timer": 0,
        "shockwave_active": False,
        "shockwave_radius": 0,
        "shockwave_center": [WIDTH // 2, HEIGHT // 2],
        "game_speed_multiplier": 1.0,
        "barrier_active": False,
        "barrier_timer": 0,
        "barrier_cooldown": 0,
        "inverter_active": False,
        "inverter_timer": 0,
        "upgrades": {
            "multishot": 0,
            "piercing": 0,
            "freeze": 0
        },
        "active_powerups": {
            "shield": 0,
            "double_damage": 0
        }
    }


def spawn_enemy_far(player_pos):
    while True:
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        if math.hypot(x - player_pos[0], y - player_pos[1]) > 250:
            return [x, y]


def spawn_backline_pos(player_pos):
    while True:
        x = random.randint(20, WIDTH - 20)
        y = random.randint(20, HEIGHT - 20)
        in_outer_band = (
            x <= INNER_ZONE_X_MIN or x >= INNER_ZONE_X_MAX or
            y <= INNER_ZONE_Y_MIN or y >= INNER_ZONE_Y_MAX
        )
        if in_outer_band and math.hypot(x - player_pos[0], y - player_pos[1]) > 250:
            return [x, y]


def create_enemy_from_type(enemy_type, player_pos):
    pos = spawn_backline_pos(player_pos) if enemy_type in {"magnet", "protector", "medic"} else spawn_enemy_far(player_pos)

    enemy = {
        "pos": pos,
        "type": enemy_type,
        "shield_health": 0,
        "shield_source": False,
        "color_dot": WHITE
    }

    if enemy_type == "normal":
        enemy.update({"hp": 1, "max_hp": 1, "speed": 1.4})
    elif enemy_type == "fast":
        enemy.update({"hp": 1, "max_hp": 1, "speed": 2.45})
    elif enemy_type == "tank":
        enemy.update({"hp": 3, "max_hp": 3, "speed": 0.84})
    elif enemy_type == "splitter":
        enemy.update({"hp": 1, "max_hp": 1, "speed": 0.7, "color_dot": ORANGE})
    elif enemy_type == "shielder":
        enemy.update({"hp": 2, "max_hp": 2, "speed": 0.7, "shield_health": 2, "color_dot": CYAN})
    elif enemy_type == "zigzagger":
        enemy.update({
            "hp": 1,
            "max_hp": 1,
            "speed": 1.225,
            "baseline_y": pos[1],
            "zig_x": pos[0],
            "frequency": 0.03,
            "amplitude": 45,
            "color_dot": YELLOW
        })
    elif enemy_type == "sapper":
        enemy.update({
            "hp": 2,
            "max_hp": 2,
            "speed": 0.84,
            "orbit_center": pos[:],
            "orbit_a": random.randint(45, 90),
            "orbit_b": random.randint(25, 60),
            "orbit_speed": random.uniform(0.0015, 0.003),
            "wall_timer": 0,
            "color_dot": PURPLE
        })
    elif enemy_type == "magnet":
        enemy.update({"hp": 2, "max_hp": 2, "speed": 0.63, "color_dot": ROYAL_BLUE})
    elif enemy_type == "protector":
        enemy.update({"hp": 2, "max_hp": 2, "speed": 0.56, "protected_targets": [], "color_dot": GOLD})
    elif enemy_type == "medic":
        enemy.update({"hp": 2, "max_hp": 2, "speed": 0.56, "heal_timer": 0, "color_dot": LIME_GREEN})
    elif enemy_type == "smasher":
        enemy.update({"hp": 2, "max_hp": 2, "speed": 0.91, "overlay_timer": 0, "color_dot": CHARCOAL})
    elif enemy_type == "charger":
        enemy.update({
            "hp": 2,
            "max_hp": 2,
            "speed": 1.05,
            "charge_state": "idle",
            "charge_timer": 0,
            "charge_target": pos[:],
            "color_dot": CRIMSON
        })
    elif enemy_type == "mini":
        enemy.update({"hp": 1, "max_hp": 1, "speed": 1.12})
    elif enemy_type in MINIBOSS_TYPES:
        return create_miniboss(enemy_type, player_pos) if enemy_type != "inverter" else create_inverter(player_pos)

    return enemy


def create_enemy(player_pos):
    enemy_rolls = [
        ("normal", 0.22),
        ("fast", 0.12),
        ("tank", 0.08),
        ("splitter", 0.08),
        ("shielder", 0.08),
        ("zigzagger", 0.08),
        ("sapper", 0.08),
        ("magnet", 0.07),
        ("protector", 0.07),
        ("medic", 0.07),
        ("smasher", 0.07),
        ("charger", 0.06),
    ]
    types = [enemy_type for enemy_type, _ in enemy_rolls]
    weights = [weight for _, weight in enemy_rolls]
    return create_enemy_from_type(random.choices(types, weights=weights, k=1)[0], player_pos)


def create_boss(player_pos):
    pos = spawn_enemy_far(player_pos)
    return Boss(pos).to_enemy()


def create_miniboss(miniboss_type, player_pos):
    pos = spawn_enemy_far(player_pos)
    boss_entity = Boss(pos)
    enemy = boss_entity.to_enemy()
    enemy.update({
        "type": miniboss_type,
        "hp": MINIBOSS_HEALTH,
        "max_hp": MINIBOSS_HEALTH,
        "is_miniboss": True,
        "special_timer": 0,
        "shield_pulse_timer": 0,
        "reflect_shield_timer": 0,
        "reflect_shield": False
    })
    if miniboss_type == "multiplier":
        enemy["color_dot"] = MAGENTA
    elif miniboss_type == "singularity":
        enemy["color_dot"] = DARK_BLUE
    elif miniboss_type == "strobe":
        enemy["color_dot"] = SILVER
    elif miniboss_type == "prism":
        enemy["color_dot"] = TEAL
    return enemy


def create_inverter(player_pos):
    pos = spawn_enemy_far(player_pos)
    boss_entity = Boss(pos)
    enemy = boss_entity.to_enemy()
    boss_health = boss_entity.max_hp
    enemy.update({
        "type": "inverter",
        "hp": boss_health * 10,
        "max_hp": boss_health * 10,
        "is_miniboss": True,
        "special_timer": INVERTER_INVERT_DURATION,
        "color_dot": RED
    })
    return enemy


def create_random_powerup():
    powerup_type = random.choice(["shield", "double_damage", "extra_life"])
    x = random.randint(40, WIDTH - 40)
    y = random.randint(40, HEIGHT - 40)
    return PowerUp(powerup_type, [x, y])


def create_reward_powerup(pos):
    powerup_type = random.choice(["shield", "double_damage", "extra_life"])
    x = pos[0] + random.randint(-80, 80)
    y = pos[1] + random.randint(-80, 80)
    x = max(40, min(WIDTH - 40, int(x)))
    y = max(40, min(HEIGHT - 40, int(y)))
    return PowerUp(powerup_type, [x, y])


def create_coin():
    x = random.randint(40, WIDTH - 40)
    y = random.randint(40, HEIGHT - 40)
    return Coin([x, y])


def create_barrel():
    x = random.randint(70, WIDTH - 70)
    y = random.randint(70, HEIGHT - 70)
    return Barrel([x, y])


def get_difficulty(score):
    level = score // 15
    speed_scale = 1 + level * 0.1
    spawn_delay = max(400, int((1800 - level * 200) / 1.5))
    return speed_scale, spawn_delay


def activate_powerup(game, powerup_type):
    if powerup_type == "extra_life":
        game["player_lives"] += 1
        game["lives"] = game["player_lives"]
    else:
        game["active_powerups"][powerup_type] += POWERUP_DURATION


def take_player_hit(game):
    if game["active_powerups"]["shield"] > 0:
        return

    game["player_lives"] -= 1
    game["lives"] = game["player_lives"]


def update_powerup_timers(game, dt):
    for powerup_type in game["active_powerups"]:
        if game["active_powerups"][powerup_type] > 0:
            game["active_powerups"][powerup_type] = max(0, game["active_powerups"][powerup_type] - dt)


def update_game_timers(game, dt):
    update_powerup_timers(game, dt)

    if game["shockwave_timer"] > 0:
        game["shockwave_timer"] = max(0, game["shockwave_timer"] - dt)

    if game["barrier_cooldown"] > 0:
        game["barrier_cooldown"] = max(0, game["barrier_cooldown"] - dt)

    if game["barrier_active"]:
        game["barrier_timer"] = max(0, game["barrier_timer"] - dt)
        if game["barrier_timer"] == 0:
            game["barrier_active"] = False

    if game["inverter_active"]:
        game["inverter_timer"] = max(0, game["inverter_timer"] - dt)
        if game["inverter_timer"] == 0:
            game["inverter_active"] = False

    if game["shockwave_active"]:
        game["shockwave_radius"] += dt * 1.8
        center_x, center_y = game["shockwave_center"]
        max_radius = max(
            math.hypot(center_x, center_y),
            math.hypot(WIDTH - center_x, center_y),
            math.hypot(center_x, HEIGHT - center_y),
            math.hypot(WIDTH - center_x, HEIGHT - center_y)
        )
        if game["shockwave_radius"] >= max_radius:
            game["shockwave_active"] = False
            game["shockwave_radius"] = max_radius
            game["game_speed_multiplier"] = 1.0

    for smasher_field in game["smasher_fields"][:]:
        smasher_field["timer"] = max(0, smasher_field["timer"] - dt)
        if smasher_field["timer"] == 0:
            game["smasher_fields"].remove(smasher_field)


def spawn_powerup_if_needed(game, dt):
    game["powerup_timer"] += dt
    if game["powerup_timer"] > POWERUP_SPAWN_DELAY:
        if len(game["powerups"]) < 3:
            game["powerups"].append(create_random_powerup())
        game["powerup_timer"] = 0


def spawn_coin_if_needed(game, dt):
    game["coin_timer"] += dt
    if game["coin_timer"] > COIN_SPAWN_DELAY:
        if len(game["coins"]) < 4:
            game["coins"].append(create_coin())
        game["coin_timer"] = 0


def spawn_barrel_if_needed(game, dt):
    game["barrel_timer"] += dt
    if game["barrel_timer"] > BARREL_SPAWN_DELAY:
        if len(game["barrels"]) < 3:
            game["barrels"].append(create_barrel())
        game["barrel_timer"] = 0


def cleanup_expired_pickups(game):
    current_time = pygame.time.get_ticks()
    game["powerups"] = [powerup for powerup in game["powerups"] if current_time - powerup.spawn_time <= POWERUP_DECAY_TIME]
    game["coins"] = [coin for coin in game["coins"] if current_time - coin.spawn_time <= POWERUP_DECAY_TIME]
    game["black_holes"] = [black_hole for black_hole in game["black_holes"] if current_time - black_hole["spawn_time"] <= SINGULARITY_DURATION]


def on_boss_death(game, boss_pos):
    game["walls"].clear()
    for _ in range(3):
        game["powerups"].append(create_reward_powerup(boss_pos))
    for _ in range(random.randint(5, 10)):
        game["coins"].append(create_coin())


def spawn_splitter_children(game, enemy):
    for _ in range(2):
        child = create_enemy_from_type("mini", game["player_pos"])
        child["pos"] = [
            max(20, min(WIDTH - 20, int(enemy["pos"][0] + random.randint(-16, 16)))),
            max(20, min(HEIGHT - 20, int(enemy["pos"][1] + random.randint(-16, 16))))
        ]
        game["enemies"].append(child)


def on_enemy_death(game, enemy, give_score=True):
    if enemy["type"] == "boss":
        if give_score:
            game["score"] += 5
        on_boss_death(game, enemy["pos"])
    elif enemy["type"] == "inverter":
        if give_score:
            game["score"] += 10
        game["inverter_active"] = False
        game["inverter_timer"] = 0
    else:
        if give_score:
            game["score"] += 3 if enemy["type"] in MINIBOSS_TYPES else 1
        if enemy["type"] == "splitter":
            spawn_splitter_children(game, enemy)
        if enemy["type"] == "smasher":
            game["smasher_fields"].append({
                "pos": [enemy["pos"][0], enemy["pos"][1]],
                "timer": SMASHER_FIELD_DURATION,
                "radius": SMASHER_FIELD_RADIUS
            })


def get_upgrade_cost(level):
    return 1 + (level * 2)


def purchase_upgrade(game, upgrade_name):
    level = game["upgrades"][upgrade_name]
    cost = get_upgrade_cost(level)
    if game["coin_count"] >= cost:
        game["coin_count"] -= cost
        game["upgrades"][upgrade_name] += 1


def fire_bullets(game, start_x, start_y, dx, dy):
    dist = math.hypot(dx, dy) or 1
    dir_x = dx / dist
    dir_y = dy / dist
    base_angle = math.atan2(dir_y, dir_x)
    multishot_level = game["upgrades"]["multishot"]
    bullet_count = 1 + multishot_level
    spread_step = math.radians(8)
    start_offset = -(bullet_count - 1) / 2

    for i in range(bullet_count):
        angle = base_angle + (start_offset + i) * spread_step
        shot_dir_x = math.cos(angle)
        shot_dir_y = math.sin(angle)
        game["bullets"].append([
            start_x + shot_dir_x * 40,
            start_y + shot_dir_y * 40,
            shot_dir_x,
            shot_dir_y,
            game["upgrades"]["piercing"]
        ])


def keep_boss_out_of_center(enemy):
    boss_margin = 50
    enemy["pos"][0] = max(boss_margin, min(WIDTH - boss_margin, enemy["pos"][0]))
    enemy["pos"][1] = max(boss_margin, min(HEIGHT - boss_margin, enemy["pos"][1]))

    center_x = WIDTH // 2
    center_y = HEIGHT // 2
    dx = enemy["pos"][0] - center_x
    dy = enemy["pos"][1] - center_y
    dist = math.hypot(dx, dy)

    if dist < BOSS_CENTER_RADIUS:
        if dist == 0:
            dx, dy = 1, 0
            dist = 1
        scale = BOSS_CENTER_RADIUS / dist
        enemy["pos"][0] = center_x + dx * scale
        enemy["pos"][1] = center_y + dy * scale

        enemy["pos"][0] = max(boss_margin, min(WIDTH - boss_margin, enemy["pos"][0]))
        enemy["pos"][1] = max(boss_margin, min(HEIGHT - boss_margin, enemy["pos"][1]))


def update_boss_orbit(enemy, dt):
    if "boss_entity" not in enemy:
        return

    boss_entity = enemy["boss_entity"]
    boss_entity.orbit_timer += dt
    if boss_entity.orbit_timer >= BOSS_ORBIT_CHANGE_DELAY:
        boss_entity.orbit_angle += random.uniform(-0.9, 0.9)
        boss_entity.orbit_radius = BOSS_CENTER_RADIUS + random.randint(-BOSS_ORBIT_JITTER, BOSS_ORBIT_JITTER)
        boss_entity.orbit_timer = 0

    center_x = WIDTH // 2
    center_y = HEIGHT // 2
    target_x = center_x + math.cos(boss_entity.orbit_angle) * boss_entity.orbit_radius
    target_y = center_y + math.sin(boss_entity.orbit_angle) * boss_entity.orbit_radius

    move_dx = target_x - enemy["pos"][0]
    move_dy = target_y - enemy["pos"][1]
    move_dist = math.hypot(move_dx, move_dy) or 1

    enemy["pos"][0] += (move_dx / move_dist) * enemy["speed"]
    enemy["pos"][1] += (move_dy / move_dist) * enemy["speed"]
    boss_entity.orbit_angle += 0.01


def trigger_shockwave(game):
    game["shockwave_active"] = True
    game["shockwave_radius"] = 0
    game["shockwave_center"] = [game["player_pos"][0], game["player_pos"][1]]
    game["shockwave_timer"] = SHOCKWAVE_COOLDOWN
    game["game_speed_multiplier"] = 0.1


def apply_barrier_push(game, enemy):
    if not game["barrier_active"]:
        return

    px, py = game["player_pos"]
    dx = enemy["pos"][0] - px
    dy = enemy["pos"][1] - py
    dist = math.hypot(dx, dy)

    if dist < BARRIER_RADIUS:
        if dist == 0:
            dx, dy = 1, 0
            dist = 1
        enemy["pos"][0] = px + (dx / dist) * BARRIER_RADIUS
        enemy["pos"][1] = py + (dy / dist) * BARRIER_RADIUS


def clamp_to_backline(enemy):
    enemy["pos"][0] = max(15, min(WIDTH - 15, enemy["pos"][0]))
    enemy["pos"][1] = max(15, min(HEIGHT - 15, enemy["pos"][1]))

    if INNER_ZONE_X_MIN < enemy["pos"][0] < INNER_ZONE_X_MAX and INNER_ZONE_Y_MIN < enemy["pos"][1] < INNER_ZONE_Y_MAX:
        left_dist = enemy["pos"][0] - INNER_ZONE_X_MIN
        right_dist = INNER_ZONE_X_MAX - enemy["pos"][0]
        top_dist = enemy["pos"][1] - INNER_ZONE_Y_MIN
        bottom_dist = INNER_ZONE_Y_MAX - enemy["pos"][1]
        nearest = min(left_dist, right_dist, top_dist, bottom_dist)

        if nearest == left_dist:
            enemy["pos"][0] = INNER_ZONE_X_MIN
        elif nearest == right_dist:
            enemy["pos"][0] = INNER_ZONE_X_MAX
        elif nearest == top_dist:
            enemy["pos"][1] = INNER_ZONE_Y_MIN
        else:
            enemy["pos"][1] = INNER_ZONE_Y_MAX


def update_protector_shields(game):
    for enemy in game["enemies"]:
        enemy["shield_source"] = False
        if enemy["type"] != "shielder":
            enemy["shield_health"] = 0

    for protector in [enemy for enemy in game["enemies"] if enemy["type"] == "protector"]:
        protector["protected_targets"] = []
        for enemy in game["enemies"]:
            if enemy is protector or enemy["type"] == "boss":
                continue
            if math.hypot(enemy["pos"][0] - protector["pos"][0], enemy["pos"][1] - protector["pos"][1]) <= PROTECTOR_RADIUS:
                if enemy.get("shield_health", 0) <= 0:
                    enemy["shield_health"] = 1
                enemy["shield_source"] = True
                protector["protected_targets"].append(enemy)


def update_reflect_shields(game, dt):
    for enemy in game["enemies"]:
        if enemy.get("reflect_shield_timer", 0) > 0:
            enemy["reflect_shield_timer"] = max(0, enemy["reflect_shield_timer"] - dt)
            enemy["reflect_shield"] = enemy["reflect_shield_timer"] > 0
        else:
            enemy["reflect_shield"] = False


def update_boss_like_specials(game, enemy, dt):
    if "boss_entity" not in enemy:
        return

    enemy["special_timer"] = enemy.get("special_timer", 0) + dt

    if enemy["type"] == "multiplier" and enemy["special_timer"] >= MINIBOSS_TIMER_DELAY:
        clone = create_miniboss("multiplier", game["player_pos"])
        clone["pos"] = [enemy["pos"][0] + random.randint(-25, 25), enemy["pos"][1] + random.randint(-25, 25)]
        clone["boss_entity"].pos[0] = clone["pos"][0]
        clone["boss_entity"].pos[1] = clone["pos"][1]
        game["enemies"].append(clone)
        enemy["special_timer"] = 0
    elif enemy["type"] == "singularity" and enemy["special_timer"] >= MINIBOSS_TIMER_DELAY:
        if len(game["black_holes"]) == 0:
            game["black_holes"].append({
                "pos": [random.randint(80, WIDTH - 80), random.randint(80, HEIGHT - 80)],
                "spawn_time": pygame.time.get_ticks(),
                "radius": SINGULARITY_RADIUS
            })
        enemy["special_timer"] = 0
    elif enemy["type"] == "strobe" and enemy["special_timer"] >= STROBE_TELEPORT_DELAY:
        new_pos = spawn_enemy_far(game["player_pos"])
        enemy["pos"] = [new_pos[0], new_pos[1]]
        enemy["boss_entity"].pos[0] = enemy["pos"][0]
        enemy["boss_entity"].pos[1] = enemy["pos"][1]
        enemy["special_timer"] = 0
    elif enemy["type"] == "prism":
        enemy["shield_pulse_timer"] = enemy.get("shield_pulse_timer", 0) + dt
        if enemy["shield_pulse_timer"] >= PRISM_SHIELD_DELAY:
            for target_enemy in game["enemies"]:
                if target_enemy is enemy or target_enemy["type"] == "boss":
                    continue
                if math.hypot(target_enemy["pos"][0] - enemy["pos"][0], target_enemy["pos"][1] - enemy["pos"][1]) <= PRISM_RADIUS:
                    target_enemy["reflect_shield_timer"] = PRISM_SHIELD_DURATION
                    target_enemy["reflect_shield"] = True
            enemy["shield_pulse_timer"] = 0
    elif enemy["type"] == "inverter" and enemy["special_timer"] >= INVERTER_INVERT_DURATION and not game["inverter_active"]:
        game["inverter_active"] = True
        game["inverter_timer"] = INVERTER_INVERT_DURATION
        enemy["special_timer"] = 0


def trigger_smasher_overlay(game):
    rect_width = random.randint(180, 320)
    rect_height = random.randint(120, 240)
    rect_x = random.randint(0, WIDTH - rect_width)
    rect_y = random.randint(0, HEIGHT - rect_height)
    game["smasher_overlays"].append({
        "rect": pygame.Rect(rect_x, rect_y, rect_width, rect_height),
        "timer": SMASHER_OVERLAY_DURATION
    })


def update_smasher_overlays(game, dt):
    for overlay in game["smasher_overlays"][:]:
        overlay["timer"] = max(0, overlay["timer"] - dt)
        if overlay["timer"] == 0:
            game["smasher_overlays"].remove(overlay)


def draw_enemy_legend():
    box_width = 210
    box_height = 24 + len(ENEMY_LEGEND) * 22
    box_rect = pygame.Rect(WIDTH - box_width - 12, 12, box_width, box_height)
    pygame.draw.rect(screen, WHITE, box_rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, box_rect, 2, border_radius=8)
    title = small_font.render("Enemy Legend", True, BLACK)
    screen.blit(title, (box_rect.x + 10, box_rect.y + 8))

    y = box_rect.y + 30
    for name, color in ENEMY_LEGEND:
        if name in {"Multiplier", "Singularity", "Strobe", "Prism", "Inverter"}:
            pygame.draw.polygon(screen, color, [
                (box_rect.x + 16, y + 1),
                (box_rect.x + 10, y + 12),
                (box_rect.x + 22, y + 12)
            ])
            pygame.draw.polygon(screen, BLACK, [
                (box_rect.x + 16, y + 1),
                (box_rect.x + 10, y + 12),
                (box_rect.x + 22, y + 12)
            ], 1)
        else:
            pygame.draw.circle(screen, color, (box_rect.x + 16, y + 7), 5)
        text = small_font.render(f"- {name}", True, BLACK)
        screen.blit(text, (box_rect.x + 28, y))
        y += 22


def draw_active_powerups(game):
    y = 20
    for powerup_type, time_left in game["active_powerups"].items():
        if time_left > 0:
            seconds = time_left / 1000
            label = PowerUp.LABELS[powerup_type]
            text = font.render(f"{label}: {seconds:.1f}s", True, BLACK)
            screen.blit(text, (WIDTH - text.get_width() - 10, y))
            y += 30


def draw_controls_overlay():
    lines = [
        "Left Click: Shoot | Right Click: Plant Mine",
        "X: Shockwave | Z: Barrier | 1-3: Upgrades",
        "Shoot Power-ups/Coins to collect"
    ]
    y = 470
    for line in lines:
        text = small_font.render(line, True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
        y += 28


def draw_grid_background():
    screen.fill(WHITE)
    for x in range(0, WIDTH - LAB_PANEL_WIDTH, 40):
        pygame.draw.line(screen, LAB_GRID_COLOR, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, LAB_GRID_COLOR, (0, y), (WIDTH - LAB_PANEL_WIDTH, y), 1)


def get_laboratory_buttons():
    buttons = []
    panel_x = WIDTH - LAB_PANEL_WIDTH + 15
    y = 60

    enemy_buttons = [
        ("Normal", "normal"),
        ("Fast", "fast"),
        ("Tank", "tank"),
        ("Splitter", "splitter"),
        ("Shielder", "shielder"),
        ("Zig-Zagger", "zigzagger"),
        ("Sapper", "sapper"),
        ("Magnet", "magnet"),
        ("Protector", "protector"),
        ("Medic", "medic"),
        ("Smasher", "smasher"),
        ("Charger", "charger"),
        ("Multiplier", "multiplier"),
        ("Singularity", "singularity"),
        ("Strobe", "strobe"),
        ("Prism", "prism"),
        ("Inverter", "inverter"),
        ("Boss", "boss"),
    ]

    for label, enemy_type in enemy_buttons:
        buttons.append({
            "label": label,
            "action": "spawn",
            "value": enemy_type,
            "rect": pygame.Rect(panel_x, y, LAB_PANEL_WIDTH - 30, LAB_BUTTON_HEIGHT)
        })
        y += LAB_BUTTON_HEIGHT + 6

    bottom_y = HEIGHT - 42
    bottom_x = 20
    bottom_specs = [
        ("Back to Menu", "back", 150),
        ("Freeze Enemies", "toggle_freeze", 170),
        ("Show Range", "toggle_range", 140),
        ("Clear All", "clear_all", 110),
    ]
    for label, action, width in bottom_specs:
        buttons.append({
            "label": label,
            "action": action,
            "rect": pygame.Rect(bottom_x, bottom_y, width, LAB_BUTTON_HEIGHT)
        })
        bottom_x += width + 12
    return buttons


def draw_laboratory_sidebar(lab_state):
    panel_rect = pygame.Rect(WIDTH - LAB_PANEL_WIDTH, 0, LAB_PANEL_WIDTH, HEIGHT)
    pygame.draw.rect(screen, MINT, panel_rect)
    pygame.draw.line(screen, BLACK, (panel_rect.x, 0), (panel_rect.x, HEIGHT), 2)

    title = font.render("Laboratory", True, BLACK)
    screen.blit(title, (panel_rect.x + 20, 15))

    for button in lab_state["buttons"]:
        color = WHITE
        if button["action"] == "toggle_freeze" and lab_state["freeze_enemies"]:
            color = BLUE
        if button["action"] == "toggle_range" and lab_state["show_range"]:
            color = GREEN
        pygame.draw.rect(screen, color, button["rect"], border_radius=6)
        pygame.draw.rect(screen, BLACK, button["rect"], 2, border_radius=6)
        label = small_font.render(button["label"], True, BLACK)
        screen.blit(label, (button["rect"].x + 10, button["rect"].y + 6))

    info_lines = [
        f"Freeze: {'ON' if lab_state['freeze_enemies'] else 'OFF'}",
        f"Ranges: {'ON' if lab_state['show_range'] else 'OFF'}",
        "Click field to shoot",
        "Press C to clear"
    ]
    y = HEIGHT - 130
    for line in info_lines:
        text = small_font.render(line, True, BLACK)
        screen.blit(text, (20, y))
        y += 22


def draw_laboratory_player(player_pos, gun_img):
    px, py = player_pos
    screen.blit(face_img, (px - 30, py - 65))
    pygame.draw.line(screen, BLACK, (px, py), (px, py + 45), 4)
    pygame.draw.line(screen, BLACK, (px, py + 45), (px - 20, py + 75), 4)
    pygame.draw.line(screen, BLACK, (px, py + 45), (px + 20, py + 75), 4)
    gun_rect = gun_img.get_rect(center=player_pos)
    screen.blit(gun_img, gun_rect)


def run_laboratory_mode():
    lab_game = reset_game()
    lab_game["player_pos"] = LAB_SHOOTER_POS[:]
    lab_game["player_lives"] = 999999
    lab_game["lives"] = lab_game["player_lives"]

    lab_state = {
        "game": lab_game,
        "freeze_enemies": False,
        "show_range": False,
        "buttons": get_laboratory_buttons(),
        "spawn_line_x": WIDTH - LAB_PANEL_WIDTH - 70
    }

    running_lab = True
    while running_lab:
        dt = clock.tick(60)
        draw_grid_background()
        update_game_timers(lab_game, dt)
        cleanup_expired_pickups(lab_game)
        update_smasher_overlays(lab_game, dt)
        update_protector_shields(lab_game)
        update_reflect_shields(lab_game, dt)

        mx, my = pygame.mouse.get_pos()
        dx = mx - lab_game["player_pos"][0]
        dy = my - lab_game["player_pos"][1]
        angle = math.degrees(math.atan2(-dy, dx)) + 180
        gun_img = pygame.transform.rotate(gun_img_original, angle)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                lab_game["enemies"].clear()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked_button = None
                for button in lab_state["buttons"]:
                    if button["rect"].collidepoint(event.pos):
                        clicked_button = button
                        break

                if clicked_button:
                    if clicked_button["action"] == "spawn":
                        enemy_type = clicked_button["value"]
                        spawn_y = random.randint(60, HEIGHT - 120)
                        if enemy_type == "boss":
                            enemy = create_boss(lab_game["player_pos"])
                            enemy["pos"] = [lab_state["spawn_line_x"], spawn_y]
                        else:
                            enemy = create_enemy_from_type(enemy_type, lab_game["player_pos"])
                            enemy["pos"] = [lab_state["spawn_line_x"], spawn_y]
                            if enemy["type"] == "sapper":
                                enemy["orbit_center"] = enemy["pos"][:]
                        lab_game["enemies"].append(enemy)
                    elif clicked_button["action"] == "back":
                        return
                    elif clicked_button["action"] == "toggle_freeze":
                        lab_state["freeze_enemies"] = not lab_state["freeze_enemies"]
                    elif clicked_button["action"] == "toggle_range":
                        lab_state["show_range"] = not lab_state["show_range"]
                    elif clicked_button["action"] == "clear_all":
                        lab_game["enemies"].clear()
                elif mx < WIDTH - LAB_PANEL_WIDTH:
                    fire_bullets(lab_game, lab_game["player_pos"][0], lab_game["player_pos"][1], dx, dy)

        for enemy in lab_game["enemies"][:]:
            speed = enemy["speed"]

            if "boss_entity" in enemy:
                boss_entity = enemy["boss_entity"]
                boss_entity.pos[0] = enemy["pos"][0]
                boss_entity.pos[1] = enemy["pos"][1]
                boss_entity.minion_timer += dt
                boss_entity.wall_timer += dt
                if boss_entity.minion_timer >= BOSS_MINION_DELAY:
                    lab_game["enemies"].append(boss_entity.spawn_minion())
                    boss_entity.minion_timer = 0
                if boss_entity.wall_timer >= BOSS_WALL_DELAY:
                    lab_game["walls"].append(boss_entity.spawn_wall())
                    boss_entity.wall_timer = 0
                update_boss_like_specials(lab_game, enemy, dt)

            if enemy["type"] == "sapper":
                enemy["wall_timer"] += dt
                if enemy["wall_timer"] >= SAPPER_WALL_DELAY:
                    lab_game["walls"].append(Wall(enemy["pos"][0] - 12, enemy["pos"][1] - 12, 24, 24))
                    enemy["wall_timer"] = 0
            if enemy["type"] == "medic":
                enemy["heal_timer"] += dt
                if enemy["heal_timer"] >= MEDIC_HEAL_DELAY:
                    for heal_target in lab_game["enemies"]:
                        if heal_target is enemy:
                            continue
                        if math.hypot(heal_target["pos"][0] - enemy["pos"][0], heal_target["pos"][1] - enemy["pos"][1]) <= MEDIC_HEAL_RADIUS:
                            heal_target["hp"] = min(heal_target["max_hp"], heal_target["hp"] + 1)
                    enemy["heal_timer"] = 0
            if enemy["type"] == "smasher":
                if math.hypot(enemy["pos"][0] - lab_game["player_pos"][0], enemy["pos"][1] - lab_game["player_pos"][1]) < SMASHER_TRIGGER_DISTANCE:
                    enemy["overlay_timer"] += dt
                    if enemy["overlay_timer"] >= SMASHER_OVERLAY_DURATION:
                        trigger_smasher_overlay(lab_game)
                        enemy["overlay_timer"] = 0
                else:
                    enemy["overlay_timer"] = 0
            if enemy["type"] == "charger":
                enemy["charge_timer"] += dt
                if enemy["charge_state"] == "idle" and enemy["charge_timer"] >= CHARGER_IDLE_DELAY:
                    enemy["charge_state"] = "scream"
                    enemy["charge_timer"] = 0
                    enemy["charge_target"] = lab_game["player_pos"][:]
                elif enemy["charge_state"] == "scream" and enemy["charge_timer"] >= CHARGER_SCREAM_DELAY:
                    enemy["charge_state"] = "charge"
                    enemy["charge_timer"] = 0

            if lab_state["freeze_enemies"]:
                continue

            if "boss_entity" in enemy:
                enemy["speed"] = 0.4
                update_boss_orbit(enemy, dt)
                keep_boss_out_of_center(enemy)
            elif enemy["type"] == "sapper":
                theta = pygame.time.get_ticks() * enemy["orbit_speed"]
                enemy["pos"][0] = enemy["orbit_center"][0] + enemy["orbit_a"] * math.cos(theta)
                enemy["pos"][1] = enemy["orbit_center"][1] + enemy["orbit_b"] * math.sin(theta)
            elif enemy["type"] in {"magnet", "protector", "medic"}:
                if enemy["pos"][0] < lab_game["player_pos"][0]:
                    enemy["pos"][0] += speed * 0.35
                if enemy["pos"][0] > lab_game["player_pos"][0]:
                    enemy["pos"][0] -= speed * 0.35
                if enemy["pos"][1] < lab_game["player_pos"][1]:
                    enemy["pos"][1] += speed * 0.35
                if enemy["pos"][1] > lab_game["player_pos"][1]:
                    enemy["pos"][1] -= speed * 0.35
                clamp_to_backline(enemy)
            elif enemy["type"] == "smasher":
                if enemy["pos"][0] < lab_game["player_pos"][0]:
                    enemy["pos"][0] += speed
                if enemy["pos"][0] > lab_game["player_pos"][0]:
                    enemy["pos"][0] -= speed
                if enemy["pos"][1] < lab_game["player_pos"][1]:
                    enemy["pos"][1] += speed
                if enemy["pos"][1] > lab_game["player_pos"][1]:
                    enemy["pos"][1] -= speed
            elif enemy["type"] == "charger" and enemy["charge_state"] == "charge":
                current = pygame.math.Vector2(enemy["pos"][0], enemy["pos"][1])
                target = pygame.math.Vector2(enemy["charge_target"][0], enemy["charge_target"][1])
                distance = current.distance_to(target)
                if distance > 1:
                    current = current.lerp(target, min(1.0, (speed * 5) / distance))
                    enemy["pos"][0], enemy["pos"][1] = current.x, current.y
                else:
                    enemy["charge_state"] = "idle"
                    enemy["charge_timer"] = 0
            elif enemy["type"] == "zigzagger":
                dir_sign = 1 if enemy["pos"][0] < lab_game["player_pos"][0] else -1
                enemy["baseline_y"] += (lab_game["player_pos"][1] - enemy["baseline_y"]) * 0.02
                enemy["zig_x"] += speed * dir_sign
                enemy["pos"][0] += speed * dir_sign
                enemy["pos"][1] = enemy["baseline_y"] + math.sin(enemy["zig_x"] * enemy["frequency"]) * enemy["amplitude"]
            else:
                if enemy["pos"][0] < lab_game["player_pos"][0]:
                    enemy["pos"][0] += speed
                if enemy["pos"][0] > lab_game["player_pos"][0]:
                    enemy["pos"][0] -= speed
                if enemy["pos"][1] < lab_game["player_pos"][1]:
                    enemy["pos"][1] += speed
                if enemy["pos"][1] > lab_game["player_pos"][1]:
                    enemy["pos"][1] -= speed

        for bullet in lab_game["bullets"][:]:
            bullet_pos = pygame.math.Vector2(bullet[0], bullet[1])
            bullet_vel = pygame.math.Vector2(bullet[2], bullet[3])
            for magnet in [enemy for enemy in lab_game["enemies"] if enemy["type"] == "magnet"]:
                magnet_vec = pygame.math.Vector2(magnet["pos"][0], magnet["pos"][1])
                dist_to_magnet = bullet_pos.distance_to(magnet_vec)
                if dist_to_magnet <= MAGNET_RADIUS:
                    pull_dir = magnet_vec - bullet_pos
                    if pull_dir.length() > 0:
                        bullet_vel = bullet_vel.lerp(pull_dir.normalize(), 0.06)
            for black_hole in lab_game["black_holes"]:
                hole_vec = pygame.math.Vector2(black_hole["pos"][0], black_hole["pos"][1])
                dist_to_hole = bullet_pos.distance_to(hole_vec)
                if dist_to_hole <= black_hole["radius"]:
                    pull_dir = hole_vec - bullet_pos
                    if pull_dir.length() > 0:
                        bullet_vel = bullet_vel.lerp(pull_dir.normalize(), 0.08)
            for smasher_field in lab_game["smasher_fields"]:
                field_vec = pygame.math.Vector2(smasher_field["pos"][0], smasher_field["pos"][1])
                dist_to_field = bullet_pos.distance_to(field_vec)
                if dist_to_field <= smasher_field["radius"]:
                    pull_dir = field_vec - bullet_pos
                    if pull_dir.length() > 0:
                        bullet_vel = bullet_vel.lerp(pull_dir.normalize(), 0.08)
            bullet[2], bullet[3] = bullet_vel.x, bullet_vel.y
            bullet[0] += bullet[2] * 10
            bullet[1] += bullet[3] * 10

            if not (0 <= bullet[0] <= WIDTH - LAB_PANEL_WIDTH and 0 <= bullet[1] <= HEIGHT):
                lab_game["bullets"].remove(bullet)
                continue

            bullet_rect = pygame.Rect(int(bullet[0]) - 4, int(bullet[1]) - 4, 8, 8)
            for enemy in lab_game["enemies"][:]:
                hitbox = 50 if "boss_entity" in enemy else 25
                if abs(enemy["pos"][0] - bullet[0]) < hitbox and abs(enemy["pos"][1] - bullet[1]) < hitbox:
                    if enemy.get("reflect_shield", False):
                        bullet[2] *= -1
                        bullet[3] *= -1
                        bullet[0] += bullet[2] * 12
                        bullet[1] += bullet[3] * 12
                    elif enemy["type"] == "shielder" and enemy.get("shield_health", 0) > 0:
                        enemy["shield_health"] = max(0, enemy["shield_health"] - 1)
                    else:
                        enemy["hp"] -= 1
                    if bullet in lab_game["bullets"] and not enemy.get("reflect_shield", False):
                        if bullet[4] > 0:
                            bullet[4] -= 1
                        else:
                            lab_game["bullets"].remove(bullet)
                    if enemy["hp"] <= 0:
                        lab_game["enemies"].remove(enemy)
                        on_enemy_death(lab_game, enemy)
                    break

        for wall in lab_game["walls"]:
            wall.draw(screen)

        for black_hole in lab_game["black_holes"]:
            pygame.draw.circle(screen, BLACK, (int(black_hole["pos"][0]), int(black_hole["pos"][1])), black_hole["radius"], 1)
            pygame.draw.circle(screen, DARK_BLUE, (int(black_hole["pos"][0]), int(black_hole["pos"][1])), 12)

        for smasher_field in lab_game["smasher_fields"]:
            pygame.draw.circle(screen, DARK_BLUE, (int(smasher_field["pos"][0]), int(smasher_field["pos"][1])), smasher_field["radius"], 1)

        for protector in [enemy for enemy in lab_game["enemies"] if enemy["type"] == "protector"]:
            for target_enemy in protector.get("protected_targets", []):
                pygame.draw.line(screen, GOLD, (int(protector["pos"][0]), int(protector["pos"][1])), (int(target_enemy["pos"][0]), int(target_enemy["pos"][1])), 2)

        for enemy in lab_game["enemies"]:
            ex, ey = enemy["pos"]
            if "boss_entity" in enemy:
                screen.blit(boss_img, (ex - 50, ey - 50))
                hp_ratio = enemy["hp"] / enemy["max_hp"]
                pygame.draw.rect(screen, (200, 0, 0), (ex - 50, ey - 70, 100, 8))
                pygame.draw.rect(screen, (0, 200, 0), (ex - 50, ey - 70, 100 * hp_ratio, 8))
            else:
                screen.blit(enemy_img, (ex - 20, ey - 20))
                if enemy["type"] == "mini":
                    mini_rect = pygame.transform.scale(enemy_img, (24, 24))
                    screen.blit(mini_rect, (ex - 12, ey - 12))
                if enemy["type"] == "shielder" and enemy.get("shield_health", 0) > 0:
                    pygame.draw.circle(screen, BLUE, (int(ex), int(ey)), 28, 3)
                if enemy.get("shield_source", False):
                    pygame.draw.circle(screen, WHITE, (int(ex), int(ey)), 24, 1)
                if enemy.get("is_miniboss", False):
                    pygame.draw.polygon(screen, enemy["color_dot"], [
                        (int(ex), int(ey - 36)),
                        (int(ex - 6), int(ey - 24)),
                        (int(ex + 6), int(ey - 24))
                    ])
                    pygame.draw.polygon(screen, BLACK, [
                        (int(ex), int(ey - 36)),
                        (int(ex - 6), int(ey - 24)),
                        (int(ex + 6), int(ey - 24))
                    ], 1)
                elif enemy.get("color_dot"):
                    pygame.draw.circle(screen, enemy["color_dot"], (int(ex), int(ey - 28)), 5)
                    pygame.draw.circle(screen, BLACK, (int(ex), int(ey - 28)), 5, 1)
                if enemy["type"] == "charger" and enemy.get("charge_state") == "scream":
                    rush_text = small_font.render("!!!RUSHING!!!", True, RED)
                    screen.blit(rush_text, (int(ex) - rush_text.get_width() // 2, int(ey) - 55))

                hp_ratio = enemy["hp"] / enemy["max_hp"]
                pygame.draw.rect(screen, (200, 0, 0), (ex - 20, ey - 30, 40, 5))
                pygame.draw.rect(screen, (0, 200, 0), (ex - 20, ey - 30, 40 * hp_ratio, 5))

            if enemy.get("is_miniboss", False):
                pygame.draw.polygon(screen, enemy["color_dot"], [
                    (int(ex), int(ey - 36)),
                    (int(ex - 6), int(ey - 24)),
                    (int(ex + 6), int(ey - 24))
                ])
                pygame.draw.polygon(screen, BLACK, [
                    (int(ex), int(ey - 36)),
                    (int(ex - 6), int(ey - 24)),
                    (int(ex + 6), int(ey - 24))
                ], 1)

            if lab_state["show_range"] and enemy["type"] == "protector":
                pygame.draw.circle(screen, GOLD, (int(ex), int(ey)), PROTECTOR_RADIUS, 1)
            if lab_state["show_range"] and enemy["type"] == "medic":
                pygame.draw.circle(screen, LIME_GREEN, (int(ex), int(ey)), MEDIC_HEAL_RADIUS, 1)

        for bullet in lab_game["bullets"]:
            pygame.draw.circle(screen, BLACK, (int(bullet[0]), int(bullet[1])), 8)

        draw_laboratory_player(lab_game["player_pos"], gun_img)
        draw_laboratory_sidebar(lab_state)

        for overlay in lab_game["smasher_overlays"]:
            overlay_surface = pygame.Surface((overlay["rect"].width, overlay["rect"].height), pygame.SRCALPHA)
            overlay_surface.fill((200, 200, 200, 90))
            for _ in range(40):
                line_y = random.randint(0, overlay["rect"].height - 1)
                pygame.draw.line(overlay_surface, (80, 80, 80, 120), (0, line_y), (overlay["rect"].width, line_y), 1)
            screen.blit(overlay_surface, overlay["rect"].topleft)

        pygame.display.flip()


# ---------- BOSS INTRO ----------
def play_boss_intro():
    duration = 2500
    start_time = pygame.time.get_ticks()

    font_size = 64
    grow = True
    boss_text = "BOSS INCOMING!"
    sub_text = "GET READY..."

    line_count = 12
    line_speed = 8
    lines = []
    for _ in range(line_count):
        lines.append({
            "x": random.randint(0, WIDTH),
            "y": random.randint(-HEIGHT, 0),
            "angle": random.uniform(-0.3, 0.3),
            "width": random.randint(2, 5),
            "color": (255, random.randint(0, 60), random.randint(0, 60))
        })

    while pygame.time.get_ticks() - start_time < duration:
        clock.tick(60)
        screen.fill((0, 0, 0))

        for line in lines:
            line_len = random.randint(180, 260)
            end_x = int(line["x"] + math.sin(line["angle"]) * line_len)
            end_y = int(line["y"] + math.cos(line["angle"]) * line_len)
            pygame.draw.line(screen, line["color"], (line["x"], line["y"]), (end_x, end_y), line["width"])
            line["y"] += line_speed
            if line["y"] > HEIGHT + 40:
                line["x"] = random.randint(0, WIDTH)
                line["y"] = random.randint(-HEIGHT, 0)
                line["angle"] = random.uniform(-0.3, 0.3)
                line["width"] = random.randint(2, 5)
                line["color"] = (255, random.randint(0, 60), random.randint(0, 60))

        if grow:
            font_size += 2
            if font_size >= 90:
                grow = False
        else:
            font_size -= 2
            if font_size <= 64:
                grow = True

        anim_font = pygame.font.SysFont("arial", font_size, bold=True)
        text = anim_font.render(boss_text, True, (255, 0, 0))
        shadow = anim_font.render(boss_text, True, (40, 40, 40))

        screen.blit(shadow, (WIDTH // 2 - text.get_width() // 2 + 6, HEIGHT // 2 - text.get_height() // 2 + 6))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

        sub_font = pygame.font.SysFont("consolas", 38, bold=True)
        sub = sub_font.render(sub_text, True, (200, 200, 200))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + text.get_height() // 2 + 20))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()


# ---------- LEVEL 100 EVENT ----------
def play_level100_event():
    duration = 2000
    start_time = pygame.time.get_ticks()

    while pygame.time.get_ticks() - start_time < duration:
        screen.fill((0, 0, 0))

        rect = wts_img_original.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        text = big_font.render("FINAL TEST", True, (255, 0, 0))

        screen.blit(wts_img_original, rect)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    q_list = questions[:]
    random.shuffle(q_list)
    q = q_list[0]
    user_input = ""

    while True:
        screen.fill(MINT)

        qtxt = font.render(q["q"], True, BLACK)
        atxt = font.render("Answer: " + user_input, True, BLACK)

        screen.blit(qtxt, (200, 200))
        screen.blit(atxt, (200, 250))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return user_input.strip() == q["a"]
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    user_input += event.unicode


# ---------- MENU ----------
def show_menu():
    start_rect = pygame.Rect(WIDTH // 2 - 160, 380, 320, 44)
    lab_rect = pygame.Rect(WIDTH - 190, 20, 170, 40)
    while True:
        screen.fill(MINT)

        title = big_font.render("Aryan Killer", True, BLACK)
        hs = font.render(f"High Score: {stats['high_score']}", True, BLACK)
        gp = font.render(f"Games Played: {stats['games_played']}", True, BLACK)
        start = font.render("Start Game", True, BLACK)
        lab = small_font.render("Laboratory", True, BLACK)

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
        screen.blit(hs, (WIDTH // 2 - hs.get_width() // 2, 260))
        screen.blit(gp, (WIDTH // 2 - gp.get_width() // 2, 300))
        pygame.draw.rect(screen, WHITE, start_rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, start_rect, 2, border_radius=8)
        screen.blit(start, (start_rect.centerx - start.get_width() // 2, start_rect.y + 7))
        pygame.draw.rect(screen, WHITE, lab_rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, lab_rect, 2, border_radius=8)
        screen.blit(lab, (lab_rect.centerx - lab.get_width() // 2, lab_rect.y + 8))
        draw_controls_overlay()

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "game"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_rect.collidepoint(event.pos):
                    return "game"
                if LABORATORY_MODE_ENABLED and lab_rect.collidepoint(event.pos):
                    return "laboratory"


# ---------- MAIN ----------
running = True

while running:
    selected_mode = show_menu()
    if selected_mode == "laboratory":
        run_laboratory_mode()
        continue
    game = reset_game()

    for _ in range(2):
        game["enemies"].append(create_enemy(game["player_pos"]))

    while not game["game_over"]:
        dt = clock.tick(60)
        screen.fill(MINT)

        speed_scale, spawn_delay = get_difficulty(game["score"])
        speed_mult = 2 if game["fast_forward"] else 1
        frame_speed_mult = speed_mult * game["game_speed_multiplier"]
        update_game_timers(game, dt)
        spawn_powerup_if_needed(game, dt)
        spawn_coin_if_needed(game, dt)
        spawn_barrel_if_needed(game, dt)
        cleanup_expired_pickups(game)
        update_smasher_overlays(game, dt)
        update_reflect_shields(game, dt)
        current_level = max(1, game["score"])
        boss_level_active = any("boss_entity" in enemy for enemy in game["enemies"])
        spawn_regular_enemies = not boss_level_active

        mx, my = pygame.mouse.get_pos()

        target = None
        if game["enemies"]:
            target = min(game["enemies"],
                key=lambda e: math.hypot(
                    e["pos"][0] - game["player_pos"][0],
                    e["pos"][1] - game["player_pos"][1]
                ))

        dx = (target["pos"][0] - game["player_pos"][0]) if game["auto_mode"] and target else (mx - game["player_pos"][0])
        dy = (target["pos"][1] - game["player_pos"][1]) if game["auto_mode"] and target else (my - game["player_pos"][1])

        angle = math.degrees(math.atan2(-dy, dx)) + 180
        gun_img = pygame.transform.rotate(gun_img_original, angle)
        gun_rect = gun_img.get_rect(center=game["player_pos"])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game["game_over"] = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game["auto_mode"] = not game["auto_mode"]
                if event.key == pygame.K_f and game["auto_mode"]:
                    game["fast_forward"] = not game["fast_forward"]
                    game["auto_timer"] = 0
                if event.key == pygame.K_x and game["shockwave_timer"] == 0:
                    trigger_shockwave(game)
                if event.key == pygame.K_z and game["barrier_cooldown"] == 0:
                    game["barrier_active"] = True
                    game["barrier_timer"] = BARRIER_DURATION
                    game["barrier_cooldown"] = BARRIER_COOLDOWN
                if event.key == pygame.K_1:
                    purchase_upgrade(game, "multishot")
                if event.key == pygame.K_2:
                    purchase_upgrade(game, "piercing")
                if event.key == pygame.K_3:
                    purchase_upgrade(game, "freeze")

            if not game["auto_mode"] and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    fire_bullets(game, game["player_pos"][0], game["player_pos"][1], dx, dy)
                if event.button == 3 and game["mine_count"] > 0:
                    game["mines"].append(Mine([mx, my]))
                    game["mine_count"] -= 1

        # movement
        keys = pygame.key.get_pressed()
        input_mult = -1 if game["inverter_active"] else 1
        if keys[pygame.K_w]:
            game["player_pos"][1] -= 5 * frame_speed_mult * input_mult
        if keys[pygame.K_s]:
            game["player_pos"][1] += 5 * frame_speed_mult * input_mult
        if keys[pygame.K_a]:
            game["player_pos"][0] -= 5 * frame_speed_mult * input_mult
        if keys[pygame.K_d]:
            game["player_pos"][0] += 5 * frame_speed_mult * input_mult

        game["player_pos"][0] = max(30, min(WIDTH - 30, game["player_pos"][0]))
        game["player_pos"][1] = max(30, min(HEIGHT - 30, game["player_pos"][1]))

        # auto fire
        if game["auto_mode"] and target:
            game["auto_timer"] += dt
            if game["auto_timer"] > 300:
                game["auto_timer"] = 0
                fire_bullets(game, game["player_pos"][0], game["player_pos"][1], dx, dy)

        # fast forward - auto stop 5 below boss levels
        if game["fast_forward"] and game["score"] > 0 and game["score"] % 50 == 45:
            game["fast_forward"] = False

        # boss intro 50
        if game["score"] == 50 and not game["boss_intro_done"]:
            play_boss_intro()
            game["boss_intro_done"] = True

        # boss spawn
        if game["score"] > 0 and game["score"] % 50 == 0 and not game["boss_spawned"] and current_level != INVERTER_TRIGGER_LEVEL:
            game["enemies"].append(create_boss(game["player_pos"]))
            game["boss_spawned"] = True
        if game["score"] % 50 != 0:
            game["boss_spawned"] = False

        if current_level == INVERTER_TRIGGER_LEVEL and not game["inverter_spawned"]:
            game["enemies"].append(create_inverter(game["player_pos"]))
            game["inverter_spawned"] = True
        elif current_level > 0 and current_level % 5 == 0 and game["miniboss_level_checked"] != current_level and current_level != INVERTER_TRIGGER_LEVEL:
            game["miniboss_level_checked"] = current_level
            if not boss_level_active and random.randint(1, MINIBOSS_SPAWN_CHANCE) == 1:
                miniboss_type = random.choice(["multiplier", "singularity", "strobe", "prism"])
                game["enemies"].append(create_miniboss(miniboss_type, game["player_pos"]))

        # level 100 event
        if game["score"] >= 100 and not game["level100_done"]:
            result = play_level100_event()
            game["level100_done"] = True

            if not result:
                game["game_over"] = True
            else:
                game["enemies"].append(create_boss(game["player_pos"]))

        # boss abilities
        for enemy in game["enemies"][:]:
            if "boss_entity" in enemy:
                boss_entity = enemy["boss_entity"]
                boss_entity.pos[0] = enemy["pos"][0]
                boss_entity.pos[1] = enemy["pos"][1]
                boss_entity.minion_timer += dt
                boss_entity.wall_timer += dt

                if boss_entity.minion_timer >= BOSS_MINION_DELAY:
                    game["enemies"].append(boss_entity.spawn_minion())
                    boss_entity.minion_timer = 0

                if boss_entity.wall_timer >= BOSS_WALL_DELAY:
                    game["walls"].append(boss_entity.spawn_wall())
                    boss_entity.wall_timer = 0
                update_boss_like_specials(game, enemy, dt)

        update_protector_shields(game)

        # spawn enemies
        game["spawn_timer"] += dt
        if spawn_regular_enemies and game["spawn_timer"] > spawn_delay:
            game["enemies"].append(create_enemy(game["player_pos"]))
            game["spawn_timer"] = 0

        # enemies move + hit
        for enemy in game["enemies"][:]:
            speed = enemy["speed"] if enemy["type"] == "boss" else enemy["speed"] * speed_scale * frame_speed_mult
            if enemy.get("slow_timer", 0) > 0:
                enemy["slow_timer"] = max(0, enemy["slow_timer"] - dt)
                speed *= 0.5

            if "boss_entity" in enemy:
                enemy["speed"] = 0.4 * frame_speed_mult
                update_boss_orbit(enemy, dt)
                keep_boss_out_of_center(enemy)
            elif enemy["type"] == "sapper":
                theta = pygame.time.get_ticks() * enemy["orbit_speed"]
                enemy["pos"][0] = enemy["orbit_center"][0] + enemy["orbit_a"] * math.cos(theta)
                enemy["pos"][1] = enemy["orbit_center"][1] + enemy["orbit_b"] * math.sin(theta)
                enemy["wall_timer"] += dt
                if enemy["wall_timer"] >= SAPPER_WALL_DELAY:
                    game["walls"].append(Wall(enemy["pos"][0] - 12, enemy["pos"][1] - 12, 24, 24))
                    enemy["wall_timer"] = 0
            elif enemy["type"] in {"magnet", "protector", "medic"}:
                if enemy["pos"][0] < game["player_pos"][0]:
                    enemy["pos"][0] += speed * 0.35
                if enemy["pos"][0] > game["player_pos"][0]:
                    enemy["pos"][0] -= speed * 0.35
                if enemy["pos"][1] < game["player_pos"][1]:
                    enemy["pos"][1] += speed * 0.35
                if enemy["pos"][1] > game["player_pos"][1]:
                    enemy["pos"][1] -= speed * 0.35
                clamp_to_backline(enemy)
                if enemy["type"] == "medic":
                    enemy["heal_timer"] += dt
                    if enemy["heal_timer"] >= MEDIC_HEAL_DELAY:
                        for heal_target in game["enemies"]:
                            if heal_target is enemy:
                                continue
                            if math.hypot(heal_target["pos"][0] - enemy["pos"][0], heal_target["pos"][1] - enemy["pos"][1]) <= MEDIC_HEAL_RADIUS:
                                heal_target["hp"] = min(heal_target["max_hp"], heal_target["hp"] + 1)
                        enemy["heal_timer"] = 0
            elif enemy["type"] == "smasher":
                if enemy["pos"][0] < game["player_pos"][0]:
                    enemy["pos"][0] += speed
                if enemy["pos"][0] > game["player_pos"][0]:
                    enemy["pos"][0] -= speed
                if enemy["pos"][1] < game["player_pos"][1]:
                    enemy["pos"][1] += speed
                if enemy["pos"][1] > game["player_pos"][1]:
                    enemy["pos"][1] -= speed
                if math.hypot(enemy["pos"][0] - game["player_pos"][0], enemy["pos"][1] - game["player_pos"][1]) < SMASHER_TRIGGER_DISTANCE:
                    enemy["overlay_timer"] += dt
                    if enemy["overlay_timer"] >= SMASHER_OVERLAY_DURATION:
                        trigger_smasher_overlay(game)
                        enemy["overlay_timer"] = 0
                else:
                    enemy["overlay_timer"] = 0
            elif enemy["type"] == "charger":
                enemy["charge_timer"] += dt
                if enemy["charge_state"] == "idle":
                    if enemy["charge_timer"] >= CHARGER_IDLE_DELAY:
                        enemy["charge_state"] = "scream"
                        enemy["charge_timer"] = 0
                        enemy["charge_target"] = game["player_pos"][:]
                elif enemy["charge_state"] == "scream":
                    if enemy["charge_timer"] >= CHARGER_SCREAM_DELAY:
                        enemy["charge_state"] = "charge"
                        enemy["charge_timer"] = 0
                else:
                    current = pygame.math.Vector2(enemy["pos"][0], enemy["pos"][1])
                    target = pygame.math.Vector2(enemy["charge_target"][0], enemy["charge_target"][1])
                    distance = current.distance_to(target)
                    if distance > 1:
                        lerp_factor = min(1.0, (speed * 5) / distance)
                        current = current.lerp(target, lerp_factor)
                        enemy["pos"][0], enemy["pos"][1] = current.x, current.y
                    else:
                        enemy["charge_state"] = "idle"
                        enemy["charge_timer"] = 0
            elif enemy["type"] == "zigzagger":
                dir_sign = 1 if enemy["pos"][0] < game["player_pos"][0] else -1
                enemy["baseline_y"] += (game["player_pos"][1] - enemy["baseline_y"]) * 0.02
                enemy["zig_x"] += speed * dir_sign
                enemy["pos"][0] += speed * dir_sign
                enemy["pos"][1] = enemy["baseline_y"] + math.sin(enemy["zig_x"] * enemy["frequency"]) * enemy["amplitude"]
            else:
                if enemy["pos"][0] < game["player_pos"][0]:
                    enemy["pos"][0] += speed
                if enemy["pos"][0] > game["player_pos"][0]:
                    enemy["pos"][0] -= speed
                if enemy["pos"][1] < game["player_pos"][1]:
                    enemy["pos"][1] += speed
                if enemy["pos"][1] > game["player_pos"][1]:
                    enemy["pos"][1] -= speed

            apply_barrier_push(game, enemy)
            hitbox = 50 if "boss_entity" in enemy else 30
            if abs(enemy["pos"][0] - game["player_pos"][0]) < hitbox and abs(enemy["pos"][1] - game["player_pos"][1]) < hitbox:
                game["enemies"].remove(enemy)
                take_player_hit(game)
                on_enemy_death(game, enemy, give_score=False)
                if game["player_lives"] <= 0:
                    game["game_over"] = True

        # mines explode on contact
        for mine in game["mines"][:]:
            exploded = False
            for enemy in game["enemies"][:]:
                if math.hypot(enemy["pos"][0] - mine.pos[0], enemy["pos"][1] - mine.pos[1]) < 28:
                    exploded = True
                    break
            if exploded:
                for enemy in game["enemies"][:]:
                    if math.hypot(enemy["pos"][0] - mine.pos[0], enemy["pos"][1] - mine.pos[1]) <= mine.radius:
                        enemy["hp"] -= mine.damage
                        if enemy["hp"] <= 0 and enemy in game["enemies"]:
                            game["enemies"].remove(enemy)
                            on_enemy_death(game, enemy)
                game["mines"].remove(mine)

        # bullets
        damage = 2 if game["active_powerups"]["double_damage"] > 0 else 1
        for bullet in game["bullets"][:]:
            bullet_pos = pygame.math.Vector2(bullet[0], bullet[1])
            bullet_vel = pygame.math.Vector2(bullet[2], bullet[3])
            for magnet in [enemy for enemy in game["enemies"] if enemy["type"] == "magnet"]:
                magnet_vec = pygame.math.Vector2(magnet["pos"][0], magnet["pos"][1])
                dist_to_magnet = bullet_pos.distance_to(magnet_vec)
                if dist_to_magnet <= MAGNET_RADIUS:
                    pull_dir = (magnet_vec - bullet_pos)
                    if pull_dir.length() > 0:
                        bullet_vel = bullet_vel.lerp(pull_dir.normalize(), 0.06)
            for black_hole in game["black_holes"]:
                hole_vec = pygame.math.Vector2(black_hole["pos"][0], black_hole["pos"][1])
                dist_to_hole = bullet_pos.distance_to(hole_vec)
                if dist_to_hole <= black_hole["radius"]:
                    pull_dir = hole_vec - bullet_pos
                    if pull_dir.length() > 0:
                        bullet_vel = bullet_vel.lerp(pull_dir.normalize(), 0.08)
            for smasher_field in game["smasher_fields"]:
                field_vec = pygame.math.Vector2(smasher_field["pos"][0], smasher_field["pos"][1])
                dist_to_field = bullet_pos.distance_to(field_vec)
                if dist_to_field <= smasher_field["radius"]:
                    pull_dir = field_vec - bullet_pos
                    if pull_dir.length() > 0:
                        bullet_vel = bullet_vel.lerp(pull_dir.normalize(), 0.08)
            bullet[2], bullet[3] = bullet_vel.x, bullet_vel.y
            bullet[0] += bullet[2] * 10 * frame_speed_mult
            bullet[1] += bullet[3] * 10 * frame_speed_mult

            if not (0 <= bullet[0] <= WIDTH and 0 <= bullet[1] <= HEIGHT):
                game["bullets"].remove(bullet)
                continue

            bullet_rect = pygame.Rect(int(bullet[0]) - 4, int(bullet[1]) - 4, 8, 8)

            wall_hit = False
            for wall in game["walls"]:
                if wall.rect.colliderect(bullet_rect):
                    if bullet in game["bullets"]:
                        game["bullets"].remove(bullet)
                    wall_hit = True
                    break
            if wall_hit:
                continue

            barrel_hit = False
            for barrel in game["barrels"][:]:
                if barrel.rect.colliderect(bullet_rect):
                    if bullet in game["bullets"]:
                        game["bullets"].remove(bullet)
                    for enemy in game["enemies"][:]:
                        if enemy["type"] == "boss":
                            continue
                        if math.hypot(enemy["pos"][0] - barrel.pos[0], enemy["pos"][1] - barrel.pos[1]) <= barrel.radius:
                            game["enemies"].remove(enemy)
                            on_enemy_death(game, enemy)
                    game["barrels"].remove(barrel)
                    barrel_hit = True
                    break
            if barrel_hit:
                continue

            collected_powerup = False
            for powerup in game["powerups"][:]:
                if powerup.get_rect().colliderect(bullet_rect):
                    activate_powerup(game, powerup.type)
                    game["powerups"].remove(powerup)
                    if bullet in game["bullets"]:
                        game["bullets"].remove(bullet)
                    collected_powerup = True
                    break
            if collected_powerup:
                continue

            collected_coin = False
            for coin in game["coins"][:]:
                if coin.get_rect().colliderect(bullet_rect):
                    game["coin_count"] += 1
                    game["coins"].remove(coin)
                    if bullet in game["bullets"]:
                        game["bullets"].remove(bullet)
                    collected_coin = True
                    break
            if collected_coin:
                continue

            for enemy in game["enemies"][:]:
                hitbox = 50 if "boss_entity" in enemy else 25
                if abs(enemy["pos"][0] - bullet[0]) < hitbox and abs(enemy["pos"][1] - bullet[1]) < hitbox:
                    if enemy.get("reflect_shield", False):
                        bullet[2] *= -1
                        bullet[3] *= -1
                        bullet[0] += bullet[2] * 12
                        bullet[1] += bullet[3] * 12
                    elif enemy["type"] == "shielder" and enemy.get("shield_health", 0) > 0:
                        enemy["shield_health"] = max(0, enemy["shield_health"] - damage)
                    else:
                        enemy["hp"] -= damage
                        freeze_level = game["upgrades"]["freeze"]
                        if freeze_level > 0 and random.random() < min(0.2 * freeze_level, 0.8):
                            enemy["slow_timer"] = FREEZE_DURATION

                    if bullet in game["bullets"] and not enemy.get("reflect_shield", False):
                        if bullet[4] > 0:
                            bullet[4] -= 1
                        else:
                            game["bullets"].remove(bullet)
                    if enemy["hp"] <= 0:
                        game["enemies"].remove(enemy)
                        on_enemy_death(game, enemy)
                    break

        # draw walls
        for wall in game["walls"]:
            wall.draw(screen)

        for black_hole in game["black_holes"]:
            pygame.draw.circle(screen, BLACK, (int(black_hole["pos"][0]), int(black_hole["pos"][1])), black_hole["radius"], 1)
            pygame.draw.circle(screen, DARK_BLUE, (int(black_hole["pos"][0]), int(black_hole["pos"][1])), 12)

        for smasher_field in game["smasher_fields"]:
            pygame.draw.circle(screen, DARK_BLUE, (int(smasher_field["pos"][0]), int(smasher_field["pos"][1])), smasher_field["radius"], 1)

        # draw barrels
        for barrel in game["barrels"]:
            barrel.draw(screen)

        # draw powerups
        for powerup in game["powerups"]:
            powerup.draw(screen, small_font)

        # draw coins
        for coin in game["coins"]:
            coin.draw(screen, small_font)

        # draw mines
        for mine in game["mines"]:
            mine.draw(screen)

        draw_enemy_legend()

        if game["shockwave_active"]:
            pygame.draw.circle(
                screen,
                DARK_BLUE,
                (int(game["shockwave_center"][0]), int(game["shockwave_center"][1])),
                int(game["shockwave_radius"]),
                2
            )

        # draw player
        px, py = game["player_pos"]
        screen.blit(face_img, (px - 30, py - 65))
        pygame.draw.line(screen, BLACK, (px, py), (px, py + 45), 4)
        pygame.draw.line(screen, BLACK, (px, py + 45), (px - 20, py + 75), 4)
        pygame.draw.line(screen, BLACK, (px, py + 45), (px + 20, py + 75), 4)
        screen.blit(gun_img, gun_rect)

        if game["barrier_active"]:
            pygame.draw.circle(screen, CYAN, (int(px), int(py)), BARRIER_RADIUS, 3)
            pygame.draw.circle(screen, WHITE, (int(px), int(py)), BARRIER_RADIUS + 4, 1)

        # draw enemies
        for protector in [enemy for enemy in game["enemies"] if enemy["type"] == "protector"]:
            for target_enemy in protector.get("protected_targets", []):
                pygame.draw.line(
                    screen,
                    GOLD,
                    (int(protector["pos"][0]), int(protector["pos"][1])),
                    (int(target_enemy["pos"][0]), int(target_enemy["pos"][1])),
                    2
                )

        for enemy in game["enemies"]:
            ex, ey = enemy["pos"]

            if "boss_entity" in enemy:
                screen.blit(boss_img, (ex - 50, ey - 50))

                hp_ratio = enemy["hp"] / enemy["max_hp"]

                pygame.draw.rect(screen, (200, 0, 0), (ex - 50, ey - 70, 100, 8))
                pygame.draw.rect(screen, (0, 200, 0), (ex - 50, ey - 70, 100 * hp_ratio, 8))

            else:
                if enemy["type"] == "mini":
                    mini_rect = pygame.transform.scale(enemy_img, (24, 24))
                    screen.blit(mini_rect, (ex - 12, ey - 12))
                else:
                    screen.blit(enemy_img, (ex - 20, ey - 20))

                hp_ratio = enemy["hp"] / enemy["max_hp"]
                bar_width = 40
                bar_height = 5

                pygame.draw.rect(screen, (200, 0, 0),
                    (ex - bar_width // 2, ey - 30, bar_width, bar_height))

                pygame.draw.rect(screen, (0, 200, 0),
                    (ex - bar_width // 2, ey - 30, bar_width * hp_ratio, bar_height))

                if enemy["type"] == "shielder" and enemy.get("shield_health", 0) > 0:
                    pygame.draw.circle(screen, BLUE, (int(ex), int(ey)), 28, 3)
                if enemy.get("shield_source", False):
                    pygame.draw.circle(screen, WHITE, (int(ex), int(ey)), 24, 1)
            if enemy.get("reflect_shield", False):
                pygame.draw.circle(screen, CYAN, (int(ex), int(ey)), 30, 2)

            if enemy.get("is_miniboss", False):
                pygame.draw.polygon(screen, enemy["color_dot"], [
                    (int(ex), int(ey - 36)),
                    (int(ex - 6), int(ey - 24)),
                    (int(ex + 6), int(ey - 24))
                ])
                pygame.draw.polygon(screen, BLACK, [
                    (int(ex), int(ey - 36)),
                    (int(ex - 6), int(ey - 24)),
                    (int(ex + 6), int(ey - 24))
                ], 1)
            elif enemy.get("color_dot") and "boss_entity" not in enemy:
                pygame.draw.circle(screen, enemy["color_dot"], (int(ex), int(ey - 28)), 5)
                pygame.draw.circle(screen, BLACK, (int(ex), int(ey - 28)), 5, 1)

            if enemy["type"] == "charger" and enemy.get("charge_state") == "scream":
                rush_text = small_font.render("!!!RUSHING!!!", True, RED)
                screen.blit(rush_text, (int(ex) - rush_text.get_width() // 2, int(ey) - 55))

        for bullet in game["bullets"]:
            pygame.draw.circle(screen, BLACK, (int(bullet[0]), int(bullet[1])), 8)

        for i in range(game["player_lives"]):
            screen.blit(life_img, (10 + i * 35, 10))

        score_text = font.render(f"Score: {game['score']}", True, BLACK)
        coins_text = font.render(f"Coins: {game['coin_count']}", True, BLACK)
        mines_text = font.render(f"Mines: {game['mine_count']}", True, BLACK)
        auto_text = font.render(f"Auto: {game['auto_mode']}", True, BLACK)
        ff_text = font.render(f"Fast: {game['fast_forward']}", True, BLACK)
        multi_text = small_font.render(
            f"1 Multishot L{game['upgrades']['multishot']} C{get_upgrade_cost(game['upgrades']['multishot'])}",
            True, BLACK
        )
        pierce_text = small_font.render(
            f"2 Piercing L{game['upgrades']['piercing']} C{get_upgrade_cost(game['upgrades']['piercing'])}",
            True, BLACK
        )
        freeze_text = small_font.render(
            f"3 Freeze L{game['upgrades']['freeze']} C{get_upgrade_cost(game['upgrades']['freeze'])}",
            True, BLACK
        )
        shock_text = small_font.render(f"Shockwave: {game['shockwave_timer'] / 1000:.1f}s", True, BLACK)
        if game["barrier_cooldown"] == 0:
            barrier_text = small_font.render("Barrier: READY", True, BLACK)
        else:
            barrier_text = small_font.render(f"Barrier: {game['barrier_cooldown'] / 1000:.1f}s", True, BLACK)
        if game["inverter_active"]:
            inverter_text = small_font.render(f"INVERTED: {game['inverter_timer'] / 1000:.1f}s", True, RED)
        else:
            inverter_text = None

        screen.blit(score_text, (10, 50))
        screen.blit(coins_text, (10, 80))
        screen.blit(mines_text, (10, 110))
        screen.blit(auto_text, (10, 140))
        screen.blit(ff_text, (10, 170))
        screen.blit(shock_text, (10, 200))
        screen.blit(barrier_text, (10, 225))
        if inverter_text:
            screen.blit(inverter_text, (10, 250))
        screen.blit(multi_text, (10, HEIGHT - 80))
        screen.blit(pierce_text, (10, HEIGHT - 55))
        screen.blit(freeze_text, (10, HEIGHT - 30))
        draw_active_powerups(game)

        if game["inverter_active"]:
            inverter_tint = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            inverter_tint.fill((255, 60, 60, 35))
            screen.blit(inverter_tint, (0, 0))

        for overlay in game["smasher_overlays"]:
            overlay_surface = pygame.Surface((overlay["rect"].width, overlay["rect"].height), pygame.SRCALPHA)
            overlay_surface.fill((200, 200, 200, 90))
            for _ in range(40):
                line_y = random.randint(0, overlay["rect"].height - 1)
                pygame.draw.line(
                    overlay_surface,
                    (80, 80, 80, 120),
                    (0, line_y),
                    (overlay["rect"].width, line_y),
                    1
                )
            screen.blit(overlay_surface, overlay["rect"].topleft)

        pygame.display.flip()

    stats["games_played"] += 1
    stats["high_score"] = max(stats["high_score"], game["score"])
    save_stats(stats)

pygame.quit()
