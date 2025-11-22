"""
Système d'analyse de combat et recommandations d'équilibrage
Collecte les statistiques pendant le combat et génère des recommandations
"""

from typing import Dict, List, Tuple, Optional
from models.character import Character, Enemy
import streamlit as st


class CombatStatsTracker:
    """Collecte les statistiques pendant un combat"""

    def __init__(self):
        self.stats = {
            'start_round': 1,
            'end_round': 1,
            'total_turns': 0,
            'heroes': {},  # {hero_code: hero_stats}
            'enemies': {},  # {enemy_code: enemy_stats}
            'victory': None,  # True/False/None
        }

    def initialize_hero(self, hero: Character):
        """Initialise les stats d'un héros"""
        self.stats['heroes'][hero.code] = {
            'name': hero.name,
            'initial_health': hero.current_health,
            'max_health': hero.get_total_health(),
            'initial_spells': hero.spells,
            'damage_dealt': 0,
            'damage_taken': 0,
            'attacks_made': 0,
            'attacks_hit': 0,
            'criticals': 0,
            'critical_fails': 0,
            'parade_tokens_used': 0,
            'abilities_used': [],
            'potions_used': {'small': 0, 'large': 0},
            'healing_received': 0,
            'spells_spent': 0,
            'final_health': None,
            'survived': None,
            'death_turn': None,
        }

    def initialize_enemy(self, enemy: Enemy):
        """Initialise les stats d'un ennemi"""
        self.stats['enemies'][enemy.code] = {
            'name': enemy.name,
            'initial_health': enemy.current_health,
            'max_health': enemy.max_health,
            'damage_dealt': 0,
            'damage_taken': 0,
            'attacks_made': 0,
            'turns_survived': 0,
            'targets_attacked': {},  # {hero_code: count}
            'final_health': None,
            'survived': None,
            'death_turn': None,
        }

    def record_attack(self, attacker_code: str, is_hero: bool, hit: bool,
                     damage: int, is_critical: bool = False, is_fail: bool = False):
        """Enregistre une attaque"""
        stats_dict = self.stats['heroes'] if is_hero else self.stats['enemies']
        if attacker_code in stats_dict:
            stats_dict[attacker_code]['attacks_made'] += 1
            if hit:
                stats_dict[attacker_code]['attacks_hit'] += 1
                stats_dict[attacker_code]['damage_dealt'] += damage
            if is_critical:
                stats_dict[attacker_code]['criticals'] += 1
            if is_fail:
                stats_dict[attacker_code]['critical_fails'] += 1

    def record_damage_taken(self, target_code: str, is_hero: bool, damage: int):
        """Enregistre des dégâts subis"""
        stats_dict = self.stats['heroes'] if is_hero else self.stats['enemies']
        if target_code in stats_dict:
            stats_dict[target_code]['damage_taken'] += damage

    def record_parade_used(self, hero_code: str):
        """Enregistre l'utilisation d'un jeton de parade"""
        if hero_code in self.stats['heroes']:
            self.stats['heroes'][hero_code]['parade_tokens_used'] += 1

    def record_ability_used(self, hero_code: str, ability_name: str, spell_cost: int):
        """Enregistre l'utilisation d'une capacité"""
        if hero_code in self.stats['heroes']:
            self.stats['heroes'][hero_code]['abilities_used'].append(ability_name)
            self.stats['heroes'][hero_code]['spells_spent'] += spell_cost

    def record_potion_used(self, hero_code: str, potion_type: str, healing: int):
        """Enregistre l'utilisation d'une potion"""
        if hero_code in self.stats['heroes']:
            if potion_type == 'small':
                self.stats['heroes'][hero_code]['potions_used']['small'] += 1
            elif potion_type == 'large':
                self.stats['heroes'][hero_code]['potions_used']['large'] += 1
            self.stats['heroes'][hero_code]['healing_received'] += healing

    def record_healing_received(self, hero_code: str, healing: int):
        """Enregistre des soins reçus (capacités)"""
        if hero_code in self.stats['heroes']:
            self.stats['heroes'][hero_code]['healing_received'] += healing

    def finalize_combat(self, heroes: List[Character], enemies: List[Enemy],
                       current_round: int, victory: bool):
        """Finalise les stats à la fin du combat"""
        self.stats['end_round'] = current_round
        self.stats['victory'] = victory

        # Stats finales héros
        for hero in heroes:
            if hero.code in self.stats['heroes']:
                hero_stats = self.stats['heroes'][hero.code]
                hero_stats['final_health'] = hero.current_health
                hero_stats['survived'] = hero.is_alive()
                if not hero.is_alive() and hero_stats['death_turn'] is None:
                    hero_stats['death_turn'] = current_round

        # Stats finales ennemis
        for enemy in enemies:
            if enemy.code in self.stats['enemies']:
                enemy_stats = self.stats['enemies'][enemy.code]
                enemy_stats['final_health'] = enemy.current_health
                enemy_stats['survived'] = enemy.is_alive()
                if not enemy.is_alive() and enemy_stats['death_turn'] is None:
                    enemy_stats['death_turn'] = current_round


