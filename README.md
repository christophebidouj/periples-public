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
- **8 héros principaux** avec formes d'Elneha gérées en combat
- **3 builds prédéfinis par héros** (Facile, Normal, Difficile)
- **72 ennemis évolutifs** selon le nombre de joueurs
- **Interface grille 2x4** pour navigation optimisée
- Sélecteur de difficulté intégré pour chaque héros
- **Expander détails builds** : affichage des équipements, capacités et potions
- Recherche d'ennemis par nom ou numéro
- Récapitulatif de formation avant combat

### Système de Builds Prédéfinis

#### 3 Niveaux de Difficulté
- **🟢 Facile** : Équipements améliorés, statistiques renforcées
- **🔵 Normal** : Équipements standards, équilibrage de référence
- **🔴 Difficile** : Équipements basiques, challenge accru

#### Architecture Optimisée
- **Données pré-calculées** : Builds, équipements, capacités et potions calculés au démarrage
- **Cache Streamlit** : `@st.cache_data` pour équipements et capacités
- **Réactivité instantanée** : Callbacks natifs Streamlit avec données en mémoire
- **Aucune requête en cours d'usage** : CSV lu une seule fois au chargement

### Forge des Équipements
- **52 équipements** répartis en 3 catégories (Armes, Armures, Accessoires)
- **48 capacités spéciales** (6 par héros) avec noms officiels du livre de règles
- **Système de potions** : Petites (4 PV) et Grandes (PV max)
- **Builds personnalisés** combinant équipements, capacités et potions
- **Interface expanders natifs** Streamlit pour meilleure compatibilité
- **Les builds custom remplacent automatiquement les prédéfinis**

### Moteur de Combat
- **Implémentation des règles officielles** V3.0
- **Support des 3 builds** : Utilise automatiquement le niveau sélectionné ou le build custom
- **IA tactique** pour l'utilisation des capacités et potions
- **Système de jetons parade rechargeable** pour héros et ennemis
- **Journal détaillé** des actions de combat

### Mode Sandbox
- **Contrôle manuel complet** des combats pour tests d'équilibrage avancés
- **Interface proche du prototype** avec zones cliquables
- **Grille capacités 3x2** pour visualiser les 6 capacités par héros
- **Système d'historique** : Undo/Redo fonctionnels
- **Support des builds** : Utilise les builds sélectionnés (prédéfinis + custom)

## Nouveautés Récentes

### ✅ Système de Boutons Flexible (Dernière Mise à Jour)

#### Problème Résolu
- **Suppression du CSS hyper-agressif** qui forçait brutalement tous les boutons en bordeaux
- **Fin des conflits avec Streamlit** - système respectueux des types natifs
- **Conservation du thème bordeaux** comme style par défaut

#### Nouveau Système de Couleurs
- 🔴 **Bordeaux** (défaut) - thème de base conservé
- 🟢 **Vert** (succès/validation) - `success_button()`
- 🔵 **Bleu** (information/neutre) - `info_button()`
- 🟠 **Orange** (avertissement) - `warning_button()`
- 🔴 **Rouge** (danger/suppression) - `danger_button()`
- 🟣 **Violet** (capacités magiques) - `magic_button()`
- ⚫ **Gris** (neutre/désactivé) - `neutral_button()`
- 🟡 **Doré** (premium/spécial) - `gold_button()`

#### Usage Simple
```python
from ui.components.button_utils import success_button, danger_button, magic_button

# Boutons colorés
if success_button("✅ Valider", "btn_validate"):
    handle_validation()

if danger_button("🗑️ Supprimer", "btn_delete"):
    handle_deletion()

# Boutons contextuels
if create_contextual_button('combat', '⚔️ Attaque', 'btn_attack'):
    handle_combat()
```

