# ⚠️ RÈGLE ABSOLUE - VÉRIFICATION ARCHITECTURE OBLIGATOIRE

**Date de création** : 28 octobre 2025  
**Priorité** : CRITIQUE  
**Statut** : OBLIGATOIRE AVANT TOUT DÉVELOPPEMENT

---

## 🚨 RÈGLE NUMÉRO 1 - ZÉRO DUPLICATION

**AVANT d'écrire UNE SEULE LIGNE DE CODE, TOUJOURS :**

### **Étape 1 : Recherche Architecture Exhaustive (OBLIGATOIRE)**

```bash
# RECHERCHES OBLIGATOIRES AVANT TOUT CODE :

1. project_knowledge_search "nom_fonctionnalité architecture existante"
2. project_knowledge_search "APIs classe_concernée"
3. project_knowledge_search "gestionnaire nom_fonctionnalité"
4. Lire documentation_architecture_périples.md
```

### **Étape 2 : Checklist Vérification**

Avant de créer TOUTE nouvelle classe/fonction, vérifier :

- [ ] **Une classe similaire existe-t-elle déjà ?**
  - Exemple : TurnManager, CombatActions, SpellManager
  
- [ ] **Cette méthode existe-t-elle dans Character/Enemy ?**
  - Exemple : start_hero_turn(), apply_damage_with_parade()
  
- [ ] **Un gestionnaire gère-t-il déjà cette logique ?**
  - Exemple : AbilityEffectsManager, TurnManager
  
- [ ] **Cette API est-elle documentée dans documentation_architecture_périples.md ?**
  
- [ ] **Le Plan-d-action.md mentionne-t-il cette fonctionnalité ?**

### **Étape 3 : Décision**

**SI une API/classe existe :**
- ✅ **RÉUTILISER** l'existant
- ✅ **WRAPPER** si besoin d'adaptation légère
- ❌ **NE JAMAIS DUPLIQUER**

**SI aucune API n'existe :**
- ✅ **DOCUMENTER** pourquoi nouvelle création nécessaire
- ✅ **VÉRIFIER** avec l'utilisateur avant de coder
- ✅ **AJOUTER** à la documentation après création

---

## 🔍 PROCESSUS DE VÉRIFICATION OBLIGATOIRE

### **Exemple : Créer système de combat pour Sandbox**

#### ❌ **MAUVAISE APPROCHE (Ce que j'ai fait)**
```python
# 1. Coder directement sans vérifier
class SandboxCombat:
    def start_player_turn(self):  # ❌ DUPLICATION de TurnManager
        # Réinventer la roue...
    
    def enemy_attack(self):  # ❌ DUPLICATION de CombatActions
        # Recréer calculs existants...
```

#### ✅ **BONNE APPROCHE (Ce qu'il fallait faire)**
```python
# 1. VÉRIFIER ARCHITECTURE
project_knowledge_search("TurnManager combat tour")
project_knowledge_search("CombatActions attaque")
project_knowledge_search("Character APIs tour")

# 2. DÉCOUVRIR L'EXISTANT
# - TurnManager.heroes_turn() existe
# - TurnManager.enemies_turn() existe
# - Character.start_hero_turn() existe
# - CombatActions.hero_attack() existe

# 3. RÉUTILISER + WRAPPER LÉGER
class SandboxTurnAdapter:
    """Adapter léger qui UTILISE TurnManager existant"""
    def __init__(self):
        self.turn_manager = TurnManager(...)  # ✅ RÉUTILISE
    
    def execute_hero_action_with_targeting(self, hero, target):
        # ✅ Ajoute SEULEMENT le ciblage manuel
        # ✅ Délègue le reste à TurnManager
        self.turn_manager.hero_turn(hero, ...)
```

---

## 📋 CHECKLIST PRÉ-DÉVELOPPEMENT MISE À JOUR

### **AVANT DE CODER (dans l'ordre) :**

1. [ ] **Lire Plan-d-action.md** (règles absolues)
2. [ ] **Lire documentation_architecture_périples.md** (architecture)
3. [ ] **project_knowledge_search exhaustive** (3-5 recherches minimum)
4. [ ] **Lister APIs existantes** trouvées
5. [ ] **Identifier réutilisables** vs à créer
6. [ ] **Demander validation** utilisateur si doute
7. [ ] **SEULEMENT APRÈS** → Écrire le code

### **PENDANT LE DÉVELOPPEMENT :**

