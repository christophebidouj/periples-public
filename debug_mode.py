# debug_mode.py - Mode Debug Capacités pour Streamlit
"""
Mode debug intégré pour tester les capacités individuellement
À ajouter dans l'application Streamlit principale
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
            selected_hero_code = st.selectbox(
                "Héros", 
                options=list(heroes_data.keys()),
                format_func=lambda x: f"{x} ({len(heroes_data[x])} capacités)"
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
                if hasattr(ability_instance, 'limitation') and ability_instance.limitation:
                    st.write(f"**Limitation:** {ability_instance.limitation}")
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
        user_health = st.number_input("PV", 1, 30, 15, key="user_health")
        user_spells = st.number_input("Sorts", 0, 10, 5, key="user_spells")
        user_precision = st.number_input("Précision", 1, 15, 8, key="user_precision")
    
    with col2:
        st.write("**Alliés**")
        ally_count = st.number_input("Nombre", 0, 3, 1, key="ally_count")
        ally_health = st.number_input("PV alliés", 1, 30, 10, key="ally_health")
    
    with col3:
        st.write("**Ennemis**")
        enemy_count = st.number_input("Nombre", 0, 5, 2, key="enemy_count")
        enemy_health = st.number_input("PV ennemis", 1, 50, 20, key="enemy_health")
    
    # Bouton de test
    if st.button("🧪 TESTER CAPACITÉ", type="primary"):
        _execute_ability_test(
            ability_instance, hero_code,
            user_health, user_spells, user_precision,
            ally_count, ally_health,
            enemy_count, enemy_health
        )

def _execute_ability_test(ability_instance, hero_code: str, 
                         user_health: int, user_spells: int, user_precision: int,
                         ally_count: int, ally_health: int,
                         enemy_count: int, enemy_health: int):
    """Exécute le test de la capacité"""
    
    st.subheader("🔍 Exécution du Test")
    
    try:
        # Créer contexte de test
        user, allies, enemies, combat_state = _create_test_context(
            hero_code, user_health, user_spells, user_precision,
            ally_count, ally_health, enemy_count, enemy_health
        )
        
        # Déterminer cibles selon type de capacité
        targets = _determine_targets(ability_instance, user, allies, enemies)
        
        # Phase 1: Test direct execute (pas de can_be_used selon base_ability.py)
        with st.expander("📋 Phase 1: Test Direct Execute", expanded=True):
            st.write("**Contexte:**")
            st.write(f"- Sorts disponibles: {getattr(user, 'current_spells', user.spells)}/{ability_instance.spell_cost}")
            st.write(f"- PV utilisateur: {user.current_health}/{user.health}")
            st.write(f"- Nombre cibles: {len(targets)}")
            
            # Préparer context selon base_ability.py
            from models.combat.spell_manager import SpellManager
            
            spell_manager = SpellManager()
            context = {
                'spell_manager': spell_manager,
                'rules': combat_state.get('rules'),
                'all_heroes': combat_state.get('allies', []),
                'all_enemies': combat_state.get('enemies', [])
            }
            
            # Log pour execute()
            execution_log = []
            
            try:
                # Appel selon signature base_ability.py: execute(caster, targets, context, log)
                result = ability_instance.execute(user, targets, context, execution_log)
                
                if result:
                    st.success("✅ Execute() retourné True")
                else:
                    st.warning("⚠️ Execute() retourné False")
                
                # Afficher logs d'exécution
                if execution_log:
                    st.write("**Logs d'exécution:**")
                    for log_entry in execution_log:
                        st.write(f"• {log_entry}")
                
            except Exception as e:
                st.error(f"❌ Erreur execute(): {e}")
                result = False
        
        # Phase 2: Exécution et résultats
        with st.expander("⚡ Phase 2: Exécution et Résultats", expanded=True):
            
            # État avant
            st.write("**État AVANT:**")
            _display_entities_state(user, allies, enemies)
            
            # État après
            st.write("**État APRÈS:**")
            _display_entities_state(user, allies, enemies)
            
            # Logs de combat
            if combat_state.get("logs"):
                st.write("**Logs générés:**")
                for log in combat_state["logs"]:
                    st.write(f"• {log}")
        
        st.success("🎉 Test terminé")
    
    except Exception as e:
        st.error(f"💥 Erreur critique durant test: {e}")
        st.code(traceback.format_exc())

def _create_test_context(hero_code: str, user_health: int, user_spells: int, user_precision: int,
                        ally_count: int, ally_health: int, enemy_count: int, enemy_health: int):
    """Crée le contexte de test basé sur le vrai modèle Character"""
    
    from models.character import Character, Enemy
    
    # Créer utilisateur selon modèle Pydantic réel
    user = Character(
        code=hero_code,
        name="TestUser", 
        precision=user_precision,
        damage=4,
        spells=user_spells, 
        health=user_health
    )
    # current_health s'initialise automatiquement via model_post_init
    
    # Créer alliés
    allies = []
    for i in range(ally_count):
        ally = Character(
            code="P-1",
            name=f"Ally{i+1}", 
            precision=6,
            damage=2, 
            spells=3,
            health=ally_health
        )
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
        "allies": [user] + allies,
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

def _display_entities_state(user, allies, enemies):
    """Affiche l'état selon character.py exact"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Utilisateur:**")
        st.write(f"PV: {user.current_health}/{user.get_total_health()}")
        current_spells = getattr(user, 'current_spells', None) or user.get_total_spells()
        st.write(f"Sorts: {current_spells}/{user.get_total_spells()}")
        st.write(f"Précision: {user.get_total_precision()}")
    
    with col2:
        st.write("**Alliés:**")
        for i, ally in enumerate(allies):
            st.write(f"Allié {i+1}: {ally.current_health}/{ally.get_total_health()} PV")
    
    with col3:
        st.write("**Ennemis:**")
        for i, enemy in enumerate(enemies):
            st.write(f"Ennemi {i+1}: {enemy.current_health}/{enemy.max_health} PV")

