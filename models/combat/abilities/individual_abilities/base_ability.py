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

    @property
    def unique_id(self) -> str:
        """Identifiant unique de la capacité"""
        return f"{self.hero_code}_ability_{self.ability_number}"

    @abstractmethod
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]):
        """
        Exécute la capacité avec ses effets mécaniques réels

        Args:
            caster: Personnage qui lance la capacité
            targets: Liste des cibles (héros/ennemis selon le type)
            context: Contexte du combat (spell_manager, rules, etc.)
            log: Liste pour ajouter les messages de log

        Returns:
            bool OU dict:
            - bool (legacy): True si succès, False sinon
            - dict (nouveau): {'success': bool, 'damage_dealt': int}

            Les capacités qui font des dégâts directs doivent retourner le dict
            Les capacités de buff/soin peuvent continuer à retourner bool
        """
        pass
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        spell_manager = context.get('spell_manager')
        if not spell_manager:
            return False

        # Vérifier les utilisations restantes
        if hasattr(self, 'uses_remaining_combat') and self.uses_remaining_combat is not None:
            uses_remaining = getattr(self, 'uses_remaining_combat', None)
            if uses_remaining is not None and uses_remaining <= 0:
                return False

        # Vérifier le coût en sorts
        if hasattr(self, 'spell_cost') and self.spell_cost is not None and self.spell_cost > 0:
            current_spells = getattr(caster, 'current_spells', None)
            if current_spells is None:
                return False
            return current_spells >= self.spell_cost

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
            old_wounds = getattr(target, 'current_wounds', None)
            health = getattr(target, 'health', None)
            if old_wounds is not None and health is not None:
                target.current_wounds = max(0, old_wounds - amount)
                actual_healing = old_wounds - target.current_wounds

                if actual_healing > 0:
                    log.append(f"💚 {target.name} guérit {actual_healing} blessure(s)")
                return actual_healing

        # Système de PV classique (fallback) - PV augmentent avec les soins
        if hasattr(target, 'current_health'):
            old_health = getattr(target, 'current_health', None)
            if old_health is None:
                return 0

            # Déterminer PV max (utiliser get_total_health() pour les héros, max_health pour les ennemis)
            if hasattr(target, 'get_total_health'):
                max_hp = target.get_total_health()
            elif hasattr(target, 'max_health'):
                max_hp = target.max_health
            else:
                # Pas de limite si aucun max défini (cas rare)
                max_hp = old_health + amount

            # Plafonner les soins au maximum
            target.current_health = min(old_health + amount, max_hp)
            actual_healing = target.current_health - old_health

            if actual_healing > 0:
                log.append(f"💚 {target.name} récupère {actual_healing} PV (max {max_hp})")
            elif amount > 0 and actual_healing == 0:
                log.append(f"⚠️ {target.name} est déjà à PV max ({max_hp})")
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
            old_wounds = getattr(target, 'current_wounds', None)
            health = getattr(target, 'health', None)
            if old_wounds is not None and health is not None:
                target.current_wounds = min(health, old_wounds + amount)
                actual_damage = target.current_wounds - old_wounds

                if actual_damage > 0:
                    emoji = "⚡" if damage_type == "magical" else "💥"
                    log.append(f"{emoji} {target.name} subit {actual_damage} blessure(s)")

                # NOUVEAU : Accumuler dans compteur si présent
                if hasattr(self, '_damage_counter') and isinstance(self._damage_counter, dict):
                    self._damage_counter['total'] += actual_damage
                    # Aussi tracker la cible et ses dégâts pour record_damage_taken()
                    if 'targets' not in self._damage_counter:
                        self._damage_counter['targets'] = []
                    self._damage_counter['targets'].append((target, actual_damage))

                return actual_damage

        # Système de PV classique (fallback) - PV diminuent avec les dégâts
        if hasattr(target, 'current_health'):
            old_health = getattr(target, 'current_health', None)
            if old_health is None:
                return 0
            target.current_health = max(0, old_health - amount)
            actual_damage = old_health - target.current_health

            if actual_damage > 0:
                emoji = "⚡" if damage_type == "magical" else "💥"
                log.append(f"{emoji} {target.name} subit {actual_damage} dégâts")

            # NOUVEAU : Accumuler dans compteur si présent
            if hasattr(self, '_damage_counter') and isinstance(self._damage_counter, dict):
                self._damage_counter['total'] += actual_damage
                # Aussi tracker la cible et ses dégâts pour record_damage_taken()
                if 'targets' not in self._damage_counter:
                    self._damage_counter['targets'] = []
                self._damage_counter['targets'].append((target, actual_damage))

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
        # Système de blessures (Périples) - vérifier ET que les valeurs ne sont pas None
        if hasattr(character, 'current_wounds') and hasattr(character, 'health'):
            wounds = getattr(character, 'current_wounds', None)
            health = getattr(character, 'health', None)
            if wounds is not None and health is not None:
                return wounds < health

        # Système de PV classique - fallback si blessures non disponibles
        if hasattr(character, 'current_health'):
            current_health = getattr(character, 'current_health', None)
            if current_health is not None:
                return current_health > 0

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
            wounds = getattr(character, 'current_wounds', None)
            health = getattr(character, 'health', None)
            if wounds is not None and health is not None:
                return wounds >= health

        # Système de PV classique - inconscient si PV <= 0
        if hasattr(character, 'current_health'):
            current_health = getattr(character, 'current_health', None)
            if current_health is not None:
                return current_health <= 0

        return False

    def _check_uses_remaining(self) -> bool:
        """
        Vérifie si la capacité a encore des utilisations restantes
        Gère les cas où uses_remaining_combat pourrait être None

        Returns:
            bool: True si la capacité peut encore être utilisée, False sinon
        """
        if not hasattr(self, 'uses_remaining_combat'):
            return True  # Pas de limitation

        uses_remaining = getattr(self, 'uses_remaining_combat', None)
        if uses_remaining is None:
            return True  # Pas de limitation définie

        return uses_remaining > 0

    def reset_combat_uses(self):
        """
        Réinitialise les utilisations par combat au début d'un nouveau combat
        À appeler depuis Character.start_new_combat()
        """
        if hasattr(self, 'uses_per_combat') and hasattr(self, 'uses_remaining_combat'):
            self.uses_remaining_combat = self.uses_per_combat

    def __str__(self):
        """ReprÃ©sentation textuelle de la capacitÃ©"""
        return f"{self.hero_code}-{self.ability_number}: {self.name}"
    
    def __repr__(self):
        """ReprÃ©sentation technique de la capacitÃ©"""
        return f"<{self.__class__.__name__}({self.hero_code}, {self.ability_number}, '{self.name}')>"