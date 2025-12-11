"""
Système de capacités pour les ennemis - Périples Balance Workshop
Capacités spéciales des ennemis (immunités, attaques multiples, effets de contrôle, etc.)
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class EnemyAbilityTrigger(Enum):
    """Moments d'activation des capacités ennemis"""
    ON_COMBAT_START = "on_combat_start"      # Début du combat (flags permanents)
    ON_ROUND_START = "on_round_start"        # Début de chaque round (avant tous les tours)
    ON_TURN_START = "on_turn_start"          # Début du tour de l'ennemi
    BEFORE_ATTACK = "before_attack"          # Avant d'attaquer
    AFTER_ATTACK = "after_attack"            # Après avoir attaqué
    ON_RECEIVE_DAMAGE = "on_receive_damage"  # Quand l'ennemi reçoit des dégâts


class EnemyAbilityEffect(Enum):
    """Types d'effets de capacités ennemis"""
    # Niveau 1 - Flags permanents
    IMMUNITY_STUN = "immunity_stun"                  # Ne peut pas être Stun
    BLOCK_HERO_ABILITIES = "block_hero_abilities"    # Bloque toutes capacités héros

    # Niveau 2 - Attaques multiples
    EXTRA_ATTACKS = "extra_attacks"                  # Attaques supplémentaires

    # Niveau 3 - Effets récurrents
    STUN_HERO_PERMANENT = "stun_hero_permanent"      # Stun jusqu'à fin combat
    STUN_HERO_TEMPORARY = "stun_hero_temporary"      # Stun pour N tours

    # Niveau 4 - Effets alternants
    ALTERNATING_EFFECTS = "alternating_effects"      # Effets pairs/impairs
    DAMAGE_ALL_HEROES = "damage_all_heroes"          # Dégâts AoE magiques

    # Niveau 5 - Effets périodiques
    PERIODIC_STUN = "periodic_stun"                  # Stun tous les N tours
    PERIODIC_DAMAGE = "periodic_damage"              # Dégâts tous les N tours

    # Niveau 6 - Conditions spéciales
    ABILITY_CHECK_STUN = "ability_check_stun"        # Check D20 + capacité
    # Note: RANGED_ONLY_THRESHOLD (EA-12) non implémenté - attaques à distance non gérées


class EnemyAbility(BaseModel):
    """Capacité d'ennemi avec système de triggers et effects"""

    # Identifiants
    code: str                    # EA-X
    name: str                    # Nom court
    description: str             # Description complète

    # Mécaniques
    triggers: List[str] = Field(default_factory=list)  # Quand s'active
    effects: List[str] = Field(default_factory=list)   # Que fait-elle
    parameters: Dict[str, Any] = Field(default_factory=dict)  # Configuration

    # État runtime (géré par le manager)
    turn_counter: int = 0
    active: bool = True

    class Config:
        use_enum_values = True

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def has_trigger(self, trigger: str) -> bool:
        """Vérifie si la capacité a un trigger spécifique"""
        return trigger in self.triggers

    def has_effect(self, effect: str) -> bool:
        """Vérifie si la capacité a un effect spécifique"""
        return effect in self.effects

    def get_parameter(self, key: str, default=None):
        """Récupère un paramètre avec valeur par défaut"""
        return self.parameters.get(key, default)

    def increment_turn(self):
        """Incrémente le compteur de tours"""
        self.turn_counter += 1

    def reset_counter(self):
        """Reset le compteur de tours"""
        self.turn_counter = 0