### ✅ Capacités Officielles (Mise à Jour Récente)
- **Noms officiels** : Tous les noms de capacités mis à jour selon le livre de règles
- **Correspondance exacte** : P-1 Druide → "Forme d'ours", P-2 Mage → "Éclair magique", etc.
- **48 capacités** avec noms corrects pour les 8 héros principaux

### ✅ Optimisation Performance (Précédente)

#### Système de Cache Intelligent
- **Cache équipements** : `load_equipment_details_cache()` avec `@st.cache_data`
- **Cache capacités** : `load_abilities_details_cache()` pour tous les héros
- **Pré-calcul build détails** : Équipements, capacités et potions inclus dans `preloaded_builds`

#### Élimination des Requêtes Répétées
- **Plus de lecture CSV** en cours d'utilisation (équipements lus 1x au démarrage)
- **Plus de `DataLoader()`** créé à chaque affichage
- **Plus d'import répétés** de `get_abilities_for_hero`
- **Données en mémoire** : Affichage instantané des détails builds

#### Expander Détails Builds
- **Affichage complet** : Équipements avec stats, capacités avec coûts, potions
- **Performance optimisée** : Données pré-calculées, zéro latence
- **Support builds custom** : Calcul à la volée avec caches

### Migration 8 Héros (Précédente)
- **Supprimés** : P-9 à P-12 (pseudo-héros)
- **Conservés** : 8 héros principaux (P-1 à P-8)
- **Grille 2x4** optimisée
- **Session state** nettoyé automatiquement

## Architecture Technique

### Optimisations Récentes
- **Système de boutons flexible** : Évite les conflits CSS avec Streamlit
- **Système de cache Streamlit** : `@st.cache_data` pour données statiques
- **Pré-calcul complet** : Builds avec détails calculés une seule fois au chargement
- **Performance optimisée** : Élimination des lectures CSV et requêtes répétées
- **Expander détails** : Affichage instantané des équipements/capacités/potions

### Structure des Données
```python
# Structure des builds pré-calculés avec détails complets
preloaded_builds = {
    "P-1": [
        {
            'build_name': '🟢 Build Renforcé',
            'stats': {...},
            'build_details': {
                'equipment': [...],    # Détails complets équipements
                'abilities': [...],    # Détails complets capacités  
                'potions': {...}       # Quantités potions
            }
        },
        # ... Normal, Difficile
    ],
    # ... P-2 à P-8
}
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
2. Sélectionner le niveau de difficulté (réactivité en 1 clic)
3. **Cliquer sur l'expander** pour voir détails du build (équipements, capacités, potions)
4. Sélectionner les ennemis
5. Valider la formation et configurer les règles

#### Mode Sandbox
1. Configurer les équipes dans l'onglet "Sélection"
2. Accéder à l'onglet "Arène" (Mode Sandbox)
3. Générer l'initiative et contrôler manuellement chaque personnage
4. Utiliser l'historique pour tester différentes approches

#### Utilisation des Boutons Colorés
```python
# Import des utilitaires
from ui.components.button_utils import (
    ButtonStyle, success_button, danger_button, 
    magic_button, create_contextual_button
)

# Boutons spécialisés
if success_button("✅ Sauvegarder", "btn_save"):
    save_data()

if danger_button("🗑️ Reset", "btn_reset"):
    reset_data()

# Boutons contextuels
if create_contextual_button('abilities', '🔮 Lancer Sort', 'btn_cast'):
    cast_spell()
