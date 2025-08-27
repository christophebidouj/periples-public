# CLEANUP_NOTES.md
# 🧹 NOTES POUR NETTOYAGE DU PROJET APRÈS MIGRATION

## 🎯 OBJECTIF
Supprimer le code legacy devenu inutile après migration complète vers capacités individuelles.

## ⚠️ ÉTAT ACTUEL (Mis à jour Décembre 2024)
- **Ancien système DÉSACTIVÉ** dans `ability_manager.py` (return False)
- **Fallback COMMENTÉ** dans `combat_actions.py` 
- **Capacités individuelles** : P-1, P-2 implémentées (12/59)
- **Système stun** : Implémenté dans `turn_manager.py`

## 📂 FICHIERS À NETTOYER

### `models/combat/abilities/ability_manager.py`
- **DÉJÀ FAIT** : `_apply_legacy_system()` désactivé (return False ligne ~55)
- **À SUPPRIMER** : `_apply_legacy_system()`, `_is_hero_specific_ability()`, `_activates_persistent_effect()`
- **À SUPPRIMER** : Imports modules legacy (`generic_effects`, `hero_specific`, `persistent_effects`)
- **CONSERVER** : `_try_individual_ability()` et `apply_ability_effects()`

### `combat_actions.py`  
- **DÉJÀ FAIT** : Fallback générique commenté ligne ~245-250
- **À SUPPRIMER** : Code commenté après migration complète

### `models/combat/abilities/generic_effects.py`
- **ATTENTION** : Contient système stun générique utilisé par ancien système
- **ACTION** : Analyser après migration complète P-3 à P-8

### `models/combat/abilities/hero_specific.py`
- **ACTION** : Supprimer après migration complète (remplacé par individual_abilities)

### `models/combat/abilities/persistent_effects.py`
- **CONSERVER** : Effets persistants utilisés par système global

## 🔍 MÉTHODES LEGACY À SUPPRIMER

### Dans `ability_manager.py`
```python
# À SUPPRIMER après migration complète
def _apply_legacy_system()
def _is_hero_specific_ability() 
def _activates_persistent_effect()
```

### Dans `combat_actions.py`
```python
# À SUPPRIMER (déjà commenté)
# if not effects_applied:
#     log.append(f"📖 {combatant_name} utilise {ability.name}")
#     log.append(f"   (Effet générique - capacité non implémentée)")
```

## 📊 STATISTIQUES MIGRATION

### Capacités implémentées
- **P-1 (Elneha)** : 6/6 ✅
- **P-2 (Liarie)** : 6/6 ✅
- **Autres** : À faire

### Système legacy utilisé
- **Ancien parsing** : 0% (désactivé)
- **Nouveau individuel** : 100% pour P-1/P-2

## ⚠️ ATTENTION AVANT NETTOYAGE

### Tests obligatoires
1. **Tous héros** fonctionnent (P-1 à P-8)
2. **48 capacités** implémentées
3. **diagnostic_capacites.py** = 48/48
4. **Aucune régression** fonctionnelle

### Ordre de suppression recommandé
1. `hero_specific.py` (premier)
2. `generic_effects.py` (si pas utilisé)
3. Méthodes legacy dans `ability_manager.py`
4. Fallbacks dans `combat_actions.py`

## 📅 PLANNING NETTOYAGE

- **Phase actuelle** : P-1/P-2 migrés, ancien système désactivé
- **Nettoyage intermédiaire** : Après P-3/P-4 (50%)
- **Nettoyage final** : Après migration complète (100%)

---
**Créé** : Décembre 2024  
**But** : Éviter d'oublier le code legacy à supprimer