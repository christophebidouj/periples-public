"""
Moteur de combat corrigé pour Périples
VERSION AVEC SYSTÈME JETONS PARADE RECHARGEABLE
🛡️ Parade = jetons qui se rechargent à chaque tour (héros ET ennemis)
🎯 Ennemis touchent toujours, héros font jets d'attaque
🩸 Système potions et capacités intégré
"""

import random
import time
import streamlit as st
from typing import List, Dict, Any

def safe_randint(min_val: int, max_val: int) -> int:
    """Version sécurisée de randint qui évite les crashes"""
    if min_val >= max_val:
        return min_val
    return random.randint(min_val, max_val)

class CombatEngine:
    """Moteur de combat avec système jetons parade"""
    
    def __init__(self, rules):
        self.rules = rules
        # Support capacités
        try:
            from .abilities import Ability
            self.abilities_enabled = True
        except ImportError:
            self.abilities_enabled = False
    
    def simulate_single_combat(self, heroes: List, enemies: List, player_count: int) -> Dict[str, Any]:
        """Combat principal avec système jetons parade"""
        start_time = time.time()
        log = ["=== DÉBUT DU COMBAT ==="]
        
        # Préparation
        heroes_combat = [hero.model_copy() for hero in heroes]
        enemies_combat = [enemy.model_copy() for enemy in enemies]
        
        self._prepare_heroes(heroes_combat, log)
        self._prepare_enemies(enemies_combat, player_count, log)
        self._log_start(heroes_combat, enemies_combat, log)
        
        # Combat principal
        for round_num in range(1, self.rules.max_rounds + 1):
            log.append(f"=== ROUND {round_num} ===")
            
            # Phase héros (rechargent parade + agissent)
            self._heroes_turn(heroes_combat, enemies_combat, player_count, log)
            if self._check_victory(enemies_combat, "héros", round_num, log):
                return self._make_result('heroes', round_num, heroes_combat, enemies_combat, log, start_time)
            
            # Phase ennemis (rechargent parade + attaquent)
            self._enemies_turn(enemies_combat, heroes_combat, player_count, log)
            if self._check_victory(heroes_combat, "ennemis", round_num, log):
                self._apply_defeat(heroes_combat, log)
                return self._make_result('enemies', round_num, heroes_combat, enemies_combat, log, start_time)
        
        # Match nul
        log.append(f"⏱️ Combat trop long ({self.rules.max_rounds} rounds)")
        return self._make_result('draw', self.rules.max_rounds, heroes_combat, enemies_combat, log, start_time)
    
    def _prepare_heroes(self, heroes: List, log: List[str]):
        """Initialise héros pour combat"""
        for hero in heroes:
            hero.reset_health()
            hero.current_spells = hero.get_total_spells()
            hero.spells_used = 0
            
            # NOUVEAU - Initialise système parade
            hero._update_parade_from_equipment()
            hero.refresh_parade_tokens()
            
            # Capacités avec protection builds custom
            if self.abilities_enabled and hasattr(hero, 'start_new_combat'):
                hero.start_new_combat()
                self._setup_abilities(hero, log)
    
    def _prepare_enemies(self, enemies: List, player_count: int, log: List[str]):
        """Initialise ennemis avec système parade"""
        for enemy in enemies:
            enemy.initialize_for_combat(player_count)
            # Log parade si présente
            if enemy.max_parade_tokens > 0:
                log.append(f"🛡️ {enemy.name} : {enemy.max_parade_tokens} jetons parade")
    
    def _setup_abilities(self, hero, log: List[str]):
        """Configure capacités : custom OU aléatoire - VERSION ANTI-CRASH"""
        if not hasattr(hero, 'abilities') or not hero.abilities:
            return
        
        # === PROTECTION BUILDS CUSTOM ===
        custom_builds = st.session_state.get('custom_builds', {})
        hero_build = custom_builds.get(hero.code, {})
        
        if hero_build.get('abilities_custom', False) and 'abilities' in hero_build:
            # Utilise capacités choisies par l'utilisateur
            custom_abilities = hero_build['abilities']
            unlocked = []
            
            for num in custom_abilities:
                if hero.unlock_ability(num):
                    ability = next((a for a in hero.abilities if a.ability_number == num), None)
                    if ability:
                        unlocked.append(ability.name)
            
            if unlocked:
                log.append(f"🎯 {hero.name} (Custom): {', '.join(unlocked)}")
            return
        
        # === GÉNÉRATION ALÉATOIRE SÉCURISÉE ===
        # Exclusions Kraor (P-4)
        if hero.code == "P-4":
            allowed = [2, 4, 5, 6]  # Pas de 1 et 3 en combat
        else:
            allowed = list(range(1, len(hero.abilities) + 1))
        
        available = [i for i in allowed if i <= len(hero.abilities)]
        if not available:
            return
        
        # CORRECTION ANTI-CRASH : Gestion des cas limites
        max_possible = len(available)
        if max_possible <= 1:
            count = max_possible
        elif max_possible == 2:
            count = 2
        else:
            count = safe_randint(2, min(3, max_possible))
        
        # Sélection sécurisée
        if count >= max_possible:
            selected = available
        else:
            selected = random.sample(available, count)
        
        unlocked = []
        for num in selected:
            if hero.unlock_ability(num):
                ability = next((a for a in hero.abilities if a.ability_number == num), None)
                if ability:
                    unlocked.append(ability.name)
        
        if unlocked:
            log.append(f"🔓 {hero.name} (Aléatoire): {', '.join(unlocked)}")
    
    def _log_start(self, heroes: List, enemies: List, log: List[str]):
        """Log initial avec info parade"""
        log.append(f"Héros: {', '.join([h.name for h in heroes])}")
        log.append(f"Ennemis: {', '.join([e.name for e in enemies])}")
        
        # Info parade
        heroes_with_parade = [h for h in heroes if h.max_parade_tokens > 0]
        if heroes_with_parade:
            parade_info = [f"{h.name}({h.max_parade_tokens}🛡️)" for h in heroes_with_parade]
            log.append(f"Parade héros: {', '.join(parade_info)}")
        
        log.append("")
    
    def _heroes_turn(self, heroes: List, enemies: List, player_count: int, log: List[str]):
        """Phase héros avec recharge parade et capacités"""
        log.append("🛡️ Phase des Héros")
        
        for hero in [h for h in heroes if h.is_alive()]:
            alive_enemies = [e for e in enemies if e.is_alive()]
            if not alive_enemies:
                break
            
            # NOUVEAU - Début tour héros (recharge parade)
            hero.start_hero_turn()
            if hero.max_parade_tokens > 0:
                log.append(f"🔄 {hero.name} recharge {hero.max_parade_tokens} jetons parade")
            
            # Potion d'abord si nécessaire
            self._try_health_potion(hero, log)
            
            # Capacité puis attaque
            ability_used = self._try_ability(hero, alive_enemies, log)
            
            # Attaque si autorisée
            can_attack = not hasattr(hero, 'can_attack_this_turn') or hero.can_attack_this_turn
            if can_attack and not getattr(hero, 'action_taken_this_turn', False):
                self._hero_attack(hero, alive_enemies, player_count, log)
            elif ability_used:
                log.append(f"  {hero.name} ne peut pas attaquer (capacité magique)")
    
    def _enemies_turn(self, enemies: List, heroes: List, player_count: int, log: List[str]):
        """Phase ennemis avec recharge parade - ATTAQUENT L'ÉQUIPE"""
        log.append("👹 Phase des Ennemis")
        
        for enemy in [e for e in enemies if e.is_alive()]:
            alive_heroes = [h for h in heroes if h.is_alive()]
            if not alive_heroes:
                break
            
            # NOUVEAU - Début tour ennemi (recharge parade)
            enemy.start_enemy_turn()
            if enemy.max_parade_tokens > 0:
                log.append(f"🔄 {enemy.name} recharge {enemy.max_parade_tokens} jetons parade")
            
            # RÈGLE OFFICIELLE : Ennemis attaquent l'équipe
            # Les joueurs (via IA) choisissent qui prend les dégâts
            enemy_stats = enemy.get_stats_for_players(player_count)
            damage = enemy_stats['damage']
            
            # Les héros répartissent les dégâts entre eux (IA tactique)
            target = self._heroes_distribute_damage(alive_heroes, damage, enemy.name, log)
            
            # Application dégâts avec système parade
            damage_result = target.apply_damage_with_parade(damage)
            
            # Log détaillé
            log_parts = [f"{enemy.name} attaque l'équipe: {damage} dégâts → {target.name}"]
            
            if damage_result['blocked_by_parade'] > 0:
                log_parts.append(f"({damage_result['blocked_by_parade']} bloqués par parade)")
                log_parts.append(f"{damage_result['health_damage']} aux PV")
            else:
                log_parts.append(f"{damage_result['health_damage']} aux PV")
            
            log.append(' '.join(log_parts))
            
            # Jetons parade restants
            if target.max_parade_tokens > 0:
                log.append(f"  🛡️ {target.name}: {target.current_parade_tokens}/{target.max_parade_tokens} jetons restants")
            
            if not target.is_alive():
                log.append(f"💀 {target.name} tombe !")
    
    def _heroes_distribute_damage(self, heroes: List, damage: int, enemy_name: str, log: List[str]):
        """IA qui simule la décision tactique des JOUEURS pour répartir les dégâts"""
        if len(heroes) == 1:
            return heroes[0]
        
        # Évaluation tactique - simule des joueurs intelligents
        target_scores = []
        
        for hero in heroes:
            score = 0
            health_percent = (hero.current_health / hero.get_total_health()) * 100
            
            # 1. Priorité aux héros les moins blessés (plus de PV)
            score += health_percent * 0.4
            
            # 2. Priorité aux héros avec parade disponible
            if hasattr(hero, 'current_parade_tokens') and hero.current_parade_tokens > 0:
                parade_percent = (hero.current_parade_tokens / hero.max_parade_tokens) * 100
                score += parade_percent * 0.3
            
            # 3. Bonus si le héros a des potions (peut se soigner)
            if hasattr(hero, 'can_use_potion'):
                can_heal, _ = hero.can_use_potion()
                if can_heal:
                    score += 15
            
            # 4. Malus si héros critique (< 25% PV) - éviter de le tuer
            if health_percent < 25:
                score -= 30
            
            # 5. Bonus léger si héros a beaucoup de parade max (tank)
            if hasattr(hero, 'max_parade_tokens') and hero.max_parade_tokens > 2:
                score += 10
            
            target_scores.append((hero, score))
        
        # Les joueurs choisissent le héros avec le meilleur score (le plus apte à encaisser)
        target_scores.sort(key=lambda x: x[1], reverse=True)
        chosen_hero = target_scores[0][0]
        
        return chosen_hero
    
    def _hero_attack(self, hero, enemies: List, player_count: int, log: List[str]):
        """Attaque héros avec jets et système parade"""
        if not enemies:
            return
            
        target = enemies[0]  # Premier ennemi
        
        attack_roll = random.randint(1, 20)
        
        # Critique
        if self.rules.criticals and attack_roll == 20:
            damage = hero.get_total_damage() * 2
            damage_result = target.apply_damage_with_parade(damage)
            
            log.append(f"💥 CRITIQUE ! {hero.name} → {target.name}: {damage} dégâts")
            if damage_result['blocked_by_parade'] > 0:
                log.append(f"  🛡️ {damage_result['blocked_by_parade']} bloqués, {damage_result['health_damage']} aux PV")
            
            if not target.is_alive():
                log.append(f"💀 {target.name} vaincu !")
            return
        
        # Échec critique
        if self.rules.criticals and attack_roll == 1:
            log.append(f"💢 {hero.name} manque complètement")
            return
        
        # Attaque normale
        total_attack = attack_roll + hero.get_total_precision()
        if total_attack >= target.defense:
            damage = hero.get_total_damage()
            damage_result = target.apply_damage_with_parade(damage)
            
            log_parts = [f"{hero.name} → {target.name}: {damage} dégâts"]
            
            if damage_result['blocked_by_parade'] > 0:
                log_parts.append(f"({damage_result['blocked_by_parade']} bloqués)")
                log_parts.append(f"{damage_result['health_damage']} aux PV")
            else:
                log_parts.append(f"{damage_result['health_damage']} aux PV")
            
            log.append(' '.join(log_parts))
            
            # Jetons parade restants
            if target.max_parade_tokens > 0:
                log.append(f"  🛡️ {target.name}: {target.current_parade_tokens}/{target.max_parade_tokens} jetons restants")
            
            if not target.is_alive():
                log.append(f"💀 {target.name} vaincu !")
        else:
            log.append(f"{hero.name} manque {target.name} (attaque: {total_attack} vs défense: {target.defense})")
    
    def _try_health_potion(self, hero, log: List[str]):
        """IA utilise potions intelligemment"""
        if not hasattr(hero, 'use_health_potion'):
            return
        
        # Logique IA : utilise potion si PV < 50%
        health_percent = (hero.current_health / hero.get_total_health()) * 100
        
        if health_percent < 50:
            can_use, _ = hero.can_use_potion()
            if can_use:
                result = hero.use_health_potion()
                if result['success']:
                    log.append(f"🧪 {hero.name} boit une potion : {result['message']}")
    
    def _try_ability(self, hero, enemies: List, log: List[str]) -> bool:
        """IA capacités intelligente"""
        if not hasattr(hero, 'get_available_abilities'):
            return False
        
        available = hero.get_available_abilities()
        if not available:
            return False
        
        # 1. Soin si PV < 50%
        health_percent = (hero.current_health / hero.get_total_health()) * 100
        if health_percent < 50:
            heal_abilities = [a for a in available if 'soin' in a.name.lower()]
            if heal_abilities:
                return self._use_ability(hero, heal_abilities[0], log)
        
        # 2. Zone si 3+ ennemis
        if len(enemies) >= 3:
            aoe_abilities = [a for a in available if 'tous les adversaires' in a.description.lower()]
            if aoe_abilities:
                return self._use_ability(hero, aoe_abilities[0], log)
        
        # 3. Attaque offensive
        offensive = [a for a in available if any(word in a.description.lower() for word in ['dégât', 'inflige'])]
        if offensive:
            return self._use_ability(hero, offensive[0], log)
        
        # 4. Première capacité disponible
        for ability in sorted(available, key=lambda a: a.spell_cost):
            return self._use_ability(hero, ability, log)
        
        return False
    
    def _use_ability(self, hero, ability, log: List[str]) -> bool:
        """Utilise une capacité"""
        action = hero.use_ability(ability)
        if not action.success:
            return False
        
        log.append(f"🔮 {hero.name} utilise {ability.name}")
        if action.spell_cost_paid > 0:
            log.append(f"  Coût: {action.spell_cost_paid} sorts")
        
        # Effets simples selon description
        desc = ability.description.lower()
        
        if "soin" in ability.name.lower():
            heal = 8 if "8 blessures" in desc else 4 if "4 blessures" in desc else 2
            actual = hero.heal(heal)
            if actual > 0:
                log.append(f"  💚 {hero.name} récupère {actual} PV")
        
        elif any(word in desc for word in ["dégât", "inflige"]):
            damage = 6 if "6 dégâts" in desc else 4 if "4 dégâts" in desc else 3
            log.append(f"  ⚡ Dégâts magiques: {damage}")
        
        return True
    
    def _check_victory(self, combatants: List, faction: str, round_num: int, log: List[str]) -> bool:
        """Vérifie victoire"""
        if not any(c.is_alive() for c in combatants):
            log.append(f"🏆 Victoire ! Tous les {faction} vaincus au round {round_num}")
            return True
        return False
    
    def _apply_defeat(self, heroes: List, log: List[str]):
        """Pénalités défaite"""
        log.append("💀 DÉFAITE - Pénalités appliquées")
        for hero in heroes:
            if hasattr(hero, 'current_spells') and hero.current_spells > 0:
                hero.current_spells = max(0, hero.current_spells - 1)
    
    def _make_result(self, winner: str, rounds: int, heroes: List, enemies: List, 
                     log: List[str], start_time: float) -> Dict[str, Any]:
        """Résultat final avec métriques parade"""
        duration = time.time() - start_time
        
        # Métriques par héros avec info parade
        heroes_individual = []
        total_damage = 0
        total_spells = 0
        
        for hero in heroes:
            damage_taken = hero.get_total_health() - hero.current_health
            total_damage += damage_taken
            total_spells += getattr(hero, 'spells_used', 0)
            
            # Info parade
            parade_status = hero.get_parade_status() if hasattr(hero, 'get_parade_status') else {
                'current_tokens': 0, 'max_tokens': 0, 'has_parade': False
            }
            
            heroes_individual.append({
                'name': hero.name,
                'damage_taken': damage_taken,
                'spells_used': getattr(hero, 'spells_used', 0),
                'health_remaining': hero.current_health,
                'health_percentage': f"{(hero.current_health / hero.get_total_health() * 100):.0f}",
                'is_alive': hero.is_alive(),
                'build': getattr(hero, 'build_name', 'Standard'),
                'parade_tokens_remaining': parade_status['current_tokens'],
                'parade_tokens_max': parade_status['max_tokens']
            })
        
        # Métriques compatibles interface
        resource_metrics = {
            'total_damage_taken': total_damage,
            'total_spells_used': total_spells,
            'average_damage_per_hero': round(total_damage / len(heroes), 1) if heroes else 0,
            'heroes_individual': heroes_individual
        }
        
        return {
            'winner': winner,
            'rounds': rounds,
            'duration': round(duration, 2),
            'heroes_alive': len([h for h in heroes if h.is_alive()]),
            'enemies_alive': len([e for e in enemies if e.is_alive()]),
            'log': log,
            'resource_metrics': resource_metrics,
            'summary': {
                'total_heroes': len(heroes),
                'survival_rate': (len([h for h in heroes if h.is_alive()]) / len(heroes)) * 100 if heroes else 0,
                'abilities_system_active': self.abilities_enabled,
                'potions_system_active': any(hasattr(h, 'health_potions') for h in heroes),
                'parade_system_active': True
            }
        }

# Fonctions utilitaires
def create_combat_engine_with_abilities(rules, enable_abilities: bool = True):
    """Crée moteur avec capacités et parade"""
    if hasattr(rules, 'abilities_enabled'):
        rules.abilities_enabled = enable_abilities
    return CombatEngine(rules)