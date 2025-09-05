# debug_mode.py - Mode Debug Capacités pour Streamlit
"""
Mode debug intégré pour tester les capacités individuellement
À ajouter dans l'application Streamlit principale
VERSION CORRIGÉE - Fix réinitialisation uses_remaining_combat
"""

import streamlit as st
import traceback
from typing import List, Dict, Any, Optional
import sys
import os

def create_debug_tab():
    """
    Onglet debug principal - À ajouter dans l'app Streamlit
    """
    st.header("🔧 Mode Debug Capacités")
    st.markdown("Interface de test direct des capacités sans dépendre de l'IA")
    
    # Test des imports critiques d'abord
    if not _test_imports():
        st.error("❌ Imports critiques défaillants - Impossible d'utiliser le mode debug")
        return
    
    # Interface principale
    _create_debug_interface()

def _test_imports() -> bool:
    """Teste les imports critiques pour le debug"""
    try:
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        from models.character import Character, Enemy
        return True
    except ImportError as e:
        st.error(f"Erreur import: {e}")
        return False

def _create_debug_interface():
    """Interface principale du mode debug"""
    try:
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        
        # Statistiques registre
        total_registered = ABILITY_REGISTRY.get_registered_count()
        st.info(f"📊 Capacités disponibles: {total_registered}/59")
        
        if total_registered == 0:
            st.warning("⚠️ Aucune capacité enregistrée")
            return
        
        # Sélection héros et capacité
        heroes_data = _get_available_heroes_data()
        if not heroes_data:
            st.warning("⚠️ Aucun héros avec capacités trouvé")
            return
        
        # Interface de sélection
        col1, col2 = st.columns(2)
        
        with col1:
            # Créer mapping des noms de héros
            hero_names = {
                'P-1': 'P-1 Elneha',
                'P-2': 'P-2 Liarie', 
                'P-3': 'P-3 Atucan',
                'P-4': 'P-4 Kraor',
                'P-5': 'P-5 Thordius',
                'P-6': 'P-6 Stèphe',
                'P-7': 'P-7 Lame',
                'P-8': 'P-8 Raishi'
            }
            
            selected_hero_code = st.selectbox(
                "Héros", 
                options=list(heroes_data.keys()),
                format_func=lambda x: f"{hero_names.get(x, x)} ({len(heroes_data[x])} capacités)"
            )
        
        with col2:
            if selected_hero_code:
                abilities = heroes_data[selected_hero_code]
                ability_options = {f"{ab['name']} (#{ab['number']})": ab for ab in abilities}
                
                selected_ability_name = st.selectbox(
                    "Capacité", 
                    options=list(ability_options.keys())
                )
                selected_ability_data = ability_options[selected_ability_name]
        
        if selected_hero_code and selected_ability_name:
            _test_selected_ability(selected_hero_code, selected_ability_data)
    
    except Exception as e:
        st.error(f"💥 Erreur interface debug: {e}")
        st.code(traceback.format_exc())

def _get_available_heroes_data() -> Dict[str, List[Dict]]:
    """Récupère les données des héros disponibles"""
    try:
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        
        debug_info = ABILITY_REGISTRY.get_debug_info()
        heroes_data = {}
        
        for hero_code, hero_info in debug_info['heroes'].items():
            if hero_info['registered'] > 0:
                heroes_data[hero_code] = hero_info['abilities']
        
        return heroes_data
    
    except Exception as e:
        st.error(f"Erreur récupération héros: {e}")
        return {}

def _reset_ability_for_new_test(ability_instance):
    """Réinitialise une capacité pour un nouveau test debug"""
    if not ability_instance:
        return
    
    # Réinitialiser les utilisations restantes
    if hasattr(ability_instance, 'uses_per_combat') and ability_instance.uses_per_combat is not None:
        ability_instance.uses_remaining_combat = ability_instance.uses_per_combat
        st.info(f"🔄 Réinitialisation {ability_instance.name}: {ability_instance.uses_remaining_combat}/{ability_instance.uses_per_combat}")
    
    # Réinitialiser autres états si nécessaire
    if hasattr(ability_instance, 'combat_used'):
        ability_instance.combat_used = False

