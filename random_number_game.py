"""Terminal prototype for The Grid, a geolocation-inspired territory MMO.

The real product would consume live GPS and render a 2.5D map. This prototype keeps
those core rules deterministic and playable from the command line so the game loop
can be tested without network or location services.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Iterable
from urllib.parse import parse_qs, urlparse

GRID_SIZE = 7
CAPTURE_XP = 25
DISCOVERY_XP = 5
LEVEL_XP = 100
TEAM_COLORS = {
    "cyan": "Bleu Cyan",
    "violet": "Violet",
    "ember": "Orange Braise",
    "acid": "Vert Acide",
}


class SovereignDuration(Enum):
    """Fixed territory ownership packages for the sovereign mode."""

    DAY = ("1 day", timedelta(days=1))
    WEEK = ("1 week", timedelta(weeks=1))
    MONTH = ("1 month", timedelta(days=30))
    YEAR = ("1 year", timedelta(days=365))

    def __init__(self, label: str, delta: timedelta) -> None:
        self.label = label
        self.delta = delta


@dataclass
class Player:
    """A player walking through the city grid."""

    name: str
    team: str
    avatar: str = "◎"
    x: int = GRID_SIZE // 2
    y: int = GRID_SIZE // 2
    xp: int = 0
    discovered: set[tuple[int, int]] = field(default_factory=set)
    owned_cells: set[tuple[int, int]] = field(default_factory=set)
    trail: list[tuple[int, int]] = field(default_factory=list)

    @property
    def level(self) -> int:
        return self.xp // LEVEL_XP + 1

    @property
    def capture_radius(self) -> int:
        """Capture radius grows with levels to model progression bonuses."""

        return 1 + (self.level - 1) // 3

    @property
    def trail_intensity(self) -> str:
        if self.level >= 7:
            return "legendary neon comet"
        if self.level >= 4:
            return "bright electric ribbon"
        return "soft luminous trail"


@dataclass
class Cell:
    """A 50m x 50m territory tile in The Grid."""

    x: int
    y: int
    team: str | None = None
    captured_by: str | None = None
    sovereign_owner: str | None = None
    sovereign_avatar: str | None = None
    sovereign_until: datetime | None = None

    def is_sovereign(self, now: datetime) -> bool:
        return self.sovereign_until is not None and self.sovereign_until > now

    def sovereign_badge(self, now: datetime) -> str:
        if not self.is_sovereign(now):
            return ""
        return f" 👑 {self.sovereign_owner} {self.sovereign_avatar or ''}".rstrip()


class TheGridGame:
    """Core game rules for walk-to-capture territory play."""

    def __init__(self, size: int = GRID_SIZE) -> None:
        if size < 3:
            raise ValueError("The Grid needs at least a 3x3 city block.")
        self.size = size
        self.cells = {(x, y): Cell(x, y) for y in range(size) for x in range(size)}
        self.player = Player(name="Neon Runner", team="cyan", x=size // 2, y=size // 2)
        self.now = datetime.now(UTC)
        self.discover(self.player.x, self.player.y)
        self.capture_current_position()

    def discover(self, x: int, y: int) -> list[tuple[int, int]]:
        """Reveal nearby cells, replacing fog of war with known city blocks."""

        newly_seen: list[tuple[int, int]] = []
        for nx, ny in self.neighbors_in_radius(x, y, radius=1):
            position = (nx, ny)
            if position not in self.player.discovered:
                self.player.discovered.add(position)
                self.player.xp += DISCOVERY_XP
                newly_seen.append(position)
        return newly_seen

    def neighbors_in_radius(self, x: int, y: int, radius: int) -> Iterable[tuple[int, int]]:
        for ny in range(max(0, y - radius), min(self.size, y + radius + 1)):
            for nx in range(max(0, x - radius), min(self.size, x + radius + 1)):
                yield nx, ny

    def move(self, direction: str) -> str:
        """Move the avatar one block and apply discovery and capture effects."""

        offsets = {
            "north": (0, -1),
            "n": (0, -1),
            "south": (0, 1),
            "s": (0, 1),
            "east": (1, 0),
            "e": (1, 0),
            "west": (-1, 0),
            "w": (-1, 0),
        }
        if direction not in offsets:
            return "Unknown direction. Use north, south, east, or west."

        dx, dy = offsets[direction]
        next_x = self.player.x + dx
        next_y = self.player.y + dy
        if not (0 <= next_x < self.size and 0 <= next_y < self.size):
            return "A black-glass barrier marks the edge of this prototype city."

        self.player.trail.append((self.player.x, self.player.y))
        self.player.trail = self.player.trail[-8:]
        self.player.x = next_x
        self.player.y = next_y
        discovered = self.discover(next_x, next_y)
        captured = self.capture_current_position()
        return (
            f"Moved to ({next_x}, {next_y}). Discovered {len(discovered)} fogged blocks. "
            f"Captured {captured} cells with a {self.player.trail_intensity}."
        )

    def capture_current_position(self) -> int:
        """Capture every eligible tile in the player's current level-based radius."""

        captured = 0
        for position in self.neighbors_in_radius(
            self.player.x, self.player.y, self.player.capture_radius
        ):
            cell = self.cells[position]
            if cell.is_sovereign(self.now) and cell.sovereign_owner != self.player.name:
                continue
            if cell.team != self.player.team or cell.captured_by != self.player.name:
                cell.team = self.player.team
                cell.captured_by = self.player.name
                self.player.owned_cells.add(position)
                self.player.xp += CAPTURE_XP
                captured += 1
        return captured

    def buy_current_cell(self, duration: SovereignDuration) -> str:
        """Purchase sovereign status for the current tile."""

        position = (self.player.x, self.player.y)
        cell = self.cells[position]
        cell.team = self.player.team
        cell.captured_by = self.player.name
        cell.sovereign_owner = self.player.name
        cell.sovereign_avatar = self.player.avatar
        cell.sovereign_until = self.now + duration.delta
        self.player.owned_cells.add(position)
        return (
            f"Sovereign contract activated for {duration.label}: {self.player.name}'s "
            "marble hologram now protects this cell."
        )

    def leaderboard(self) -> str:
        """Render real-time mayor and dominant-team standings."""

        team_scores = {team: 0 for team in TEAM_COLORS}
        player_scores: dict[str, int] = {}
        for cell in self.cells.values():
            if cell.team:
                team_scores[cell.team] += 1
            if cell.captured_by:
                player_scores[cell.captured_by] = player_scores.get(cell.captured_by, 0) + 1

        mayor, mayor_cells = max(player_scores.items(), key=lambda item: item[1])
        dominant_team, team_cells = max(team_scores.items(), key=lambda item: item[1])
        return (
            f"Mayor: {mayor} with {mayor_cells} cells\n"
            f"Dominant team: {TEAM_COLORS[dominant_team]} with {team_cells} cells\n"
            f"Level {self.player.level} · {self.player.xp} XP · radius {self.player.capture_radius}"
        )

    def state_payload(self) -> dict[str, object]:
        """Return a JSON-serializable state snapshot for the web preview."""

        teams = {key: {"label": label} for key, label in TEAM_COLORS.items()}
        cells = []
        for cell in self.cells.values():
            position = (cell.x, cell.y)
            cells.append(
                {
                    "x": cell.x,
                    "y": cell.y,
                    "team": cell.team,
                    "capturedBy": cell.captured_by,
                    "discovered": position in self.player.discovered,
                    "sovereign": cell.is_sovereign(self.now),
                    "sovereignOwner": cell.sovereign_owner,
                    "sovereignAvatar": cell.sovereign_avatar,
                    "sovereignUntil": cell.sovereign_until.isoformat()
                    if cell.sovereign_until
                    else None,
                }
            )

        return {
            "size": self.size,
            "teams": teams,
            "player": {
                "name": self.player.name,
                "team": self.player.team,
                "avatar": self.player.avatar,
                "x": self.player.x,
                "y": self.player.y,
                "xp": self.player.xp,
                "level": self.player.level,
                "captureRadius": self.player.capture_radius,
                "trailIntensity": self.player.trail_intensity,
                "trail": [{"x": x, "y": y} for x, y in self.player.trail],
            },
            "cells": cells,
            "leaderboard": self.leaderboard(),
            "status": self.status(),
        }

    def render_map(self) -> str:
        """Render a dark-mode 2.5D-inspired text map with fog and sovereign glow."""

        symbols = {"cyan": "C", "violet": "V", "ember": "O", "acid": "A", None: "·"}
        lines = ["THE GRID // #0A0A0A dark mode // 50m x 50m cells"]
        for y in range(self.size):
            row = []
            for x in range(self.size):
                position = (x, y)
                if (self.player.x, self.player.y) == position:
                    row.append(self.player.avatar)
                    continue
                if position not in self.player.discovered:
                    row.append("░")
                    continue
                cell = self.cells[position]
                symbol = symbols[cell.team]
                if cell.is_sovereign(self.now):
                    symbol = symbol.lower() + "✦"
                row.append(symbol)
            lines.append(" ".join(row))
        return "\n".join(lines)

    def status(self) -> str:
        cell = self.cells[(self.player.x, self.player.y)]
        return (
            f"{self.player.name} · {TEAM_COLORS[self.player.team]} · "
            f"position ({self.player.x}, {self.player.y}) · level {self.player.level}"
            f"{cell.sovereign_badge(self.now)}"
        )


