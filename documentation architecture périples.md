# 📚 DOCUMENTATION ARCHITECTURE PÉRIPLES
**Guide complet du flux de l'application et des APIs**

## 🎯 OBJECTIF DE CE DOCUMENT

Cette documentation résout les problèmes récurrents :
- **Imports qui échouent** (exemple: kraor.py)
- **Fichiers orphelins** sans comprendre leur rôle
- **Flux de données** obscur entre composants
- **APIs cachées** et interactions complexes

## 🏗️ VUE D'ENSEMBLE DE L'ARCHITECTURE

```
Périples Balance Workshop
├── 🎮 Interface Streamlit (app.py)
├── 🧠 Logique Métier (models/)
├── 🎨 Interface Utilisateur (ui/)
├── 🔧 Utilitaires (utils/)
└── 📊 Données (data/)
```

### Flux Principal de Données
```
CSV/Excel → DataLoader → Character/Enemy → CombatEngine → Streamlit UI
    ↓           ↓            ↓              ↓            ↓
ability_names  heroes.csv   combat_actions  spell_manager  components/
equipment.csv  enemies.csv  ability_effects turn_manager   hero_components
```

---

## 📁 STRUCTURE DÉTAILLÉE DES FICHIERS

### 🎮 **Point d'Entrée Principal**
```
app.py (Application Streamlit principale)
├── Gestion des sessions utilisateur
├── Interface multi-onglets
├── Appel des composants UI
└── Orchestration générale
```

### 🧠 **Logique Métier - models/**

#### **models/character.py** - Cœur du système
```python
Classes principales :
- Character (héros + stats + équipements + buffs + capacités)
- Enemy (ennemis + stats basés CSV)
- Equipment (objets + bonus)
- HealthPotion (potions + mécaniques)
- VirtualAbility (capacités spéciales pets)

APIs critiques :
- current_health, get_total_health()
- temporary_buffs{} (système buffs temporaires)
- equipped_items[] (équipements)
- apply_damage_with_parade() (dégâts + parade)
- heal() (soins avec plafonnement)
```

#### **models/combat/combat_engine.py** ⚠️ **FICHIER VOLUMINEUX**
```python
Responsabilités (978 lignes) :
- Orchestration des combats
- Gestion des tours
- IA tactique
- Logs de combat
- Métriques finales

APIs principales :
- start_combat()
- process_turn()
- check_combat_end()
- generate_combat_report()
```

#### **models/combat/combat_actions.py** - Actions concrètes
```python
Responsabilités :
- Attaques physiques/magiques
- Utilisation des capacités
- Gestion des potions
- Modificateurs d'attaque

APIs importantes :
- hero_attack() - attaques de base
- use_ability() - système capacités
- apply_potion() - soins potion
```

#### **models/combat/spell_manager.py** - Gestion des sorts
```python
Responsabilités :
- Comptabilité sorts disponibles/utilisés
- Vérification coûts capacités magiques
- Synchronisation Character <-> SpellManager

APIs critiques :
- initialize_spells() - OBLIGATOIRE
- get_current_spells()
- consume_spells()
- can_use_magical_ability()
```

#### **models/combat/abilities/** - Système Capacités

**AbilityEffectsManager** - Chef d'orchestre
```python
Point d'entrée principal :
- apply_ability_effects() - API OFFICIELLE
- Remplace ancien système parsing
- Utilisé par debug_mode.py ET app principale
```

**BaseAbility** - Classe parente
```python
Méthodes héritées par toutes les capacités :
- _consume_spell_cost()
- _apply_healing()
- _apply_damage()
- _get_all_allies()
- _get_all_enemies()
- can_execute() (vérifications coût/limitations)
```

### 🎨 **Interface - ui/**

#### **ui/components/hero_components.py**
```python
Responsabilités :
- Calcul des builds basés équipements RÉELS
- Interface sélection héros
- Affichage stats équipe

Cache performance :
- @st.cache_data pour pré-calculs
- Évite recalculs identiques
```

### 🔧 **Utilitaires - utils/**

