"""
Système d'effets persistants pour les capacités
Gère les effets qui durent plusieurs tours (buffs, debuffs, transformations)
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class EffectTrigger(Enum):
    """Moments de déclenchement des effets"""
    TURN_START = "turn_start"
    TURN_END = "turn_end"
    ATTACK = "attack"
    DAMAGE_TAKEN = "damage_taken"
    PARADE_REFRESH = "parade_refresh"

class EffectDuration(Enum):
    """Types de durée des effets"""
    PERMANENT = "permanent"  # Jusqu'à la fin du combat
    TURNS = "turns"         # Nombre de tours limité
    CONDITIONAL = "conditional"  # Jusqu'à condition remplie

@dataclass
class PersistentEffect:
    """Définition d'un effet persistant"""
    name: str
    effect_type: str  # 'buff', 'debuff', 'transformation', 'special'
    trigger: EffectTrigger
    duration: EffectDuration
    remaining_turns: Optional[int] = None
    stacks: int = 1  # Pour effets cumulatifs
    max_stacks: int = 10
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class PersistentEffectsSystem:
    """Gestionnaire centralisé des effets persistants"""
    
    def __init__(self):
        self.effect_definitions = self._initialize_effect_definitions()
    
    def _initialize_effect_definitions(self) -> Dict[str, Dict]:
        """Définit tous les effets persistants possibles"""
        return {
            # Liarie P-2
            'armure_mage': {
                'type': 'buff',
                'trigger': EffectTrigger.PARADE_REFRESH,
                'duration': EffectDuration.PERMANENT,
                'description': 'Gagne +1 jeton parade par tour'
            },
            
            # Thordius P-5
            'rage_berserker': {
                'type': 'buff_debuff',
                'trigger': EffectTrigger.TURN_START,
                'duration': EffectDuration.CONDITIONAL,
                'description': '+2 dégâts, -1 PV par tour'
            },
            
            'rage_insatiable': {
                'type': 'buff_debuff', 
                'trigger': EffectTrigger.TURN_START,
                'duration': EffectDuration.CONDITIONAL,
                'description': '+3 dégâts, -1 PV par tour'
            },
            
            'temerite': {
                'type': 'buff_debuff',
                'trigger': EffectTrigger.TURN_START,
                'duration': EffectDuration.PERMANENT,
                'description': 'Ennemis attaquent en priorité, +2 dégâts'
            },
            
            'charge_taureau': {
                'type': 'buff',
                'trigger': EffectTrigger.ATTACK,
                'duration': EffectDuration.TURNS,
                'description': 'Prochaine attaque doublée + parade ce tour'
            },
            
            # Raishi P-8
            'zui_quan': {
                'type': 'buff',
                'trigger': EffectTrigger.TURN_START,
                'duration': EffectDuration.PERMANENT,
                'description': '+1 dégât et +1 parade cumulatifs'
            },
            
            # Stephe P-6
            'inspiration': {
                'type': 'buff',
                'trigger': EffectTrigger.ATTACK,
                'duration': EffectDuration.TURNS,
                'description': 'Peut attaquer deux fois ce tour'
            },
            
            'invisibilite': {
                'type': 'protection',
                'trigger': EffectTrigger.DAMAGE_TAKEN,
                'duration': EffectDuration.TURNS,
                'description': 'Intouchable jusqu\'au prochain tour'
            }
        }
    
    def activate_persistent_effect(self, hero, ability, log: List[str]) -> bool:
        """Active un effet persistant selon la capacité utilisée"""
        effect_name = self._identify_persistent_effect(ability)
        if not effect_name:
            return False
        
        # Vérifier si l'effet existe déjà
        if self._has_active_effect(hero, effect_name):
            return self._handle_duplicate_effect(hero, effect_name, log)
        
        # Créer et ajouter l'effet
        effect = self._create_effect(effect_name, ability)
        if effect:
            self._add_effect_to_hero(hero, effect)
            combatant_name = getattr(hero, 'display_name', hero.name)
            effect_def = self.effect_definitions[effect_name]
            log.append(f"  🔮 {combatant_name} active {effect_def['description']}")
            return True
        
        return False
    
    def apply_turn_start_effects(self, hero, log: List[str]):
        """Applique tous les effets de début de tour"""
        if not hasattr(hero, 'active_persistent_effects'):
            return
        
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        for effect in hero.active_persistent_effects[:]:  # Copie pour éviter modification pendant itération
            if effect.trigger == EffectTrigger.TURN_START:
                self._apply_specific_effect(hero, effect, log, combatant_name)
                
                # Gérer la durée
                if effect.duration == EffectDuration.TURNS:
                    effect.remaining_turns -= 1
                    if effect.remaining_turns <= 0:
                        self._remove_effect(hero, effect, log, combatant_name)
    
    def apply_parade_refresh_effects(self, hero):
        """Applique les effets lors de la recharge de parade"""
        if not hasattr(hero, 'active_persistent_effects'):
            return
        
        for effect in hero.active_persistent_effects:
            if effect.trigger == EffectTrigger.PARADE_REFRESH:
                self._apply_parade_effect(hero, effect)
    
    def apply_turn_end_effects(self, hero, log: List[str]):
        """Applique tous les effets de fin de tour"""
        if not hasattr(hero, 'active_persistent_effects'):
            return
        
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        for effect in hero.active_persistent_effects:
            if effect.trigger == EffectTrigger.TURN_END:
                self._apply_specific_effect(hero, effect, log, combatant_name)
    
    def remove_expired_effects(self, hero, log: List[str]):
        """Supprime les effets expirés"""
        if not hasattr(hero, 'active_persistent_effects'):
            return
        
        combatant_name = getattr(hero, 'display_name', hero.name)
        expired_effects = [e for e in hero.active_persistent_effects 
                          if e.duration == EffectDuration.TURNS and e.remaining_turns <= 0]
        
        for effect in expired_effects:
            self._remove_effect(hero, effect, log, combatant_name)
    
    def _identify_persistent_effect(self, ability) -> Optional[str]:
        """Identifie quel effet persistant correspond à une capacité"""
        name = ability.name.lower()
        description = ability.description.lower()
        
        # Mapping capacité → effet
        mappings = {
            'armure du mage': 'armure_mage',
            'rage de berserker': 'rage_berserker', 
            'rage insatiable': 'rage_insatiable',
            'témérité': 'temerite',
            'charge de taureau': 'charge_taureau',
            'zui quan': 'zui_quan',
            'inspiration': 'inspiration',
            'invisibilité': 'invisibilite'
        }
        
        for ability_name, effect_name in mappings.items():
            if ability_name in name:
                return effect_name
        
        return None
    
    def _create_effect(self, effect_name: str, ability) -> Optional[PersistentEffect]:
        """Crée un effet persistant"""
        if effect_name not in self.effect_definitions:
            return None
        
        definition = self.effect_definitions[effect_name]
        
        # Durée spécifique selon l'effet
        remaining_turns = None
        if definition['duration'] == EffectDuration.TURNS:
            if effect_name == 'charge_taureau':
                remaining_turns = 1  # Un tour seulement
            elif effect_name == 'inspiration':
                remaining_turns = 1  # Ce tour uniquement
            elif effect_name == 'invisibilite':
                remaining_turns = 1  # Jusqu'au prochain tour
        
        return PersistentEffect(
            name=effect_name,
            effect_type=definition['type'],
            trigger=definition['trigger'],
            duration=definition['duration'],
            remaining_turns=remaining_turns,
            metadata={'ability_name': ability.name}
        )
    
    def _add_effect_to_hero(self, hero, effect: PersistentEffect):
        """Ajoute un effet à un héros"""
        if not hasattr(hero, 'active_persistent_effects'):
            hero.active_persistent_effects = []
        
        hero.active_persistent_effects.append(effect)
    
    def _has_active_effect(self, hero, effect_name: str) -> bool:
        """Vérifie si un héros a déjà un effet actif"""
        if not hasattr(hero, 'active_persistent_effects'):
            return False
        
        return any(effect.name == effect_name for effect in hero.active_persistent_effects)
    
    def _handle_duplicate_effect(self, hero, effect_name: str, log: List[str]) -> bool:
        """Gère l'application d'un effet déjà actif"""
        # Effets cumulatifs
        if effect_name == 'zui_quan':
            for effect in hero.active_persistent_effects:
                if effect.name == effect_name and effect.stacks < effect.max_stacks:
                    effect.stacks += 1
                    combatant_name = getattr(hero, 'display_name', hero.name)
                    log.append(f"  📈 {combatant_name} - Zui quan niveau {effect.stacks}")
                    return True
        
        # Effets non-cumulatifs (renouveler la durée)
        elif effect_name in ['inspiration', 'invisibilite']:
            for effect in hero.active_persistent_effects:
                if effect.name == effect_name:
                    effect.remaining_turns = 1  # Renouveler
                    return True
        
        return False
    
    def _apply_specific_effect(self, hero, effect: PersistentEffect, log: List[str], combatant_name: str):
        """Applique un effet spécifique"""
        if effect.name == 'rage_berserker':
            # +2 dégâts déjà géré dans get_total_damage(), appliquer malus
            damage_result = hero.apply_damage_with_parade(1)
            log.append(f"  🩸 {combatant_name} - Rage de berserker: {damage_result['health_damage']} dégât")
            
        elif effect.name == 'rage_insatiable':
            # +3 dégâts déjà géré, appliquer malus
            damage_result = hero.apply_damage_with_parade(1)
            log.append(f"  🩸 {combatant_name} - Rage insatiable: {damage_result['health_damage']} dégât")
            
        elif effect.name == 'zui_quan':
            # Effet cumulatif géré dans get_total_damage() et get_total_parade()
            log.append(f"  🥋 {combatant_name} - Zui quan actif (niveau {effect.stacks})")
    
    def _apply_parade_effect(self, hero, effect: PersistentEffect):
        """Applique les effets liés à la parade"""
        if effect.name == 'armure_mage':
            # +1 jeton parade supplémentaire
            hero.current_parade_tokens += 1
    
    def _remove_effect(self, hero, effect: PersistentEffect, log: List[str], combatant_name: str):
        """Supprime un effet d'un héros"""
        if effect in hero.active_persistent_effects:
            hero.active_persistent_effects.remove(effect)
            effect_def = self.effect_definitions[effect.name]
            log.append(f"  ⏰ {combatant_name} - {effect_def['description']} terminé")
    
    def get_active_effects(self, hero) -> List[Dict[str, Any]]:
        """Retourne la liste des effets actifs sur un héros"""
        if not hasattr(hero, 'active_persistent_effects'):
            return []
        
        return [
            {
                'name': effect.name,
                'type': effect.effect_type,
                'description': self.effect_definitions[effect.name]['description'],
                'duration': effect.duration.value,
                'remaining_turns': effect.remaining_turns,
                'stacks': effect.stacks if effect.stacks > 1 else None
            }
            for effect in hero.active_persistent_effects
        ]
    
    def has_active_effects(self, hero) -> bool:
        """Vérifie si un héros a des effets actifs"""
        return hasattr(hero, 'active_persistent_effects') and len(hero.active_persistent_effects) > 0
    
    def get_persistent_preview(self, ability) -> Optional[str]:
        """Génère un aperçu pour un effet persistant"""
        effect_name = self._identify_persistent_effect(ability)
        if effect_name and effect_name in self.effect_definitions:
            definition = self.effect_definitions[effect_name]
            return f"🔮 {definition['description']}"
        return None
    
    def get_damage_bonus(self, hero) -> int:
        """Calcule le bonus de dégâts total des effets persistants"""
        if not hasattr(hero, 'active_persistent_effects'):
            return 0
        
        bonus = 0
        for effect in hero.active_persistent_effects:
            if effect.name == 'rage_berserker':
                bonus += 2
            elif effect.name == 'rage_insatiable':
                bonus += 3
            elif effect.name == 'temerite':
                bonus += 2
            elif effect.name == 'zui_quan':
                bonus += effect.stacks
        
        return bonus
    
    def get_parade_bonus(self, hero) -> int:
        """Calcule le bonus de parade total des effets persistants"""
        if not hasattr(hero, 'active_persistent_effects'):
            return 0
        
        bonus = 0
        for effect in hero.active_persistent_effects:
            if effect.name == 'zui_quan':
                bonus += effect.stacks
        
        return bonus