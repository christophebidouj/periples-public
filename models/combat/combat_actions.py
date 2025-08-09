"""
Gestionnaire des actions de combat (attaques, capacités, potions)
VERSION MISE À JOUR - Utilise le système modulaire d'effets de capacités
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
            
            log_parts = [f"{damage_type_emoji} CRITIQUE ! {combatant_name} (🎲 20+{hero.get_total_precision()}={total_attack}) → {target.name}: {final_damage} dégâts {damage_type}s"]
            
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
        if self.rules.criticals and attack_roll == 1:
            total_attack = attack_roll + hero.get_total_precision()
            log.append(f"💢 ÉCHEC CRITIQUE ! {combatant_name} (🎲 1+{hero.get_total_precision()}={total_attack}) manque complètement")
            
            # NOUVEAU - Consommer buffs même en cas d'échec critique
            CharacterAbilitiesIntegration.enhance_hero_attack(hero, target, 0)
            return
        
        # Attaque normale
        total_attack = attack_roll + hero.get_total_precision()
        if total_attack >= target.defense:
            damage_result = target.apply_damage_with_parade(damage_value)
            
            # Log avec modificateurs
            damage_type_text = "magiques" if damage_type == "magical" else "physiques"
            log_parts = [f"{combatant_name} (🎲 {attack_roll}+{hero.get_total_precision()}={total_attack} vs défense {target.defense}) → {target.name}: {damage_value} dégâts {damage_type_text}"]
            
            # NOUVEAU - Log des modificateurs
            modifier_details = []
            if attack_modifiers['damage_multiplier'] > 1.0:
                modifier_details.append(f"x{attack_modifiers['damage_multiplier']}")
            if attack_modifiers['damage_bonus'] > 0:
                modifier_details.append(f"+{attack_modifiers['damage_bonus']}")
            if mark_bonus > 0:
                modifier_details.append(f"+{mark_bonus} marque")
            
            if modifier_details:
                log_parts.append(f"({' '.join(modifier_details)})")
            
            # Log conversion selon l'objet spécial
            conversion_log = self._get_conversion_log(attack_info)
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
            
            # NOUVEAU - Consommer buffs temporaires après attaque réussie
            CharacterAbilitiesIntegration.enhance_hero_attack(hero, target, damage_result['health_damage'])
        else:
            log.append(f"{combatant_name} (🎲 {attack_roll}+{hero.get_total_precision()}={total_attack} vs défense {target.defense}) manque {target.name}")
            
            # NOUVEAU - Consommer buffs même en cas d'échec
            CharacterAbilitiesIntegration.enhance_hero_attack(hero, target, 0)
    
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
    
    def try_ability_with_summon(self, hero, enemies: list, log: list, active_pets: list) -> bool:
        """
        IA capacités intelligente + gestion invocations + NOUVEAU système modulaire d'effets
        """
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
    
    def use_summon_ability(self, hero, ability, log: list, active_pets: list) -> bool:
        """Utilise une capacité d'invocation - INCHANGÉ"""
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
            log.append(f"  ✨ {pet_name} invoqué ! (Précision: {new_pet.precision}, Dégâts magiques: {new_pet.get_total_magical_damage()}, Santé: {new_pet.health})")
            
            # Marquer action prise
            hero.action_taken_this_turn = True
            return True
        
        return False
    
    def use_ability(self, hero, ability, log: list) -> bool:
        """
        NOUVEAU - Utilise une capacité avec le système modulaire d'effets
        """
        
        # Vérification CENTRALISÉE des sorts
        can_use, reason = self.spell_manager.can_use_magical_ability(hero, ability)
        if not can_use:
            combatant_name = getattr(hero, 'display_name', hero.name)
            log.append(f"❌ {combatant_name} ne peut pas utiliser {ability.name}: {reason}")
            return False
        
        # Consommation CENTRALISÉE des sorts
        spell_cost = getattr(ability, 'spell_cost', 0)
        if not self.spell_manager.consume_spells(hero, spell_cost):
            combatant_name = getattr(hero, 'display_name', hero.name)
            log.append(f"❌ {combatant_name} échec consommation sorts pour {ability.name}")
            return False
        
        # NOUVEAU - Appliquer effets de début de tour si nécessaire
        self.ability_effects_manager.apply_turn_start_effects(hero, log)
        
        # Utilisation de la capacité sur le Character
        action = hero.use_ability(ability)
        if not action.success:
            return False
        
        # Affichage utilisation capacité
        combatant_name = getattr(hero, 'display_name', hero.name)
        log.append(f"🔮 {combatant_name} utilise {ability.name}")
        
        # Log avec règles officielles
        if spell_cost > 0:
            current_spells = self.spell_manager.get_current_spells(hero)
            log.append(f"  💫 Coût: {spell_cost} sorts (reste: {current_spells})")
            log.append(f"  🚫 Attaque physique bloquée (règle capacité magique)")
        
        # NOUVEAU - Appliquer effets avec le système modulaire
        effects_applied = self.ability_effects_manager.apply_ability_effects(hero, ability, log)
        
        if not effects_applied:
            # Fallback : affichage générique si aucun effet spécifique
            log.append(f"  ✨ Effet de {ability.name} appliqué")
        
        # NOUVEAU - Appliquer effets de fin de capacité
        self.ability_effects_manager.apply_turn_end_effects(hero, log)
        
        return True
    
    # === NOUVELLES MÉTHODES UTILITAIRES ===
    
    def _get_mark_bonus_for_target(self, attacker, target) -> int:
        """Vérifie si la cible est marquée et retourne le bonus de dégâts"""
        if not hasattr(target, 'marks'):
            return 0
        
        # Marque du chasseur (Kraor)
        if 'chasseur' in target.marks:
            mark_info = target.marks['chasseur']
            return mark_info.get('bonus_damage', 0)
        
        return 0
    
    def _add_modifier_logs(self, log_parts: list, modifiers: dict, mark_bonus: int, final_damage: int, base_damage: int):
        """Ajoute les logs des modificateurs d'attaque"""
        modifier_details = []
        
        if modifiers['damage_multiplier'] > 1.0:
            modifier_details.append(f"x{modifiers['damage_multiplier']}")
        
        if modifiers['damage_bonus'] > 0:
            modifier_details.append(f"+{modifiers['damage_bonus']}")
        
        if mark_bonus > 0:
            modifier_details.append(f"+{mark_bonus} marque")
        
        if modifier_details:
            log_parts.append(f"({' '.join(modifier_details)})")
    
    def _add_conversion_logs(self, log: list, attack_info: dict):
        """Ajoute les logs de conversion d'objets spéciaux"""
        if attack_info.get('conversion_source') == 'lyre_phoenix':
            log.append(f"  🎵 Lyre phoenix: attaque convertie en dégâts magiques")
        elif attack_info.get('conversion_source') == 'gemme_pouvoir':
            form_display = attack_info.get('form_display', 'forme inconnue')
            log.append(f"  💎 Gemme de pouvoir: {form_display} → attaque magique")
        elif attack_info.get('pet_attack'):
            log.append(f"  🐾 Attaque de Pet invoqué")
    
    def _get_conversion_log(self, attack_info: dict) -> str:
        """Retourne le log de conversion en format court"""
        if attack_info.get('conversion_source') == 'lyre_phoenix':
            return "(🎵 Lyre phoenix)"
        elif attack_info.get('conversion_source') == 'gemme_pouvoir':
            form_display = attack_info.get('form_display', '').replace('🐻 ', '🐻').replace('🐺 ', '🐺')
            return f"(💎 {form_display})"
        elif attack_info.get('pet_attack'):
            return "(🐾 Pet)"
        return ""