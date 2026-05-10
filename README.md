# Statue

Statue est une application iOS SwiftUI pour un réseau social fermé et payant destiné aux jeunes professionnels ambitieux. L'expérience visuelle suit une esthétique `quiet luxury` : typographie serif, couleurs sobres par rang, séparateurs très fins et beaucoup d'espace négatif.

## Fonctionnalités prototypées

- Fil membre avec accès progressif selon le rang Bronze, Gold ou Diamond.
- Carte membre plein écran inspirée d'une carte de crédit luxe.
- QR code natif CoreImage encodant `https://statue.app/member/{username}`.
- Numéro membre séquentiel affiché au format `N° 0247`.
- Statistiques de posts et de liens sous la carte.
- Grille d'archives de posts passés.
- Profil avec cadre Gold et sélection visuelle d'abonnement.
- Onglet Moi pour modifier le profil, gérer l'abonnement, les notifications et la déconnexion.

## Design system

| Rang | Prix | Fond carte | Texte | Bordure |
| --- | --- | --- | --- | --- |
| Bronze | 5 €/mois | `#2a1f17` | `#b87333` | `#3a2a1d` |
| Gold | 50 €/mois | `#1a1407` | `#d4af37` | `#2a2008` |
| Diamond | 100 €/mois | `#f5f5f5` | `#1a1a1a` | `#c0c0c0` |

Typographie :

- Marque et titres : Georgia avec letter-spacing élevé.
- Corps : SF Pro via la police système iOS.
- Badges : 10 px, uppercase, letter-spacing 1 px.

## Structure

```text
Package.swift
StatueApp/
  StatueApp.swift
  Design/StatueTheme.swift
  Models/
  Views/
    Components/
    Tabs/
```

## Lancer dans Xcode

1. Ouvrir le dossier du dépôt dans Xcode 15 ou plus récent.
2. Sélectionner le produit `Statue`.
3. Choisir un simulateur iOS 17+.
4. Lancer l'application.

## Prochaines intégrations backend

- Firebase Auth pour l'inscription et la connexion.
- Firestore pour les profils, posts, salons et numéros membres séquentiels.
- Firebase Storage pour les photos de profil.
- RevenueCat ou StoreKit 2 pour les abonnements in-app.
- Firebase Cloud Messaging pour les notifications push.
