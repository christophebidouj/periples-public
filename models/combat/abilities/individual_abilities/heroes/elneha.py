# elneha_pilots
"""
Capacités individuelles d'Elneha (P-1)
Version pilote avec 2 capacités : Forme d'ours et Soin mineur
"""

from typing import List, Dict, Any
from ..base_ability import BaseAbility
from ..ability_registry import register_ability

@register_ability
class ElnehaFormeOurs(BaseAbility):
    """P-1-1: Forme d'ours - Transformation physique"""
    
    hero_code = "P-1"
    ability_number = 1
    name = "Forme d'ours"
    description = "Permet à Elneha de se métamorphoser en Ours."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0  # Capacité physique
        self.transformation_attack_bonus = 2
        self.transformation_defense_bonus = 1
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """
        Exécute la transformation en ours
        
        Effets:
        - +2 Attaque physique
        - +1 Défense
        - Transformation persiste jusqu'à transformation différente
        """
        try:
            # Vérifier que c'est bien Elneha
            if caster.code != "P-1":
                log.append(f"❌ {self.name} ne peut être utilisée que par Elneha")
                return False
            
            # Appliquer la transformation
            old_attack = caster.current_attack
            old_defense = caster.current_defense
            
            # Réinitialiser aux stats de base avant d'appliquer la nouvelle transformation
            caster.reset_current_stats()
            
            # Appliquer les bonus de forme d'ours
            caster.current_attack += self.transformation_attack_bonus
            caster.current_defense += self.transformation_defense_bonus
            
            # Marquer la transformation active (utiliser le système existant)
            if hasattr(caster, 'set_form'):
                caster.set_form("bear")
            else:
                caster.current_form = "bear"
            
            log.append(f"🐻 {caster.name} se transforme en Ours !")
            log.append(f"   ⚔️ Attaque: {old_attack} → {caster.current_attack} (+{self.transformation_attack_bonus})")
            log.append(f"   🛡️ Défense: {old_defense} → {caster.current_defense} (+{self.transformation_defense_bonus})")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur transformation ours: {str(e)}")
            return False
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        """Vérifie si la transformation peut être activée"""
        return caster.code == "P-1"  # Seule Elneha peut utiliser cette capacité
    
    def get_preview(self) -> str:
        """Aperçu des effets"""
        return f"🐻 {self.name}: +{self.transformation_attack_bonus} ATT, +{self.transformation_defense_bonus} DEF"
    
    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        """La transformation cible toujours le lanceur"""
        return [caster]


@register_ability  
class ElnehaSoinMineur(BaseAbility):
    """P-1-2: Soin mineur - Soigne jusqu'à 4 blessures"""
    
    hero_code = "P-1"
    ability_number = 2
    name = "Soin mineur"
    description = "Soigner jusqu'à 4 blessures de n'importe quel personnage."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 1  # Capacité magique
        self.healing_amount = 4
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """
        Exécute le soin mineur
        
        Effets:
        - Soigne 4 points de vie
        - Peut cibler n'importe quel personnage (allié ou soi-même)
        - Coûte 1 sort
        """
        try:
            # Vérifier le coût en sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # Vérifier qu'il y a une cible
            if not targets:
                log.append(f"❌ {self.name}: Aucune cible sélectionnée")
                return False
            
            target = targets[0]  # Premier (et normalement seul) cible
            
            # Appliquer les soins
            healing_applied = self._apply_healing(target, self.healing_amount, log)
            
            if healing_applied:
                log.append(f"✨ {caster.name} utilise {self.name} sur {target.name}")
                return True
            else:
                # Même si pas de soins effectifs, la capacité a été utilisée
                log.append(f"✨ {caster.name} utilise {self.name} sur {target.name}")
                return True
                
        except Exception as e:
            log.append(f"❌ Erreur soin mineur: {str(e)}")
            return False
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        """Vérifie si le soin peut être lancé"""
        if caster.code != "P-1":
            return False
            
        # Vérifier si assez de sorts
        return caster.current_spells >= self.spell_cost
    
    def get_preview(self) -> str:
        """Aperçu des effets"""
        return f"💚 {self.name}: Soigne {self.healing_amount} PV (Coût: {self.spell_cost} sort)"
    
    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        """
        Retourne tous les héros vivants comme cibles potentielles
        Le soin mineur peut cibler n'importe quel personnage
        """
        valid_targets = []
        
        # Ajouter tous les héros vivants (blessés ou non)
        for hero in all_heroes:
            if hasattr(hero, 'current_health') and hero.current_health > 0:
                valid_targets.append(hero)
        
        return valid_targets


# Utilitaires pour les transformations d'Elneha
class ElnehaTransformationHelper:
    """Classe utilitaire pour gérer les transformations d'Elneha"""
    
    @staticmethod
    def reset_transformation(caster, log: List[str]):
        """Remet Elneha à sa forme normale"""
        if hasattr(caster, 'set_form'):
            old_form = getattr(caster, 'current_form', 'human')
            caster.set_form("human")
            log.append(f"🔄 {caster.name} reprend sa forme normale (était: {old_form})")
        elif hasattr(caster, 'current_form'):
            old_form = caster.current_form
            caster.current_form = "human"
            caster.reset_current_stats()
            log.append(f"🔄 {caster.name} reprend sa forme normale (était: {old_form})")
    
    @staticmethod
    def get_current_transformation(caster) -> str:
        """Retourne la transformation actuelle d'Elneha"""
        return getattr(caster, 'current_form', 'human')
    
    @staticmethod
    def is_transformed(caster) -> bool:
        """Vérifie si Elneha est transformée"""
        current_form = getattr(caster, 'current_form', 'human')
        return current_form != 'human'