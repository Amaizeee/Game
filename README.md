# Game

Ce dépôt contient maintenant deux mini-projets :

1. un jeu Python de nombre aléatoire,
2. un visualiseur 3D de la Terre avec satellites et caméras OpenStreetMap.

## 1) Jeu du nombre aléatoire

### Lancer

```bash
python random_number_game.py
```

## 2) Terre 3D interactive (satellites + caméras)

Le fichier `globe_viewer.html` affiche :

- une Terre 3D manipulable (caméra libre avec la souris),
- des satellites actifs (données TLE CelesTrak propagées côté client),
- des caméras géolocalisées via OpenStreetMap / Overpass (`man_made=surveillance`).

### Lancer

Comme le navigateur bloque parfois certaines requêtes depuis `file://`, lance un petit serveur local :

```bash
python -m http.server 8000
```

Puis ouvre :

```text
http://localhost:8000/globe_viewer.html
```

### Contrôles

- clic gauche + glisser : rotation,
- molette : zoom,
- clic droit + glisser : déplacement de caméra,
- panneau en haut à gauche : vitesse du temps, affichage satellites/caméras, rechargement des données.
