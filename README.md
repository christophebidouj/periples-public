# Périples Balance Workshop

**Simulateur pour l'équilibrage du jeu de société "Périples"**

## Présentation

Le Périples Balance Workshop est un outil de simulation développé pour le jeu de société **Périples** © Bastien LIAUTY. Il permet de tester l'équilibrage des combats, équipements, capacités spéciales et potions de santé avec un système entièrement basé sur des équipements authentiques.

### Objectifs
- Équilibrage des ennemis selon le nombre de joueurs
- Validation des règles de combat avec système de jetons parade rechargeable
- Test des équipements et builds personnalisés basés sur 56 équipements réels
- Simulation des capacités spéciales des héros (système séquentiel 1→6)
- Gestion des potions de santé et objets spéciaux uniques
- Analyse statistique des combats incluant les Pets invoqués

## Fonctionnalités Principales

### Sélection des Équipes
- **8 héros principaux** avec formes d'Elneha gérées en combat
- **3 builds prédéfinis par héros** basés sur équipements réels (Facile/Normal/Difficile)
- **72 ennemis évolutifs** selon le nombre de joueurs
- **Interface grille 2x4** pour navigation optimisée
- Sélecteur de difficulté intégré pour chaque héros
- **Expander détails builds** : affichage des équipements, capacités et potions
- Recherche d'ennemis par nom ou numéro
- Récapitulatif de formation avant combat

### Système de Builds Authentiques

#### 3 Niveaux de Difficulté
- **🟢 Facile** : Équipements renforcés + objets spéciaux, 6 capacités
- **🔵 Normal** : Équipements standards, 3 capacités
- **🔴 Difficile** : Équipements basiques, 1 capacité

#### Architecture Optimisée
- **Calcul depuis équipements réels** : Stats calculées dynamiquement depuis 56 équipements
- **Cache Streamlit** : `@st.cache_data` pour équipements et capacités
- **Réactivité instantané** : Callbacks natifs Streamlit avec données en mémoire
- **Plus de stats hardcodées** : Système 100% authentique

### Forge des Équipements Modernisée
- **56 équipements** répartis en 3 catégories (Armes, Armures, Accessoires)
- **48 capacités spéciales** avec noms officiels du livre de règles
- **Interface slider séquentiel** : Capacités 0-6 au lieu de checkboxes individuelles
- **Système de potions** : Petites (4 PV) et Grandes (PV max)
- **Builds personnalisés** combinant équipements, capacités et potions
- **Comparaison builds prédéfinis** : Référence pour équilibrage

### Moteur de Combat Avancé
- **Implémentation des règles officielles** V3.0
- **Support des 3 builds** : Utilise automatiquement le niveau sélectionné ou le build custom
- **IA tactique** pour l'utilisation des capacités et potions
- **Système de jetons parade rechargeable** pour héros et ennemis
- **Support complet des Pets** invoqués en combat
- **Journal détaillé** des actions avec jets de dés affichés

### 4 Objets Spéciaux Opérationnels

#### O-1 : Gemme de pouvoir (Elneha)
- **Effet** : Formes d'ours/loup → attaques magiques
- **Combat** : Transformation automatique + conversion des dégâts

#### O-2 : Baton de puissance (Liarie)
- **Effet** : +1 utilisation pour toutes les capacités magiques
- **Combat** : Bonus appliqué au début du combat

#### O-3 : Médaillon d'appel (Kraor)
- **Effet** : Invoque un Pet (Précision 4, Dégâts magiques 4, Santé 15)
- **Combat** : Pet agit avec les héros, peut être ciblé par les ennemis

#### O-4 : Lyre phoenix (Stèphe)
- **Effet** : +4 sorts + toutes les attaques → dégâts magiques
- **Combat** : Conversion automatique + logs contextuels

### Mode Sandbox
- **Contrôle manuel complet** des combats pour tests d'équilibrage avancés
- **Interface proche du prototype** avec zones cliquables
- **Grille capacités 3x2** pour visualiser les 6 capacités par héros
- **Système d'historique** : Undo/Redo fonctionnels
- **Support des builds** : Utilise les builds sélectionnés (prédéfinis + custom)

## État Actuel du Projet

### ✅ **FONCTIONNALITÉS COMPLÈTES**

