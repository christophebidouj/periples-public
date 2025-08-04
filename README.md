# Périples Balance Workshop

**Simulateur pour l'équilibrage du jeu de société "Périples"**

## Présentation

Le Périples Balance Workshop est un outil de simulation développé pour le jeu de société **Périples** © Bastien LIAUTY. Il permet de tester l'équilibrage des combats, équipements, capacités spéciales et potions de santé.

### Objectifs
- Équilibrage des ennemis selon le nombre de joueurs
- Validation des règles de combat
- Test des équipements et builds personnalisés
- Simulation des capacités spéciales des héros
- Gestion des potions de santé
- Analyse statistique des combats

## Fonctionnalités

### Sélection des Équipes
- 12 héros avec formes d'Elneha
- 72 ennemis évolutifs selon le nombre de joueurs
- Interface avec images et statistiques détaillées
- Recherche d'ennemis par nom ou numéro
- Récapitulatif de formation avant combat

### Forge des Équipements
- 52 équipements répartis en 3 catégories (Armes, Armures, Accessoires)
- Système de capacités : 48 capacités (6 par héros)
- Système de potions : Petites (4 PV) et Grandes (PV max)
- Création de builds personnalisés combinant équipements, capacités et potions
- Interface avec grilles organisées pour la sélection
- Aperçu en temps réel des statistiques et coûts
- Sauvegarde des configurations personnalisées

### Moteur de Combat
- Implémentation des règles officielles V3.0
- IA pour l'utilisation des capacités et potions
- Gestion automatique des potions selon les points de vie
- Journal détaillé des actions de combat
- Calcul des métriques d'équilibrage

### Analyses et Métriques
- Taux de survie des héros
- Gestion de l'attrition (état des héros après combat)
- Durée de combat
- Utilisation des ressources (sorts, potions, capacités)
- Recommandations d'équilibrage
- Score global d'équilibrage

## Système de Capacités

### Interface
- Grille 3x2 pour visualiser les 6 capacités par héros
- Couleurs par type : Magique (violet) et Physique (orange)
- Sélection/désélection interactive
- Aperçu en temps réel des capacités sélectionnées

### Gestion des Capacités
- Respect des choix utilisateur pour les builds personnalisés
- Génération aléatoire pour les builds standard
- Exclusions spécifiques (ex: Kraor capacités 1 et 3 en combat)
- Intégration avec le système de coût en sorts

## Système de Potions

### Types de Potions
- **Petites potions** : +4 PV (limite : 3 par build)
- **Grandes potions** : restauration complète des PV (limite : 1 par build)

### Interface
- Grille 2x1 pour les deux types de potions
- Sélection par cycles pour les petites potions
- Toggle pour les grandes potions
- Aperçu des quantités sélectionnées

### Utilisation par l'IA
- Utilisation automatique si PV < 50%
- Choix optimal selon l'état du héros
- Intégration dans la séquence de combat
- Journal détaillé des utilisations

## IA Tactique

### Séquence de Combat
1. Évaluation et utilisation des potions si nécessaire
2. Analyse tactique et décision sur les capacités
3. Attaque physique (selon les règles)

### Logique de Décision
- **Potions** : Utilisation automatique selon les PV
- **Survie** : Priorité aux capacités de soin si équipe blessée
- **Zone** : Capacités de zone contre 3+ ennemis
- **Offensive** : Capacités d'attaque en combat standard
- **Économique** : Capacité la moins chère en dernier recours

### Règles d'Utilisation
- Respect des conditions de lancement (progression, coût en sorts)
- Application des limitations (usages par combat/jour)
- Impact sur l'attaque selon le type de capacité
- Exclusions spécifiques par personnage

## Structure du Projet

```
périples-balance-workshop/
├── app.py                          # Application principale Streamlit
├── models/
│   ├── character.py                # Modèles héros/ennemis
│   ├── abilities.py                # Système de capacités
│   ├── combat_engine.py            # Moteur de combat et IA
│   └── rules_engine.py             # Règles de jeu
├── ui/
│   ├── styling.py                  # Thème interface
│   └── components/                 # Composants interface
│       ├── hero_components.py
│       ├── equipment_components.py
│       ├── forge_abilities_components.py
│       ├── combat_components.py
│       └── sandbox_interface.py
├── utils/
│   ├── data_loader.py             # Chargement des données
│   ├── abilities_loader.py        # Import des capacités
│   └── stats_analyzer.py          # Analyse statistique
├── data/
│   ├── Data_cards.xlsx           # Données officielles
│   ├── Sorts.xlsx                # Capacités des héros
│   ├── heroes.csv                # Données héros
│   ├── enemies.csv               # Données ennemis
│   ├── equipment.csv             # Données équipements
│   └── images/                   # Images (optionnelles)
└── docs/
    └── README.md                 # Documentation
```

## Installation et Utilisation

### Prérequis
- Python 3.10+
- Streamlit 1.28+
- Pydantic 2.0+
- Pandas 2.0+

### Installation
```bash
git clone [url-du-repo]
cd periples-balance-workshop
pip install -r requirements.txt
streamlit run app.py
```

### Utilisation

#### Sélection des Équipes
1. Choisir 2+ héros dans la grille
2. Sélectionner les ennemis
3. Valider la formation
4. Configurer les règles de combat

#### Forge des Équipements
1. Sélectionner un héros
2. Choisir les équipements par catégorie
3. Sélectionner les capacités (1 à 6)
4. Configurer les potions
5. Sauvegarder le build personnalisé

