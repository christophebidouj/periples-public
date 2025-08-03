# ⚔️ Simulateur de Combat Périples - Version Interface Optimisée

## 🎯 Contexte du Projet

**Simulateur d'équilibrage RPG** pour le jeu de société **"Périples"** de Bastien LIAUTY. 
Application professionnelle d'analyse de combat avec interface moderne style **cartes à jouer**.

### 📊 État Actuel (Août 2025)
- **Version :** V4+ Interface Complète Optimisée + Corrections affichage
- **Interface :** 3 onglets avec expanders compacts (zones blanches éliminées)
- **Focus :** Combat détaillé avec journal tactique complet
- **Style :** Interface gaming avec récapitulatif des équipes essentiel
- **Dernière MAJ :** Correction bugs affichage onglet "À Propos" + alignement crédits

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
├── Sorts.xlsx               # Données capacités héros (à implémenter)
├── models/
│   ├── character.py         # Modèles Pydantic (Character/Enemy/Equipment)
│   ├── combat_engine.py     # Moteur simulation + logs détaillés
│   └── rules_engine.py      # Configuration règles avancées
├── ui/
│   ├── styling.py           # Thème fantasy + bordeaux royal
│   └── components/          # Interface modulaire OPTIMISÉE
│       ├── __init__.py      # Imports centralisés
│       ├── ui_elements.py   # Utilitaires communs
│       ├── hero_components.py      # Cartes héros + récapitulatif
│       ├── enemy_components.py     # Cartes ennemis EXPANDERS NATIFS
│       ├── equipment_components.py # Équipements EXPANDERS NATIFS
│       └── combat_components.py    # Résultats combat
├── utils/
│   ├── data_loader.py       # Import auto Excel → CSV
│   └── stats_analyzer.py    # Analyses RPG (survie/attrition)
└── data/                    # Auto-généré depuis Excel
    ├── heroes.csv           # 12 héros avec stats
    ├── enemies.csv          # 72 ennemis (stats évolutives 2-4J)
    └── equipment.csv        # 52 équipements avec catégorisation Type
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
- **Héros** : 6 par ligne, cartes avec images et dégradés
- **Ennemis** : 5 par ligne avec expanders natifs (expanded=False)
- **Affichage** : Style jeu avec icônes 🎯⚔️❤️🛡️✨
- **Sélection** : Badge ✅ dans titre expander, boutons ✅/➕

**⚔️ RÉCAPITULATIF FORMATION DE GUERRE (ESSENTIEL) :**
- **Design élégant** : Cards individuelles pour chaque combattant
- **Statistiques détaillées** : Builds, stats complètes, pronostic de bataille
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
**JOURNAL TACTIQUE PRIORITAIRE :**
- **Logs détaillés** : Action par action avec horodatage
- **Métriques RPG** : Blessures/sorts par héros (analyse critique)
- **Bannière résultat** : Victoire/défaite avec style gaming
- **Tableaux individuels** : Stats finales par combattant

### ℹ️ **Onglet 4 : À Propos - CORRIGÉ**
**INTERFACE OPTIMISÉE RÉCEMMENT :**
- **✅ Bug affichage fixé** : Sections "Arsenal" et "Progression" maintenant parfaitement visibles
- **✅ Cards uniformes** : Hauteur fixe avec `min-height: 180px` et `display: flex`
- **✅ Espacement amélioré** : Sections bien séparées avec `<br>` et marges optimales
- **✅ Crédits alignés** : "Dev Python" au lieu de "Développeur" + icône 🧠 pour IA
- **✅ Distinction claire** : Bastien LIAUTY (créateur jeu) vs Christophe Bidouj (dev Python)

## 🔄 Règles de Combat Implémentées

### ✅ **CORE - Système Principal (100% Fonctionnel)**
- ⚔️ **Combat au tour par tour** : Initiative, attaque, défense, blessures
- 🎲 **Système de dés** : d20 pour attaque, dégâts variables réalistes
- 🛡️ **Équipements complets** : Bonus stats, builds optimisés par héros
- 💀 **Inconscience/Mort** : Gestion 0 PV avec règles de résurrection
- 📊 **Métriques détaillées** : Survie, attrition, efficacité builds