def analyze_combat_results(stats: Dict) -> Dict:
    """Analyse les résultats du combat et retourne des métriques d'équilibrage"""

    heroes_stats = stats['heroes']
    enemies_stats = stats['enemies']

    # Calculs héros
    total_heroes = len(heroes_stats)
    surviving_heroes = sum(1 for h in heroes_stats.values() if h['survived'])
    total_hero_damage = sum(h['damage_dealt'] for h in heroes_stats.values())
    total_hero_damage_taken = sum(h['damage_taken'] for h in heroes_stats.values())

    # PV finaux moyens en %
    avg_hero_hp_percent = 0
    if total_heroes > 0:
        hp_percents = []
        for h in heroes_stats.values():
            if h['final_health'] is not None and h['max_health'] > 0:
                hp_percents.append((h['final_health'] / h['max_health']) * 100)
        avg_hero_hp_percent = sum(hp_percents) / len(hp_percents) if hp_percents else 0

    # Sorts utilisés
    total_spells_initial = sum(h['initial_spells'] for h in heroes_stats.values())
    total_spells_spent = sum(h['spells_spent'] for h in heroes_stats.values())
    spells_usage_percent = (total_spells_spent / total_spells_initial * 100) if total_spells_initial > 0 else 0

    # Potions
    total_small_potions = sum(h['potions_used']['small'] for h in heroes_stats.values())
    total_large_potions = sum(h['potions_used']['large'] for h in heroes_stats.values())

    # Calculs ennemis
    total_enemies = len(enemies_stats)
    surviving_enemies = sum(1 for e in enemies_stats.values() if e['survived'])
    total_enemy_damage = sum(e['damage_dealt'] for e in enemies_stats.values())
    total_enemy_damage_taken = sum(e['damage_taken'] for e in enemies_stats.values())

    # Durée
    combat_duration = stats['end_round'] - stats['start_round'] + 1

    return {
        'duration_rounds': combat_duration,
        'victory': stats['victory'],
        'heroes': {
            'total': total_heroes,
            'surviving': surviving_heroes,
            'survival_rate': (surviving_heroes / total_heroes * 100) if total_heroes > 0 else 0,
            'avg_hp_percent': avg_hero_hp_percent,
            'total_damage_dealt': total_hero_damage,
            'total_damage_taken': total_hero_damage_taken,
            'spells_usage_percent': spells_usage_percent,
            'total_spells_spent': total_spells_spent,
            'small_potions_used': total_small_potions,
            'large_potions_used': total_large_potions,
        },
        'enemies': {
            'total': total_enemies,
            'eliminated': total_enemies - surviving_enemies,
            'total_damage_dealt': total_enemy_damage,
            'total_damage_taken': total_enemy_damage_taken,
        },
        'balance_score': calculate_balance_score(
            stats['victory'], combat_duration, surviving_heroes, total_heroes,
            avg_hero_hp_percent, spells_usage_percent
        )
    }


