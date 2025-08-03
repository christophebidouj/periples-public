"""
Modèles de personnages pour le Simulateur Périples
VERSION MISE À JOUR avec support du système de capacités
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, TYPE_CHECKING
from .abilities import Ability, AbilityAction, AbilityType, AbilityManager

if TYPE_CHECKING:
    pass

class Character(BaseModel):
    """Modèle d'un personnage héros avec support des capacités"""
    
    # === DONNÉES DE BASE (INCHANGÉES) ===
    code: str
    name: str
    precision: int
    damage: int
    spells: int
    health: int
    current_health: Optional[int] = None
    
    # === ÉQUIPEMENTS (INCHANGÉES) ===
    equipped_items: List['Equipment'] = []
    build_name: Optional[str] = None
    
    # === TRACKING RESSOURCES COMBAT (EXISTANT) ===
    initial_health: Optional[int] = None
    initial_spells: Optional[int] = None
    current_spells: Optional[int] = None
    spells_used: int = 0
    
    # === NOUVEAU - SYSTÈME DE CAPACITÉS ===
    abilities: List[Ability] = Field(default_factory=list, description="Capacités du héros")
    unlocked_abilities: List[int] = Field(default_factory=list, description="Numéros de capacités débloquées")
    
    # === NOUVEAU - ÉTAT DE COMBAT ===
    action_taken_this_turn: bool = Field(False, description="Action principale déjà effectuée ce tour")
    ability_used_this_turn: Optional[Ability] = Field(None, description="Capacité utilisée ce tour")
    can_attack_this_turn: bool = Field(True, description="Peut attaquer ce tour")
    
    def model_post_init(self, __context):
        """Initialise les PV actuels et l'état si non définis"""
        if self.current_health is None:
            self.current_health = self.health
        
        # Initialise la première capacité si des capacités sont présentes
        if self.abilities and not self.unlocked_abilities:
            self.unlock_ability(1)
    
    # === MÉTHODES EXISTANTES (INCHANGÉES) ===
    
    def reset_health(self):
        """Remet les PV au maximum (avec bonus équipements)"""
        self.current_health = self.get_total_health()
    
    def is_alive(self) -> bool:
        """Vérifie si le personnage est vivant"""
        return self.current_health > 0
    
    def take_damage(self, damage: int):
        """Fait subir des dégâts au personnage"""
        self.current_health = max(0, self.current_health - damage)
    
    def equip_items(self, items: List['Equipment'], build_name: str = None):
        """Équipe des objets au personnage"""
        self.equipped_items = items
        self.build_name = build_name
        # Recalcule les PV actuels avec les nouveaux bonus
        if self.current_health == self.health:  # Si à pleine santé
            self.reset_health()
    
    def get_equipment_bonus(self, stat_type: str) -> int:
        """Calcule le bonus total d'une statistique grâce aux équipements"""
        total_bonus = 0
        for item in self.equipped_items:
            if stat_type == 'precision':
                total_bonus += item.precision
            elif stat_type == 'physical_damage':
                total_bonus += item.physical_damage
            elif stat_type == 'magical_damage':
                total_bonus += item.magical_damage
            elif stat_type == 'defense':
                total_bonus += item.defense
            elif stat_type == 'spells':
                total_bonus += item.spells
            elif stat_type == 'health':
                total_bonus += item.health
        return total_bonus
    
    def get_total_precision(self) -> int:
        """Précision totale (base + équipements)"""
        return self.precision + self.get_equipment_bonus('precision')
    
    def get_total_damage(self) -> int:
        """Dégâts physiques totaux (base + équipements)"""
        return self.damage + self.get_equipment_bonus('physical_damage')
    
    def get_total_magical_damage(self) -> int:
        """Dégâts magiques totaux (équipements uniquement)"""
        return self.get_equipment_bonus('magical_damage')
    
    def get_total_parade(self) -> int:
        """Parade totale (équipements uniquement)"""
        return self.get_equipment_bonus('defense')
    
    def get_total_defense(self) -> int:
        """Alias pour compatibilité - À supprimer progressivement"""
        return self.get_total_parade()
    
    def get_total_spells(self) -> int:
        """Points de sorts totaux (base + équipements)"""
        return self.spells + self.get_equipment_bonus('spells')
    
    def get_total_health(self) -> int:
        """Points de vie totaux (base + équipements)"""
        return self.health + self.get_equipment_bonus('health')
    
    def get_stats_summary(self) -> Dict[str, Dict[str, int]]:
        """Retourne un résumé des stats : base, bonus, total"""
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
    
    def get_equipment_names(self) -> List[str]:
        """Retourne la liste des noms d'équipements"""
        return [item.name for item in self.equipped_items]
    
    def has_ranged_weapon(self) -> bool:
        """Vérifie si le personnage a une arme à distance"""
        ranged_weapons = ['Arc long', 'Arbalète légère', 'Dagues jumelles']
        return any(item.name in ranged_weapons for item in self.equipped_items)
    
    # === NOUVELLES MÉTHODES - SYSTÈME DE CAPACITÉS ===
    
    def add_abilities(self, abilities: List[Ability]):
        """
        Ajoute les capacités du personnage
        
        Args:
            abilities: Liste des capacités à ajouter
        """
        self.abilities = abilities
        
        # S'assurer qu'au moins la capacité 1 est débloquée
        if abilities and 1 not in self.unlocked_abilities:
            self.unlock_ability(1)
    
    def get_ability_manager(self) -> AbilityManager:
        """
        Retourne un gestionnaire pour les capacités
        
        Returns:
            AbilityManager: Gestionnaire des capacités
        """
        return AbilityManager(self.abilities)
    
    def unlock_ability(self, ability_number: int) -> bool:
        """
        Débloque une capacité
        
        Args:
            ability_number: Numéro de la capacité (1-6)
            
        Returns:
            bool: True si débloquée avec succès
        """
        if not (1 <= ability_number <= 6):
            return False
        
        if ability_number in self.unlocked_abilities:
            return True  # Déjà débloquée
        
        # Vérifie que les capacités précédentes sont débloquées
        for i in range(1, ability_number):
            if i not in self.unlocked_abilities:
                return False  # Capacité précédente manquante
        
        self.unlocked_abilities.append(ability_number)
        
        # Met à jour l'état de la capacité correspondante
        for ability in self.abilities:
            if ability.ability_number == ability_number:
                ability.is_unlocked = True
                ability.reset_combat_uses()
                ability.reset_daily_uses()
                break
        
        return True
    
    def get_ability_by_number(self, number: int) -> Optional[Ability]:
        """
        Récupère une capacité par son numéro
        
        Args:
            number: Numéro de la capacité
            
        Returns:
            Optional[Ability]: Capacité trouvée ou None
        """
        for ability in self.abilities:
            if ability.ability_number == number:
                return ability
        return None
    
    def get_unlocked_abilities(self) -> List[Ability]:
        """
        Retourne les capacités débloquées
        
        Returns:
            List[Ability]: Capacités débloquées
        """
        return [ability for ability in self.abilities if ability.is_unlocked]
    
    def get_available_abilities(self) -> List[Ability]:
        """
        Retourne les capacités utilisables actuellement
        
        Returns:
            List[Ability]: Capacités utilisables
        """
        available = []
        current_spells = self.current_spells if self.current_spells is not None else self.get_total_spells()
        
        for ability in self.get_unlocked_abilities():
            can_use, _ = ability.can_use(current_spells)
            if can_use:
                available.append(ability)
        
        return available
    
    def can_use_ability(self, ability: Ability) -> tuple[bool, str]:
        """
        Vérifie si une capacité peut être utilisée
        
        Args:
            ability: Capacité à vérifier
            
        Returns:
            tuple[bool, str]: (peut_utiliser, raison)
        """
        if not ability.is_unlocked:
            return False, "Capacité non débloquée"
        
        current_spells = self.current_spells if self.current_spells is not None else self.get_total_spells()
        return ability.can_use(current_spells)
    
    def use_ability(self, ability: Ability, target=None) -> AbilityAction:
        """
        Utilise une capacité en combat
        
        Args:
            ability: Capacité à utiliser
            target: Cible de la capacité (optionnel)
            
        Returns:
            AbilityAction: Résultat de l'action
        """
        # Création de l'action
        action = AbilityAction(
            ability_id=ability.unique_id,
            ability_name=ability.name,
            user_name=self.name,
            prevents_attack=ability.prevents_attack
        )
        
        # Vérifications préalables
        can_use, reason = self.can_use_ability(ability)
        if not can_use:
            action.add_effect(f"Échec: {reason}")
            return action
        
        # Consommation des ressources
        if ability.spell_cost > 0:
            current_spells = self.current_spells if self.current_spells is not None else self.get_total_spells()
            self.current_spells = current_spells - ability.spell_cost
            self.spells_used += ability.spell_cost
            action.spell_cost_paid = ability.spell_cost
        
        # Consommation des utilisations
        if not ability.use_ability():
            action.add_effect("Échec: Plus d'utilisations disponibles")
            return action
        
        # Mise à jour de l'état du tour
        self.ability_used_this_turn = ability
        if ability.prevents_attack:
            self.action_taken_this_turn = True
            self.can_attack_this_turn = False
        
        # Succès
        action.success = True
        action.add_effect(f"Capacité {ability.name} utilisée avec succès")
        
        if ability.spell_cost > 0:
            action.add_effect(f"Coût: {ability.spell_cost} sorts")
        
        return action
    
    def can_attack_after_ability(self, ability: Ability) -> bool:
        """
        Vérifie si le personnage peut attaquer après avoir utilisé cette capacité
        
        Args:
            ability: Capacité utilisée
            
        Returns:
            bool: True si peut attaquer après
        """
        return ability.ability_type == AbilityType.PHYSICAL
    
    def reset_turn_state(self):
        """Remet l'état du tour à zéro"""
        self.action_taken_this_turn = False
        self.ability_used_this_turn = None
        self.can_attack_this_turn = True
    
    def start_new_combat(self):
        """Prépare le personnage pour un nouveau combat"""
        self.reset_turn_state()
        
        # Initialise les ressources de combat
        if self.initial_health is None:
            self.initial_health = self.current_health
        if self.initial_spells is None:
            self.initial_spells = self.get_total_spells()
        if self.current_spells is None:
            self.current_spells = self.initial_spells
        
        self.spells_used = 0
        
        # Reset des utilisations par combat pour toutes les capacités
        for ability in self.abilities:
            ability.reset_combat_uses()
    
    def rest(self):
        """Effectue un repos - récupère sorts et utilisations quotidiennes"""
        # Récupération des sorts
        self.current_spells = self.get_total_spells()
        self.spells_used = 0
        
        # Reset des utilisations quotidiennes
        for ability in self.abilities:
            ability.reset_daily_uses()
        
        # Reset de l'état du tour
        self.reset_turn_state()
    
    def get_abilities_summary(self) -> Dict[str, int]:
        """
        Retourne un résumé des capacités
        
        Returns:
            Dict[str, int]: Statistiques des capacités
        """
        total = len(self.abilities)
        unlocked = len(self.unlocked_abilities)
        available = len(self.get_available_abilities())
        
        return {
            'total_abilities': total,
            'unlocked_abilities': unlocked,
            'available_abilities': available,
            'locked_abilities': total - unlocked
        }
    
    def get_combat_status(self) -> Dict[str, any]:
        """
        Retourne l'état de combat du personnage
        
        Returns:
            Dict[str, any]: État de combat complet
        """
        current_spells = self.current_spells if self.current_spells is not None else self.get_total_spells()
        max_spells = self.get_total_spells()
        
        return {
            'health': {
                'current': self.current_health,
                'max': self.get_total_health(),
                'percentage': round((self.current_health / self.get_total_health()) * 100, 1)
            },
            'spells': {
                'current': current_spells,
                'max': max_spells,
                'used': self.spells_used
            },
            'turn_state': {
                'action_taken': self.action_taken_this_turn,
                'can_attack': self.can_attack_this_turn,
                'ability_used': self.ability_used_this_turn.name if self.ability_used_this_turn else None
            },
            'abilities': self.get_abilities_summary()
        }

