"""
Gestionnaire principal des effets de capacités
Orchestrateur central qui délègue aux modules spécialisés
"""

from typing import List, Dict, Any
from .persistent_effects import PersistentEffectsSystem
from .generic_effects import GenericEffectsHandler
from .hero_specific import HeroSpecificEffects

class AbilityEffectsManager:
    """
    Orchestrateur principal pour tous les effets de capacités
    Délègue aux modules spécialisés selon le type d'effet
    """
    
    def __init__(self, spell_manager):
        self.spell_manager = spell_manager
        
        # Modules spécialisés
        self.persistent_system = PersistentEffectsSystem()
        self.generic_handler = GenericEffectsHandler(spell_manager)
        self.hero_specific = HeroSpecificEffects(spell_manager)
    
    def apply_ability_effects(self, hero, ability, log: List[str]) -> bool:
        """
        Point d'entrée principal pour appliquer les effets d'une capacité
        
        Args:
            hero: Héros utilisant la capacité
            ability: Capacité à appliquer
            log: Journal de combat
            
        Returns:
            bool: True si des effets ont été appliqués
        """
        if not ability or not hasattr(ability, 'description'):
            return False
        
        effects_applied = False
        
        # 1. Vérifier si c'est une capacité spécifique à un héros
        if self._is_hero_specific_ability(hero, ability):
            if self.hero_specific.apply_specific_ability(hero, ability, log):
                effects_applied = True
        
        # 2. Appliquer les effets génériques
        if self.generic_handler.apply_generic_effects(hero, ability, log):
            effects_applied = True
        
        # 3. Gérer les effets persistants (activation)
        if self._activates_persistent_effect(ability):
            if self.persistent_system.activate_persistent_effect(hero, ability, log):
                effects_applied = True
        
        return effects_applied
    
    def _is_hero_specific_ability(self, hero, ability) -> bool:
        """Détermine si une capacité nécessite un traitement spécifique"""
        hero_code = hero.code
        ability_name = ability.name.lower()
        
        # Capacités spécifiques identifiées
        specific_abilities = {
            'P-1': ['forme d\'ours', 'forme de loup'],  # Elneha transformations
            'P-2': ['armure du mage'],  # Liarie persistant
            'P-4': ['cueilleur / chasseur', 'marque du chasseur', 'ambidextre'],  # Kraor mécaniques uniques
            'P-5': ['rage de berserker', 'charge de taureau', 'témérité', 'rage insatiable'],  # Thordius buffs complexes
            'P-6': ['mot de mort'],  # Stephe effet spécial
            'P-7': ['attaque furtive', 'vol à la tire', 'bombe fumigène'],  # Lame mécaniques spéciales
            'P-8': ['point faible', 'zui quan']  # Raishi effets cumulatifs
        }
        
        hero_specifics = specific_abilities.get(hero_code, [])
        return any(specific in ability_name for specific in hero_specifics)
    
    def _activates_persistent_effect(self, ability) -> bool:
        """Détermine si une capacité active un effet persistant"""
        description = ability.description.lower()
        name = ability.name.lower()
        
        # Mots-clés indiquant un effet persistant
        persistent_keywords = [
            'par tour', 'tant que', 'jusqu\'à', 'à chaque tour',
            'de façon cumulative', 'reste actif', 'armure du mage',
            'rage de berserker', 'rage insatiable', 'témérité'
        ]
        
        return any(keyword in description or keyword in name for keyword in persistent_keywords)
    
    def apply_turn_start_effects(self, hero, log: List[str]):
        """Applique les effets de début de tour (effets persistants)"""
        self.persistent_system.apply_turn_start_effects(hero, log)
    
    def apply_turn_end_effects(self, hero, log: List[str]):
        """Applique les effets de fin de tour"""
        self.persistent_system.apply_turn_end_effects(hero, log)
    
    def remove_expired_effects(self, hero, log: List[str]):
        """Supprime les effets expirés"""
        self.persistent_system.remove_expired_effects(hero, log)
    
    def get_effect_preview(self, ability) -> str:
        """Génère un aperçu des effets d'une capacité pour l'interface"""
        if not ability or not hasattr(ability, 'description'):
            return "Effet inconnu"
        
        # Déléguer aux modules spécialisés
        preview_parts = []
        
        # Effets génériques
        generic_preview = self.generic_handler.get_generic_preview(ability)
        if generic_preview:
            preview_parts.append(generic_preview)
        
        # Effets spécifiques
        specific_preview = self.hero_specific.get_specific_preview(ability)
        if specific_preview:
            preview_parts.append(specific_preview)
        
        # Effets persistants
        persistent_preview = self.persistent_system.get_persistent_preview(ability)
        if persistent_preview:
            preview_parts.append(persistent_preview)
        
        return " | ".join(preview_parts) if preview_parts else "Effet spécial"
    
    def get_active_effects_summary(self, hero) -> Dict[str, Any]:
        """Retourne un résumé des effets actifs sur un héros"""
        return {
            'persistent_effects': self.persistent_system.get_active_effects(hero),
            'temporary_buffs': getattr(hero, 'temporary_buffs', {}),
            'has_active_effects': self.persistent_system.has_active_effects(hero)
        }