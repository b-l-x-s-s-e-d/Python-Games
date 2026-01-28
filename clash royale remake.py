"""
Clash Royale 1:1 Python Remake (Educational)

Single-file, runnable prototype that operationalizes the prior master plan.
Constraints honored:
- Python 3.12+
- Pygame rendering + pygame.mixer hooks
- Deterministic 20 TPS simulation with 60 FPS rendering
- Data-first card definitions (inline JSON for this single-file constraint)

This is a minimal playable prototype that demonstrates:
- Arena rendering (two lanes + river + bridges)
- Placeholder towers for each side
- One troop card with elixir ticking
- Deterministic fixed-step sim loop
- Validated placement and server-authoritative logic (single-process for now)

Controls
- Left click to place a troop on your side (bottom half)
- Esc or window close to exit
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import pygame

# ==========================
# Constants and Configuration
# ==========================
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 1200
FPS = 60
TPS = 20
DT_TICK = 1.0 / TPS

GRID_WIDTH = 18
GRID_HEIGHT = 32
TILE_SIZE = SCREEN_WIDTH // GRID_WIDTH

RIVER_ROW = GRID_HEIGHT // 2
BRIDGE_COLUMNS = (GRID_WIDTH // 3, GRID_WIDTH * 2 // 3)

MAX_ELIXIR = 10
START_ELIXIR = 5
ELIXIR_SECONDS_PER_POINT = 2.8
ELIXIR_TICKS_PER_POINT = int(round(ELIXIR_SECONDS_PER_POINT * TPS))

PLAYER_TEAM = 1
ENEMY_TEAM = 2

# ==========================
# Data-Driven Card Definitions (placeholder values)
# ==========================
CARD_DEFS_JSON = """
{
  "cards": [
    {
      "id": "melee_knight_placeholder",
      "name": "Knight (Placeholder)",
      "rarity": "common",
      "type": "troop",
      "elixir_cost": 3,
      "deploy_time_ticks": 20,
      "stats": {
        "hp": 1000,
        "damage": 120,
        "hit_speed_ticks": 30,
        "move_speed": "medium",
        "range": 1.0,
        "target_type": "ground",
        "splash": false,
        "splash_radius": 0.0,
        "mass": 4,
        "projectile": null
      },
      "abilities": [],
      "crown_tower_damage_scalar": 1.0,
      "level_scaling": {"hp_per_level": 70, "damage_per_level": 8}
    }
  ]
}
"""

CARD_DEFS = json.loads(CARD_DEFS_JSON)["cards"]

# ==========================
# Utility Functions
# ==========================

def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def grid_to_world(tile: Tuple[int, int]) -> Tuple[int, int]:
    x, y = tile
    return (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)


def world_to_grid(pos: Tuple[int, int]) -> Tuple[int, int]:
    x, y = pos
    return (x // TILE_SIZE, y // TILE_SIZE)


def manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ==========================
# Pathfinding (A*)
# ==========================

def astar(grid: List[List[int]], start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    open_set: List[Tuple[int, Tuple[int, int]]] = [(0, start)]
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
    g_score: Dict[Tuple[int, int], int] = {start: 0}

    while open_set:
        open_set.sort(key=lambda x: x[0])
        _, current = open_set.pop(0)
        if current == goal:
            break

        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (current[0] + dx, current[1] + dy)
            if not (0 <= nxt[0] < GRID_WIDTH and 0 <= nxt[1] < GRID_HEIGHT):
                continue
            if grid[nxt[1]][nxt[0]] == 1:
                continue
            ng = g_score[current] + 1
            if ng < g_score.get(nxt, 10**9):
                g_score[nxt] = ng
                f = ng + manhattan(nxt, goal)
                open_set.append((f, nxt))
                came_from[nxt] = current

    if goal not in came_from and goal != start:
        return [start]

    path = [goal]
    while path[-1] != start:
        path.append(came_from[path[-1]])
    path.reverse()
    return path


# ==========================
# Core Entity Models
# ==========================

@dataclass
class Entity:
    entity_id: int
    team: int
    x: float
    y: float
    hp: int
    radius: float

    def pos(self) -> Tuple[float, float]:
        return (self.x, self.y)


@dataclass
class Troop(Entity):
    damage: int
    hit_speed_ticks: int
    range: float
    move_speed: float
    target_id: Optional[int] = None
    attack_cooldown: int = 0
    path: List[Tuple[int, int]] = field(default_factory=list)


@dataclass
class Tower(Entity):
    damage: int
    hit_speed_ticks: int
    range: float
    attack_cooldown: int = 0


# ==========================
# Simulation Layer (Authoritative)
# ==========================

class Sim:
    def __init__(self, seed: int = 12345) -> None:
        self.rng = random.Random(seed)
        self.tick_count = 0
        self.entities: Dict[int, Entity] = {}
        self.next_entity_id = 1
        self.elixir = {PLAYER_TEAM: START_ELIXIR, ENEMY_TEAM: START_ELIXIR}
        self.elixir_tick_counter = 0
        self.grid = self._build_grid()
        self._spawn_towers()

    def _build_grid(self) -> List[List[int]]:
        grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        for x in range(GRID_WIDTH):
            grid[RIVER_ROW][x] = 1
        for bx in BRIDGE_COLUMNS:
            grid[RIVER_ROW][bx] = 0
        return grid

    def _spawn_towers(self) -> None:
        # Princess towers
        princess_offsets = [(-4, -8), (4, -8)]
        for dx, dy in princess_offsets:
            x = GRID_WIDTH // 2 + dx
            y = GRID_HEIGHT - 6 + dy
            self._add_tower(PLAYER_TEAM, x, y)
        for dx, dy in princess_offsets:
            x = GRID_WIDTH // 2 + dx
            y = 5 + dy
            self._add_tower(ENEMY_TEAM, x, y)
        # King towers
        self._add_tower(PLAYER_TEAM, GRID_WIDTH // 2, GRID_HEIGHT - 3, king=True)
        self._add_tower(ENEMY_TEAM, GRID_WIDTH // 2, 2, king=True)

    def _add_tower(self, team: int, gx: int, gy: int, king: bool = False) -> None:
        x, y = grid_to_world((gx, gy))
        tower = Tower(
            entity_id=self._next_id(),
            team=team,
            x=float(x),
            y=float(y),
            hp=1600 if king else 1200,
            radius=28.0,
            damage=90 if king else 70,
            hit_speed_ticks=40,
            range=180.0,
        )
        self.entities[tower.entity_id] = tower

    def _next_id(self) -> int:
        eid = self.next_entity_id
        self.next_entity_id += 1
        return eid

    def can_place(self, team: int, gx: int, gy: int, elixir_cost: int) -> bool:
        if team == PLAYER_TEAM and gy <= RIVER_ROW:
            return False
        if team == ENEMY_TEAM and gy >= RIVER_ROW:
            return False
        if self.grid[gy][gx] == 1:
            return False
        if self.elixir[team] < elixir_cost:
            return False
        return True

    def place_troop(self, team: int, gx: int, gy: int, card_def: Dict[str, object]) -> bool:
        if not self.can_place(team, gx, gy, int(card_def["elixir_cost"])):
            return False
        x, y = grid_to_world((gx, gy))
        stats = card_def["stats"]
        troop = Troop(
            entity_id=self._next_id(),
            team=team,
            x=float(x),
            y=float(y),
            hp=int(stats["hp"]),
            radius=18.0,
            damage=int(stats["damage"]),
            hit_speed_ticks=int(stats["hit_speed_ticks"]),
            range=float(stats["range"]) * TILE_SIZE,
            move_speed=60.0,
        )
        self.entities[troop.entity_id] = troop
        self.elixir[team] -= int(card_def["elixir_cost"])
        return True

    def tick(self) -> None:
        # Elixir
        self.elixir_tick_counter += 1
        if self.elixir_tick_counter >= ELIXIR_TICKS_PER_POINT:
            self.elixir_tick_counter = 0
            for team in (PLAYER_TEAM, ENEMY_TEAM):
                self.elixir[team] = clamp(self.elixir[team] + 1, 0, MAX_ELIXIR)

        # Update entities
        entity_list = list(self.entities.values())
        for entity in entity_list:
            if isinstance(entity, Troop):
                self._update_troop(entity)
            if isinstance(entity, Tower):
                self._update_tower(entity)

        # Remove dead
        for eid, ent in list(self.entities.items()):
            if ent.hp <= 0:
                del self.entities[eid]

        self.tick_count += 1

    def _find_target(self, source: Entity, target_team: int, max_range: float) -> Optional[int]:
        best_id = None
        best_dist = float("inf")
        for ent in self.entities.values():
            if ent.team != target_team:
                continue
            dx = ent.x - source.x
            dy = ent.y - source.y
            dist = math.hypot(dx, dy)
            if dist <= max_range and dist < best_dist:
                best_dist = dist
                best_id = ent.entity_id
        return best_id

    def _update_troop(self, troop: Troop) -> None:
        target_team = ENEMY_TEAM if troop.team == PLAYER_TEAM else PLAYER_TEAM
        if troop.target_id not in self.entities:
            troop.target_id = self._find_target(troop, target_team, troop.range + 120)

        if troop.target_id is None:
            return

        target = self.entities[troop.target_id]
        dx = target.x - troop.x
        dy = target.y - troop.y
        dist = math.hypot(dx, dy)

        if dist <= troop.range:
            if troop.attack_cooldown <= 0:
                target.hp -= troop.damage
                troop.attack_cooldown = troop.hit_speed_ticks
            else:
                troop.attack_cooldown -= 1
            return

        # Movement
        if dist > 0:
            step = troop.move_speed * DT_TICK
            troop.x += (dx / dist) * step
            troop.y += (dy / dist) * step

    def _update_tower(self, tower: Tower) -> None:
        target_team = ENEMY_TEAM if tower.team == PLAYER_TEAM else PLAYER_TEAM
        if tower.attack_cooldown > 0:
            tower.attack_cooldown -= 1
            return
        target_id = self._find_target(tower, target_team, tower.range)
        if target_id is None:
            return
        target = self.entities[target_id]
        target.hp -= tower.damage
        tower.attack_cooldown = tower.hit_speed_ticks


# ==========================
# Rendering / UI
# ==========================

class GameRenderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 20)

    def draw_arena(self) -> None:
        self.screen.fill((55, 140, 70))
        river_y = RIVER_ROW * TILE_SIZE
        pygame.draw.rect(self.screen, (40, 80, 160), (0, river_y, SCREEN_WIDTH, TILE_SIZE))
        for bx in BRIDGE_COLUMNS:
            pygame.draw.rect(
                self.screen,
                (120, 80, 40),
                (bx * TILE_SIZE, river_y, TILE_SIZE, TILE_SIZE),
            )

    def draw_entity(self, entity: Entity) -> None:
        color = (40, 120, 240) if entity.team == PLAYER_TEAM else (220, 60, 60)
        pygame.draw.circle(self.screen, color, (int(entity.x), int(entity.y)), int(entity.radius))
        hp_text = self.font.render(str(entity.hp), True, (255, 255, 255))
        self.screen.blit(hp_text, (entity.x - hp_text.get_width() // 2, entity.y - 35))

    def draw_ui(self, sim: Sim) -> None:
        elixir_text = self.font.render(f"Elixir: {sim.elixir[PLAYER_TEAM]:.0f}", True, (255, 255, 255))
        self.screen.blit(elixir_text, (20, SCREEN_HEIGHT - 40))
        tick_text = self.font.render(f"Tick: {sim.tick_count}", True, (255, 255, 255))
        self.screen.blit(tick_text, (20, 20))


# ==========================
# Main Game Loop
# ==========================

def main() -> None:
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Clash Royale Remake Prototype")

    clock = pygame.time.Clock()
    renderer = GameRenderer(screen)
    sim = Sim(seed=12345)

    card_def = CARD_DEFS[0]

    accumulator = 0.0
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        accumulator += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                gx, gy = world_to_grid((mx, my))
                if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                    sim.place_troop(PLAYER_TEAM, gx, gy, card_def)

        # Fixed-step simulation
        while accumulator >= DT_TICK:
            sim.tick()
            accumulator -= DT_TICK

        # Render
        renderer.draw_arena()
        for entity in sim.entities.values():
            renderer.draw_entity(entity)
        renderer.draw_ui(sim)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
