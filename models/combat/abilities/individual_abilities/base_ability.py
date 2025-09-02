# base_ability
"""
Classe de base pour toutes les capacitÃ©s individuelles
Architecture modulaire pour le systÃ¨me PÃ©riples Balance Workshop
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import random

class BaseAbility(ABC):
    """Classe abstraite de base pour toutes les capacitÃ©s individuelles"""
    
    def __init__(self, hero_code: str, ability_number: int, name: str, description: str):
        """
        Initialise une capacitÃ© individuelle
        
        Args:
            hero_code: Code du hÃ©ros (P-1, P-2, etc.)
            ability_number: NumÃ©ro de capacitÃ© (1-6)
            name: Nom de la capacitÃ©
            description: Description textuelle
        """
        self.hero_code = hero_code
        self.ability_number = ability_number
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """
        ExÃ©cute la capacitÃ© avec ses effets mÃ©caniques rÃ©els
        
        Args:
            caster: Personnage qui lance la capacitÃ©
            targets: Liste des cibles (hÃ©ros/ennemis selon le type)
            context: Contexte du combat (spell_manager, rules, etc.)
            log: Liste pour ajouter les messages de log
            
        Returns:
            bool: True si la capacitÃ© a eu un effet mÃ©canique, False sinon
        """
        pass
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        spell_manager = context.get('spell_manager')
        if not spell_manager:
            return False
            
        # Vérifier les utilisations restantes (MANQUANT)
        if hasattr(self, 'uses_remaining_combat') and self.uses_remaining_combat is not None:
            if self.uses_remaining_combat <= 0:
                return False
        
        # Vérifier le coût en sorts
        if hasattr(self, 'spell_cost') and self.spell_cost > 0:
            return caster.current_spells >= self.spell_cost
            
        return True
    
    def get_preview(self) -> str:
        """
        Retourne un aperçu des effets de la capacité
        
        Returns:
            str: Description des effets mécaniques
        """
        return f"📋 {self.name}: Effet mécanique défini"
    
    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        """
        DÃ©termine les cibles valides pour cette capacitÃ©
        
        Args:
            caster: Personnage qui lance la capacitÃ©
            all_heroes: Liste de tous les hÃ©ros
            all_enemies: Liste de tous les ennemis
            context: Contexte du combat
            
        Returns:
            List: Liste des cibles appropriÃ©es
        """
        # Par dÃ©faut, retourne le lanceur (self-target)
        return [caster]
    
    def _apply_healing(self, target, amount: int, log: List[str]) -> int:
        """
        Utilitaire pour appliquer des soins
        
        Args:
            target: Cible Ã  soigner
            amount: Montant de soins
            log: Liste des logs
            
        Returns:
            int: Montant de soins réellement appliqués
        """
        if amount <= 0:
            return 0
        
        # Système de blessures (Périples) - blessures diminuent avec les soins
        if hasattr(target, 'current_wounds') and hasattr(target, 'health'):
            old_wounds = target.current_wounds
            target.current_wounds = max(0, target.current_wounds - amount)
            actual_healing = old_wounds - target.current_wounds
            
            if actual_healing > 0:
                log.append(f"💚 {target.name} guérit {actual_healing} blessure(s)")
            return actual_healing
        
        # Système de PV classique (fallback) - PV augmentent avec les soins
        elif hasattr(target, 'current_health') and hasattr(target, 'max_health'):
            old_health = target.current_health
            target.current_health = min(target.current_health + amount, target.max_health)
            actual_healing = target.current_health - old_health
            
            if actual_healing > 0:
                log.append(f"💚 {target.name} récupère {actual_healing} PV")
            return actual_healing
        
        # Système simple sans max_health
        elif hasattr(target, 'current_health'):
            old_health = target.current_health
            target.current_health = target.current_health + amount
            actual_healing = amount
            
            if actual_healing > 0:
                log.append(f"💚 {target.name} récupère {actual_healing} PV")
            return actual_healing
        
        return 0
    
    def _apply_damage(self, target, amount: int, damage_type: str, log: List[str]) -> int:
        """
        Utilitaire pour appliquer des dÃ©gÃ¢ts
        
        Args:
            target: Cible Ã  endommager
            amount: Montant de dÃ©gÃ¢ts
            damage_type: Type de dÃ©gÃ¢ts ("physical" ou "magical")
            log: Liste des logs
            
        Returns:
            int: Montant de dégâts réellement infligés
        """
        if amount <= 0:
            return 0
        
        # Système de blessures (Périples) - blessures augmentent avec les dégâts
        if hasattr(target, 'current_wounds') and hasattr(target, 'health'):
            old_wounds = target.current_wounds
            target.current_wounds = min(target.health, target.current_wounds + amount)
            actual_damage = target.current_wounds - old_wounds
            
            if actual_damage > 0:
                emoji = "⚡" if damage_type == "magical" else "💥"
                log.append(f"{emoji} {target.name} subit {actual_damage} blessure(s)")
            return actual_damage
        
        # Système de PV classique (fallback) - PV diminuent avec les dégâts
        elif hasattr(target, 'current_health'):
            old_health = target.current_health
            target.current_health = max(0, target.current_health - amount)
            actual_damage = old_health - target.current_health
            
            if actual_damage > 0:
                emoji = "⚡" if damage_type == "magical" else "💥"
                log.append(f"{emoji} {target.name} subit {actual_damage} dégâts")
            return actual_damage
                
        return 0
    
    def _apply_stat_modifier(self, target, stat: str, value: int, log: List[str]) -> bool:
        """
        Utilitaire pour modifier temporairement les stats
        
        Args:
            target: Cible à modifier
            stat: Nom de la stat ("attack", "defense", "precision")
            value: Valeur à ajouter (peut être négative)
            log: Liste des logs
            
        Returns:
            bool: True si la modification a été appliquée
        """
        stat_map = {
            "attack": "current_attack",
            "defense": "current_defense", 
            "precision": "current_precision"
        }
        
        current_attr = stat_map.get(stat)
        if not current_attr or not hasattr(target, current_attr):
            return False
            
        old_value = getattr(target, current_attr)
        new_value = max(0, old_value + value)  # Empêcher valeurs négatives
        setattr(target, current_attr, new_value)
        
        if value > 0:
            log.append(f"⬆️ {target.name} gagne +{value} {stat} ({old_value} → {new_value})")
        elif value < 0:
            log.append(f"⬇️ {target.name} perd {abs(value)} {stat} ({old_value} → {new_value})")
        
        return True
    
    def _consume_spell_cost(self, caster, cost: int, spell_manager, log: List[str]) -> bool:
        if cost <= 0:
            return True
            
        # CORRECTION : Utiliser spell_manager au lieu de caster.current_spells
        success = spell_manager.consume_spells(caster, cost)
        if success:
            if cost > 0:
                current = spell_manager.get_current_spells(caster)
                log.append(f"🔮 {caster.name} dépense {cost} sort(s) ({current + cost} → {current})")
            return True
        else:
            current = spell_manager.get_current_spells(caster)
            log.append(f"❌ {caster.name} n'a pas assez de sorts (besoin: {cost}, disponible: {current})")
            return False
    
    def _get_all_allies(self, caster, context: Dict[str, Any]) -> List:
        """
        Récupère tous les alliés du lanceur incluant lui-même
        
        Args:
            caster: Personnage lanceur
            context: Contexte du combat
            
        Returns:
            List: Liste des alliés vivants
        """
        allies = [caster]
        
        # Rechercher les alliés dans le contexte
        if hasattr(context, 'heroes') and context.heroes:
            for hero in context.heroes:
                if hero != caster and self._is_alive(hero):
                    allies.append(hero)
        elif 'heroes' in context:
            for hero in context['heroes']:
                if hero != caster and self._is_alive(hero):
                    allies.append(hero)
        elif hasattr(context, 'party') and context.party:
            for member in context.party:
                if member != caster and self._is_alive(member):
                    allies.append(member)
        
        return allies
    
    def _get_all_enemies(self, caster, context: Dict[str, Any]) -> List:
        """Récupère tous les ennemis vivants"""
        # PRIORITÉ : 'alive_enemies' utilisé par combat_actions
        if 'alive_enemies' in context and context['alive_enemies']:
            return [e for e in context['alive_enemies'] if self._is_alive(e)]
        
        # Fallback vers autres clés
        for key in ['enemies', 'opponents']:
            if key in context and context[key]:
                return [e for e in context[key] if self._is_alive(e)]
            if hasattr(context, key) and getattr(context, key):
                return [e for e in getattr(context, key) if self._is_alive(e)]
        
        return []
    
    def _is_alive(self, character) -> bool:
        """
        Vérifie si un personnage est vivant
        
        Args:
            character: Personnage à vérifier
            
        Returns:
            bool: True si le personnage est vivant
        """
        # Système de blessures (Périples)
        if hasattr(character, 'current_wounds') and hasattr(character, 'health'):
            return character.current_wounds < character.health
        
        # Système de PV classique
        elif hasattr(character, 'current_health'):
            return character.current_health > 0
        
        # Fallback: supposer vivant si pas d'info
        return True
    
    def _is_unconscious(self, character) -> bool:
        """
        Vérifie si un personnage est inconscient
        
        Args:
            character: Personnage à vérifier
            
        Returns:
            bool: True si le personnage est inconscient
        """
        # Vérification explicite d'état
        if hasattr(character, 'is_unconscious'):
            return character.is_unconscious
        
        # Système de blessures (Périples) - inconscient si blessures >= santé max
        if hasattr(character, 'current_wounds') and hasattr(character, 'health'):
            return character.current_wounds >= character.health
        
        # Système de PV classique - inconscient si PV <= 0
        elif hasattr(character, 'current_health'):
            return character.current_health <= 0
        
        return False
    
    def __str__(self):
        """ReprÃ©sentation textuelle de la capacitÃ©"""
        return f"{self.hero_code}-{self.ability_number}: {self.name}"
    
    def __repr__(self):
        """ReprÃ©sentation technique de la capacitÃ©"""
        return f"<{self.__class__.__name__}({self.hero_code}, {self.ability_number}, '{self.name}')>"