1. [ ] **Réutiliser** classes/méthodes existantes
2. [ ] **Wrapper** si adaptation légère nécessaire
3. [ ] **Commenter** pourquoi choix faits
4. [ ] **Tester** intégration avec existant

### **APRÈS LE DÉVELOPPEMENT :**

1. [ ] **Documenter** nouvelles APIs créées
2. [ ] **Mettre à jour** documentation_architecture_périples.md
3. [ ] **Vérifier** pas de conflits avec existant

---

## 🚨 EXEMPLES DE DUPLICATIONS À ÉVITER

### **Duplication Type 1 : Gestionnaire de Combat**
```python
# ❌ MAUVAIS - Créer nouveau gestionnaire
class NewCombatManager:
    def manage_turns(self): ...

# ✅ BON - Utiliser existant
combat_engine = CombatEngine(rules)
turn_manager = TurnManager(spell_manager, combat_actions)
```

### **Duplication Type 2 : Méthodes Character**
```python
# ❌ MAUVAIS - Réinventer calculs
def calculate_total_health(character):
    return character.health + sum(item.health_bonus for item in character.equipped_items)

# ✅ BON - Utiliser API existante
total_health = character.get_total_health()
```

### **Duplication Type 3 : Gestion des Tours**
```python
# ❌ MAUVAIS - Recréer logique tour
def hero_start_turn(hero):
    hero.current_parade = hero.base_parade
    # Reset capacités...

# ✅ BON - Utiliser méthode existante
hero.start_hero_turn()
```

### **Duplication Type 4 : Calculs de Dégâts**
```python
# ❌ MAUVAIS - Calculs manuels
damage_dealt = max(0, base_damage - target.parade)
target.current_health -= damage_dealt

# ✅ BON - Utiliser API existante
damage_result = target.apply_damage_with_parade(base_damage)
```

---

## 📊 ARCHITECTURE EXISTANTE - RÉFÉRENCE RAPIDE

### **Gestionnaires Principaux**
- `CombatEngine` : Orchestration combat complet
- `TurnManager` : Gestion tours héros/ennemis
- `CombatActions` : Actions concrètes (attaques, capacités)
- `SpellManager` : Gestion des sorts
- `AbilityEffectsManager` : Application capacités
- `CombatLogger` : Logs de combat

### **Classes de Base**
- `Character` : Héros avec stats, équipements, capacités
- `Enemy` : Ennemis avec stats multi-joueurs
- `BaseAbility` : Classe parente capacités

### **APIs Critiques Character**
```python
.start_hero_turn()              # Début tour (parade + reset)
.get_total_health()             # HP totaux
.get_total_damage()             # Dégâts totaux
.get_total_parade()             # Parade totale
.apply_damage_with_parade(dmg) # Appliquer dégâts
.heal(amount)                   # Soigner
.is_alive()                     # Vivant ?
.use_ability(ability)           # Utiliser capacité
.use_health_potion()            # Utiliser potion
```

### **APIs Critiques TurnManager**
```python
.heroes_turn(heroes, enemies, player_count, log, active_pets)
.enemies_turn(enemies, heroes, player_count, log, active_pets)
.hero_turn(hero, alive_enemies, player_count, log, active_pets)
.pet_turn(pet, alive_enemies, player_count, log)
.heroes_distribute_damage(heroes, damage, enemy_name, log)
```

### **APIs Critiques CombatActions**
```python
.hero_attack(hero, enemies, player_count, log)
.use_ability_with_summon(hero, enemies, log, active_pets)
.try_health_potion(hero, log)
```

---

## 💡 QUAND CRÉER DE NOUVELLES APIS

### **Créer SEULEMENT si :**

1. **Fonctionnalité vraiment nouvelle**
   - Pas de duplication avec existant
   - Complète l'architecture (pas la remplace)
   - Besoin validé avec utilisateur

2. **Adaptation légère nécessaire**
   - Wrapper autour de classes existantes
   - Ajoute UNE fonctionnalité manquante
   - Délègue le reste à l'existant

3. **Interface utilisateur spécifique**
   - UI différente mais logique réutilisée
   - Exemple : Ciblage manuel vs IA

### **NE JAMAIS créer si :**