def _test_selected_ability(hero_code: str, ability_data: Dict):
    """Teste la capacité sélectionnée"""
    st.subheader(f"🧪 Test: {ability_data['name']}")
    
    # Informations capacité
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Héros:** {hero_code}")
        st.write(f"**Numéro:** {ability_data['number']}")
    
    with col2:
        # Récupérer instance pour infos détaillées
        try:
            from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
            ability_instance = ABILITY_REGISTRY.get_ability_instance(hero_code, ability_data['number'])
            
            if ability_instance:
                st.write(f"**Coût sorts:** {ability_instance.spell_cost}")
                
                # Afficher limitations par combat
                if hasattr(ability_instance, 'uses_per_combat'):
                    st.write(f"**Utilisations/combat:** {ability_instance.uses_per_combat}")
                    if hasattr(ability_instance, 'uses_remaining_combat'):
                        st.write(f"**Restantes:** {ability_instance.uses_remaining_combat}")
                elif hasattr(ability_instance, 'limitation') and ability_instance.limitation:
                    st.write(f"**Limitation:** {ability_instance.limitation}")
                else:
                    st.write("**Utilisations:** Illimitée")
            else:
                st.error("❌ Impossible de créer l'instance")
                return
        
        except Exception as e:
            st.error(f"Erreur récupération instance: {e}")
            return
    
    # Configuration du test
    st.subheader("⚙️ Configuration Test")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Utilisateur**")
        user_max_health = st.number_input("PV max", 1, 30, 15, key="user_max_health")
        user_current_health = st.number_input("PV actuels", 1, user_max_health, user_max_health, key="user_current_health")
        user_spells = st.number_input("Sorts", 0, 10, 5, key="user_spells")
        user_precision = st.number_input("Précision", 1, 15, 8, key="user_precision")
    
    with col2:
        st.write("**Alliés**")
        ally_count = st.number_input("Nombre", 0, 3, 1, key="ally_count")
        ally_max_health = st.number_input("PV max alliés", 1, 30, 10, key="ally_max_health")
        ally_current_health = st.number_input("PV actuels alliés", 1, ally_max_health, ally_max_health, key="ally_current_health")
    
    with col3:
        st.write("**Ennemis**")
        enemy_count = st.number_input("Nombre", 0, 5, 2, key="enemy_count")
        enemy_health = st.number_input("PV ennemis", 1, 50, 20, key="enemy_health")
    
    # Bouton de test
    if st.button("🧪 TESTER CAPACITÉ", type="primary"):
        _execute_ability_test(
            ability_instance, hero_code,
            user_max_health, user_current_health, user_spells, user_precision,
            ally_count, ally_max_health, ally_current_health,
            enemy_count, enemy_health
        )

