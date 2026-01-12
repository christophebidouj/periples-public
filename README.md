# Périples Balance Workshop

**Outil professionnel d'équilibrage pour le jeu de société "Périples"**

[![Streamlit](https://img.shields.io/badge/Streamlit-1.47+-FF4B4B.svg)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](#licence)

---

## Vue d'ensemble

Le **Périples Balance Workshop** est un simulateur de combat développé spécifiquement pour l'équilibrage et le développement du jeu de société **Périples** © Bastien LIAUTY. Cet outil permet aux game designers de tester, valider et ajuster les mécaniques de jeu avec des données authentiques issues des règles officielles V3.0.

### Objectifs principaux

- **Validation des règles** – Tester les mécaniques avant impression finale
- **Équilibrage multi-joueurs** – Ajuster la difficulté selon le nombre de joueurs (1-4)
- **Test d'équipements** – Valider l'impact des 56 équipements sur les statistiques
- **Calibrage des capacités** – Analyser l'équilibre des 48 capacités spéciales
- **Simulation de scénarios** – Reproduire des situations de jeu pour détecter les déséquilibres

### Données authentiques

- **8 héros jouables** avec statistiques de base
- **72 ennemis évolutifs** adaptés au nombre de joueurs
- **56 équipements** (armes, armures, accessoires) + 4 objets spéciaux
- **48 capacités spéciales** issues du livre de règles V3.0
- **Système de potions** (Petite : 4 PV | Grande : PV max)

---

## Fonctionnalités principales

### 🏰 Sélection des équipes

Module de configuration rapide pour lancer des simulations.

- Sélection des héros avec **3 builds prédéfinis** (Facile/Normal/Difficile) ou builds personnalisés
- Sélection des ennemis avec recherche par nom/numéro
- Configuration des règles : initiative D20, coups critiques, dégâts magiques
- Support des builds personnalisés créés dans la Forge

### 🎮 Playtest Manuel (Sandbox V2)

Mode de simulation avancé avec contrôle total des actions.

**Mode Initiative (règles officielles)** : Jets de D20 pour déterminer l'ordre des tours, héros prioritaires en cas d'égalité.

**Mode Manuel (tests de scénarios)** : Sélection manuelle du personnage actif, actions multiples par tour (⚔️ Attaquer, 🔮 Utiliser capacité, 🩸 Boire potion, 🤝 Faire boire un allié), système **undo/redo** pour explorer différentes stratégies.

### ⚙️ Forge des équipements

Éditeur de builds personnalisés pour expérimenter avec les combinaisons d'équipements.

- Sélection parmi 56 équipements officiels + 4 objets spéciaux
- Slider séquentiel de capacités (0-6) pour débloquer progressivement les pouvoirs
- Configuration des potions (quantités personnalisables)
- Sauvegarde dans `custom_builds.csv`

### ⚔️ Gestion des ennemis

Éditeur d'ennemis personnalisés pour tester de nouvelles créatures.

- Création d'ennemis avec statistiques et capacités personnalisées
- Configuration de la scalabilité multi-joueurs
- Sauvegarde dans `custom_enemies.csv`

### ℹ️ À propos

Documentation intégrée et crédits du projet.

---

## Installation

### Prérequis

- **Python 3.10+** (testé avec Python 3.10 et 3.11)
- **pip** (gestionnaire de paquets Python)

### Installation rapide

```bash
# Cloner le dépôt
git clone [url-du-repo]
cd periples-balance-workshop

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app.py
```

L'application sera accessible à l'adresse : `https://periples-equilibrage.streamlit.app/`

### Dépendances

```
streamlit==1.47.1      # Interface utilisateur
pandas==2.3.1          # Manipulation des données CSV
openpyxl==3.1.2        # Lecture des fichiers Excel (capacités)
numpy==2.2.6           # Calculs numériques
plotly==6.2.0          # Visualisations (futurs graphiques)
pydantic==2.11.7       # Validation des modèles de données
```

---

## Démarrage rapide

### Workflow d'équilibrage type

**Objectif :** Valider l'équilibre d'un ennemi contre une formation type.

```
1. 🏰 Sélection
   ├─ Choisir 2-3 héros en difficulté Normal
   ├─ Sélectionner l'ennemi à tester
   ├─ Activer Initiative D20 et Critiques
   └─ Lancer le Playtest Manuel

2. 🎮 Playtest Manuel
   ├─ Mode Initiative : Jouer le combat en suivant l'ordre D20
   ├─ Mode Manuel : Contrôle total de l'ordre des actions
   └─ Analyser les métriques (durée, survie, ressources consommées)

3. Utiliser undo/redo pour :
   ├─ Corriger les erreurs de manipulation
   ├─ Refaire un jet de dés défavorable
   └─ Tester différentes décisions tactiques
```

### Autres scénarios de test

- **Test multi-joueurs** : Lancer 2/3/4 héros contre le même ennemi, comparer les métriques
- **Test de builds** : Comparer Facile/Normal/Difficile sur le même combat
- **Validation d'équipement** : Créer un build custom dans la Forge, tester contre plusieurs ennemis
- **Exploration tactique** : Mode Manuel + undo/redo pour analyser l'impact des capacités

---

## Mécaniques de jeu

### Système de jetons parade

Implémentation fidèle des règles V3.0 (page 26 du livre de règles).

**Fonctionnement :** Chaque héros/ennemi commence avec **N jetons** (N = nombre de personnages dans le camp adverse). Lors d'une attaque réussie, la cible peut dépenser 1 jeton pour annuler les dégâts. Au début du tour d'un personnage, ses jetons sont réinitialisés au maximum.

**Impact stratégique :** Les héros en infériorité numérique ont plus de jetons (meilleure défense), les ennemis nombreux ont moins de jetons (plus vulnérables individuellement). Encourage la coordination des attaques pour épuiser les jetons.

### Objets magiques (O-1 à O-4)

Les 4 objets magiques permettent de tester des mécaniques avancées avec effets spéciaux uniques. Entièrement opérationnels dans le simulateur.

| Code | Héros | Effet magique |
|------|-------|---------------|
| **O-1** | Elneha | Gemme de pouvoir – Convertit les attaques Ours/Loup en dégâts magiques |
| **O-2** | Liarie | Bâton de puissance – +1 utilisation pour toutes les capacités magiques |
| **O-3** | Kraor | Médaillon d'appel – Invoque un Pet (Précision 4, Dégâts magiques 4, Santé 15) |
| **O-4** | Stèphe | Lyre phœnix – +4 sorts maximum + toutes les attaques en dégâts magiques |

### Métriques d'équilibrage

**Combat équilibré en difficulté Normal :**
- Taux de victoire : **60-75%** | Durée : **4-8 rounds** | Survivants : **2-3 sur 3** héros
- Consommation de ressources : **50-80%** (sorts + potions)

**Signaux de déséquilibre :**
- ⚠️ Victoire en <3 rounds → Ennemi trop faible
- ⚠️ Défaite avec 0 survivant → Ennemi trop fort
- ⚠️ Aucune ressource consommée → Héros sur-équipés
- ⚠️ Héros bloqués (ne peuvent pas attaquer) → Capacités ennemies trop puissantes

---

## Architecture technique

### Organisation modulaire

L'application suit une architecture MVC adaptée à Streamlit avec **séparation stricte** entre logique métier et interface.

```
periples-balance-workshop/
├── app.py                              # Application principale Streamlit
├── models/                             # Logique métier (business logic)
│   ├── character.py                    # Héros et ennemis
│   ├── abilities.py                    # Système de capacités
│   ├── rules_engine.py                 # Règles de jeu configurables
│   └── combat/                         # Module de combat modulaire
│       ├── initiative_manager.py       # Jets de D20 et ordre des tours
│       ├── spell_manager.py            # Gestion centralisée des sorts
│       ├── combat_actions.py           # Attaques, capacités, potions
│       ├── turn_manager.py             # Gestion des tours + IA tactique
│       └── combat_engine.py            # Orchestrateur principal
├── ui/components/                      # Interface utilisateur
│   ├── sandbox_interface_v2.py         # Mode Playtest Manuel
│   ├── hero_components.py              # Cartes héros + builds
│   └── forge_abilities_components.py   # Interface Forge
├── utils/                              # Utilitaires
│   ├── data_loader.py                  # Chargement des CSV/Excel
│   └── abilities_loader.py             # Import des capacités
├── data/                               # Données du jeu
│   ├── heroes.csv                      # 8 héros officiels
│   ├── enemies.csv                     # 72 ennemis évolutifs
│   ├── equipment.csv                   # 56 équipements + 4 objets spéciaux
│   ├── Sorts.xlsx                      # Données complètes des capacités
│   └── custom_builds.csv               # Builds personnalisés
└── hero_builds_data.py                 # Configuration des builds prédéfinis
```

### Système de combat refactorisé

Le moteur de combat a été refactorisé en **6 modules spécialisés** (~1800 lignes) :

- **InitiativeManager** : Jets de D20, tri par ordre décroissant, gestion des égalités (héros prioritaires)
- **SpellManager** : Compteur de sorts centralisé, support du Bâton de puissance (O-2)
- **CombatActions** : Exécution des attaques, capacités, potions, objets spéciaux, coups critiques
- **TurnManager** : Orchestration des tours (héros → ennemis), IA tactique, gestion des Pets
- **CombatLogger** : Formatage des messages de combat, affichage des jets de dés
- **CombatEngine** : Orchestrateur principal, boucle de combat, calcul des métriques

### Optimisations performance

**Cache Streamlit** : Données statiques (CSV, Excel) chargées une seule fois au démarrage via `@st.cache_data`.

**Calcul dynamique** : Stats finales = stats de base (CSV) + bonus d'équipements. Aucune stat hardcodée, garantit la cohérence avec les équipements officiels.

**Session state optimisé** : Stockage minimal des choix utilisateur, historique undo/redo basé sur deepcopy d'états.

---

## Développement et maintenance

### État du projet

**Application stable et fonctionnelle** – Version complète en production.

✅ Toutes les fonctionnalités critiques implémentées :
- Système de combat conforme aux règles V3.0
- Playtest manuel avec modes Initiative et Manuel
- Forge d'équipements et gestion d'ennemis personnalisés
- Architecture modulaire refactorisée
- Métriques d'équilibrage précises

**Évolutions futures** : Des améliorations mineures restent possibles (visualisations, exports, nouvelles mécaniques) en fonction des besoins de l'équipe.

### Contexte de développement

**Outil interne, pas un produit commercial**

Cet outil de travail pour l'équipe de développement de Périples privilégie :
1. **Fiabilité** – Simulations précises conformes aux règles V3.0
2. **Flexibilité** – Adaptation rapide aux changements de règles
3. **Traçabilité** – Logs détaillés pour analyse post-mortem

### Standards de code

**Séparation logique/UI stricte**
- `models/` : Logique métier pure (pas d'import Streamlit)
- `ui/components/` : Interface (appels à `models/`)

**Données authentiques uniquement**
- Tous les CSV/Excel proviennent des sources officielles
- Pas de stats inventées ou hardcodées

**Documentation inline**
- Docstrings pour toutes les fonctions publiques
- Commentaires pour les mécaniques complexes (parade, objets spéciaux)

---

## Équipe

### Créateur du jeu
**Bastien LIAUTY** – Game Designer, Créateur de Périples

### Développement du simulateur
**Christophe Bidouj** – Développeur principal
- Architecture et développement
- Intégration des règles V3.0
- Assistance : Claude AI (Anthropic)

---

## Licence

### Propriété intellectuelle

**Jeu "Périples"** © Bastien LIAUTY – Tous droits réservés

Le contenu du jeu (règles, personnages, équipements, illustrations) est la propriété exclusive de l'auteur.

### Code source

**Périples Balance Workshop** – Code développé par Christophe Bidouj

### Usage autorisé

✅ **Utilisation pour le développement de Périples**
- Équilibrage du jeu par l'équipe de développement
- Tests de nouvelles mécaniques et extensions
- Validation des règles avant publication
- Prototypage de contenu additionnel

❌ **Utilisation interdite**
- Usage commercial sans autorisation
- Redistribution publique du code ou des données
- Adaptation pour d'autres jeux sans accord
- Publication des données de jeu confidentielles

---

**Note :** Cet outil est destiné exclusivement à l'équipe de développement de Périples. Il n'y a pas de support public.

---

<div align="center">

**Périples Balance Workshop**
*Dernière mise à jour : Janvier 2026*

</div>