#### **utils/data_loader.py** - Chargeur de données
```python
APIs principales :
- load_heroes_data()
- load_enemies_data()
- load_equipment_data()
- get_hero_by_code() / get_enemy_by_code()

Gestion du cache :
- @st.cache_data pour fichiers CSV
- Évite rechargements multiples
```

---

## 🔄 **FLUX DE DONNÉES DÉTAILLÉ**

### 1. **Démarrage de l'Application**
```
app.py
├── DataLoader charge CSV/Excel → cache Streamlit
├── Interface utilisateur initialisée → session_state
└── Composants UI disponibles → hero_components, etc.
```

### 2. **Sélection d'Équipe**
```
hero_components.py
├── Lecture heroes.csv → DataLoader
├── Calcul builds équipements → equipment.csv 
├── Validation équipe → 2-4 héros
└── Création instances Character → character.py
```

### 3. **Configuration Combat**
```
app.py (onglet combat)
├── Sélection ennemis → enemies.csv
├── Création CombatEngine → combat_engine.py
├── Initialisation SpellManager → spell_manager.py
└── Lancement combat → process_turn()
```

### 4. **Tour de Combat**
```
combat_engine.py
├── Détermination initiative → random/stats
├── Actions héros → combat_actions.py
│   ├── Attaque normale → hero_attack()
│   ├── Capacité → AbilityEffectsManager
│   └── Potion → apply_potion()
├── Actions ennemis → enemy_attack()
└── Vérification fin → check_combat_end()
```

### 5. **Exécution Capacité**
```
AbilityEffectsManager.apply_ability_effects()
├── Recherche capacité → individual_abilities/
├── Vérification coût → spell_manager
├── Exécution → BaseAbility.execute()
├── Application effets → character.temporary_buffs
└── Logs → combat_logger
```

---

## 🚨 **PROBLÈMES COURANTS ET SOLUTIONS**

### ❌ **Problème : Import de Capacité Échoue**
```python
# ERREUR TYPIQUE
ImportError: cannot import name 'KraorCapacity' from 'models.combat.abilities.individual_abilities.heroes.kraor'

# CAUSES POSSIBLES :
1. Fichier kraor.py pas créé
2. Classe mal nommée  
3. @register_ability manquant
4. __init__.py non mis à jour
```

**✅ Solution :**
```python
# 1. Créer kraor.py dans individual_abilities/heroes/
# 2. Structure obligatoire :
from ..base_ability import BaseAbility
from ..ability_registry import register_ability

@register_ability  # ← CRITIQUE
class KraorCapacity1(BaseAbility):
    hero_code = "P-4"
    ability_number = 1
    # ...

# 3. Mettre à jour __init__.py :
__all__ = ['KraorCapacity1', ...]
```

### ❌ **Problème : APIs Character Incorrectes**
```python
# ERREURS FRÉQUENTES
character.current_wounds  # ← N'EXISTE PAS
character.max_health      # ← N'EXISTE PAS  
character.remove_debuffs()  # ← N'EXISTE PAS
```

**✅ APIs Correctes :**
```python
# SANTÉ
character.current_health  
character.get_total_health()  # ← Au lieu de max_health
character.heal(amount)

# BUFFS
character.temporary_buffs['buff_name'] = value
character.cleanup_expired_effects()  # ← Au lieu de remove_debuffs

# DÉGÂTS  
character.apply_damage_with_parade(damage)
```

### ❌ **Problème : SpellManager Désynchronisé**
```python
# SYMPTÔME
# Debug affiche "Sorts: 3/5" au lieu de "Sorts: 8/8"
```

**✅ Solution :**
```python
# SYNCHRONISATION OBLIGATOIRE
spell_manager = SpellManager()
spell_manager.initialize_spells(character)  # ← CRITIQUE
character.current_spells = character.spells  # ← DOUBLE INIT

# Dans debug_mode.py
combatant_id = spell_manager.get_combatant_id(user)
spell_manager.combatant_spells[combatant_id] = user_spells
user.current_spells = user_spells  # ← FORCE SYNC
```

---

## 🔌 **APIS ESSENTIELLES PAR COMPOSANT**

