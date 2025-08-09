"""
Gestionnaire des actions de combat (attaques, capacités, potions)
Extrait de combat_engine.py pour modularité
"""

import random
import streamlit as st

class CombatActions:
    """Gestion des actions de combat pour héros et pets"""
    
    def __init__(self, spell_manager, rules):
        self.spell_manager = spell_manager
        self.rules = rules
    
    def hero_attack(self, hero, enemies: list, player_count: int, log: list):
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
    
    def try_health_potion(self, hero, log: list):
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
    
    def try_ability_with_summon(self, hero, enemies: list, log: list, active_pets: list) -> bool:
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
            
            active_pets.append(new_pet)
            
            pet_name = getattr(new_pet, 'display_name', 'Pet')
            log.append(f"🔮 {hero.name} utilise {ability.name}")
            log.append(f"  ✨ {pet_name} invoqué ! (Précision: {new_pet.precision}, Dégâts magiques: {new_pet.get_total_magical_damage()}, Santé: {new_pet.health})")
            
            # Marquer action prise
            hero.action_taken_this_turn = True
            return True
        
        return False
    
    def use_ability(self, hero, ability, log: list) -> bool:
        """Utilise une capacité avec gestion CENTRALISÉE des sorts + ciblage tactique"""
        
        # Vérification CENTRALISÉE des sorts
        can_use, reason = self.spell_manager.can_use_magical_ability(hero, ability)
        if not can_use:
            # Ne devrait jamais arriver si le filtrage est correct
            combatant_name = getattr(hero, 'display_name', hero.name)
            log.append(f"❌ {combatant_name} ne peut pas utiliser {ability.name}: {reason}")
            return False
        
        # Consommation CENTRALISÉE des sorts
        spell_cost = getattr(ability, 'spell_cost', 0)
        if not self.spell_manager.consume_spells(hero, spell_cost):
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
            current_spells = self.spell_manager.get_current_spells(hero)
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
            # Appliquer VRAIS dégâts aux ennemis avec ciblage tactique
            return self.apply_ability_damage(hero, ability, spell_cost, log)
        
        return True
    
    def apply_ability_damage(self, hero, ability, spell_cost: int, log: list) -> bool:
        """Applique les dégâts d'une capacité aux ennemis avec ciblage tactique"""
        # Récupérer tous les ennemis vivants
        alive_enemies = [e for e in st.session_state.get('current_enemies', []) if e.is_alive()]
        if not alive_enemies:
            return True
        
        # Extraire dégâts de la description
        desc = ability.description.lower()
        damage = 6 if "6 dégâts" in desc else 4 if "4 dégâts" in desc else 3
        
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        # Gestion AoE (tous les adversaires)
        if "tous les adversaires" in desc:
            log.append(f"  ⚡ Dégâts magiques AoE: {damage} à tous les ennemis")
            for enemy in alive_enemies:
                damage_result = enemy.apply_damage_with_parade(damage)
                log.append(f"    → {enemy.name}: {damage_result['health_damage']} dégâts")
                if damage_result['blocked_by_parade'] > 0:
                    log.append(f"      🛡️ ({damage_result['blocked_by_parade']} bloqués par parade)")
                if not enemy.is_alive():
                    log.append(f"    💀 {enemy.name} vaincu !")
        else:
            # Ciblage tactique selon type de capacité
            if spell_cost > 0:
                # Capacité MAGIQUE = attaque à distance = choix tactique
                player_count = len(st.session_state.get('selected_heroes', []))
                target = self._choose_target_tactically(alive_enemies, player_count)
                targeting_reason = "ciblage tactique"
            else:
                # Capacité PHYSIQUE = corps à corps = premier ennemi obligatoire
                target = alive_enemies[0]
                targeting_reason = "corps à corps"
            
            # Application des dégâts
            damage_result = target.apply_damage_with_parade(damage)
            
            # Log détaillé
            damage_type = "magiques" if spell_cost > 0 else "physiques"
            log.append(f"  ⚡ {combatant_name} → {target.name}: {damage} dégâts {damage_type} ({targeting_reason})")
            
            if damage_result['blocked_by_parade'] > 0:
                log.append(f"    🛡️ {damage_result['blocked_by_parade']} bloqués par parade, {damage_result['health_damage']} aux PV")
            else:
                log.append(f"    💥 {damage_result['health_damage']} aux PV")
            
            # Jetons parade restants
            if target.max_parade_tokens > 0:
                log.append(f"    🛡️ {target.name}: {target.current_parade_tokens}/{target.max_parade_tokens} jetons restants")
            
            if not target.is_alive():
                log.append(f"    💀 {target.name} vaincu !")
        
        return True
    
    def _choose_target_tactically(self, enemies: list, player_count: int):
        """IA tactique pour choisir la meilleure cible (style D&D)"""
        if len(enemies) == 1:
            return enemies[0]
        
        scores = []
        for enemy in enemies:
            score = 0
            
            # 1. Priorité ennemis affaiblis (finir les blessés)
            health_percent = (enemy.current_health / enemy.max_health) * 100
            if health_percent < 30:
                score += 50  # Haute priorité - finir les mourants
            elif health_percent < 60:
                score += 20
            
            # 2. Priorité ennemis magiques (plus dangereux)
            if getattr(enemy, 'is_magical', False):
                score += 30
            
            # 3. Favoriser cibles avec dégâts élevés (menace offensive)
            enemy_stats = enemy.get_stats_for_players(player_count)
            if enemy_stats['damage'] > 8:
                score += 15
            
            # 4. Malus pour ennemis très résistants (éviter les tanks)
            if enemy_stats['health'] > 20:
                score -= 5
            
            scores.append((enemy, score))
        
        # Retourner l'ennemi avec le meilleur score tactique
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0]