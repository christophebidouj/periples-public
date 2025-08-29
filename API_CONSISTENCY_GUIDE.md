# API_CONSISTENCY_GUIDE.md
# 🔧 GUIDE COHÉRENCE API - ÉVITER LES INCOHÉRENCES

## 🚨 **AVERTISSEMENT CRITIQUE - INTÉGRITÉ DES DONNÉES**

### ⚠️ **RÈGLE ABSOLUE : JAMAIS INVENTER DE DONNÉES**

**POUR TOUT DÉVELOPPEUR/CLAUDE FUTUR : NE JAMAIS INVENTER DE DONNÉES NUMÉRIQUES OU MÉCANIQUES**

#### 🔍 **SOURCES DE DONNÉES OFFICIELLES OBLIGATOIRES**

| Donnée | Source officielle | Localisation | Format |
|--------|------------------|--------------|---------|
| **Coûts en sorts** | `Sorts.xlsx` | Feuille "Capacités", colonne "Cout" | Numérique 0-4 |
| **Limitations d'usage** | `Sorts.xlsx` | Feuille "Capacités", colonne "Limitation" | "1 / combat" ou vide |
| **Descriptions capacités** | `ability_names.csv` | Colonne "clean_description" | Texte descriptif |
| **Statistiques héros** | `Sorts.xlsx` | Feuille "Personnages" | Précis, Dégâts, Sort, Santé |
| **Équipements** | `Sorts.xlsx` | Feuille "Equipement" | Stats complètes |
| **Ennemis** | `Sorts.xlsx` | Feuille "Ennemis" | Stats par nombre joueurs |

#### ❌ **ERREUR CRITIQUE COMMISE - CAS ATUCAN**

**Fichier** : `atucan.py` (première version)  
**Erreur** : Invention complète des coûts en sorts d'Atucan  
**Impact** : Déséquilibre du jeu, données incorrectes  

**Coûts inventés (FAUX)** vs **Coûts officiels (CORRECT)** :
```
❌ INVENTÉS           ✅ OFFICIELS (Sorts.xlsx)
1. 1 sort             1. 1 sort          ✅ Identique
2. 1 sort             2. 0 sort          ❌ ERREUR
3. 2 sorts            3. 1 sort          ❌ ERREUR
4. 2 sorts            4. 1 sort          ❌ ERREUR
5. 2 sorts            5. 1 sort          ❌ ERREUR
6. 3 sorts            6. 2 sorts         ❌ ERREUR
```

**Conséquences** : Atucan rendu trop cher (11 sorts inventés vs 6 sorts officiels)

#### 🛠️ **PROCÉDURE OBLIGATOIRE AVANT IMPLÉMENTATION**

```bash
# 1. TOUJOURS vérifier les données sources d'abord
python -c "
import pandas as pd
# Lire le fichier Excel officiel
df = pd.read_excel('Sorts.xlsx', sheet_name='Capacités')
# Filtrer pour le héros concerné
hero_data = df[df['Nom'].str.contains('HERO_NAME', case=False)]
print('DONNÉES OFFICIELLES:')
print(hero_data[['Nom', 'Cout', 'Limitation']].to_string())
"

# 2. Implémenter SEULEMENT après vérification des données
```

#### 🎯 **RÈGLES STRICTES D'INTÉGRITÉ**

1. **INTERDICTION ABSOLUE** d'inventer des valeurs numériques
2. **OBLIGATION** de vérifier `Sorts.xlsx` pour toute nouvelle capacité
3. **VALIDATION** des coûts avec les données officielles
4. **DOCUMENTATION** de la source pour chaque valeur utilisée
5. **TEST** des équilibres après implémentation avec vraies données

---

## 📋 **PROBLÈME API IDENTIFIÉ**
Différents Claudes utilisent des noms de méthodes divergents et ne lisent pas les fichiers fournis, causant des bugs AttributeError.

