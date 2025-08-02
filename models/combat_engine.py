import random
from typing import List, Dict, Any, Tuple
import time
from .character import Character, Enemy
from .rules_engine import GameRules
from typing import List, Optional

class CombatEngine:
    """Moteur de simulation de combat avec support des équipements"""
    
    def __init__(self, rules: GameRules):
        self.rules = rules
        
    def simulate_single_combat(
        self, 
        heroes: List[Character], 
        enemies: List[Enemy], 
        player_count: int
    ) -> Dict[str, Any]:
        """Simule un combat unique avec log détaillé et support équipements"""
        
        start_time = time.time()
        log = []
        
        # Préparation des combattants (copies pour ne pas modifier les originaux)
        heroes_in_combat = [hero.model_copy() for hero in heroes]
        enemies_in_combat = [enemy.model_copy() for enemy in enemies]
        
        # Initialisation des PV avec équipements et tracking ressources
        for hero in heroes_in_combat:
            hero.reset_health()  # Utilise les PV totaux avec équipements
            # AJOUT : Tracking ressources initial
            hero.initial_health = hero.current_health
            hero.initial_spells = hero.get_total_spells()
            hero.current_spells = hero.initial_spells
            hero.spells_used = 0
            
        for enemy in enemies_in_combat:
            enemy.initialize_for_combat(player_count)
        
        log.append("=== DÉBUT DU COMBAT ===")
        log.append(f"Héros: {', '.join([self._get_hero_display_name(h) for h in heroes_in_combat])}")
        log.append(f"Ennemis: {', '.join([e.name for e in enemies_in_combat])}")
        log.append(f"Règles actives: {', '.join(self.rules.get_active_rules())}")
        
        # Affichage des builds héros
        for hero in heroes_in_combat:
            if hero.equipped_items:
                equipment_names = ", ".join([eq.name for eq in hero.equipped_items])
                build_info = f" ({hero.build_name})" if hero.build_name else ""
                log.append(f"• {hero.name}{build_info}: {equipment_names}")
                
                stats = hero.get_stats_summary()
                log.append(f"  Stats: Pré:{stats['total']['precision']}, Dég:{stats['total']['damage']}, PV:{stats['total']['health']}")
                if stats['total']['parade'] > 0:  # CORRIGÉ: defense → parade
                    log.append(f"  Parade: {stats['total']['parade']}")
                if stats['total']['spells'] > 0:
                    log.append(f"  Sorts disponibles: {stats['total']['spells']}")
        
        round_num = 1
        max_rounds = 50
        
        # Ordre d'initiative si activé
        if self.rules.initiative:
            log.append(self._setup_initiative(heroes_in_combat, enemies_in_combat))
        
        while round_num <= max_rounds:
            alive_heroes = [h for h in heroes_in_combat if h.is_alive()]
            alive_enemies = [e for e in enemies_in_combat if e.is_alive()]
            
            log.append(f"\n--- Round {round_num} ---")
            
            # Phase héros
            self._execute_heroes_phase(alive_heroes, enemies_in_combat, player_count, log)
            
            # CORRECTION BUG : Vérifier victoire après phase héros
            alive_heroes_after = [h for h in heroes_in_combat if h.is_alive()]
            alive_enemies_after = [e for e in enemies_in_combat if e.is_alive()]
            
            # Conditions de victoire après phase héros
            if not alive_heroes_after:
                log.append(f"💀 DÉFAITE ! Tous les héros sont tombés au round {round_num}")
                return self._create_combat_result('enemies', round_num, 0, len(alive_enemies_after), log, start_time, heroes_in_combat)
            
            if not alive_enemies_after:
                log.append(f"🏆 VICTOIRE ! Tous les ennemis sont vaincus au round {round_num}")
                return self._create_combat_result('heroes', round_num, len(alive_heroes_after), 0, log, start_time, heroes_in_combat)
            
            # Phase ennemis (seulement si le combat continue)
            self._execute_enemies_phase(alive_enemies_after, alive_heroes_after, player_count, log)
            
            # Vérification finale après phase ennemis
            final_alive_heroes = [h for h in heroes_in_combat if h.is_alive()]
            final_alive_enemies = [e for e in enemies_in_combat if e.is_alive()]
            
            if not final_alive_heroes:
                log.append(f"💀 DÉFAITE ! Tous les héros sont tombés au round {round_num}")
                return self._create_combat_result('enemies', round_num, 0, len(final_alive_enemies), log, start_time, heroes_in_combat)
            
            round_num += 1
        
        # Combat trop long
        log.append(f"⏱️ Combat interrompu après {max_rounds} rounds (match nul)")
        alive_heroes = [h for h in heroes_in_combat if h.is_alive()]
        alive_enemies = [e for e in enemies_in_combat if e.is_alive()]
        
        return self._create_combat_result('draw', max_rounds, len(alive_heroes), len(alive_enemies), log, start_time, heroes_in_combat)
    
    def _get_hero_display_name(self, hero: Character) -> str:
        """Retourne le nom d'affichage du héros avec son build"""
        if hero.build_name:
            return f"{hero.name} ({hero.build_name})"
        return hero.name
    
    def _setup_initiative(self, heroes: List[Character], enemies: List[Enemy]) -> str:
        """Configure l'ordre d'initiative aléatoire"""
        # Pour l'instant, on garde l'ordre classique mais on pourrait implémenter
        # un vrai système d'initiative ici
        return "Initiative: Ordre classique (héros puis ennemis)"
    
    def _execute_heroes_phase(self, heroes: List[Character], enemies: List[Enemy], player_count: int, log: List[str]):
        """Exécute la phase d'attaque des héros"""
        log.append("🛡️ Phase des Héros")
        
        for hero in heroes:
            alive_enemies = [e for e in enemies if e.is_alive()]
            if not alive_enemies:
                break
            self._hero_turn(hero, alive_enemies, player_count, log)
    
    def _execute_enemies_phase(self, enemies: List[Enemy], heroes: List[Character], player_count: int, log: List[str]):
        """Exécute la phase d'attaque des ennemis"""
        log.append("👹 Phase des Ennemis")
        
        for enemy in enemies:
            alive_heroes = [h for h in heroes if h.is_alive()]
            if not alive_heroes:
                break
            self._enemy_turn(enemy, alive_heroes, player_count, log)
    
    def _hero_turn(self, hero: Character, enemies: List[Enemy], player_count: int, log: List[str]):
        """Gère le tour d'un héros avec stats équipées"""
        if not enemies:
            return
        
        # Choix de la cible selon les règles
        target = self._select_target(enemies, self.rules.ranged_attacks, hero)
        
        # Jet d'attaque avec précision équipée
        attack_roll = random.randint(1, 20)
        total_attack = attack_roll + hero.get_total_precision()
        
        # Gestion des critiques
        if self.rules.criticals:
            critical_result = self._handle_critical(attack_roll, hero, target, player_count, log)
            if critical_result is not None:
                return  # Le critique a été géré
        
        # Test de réussite normal
        if total_attack >= target.defense:
            # Utilisation des dégâts équipés
            damage = hero.get_total_damage()
            
            # Gestion des dégâts magiques si l'équipement en donne
            if self.rules.magical_damage and hero.get_total_magical_damage() > 0:
                damage += hero.get_total_magical_damage()
                log.append(f"{hero.name} utilise des dégâts magiques ! (+{hero.get_total_magical_damage()})")
            
            actual_damage = target.take_damage(damage, player_count)
            precision_display = f"({attack_roll}+{hero.get_total_precision()}={total_attack})"
            log.append(f"{hero.name} attaque {target.name} → {actual_damage} dégâts {precision_display} vs Déf:{target.defense}")
            
            if not target.is_alive():
                log.append(f"💀 {target.name} est vaincu !")
        else:
            precision_display = f"({total_attack} vs Déf:{target.defense})"
            log.append(f"{hero.name} manque {target.name} {precision_display}")
    
    def _enemy_turn(self, enemy: Enemy, heroes: List[Character], player_count: int, log: List[str]):
        """Gère le tour d'un ennemi avec support de la parade des héros"""
        if not heroes:
            return
        
        # Sélection de la cible
        target = self._select_hero_target(heroes, enemy, player_count)
        enemy_stats = enemy.get_stats_for_players(player_count)
        damage = enemy_stats['damage']
        
        # Application de la parade du héros équipé - CORRIGÉ: utilise nouvelle méthode
        hero_parade = target.get_total_parade()
        actual_damage = max(1, damage - hero_parade)
        
        target.take_damage(actual_damage)
        
        parade_info = f" (Parade héros: {hero_parade})" if hero_parade > 0 else ""
        log.append(f"{enemy.name} attaque {target.name} → {actual_damage} dégâts{parade_info}")
        
        if not target.is_alive():
            log.append(f"💀 {target.name} tombe inconscient !")
    
    def _select_target(self, enemies: List[Enemy], ranged_attacks: bool, hero: Character) -> Enemy:
        """Sélectionne une cible selon les règles d'attaque et l'équipement du héros"""
        
        # Vérifier si le héros a une arme à distance
        has_ranged_weapon = hero.has_ranged_weapon() if hasattr(hero, 'has_ranged_weapon') else False
        
        if ranged_attacks or has_ranged_weapon:
            # Attaque à distance : cible libre
            return random.choice(enemies)
        else:
            # Corps à corps : premier ennemi
            return enemies[0]
    
    def _select_hero_target(self, heroes: List[Character], enemy: Enemy, player_count: int) -> Character:
        """Sélectionne un héros cible selon la stratégie de l'ennemi"""
        
        # Stratégie simple : attaquer le héros avec le moins de parade - CORRIGÉ
        if self.rules.ranged_attacks and enemy.has_magical_damage:
            # Les ennemis à distance ciblent le héros le moins paré
            return min(heroes, key=lambda h: h.get_total_parade())
        else:
            # Cible aléatoire parmi les héros
            return random.choice(heroes)
    
    def _handle_critical(self, roll: int, attacker: Character, target: Enemy, player_count: int, log: List[str]) -> Optional[bool]:
        """Gère les jets critiques avec équipements"""
        if roll == 20:
            # Réussite critique : double dégâts (avec équipements)
            log.append(f"⚡ {attacker.name} fait une RÉUSSITE CRITIQUE !")
            critical_damage = attacker.get_total_damage() * 2
            
            # Ajout des dégâts magiques si disponibles
            if self.rules.magical_damage and attacker.get_total_magical_damage() > 0:
                critical_damage += attacker.get_total_magical_damage() * 2
            
            actual_damage = target.take_damage(critical_damage, player_count)
            log.append(f"   → {target.name} subit {actual_damage} dégâts CRITIQUES !")
            
            if not target.is_alive():
                log.append(f"💀 {target.name} est vaincu par le coup critique !")
            return True
            
        elif roll == 1:
            # Échec critique : contre-attaque (la parade du héros s'applique) - CORRIGÉ
            log.append(f"💥 {attacker.name} fait un ÉCHEC CRITIQUE !")
            target_stats = target.get_stats_for_players(player_count)
            counter_damage = max(1, target_stats['damage'] - attacker.get_total_parade())
            attacker.take_damage(counter_damage)
            
            parade_info = f" (Parade: {attacker.get_total_parade()})" if attacker.get_total_parade() > 0 else ""
            log.append(f"   → {target.name} contre-attaque pour {counter_damage} dégâts{parade_info} !")
            
            if not attacker.is_alive():
                log.append(f"💀 {attacker.name} est terrassé par la contre-attaque !")
            return True
        
        return None
    
    def _calculate_resource_metrics(self, heroes_in_combat: List[Character]) -> Dict[str, Any]:
        """
        AJOUT - Calcule les métriques de consommation de ressources PRIMORDIALES
        selon les besoins utilisateur (blessures = critère principal)
        """
        
        metrics = {
            'total_damage_taken': 0,
            'total_spells_used': 0,
            'average_damage_per_hero': 0,
            'difficulty_distribution': {
                'tres_facile': 0,      # 0 blessures
                'normal': 0,           # 1-2 blessures  
                'difficile': 0,        # 3-4 blessures
                'trop_difficile': 0    # 4+ blessures
            },
            'heroes_individual': []
        }
        
        total_damage = 0
        total_spells = 0
        
        for hero in heroes_in_combat:
            # Calcul des dégâts subis (PV initiaux - PV actuels)
            if hasattr(hero, 'initial_health'):
                damage_taken = hero.initial_health - hero.current_health
            else:
                # Fallback si pas de tracking initial
                max_health = hero.get_total_health()
                damage_taken = max_health - hero.current_health
            
            # Calcul des sorts utilisés
            if hasattr(hero, 'spells_used'):
                spells_used = hero.spells_used
            else:
                # Fallback si pas de tracking sorts
                spells_used = max(0, hero.get_total_spells() - getattr(hero, 'current_spells', hero.get_total_spells()))
            
            total_damage += damage_taken
            total_spells += spells_used
            
            # Évaluation difficulté individuelle selon critères utilisateur
            if damage_taken == 0:
                difficulty = "Très facile"
                metrics['difficulty_distribution']['tres_facile'] += 1
            elif damage_taken <= 2:
                difficulty = "Normal" 
                metrics['difficulty_distribution']['normal'] += 1
            elif damage_taken <= 4:
                difficulty = "Difficile"
                metrics['difficulty_distribution']['difficile'] += 1
            else:
                difficulty = "Trop difficile"
                metrics['difficulty_distribution']['trop_difficile'] += 1
            
            # Calcul pourcentage PV restants
            current_health = hero.current_health if hero.is_alive() else 0
            max_health = hero.get_total_health()
            health_percentage = round((current_health / max_health) * 100, 1) if max_health > 0 else 0
            
            # Données individuelles
            hero_metrics = {
                'name': hero.name,
                'build': hero.build_name or "Standard",
                'damage_taken': damage_taken,
                'health_remaining': current_health,
                'health_percentage': health_percentage,
                'spells_used': spells_used,
                'difficulty_assessment': difficulty,
                'is_alive': hero.is_alive()
            }
            
            metrics['heroes_individual'].append(hero_metrics)
        
        # Métriques globales
        heroes_count = len(heroes_in_combat)
        metrics['total_damage_taken'] = total_damage
        metrics['total_spells_used'] = total_spells
        metrics['average_damage_per_hero'] = round(total_damage / heroes_count, 1) if heroes_count > 0 else 0
        
        return metrics
    
    def _create_combat_result(
        self,
        winner: str,
        round_num: int,
        heroes_remaining: int,
        enemies_remaining: int,
        log: List[str],
        start_time: float,
        heroes_in_combat: List[Character]  # AJOUT du paramètre manquant
    ) -> Dict[str, Any]:
        """Construit le dictionnaire de résultat de combat"""
        duration = round(time.time() - start_time, 2)
        return {
            'winner': winner,
            'rounds': round_num,
            'heroes_remaining': heroes_remaining,
            'enemies_remaining': enemies_remaining,
            'log': log,
            'duration': duration,
            'resource_metrics': self._calculate_resource_metrics(heroes_in_combat)  # Maintenant fonctionnel
        }

    def simulate_multiple_combats(
        self, 
        heroes: List[Character], 
        enemies: List[Enemy], 
        player_count: int, 
        combat_count: int = 100
    ) -> Dict[str, Any]:
        """Simule plusieurs combats pour obtenir des statistiques"""
        
        results = []
        hero_wins = 0
        total_rounds = 0
        total_survivors = 0
        
        for i in range(combat_count):
            result = self.simulate_single_combat(heroes, enemies, player_count)
            results.append(result)
            
            if result['winner'] == 'heroes':
                hero_wins += 1
            
            total_rounds += result['rounds']
            total_survivors += result['heroes_remaining']
        
        # Compilation des statistiques
        round_distribution = [r['rounds'] for r in results]
        
        return {
            'stats': {
                'total_combats': combat_count,
                'hero_wins': hero_wins,
                'average_rounds': round(total_rounds / combat_count, 1),
                'average_survivors': round(total_survivors / combat_count, 1)
            },
            'round_distribution': round_distribution,
            'detailed_results': results
        }