def _execute_ability_test(ability_instance, hero_code: str, 
                         user_max_health: int, user_current_health: int, user_spells: int, user_precision: int,
                         ally_count: int, ally_max_health: int, ally_current_health: int,
                         enemy_count: int, enemy_health: int):
    """Exécute le test de la capacité EN UTILISANT LA MÊME API QUE L'APP PRINCIPALE"""
    
    st.subheader("🔍 Exécution du Test")
    
    try:
        # 🚨 FIX CRITIQUE - Réinitialiser la capacité AVANT le test
        _reset_ability_for_new_test(ability_instance)
        
        # Créer contexte de test
        user, allies, enemies, combat_state = _create_test_context(
            hero_code, user_max_health, user_current_health, user_spells, user_precision,
            ally_count, ally_max_health, ally_current_health, enemy_count, enemy_health
        )
        
        # 🎯 CORRECTION MAJEURE : Utiliser la MÊME API que l'app principale
        # Au lieu de : ability_instance.execute(user, targets, context, execution_log)
        # Utiliser : ability_effects_manager.apply_ability_effects() comme dans combat_actions.py
        
        from models.combat.spell_manager import SpellManager
        from models.combat.abilities import AbilityEffectsManager
        
        spell_manager = SpellManager()
        spell_manager.initialize_spells(user)
        for ally in allies:
            spell_manager.initialize_spells(ally)
        
        # Log pour execute()
        execution_log = []
        
        # 🔧 CRÉER LE MÊME CONTEXTE que combat_actions.py
        context = {
            'alive_enemies': enemies,      # Même clé que l'app principale
            'current_enemies': enemies,    # Même clé que l'app principale
            'enemies': enemies,           # Même clé que l'app principale
            'heroes': [user] + allies,    # Même clé que l'app principale
            'current_heroes': [user] + allies,  # Même clé que l'app principale
            'spell_manager': spell_manager,
            'log': execution_log,
            'player_count': len([user] + allies)
        }
        
        # ✅ UTILISER LA MÊME API QUE L'APP PRINCIPALE
        ability_effects_manager = AbilityEffectsManager(spell_manager)
        ability_effects_manager._current_alive_enemies = enemies
        ability_effects_manager._current_heroes = [user] + allies
        
        # ✅ FIX - Capturer l'état AVANT l'exécution
        with st.expander("📋 Phase 1: État AVANT", expanded=True):
            st.write("**Contexte:**")
            st.write(f"- Sorts disponibles: {getattr(user, 'current_spells', user.spells)}/{ability_instance.spell_cost}")
            st.write(f"- PV utilisateur: {user.current_health}/{user.health}")
            st.write(f"- SpellManager initialisé: User sorts = {spell_manager.get_current_spells(user)}")
            
            # Debug context
            st.write("**Context Debug:**")
            st.write(f"- Heroes: {len(context['heroes'])}")
            st.write(f"- Enemies: {len(context['alive_enemies'])}")
            
            st.write("**État AVANT exécution:**")
            _display_entities_state_enhanced(user, allies, enemies, spell_manager)
        
        # Phase 2: Exécution AVEC LA VRAIE API
        with st.expander("⚡ Phase 2: Exécution", expanded=True):
            try:
                # 🎯 UTILISER EXACTEMENT LA MÊME API QUE combat_actions.py:use_ability()
                # Vérification des prérequis (comme dans l'app)
                can_use, reason = spell_manager.can_use_magical_ability(user, ability_instance)
                if not can_use:
                    st.error(f"❌ Ne peut pas utiliser {ability_instance.name}: {reason}")
                    result = False
                else:
                    # Appel IDENTIQUE à l'app principale
                    result = ability_effects_manager.apply_ability_effects(
                        user, ability_instance, execution_log, context
                    )
                    
                    if result:
                        st.success("✅ apply_ability_effects() retourné True")
                        user.action_taken_this_turn = True  # Comme dans l'app
                    else:
                        st.warning("⚠️ apply_ability_effects() retourné False")
                
                # Afficher logs d'exécution
                if execution_log:
                    st.write("**Logs d'exécution:**")
                    for log_entry in execution_log:
                        st.write(f"• {log_entry}")
                
            except Exception as e:
                st.error(f"❌ Erreur apply_ability_effects(): {e}")
                result = False
        
        # Phase 3: Résultats APRÈS
        with st.expander("🎯 Phase 3: État APRÈS", expanded=True):
            st.write("**État APRÈS exécution:**")
            _display_entities_state_enhanced(user, allies, enemies, spell_manager)
            
            # Afficher utilisations restantes de la capacité
            st.write("**Capacité utilisée:**")
            if hasattr(ability_instance, 'uses_per_combat') and ability_instance.uses_per_combat is not None:
                # Vérifier les deux attributs possibles pour compatibilité
                remaining = getattr(ability_instance, 'uses_remaining_combat', None)
                if remaining is None:
                    remaining = getattr(ability_instance, 'uses_remaining', ability_instance.uses_per_combat)
                
                st.write(f"- **{ability_instance.name}:** {remaining}/{ability_instance.uses_per_combat} utilisations restantes")
                
                # Debug info si pas cohérent
                if remaining == ability_instance.uses_per_combat:
                    st.warning("⚠️ Utilisation non décomptée - vérifier l'implémentation")
            else:
                st.write(f"- **{ability_instance.name}:** Utilisations illimitées")
            
            # Logs de combat
            if combat_state.get("logs"):
                st.write("**Logs générés:**")
                for log in combat_state["logs"]:
                    st.write(f"• {log}")
        
        st.success("🎉 Test terminé")
    
    except Exception as e:
        st.error(f"💥 Erreur critique durant test: {e}")
        st.code(traceback.format_exc())

