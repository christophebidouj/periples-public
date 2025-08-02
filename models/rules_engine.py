from pydantic import BaseModel
from typing import List

class GameRules(BaseModel):
    """Configuration des règles de jeu"""
    
    # Règles avancées de combat
    ranged_attacks: bool = False      # Attaques à distance vs corps à corps
    magical_damage: bool = False      # Dégâts magiques ignorent la parade
    criticals: bool = False          # Gestion des critiques (1 et 20)
    initiative: bool = False         # Ordre aléatoire vs ordre fixe
    
    # Systèmes avancés (à développer)
    element_system: bool = False     # Système de cubes d'éléments
    capacities: bool = False         # Capacités spéciales des personnages
    
    def get_active_rules(self) -> List[str]:
        """Retourne la liste des règles actives"""
        active = []
        if self.ranged_attacks:
            active.append("Attaques à distance")
        if self.magical_damage:
            active.append("Dégâts magiques") 
        if self.criticals:
            active.append("Critiques")
        if self.initiative:
            active.append("Initiative aléatoire")
        if self.element_system:
            active.append("Système d'éléments")
        if self.capacities:
            active.append("Capacités")
        
        return active if active else ["Règles de base uniquement"]
    
    def is_advanced_mode(self) -> bool:
        """Vérifie si des règles avancées sont activées"""
        return any([
            self.ranged_attacks,
            self.magical_damage, 
            self.criticals,
            self.initiative,
            self.element_system,
            self.capacities
        ])
    
    def get_difficulty_modifier(self) -> float:
        """Retourne un modificateur de difficulté basé sur les règles actives"""
        modifier = 1.0
        
        # Les critiques rendent le combat plus imprévisible
        if self.criticals:
            modifier += 0.1
            
        # L'initiative aléatoire peut avantager les ennemis
        if self.initiative:
            modifier += 0.05
            
        # Les attaques à distance avantagent généralement les héros
        if self.ranged_attacks:
            modifier -= 0.05
            
        return max(0.8, min(1.3, modifier))  # Limité entre 0.8 et 1.3