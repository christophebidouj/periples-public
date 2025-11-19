# individual_abilities_init
"""
Module des capacités individuelles
Architecture modulaire pour le système Périples Balance Workshop

Ce module remplace le système de parsing de texte par des classes dédiées
pour chacune des 48 capacités (8 héros × 6 capacités).
"""

from .base_ability import BaseAbility
from .ability_registry import ABILITY_REGISTRY, register_ability

# Import des capacités par héros (sera ajouté au fur et à mesure)
try:
    from .heroes import *  # Import des modules de héros
except ImportError:
    # Pas encore de modules de héros créés
    pass

# Points d'entrée principaux
__all__ = [
    'BaseAbility',
    'ABILITY_REGISTRY',
    'register_ability',
    'reset_all_combat_uses'
]

# Version du module
__version__ = "1.0.0"

def get_ability(hero_code: str, ability_number: int):
    """
    Point d'entrée simplifié pour récupérer une capacité
    
    Args:
        hero_code: Code du héros (P-1, P-2, etc.)
        ability_number: Numéro de capacité (1-6)
        
    Returns:
        Instance de BaseAbility ou None
    """
    return ABILITY_REGISTRY.get_ability_instance(hero_code, ability_number)

def get_hero_abilities(hero_code: str):
    """
    Point d'entrée simplifié pour récupérer toutes les capacités d'un héros
    
    Args:
        hero_code: Code du héros (P-1, P-2, etc.)
        
    Returns:
        Liste des instances de capacités
    """
    return ABILITY_REGISTRY.get_hero_abilities(hero_code)

def get_registry_stats():
    """
    Retourne les statistiques du registre

    Returns:
        Dict avec les stats (total, par héros, etc.)
    """
    return ABILITY_REGISTRY.get_debug_info()

def reset_all_combat_uses():
    """
    Réinitialise les compteurs uses_remaining_combat de toutes les capacités

    À appeler au début d'un nouveau combat pour réinitialiser les limitations
    d'utilisation (ex: Châtiment divin 1/combat, Mur de glace 2/combat, etc.)

    Cette fonction parcourt toutes les instances cachées dans le registre
    et remet uses_remaining_combat à uses_per_combat.
    """
    for ability_instance in ABILITY_REGISTRY._instances_cache.values():
        if hasattr(ability_instance, 'uses_per_combat') and hasattr(ability_instance, 'uses_remaining_combat'):
            if ability_instance.uses_per_combat is not None:
                ability_instance.uses_remaining_combat = ability_instance.uses_per_combat