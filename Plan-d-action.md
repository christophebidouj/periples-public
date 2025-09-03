# 🎯 PLAN D'ACTION - MIGRATION CAPACITÉS PÉRIPLES
**Version : API Consistency Fixes - Septembre 2025**

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
- **P-1 (Elneha)** : 6/6 ⚠️ RETEST après fixes debug + BaseAbility
- **P-2 (Liarie)** : 6/6 ⚠️ RETEST + corriger magical_armor_bonus 
- **P-3 (Atucan)** : 6/6 ⚠️ RETEST + revoir IA restrictive

**PRIORITÉ CRITIQUE** : BaseAbility.can_execute() incomplet - **fix avant tests**

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
    
    # 🚨 REQUIS - Fix can_execute() manquant
    def can_execute(self, caster, context):
        # Vérifications uses_remaining_combat manquantes
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

### Bug Forme d'ours décompte (résolu)
- **Problème** : `self.uses_remaining_combat -= 1` manquant dans execute()
- **Solution** : Ajout décompte avant return True

### Bug Forme de loup NoneType (résolu)
- **Problème** : `current_attack += 1` sur attribut None
- **Solution** : Initialisation `current_attack = caster.damage` avant modification

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
        # Initialiser attributs si None (transformations)
        if not hasattr(caster, 'current_attack') or caster.current_attack is None:
            caster.current_attack = caster.damage
        # Implémentation...
        # Décompter utilisations si limitées
        if hasattr(self, 'uses_remaining_combat') and self.uses_remaining_combat is not None:
            self.uses_remaining_combat -= 1
```

### 3. Validation (10 min)  
- Execute() retourne True
- Logs corrects (sorts consommés, effets appliqués)
- État avant/après cohérent
- Uses_remaining_combat décompté correctement

### 4. Documentation (5 min)
- Mettre à jour statut dans ce plan
- Noter API utilisée

---

## 🛠️ PRIORITÉ #1 : FIX BASEABILITY PUIS RETEST

### Phase A - Fix BaseAbility critique
1. **Corriger BaseAbility.can_execute()** - Ajouter vérification uses_remaining_combat
2. **Tester correction** avec Forme d'ours (doit passer 1/1 → 0/1)

### Phase B - Validation fixes précédents
1. **Éclair magique P-2** - Test référence (doit fonctionner)
2. **Armure du mage P-2** - Test sorts coûteux (doit fonctionner)  
3. **Forme d'ours P-1** - Test transformations + décompte correct

### Phase C - Retest complet P-1/P-2/P-3
- **Toutes les 18 capacités** à retester avec BaseAbility corrigé
- **Identifier** celles qui échouent encore  
- **Corriger** une par une

### Phase D - Correction erreurs identifiées
- **magical_armor_bonus** → max_parade_tokens (P-2)
- **IA Atucan** trop restrictive (P-3)

---

## 📊 API CONSISTENCY GUIDE - TRAVAIL EFFECTUÉ

### Problèmes identifiés et résolus
1. **current_spells non initialisé** → Fix appliqué debug_mode.py
2. **SpellManager vide** → initialize_spells() obligatoire  
3. **Context debug incompatible** → Clés BaseAbility ajoutées
4. **Mauvaise API Enemy** → get_damage_info(player_count) documentée
5. **BaseAbility.can_execute() incomplet** → Manque vérification uses_remaining_combat
6. **Duplication logique** → can_use() vs can_execute() font le même travail
7. **Transformations NoneType** → Initialisation attributs manquante
8. **Décompte utilisations manquant** → uses_remaining_combat -= 1 oublié

### 🚨 PROBLÈME CRITIQUE DÉCOUVERT - BaseAbility.can_execute()

**Bug identifié :** `BaseAbility.can_execute()` ne vérifie pas `uses_remaining_combat`
```python
# ❌ ACTUEL - Vérifications incomplètes dans base_ability.py
def can_execute(self, caster, context):
    spell_manager = context.get('spell_manager')
    if not spell_manager: return False
    if hasattr(self, 'spell_cost') and self.spell_cost > 0:
        return caster.current_spells >= self.spell_cost
    return True  # MANQUE : uses_remaining_combat <= 0

# ✅ REQUIS - Vérifications complètes
def can_execute(self, caster, context):
    spell_manager = context.get('spell_manager')
    if not spell_manager: return False
    
    # Vérifier utilisations restantes (MANQUANT ACTUELLEMENT)
    if hasattr(self, 'uses_remaining_combat') and self.uses_remaining_combat is not None:
        if self.uses_remaining_combat <= 0:
            return False
    
    # Vérifier coût en sorts
    if hasattr(self, 'spell_cost') and self.spell_cost > 0:
        current_spells = spell_manager.get_current_spells(caster)
        return current_spells >= self.spell_cost
    
    return True
```

**Impact :** Capacités limitées (Forme d'ours 1/combat) restent "utilisables" après consommation

### Architecture dédoublée identifiée
- **abilities.py** : `can_use()` avec toutes vérifications (ancien système) ✅
- **BaseAbility** : `can_execute()` avec vérifications partielles (nouveau système) ❌

### Pattern transformations découvert
```python
# 🚨 PATTERN REQUIS pour toutes transformations
# Initialiser AVANT modification pour éviter NoneType
if not hasattr(caster, 'current_attack') or caster.current_attack is None:
    caster.current_attack = caster.damage
if not hasattr(caster, 'current_precision') or caster.current_precision is None:
    caster.current_precision = caster.precision

# Puis appliquer bonus
caster.current_attack += bonus_value
```

### Règles validées par l'expérience
- **SpellManager prioritaire** sur current_spells direct
- **BaseAbility cherche clés spécifiques** dans context
- **API Character ≠ API Enemy** (méthodes différentes)
- **Debug doit simuler vrai contexte combat**
- **Vérifications uses_remaining_combat obligatoires** dans can_execute()
- **Initialisation attributs current_* obligatoire** avant modifications
- **Décompte uses_remaining_combat obligatoire** dans execute()

### Template debug validé
```python
# Configuration utilisateur
user.current_spells = user_spells  # CRITIQUE

# SpellManager 
spell_manager.initialize_spells(user)  # CRITIQUE

# Context BaseAbility
context = {'spell_manager', 'heroes', 'alive_enemies', 'log', 'player_count'}

# Pattern capacité sécurisé
class SecureAbility(BaseAbility):
    def execute(self, caster, targets, context, log):
        # 1. Coût sorts
        if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
            return False
        
        # 2. Initialiser attributs si None (transformations)
        if not hasattr(caster, 'current_stat') or caster.current_stat is None:
            caster.current_stat = caster.base_stat
        
        # 3. Logique capacité
        # ...
        
        # 4. Décompte utilisations
        if hasattr(self, 'uses_remaining_combat') and self.uses_remaining_combat is not None:
            self.uses_remaining_combat -= 1
        
        return True
```

---

## 🎯 ACTIONS IMMÉDIATES

### 🔥 URGENT - Fix BaseAbility puis validation
1. **Corriger BaseAbility.can_execute()** - Ajouter vérification uses_remaining_combat

### 📋 COURT TERME - Retest complet
1. **Retester les 18 capacités** avec BaseAbility corrigé
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
**Version** : API Consistency Fixes - BaseAbility can_execute() critique  
**Usage** : Guide de développement sans régression technique  
**Prochaine étape** : Fix BaseAbility puis retest systématique