# Périples Balance Workshop

**Outil professionnel d'équilibrage pour le jeu de société "Périples"**

[![Streamlit](https://img.shields.io/badge/Streamlit-1.47+-FF4B4B.svg)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](#licence)

---

## Vue d'ensemble

Le **Périples Balance Workshop** est un simulateur de combat développé spécifiquement pour l'équilibrage et le développement du jeu de société **Périples** © Bastien LIAUTY. Cet outil permet aux game designers de tester, valider et ajuster les mécaniques de jeu avec des données authentiques issues des règles officielles V3.0.

### Objectif principal : Équilibrage du jeu

Cet outil répond aux besoins critiques du développement d'un jeu de société :

- **Validation des règles de combat** – Tester les mécaniques avant impression finale
- **Équilibrage des ennemis** – Ajuster la difficulté selon le nombre de joueurs (1-4 joueurs)
- **Test des équipements** – Valider l'impact de 56 équipements sur les statistiques
- **Calibrage des capacités** – Analyser l'équilibre des 48 capacités spéciales
- **Simulation de scénarios** – Reproduire des situations de jeu pour détecter les déséquilibres
- **Analyse de données** – Métriques précises pour ajuster la courbe de difficulté

### Données authentiques

Le simulateur utilise exclusivement les données officielles du jeu :
- **8 héros jouables** avec leurs statistiques de base
- **72 ennemis évolutifs** adaptés au nombre de joueurs
- **56 équipements** répartis en armes, armures et accessoires
- **48 capacités spéciales** issues du livre de règles V3.0
- **4 objets spéciaux uniques** avec mécaniques avancées
- **Système de potions** (Petite : 4 PV | Grande : PV max)

---

## Fonctionnalités principales

L'application est organisée en **5 modules** spécialisés accessibles via une navigation par onglets.

### 🏰 Sélection des équipes

Module de configuration rapide pour lancer des simulations de combat.

**Fonctionnalités :**
- Sélection des héros dans une grille 2×4 optimisée
- **3 builds prédéfinis par héros** (Facile / Normal / Difficile)
  - Basés sur les équipements officiels du jeu
  - Stats calculées dynamiquement depuis les équipements réels
  - Nombre de capacités variable selon la difficulté (1/3/6)
- Sélection des ennemis avec recherche par nom/numéro
- **Support des builds personnalisés** créés dans la Forge
- Configuration des règles : initiative D20, coups critiques, dégâts magiques
- Pourcentage de santé initiale par héros (pour tests de survie)
- Récapitulatif de formation avant lancement

**Utilité pour l'équilibrage :**
- Tester rapidement différentes compositions d'équipe
- Comparer les 3 niveaux de difficulté
- Valider la scalabilité des ennemis (2-4 joueurs)

### 🎮 Playtest Manuel (Sandbox V2)

Mode de simulation avancé avec contrôle total des actions pour tests d'équilibrage précis.

**Deux modes de jeu :**

#### Mode Initiative (règles officielles V3.0)
- Jets de D20 pour déterminer l'ordre des tours
- Héros prioritaires en cas d'égalité
- Affichage en grille unique triée par initiative

#### Mode Manuel (tests de scénarios)
- Sélection manuelle du personnage actif
- Actions multiples par tour :
  - ⚔️ Attaquer (une fois par tour)
  - 🔮 Utiliser une capacité
  - 🩸 Boire une potion (Petite ou Grande)
  - 🤝 Faire boire une potion à un allié (action exclusive)
- **Système undo/redo** pour explorer différentes stratégies
- Historique des états de jeu pour analyse

**Utilité pour l'équilibrage :**
- Reproduire des situations de jeu spécifiques
- Tester les edge cases et combinaisons de capacités
- Valider le système de jetons parade
- Analyser l'impact des coups critiques

### ⚙️ Forge des équipements

Éditeur de builds personnalisés pour expérimenter avec les combinaisons d'équipements.

**Fonctionnalités :**
- Sélection parmi **56 équipements officiels** (armes, armures, accessoires)
- **Slider séquentiel de capacités** (0-6) pour débloquer progressivement les pouvoirs
- Configuration des potions (quantités personnalisables)
- Sauvegarde des builds dans `custom_builds.csv`
- Comparaison avec les builds prédéfinis

**Utilité pour l'équilibrage :**
- Tester des combinaisons d'équipements non prévues
- Identifier les synergies puissantes ou faibles
- Calibrer le coût en sorts des capacités
- Valider l'impact des objets spéciaux (O-1 à O-4)

### ⚔️ Gestion des ennemis

Éditeur d'ennemis personnalisés pour tester de nouvelles créatures.

**Fonctionnalités :**
- Création d'ennemis avec statistiques personnalisées
- Configuration de la scalabilité multi-joueurs
- Attribution de capacités ennemies
- Sauvegarde dans `custom_enemies.csv`
- Intégration automatique dans la sélection d'équipes

**Utilité pour l'équilibrage :**
- Prototyper de nouveaux ennemis pour extensions
- Tester des mécaniques ennemies expérimentales
- Ajuster la courbe de difficulté par niveau

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

## Guide d'utilisation

### Workflow d'équilibrage typique

#### 1. Test rapide d'un combat

**Objectif :** Valider rapidement l'équilibre d'un ennemi contre une formation type.

```
🏰 Sélection
├─ Choisir 2-3 héros en difficulté Normal
├─ Sélectionner l'ennemi à tester
├─ Activer Initiative D20 et Critiques
└─ Lancer la simulation automatique
```

**Analyse :** Consulter les métriques (taux de survie, durée, consommation de ressources).

#### 2. Test approfondi avec contrôle manuel

**Objectif :** Reproduire un scénario problématique rapporté en playtest.

```
🏰 Sélection
├─ Configurer l'équipe exacte du playtest
└─ Désactiver l'initiative pour contrôle total

🎮 Playtest Manuel
├─ Sélectionner manuellement l'ordre des actions
├─ Utiliser undo/redo pour tester différentes stratégies
└─ Analyser l'impact des capacités dans le journal de combat
```

**Analyse :** Identifier les capacités déséquilibrées ou les combinaisons problématiques.

#### 3. Validation d'un nouvel équipement

**Objectif :** Tester l'impact d'un équipement avant ajout au jeu.

```
⚙️ Forge
├─ Ajouter l'équipement dans equipment.csv
├─ Créer un build custom avec cet équipement
└─ Sauvegarder le build

🏰 Sélection
├─ Sélectionner le héros avec le build custom
└─ Lancer des combats contre différents ennemis

🎮 Playtest Manuel
└─ Observer l'impact détaillé en conditions réelles
```

**Analyse :** Comparer les performances avec les builds prédéfinis (baseline).

#### 4. Calibrage de la difficulté multi-joueurs

**Objectif :** Vérifier que les ennemis s'adaptent bien au nombre de joueurs.

```
🏰 Sélection
├─ Test 1 : 2 héros + ennemi cible (configuration minimale)
├─ Test 2 : 3 héros + même ennemi (configuration standard)
├─ Test 3 : 4 héros + même ennemi (configuration maximale)
└─ Comparer les métriques de difficulté
```

**Analyse :** Vérifier que le taux de victoire reste cohérent (≈70% pour difficulté Normal).

---

## Architecture technique

### Structure modulaire

L'application suit une architecture MVC adaptée à Streamlit avec séparation stricte entre logique métier et interface.

```
periples-balance-workshop/
├── app.py                              # Application principale Streamlit
├── models/                             # Logique métier (business logic)
│   ├── character.py                    # Héros et ennemis (classes de base)
│   ├── abilities.py                    # Système de capacités
│   ├── enemy_ability.py                # Capacités ennemies
│   ├── rules_engine.py                 # Règles de jeu configurables
│   └── combat/                         # ⭐ Module de combat modulaire
│       ├── initiative_manager.py       # Jets de D20 et ordre des tours
│       ├── spell_manager.py            # Gestion centralisée des sorts
│       ├── combat_actions.py           # Attaques, capacités, potions
│       ├── turn_manager.py             # Gestion des tours + IA tactique
│       ├── combat_logger.py            # Journalisation des actions
│       └── combat_engine.py            # Orchestrateur principal
├── ui/                                 # Interface utilisateur
│   ├── styling.py                      # Thème visuel
│   └── components/                     # Composants UI modulaires
│       ├── hero_components.py          # Cartes héros + builds
│       ├── enemy_components.py         # Cartes ennemis
│       ├── forge_abilities_components.py  # Interface Forge
│       ├── sandbox_interface_v2.py     # Mode Playtest Manuel
│       └── enemy_editor.py             # Éditeur d'ennemis
├── utils/                              # Utilitaires
│   ├── data_loader.py                  # Chargement des CSV/Excel
│   ├── abilities_loader.py             # Import des capacités depuis Sorts.xlsx
│   └── paths.py                        # Gestion des chemins cross-platform
├── data/                               # Données du jeu
│   ├── heroes.csv                      # 8 héros officiels
│   ├── enemies.csv                     # 72 ennemis évolutifs
│   ├── equipment.csv                   # 56 équipements + 4 objets spéciaux
│   ├── ability_names.csv               # Noms officiels des capacités
│   ├── Sorts.xlsx                      # Données complètes des capacités
│   ├── Data_cards.xlsx                 # Données sources (backup)
│   ├── custom_builds.csv               # Builds personnalisés (Forge)
│   ├── custom_enemies.csv              # Ennemis personnalisés
│   ├── enemy_abilities.csv             # Capacités ennemies
│   └── images/                         # Images des personnages
│       ├── *.jpg                       # Portraits des héros
│       └── Images Bestiaire/           # Illustrations des ennemis (42 images)
└── hero_builds_data.py                 # Configuration des builds prédéfinis
```

### Système de combat (architecture refactorisée)

Le moteur de combat a été refactorisé en **7 modules spécialisés** (~1800 lignes) pour faciliter la maintenance et l'évolution.

**InitiativeManager** (`initiative_manager.py`)
- Jets de D20 pour tous les combattants
- Tri par ordre décroissant (initiative haute = joue en premier)
- Gestion des égalités (héros prioritaires, règle officielle page 26)

**SpellManager** (`spell_manager.py`)
- Compteur de sorts centralisé par personnage
- Initialisation depuis statistiques de base
- Décompte lors de l'utilisation des capacités
- Support du Bâton de puissance (O-2) : +1 utilisation

**CombatActions** (`combat_actions.py`)
- Exécution des attaques (jets de D20 + dégâts)
- Utilisation des capacités avec coût en sorts
- Gestion des potions (Petite/Grande, auto/allié)
- Support des objets spéciaux (O-1, O-3, O-4)
- Système de coups critiques (Nat 20 = ×2 dégâts, Nat 1 = échec)

**TurnManager** (`turn_manager.py`)
- Orchestration des tours (héros → ennemis)
- IA tactique pour distribution des dégâts
- Gestion des Pets invoqués (Kraor + O-3)
- Réinitialisation des jetons parade par tour

**CombatLogger** (`combat_logger.py`)
- Formatage des messages de combat
- Affichage des jets de dés (🎲)
- Logs contextuels pour capacités et objets spéciaux

**CombatEngine** (`combat_engine.py`)
- Orchestrateur principal
- Boucle de combat (jusqu'à victoire/défaite)
- Calcul des métriques finales
- Gestion de l'état global du combat

### Optimisations performance

**Cache Streamlit**
```python
@st.cache_data
def load_data():
    """Mise en cache des données statiques (CSV, Excel)"""
    # Chargement unique au démarrage
    # Réutilisation automatique entre reruns
```

**Calcul dynamique des stats**
- Stats de base (CSV) + bonus d'équipements = stats finales
- Pas de stats hardcodées, 100% calculé à la volée
- Garantit la cohérence avec les équipements officiels

**Session state optimisé**
- Stockage minimal : seulement les choix utilisateur
- Recalcul des builds à chaque rerun (données cachées)
- Historique undo/redo basé sur deepcopy d'états

---

## Système de jetons parade

Implémentation fidèle des règles V3.0 (page 26 du livre de règles).

### Fonctionnement

**Initialisation :**
- Chaque héros/ennemi commence avec **N jetons** (N = nombre de personnages dans le camp adverse)
- Exemple : 3 héros vs 2 ennemis → Héros ont 2 jetons, Ennemis ont 3 jetons

**Utilisation :**
- Lors d'une attaque réussie, la cible peut dépenser **1 jeton** pour annuler les dégâts
- Si plus de jetons, les dégâts sont appliqués normalement

**Rechargement :**
- Au **début du tour** d'un personnage, ses jetons sont **réinitialisés au maximum**
- Permet une rotation stratégique entre attaquer et se défendre

### Impact sur l'équilibrage

Cette mécanique crée un équilibre naturel :
- Les héros en infériorité numérique ont **plus de jetons** (meilleure défense)
- Les ennemis nombreux ont **moins de jetons** (plus vulnérables individuellement)
- Encourage la coordination des attaques pour épuiser les jetons

---

## Objets spéciaux (O-1 à O-4)

Les 4 objets spéciaux sont entièrement opérationnels dans le simulateur.

### O-1 : Gemme de pouvoir (Elneha)

**Effet :** Transforme les attaques physiques des formes Ours/Loup en dégâts magiques.

**Implémentation :**
- Détection automatique de la forme active (capacité 1 ou 101 pour Ours, 102 pour Loup)
- Conversion `attack_damage → magical_damage` dans `CombatActions`
- Log contextuel : "🔮 [Gemme de pouvoir] Attaque convertie en magie"

**Utilité équilibrage :** Tester l'impact des dégâts magiques contournant les armures physiques.

### O-2 : Bâton de puissance (Liarie)

**Effet :** +1 utilisation pour toutes les capacités magiques.

**Implémentation :**
- Bonus appliqué dans `SpellManager.initialize_spells()`
- Affecte uniquement les capacités avec `spell_cost > 0`
- Log au début du combat : "✨ [Bâton de puissance] +1 utilisation sur toutes les capacités"

**Utilité équilibrage :** Mesurer l'impact d'une capacité supplémentaire sur le taux de victoire.

### O-3 : Médaillon d'appel (Kraor)

**Effet :** Invoque un Pet (Précision 4, Dégâts magiques 4, Santé 15).

**Implémentation :**
- Pet créé automatiquement au début du combat
- Agit pendant la phase héros (via `TurnManager.pet_turn()`)
- Les ennemis peuvent cibler le Pet (IA tactique)
- Métriques séparées : survie du Pet, dégâts infligés

**Utilité équilibrage :** Valider l'équilibre d'un 9e combattant dans une équipe de 3 héros.

### O-4 : Lyre phœnix (Stèphe)

**Effet :** +4 sorts maximum + conversion de toutes les attaques en dégâts magiques.

**Implémentation :**
- Bonus de sorts dans `SpellManager.initialize_spells()`
- Conversion automatique dans `CombatActions.hero_attack()`
- Log : "🎶 [Lyre phœnix] Attaque convertie en magie"

**Utilité équilibrage :** Tester un héros full-magie avec ressources étendues.

---

## Métriques et analyse

### Métriques de combat

Après chaque simulation, le moteur calcule :

**Résultat global**
- Victoire/Défaite
- Nombre de rounds
- Temps de simulation

**Statistiques héros**
- Taux de survie (% héros vivants)
- PV restants par héros
- Sorts consommés
- Potions utilisées (Petites/Grandes)
- Capacités activées (avec détail par numéro)

**Statistiques ennemis**
- PV totaux infligés aux héros
- Capacités ennemies utilisées (si présentes)

**Statistiques Pets** (si invoqués)
- Survie du Pet
- Dégâts infligés par le Pet

### Indicateurs d'équilibrage

**Pour un combat équilibré en difficulté Normal :**
- Taux de victoire cible : **60-75%**
- Durée moyenne : **4-8 rounds**
- Héros survivants : **2-3 sur 3** (ou 3-4 sur 4)
- Consommation de ressources : **50-80%** (sorts + potions)

**Signaux de déséquilibre :**
- ⚠️ Victoire systématique en 2-3 rounds → Ennemi trop faible
- ⚠️ Défaite avec 0 survivant → Ennemi trop fort
- ⚠️ Aucune ressource consommée → Héros sur-équipés
- ⚠️ Héros ne peuvent pas attaquer → Capacités ennemies trop puissantes

---

## Développement et maintenance

### État du projet

**Application stable et fonctionnelle** – Version complète en production.

L'outil a atteint un état de maturité avec toutes les fonctionnalités critiques implémentées :
- ✅ Système de combat complet conforme aux règles V3.0
- ✅ Playtest manuel avec modes Initiative et Manuel
- ✅ Forge d'équipements et gestion d'ennemis personnalisés
- ✅ Architecture modulaire refactorisée
- ✅ Métriques d'équilibrage précises

**Évolutions futures :** Bien que l'application soit complète, des améliorations mineures restent possibles en fonction des besoins de l'équipe (visualisations, exports, nouvelles mécaniques de jeu).

### Contexte de développement

**Outil interne, pas un produit commercial**

Cette application est un outil de travail pour l'équipe de développement de Périples. Les priorités sont :
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