### **Character APIs (character.py)**
```python
# SANTÉ
.current_health : int                    # PV actuels
.get_total_health() : int               # PV max (base + équipement)
.heal(amount) : int                     # Soins (retourne réel soigné)
.apply_damage_with_parade(damage) : int # Dégâts avec parade

# STATS
.get_total_damage() : int               # Dégâts (base + équipement + buffs)
.get_total_precision() : int            # Précision totale
.get_equipment_bonus(type) : int        # Bonus équipement

# BUFFS/EFFETS
.temporary_buffs : Dict[str, Any]       # Buffs temporaires
.permanent_buffs : Dict[str, bool]      # Buffs permanents
.status_effects : Dict[str, int]        # Effets avec durée

# PARADE
.max_parade_tokens : int                # Parade maximum
.current_parade_tokens : int            # Parade actuelle
.reset_parade_tokens()                  # Reset début tour

# ÉQUIPEMENTS
.equipped_items : List[Equipment]       # Liste équipements
.has_equipment(code) : bool             # Vérification équipement
```

### **SpellManager APIs (spell_manager.py)**
```python
# INITIALISATION (OBLIGATOIRE)
.initialize_spells(character)           # Init système sorts

# LECTURE
.get_current_spells(character) : int    # Sorts actuels
.get_spells_used(character) : int       # Sorts consommés
.get_spells_max(character) : int        # Sorts maximum

# CONSOMMATION
.consume_spells(character, cost) : bool # Consommer sorts
.can_use_magical_ability(char, ability) # Vérifier utilisation

# INTERNAL (ne pas utiliser directement)
.combatant_spells : Dict[str, int]      # Stockage interne
```

### **AbilityEffectsManager APIs (ability_manager.py)**
```python
# API PRINCIPALE (utilisée partout)
.apply_ability_effects(character, ability, log, context) : bool

# CONTEXTE REQUIS
context = {
    'alive_enemies': enemies,           # Ennemis vivants
    'current_enemies': enemies,         # Alias
    'heroes': heroes,                   # Tous héros
    'current_heroes': heroes,           # Alias  
    'spell_manager': spell_manager,     # Manager sorts
    'log': log,                        # Liste logs
    'player_count': len(heroes)        # Nombre joueurs
}
```

### **BaseAbility APIs (base_ability.py)**
```python
# MÉTHODES HÉRITÉES (pour capacités individuelles)
._consume_spell_cost(caster, cost, mgr, log) : bool
._apply_healing(target, amount, log) : int
._apply_damage(target, amount, type, log) : int
._get_all_allies(caster, context) : List
._get_all_enemies(caster, context) : List
._is_alive(character) : bool

# MÉTHODES À IMPLÉMENTER
.execute(caster, targets, context, log) : bool
.can_execute(caster, context) : bool
.get_preview() : str  
.get_targets(caster, all_heroes, all_enemies, context) : List
```

---

## 🎯 **PATTERNS DE DÉVELOPPEMENT**

### **Pattern: Création Nouvelle Capacité**
```python
# 1. Créer fichier hero.py dans individual_abilities/heroes/
# 2. Structure standard :

from typing import List, Dict, Any
from ..base_ability import BaseAbility
from ..ability_registry import register_ability

@register_ability
class HeroNewAbility(BaseAbility):
    hero_code = "P-X"  # Code héros
    ability_number = Y  # Numéro capacité
    name = "Nom Officiel"  # Depuis ability_names.csv
    description = "Description"
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = Z  # Depuis Sorts.xlsx
        self.uses_per_combat = None  # Si limité
    
    def execute(self, caster, targets, context, log):
        # 1. Vérifier/consommer sorts
        spell_manager = context.get('spell_manager')
        if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
            return False
        
        # 2. Logique capacité
        # 3. Retourner True/False
        
    def can_execute(self, caster, context):
        # Vérifications pré-exécution
        return super().can_execute(caster, context)
```