def calculate_balance_score(victory: bool, duration: int, surviving: int,
                           total: int, avg_hp: float, spells_usage: float) -> float:
    """Calcule un score d'équilibrage de 0 à 10"""

    # Critères idéaux
    IDEAL_DURATION_MIN = 4
    IDEAL_DURATION_MAX = 6
    IDEAL_SURVIVAL_MIN = 60
    IDEAL_SURVIVAL_MAX = 80
    IDEAL_HP_MIN = 40
    IDEAL_HP_MAX = 60
    IDEAL_SPELLS_MIN = 60
    IDEAL_SPELLS_MAX = 80

    score = 10.0

    # Défaite = pénalité importante
    if not victory:
        score -= 5.0

    # Durée
    if duration < IDEAL_DURATION_MIN:
        score -= (IDEAL_DURATION_MIN - duration) * 1.0  # Trop court
    elif duration > IDEAL_DURATION_MAX:
        score -= (duration - IDEAL_DURATION_MAX) * 0.5  # Trop long

    # Survie
    survival_rate = (surviving / total * 100) if total > 0 else 0
    if survival_rate < IDEAL_SURVIVAL_MIN:
        score -= (IDEAL_SURVIVAL_MIN - survival_rate) / 10
    elif survival_rate > IDEAL_SURVIVAL_MAX:
        score -= (survival_rate - IDEAL_SURVIVAL_MAX) / 20

    # PV finaux
    if avg_hp < IDEAL_HP_MIN:
        score -= (IDEAL_HP_MIN - avg_hp) / 10
    elif avg_hp > IDEAL_HP_MAX:
        score -= (avg_hp - IDEAL_HP_MAX) / 20

    # Utilisation sorts
    if spells_usage < IDEAL_SPELLS_MIN:
        score -= (IDEAL_SPELLS_MIN - spells_usage) / 20
    elif spells_usage > IDEAL_SPELLS_MAX:
        score -= (spells_usage - IDEAL_SPELLS_MAX) / 30

    return max(0.0, min(10.0, score))


