"""
Moteur de combat simplifié - MÊME fonctionnalités, code plus simple
Version débutant Python avec TOUTES les features originales
+ CORRECTION code Kraor P-6 → P-4
"""

import random
from typing import List, Dict, Any, Optional
import time

class CombatEngine:
    """Moteur de combat avec toutes les fonctionnalités originales"""
    
    def __init__(self, rules):
        self.rules = rules
        # Support système de capacités
        try:
            from .abilities import Ability, AbilityType, AbilityAction
            self.abilities_enabled = True
        except ImportError:
            self.abilities_enabled = False
    
    def simulate_single_combat(self, heroes: List, enemies: List, player_count: int) -> Dict[str, Any]:
        """Combat principal - Identique à l'original mais plus simple"""
        start_time = time.time()
        log = ["=== DÉBUT DU COMBAT ==="]
        
        # Préparation (copie + initialisation)
        heroes_combat = [hero.model_copy() for hero in heroes]
        enemies_combat = [enemy.model_copy() for enemy in enemies]
        
        self._init_heroes(heroes_combat, log)
        self._init_enemies(enemies_combat, player_count)
        
        self._log_combat_start(heroes_combat, enemies_combat, log)
        
        # Boucle de combat
        for round_num in range(1, self.rules.max_rounds + 1):
            log.append(f"=== ROUND {round_num} ===")
            
            # Tour héros avec capacités
            self._heroes_phase(heroes_combat, enemies_combat, player_count, log)
            if not self._any_alive(enemies_combat):
                log.append(f"🏆 Victoire ! Tous les ennemis vaincus au round {round_num}")
                return self._make_result('heroes', round_num, heroes_combat, enemies_combat, log, start_time)
            
            # Tour ennemis
            self._enemies_phase(enemies_combat, heroes_combat, player_count, log)
            if not self._any_alive(heroes_combat):
                log.append(f"💀 Défaite... Tous les héros tombés au round {round_num}")
                self._apply_defeat_penalties(heroes_combat, log)
                return self._make_result('enemies', round_num, heroes_combat, enemies_combat, log, start_time)
        
        # Match nul (trop de rounds)
        log.append(f"⏱️ Combat interrompu après {self.rules.max_rounds} rounds")
        return self._make_result('draw', self.rules.max_rounds, heroes_combat, enemies_combat, log, start_time)
    
    def _init_heroes(self, heroes: List, log: List[str]):
        """Initialise les héros (PV, sorts, capacités)"""
        for hero in heroes:
            hero.reset_health()
            hero.initial_health = hero.current_health
            hero.initial_spells = hero.get_total_spells()
            hero.current_spells = hero.initial_spells
            hero.spells_used = 0
            
            # Capacités : déblocage + start_combat
            if self.abilities_enabled and hasattr(hero, 'start_new_combat'):
                hero.start_new_combat()
                self._unlock_random_abilities(hero, log)
    
    def _init_enemies(self, enemies: List, player_count: int):
        """Initialise les ennemis"""
        for enemy in enemies:
            enemy.initialize_for_combat(player_count)
    
    def _unlock_random_abilities(self, hero, log: List[str]):
        """Débloque 2-3 capacités aléatoirement (EXCLUSION KRAOR)"""
        if not hasattr(hero, 'abilities') or not hero.abilities:
            return
        
        # CORRECTION: Kraor est P-4, pas P-6
        if hero.code == "P-4":  # Kraor
            allowed_abilities = [2, 4, 5, 6]  # Exclut 1 et 3
        else:
            allowed_abilities = list(range(1, len(hero.abilities) + 1))  # Toutes autorisées
        
        # Filtre selon les capacités disponibles
        available_to_unlock = [i for i in allowed_abilities if i <= len(hero.abilities)]
        
        if not available_to_unlock:
            return
        
        # Nombre à débloquer (2-3) mais limité par les capacités autorisées
        num_to_unlock = random.randint(2, min(3, len(available_to_unlock)))
        
        # Sélection aléatoire des capacités à débloquer
        selected_abilities = random.sample(available_to_unlock, num_to_unlock)
        
        unlocked_names = []
        for ability_num in selected_abilities:
            if hero.unlock_ability(ability_num):
                # Trouve le nom de la capacité
                for ability in hero.abilities:
                    if ability.ability_number == ability_num:
                        unlocked_names.append(ability.name)
                        break
        
        if unlocked_names:
            log.append(f"🔓 {hero.name} débloque: {', '.join(unlocked_names)}")
            if hero.code == "P-4":  # CORRECTION: P-4 au lieu de P-6
                log.append(f"  ⚠️ {hero.name}: Capacités 1 et 3 non autorisées en combat")
    
    def _log_combat_start(self, heroes: List, enemies: List, log: List[str]):
        """Log initial du combat (affichage builds, capacités, stats)"""
        log.append(f"Héros: {', '.join([self._hero_display_name(h) for h in heroes])}")
        log.append(f"Ennemis: {', '.join([e.name for e in enemies])}")
        log.append(f"Règles: {', '.join(self.rules.get_active_rules())}")
        
        # Log capacités
        if self.abilities_enabled:
            log.append("🔮 CAPACITÉS ACTIVÉES")
            for hero in heroes:
                if hasattr(hero, 'abilities') and hero.abilities:
                    unlocked = [a for a in hero.abilities if a.ability_number in hero.unlocked_abilities]
                    if unlocked:
                        log.append(f"• {hero.name}: {', '.join([a.name for a in unlocked])}")
        
        # Log builds équipements
        for hero in heroes:
            if hero.equipped_items:
                build_info = f" ({hero.build_name})" if hero.build_name else ""
                equipment_names = ", ".join([eq.name for eq in hero.equipped_items])
                log.append(f"• {hero.name}{build_info}: {equipment_names}")
                
                stats = hero.get_stats_summary()
                log.append(f"  Stats: Pré:{stats['total']['precision']}, Dég:{stats['total']['damage']}, PV:{stats['total']['health']}")
                if stats['total']['parade'] > 0:
                    log.append(f"  Parade: {stats['total']['parade']}")
        log.append("")
    
    def _heroes_phase(self, heroes: List, enemies: List, player_count: int, log: List[str]):
        """Phase héros avec capacités (identique logique originale)"""
        log.append("🛡️ Phase des Héros")
        
        for hero in [h for h in heroes if h.is_alive()]:
            alive_enemies = [e for e in enemies if e.is_alive()]
            if not alive_enemies:
                break
            
            # Reset état tour
            if self.abilities_enabled and hasattr(hero, 'reset_turn_state'):
                hero.reset_turn_state()
            
            # Capacité + attaque selon règles
            if self.abilities_enabled and hasattr(hero, 'abilities') and hero.abilities:
                ability_used = self._try_hero_ability(hero, alive_enemies, log)
                
                # Attaque si autorisée après capacité
                if hasattr(hero, 'can_attack_this_turn') and hero.can_attack_this_turn:
                    if not hasattr(hero, 'action_taken_this_turn') or not hero.action_taken_this_turn:
                        self._hero_attack(hero, alive_enemies, player_count, log)
                elif ability_used and hasattr(hero, 'can_attack_this_turn') and not hero.can_attack_this_turn:
                    log.append(f"  {hero.name} ne peut pas attaquer (capacité magique utilisée)")
            else:
                # Pas de capacités : attaque classique
                self._hero_attack(hero, alive_enemies, player_count, log)
    
    def _try_hero_ability(self, hero, enemies: List, log: List[str]) -> bool:
        """IA capacités avec EXCLUSION STRICTE Kraor capacités 1 et 3"""
        if not hasattr(hero, 'get_available_abilities'):
            return False
        
        available = hero.get_available_abilities()
        if not available:
            return False
        
        # CORRECTION: Kraor est P-4, pas P-6
        if hero.code == "P-4":  # Kraor
            # Double vérification - l'exclusion est déjà dans get_available_abilities()
            # mais on vérifie encore ici par sécurité
            available = [a for a in available if a.ability_number not in [1, 3]]
            
            if not available:
                log.append(f"  ⚠️ {hero.name}: Aucune capacité de combat disponible")
                return False
        
        # DEBUG : Log détaillé pour Kraor
        if hero.code == "P-4":
            available_info = [(a.ability_number, a.name) for a in available]
            log.append(f"  🔍 {hero.name}: Capacités autorisées {available_info}")
        
        # 1. PV bas < 50% → Soin prioritaire
        health_percent = (hero.current_health / hero.get_total_health()) * 100
        if health_percent < 50:
            healing = [a for a in available if 'soin' in a.name.lower() or 'soigne' in a.description.lower()]
            if healing:
                best_heal = max(healing, key=lambda a: self._heal_power(a))
                return self._use_ability(hero, best_heal, enemies, log)
        
        # 2. Plusieurs ennemis ≥ 3 → Zone
        alive_count = len([e for e in enemies if e.is_alive()])
        if alive_count >= 3:
            aoe = [a for a in available if 'tous les adversaires' in a.description.lower()]
            if aoe:
                best_aoe = max(aoe, key=lambda a: self._damage_power(a))
                if hero.current_spells >= best_aoe.spell_cost:
                    return self._use_ability(hero, best_aoe, enemies, log)
        
        # 3. Offensive standard
        if alive_count > 0:
            offensive = [a for a in available if any(word in a.description.lower() for word in ['dégât', 'inflige', 'attaque'])]
            if offensive:
                cheapest = min(offensive, key=lambda a: a.spell_cost)
                if hero.current_spells >= cheapest.spell_cost:
                    return self._use_ability(hero, cheapest, enemies, log)
        
        # 4. Fallback : première capacité possible (DOUBLE VÉRIFICATION)
        for ability in sorted(available, key=lambda a: a.spell_cost):
            # Triple vérification pour Kraor
            if hero.code == "P-4":
                if ability.ability_number in [1, 3]:
                    continue
                    
            can_use, _ = hero.can_use_ability(ability)
            if can_use:
                return self._use_ability(hero, ability, enemies, log)
        
        return False
    
    def _use_ability(self, hero, ability, enemies: List, log: List[str]) -> bool:
        """Utilise capacité + applique effets (logique identique originale)"""
        can_use, reason = hero.can_use_ability(ability)
        if not can_use:
            return False
        
        action = hero.use_ability(ability)
        if not action.success:
            log.append(f"❌ {hero.name} échec {ability.name}: {getattr(action, 'failure_reason', 'Erreur')}")
            return False
        
        log.append(f"🔮 {hero.name} utilise {ability.name}")
        if action.spell_cost_paid > 0:
            log.append(f"  Coût: {action.spell_cost_paid} sorts, Reste: {hero.current_spells}")
        
        # Effets selon type (même logique que l'original)
        desc = ability.description.lower()
        name = ability.name.lower()
        
        if "soin" in name or "soigne" in desc:
            self._apply_heal(hero, ability, log)
        elif any(word in desc for word in ["dégat", "inflige"]):
            self._apply_damage(hero, ability, enemies, log)
        elif "métamorphose" in name:
            self._apply_transform(hero, ability, log)
        elif any(word in desc for word in ["bouclier", "parade"]):
            self._apply_shield(hero, ability, log)
        else:
            log.append(f"  Effet: {ability.description[:50]}...")
        
        return True
    
    def _apply_heal(self, hero, ability, log: List[str]):
        """Effet soin (même calculs que l'original)"""
        desc = ability.description.lower()
        heal_amount = 8 if "8 blessures" in desc else 4 if "4 blessures" in desc else hero.get_total_health() if "totalité" in desc else 2
        
        actual_heal = hero.heal(heal_amount)
        if actual_heal > 0:
            log.append(f"  💚 {hero.name} récupère {actual_heal} PV")
        else:
            log.append(f"  💚 {hero.name} déjà en pleine santé")
    
    def _apply_damage(self, hero, ability, enemies: List, log: List[str]):
        """Effets dégâts magiques (même logique originale)"""
        desc = ability.description.lower()
        damage = 10 if "10 dégats" in desc else 6 if "6 dégats" in desc else 4 if "4 dégats" in desc else 3
        
        if "tous les adversaires" in desc:
            # Zone
            targets = [e for e in enemies if e.is_alive()]
            log.append(f"  ⚡ Dégâts magiques zone: {damage}")
            for enemy in targets:
                actual = enemy.take_damage(damage, player_count=2)
                log.append(f"    💥 {enemy.name}: {actual} dégâts magiques")
                if not enemy.is_alive():
                    log.append(f"    💀 {enemy.name} vaincu !")
        
        elif "repartis au choix" in desc:
            # Répartis (IA: concentre sur un)
            targets = [e for e in enemies if e.is_alive()]
            if targets:
                target = targets[0]
                actual = target.take_damage(damage, player_count=2)
                log.append(f"  ⚡ {hero.name} concentre {damage} dégâts sur {target.name}: {actual}")
                if not target.is_alive():
                    log.append(f"    💀 {target.name} vaincu !")
        else:
            # Ciblé
            targets = [e for e in enemies if e.is_alive()]
            if targets:
                target = targets[0]
                actual = target.take_damage(damage, player_count=2)
                log.append(f"  ⚡ {target.name} subit {actual} dégâts magiques")
                if not target.is_alive():
                    log.append(f"    💀 {target.name} vaincu !")
    
    def _apply_transform(self, hero, ability, log: List[str]):
        """Métamorphoses"""
        if "ours" in ability.name.lower():
            log.append(f"  🐻 {hero.name} → Ours (défense +)")
        elif "loup" in ability.name.lower():
            log.append(f"  🐺 {hero.name} → Loup (vitesse +)")
        else:
            log.append(f"  🔄 {hero.name} se métamorphose")
    
    def _apply_shield(self, hero, ability, log: List[str]):
        """Boucliers/protections"""
        desc = ability.description.lower()
        if "bouclier de 2" in desc:
            log.append(f"  🛡️ {hero.name} bouclier magique (+2 parade)")
        elif "ignorer" in desc and "blessure" in desc:
            log.append(f"  🛡️ {hero.name} protection active")
        else:
            log.append(f"  🛡️ {hero.name} défense renforcée")
    
    def _hero_attack(self, hero, enemies: List, player_count: int, log: List[str]):
        """Attaque normale héros (avec critiques, dégâts magiques équipement, etc.)"""
        target = enemies[0] if not self.rules.ranged_attacks else random.choice(enemies)
        
        attack_roll = random.randint(1, 20)
        total_attack = attack_roll + hero.get_total_precision()
        
        # Critiques
        if self.rules.criticals:
            if attack_roll == 20:
                damage = hero.get_total_damage() * 2
                actual = target.take_damage(damage, player_count)
                log.append(f"💥 CRITIQUE ! {hero.name} → {target.name}: {actual} dégâts")
                if not target.is_alive():
                    log.append(f"💀 {target.name} vaincu par critique !")
                return
            elif attack_roll == 1:
                log.append(f"💢 ÉCHEC CRITIQUE ! {hero.name} manque complètement")
                return
        
        # Attaque normale
        if total_attack >= target.defense:
            damage = hero.get_total_damage()
            
            # Dégâts magiques équipement
            if self.rules.magical_damage and hero.get_total_magical_damage() > 0:
                damage += hero.get_total_magical_damage()
                log.append(f"{hero.name} dégâts magiques ! (+{hero.get_total_magical_damage()})")
                
                # Coût sort pour attaque magique
                if self.abilities_enabled and hasattr(hero, 'current_spells') and hero.current_spells > 0:
                    hero.current_spells -= 1
                    hero.spells_used += 1
                    log.append(f"  📘 {hero.name}: 1 sort utilisé, reste: {hero.current_spells}")
            
            actual = target.take_damage(damage, player_count)
            precision_display = f"({attack_roll}+{hero.get_total_precision()}={total_attack})"
            log.append(f"{hero.name} → {target.name}: {actual} dégâts {precision_display} vs Déf:{target.defense}")
            
            if not target.is_alive():
                log.append(f"💀 {target.name} vaincu !")
        else:
            log.append(f"{hero.name} manque {target.name} ({total_attack} vs Déf:{target.defense})")
    
    def _enemies_phase(self, enemies: List, heroes: List, player_count: int, log: List[str]):
        """Phase ennemis (identique original)"""
        log.append("👹 Phase des Ennemis")
        
        for enemy in [e for e in enemies if e.is_alive()]:
            alive_heroes = [h for h in heroes if h.is_alive()]
            if not alive_heroes:
                break
            
            target = random.choice(alive_heroes)
            enemy_stats = enemy.get_stats_for_players(player_count)
            damage = enemy_stats['damage']
            
            # Parade héros
            hero_parade = target.get_total_parade()
            actual_damage = max(1, damage - hero_parade)
            target.take_damage(actual_damage)
            
            parade_info = f" (Parade: {hero_parade})" if hero_parade > 0 else ""
            log.append(f"{enemy.name} → {target.name}: {actual_damage} dégâts{parade_info}")
            
            if not target.is_alive():
                log.append(f"💀 {target.name} tombe inconscient !")
    
    def _apply_defeat_penalties(self, heroes: List, log: List[str]):
        """Pénalités défaite totale (identique original)"""
        log.append("💀 DÉFAITE TOTALE - Pénalités")
        for hero in heroes:
            if hasattr(hero, 'current_spells') and hero.current_spells > 0:
                hero.current_spells = max(0, hero.current_spells - 1)
                log.append(f"  📘 {hero.name}: -1 sort (pénalité)")
            
            if hasattr(hero, 'current_health'):
                max_recovery = hero.get_total_health() // 2
                hero.current_health = min(max_recovery, hero.get_total_health())
                log.append(f"  ❤️ {hero.name}: Récupération limitée à {hero.current_health} PV")
    
    def _make_result(self, winner: str, rounds: int, heroes: List, enemies: List, log: List[str], start_time: float) -> Dict[str, Any]:
        """Résultat final avec métriques complètes (format identique)"""
        duration = time.time() - start_time
        heroes_alive = len([h for h in heroes if h.is_alive()])
        enemies_alive = len([e for e in enemies if e.is_alive()])
        
        # Métriques étendues par héros
        extended_metrics = {}
        for hero in heroes:
            hero_metrics = {
                'name': hero.name,
                'final_health': hero.current_health,
                'max_health': hero.get_total_health(),
                'health_lost': hero.get_total_health() - hero.current_health,
                'survival_rate': (hero.current_health / hero.get_total_health()) * 100,
                'final_spells': getattr(hero, 'current_spells', hero.get_total_spells()),
                'max_spells': hero.get_total_spells(),
                'spells_used': getattr(hero, 'spells_used', 0),
                'spell_efficiency': 0
            }
            
            # Métriques capacités
            if self.abilities_enabled and hasattr(hero, 'abilities'):
                hero_metrics.update({
                    'total_abilities': len(hero.abilities),
                    'unlocked_abilities': len(hero.unlocked_abilities) if hasattr(hero, 'unlocked_abilities') else 0,
                    'abilities_used_combat': 0,
                    'magical_abilities': len([a for a in hero.abilities if a.spell_cost > 0]),
                    'physical_abilities': len([a for a in hero.abilities if a.spell_cost == 0])
                })
            
            if hero_metrics['spells_used'] > 0 and winner == 'heroes':
                hero_metrics['spell_efficiency'] = round(100 / hero_metrics['spells_used'], 1)
            
            extended_metrics[hero.code] = hero_metrics
        
        # Adaptation format interface (exactement comme l'original)
        compatible_metrics = self._adapt_for_interface(extended_metrics, heroes)
        
        return {
            'winner': winner,
            'rounds': rounds,
            'duration': round(duration, 2),
            'heroes_alive': heroes_alive,
            'enemies_alive': enemies_alive,
            'log': log,
            'resource_metrics': compatible_metrics,
            'summary': {
                'total_heroes': len(heroes),
                'survival_rate': (heroes_alive / len(heroes)) * 100 if heroes else 0,
                'combat_intensity': 'Élevée' if rounds <= 3 else 'Modérée' if rounds <= 6 else 'Faible',
                'abilities_system_active': self.abilities_enabled
            }
        }
    
    def _adapt_for_interface(self, extended_metrics: Dict, heroes: List) -> Dict[str, Any]:
        """Adaptateur format interface (identique original)"""
        if not extended_metrics:
            return {'total_damage_taken': 0, 'total_spells_used': 0, 'average_damage_per_hero': 0, 'heroes_individual': []}
        
        total_damage = sum(m.get('health_lost', 0) for m in extended_metrics.values())
        total_spells = sum(m.get('spells_used', 0) for m in extended_metrics.values())
        
        heroes_individual = []
        for hero_code, metrics in extended_metrics.items():
            hero = next((h for h in heroes if h.code == hero_code), None)
            
            hero_data = {
                'name': metrics.get('name', 'Héros'),
                'damage_taken': metrics.get('health_lost', 0),
                'spells_used': metrics.get('spells_used', 0),
                'health_remaining': metrics.get('final_health', 0),
                'health_percentage': f"{metrics.get('survival_rate', 0):.0f}",
                'is_alive': metrics.get('final_health', 0) > 0,
                'build': getattr(hero, 'build_name', 'Standard') if hero else 'Standard'
            }
            
            if self.abilities_enabled:
                hero_data.update({
                    'abilities_used': metrics.get('abilities_used_combat', 0),
                    'abilities_available': metrics.get('unlocked_abilities', 0)
                })
            
            heroes_individual.append(hero_data)
        
        return {
            'total_damage_taken': total_damage,
            'total_spells_used': total_spells,
            'average_damage_per_hero': round(total_damage / len(extended_metrics), 1) if extended_metrics else 0,
            'heroes_individual': heroes_individual
        }
    
    # Fonctions utilitaires simples
    def _hero_display_name(self, hero) -> str:
        return f"{hero.name} ({hero.build_name})" if hero.build_name else hero.name
    
    def _any_alive(self, combatants: List) -> bool:
        return any(c.is_alive() for c in combatants)
    
    def _heal_power(self, ability) -> int:
        desc = ability.description.lower()
        return 10 if "totalité" in desc else 8 if "8 blessures" in desc else 4 if "4 blessures" in desc else 2
    
    def _damage_power(self, ability) -> int:
        desc = ability.description.lower()
        return 10 if "10 dégâts" in desc else 6 if "6 dégâts" in desc else 4 if "4 dégâts" in desc else 3

