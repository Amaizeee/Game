# The Grid

The Grid is a mobile-first browser and terminal prototype for a real-world geolocation territory MMO. The production vision is a premium dark-mode 2.5D map where four electric factions compete to color a living city grid made of 50m x 50m cells.

## Core Vision

- **World:** the city is represented as square territory cells, matching the intended 50m x 50m live GPS grid.
- **Conflict:** four factions compete for control: Bleu Cyan, Violet, Orange Braise, and Vert Acide.
- **Style:** the browser preview now presents a mobile app shell with a visible neon avatar, dark city-map background, 2.5D grid, extruded cell blocks, tactile controls, and sovereign glow markers as a lightweight stand-in for the planned Mapbox/mobile experience.

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


## Architecture Technique Cible

Le prototype actuel reste volontairement local et sans dépendances, mais la version mobile/production doit évoluer vers une architecture temps réel géospatiale :

- **Moteur de carte : Mapbox GL SDK** pour la vue 2.5D/3D, les extrusions de bâtiments, le style dark premium custom et les animations de couches de territoire.
- **Localisation : Background Geolocation** côté mobile pour continuer à détecter les déplacements et les captures quand le téléphone est en poche, avec une logique anti-spam/anti-triche côté serveur.
- **Indexation de grille : H3 (Uber) ou S2 (Google)** pour convertir chaque position GPS en identifiant de cellule léger, stable et rapide à comparer côté backend. H3 est un bon premier choix pour prototyper vite; S2 reste une alternative solide si l'équipe préfère les cellules hiérarchiques Google.
- **Backend : Node.js / Express** pour exposer les API de session, capture, achat souverain, profil joueur, progression XP et leaderboard.
- **Temps réel : Socket.io** pour diffuser les mouvements d'avatars, les changements de couleur de cases, les captures ennemies et les mises à jour de classement sans recharger la carte.
- **Redis : positions temps réel et King of the Hill** avec TTL courts pour suivre les joueurs actifs, calculer les zones chaudes et maintenir les classements instantanés.
- **PostgreSQL + PostGIS : stockage durable** des achats de cases, contrats souverains, historique des captures, géométries de cellules, audits anti-fraude et analytics de territoire.

### Flux de Capture Production

1. L'app mobile reçoit une position GPS en background.
2. Le client calcule ou envoie la coordonnée brute au backend.
3. Le backend convertit la position en cellule H3/S2, vérifie la vitesse, la précision GPS et les règles anti-triche.
4. Redis met à jour la position live du joueur et les scores temps réel.
5. PostgreSQL/PostGIS persiste la capture si la case n'est pas protégée par un contrat souverain actif.
6. Socket.io diffuse l'événement aux joueurs proches pour recolorer la carte instantanément.
7. Mapbox GL met à jour les couches visuelles : couleur d'équipe, extrusion 3D, brillance souveraine, plaque/hologramme et onde de choc.

### Découpage des Services

| Service | Stack cible | Responsabilité |
| --- | --- | --- |
| Mobile app | Mapbox GL SDK + Background Geolocation | Affichage 3D, tracking GPS, actions joueur |
| API gameplay | Node.js / Express | Capture, XP, niveaux, achats, profils |
| Realtime gateway | Socket.io | Mouvements live, captures, leaderboard |
| Cache live | Redis | Positions actives, King of the Hill, TTL |
| Data durable | PostgreSQL + PostGIS | Territoires achetés, historique, géospatial, audit |

## Run Locally on Your Computer

The Grid uses only the Python standard library, so there are no packages to install. The browser preview is designed mobile-first: open it on a phone-sized browser window or use your browser devtools device toolbar to test the mobile layout.

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
