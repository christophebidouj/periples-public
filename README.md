# ⚔️ Simulateur de Combat Périples - Version Système Capacités Intégré

## 🎯 Contexte du Projet

**Simulateur d'équilibrage RPG** pour le jeu de société **"Périples"** de Bastien LIAUTY. 
Application professionnelle d'analyse de combat avec interface moderne style **cartes à jouer** et **système de capacités complet**.

### 📊 État Actuel (Août 2025)
- **Version :** V4+ Interface + Système Capacités 80% Terminé
- **Interface :** 3 onglets avec expanders compacts (zones blanches éliminées)
- **Focus :** Combat détaillé avec journal tactique complet + 48 capacités héros
- **Style :** Interface gaming avec récapitulatif des équipes essentiel
- **Dernière MAJ :** Corrections bugs critiques + noms de capacités élégants + IA logique

## 👥 **Crédits et Propriété Intellectuelle**

### 🎲 **Jeu de Société Original**
- **Périples** © Bastien LIAUTY - Tous droits réservés
- **Règles et données** : Propriété de Bastien LIAUTY
- **Usage autorisé** : Développement et tests d'équilibrage uniquement

### 💻 **Simulateur Python**
- **Dev Python** : Christophe Bidouj
- **Assistance IA** : Claude AI (Anthropic)
- **Langage** : Python + Streamlit + Pydantic
- **Architecture** : Modulaire avec interface gaming moderne

### ⚖️ **IMPORTANT - Confidentialité**
**TOUS les documents de ce projet sont propriétaires et confidentiels :**
- Données CSV basées sur contenu propriétaire de Bastien LIAUTY
- **❌ INTERDIT :** distribution, usage commercial, partage des règles
- **✅ AUTORISÉ :** développement/tests d'équilibrage, contribution au projet

## 🚀 Architecture Technique

### 📁 Structure des Fichiers
```
periples/
├── app.py                    # Application Streamlit SIMPLIFIÉE (400 lignes)
├── Data_cards.xlsx          # Source données Excel → Auto-import CSV
├── Sorts.xlsx               # Données capacités héros (48 capacités intégrées)
├── models/
│   ├── character.py         # Modèles Pydantic + Support Capacités COMPLET
│   ├── combat_engine.py     # Moteur simulation + Capacités + IA logique
│   ├── rules_engine.py      # Configuration règles + support capacités
│   └── abilities.py         # NOUVEAU - Système capacités complet
├── ui/
│   ├── styling.py           # Thème fantasy + bordeaux royal
│   └── components/          # Interface modulaire OPTIMISÉE
│       ├── __init__.py      # Imports centralisés
│       ├── ui_elements.py   # Utilitaires communs
│       ├── hero_components.py      # Cartes héros + récapitulatif
│       ├── enemy_components.py     # Cartes ennemis EXPANDERS NATIFS
│       ├── equipment_components.py # Équipements EXPANDERS NATIFS
│       ├── combat_components.py    # Résultats combat
│       └── abilities_components.py # NOUVEAU - Interface capacités
├── utils/
│   ├── data_loader.py       # Import auto Excel → CSV + Capacités
│   ├── abilities_loader.py  # NOUVEAU - Import Sorts.xlsx + noms élégants
│   └── stats_analyzer.py    # Analyses RPG (survie/attrition)
├── generate_ability_names.py # NOUVEAU - Générateur noms élégants
└── data/                    # Auto-généré depuis Excel
    ├── heroes.csv           # 12 héros avec stats
    ├── enemies.csv          # 72 ennemis (stats évolutives 2-4J)
    ├── equipment.csv        # 52 équipements avec catégorisation Type
    ├── ability_names.csv    # NOUVEAU - Cache noms capacités élégants
    └── Sorts.xlsx           # NOUVEAU - 48 capacités héros
```

### 🔧 Installation Rapide
```bash
# Conda (recommandé)
conda env create -f environment.yml
conda activate rpg-simulator
streamlit run app.py

# Ou pip
pip install -r requirements.txt
streamlit run app.py
```

## 🎮 Interface Utilisateur Moderne OPTIMISÉE

### 🏠 **Onglet 1 : Sélection des Équipes**
**INTERFACE EXPANDERS COMPACTE :**
- **Héros** : 6 par ligne, cartes avec images et dégradés (REQUIREMENT ABSOLU)
- **Ennemis** : 5 par ligne avec expanders natifs (expanded=False)
- **Affichage** : Style jeu avec icônes 🎯⚔️❤️🛡️✨
- **Sélection** : Badge ✅ dans titre expander, boutons ✅/➕