- ❌ Fonctionnalité existe déjà
- ❌ Peut être fait avec APIs existantes
- ❌ "Amélioration" d'une classe existante (modifier l'existant à la place)
- ❌ Doute sur nécessité (demander d'abord)

---

## 🎯 CAS D'USAGE : SANDBOX AVEC CIBLAGE MANUEL

### **Besoin Réel**
Ajouter ciblage manuel joueur au combat existant (remplacer IA)

### **Analyse Architecture**
```python
# ✅ EXISTE DÉJÀ :
- TurnManager gère tours héros/ennemis
- CombatActions applique attaques
- Character.apply_damage_with_parade() calcule dégâts
- heroes_distribute_damage() = IA tactique

# ❌ MANQUE :
- Interface UI pour joueur choisit cible (ennemi OU héros)
```

### **Solution Correcte**
```python
# 1. Créer SEULEMENT interface ciblage (UI)
class SandboxTargeting:
    """SEULEMENT l'interface de sélection"""
    @staticmethod
    def select_enemy_target(...):
        # UI Streamlit pour choisir ennemi
    
    @staticmethod
    def select_hero_target_for_enemy_attack(...):
        # UI Streamlit pour choisir héros (NOUVELLE RÈGLE)

# 2. Adapter TurnManager (wrapper léger)
class SandboxTurnManagerAdapter:
    """Adapter qui UTILISE TurnManager existant"""
    def __init__(self):
        self.turn_manager = TurnManager(...)  # ✅ RÉUTILISE
    
    def hero_turn_with_manual_targeting(self, hero, enemies, ...):
        # 1. UI : Joueur choisit cible
        target = SandboxTargeting.select_enemy_target(...)
        
        # 2. Déléguer à TurnManager existant
        self.turn_manager.hero_turn(hero, [target], ...)  # ✅ RÉUTILISE
    
    def enemy_turn_with_manual_targeting(self, enemy, heroes, ...):
        # 1. UI : Joueur choisit cible (REMPLACE IA)
        target = SandboxTargeting.select_hero_target_for_enemy_attack(...)
        
        # 2. Appliquer dégâts avec API existante
        self.combat_actions.apply_enemy_attack(enemy, target, ...)  # ✅ RÉUTILISE
```

### **Résultat**
- ✅ **Réutilise** 95% du code existant
- ✅ **Ajoute** SEULEMENT UI ciblage manuel (5% nouveau)
- ✅ **Pas de duplication** de logique combat
- ✅ **Maintient** cohérence architecture

---

## 🔴 CONSÉQUENCES NON-RESPECT RÈGLE

### **Si duplication créée :**

1. **Bugs différents** entre ancien et nouveau code
2. **Maintenance double** (corriger 2x)
3. **Incohérences** comportement
4. **Confusion** développeurs futurs
5. **Perte de temps** massif

### **Si règle respectée :**

1. ✅ **Code cohérent** partout
2. ✅ **Maintenance simple** (1 seul endroit)
3. ✅ **Bugs corrigés** globalement
4. ✅ **Architecture claire**
5. ✅ **Développement rapide**

---

## 📝 COMMIT À CETTE RÈGLE

**Je m'engage à :**

1. ✅ **TOUJOURS** faire 3-5 project_knowledge_search AVANT de coder
2. ✅ **TOUJOURS** lire documentation_architecture_périples.md AVANT
3. ✅ **TOUJOURS** lister APIs existantes AVANT
4. ✅ **TOUJOURS** demander validation utilisateur si doute
5. ✅ **JAMAIS** dupliquer code existant
6. ✅ **TOUJOURS** réutiliser et wrapper
7. ✅ **TOUJOURS** documenter nouvelles APIs créées

---

## 🎓 LEÇONS APPRISES

### **Erreur Commise (28 oct 2025)**
Création de `sandbox_combat.py` avec duplications massives :
- Dupliqué `TurnManager.start_player_turn()`
- Dupliqué `Character.start_hero_turn()`
- Dupliqué calculs dégâts
- Dupliqué gestion tours

### **Correction Appliquée**
- Suppression fichiers dupliqués
- Création adapter léger réutilisant existant
- Ajout SEULEMENT UI ciblage manuel
- Documentation de cette règle

### **Impact Positif**
- Code réduit de 80% (11Ko → 2Ko)
- Réutilisation architecture validée
- Pas de bugs divergents
- Maintenance simplifiée

---

**Cette règle est ABSOLUE et NON NÉGOCIABLE.**

**Date d'application** : Immédiate  
**Dernière mise à jour** : 28 octobre 2025