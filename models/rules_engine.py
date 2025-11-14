from pydantic import BaseModel
from typing import List

class GameRules(BaseModel):
    """Configuration des règles de jeu"""
    
    # Règles avancées de combat
    ranged_attacks: bool = False      # Attaques à distance vs corps à corps
    magical_damage: bool = False      # Dégâts magiques ignorent la parade
    criticals: bool = False          # Gestion des critiques (1 et 20)
    initiative: bool = False         # Ordre aléatoire vs ordre fixe
    
    # CORRECTION BUG : Ajout attribut manquant
    max_rounds: int = 20             # Nombre maximum de rounds (évite combats infinis)
    
    # Systèmes avancés (à développer)
    element_system: bool = False     # Système de cubes d'éléments
    capacities: bool = False         # Capacités spéciales des personnages
    
    # NOUVEAU - Support système de capacités
    abilities_enabled: bool = True   # Active/désactive le système de capacités
    
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
        if self.abilities_enabled:
            active.append("Système de capacités")
        
        return active if active else ["Règles de base uniquement"]
    
    def is_advanced_mode(self) -> bool:
        """Vérifie si des règles avancées sont activées"""
        return any([
            self.ranged_attacks,
            self.magical_damage, 
            self.criticals,
            self.initiative,
            self.element_system,
            self.capacities,
            self.abilities_enabled
        ])
    
    def get_difficulty_modifier(self) -> float:
        """Retourne un modificateur de difficulté basé sur les règles actives"""
        modifier = 1.0

        # Les critiques rendent le combat plus imprévisible
        if self.criticals:
            modifier += 0.1

        # L'initiative affecte la difficulté de manière qualitative (ordre aléatoire)
        # mais pas via un modificateur numérique selon les règles officielles

        # Les attaques à distance avantagent généralement les héros
        if self.ranged_attacks:
            modifier -= 0.05

        # Le système de capacités peut faciliter les combats
        if self.abilities_enabled:
            modifier -= 0.1

        return max(0.8, min(1.3, modifier))  # Limité entre 0.8 et 1.3
    
    def get_max_rounds_display(self) -> str:
        """Retourne l'affichage de la limite de rounds"""
        return f"Maximum {self.max_rounds} rounds"