def generate_balance_recommendations(analysis: Dict, enemies: List[Enemy],
                                     player_count: int) -> List[Dict]:
    """Génère 2 recommandations d'équilibrage basées sur l'analyse"""

    recommendations = []
    victory = analysis['victory']
    duration = analysis['duration_rounds']
    avg_hp = analysis['heroes']['avg_hp_percent']
    survival_rate = analysis['heroes']['survival_rate']

    # Déterminer si le combat était trop facile, difficile, ou équilibré
    if victory:
        if duration <= 3 and avg_hp > 70:
            difficulty = 'too_easy'
        else:
            difficulty = 'balanced_hard'  # Victoire normale
    else:
        difficulty = 'too_hard'

    # === OPTION 1 : Ajuster stats ennemis ===
    if difficulty == 'too_easy':
        # Combat trop facile → Augmenter stats
        hp_increase = calculate_stat_adjustment(duration, avg_hp, 'increase', 'hp')
        dmg_increase = calculate_stat_adjustment(duration, avg_hp, 'increase', 'damage')

        option1 = {
            'type': 'adjust_stats',
            'direction': 'increase',
            'adjustments': [],
            'reason': f"Combat trop rapide ({duration} tours), héros terminent à {avg_hp:.0f}% PV",
            'estimated_duration': duration + 2,
            'estimated_hp': avg_hp - 15,
        }

        for enemy in enemies:
            stats = enemy.get_stats_for_players(player_count)
            option1['adjustments'].append({
                'enemy_code': enemy.code,
                'enemy_name': enemy.name,
                'hp_old': enemy.max_health,
                'hp_new': int(enemy.max_health * (1 + hp_increase)),
                'damage_old': stats['damage'],
                'damage_new': int(stats['damage'] * (1 + dmg_increase)),
            })

        recommendations.append(option1)

    elif difficulty == 'too_hard':
        # Combat trop difficile → Réduire stats OU retirer ennemi
        hp_decrease = calculate_stat_adjustment(duration, avg_hp, 'decrease', 'hp')
        dmg_decrease = calculate_stat_adjustment(duration, avg_hp, 'decrease', 'damage')

        # Option 1: Réduire stats
        option1 = {
            'type': 'adjust_stats',
            'direction': 'decrease',
            'adjustments': [],
            'reason': f"Défaite rapide, héros submergés",
            'estimated_duration': min(duration + 2, 6),
            'estimated_hp': min(avg_hp + 20, 60),
        }

        for enemy in enemies:
            stats = enemy.get_stats_for_players(player_count)
            option1['adjustments'].append({
                'enemy_code': enemy.code,
                'enemy_name': enemy.name,
                'hp_old': enemy.max_health,
                'hp_new': max(5, int(enemy.max_health * (1 - hp_decrease))),
                'damage_old': stats['damage'],
                'damage_new': max(1, int(stats['damage'] * (1 - dmg_decrease))),
            })

        recommendations.append(option1)

        # Option 2: Retirer un ennemi (uniquement en cas de défaite)
        if len(enemies) > 1:
            # Retirer l'ennemi le plus fort (le plus de PV)
            strongest = max(enemies, key=lambda e: e.max_health)
            option2 = {
                'type': 'remove_enemy',
                'enemy_code': strongest.code,
                'enemy_name': strongest.name,
                'enemy_hp': strongest.max_health,
                'enemy_damage': strongest.get_stats_for_players(player_count)['damage'],
                'reason': f"Réduire pression en retirant l'ennemi le plus fort",
                'estimated_duration': max(duration - 1, 3),
                'estimated_hp': min(avg_hp + 25, 65),
            }
            recommendations.append(option2)

    else:  # balanced_hard - Victoire normale
        # Combat équilibré mais peut proposer légers ajustements
        if avg_hp < 50:
            # Légère réduction
            option1 = {
                'type': 'adjust_stats',
                'direction': 'decrease',
                'adjustments': [],
                'reason': f"Affiner équilibrage (PV finaux un peu bas: {avg_hp:.0f}%)",
                'estimated_duration': duration,
                'estimated_hp': avg_hp + 10,
            }

            hp_decrease = 0.10
            dmg_decrease = 0.05

            for enemy in enemies:
                stats = enemy.get_stats_for_players(player_count)
                option1['adjustments'].append({
                    'enemy_code': enemy.code,
                    'enemy_name': enemy.name,
                    'hp_old': enemy.max_health,
                    'hp_new': max(5, int(enemy.max_health * 0.90)),
                    'damage_old': stats['damage'],
                    'damage_new': max(1, int(stats['damage'] * 0.95)),
                })

            recommendations.append(option1)

    # Retourner maximum 2 recommandations
    return recommendations[:2]


def calculate_stat_adjustment(duration: int, avg_hp: float,
                              direction: str, stat_type: str) -> float:
    """Calcule le pourcentage d'ajustement nécessaire"""

    IDEAL_DURATION = 5
    IDEAL_HP = 50

    if direction == 'increase':
        # Trop facile → Augmenter
        duration_gap = (IDEAL_DURATION - duration) / IDEAL_DURATION
        hp_gap = (avg_hp - IDEAL_HP) / 100

        if stat_type == 'hp':
            return min(0.50, max(0.20, duration_gap * 0.60 + hp_gap * 0.40))
        else:  # damage
            return min(0.30, max(0.10, duration_gap * 0.40 + hp_gap * 0.30))

    else:  # decrease
        # Trop difficile → Réduire
        duration_gap = (duration - IDEAL_DURATION) / IDEAL_DURATION
        hp_gap = (IDEAL_HP - avg_hp) / 100

        if stat_type == 'hp':
            return min(0.40, max(0.15, hp_gap * 0.50 + duration_gap * 0.30))
        else:  # damage
            return min(0.25, max(0.10, hp_gap * 0.40 + duration_gap * 0.20))