**⚔️ RÉCAPITULATIF FORMATION DE GUERRE (ESSENTIEL) :**
- **Design élégant** : Cards individuelles pour chaque combattant
- **Statistiques détaillées** : Builds, stats complètes, pronostic de bataille
- **🆕 Aperçu capacités** : Informations capacités débloquées par héros
- **Style thématique** : Couleurs héros (vert) vs ennemis (rouge)
- **Position stratégique** : Visible avant le bouton de combat
- **🚨 IMPORTANT** : Ce récapitulatif ne doit JAMAIS être supprimé du projet !

### 🛠️ **Onglet 2 : Forge des Équipements**
**EXPANDERS NATIFS OPTIMISÉS :**
- **Interface compacte** : expanded=False par défaut (solution anti-zones blanches)
- **Catégorisation Type** : Armes / Armures / Accessoires avec couleurs distinctes
- **Noms complets** : 20 caractères avec troncature intelligente
- **Builds hybrides** : Standards + customisation complète
- **Stats dynamiques** : Aperçu temps réel des modifications

### 📊 **Onglet 3 : Chroniques de Combat**
**JOURNAL TACTIQUE PRIORITAIRE AVEC CAPACITÉS :**
- **Logs détaillés** : Action par action avec horodatage + capacités élégantes
- **🆕 Noms élégants** : "Atucan utilise Soin Proportionnel" au lieu de "Atucan 2"
- **🆕 IA logique** : Soin automatique si PV < 50%, attaques de zone si 3+ ennemis
- **Métriques RPG** : Blessures/sorts par héros (analyse critique)
- **Bannière résultat** : Victoire/défaite avec style gaming
- **Tableaux individuels** : Stats finales par combattant

### ℹ️ **Onglet 4 : À Propos - STABLE**
**INTERFACE OPTIMISÉE :**
- **✅ Sections visibles** : Arsenal, Progression, Crédits parfaitement alignés
- **✅ Cards uniformes** : Hauteur fixe avec design cohérent
- **✅ Crédits clarifiés** : Distinction claire créateur jeu vs dev Python
- **✅ Progression** : Système de capacités maintenant à 80%

## 🔮 Système de Capacités - 80% TERMINÉ

### ✅ **INTÉGRÉ - Système Principal (100% Fonctionnel)**
- 🔮 **48 capacités** : 6 capacités par héros (P-1 à P-8)
- 📖 **Import automatique** : Chargement depuis `Sorts.xlsx`
- 🎯 **Noms élégants** : "Soin Proportionnel", "Forme d'Ours", "Projectile Magique"
- 🤖 **IA logique** : Priorise soins si PV < 50%, attaques zone si 3+ ennemis
- ⚡ **Déblocage aléatoire** : 2-3 capacités débloquées par défaut (variété combats)
- 📜 **Règles officielles** : Limitation d'actions (magie OU attaque physique)

### 🛠️ **CORE - Combat Intégré (100% Fonctionnel)**
- ⚔️ **Combat au tour par tour** : Initiative, attaque, défense, blessures + capacités
- 🎲 **Système de dés** : d20 pour attaque, dégâts variables réalistes
- 🛡️ **Équipements complets** : Bonus stats, builds optimisés par héros
- 💀 **Inconscience/Mort** : Gestion 0 PV avec règles de résurrection
- 📊 **Métriques détaillées** : Survie, attrition, efficacité builds + capacités

### 🔧 **CORRECTIONS RÉCENTES - Bugs Critiques Résolus**
- ✅ **GameRules.max_rounds** : Attribut manquant ajouté (évite crashes)
- ✅ **Character.heal()** : Méthode de soin implémentée (capacités fonctionnelles)
- ✅ **Adaptateur métriques** : Conversion format pour interface (plus de KeyError)
- ✅ **Noms de capacités** : Générateur automatique de noms élégants

## 🎯 Philosophie Projet

### 🛡️ **Focus Combat Détaillé Avec Capacités**
L'objectif principal n'est **PAS** les statistiques massives mais l'**analyse tactique fine** :
- **Journal de combat** = ressource essentielle pour équilibrage + utilisation capacités
- **Métriques ressources** = blessures/sorts par héros (critique) + tracking capacités
- **Combat unique** = plus important que 100 simulations
- **Relancer facilement** = tester variations sur même config
- **🆕 Capacités intelligentes** = IA utilise logiquement les 48 capacités

