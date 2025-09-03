"""
Module abilities - Système de gestion des effets de capacités
Architecture modulaire pour le moteur de combat Périples
"""

from .ability_manager import AbilityEffectsManager
from .persistent_effects import PersistentEffectsSystem
from .character_integration import CharacterAbilitiesIntegration

# Point d'entrée principal
__all__ = [
    'AbilityEffectsManager',
    'PersistentEffectsSystem',
    'CharacterAbilitiesIntegration'
]

# Version pour compatibilité
__version__ = "1.0.0"