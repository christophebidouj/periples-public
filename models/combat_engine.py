"""
Moteur de combat mis à jour avec support du système de capacités
VERSION PHASE 4 - Intégration complète des règles de capacités (p.24)
CORRECTIONS : Noms capacités + Déblocage aléatoire + IA basique
"""

import random
from typing import List, Dict, Any, Tuple, Optional
import time
from .character import Character, Enemy
from .rules_engine import GameRules

# Import du système de capacités
try:
    from .abilities import Ability, AbilityType, AbilityAction
    ABILITIES_SYSTEM_AVAILABLE = True
except ImportError:
    try:
        from models.abilities import Ability, AbilityType, AbilityAction
        ABILITIES_SYSTEM_AVAILABLE = True
    except ImportError:
        ABILITIES_SYSTEM_AVAILABLE = False
        print("⚠️ Système de capacités non disponible dans combat_engine")

class CombatEngine:
    """Moteur de simulation de combat avec support complet des capacités"""
    
    def __init__(self, rules: GameRules):
        self.rules = rules
        # NOUVEAU - Support capacités
        self.abilities_enabled = ABILITIES_SYSTEM_AVAILABLE and getattr(rules, 'abilities_enabled', True)
        
    def simulate_single_combat(
        self, 
        heroes: List[Character], 
        enemies: List[Enemy], 
        player_count: int
    ) -> Dict[str, Any]:
        """Simule un combat unique avec log détaillé et support capacités"""
        
        start_time = time.time()
        log = []
        
        # Préparation des combattants (copies pour ne pas modifier les originaux)
        heroes_in_combat = [hero.model_copy() for hero in heroes]
        enemies_in_combat = [enemy.model_copy() for enemy in enemies]
        
        # Initialisation des PV avec équipements et tracking ressources
        for hero in heroes_in_combat:
            hero.reset_health()  # Utilise les PV totaux avec équipements
            # Tracking ressources initial
            hero.initial_health = hero.current_health
            hero.initial_spells = hero.get_total_spells()
            hero.current_spells = hero.initial_spells
            hero.spells_used = 0
            
            # NOUVEAU - Initialisation combat pour capacités + DÉBLOCAGE ALÉATOIRE
            if self.abilities_enabled and hasattr(hero, 'start_new_combat'):
                hero.start_new_combat()
                # CORRECTION - Déblocage de capacités aléatoires
                self._unlock_random_abilities(hero, log)
                
        for enemy in enemies_in_combat:
            enemy.initialize_for_combat(player_count)
        
        log.append("=== DÉBUT DU COMBAT ===")
        log.append(f"Héros: {', '.join([self._get_hero_display_name(h) for h in heroes_in_combat])}")
        log.append(f"Ennemis: {', '.join([e.name for e in enemies_in_combat])}")
        log.append(f"Règles actives: {', '.join(self.rules.get_active_rules())}")
        
        # NOUVEAU - Log des capacités disponibles avec vrais noms
        if self.abilities_enabled:
            log.append("🔮 CAPACITÉS ACTIVÉES")
            for hero in heroes_in_combat:
                if hasattr(hero, 'abilities') and hero.abilities:
                    unlocked_abilities = [a for a in hero.abilities if a.ability_number in hero.unlocked_abilities]
                    if unlocked_abilities:
                        ability_names = [a.name for a in unlocked_abilities]
                        log.append(f"• {hero.name}: {', '.join(ability_names)}")
        
        # Affichage des builds héros (INCHANGÉ)
        for hero in heroes_in_combat:
            if hero.equipped_items:
                equipment_names = ", ".join([eq.name for eq in hero.equipped_items])
                build_info = f" ({hero.build_name})" if hero.build_name else ""
                log.append(f"• {hero.name}{build_info}: {equipment_names}")
                
                stats = hero.get_stats_summary()
                log.append(f"  Stats: Pré:{stats['total']['precision']}, Dég:{stats['total']['damage']}, PV:{stats['total']['health']}")
                if stats['total']['parade'] > 0:
                    log.append(f"  Parade: {stats['total']['parade']}")
        
        log.append("")
        
        # Boucle de combat principale
        round_num = 1
        max_rounds = self.rules.max_rounds
        
        while round_num <= max_rounds:
            log.append(f"=== ROUND {round_num} ===")
            
            # NOUVEAU - Reset des états de tour pour capacités
            if self.abilities_enabled:
                for hero in heroes_in_combat:
                    if hasattr(hero, 'reset_turn_state'):
                        hero.reset_turn_state()
            
            # Configuration initiative (si activée)
            if self.rules.initiative:
                init_info = self._setup_initiative(heroes_in_combat, enemies_in_combat)
                log.append(init_info)
            
            # Phase des héros avec capacités
            alive_heroes = [h for h in heroes_in_combat if h.is_alive()]
            if alive_heroes:
                self._execute_heroes_phase_with_abilities(alive_heroes, enemies_in_combat, player_count, log)
            
            # Vérification victoire héros
            alive_enemies = [e for e in enemies_in_combat if e.is_alive()]
            if not alive_enemies:
                log.append(f"🏆 Victoire ! Tous les ennemis sont vaincus au round {round_num}")
                return self._create_combat_result('heroes', round_num, len(alive_heroes), 0, log, start_time, heroes_in_combat)
            
            # Phase des ennemis
            if alive_enemies:
                self._execute_enemies_phase(alive_enemies, heroes_in_combat, player_count, log)
            
            # Vérification défaite héros
            final_alive_heroes = [h for h in heroes_in_combat if h.is_alive()]
            if not final_alive_heroes:
                log.append(f"💀 Défaite... Tous les héros sont tombés au round {round_num}")
                
                # NOUVEAU - Application des règles de défaite avec capacités
                if self.abilities_enabled:
                    self._apply_defeat_penalties(heroes_in_combat, log)
                
                final_alive_enemies = [e for e in enemies_in_combat if e.is_alive()]
                return self._create_combat_result('enemies', round_num, 0, len(final_alive_enemies), log, start_time, heroes_in_combat)
            
            round_num += 1
        
        # Combat trop long
        log.append(f"⏱️ Combat interrompu après {max_rounds} rounds (match nul)")
        alive_heroes = [h for h in heroes_in_combat if h.is_alive()]
        alive_enemies = [e for e in enemies_in_combat if e.is_alive()]
        
        return self._create_combat_result('draw', max_rounds, len(alive_heroes), len(alive_enemies), log, start_time, heroes_in_combat)
    
    # === CORRECTION 1 : DÉBLOCAGE ALÉATOIRE DES CAPACITÉS ===
    
    def _unlock_random_abilities(self, hero: Character, log: List[str]):
        """
        Débloque aléatoirement 2-3 capacités pour le héros
        
        Args:
            hero: Héros pour qui débloquer les capacités
            log: Journal de combat pour logging
        """
        if not hasattr(hero, 'abilities') or not hero.abilities:
            return
        
        # Nombre aléatoire de capacités à débloquer (2-3)
        num_to_unlock = random.randint(2, 3)
        max_available = min(num_to_unlock, len(hero.abilities))
        
        # Déblocage séquentiel (respecte l'ordre 1→2→3→4→5→6)
        unlocked_count = 0
        for i in range(1, len(hero.abilities) + 1):
            if unlocked_count >= max_available:
                break
            
            if hero.unlock_ability(i):
                unlocked_count += 1
        
        # Log informatif
        if unlocked_count > 0:
            unlocked_names = []
            for ability in hero.abilities:
                if ability.ability_number <= unlocked_count:
                    unlocked_names.append(ability.name)
            
            log.append(f"🔓 {hero.name} débloquer: {', '.join(unlocked_names)}")
    
    # === NOUVELLES MÉTHODES CAPACITÉS ===
    
    def _execute_heroes_phase_with_abilities(self, heroes: List[Character], enemies: List[Enemy], player_count: int, log: List[str]):
        """Exécute la phase d'attaque des héros avec support des capacités"""
        log.append("🛡️ Phase des Héros")
        
        for hero in heroes:
            alive_enemies = [e for e in enemies if e.is_alive()]
            if not alive_enemies:
                break
            
            # NOUVEAU - Gestion du tour avec capacités
            if self.abilities_enabled and hasattr(hero, 'abilities') and hero.abilities:
                self._hero_turn_with_abilities(hero, alive_enemies, player_count, log)
            else:
                # Tour classique sans capacités
                self._hero_turn(hero, alive_enemies, player_count, log)
    
    def _hero_turn_with_abilities(self, hero: Character, enemies: List[Enemy], player_count: int, log: List[str]):
        """
        Gère le tour d'un héros avec possibilité d'utiliser des capacités
        
        Règles importantes (p.24) :
        - Capacité magique (coût > 0) OU attaque par tour
        - Capacité physique (coût = 0) ET attaque possible
        """
        if not enemies:
            return
        
        # Phase 1: Tentative d'utilisation de capacité
        ability_used = self._try_use_hero_ability(hero, enemies, log)
        
        # Phase 2: Attaque normale si autorisée
        if hasattr(hero, 'can_attack_this_turn') and hero.can_attack_this_turn:
            if not hasattr(hero, 'action_taken_this_turn') or not hero.action_taken_this_turn:
                self._hero_attack(hero, enemies, player_count, log)
        elif ability_used and hasattr(hero, 'can_attack_this_turn') and not hero.can_attack_this_turn:
            log.append(f"  {hero.name} ne peut pas attaquer (capacité magique utilisée)")
    
    def _try_use_hero_ability(self, hero: Character, enemies: List[Enemy], log: List[str]) -> bool:
        """
        Tente d'utiliser une capacité du héros avec IA BASIQUE LOGIQUE
        
        Returns:
            bool: True si une capacité a été utilisée
        """
        if not hasattr(hero, 'get_available_abilities'):
            return False
        
        available_abilities = hero.get_available_abilities()
        if not available_abilities:
            return False
        
        # === IA BASIQUE LOGIQUE ===
        
        # 1. PV bas (< 50%) → Priorité soin
        health_percentage = (hero.current_health / hero.get_total_health()) * 100
        if health_percentage < 50:
            healing_abilities = [
                a for a in available_abilities 
                if 'soin' in a.name.lower() or 'soigne' in a.description.lower() or 'guéri' in a.description.lower()
            ]
            if healing_abilities:
                # Utilise le soin le plus puissant disponible
                best_heal = max(healing_abilities, key=lambda a: self._estimate_heal_power(a))
                return self._use_ability_with_effects(hero, best_heal, enemies, log)
        
        # 2. Plusieurs ennemis (> 2) → Capacités de zone
        alive_enemies_count = len([e for e in enemies if e.is_alive()])
        if alive_enemies_count >= 3:
            aoe_abilities = [
                a for a in available_abilities
                if 'tous les adversaires' in a.description.lower() or 'tous les ennemis' in a.description.lower()
            ]
            if aoe_abilities:
                # Utilise l'attaque de zone la plus puissante
                best_aoe = max(aoe_abilities, key=lambda a: self._estimate_damage_power(a))
                if hero.current_spells >= best_aoe.spell_cost:
                    return self._use_ability_with_effects(hero, best_aoe, enemies, log)
        
        # 3. Capacités offensives si ennemis présents
        if alive_enemies_count > 0:
            offensive_abilities = [
                a for a in available_abilities
                if 'dégât' in a.description.lower() or 'inflige' in a.description.lower() or 'attaque' in a.description.lower()
            ]
            if offensive_abilities:
                # Utilise l'attaque la moins chère
                cheapest_offensive = min(offensive_abilities, key=lambda a: a.spell_cost)
                if hero.current_spells >= cheapest_offensive.spell_cost:
                    return self._use_ability_with_effects(hero, cheapest_offensive, enemies, log)
        
        # 4. Fallback : capacité la moins chère disponible
        available_abilities.sort(key=lambda a: a.spell_cost)
        for ability in available_abilities:
            can_use, reason = hero.can_use_ability(ability)
            if can_use:
                return self._use_ability_with_effects(hero, ability, enemies, log)
        
        return False
    
    def _estimate_heal_power(self, ability: Ability) -> int:
        """Estime la puissance de soin d'une capacité"""
        description = ability.description.lower()
        if "8 blessures" in description or "8" in description:
            return 8
        elif "4 blessures" in description or "4" in description:
            return 4
        elif "totalité" in description:
            return 10  # Considéré comme très puissant
        else:
            return 2  # Défaut
    
    def _estimate_damage_power(self, ability: Ability) -> int:
        """Estime la puissance d'attaque d'une capacité"""
        description = ability.description.lower()
        if "6 dégâts" in description or "6" in description:
            return 6
        elif "4 dégâts" in description or "4" in description:
            return 4
        elif "10 dégâts" in description or "10" in description:
            return 10
        else:
            return 3  # Défaut
    
    def _use_ability_with_effects(self, hero: Character, ability: Ability, enemies: List[Enemy], log: List[str]) -> bool:
        """
        Utilise une capacité et applique ses effets
        
        Returns:
            bool: True si la capacité a été utilisée avec succès
        """
        can_use, reason = hero.can_use_ability(ability)
        if not can_use:
            return False
        
        # Utilisation de la capacité
        action = hero.use_ability(ability)
        
        if action.success:
            # CORRECTION 2 : UTILISE LE VRAI NOM DE LA CAPACITÉ
            log.append(f"🔮 {hero.name} utilise {ability.name}")  # ✅ VRAI NOM au lieu de "Atucan 1"
            
            if action.spell_cost_paid > 0:
                log.append(f"  Coût: {action.spell_cost_paid} sorts, Sorts restants: {hero.current_spells}")
            
            # Application des effets selon le type de capacité
            self._apply_ability_effects(hero, ability, enemies, action, log)
            
            return True
        else:
            log.append(f"❌ {hero.name} échec utilisation {ability.name}: {getattr(action, 'failure_reason', 'Raison inconnue')}")
            return False
    
    def _apply_ability_effects(self, caster: Character, ability: Ability, enemies: List[Enemy], action: AbilityAction, log: List[str]):
        """
        Applique les effets d'une capacité (version simplifiée)
        
        Note: Cette version contient une logique basique.
        Une version complète nécessiterait un système d'effets plus sophistiqué.
        """
        # Effets basés sur le nom/description de la capacité
        # TODO: Implémenter un système d'effets plus robuste
        
        ability_name = ability.name.lower()
        description = ability.description.lower()
        
        # Détection des effets communs
        if "soin" in ability_name or "soigne" in description:
            self._apply_healing_effect(caster, ability, log)
        
        elif "dégat" in description or "inflige" in description:
            self._apply_damage_effect(caster, ability, enemies, log)
        
        elif "métamorphose" in ability_name:
            self._apply_transformation_effect(caster, ability, log)
        
        elif "bouclier" in description or "parade" in description:
            self._apply_shield_effect(caster, ability, log)
        
        else:
            log.append(f"  Effet: {ability.description[:50]}...")
    
    def _apply_healing_effect(self, caster: Character, ability: Ability, log: List[str]):
        """Applique un effet de soin"""
        # Analyse de la description pour déterminer la puissance
        description = ability.description.lower()
        
        if "4 blessures" in description:
            heal_amount = 4
        elif "8 blessures" in description:
            heal_amount = 8
        elif "totalité" in description:
            heal_amount = caster.get_total_health()  # Soin complet
        else:
            heal_amount = 2  # Défaut
        
        old_health = caster.current_health
        actual_heal = caster.heal(heal_amount)  # CORRECTION : Utilise la nouvelle méthode heal()
        
        if actual_heal > 0:
            log.append(f"  💚 {caster.name} récupère {actual_heal} PV")
        else:
            log.append(f"  💚 {caster.name} est déjà en pleine santé")
    
    def _apply_damage_effect(self, caster: Character, ability: Ability, enemies: List[Enemy], log: List[str]):
        """Applique un effet de dégâts magiques"""
        description = ability.description.lower()
        
        # Analyse de la puissance des dégâts
        if "4 dégats" in description:
            damage = 4
        elif "6 dégats" in description:
            damage = 6
        elif "10 dégats" in description:
            damage = 10
        else:
            damage = 3  # Défaut
        
        # Analyse du ciblage
        if "tous les adversaires" in description:
            # Attaque de zone
            targets = [e for e in enemies if e.is_alive()]
            log.append(f"  ⚡ Dégâts magiques à tous les ennemis: {damage}")
            
            for enemy in targets:
                actual_damage = enemy.take_damage(damage, player_count=2)  # Les dégâts magiques ignorent la parade
                log.append(f"    💥 {enemy.name}: {actual_damage} dégâts magiques")
                if not enemy.is_alive():
                    log.append(f"    💀 {enemy.name} est vaincu !")
        
        elif "repartis au choix" in description:
            # Dégâts répartis (IA simple: concentre sur un ennemi)
            targets = [e for e in enemies if e.is_alive()]
            if targets:
                target = targets[0]  # IA simple
                actual_damage = target.take_damage(damage, player_count=2)
                log.append(f"  ⚡ {caster.name} concentre {damage} dégâts magiques sur {target.name}: {actual_damage}")
                if not target.is_alive():
                    log.append(f"    💀 {target.name} est vaincu !")
        
        else:
            # Attaque ciblée sur un ennemi
            targets = [e for e in enemies if e.is_alive()]
            if targets:
                target = targets[0]  # IA simple: premier ennemi
                actual_damage = target.take_damage(damage, player_count=2)
                log.append(f"  ⚡ {target.name} subit {actual_damage} dégâts magiques")
                if not target.is_alive():
                    log.append(f"    💀 {target.name} est vaincu !")
    
    def _apply_transformation_effect(self, caster: Character, ability: Ability, log: List[str]):
        """Applique un effet de métamorphose"""
        if "ours" in ability.name.lower():
            log.append(f"  🐻 {caster.name} se transforme en Ours (défense renforcée)")
            # TODO: Appliquer bonus défense temporaire
        elif "loup" in ability.name.lower():
            log.append(f"  🐺 {caster.name} se transforme en Loup (vitesse renforcée)")
            # TODO: Appliquer bonus vitesse/dégâts temporaire
        else:
            log.append(f"  🔄 {caster.name} se métamorphose")
    
    def _apply_shield_effect(self, caster: Character, ability: Ability, log: List[str]):
        """Applique un effet de bouclier/protection"""
        description = ability.description.lower()
        
        if "bouclier de 2" in description:
            log.append(f"  🛡️ {caster.name} crée un bouclier magique (+2 parade)")
            # TODO: Appliquer bonus parade temporaire
        elif "ignorer" in description and "blessure" in description:
            log.append(f"  🛡️ {caster.name} active une protection")
        else:
            log.append(f"  🛡️ {caster.name} renforce sa défense")
    
    def _apply_defeat_penalties(self, heroes: List[Character], log: List[str]):
        """
        Applique les pénalités de défaite totale selon les règles (p.18)
        
        Règles:
        - Si tous inconscients → coût 1 cube bleu par héros
        - Récupération de 50% des PV seulement
        """
        log.append("💀 DÉFAITE TOTALE - Application des pénalités")
        
        for hero in heroes:
            # Pénalité ressources
            if hasattr(hero, 'current_spells') and hero.current_spells > 0:
                penalty = 1
                hero.current_spells = max(0, hero.current_spells - penalty)
                log.append(f"  📘 {hero.name}: -{penalty} sort (pénalité défaite)")
            
            # Récupération limitée à 50% des PV
            if hasattr(hero, 'current_health'):
                max_recovery = hero.get_total_health() // 2
                hero.current_health = min(max_recovery, hero.get_total_health())
                log.append(f"  ❤️ {hero.name}: Récupération limitée à {hero.current_health} PV")
    
    # === MÉTHODES EXISTANTES MISES À JOUR ===
    
    def _hero_turn(self, hero: Character, enemies: List[Enemy], player_count: int, log: List[str]):
        """Gère le tour d'un héros SANS capacités (méthode classique)"""
        self._hero_attack(hero, enemies, player_count, log)
    
    def _hero_attack(self, hero: Character, enemies: List[Enemy], player_count: int, log: List[str]):
        """Exécute une attaque normale du héros"""
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
            
            # NOUVEAU - Décompte sorts si attaque magique équipée
            if self.abilities_enabled and hero.get_total_magical_damage() > 0:
                if hasattr(hero, 'current_spells') and hero.current_spells > 0:
                    hero.current_spells -= 1
                    hero.spells_used += 1
                    log.append(f"  📘 {hero.name}: 1 sort utilisé (attaque magique), reste: {hero.current_spells}")
            
            if not target.is_alive():
                log.append(f"💀 {target.name} est vaincu !")
        else:
            precision_display = f"({total_attack} vs Déf:{target.defense})"
            log.append(f"{hero.name} manque {target.name} {precision_display}")
    
    # === MÉTHODES EXISTANTES INCHANGÉES ===
    
    def _get_hero_display_name(self, hero: Character) -> str:
        """Retourne le nom d'affichage du héros avec son build"""
        if hero.build_name:
            return f"{hero.name} ({hero.build_name})"
        return hero.name
    
    def _setup_initiative(self, heroes: List[Character], enemies: List[Enemy]) -> str:
        """Configure l'ordre d'initiative aléatoire"""
        return "Initiative: Ordre classique (héros puis ennemis)"
    
    def _execute_enemies_phase(self, enemies: List[Enemy], heroes: List[Character], player_count: int, log: List[str]):
        """Exécute la phase d'attaque des ennemis (INCHANGÉE)"""
        log.append("👹 Phase des Ennemis")
        
        for enemy in enemies:
            alive_heroes = [h for h in heroes if h.is_alive()]
            if not alive_heroes:
                break
            self._enemy_turn(enemy, alive_heroes, player_count, log)
    
    def _enemy_turn(self, enemy: Enemy, heroes: List[Character], player_count: int, log: List[str]):
        """Gère le tour d'un ennemi avec support de la parade des héros (INCHANGÉE)"""
        if not heroes:
            return
        
        # Sélection de la cible
        target = self._select_hero_target(heroes, enemy, player_count)
        enemy_stats = enemy.get_stats_for_players(player_count)
        damage = enemy_stats['damage']
        
        # Application de la parade du héros équipé
        hero_parade = target.get_total_parade()
        actual_damage = max(1, damage - hero_parade)
        
        target.take_damage(actual_damage)
        
        parade_info = f" (Parade héros: {hero_parade})" if hero_parade > 0 else ""
        log.append(f"{enemy.name} attaque {target.name} → {actual_damage} dégâts{parade_info}")
        
        if not target.is_alive():
            log.append(f"💀 {target.name} tombe inconscient !")
    
    def _select_target(self, enemies: List[Enemy], ranged_mode: bool, attacker: Character) -> Enemy:
        """Sélectionne une cible ennemie (INCHANGÉE)"""
        alive_enemies = [e for e in enemies if e.is_alive()]
        if not alive_enemies:
            return None
        
        if ranged_mode:
            return random.choice(alive_enemies)
        else:
            return alive_enemies[0]
    
    def _select_hero_target(self, heroes: List[Character], attacker: Enemy, player_count: int) -> Character:
        """Sélectionne un héros cible (INCHANGÉE)"""
        alive_heroes = [h for h in heroes if h.is_alive()]
        if not alive_heroes:
            return None
        
        return random.choice(alive_heroes)
    
    def _handle_critical(self, roll: int, attacker: Character, target: Enemy, player_count: int, log: List[str]) -> Optional[bool]:
        """Gère les coups critiques (INCHANGÉE)"""
        if roll == 20:
            damage = attacker.get_total_damage() * 2
            actual_damage = target.take_damage(damage, player_count)
            log.append(f"💥 CRITIQUE ! {attacker.name} inflige {actual_damage} dégâts à {target.name}")
            
            if not target.is_alive():
                log.append(f"💀 {target.name} est vaincu par le critique !")
            return True
        elif roll == 1:
            log.append(f"💢 ÉCHEC CRITIQUE ! {attacker.name} manque complètement")
            return True
        
        return None
    
    # === CORRECTION BUG : ADAPTATEUR MÉTRIQUES ===
    
    def _create_combat_result(self, winner: str, rounds: int, heroes_alive: int, enemies_alive: int, 
                            log: List[str], start_time: float, heroes: List[Character]) -> Dict[str, Any]:
        """Crée le résultat de combat avec métriques étendues COMPATIBLES avec l'interface"""
        
        duration = time.time() - start_time
        
        # === NOUVEAU FORMAT ÉTENDU (avec capacités) ===
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
            
            # NOUVEAU - Métriques capacités
            if self.abilities_enabled and hasattr(hero, 'abilities'):
                abilities_metrics = {
                    'total_abilities': len(hero.abilities),
                    'unlocked_abilities': len(hero.unlocked_abilities) if hasattr(hero, 'unlocked_abilities') else 0,
                    'abilities_used_combat': 0,  # TODO: Tracker usage
                    'magical_abilities': len([a for a in hero.abilities if a.spell_cost > 0]),
                    'physical_abilities': len([a for a in hero.abilities if a.spell_cost == 0])
                }
                hero_metrics.update(abilities_metrics)
            
            # Calcul efficacité sorts
            if hero_metrics['spells_used'] > 0 and winner == 'heroes':
                hero_metrics['spell_efficiency'] = round(100 / hero_metrics['spells_used'], 1)
            
            extended_metrics[hero.code] = hero_metrics
        
        # === ADAPTATEUR COMPATIBILITÉ - ANCIEN FORMAT INTERFACE ===
        compatible_metrics = self._adapt_metrics_for_interface(extended_metrics, heroes)
        
        return {
            'winner': winner,
            'rounds': rounds,
            'duration': round(duration, 2),
            'heroes_alive': heroes_alive,
            'enemies_alive': enemies_alive,
            'log': log,
            'resource_metrics': compatible_metrics,  # ✅ FORMAT COMPATIBLE
            'summary': {
                'total_heroes': len(heroes),
                'survival_rate': (heroes_alive / len(heroes)) * 100 if heroes else 0,
                'combat_intensity': 'Élevée' if rounds <= 3 else 'Modérée' if rounds <= 6 else 'Faible',
                'abilities_system_active': self.abilities_enabled
            }
        }
    
    def _adapt_metrics_for_interface(self, extended_metrics: Dict, heroes: List[Character]) -> Dict[str, Any]:
        """
        CORRECTION BUG : Adapte les nouvelles métriques au format attendu par l'interface
        
        Convertit le format par héros vers le format global + individuel attendu
        """
        if not extended_metrics:
            # Fallback si pas de métriques
            return {
                'total_damage_taken': 0,
                'total_spells_used': 0,
                'average_damage_per_hero': 0,
                'heroes_individual': []
            }
        
        # === CALCULS GLOBAUX (pour l'interface existante) ===
        total_damage_taken = 0
        total_spells_used = 0
        heroes_individual = []
        
        for hero_code, metrics in extended_metrics.items():
            # Accumulation globale
            total_damage_taken += metrics.get('health_lost', 0)
            total_spells_used += metrics.get('spells_used', 0)
            
            # Héros individuel pour tableau détaillé (FORMAT ATTENDU par combat_components.py)
            hero_individual = {
                'name': metrics.get('name', 'Héros'),
                'damage_taken': metrics.get('health_lost', 0),  # ✅ NOM ATTENDU
                'spells_used': metrics.get('spells_used', 0),
                'health_remaining': metrics.get('final_health', 0),
                'health_percentage': f"{metrics.get('survival_rate', 0):.0f}",
                'is_alive': metrics.get('final_health', 0) > 0,
                'build': 'Standard'  # Défaut
            }
            
            # Récupération du vrai nom de build
            hero = next((h for h in heroes if h.code == hero_code), None)
            if hero and hasattr(hero, 'build_name') and hero.build_name:
                hero_individual['build'] = hero.build_name
            
            # NOUVEAU - Métriques capacités (optionnel)
            if self.abilities_enabled:
                hero_individual.update({
                    'abilities_used': metrics.get('abilities_used_combat', 0),
                    'abilities_available': metrics.get('unlocked_abilities', 0)
                })
            
            heroes_individual.append(hero_individual)
        
        # Calcul moyenne
        hero_count = len(extended_metrics)
        average_damage_per_hero = round(total_damage_taken / hero_count, 1) if hero_count > 0 else 0
        
        # === RETOUR FORMAT COMPATIBLE INTERFACE ===
        return {
            # MÉTRIQUES GLOBALES (attendues par combat_components.py)
            'total_damage_taken': total_damage_taken,           # ✅ CORRIGÉ
            'total_spells_used': total_spells_used,             # ✅ CORRIGÉ
            'average_damage_per_hero': average_damage_per_hero, # ✅ CORRIGÉ
            
            # MÉTRIQUES INDIVIDUELLES (pour tableau détaillé)
            'heroes_individual': heroes_individual              # ✅ FORMAT CORRECT
        }

