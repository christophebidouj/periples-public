# API_CONSISTENCY_GUIDE.md
# 🔧 GUIDE COHÉRENCE API - ÉVITER LES INCOHÉRENCES

## 🚨 **PROBLÈME IDENTIFIÉ**
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

### **1. TOUJOURS vérifier avant d'utiliser**
```python
# Avant d'écrire du code, VÉRIFIER l'API
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
1. `character.py` - API Character/Hero
2. `enemies.py` ou fichiers Enemy - API Enemy  
3. `combat_actions.py` - Utilisation existante
4. `diagnostic_capacites.py` - État réel

### **Commandes de vérification :**
```bash
# Vérifier attributs/méthodes existants
python -c "
from models.character import Character
from models.enemy import Enemy  # ou équivalent
print('Character methods:', [m for m in dir(Character) if not m.startswith('_')])
print('Enemy methods:', [m for m in dir(Enemy) if not m.startswith('_')])
"
```

---

## 🔍 **CHECKLIST PRE-DÉVELOPPEMENT**

### **Pour chaque Claude :**
- [ ] Lire fichiers existants AVANT de coder
- [ ] Vérifier API avec `dir()` ou `hasattr()`
- [ ] Tester imports : `from models.character import Character`
- [ ] Éviter assumptions sur noms de méthodes
- [ ] Utiliser fonctions utilitaires défensives

### **Pour chaque modification :**
- [ ] Identifier type d'objet (Character vs Enemy)
- [ ] Vérifier méthode existe avec `hasattr()`
- [ ] Tester avec `python diagnostic_capacites.py`
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

---

## 🎯 **RÈGLES ABSOLUES**

1. **JAMAIS** inventer noms de méthodes
2. **TOUJOURS** vérifier avec `hasattr()` si incertain
3. **OBLIGATOIRE** lire fichiers existants avant modification
4. **INTERDIT** modifier API sans documentation
5. **REQUIS** tester avec diagnostic après changement

---

**Usage** : Document de référence pour maintenir cohérence API
**Mise à jour** : Après chaque modification d'API