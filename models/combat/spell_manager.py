"""
Gestionnaire centralisé des sorts pour le moteur de combat
Extrait de combat_engine.py pour modularité
"""

class SpellManager:
    """Gestion centralisée des sorts pour tous les combattants"""
    
    def __init__(self):
        self.combatant_spells = {}  # {combatant_id: current_spells}
        self.combatant_spells_used = {}  # {combatant_id: spells_used}
        self.combatant_magic_abilities_this_turn = {}  # {combatant_id: count}
    
    def get_combatant_id(self, combatant) -> str:
        """Génère un ID unique pour le combattant"""
        if hasattr(combatant, 'owner_code'):  # Pet
            return f"{combatant.owner_code}_pet"
        return combatant.code
    
    def initialize_spells(self, combatant):
        """Initialise les sorts d'un combattant"""
        combatant_id = self.get_combatant_id(combatant)
        max_spells = combatant.get_total_spells() if hasattr(combatant, 'get_total_spells') else 0
        
        self.combatant_spells[combatant_id] = max_spells
        self.combatant_spells_used[combatant_id] = 0
        self.combatant_magic_abilities_this_turn[combatant_id] = 0
    
    def get_current_spells(self, combatant) -> int:
        """Retourne les sorts actuels d'un combattant"""
        combatant_id = self.get_combatant_id(combatant)
        return self.combatant_spells.get(combatant_id, 0)
    
    def get_spells_used(self, combatant) -> int:
        """Retourne les sorts utilisés par un combattant"""
        combatant_id = self.get_combatant_id(combatant)
        return self.combatant_spells_used.get(combatant_id, 0)
    
    def can_use_magical_ability(self, combatant, ability) -> tuple[bool, str]:
        """Vérifie si un combattant peut utiliser une capacité magique"""
        spell_cost = getattr(ability, 'spell_cost', 0)
        
        if spell_cost <= 0:
            return True, "Capacité physique"
        
        combatant_id = self.get_combatant_id(combatant)
        
        # Vérification : une seule capacité magique par tour
        magic_used_this_turn = self.combatant_magic_abilities_this_turn.get(combatant_id, 0)
        if magic_used_this_turn > 0:
            return False, "Une capacité magique déjà utilisée ce tour"
        
        # Vérification : sorts disponibles
        current_spells = self.get_current_spells(combatant)
        if current_spells < spell_cost:
            return False, f"Pas assez de sorts ({current_spells}/{spell_cost})"
        
        return True, "Utilisable"
    
    def consume_spells(self, combatant, spell_cost: int) -> bool:
        """Consomme les sorts d'un combattant"""
        if spell_cost <= 0:
            return True
        
        combatant_id = self.get_combatant_id(combatant)
        current_spells = self.get_current_spells(combatant)
        
        if current_spells < spell_cost:
            return False
        
        # Décompte
        self.combatant_spells[combatant_id] = current_spells - spell_cost
        self.combatant_spells_used[combatant_id] = self.combatant_spells_used.get(combatant_id, 0) + spell_cost
        
        # Marquer capacité magique utilisée ce tour
        if spell_cost > 0:
            self.combatant_magic_abilities_this_turn[combatant_id] = self.combatant_magic_abilities_this_turn.get(combatant_id, 0) + 1
        
        return True
    
    def reset_magic_abilities_turn(self, combatant):
        """Reset le compteur de capacités magiques pour un nouveau tour"""
        combatant_id = self.get_combatant_id(combatant)
        self.combatant_magic_abilities_this_turn[combatant_id] = 0