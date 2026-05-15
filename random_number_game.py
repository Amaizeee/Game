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
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>The Grid Preview</title>
  <style>
    :root {
      --bg: #0A0A0A;
      --panel: rgba(18, 18, 24, 0.82);
      --line: rgba(255, 255, 255, 0.14);
      --cyan: #00E5FF;
      --violet: #9B5CFF;
      --ember: #FF6A00;
      --acid: #B6FF00;
      --text: #F8FAFC;
      --muted: #8B93A7;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 20% 10%, rgba(0, 229, 255, 0.22), transparent 28rem),
        radial-gradient(circle at 84% 18%, rgba(155, 92, 255, 0.18), transparent 24rem),
        linear-gradient(135deg, #050505 0%, var(--bg) 48%, #111111 100%);
      overflow-x: hidden;
    }

    main {
      display: grid;
      grid-template-columns: minmax(22rem, 1fr) minmax(20rem, 28rem);
      gap: 2rem;
      width: min(1180px, calc(100vw - 2rem));
      margin: 0 auto;
      padding: 2rem 0;
    }

    .hero, .panel {
      border: 1px solid var(--line);
      border-radius: 28px;
      background: var(--panel);
      box-shadow: 0 24px 80px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.08);
      backdrop-filter: blur(18px);
    }

    .hero { padding: 2rem; }
    .eyebrow { color: var(--cyan); font-size: 0.8rem; font-weight: 800; letter-spacing: 0.22em; text-transform: uppercase; }
    h1 { margin: 0.4rem 0 0.7rem; font-size: clamp(2.5rem, 8vw, 5.7rem); line-height: 0.88; letter-spacing: -0.08em; }
    .subtitle { max-width: 44rem; color: #C9D2E3; font-size: 1.05rem; line-height: 1.65; }

    .map-wrap {
      margin-top: 2rem;
      perspective: 900px;
    }

    #grid {
      display: grid;
      gap: 0.35rem;
      transform: rotateX(58deg) rotateZ(-42deg);
      transform-origin: center;
      width: min(68vw, 620px);
      aspect-ratio: 1;
      margin: 1.5rem auto 4rem;
      filter: drop-shadow(0 36px 36px rgba(0, 0, 0, 0.55));
    }

    .cell {
      position: relative;
      border: 1px solid rgba(255,255,255,0.14);
      border-radius: 10px;
      background: rgba(255, 255, 255, 0.035);
      min-width: 0;
      transition: transform 180ms ease, box-shadow 180ms ease, opacity 180ms ease;
    }

    .cell::after {
      content: "";
      position: absolute;
      inset: 10%;
      border-radius: 8px;
      background: linear-gradient(135deg, rgba(255,255,255,0.16), rgba(255,255,255,0.02));
      opacity: 0.45;
    }

    .fog { background: rgba(5, 5, 5, 0.9); border-color: rgba(255,255,255,0.05); opacity: 0.72; }
    .cyan { --team: var(--cyan); }
    .violet { --team: var(--violet); }
    .ember { --team: var(--ember); }
    .acid { --team: var(--acid); }
    .owned { background: color-mix(in srgb, var(--team) 42%, transparent); box-shadow: 0 0 18px color-mix(in srgb, var(--team) 48%, transparent); }
    .sovereign { transform: translateY(-12px); box-shadow: 0 0 34px var(--team), inset 0 0 28px rgba(255,255,255,0.25); }
    .player { transform: translateY(-22px) scale(1.08); box-shadow: 0 0 28px #fff, 0 0 46px var(--team); z-index: 3; }
    .player::before {
      content: "◎";
      position: absolute;
      inset: -30%;
      display: grid;
      place-items: center;
      color: #fff;
      font-size: 1.4rem;
      text-shadow: 0 0 16px var(--team), 0 0 30px var(--team);
      transform: rotateZ(42deg) rotateX(-58deg);
    }

    .panel { padding: 1.3rem; align-self: start; }
    .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin: 1rem 0; }
    .stat { padding: 1rem; border: 1px solid var(--line); border-radius: 18px; background: rgba(255,255,255,0.045); }
    .stat span { display: block; color: var(--muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.14em; }
    .stat strong { display: block; margin-top: 0.25rem; font-size: 1.2rem; }
    .controls { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.65rem; margin: 1rem 0; }
    button {
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 16px;
      padding: 0.85rem 0.75rem;
      color: var(--text);
      background: linear-gradient(180deg, rgba(255,255,255,0.13), rgba(255,255,255,0.04));
      cursor: pointer;
      font-weight: 800;
      letter-spacing: 0.04em;
    }
    button:hover { border-color: var(--cyan); box-shadow: 0 0 18px rgba(0,229,255,0.25); }
    .wide { grid-column: span 3; }
    pre { white-space: pre-wrap; color: #DDE7F8; line-height: 1.55; }

    @media (max-width: 860px) {
      main { grid-template-columns: 1fr; }
      #grid { width: min(86vw, 560px); }
    }
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="eyebrow">MMO Territory Prototype</div>
      <h1>The Grid</h1>
      <p class="subtitle">A premium dark-mode city map where Bleu Cyan, Violet, Orange Braise, and Vert Acide fight for persistent 50m x 50m territory. Walk, reveal fog, capture cells, and buy sovereign visibility.</p>
      <div class="map-wrap"><div id="grid" aria-label="The Grid map"></div></div>
    </section>

    <aside class="panel">
      <div class="eyebrow">Live Preview</div>
      <div class="stat-grid">
        <div class="stat"><span>Level</span><strong id="level">—</strong></div>
        <div class="stat"><span>XP</span><strong id="xp">—</strong></div>
        <div class="stat"><span>Radius</span><strong id="radius">—</strong></div>
        <div class="stat"><span>Trail</span><strong id="trail">—</strong></div>
      </div>
      <div class="controls">
        <button></button><button data-move="n">N</button><button></button>
        <button data-move="w">W</button><button data-buy="day">BUY</button><button data-move="e">E</button>
        <button></button><button data-move="s">S</button><button></button>
        <button class="wide" data-buy="week">Sovereign Week</button>
      </div>
      <pre id="status"></pre>
      <pre id="leaderboard"></pre>
    </aside>
  </main>

  <script>
    const grid = document.querySelector('#grid');
    const teamClass = { cyan: 'cyan', violet: 'violet', ember: 'ember', acid: 'acid' };

    async function api(path) {
      const response = await fetch(path);
      if (!response.ok) throw new Error(await response.text());
      return response.json();
    }

    function render(state) {
      grid.style.gridTemplateColumns = `repeat(${state.size}, 1fr)`;
      grid.innerHTML = '';
      for (const cell of state.cells) {
        const tile = document.createElement('div');
        tile.className = 'cell';
        if (!cell.discovered) tile.classList.add('fog');
        if (cell.team) tile.classList.add(teamClass[cell.team], 'owned');
        if (cell.sovereign) tile.classList.add('sovereign');
        if (cell.x === state.player.x && cell.y === state.player.y) {
          tile.classList.add('player', teamClass[state.player.team]);
        }
        tile.title = cell.sovereign ? `Sovereign: ${cell.sovereignOwner}` : `${cell.x}, ${cell.y}`;
        grid.appendChild(tile);
      }
      document.querySelector('#level').textContent = state.player.level;
      document.querySelector('#xp').textContent = state.player.xp;
      document.querySelector('#radius').textContent = state.player.captureRadius;
      document.querySelector('#trail').textContent = state.player.trailIntensity;
      document.querySelector('#status').textContent = state.status;
      document.querySelector('#leaderboard').textContent = state.leaderboard;
    }

    document.addEventListener('click', async (event) => {
      const move = event.target.dataset.move;
      const buy = event.target.dataset.buy;
      if (move) render(await api(`/api/move?direction=${move}`));
      if (buy) render(await api(`/api/buy?duration=${buy}`));
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