# === NOUVELLES CLASSES UTILITAIRES ===

class AbilityCombatManager:
    """
    Gestionnaire spécialisé pour les capacités en combat
    Sépare la logique des capacités du moteur principal
    """
    
    def __init__(self, heroes: List[Character]):
        self.heroes = heroes
        self.abilities_log = []
    
    def get_available_actions(self, hero: Character) -> Dict[str, Any]:
        """
        Retourne les actions disponibles pour un héros
        
        Returns:
            Dict contenant les capacités utilisables et l'état d'attaque
        """
        if not hasattr(hero, 'abilities'):
            return {
                'can_attack': True,
                'can_use_abilities': False,
                'available_abilities': [],
                'action_taken': False
            }
        
        available_abilities = hero.get_available_abilities() if hasattr(hero, 'get_available_abilities') else []
        can_attack = getattr(hero, 'can_attack_this_turn', True)
        action_taken = getattr(hero, 'action_taken_this_turn', False)
        
        return {
            'can_attack': can_attack,
            'can_use_abilities': len(available_abilities) > 0,
            'available_abilities': available_abilities,
            'action_taken': action_taken,
            'current_spells': getattr(hero, 'current_spells', hero.spells)
        }
    
    def simulate_ai_decision(self, hero: Character, enemies: List[Enemy]) -> Dict[str, Any]:
        """
        IA simple pour décider de l'action du héros
        
        Returns:
            Dict avec la décision (ability ou attack)
        """
        actions = self.get_available_actions(hero)
        
        if not actions['can_use_abilities']:
            return {'type': 'attack', 'reason': 'Aucune capacité disponible'}
        
        # IA basique: préfère les capacités de soin si PV bas
        if hero.current_health <= hero.get_total_health() // 2:
            healing_abilities = [
                a for a in actions['available_abilities'] 
                if 'soin' in a.name.lower() or 'soigne' in a.description.lower()
            ]
            if healing_abilities:
                return {
                    'type': 'ability',
                    'ability': healing_abilities[0],
                    'reason': 'PV bas, priorité soin'
                }
        
        # IA basique: utilise capacités d'attaque si plusieurs ennemis
        if len([e for e in enemies if e.is_alive()]) > 2:
            aoe_abilities = [
                a for a in actions['available_abilities']
                if 'tous les adversaires' in a.description.lower()
            ]
            if aoe_abilities and hero.current_spells >= aoe_abilities[0].spell_cost:
                return {
                    'type': 'ability',
                    'ability': aoe_abilities[0],
                    'reason': 'Plusieurs ennemis, attaque de zone'
                }
        
        # Défaut: attaque normale
        return {'type': 'attack', 'reason': 'Stratégie conservatrice'}