---

## 📋 **API OFFICIELLE DU PROJET**

### **Character (Héros)**
```python
# ✅ CORRECT
hero.get_attack_damage_info()['damage_value']
hero.get_total_precision()
hero.get_total_damage()
hero.is_alive()
hero.apply_damage_with_parade(damage)

# Attributs stats dynamiques
hero.current_attack  # Peut être None
hero.current_precision  # Peut être None
hero.current_defense  # Peut être None
```

### **Enemy (Ennemis)**
```python
# ✅ CORRECT
enemy.get_damage_info(player_count)['damage_value']
enemy.defense
enemy.is_alive()
enemy.apply_damage_with_parade(damage)

# ❌ FAUX - N'existe PAS
enemy.get_attack_damage_info()  # AttributeError !
```

### **Méthodes communes**
```python
# ✅ CORRECT pour tous
entity.is_alive() -> bool
entity.apply_damage_with_parade(damage) -> dict
entity.name -> str
```

---

## 🛠️ **PROTOCOLE OBLIGATOIRE POUR CLAUDES**

### **1. TOUJOURS vérifier les données ET l'API avant d'utiliser**
```python
# ÉTAPE 1: Vérifier les données sources
# Consulter Sorts.xlsx pour les coûts officiels

# ÉTAPE 2: Vérifier l'API existante
if isinstance(target, Enemy):
    damage_info = target.get_damage_info(player_count)
else:  # Character/Hero
    damage_info = target.get_attack_damage_info()

damage_value = damage_info['damage_value']
```

### **2. Utiliser hasattr() pour la sécurité**
```python
# Défensif - évite les AttributeError
if hasattr(target, 'get_attack_damage_info'):
    damage_info = target.get_attack_damage_info()
elif hasattr(target, 'get_damage_info'):
    damage_info = target.get_damage_info(player_count)
else:
    raise ValueError(f"Type {type(target)} non supporté")
```

### **3. Fonction utilitaire recommandée**
```python
def get_entity_damage_info(entity, player_count=None):
    """Fonction utilitaire pour obtenir damage_info de tout type d'entité"""
    if hasattr(entity, 'get_attack_damage_info'):
        return entity.get_attack_damage_info()
    elif hasattr(entity, 'get_damage_info'):
        if player_count is None:
            raise ValueError("player_count requis pour Enemy")
        return entity.get_damage_info(player_count)
    else:
        raise AttributeError(f"Aucune méthode damage_info pour {type(entity)}")
```

---

## 📖 **LECTURE OBLIGATOIRE DES FICHIERS**

### **Avant modification, LIRE :**
1. **`Sorts.xlsx`** - DONNÉES OFFICIELLES (coûts, limitations, stats)
2. `character.py` - API Character/Hero
3. `enemies.py` ou fichiers Enemy - API Enemy  
4. `combat_actions.py` - Utilisation existante
5. `diagnostic_capacites.py` - État réel

### **Commandes de vérification :**
```bash
# 1. Vérifier données sources Excel
python -c "
import pandas as pd
try:
    df = pd.read_excel('Sorts.xlsx', sheet_name='Capacités')
    print('✅ Sorts.xlsx accessible')
    print('Colonnes:', df.columns.tolist())
except Exception as e:
    print('❌ Erreur lecture Sorts.xlsx:', e)
"

# 2. Vérifier API existante
python -c "
from models.character import Character
from models.enemy import Enemy  # ou équivalent
print('Character methods:', [m for m in dir(Character) if not m.startswith('_')])
print('Enemy methods:', [m for m in dir(Enemy) if not m.startswith('_')])
"
```

---

## 🔍 **CHECKLIST PRE-DÉVELOPPEMENT MISE À JOUR**

