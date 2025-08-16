# combat_actions.py
"""
Gestionnaire des actions de combat (attaques, capacités, potions)
VERSION CORRIGÉE COMPLÈTE - Fix contexte ennemis + toutes méthodes
"""

import random
import streamlit as st
from models.combat.abilities import AbilityEffectsManager
from models.combat.abilities.character_integration import CharacterAbilitiesIntegration

class CombatActions:
    """Gestion des actions de combat pour héros et pets avec système d'effets modulaire"""
    
    def __init__(self, spell_manager, rules):
        self.spell_manager = spell_manager
        self.rules = rules
        
        # NOUVEAU - Système modulaire d'effets
        self.ability_effects_manager = AbilityEffectsManager(spell_manager)
        
        # NOUVEAU - Stockage temporaire des ennemis pour contexte
        self._current_alive_enemies = []
        self._current_heroes = []
    
    def hero_attack(self, hero, enemies: list, player_count: int, log: list):
        """Attaque héros avec objets spéciaux + système d'effets modulaire"""
        if not enemies:
            return
            
        target = enemies[0]  # Premier ennemi
        
        # NOUVEAU - Vérifier modificateurs d'attaque avant l'attaque
        attack_modifiers = CharacterAbilitiesIntegration.check_attack_modifiers(hero)
        
        attack_roll = random.randint(1, 20)
        
        # Détection type d'attaque (physique ou magique)
        attack_info = hero.get_attack_damage_info()
        damage_type = attack_info['damage_type']
        base_damage_value = attack_info['damage_value']
        
        # NOUVEAU - Appliquer modificateurs de dégâts
        damage_value = base_damage_value
        if attack_modifiers['damage_multiplier'] > 1.0:
            damage_value = int(base_damage_value * attack_modifiers['damage_multiplier'])
        damage_value += attack_modifiers['damage_bonus']
        
        # NOUVEAU - Vérifier bonus de marquage (Kraor)
        mark_bonus = self._get_mark_bonus_for_target(hero, target)
        damage_value += mark_bonus
        
        # Nom du combattant (héros ou Pet)
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        # Critique
        if self.rules.criticals and attack_roll == 20:
            final_damage = damage_value * 2
            damage_result = target.apply_damage_with_parade(final_damage)
            
            # Log avec modificateurs
            total_attack = attack_roll + hero.get_total_precision()
            damage_type_emoji = "✨" if damage_type == "magical" else "💥"
            
            log_parts = [f"{damage_type_emoji} CRITIQUE ! {combatant_name}[{total_attack}] → {target.name}({damage_result['health_damage']})"]
            
            # NOUVEAU - Log des modificateurs actifs
            self._add_modifier_logs(log_parts, attack_modifiers, mark_bonus, damage_value, base_damage_value)
            
            log.append(' '.join(log_parts))
            
            # Log conversion selon l'objet spécial
            self._add_conversion_logs(log, attack_info)
            
            if damage_result['blocked_by_parade'] > 0:
                log.append(f"  🛡️ {damage_result['blocked_by_parade']} bloqués, {damage_result['health_damage']} aux PV")
            
            if not target.is_alive():
                log.append(f"💀 {target.name} vaincu !")
            
            # NOUVEAU - Consommer buffs temporaires après attaque réussie
            CharacterAbilitiesIntegration.enhance_hero_attack(hero, target, damage_result['health_damage'])
            return
        
        # Échec critique
        elif self.rules.criticals and attack_roll == 1:
            total_attack = attack_roll + hero.get_total_precision()
            damage_type_emoji = "✨" if damage_type == "magical" else "💥"
            
            log.append(f"{damage_type_emoji} ÉCHEC ! {combatant_name}[{total_attack}] attaque {target.name}")
            self._handle_critical_failure(hero, target, log)
        
        # Attaque normale
        else:
            total_attack = attack_roll + hero.get_total_precision()
            
            if total_attack >= target.defense:
                damage_result = target.apply_damage_with_parade(damage_value)
                damage_type_emoji = "✨" if damage_type == "magical" else "⚔️"
                
                log_parts = [f"{damage_type_emoji} {combatant_name}[{total_attack}] → {target.name}({damage_result['health_damage']})"]
                
                # NOUVEAU - Log des modificateurs actifs
                self._add_modifier_logs(log_parts, attack_modifiers, mark_bonus, damage_value, base_damage_value)
                
                log.append(' '.join(log_parts))
                
                # Log conversion objets spéciaux
                self._add_conversion_logs(log, attack_info)
                
                if damage_result['blocked_by_parade'] > 0:
                    log.append(f"  🛡️ {damage_result['blocked_by_parade']} bloqués par parade, {damage_result['health_damage']} aux PV")
                else:
                    log.append(f"  💥 {damage_result['health_damage']} aux PV")
                
                if not target.is_alive():
                    log.append(f"💀 {target.name} vaincu !")
                
                # NOUVEAU - Consommer buffs temporaires après attaque réussie
                CharacterAbilitiesIntegration.enhance_hero_attack(hero, target, damage_result['health_damage'])
            else:
                damage_type_emoji = "✨" if damage_type == "magical" else "⚔️"
                log.append(f"{damage_type_emoji} {combatant_name}[{total_attack}] vs DEF[{target.defense}] → Échec")
                
                # NOUVEAU - Consommer buffs même en cas d'échec
                CharacterAbilitiesIntegration.enhance_hero_attack(hero, target, 0)
        
        # Marquer action prise
        hero.action_taken_this_turn = True

    def _get_mark_bonus_for_target(self, hero, target) -> int:
        """Calcule le bonus de dégâts contre une cible marquée (Kraor)"""
        if hero.code != "P-4":  # Seulement pour Kraor
            return 0
        
        # Vérifier si la cible est marquée
        if hasattr(target, 'is_marked') and target.is_marked:
            return 2  # Bonus de marquage selon les règles
        elif hasattr(target, 'marked_by') and hero.code in target.marked_by:
            return 2
        
        return 0

    def _handle_critical_failure(self, attacker, target, log: list):
        """Gère l'échec critique avec riposte de l'ennemi (ligne 91 identifiée dans documentation)"""
        try:
            # FIX CRITIQUE: Utiliser get_damage_info() pour Enemy au lieu de get_attack_damage_info()
            if hasattr(target, 'get_damage_info'):
                # C'est un Enemy - utiliser get_damage_info avec player_count
                player_count = len(st.session_state.get('current_heroes', []))
                enemy_damage_info = target.get_damage_info(player_count)
                counter_damage = enemy_damage_info['damage_value']
            elif hasattr(target, 'get_attack_damage_info'):
                # C'est un Character/Hero - utiliser get_attack_damage_info
                counter_damage_info = target.get_attack_damage_info()
                counter_damage = counter_damage_info['damage_value']
            else:
                # Fallback si aucune méthode disponible
                counter_damage = getattr(target, 'damage', 1)
            
            # Appliquer dégâts de riposte sans parade possible
            if hasattr(attacker, 'current_health'):
                old_health = attacker.current_health
                attacker.current_health = max(0, attacker.current_health - counter_damage)
                actual_damage = old_health - attacker.current_health
                log.append(f"    ⚡ {target.name} riposte immédiatement ! {actual_damage} dégâts à {attacker.name}")
                
                if not attacker.is_alive():
                    log.append(f"    💀 {attacker.name} vaincu par la riposte !")
        except Exception as e:
            log.append(f"    ⚠️ Erreur riposte échec critique: {str(e)}")

    def _add_modifier_logs(self, log_parts: list, attack_modifiers: dict, mark_bonus: int, damage_value: int, base_damage_value: int):
        """Ajoute les logs des modificateurs d'attaque"""
        modifiers = []
        
        if attack_modifiers['damage_bonus'] > 0:
            modifiers.append(f"+{attack_modifiers['damage_bonus']}bonus")
        
        if attack_modifiers['damage_multiplier'] > 1.0:
            modifiers.append(f"x{attack_modifiers['damage_multiplier']}")
        
        if mark_bonus > 0:
            modifiers.append(f"+{mark_bonus}marquage")
        
        if modifiers:
            log_parts.append(f"[{','.join(modifiers)}]")

    def _add_conversion_logs(self, log: list, attack_info: dict):
        """Ajoute les logs de conversion d'objets spéciaux"""
        conversion_log = self._get_conversion_log(attack_info)
        if conversion_log:
            log.append(f"  {conversion_log}")
    
    def _get_conversion_log(self, attack_info: dict) -> str:
        """Génère le log de conversion selon l'objet spécial équipé"""
        if attack_info.get('converted_by') == 'O-1':
            return "💎 Gemme de pouvoir: Attaque convertie en magie (forme animale)"
        elif attack_info.get('converted_by') == 'O-4':
            return "🎭 Lyre phoenix: Attaque convertie en magie"
        return ""
    
    # NOUVEAU - Méthodes pour transmission contexte
    def set_combat_context(self, heroes: list, enemies: list):
        """Définit le contexte de combat pour les capacités individuelles"""
        self._current_heroes = [h for h in heroes if h.is_alive()]
        self._current_alive_enemies = [e for e in enemies if e.is_alive()]
        
        # Transmettre au manager d'effets
        self.ability_effects_manager._current_heroes = self._current_heroes
        self.ability_effects_manager._current_alive_enemies = self._current_alive_enemies
    
    def update_alive_enemies(self, enemies: list):
        """Met à jour la liste des ennemis vivants"""
        self._current_alive_enemies = [e for e in enemies if e.is_alive()]
        self.ability_effects_manager._current_alive_enemies = self._current_alive_enemies

    def use_ability(self, hero, ability, log: list) -> bool:
        """
        MODIFIÉ - Utilise une capacité avec le système modulaire d'effets + contexte ennemis FIXÉ
        """
        
        # Vérification CENTRALISÉE des sorts
        can_use, reason = self.spell_manager.can_use_magical_ability(hero, ability)
        if not can_use:
            combatant_name = getattr(hero, 'display_name', hero.name)
            log.append(f"❌ {combatant_name} ne peut pas utiliser {ability.name}: {reason}")
            return False
        
        # NOUVEAU - Appliquer effets de début de tour si nécessaire
        self.ability_effects_manager.apply_turn_start_effects(hero, log)
        
        # FIX CRITIQUE - Créer contexte complet avec ennemis actuels
        context = {
            'alive_enemies': self._current_alive_enemies,  # CLEF PRINCIPALE pour BaseAbility._get_all_enemies()
            'current_enemies': self._current_alive_enemies,  # Fallback
            'enemies': self._current_alive_enemies,  # Fallback alternatif
            'heroes': self._current_heroes,
            'current_heroes': self._current_heroes,
            'spell_manager': self.spell_manager,
            'log': log,
            'player_count': len(self._current_heroes)
        }
        
        # NOUVEAU - Passer le contexte complet au manager d'effets
        self.ability_effects_manager._current_alive_enemies = self._current_alive_enemies
        self.ability_effects_manager._current_heroes = self._current_heroes
        
        # NOUVEAU - Appliquer effets avec le système modulaire + contexte fixé
        effects_applied = self.ability_effects_manager.apply_ability_effects(hero, ability, log, context)
        
        #if not effects_applied:
            # Fallback : affichage basique si capacité non trouvée
        #    combatant_name = getattr(hero, 'display_name', hero.name)
        #    log.append(f"📖 {combatant_name} utilise {ability.name}")
        #    log.append(f"   (Effet générique - capacité non implémentée)")
        
        # Marquer action prise après utilisation
        hero.action_taken_this_turn = True
        return True

    def try_health_potion(self, hero, log: list):
        """IA utilise potions intelligemment - INCHANGÉ"""
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

    def pet_attack(self, pet, enemies: list, player_count: int, log: list):
        """Attaque Pet - logique simplifiée"""
        if not enemies:
            return
            
        target = enemies[0]
        attack_roll = random.randint(1, 20)
        
        damage_info = pet.get_attack_damage_info()
        damage_value = damage_info['damage_value']
        damage_type = damage_info['damage_type']
        
        total_attack = attack_roll + pet.precision
        pet_name = getattr(pet, 'display_name', 'Pet')
        
        if total_attack >= target.defense:
            damage_result = target.apply_damage_with_parade(damage_value)
            damage_type_emoji = "✨" if damage_type == "magical" else "🐾"
            
            log.append(f"{damage_type_emoji} {pet_name}[{total_attack}] → {target.name}({damage_result['health_damage']})")
            
            if damage_result['blocked_by_parade'] > 0:
                log.append(f"    [{damage_result['blocked_by_parade']}🛡️ bloqué]")
            
            if not target.is_alive():
                log.append(f"    💀 {target.name} vaincu !")
        else:
            damage_type_emoji = "✨" if damage_type == "magical" else "🐾"
            log.append(f"{damage_type_emoji} {pet_name}[{total_attack}] vs DEF[{target.defense}] → Échec")

    def smart_pet_ability_usage(self, pet, log: list) -> bool:
        """IA tactique pour Pets"""
        if not hasattr(pet, 'abilities') or not pet.abilities:
            return False
        
        # Ennemis pour contexte
        enemies = self._current_alive_enemies
        if not enemies:
            return False
        
        # Capacités utilisables
        usable_abilities = [a for a in pet.abilities if self.spell_manager.can_use_magical_ability(pet, a)[0]]
        if not usable_abilities:
            return False
        
        # 1. Soin si santé basse
        if pet.current_health / pet.get_total_health() < 0.5:
            healing_abilities = [a for a in usable_abilities if 'soin' in a.description.lower()]
            if healing_abilities:
                return self.use_ability(pet, healing_abilities[0], log)
        
        # 2. Zone si 3+ ennemis
        if len(enemies) >= 3:
            aoe_abilities = [a for a in usable_abilities if 'tous les adversaires' in a.description.lower()]
            if aoe_abilities:
                return self.use_ability(pet, aoe_abilities[0], log)
        
        # 3. Attaque offensive
        offensive = [a for a in usable_abilities if any(word in a.description.lower() for word in ['dégât', 'inflige'])]
        if offensive:
            return self.use_ability(pet, offensive[0], log)
        
        # 4. Première capacité utilisable
        if usable_abilities:
            return self.use_ability(pet, usable_abilities[0], log)
        
        return False
    
    def use_summon_ability(self, hero, ability, log: list, active_pets: list) -> bool:
        """Utilise une capacité d'invocation"""
        # Supprimer Pet existant du même propriétaire
        active_pets[:] = [p for p in active_pets if not (hasattr(p, 'owner_code') and p.owner_code == hero.code)]
        
        # Invoquer nouveau Pet
        new_pet = hero.summon_pet()
        if new_pet:
            if hasattr(new_pet, 'start_new_combat'):
                new_pet.start_new_combat()  # Initialiser pour le combat
            
            # Initialiser sorts pour le Pet
            self.spell_manager.initialize_spells(new_pet)
            
            # NOUVEAU - Initialiser attributs d'effets pour le Pet
            CharacterAbilitiesIntegration.add_required_attributes(new_pet)
            
            active_pets.append(new_pet)
            
            pet_name = getattr(new_pet, 'display_name', 'Pet')
            log.append(f"🔮 {hero.name} utilise {ability.name}")
            log.append(f"  ✨ {pet_name} invoqué !")
            log.append(f"    (Précision: {new_pet.precision}, Dégâts magiques: {new_pet.get_total_magical_damage()}, Santé: {new_pet.health})")
            
            # Marquer action prise
            hero.action_taken_this_turn = True
            return True
        
        return False
    
    def try_ability_with_summon(self, hero, enemies: list, log: list, active_pets: list) -> bool:
        """
        IA capacités intelligente + gestion invocations + NOUVEAU système modulaire d'effets
        MODIFIÉ: Stocke les ennemis pour transmission au contexte
        """
        # NOUVEAU - Stocker ennemis et héros pour contexte
        self._current_alive_enemies = [e for e in enemies if e.is_alive()]
        self._current_heroes = [hero]  # Pour l'instant, juste le héros actuel
        
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
                    return self.use_summon_ability(hero, summon_ability, log, active_pets)
        
        # Filtrer les capacités utilisables avec vérification CENTRALISÉE
        usable_abilities = []
        for ability in available:
            if getattr(ability, 'ability_number', 0) == 99:  # Skip invocation
                continue
            
            # Vérification CENTRALISÉE des sorts
            can_use, reason = self.spell_manager.can_use_magical_ability(hero, ability)
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
                return self.use_ability(hero, heal_abilities[0], log)
        
        # 2. Zone si 3+ ennemis
        if len(enemies) >= 3:
            aoe_abilities = [a for a in usable_abilities if 'tous les adversaires' in a.description.lower()]
            if aoe_abilities:
                return self.use_ability(hero, aoe_abilities[0], log)
        
        # 3. Attaque offensive
        offensive = [a for a in usable_abilities if any(word in a.description.lower() for word in ['dégât', 'inflige'])]
        if offensive:
            return self.use_ability(hero, offensive[0], log)
        
        # 4. Première capacité utilisable
        if usable_abilities:
            return self.use_ability(hero, usable_abilities[0], log)
        
        return False

    def enemy_attack(self, enemy, heroes: list, player_count: int, log: list, active_pets: list):
        """Attaque ennemi AMÉLIORÉE - cible l'équipe + Pets selon règles"""
        all_targets = heroes + active_pets
        alive_targets = [t for t in all_targets if t.is_alive()]
        
        if not alive_targets:
            return
        
        # Recharge parade pour l'ennemi
        enemy.current_parade_tokens = enemy.get_total_parade_tokens()
        
        # Stats ennemis selon nombre de joueurs
        enemy_stats = enemy.get_stats_for_players(player_count)
        damage = enemy_stats['damage']
        
        # Ciblage intelligent selon les règles
        target = self._select_enemy_target(enemy, alive_targets)
        
        # Log attaque
        enemy_name = getattr(enemy, 'display_name', enemy.name)
        target_name = getattr(target, 'display_name', target.name)
        
        # Ennemis touchent toujours (pas de jet d'attaque)
        damage_result = target.apply_damage_with_parade(damage)
        
        log.append(f"👹 {enemy_name} attaque {target_name}: {damage} dégâts")
        
        if damage_result['blocked_by_parade'] > 0:
            log.append(f"  🛡️ {damage_result['blocked_by_parade']} bloqués par parade, {damage_result['health_damage']} aux PV")
        else:
            log.append(f"  💥 {damage_result['health_damage']} aux PV")
        
        if not target.is_alive():
            log.append(f"  💀 {target_name} vaincu !")

    def _select_enemy_target(self, enemy, alive_targets: list):
        """Sélection de cible selon les règles d'IA tactique"""
        if not alive_targets:
            return None
        
        # Règle 1: Cible avec parade la plus faible (règles du jeu)
        targets_with_parade = [(t, getattr(t, 'current_parade_tokens', 0)) for t in alive_targets]
        min_parade = min(targets_with_parade, key=lambda x: x[1])[1]
        lowest_parade_targets = [t for t, p in targets_with_parade if p == min_parade]
        
        # Règle 2: Si égalité, cible avec moins de PV
        if len(lowest_parade_targets) > 1:
            return min(lowest_parade_targets, key=lambda t: t.current_health)
        
        return lowest_parade_targets[0]