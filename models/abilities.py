"""
Modèles de données pour le système de capacités du Simulateur Périples
Version simplifiée - Focus combat uniquement
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from enum import Enum

class AbilityType(Enum):
    """Types de capacités selon les règles Périples (p.24)"""
    PHYSICAL = "physical"      # Coût: 0 - Permet attaque après
    MAGICAL = "magical"        # Coût: 1+ - Empêche attaque ce tour

class TargetType(Enum):
    """Types de ciblage des capacités"""
    SELF = "self"
    ALLY = "ally"
    ENEMY = "enemy"
    ALL_ALLIES = "all_allies"
    ALL_ENEMIES = "all_enemies"
    ANY = "any"

class AbilityEffect(BaseModel):
    """Effet d'une capacité"""
    type: str = Field(..., description="Type: heal, damage, buff, debuff, special")
    value: Optional[int] = None
    description: str

class Ability(BaseModel):
    """Capacité de personnage pour combat"""
    
    # Identifiants
    hero_code: str
    ability_number: int = Field(..., ge=1, le=7)
    name: str
    
    # Coût et limitations
    spell_cost: int = Field(0, ge=0)
    uses_per_combat: Optional[int] = None
    
    # Mécaniques
    description: str
    effects: List[AbilityEffect] = Field(default_factory=list)
    target_type: TargetType = TargetType.SELF
    
    # État runtime
    uses_remaining_combat: Optional[int] = None
    is_unlocked: bool = False
    
    @property
    def ability_type(self) -> AbilityType:
        """Type selon coût (règle p.24)"""
        return AbilityType.PHYSICAL if self.spell_cost == 0 else AbilityType.MAGICAL
    
    @property
    def unique_id(self) -> str:
        return f"{self.hero_code}_ability_{self.ability_number}"
    
    @property
    def prevents_attack(self) -> bool:
        """Capacités magiques empêchent l'attaque (règle p.24)"""
        return self.ability_type == AbilityType.MAGICAL
    
    def can_use(self, current_spells: Optional[int]) -> tuple[bool, str]:
        """Vérifie si utilisable"""
        if not self.is_unlocked:
            return False, "Capacité non débloquée"
        
        current_spells = current_spells or 0
        if self.spell_cost > current_spells:
            return False, f"Sorts insuffisants ({self.spell_cost} requis, {current_spells} disponibles)"
        
        if self.uses_remaining_combat is not None and self.uses_remaining_combat <= 0:
            return False, "Plus d'utilisations ce combat"
        
        return True, "Utilisable"
    
    def use_ability(self) -> bool:
        """Consomme une utilisation"""
        if self.uses_remaining_combat is not None and self.uses_remaining_combat <= 0:
            return False
        
        if self.uses_remaining_combat is not None:
            self.uses_remaining_combat = max(0, self.uses_remaining_combat - 1)
        
        return True
    
    def reset_combat_uses(self):
        """Reset utilisations pour nouveau combat"""
        if self.uses_per_combat is not None:
            self.uses_remaining_combat = self.uses_per_combat

class AbilityAction(BaseModel):
    """Action d'utilisation d'une capacité en combat"""
    
    ability_id: str
    ability_name: str
    user_name: str
    
    # Résultats
    success: bool = False
    spell_cost_paid: int = 0
    effects_applied: List[str] = Field(default_factory=list)
    
    # Métriques
    damage_dealt: int = 0
    healing_done: int = 0
    targets_affected: List[str] = Field(default_factory=list)
    
    # Contexte
    turn_number: Optional[int] = None
    prevents_attack: bool = False
    failure_reason: str = ""
    
    def add_effect(self, effect_description: str):
        self.effects_applied.append(effect_description)
    
    def add_target(self, target_name: str):
        if target_name not in self.targets_affected:
            self.targets_affected.append(target_name)
    
    def get_summary(self) -> str:
        """Résumé pour journal de combat"""
        summary = f"{self.user_name} utilise {self.ability_name}"
        
        if self.spell_cost_paid > 0:
            summary += f" (coût: {self.spell_cost_paid} sorts)"
        
        if not self.success:
            summary += f" → ÉCHEC: {self.failure_reason}"
            return summary
        
        effects = []
        if self.damage_dealt > 0:
            effects.append(f"{self.damage_dealt} dégâts")
        if self.healing_done > 0:
            effects.append(f"{self.healing_done} soins")
        
        if effects:
            summary += f" → {', '.join(effects)}"
        
        if self.prevents_attack:
            summary += " (pas d'attaque ce tour)"
        
        return summary

class AbilityManager:
    """Gestionnaire des capacités pour un personnage"""
    
    def __init__(self, abilities: List[Ability]):
        self.abilities = {ability.ability_number: ability for ability in abilities}
    
    def get_ability(self, number: int) -> Optional[Ability]:
        return self.abilities.get(number)
    
    def get_unlocked_abilities(self) -> List[Ability]:
        return [ability for ability in self.abilities.values() if ability.is_unlocked]
    
    def get_available_abilities(self, current_spells: int) -> List[Ability]:
        """Capacités utilisables avec les sorts actuels"""
        available = []
        for ability in self.get_unlocked_abilities():
            can_use, _ = ability.can_use(current_spells)
            if can_use:
                available.append(ability)
        return available
    
    def unlock_ability(self, number: int) -> bool:
        """Débloque une capacité"""
        ability = self.get_ability(number)
        if ability and not ability.is_unlocked:
            ability.is_unlocked = True
            ability.reset_combat_uses()
            return True
        return False
    
    def reset_combat_uses(self):
        """Reset toutes les utilisations par combat"""
        for ability in self.abilities.values():
            ability.reset_combat_uses()
    
    def get_stats_summary(self) -> Dict[str, int]:
        """Résumé statistique"""
        total = len(self.abilities)
        unlocked = len(self.get_unlocked_abilities())
        
        return {
            'total_abilities': total,
            'unlocked_abilities': unlocked,
            'locked_abilities': total - unlocked
        }