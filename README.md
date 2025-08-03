# ⚔️ Simulateur de Combat Périples - Version Finale

## 🎯 Contexte du Projet

**Simulateur d'équilibrage RPG** pour le jeu de société **"Périples"** de Bastien LIAUTY. 
Application professionnelle d'analyse de combat avec interface moderne style **cartes à jouer**.

### 📊 État Actuel (Août 2025)
- **Version :** V4 Finale - Style Cartes Ultra-Compact avec Récapitulatif Élégant
- **Interface :** 3 onglets avec affichage 4 héros + 5 ennemis par ligne
- **Focus :** Combat détaillé avec journal tactique complet
- **Style :** Cartes gaming avec récapitulatif des équipes essentiel

## 🚀 Architecture Technique

### 📁 Structure des Fichiers
```
periples/
├── app.py                    # Application Streamlit SIMPLIFIÉE (400 lignes)
├── Data_cards.xlsx          # Source données Excel → Auto-import CSV
├── models/
│   ├── character.py         # Modèles Pydantic (Character/Enemy/Equipment)
│   ├── combat_engine.py     # Moteur simulation + logs détaillés
│   └── rules_engine.py      # Configuration règles avancées
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

## 🎮 Interface Utilisateur Moderne

### 🏠 **Onglet 1 : Sélection des Équipes**
**STYLE CARTES ULTRA-COMPACT :**
- **Héros** : 4 par ligne, cartes avec images et dégradés
- **Ennemis** : 5 par ligne, cartes sombres thème gaming
- **Affichage** : Style jeu avec icônes 🎯⚔️❤️🛡️✨
- **Sélection** : Bordures vertes/rouges, boutons ✅/➕

**⚔️ RÉCAPITULATIF FORMATION DE GUERRE (ESSENTIEL) :**
- **Design élégant** : Cards individuelles pour chaque combattant
- **Statistiques détaillées** : Builds, stats complètes, pronostic de bataille
- **Style thématique** : Couleurs héros (vert) vs ennemis (rouge)
- **Position stratégique** : Visible avant le bouton de combat
- **🚨 IMPORTANT** : Ce récapitulatif ne doit JAMAIS être supprimé du projet !

**Fonctionnalités :**
- Minimum 2 héros obligatoire
- Mode auto : 2 héros = 2 joueurs, 3 héros = 3 joueurs...
- Recherche ennemis par numéro (ex: "34") ou nom
- Indicateurs visuels : 📋 = Standard, 🔧 = Custom, ✨ = Magique

### ⚙️ **Onglet 2 : Forge des Équipements**
- **Catégorisation fonctionnelle** : ⚔️ Armes, 🛡️ Armures, 💍 Accessoires
- **52 équipements** triés par type Excel
- **Builds personnalisés** avec noms custom
- **Aperçu temps réel** : comparaison base vs nouveau
- **Sauvegarde persistante** entre sessions

### 📊 **Onglet 3 : Chroniques du Combat**
- **Combat unique détaillé** (priorité absolue)
- **Journal complet** : chaque action, jet de dé, résultat
- **Métriques ressources** : blessures par héros, sorts utilisés
- **Bouton relancer** : même combat, nouvelles probabilités

## 🎲 Système de Jeu Périples

### ⚔️ Mécaniques Core
- **Jet d'attaque :** D20 + Précision ≥ Défense ennemi
- **Dégâts :** Damage héros - Parade ennemi (min 1)
- **Stats évolutives :** Ennemis s'adaptent au nombre de joueurs
- **Équipements :** Bonus cumulables sur toutes stats

### 🛡️ Règles Avancées (Optionnelles)
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

### ✅ **TERMINÉ - Interface Style Cartes avec Récapitulatif**
- [x] **app.py optimisé** : 400 lignes, code lisible
- [x] **Style cartes gaming** : 4 héros + 5 ennemis par ligne
- [x] **Récapitulatif FORMATION DE GUERRE** : Essentiel au projet
- [x] **Catégorisation équipements** : Fonctionnelle par type Excel
- [x] **Noms complets** : Plus de troncature d'équipements
- [x] **Bouton combat stylisé** : Design épique avec effets

### ✅ **FONCTIONNEL - Système Complet**
- [x] **Combat détaillé** : logs round par round prioritaires
- [x] **Builds hybrides** : pré-définis + customisation complète
- [x] **72 ennemis** : recherche par numéro/nom efficace
- [x] **Validation UX** : minimum 2 héros, mode auto joueurs
- [x] **Workflow fluide** : sélection → récapitulatif → combat → analyse

## 🎯 Philosophie Projet

### 🛡️ **Focus Combat Détaillé**
L'objectif principal n'est **PAS** les statistiques massives mais l'**analyse tactique fine** :
- **Journal de combat** = ressource essentielle pour équilibrage
- **Métriques ressources** = blessures/sorts par héros (critique)
- **Combat unique** = plus important que 100 simulations
- **Relancer facilement** = tester variations sur même config

### 🎨 **Interface Gaming Moderne avec Récapitulatif**
- **Style cartes** inspire confiance et engagement utilisateur
- **Récapitulatif élégant** = vue claire des équipes avant combat
- **Ultra-compact** = 75% gain d'espace vs version précédente
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

**Localisation :** `ui/components.py` → `display_team_recap()`

## 🚨 Propriété Intellectuelle

### ⚖️ **IMPORTANT - Confidentialité**
**TOUS les documents de ce projet sont propriétaires et confidentiels :**
- Jeu Périples © Bastien LIAUTY - Tous droits réservés
- Données CSV basées sur contenu propriétaire
- Usage autorisé : développement/tests d'équilibrage uniquement
- **❌ INTERDIT :** distribution, usage commercial, partage des règles

## 🔮 Informations pour Prochaine Session Claude

### 📋 **Contexte Critique à Retenir**
1. **Code optimisé** : app.py = 400 lignes, style cartes + récapitulatif
2. **Récapitulatif essentiel** : "Formation de Guerre" = fonctionnalité à préserver
3. **Catégorisation équipements** : Fonctionnelle via colonne Type Excel
4. **Focus combat unique** : journal prioritaire, pas de stats massives
5. **Builds hybrides** : pré-définis + custom avec noms

### 🛠️ **TODO - Règles Manquantes à Implémenter**

**URGENT - Conformité aux Règles Officielles :**

1. **⚔️ Combat - Ordre d'Attaque (p.25-26)**
   - ❌ MANQUANT : Attaque corps à corps doit cibler le **premier ennemi VIVANT**
   - ❌ MANQUANT : Vérification que la cible est encore en vie avant attaque
   - 📝 Localisation : `combat_engine.py` → `_select_target()`

2. **✨ Capacités Magiques - Limitation d'Actions (p.24)**
   - ❌ MANQUANT : "Les capacités magiques ne permettent pas de réaliser une attaque physique en plus"
   - ❌ MANQUANT : Système de tracking des actions par tour (magie OU attaque)
   - 📝 Localisation : `character.py` + `combat_engine.py` → `_hero_turn()`

3. **🛡️ Ennemis Magiques - Résistance (p.26)**
   - ❌ MANQUANT : Ennemis magiques divisent les dégâts physiques par 2
   - ❌ MANQUANT : Les dégâts magiques ignorent cette résistance
   - 📝 Localisation : `character.py` → `Enemy.take_damage()`

4. **💀 Inconscience - Règles de Ciblage (p.18)**
   - ❌ MANQUANT : Héros inconscients ne peuvent plus être ciblés par les ennemis
   - ❌ MANQUANT : Soins sur inconscients ne récupèrent qu'1 PV (pas le montant normal)
   - 📝 Localisation : `combat_engine.py` → `_select_hero_target()`

5. **🔴 Défaite Totale - Malus (p.18)**
   - ❌ MANQUANT : Si tous inconscients → coût 1 cube bleu par héros
   - ❌ MANQUANT : Récupération de 50% des PV seulement
   - 📝 Localisation : `combat_engine.py` → gestion fin de combat

### 🚀 **Prochaines Étapes d'Amélioration**

3. **📊 Analytics** : métriques ressources étendues
4. **🎮 UX** : raccourcis clavier, workflow optimisé
5. **💾 Export** : sauvegarde configurations, PDF reports
6. **🎲 Initiative** : Implémentation complète du système de piste d'initiative (p.26-27)
7. **🧪 Potions** : Limitation stricte aux objets équipés en combat (p.24)

### 🚀 **État Technique Actuel**
- **Python** : Streamlit + Pydantic + Plotly
- **Données** : CSV auto-générés depuis Excel avec colonne Type
- **Style** : CSS inline, cartes responsive + récapitulatif élégant
- **Session** : st.session_state pour persistance
- **Performance** : @st.cache_data pour optimisation

### 💡 **Points d'Attention Critiques**
- **Garder récapitulatif** : La "Formation de Guerre" est ESSENTIELLE
- **Respecter catégorisation** : Équipements triés par type Excel
- **Maintenir style cartes** : Design gaming moderne
- **Focus combat détaillé** : éviter sur-optimisation stats
- **Propriété intellectuelle** : rappeler confidentialité si nécessaire

---

## 📞 **Contact & Statut**

- **Utilisateur Principal :** Bastien LIAUTY (créateur Périples)
- **Version Actuelle :** V4 Finale - Cartes + Récapitulatif Élégant
- **Statut :** Projet fonctionnel, prêt pour utilisation professionnelle
- **Dernière MAJ :** Août 2025 - Récapitulatif Formation de Guerre ajouté

**L'application est PRÊTE pour l'équilibrage professionnel avec interface gaming moderne, récapitulatif des équipes essentiel, et workflow optimisé.**