# Fonctions utilitaires exactement comme l'original
def create_combat_engine_with_abilities(rules, enable_abilities: bool = True):
    if hasattr(rules, 'abilities_enabled'):
        rules.abilities_enabled = enable_abilities
    return CombatEngine(rules)

def validate_heroes_for_abilities_combat(heroes: List) -> Dict[str, Any]:
    validation = {'ready': True, 'issues': [], 'heroes_with_abilities': 0, 'total_unlocked_abilities': 0}
    
    for hero in heroes:
        if not hasattr(hero, 'abilities'):
            validation['issues'].append(f"{hero.name}: Pas d'attribut 'abilities'")
            continue
        if not hasattr(hero, 'unlocked_abilities'):
            validation['issues'].append(f"{hero.name}: Pas d'attribut 'unlocked_abilities'")
            continue
        
        if len(hero.abilities) > 0:
            validation['heroes_with_abilities'] += 1
            validation['total_unlocked_abilities'] += len(hero.unlocked_abilities)
    
    if validation['issues']:
        validation['ready'] = False
    return validation

def test_combat_with_abilities():
    print("⚔️ === TEST MOTEUR COMBAT ===")
    try:
        from models.rules_engine import GameRules
        from models.character import Character
        
        rules = GameRules(criticals=True, magical_damage=True, ranged_attacks=False, initiative=False, max_rounds=10)
        hero = Character(code="P-1", name="Test Héros", precision=6, damage=2, spells=3, health=5)
        
        engine = create_combat_engine_with_abilities(rules, enable_abilities=True)
        print(f"✅ Moteur créé avec capacités: {engine.abilities_enabled}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False