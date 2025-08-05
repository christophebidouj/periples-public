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

## Mode Sandbox

### Présentation
Le Mode Sandbox permet un contrôle manuel complet des combats pour les tests d'équilibrage avancés. Contrairement au combat automatique géré par l'IA, l'utilisateur contrôle tous les personnages (héros et ennemis) tour par tour.

### Objectifs
- Tester des cas limites et reproduire des situations spécifiques
- Valider l'équilibrage en contrôlant précisément les actions
- Déboguer des mécaniques de combat particulières
- Expérimenter avec différentes stratégies tactiques

### Interface Utilisateur

#### Système de Guidance
- **Bannière contextuelle** : Affichage coloré avec titre, description et badge d'étape
- **Fil d'Ariane** : 5 étapes visuelles (Setup → Initiative → Action → Cible → Confirmer)
- **Messages d'aide** : Conseils stratégiques selon le personnage actif
- **Progression visuelle** : Étapes complétées/actives/à venir clairement identifiées

#### Interface de Combat

##### Panneau Personnage
- **En-tête coloré** : Nom du personnage avec indicateur de faction
- **Stats en temps réel** : PV, ATT, DEF, MAG avec couleurs dynamiques
- **État de santé** : Codes couleur selon le pourcentage de PV restants
- **Indication de tour** : Personnage actif clairement identifié

##### Capacités Spéciales
- **Grille 3x2** : 6 emplacements pour les capacités du héros
- **Cartes cliquables** : Zones entières cliquables (pas de boutons internes)
- **Badges d'état** : Disponible (✅) / Indisponible (❌) avec compteurs
- **Types visuels** : Magique (🔮) / Physique (⚔️) avec couleurs distinctes
- **Informations détaillées** : Coût, description, conditions d'utilisation

##### Système de Potions
- **4 emplacements** : Soin, Force, Vide, Vitesse
- **Compteurs visuels** : Quantités restantes clairement affichées
- **Zones cliquables** : Utilisation directe pour potions disponibles
- **États différenciés** : Actif/Inactif/Placeholder selon le type

#### Actions de Base
- **Boutons standards limités** : Seulement pour actions principales
- **Actions disponibles** : Attaquer, Capacité, Passer le tour
- **Feedback immédiat** : Messages de confirmation des actions
- **Interface épurée** : Minimal de boutons standards selon le prototype

### Fonctionnalités Avancées

#### Contrôle Dual
- **Alternance factions** : L'utilisateur contrôle héros ET ennemis
- **Indication visuelle** : Bannières distinctes par faction (vert/rouge)
- **Tour par tour** : Chaque personnage agit individuellement
- **Liberté totale** : Aucune restriction sur les choix tactiques

#### Système d'Historique
- **Sauvegarde automatique** : Chaque action est enregistrée
- **Navigation temporelle** : Undo/Redo fonctionnels
- **États complets** : PV, sorts, équipements, potions sauvegardés
- **Description des actions** : Historique lisible des modifications
- **Reset global** : Possibilité de recommencer le combat

#### Journal de Combat
- **Suivi détaillé** : Toutes les actions enregistrées chronologiquement
- **Format lisible** : Messages clairs et structurés
- **Intégration capacités** : Utilisation des sorts et potions trackée
- **Résultats des actions** : Dégâts, soins, effets appliqués

### Workflow d'Utilisation

#### Phase 1 : Configuration
1. **Détection automatique** : Utilise les équipes sélectionnées dans l'onglet principal
2. **Préparation des builds** : Application des builds custom et capacités
3. **Validation** : Vérification de la configuration (2+ héros, 1+ ennemi)
4. **Initialisation** : Remise à zéro des stats de combat

#### Phase 2 : Initiative
1. **Génération aléatoire** : Jet d'initiative pour tous les combattants
2. **Ordre de tour** : Tri par initiative décroissante
3. **Affichage** : Liste ordonnée visible dans le journal
4. **Transition** : Passage automatique au combat