def choose_team() -> str:
    print("Choose your faction:")
    for key, label in TEAM_COLORS.items():
        print(f"- {key}: {label}")
    team = input("Team [cyan]: ").strip().lower() or "cyan"
    return team if team in TEAM_COLORS else "cyan"


WEB_APP_HTML = """<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>The Grid — Mobile Preview</title>
  <style>
    :root {
      --bg: #0A0A0A;
      --phone: #101017;
      --panel: rgba(14, 18, 30, 0.74);
      --line: rgba(255, 255, 255, 0.14);
      --cyan: #00E5FF;
      --violet: #9B5CFF;
      --ember: #FF6A00;
      --acid: #B6FF00;
      --text: #F8FAFC;
      --muted: #97A0B8;
      --street: rgba(255, 255, 255, 0.09);
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 16% 12%, rgba(0, 229, 255, 0.24), transparent 26rem),
        radial-gradient(circle at 80% 0%, rgba(155, 92, 255, 0.2), transparent 30rem),
        radial-gradient(circle at 70% 92%, rgba(182, 255, 0, 0.13), transparent 24rem),
        linear-gradient(135deg, #030305 0%, var(--bg) 48%, #111018 100%);
      overflow-x: hidden;
    }

    .page {
      display: grid;
      grid-template-columns: minmax(20rem, 1fr) minmax(20rem, 26rem);
      gap: 2rem;
      align-items: center;
      width: min(1180px, calc(100vw - 2rem));
      min-height: 100vh;
      margin: 0 auto;
      padding: 2rem 0;
    }

    .pitch { padding: 1rem; }
    .eyebrow { color: var(--cyan); font-size: 0.76rem; font-weight: 900; letter-spacing: 0.22em; text-transform: uppercase; }
    h1 { margin: 0.55rem 0 0.8rem; font-size: clamp(3rem, 9vw, 7.2rem); line-height: 0.84; letter-spacing: -0.09em; }
    .subtitle { max-width: 42rem; color: #CFD7EA; font-size: clamp(1rem, 2vw, 1.18rem); line-height: 1.7; }
    .feature-row { display: flex; flex-wrap: wrap; gap: 0.65rem; margin-top: 1.4rem; }
    .feature-row span {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 0.62rem 0.82rem;
      color: #EAF2FF;
      background: rgba(255, 255, 255, 0.06);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
      font-size: 0.82rem;
      font-weight: 800;
    }

    .phone {
      position: relative;
      width: min(100%, 410px);
      min-height: 820px;
      margin: 0 auto;
      border: 1px solid rgba(255,255,255,0.2);
      border-radius: 48px;
      padding: 0.75rem;
      background:
        linear-gradient(145deg, rgba(255,255,255,0.2), transparent 14%),
        linear-gradient(180deg, #1E2230, #07070B 28%, #11131E);
      box-shadow: 0 42px 120px rgba(0,0,0,0.65), 0 0 90px rgba(0,229,255,0.1);
    }

    .screen {
      position: relative;
      min-height: 790px;
      overflow: hidden;
      border-radius: 40px;
      border: 1px solid rgba(255,255,255,0.1);
      background: #06070C;
      isolation: isolate;
    }

    .screen::before {
      content: "";
      position: absolute;
      inset: 0;
      background:
        linear-gradient(90deg, transparent 49%, var(--street) 50%, transparent 51%) 0 0 / 92px 92px,
        linear-gradient(0deg, transparent 49%, var(--street) 50%, transparent 51%) 0 0 / 92px 92px,
        radial-gradient(circle at 50% 42%, rgba(0,229,255,0.18), transparent 18rem),
        radial-gradient(circle at 10% 90%, rgba(255,106,0,0.14), transparent 14rem);
      transform: rotate(0deg) scale(1.08);
      opacity: 0.9;
      z-index: -2;
    }

    .screen::after {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(0,0,0,0.82), transparent 22%, transparent 62%, rgba(0,0,0,0.88));
      z-index: -1;
      pointer-events: none;
    }

    .statusbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.9rem 1.1rem 0.35rem;
      color: #F7FBFF;
      font-size: 0.78rem;
      font-weight: 900;
      letter-spacing: 0.03em;
    }

    .hud {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 0.7rem;
      padding: 0.6rem 0.9rem;
    }

    .profile, .team-pill, .gps-pill {
      border: 1px solid var(--line);
      border-radius: 22px;
      background: rgba(8, 11, 20, 0.72);
      backdrop-filter: blur(16px);
      box-shadow: 0 14px 36px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.08);
    }

    .profile { display: flex; align-items: center; gap: 0.7rem; padding: 0.55rem 0.7rem; min-width: 0; }
    .avatar-card {
      position: relative;
      width: 3.1rem;
      height: 3.1rem;
      display: grid;
      place-items: center;
      border-radius: 18px;
      background: radial-gradient(circle at 50% 35%, #FFFFFF, var(--team, var(--cyan)) 34%, #111827 68%);
      box-shadow: 0 0 24px var(--team, var(--cyan));
      color: #051018;
      font-size: 1.7rem;
      font-weight: 1000;
    }
    .avatar-card::after {
      content: "";
      position: absolute;
      inset: -0.35rem;
      border: 1px solid color-mix(in srgb, var(--team, var(--cyan)) 72%, transparent);
      border-radius: 22px;
      opacity: 0.7;
    }
    .profile strong, .profile span { display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .profile span { color: var(--muted); font-size: 0.72rem; margin-top: 0.1rem; }
    .gps-pill { padding: 0.75rem 0.85rem; color: var(--acid); font-weight: 900; font-size: 0.74rem; }

    .map-stage {
      position: relative;
      height: 480px;
      margin: 0.3rem 0.8rem 0;
      border-radius: 30px;
      overflow: hidden;
      border: 1px solid rgba(255,255,255,0.08);
      background:
        radial-gradient(circle at 50% 50%, rgba(255,255,255,0.08), transparent 16rem),
        linear-gradient(135deg, rgba(0,229,255,0.05), rgba(155,92,255,0.08));
      perspective: 760px;
    }

    .map-label {
      position: absolute;
      left: 1rem;
      top: 1rem;
      z-index: 4;
      padding: 0.55rem 0.75rem;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(0,0,0,0.52);
      backdrop-filter: blur(14px);
      color: #DDE7FF;
      font-size: 0.72rem;
      font-weight: 900;
      letter-spacing: 0.13em;
      text-transform: uppercase;
    }

    #grid {
      position: absolute;
      left: 50%;
      top: 50%;
      display: grid;
      gap: 0.42rem;
      width: 475px;
      height: 475px;
      transform: translate(-50%, -46%) rotateX(58deg) rotateZ(-42deg);
      transform-origin: center;
      filter: drop-shadow(0 36px 36px rgba(0, 0, 0, 0.55));
    }

    .cell {
      position: relative;
      border: 1px solid rgba(255,255,255,0.14);
      border-radius: 10px;
      background: rgba(255, 255, 255, 0.04);
      min-width: 0;
      transition: transform 180ms ease, box-shadow 180ms ease, opacity 180ms ease;
    }
    .cell::after {
      content: "";
      position: absolute;
      inset: 12% 14% 0;
      border-radius: 8px 8px 4px 4px;
      background: linear-gradient(160deg, rgba(255,255,255,0.22), rgba(255,255,255,0.04));
      transform: translateY(-12%);
      opacity: 0.42;
    }

    .fog { background: rgba(5, 5, 8, 0.9); border-color: rgba(255,255,255,0.04); opacity: 0.78; }
    .fog::before { content: ""; position: absolute; inset: 0; border-radius: inherit; background: repeating-linear-gradient(45deg, transparent 0 7px, rgba(255,255,255,0.035) 8px 11px); }
    .cyan { --team: var(--cyan); }
    .violet { --team: var(--violet); }
    .ember { --team: var(--ember); }
    .acid { --team: var(--acid); }
    .owned { background: color-mix(in srgb, var(--team) 42%, rgba(0,0,0,0.5)); box-shadow: 0 0 18px color-mix(in srgb, var(--team) 48%, transparent); }
    .sovereign { transform: translateY(-18px); box-shadow: 0 0 34px var(--team), inset 0 0 28px rgba(255,255,255,0.25); }
    .sovereign::before { content: "👑"; position: absolute; inset: -18px -8px auto auto; transform: rotateZ(42deg) rotateX(-58deg); z-index: 5; font-size: 1.1rem; }
    .player { transform: translateY(-26px) scale(1.1); box-shadow: 0 0 34px #fff, 0 0 58px var(--team); z-index: 8; }
    .player::before {
      content: "";
      position: absolute;
      inset: -68%;
      border-radius: 999px;
      background: radial-gradient(circle, rgba(255,255,255,0.95) 0 10%, var(--team) 11% 25%, transparent 26% 100%);
      box-shadow: 0 0 36px var(--team), 0 0 68px var(--team);
      transform: rotateZ(42deg) rotateX(-58deg);
      animation: pulse 1.5s ease-in-out infinite;
      z-index: 5;
    }
    .player::after {
      content: "🛸";
      position: absolute;
      inset: -76%;
      display: grid;
      place-items: center;
      font-size: 1.55rem;
      transform: rotateZ(42deg) rotateX(-58deg);
      z-index: 6;
      filter: drop-shadow(0 0 12px var(--team));
    }

    @keyframes pulse { 50% { transform: rotateZ(42deg) rotateX(-58deg) scale(1.18); opacity: 0.72; } }

    .bottom-sheet {
      position: absolute;
      left: 0.8rem;
      right: 0.8rem;
      bottom: 0.85rem;
      z-index: 6;
      border: 1px solid var(--line);
      border-radius: 28px;
      padding: 1rem;
      background: rgba(8, 10, 18, 0.86);
      backdrop-filter: blur(20px);
      box-shadow: 0 -18px 60px rgba(0,0,0,0.44), inset 0 1px 0 rgba(255,255,255,0.08);
    }
    .stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.55rem; }
    .stat { padding: 0.72rem 0.55rem; border: 1px solid rgba(255,255,255,0.1); border-radius: 17px; background: rgba(255,255,255,0.045); text-align: center; }
    .stat span { display: block; color: var(--muted); font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.12em; }
    .stat strong { display: block; margin-top: 0.22rem; font-size: 1rem; }
    .controls { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.55rem; margin-top: 0.85rem; }
    button {
      min-height: 3rem;
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 17px;
      color: var(--text);
      background: linear-gradient(180deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05));
      cursor: pointer;
      font-weight: 1000;
      letter-spacing: 0.04em;
      touch-action: manipulation;
    }
    button:hover { border-color: var(--cyan); box-shadow: 0 0 18px rgba(0,229,255,0.25); }
    .buy { color: #111; background: linear-gradient(135deg, #FFFFFF, var(--acid)); box-shadow: 0 0 22px rgba(182,255,0,0.35); }
    .wide { grid-column: span 3; }
    .readout { display: grid; gap: 0.35rem; margin-top: 0.85rem; color: #DDE7F8; font-size: 0.78rem; line-height: 1.38; }
    .readout pre { margin: 0; white-space: pre-wrap; font: inherit; }

    @media (max-width: 860px) {
      body { background: #050509; }
      .page { display: block; width: 100%; padding: 0; min-height: 100vh; }
      .pitch { display: none; }
      .phone { width: 100%; min-height: 100vh; border: 0; border-radius: 0; padding: 0; background: #050509; }
      .screen { min-height: 100vh; border: 0; border-radius: 0; }
      .map-stage { height: calc(100vh - 246px); min-height: 430px; margin: 0.1rem 0.7rem 0; }
      #grid { width: 430px; height: 430px; }
      .bottom-sheet { position: fixed; }
    }
  </style>
</head>
<body>
  <main class="page">
    <section class="pitch">
      <div class="eyebrow">Mobile-first territory MMO</div>
      <h1>The Grid</h1>
      <p class="subtitle">Cette preview ressemble maintenant à une app mobile : avatar visible, carte urbaine sombre, grille 2.5D, cellules 3D, contrôles tactiles et feedback temps réel.</p>
      <div class="feature-row">
        <span>Avatar néon</span>
        <span>Carte 2.5D</span>
        <span>Fog of war</span>
        <span>Mode souverain</span>
      </div>
    </section>

    <section class="phone" aria-label="Mobile game preview">
      <div class="screen">
        <div class="statusbar"><span>9:41</span><span>5G ▰▰▰ 🔋</span></div>
        <div class="hud">
          <div class="profile">
            <div class="avatar-card" id="avatar">◎</div>
            <div><strong id="player-name">Neon Runner</strong><span id="team-name">Bleu Cyan</span></div>
          </div>
          <div class="gps-pill">GPS LIVE</div>
        </div>

        <div class="map-stage">
          <div class="map-label">Mapbox-style city grid · 50m</div>
          <div id="grid" aria-label="The Grid map"></div>
        </div>

        <aside class="bottom-sheet">
          <div class="stat-grid">
            <div class="stat"><span>Lvl</span><strong id="level">—</strong></div>
            <div class="stat"><span>XP</span><strong id="xp">—</strong></div>
            <div class="stat"><span>Rayon</span><strong id="radius">—</strong></div>
            <div class="stat"><span>Trail</span><strong id="trail">—</strong></div>
          </div>
          <div class="controls">
            <button></button><button data-move="n">▲</button><button></button>
            <button data-move="w">◀</button><button class="buy" data-buy="day">BUY</button><button data-move="e">▶</button>
            <button></button><button data-move="s">▼</button><button></button>
            <button class="wide buy" data-buy="week">Souverain 1 semaine</button>
          </div>
          <div class="readout">
            <pre id="status"></pre>
            <pre id="leaderboard"></pre>
          </div>
        </aside>
      </div>
    </section>
  </main>

  <script>
    const grid = document.querySelector('#grid');
    const avatar = document.querySelector('#avatar');
    const teamClass = { cyan: 'cyan', violet: 'violet', ember: 'ember', acid: 'acid' };
    const teamNames = { cyan: 'Bleu Cyan', violet: 'Violet', ember: 'Orange Braise', acid: 'Vert Acide' };

    async function api(path) {
      const response = await fetch(path);
      if (!response.ok) throw new Error(await response.text());
      return response.json();
    }

    function render(state) {
      const currentTeam = teamClass[state.player.team];
      grid.style.gridTemplateColumns = `repeat(${state.size}, 1fr)`;
      document.body.className = currentTeam;
      avatar.className = `avatar-card ${currentTeam}`;
      avatar.textContent = state.player.avatar;
      document.querySelector('#player-name').textContent = state.player.name;
      document.querySelector('#team-name').textContent = teamNames[state.player.team];
      grid.innerHTML = '';
      for (const cell of state.cells) {
        const tile = document.createElement('div');
        tile.className = 'cell';
        if (!cell.discovered) tile.classList.add('fog');
        if (cell.team) tile.classList.add(teamClass[cell.team], 'owned');
        if (cell.sovereign) tile.classList.add('sovereign');
        if (cell.x === state.player.x && cell.y === state.player.y) {
          tile.classList.add('player', currentTeam);
        }
        tile.title = cell.sovereign ? `Souverain: ${cell.sovereignOwner}` : `${cell.x}, ${cell.y}`;
        grid.appendChild(tile);
      }
      document.querySelector('#level').textContent = state.player.level;
      document.querySelector('#xp').textContent = state.player.xp;
      document.querySelector('#radius').textContent = state.player.captureRadius;
      document.querySelector('#trail').textContent = state.player.trailIntensity.replace(' ', '\n');
      document.querySelector('#status').textContent = state.status;
      document.querySelector('#leaderboard').textContent = state.leaderboard;
    }

    document.addEventListener('click', async (event) => {
      const move = event.target.dataset.move;
      const buy = event.target.dataset.buy;
      if (move) render(await api(`/api/move?direction=${move}`));
      if (buy) render(await api(`/api/buy?duration=${buy}`));
    });

    window.addEventListener('keydown', async (event) => {
      const keys = { ArrowUp: 'n', ArrowDown: 's', ArrowLeft: 'w', ArrowRight: 'e' };
      if (keys[event.key]) render(await api(`/api/move?direction=${keys[event.key]}`));
    });

    api('/api/state').then(render).catch((error) => {
      document.querySelector('#status').textContent = error.message;
    });
  </script>
</body>
</html>
"""


