# combat_logger.py
"""
Gestionnaire des logs et formatage pour le moteur de combat
Extrait de combat_engine.py pour modularitÃ©
"""

import streamlit as st

class CombatLogger:
    """Gestion des logs et formatage du combat"""
    
    def __init__(self, spell_manager):
        self.spell_manager = spell_manager
        self.abilities_enabled = True
        try:
            from models.abilities import Ability
        except ImportError:
            self.abilities_enabled = False
    
    def format_status_line(self, heroes: list, enemies: list, active_pets: list = None) -> str:
        """Formate une ligne de status avec PV, parade et indicateurs critiques"""
        active_pets = active_pets or []
        
        # Formater hÃ©ros + pets
        allies_status = []
        for ally in heroes + active_pets:
            name = getattr(ally, 'display_name', ally.name)
            current_hp = ally.current_health
            max_hp = ally.get_total_health()
            current_parade = getattr(ally, 'current_parade_tokens', 0)
            max_parade = getattr(ally, 'max_parade_tokens', 0)
            
            # Indicateurs de santÃ©
            health_percent = (current_hp / max_hp) * 100
            if health_percent < 25:
                health_indicator = "🔴"  # Critique
            elif health_percent < 50:
                health_indicator = "🟡"  # BlessÃ©
            else:
                health_indicator = ""
            
            # Format: Nom(PV,parade) avec indicateurs
            if max_parade > 0:
                ally_status = f"{health_indicator}{name}({current_hp}/{max_hp}PV,{current_parade}🛡️)"
            else:
                ally_status = f"{health_indicator}{name}({current_hp}/{max_hp}PV)"
            
            allies_status.append(ally_status)
        
        # Formater ennemis
        enemies_status = []
        for enemy in enemies:
            if not enemy.is_alive():
                continue  # Skip ennemis morts
                
            current_hp = enemy.current_health
            max_hp = enemy.max_health
            current_parade = getattr(enemy, 'current_parade_tokens', 0)
            max_parade = getattr(enemy, 'max_parade_tokens', 0)
            
            # Indicateurs de santÃ©
            health_percent = (current_hp / max_hp) * 100
            if health_percent < 25:
                health_indicator = "🔴"  # Critique
            elif health_percent < 50:
                health_indicator = "🟡"  # BlessÃ©
            else:
                health_indicator = ""
            
            # Format ennemi
            if max_parade > 0:
                enemy_status = f"{health_indicator}{enemy.name}({current_hp}/{max_hp}PV,{current_parade}🛡️)"
            else:
                enemy_status = f"{health_indicator}{enemy.name}({current_hp}/{max_hp}PV)"
            
            enemies_status.append(enemy_status)
        
        # Assembler la ligne finale avec mise en valeur COULEUR
        allies_part = " | ".join(allies_status)
        enemies_part = " | ".join(enemies_status) if enemies_status else "Aucun ennemi"
        
        # VERSION AVEC COULEUR ET EMOJIS
        status_content = f"{allies_part} vs {enemies_part}"
        return f"📊 **STATUS:** {status_content}"
    
    def prepare_heroes(self, heroes: list, log: list):
        """Initialise hÃ©ros pour combat + dÃ©tection objets spÃ©ciaux + gestion sorts centralisÃ©e"""
        for hero in heroes:
            hero.reset_health()
            
            # Initialisation centralisÃ©e des sorts
            self.spell_manager.initialize_spells(hero)
            
            # Initialise systÃ¨me parade
            hero._update_parade_from_equipment()
            hero.refresh_parade_tokens()
            
            # Log objets spÃ©ciaux dÃ©tectÃ©s
            special_effects = hero.get_special_equipment_effects()
            active_effects = [name for name, active in special_effects.items() if active]
            if active_effects:
                log.append(f"✨ {hero.name} - Objets spÃ©ciaux: {', '.join(active_effects)}")
            
            # Log sorts disponibles
            current_spells = self.spell_manager.get_current_spells(hero)
            if current_spells > 0:
                log.append(f"🔮{hero.name} - Sorts disponibles: {current_spells}")
            
            # CapacitÃ©s avec protection builds custom
            if self.abilities_enabled and hasattr(hero, 'start_new_combat'):
                hero.start_new_combat()
                self._setup_abilities(hero, log)
    
    def prepare_enemies(self, enemies: list, player_count: int, log: list):
        """Initialise ennemis avec systÃ¨me parade + sorts centralisÃ©s"""
        for enemy in enemies:
            enemy.initialize_for_combat(player_count)
            
            # Initialiser sorts pour ennemis (gÃ©nÃ©ralement 0)
            self.spell_manager.initialize_spells(enemy)
            
            # Log parade si prÃ©sente
            if enemy.max_parade_tokens > 0:
                log.append(f"🛡️¸ {enemy.name} : {enemy.max_parade_tokens} jetons parade")
    
    def log_start(self, heroes: list, enemies: list, log: list):
        """Log initial avec info parade + objets spÃ©ciaux + sorts"""
        log.append(f"Héros: {', '.join([h.name for h in heroes])}")
        log.append(f"Ennemis: {', '.join([e.name for e in enemies])}")
        
        # Info parade
        heroes_with_parade = [h for h in heroes if h.max_parade_tokens > 0]
        if heroes_with_parade:
            parade_info = [f"{h.name}({h.max_parade_tokens}🛡️)" for h in heroes_with_parade]
            log.append(f"Parade héros: {', '.join(parade_info)}")
        
        # Info objets spÃ©ciaux
        heroes_with_special = []
        for hero in heroes:
            effects = hero.get_special_equipment_effects()
            active = [name for name, active in effects.items() if active]
            if active:
                # Ajout info formes pour Druide
                if hero.code == "P-1" and hasattr(hero, 'current_form'):
                    form_info = f"forme:{hero.current_form}"
                    active.append(form_info)
                heroes_with_special.append(f"{hero.name}({','.join(active)})")
        
        if heroes_with_special:
            log.append(f"Objets spéciaux: {', '.join(heroes_with_special)}")
        
        log.append("")
    
    def _setup_abilities(self, hero, log: list):
        """
        CORRIGÉ - Builds par défaut = toutes capacités, pas de modification aléatoire
        """
        if not hasattr(hero, 'abilities') or not hero.abilities:
            return
        
        import random
        from utils.data_loader import safe_randint
        
        # Protection BUILDS CUSTOM
        custom_builds = st.session_state.get('custom_builds', {})
        hero_build = custom_builds.get(hero.code, {})
        
        if hero_build.get('abilities_custom', False) and 'abilities' in hero_build:
            # Utilise capacités choisies
            custom_abilities = hero_build['abilities']
            for ability in hero.abilities:
                ability.is_unlocked = ability.ability_number in custom_abilities
            
            unlocked = [a for a in hero.abilities if a.is_unlocked]
            log.append(f"🎯 {hero.name}: {len(unlocked)} capacités custom")
        else:
            # 🔧 CORRECTION: BUILDS PAR DÉFAUT = TOUTES CAPACITÉS
            for ability in hero.abilities:
                ability.is_unlocked = True  # TOUTES débloquées
            
            unlocked = hero.abilities  # TOUTES les capacités
            log.append(f"🔧 {hero.name}: {len(unlocked)} capacités (build fixe)")
        
        # 🔧 CORRECTION: Utiliser name au lieu de generated_name
        if unlocked:
            abilities_names = [getattr(a, 'generated_name', a.name) for a in unlocked]
            log.append(f"   Capacités: {', '.join(abilities_names[:3])}{'...' if len(abilities_names) > 3 else ''}")

    def log_round_start(self, round_num: int, heroes: list, enemies: list, active_pets: list, log: list):
        """Log début de round avec status complet"""
        log.append(f"=== ROUND {round_num} ===")
        status_line = self.format_status_line(heroes, enemies, active_pets)
        log.append(status_line)
        log.append("")
    
    def log_turn_start(self, entity, log: list):
        """Log début de tour avec informations contextuelles"""
        entity_type = "🎭" if hasattr(entity, 'code') else "👹"
        log.append(f"{entity_type} Tour de {entity.name}")
    
    def log_ability_use(self, caster, ability, log: list):
        """Log utilisation de capacité avec détails"""
        ability_name = getattr(ability, 'generated_name', ability.name)
        log.append(f"✨ {caster.name} utilise {ability_name}")
    
    def log_potion_use(self, user, potion_type: str, heal_amount: int, log: list):
        """Log utilisation de potion"""
        potion_emoji = "🧪" if potion_type == "small" else "🍶"
        log.append(f"{potion_emoji} {user.name} boit une potion ({heal_amount} PV)")
    
    def log_death(self, entity, log: list):
        """Log mort d'une entité"""
        entity_type = "héros" if hasattr(entity, 'code') else "ennemi"
        log.append(f"💀 {entity.name} ({entity_type}) est vaincu !")
    
    def log_combat_end(self, winner: str, rounds: int, log: list):
        """Log fin de combat avec résultat"""
        log.append("")
        log.append("=== FIN DU COMBAT ===")
        if winner == "heroes":
            log.append("🏆 VICTOIRE des héros !")
        elif winner == "enemies":
            log.append("💀 DÉFAITE - Les ennemis l'emportent")
        else:
            log.append("⏰ MATCH NUL - Temps écoulé")
        log.append(f"Combat terminé en {rounds} rounds")
    
    def get_resource_summary(self, heroes: list, log: list):
        """Génère un résumé des ressources utilisées"""
        resource_info = []
        
        for hero in heroes:
            if not hero.is_alive():
                continue
                
            # Sorts utilisés
            if hasattr(self.spell_manager, 'get_spells_used'):
                used_spells = self.spell_manager.get_spells_used(hero)
                max_spells = self.spell_manager.get_max_spells(hero)
                if max_spells > 0:
                    remaining = max_spells - used_spells
                    resource_info.append(f"🔮 {hero.name}: {used_spells}/{max_spells} sorts ({remaining} restants)")
        
        if resource_info:
            log.extend(["", "📊 RESSOURCES UTILISÉES:"] + resource_info)