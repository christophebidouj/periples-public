"""
Moteur de combat refactorisé pour Périples
VERSION MODULAIRE - Orchestrateur principal utilisant les modules spécialisés
🛡️ Parade = jetons qui se rechargent à chaque tour (héros ET ennemis)
🎯 Ennemis touchent toujours, héros font jets d'attaque
🔮 Gestion centralisée des sorts via SpellManager
🩸 Système potions et capacités intégré
🎭 Support complet des objets spéciaux et Pets
"""

import random
import time
import streamlit as st
from typing import List, Dict, Any

from models.combat.spell_manager import SpellManager
from models.combat.combat_logger import CombatLogger
from models.combat.combat_actions import CombatActions
from models.combat.turn_manager import TurnManager

class CombatEngine:
    """Moteur de combat modulaire avec orchestration centralisée"""
    
    def __init__(self, rules):
        self.rules = rules
        
        # Modules spécialisés
        self.spell_manager = SpellManager()
        self.combat_logger = CombatLogger(self.spell_manager)
        self.combat_actions = CombatActions(self.spell_manager, rules)
        self.turn_manager = TurnManager(self.spell_manager, self.combat_actions)
    
    def simulate_single_combat(self, heroes: List, enemies: List, player_count: int) -> Dict[str, Any]:
        """Combat principal avec système jetons parade + objets spéciaux + Pets + sorts centralisés"""
        start_time = time.time()
        log = ["=== DÉBUT DU COMBAT ==="]
        
        # Préparation
        heroes_combat = [hero.model_copy() for hero in heroes]
        enemies_combat = [enemy.model_copy() for enemy in enemies]
        
        # Stocker les ennemis pour le ciblage tactique
        if 'current_enemies' not in st.session_state:
            st.session_state.current_enemies = []
        st.session_state.current_enemies = enemies_combat
        
        # Liste des Pets invoqués
        active_pets = []
        
        self.combat_logger.prepare_heroes(heroes_combat, log)
        self.combat_logger.prepare_enemies(enemies_combat, player_count, log)
        self.combat_logger.log_start(heroes_combat, enemies_combat, log)
        
        # Combat principal
        for round_num in range(1, self.rules.max_rounds + 1):
            log.append(f"=== ROUND {round_num} ===")
            
            # Status initial du round
            status_line = self.combat_logger.format_status_line(heroes_combat, enemies_combat, active_pets)
            log.append(status_line)
            log.append("")  # Ligne vide pour clarté
            
            # Phase héros + Pets (rechargent parade + agissent)
            self.turn_manager.heroes_turn(heroes_combat, enemies_combat, player_count, log, active_pets)
            if self._check_victory(enemies_combat, "héros", round_num, log):
                return self._make_result('heroes', round_num, heroes_combat, enemies_combat, log, start_time, active_pets)
            
            # Phase ennemis (rechargent parade + attaquent)
            self.turn_manager.enemies_turn(enemies_combat, heroes_combat, player_count, log, active_pets)
            if self._check_victory(heroes_combat + active_pets, "ennemis", round_num, log):
                self._apply_defeat(heroes_combat, log)
                return self._make_result('enemies', round_num, heroes_combat, enemies_combat, log, start_time, active_pets)
        
        # Match nul
        log.append(f"⏱️ Combat trop long ({self.rules.max_rounds} rounds)")
        return self._make_result('draw', self.rules.max_rounds, heroes_combat, enemies_combat, log, start_time, active_pets)
    
    def _check_victory(self, combatants: List, faction: str, round_num: int, log: List[str]) -> bool:
        """Vérifie victoire"""
        if not any(c.is_alive() for c in combatants):
            log.append(f"🏆 Victoire ! Tous les {faction} vaincus au round {round_num}")
            return True
        return False
    
    def _apply_defeat(self, heroes: List, log: List[str]):
        """Pénalités défaite avec gestion CENTRALISÉE"""
        log.append("💀 DÉFAITE - Pénalités appliquées")
        for hero in heroes:
            current_spells = self.spell_manager.get_current_spells(hero)
            if current_spells > 0:
                # Décompte de 1 sort en pénalité
                combatant_id = self.spell_manager.get_combatant_id(hero)
                self.spell_manager.combatant_spells[combatant_id] = max(0, current_spells - 1)
    
    def _make_result(self, winner: str, rounds: int, heroes: List, enemies: List, 
                     log: List[str], start_time: float, active_pets: List = None) -> Dict[str, Any]:
        """Résultat final avec métriques parade + objets spéciaux + Pets + sorts CENTRALISÉS"""
        duration = time.time() - start_time
        active_pets = active_pets or []
        
        # Métriques par héros avec info parade + objets spéciaux + sorts CENTRALISÉS
        heroes_individual = []
        total_damage = 0
        total_spells = 0
        
        for hero in heroes:
            damage_taken = hero.get_total_health() - hero.current_health
            total_damage += damage_taken
            spells_used = self.spell_manager.get_spells_used(hero)
            total_spells += spells_used
            
            # Info parade
            parade_status = hero.get_parade_status() if hasattr(hero, 'get_parade_status') else {
                'current_tokens': 0, 'max_tokens': 0, 'has_parade': False
            }
            
            # Info objets spéciaux
            special_effects = hero.get_special_equipment_effects() if hasattr(hero, 'get_special_equipment_effects') else {}
            active_specials = [name for name, active in special_effects.items() if active]
            
            heroes_individual.append({
                'name': hero.name,
                'damage_taken': damage_taken,
                'spells_used': spells_used,  # CENTRALISÉ
                'spells_remaining': self.spell_manager.get_current_spells(hero),  # CENTRALISÉ
                'health_remaining': hero.current_health,
                'health_percentage': f"{(hero.current_health / hero.get_total_health() * 100):.0f}",
                'is_alive': hero.is_alive(),
                'build': getattr(hero, 'build_name', 'Standard'),
                'parade_tokens_remaining': parade_status['current_tokens'],
                'parade_tokens_max': parade_status['max_tokens'],
                'special_effects': active_specials
            })
        
        # Ajouter les Pets aux métriques individuelles
        if active_pets:
            for pet in active_pets:
                if hasattr(pet, 'display_name'):
                    pet_damage_taken = pet.get_total_health() - pet.current_health
                    total_damage += pet_damage_taken
                    
                    # Parade status pour Pet
                    pet_parade_status = pet.get_parade_status() if hasattr(pet, 'get_parade_status') else {
                        'current_tokens': 0, 'max_tokens': 0, 'has_parade': False
                    }
                    
                    pet_info = {
                        'name': pet.display_name,
                        'damage_taken': pet_damage_taken,
                        'spells_used': self.spell_manager.get_spells_used(pet),  # CENTRALISÉ
                        'spells_remaining': self.spell_manager.get_current_spells(pet),  # CENTRALISÉ
                        'health_remaining': pet.current_health,
                        'health_percentage': f"{(pet.current_health / pet.get_total_health() * 100):.0f}",
                        'is_alive': pet.is_alive(),
                        'build': 'Pet Invoqué',
                        'parade_tokens_remaining': pet_parade_status['current_tokens'],
                        'parade_tokens_max': pet_parade_status['max_tokens'],
                        'special_effects': []  # Pets n'ont pas d'objets spéciaux
                    }
                    heroes_individual.append(pet_info)
        
        # Métriques compatibles interface
        total_combatants = len(heroes) + len(active_pets)
        resource_metrics = {
            'total_damage_taken': total_damage,
            'total_spells_used': total_spells,
            'average_damage_per_hero': round(total_damage / total_combatants, 1) if total_combatants > 0 else 0,
            'heroes_individual': heroes_individual
        }
        
        # Comptage des survivants (héros + pets)
        heroes_alive = len([h for h in heroes if h.is_alive()])
        pets_alive = len([p for p in active_pets if p.is_alive()])
        total_alive = heroes_alive + pets_alive
        
        # Log récapitulatif sorts avec gestion CENTRALISÉE
        heroes_with_spells = [h for h in heroes if self.spell_manager.get_spells_used(h) > 0]
        if heroes_with_spells:
            log.append("=== UTILISATION DES SORTS ===")
            for hero in heroes_with_spells:
                total_spells_max = hero.get_total_spells()
                used = self.spell_manager.get_spells_used(hero)
                remaining = self.spell_manager.get_current_spells(hero)
                log.append(f"🔮 {hero.name}: {used}/{total_spells_max} sorts utilisés ({remaining} restants)")
        
        return {
            'winner': winner,
            'rounds': rounds,
            'duration': round(duration, 2),
            'heroes_alive': total_alive,  # Inclut les Pets
            'enemies_alive': len([e for e in enemies if e.is_alive()]),
            'log': log,
            'resource_metrics': resource_metrics,
            'summary': {
                'total_heroes': len(heroes),
                'total_pets': len(active_pets),
                'survival_rate': (total_alive / total_combatants * 100) if total_combatants > 0 else 0,
                'abilities_system_active': self.combat_logger.abilities_enabled,
                'potions_system_active': any(hasattr(h, 'health_potions') for h in heroes),
                'parade_system_active': True,
                'pets_system_active': len(active_pets) > 0,
                'special_objects_active': any(any(special_effects.values()) for h in heroes 
                                            if hasattr(h, 'get_special_equipment_effects') 
                                            for special_effects in [h.get_special_equipment_effects()]),
                'spells_system_active': any(self.spell_manager.get_spells_used(h) > 0 for h in heroes)
            }
        }

# Fonction utilitaire pour compatibilité
def create_combat_engine_with_abilities(rules, enable_abilities: bool = True):
    """Crée moteur avec capacités, parade, objets spéciaux, Pets et sorts centralisés"""
    if hasattr(rules, 'abilities_enabled'):
        rules.abilities_enabled = enable_abilities
    return CombatEngine(rules)