### **Pattern: Debug d'une Capacité**
```python
# debug_mode.py - Structure type

# 1. Contexte standard
context = {
    'alive_enemies': enemies,
    'heroes': [user] + allies,
    'spell_manager': spell_manager,
    'log': execution_log
}

# 2. API officielle (IDENTIQUE app principale)
ability_effects_manager = AbilityEffectsManager(spell_manager)
result = ability_effects_manager.apply_ability_effects(
    user, ability_instance, execution_log, context
)

# 3. Vérifications
if result:
    st.success("✅ apply_ability_effects() retourné True")
else:
    st.warning("⚠️ apply_ability_effects() retourné False")
```

### **Pattern: Synchronisation SpellManager**
```python
# TOUJOURS faire cette séquence pour éviter désync

spell_manager = SpellManager()

# Pour chaque personnage :
spell_manager.initialize_spells(character)  # ← ÉTAPE 1
character.current_spells = character.spells # ← ÉTAPE 2

# En debug mode, forcer sync :
combatant_id = spell_manager.get_combatant_id(character)
spell_manager.combatant_spells[combatant_id] = desired_spells
character.current_spells = desired_spells
```

---

## 🚀 **OPTIMISATIONS ET PERFORMANCES**

### **Cache Streamlit**
```python
# Données statiques (CSV/Excel)
@st.cache_data
def load_static_data():
    return pd.read_csv('data/heroes.csv')

# Calculs coûteux mais déterministes  
@st.cache_data
def calculate_build_stats(hero_code, equipment_codes):
    # Calcul basé uniquement sur paramètres
    return stats
```

### **Gestion Mémoire**
```python
# Éviter les fuites lors des combats longs
def cleanup_after_combat():
    character.cleanup_expired_effects()
    spell_manager.reset_all_counters()
    ability_effects_manager.clear_caches()
```

### **Architecture Modulaire Future**
```
# PRÉVU : Split combat_engine.py (978 lignes)
models/combat/
├── spell_manager.py      (~120 lignes)
├── combat_actions.py     (~200 lignes)  
├── turn_manager.py       (~220 lignes)
├── combat_logger.py      (~180 lignes)
└── combat_engine.py      (~250 lignes)
```

---

## 📝 **CHECKLIST DÉVELOPPEMENT**

### **Avant de créer une nouvelle capacité :**
- [ ] Vérifier ability_names.csv pour nom officiel
- [ ] Vérifier Sorts.xlsx pour coût et limitations
- [ ] project_knowledge_search pour APIs existantes
- [ ] Identifier template BaseAbility approprié

### **Pendant le développement :**
- [ ] Utiliser UNIQUEMENT APIs confirmées (character.py, spell_manager.py)
- [ ] Implémenter mécaniques réelles (pas seulement logs)
- [ ] Tester execute(), can_execute(), get_preview()
- [ ] Vérifier gestion d'erreurs (try/except)

### **Après implémentation :**
- [ ] Test debug_mode.py → Niveau 2 minimum
- [ ] Vérifier @register_ability présent
- [ ] Mettre à jour __init__.py et __all__
- [ ] Test production si possible → Niveau 3

### **Résolution problèmes import :**
- [ ] Fichier existe dans bon dossier ?
- [ ] Classe bien nommée et exportée ?
- [ ] @register_ability présent ?
- [ ] __init__.py mis à jour ?
- [ ] Pas de circular imports ?

---

## 🎯 **RÉSUMÉ POUR DÉVELOPPEMENT RAPIDE**

**Pour ajouter une nouvelle capacité :**
1. **project_knowledge_search** → APIs existantes
2. **Créer fichier hero.py** → individual_abilities/heroes/
3. **Structure BaseAbility** → @register_ability + execute()
4. **Test debug_mode.py** → apply_ability_effects()
5. **Mettre à jour __init__.py** → exports

**Pour débugger un problème :**
1. **Vérifier imports** → __init__.py et chemins
2. **Vérifier APIs** → character.py documentation
3. **Vérifier SpellManager sync** → initialize_spells()
4. **Logs debug_mode.py** → exécution pas à pas

**Pour optimiser :**
1. **Cache Streamlit** → @st.cache_data
2. **APIs directes** → Éviter couches inutiles  
3. **Cleanup régulier** → Éviter fuites mémoire

Cette documentation devrait considérablement réduire le temps perdu à chercher des informations techniques et résoudre les problèmes d'import récurrents !