#### Combat
1. Accéder aux "Chroniques"
2. Observer le combat automatique
3. Analyser les métriques et recommandations

## Équilibrage

### Métriques Importantes
- **Taux de survie** : Pourcentage de héros survivants
- **Durée de combat** : Nombre de rounds
- **Attrition** : État des héros après combat
- **Usage des ressources** : Utilisation des sorts, potions et capacités
- **Score global** : Évaluation générale de l'équilibrage

### Workflow d'Équilibrage
1. Tester différentes configurations d'équipes
2. Analyser les métriques de combat
3. Ajuster les statistiques selon les recommandations
4. Valider les builds personnalisés
5. Itérer jusqu'à obtenir un équilibrage satisfaisant

## Équipe et Contribution

- **Game Design** : Bastien LIAUTY (Créateur Périples)
- **Développement** : Christophe Bidouj

### Spécifications Techniques
- **Langage** : Python 3.10+
- **Interface** : Streamlit
- **Architecture** : Modulaire et extensible

## Licence

- **Jeu "Périples"** © Bastien LIAUTY - Tous droits réservés
- **Simulateur** : Usage autorisé pour le développement et les tests du jeu
- **Code source** : Développé par Christophe Bidouj

### Usage Autorisé
- Tests d'équilibrage pour l'équipe de développement
- Validation des règles et mécaniques
- Développement et amélioration du jeu

L'usage commercial ou la redistribution ne sont pas autorisés.

## Mode Sandbox

### Présentation
Le Mode Sandbox permet un contrôle manuel complet des combats pour les tests d'équilibrage avancés. Contrairement au combat automatique géré par l'IA, l'utilisateur contrôle tous les personnages (héros et ennemis) tour par tour.

### Objectifs
- Tester des cas limites et reproduire des situations spécifiques
- Valider l'équilibrage en contrôlant précisément les actions
- Déboguer des mécaniques de combat particulières
- Expérimenter avec différentes stratégies tactiques

### Fonctionnalités

#### Interface de Contrôle
- **Contrôle dual** : L'utilisateur contrôle alternativement héros et ennemis
- **Indication de faction** : Bannières visuelles distinctes (vert pour héros, rouge pour ennemis)
- **Tour par tour** : Chaque personnage peut effectuer une action à son tour
- **Système de guidance** : Messages contextuels pour guider l'utilisateur

#### Actions Disponibles
- **Attaque** : Sélection manuelle de la cible
- **Capacités spéciales** : Menu adaptatif selon les capacités du personnage (0-6 par héros)
- **Passer le tour** : Passage au personnage suivant
- **Options de débogage** : Possibilité de forcer certains effets pour les tests

#### Système d'Historique
- **Sauvegarde d'état** : Chaque action est sauvegardée automatiquement
- **Undo/Redo** : Possibilité de revenir en arrière ou refaire des actions
- **Navigation temporelle** : Visualisation de la position dans l'historique
- **États complets** : Sauvegarde de tous les paramètres (PV, équipements, sorts utilisés)

#### Workflow d'Utilisation
1. **Configuration** : Utilisation de l'onglet de sélection des équipes
2. **Lancement** : Bouton "Mode Sandbox" pour démarrer le mode manuel
3. **Initiative** : Génération automatique de l'ordre des tours
4. **Combat** : Contrôle manuel de chaque personnage à son tour
5. **Navigation** : Utilisation de l'historique pour tester différentes approches

### Intégration Technique
- **Réutilisation** : Utilise les mêmes modèles et moteur de combat que le mode automatique
- **Interface cohérente** : Même thème visuel que le reste de l'application
- **Session persistante** : Maintien de l'état de jeu pendant toute la session
- **Système de capacités** : Intégration complète avec le système de sorts existant

### Avantages pour l'Équilibrage
- **Reproductibilité** : Possibilité de reproduire exactement des situations problématiques
- **Tests exhaustifs** : Validation de tous les cas de figure possibles
- **Analyse fine** : Compréhension détaillée des mécaniques de combat
- **Itération rapide** : Modifications et tests immédiats grâce à l'historique

### Études d'Interface

Le développement du Mode Sandbox s'appuie sur des études d'interface détaillées comprenant :

#### Système de Guidance
- **Bannières contextuelles** avec indication d'étape (ex: "Étape 3/5")
- **Fil d'Ariane** montrant la progression (Setup → Initiative → Action → Cible → Confirmer)
- **Messages d'aide contextuelle** selon le personnage contrôlé
- **Conseils stratégiques** adaptés à la situation de combat

#### Interface de Contrôle des Capacités
- **Grille organisée** des capacités spéciales disponibles par héros
- **Indicateurs visuels** : coût en actions, usages restants, type de capacité
- **Actions de base** : Attaque, Défense, Passer le tour
- **Gestion des potions** : Interface dédiée avec compteurs visuels
- **Badges de statut** pour chaque capacité (disponible/utilisée/indisponible)

#### Principe de Développement
Le Mode Sandbox privilégie l'utilisation **d'éléments natifs Streamlit** pour garantir :
- **Fluidité** : Interactions responsives sans délais
- **Fiabilité** : Comportement prévisible et stable
- **Maintenabilité** : Code simple et facilement extensible
- **Compatibilité** : Fonctionnement optimal sur tous les navigateurs

L'interface s'appuie principalement sur les composants Streamlit standards (boutons, colonnes, conteneurs, sélecteurs) avec un styling CSS minimal pour préserver les performances et la stabilité.