### 🔮 **NOUVEAU - Système de Capacités (Phase 1-2 TERMINÉES)**
- [x] **Modèles Pydantic** : `models/abilities.py` avec validation complète
- [x] **Import automatique** : `utils/abilities_loader.py` pour `Sorts.xlsx`
- [x] **Intégration Character** : `models/character.py` avec gestion capacités
- [x] **Règles officielles** : Limitation d'actions (magie OU attaque)
- [x] **Déblocage progressif** : Système 1→2→3→4→5→6
- [x] **Tracking usage** : Par combat et quotidien

### 🛠️ **TODO - Règles Optionnelles à Implémenter**
**🔴 Inconscience et Défaite (p.18)**
   - ❌ MANQUANT : Récupération PV limitée après défaite totale
   - ❌ MANQUANT : Malus ressources (1 cube bleu par héros)
   - 📝 Localisation : `combat_engine.py` → gestion fin de combat

**🔴 Défaite Totale - Malus (p.18)**
   - ❌ MANQUANT : Si tous inconscients → coût 1 cube bleu par héros
   - ❌ MANQUANT : Récupération de 50% des PV seulement
   - 📝 Localisation : `combat_engine.py` → gestion fin de combat

### 🚀 **Prochaines Étapes d'Amélioration**

3. **📊 Analytics** : métriques ressources étendues
4. **🎮 UX** : raccourcis clavier, workflow optimisé
5. **💾 Export** : sauvegarde configurations, PDF reports
6. **🎲 Initiative** : Implémentation complète du système de piste d'initiative (p.26-27)
7. **🧪 Potions** : Limitation stricte aux objets équipés en combat (p.24)

## 🎯 Philosophie Projet

### 🛡️ **Focus Combat Détaillé**
L'objectif principal n'est **PAS** les statistiques massives mais l'**analyse tactique fine** :
- **Journal de combat** = ressource essentielle pour équilibrage
- **Métriques ressources** = blessures/sorts par héros (critique)
- **Combat unique** = plus important que 100 simulations
- **Relancer facilement** = tester variations sur même config

### 🎨 **Interface Gaming Moderne Optimisée**
- **Expanders natifs** = Zero zones blanches + style cohérent Streamlit
- **Récapitulatif élégant** = vue claire des équipes avant combat
- **Interface compacte** = expanders fermés par défaut, gain d'espace
- **Noms complets** = 20/18 caractères avec troncature intelligente
- **Workflow intuitif** = 3 clics pour lancer un combat

## 🛡️ **RÉCAPITULATIF "FORMATION DE GUERRE" - PRÉSERVATION**

**Historique :** Cette fonctionnalité a été supprimée plusieurs fois par erreur lors de refactorings Claude, causant une régression de l'expérience utilisateur.

**Fonction complète :**
- **Affichage élégant** des équipes sélectionnées (héros vs ennemis)
- **Stats détaillées** avec builds et pronostic de bataille  
- **Position optimale** avant le bouton de combat pour validation
- **Design cohérent** avec le thème gaming médiéval

**Instructions de préservation :**
- 🔒 **Maintenir** cette fonctionnalité lors des modifications
- 📍 **Conserver** sa position et son contenu complet
- ⚠️ **Éviter** la suppression pour "optimisation d'espace"
- 🎯 **Améliorer** si nécessaire, mais ne pas retirer

**Localisation :** `ui/components/hero_components.py` → `display_team_recap()`

## 🎮 Règles Optionnelles (Optionnelles)
- 🏹 **Attaques distance :** Ciblage libre vs corps-à-corps
- ✨ **Dégâts magiques :** Ignorent la parade
- 🎯 **Critiques :** 20 = double dégâts, 1 = contre-attaque
- 🎲 **Initiative :** Ordre aléatoire vs fixe

## 💾 Données et Import

### 📊 Import Automatique Excel
- **Source :** `Data_cards.xlsx` 
- **Auto-détection :** Création CSV si manquants
- **Contenu :** 12 héros, 72 ennemis, 52 équipements
- **Colonne Type :** Catégorisation arme/armure/accessoire