```

## Structure du Projet

```
périples-balance-workshop/
├── app.py                          # Application principale (version 8 héros)
├── models/
│   ├── character.py                # Modèles héros/ennemis avec système parade
│   ├── abilities.py                # Système de capacités
│   ├── combat_engine.py            # Moteur de combat et IA
│   └── rules_engine.py             # Règles de jeu
├── ui/
│   ├── styling.py                  # Thème interface AVEC SYSTÈME FLEXIBLE
│   └── components/                 # Composants interface
│       ├── hero_components.py      # Composants héros OPTIMISÉS avec cache
│       ├── ui_elements.py          # Éléments UI PROPRES (sans forçage CSS)
│       ├── button_utils.py         # NOUVEAU - Utilitaires boutons colorés
│       ├── forge_abilities_components.py  # Interface capacités/potions
│       └── sandbox_interface.py    # Mode Sandbox
├── utils/
│   ├── data_loader.py             # Chargement des données (version 8 héros)
│   └── abilities_loader.py        # Import des capacités
├── data/
│   ├── heroes.csv                # 8 héros principaux
│   ├── enemies.csv               # Données ennemis
│   ├── equipment.csv             # 52 équipements avec détails
│   ├── ability_names.csv         # CAPACITÉS OFFICIELLES (noms du livre de règles)
│   └── images/                   # Images JPG optimisées
└── hero_builds_data.py           # Builds prédéfinis détaillés P-1 à P-8
```

## Équilibrage et Métriques

### Workflow d'Équilibrage
1. Tester les 3 niveaux de difficulté avec différentes configurations
2. **Consulter détails builds** via expanders pour comprendre les compositions
3. Analyser les métriques de combat (taux de survie, durée, ressources)
4. Ajuster les builds personnalisés avec boutons colorés appropriés
5. Utiliser le Mode Sandbox pour tests précis
6. Itérer jusqu'à obtenir un équilibrage satisfaisant

### Métriques Importantes
- **Taux de survie** : Pourcentage de héros survivants
- **Durée de combat** : Nombre de rounds
- **Usage des ressources** : Utilisation des sorts, potions et capacités
- **Analyse par difficulté** : Comparaison des performances entre builds

## Notes Développement

### Performance et Architecture
- **Système de boutons flexible** : Compatible PyInstaller, évite les conflits Streamlit
- **Cache Streamlit** : Utilisé pour données statiques (équipements, capacités)
- **Pré-calcul** : Privilégier le calcul au démarrage vs calcul à la demande
- **Session state minimal** : Éviter de stocker des données lourdes
- **Callbacks natifs** : Utiliser `on_change` pour réactivité instantanée

### Système de Boutons
- **CSS non-agressif** : Évite le forçage brutal avec `!important`
- **Classes ciblées** : Styles appliqués via attributs `data-*`
- **Compatibilité** : Respecte les types Streamlit (`primary`, `secondary`)
- **Extensibilité** : Facile d'ajouter de nouveaux styles

### Compatibilité PyInstaller
- **Imports conditionnels** : `try/except` pour modules optionnels
- **Chemins relatifs** : `data/` pour fichiers CSV et images
- **Pas de dépendances lourdes** : Privilégier stdlib Python
- **Boutons natifs** : Système compatible compilation

### Code Style
- **Fonctions courtes** : Lisibilité pour débutants Python
- **Cache documenté** : `@st.cache_data` avec commentaires
- **Gestion erreurs** : `try/except` avec fallbacks gracieux
- **Boutons sémantiques** : Usage contextuel des couleurs

## Équipe et Contribution

- **Game Design** : Bastien LIAUTY (Créateur Périples)
- **Développement** : Christophe Bidouj

### Spécifications Techniques
- **Langage** : Python 3.10+
- **Interface** : Streamlit natif optimisé avec callbacks
- **Architecture** : Cache Streamlit + pré-calcul + système de boutons flexible
- **Déploiement** : Compatible PyInstaller

## Licence

- **Jeu "Périples"** © Bastien LIAUTY - Tous droits réservés
- **Simulateur** : Usage autorisé pour le développement et les tests du jeu
- **Code source** : Développé par Christophe Bidouj

### Usage Autorisé
- Tests d'équilibrage pour l'équipe de développement
- Validation des règles et mécaniques
- Développement et amélioration du jeu
- Tests de progression de difficulté entre les 3 builds prédéfinis

L'usage commercial ou la redistribution ne sont pas autorisés.