class Enemy(BaseModel):
    """Modèle d'un ennemi - INCHANGÉ"""
    code: str
    name: str
    defense: int
    stats_by_players: Dict[int, Dict[str, int]]  # Stats selon nb joueurs
    is_magical: bool = False
    has_magical_damage: bool = False
    current_health: Optional[int] = None
    max_health: Optional[int] = None
    
    def get_stats_for_players(self, player_count: int) -> Dict[str, int]:
        """Retourne les stats pour un nombre de joueurs donné"""
        return self.stats_by_players.get(player_count, self.stats_by_players[4])
    
    def initialize_for_combat(self, player_count: int):
        """Initialise l'ennemi pour un combat"""
        stats = self.get_stats_for_players(player_count)
        self.max_health = stats['health']
        self.current_health = stats['health']
    
    def is_alive(self) -> bool:
        """Vérifie si l'ennemi est vivant"""
        return self.current_health > 0
    
    def take_damage(self, damage: int, player_count: int):
        """Fait subir des dégâts à l'ennemi en tenant compte de sa parade"""
        stats = self.get_stats_for_players(player_count)
        defense_value = stats.get('defense', 0)
        actual_damage = max(1, damage - defense_value)
        self.current_health = max(0, self.current_health - actual_damage)
        return actual_damage

