# combat_actions.py
"""
Gestionnaire des actions de combat (attaques, capacités, potions)
VERSION CORRIGÉE - Fix IA logique + optimisation + transformations intelligentes + SUPPORT FORMES ELNEHA via temporary_buffs
CORRECTION KRAOR: Utilise marks/status_effects existants au lieu de is_marked/marked_by
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
        self.ability_effects_manager = AbilityEffectsManager(spell_manager)
        self._current_alive_enemies = []
        self._current_heroes = []
    
    def hero_attack(self, hero, enemies: list, player_count: int, log: list):
        """Attaque héros avec objets spéciaux + système d'effets modulaire + FORME DE LOUP via temporary_buffs

        Returns:
            dict: {'hit': bool, 'damage': int, 'critical': bool, 'critical_fail': bool, 'target': Character}
        """
        if not enemies:
            return {'hit': False, 'damage': 0, 'critical': False, 'critical_fail': False, 'target': None}
            
        target = enemies[0]
        attack_modifiers = CharacterAbilitiesIntegration.check_attack_modifiers(hero)

        # 🎯 NOUVEAU - Assaut furieux (Lame P-7-6) : Auto-hit (pas de dé)
        auto_hit = False
        if hasattr(hero, 'temporary_buffs'):
            assaut_buff = hero.temporary_buffs.get('assaut_furieux_permanent')
            if assaut_buff and assaut_buff.get('auto_hit'):
                auto_hit = True
                attack_roll = 20  # Considéré comme réussite automatique (pas critique)
                log.append(f"  ⚡ ASSAUT FURIEUX : Attaque réussit automatiquement (pas de dé)")
            else:
                attack_roll = random.randint(1, 20)
        else:
            attack_roll = random.randint(1, 20)

        # ⚖️ NOUVEAU - Sens de la justice (Atucan P-3-2) : Relance dé si 1 ou 2
        if not auto_hit and hasattr(hero, 'temporary_buffs'):
            justice_buff = hero.temporary_buffs.get('sens_de_la_justice_active')
            if justice_buff:
                reroll_on = justice_buff.get('reroll_on', [])
                max_rerolls = justice_buff.get('max_rerolls_per_turn', 0)
                rerolls_used = justice_buff.get('rerolls_used_this_turn', 0)

                if attack_roll in reroll_on and rerolls_used < max_rerolls:
                    log.append(f"  ⚖️ SENS DE LA JUSTICE : Dé = {attack_roll} → Relance autorisée !")
                    old_roll = attack_roll
                    attack_roll = random.randint(1, 20)
                    justice_buff['rerolls_used_this_turn'] += 1
                    log.append(f"  🎲 Nouveau résultat : {old_roll} → {attack_roll}")
        
        attack_info = hero.get_attack_damage_info()
        damage_type = attack_info['damage_type']
        base_damage = attack_info['damage_value']
        
        # Appliquer modificateurs
        damage_value = base_damage
        if attack_modifiers['damage_multiplier'] > 1.0:
            damage_value = int(base_damage * attack_modifiers['damage_multiplier'])
        damage_value += attack_modifiers['damage_bonus']
        damage_value += self._get_mark_bonus_for_target(hero, target)

        # 🐺 NOUVEAU: Détection source multiplicateur de dégâts pour logs explicites
        damage_multiplier_source = None  # Stocke la source du multiplicateur
        elneha_wolf_used = False

        if hasattr(hero, 'temporary_buffs') and attack_modifiers['damage_multiplier'] > 1.0:
            # Système ancien (avec compteur elneha_wolf_remaining)
            if hero.temporary_buffs.get('elneha_wolf_remaining', 0) > 0:
                hero.temporary_buffs['elneha_wolf_remaining'] -= 1
                # CORRECTION : Vérifier que c'est bien Elneha (P-1) avant de marquer le log
                if hero.code == "P-1":
                    elneha_wolf_used = True
                    damage_multiplier_source = "elneha_wolf"
                # Réactiver pour prochaine attaque si compteur > 0
                if hero.temporary_buffs['elneha_wolf_remaining'] > 0:
                    hero.temporary_buffs['double_next_attack'] = True
                else:
                    # Plus d'utilisations, retirer le flag
                    hero.temporary_buffs.pop('double_next_attack', None)

            # Assaut furieux (Lame P-7-6) - permanent
            elif hero.temporary_buffs.get('assaut_furieux_permanent'):
                damage_multiplier_source = "lame_assaut_furieux"

            # Système nouveau (Férocité du loup - individual ability ou Attaque furtive Lame)
            elif hero.temporary_buffs.get('double_next_attack', False):
                # Consommer le buff après l'attaque
                hero.temporary_buffs.pop('double_next_attack', None)
                # Identifier la source selon le héros
                if hero.code == "P-1":  # Elneha
                    elneha_wolf_used = True
                    damage_multiplier_source = "elneha_wolf"
                elif hero.code == "P-7":  # Lame
                    damage_multiplier_source = "lame_furtivite"
                else:
                    damage_multiplier_source = "generic_double"
        
        combatant_name = getattr(hero, 'display_name', hero.name)

        # Vérifier plage de critiques étendue (Thordius Cri de guerre)
        is_critical = False
        if self.rules.criticals:
            if hasattr(hero, 'temporary_buffs') and 'expanded_crit_range' in hero.temporary_buffs:
                crit_range = hero.temporary_buffs['expanded_crit_range'].get('critical_rolls', [20])
                is_critical = attack_roll in crit_range
            else:
                is_critical = attack_roll == 20

        # Critique
        if is_critical:
            final_damage = damage_value * 2
            # Dégâts magiques ignorent la parade (règles officielles p.26) + Raishi Art martial
            ignore_parade = (damage_type == 'magical') or attack_modifiers.get('ignore_parade', False)
            is_magical_dmg = (damage_type == 'magical')
            damage_result = target.apply_damage_with_parade(final_damage, ignore_parade=ignore_parade, is_magical_damage=is_magical_dmg)

            total_attack = attack_roll + hero.get_total_precision()
            precision_bonus = hero.get_total_precision()
            damage_type_emoji = "✨" if damage_type == "magical" else "💥"

            log_parts = [f"{damage_type_emoji} CRITIQUE ! {combatant_name}[🎲{attack_roll}+{precision_bonus}={total_attack}] → {target.name}({damage_result['health_damage']})"]
            self._add_modifier_logs(log_parts, attack_modifiers, self._get_mark_bonus_for_target(hero, target), damage_value, base_damage, elneha_wolf_used)
            log.append(' '.join(log_parts))

            # 🔥 Log Cri de guerre si critique sur 18-19 (pas 20)
            if attack_roll in [18, 19] and hasattr(hero, 'temporary_buffs') and 'expanded_crit_range' in hero.temporary_buffs:
                log.append(f"  🔥 CRI DE GUERRE ! Critique sur {attack_roll} (plage étendue 18-19-20)")

            self._add_conversion_logs(log, attack_info, final_damage)

            # 🐺 Log multiplicateur de dégâts selon la source
            if damage_multiplier_source == "elneha_wolf":
                remaining = hero.temporary_buffs.get('elneha_wolf_remaining', 0)
                log.append(f"  🐺 Forme de loup activée ! Dégâts ×{attack_modifiers['damage_multiplier']:.0f} ({remaining} utilisations restantes)")
            elif damage_multiplier_source == "lame_furtivite":
                log.append(f"  🌑 Attaque furtive ! Dégâts ×{attack_modifiers['damage_multiplier']:.0f}")
            elif damage_multiplier_source == "lame_assaut_furieux":
                log.append(f"  ⚡💀 Assaut furieux ! Dégâts ×{attack_modifiers['damage_multiplier']:.0f}")
            elif damage_multiplier_source == "generic_double":
                log.append(f"  ⚔️ Dégâts multipliés ×{attack_modifiers['damage_multiplier']:.0f}")

            # NOUVEAU : Log résistance magique si active
            if damage_result.get('magical_resistance', 0) > 0:
                log.append(f"  ✨ Résistance magique : -{damage_result['magical_resistance']} dégât(s) (créature magique)")

            if damage_result['blocked_by_parade'] > 0:
                log.append(f"  🛡️ {damage_result['blocked_by_parade']} bloqués, {damage_result['health_damage']} aux PV")

            # NOUVEAU - Elneha formes animales : Log retour forme humaine si santé à 0
            if damage_result.get('form_reverted', False):
                log.append(f"  💫 {target.name} perd sa forme animale et reprend forme humaine ({target.current_health}/{target.health} PV)")

            # NOUVEAU - Châtiment divin : 2e frappe magique après attaque critique réussie
            if hasattr(hero, 'temporary_buffs') and 'chatiment_divin_active' in hero.temporary_buffs:
                chatiment_info = hero.temporary_buffs['chatiment_divin_active']
                chatiment_damage = chatiment_info['damage']
                # 2e frappe magique qui ignore parade (règles officielles)
                chatiment_result = target.apply_damage_with_parade(chatiment_damage, ignore_parade=True, is_magical_damage=True)
                log.append(f"  ⚡ CHÂTIMENT DIVIN ! +{chatiment_result['health_damage']} dégâts magiques (ignore parade)")
                # Consommer le buff après utilisation
                hero.temporary_buffs.pop('chatiment_divin_active', None)

            # NOUVEAU - Méditation (Raishi P-8-2) : 2e frappe avec dégâts / 2 après attaque réussie
            if hasattr(hero, 'temporary_buffs') and 'meditation_double_hit' in hero.temporary_buffs:
                meditation_info = hero.temporary_buffs['meditation_double_hit']
                second_hit_multiplier = meditation_info.get('second_hit_multiplier', 0.5)
                # Utiliser les dégâts de BASE (avant critique) divisés par 2
                meditation_damage = int(damage_value * second_hit_multiplier)
                # 2e frappe sur même cible (respecte parade)
                ignore_parade_meditation = (damage_type == 'magical') or attack_modifiers.get('ignore_parade', False)
                is_magical_dmg = (damage_type == 'magical')
                meditation_result = target.apply_damage_with_parade(meditation_damage, ignore_parade=ignore_parade_meditation, is_magical_damage=is_magical_dmg)
                log.append(f"  🧘 MÉDITATION ! 2e frappe sur {target.name} : {meditation_result['health_damage']} dégâts (dégâts / 2)")
                # Consommer le buff après utilisation
                hero.temporary_buffs.pop('meditation_double_hit', None)

            # NOUVEAU - Combo (Raishi P-8-5) : Stun ennemi 3 tours après attaque réussie
            if hasattr(hero, 'temporary_buffs') and 'combo_ready' in hero.temporary_buffs:
                combo_info = hero.temporary_buffs['combo_ready']
                stun_duration = combo_info.get('stun_duration', 3)

                # Effet stun Paume ouverte (AVEC vérification immunité)
                stunned = CharacterAbilitiesIntegration.apply_stun_with_immunity_check(
                    target, duration=stun_duration, source='raishi_paume_ouverte', log=log
                )
                if stunned:
                    log.append(f"  🥋 Paume ouverte ! {target.name} assommé pour {stun_duration} tours")
                else:
                    log.append(f"  (effet annulé)")

                # Consommer le buff après utilisation
                hero.temporary_buffs.pop('combo_ready', None)

            # NOUVEAU - Charge de taureau (Thordius P-5-3) : Stun ennemi 1 tour après attaque réussie
            if hasattr(hero, 'temporary_buffs') and 'charge_taureau_ready' in hero.temporary_buffs:
                charge_info = hero.temporary_buffs['charge_taureau_ready']
                stun_duration = charge_info.get('stun_duration', 1)

                # Effet stun Charge de taureau (AVEC vérification immunité)
                stunned = CharacterAbilitiesIntegration.apply_stun_with_immunity_check(
                    target, duration=stun_duration, source='thordius_charge_taureau', log=log
                )
                if stunned:
                    log.append(f"  🐂 CHARGE DE TAUREAU ! {target.name} assommé pour {stun_duration} tour")
                else:
                    log.append(f"  (effet annulé)")

                # Consommer le buff après utilisation
                hero.temporary_buffs.pop('charge_taureau_ready', None)

            if not target.is_alive():
                log.append(f"💀 {target.name} vaincu !")

            # NOUVEAU - Retirer furtivité de Lame si dégâts infligés
            self._remove_stealth_on_damage(hero, log)

            CharacterAbilitiesIntegration.enhance_hero_attack(hero, target, damage_result['health_damage'])

            # Return attack result for stats tracking
            return {
                'hit': True,
                'damage': damage_result['health_damage'],
                'critical': True,
                'critical_fail': False,
                'target': target
            }
        
        # Échec critique
        elif self.rules.criticals and attack_roll == 1:
            total_attack = attack_roll + hero.get_total_precision()
            damage_type_emoji = "✨" if damage_type == "magical" else "💥"
            precision_bonus = hero.get_total_precision()
            log.append(f"{damage_type_emoji} ÉCHEC ! {combatant_name}[🎲{attack_roll}+{precision_bonus}={total_attack}] attaque {target.name}")
            # 🐺 Multiplicateur gaspillé en cas d'échec critique
            if damage_multiplier_source == "elneha_wolf":
                log.append(f"  🐺 Forme de loup gaspillée par l'échec critique...")
            elif damage_multiplier_source == "lame_furtivite":
                log.append(f"  🌑 Attaque furtive gaspillée par l'échec critique...")
            elif damage_multiplier_source in ["lame_assaut_furieux", "generic_double"]:
                # Assaut furieux permanent n'est pas "gaspillé", juste inutile sur cet échec
                pass
            self._handle_critical_failure(hero, target, log, player_count)

            # Return attack result for stats tracking
            return {
                'hit': False,
                'damage': 0,
                'critical': False,
                'critical_fail': True,
                'target': target
            }
        
        # Attaque normale
        else:
            total_attack = attack_roll + hero.get_total_precision()
            precision_bonus = hero.get_total_precision()

            if total_attack >= target.defense:
                # Dégâts magiques ignorent la parade (règles officielles p.26) + Raishi Art martial
                ignore_parade = (damage_type == 'magical') or attack_modifiers.get('ignore_parade', False)
                is_magical_dmg = (damage_type == 'magical')
                damage_result = target.apply_damage_with_parade(damage_value, ignore_parade=ignore_parade, is_magical_damage=is_magical_dmg)
                damage_type_emoji = "✨" if damage_type == "magical" else "⚔️"

                log_parts = [f"{damage_type_emoji} {combatant_name}[🎲{attack_roll}+{precision_bonus}={total_attack}] → {target.name}({damage_result['health_damage']})"]
                self._add_modifier_logs(log_parts, attack_modifiers, self._get_mark_bonus_for_target(hero, target), damage_value, base_damage, elneha_wolf_used)
                log.append(' '.join(log_parts))

                self._add_conversion_logs(log, attack_info, damage_value)

                # 🐺 Log multiplicateur de dégâts selon la source
                if damage_multiplier_source == "elneha_wolf":
                    remaining = hero.temporary_buffs.get('elneha_wolf_remaining', 0)
                    log.append(f"  🐺 Forme de loup activée ! Dégâts ×{attack_modifiers['damage_multiplier']:.0f} ({remaining} utilisations restantes)")
                elif damage_multiplier_source == "lame_furtivite":
                    log.append(f"  🌑 Attaque furtive ! Dégâts ×{attack_modifiers['damage_multiplier']:.0f}")
                elif damage_multiplier_source == "lame_assaut_furieux":
                    log.append(f"  ⚡💀 Assaut furieux ! Dégâts ×{attack_modifiers['damage_multiplier']:.0f}")
                elif damage_multiplier_source == "generic_double":
                    log.append(f"  ⚔️ Dégâts multipliés ×{attack_modifiers['damage_multiplier']:.0f}")

                # NOUVEAU : Log résistance magique si active
                if damage_result.get('magical_resistance', 0) > 0:
                    log.append(f"  ✨ Résistance magique : -{damage_result['magical_resistance']} dégât(s) (créature magique)")

                if damage_result['blocked_by_parade'] > 0:
                    log.append(f"  🛡️ {damage_result['blocked_by_parade']} bloqués par parade, {damage_result['health_damage']} aux PV")
                else:
                    log.append(f"  💥 {damage_result['health_damage']} aux PV")

                # NOUVEAU - Elneha formes animales : Log retour forme humaine si santé à 0
                if damage_result.get('form_reverted', False):
                    log.append(f"  💫 {target.name} perd sa forme animale et reprend forme humaine ({target.current_health}/{target.health} PV)")

                # NOUVEAU - Châtiment divin : 2e frappe magique après attaque réussie
                if hasattr(hero, 'temporary_buffs') and 'chatiment_divin_active' in hero.temporary_buffs:
                    chatiment_info = hero.temporary_buffs['chatiment_divin_active']
                    chatiment_damage = chatiment_info['damage']
                    # 2e frappe magique qui ignore parade (règles officielles)
                    chatiment_result = target.apply_damage_with_parade(chatiment_damage, ignore_parade=True, is_magical_damage=True)
                    log.append(f"  ⚡ CHÂTIMENT DIVIN ! +{chatiment_result['health_damage']} dégâts magiques (ignore parade)")
                    # Consommer le buff après utilisation
                    hero.temporary_buffs.pop('chatiment_divin_active', None)

                # NOUVEAU - Méditation (Raishi P-8-2) : 2e frappe avec dégâts / 2 après attaque réussie
                if hasattr(hero, 'temporary_buffs') and 'meditation_double_hit' in hero.temporary_buffs:
                    meditation_info = hero.temporary_buffs['meditation_double_hit']
                    second_hit_multiplier = meditation_info.get('second_hit_multiplier', 0.5)
                    # Utiliser les dégâts de BASE divisés par 2
                    meditation_damage = int(damage_value * second_hit_multiplier)
                    # 2e frappe sur même cible (respecte parade)
                    ignore_parade_meditation = (damage_type == 'magical') or attack_modifiers.get('ignore_parade', False)
                    is_magical_dmg = (damage_type == 'magical')
                    meditation_result = target.apply_damage_with_parade(meditation_damage, ignore_parade=ignore_parade_meditation, is_magical_damage=is_magical_dmg)
                    log.append(f"  🧘 MÉDITATION ! 2e frappe sur {target.name} : {meditation_result['health_damage']} dégâts (dégâts / 2)")
                    # Consommer le buff après utilisation
                    hero.temporary_buffs.pop('meditation_double_hit', None)

                # NOUVEAU - Combo (Raishi P-8-5) : Stun ennemi 3 tours après attaque réussie
                if hasattr(hero, 'temporary_buffs') and 'combo_ready' in hero.temporary_buffs:
                    combo_info = hero.temporary_buffs['combo_ready']
                    stun_duration = combo_info.get('stun_duration', 3)

                    # Effet stun Paume ouverte (AVEC vérification immunité)
                    stunned = CharacterAbilitiesIntegration.apply_stun_with_immunity_check(
                        target, duration=stun_duration, source='raishi_paume_ouverte', log=log
                    )
                    if stunned:
                        log.append(f"  🥋 Paume ouverte ! {target.name} assommé pour {stun_duration} tours")
                    else:
                        log.append(f"  (effet annulé)")

                    # Consommer le buff après utilisation
                    hero.temporary_buffs.pop('combo_ready', None)

                # NOUVEAU - Charge de taureau (Thordius P-5-3) : Stun ennemi 1 tour après attaque réussie
                if hasattr(hero, 'temporary_buffs') and 'charge_taureau_ready' in hero.temporary_buffs:
                    charge_info = hero.temporary_buffs['charge_taureau_ready']
                    stun_duration = charge_info.get('stun_duration', 1)

                    # Effet stun Charge de taureau (AVEC vérification immunité)
                    stunned = CharacterAbilitiesIntegration.apply_stun_with_immunity_check(
                        target, duration=stun_duration, source='thordius_charge_taureau', log=log
                    )
                    if stunned:
                        log.append(f"  🐂 CHARGE DE TAUREAU ! {target.name} assommé pour {stun_duration} tour")
                    else:
                        log.append(f"  (effet annulé)")

                    # Consommer le buff après utilisation
                    hero.temporary_buffs.pop('charge_taureau_ready', None)

                if not target.is_alive():
                    log.append(f"💀 {target.name} vaincu !")

                # NOUVEAU - Retirer furtivité de Lame si dégâts infligés
                self._remove_stealth_on_damage(hero, log)

                CharacterAbilitiesIntegration.enhance_hero_attack(hero, target, damage_result['health_damage'])

                hero.action_taken_this_turn = True

                # Return attack result for stats tracking
                return {
                    'hit': True,
                    'damage': damage_result['health_damage'],
                    'parade_used': damage_result.get('parade_tokens_used', 0),
                    'critical': False,
                    'critical_fail': False,
                    'target': target
                }
            else:
                damage_type_emoji = "✨" if damage_type == "magical" else "⚔️"
                precision_bonus = hero.get_total_precision()
                log.append(f"{damage_type_emoji} {combatant_name}[🎲{attack_roll}+{precision_bonus}={total_attack}] vs DEF[{target.defense}] → Échec")
                # 🐺 Multiplicateur gaspillé en cas d'échec
                if damage_multiplier_source == "elneha_wolf":
                    log.append(f"  🐺 Forme de loup gaspillée par l'échec...")
                elif damage_multiplier_source == "lame_furtivite":
                    log.append(f"  🌑 Attaque furtive gaspillée par l'échec...")
                elif damage_multiplier_source in ["lame_assaut_furieux", "generic_double"]:
                    # Assaut furieux permanent n'est pas "gaspillé"
                    pass
                CharacterAbilitiesIntegration.enhance_hero_attack(hero, target, 0)

                hero.action_taken_this_turn = True

                # Return attack result for stats tracking
                return {
                    'hit': False,
                    'damage': 0,
                    'parade_used': 0,
                    'critical': False,
                    'critical_fail': False,
                    'target': target
                }

    def _get_mark_bonus_for_target(self, hero, target) -> int:
        """
        Calcule le bonus de dégâts contre une cible marquée par Kraor
        IMPORTANT: Le bonus s'applique à TOUS les alliés qui attaquent la cible marquée
        CORRIGÉ: Utilise status_effects/marks existants au lieu de is_marked/marked_by
        """
        # CORRECTION: Tous les alliés bénéficient du bonus, pas seulement Kraor
        # La capacité dit: "Tous les dégâts infligés sur ce dernier, par n'importe quel membre du groupe"

        # Vérifier dans status_effects (écrit par kraor.py)
        if hasattr(target, 'status_effects') and target.status_effects:
            if 'kraor_marked' in target.status_effects:
                mark_info = target.status_effects['kraor_marked']
                return mark_info.get('bonus_damage', 2)

        # Fallback: vérifier dans marks
        if hasattr(target, 'marks') and target.marks:
            if 'kraor_hunter_mark' in target.marks:
                mark_info = target.marks['kraor_hunter_mark']
                return mark_info.get('bonus_damage', 2)

        return 0

    def _remove_stealth_on_damage(self, hero, log: list):
        """
        Retire le statut de furtivité de Lame quand il inflige des dégâts
        (Règle: Furtivité se termine si Lame attaque ou utilise une capacité qui inflige des dégâts)
        """
        if not hasattr(hero, 'status_effects'):
            return

        if 'invisible' in hero.status_effects:
            stealth_data = hero.status_effects['invisible']
            # Vérifier si c'est la furtivité de Lame (source = lame_furtivite) et qu'elle expire sur dégâts
            if isinstance(stealth_data, dict) and stealth_data.get('source') == 'lame_furtivite':
                if stealth_data.get('expires_on_damage_dealt', False):
                    del hero.status_effects['invisible']
                    log.append(f"  🌑 Furtivité terminée - {hero.name} redevient visible (dégâts infligés)")

    def _handle_critical_failure(self, attacker, target, log: list, player_count: int):
        """Gère l'échec critique avec riposte de l'ennemi (ignore la parade)"""
        try:
            # Récupérer les dégâts de l'ennemi (utilise combat_player_count figé)
            enemy_stats = target.get_combat_stats()
            counter_damage = enemy_stats['damage']

            # Appliquer les dégâts DIRECTEMENT aux PV (ignore parade selon règles p.26)
            old_health = attacker.current_health
            attacker.current_health = max(0, attacker.current_health - counter_damage)
            actual_damage = old_health - attacker.current_health

            log.append(f"    ⚡ {target.name} riposte immédiatement ! {actual_damage} dégâts (ignore parade)")

            if not attacker.is_alive():
                log.append(f"    💀 {attacker.name} vaincu par la riposte !")
        except Exception as e:
            log.append(f"    ⚠️ Erreur riposte échec critique: {str(e)}")

    def _add_modifier_logs(self, log_parts: list, attack_modifiers: dict, mark_bonus: int, damage_value: int, base_damage: int, elneha_wolf_used: bool = False):
        """Ajoute les logs des modificateurs d'attaque - MODIFIÉ pour inclure forme de loup"""
        modifiers = []
        
        if attack_modifiers['damage_bonus'] > 0:
            modifiers.append(f"+{attack_modifiers['damage_bonus']}bonus")
        if attack_modifiers['damage_multiplier'] > 1.0:
            modifiers.append(f"x{attack_modifiers['damage_multiplier']}")
        if mark_bonus > 0:
            modifiers.append(f"+{mark_bonus}marquage")
        # 🐺 NOUVEAU: Indicateur forme de loup dans les modificateurs
        if elneha_wolf_used:
            modifiers.append("🐺x2loup")
        
        if modifiers:
            log_parts.append(f"[{','.join(modifiers)}]")

    def _add_conversion_logs(self, log: list, attack_info: dict, damage_value: int = 0):
        """Ajoute les logs de conversion d'objets spéciaux"""
        conversion_log = self._get_conversion_log(attack_info, damage_value)
        if conversion_log:
            log.append(f"  {conversion_log}")

    def _get_conversion_log(self, attack_info: dict, damage_value: int = 0) -> str:
        """Génère le log de conversion selon l'objet spécial équipé"""
        if attack_info.get('conversion_source') == 'gemme_pouvoir':
            return "💎 Gemme de pouvoir: Attaque convertie en magie (forme animale)"
        elif attack_info.get('conversion_source') == 'lyre_phoenix':
            return f"🎭 Lyre phoenix: Attaque convertie → {damage_value} dégâts magiques"
        return ""
    
    def set_combat_context(self, heroes: list, enemies: list):
        """Définit le contexte de combat pour les capacités individuelles"""
        self._current_heroes = [h for h in heroes if h.is_alive()]
        self._current_alive_enemies = [e for e in enemies if e.is_alive()]
        
        self.ability_effects_manager._current_heroes = self._current_heroes
        self.ability_effects_manager._current_alive_enemies = self._current_alive_enemies
    
    def update_alive_enemies(self, enemies: list):
        """Met à jour la liste des ennemis vivants"""
        self._current_alive_enemies = [e for e in enemies if e.is_alive()]
        self.ability_effects_manager._current_alive_enemies = self._current_alive_enemies

    def use_ability(self, hero, ability, log: list) -> bool:
        """Utilise une capacité avec le système modulaire d'effets + contexte ennemis"""
        can_use, reason = self.spell_manager.can_use_magical_ability(hero, ability)
        if not can_use:
            combatant_name = getattr(hero, 'display_name', hero.name)
            log.append(f"❌ {combatant_name} ne peut pas utiliser {ability.name}: {reason}")
            return False
        
        self.ability_effects_manager.apply_turn_start_effects(hero, log)
        
        context = {
            'alive_enemies': self._current_alive_enemies,
            'current_enemies': self._current_alive_enemies,
            'enemies': self._current_alive_enemies,
            'heroes': self._current_heroes,
            'current_heroes': self._current_heroes,
            'spell_manager': self.spell_manager,
            'log': log,
            'player_count': len(self._current_heroes)
        }
        
        self.ability_effects_manager._current_alive_enemies = self._current_alive_enemies
        self.ability_effects_manager._current_heroes = self._current_heroes
        
        effects_applied = self.ability_effects_manager.apply_ability_effects(hero, ability, log, context)
        
        hero.action_taken_this_turn = True
        return True

    def try_health_potion(self, hero, log: list):
        """IA utilise potions intelligemment"""
        if not hasattr(hero, 'use_health_potion'):
            return
        
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
            # Dégâts magiques des pets ignorent la parade (règles officielles p.26)
            ignore_parade = (damage_type == 'magical')
            is_magical_dmg = (damage_type == 'magical')
            damage_result = target.apply_damage_with_parade(damage_value, ignore_parade=ignore_parade, is_magical_damage=is_magical_dmg)
            damage_type_emoji = "✨" if damage_type == "magical" else "🐾"

            log.append(f"{damage_type_emoji} {pet_name}[🎲{attack_roll}+{pet.precision}={total_attack}] → {target.name}({damage_result['health_damage']})")

            # NOUVEAU : Log résistance magique si active
            if damage_result.get('magical_resistance', 0) > 0:
                log.append(f"    [✨ Résistance magique: -{damage_result['magical_resistance']} dégât(s)]")

            if damage_result['blocked_by_parade'] > 0:
                log.append(f"    [{damage_result['blocked_by_parade']}🛡️ bloqué]")
            
            if not target.is_alive():
                log.append(f"    💀 {target.name} vaincu !")
        else:
            damage_type_emoji = "✨" if damage_type == "magical" else "🐾"
            log.append(f"{damage_type_emoji} {pet_name}[🎲{attack_roll}+{pet.precision}={total_attack}] vs DEF[{target.defense}] → Échec")

    def smart_pet_ability_usage(self, pet, log: list) -> bool:
        """IA tactique pour Pets"""
        if not hasattr(pet, 'abilities') or not pet.abilities:
            return False
        
        enemies = self._current_alive_enemies
        if not enemies:
            return False
        
        usable_abilities = [a for a in pet.abilities if self.spell_manager.can_use_magical_ability(pet, a)[0]]
        if not usable_abilities:
            return False
        
        # Soin si santé basse
        if pet.current_health / pet.get_total_health() < 0.5:
            healing_abilities = [a for a in usable_abilities if 'soin' in a.description.lower()]
            if healing_abilities:
                return self.use_ability(pet, healing_abilities[0], log)
        
        # Zone si 3+ ennemis
        if len(enemies) >= 3:
            aoe_abilities = [a for a in usable_abilities if 'tous les adversaires' in a.description.lower()]
            if aoe_abilities:
                return self.use_ability(pet, aoe_abilities[0], log)
        
        # Attaque offensive
        offensive = [a for a in usable_abilities if any(word in a.description.lower() for word in ['dégât', 'inflige'])]
        if offensive:
            return self.use_ability(pet, offensive[0], log)
        
        # Première capacité utilisable
        if usable_abilities:
            return self.use_ability(pet, usable_abilities[0], log)
        
        return False
    
    def use_summon_ability(self, hero, ability, log: list, active_pets: list) -> bool:
        """Utilise une capacité d'invocation"""
        active_pets[:] = [p for p in active_pets if not (hasattr(p, 'owner_code') and p.owner_code == hero.code)]
        
        new_pet = hero.summon_pet()
        if new_pet:
            if hasattr(new_pet, 'start_new_combat'):
                new_pet.start_new_combat()
            
            self.spell_manager.initialize_spells(new_pet)
            CharacterAbilitiesIntegration.add_required_attributes(new_pet)
            active_pets.append(new_pet)
            
            pet_name = getattr(new_pet, 'display_name', 'Pet')
            log.append(f"🔮 {hero.name} utilise {ability.name}")
            log.append(f"  ✨ {pet_name} invoqué !")
            log.append(f"    (Précision: {new_pet.precision}, Dégâts magiques: {new_pet.get_total_magical_damage()}, Santé: {new_pet.health})")
            
            hero.action_taken_this_turn = True
            return True
        
        return False
    
    def try_ability_with_summon(self, hero, enemies: list, log: list, active_pets: list) -> bool:
        """
        IA capacités intelligente + gestion invocations + transformations Elneha
        CORRIGÉ: Logique tactique avec buffing prioritaire
        """
        self._current_alive_enemies = [e for e in enemies if e.is_alive()]
        self._current_heroes = [hero]
        
        if not hasattr(hero, 'get_available_abilities'):
            return False
        
        available = hero.get_available_abilities()
        if not available:
            return False
        
        # Priorité 1 : Invocation si pas de Pet actuel pour Kraor
        if hero.code == "P-4" and hero.can_summon_pet():
            current_pets = [p for p in active_pets if hasattr(p, 'owner_code') and p.owner_code == hero.code]
            if not current_pets:
                summon_ability = next((a for a in available if getattr(a, 'ability_number', 0) == 99), None)
                if summon_ability:
                    return self.use_summon_ability(hero, summon_ability, log, active_pets)
        
        # Filtrer les capacités utilisables
        usable_abilities = []
        for ability in available:
            if getattr(ability, 'ability_number', 0) == 99:
                continue
            
            can_use, reason = self.spell_manager.can_use_magical_ability(hero, ability)
            if can_use:
                usable_abilities.append(ability)
        
        if not usable_abilities:
            return False
        
        # LOGIQUE IA CORRIGÉE
        
        # PRIORITÉ ABSOLUE : Transformations Elneha (buffs permanents)
        if hasattr(hero, 'current_form') and hero.current_form == 'human':  # Pas encore transformé
            transform_abilities = [a for a in usable_abilities 
                      if 'forme' in a.name.lower() and 
                      hasattr(a, 'uses_remaining_combat') and 
                      a.uses_remaining_combat is not None and 
                      a.uses_remaining_combat > 0]
            if transform_abilities:
                # ANALYSE TACTIQUE DE LA SITUATION
                health_percent = (hero.current_health / hero.get_total_health()) * 100
                current_parade = getattr(hero, 'current_parade_tokens', 0)
                max_parade = getattr(hero, 'max_parade_tokens', 0)
                
                # Évaluer la menace ennemie
                total_enemy_damage = sum(getattr(e, 'get_damage_info', lambda x: {'damage': 5})(2).get('damage', 5) 
                                       for e in self._current_alive_enemies[:3])  # Max 3 premiers ennemis
                
                # DÉCISION TACTIQUE INTELLIGENTE
                bear_form = next((a for a in transform_abilities if 'ours' in a.name.lower()), None)
                wolf_form = next((a for a in transform_abilities if 'loup' in a.name.lower()), None)
                
                # Priorité OURS si :
                # - PV < 70% (besoin défense) 
                # - Parade épuisée (current_parade == 0)
                # - Ennemis font beaucoup de dégâts (> 15 total)
                should_go_bear = (health_percent < 70 or 
                                 current_parade == 0 or 
                                 total_enemy_damage > 15)
                
                if bear_form and should_go_bear:
                    return self.use_ability(hero, bear_form, log)
                elif wolf_form:  # Sinon forme loup pour DPS
                    return self.use_ability(hero, wolf_form, log)
                elif bear_form:  # Fallback sur ours si loup indisponible
                    return self.use_ability(hero, bear_form, log)
        
        # 1. Soin d'alliés SI il y a des alliés blessés
        allies_need_healing = any(ally.current_health < ally.get_total_health() 
                                for ally in self._current_heroes if ally != hero and ally.is_alive())
        if allies_need_healing:
            heal_abilities = [a for a in usable_abilities if 'soin' in a.name.lower()]
            if heal_abilities:
                return self.use_ability(hero, heal_abilities[0], log)
        
        # 2. Auto-soin si PV < 30%
        health_percent = (hero.current_health / hero.get_total_health()) * 100
        if health_percent < 30:
            self_heal_abilities = [a for a in usable_abilities if 'soin' in a.name.lower() 
                                 and ('soi' in a.description.lower() or 'personnage' not in a.description.lower())]
            if self_heal_abilities:
                return self.use_ability(hero, self_heal_abilities[0], log)
        
        # 3. Zone si 3+ ennemis
        if len(enemies) >= 3:
            aoe_abilities = [a for a in usable_abilities if 'tous les adversaires' in a.description.lower()]
            if aoe_abilities:
                return self.use_ability(hero, aoe_abilities[0], log)
        
        # 4. Capacités défensives si santé < 70%
        if health_percent < 70:
            defensive_abilities = [a for a in usable_abilities if any(word in a.description.lower() 
                                 for word in ['bouclier', 'défense', 'protection', 'parade'])]
            if defensive_abilities:
                return self.use_ability(hero, defensive_abilities[0], log)
        
        # 5. Attaque offensive seulement si ennemis présents
        if enemies and len(enemies) > 0:
            offensive = [a for a in usable_abilities if any(word in a.description.lower() 
                        for word in ['dégât', 'inflige', 'attaque', 'frappe'])]
            if offensive:
                return self.use_ability(hero, offensive[0], log)
        
        # PLUS D'USAGE AVEUGLE - Si aucune logique ne s'applique, ne rien faire
        return False

    def enemy_attack(self, enemy, heroes: list, player_count: int, log: list, active_pets: list, manual_target=None):
        """Attaque ennemi - cible l'équipe (Héros + Pets) selon règles + FORME D'OURS via temporary_buffs

        Args:
            manual_target: Si fourni, cible spécifique (bypass sélection automatique IA)

        Returns:
            dict: {'hit': bool, 'damage': int, 'target': Character} ou None si pas de cible
        """
        # Les ennemis peuvent cibler héros ET pets
        all_targets = heroes + active_pets
        alive_targets = [t for t in all_targets if t.is_alive()]

        if not alive_targets:
            return None

        # Récupérer stats de combat (utilise combat_player_count figé)
        enemy_stats = enemy.get_combat_stats()
        damage = enemy_stats['damage']

        # Sélection de cible : manuelle OU automatique (IA)
        if manual_target:
            target = manual_target
        else:
            target = self._select_enemy_target(enemy, alive_targets)

        # NOUVEAU - Si aucune cible disponible (tous héros invisibles), ennemi ne peut pas attaquer
        if target is None:
            enemy_name = getattr(enemy, 'display_name', enemy.name)
            log.append(f"👹 {enemy_name} cherche une cible...")
            log.append(f"  👻 Aucune cible visible ! L'attaque échoue (tous les héros sont invisibles)")
            return {'hit': False, 'damage': 0, 'parade_used': 0, 'target': None}

        enemy_name = getattr(enemy, 'display_name', enemy.name)
        target_name = getattr(target, 'display_name', target.name)
        
        # 🐻 NOUVELLE MÉCANIQUE: FORME D'OURS - IGNORE PROCHAINE ATTAQUE via temporary_buffs
        if (hasattr(target, 'temporary_buffs') and
            target.temporary_buffs.get('ignore_next_attack', False)):
            target.temporary_buffs['ignore_next_attack'] = False
            log.append(f"👹 {enemy_name} attaque {target_name}")
            log.append(f"  🐻 {target_name} ignore l'attaque grâce à sa forme d'ours !")
            return {'hit': False, 'damage': 0, 'parade_used': 0, 'target': target}
        
        # Attaque normale
        # Dégâts magiques des ennemis ignorent la parade (règles officielles p.26)
        # CORRECTION: Seul has_magical_damage fait ignorer la parade
        has_magical_dmg = getattr(enemy, 'has_magical_damage', False)
        ignore_parade = has_magical_dmg
        damage_result = target.apply_damage_with_parade(damage, ignore_parade=ignore_parade)

        damage_type_emoji = "✨" if ignore_parade else "👹"
        log.append(f"{damage_type_emoji} {enemy_name} attaque {target_name}: {damage} dégâts")

        # NOUVEAU : Log explicite si dégâts magiques (ignore parade)
        if has_magical_dmg:
            log.append(f"  ✨ Dégâts magiques ! La créature ignore les jetons de parade")

        # NOUVEAU : Log Aura sacrée si active
        if damage_result.get('aura_reduction', 0) > 0:
            log.append(f"  ✨ Aura sacrée : -{damage_result['aura_reduction']} dégât(s) ignoré(s)")

        if damage_result['blocked_by_parade'] > 0:
            log.append(f"  🛡️ {damage_result['blocked_by_parade']} bloqués par parade, {damage_result['health_damage']} aux PV")
        else:
            log.append(f"  💥 {damage_result['health_damage']} aux PV")

        if not target.is_alive():
            log.append(f"  💀 {target_name} vaincu !")

        # Return attack result for stats tracking
        return {
            'hit': True,
            'damage': damage_result['health_damage'],
            'parade_used': damage_result.get('parade_tokens_used', 0),
            'target': target
        }

    def _select_enemy_target(self, enemy, alive_targets: list):
        """Sélection de cible selon les règles d'IA tactique (exclut héros invisibles)"""
        if not alive_targets:
            return None

        # NOUVEAU - Filtrer les héros invisibles/non-ciblables (Lame Furtivité, etc.)
        targetable_heroes = []
        for target in alive_targets:
            is_untargetable = False

            # Vérifier si le héros a un statut 'untargetable'
            if hasattr(target, 'status_effects') and target.status_effects:
                for effect_name, effect_data in target.status_effects.items():
                    if isinstance(effect_data, dict) and effect_data.get('type') == 'untargetable':
                        is_untargetable = True
                        break

            if not is_untargetable:
                targetable_heroes.append(target)

        # Si tous les héros sont invisibles, retourner None (ennemi ne peut pas attaquer)
        if not targetable_heroes:
            return None

        targets_with_parade = [(t, getattr(t, 'current_parade_tokens', 0)) for t in targetable_heroes]
        min_parade = min(targets_with_parade, key=lambda x: x[1])[1]
        lowest_parade_targets = [t for t, p in targets_with_parade if p == min_parade]

        if len(lowest_parade_targets) > 1:
            return min(lowest_parade_targets, key=lambda t: t.current_health)

        return lowest_parade_targets[0]