# ============================================================================
# INTÉGRATION DANS L'APP PRINCIPALE
# ============================================================================

def integrate_debug_mode_in_app():
    """
    Code d'intégration pour ajouter le mode debug dans l'app principale
    
    À ajouter dans app.py dans la fonction main():
    
    # Ajouter un onglet debug
    tabs = st.tabs(["🏰 Sélection", "⚙️ Forge", "📜 Chroniques", "⚔️ Arène", "🔧 Debug", "ℹ️ À Propos"])
    
    # Dans la boucle des onglets:
    with tabs[4]:  # Onglet Debug
        from debug_mode import create_debug_tab
        create_debug_tab()
    """
    pass

# ============================================================================
# MODE DEBUG SIDEBAR (Alternative)
# ============================================================================

def create_debug_sidebar():
    """
    Alternative: Mode debug dans la sidebar
    À ajouter dans app.py:
    
    if st.sidebar.checkbox("🔧 Mode Debug Capacités"):
        with st.sidebar.expander("Debug Interface", expanded=True):
            create_debug_sidebar()
    """
    
    st.write("🔧 **Debug Capacités**")
    
    try:
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        total = ABILITY_REGISTRY.get_registered_count()
        st.write(f"📊 {total}/59 capacités")
        
        if st.button("Test Rapide P-1"):
            _quick_test("P-1", 1)
        
        if st.button("Test Rapide P-2"):
            _quick_test("P-2", 1)
    
    except Exception as e:
        st.error(f"Erreur debug: {e}")

def _quick_test(hero_code: str, ability_num: int):
    """Test rapide d'une capacité"""
    try:
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        
        ability = ABILITY_REGISTRY.get_ability_instance(hero_code, ability_num)
        if ability:
            st.success(f"✅ {ability.name} - Coût: {ability.spell_cost}")
        else:
            st.error(f"❌ Capacité {hero_code}-{ability_num} non trouvée")
    
    except Exception as e:
        st.error(f"Erreur test: {e}")