#### Systèmes Opérationnels
- ✅ **Système de combat** : Entièrement fonctionnel avec toutes les règles V3.0
- ✅ **Gestion des sorts** : Système centralisé stable
- ✅ **Objets spéciaux** : 4/4 objets opérationnels en combat
- ✅ **Support Pets** : Invocation + combat + métriques complètes
- ✅ **Système parade** : Jetons rechargeables pour héros et ennemis
- ✅ **Builds authentiques** : Calcul depuis 56 équipements réels

#### Interface Utilisateur
- ✅ **Navigation optimisée** : Grille 2x4 héros + recherche ennemis
- ✅ **Forge modernisée** : Slider séquentiel capacités 0-6
- ✅ **Mode Sandbox** : Contrôle manuel complet
- ✅ **Cache performant** : Streamlit optimisé

### 🔄 **AMÉLIORATION PRÉVUE : REFACTORISATION**

#### Problème Identifié
- **combat_engine.py** : 978 lignes (fichier trop volumineux)
- **Impact** : Difficile à maintenir et travailler avec IA
- **Solution** : Split en 5 fichiers modulaires

#### Plan de Refactorisation
```
models/combat/
├── spell_manager.py      # ~120 lignes - Gestion sorts centralisée
├── combat_actions.py     # ~200 lignes - Attaques + capacités + pets
├── turn_manager.py       # ~220 lignes - Tours + IA tactique
├── combat_logger.py      # ~180 lignes - Logs + formatage
└── combat_engine.py      # ~250 lignes - Orchestrateur + résultats
```

#### Bénéfices Attendus
- Fichiers gérables pour le travail avec IA (120-250 lignes vs 978)
- Maintenance simplifiée avec responsabilités claires
- Architecture plus évolutive
- Conservation de toutes les fonctionnalités existantes

## Architecture Technique

### Optimisations Actuelles
- **Système authentique** : 100% basé sur équipements réels, 0% stats hardcodées
- **Cache Streamlit optimisé** : `@st.cache_data` pour données statiques
- **VirtualAbility** : Évite conflits Pydantic pour capacités spéciales
- **Interface séquentielle** : Slider moderne pour capacités
- **Support Pets complet** : Gestion combat + métriques

### Structure Actuelle
```
périples-balance-workshop/
├── app.py                          # Application principale (VERSION MIGRÉE)
├── models/
│   ├── character.py                # VirtualAbility + système parade + objets spéciaux
│   ├── abilities.py                # Système de capacités séquentielles
│   ├── combat_engine.py            # ⚠️ 978 lignes - À refactoriser
│   └── rules_engine.py             # Règles de jeu
├── ui/
│   ├── styling.py                  # Thème interface
│   └── components/                 # Composants interface
│       ├── hero_components.py      # MIGRÉ - Calcul depuis équipements réels
│       ├── ui_elements.py          # Éléments UI propres
│       ├── button_utils.py         # Utilitaires boutons colorés
│       ├── forge_abilities_components.py  # MIGRÉ - Interface slider séquentiel
│       └── sandbox_interface.py    # Mode Sandbox
├── utils/
│   ├── data_loader.py             # Chargement des données (version 8 héros)
│   └── abilities_loader.py        # Import des capacités
├── data/
│   ├── heroes.csv                # 8 héros principaux
│   ├── enemies.csv               # Données ennemis
│   ├── equipment.csv             # 56 équipements complets (52 + 4 objets spéciaux)
│   ├── ability_names.csv         # Capacités officielles (noms du livre de règles)
│   └── images/                   # Images JPG optimisées
└── hero_builds_data.py           # NETTOYÉ - Builds authentiques sans stats temporaires
```

### Structure Post-Refactorisation (Prévue)
```
périples-balance-workshop/
├── app.py                          # Application principale
├── models/
│   ├── character.py                # Classes de base
│   ├── abilities.py                # Système capacités
│   ├── rules_engine.py             # Règles de jeu
│   └── combat/                     # ⭐ NOUVEAU - Module combat modulaire
│       ├── spell_manager.py        # Gestion sorts centralisée
│       ├── combat_actions.py       # Attaques + capacités + pets
│       ├── turn_manager.py         # Tours + IA tactique
│       ├── combat_logger.py        # Logs + formatage
│       └── combat_engine.py        # Orchestrateur allégé
├── ui/ [inchangé]
├── utils/ [inchangé]
├── data/ [inchangé]
└── hero_builds_data.py [inchangé]
```

## Installation et Utilisation