def _display_entities_state_enhanced(user, allies, enemies, spell_manager=None):
    """Affiche l'état avec attaque et parade pour débogage capacités"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Utilisateur:**")
        # API RÉELLE - current_health ne peut pas dépasser max
        max_health = user.get_total_health()
        current_health = min(user.current_health, max_health)
        st.write(f"PV: {current_health}/{max_health}")
        
        # SpellManager ou current_spells
        if spell_manager:
            current_spells = spell_manager.get_current_spells(user)
            max_spells = user.get_total_spells()
        else:
            current_spells = getattr(user, 'current_spells', None) or user.get_total_spells()
            max_spells = user.get_total_spells()
            
        st.write(f"Sorts: {current_spells}/{max_spells}")
        st.write(f"Précision: {user.get_total_precision()}")
        
        # ✅ NOUVEAU - Afficher attaque et parade pour debug
        # Attaque (peut être modifiée par capacités)
        base_attack = getattr(user, 'damage', 0)
        current_attack = getattr(user, 'current_attack', base_attack)
        if current_attack != base_attack:
            st.write(f"**Attaque: {current_attack}** (base: {base_attack})")
        else:
            st.write(f"Attaque: {current_attack}")
        
        # Parade (jetons)
        current_parade = getattr(user, 'current_parade_tokens', 0)
        max_parade = getattr(user, 'max_parade_tokens', 0)
        if max_parade > 0:
            st.write(f"**Parade: {current_parade}/{max_parade}** 🛡️")
        
        # Afficher transformations si Elneha
        if user.code == "P-1" and hasattr(user, 'current_form'):
            form_display = user.get_form_display() if hasattr(user, 'get_form_display') else user.current_form
            st.write(f"**Forme: {form_display}**")
    
    with col2:
        st.write("**Alliés:**")
        for i, ally in enumerate(allies):
            max_health = ally.get_total_health()
            current_health = min(ally.current_health, max_health)
            st.write(f"Allié {i+1}: {current_health}/{max_health} PV")
            
            # Attaque et parade des alliés
            current_attack = getattr(ally, 'current_attack', getattr(ally, 'damage', 0))
            current_parade = getattr(ally, 'current_parade_tokens', 0)
            max_parade = getattr(ally, 'max_parade_tokens', 0)
            
            attack_display = f"ATT: {current_attack}"
            if max_parade > 0:
                attack_display += f", 🛡️{current_parade}/{max_parade}"
            
            st.write(f"  {attack_display}")
    
    with col3:
        st.write("**Ennemis:**")
        for i, enemy in enumerate(enemies):
            st.write(f"Ennemi {i+1}: {enemy.current_health}/{enemy.max_health} PV")
            st.write(f"  DEF: {getattr(enemy, 'defense', 0)}")

def _create_test_context(hero_code: str, user_max_health: int, user_current_health: int, user_spells: int, user_precision: int,
                        ally_count: int, ally_max_health: int, ally_current_health: int, enemy_count: int, enemy_health: int):
    """Créé le contexte de test basé sur le vrai modèle Character"""
    
    from models.character import Character, Enemy
    
    # Créer utilisateur selon modèle Pydantic réel
    user = Character(
        code=hero_code,
        name="TestUser", 
        precision=user_precision,
        damage=4,
        spells=user_spells, 
        health=user_max_health
    )
    # Ajuster les PV actuels (pour héros blessé)
    user.current_health = user_current_health
    
    # FIX CRITIQUE #1: Initialiser current_spells explicitement
    user.current_spells = user_spells
    
    # Créer alliés
    allies = []
    for i in range(ally_count):
        ally = Character(
            code="P-1",
            name=f"Ally{i+1}", 
            precision=6,
            damage=2, 
            spells=3,
            health=ally_max_health
        )
        # Ajuster les PV actuels des alliés
        ally.current_health = ally_current_health
        ally.current_spells = ally.spells
        allies.append(ally)
    
    # Créer ennemis selon structure CSV
    enemies = []
    for i in range(enemy_count):
        enemy = Enemy(
            code=f"TEST-{i+1}",
            name=f"Enemy{i+1}", 
            defense=2,
            stats_by_players={
                2: {'damage': 3, 'health': enemy_health, 'defense': 1},
                3: {'damage': 3, 'health': enemy_health, 'defense': 1}, 
                4: {'damage': 3, 'health': enemy_health, 'defense': 1}
            },
            is_magical=False,
            has_magical_damage=False
        )
        enemy.initialize_for_combat(2)  # Initialise current_health
        enemies.append(enemy)
    
    combat_state = {
        "aliases": [user] + allies,
        "enemies": enemies,
        "turn": 1,
        "logs": []
    }
    
    return user, allies, enemies, combat_state

def _determine_targets(ability_instance, user, allies, enemies):
    """Détermine les cibles selon le type de capacité"""
    
    ability_name = ability_instance.name.lower()
    
    # Règles heuristiques pour déterminer les cibles
    if any(word in ability_name for word in ["soin", "guérison", "résurrection", "aura", "bouclier"]):
        return [user] + allies
    elif any(word in ability_name for word in ["attaque", "dégât", "châtiment", "jugement", "projectile"]):
        return enemies if enemies else [user]  # Fallback si pas d'ennemis
    else:
        # Capacité mixte ou inconnue - toutes les cibles
        return [user] + allies + enemies