"""
Tracking temps réel des statistiques de combat
Collecte toutes les données nécessaires pour l'analyse d'équilibrage
"""

from typing import Dict, List, Any
from models.character import Character, Enemy
from datetime import datetime


class CombatStatsTracker:
    """
    Collecte les statistiques pendant un combat pour analyse post-combat.
    Utilisé par Sandbox V2 pour générer récapitulatif détaillé.
    """

    def __init__(self):
        """Initialise le tracker avec structure de données vide"""
        self.stats = {
            'start_time': None,
            'end_time': None,
            'start_round': 1,
            'end_round': 1,
            'victory': None,
            'heroes': {},      # {hero_code: hero_stats_dict}
            'enemies': {},     # {enemy_code: enemy_stats_dict}
            'hp_history': {},  # {combatant_id: {turn_number: current_hp}}
            'turn_order': []   # Liste chronologique des tours joués
        }

    def initialize_combat(self, heroes: List[Character], enemies: List[Enemy]):
        """
        Initialise le tracking au début du combat

        Args:
            heroes: Liste des héros participant au combat
            enemies: Liste des ennemis participant au combat
        """
        self.stats['start_time'] = datetime.now()
        self.stats['start_round'] = 1

        # Initialiser stats pour chaque héros
        for hero in heroes:
            self.stats['heroes'][hero.code] = self._create_hero_stats(hero)
            self.stats['hp_history'][f"hero_{hero.code}"] = {}

        # Initialiser stats pour chaque ennemi
        for enemy in enemies:
            self.stats['enemies'][enemy.code] = self._create_enemy_stats(enemy)
            self.stats['hp_history'][f"enemy_{enemy.code}"] = {}

    def _create_hero_stats(self, hero: Character) -> Dict[str, Any]:
        """Crée la structure de stats pour un héros"""
        return {
            'name': hero.name,
            'code': hero.code,
            'initial_health': hero.current_health,
            'max_health': hero.get_total_health(),
            'initial_spells': getattr(hero, 'spells', 0),
            'final_health': None,
            'survived': None,
            'death_turn': None,

            # Dégâts
            'damage_dealt': 0,
            'damage_taken': 0,

            # Attaques
            'attacks_made': 0,
            'attacks_hit': 0,
            'criticals': 0,
            'critical_fails': 0,

            # Défense
            'parade_tokens_used': 0,

            # Capacités
            'abilities_used': [],  # Liste des capacités utilisées
            'abilities_stats': {},  # {ability_name: {attempted: X, succeeded: Y}}
            'spells_spent': 0,

            # Potions
            'potions_used': {'small': 0, 'large': 0},
            'healing_received': 0,

            # Effets (Niveau 1)
            'effects_applied': {
                'stunned': 0,
                'invisible_turns': 0,
                'kraor_marked': 0,
                'damage_buffs_used': 0
            },
            'effects_received': {
                'stunned_turns': 0,
                'dodges_triggered': 0,
                'damage_dodged': 0
            },

            # Tours et kills
            'turns_played': 0,
            'kills': 0,
            'kills_details': []  # Liste des victimes (optionnel)
        }

    def _create_enemy_stats(self, enemy: Enemy) -> Dict[str, Any]:
        """Crée la structure de stats pour un ennemi"""
        return {
            'name': enemy.name,
            'code': enemy.code,
            'initial_health': enemy.current_health,
            'max_health': enemy.max_health,
            'final_health': None,
            'survived': None,
            'death_turn': None,

            # Dégâts
            'damage_dealt': 0,
            'damage_taken': 0,

            # Attaques
            'attacks_made': 0,
            'attacks_hit': 0,

            # Tours
            'turns_played': 0,
            'turns_survived': 0,

            # Effets reçus
            'effects_received': {
                'stunned_turns': 0,
                'kraor_marked_turns': 0
            },

            # Ciblage
            'targets_attacked': {},  # {hero_code: count}
        }

    def record_attack(self, attacker: Character, target: Character,
                     hit: bool, damage: int = 0, is_critical: bool = False,
                     is_fail: bool = False):
        """
        Enregistre une attaque

        Args:
            attacker: Personnage qui attaque
            target: Cible de l'attaque
            hit: True si l'attaque a touché
            damage: Dégâts infligés (si hit=True)
            is_critical: True si coup critique (nat 20)
            is_fail: True si échec critique (nat 1)
        """
        is_hero = isinstance(attacker, Character) and hasattr(attacker, 'abilities')
        stats_dict = self.stats['heroes'] if is_hero else self.stats['enemies']

        attacker_code = attacker.code
        if attacker_code in stats_dict:
            stats_dict[attacker_code]['attacks_made'] += 1

            if hit:
                stats_dict[attacker_code]['attacks_hit'] += 1
                stats_dict[attacker_code]['damage_dealt'] += damage

            if is_critical:
                stats_dict[attacker_code]['criticals'] += 1

            if is_fail and is_hero:
                stats_dict[attacker_code]['critical_fails'] += 1

        # Enregistrer ciblage pour ennemis
        if not is_hero and hasattr(target, 'code'):
            if attacker_code in self.stats['enemies']:
                targets = self.stats['enemies'][attacker_code]['targets_attacked']
                targets[target.code] = targets.get(target.code, 0) + 1

    def record_ability_used(self, caster: Character, ability_name: str,
                           success: bool, spell_cost: int = 0):
        """
        Enregistre l'utilisation d'une capacité

        Args:
            caster: Héros qui utilise la capacité
            ability_name: Nom de la capacité
            success: True si la capacité a réussi
            spell_cost: Coût en sorts de la capacité
        """
        if caster.code in self.stats['heroes']:
            hero_stats = self.stats['heroes'][caster.code]

            # Ajouter à la liste des capacités utilisées
            hero_stats['abilities_used'].append(ability_name)

            # Tracking précision par capacité
            if ability_name not in hero_stats['abilities_stats']:
                hero_stats['abilities_stats'][ability_name] = {
                    'attempted': 0,
                    'succeeded': 0
                }

            hero_stats['abilities_stats'][ability_name]['attempted'] += 1
            if success:
                hero_stats['abilities_stats'][ability_name]['succeeded'] += 1

            # Coût en sorts
            hero_stats['spells_spent'] += spell_cost

    def record_damage_taken(self, target: Character, damage: int, parade_used: int = 0):
        """
        Enregistre des dégâts subis

        Args:
            target: Combattant qui subit les dégâts
            damage: Dégâts réels encaissés (après parade)
            parade_used: Nombre de dégâts absorbés par parade
        """
        is_hero = isinstance(target, Character) and hasattr(target, 'abilities')
        stats_dict = self.stats['heroes'] if is_hero else self.stats['enemies']

        if target.code in stats_dict:
            stats_dict[target.code]['damage_taken'] += damage

            if is_hero and parade_used > 0:
                stats_dict[target.code]['parade_tokens_used'] += 1

    def record_effect_applied(self, caster: Character, effect_type: str, target: Character = None):
        """
        Enregistre un effet de statut appliqué (Niveau 1 tracking)

        Args:
            caster: Personnage qui applique l'effet
            effect_type: Type d'effet ('stunned', 'invisible', 'kraor_marked', 'damage_buff', 'dodge')
            target: Cible de l'effet (si applicable)
        """
        if caster.code in self.stats['heroes']:
            effects = self.stats['heroes'][caster.code]['effects_applied']

            if effect_type == 'stunned':
                effects['stunned'] += 1
            elif effect_type == 'invisible':
                effects['invisible_turns'] += 1
            elif effect_type == 'kraor_marked':
                effects['kraor_marked'] += 1
            elif effect_type == 'damage_buff':
                effects['damage_buffs_used'] += 1

    def record_effect_received(self, target: Character, effect_type: str, value: int = 1):
        """
        Enregistre un effet reçu

        Args:
            target: Combattant qui reçoit l'effet
            effect_type: Type d'effet ('stunned', 'dodge', etc.)
            value: Valeur associée (tours, dégâts évités, etc.)
        """
        is_hero = isinstance(target, Character) and hasattr(target, 'abilities')
        stats_dict = self.stats['heroes'] if is_hero else self.stats['enemies']

        if target.code in stats_dict:
            effects = stats_dict[target.code]['effects_received']

            if effect_type == 'stunned':
                effects['stunned_turns'] += value
            elif effect_type == 'dodge' and is_hero:
                effects['dodges_triggered'] += 1
                effects['damage_dodged'] += value
            elif effect_type == 'kraor_marked' and not is_hero:
                effects['kraor_marked_turns'] += value

    def record_potion_used(self, hero: Character, potion_type: str, healing: int):
        """
        Enregistre l'utilisation d'une potion

        Args:
            hero: Héros qui utilise la potion
            potion_type: 'small' ou 'large'
            healing: PV soignés
        """
        if hero.code in self.stats['heroes']:
            hero_stats = self.stats['heroes'][hero.code]

            if potion_type in ['small', 'large']:
                hero_stats['potions_used'][potion_type] += 1

            hero_stats['healing_received'] += healing

    def record_healing_received(self, hero: Character, healing: int):
        """
        Enregistre des soins reçus (capacités, sorts)

        Args:
            hero: Héros qui reçoit les soins
            healing: PV soignés
        """
        if hero.code in self.stats['heroes']:
            self.stats['heroes'][hero.code]['healing_received'] += healing

    def record_turn_end(self, combatant_id: str, turn_number: int):
        """
        Enregistre la fin du tour d'un combattant

        Args:
            combatant_id: ID du combattant (ex: 'hero_P-1', 'enemy_E-12_0')
            turn_number: Numéro du tour actuel
        """
        # Extraire code du combattant
        parts = combatant_id.split('_')
        if len(parts) >= 2:
            faction = parts[0]  # 'hero' ou 'enemy'

            # Pour les ennemis, l'ID est au format "enemy_CODE_INDEX"
            # Pour les héros, c'est "hero_CODE"
            # On doit extraire CODE sans l'index
            if faction == 'enemy' and len(parts) >= 3:
                # Enlever le dernier élément (index) pour les ennemis
                code = '_'.join(parts[1:-1])
            else:
                # Pour les héros ou format legacy
                code = '_'.join(parts[1:])

            stats_dict = self.stats['heroes'] if faction == 'hero' else self.stats['enemies']

            if code in stats_dict:
                stats_dict[code]['turns_played'] += 1

        # Ajouter à l'historique des tours
        self.stats['turn_order'].append({
            'turn': turn_number,
            'combatant_id': combatant_id
        })

    def snapshot_hp(self, turn_number: int, combatants: List[Dict] = None):
        """
        Prend un snapshot des PV de tous les combattants (pour courbe)

        Args:
            turn_number: Numéro du tour actuel
            combatants: Liste des combattants avec leur état actuel
        """
        if combatants:
            for combatant in combatants:
                char = combatant['character']
                combatant_id = combatant['id']

                if combatant_id in self.stats['hp_history']:
                    self.stats['hp_history'][combatant_id][turn_number] = char.current_health

    def record_kill(self, killer: Character, victim: Character):
        """
        Enregistre un kill

        Args:
            killer: Combattant qui a tué
            victim: Combattant éliminé
        """
        is_hero = isinstance(killer, Character) and hasattr(killer, 'abilities')
        stats_dict = self.stats['heroes'] if is_hero else self.stats['enemies']

        if killer.code in stats_dict:
            stats_dict[killer.code]['kills'] += 1
            stats_dict[killer.code]['kills_details'].append({
                'victim_name': victim.name,
                'victim_code': victim.code
            })

    def finalize_combat(self, victory: bool, end_round: int,
                       heroes: List[Character] = None, enemies: List[Enemy] = None):
        """
        Finalise les stats à la fin du combat

        Args:
            victory: True si les héros ont gagné
            end_round: Numéro du dernier tour
            heroes: Liste finale des héros (optionnel)
            enemies: Liste finale des ennemis (optionnel)
        """
        self.stats['end_time'] = datetime.now()
        self.stats['end_round'] = end_round
        self.stats['victory'] = victory

        # Mettre à jour stats finales des héros
        if heroes:
            for hero in heroes:
                if hero.code in self.stats['heroes']:
                    hero_stats = self.stats['heroes'][hero.code]
                    hero_stats['final_health'] = hero.current_health
                    hero_stats['survived'] = hero.is_alive()
                    if not hero.is_alive() and hero_stats['death_turn'] is None:
                        hero_stats['death_turn'] = end_round

        # Mettre à jour stats finales des ennemis
        if enemies:
            for enemy in enemies:
                if enemy.code in self.stats['enemies']:
                    enemy_stats = self.stats['enemies'][enemy.code]
                    enemy_stats['final_health'] = enemy.current_health
                    enemy_stats['survived'] = enemy.is_alive()
                    enemy_stats['turns_survived'] = enemy_stats['turns_played']
                    if not enemy.is_alive() and enemy_stats['death_turn'] is None:
                        enemy_stats['death_turn'] = end_round

    def get_stats(self) -> Dict:
        """
        Retourne les stats brutes pour analyse

        Returns:
            Dict contenant toutes les statistiques collectées
        """
        return self.stats

    def get_combat_duration(self) -> int:
        """Retourne la durée du combat en nombre de tours"""
        return self.stats['end_round'] - self.stats['start_round'] + 1