### **Pour chaque Claude :**
- [ ] **PRIORITÉ 1**: Vérifier `Sorts.xlsx` pour les données officielles
- [ ] **PRIORITÉ 2**: Lire fichiers existants AVANT de coder
- [ ] Vérifier API avec `dir()` ou `hasattr()`
- [ ] Tester imports : `from models.character import Character`
- [ ] **INTERDICTION**: Inventer des valeurs numériques
- [ ] Documenter la source de chaque donnée utilisée

### **Pour chaque modification :**
- [ ] **ÉTAPE 0**: Consulter les sources de données officielles
- [ ] Identifier type d'objet (Character vs Enemy)
- [ ] Vérifier méthode existe avec `hasattr()`
- [ ] Tester avec `python diagnostic_capacites.py`
- [ ] Valider équilibrage avec vraies données
- [ ] Documenter nouvelles méthodes dans ce guide

---

## ⚡ **CORRECTION RAPIDE INCOHÉRENCES ACTUELLES**

### **Combat_actions.py - Line 91**
```python
# ❌ AVANT
counter_damage = target.get_attack_damage_info()['damage_value']

# ✅ APRÈS  
enemy_damage_info = target.get_damage_info(player_count)
counter_damage = enemy_damage_info['damage_value']
```

### **Character.py - Line 395**
```python
# ❌ AVANT
def _get_mark_damage_bonus(self) -> int:
    return  # Vide

# ✅ APRÈS
def _get_mark_damage_bonus(self) -> int:
    """Calcule bonus dégâts contre ennemis marqués"""
    # TODO: Implémenter logique marquage
    return 0
```

### **Atucan.py - Coûts corrigés**
```python
# ❌ AVANT (inventé)
self.spell_cost = 2  # Châtiment divin

# ✅ APRÈS (Sorts.xlsx)
self.spell_cost = 1  # Châtiment divin - DONNÉES OFFICIELLES
```

---

## 🎯 **RÈGLES ABSOLUES MISES À JOUR**

1. **JAMAIS** inventer de données numériques ou mécaniques
2. **TOUJOURS** consulter `Sorts.xlsx` avant d'implémenter une capacité
3. **OBLIGATOIRE** vérifier avec `hasattr()` si incertain sur l'API
4. **OBLIGATOIRE** lire fichiers existants avant modification
5. **INTERDIT** modifier API sans documentation
6. **REQUIS** tester avec diagnostic après changement
7. **OBLIGATOIRE** documenter la source de chaque donnée utilisée

---

## 📊 **VALIDATION DES DONNÉES - EXEMPLES OFFICIELS**

### **Héros P-1 (Elneha) - VALIDÉ**
```python
# Coûts vérifiés depuis Sorts.xlsx
spell_costs = {
    "Forme d'ours": 1,      # ✅ Officiel
    "Soin mineur": 1,       # ✅ Officiel
    "Forme de loup": 1,     # ✅ Officiel
    "Soin multiple": 2,     # ✅ Officiel
    "Onde tonnante": 1,     # ✅ Officiel
    "Résurrection": 2       # ✅ Officiel
}
```

### **Héros P-3 (Atucan) - CORRIGÉ**
```python
# Coûts corrigés depuis Sorts.xlsx
spell_costs = {
    "Soin proportionnel": 1,    # ✅ Officiel (était inventé à 1, par chance correct)
    "Bouclier renforcé": 0,     # ✅ Corrigé (était inventé à 1)
    "Châtiment divin": 1,       # ✅ Corrigé (était inventé à 2)
    "Aura protectrice": 1,      # ✅ Corrigé (était inventé à 2)
    "Soin de groupe": 1,        # ✅ Corrigé (était inventé à 2)
    "Jugement dernier": 2       # ✅ Corrigé (était inventé à 3)
}
```

---

**Usage** : Document de référence pour maintenir cohérence API ET intégrité données  
**Mise à jour** : Août 2025 après correction erreur critique Atucan  
**Priorité** : CRITIQUE - Consulter AVANT toute implémentation de capacités