#### Phase 3 : Combat Manuel
1. **Tour actif** : Affichage du personnage dont c'est le tour
2. **Interface contextuelle** : Panneaux adaptés à la faction (héros/ennemi)
3. **Actions disponibles** : Capacités, potions, actions de base
4. **Validation** : Confirmation et application des effets
5. **Passage au suivant** : Rotation automatique des tours

#### Phase 4 : Navigation
1. **Historique accessible** : Boutons Undo/Redo toujours disponibles
2. **Journal consultable** : Historique des 10 dernières actions
3. **Reset possible** : Recommencer le combat à tout moment
4. **État persistant** : Sauvegarde maintenue pendant la session

### Intégration Technique

#### Réutilisation du Système Existant
- **Modèles identiques** : Utilise les mêmes classes Character/Enemy
- **Moteur de combat** : Réutilise les mécaniques de dégâts/soins
- **Système de capacités** : Intégration complète avec les 48 capacités
- **Builds custom** : Support total des configurations personnalisées

#### Interface Streamlit Native
- **Composants standards** : 100% Streamlit natif pour la stabilité
- **Zones colorées** : st.success/warning/error/info pour la guidance
- **Métriques** : st.metric() pour les statistiques en temps réel
- **Colonnes** : st.columns() pour les layouts en grille
- **Expanders** : Pour les informations détaillées optionnelles

#### Gestion d'État
- **Session state** : Persistance complète entre les interactions
- **Copies profondes** : Sauvegarde sécurisée des états de jeu
- **Clés uniques** : Évite les conflits entre les composants
- **Réactivité** : st.rerun() pour la mise à jour immédiate

### Avantages pour l'Équilibrage

#### Tests Reproductibles
- **Scénarios fixes** : Possibilité de reproduire exactement une situation
- **Validation précise** : Test de chaque mécanisme individuellement
- **Documentation** : Historique complet des actions pour analyse
- **Comparaisons** : Tests A/B avec navigation temporelle

#### Analyses Détaillées
- **Granularité maximale** : Contrôle action par action
- **Métriques précises** : Suivi exact des ressources (PV, sorts, potions)
- **Patterns tactiques** : Identification des stratégies optimales
- **Points de rupture** : Détection des déséquilibres critiques

#### Flexibilité Totale
- **Liberté stratégique** : Aucune contrainte d'IA
- **Tests exhaustifs** : Exploration de toutes les possibilités
- **Modifications en temps réel** : Ajustements immédiats visibles
- **Validation règles** : Vérification des mécaniques de jeu

### Interface Responsive

#### Adaptation Automatique
- **Grilles flexibles** : Colonnes qui s'adaptent à la largeur d'écran
- **Contenus scrollables** : Journal et historique avec défilement
- **Boutons full-width** : Utilisation optimale de l'espace disponible
- **Textes adaptatifs** : Troncature intelligente des descriptions longues

#### Performance Optimisée
- **Chargement minimal** : Seuls les composants nécessaires sont affichés
- **Mise à jour ciblée** : Rerun uniquement lors d'actions utilisateur
- **Cache intelligent** : Réutilisation des calculs de stats
- **Navigation fluide** : Transitions rapides entre les phases

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
│       └── sandbox_interface.py    # Mode Sandbox (nouveau)
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

#### Combat Automatique
1. Accéder aux "Chroniques"
2. Observer le combat automatique
3. Analyser les métriques et recommandations

#### Mode Sandbox
1. Configurer les équipes dans l'onglet "Sélection"
2. Accéder à l'onglet "Arène" (Mode Sandbox)
3. Générer l'initiative
4. Contrôler manuellement chaque personnage à son tour
5. Utiliser l'historique pour tester différentes approches

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
5. Utiliser le Mode Sandbox pour tests précis
6. Itérer jusqu'à obtenir un équilibrage satisfaisant

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