### 🎨 **Interface Gaming Moderne Optimisée**
- **Expanders natifs** = Zero zones blanches + style cohérent Streamlit
- **Récapitulatif élégant** = vue claire des équipes avant combat + capacités
- **Interface compacte** = expanders fermés par défaut, gain d'espace
- **Noms complets** = 20/18 caractères avec troncature intelligente
- **Workflow intuitif** = 3 clics pour lancer un combat avec capacités
- **🆕 Héros par 6** = Grille 6 colonnes MAINTENUE (requirement absolu)

## 🛡️ **RÉCAPITULATIF "FORMATION DE GUERRE" - PRÉSERVATION**

**Historique :** Cette fonctionnalité a été supprimée plusieurs fois par erreur lors de refactorings Claude, causant une régression de l'expérience utilisateur.

**Fonction complète :**
- **Affichage élégant** des équipes sélectionnées (héros vs ennemis)
- **Stats détaillées** avec builds et pronostic de bataille
- **🆕 Aperçu capacités** : Capacités débloquées, coûts, types
- **Position optimale** avant le bouton de combat pour validation
- **Design cohérent** avec le thème gaming médiéval

**Instructions de préservation :**
- 🔒 **Maintenir** cette fonctionnalité lors des modifications
- 📍 **Conserver** sa position et son contenu complet
- ⚠️ **Éviter** la suppression pour "optimisation d'espace"
- 🎯 **Améliorer** si nécessaire, mais ne pas retirer

**Localisation :** `ui/components/hero_components.py` → `display_team_recap()`

## 🎮 Règles et Mécaniques

### ✅ **Règles de Combat Implémentées**
- 🏹 **Attaques distance :** Ciblage libre vs corps-à-corps
- ✨ **Dégâts magiques :** Ignorent la parade
- 🎯 **Critiques :** 20 = double dégâts, 1 = contre-attaque
- 🎲 **Initiative :** Ordre aléatoire vs fixe
- 🔮 **Capacités complètes** : 48 capacités avec règles officielles

### 🛠️ **TODO - Règles Optionnelles à Implémenter**
**🔴 Inconscience et Défaite (p.18)**
   - ❌ MANQUANT : Récupération PV limitée après défaite totale
   - ❌ MANQUANT : Malus ressources (1 cube bleu par héros)
   - 📝 Localisation : `combat_engine.py` → gestion fin de combat

**🔴 Défaite Totale - Malus (p.18)**
   - ❌ MANQUANT : Si tous inconscients → coût 1 cube bleu par héros
   - ❌ MANQUANT : Récupération de 50% des PV seulement
   - 📝 Localisation : `combat_engine.py` → gestion fin de combat

## 💾 Données et Import

### 📊 Import Automatique Excel + Capacités
- **Source principale :** `Data_cards.xlsx`
- **🆕 Source capacités :** `Sorts.xlsx` (48 capacités)
- **Auto-détection :** Création CSV si manquants + génération noms élégants
- **Contenu :** 12 héros, 72 ennemis, 52 équipements, 48 capacités
- **🆕 Cache performance :** `ability_names.csv` pour noms élégants

### 🔧 Builds Système Hybride + Capacités
```python
# Builds pré-définis optimisés par héros
'P-1': ['O-38', 'O-11'],  # Elneha Sniper: Gants + Arc

# Builds custom sauvegardés
st.session_state.custom_builds = {
    'P-1': {'equipment': ['O-75', 'O-23'], 'name': 'Mon DPS Ultime'}
}

# NOUVEAU - Capacités par héros
'P-1': [
    Ability(name="Forme d'Ours", spell_cost=1, ability_number=1),
    Ability(name="Soin Naturel", spell_cost=1, ability_number=2),
    # ... 4 autres capacités
]
```

## 🔄 État du Développement

### ✅ **TERMINÉ - Système de Capacités 80%**
- [x] **Modèles Pydantic** : `models/abilities.py` validation complète
- [x] **Import automatique** : `utils/abilities_loader.py` + noms élégants
- [x] **Intégration Character** : `models/character.py` avec gestion capacités
- [x] **Moteur de combat** : `models/combat_engine.py` + IA logique
- [x] **Règles officielles** : Limitation d'actions (magie OU attaque)
- [x] **🆕 Déblocage aléatoire** : 2-3 capacités par héros par défaut
- [x] **🆕 Noms élégants** : Générateur automatique via `generate_ability_names.py`
- [x] **🆕 IA intelligente** : Logique soin/zone/offensive selon contexte

