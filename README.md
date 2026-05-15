# The Grid

The Grid is a terminal prototype for a real-world geolocation territory MMO. The production vision is a premium dark-mode 2.5D map where four electric factions compete to color a living city grid made of 50m x 50m cells.

## Core Vision

- **World:** the city is represented as square territory cells, matching the intended 50m x 50m live GPS grid.
- **Conflict:** four factions compete for control: Bleu Cyan, Violet, Orange Braise, and Vert Acide.
- **Style:** the terminal renderer uses a deep-black map mood, fog glyphs, neon faction initials, and sovereign glow markers as a lightweight stand-in for the planned glass/metal 3D buildings.

## Gameplay Implemented

- **Walk-to-capture:** moving north, south, east, or west captures the current area for your faction.
- **Persistent territory:** captured cells stay colored until an opponent recaptures them; there is no automatic reset.
- **Fog of war:** unexplored cells are hidden until the player walks close enough to discover them.
- **XP and levels:** discovery and capture grant XP. Higher levels increase capture radius and strengthen the light-trail description.
- **Leaderboard:** the prototype reports the current Mayor and dominant team based on controlled cells.

## Sovereign Monetization Mode

Players can buy the current cell for a fixed duration:

- `buy day`
- `buy week`
- `buy month`
- `buy year`

A sovereign cell becomes immune to enemy capture until the contract expires, displays the owner's name/avatar in status text, and renders with a permanent glow marker (`✦`).

## Run Locally on Your Computer

The Grid uses only the Python standard library, so there are no packages to install.

1. Install **Python 3.11+** from [python.org](https://www.python.org/downloads/) if it is not already installed.
2. Download or clone this repository, then open a terminal in the project folder.
3. Confirm Python is available:

   ```bash
   python --version
   ```

   On macOS or Linux, use `python3 --version` if `python` is not found.

4. Start the browser preview:

   ```bash
   python random_number_game.py --web --host 127.0.0.1 --port 8000
   ```

   On macOS or Linux, use `python3 random_number_game.py --web --host 127.0.0.1 --port 8000` if your Python command is `python3`.

5. Open this URL in your browser:

   ```text
   http://localhost:8000
   ```

6. If port `8000` is already in use, choose another port and open the matching URL:

   ```bash
   python random_number_game.py --web --host 127.0.0.1 --port 8080
   ```

   ```text
   http://localhost:8080
   ```

7. Stop the local server with `Ctrl+C` in the terminal.

## How to Play

1. To play in the terminal instead of the browser, run:

   ```bash
   python random_number_game.py
   ```

2. Pick a name and faction in the terminal game.
3. Use these commands:

   | Command | Effect |
   | --- | --- |
   | `n`, `s`, `e`, `w` | Move and capture territory |
   | `map` | Redraw the dark-mode grid |
   | `status` | Show player, team, level, position, and sovereign badge |
   | `leaderboard` | Show the Mayor and dominant faction |
   | `buy day\|week\|month\|year` | Activate sovereign protection on the current cell |
   | `quit` | Exit the prototype |

## Automated Checks

Run the test suite with:

```bash
python -m unittest discover -s tests
```
