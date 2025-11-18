# 🔮 DOCUMENTATION : Intégration des Capacités dans SandboxV2

**Date de création** : 18 novembre 2025
**Objectif** : Guide complet pour implémenter et tester les capacités des héros dans SandboxV2
**Sessions concernées** : Toutes les sessions Claude travaillant sur les capacités individuelles

---

## 📋 TABLE DES MATIÈRES

1. [Architecture globale](#architecture-globale)
2. [Flux d'exécution des capacités](#flux-dexécution-des-capacités)
3. [Anatomie d'une capacité](#anatomie-dune-capacité)
4. [Bugs communs et solutions](#bugs-communs-et-solutions)
5. [Protocole de test](#protocole-de-test)
6. [Checklist avant commit](#checklist-avant-commit)

---

## 🏗️ ARCHITECTURE GLOBALE

### Principe clé : **ZÉRO DUPLICATION**

SandboxV2 **RÉUTILISE** l'architecture existante via des adapters :

```
UI (sandbox_interface_v2.py)
    ↓
use_ability_action()
    ↓
Character.use_ability() ← Vérifications (sorts, limitations)
    ↓
AbilityEffectsManager.apply_ability_effects() ← Exécution effets RÉELS
    ↓
Capacité individuelle (atucan.py, elneha.py, etc.)
    ↓
Modifications des objets Character/Enemy (PV, buffs, etc.)
    ↓
st.rerun() → Cartes UI se rafraîchissent automatiquement
```

### Fichiers clés

| Fichier | Rôle | À modifier ? |
|---------|------|--------------|
| `ui/components/sandbox_interface_v2.py` | Interface UI + ciblage manuel | ⚠️ Rarement |
| `models/combat/abilities/individual_abilities/heroes/*.py` | Capacités individuelles par héros | ✅ Toujours |
| `models/combat/abilities/ability_manager.py` | Manager central capacités | ❌ Jamais |
| `models/character.py` | APIs héros (PV, buffs, parade) | ⚠️ Occasionnellement |
| `models/combat/abilities/individual_abilities/base_ability.py` | Classe parente + méthodes utilitaires | ⚠️ Occasionnellement |

---

## ⚡ FLUX D'EXÉCUTION DES CAPACITÉS

### Étape 1 : Clic sur bouton capacité

```python
# ui/components/sandbox_interface_v2.py:1010
if st.button(button_label, key=button_key, disabled=not is_available):
    if is_available:
        use_ability_action(char, ability)  # ← Point d'entrée
```

### Étape 2 : Vérifications + préparation contexte

```python
# ui/components/sandbox_interface_v2.py:1197-1241
def use_ability_action(char: Character, ability):
    # 1. Vérifications (sorts, limitations)
    action = char.use_ability(ability)

    if action.success:
        # 2. Préparer contexte pour AbilityEffectsManager
        context = {
            'alive_enemies': [e for e in enemies if e.is_alive()],
            'current_enemies': [...],  # Alias
            'heroes': heroes,
            'current_heroes': heroes,  # Alias
            'spell_manager': adapter.spell_manager,
            'log': st.session_state.sandbox_v2_log,
            'player_count': len([h for h in heroes if h.is_alive()])
        }

        # 3. Exécuter effets RÉELS
        result = adapter.ability_effects_manager.apply_ability_effects(
            char, ability, st.session_state.sandbox_v2_log, context
        )

        # 4. Sauvegarder + rafraîchir
        save_game_state(...)
        st.rerun()  # ← Les cartes affichent les nouvelles stats
```

### Étape 3 : Exécution dans la capacité individuelle

```python
# models/combat/abilities/individual_abilities/heroes/atucan.py:54
def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
    # 1. Consommer sorts
    if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
        return False

    # 2. Logique métier (calculs, ciblage)
    healing_amount = caster.current_health // 2

    # 3. Appliquer effets via APIs
    self._apply_healing(target, healing_amount, log)

    # 4. Logs détaillés
    log.append(f"✨ {caster.name} impose ses mains sur {target.name}")

    return True
```

---

## 🧬 ANATOMIE D'UNE CAPACITÉ

### Structure minimale

```python
from typing import List, Dict, Any
from ..base_ability import BaseAbility
from ..ability_registry import register_ability

@register_ability  # ← OBLIGATOIRE pour enregistrement
class HeroAbilityName(BaseAbility):
    """Description courte de la capacité"""

    hero_code = "P-X"  # Code du héros (P-1, P-2, etc.)
    ability_number = Y  # Numéro de capacité (1-6)
    name = "Nom Officiel"  # Depuis ability_names.csv
    description = "Description officielle"

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = Z  # Coût en sorts (depuis Sorts.xlsx)
        self.uses_per_combat = N  # Si limité (1/combat, 2/combat, etc.)
        self.uses_remaining_combat = N  # Compteur

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Exécute les effets RÉELS de la capacité"""
        try:
            # 1. Consommer sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False

            # 2. Vérifier limitation combat
            if hasattr(self, 'uses_remaining_combat') and self.uses_remaining_combat <= 0:
                log.append(f"⚠️ {self.name} déjà utilisée ce combat")
                return False

            # 3. LOGIQUE MÉTIER (spécifique à chaque capacité)
            # ...

            # 4. Appliquer effets via APIs BaseAbility
            # ...

            # 5. Décompter utilisation si limitée
            if hasattr(self, 'uses_remaining_combat'):
                self.uses_remaining_combat -= 1

            # 6. Logs descriptifs
            log.append(f"✨ {caster.name} utilise {self.name}")

            return True

        except Exception as e:
            log.append(f"❌ Erreur {self.name}: {e}")
            return False

    def get_preview(self) -> str:
        """Aperçu des effets pour UI"""
        return f"🔮 {self.name}: Description courte (Coût: {self.spell_cost} sorts)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        """Détermine les cibles valides"""
        # Exemples :
        # - Soins alliés sauf caster : [h for h in all_heroes if h != caster and h.is_alive()]
        # - Tous ennemis : [e for e in all_enemies if e.is_alive()]
        # - Caster uniquement : [caster]
        return [caster]
```

### APIs BaseAbility disponibles

```python
# SOINS
self._apply_healing(target, amount, log) → int
# Plafonne automatiquement au PV max, log détaillé

# DÉGÂTS
self._apply_damage(target, amount, damage_type, log) → int
# damage_type: 'physical' ou 'magical'
# Gère automatiquement la parade

# SORTS
self._consume_spell_cost(caster, cost, spell_manager, log) → bool
# Vérifie + consomme, retourne False si insuffisant

# CIBLAGE
self._get_all_allies(caster, context) → List[Character]
self._get_all_enemies(caster, context) → List[Enemy]

# VÉRIFICATIONS
self._is_alive(character) → bool
```

### APIs Character pour buffs temporaires

```python
# BUFFS TEMPORAIRES (durée 1 tour)
caster.temporary_buffs['buff_name'] = value

# Exemples documentés :
caster.temporary_buffs['temporary_defense_bonus'] = 2  # +2 parade (Parade Atucan)
caster.temporary_buffs['damage_bonus_next_attack'] = 4  # +4 dégâts (Châtiment divin)
caster.temporary_buffs['double_next_attack'] = True  # x2 dégâts (Forme de loup)
caster.temporary_buffs['no_retaliation'] = True  # Pas de riposte

# FLAGS LIMITATIFS (1 fois par tour)
caster.temporary_buffs['parade_used_this_turn'] = True
caster.can_attack_this_turn = False  # Bloquer attaque
```

### Reset automatique des buffs temporaires

**IMPORTANT** : Les buffs temporaires sont **automatiquement nettoyés** au début du tour suivant :

```python
# models/character.py:1211-1218 (start_hero_turn)
if hasattr(self, 'temporary_buffs'):
    self.temporary_buffs.pop('parade_used_this_turn', None)
    self.temporary_buffs.pop('cannot_attack_this_turn', None)
    self.temporary_buffs.pop('temporary_defense_bonus', None)  # Parade d'Atucan
```

**Ajouter** vos buffs temporaires à cette liste si durée = 1 tour.

---

## 🐛 BUGS COMMUNS ET SOLUTIONS

### Bug 1 : Capacité n'apparaît pas dans l'UI

**Symptôme** : Grille de capacités vide ou capacité manquante

**Causes** :
1. `@register_ability` manquant
2. Fichier non importé dans `__init__.py`
3. Classe mal nommée

**Solution** :
```python
# 1. Vérifier décorateur
@register_ability  # ← OBLIGATOIRE
class AtucanParade(BaseAbility):
    ...

# 2. Vérifier __init__.py
# models/combat/abilities/individual_abilities/heroes/__init__.py
from .atucan import AtucanImpositionDesMains, AtucanParade  # ...
__all__ = ['AtucanImpositionDesMains', 'AtucanParade', ...]
```

---

### Bug 2 : Effets ne se produisent pas (PV inchangés)

**Symptôme** : Logs affichés mais stats non modifiées sur cartes

**Causes** :
1. Utilisation de logs au lieu d'APIs réelles
2. Oubli de `st.rerun()` dans UI

**Solution** :
```python
# ❌ MAUVAIS - Logs seulement (simulation)
log.append(f"💚 {target.name} récupère 5 PV")

# ✅ BON - API réelle
actual_healing = self._apply_healing(target, 5, log)
# → Modifie target.current_health + log automatique
```

---

### Bug 3 : Soins dépassent PV max

**Symptôme** : Héros a 25/20 PV après soin

**Cause** : Ancienne version de `_apply_healing()` sans plafonnement

**Solution** : **Déjà corrigée** dans `base_ability.py:112-132`

```python
# Plafonnement automatique
max_hp = target.get_total_health() if hasattr(target, 'get_total_health') else target.max_health
target.current_health = min(target.current_health + amount, max_hp)
```

---

### Bug 4 : Détection d'équipement incorrecte

**Symptôme** : Capacité ne détecte pas un bouclier/armure

**Cause** : Vérification via `equipment.type` au lieu du nom

**Solution** :
```python
# ❌ MAUVAIS - Type générique
if equipment.type.lower() == 'armure':  # Attrape plastrons, casques, etc.

# ✅ BON - Nom spécifique
equipment_name_lower = equipment.name.lower()
if 'bouclier' in equipment_name_lower or 'rondache' in equipment_name_lower:
```

**Liste des boucliers officiels** :
- Rondache de bois (O-29, DEF+1)
- Bouclier de bois (O-30, DEF+2)
- Bouclier de fer (O-31, DEF+3)

---

### Bug 5 : Capacité réutilisable à l'infini

**Symptôme** : Parade/Châtiment utilisable plusieurs fois par tour

**Causes** :
1. Pas de flag `used_this_turn`
2. Pas de reset du flag au tour suivant

**Solution** :
```python
# 1. Dans execute() - Marquer comme utilisée
caster.temporary_buffs['ability_name_used_this_turn'] = True

# 2. Dans character.py:start_hero_turn() - Reset automatique
self.temporary_buffs.pop('ability_name_used_this_turn', None)

# 3. Dans UI - Vérifier flag pour griser bouton
ability_already_used = char.temporary_buffs.get('ability_name_used_this_turn', False)
is_available = ... and not ability_already_used
```

---

### Bug 6 : Bonus non visible sur cartes

**Symptôme** : Parade activée mais 🛡️ inchangé sur carte

**Cause** : Buff non pris en compte dans `get_total_parade()`

**Solution** : **Déjà corrigée** dans `character.py:326-352`

```python
def get_total_parade(self) -> int:
    base_parade = self.get_equipment_bonus('defense')
    # ...
    temporary_bonus = self.temporary_buffs.get('temporary_defense_bonus', 0)  # ← NOUVEAU
    return base_parade + ... + temporary_bonus
```

**Principe** : Les cartes appellent `get_total_X()` pour afficher les stats → buffs temporaires doivent être inclus.

---

### Bug 7 : Capacité cible le lanceur alors qu'elle ne devrait pas

**Symptôme** : Imposition des mains soigne Atucan lui-même

**Cause** : Filtre `hero != caster` manquant

**Solution** :
```python
def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
    # ❌ MAUVAIS - Inclut le lanceur
    return [hero for hero in all_heroes if hero.is_alive()]

    # ✅ BON - Exclut le lanceur (règle "autre personnage")
    return [hero for hero in all_heroes if hero != caster and hero.is_alive()]
```

---

## 🧪 PROTOCOLE DE TEST

### Configuration standard

1. Lancer `streamlit run app.py`
2. **Onglet Sélection** : Choisir 2+ héros (dont le héros à tester)
3. **Onglet Sélection** : Choisir 1-2 ennemis (E-1 faible + E-10 moyen)
4. **Sandbox V2** : Désactiver Initiative (mode manuel)
5. **Sandbox V2** : Cliquer "Configurer le Combat"

### Checklist de test par capacité

Pour **chaque capacité testée** :

- [ ] **Bouton visible** : Capacité apparaît dans la grille 3x2
- [ ] **Bouton activable** : Pas grisé si conditions remplies (sorts, non utilisée)
- [ ] **Coût sorts** : Sorts diminuent après utilisation (ex: 8→7)
- [ ] **Logs détaillés** : Messages descriptifs dans panneau de combat
- [ ] **PV modifiés** : PV changent sur cartes cibles (soins/dégâts)
- [ ] **Stats modifiées** : DEF/ATT/MAG changent si applicable
- [ ] **Effets visuels** : Cartes se rafraîchissent après action
- [ ] **Limitation respectée** : Capacité 1/combat non réutilisable
- [ ] **Reset correct** : Buffs temporaires disparaissent au tour suivant
- [ ] **Ciblage correct** : Ne cible pas qui elle ne devrait pas

### Scénarios de test recommandés

#### Capacités de soins
1. ✅ Blesser un allié (laisser l'ennemi attaquer)
2. 🔮 Utiliser capacité de soin
3. 🔍 Vérifier : PV augmentent, plafonnés au max

#### Capacités de dégâts
1. 🔮 Utiliser capacité offensive
2. 🔍 Vérifier : PV ennemis diminuent, parade prise en compte

#### Capacités de buff
1. 🔮 Utiliser capacité de buff (Parade, Armure du Mage)
2. 🔍 Vérifier : Stat visible sur carte (DEF augmente)
3. ⏭️ Passer au tour suivant
4. 🔍 Vérifier : Buff disparu (si temporaire 1 tour)

---

## ✅ CHECKLIST AVANT COMMIT

Avant de commiter une nouvelle capacité :

### Code
- [ ] `@register_ability` présent
- [ ] `__init__.py` mis à jour avec imports
- [ ] `hero_code` et `ability_number` corrects
- [ ] `spell_cost` conforme à Sorts.xlsx
- [ ] `uses_per_combat` défini si limité
- [ ] `execute()` utilise APIs BaseAbility (pas de logs simulés)
- [ ] `get_targets()` filtre correctement les cibles
- [ ] Gestion d'erreurs (`try/except`)
- [ ] Logs descriptifs avec émojis

### Tests
- [ ] Testé en mode manuel (SandboxV2)
- [ ] PV/stats modifiés visuellement vérifiés
- [ ] Limitation 1/combat testée
- [ ] Reset au tour suivant testé
- [ ] Pas d'erreurs console Streamlit

### Documentation
- [ ] Description conforme aux règles officielles
- [ ] Commentaires explicatifs dans le code
- [ ] Message de commit descriptif

---

## 📚 RESSOURCES COMPLÉMENTAIRES

### Fichiers de référence
- `tour de combat.md` - Règles officielles Périples V3.0
- `CLAUDE.md` - Règles architecturales du projet
- `documentation architecture périples.md` - APIs détaillées
- `Regle absolue verification architecture.md` - Zéro duplication

### Capacités déjà implémentées (exemples)

| Héros | Capacités fonctionnelles | Fichier |
|-------|-------------------------|---------|
| Atucan (P-3) | Imposition des mains, Parade | `atucan.py` |
| Elneha (P-1) | Formes (ours/loup), Soins | `elneha.py` |
| Kraor (P-4) | Piège, Poison | `kraor.py` |
| Liarie (P-5) | Éclairs, Armure du Mage | `liarie.py` |

**Consulter ces fichiers** pour des exemples concrets de patterns.

---

## 🚨 RÈGLES CRITIQUES

### ❌ NE JAMAIS
1. Dupliquer la logique métier existante
2. Créer de nouveaux managers/engines
3. Modifier `AbilityEffectsManager` sans raison majeure
4. Utiliser des logs au lieu d'APIs réelles
5. Coder sans lire `CLAUDE.md` d'abord

### ✅ TOUJOURS
1. Réutiliser l'architecture via adapters
2. Utiliser les APIs BaseAbility
3. Tester visuellement dans SandboxV2
4. Documenter les nouveaux buffs temporaires
5. Demander validation si doute

---

**Dernière mise à jour** : 18 novembre 2025
**Auteur session** : Claude Code (session 01AJXmy5vq4du2vGgvEJd5Yq)
**Bugs corrigés cette session** : 7 (affichage cartes, soins plafonnés, détection bouclier, parade infinie, bonus invisibles, ciblage incorrect, UI feedback)
