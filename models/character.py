"""
Modèles de personnages pour le Simulateur Périples
VERSION SIMPLIFIÉE avec système de potions de santé 🩸❤️‍🩹
NOUVEAU : Support potions dans builds custom
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum
from .abilities import Ability, AbilityAction, AbilityType, AbilityManager

class PotionType(Enum):
    """Types de potions de santé"""
    SMALL = "small"    # 🩸 Petite Potion - 4 PV
    LARGE = "large"    # ❤️‍🩹 Grande Potion - PV max

class HealthPotion(BaseModel):
    """Potion de santé consommable"""
    
    potion_type: PotionType
    quantity: int = Field(1, ge=0)
    
    @property
    def name(self) -> str:
        return "Petite Potion" if self.potion_type == PotionType.SMALL else "Grande Potion"
    
    @property
    def icon(self) -> str:
        return "🩸" if self.potion_type == PotionType.SMALL else "❤️‍🩹"
    
    @property
    def heal_amount(self) -> int:
        """4 PV pour petite, 0 pour grande (= PV max)"""
        return 4 if self.potion_type == PotionType.SMALL else 0
    
    @property
    def is_full_heal(self) -> bool:
        return self.potion_type == PotionType.LARGE
    
    def can_use(self) -> bool:
        return self.quantity > 0
    
    def use_potion(self) -> bool:
        """Consomme une potion"""
        if self.quantity > 0:
            self.quantity -= 1
            return True
        return False

class Character(BaseModel):
    """Héros avec capacités et potions"""
    
    # Stats de base
    code: str
    name: str
    precision: int
    damage: int
    spells: int
    health: int
    current_health: Optional[int] = None
    
    # Équipements
    equipped_items: List['Equipment'] = []
    build_name: Optional[str] = None
    
    # Combat
    current_spells: Optional[int] = None
    spells_used: int = 0
    
    # Capacités
    abilities: List[Ability] = Field(default_factory=list)
    unlocked_abilities: List[int] = Field(default_factory=list)
    
    # Potions
    health_potions: List[HealthPotion] = Field(default_factory=list)
    
    # État du tour
    action_taken_this_turn: bool = False
    ability_used_this_turn: Optional[Ability] = None
    can_attack_this_turn: bool = True
    potion_used_this_turn: bool = False
    
    def model_post_init(self, __context):
        """Initialisation"""
        if self.current_health is None:
            self.current_health = self.health
        
        if self.abilities and not self.unlocked_abilities:
            self.unlock_ability(1)
        
        if not self.health_potions:
            self.add_default_potions()
    
    # === POTIONS - SECTION ÉTENDUE POUR BUILDS CUSTOM ===
    
    def add_default_potions(self):
        """Ajoute 1 Petite Potion par défaut"""
        self.health_potions = [HealthPotion(potion_type=PotionType.SMALL, quantity=1)]
    
    def set_custom_potions(self, potions_config: List[Dict]):
        """
        Configure potions pour build custom
        NOUVEAU - Interface avec validation
        
        Args:
            potions_config: [{'type': 'small', 'quantity': 2}, {'type': 'large', 'quantity': 1}]
        """
        self.health_potions = []
        
        for config in potions_config:
            potion_type = PotionType.SMALL if config['type'] == 'small' else PotionType.LARGE
            quantity = min(3, max(0, config['quantity']))  # Limite 0-3
            
            if quantity > 0:
                potion = HealthPotion(potion_type=potion_type, quantity=quantity)
                self.health_potions.append(potion)
    
    def set_potions_from_selection(self, small_count: int = 0, large_count: int = 0):
        """
        NOUVEAU - Configuration simple depuis interface Forge
        
        Args:
            small_count: Nombre de petites potions (0-3)
            large_count: Nombre de grandes potions (0-1)
        """
        self.health_potions = []
        
        # Validation et ajout Petites Potions
        small_count = min(3, max(0, small_count))
        if small_count > 0:
            small_potion = HealthPotion(potion_type=PotionType.SMALL, quantity=small_count)
            self.health_potions.append(small_potion)
        
        # Validation et ajout Grande Potion
        large_count = min(1, max(0, large_count))
        if large_count > 0:
            large_potion = HealthPotion(potion_type=PotionType.LARGE, quantity=large_count)
            self.health_potions.append(large_potion)
    
    def get_potion_by_type(self, potion_type: PotionType) -> Optional[HealthPotion]:
        """Trouve une potion utilisable du type demandé"""
        for potion in self.health_potions:
            if potion.potion_type == potion_type and potion.can_use():
                return potion
        return None
    
    def can_use_potion(self) -> tuple[bool, str]:
        """Vérifie si une potion peut être utilisée"""
        if self.is_at_full_health():
            return False, "Santé déjà au maximum"
        
        available = any(p.can_use() for p in self.health_potions)
        if not available:
            return False, "Aucune potion disponible"
        
        return True, "Potion utilisable"
    
    def use_health_potion(self) -> Dict:
        """Utilise automatiquement la meilleure potion"""
        result = {
            'success': False,
            'potion_used': None,
            'healing_done': 0,
            'message': '',
            'prevents_attack': False
        }
        
        can_use, reason = self.can_use_potion()
        if not can_use:
            result['message'] = reason
            return result
        
        # Choix intelligent
        potion_type = self._choose_best_potion()
        if not potion_type:
            result['message'] = "Aucune potion appropriée"
            return result
        
        # Utilisation
        potion = self.get_potion_by_type(potion_type)
        if not potion or not potion.use_potion():
            result['message'] = "Échec utilisation potion"
            return result
        
        # Soins
        if potion.is_full_heal:
            old_health = self.current_health
            self.current_health = self.get_total_health()
            healing = self.current_health - old_health
        else:
            healing = self.heal(potion.heal_amount)
        
        self.potion_used_this_turn = True
        
        result.update({
            'success': True,
            'potion_used': potion.name,
            'potion_icon': potion.icon,
            'healing_done': healing,
            'message': f"{potion.icon} {potion.name} utilisée : +{healing} PV"
        })
        
        return result
    
    def _choose_best_potion(self) -> Optional[PotionType]:
        """IA : Choisit la meilleure potion"""
        health_percent = (self.current_health / self.get_total_health()) * 100
        
        # Critique : Grande potion
        if health_percent < 25:
            if self.get_potion_by_type(PotionType.LARGE):
                return PotionType.LARGE
        
        # Normal : Petite potion
        if health_percent < 75:
            if self.get_potion_by_type(PotionType.SMALL):
                return PotionType.SMALL
        
        # Fallback
        for potion in self.health_potions:
            if potion.can_use():
                return potion.potion_type
        
        return None
    
    def get_potions_summary(self) -> Dict:
        """
        NOUVEAU - Résumé potions pour affichage interface
        """
        small_total = sum(p.quantity for p in self.health_potions if p.potion_type == PotionType.SMALL)
        large_total = sum(p.quantity for p in self.health_potions if p.potion_type == PotionType.LARGE)
        total = small_total + large_total
        
        parts = []
        if small_total > 0:
            parts.append(f"🩸 {small_total} Petite{'s' if small_total > 1 else ''}")
        if large_total > 0:
            parts.append(f"❤️‍🩹 {large_total} Grande{'s' if large_total > 1 else ''}")
        
        return {
            'has_potions': total > 0,
            'total_count': total,
            'small_count': small_total,
            'large_count': large_total,
            'display_text': ", ".join(parts) if parts else "Aucune potion",
            'display_short': f"🧪 {total}" if total > 0 else "🧪 0"
        }
    
    def get_potions_for_forge_display(self) -> Dict:
        """
        NOUVEAU - Format spécial pour interface Forge
        """
        summary = self.get_potions_summary()
        
        return {
            'small_count': summary['small_count'],
            'large_count': summary['large_count'],
            'total_display': summary['display_text'],
            'preview_text': f"🧪 Potions: {summary['display_text']}" if summary['has_potions'] else "🧪 Aucune potion sélectionnée"
        }
    
    # === SANTÉ (INCHANGÉ) ===
    
    def is_alive(self) -> bool:
        return self.current_health > 0
    
    def take_damage(self, damage: int):
        self.current_health = max(0, self.current_health - damage)
    
    def heal(self, heal_amount: int) -> int:
        """Soigne et retourne le montant réellement soigné"""
        if heal_amount <= 0:
            return 0
        
        max_health = self.get_total_health()
        old_health = self.current_health
        self.current_health = min(max_health, self.current_health + heal_amount)
        
        return self.current_health - old_health
    
    def is_at_full_health(self) -> bool:
        return self.current_health >= self.get_total_health()
    
    def reset_health(self):
        self.current_health = self.get_total_health()
    
    # === ÉQUIPEMENTS (INCHANGÉ) ===
    
    def equip_items(self, items: List['Equipment'], build_name: str = None):
        self.equipped_items = items
        self.build_name = build_name
        if self.current_health == self.health:
            self.reset_health()
    
    def get_equipment_bonus(self, stat_type: str) -> int:
        total = 0
        for item in self.equipped_items:
            if stat_type == 'precision':
                total += item.precision
            elif stat_type == 'physical_damage':
                total += item.physical_damage
            elif stat_type == 'magical_damage':
                total += item.magical_damage
            elif stat_type == 'defense':
                total += item.defense
            elif stat_type == 'spells':
                total += item.spells
            elif stat_type == 'health':
                total += item.health
        return total
    
    def get_total_precision(self) -> int:
        return self.precision + self.get_equipment_bonus('precision')
    
    def get_total_damage(self) -> int:
        return self.damage + self.get_equipment_bonus('physical_damage')
    
    def get_total_magical_damage(self) -> int:
        return self.get_equipment_bonus('magical_damage')
    
    def get_total_parade(self) -> int:
        return self.get_equipment_bonus('defense')
    
    def get_total_spells(self) -> int:
        return self.spells + self.get_equipment_bonus('spells')
    
    def get_total_health(self) -> int:
        return self.health + self.get_equipment_bonus('health')
    
    def get_stats_summary(self) -> Dict:
        return {
            'base': {
                'precision': self.precision,
                'damage': self.damage,
                'spells': self.spells,
                'health': self.health,
                'parade': 0
            },
            'bonus': {
                'precision': self.get_equipment_bonus('precision'),
                'damage': self.get_equipment_bonus('physical_damage'),
                'magical_damage': self.get_equipment_bonus('magical_damage'),
                'parade': self.get_equipment_bonus('defense'),
                'spells': self.get_equipment_bonus('spells'),
                'health': self.get_equipment_bonus('health')
            },
            'total': {
                'precision': self.get_total_precision(),
                'damage': self.get_total_damage(),
                'magical_damage': self.get_total_magical_damage(),
                'parade': self.get_total_parade(),
                'spells': self.get_total_spells(),
                'health': self.get_total_health()
            }
        }
    
    # === CAPACITÉS (INCHANGÉ) ===
    
    def add_abilities(self, abilities: List[Ability]):
        self.abilities = abilities
        if abilities and 1 not in self.unlocked_abilities:
            self.unlock_ability(1)
    
    def unlock_ability(self, ability_number: int) -> bool:
        if not (1 <= ability_number <= 6) or ability_number in self.unlocked_abilities:
            return ability_number in self.unlocked_abilities
        
        # Vérifie prérequis
        for i in range(1, ability_number):
            if i not in self.unlocked_abilities:
                return False
        
        self.unlocked_abilities.append(ability_number)
        
        # Met à jour la capacité
        for ability in self.abilities:
            if ability.ability_number == ability_number:
                ability.is_unlocked = True
                ability.reset_combat_uses()
        
        return True
    
    def get_available_abilities(self) -> List[Ability]:
        """Capacités utilisables (exclusion Kraor 1&3)"""
        available = []
        current_spells = self.current_spells or self.get_total_spells()
        
        for ability in self.abilities:
            if not ability.is_unlocked:
                continue
            
            # Exclusion Kraor
            if self.code == "P-4" and ability.ability_number in [1, 3]:
                continue
            
            can_use, _ = ability.can_use(current_spells)
            if can_use:
                available.append(ability)
        
        return available
    
    def use_ability(self, ability: Ability) -> AbilityAction:
        action = AbilityAction(
            ability_id=ability.unique_id,
            ability_name=ability.name,
            user_name=self.name,
            prevents_attack=ability.prevents_attack
        )
        
        # Consommation sorts
        if ability.spell_cost > 0:
            current_spells = self.current_spells or self.get_total_spells()
            self.current_spells = current_spells - ability.spell_cost
            self.spells_used += ability.spell_cost
            action.spell_cost_paid = ability.spell_cost
        
        # Consommation utilisations
        ability.use_ability()
        
        # État tour
        self.ability_used_this_turn = ability
        if ability.prevents_attack:
            self.action_taken_this_turn = True
            self.can_attack_this_turn = False
        
        action.success = True
        return action
    
    # === COMBAT (INCHANGÉ) ===
    
    def reset_turn_state(self):
        """Reset état du tour"""
        self.action_taken_this_turn = False
        self.ability_used_this_turn = None
        self.can_attack_this_turn = True
        self.potion_used_this_turn = False
    
    def start_new_combat(self):
        """Prépare nouveau combat"""
        self.reset_turn_state()
        self.current_spells = self.get_total_spells()
        self.spells_used = 0
        
        # Reset capacités
        for ability in self.abilities:
            ability.reset_combat_uses()
    
    def get_combat_status(self) -> Dict:
        """État complet pour interface"""
        current_spells = self.current_spells or self.get_total_spells()
        
        return {
            'health': {
                'current': self.current_health,
                'max': self.get_total_health(),
                'percentage': round((self.current_health / self.get_total_health()) * 100, 1)
            },
            'spells': {
                'current': current_spells,
                'max': self.get_total_spells(),
                'used': self.spells_used
            },
            'potions': self.get_potions_summary(),
            'turn_state': {
                'action_taken': self.action_taken_this_turn,
                'can_attack': self.can_attack_this_turn,
                'potion_used': self.potion_used_this_turn
            }
        }

# === MODÈLES ENEMY ET EQUIPMENT (INCHANGÉS) ===

class Enemy(BaseModel):
    """Modèle ennemi - inchangé"""
    code: str
    name: str
    defense: int
    stats_by_players: Dict[int, Dict[str, int]]
    is_magical: bool = False
    has_magical_damage: bool = False
    current_health: Optional[int] = None
    max_health: Optional[int] = None
    
    def get_stats_for_players(self, player_count: int) -> Dict[str, int]:
        return self.stats_by_players.get(player_count, self.stats_by_players[4])
    
    def initialize_for_combat(self, player_count: int):
        stats = self.get_stats_for_players(player_count)
        self.max_health = stats['health']
        self.current_health = stats['health']
    
    def is_alive(self) -> bool:
        return self.current_health > 0
    
    def take_damage(self, damage: int, player_count: int):
        stats = self.get_stats_for_players(player_count)
        defense_value = stats.get('defense', 0)
        actual_damage = max(1, damage - defense_value)
        self.current_health = max(0, self.current_health - actual_damage)
        return actual_damage

class Equipment(BaseModel):
    """Modèle équipement - inchangé"""
    code: str
    name: str
    type: str = "accessoire"
    precision: int = 0
    physical_damage: int = 0
    magical_damage: int = 0
    defense: int = 0
    spells: int = 0
    health: int = 0