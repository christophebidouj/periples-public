"""
Moteur de combat corrigé pour Périples
VERSION AVEC COMBATENGINE MAÎTRE DES SORTS + SYSTÈME JETONS PARADE RECHARGEABLE + OBJETS SPÉCIAUX + PETS
🛡️ Parade = jetons qui se rechargent à chaque tour (héros ET ennemis)
🎯 Ennemis touchent toujours, héros font jets d'attaque
🔮 NOUVEAU - CombatEngine maître de la gestion des sorts (plus de sorts négatifs)
🩸 Système potions et capacités intégré
🎭 O-4 (Lyre phoenix) : Stèphe attaques → dégâts magiques
🐾 Support complet des Pets invoqués
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
    """Moteur de combat avec gestion centralisée des sorts + système jetons parade + objets spéciaux + Pets"""
    
    def __init__(self, rules):
        self.rules = rules
        # NOUVEAU - Gestion centralisée des sorts
        self.combatant_spells = {}  # {combatant_id: current_spells}
        self.combatant_spells_used = {}  # {combatant_id: spells_used}
        self.combatant_magic_abilities_this_turn = {}  # {combatant_id: count}
        
        # Support capacités
        try:
            from .abilities import Ability
            self.abilities_enabled = True
        except ImportError:
            self.abilities_enabled = False
    
    def simulate_single_combat(self, heroes: List, enemies: List, player_count: int) -> Dict[str, Any]:
        """Combat principal avec système jetons parade + objets spéciaux + Pets + sorts centralisés"""
        start_time = time.time()
        log = ["=== DÉBUT DU COMBAT ==="]
        
        # Préparation
        heroes_combat = [hero.model_copy() for hero in heroes]
        enemies_combat = [enemy.model_copy() for enemy in enemies]
        
        # Liste des Pets invoqués
        active_pets = []
        
        self._prepare_heroes(heroes_combat, log)
        self._prepare_enemies(enemies_combat, player_count, log)
        self._log_start(heroes_combat, enemies_combat, log)
        
        # Combat principal
        for round_num in range(1, self.rules.max_rounds + 1):
            log.append(f"=== ROUND {round_num} ===")
            
            # Phase héros + Pets (rechargent parade + agissent)
            self._heroes_turn(heroes_combat, enemies_combat, player_count, log, active_pets)
            if self._check_victory(enemies_combat, "héros", round_num, log):
                return self._make_result('heroes', round_num, heroes_combat, enemies_combat, log, start_time, active_pets)
            
            # Phase ennemis (rechargent parade + attaquent)
            self._enemies_turn(enemies_combat, heroes_combat, player_count, log, active_pets)
            if self._check_victory(heroes_combat + active_pets, "ennemis", round_num, log):
                self._apply_defeat(heroes_combat, log)
                return self._make_result('enemies', round_num, heroes_combat, enemies_combat, log, start_time, active_pets)
        
        # Match nul
        log.append(f"⏱️ Combat trop long ({self.rules.max_rounds} rounds)")
        return self._make_result('draw', self.rules.max_rounds, heroes_combat, enemies_combat, log, start_time, active_pets)
    
    # === GESTION CENTRALISÉE DES SORTS ===
    
    def _get_combatant_id(self, combatant) -> str:
        """Génère un ID unique pour le combattant"""
        if hasattr(combatant, 'owner_code'):  # Pet
            return f"{combatant.owner_code}_pet"
        return combatant.code
    
    def _initialize_spells(self, combatant):
        """Initialise les sorts d'un combattant"""
        combatant_id = self._get_combatant_id(combatant)
        max_spells = combatant.get_total_spells() if hasattr(combatant, 'get_total_spells') else 0
        
        self.combatant_spells[combatant_id] = max_spells
        self.combatant_spells_used[combatant_id] = 0
        self.combatant_magic_abilities_this_turn[combatant_id] = 0
    
    def _get_current_spells(self, combatant) -> int:
        """Retourne les sorts actuels d'un combattant"""
        combatant_id = self._get_combatant_id(combatant)
        return self.combatant_spells.get(combatant_id, 0)
    
    def _get_spells_used(self, combatant) -> int:
        """Retourne les sorts utilisés par un combattant"""
        combatant_id = self._get_combatant_id(combatant)
        return self.combatant_spells_used.get(combatant_id, 0)
    
    def _can_use_magical_ability(self, combatant, ability) -> tuple[bool, str]:
        """Vérifie si un combattant peut utiliser une capacité magique"""
        spell_cost = getattr(ability, 'spell_cost', 0)
        
        if spell_cost <= 0:
            return True, "Capacité physique"
        
        combatant_id = self._get_combatant_id(combatant)
        
        # Vérification : une seule capacité magique par tour
        magic_used_this_turn = self.combatant_magic_abilities_this_turn.get(combatant_id, 0)
        if magic_used_this_turn > 0:
            return False, "Une capacité magique déjà utilisée ce tour"
        
        # Vérification : sorts disponibles
        current_spells = self._get_current_spells(combatant)
        if current_spells < spell_cost:
            return False, f"Pas assez de sorts ({current_spells}/{spell_cost})"
        
        return True, "Utilisable"
    
    def _consume_spells(self, combatant, spell_cost: int) -> bool:
        """Consomme les sorts d'un combattant"""
        if spell_cost <= 0:
            return True
        
        combatant_id = self._get_combatant_id(combatant)
        current_spells = self._get_current_spells(combatant)
        
        if current_spells < spell_cost:
            return False
        
        # Décompte
        self.combatant_spells[combatant_id] = current_spells - spell_cost
        self.combatant_spells_used[combatant_id] = self.combatant_spells_used.get(combatant_id, 0) + spell_cost
        
        # Marquer capacité magique utilisée ce tour
        if spell_cost > 0:
            self.combatant_magic_abilities_this_turn[combatant_id] = self.combatant_magic_abilities_this_turn.get(combatant_id, 0) + 1
        
        return True
    
    def _reset_magic_abilities_turn(self, combatant):
        """Reset le compteur de capacités magiques pour un nouveau tour"""
        combatant_id = self._get_combatant_id(combatant)
        self.combatant_magic_abilities_this_turn[combatant_id] = 0
    
    def _prepare_heroes(self, heroes: List, log: List[str]):
        """Initialise héros pour combat + détection objets spéciaux + gestion sorts centralisée"""
        for hero in heroes:
            hero.reset_health()
            
            # NOUVEAU - Initialisation centralisée des sorts
            self._initialize_spells(hero)
            
            # Initialise système parade
            hero._update_parade_from_equipment()
            hero.refresh_parade_tokens()
            
            # Log objets spéciaux détectés
            special_effects = hero.get_special_equipment_effects()
            active_effects = [name for name, active in special_effects.items() if active]
            if active_effects:
                log.append(f"✨ {hero.name} - Objets spéciaux: {', '.join(active_effects)}")
            
            # Log sorts disponibles
            current_spells = self._get_current_spells(hero)
            if current_spells > 0:
                log.append(f"🔮 {hero.name} - Sorts disponibles: {current_spells}")
            
            # Capacités avec protection builds custom
            if self.abilities_enabled and hasattr(hero, 'start_new_combat'):
                hero.start_new_combat()
                self._setup_abilities(hero, log)
    
    def _prepare_enemies(self, enemies: List, player_count: int, log: List[str]):
        """Initialise ennemis avec système parade + sorts centralisés"""
        for enemy in enemies:
            enemy.initialize_for_combat(player_count)
            
            # Initialiser sorts pour ennemis (généralement 0)
            self._initialize_spells(enemy)
            
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
        """Log initial avec info parade + objets spéciaux + sorts"""
        log.append(f"Héros: {', '.join([h.name for h in heroes])}")
        log.append(f"Ennemis: {', '.join([e.name for e in enemies])}")
        
        # Info parade
        heroes_with_parade = [h for h in heroes if h.max_parade_tokens > 0]
        if heroes_with_parade:
            parade_info = [f"{h.name}({h.max_parade_tokens}🛡️)" for h in heroes_with_parade]
            log.append(f"Parade héros: {', '.join(parade_info)}")
        
        # Info objets spéciaux
        heroes_with_special = []
        for hero in heroes:
            effects = hero.get_special_equipment_effects()
            active = [name for name, active in effects.items() if active]
            if active:
                # Ajout info formes pour Elneha
                if hero.code == "P-1" and hasattr(hero, 'current_form'):
                    form_info = f"forme:{hero.current_form}"
                    active.append(form_info)
                heroes_with_special.append(f"{hero.name}({','.join(active)})")
        
        if heroes_with_special:
            log.append(f"Objets spéciaux: {', '.join(heroes_with_special)}")
        
        log.append("")
    
    def _heroes_turn(self, heroes: List, enemies: List, player_count: int, log: List[str], active_pets: List):
        """Phase héros + Pets avec recharge parade et capacités"""
        log.append("🛡️ Phase des Héros + Pets")
        
        # Héros + Pets agissent ensemble
        all_allies = heroes + active_pets
        
        for ally in [a for a in all_allies if a.is_alive()]:
            alive_enemies = [e for e in enemies if e.is_alive()]
            if not alive_enemies:
                break
            
            # Début tour allié (recharge parade + reset capacités magiques)
            ally.start_hero_turn()
            self._reset_magic_abilities_turn(ally)
            
            if ally.max_parade_tokens > 0:
                ally_name = getattr(ally, 'display_name', ally.name)
                log.append(f"🔄 {ally_name} recharge {ally.max_parade_tokens} jetons parade")
            
            # Logique différente pour héros vs Pets
            if hasattr(ally, 'owner_code'):  # C'est un Pet
                self._pet_turn(ally, alive_enemies, player_count, log)
            else:  # C'est un héros
                self._hero_turn(ally, alive_enemies, player_count, log, active_pets)
    
    def _hero_turn(self, hero, alive_enemies: List, player_count: int, log: List[str], active_pets: List):
        """Tour d'un héros avec gestion invocations et sorts conformes + logique d'action corrigée"""
        
        # Potion d'abord si nécessaire
        self._try_health_potion(hero, log)
        
        # Logique d'action améliorée
        action_taken = False
        
        # Tentative 1 : Capacité (peut inclure invocation)
        ability_used = self._try_ability_with_summon(hero, alive_enemies, log, active_pets)
        if ability_used:
            action_taken = True
        
        # Tentative 2 : Attaque si aucune action prise et autorisée
        if not action_taken:
            can_attack = not hasattr(hero, 'can_attack_this_turn') or hero.can_attack_this_turn
            
            # Vérifier si capacité magique utilisée (bloque attaque)
            combatant_id = self._get_combatant_id(hero)
            magic_used_this_turn = self.combatant_magic_abilities_this_turn.get(combatant_id, 0)
            if magic_used_this_turn > 0:
                can_attack = False
                
            if can_attack and not getattr(hero, 'action_taken_this_turn', False):
                self._hero_attack(hero, alive_enemies, player_count, log)
                action_taken = True
        
        # Log si aucune action possible
        if not action_taken:
            combatant_name = getattr(hero, 'display_name', hero.name)
            log.append(f"⏸️ {combatant_name} ne peut pas agir ce tour")
    
    def _pet_turn(self, pet, alive_enemies: List, player_count: int, log: List[str]):
        """Tour d'un Pet (attaque automatique simple)"""
        if alive_enemies:
            # Pet attaque automatiquement le premier ennemi
            self._hero_attack(pet, alive_enemies, player_count, log)
    
    def _enemies_turn(self, enemies: List, heroes: List, player_count: int, log: List[str], active_pets: List):
        """Phase ennemis avec recharge parade - ATTAQUENT L'ÉQUIPE + Pets"""
        log.append("👹 Phase des Ennemis")
        
        for enemy in [e for e in enemies if e.is_alive()]:
            alive_heroes = [h for h in heroes if h.is_alive()]
            alive_pets = [p for p in active_pets if p.is_alive()]
            all_targets = alive_heroes + alive_pets
            
            if not all_targets:
                break
            
            # Début tour ennemi (recharge parade)
            enemy.start_enemy_turn()
            if enemy.max_parade_tokens > 0:
                log.append(f"🔄 {enemy.name} recharge {enemy.max_parade_tokens} jetons parade")
            
            # RÈGLE OFFICIELLE : Ennemis attaquent l'équipe (héros + pets)
            enemy_stats = enemy.get_stats_for_players(player_count)
            damage = enemy_stats['damage']
            
            # Les joueurs choisissent qui prend les dégâts (héros ou pets)
            target = self._heroes_distribute_damage(all_targets, damage, enemy.name, log)
            
            # Application dégâts avec système parade
            damage_result = target.apply_damage_with_parade(damage)
            
            # Log détaillé avec nom approprié
            target_name = getattr(target, 'display_name', target.name)
            log_parts = [f"{enemy.name} attaque l'équipe: {damage} dégâts → {target_name}"]
            
            if damage_result['blocked_by_parade'] > 0:
                log_parts.append(f"({damage_result['blocked_by_parade']} bloqués par parade)")
                log_parts.append(f"{damage_result['health_damage']} aux PV")
            else:
                log_parts.append(f"{damage_result['health_damage']} aux PV")
            
            log.append(' '.join(log_parts))
            
            # Jetons parade restants
            if target.max_parade_tokens > 0:
                log.append(f"  🛡️ {target_name}: {target.current_parade_tokens}/{target.max_parade_tokens} jetons restants")
            
            if not target.is_alive():
                log.append(f"💀 {target_name} tombe !")
                # Retirer Pet de la liste s'il meurt
                if hasattr(target, 'owner_code') and target in active_pets:
                    active_pets.remove(target)
    
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
        """Attaque héros avec objets spéciaux (O-4 Lyre phoenix) + support Pets"""
        if not enemies:
            return
            
        target = enemies[0]  # Premier ennemi
        
        attack_roll = random.randint(1, 20)
        
        # Détection type d'attaque (physique ou magique)
        attack_info = hero.get_attack_damage_info()
        damage_type = attack_info['damage_type']
        damage_value = attack_info['damage_value']
        
        # Nom du combattant (héros ou Pet)
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        # Critique
        if self.rules.criticals and attack_roll == 20:
            damage = damage_value * 2
            damage_result = target.apply_damage_with_parade(damage)
            
            # Log avec jet de dé et type de dégâts
            total_attack = attack_roll + hero.get_total_precision()
            damage_type_emoji = "✨" if damage_type == "magical" else "💥"
            log.append(f"{damage_type_emoji} CRITIQUE ! {combatant_name} (🎲 20+{hero.get_total_precision()}={total_attack}) → {target.name}: {damage} dégâts {damage_type}s")
            
            # Log conversion selon l'objet spécial
            if attack_info.get('conversion_source') == 'lyre_phoenix':
                log.append(f"  🎵 Lyre phoenix: attaque convertie en dégâts magiques")
            elif attack_info.get('conversion_source') == 'gemme_pouvoir':
                form_display = attack_info.get('form_display', 'forme inconnue')
                log.append(f"  💎 Gemme de pouvoir: {form_display} → attaque magique")
            elif attack_info.get('pet_attack'):
                log.append(f"  🐾 Attaque de Pet invoqué")
            
            if damage_result['blocked_by_parade'] > 0:
                log.append(f"  🛡️ {damage_result['blocked_by_parade']} bloqués, {damage_result['health_damage']} aux PV")
            
            if not target.is_alive():
                log.append(f"💀 {target.name} vaincu !")
            return
        
        # Échec critique
        if self.rules.criticals and attack_roll == 1:
            total_attack = attack_roll + hero.get_total_precision()
            log.append(f"💢 ÉCHEC CRITIQUE ! {combatant_name} (🎲 1+{hero.get_total_precision()}={total_attack}) manque complètement")
            return
        
        # Attaque normale
        total_attack = attack_roll + hero.get_total_precision()
        if total_attack >= target.defense:
            damage = damage_value
            damage_result = target.apply_damage_with_parade(damage)
            
            # Log avec jet de dé et type de dégâts
            damage_type_text = "magiques" if damage_type == "magical" else "physiques"
            log_parts = [f"{combatant_name} (🎲 {attack_roll}+{hero.get_total_precision()}={total_attack} vs défense {target.defense}) → {target.name}: {damage} dégâts {damage_type_text}"]
            
            # Log conversion selon l'objet spécial
            conversion_log = ""
            if attack_info.get('conversion_source') == 'lyre_phoenix':
                conversion_log = "(🎵 Lyre phoenix)"
            elif attack_info.get('conversion_source') == 'gemme_pouvoir':
                form_display = attack_info.get('form_display', '').replace('🐻 ', '🐻').replace('🐺 ', '🐺')
                conversion_log = f"(💎 {form_display})"
            elif attack_info.get('pet_attack'):
                conversion_log = "(🐾 Pet)"
            
            if conversion_log:
                log_parts.append(conversion_log)
            
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
            log.append(f"{combatant_name} (🎲 {attack_roll}+{hero.get_total_precision()}={total_attack} vs défense {target.defense}) manque {target.name}")
    
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
                    combatant_name = getattr(hero, 'display_name', hero.name)
                    log.append(f"🧪 {combatant_name} boit une potion : {result['message']}")
    
    def _try_ability_with_summon(self, hero, enemies: List, log: List[str], active_pets: List) -> bool:
        """IA capacités intelligente + gestion invocations + vérification sorts CENTRALISÉE"""
        if not hasattr(hero, 'get_available_abilities'):
            return False
        
        available = hero.get_available_abilities()
        if not available:
            return False
        
        # Priorité 1 : Invocation si pas de Pet actuel pour Kraor
        if hero.code == "P-4" and hero.can_summon_pet():
            current_pets = [p for p in active_pets if hasattr(p, 'owner_code') and p.owner_code == hero.code]
            if not current_pets:  # Pas de Pet actuel
                # Chercher la capacité d'invocation (VirtualAbility avec ability_number 99)
                summon_ability = next((a for a in available if getattr(a, 'ability_number', 0) == 99), None)
                if summon_ability:
                    return self._use_summon_ability(hero, summon_ability, log, active_pets)
        
        # Filtrer les capacités utilisables avec vérification CENTRALISÉE
        usable_abilities = []
        for ability in available:
            if getattr(ability, 'ability_number', 0) == 99:  # Skip invocation
                continue
            
            # Vérification CENTRALISÉE des sorts
            can_use, reason = self._can_use_magical_ability(hero, ability)
            if can_use:
                usable_abilities.append(ability)
        
        if not usable_abilities:
            return False  # Aucune capacité utilisable
        
        # Logique IA avec capacités PRÉ-FILTRÉES ET VÉRIFIÉES
        # 1. Soin si PV < 50%
        health_percent = (hero.current_health / hero.get_total_health()) * 100
        if health_percent < 50:
            heal_abilities = [a for a in usable_abilities if 'soin' in a.name.lower()]
            if heal_abilities:
                return self._use_ability(hero, heal_abilities[0], log)
        
        # 2. Zone si 3+ ennemis
        if len(enemies) >= 3:
            aoe_abilities = [a for a in usable_abilities if 'tous les adversaires' in a.description.lower()]
            if aoe_abilities:
                return self._use_ability(hero, aoe_abilities[0], log)
        
        # 3. Attaque offensive
        offensive = [a for a in usable_abilities if any(word in a.description.lower() for word in ['dégât', 'inflige'])]
        if offensive:
            return self._use_ability(hero, offensive[0], log)
        
        # 4. Première capacité utilisable
        if usable_abilities:
            return self._use_ability(hero, usable_abilities[0], log)
        
        return False
    
    def _use_summon_ability(self, hero, ability, log: List[str], active_pets: List) -> bool:
        """Utilise une capacité d'invocation"""
        # Supprimer Pet existant du même propriétaire
        active_pets[:] = [p for p in active_pets if not (hasattr(p, 'owner_code') and p.owner_code == hero.code)]
        
        # Invoquer nouveau Pet
        new_pet = hero.summon_pet()
        if new_pet:
            if hasattr(new_pet, 'start_new_combat'):
                new_pet.start_new_combat()  # Initialiser pour le combat
            
            # Initialiser sorts pour le Pet
            self._initialize_spells(new_pet)
            
            active_pets.append(new_pet)
            
            pet_name = getattr(new_pet, 'display_name', 'Pet')
            log.append(f"🔮 {hero.name} utilise {ability.name}")
            log.append(f"  ✨ {pet_name} invoqué ! (Précision: {new_pet.precision}, Dégâts magiques: {new_pet.get_total_magical_damage()}, Santé: {new_pet.health})")
            
            # Marquer action prise
            hero.action_taken_this_turn = True
            return True
        
        return False
    
    def _use_ability(self, hero, ability, log: List[str]) -> bool:
        """Utilise une capacité avec gestion CENTRALISÉE des sorts"""
        
        # Vérification CENTRALISÉE des sorts
        can_use, reason = self._can_use_magical_ability(hero, ability)
        if not can_use:
            # Ne devrait jamais arriver si le filtrage est correct
            combatant_name = getattr(hero, 'display_name', hero.name)
            log.append(f"❌ {combatant_name} ne peut pas utiliser {ability.name}: {reason}")
            return False
        
        # Consommation CENTRALISÉE des sorts
        spell_cost = getattr(ability, 'spell_cost', 0)
        if not self._consume_spells(hero, spell_cost):
            # Ne devrait jamais arriver si la vérification est correcte
            combatant_name = getattr(hero, 'display_name', hero.name)
            log.append(f"❌ {combatant_name} échec consommation sorts pour {ability.name}")
            return False
        
        # Utilisation de la capacité sur le Character
        action = hero.use_ability(ability)
        if not action.success:
            return False
        
        # Affichage utilisation capacité avec formes
        combatant_name = getattr(hero, 'display_name', hero.name)
        log.append(f"🔮 {combatant_name} utilise {ability.name}")
        
        # Log avec règles officielles
        if spell_cost > 0:
            current_spells = self._get_current_spells(hero)
            log.append(f"  💫 Coût: {spell_cost} sorts (reste: {current_spells})")
            log.append(f"  🚫 Attaque physique bloquée (règle capacité magique)")
        
        # Log des effets de transformation (Elneha)
        if action.effects_applied:
            for effect in action.effects_applied:
                if "Transformation" in effect:
                    log.append(f"  🔄 {effect}")
        
        # Effets simples selon description
        desc = ability.description.lower()
        
        if "soin" in ability.name.lower():
            heal = 8 if "8 blessures" in desc else 4 if "4 blessures" in desc else 2
            actual = hero.heal(heal)
            if actual > 0:
                log.append(f"  💚 {combatant_name} récupère {actual} PV")
        
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
        """Pénalités défaite avec gestion CENTRALISÉE"""
        log.append("💀 DÉFAITE - Pénalités appliquées")
        for hero in heroes:
            current_spells = self._get_current_spells(hero)
            if current_spells > 0:
                # Décompte de 1 sort en pénalité
                self.combatant_spells[self._get_combatant_id(hero)] = max(0, current_spells - 1)
    
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
            spells_used = self._get_spells_used(hero)
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
                'spells_remaining': self._get_current_spells(hero),  # CENTRALISÉ
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
                        'spells_used': self._get_spells_used(pet),  # CENTRALISÉ
                        'spells_remaining': self._get_current_spells(pet),  # CENTRALISÉ
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
        heroes_with_spells = [h for h in heroes if self._get_spells_used(h) > 0]
        if heroes_with_spells:
            log.append("=== UTILISATION DES SORTS ===")
            for hero in heroes_with_spells:
                total_spells_max = hero.get_total_spells()
                used = self._get_spells_used(hero)
                remaining = self._get_current_spells(hero)
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
                'abilities_system_active': self.abilities_enabled,
                'potions_system_active': any(hasattr(h, 'health_potions') for h in heroes),
                'parade_system_active': True,
                'pets_system_active': len(active_pets) > 0,
                'special_objects_active': any(any(special_effects.values()) for h in heroes 
                                            if hasattr(h, 'get_special_equipment_effects') 
                                            for special_effects in [h.get_special_equipment_effects()]),
                'spells_system_active': any(self._get_spells_used(h) > 0 for h in heroes)
            }
        }

# Fonctions utilitaires
def create_combat_engine_with_abilities(rules, enable_abilities: bool = True):
    """Crée moteur avec capacités, parade, objets spéciaux, Pets et sorts centralisés"""
    if hasattr(rules, 'abilities_enabled'):
        rules.abilities_enabled = enable_abilities
    return CombatEngine(rules)