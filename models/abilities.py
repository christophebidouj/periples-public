"""
Modèles de données pour le système de capacités du Simulateur Périples
Conforme aux règles officielles du jeu de société "Périples"
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .character import Character

class AbilityType(Enum):
    """Types de capacités selon les règles Périples (p.24)"""
    PHYSICAL = "physical"      # Coût: 0 - Permet attaque après
    MAGICAL = "magical"        # Coût: 1+ - Empêche attaque ce tour
    PASSIVE = "passive"        # Toujours active (future extension)

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
    type: str = Field(..., description="Type d'effet: heal, damage, buff, debuff, special")
    value: Optional[int] = Field(None, description="Valeur numérique de l'effet")
    duration: Optional[int] = Field(None, description="Durée en tours")
    target_stat: Optional[str] = Field(None, description="Statistique ciblée")
    description: str = Field(..., description="Description de l'effet")

class Ability(BaseModel):
    """
    Modèle d'une capacité de personnage selon les règles Périples
    
    Règles importantes :
    - Capacités magiques (coût > 0) empêchent l'attaque ce tour (p.24)
    - Une seule capacité par tour maximum
    - Récupération des sorts au repos
    """
    
    # === IDENTIFIANTS ===
    hero_code: str = Field(..., description="Code du héros (P-1, P-2, etc.)")
    ability_number: int = Field(..., ge=1, le=6, description="Numéro capacité (1-6)")
    name: str = Field(..., description="Nom de la capacité")
    
    # === COÛTS ET LIMITATIONS ===
    spell_cost: int = Field(0, ge=0, description="Coût en points de sorts")
    uses_per_combat: Optional[int] = Field(None, ge=1, description="Utilisations par combat")
    uses_per_day: Optional[int] = Field(None, ge=1, description="Utilisations par jour")
    
    # === MÉCANIQUES ===
    description: str = Field(..., description="Description complète de la capacité")
    effects: List[AbilityEffect] = Field(default_factory=list, description="Effets de la capacité")
    target_type: TargetType = Field(TargetType.SELF, description="Type de ciblage")
    
    # === ÉTAT D'USAGE (RUNTIME) ===
    uses_remaining_combat: Optional[int] = Field(None, description="Utilisations restantes ce combat")
    uses_remaining_day: Optional[int] = Field(None, description="Utilisations restantes aujourd'hui")
    is_unlocked: bool = Field(False, description="Capacité débloquée")
    
    @property
    def ability_type(self) -> AbilityType:
        """
        Détermine le type de capacité selon le coût en sorts
        Règle p.24 : capacités magiques = coût > 0
        """
        if self.spell_cost == 0:
            return AbilityType.PHYSICAL
        return AbilityType.MAGICAL
    
    @property
    def unique_id(self) -> str:
        """Identifiant unique de la capacité"""
        return f"{self.hero_code}_ability_{self.ability_number}"
    
    @property
    def prevents_attack(self) -> bool:
        """
        Vérifie si cette capacité empêche l'attaque ce tour
        Règle p.24 : "Les capacités magiques ne permettent pas de réaliser une attaque physique en plus"
        """
        return self.ability_type == AbilityType.MAGICAL
    
    def can_use(self, current_spells: Optional[int]) -> tuple[bool, str]:
        """
        Vérifie si la capacité peut être utilisée
        
        Args:
            current_spells: Points de sorts actuels du personnage (peut être None)
            
        Returns:
            tuple[bool, str]: (peut_utiliser, raison)
        """
        if not self.is_unlocked:
            return False, "Capacité non débloquée"
        
        # CORRECTION: Gérer le cas où current_spells est None
        if current_spells is None:
            current_spells = 0
        
        if self.spell_cost > current_spells:
            return False, f"Sorts insuffisants ({self.spell_cost} requis, {current_spells} disponibles)"
        
        if self.uses_remaining_combat is not None and self.uses_remaining_combat <= 0:
            return False, "Plus d'utilisations ce combat"
        
        if self.uses_remaining_day is not None and self.uses_remaining_day <= 0:
            return False, "Plus d'utilisations aujourd'hui"
        
        return True, "Utilisable"
    
    def use_ability(self) -> bool:
        """
        Consomme une utilisation de la capacité
        
        Returns:
            bool: True si l'utilisation a été consommée avec succès
        """
        # Vérifier les limitations avant de consommer
        if self.uses_remaining_combat is not None and self.uses_remaining_combat <= 0:
            return False
        
        if self.uses_remaining_day is not None and self.uses_remaining_day <= 0:
            return False
        
        # Consommer les utilisations
        if self.uses_remaining_combat is not None:
            self.uses_remaining_combat = max(0, self.uses_remaining_combat - 1)
        
        if self.uses_remaining_day is not None:
            self.uses_remaining_day = max(0, self.uses_remaining_day - 1)
        
        return True
    
    def reset_combat_uses(self):
        """Remet les utilisations par combat au maximum"""
        if self.uses_per_combat is not None:
            self.uses_remaining_combat = self.uses_per_combat
    
    def reset_daily_uses(self):
        """Remet les utilisations quotidiennes au maximum"""
        if self.uses_per_day is not None:
            self.uses_remaining_day = self.uses_per_day
    
    def get_display_info(self) -> Dict[str, str]:
        """Retourne les informations d'affichage de la capacité"""
        info = {
            'name': self.name,
            'type': "🔮 Magique" if self.ability_type == AbilityType.MAGICAL else "⚔️ Physique",
            'cost': f"{self.spell_cost} sorts" if self.spell_cost > 0 else "Gratuit",
            'description': self.description
        }
        
        # Limitations
        limitations = []
        if self.uses_per_combat:
            remaining = self.uses_remaining_combat or self.uses_per_combat
            limitations.append(f"{remaining}/{self.uses_per_combat} par combat")
        
        if self.uses_per_day:
            remaining = self.uses_remaining_day or self.uses_per_day
            limitations.append(f"{remaining}/{self.uses_per_day} par jour")
        
        if limitations:
            info['limitations'] = " • ".join(limitations)
        
        return info