### Prérequis
- Python 3.10+
- Streamlit 1.28+ (callbacks requis >= 1.12)
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
1. Choisir 2+ héros dans la grille 2x4
2. Sélectionner le niveau de difficulté (stats calculées depuis équipements)
3. **Cliquer sur l'expander** pour voir détails authentiques du build
4. Sélectionner les ennemis
5. Valider la formation et configurer les règles

#### Forge des Équipements
1. Sélectionner héros et voir ses stats de base
2. **Utiliser le slider 0-6** pour choisir le niveau de capacités
3. Sélectionner équipements parmi les 56 disponibles
4. Configurer potions (Petites/Grandes)
5. Sauvegarder le build custom

#### Mode Sandbox
1. Configurer les équipes dans l'onglet "Sélection"
2. Accéder à l'onglet "Arène" (Mode Sandbox)
3. Générer l'initiative et contrôler manuellement chaque personnage
4. Utiliser l'historique pour tester différentes approches

## Équilibrage et Métriques

### Workflow d'Équilibrage
1. Tester les 3 niveaux de difficulté avec calcul depuis équipements réels
2. **Consulter détails builds** via expanders pour voir équipements authentiques
3. Analyser les métriques de combat (taux de survie, durée, ressources)
4. **Utiliser le slider capacités** pour builds personnalisés
5. **Tester objets spéciaux** : O-1 (formes), O-2 (bonus), O-3 (pets), O-4 (magie)
6. Utiliser le Mode Sandbox pour tests précis

### Métriques Importantes
- **Taux de survie** : Héros + Pets survivants
- **Durée de combat** : Nombre de rounds
- **Usage des ressources** : Utilisation des sorts, potions et capacités
- **Objets spéciaux** : Impact des 4 objets uniques
- **Pets** : Performance des créatures invoquées

## Notes Développement

### État Post-Migration
- **Stats authentiques** : Calculées depuis 56 équipements réels
- **Capacités séquentielles** : Interface slider 0-6 moderne
- **VirtualAbility** : Solution élégante pour capacités spéciales
- **Cache optimisé** : Données pré-calculées pour réactivité
- **Support Pets complet** : Combat + métriques + logs

### Compatibilité PyInstaller
- **Imports conditionnels** : `try/except` pour modules optionnels
- **Chemins relatifs** : `data/` pour fichiers CSV et images
- **VirtualAbility** : Compatible compilation (pas de validation Pydantic)
- **Système authentique** : Basé sur données locales

### Roadmap Technique
1. **Phase 1** : Refactorisation combat_engine.py (5 fichiers modulaires)
2. **Phase 2** : Optimisation logs de combat
3. **Phase 3** : Extension système Pets (autres héros)
4. **Phase 4** : Tests de régression et validation

## État du Système

### ✅ Complètement Fonctionnel
- **Migration builds** : 100% basé sur équipements réels
- **4 objets spéciaux** : Tous opérationnels en combat
- **Système Pets** : Invocation + combat + métriques
- **Interface moderne** : Slider séquentiel pour capacités
- **Cache optimisé** : Performance maximale
- **Gestion des sorts** : Système centralisé stable

### 🔄 Améliorations Prévues
- **Refactorisation** : combat_engine.py → 5 fichiers modulaires
- **Optimisation** : Logs de combat plus concis
- **Extension** : Système Pets pour autres héros
- **Documentation** : Guide utilisateur intégré

## Équipe et Contribution

- **Game Design** : Bastien LIAUTY (Créateur Périples)
- **Développement** : Christophe Bidouj

### Spécifications Techniques Actuelles
- **Langage** : Python 3.10+
- **Interface** : Streamlit natif optimisé avec callbacks
- **Architecture** : Cache Streamlit + calcul équipements réels + VirtualAbility
- **Déploiement** : Compatible PyInstaller

## Licence

- **Jeu "Périples"** © Bastien LIAUTY - Tous droits réservés
- **Simulateur** : Usage autorisé pour le développement et les tests du jeu
- **Code source** : Développé par Christophe Bidouj

### Usage Autorisé
- Tests d'équilibrage pour l'équipe de développement
- Validation des règles et mécaniques avec équipements authentiques
- Développement et amélioration du jeu
- Tests de progression de difficulté entre les 3 builds basés sur équipements réels
- Expérimentation avec les 4 objets spéciaux et système de Pets

L'usage commercial ou la redistribution ne sont pas autorisés.