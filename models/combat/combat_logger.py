"""
Gestionnaire des logs et formatage pour le moteur de combat
Extrait de combat_engine.py pour modularité
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
        
        # Formater héros + pets
        allies_status = []
        for ally in heroes + active_pets:
            name = getattr(ally, 'display_name', ally.name)
            current_hp = ally.current_health
            max_hp = ally.get_total_health()
            current_parade = getattr(ally, 'current_parade_tokens', 0)
            max_parade = getattr(ally, 'max_parade_tokens', 0)
            
            # Indicateurs de santé
            health_percent = (current_hp / max_hp) * 100
            if health_percent < 25:
                health_indicator = "🔴"  # Critique
            elif health_percent < 50:
                health_indicator = "🟡"  # Blessé
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
            
            # Indicateurs de santé
            health_percent = (current_hp / max_hp) * 100
            if health_percent < 25:
                health_indicator = "🔴"  # Critique
            elif health_percent < 50:
                health_indicator = "🟡"  # Blessé
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
        """Initialise héros pour combat + détection objets spéciaux + gestion sorts centralisée"""
        for hero in heroes:
            hero.reset_health()
            
            # Initialisation centralisée des sorts
            self.spell_manager.initialize_spells(hero)
            
            # Initialise système parade
            hero._update_parade_from_equipment()
            hero.refresh_parade_tokens()
            
            # Log objets spéciaux détectés
            special_effects = hero.get_special_equipment_effects()
            active_effects = [name for name, active in special_effects.items() if active]
            if active_effects:
                log.append(f"✨ {hero.name} - Objets spéciaux: {', '.join(active_effects)}")
            
            # Log sorts disponibles
            current_spells = self.spell_manager.get_current_spells(hero)
            if current_spells > 0:
                log.append(f"🔮 {hero.name} - Sorts disponibles: {current_spells}")
            
            # Capacités avec protection builds custom
            if self.abilities_enabled and hasattr(hero, 'start_new_combat'):
                hero.start_new_combat()
                self._setup_abilities(hero, log)
    
    def prepare_enemies(self, enemies: list, player_count: int, log: list):
        """Initialise ennemis avec système parade + sorts centralisés"""
        for enemy in enemies:
            enemy.initialize_for_combat(player_count)
            
            # Initialiser sorts pour ennemis (généralement 0)
            self.spell_manager.initialize_spells(enemy)
            
            # Log parade si présente
            if enemy.max_parade_tokens > 0:
                log.append(f"🛡️ {enemy.name} : {enemy.max_parade_tokens} jetons parade")
    
    def log_start(self, heroes: list, enemies: list, log: list):
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
    
    def _setup_abilities(self, hero, log: list):
        """Configure capacités : custom OU aléatoire - VERSION ANTI-CRASH"""
        if not hasattr(hero, 'abilities') or not hero.abilities:
            return
        
        import random
        from utils.data_loader import safe_randint
        
        # Protection BUILDS CUSTOM
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
        
        # Génération aléatoire sécurisée
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