class Equipment(BaseModel):
    """Modèle d'un équipement - INCHANGÉ"""
    code: str
    name: str
    type: str = "accessoire"
    precision: int = 0
    physical_damage: int = 0
    magical_damage: int = 0
    defense: int = 0
    spells: int = 0
    health: int = 0
    
    def get_total_bonus(self) -> Dict[str, int]:
        """Retourne tous les bonus de l'équipement"""
        return {
            'precision': self.precision,
            'physical_damage': self.physical_damage,
            'magical_damage': self.magical_damage,
            'defense': self.defense,
            'spells': self.spells,
            'health': self.health
        }
    
    def has_bonus(self) -> bool:
        """Vérifie si l'équipement donne des bonus"""
        bonuses = self.get_total_bonus()
        return any(value > 0 for value in bonuses.values())
    
    def get_bonus_description(self) -> str:
        """Retourne une description textuelle des bonus"""
        bonuses = []
        if self.precision > 0:
            bonuses.append(f"Pré:+{self.precision}")
        if self.physical_damage > 0:
            bonuses.append(f"Dég:+{self.physical_damage}")
        if self.magical_damage > 0:
            bonuses.append(f"Mag:+{self.magical_damage}")
        if self.defense > 0:
            bonuses.append(f"Parade:+{self.defense}")
        if self.spells > 0:
            bonuses.append(f"Sorts:+{self.spells}")
        if self.health > 0:
            bonuses.append(f"PV:+{self.health}")
        
        return " • ".join(bonuses) if bonuses else "Aucun bonus"