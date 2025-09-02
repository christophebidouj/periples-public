# 🎯 PLAN D'ACTION - MIGRATION CAPACITÉS PÉRIPLES
**Version : Post-Debug Critical Fixes - Septembre 2025**

## ⚠️ RÈGLES ABSOLUES CLAUDE

### 🚨 AVANT TOUT DÉVELOPPEMENT
1. **LIRE INTÉGRALEMENT** ce plan d'action (règle critique ajoutée)
2. **VÉRIFIER** `Sorts.xlsx` pour données officielles
3. **TESTER** imports : `from models.character import Character`
4. **INTERDICTION** : Inventer valeurs numériques
5. **APPLIQUER** fixes debug_mode.py systématiquement

### 📊 Sources données OBLIGATOIRES
- **Noms** : `ability_names.csv` 
- **Mécaniques** : `Sorts.xlsx` (coûts, limitations)
- **API** : `character.py` + `data_loader.py` + `base_ability.py` + `spell_manager.py`

---

## 📈 ÉTAT ACTUEL - RETEST COMPLET REQUIS
**TOTAL** : 18/59 capacités (30%) - **TOUTES À RETESTER**
- **P-1 (Elneha)** : 6/6 ⚠️ RETEST après fixes debug
- **P-2 (Liarie)** : 6/6 ⚠️ RETEST + corriger magical_armor_bonus 
- **P-3 (Atucan)** : 6/6 ⚠️ RETEST + revoir IA restrictive

**PRIORITÉ CRITIQUE** : Debug_mode.py corrigé - **retester TOUTES les capacités**

---

## ⚙️ API VALIDÉE - FIXES CRITIQUES APPLIQUÉS

### BaseAbility (Classe mère critique)
```python
# ✅ API standardisée pour toutes les capacités
class NewAbility(BaseAbility):
    def execute(self, caster, targets, context, log):
        # Méthodes utilitaires héritées:
        self._consume_spell_cost(caster, cost, spell_manager, log)
        self._get_all_enemies(caster, context)  # cherche 'alive_enemies'
        self._get_all_allies(caster, context)   # cherche 'heroes'
        self._apply_damage(target, amount, type, log)
        self._apply_healing(target, amount, log)
```

### SpellManager (Gestion centralisée sorts)
```python
spell_manager = SpellManager()
spell_manager.initialize_spells(combatant)  # Initialisation obligatoire
spell_manager.get_current_spells(combatant)  # Sorts disponibles
spell_manager.consume_spells(combatant, cost)  # Consommation
```

### Character (Hero) - Architecture sorts résolue
```python
# ✅ DOUBLE INITIALISATION OBLIGATOIRE
user = Character(code="P-1", spells=5, ...)
user.current_spells = user.spells  # FIX #1: current_spells

# ✅ API validée
hero.get_attack_damage_info()['damage_value']
hero.current_health / hero.is_alive()
hero.apply_damage_with_parade(damage)
```

### Enemy API
```python
enemy.get_damage_info(player_count)['damage_value'] 
enemy.defense / enemy.is_alive()
# ❌ ATTENTION: N'a PAS get_attack_damage_info()
```

### Debug Context - Clés critiques identifiées
```python
# ✅ CLÉS CORRECTES (BaseAbility les cherche)
context = {
    'spell_manager': spell_manager,
    'heroes': allies,
    'current_heroes': allies,  
    'alive_enemies': enemies,
    'current_enemies': enemies,
    'log': execution_log,
    'player_count': 2
}

# ❌ CLÉS FAUSSES (à éviter)
# 'rules', 'all_heroes', 'all_enemies'
```

---

## 🚨 ERREURS RÉSOLUES

### Bug SpellManager (résolu)
- **Problème** : `spell_manager.get_current_spells(user)` retournait 0
- **Solution** : `spell_manager.initialize_spells(user)` obligatoire

### Bug Context Debug (résolu)  
- **Problème** : BaseAbility ne trouvait pas les ennemis
- **Solution** : Utiliser 'alive_enemies', 'current_enemies', 'heroes'

### Bug Affichage (résolu)
- **Solution** : Noms héros avec codes (P-1 Elneha au lieu de P-1)

---

## 🔄 PROCESSUS RÉVISÉ (30 min par capacité)

### 1. Setup Debug (5 min)
- Mode debug avec fixes appliqués  
- Configuration sorts/PV/ennemis

### 2. Test isolation (10 min)
```python
# Template sécurisé vérifié
class NewAbility(BaseAbility):
    def execute(self, caster, targets, context, log):
        spell_manager = context.get('spell_manager')
        if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
            return False
        # Implémentation...
```

### 3. Validation (10 min)  
- Execute() retourne True
- Logs corrects (sorts consommés, effets appliqués)
- État avant/après cohérent

### 4. Documentation (5 min)
- Mettre à jour statut dans ce plan
- Noter API utilisée

---

## 🛠️ PRIORITÉ #1 : RETEST SYSTÉMATIQUE

### Phase A - Validation fixes
1. **Éclair magique P-2** - Test référence (doit fonctionner)
2. **Armure du mage P-2** - Test sorts coûteux (doit fonctionner)  
3. **Forme d'ours P-1** - Test transformations (doit fonctionner)

### Phase B - Retest complet P-1/P-2/P-3
- **Toutes les 18 capacités** à retester avec debug corrigé
- **Identifier** celles qui échouent encore  
- **Corriger** une par une

### Phase C - Correction erreurs identifiées
- **magical_armor_bonus** → max_parade_tokens (P-2)
- **IA Atucan** trop restrictive (P-3)

---

## 📊 API CONSISTENCY GUIDE - TRAVAIL EFFECTUÉ

### Problèmes identifiés et résolus
1. **current_spells non initialisé** → Fix appliqué debug_mode.py
2. **SpellManager vide** → initialize_spells() obligatoire  
3. **Context debug incompatible** → Clés BaseAbility ajoutées
4. **Mauvaise API Enemy** → get_damage_info(player_count) documentée

### Règles validées par l'expérience
- **SpellManager prioritaire** sur current_spells direct
- **BaseAbility cherche clés spécifiques** dans context
- **API Character ≠ API Enemy** (méthodes différentes)
- **Debug doit simuler vrai contexte combat**

### Template debug validé
```python
# Configuration utilisateur
user.current_spells = user_spells  # CRITIQUE

# SpellManager 
spell_manager.initialize_spells(user)  # CRITIQUE

# Context BaseAbility
context = {'spell_manager', 'heroes', 'alive_enemies', 'log', 'player_count'}
```

---

## 🎯 ACTIONS IMMÉDIATES

### 🔥 URGENT - Tests de validation
1. **Tester** Éclair magique (doit infliger dégâts aux ennemis)
2. **Tester** Armure du mage (doit consommer 2 sorts) 
3. **Tester** une capacité P-1 et P-3

### 📋 COURT TERME - Retest complet
1. **Retester les 18 capacités** avec debug corrigé
2. **Identifier** et corriger les échecs restants
3. **Finaliser** P-1, P-2, P-3 avant P-4

### 🚀 LONG TERME - Suite migration  
1. **P-4 Kraor** avec processus validé
2. **P-5 à P-8** avec debug fiable
3. **Capacités bonus** P-10 à P-12

---

## 🎯 OBJECTIF FINAL
**59/59 capacités** fonctionnelles via debug_mode.py corrigé avec architecture SpellManager maîtrisée

---
**Version** : Post-debug fixes - Retest systématique requis  
**Usage** : Guide de développement sans régression technique  
**Prochaine étape** : Validation fixes puis retest complet