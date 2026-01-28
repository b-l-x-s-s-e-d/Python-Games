"""
CLASH ROYALE 1:1 PYTHON REMAKE — FULL MASTER PROMPT (TXT)

This single file contains the complete architecture plan, protocol spec,
schemas, roadmap, and a runnable skeleton reference (as code blocks) as
requested. It is intentionally data-first, deterministic-first, and
server-authoritative in design. Placeholder values are clearly labeled and
intended to be replaced via data tables without code changes.

NOTE: The deliverables below are organized in the exact required order.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# =====================================================================
# A) ARCHITECTURE
# =====================================================================
ARCHITECTURE = """
A) ARCHITECTURE

Component Diagram (textual)

[Client]
  - client.main
  - ui.basic_ui
  - network.client_ws
  - engine.sim (shared)
  - engine.entities
  - engine.pathfinding
  - assets/audio

[Server]
  - server.main
  - network.server_ws
  - engine.sim (shared)
  - engine.entities
  - engine.pathfinding
  - progression (profiles, chests, shop)

[Shared]
  - engine.sim (deterministic tick loop)
  - engine.entities (entity model, combat)
  - engine.pathfinding (A* grid)
  - cards.card_defs.json (data-driven stats)
  - arenas/*.json (tile grids, spawn points)
  - replays (input logs + checksums)

Responsibilities
- engine.sim: authoritative fixed-timestep simulation at 20 TPS. Processes input,
  validates, updates entities, resolves combat, produces state snapshots.
- engine.entities: Entity/Troop/Building/Spell/Tower/Projectile/StatusEffect
  definitions + combat rules (data-driven).
- engine.pathfinding: A* grid pathing, dynamic obstacle updates, bridge nodes.
- network.*: WebSocket protocol handling; client inputs, server snapshots.
- ui.basic_ui: HUD (elixir, hand, timer) + debug overlays.
- progression: trophies, arenas, cards, shop, chests, JSON persistence.
- replay: deterministic input recording + checksum verification.

Core Data Models
- Entity: id, team, position, hp, radius, state flags.
- Troop(Entity): move_speed, attack, target_type, range, hit_speed, status effects.
- Building(Entity): lifetime, pull logic, spawn interval.
- Spell: radius, damage, duration, crown scalar, deploy timing.
- Tower(Entity): type (king/princess), activation, targeting priority.
- StatusEffect: type, duration_ticks, magnitude, stacking rules.
- MatchState: tick, arena_id, entities, players, timer, overtime state.
- PlayerState: elixir, hand, deck, crowns, input queue.

Update Order per Tick (exact sequence)
1. Ingest Inputs (server authoritative)
2. Validate Inputs (placement, elixir, rate limits)
3. Apply Inputs (spawn entities, consume elixir)
4. Update Status Effects (ticks, expire, modify stats)
5. Update Movement (pathing, positions)
6. Update Targeting (acquire/retarget)
7. Update Combat (attack cooldowns, spawn projectiles)
8. Update Projectiles (travel, collision, apply damage)
9. Resolve Deaths (remove entities, trigger hooks)
10. Update Timers (elixir regen, overtime, match end)
11. Emit Snapshot/Delta + Determinism Checksum
"""

# =====================================================================
# B) PROTOCOL SPEC (WebSockets chosen)
# =====================================================================
PROTOCOL_SPEC = """
B) PROTOCOL SPEC

Chosen networking: WebSockets
Justification: reliable ordered delivery is critical for authoritative inputs,
replay logging, and deterministic reconciliation. WebSockets are simpler for
local dev and cross-platform clients, with acceptable latency. UDP can be added
later for production with a reliability layer.

Client -> Server Messages
1) hello
  fields: client_version, player_id, auth_token, region, latency_hint_ms
2) queue_match
  fields: deck_id, preferred_region, timestamp_ms
3) input_place_card
  fields: match_id, tick, card_id, x, y, side, client_seq
  validation: tick within input buffer window, tile legal, elixir>=cost
4) input_emote
  fields: match_id, tick, emote_id, client_seq
5) ping
  fields: client_time_ms, seq
6) request_replay
  fields: match_id
7) ack_snapshot
  fields: match_id, snapshot_seq, last_input_seq

Server -> Client Messages
1) hello_ack
  fields: server_version, motd, time_ms
2) match_found
  fields: match_id, opponent_id, arena_id, seed, start_tick
3) state_snapshot
  fields: match_id, snapshot_seq, tick, entities, players, timers, checksum
4) state_delta
  fields: match_id, snapshot_seq, tick, delta, checksum
5) input_reject
  fields: match_id, client_seq, reason
6) match_end
  fields: match_id, result, crowns, rewards
7) pong
  fields: client_time_ms, server_time_ms, seq
8) replay_data
  fields: match_id, seed, input_log, checksum_log

Sequencing & Acking
- Client includes monotonically increasing client_seq on inputs.
- Server includes snapshot_seq on snapshots; client acked with last_input_seq.
- Reconciliation uses last acknowledged input; client corrects visual drift.

Timing
- Server tick: 20 TPS fixed.
- Client render: 60 FPS; snapshots at 20 TPS, interpolated.

Rate Limits
- Placement: max 8 inputs per second (burst 2), server-enforced.
- Emotes: 1 per 2 seconds.

Validation Rules
- Tile legality, side bounds, elixir availability, cooldowns, timing window.
- Sanity checks: coordinates within arena bounds.
"""

# =====================================================================
# C) DATA SCHEMAS (data-first, placeholders)
# =====================================================================
DATA_SCHEMAS = """
C) DATA SCHEMAS (JSON schema style, placeholders)

cards/card_defs.json schema (example)
{
  "cards": [
    {
      "id": "string",
      "name": "string",
      "rarity": "common|rare|epic|legendary|champion",
      "type": "troop|building|spell",
      "elixir_cost": "int",
      "deploy_time_ticks": "int",
      "stats": {
        "hp": "int",
        "damage": "int",
        "hit_speed_ticks": "int",
        "move_speed": "slow|medium|fast",
        "range": "float",
        "target_type": "ground|air|both",
        "splash": "bool",
        "splash_radius": "float",
        "mass": "int",
        "projectile": {
          "speed": "float",
          "radius": "float",
          "travel_time_ticks": "int"
        }
      },
      "abilities": ["string"],
      "crown_tower_damage_scalar": "float",
      "level_scaling": {
        "hp_per_level": "int",
        "damage_per_level": "int"
      }
    }
  ]
}

arenas/arena_defs.json schema (example)
{
  "arenas": [
    {
      "id": "string",
      "name": "string",
      "grid_width": "int",
      "grid_height": "int",
      "river_rows": ["int"],
      "bridge_tiles": [["int","int"]],
      "spawn_points": {
        "team1": [["int","int"]],
        "team2": [["int","int"]]
      },
      "tower_positions": {
        "team1": {
          "king": ["int","int"],
          "princess": [["int","int"],["int","int"]]
        },
        "team2": {
          "king": ["int","int"],
          "princess": [["int","int"],["int","int"]]
        }
      }
    }
  ]
}

progression config schema
{
  "arenas": [{"id": "string", "trophies_min": "int"}],
  "chests": [{"id": "string", "rarity": "string", "drop_table": "string"}],
  "shop": [{"id": "string", "offer_type": "string", "price": "int"}]
}

Drop tables schema
{
  "drop_tables": [
    {
      "id": "string",
      "entries": [
        {"item_id": "string", "weight": "int", "min": "int", "max": "int"}
      ]
    }
  ]
}

Example entries (placeholder values)
- Melee troop (Knight-like)
- Ranged troop (Archer-like)
- Building puller (Cannon-like)
- Spell (Fireball-like)
"""

# =====================================================================
# D) ROADMAP + MILESTONES
# =====================================================================
ROADMAP = """
D) ROADMAP + MILESTONES

Milestone 0: Repo setup + runnable window + deterministic tick loop
- Acceptance: window opens; deterministic tick increments at 20 TPS; checksum log
- QA: tick drift check; headless sim test
- Perf: 0.5 ms/tick sim budget

Milestone 1: server-client handshake + arena render + towers
- Acceptance: server hosts match; client connects; arena + towers rendered
- QA: reconnect test; snapshot integrity
- Perf: 1 ms/tick sim, 16 ms/frame render

Milestone 2: elixir + hand + deploy 1 troop (authoritative)
- Acceptance: elixir regenerates; card placement validated; troop spawns
- QA: invalid placement rejected; elixir not spent on invalid
- Perf: 2 ms/tick with 10 entities

Milestone 3: targeting + pathfinding + combat + projectiles
- Acceptance: troop pathing via A*; projectiles hit; towers attack
- QA: targeting rules; projectile timing; deterministic hashes
- Perf: 3 ms/tick with 50 entities

Milestone 4: spells + status effects
- Acceptance: spell damage, radius, effects; status durations in ticks
- QA: stacking/refresh rules; freeze/slow/stun
- Perf: 3.5 ms/tick

Milestone 5: full card framework + more cards
- Acceptance: multiple card types; data-driven stats
- QA: unit test each card type
- Perf: 4 ms/tick at 100 entities

Milestone 6: matchmaking + bots + results screen
- Acceptance: trophy-based matching; bot fallback; results UI
- QA: bot uses input rules; fairness checks
- Perf: 4 ms/tick; 16 ms render

Milestone 7: progression + chests + shop + save system
- Acceptance: persistence, chest timers, shop rotation
- QA: data migration; encryption at rest
- Perf: <10 ms save/load

Milestone 8: replays + spectator + anti-cheat hardening
- Acceptance: replay resim matches checksum; spectator view
- QA: input sanity; replay verify
- Perf: replay sim 2x realtime

Milestone 9: polish (UI, audio, animation hooks), perf, QA suite
- Acceptance: audio hooks, animation timeline, debug overlays
- QA: full regression suite
- Perf: stable 60 FPS, <5 ms tick
"""

# =====================================================================
# E) MINIMUM WORKING SKELETON CODE (as code blocks)
# =====================================================================
SKELETON_CODE = r"""
E) MINIMUM WORKING SKELETON CODE

/server/main.py
```python
import asyncio
import json
import websockets
from engine.sim import Sim

TICK_RATE = 20
TICK_DT = 1 / TICK_RATE

async def handler(ws):
    sim = Sim(seed=12345)
    await ws.send(json.dumps({"type": "hello_ack"}))
    while True:
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=TICK_DT)
            sim.enqueue_input(json.loads(msg))
        except asyncio.TimeoutError:
            pass
        sim.tick()
        snapshot = sim.snapshot()
        await ws.send(json.dumps({"type": "state_snapshot", "data": snapshot}))

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
```

/client/main.py
```python
import asyncio
import json
import pygame
import websockets
from ui.basic_ui import BasicUI

async def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    ui = BasicUI()
    async with websockets.connect("ws://localhost:8765") as ws:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if pygame.time.get_ticks() % 50 == 0:
                await ws.send(json.dumps({"type": "input_place_card", "x": 10, "y": 10}))
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=0.01)
                data = json.loads(msg)
                ui.update_from_snapshot(data)
            except asyncio.TimeoutError:
                pass
            screen.fill((20, 120, 20))
            ui.draw(screen)
            pygame.display.flip()

if __name__ == "__main__":
    asyncio.run(main())
```

/engine/sim.py
```python
from engine.entities import Entity, Troop

class Sim:
    def __init__(self, seed=0):
        self.tick_count = 0
        self.entities = []
        self.input_queue = []
        self.seed = seed

    def enqueue_input(self, msg):
        self.input_queue.append(msg)

    def tick(self):
        # process inputs
        for msg in self.input_queue:
            if msg.get("type") == "input_place_card":
                self.entities.append(Troop(x=msg["x"], y=msg["y"], team=1))
        self.input_queue.clear()
        # update entities
        for e in self.entities:
            e.update()
        self.tick_count += 1

    def snapshot(self):
        return {
            "tick": self.tick_count,
            "entities": [e.to_dict() for e in self.entities],
        }
```

/engine/entities.py
```python
class Entity:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100

    def update(self):
        pass

    def to_dict(self):
        return {"x": self.x, "y": self.y, "team": self.team, "hp": self.hp}

class Troop(Entity):
    def update(self):
        self.x += 0.1
```

/engine/pathfinding.py
```python
import heapq

def astar(grid, start, goal):
    def h(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    open_set = [(0, start)]
    came_from = {}
    g = {start: 0}
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            break
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nxt = (current[0]+dx, current[1]+dy)
            if nxt not in grid:
                continue
            ng = g[current] + 1
            if ng < g.get(nxt, 1e9):
                g[nxt] = ng
                f = ng + h(nxt, goal)
                heapq.heappush(open_set, (f, nxt))
                came_from[nxt] = current
    return came_from
```

/ui/basic_ui.py
```python
import pygame

class BasicUI:
    def __init__(self):
        self.elixir = 5
        self.cards = ["card1", "card2", "card3", "card4"]
        self.snapshot = {}

    def update_from_snapshot(self, data):
        self.snapshot = data

    def draw(self, screen):
        pygame.draw.rect(screen, (120, 0, 180), (50, 550, 200, 30))
```

/cards/card_defs.json
```json
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
    },
    {
      "id": "ranged_archer_placeholder",
      "name": "Archer (Placeholder)",
      "rarity": "common",
      "type": "troop",
      "elixir_cost": 3,
      "deploy_time_ticks": 20,
      "stats": {
        "hp": 300,
        "damage": 90,
        "hit_speed_ticks": 30,
        "move_speed": "medium",
        "range": 5.0,
        "target_type": "both",
        "splash": false,
        "splash_radius": 0.0,
        "mass": 1,
        "projectile": {"speed": 6.0, "radius": 0.1, "travel_time_ticks": 10}
      },
      "abilities": [],
      "crown_tower_damage_scalar": 1.0,
      "level_scaling": {"hp_per_level": 20, "damage_per_level": 6}
    },
    {
      "id": "building_cannon_placeholder",
      "name": "Cannon (Placeholder)",
      "rarity": "common",
      "type": "building",
      "elixir_cost": 3,
      "deploy_time_ticks": 20,
      "stats": {
        "hp": 1500,
        "damage": 180,
        "hit_speed_ticks": 30,
        "move_speed": "none",
        "range": 5.5,
        "target_type": "ground",
        "splash": false,
        "splash_radius": 0.0,
        "mass": 5,
        "projectile": {"speed": 7.0, "radius": 0.1, "travel_time_ticks": 10}
      },
      "abilities": ["pull"],
      "crown_tower_damage_scalar": 1.0,
      "level_scaling": {"hp_per_level": 100, "damage_per_level": 12}
    },
    {
      "id": "spell_fireball_placeholder",
      "name": "Fireball (Placeholder)",
      "rarity": "rare",
      "type": "spell",
      "elixir_cost": 4,
      "deploy_time_ticks": 10,
      "stats": {
        "hp": 0,
        "damage": 325,
        "hit_speed_ticks": 0,
        "move_speed": "none",
        "range": 0.0,
        "target_type": "both",
        "splash": true,
        "splash_radius": 2.5,
        "mass": 0,
        "projectile": {"speed": 10.0, "radius": 0.1, "travel_time_ticks": 15}
      },
      "abilities": ["knockback"],
      "crown_tower_damage_scalar": 0.4,
      "level_scaling": {"hp_per_level": 0, "damage_per_level": 20}
    }
  ]
}
```
"""

# =====================================================================
# Additional deterministic strategy / performance / debug tools sections
# =====================================================================
DETERMINISM_STRATEGY = """
Determinism Strategy
- Fixed timestep 20 TPS; store time in ticks only.
- Use integer or fixed-point where possible. If floats used, clamp/round at
  defined precision (e.g., 1/1000 tile units) at each tick.
- Seeded RNG per match; record seed in replay metadata.
- All randomness derived from match seed + tick index.
- Determinism checksums: hash entity states each tick; verify in replays.
- Client prediction strictly visual; server is authoritative.
"""

PERFORMANCE_STRATEGY = """
Performance Strategy
- Object pooling for projectiles, particles, and common troops.
- Spatial partitioning with grid buckets for targeting and collisions.
- Path update throttling and caching; rebuild on obstacle change.
- Pre-allocate arrays/lists where possible; avoid per-tick allocations.
- Profiling hooks and frame budget monitors.
"""

DEBUG_TOOLS_PLAN = """
Debug Tools Plan
- Hitbox overlay
- Path overlay
- Tick step mode (pause + single-step)
- AI visualizer (targets, intent lines, heatmaps)
- Network lag simulator (delay/jitter/loss)
- Determinism checksum viewer per tick
"""

# =====================================================================
# Minimal in-file dataclasses to demonstrate schema intent
# =====================================================================
@dataclass
class StatusEffect:
    effect_type: str
    duration_ticks: int
    magnitude: float
    stacking: str = "refresh"


@dataclass
class Entity:
    entity_id: int
    team: int
    position: Tuple[int, int]
    hp: int
    radius: float
    status_effects: List[StatusEffect] = field(default_factory=list)


@dataclass
class Troop(Entity):
    move_speed: str = "medium"
    damage: int = 0
    hit_speed_ticks: int = 0
    range: float = 0.0
    target_type: str = "ground"


@dataclass
class Building(Entity):
    lifetime_ticks: int = 0
    pull_radius: float = 0.0


@dataclass
class Spell:
    spell_id: str
    radius: float
    damage: int
    crown_tower_damage_scalar: float


@dataclass
class Tower(Entity):
    tower_type: str = "princess"
    activated: bool = False


@dataclass
class PlayerState:
    player_id: str
    elixir: float
    hand: List[str]
    deck: List[str]
    crowns: int = 0


@dataclass
class MatchState:
    match_id: str
    tick: int
    arena_id: str
    players: Dict[str, PlayerState]
    entities: Dict[int, Entity]
    overtime: bool = False


def print_deliverables() -> None:
    """Prints the master plan and skeleton to stdout."""
    print(ARCHITECTURE)
    print(PROTOCOL_SPEC)
    print(DATA_SCHEMAS)
    print(ROADMAP)
    print(SKELETON_CODE)
    print(DETERMINISM_STRATEGY)
    print(PERFORMANCE_STRATEGY)
    print(DEBUG_TOOLS_PLAN)


if __name__ == "__main__":
    # Running this file prints the complete deliverables.
    print_deliverables()