class AbilityAction(BaseModel):
    """
    Action d'utilisation d'une capacité en combat
    Utilisé pour tracker les effets et résultats
    """
    ability_id: str = Field(..., description="ID unique de la capacité utilisée")
    ability_name: str = Field(..., description="Nom de la capacité")
    user_name: str = Field(..., description="Nom de l'utilisateur")
    
    # Résultats de l'action
    success: bool = Field(False, description="Action réussie")
    spell_cost_paid: int = Field(0, description="Coût en sorts payé")
    effects_applied: List[str] = Field(default_factory=list, description="Effets appliqués")
    
    # Métriques d'impact
    damage_dealt: int = Field(0, description="Dégâts infligés")
    healing_done: int = Field(0, description="Soins effectués")
    targets_affected: List[str] = Field(default_factory=list, description="Cibles affectées")
    
    # Contexte
    turn_number: Optional[int] = Field(None, description="Numéro du tour")
    prevents_attack: bool = Field(False, description="Empêche l'attaque ce tour")
    
    def add_effect(self, effect_description: str):
        """Ajoute un effet appliqué à l'action"""
        self.effects_applied.append(effect_description)
    
    def add_target(self, target_name: str):
        """Ajoute une cible affectée"""
        if target_name not in self.targets_affected:
            self.targets_affected.append(target_name)
    
    def get_summary(self) -> str:
        """Retourne un résumé de l'action pour le journal de combat"""
        summary = f"{self.user_name} utilise {self.ability_name}"
        
        if self.spell_cost_paid > 0:
            summary += f" (coût: {self.spell_cost_paid} sorts)"
        
        if not self.success:
            summary += " → ÉCHEC"
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

# Utilitaires pour l'intégration
class AbilityManager:
    """Gestionnaire des capacités pour un personnage"""
    
    def __init__(self, abilities: List[Ability]):
        self.abilities = {ability.ability_number: ability for ability in abilities}
    
    def get_ability(self, number: int) -> Optional[Ability]:
        """Récupère une capacité par son numéro"""
        return self.abilities.get(number)
    
    def get_unlocked_abilities(self) -> List[Ability]:
        """Retourne les capacités débloquées"""
        return [ability for ability in self.abilities.values() if ability.is_unlocked]
    
    def get_available_abilities(self, current_spells: int) -> List[Ability]:
        """Retourne les capacités utilisables avec les sorts actuels"""
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
            ability.reset_daily_uses()
            return True
        return False
    
    def reset_combat_uses(self):
        """Remet toutes les utilisations par combat"""
        for ability in self.abilities.values():
            ability.reset_combat_uses()
    
    def reset_daily_uses(self):
        """Remet toutes les utilisations quotidiennes"""
        for ability in self.abilities.values():
            ability.reset_daily_uses()
    
    def get_stats_summary(self) -> Dict[str, int]:
        """Retourne un résumé statistique des capacités"""
        total = len(self.abilities)
        unlocked = len(self.get_unlocked_abilities())
        
        return {
            'total_abilities': total,
            'unlocked_abilities': unlocked,
            'locked_abilities': total - unlocked
        }