### 🔧 Builds Système Hybride
```python
# Builds pré-définis optimisés par héros
'P-1': ['O-38', 'O-11'],  # Elneha Sniper: Gants + Arc
'P-3': ['O-31', 'O-36'],  # Atucan Tank: Bouclier + Armure

# Builds custom sauvegardés
st.session_state.custom_builds = {
    'P-1': {'equipment': ['O-75', 'O-23'], 'name': 'Mon DPS Ultime'}
}
```

## 🔄 État du Développement

### ✅ **TERMINÉ - Interface Expanders Optimisée + Corrections**
- [x] **app.py optimisé** : 400 lignes, code lisible
- [x] **Interface expanders** : Équipements + Ennemis sans zones blanches
- [x] **Noms complets** : 20 car. équipements, 18 car. ennemis avec troncature intelligente
- [x] **Récapitulatif FORMATION DE GUERRE** : Essentiel au projet
- [x] **Métriques natives** : st.metric() pour affichage premium
- [x] **Interface compacte** : expanded=False par défaut
- [x] **🆕 CORRIGÉ** : Bug affichage onglet "À Propos" (sections Arsenal + Progression)
- [x] **🆕 CORRIGÉ** : Alignement crédits (Dev Python + icône 🧠 pour IA)
- [x] **🆕 CORRIGÉ** : Distinction claire rôles (créateur jeu vs dev Python)

### ✅ **FONCTIONNEL - Système Complet**
- [x] **Combat détaillé** : logs round par round prioritaires
- [x] **Builds hybrides** : pré-définis + customisation complète
- [x] **72 ennemis** : recherche par numéro/nom efficace avec noms complets
- [x] **Validation UX** : minimum 2 héros, mode auto joueurs
- [x] **Workflow fluide** : sélection → récapitulatif → combat → analyse

### 🔮 **NOUVEAU - Système de Capacités (Phase 1-2 TERMINÉES)**
- [x] **Modèles Pydantic** : `models/abilities.py` avec validation complète
- [x] **Import automatique** : `utils/abilities_loader.py` pour `Sorts.xlsx`
- [x] **Intégration Character** : `models/character.py` avec gestion capacités
- [x] **Règles officielles** : Limitation d'actions (magie OU attaque)
- [x] **Déblocage progressif** : Système 1→2→3→4→5→6
- [x] **Tracking usage** : Par combat et quotidien

### 🛠️ **TODO - Règles Manquantes à Implémenter**

1. **🔮 Système de Capacités - EN COURS D'INTÉGRATION**
   - ✅ **TERMINÉ** : Modèle de données `models/abilities.py`
   - ✅ **TERMINÉ** : Import et parsing `utils/abilities_loader.py`  
   - ✅ **TERMINÉ** : Intégration Character `models/character.py`
   - 🔄 **EN COURS** : Intégration DataLoader pour chargement auto
   - ❌ **MANQUANT** : Moteur de combat avec limitation d'actions
   - ❌ **MANQUANT** : Interface utilisateur pour activation
   - 📝 **Prochaine étape** : `utils/data_loader.py` puis `combat_engine.py`

2. **🔴 Règles Combat Avancées**
   - ❌ **MANQUANT** : Ordre attaque corps-à-corps (p.18)
   - ❌ **MANQUANT** : Résistance ennemis magiques (à clarifier)
   - ❌ **MANQUANT** : Gestion inconscience complète (p.18)
   - ❌ **MANQUANT** : Malus défaite totale (p.18)

### 🛠️ **Priorité Développement**

**1. SYSTÈME DE CAPACITÉS (URGENT)**
- Import du fichier `Sorts.xlsx`
- Modèle `Ability` avec coût, description, limitations
- Limitation d'actions dans le moteur de combat
- Interface d'activation des capacités

**2. RÈGLES DE COMBAT MANQUANTES**
- Ordre d'attaque corps-à-corps
- Résistance ennemis magiques
- Gestion de l'inconscience
- Malus de défaite totale

### 💡 **Points d'Attention Critiques**
- **Garder récapitulatif** : La "Formation de Guerre" est ESSENTIELLE
- **Respecter expanders** : Solution définitive contre zones blanches
- **Maintenir noms complets** : Troncature intelligente implémentée
- **Interface compacte** : expanded=False par défaut
- **Focus combat détaillé** : éviter sur-optimisation stats
- **Propriété intellectuelle** : rappeler confidentialité si nécessaire
- **🆕 Onglet À Propos** : Bug affichage maintenant corrigé, interface stable