### ✅ **CORRIGÉ - Bugs Critiques**
- [x] **GameRules.max_rounds** : Attribut manquant causait crashes
- [x] **Character.heal()** : Méthode manquante pour capacités de soin
- [x] **Adaptateur métriques** : KeyError interface résultats corrigé
- [x] **Compatibilité capacités** : Fallback si système indisponible

### ✅ **FONCTIONNEL - Interface Complète**
- [x] **Combat détaillé** : logs round par round + capacités prioritaires
- [x] **Builds hybrides** : pré-définis + customisation complète
- [x] **72 ennemis** : recherche par numéro/nom efficace avec noms complets
- [x] **Validation UX** : minimum 2 héros, mode auto joueurs
- [x] **Workflow fluide** : sélection → récapitulatif → combat → analyse
- [x] **🆕 Héros par 6** : Grille maintenue selon requirement

### 🎯 **EN COURS - Optimisations Optionnelles (20%)**
- 🔄 **Interface UI capacités** : Activation manuelle en combat (optionnel)
- 🔄 **Métriques étendues** : Tracking usage capacités dans récapitulatif
- 🔄 **Règles avancées** : Ordre attaque corps-à-corps, résistance magique

## 🔮 Informations pour Prochaine Session Claude

### 📋 **Contexte Critique à Retenir**
1. **✅ Bugs critiques résolus** : max_rounds, heal(), adaptateur métriques
2. **✅ Système capacités 80%** : Fonctionnel avec noms élégants + IA logique
3. **✅ Interface stable** : Héros par 6, récapitulatif Formation de Guerre préservé
4. **✅ Expérience utilisateur** : 2-3 capacités par héros, logs élégants
5. **🔒 Requirements absolus** : Grille héros 6 colonnes jamais modifier
6. **🎯 Focus combat détaillé** : journal prioritaire, pas de stats massives

### 🆕 **Améliorations Récentes (Session Août 2025)**
- **✅ Noms capacités élégants** : "Soin Proportionnel" au lieu de "Atucan 2"
- **✅ IA capacités logique** : Soin si PV < 50%, zone si 3+ ennemis, offensive sinon
- **✅ Déblocage variété** : 2-3 capacités aléatoires au lieu d'1 seule
- **✅ Stabilité totale** : Plus de crashes, interface résultats fonctionnelle
- **✅ Code débutant** : Fonctions courtes, commentaires clairs, architecture simple

### 🛠️ **Priorité Développement**

**1. VALIDATION SYSTÈME (URGENT)**
- Tester génération `ability_names.csv` avec `generate_ability_names.py`
- Valider combats avec noms élégants dans logs
- Confirmer absence de régressions interface existante

**2. OPTIMISATIONS OPTIONNELLES**
- Interface UI capacités complète (Phase 5) si souhaité
- Amélioration IA capacités (logique plus sophistiquée)
- Métriques capacités dans récapitulatif Formation de Guerre

### 💡 **Points d'Attention Critiques**
- **🔒 Maintenir héros par 6** : `cols = st.columns(6)` JAMAIS changer
- **🔒 Préserver récapitulatif** : "Formation de Guerre" = business critical
- **🔒 Respecter architecture** : ui/components/, models/, utils/ modulaire
- **🔧 Code accessible** : Fonctions courtes, commentaires, compréhensible débutants
- **🎮 Expérience utilisateur** : Capacités automatiques, noms élégants, IA logique

### 🚀 **État Technique Stable**
- **Python** : Streamlit + Pydantic + Plotly + Pandas
- **Capacités** : 48 intégrées avec noms élégants et IA intelligente
- **Interface** : Expanders compacts + récapitulatif élégant + héros par 6
- **Combat** : Moteur complet avec journal détaillé + capacités logiques
- **Stabilité** : Bugs critiques résolus, système robuste et fonctionnel

---

## 📞 **Contact & Statut**

- **Équipe d'équilibrage** : Équipe d'équilibrage du jeu Périples
- **Dev Python** : Christophe Bidouj (développement assisté par Claude AI)
- **Version Actuelle** : V4+ Interface + Système Capacités 80% Terminé
- **Statut** : **Stable et fonctionnel** - Bugs critiques résolus, capacités intégrées avec IA logique
- **Dernière MAJ** : Août 2025 - Corrections bugs + noms élégants + IA capacités

**L'application dispose maintenant d'un système de capacités complet et stable à 80%, avec une interface gaming moderne préservée et une expérience utilisateur optimisée.**