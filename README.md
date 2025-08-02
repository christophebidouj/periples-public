# ⚔️ Simulateur de Combat Périples - Version Finale

## 🎯 Contexte du Projet

**Simulateur d'équilibrage RPG** pour le jeu de société **"Périples"** de Bastien LIAUTY. 
Application professionnelle d'analyse de combat avec interface moderne style **cartes à jouer**.

### 📊 État Actuel (Janvier 2025)
- **Version :** V4 Finale - Style Cartes Ultra-Compact
- **Interface :** 3 onglets avec affichage 4 héros + 5 ennemis par ligne
- **Focus :** Combat détaillé avec journal tactique complet
- **Style :** Cartes gaming avec effets visuels modernes

## 🚀 Architecture Technique

### 📁 Structure des Fichiers
```
periples/
├── app.py                    # Application Streamlit SIMPLIFIÉE (350 lignes)
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
    └── equipment.csv        # 52 équipements avec bonus
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
- **Héros** : 4 par ligne, cartes claires avec dégradés
- **Ennemis** : 5 par ligne, cartes sombres thème gaming
- **Affichage** : Style jeu avec icônes 🎯⚔️❤️🛡️✨
- **Sélection** : Bordures vertes/rouges, boutons ✅/➕

**Fonctionnalités :**
- Minimum 2 héros obligatoire
- Mode auto : 2 héros = 2 joueurs, 3 héros = 3 joueurs...
- Recherche ennemis par numéro (ex: "34") ou nom
- Indicateurs visuels : 📋 = Standard, 🔧 = Custom, ✨ = Magique

### ⚙️ **Onglet 2 : Customisation**
- **Builds personnalisés** avec noms custom
- **3 catégories** : ⚔️ Armes, 🛡️ Armures, 💍 Accessoires
- **52 équipements** disponibles
- **Aperçu temps réel** : comparaison base vs nouveau
- **Sauvegarde persistante** entre sessions

### 📊 **Onglet 3 : Résultats**
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
- **Source :** `data/Data_cards.xlsx` 
- **Auto-détection :** Création CSV si manquants
- **Contenu :** 12 héros, 72 ennemis, 52 équipements

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

### ✅ **TERMINÉ - Interface Style Cartes**
- [x] **app.py simplifié** : 350 lignes, code débutant-friendly
- [x] **Style cartes gaming** : 4 héros + 5 ennemis par ligne
- [x] **Affichage ultra-compact** : icônes au lieu de texte
- [x] **Lisibilité optimisée** : fond clair, contrastes élevés
- [x] **Effets visuels** : bordures colorées, boutons gaming

### ✅ **FONCTIONNEL - Système Complet**
- [x] **Combat détaillé** : logs round par round prioritaires
- [x] **Builds hybrides** : pré-définis + customisation complète
- [x] **72 ennemis** : recherche par numéro/nom efficace
- [x] **Validation UX** : minimum 2 héros, mode auto joueurs
- [x] **Workflow fluide** : sélection → custom → combat → analyse

## 🎯 Philosophie Projet

### 🛡️ **Focus Combat Détaillé**
L'objectif principal n'est **PAS** les statistiques massives mais l'**analyse tactique fine** :
- **Journal de combat** = ressource essentielle pour équilibrage
- **Métriques ressources** = blessures/sorts par héros (critique)
- **Combat unique** = plus important que 100 simulations
- **Relancer facilement** = tester variations sur même config

### 🎨 **Interface Gaming Moderne**
- **Style cartes** inspire confiance et engagement utilisateur
- **Ultra-compact** = 75% gain d'espace vs version précédente
- **Visuels clairs** = identification rapide héros/ennemis/builds
- **Workflow intuitif** = 3 clics pour lancer un combat

## 🚨 Propriété Intellectuelle

### ⚖️ **IMPORTANT - Confidentialité**
**TOUS les documents de ce projet sont propriétaires et confidentiels :**
- Jeu Périples © Bastien LIAUTY - Tous droits réservés
- Données CSV basées sur contenu propriétaire
- Usage autorisé : développement/tests d'équilibrage uniquement
- **❌ INTERDIT :** distribution, usage commercial, partage des règles

## 🔮 Informations pour Prochaine Session Claude

### 📋 **Contexte Critique à Retenir**
1. **Code simplifié** : app.py = 350 lignes, débutant-friendly
2. **Style cartes** : fonctionnel, 4+5 par ligne, fond clair
3. **Focus combat unique** : pas de stats massives, journal prioritaire
4. **Interface 3 onglets** : sélection/custom/résultats workflow
5. **Builds hybrides** : pré-définis + custom avec noms

### 🛠️ **Prochaines Étapes Possibles**
Si l'utilisateur demande des améliorations :

1. **🔧 Interface** : animations CSS, effets survol avancés
2. **⚡ Performance** : optimisation chargement données
3. **📊 Analytics** : métriques ressources étendues
4. **🎮 UX** : raccourcis clavier, workflow optimisé
5. **💾 Export** : sauvegarde configurations, PDF reports

### 🚀 **État Technique Actuel**
- **Python** : Streamlit + Pydantic + Plotly
- **Données** : CSV auto-générés depuis Excel
- **Style** : CSS inline, cartes responsive
- **Session** : st.session_state pour persistance
- **Performance** : @st.cache_data pour optimisation

### 💡 **Points d'Attention**
- **Garder code simple** : max 30 lignes par fonction
- **Respecter style cartes** : ne pas revenir à l'ancien design
- **Focus combat détaillé** : éviter sur-optimisation stats
- **Propriété intellectuelle** : rappeler confidentialité si nécessaire

---

## 📞 **Contact & Statut**

- **Utilisateur Principal :** Bastien LIAUTY (créateur Périples)
- **Version Actuelle :** V4 Finale - Style Cartes Ultra-Compact
- **Statut :** Projet fonctionnel, prêt pour utilisation professionnelle
- **Dernière MAJ :** AOUT 2025 - Interface cartes + code simplifié

**L'application est PRÊTE pour l'équilibrage professionnel de jeu avec interface gaming moderne et workflow optimisé.**