# CLEANUP_NOTES.md
# 🧹 NOTES POUR NETTOYAGE DU PROJET APRÈS MIGRATION

## 🎯 OBJECTIF
Supprimer le code legacy devenu inutile après migration complète vers capacités individuelles.

## 📂 FICHIERS À NETTOYER

### `models/combat/abilities/ability_manager.py`
- **Supprimer** : `_apply_legacy_system()` (ligne ~80-120)
- **Supprimer** : `_is_hero_specific_ability()` (ligne ~125-140)
- **Supprimer** : `_activates_persistent_effect()` (ligne ~145-160)
- **Supprimer** : Imports modules legacy (`generic_effects`, `hero_specific`, `persistent_effects`)
- **Conserver** : Uniquement `_try_individual_ability()` et `apply_ability_effects()`

### `models/combat/abilities/generic_effects.py`
- **ACTION** : Analyser si utilisé ailleurs
- **SI PAS UTILISÉ** : Supprimer entièrement
- **SI UTILISÉ** : Marquer comme @deprecated

### `models/combat/abilities/hero_specific.py`
- **ACTION** : Supprimer (remplacé par capacités individuelles)

### `models/combat/abilities/persistent_effects.py`
- **ACTION** : Conserver temporairement (effets de buff/debuff)
- **VÉRIFIER** : Si utilisé par le nouveau système

### `combat_actions.py`
- **Supprimer** : Ligne ~245-250 (fallback générique commenté)
- **Nettoyer** : Contexte inutile pour ancien système

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