class GridPreviewHandler(BaseHTTPRequestHandler):
    """HTTP handler for the dependency-free web preview."""

    game = TheGridGame()

    def do_HEAD(self) -> None:  # noqa: N802 - stdlib callback name
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/api/state", "/api/move", "/api/buy"}:
            self.send_response(200)
            content_type = "text/html; charset=utf-8" if parsed.path == "/" else "application/json"
            self.send_header("Content-Type", content_type)
            self.end_headers()
            return
        self.send_error(404, "Not found")

    def do_GET(self) -> None:  # noqa: N802 - stdlib callback name
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.respond_html(WEB_APP_HTML)
            return
        if parsed.path == "/api/state":
            self.respond_json(self.game.state_payload())
            return
        if parsed.path == "/api/move":
            direction = parse_qs(parsed.query).get("direction", [""])[0]
            self.game.move(direction)
            self.respond_json(self.game.state_payload())
            return
        if parsed.path == "/api/buy":
            duration_name = parse_qs(parsed.query).get("duration", ["day"])[0]
            duration = {item.name.lower(): item for item in SovereignDuration}.get(
                duration_name,
                {item.label.split()[1]: item for item in SovereignDuration}.get(
                    duration_name, SovereignDuration.DAY
                ),
            )
            self.game.buy_current_cell(duration)
            self.respond_json(self.game.state_payload())
            return
        self.send_error(404, "Not found")

    def log_message(self, format: str, *args: object) -> None:
        """Keep preview logs concise and branded."""

        print(f"[the-grid] {self.address_string()} - {format % args}")

    def respond_html(self, html: str) -> None:
        payload = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def respond_json(self, payload: dict[str, object]) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def run_web_preview(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the browser preview server."""

    server = ThreadingHTTPServer((host, port), GridPreviewHandler)
    print(f"The Grid preview running at http://{host}:{port}", flush=True)
    print(f"Local URL: http://localhost:{port}", flush=True)
    print(
        "Remote workspace: open/forward the preview for port "
        f"{port} from your editor or cloud IDE Ports panel.",
        flush=True,
    )
    server.serve_forever()


def run_cli() -> None:
    """Start the interactive terminal prototype."""

    game = TheGridGame()
    print("Welcome to The Grid — walk-to-capture territory MMO prototype.")
    name = input("Sovereign name [Neon Runner]: ").strip()
    if name:
        game.player.name = name
    game.player.team = choose_team()
    game.capture_current_position()

    print("\nCommands: map, status, leaderboard, buy day|week|month|year, n/s/e/w, quit")
    while True:
        print("\n" + game.render_map())
        command = input("grid> ").strip().lower()
        if command in {"quit", "q", "exit"}:
            print("The city keeps glowing. See you on The Grid.")
            return
        if command in {"map", "m"}:
            continue
        if command == "status":
            print(game.status())
            continue
        if command == "leaderboard":
            print(game.leaderboard())
            continue
        if command.startswith("buy"):
            _, _, duration_name = command.partition(" ")
            duration_lookup = {item.name.lower(): item for item in SovereignDuration}
            duration_lookup.update({item.label.split()[1]: item for item in SovereignDuration})
            duration = duration_lookup.get(duration_name, SovereignDuration.DAY)
            print(game.buy_current_cell(duration))
            continue
        print(game.move(command))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run The Grid prototype.")
    parser.add_argument("--web", action="store_true", help="run the browser preview")
    parser.add_argument("--host", default="0.0.0.0", help="preview host")
    parser.add_argument("--port", type=int, default=8000, help="preview port")
    args = parser.parse_args()

    if args.web:
        run_web_preview(host=args.host, port=args.port)
    else:
        run_cli()