# === FONCTIONS UTILITAIRES ===

def create_combat_engine_with_abilities(rules: GameRules, enable_abilities: bool = True) -> CombatEngine:
    """
    Crée un moteur de combat avec le système de capacités
    
    Args:
        rules: Règles de jeu
        enable_abilities: Active/désactive les capacités
        
    Returns:
        CombatEngine configuré
    """
    # Mise à jour des règles pour inclure les capacités
    if hasattr(rules, 'abilities_enabled'):
        rules.abilities_enabled = enable_abilities and ABILITIES_SYSTEM_AVAILABLE
    
    return CombatEngine(rules)

def validate_heroes_for_abilities_combat(heroes: List[Character]) -> Dict[str, Any]:
    """
    Valide que les héros sont prêts pour un combat avec capacités
    
    Returns:
        Dict avec le statut de validation
    """
    validation = {
        'ready': True,
        'issues': [],
        'heroes_with_abilities': 0,
        'total_unlocked_abilities': 0
    }
    
    for hero in heroes:
        # Vérification des attributs capacités
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

# === FONCTION DE TEST ===

def test_combat_with_abilities():
    """Test du moteur de combat avec capacités"""
    print("⚔️ === TEST MOTEUR COMBAT AVEC CAPACITÉS ===")
    print("===========================================")
    
    if not ABILITIES_SYSTEM_AVAILABLE:
        print("❌ Système de capacités non disponible")
        return False
    
    try:
        from models.rules_engine import GameRules
        from models.character import Character
        from models.abilities import Ability
        
        # Création règles de test
        rules = GameRules(
            criticals=True,
            magical_damage=True,
            ranged_attacks=False,
            initiative=False,
            max_rounds=10
        )
        
        # Héros de test avec capacité
        hero = Character(
            code="P-1",
            name="Elneha Test",
            precision=6,
            damage=2,
            spells=3,
            health=5
        )
        
        # Ajout d'une capacité de test
        test_ability = Ability(
            hero_code="P-1",
            ability_number=1,
            name="Soin Test",
            spell_cost=1,
            description="Soigne 4 blessures"
        )
        
        hero.add_abilities([test_ability])
        
        print(f"✅ Héros créé: {hero.name}")
        print(f"   - Capacités: {len(hero.abilities)}")
        print(f"   - Débloquées: {len(hero.unlocked_abilities)}")
        
        # Validation
        validation = validate_heroes_for_abilities_combat([hero])
        print(f"\n📊 Validation héros:")
        print(f"   - Prêt: {validation['ready']}")
        print(f"   - Héros avec capacités: {validation['heroes_with_abilities']}")
        print(f"   - Capacités débloquées: {validation['total_unlocked_abilities']}")
        
        if validation['issues']:
            print(f"   - Problèmes: {validation['issues']}")
        
        # Test création moteur
        engine = create_combat_engine_with_abilities(rules, enable_abilities=True)
        print(f"✅ Moteur de combat créé avec capacités: {engine.abilities_enabled}")
        
        print(f"\n🎯 MOTEUR PRÊT POUR INTÉGRATION COMPLÈTE !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test moteur: {e}")
        return False

if __name__ == "__main__":
    test_combat_with_abilities()