### 🚀 **État Technique Actuel**
- **Python** : Streamlit + Pydantic + Plotly
- **Données** : CSV auto-générés depuis Excel avec colonne Type
- **Style** : CSS inline, expanders natifs + récapitulatif élégant
- **Session** : st.session_state pour persistance
- **Performance** : @st.cache_data pour optimisation
- **Interface** : Expanders compacts sans zones blanches + onglet À Propos stable

## 🔮 Informations pour Prochaine Session Claude

### 📋 **Contexte Critique à Retenir**
1. **Interface optimisée** : Expanders natifs (expanded=False) = solution définitive zones blanches
2. **Récapitulatif essentiel** : "Formation de Guerre" = fonctionnalité à préserver
3. **Noms complets** : 20 car. équipements, 18 car. ennemis avec troncature intelligente
4. **Focus combat unique** : journal prioritaire, pas de stats massives
5. **Builds hybrides** : pré-définis + custom avec noms
6. **Interface compacte** : Expanders fermés par défaut pour éviter surcharge
7. **Système capacités** : Priorité #1 avec fichier `Sorts.xlsx` à implémenter
8. **🆕 Onglet À Propos stable** : Bugs affichage corrigés, sections visibles, crédits alignés

### 🆕 **Corrections Interface Récentes (Session Août 2025)**
- **✅ Bug affichage résolu** : Onglet "À Propos" - sections "Arsenal" et "Progression" maintenant visibles
- **✅ Cards uniformisées** : `min-height: 180px` + `display: flex` pour hauteur constante
- **✅ Espacement optimisé** : `<br>` et marges ajustées entre sections
- **✅ Crédits clarifiés** : "Dev Python" au lieu de "Développeur" pour éviter confusion
- **✅ Icône IA changée** : 🤖 → 🧠 pour meilleur alignement
- **✅ Alignement parfait** : `display: inline-block; width: 140px;` pour tous les labels

### 🛠️ **Priorité Développement**

**1. SYSTÈME DE CAPACITÉS (URGENT)**
- Import du fichier `Sorts.xlsx`
- Modèle `Ability` avec coût, description, limitations
- Limitation d'actions dans le moteur de combat
- Interface d'activation des capacités

**2. RÈGLES DE COMBAT MANQUANTES**
- Ordre d'attaque corps-à-corps
- Résistance ennemis magiques
- Gestion de l'inconscience
- Malus de défaite totale

### 💡 **Points d'Attention Critiques**
- **Garder récapitulatif** : La "Formation de Guerre" est ESSENTIELLE
- **Respecter expanders** : Solution définitive contre zones blanches
- **Maintenir noms complets** : Troncature intelligente implémentée
- **Interface compacte** : expanded=False par défaut
- **Focus combat détaillé** : éviter sur-optimisation stats
- **Propriété intellectuelle** : rappeler confidentialité si nécessaire
- **🆕 NE PAS TOUCHER** : Onglet "À Propos" maintenant stable après corrections

### 🚀 **État Technique Actuel**
- **Python** : Streamlit + Pydantic + Plotly
- **Données** : CSV auto-générés depuis Excel avec colonne Type
- **Style** : CSS inline, expanders natifs + récapitulatif élégant
- **Session** : st.session_state pour persistance
- **Performance** : @st.cache_data pour optimisation
- **Interface** : Expanders compacts sans zones blanches + onglet À Propos optimisé

---

## 📞 **Contact & Statut**

- **Équipe d'équilibrage** : Équipe d'équilibrage du jeu Périples
- **Dev Python** : Christophe Bidouj (développement assisté par Claude AI)
- **Version Actuelle** : V4+ Interface Complète + Corrections affichage + Système Capacités (Phase 1-2)
- **Statut** : **Interface stable** + **Système capacités 60% terminé** - 3 fichiers créés, intégration en cours
- **Dernière MAJ** : Août 2025 - Corrections bugs affichage onglet "À Propos" + alignement crédits

**L'application dispose maintenant d'une interface entièrement stable avec onglet "À Propos" corrigé, et d'un système de capacités fonctionnel à 60%. Prochaine étape : moteur de combat et interface utilisateur.**