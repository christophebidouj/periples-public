#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Périples Balance Workshop - Version Optimisée Performance
🎲 Jeu : Périples © Bastien LIAUTY
💻 Code : Christophe Bidouj (assistance Claude AI)
"""

import streamlit as st
import time
import os
import hashlib
from typing import List, Dict
from models.character import Character, Enemy
from models.combat_engine import CombatEngine
from models.rules_engine import GameRules
from utils.data_loader import DataLoader
import ui.components.sandbox_interface

# Import UI
from ui.styling import apply_fantasy_theme, get_combat_button_styles, get_waiting_combat_style, get_app_title_style
from ui.components import *

# Import capacités forge
try:
    from ui.components.forge_abilities_components import (
        display_abilities_selection_section,
        get_abilities_for_hero,
        validate_abilities_selection
    )
    FORGE_ABILITIES_AVAILABLE = True
except ImportError:
    FORGE_ABILITIES_AVAILABLE = False

# Configuration
ENABLE_IMAGES = True

# === FONCTIONS UTILITAIRES OPTIMISÉES ===

def get_session_hash():
    """Génère hash simple pour invalidation cache"""
    key_data = {
        'heroes': len(st.session_state.get('selected_heroes', [])),
        'enemies': len(st.session_state.get('selected_enemies', [])),
        'builds': len(st.session_state.get('custom_builds', {}))
    }
    return hashlib.md5(str(key_data).encode()).hexdigest()[:8]

def safe_session_update(key: str, value):
    """Mise à jour sécurisée session state"""
    st.session_state[key] = value

def toggle_hero_selection(hero_code: str):
    """Toggle héros avec gestion propre"""
    selected = st.session_state.get('selected_heroes', [])
    
    if hero_code in selected:
        selected.remove(hero_code)
    else:
        # Nettoyage Elneha avant ajout
        elneha_forms = ['P-1', 'P-9', 'P-10', 'P-11', 'P-12']
        if hero_code in elneha_forms:
            selected = [code for code in selected if code not in elneha_forms]
        selected.append(hero_code)
    
    safe_session_update('selected_heroes', selected)

def toggle_enemy_selection(enemy_code: str):
    """Toggle ennemi avec gestion propre"""
    selected = st.session_state.get('selected_enemies', [])
    
    if enemy_code in selected:
        selected.remove(enemy_code)
    else:
        selected.append(enemy_code)
    
    safe_session_update('selected_enemies', selected)

def get_equipment_categories(equipment):
    """Trie équipements par type"""
    weapons = [eq for eq in equipment if eq.type.lower() == 'arme']
    armor = [eq for eq in equipment if eq.type.lower() == 'armure']
    accessories = [eq for eq in equipment if eq.type.lower() not in ['arme', 'armure']]
    return weapons, armor, accessories

# === INITIALISATION OPTIMISÉE ===

def init_app():
    """Configure Streamlit et session - Version optimisée"""
    st.set_page_config(page_title="Périples Balance Workshop", page_icon="⚔️", layout="wide")
    os.makedirs("data", exist_ok=True)
    
    # Variables session avec valeurs par défaut
    defaults = {
        'selected_heroes': [], 
        'selected_enemies': [], 
        'custom_builds': {},
        'ui_state': {'needs_rerun': False}  # État UI pour éviter reruns multiples
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

@st.cache_data
def load_data(_session_hash=None):
    """Cache intelligent qui se met à jour selon les changements"""
    loader = DataLoader()
    missing = [f for f in ["heroes.csv", "enemies.csv", "equipment.csv"] if not os.path.exists(f"data/{f}")]
    
    if missing:
        st.info("🔄 Création fichiers...")
        loader.create_csv_files()
        st.success("✅ Fichiers créés !")
        time.sleep(1)
        st.rerun()
    
    return {
        'heroes': loader.load_heroes(),
        'enemies': loader.load_enemies(), 
        'equipment': loader.load_equipment(),
        'loader': loader
    }

def get_hero_build_info(hero_code: str, _loader, custom_builds_dict: Dict = None) -> Dict:
    """Version optimisée - pas de recalcul inutile"""
    hero = next(h for h in _loader.load_heroes() if h.code == hero_code)
    current_custom_builds = custom_builds_dict or st.session_state.get('custom_builds', {})
    
    # Build custom ou standard
    if hero_code in current_custom_builds:
        custom = current_custom_builds[hero_code]
        equipment = [eq for eq in _loader.load_equipment() if eq.code in custom.get('equipment', [])]
        build_name = custom.get('name', 'Build Custom')
        is_custom = True
        custom_abilities = custom.get('abilities', [])
        abilities_custom = custom.get('abilities_custom', False)
    else:
        equipment = _loader.get_hero_loadout(hero_code)
        build_name = "Build Standard"
        is_custom = False
        custom_abilities = []
        abilities_custom = False
    
    # Héros équipé
    hero_equipped = hero.model_copy()
    hero_equipped.equip_items(equipment, build_name)
    
    # Application capacités custom
    if custom_abilities and abilities_custom:
        try:
            hero_abilities = _loader.get_hero_abilities(hero_code)
            if hero_abilities:
                selected_abilities = [a for a in hero_abilities if a.ability_number in custom_abilities]
                if hasattr(hero_equipped, 'add_abilities') and selected_abilities:
                    hero_equipped.add_abilities(selected_abilities)
                    hero_equipped.unlocked_abilities = custom_abilities.copy()
                    for ability in hero_equipped.abilities:
                        if ability.ability_number in custom_abilities:
                            ability.is_unlocked = True
        except Exception as e:
            pass  # Ignore silencieusement pour éviter les erreurs
    
    return {
        'hero_equipped': hero_equipped,
        'equipment': equipment,
        'build_name': build_name,
        'is_custom': is_custom,
        'stats': hero_equipped.get_stats_summary(),
        'abilities_info': {
            'has_custom_abilities': bool(custom_abilities and abilities_custom)
        }
    }

# === ONGLETS OPTIMISÉS ===

def tab_selection(data):
    """Onglet sélection - Version optimisée performance"""
    st.header("🏰 Sélection des Équipes")
    
    heroes, enemies, loader = data['heroes'], data['enemies'], data['loader']
    nb_heroes = len(st.session_state.selected_heroes)
    nb_enemies = len(st.session_state.selected_enemies)
    
    # Reset avec indicateurs
    if display_progress_indicators_with_reset(nb_heroes, nb_enemies):
        safe_session_update('selected_heroes', [])
        safe_session_update('selected_enemies', [])
        st.success("✅ Sélections effacées !")
        st.rerun()
    
    # === HÉROS ===
    st.subheader("🛡️ Héros Disponibles")
    
    # Info Elneha
    elneha_forms = ['P-1', 'P-9', 'P-10', 'P-11', 'P-12']
    selected_elneha = [c for c in st.session_state.selected_heroes if c in elneha_forms]
    if selected_elneha:
        hero_name = next(h.name for h in heroes if h.code == selected_elneha[0])
        st.info(f"🐻 {hero_name} sélectionnée (forme d'Elneha)")
    
    # Grille héros 6 par ligne - OPTIMISÉE
    cols = st.columns(6)
    current_builds = st.session_state.get('custom_builds', {})
    hero_changes = []  # Batch des changements
    
    for i, hero in enumerate(heroes):
        build = get_hero_build_info(hero.code, loader, current_builds)
        is_selected = hero.code in st.session_state.selected_heroes
        
        with cols[i % 6]:
            # Clé de bouton STABLE (pas de is_selected dedans)
            button_key = f"hero_select_{hero.code}_{i}"
            
            if display_hero_card(hero, build, is_selected, ENABLE_IMAGES):
                hero_changes.append(hero.code)
    
    # Application batch des changements héros
    if hero_changes:
        for hero_code in hero_changes:
            toggle_hero_selection(hero_code)
        st.rerun()
    
    # === ENNEMIS ===
    st.subheader("👹 Ennemis")
    player_count = max(2, nb_heroes) if nb_heroes >= 2 else 2
    
    # Recherche
    col1, col2 = st.columns([1, 3])
    with col1:
        search = st.text_input("Recherche", placeholder="Ex: 34, Dragon...", 
                              label_visibility="collapsed", key="enemy_search")
    with col2:
        if search.strip():
            st.success("🎯 Actif")
        else:
            st.info("📜 Compendium des monstres")
    
    # Filtrage
    if search.strip():
        term = search.lower()
        filtered = [e for e in enemies if term in e.code.split('-')[-1].lower() or term in e.name.lower()]
    else:
        filtered = enemies[:15]
        st.info("💡 Tapez un numéro ou nom pour chercher")
    
    # Grille ennemis 5 par ligne - OPTIMISÉE
    if filtered:
        st.write(f"**{len(filtered)} ennemis:**")
        cols = st.columns(5)
        enemy_changes = []  # Batch des changements
        
        for i, enemy in enumerate(filtered):
            is_selected = enemy.code in st.session_state.selected_enemies
            
            with cols[i % 5]:
                # Clé stable
                button_key = f"enemy_select_{enemy.code}_{i}"
                
                if display_enemy_card(enemy, is_selected, player_count):
                    enemy_changes.append(enemy.code)
        
        # Application batch des changements ennemis
        if enemy_changes:
            for enemy_code in enemy_changes:
                toggle_enemy_selection(enemy_code)
            st.rerun()
    
    # === RÉCAPITULATIF ===
    if nb_heroes >= 2 and nb_enemies > 0:
        heroes_data, enemies_data = prepare_teams_for_recap(
            st.session_state.selected_heroes, 
            st.session_state.selected_enemies, 
            data, 
            player_count
        )
        display_team_recap(heroes_data, enemies_data, player_count)
    
    # === LANCEMENT COMBAT ===
    st.subheader("⚙️ Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        rules = {
            'ranged_attacks': True,
            'magical_damage': True,
            'criticals': st.checkbox("🎯 Critiques", value=True),
            'initiative': st.checkbox("🎲 Initiative", value=True)
        }
    with col2:
        st.info("⚔️ Combat avec journal détaillé")
    
    # Bouton combat
    ready = nb_heroes >= 2 and nb_enemies > 0
    if ready:
        if st.button("⚔️ ENGAGER LE COMBAT ! ⚔️", type="primary", use_container_width=True):
            safe_session_update('run_simulation', True)
            safe_session_update('simulation_config', {
                'hero_codes': st.session_state.selected_heroes,
                'enemy_codes': st.session_state.selected_enemies,
                'player_count': player_count,
                'rules': rules
            })
            st.success("⚡ Combat engagé ! 👉 Allez dans 'Chroniques' 👈")
            st.balloons()
    else:
        st.button("⚔️ FORMATION INCOMPLÈTE", disabled=True, use_container_width=True)

def tab_forge(data):
    """Onglet forge - Version optimisée"""
    st.header("⚙️ Forge des Équipements")
    
    heroes, equipment = data['heroes'], data['equipment']
    
    # Sélection héros
    hero_options = {h.code: f"{get_hero_icon(h.name)} {h.name}" for h in heroes}
    selected_code = st.selectbox(
        "Héros:", 
        list(hero_options.keys()), 
        format_func=lambda x: hero_options[x],
        key="forge_hero_select"
    )
    selected_hero = next(h for h in heroes if h.code == selected_code)
    
    # Stats et build actuels
    st.subheader("📊 Statistiques")
    display_hero_base_stats(selected_hero)
    
    current_builds = st.session_state.get('custom_builds', {})
    current_build = get_hero_build_info(selected_code, data['loader'], current_builds)
    display_current_build_info(current_build)
    
    # Gestion builds
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset", use_container_width=True):
            if selected_code in st.session_state.custom_builds:
                builds = st.session_state.custom_builds.copy()
                del builds[selected_code]
                safe_session_update('custom_builds', builds)
                st.rerun()
    with col2:
        if current_build['is_custom'] and st.button("🗑️ Supprimer", use_container_width=True):
            builds = st.session_state.custom_builds.copy()
            del builds[selected_code]
            safe_session_update('custom_builds', builds)
            st.rerun()
    
    # === ÉQUIPEMENTS ===
    st.subheader("⚔️ Équipements")
    weapons, armor, accessories = get_equipment_categories(equipment)
    
    selected_eq = []
    selected_eq.extend(display_equipment_selection_native(weapons, "Armes", "⚔️", "forge_w"))
    selected_eq.extend(display_equipment_selection_native(armor, "Armures", "🛡️", "forge_a"))
    selected_eq.extend(display_equipment_selection_native(accessories, "Accessoires", "💍", "forge_acc"))
    
    # === CAPACITÉS ===
    st.subheader("🔮 Capacités")
    
    selected_abilities = []
    
    if FORGE_ABILITIES_AVAILABLE:
        hero_abilities = get_abilities_for_hero(selected_code, data['loader'])
        
        if hero_abilities:
            current_abilities = []
            if selected_code in st.session_state.get('custom_builds', {}):
                current_abilities = st.session_state.custom_builds[selected_code].get('abilities', [])
            
            selected_abilities = display_abilities_selection_section(
                selected_code, 
                hero_abilities, 
                current_abilities
            )
        else:
            st.warning(f"🔮 Aucune capacité trouvée pour {selected_hero.name}")
    else:
        st.error("❌ Système de capacités non disponible")
    
    # === SAUVEGARDE BUILD ===
    st.subheader("💾 Nouveau Build")
    
    # Aperçu si sélections
    if selected_eq:
        temp_hero = selected_hero.model_copy()
        temp_eq = [eq for eq in equipment if eq.code in selected_eq]
        temp_hero.equip_items(temp_eq, "Custom")
        display_new_stats_preview(temp_hero.get_stats_summary()['total'])
    
    if selected_abilities:
        st.info(f"🔮 {len(selected_abilities)} capacités sélectionnées")
    
    # Zone sauvegarde
    col_name, col_save = st.columns([3, 1])
    
    with col_name:
        name = st.text_input("🏷️ Nom du build:", 
                           placeholder="Ex: Tank Ultime, Mage DPS...",
                           key="forge_build_name")
    
    with col_save:
        has_selection = bool(selected_eq or selected_abilities)
        button_text = "💾 Sauvegarder" if has_selection else "💾 Rien à sauver"
        
        if st.button(button_text, 
                    type="primary" if has_selection else "secondary", 
                    use_container_width=True,
                    disabled=not has_selection):
            
            build_data = {
                'equipment': selected_eq,
                'name': name.strip() or 'Build Custom'
            }
            
            if selected_abilities:
                build_data['abilities'] = selected_abilities
                build_data['abilities_custom'] = True
            
            # Sauvegarde optimisée
            builds = st.session_state.custom_builds.copy()
            builds[selected_code] = build_data
            safe_session_update('custom_builds', builds)
            
            st.success(f"✅ Build '{build_data['name']}' sauvegardé !")
            st.balloons()
            time.sleep(0.5)
            st.rerun()

def tab_combat(data):
    """Onglet combat - Version optimisée"""
    st.header("📜 Chroniques du Combat")
    
    if not st.session_state.get('run_simulation', False):
        st.markdown(get_waiting_combat_style(), unsafe_allow_html=True)
        return
    
    # Préparation combat
    config = st.session_state['simulation_config']
    heroes, enemies, loader = data['heroes'], data['enemies'], data['loader']
    
    # Équipes avec builds custom
    selected_heroes = []
    current_builds = st.session_state.get('custom_builds', {})
    
    for code in config['hero_codes']:
        build = get_hero_build_info(code, loader, current_builds)
        selected_heroes.append(build['hero_equipped'])
    
    selected_enemies = [e for e in enemies if e.code in config['enemy_codes']]
    
    # Simulation
    with st.spinner("⚔️ Combat en cours..."):
        engine = CombatEngine(GameRules(**config['rules']))
        result = engine.simulate_single_combat(selected_heroes, selected_enemies, config['player_count'])
    
    # Affichage résultats
    display_combat_result_banner(result['winner'])
    
    if 'resource_metrics' in result:
        display_combat_metrics(result['resource_metrics'])
        display_heroes_individual_table(result['resource_metrics'])
    
    display_combat_log(result['log'])
    display_combat_summary(result)
    
    # Reset
    safe_session_update('run_simulation', False)

def prepare_teams_for_recap(hero_codes: List[str], enemy_codes: List[str], data, player_count: int):
    """Prépare données pour récapitulatif - Version optimisée"""
    current_builds = st.session_state.get('custom_builds', {})
    
    # Données héros
    heroes_data = []
    for code in hero_codes:
        build = get_hero_build_info(code, data['loader'], current_builds)
        stats = build['stats']['total']
        heroes_data.append({
            'name': build['hero_equipped'].name,
            'icon': get_hero_icon(build['hero_equipped'].name),
            'build': build['build_name'],
            'is_custom': build['is_custom'],
            'precision': stats['precision'],
            'damage': stats['damage'],
            'health': stats['health'],
            'parade': stats['parade'],
            'spells': stats['spells']
        })
    
    # Données ennemis
    enemies_data = []
    for code in enemy_codes:
        enemy = next(e for e in data['enemies'] if e.code == code)
        stats = enemy.get_stats_for_players(player_count)
        enemies_data.append({
            'name': enemy.name,
            'number': enemy.code.split('-')[-1],
            'is_magical': enemy.is_magical,
            'health': stats['health'],
            'damage': stats['damage'],
            'defense': enemy.defense
        })
    
    return heroes_data, enemies_data

# === ONGLET À PROPOS (INCHANGÉ) ===
def display_about():
    """Section À Propos - Inchangée"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #8b4513, #d4af37, #8b4513);
                border: 4px solid #d4af37; border-radius: 25px; padding: 30px; margin: 25px 0;
                text-align: center; box-shadow: 0 8px 32px rgba(139,69,19,0.3);">
        <h1 style="color: #fff; font-family: 'Cinzel', serif; margin: 0; font-size: 2.5rem; 
                   text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
            ⚔️ PÉRIPLES BALANCE WORKSHOP ⚔️
        </h1>
        <h3 style="color: #f4f4f4; margin: 15px 0 5px 0; font-style: italic;">
            Outil Professionnel d'Équilibrage RPG
        </h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 🎲 **JEU DE SOCIÉTÉ**
        - **Périples** © **Bastien LIAUTY**
        - **Version :** V3.0 (2025)
        - **Genre :** RPG coopératif médiéval-fantastique
        - **Joueurs :** 1 à 4 joueurs
        - **Statut :** Prototype en développement
        """)
    
    with col2:
        st.markdown("""
        ### 💻 **BALANCE WORKSHOP**
        - **Dev Python :** Christophe Bidouj
        - **Assistance IA :** Claude AI (Anthropic)
        - **Technologies :** Python + Streamlit + Pydantic
        - **Version :** V5+ Optimisée Performance
        - **Statut :** En développement actif
        """)

# === MAIN OPTIMISÉ ===
def main():
    """Application principale - Version optimisée"""
    init_app()
    apply_fantasy_theme()
    
    # Titre
    st.markdown(get_app_title_style(), unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; font-size: 0.8rem; color: #666; margin-bottom: 20px;">
        🎲 <strong style="color: #8b4513;">Périples</strong> © <strong style="color: #228b22;">Bastien LIAUTY</strong> | 
        💻 Dev Python : <strong style="color: #4682b4;">Christophe Bidouj</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Données avec cache intelligent
    try:
        session_hash = get_session_hash()
        data = load_data(_session_hash=session_hash)
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
        st.stop()
    
    # Onglets
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏰 Sélection", "⚙️ Forge", "📜 Chroniques", "⚔️ Arène", "ℹ️ À Propos"])
    
    with tab1: tab_selection(data)
    with tab2: tab_forge(data)
    with tab3: tab_combat(data)
    with tab4: ui.components.sandbox_interface.main_sandbox_tab()
    with tab5: display_about()

if __name__ == "__main__":
    main()