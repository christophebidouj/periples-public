from pydantic import BaseModel
from typing import List, Dict, Optional

class Character(BaseModel):
    """Modèle d'un personnage héros"""
    code: str
    name: str
    precision: int
    damage: int
    spells: int
    health: int
    current_health: Optional[int] = None
    
    # Nouveaux champs pour équipements
    equipped_items: List['Equipment'] = []
    build_name: Optional[str] = None
    
    # AJOUT - Champs pour tracking ressources en combat
    initial_health: Optional[int] = None
    initial_spells: Optional[int] = None
    current_spells: Optional[int] = None
    spells_used: int = 0
    
    def model_post_init(self, __context):
        """Initialise les PV actuels si non définis"""
        if self.current_health is None:
            self.current_health = self.health
    
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
        """Parade totale (équipements uniquement) - RENOMMÉ pour cohérence"""
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
                'parade': 0  # CORRIGÉ: defense → parade
            },
            'bonus': {
                'precision': self.get_equipment_bonus('precision'),
                'damage': self.get_equipment_bonus('physical_damage'),
                'magical_damage': self.get_equipment_bonus('magical_damage'),
                'parade': self.get_equipment_bonus('defense'),  # CORRIGÉ: defense → parade
                'spells': self.get_equipment_bonus('spells'),
                'health': self.get_equipment_bonus('health')
            },
            'total': {
                'precision': self.get_total_precision(),
                'damage': self.get_total_damage(),
                'magical_damage': self.get_total_magical_damage(),
                'parade': self.get_total_parade(),  # CORRIGÉ: defense → parade + nouvelle méthode
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

class Enemy(BaseModel):
    """Modèle d'un ennemi"""
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
    """Modèle d'un équipement"""
    code: str
    name: str
    type: str = "accessoire"  # AJOUT - Type d'équipement (arme/armure/accessoire)
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
            bonuses.append(f"Parade:+{self.defense}")  # CORRIGÉ: Déf → Parade
        if self.spells > 0:
            bonuses.append(f"Sorts:+{self.spells}")
        if self.health > 0:
            bonuses.append(f"PV:+{self.health}")
        
        return " • ".join(bonuses) if bonuses else "Aucun bonus"