# base_ability
"""
Classe de base pour toutes les capacités individuelles
Architecture modulaire pour le système Périples Balance Workshop
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import random

class BaseAbility(ABC):
    """Classe abstraite de base pour toutes les capacités individuelles"""
    
    def __init__(self, hero_code: str, ability_number: int, name: str, description: str):
        """
        Initialise une capacité individuelle
        
        Args:
            hero_code: Code du héros (P-1, P-2, etc.)
            ability_number: Numéro de capacité (1-6)
            name: Nom de la capacité
            description: Description textuelle
        """
        self.hero_code = hero_code
        self.ability_number = ability_number
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """
        Exécute la capacité avec ses effets mécaniques réels
        
        Args:
            caster: Personnage qui lance la capacité
            targets: Liste des cibles (héros/ennemis selon le type)
            context: Contexte du combat (spell_manager, rules, etc.)
            log: Liste pour ajouter les messages de log
            
        Returns:
            bool: True si la capacité a eu un effet mécanique, False sinon
        """
        pass
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        """
        Vérifie si la capacité peut être exécutée
        
        Args:
            caster: Personnage qui veut lancer la capacité
            context: Contexte du combat
            
        Returns:
            bool: True si la capacité peut être lancée
        """
        # Vérifications de base par défaut
        spell_manager = context.get('spell_manager')
        if not spell_manager:
            return False
            
        # Vérifier si assez de sorts disponibles (si capacité magique)
        if hasattr(self, 'spell_cost') and self.spell_cost > 0:
            return caster.current_spells >= self.spell_cost
            
        return True
    
    def get_preview(self) -> str:
        """
        Retourne un aperçu des effets de la capacité
        
        Returns:
            str: Description des effets mécaniques
        """
        return f"🔋 {self.name}: Effet mécanique défini"
    
    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        """
        Détermine les cibles valides pour cette capacité
        
        Args:
            caster: Personnage qui lance la capacité
            all_heroes: Liste de tous les héros
            all_enemies: Liste de tous les ennemis
            context: Contexte du combat
            
        Returns:
            List: Liste des cibles appropriées
        """
        # Par défaut, retourne le lanceur (self-target)
        return [caster]
    
    def _apply_healing(self, target, amount: int, log: List[str]) -> bool:
        """
        Utilitaire pour appliquer des soins
        
        Args:
            target: Cible à soigner
            amount: Montant de soins
            log: Liste des logs
            
        Returns:
            bool: True si des soins ont été appliqués
        """
        if amount <= 0:
            return False
            
        old_health = target.current_health
        target.current_health = min(target.current_health + amount, target.max_health)
        actual_healing = target.current_health - old_health
        
        if actual_healing > 0:
            log.append(f"💚 {target.name} récupère {actual_healing} PV ({old_health} → {target.current_health})")
            return True
        else:
            log.append(f"💚 {target.name} est déjà en pleine forme")
            return False
    
    def _apply_damage(self, target, amount: int, damage_type: str, log: List[str]) -> bool:
        """
        Utilitaire pour appliquer des dégâts
        
        Args:
            target: Cible à endommager
            amount: Montant de dégâts
            damage_type: Type de dégâts ("physical" ou "magical")
            log: Liste des logs
            
        Returns:
            bool: True si des dégâts ont été infligés
        """
        if amount <= 0:
            return False
            
        # Appliquer les dégâts avec le système de parade si applicable
        if hasattr(target, 'apply_damage_with_parade'):
            damage_result = target.apply_damage_with_parade(amount)
            actual_damage = damage_result['actual_damage']
            blocked = damage_result['blocked_damage']
            
            if blocked > 0:
                log.append(f"🛡️ {target.name} pare {blocked} dégâts")
            if actual_damage > 0:
                emoji = "⚡" if damage_type == "magical" else "💥"
                log.append(f"{emoji} {target.name} subit {actual_damage} dégâts {damage_type}s")
                return True
        else:
            # Système simple pour ennemis
            old_health = target.current_health
            target.current_health = max(0, target.current_health - amount)
            actual_damage = old_health - target.current_health
            
            if actual_damage > 0:
                emoji = "⚡" if damage_type == "magical" else "💥"
                log.append(f"{emoji} {target.name} subit {actual_damage} dégâts {damage_type}s")
                return True
                
        return False
    
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
        """
        Utilitaire pour consommer les sorts nécessaires
        
        Args:
            caster: Lanceur de la capacité
            cost: Coût en sorts
            spell_manager: Gestionnaire des sorts
            log: Liste des logs
            
        Returns:
            bool: True si le coût a pu être payé
        """
        if cost <= 0:
            return True
            
        if caster.current_spells >= cost:
            caster.current_spells -= cost
            if cost > 0:
                log.append(f"🔮 {caster.name} dépense {cost} sort(s) ({caster.current_spells + cost} → {caster.current_spells})")
            return True
        else:
            log.append(f"❌ {caster.name} n'a pas assez de sorts (besoin: {cost}, disponible: {caster.current_spells})")
            return False
    
    def __str__(self):
        """Représentation textuelle de la capacité"""
        return f"{self.hero_code}-{self.ability_number}: {self.name}"
    
    def __repr__(self):
        """Représentation technique de la capacité"""
        return f"<{self.__class__.__name__}({self.hero_code}, {self.ability_number}, '{self.name}')>"