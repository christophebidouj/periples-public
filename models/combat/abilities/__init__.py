"""
Module abilities - Système de gestion des effets de capacités
Architecture modulaire pour le moteur de combat Périples
"""

from .ability_manager import AbilityEffectsManager
from .persistent_effects import PersistentEffectsSystem
from .generic_effects import GenericEffectsHandler
from .hero_specific import HeroSpecificEffects
from .character_integration import CharacterAbilitiesIntegration

# Point d'entrée principal
__all__ = [
    'AbilityEffectsManager',
    'PersistentEffectsSystem', 
    'GenericEffectsHandler',
    'HeroSpecificEffects',
    'CharacterAbilitiesIntegration'
]

# Version pour compatibilité
__version__ = "1.0.0"