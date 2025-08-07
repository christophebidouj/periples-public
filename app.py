#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Périples Balance Workshop - Version avec Builds Prédéfinis
🎲 Jeu : Périples © Bastien LIAUTY
💻 Code : Christophe Bidouj (assistance Claude AI)
"""

import streamlit as st
import time
import os
import random
from typing import List, Dict
from models.character import Character, Enemy
from models.combat_engine import CombatEngine
from models.rules_engine import GameRules
from utils.data_loader import DataLoader
import ui.components.sandbox_interface

# Import UI
from ui.styling import apply_fantasy_theme, get_combat_button_styles, get_waiting_combat_style
from ui.components import *
from ui.components.hero_components import preload_hero_builds_for_all_difficulties

# Import capacités et potions
try:
    from ui.components.forge_abilities_components import (
        display_abilities_selection_section,
        get_abilities_for_hero,
        validate_abilities_selection,
        display_potions_selection_section
    )
    FORGE_ABILITIES_AVAILABLE = True
except ImportError:
    FORGE_ABILITIES_AVAILABLE = False

# Configuration
ENABLE_IMAGES = True

# === FONCTIONS UTILITAIRES ===

def get_standard_equipment_codes(hero_code: str) -> List[str]:
    """Retourne les codes équipements standard pour un héros"""
    standard_equipment = {
        'P-1': ['E-1', 'E-7', 'E-13'],   # Elneha
        'P-2': ['E-2', 'E-8', 'E-14'],   # Liarie
        'P-3': ['E-3', 'E-9', 'E-15'],   # Atucan
        'P-4': ['E-4', 'E-10', 'E-16'],  # Kraor
        'P-5': ['E-5', 'E-11', 'E-17'],  # Thordius
        'P-6': ['E-6', 'E-12', 'E-18'],  # Stephe
        'P-7': ['E-1', 'E-7', 'E-13'],   # Lame
        'P-8': ['E-2', 'E-8', 'E-14'],   # Raishi
        'P-9': ['E-1', 'E-7', 'E-13'],   # Ours
        'P-10': ['E-1', 'E-7', 'E-13'],  # Loup
        'P-11': ['E-1', 'E-7', 'E-13'],  # Ours S.
        'P-12': ['E-1', 'E-7', 'E-13']   # Loup S.
    }
    return standard_equipment.get(hero_code, [])

def get_difficulty_level_name(hero_code: str) -> str:
    """Récupère le niveau de difficulté sélectionné pour un héros"""
    hero_difficulties = st.session_state.get('hero_difficulties', {})
    difficulty_full = hero_difficulties.get(hero_code, "🔵 Normal")
    
    # Extraction du nom sans emoji
    if "Facile" in difficulty_full:
        return "Facile"
    elif "Difficile" in difficulty_full:
        return "Difficile"
    else:
        return "Normal"

def apply_difficulty_to_equipment(equipment_codes: List[str], difficulty: str, equipment_list: List) -> List[str]:
    """
    Applique la modification de difficulté aux équipements
    
    Args:
        equipment_codes: Codes équipements de base
        difficulty: Niveau de difficulté ("Facile", "Normal", "Difficile")
        equipment_list: Liste complète des équipements
        
    Returns:
        List[str]: Codes équipements modifiés selon la difficulté
    """
    if difficulty == "Normal":
        return equipment_codes
    
    # Création mapping par catégorie
    weapons = [eq for eq in equipment_list if eq.type.lower() == 'arme']
    armor = [eq for eq in equipment_list if eq.type.lower() == 'armure']
    accessories = [eq for eq in equipment_list if eq.type.lower() not in ['arme', 'armure']]
    
    # Tri par puissance (somme des stats)
    def get_equipment_power(eq):
        return eq.precision + eq.physical_damage + eq.magical_damage + eq.defense + eq.spells + eq.health
    
    weapons.sort(key=get_equipment_power)
    armor.sort(key=get_equipment_power)
    accessories.sort(key=get_equipment_power)
    
    modified_codes = []
    
    for code in equipment_codes:
        # Trouve l'équipement actuel
        current_eq = next((eq for eq in equipment_list if eq.code == code), None)
        if not current_eq:
            modified_codes.append(code)
            continue
        
        # Détermine la catégorie
        if current_eq.type.lower() == 'arme':
            category_list = weapons
        elif current_eq.type.lower() == 'armure':
            category_list = armor
        else:
            category_list = accessories
        
        # Trouve la position actuelle
        try:
            current_index = next(i for i, eq in enumerate(category_list) if eq.code == code)
        except StopIteration:
            modified_codes.append(code)
            continue
        
        # Calcule le nouvel index selon la difficulté
        if difficulty == "Facile":
            # Améliore (+2 positions vers les plus puissants)
            new_index = min(len(category_list) - 1, current_index + 2)
        elif difficulty == "Difficile":
            # Dégrade (-1 position vers les moins puissants)
            new_index = max(0, current_index - 1)
        else:
            new_index = current_index
        
        modified_codes.append(category_list[new_index].code)
    
    return modified_codes

def get_difficulty_build_name(base_name: str, difficulty: str) -> str:
    """Génère le nom du build selon la difficulté"""
    difficulty_prefixes = {
        "Facile": "🟢 Build Facile",
        "Normal": "🔵 Build Standard", 
        "Difficile": "🔴 Build Difficile"
    }
    return difficulty_prefixes.get(difficulty, base_name)

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

# === INITIALISATION ===

def init_app():
    """Configure Streamlit et session"""
    st.set_page_config(page_title="Périples Balance Workshop", page_icon="⚔️", layout="wide")
    os.makedirs("data", exist_ok=True)
    
    # Variables session avec valeurs par défaut
    defaults = {
        'selected_heroes': [], 
        'selected_enemies': [], 
        'custom_builds': {},
        'hero_difficulties': {},  # NOUVEAU - Niveaux de difficulté
        'ui_state': {'needs_rerun': False}
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

@st.cache_data
def load_data():
    """Cache des données"""
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

@st.cache_data
def get_preloaded_builds(_heroes_list, _equipment_list, _loader):
    """Cache les builds pré-calculés pour éviter de les recalculer à chaque interaction"""
    return preload_hero_builds_for_all_difficulties(_heroes_list, _equipment_list, _loader)

def get_hero_build_info(hero_code: str, heroes_list: List, equipment_list: List, loader, custom_builds_dict: Dict = None) -> Dict:
    """Version restaurée et simplifiée pour builds custom uniquement"""
    hero = next(h for h in heroes_list if h.code == hero_code)
    current_custom_builds = custom_builds_dict or st.session_state.get('custom_builds', {})
    
    custom = current_custom_builds[hero_code]  # Assume que le héros a un build custom
    equipment = [eq for eq in equipment_list if eq.code in custom.get('equipment', [])]
    build_name = custom.get('name', 'Build Custom')
    custom_abilities = custom.get('abilities', [])
    abilities_custom = custom.get('abilities_custom', False)
    
    # Héros équipé
    hero_equipped = hero.model_copy()
    hero_equipped.equip_items(equipment, build_name)
    
    # Application capacités custom
    if custom_abilities and abilities_custom:
        try:
            hero_abilities = loader.get_hero_abilities(hero_code)
            if hero_abilities:
                selected_abilities = [a for a in hero_abilities if a.ability_number in custom_abilities]
                if hasattr(hero_equipped, 'add_abilities') and selected_abilities:
                    hero_equipped.add_abilities(selected_abilities)
                    hero_equipped.unlocked_abilities = custom_abilities.copy()
                    for ability in hero_equipped.abilities:
                        if ability.ability_number in custom_abilities:
                            ability.is_unlocked = True
        except Exception:
            pass
    
    return {
        'hero_equipped': hero_equipped,
        'equipment': equipment,
        'build_name': build_name,
        'is_custom': True,
        'stats': hero_equipped.get_stats_summary(),
        'abilities_info': {
            'has_custom_abilities': bool(custom_abilities and abilities_custom)
        }
    }

def get_hero_final_stats(hero_code: str, heroes_list: List, equipment_list: List, loader, custom_builds_dict: Dict = None) -> Dict:
    """
    Calcule les stats finales d'un héros selon la logique : Custom > Builds fixes selon difficulté
    Version utilisée pour les autres onglets (Forge, Combat, etc.)
    """
    current_custom_builds = custom_builds_dict or st.session_state.get('custom_builds', {})
    
    if hero_code in current_custom_builds:
        # BUILD CUSTOM - Utiliser get_hero_build_info complet
        return get_hero_build_info(hero_code, heroes_list, equipment_list, loader, current_custom_builds)
    else:
        # BUILDS FIXES - Utiliser les données fixes selon difficulté
        from hero_builds_data import get_hero_stats_by_difficulty, get_build_name_by_difficulty
        
        difficulty = st.session_state.get('hero_difficulties', {}).get(hero_code, "🔵 Normal")
        stats = get_hero_stats_by_difficulty(hero_code, difficulty)
        build_name = get_build_name_by_difficulty(difficulty)
        
        # Récupération info de base du héros
        hero = next(h for h in heroes_list if h.code == hero_code)
        
        # Format compatible avec display_hero_card
        return {
            'hero_equipped': hero,
            'equipment': [],  # Pas d'équipements pour builds fixes
            'build_name': build_name,
            'is_custom': False,
            'stats': {
                'total': stats  # Stats directes du fichier
            },
            'difficulty_level': difficulty.replace("🟢 ", "").replace("🔵 ", "").replace("🔴 ", "")
        }

def prepare_teams_for_recap(hero_codes: List[str], enemy_codes: List[str], data, player_count: int):
    """Prépare données pour récapitulatif - Version simplifiée"""
    current_builds = st.session_state.get('custom_builds', {})
    
    # Données héros avec logique unifiée
    heroes_data = []
    for code in hero_codes:
        build_info = get_hero_final_stats(code, data['heroes'], data['equipment'], data['loader'], current_builds)
        stats = build_info['stats']['total']
        
        heroes_data.append({
            'name': build_info['hero_equipped'].name,
            'icon': get_hero_icon(build_info['hero_equipped'].name),
            'build': build_info['build_name'],
            'is_custom': build_info['is_custom'],
            'difficulty_level': build_info.get('difficulty_level', 'Normal'),
            'precision': stats['precision'],
            'damage': stats['damage'],
            'health': stats['health'],
            'parade': stats['parade'],
            'spells': stats['spells']
        })
    
    # Données ennemis (inchangées)
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

# === ONGLETS ===

def tab_selection(data):
    """Onglet sélection des équipes avec système de builds prédéfinis"""
    st.header("🏰 Sélection des Équipes")
    
    heroes, enemies, loader = data['heroes'], data['enemies'], data['loader']
    nb_heroes = len(st.session_state.selected_heroes)
    nb_enemies = len(st.session_state.selected_enemies)
    
    # Reset avec indicateurs
    if display_progress_indicators_with_reset(nb_heroes, nb_enemies):
        safe_session_update('selected_heroes', [])
        safe_session_update('selected_enemies', [])
        safe_session_update('hero_difficulties', {})  # NOUVEAU - Reset niveaux
        st.success("✅ Sélections effacées !")
        st.rerun()
    
    # === HÉROS ===
    st.subheader("🛡️ Héros Disponibles")
    
    # Info système builds prédéfinis
    st.info("🎯 **Nouveau :** Chaque héros peut être configuré en 3 niveaux de difficulté avec équipements adaptés !")
    
    # Info Elneha
    elneha_forms = ['P-1', 'P-9', 'P-10', 'P-11', 'P-12']
    selected_elneha = [c for c in st.session_state.selected_heroes if c in elneha_forms]
    if selected_elneha:
        hero_name = next(h.name for h in heroes if h.code == selected_elneha[0])
        st.info(f"🐻 {hero_name} sélectionnée (forme d'Elneha)")
    
    # PRÉ-CALCUL DES BUILDS (mise en cache)
    preloaded_builds = get_preloaded_builds(heroes, data['equipment'], loader)
    
    # Grille héros 6 par ligne - Version avec builds pré-calculés
    cols = st.columns(6)
    current_builds = st.session_state.get('custom_builds', {})
    hero_changes = []
    
    for i, hero in enumerate(heroes):
        is_selected = hero.code in st.session_state.selected_heroes
        
        with cols[i % 6]:
            # NOUVEAU - Utilisation de display_hero_card avec builds pré-calculés
            if display_hero_card(hero, is_selected, preloaded_builds, current_builds, ENABLE_IMAGES):
                hero_changes.append(hero.code)
    
    # Application des changements héros uniquement
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
    
    # Grille ennemis 5 par ligne
    if filtered:
        st.write(f"**{len(filtered)} ennemis:**")
        cols = st.columns(5)
        enemy_changes = []
        
        for i, enemy in enumerate(filtered):
            is_selected = enemy.code in st.session_state.selected_enemies
            
            with cols[i % 5]:
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
        st.info("⚔️ Combat avec builds prédéfinis selon niveaux sélectionnés")
    
    # Bouton combat
    ready = nb_heroes >= 2 and nb_enemies > 0
    if ready:
        if st.button("⚔️ ENGAGER LE COMBAT !", type="primary", use_container_width=True):
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
    """Onglet forge des équipements"""
    st.header("⚙️ Forge des Équipements")
    
    heroes, equipment = data['heroes'], data['equipment']
    
    # Sélection héros
    hero_options = {h.code: f"{get_hero_icon(h.name)} {h.name}" for h in heroes}
    selected_code = st.selectbox(
        "Héros:", 
        list(hero_options.keys()), 
        format_func=lambda x: hero_options[x],
        key="forge_hero_selector"
    )
    selected_hero = next(h for h in heroes if h.code == selected_code)
    
    # Stats et build actuels
    st.subheader("📊 Statistiques")
    display_hero_base_stats(selected_hero)
    
    current_builds = st.session_state.get('custom_builds', {})
    current_build = get_hero_final_stats(selected_code, heroes, equipment, data['loader'], current_builds)
    display_current_build_info(current_build)
    
    # Gestion builds
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset", key="forge_reset", use_container_width=True):
            if selected_code in st.session_state.custom_builds:
                builds = st.session_state.custom_builds.copy()
                del builds[selected_code]
                safe_session_update('custom_builds', builds)
                st.rerun()
    with col2:
        if current_build['is_custom'] and st.button("🗑️ Supprimer", key="forge_delete", use_container_width=True):
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
    
    # === POTIONS ===
    st.subheader("🧪 Potions de Santé")
    
    selected_potions = {'small': 0, 'large': 0}
    
    if FORGE_ABILITIES_AVAILABLE:
        selected_potions = display_potions_selection_section(selected_code)
    else:
        st.error("❌ Système de potions non disponible")
    
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
    
    if selected_potions['small'] > 0 or selected_potions['large'] > 0:
        total_potions = selected_potions['small'] + selected_potions['large']
        st.info(f"🧪 {total_potions} potions sélectionnées")
    
    # Zone sauvegarde
    col_name, col_save = st.columns([3, 1])
    
    with col_name:
        name = st.text_input("🏷️ Nom du build:", 
                           placeholder="Ex: Tank Ultime, Mage DPS...",
                           key="forge_build_name")
    
    with col_save:
        has_selection = bool(selected_eq or selected_abilities or selected_potions['small'] > 0 or selected_potions['large'] > 0)
        button_text = "💾 Sauvegarder" if has_selection else "💾 Rien à sauver"
        
        if st.button(button_text, 
                    key="forge_save",
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
            
            if selected_potions['small'] > 0 or selected_potions['large'] > 0:
                build_data['potions'] = selected_potions
            
            # Sauvegarde
            builds = st.session_state.custom_builds.copy()
            builds[selected_code] = build_data
            safe_session_update('custom_builds', builds)
            
            st.success(f"✅ Build '{build_data['name']}' sauvegardé !")
            st.balloons()
            time.sleep(0.5)
            st.rerun()

def tab_combat(data):
    """Onglet combat avec builds prédéfinis"""
    st.header("📜 Chroniques du Combat")
    
    if not st.session_state.get('run_simulation', False):
        st.markdown(get_waiting_combat_style(), unsafe_allow_html=True)
        return
    
    # Préparation combat
    config = st.session_state['simulation_config']
    heroes, enemies, loader = data['heroes'], data['enemies'], data['loader']
    
    # Équipes avec builds selon niveaux de difficulté
    selected_heroes = []
    current_builds = st.session_state.get('custom_builds', {})
    
    for code in config['hero_codes']:
        build = get_hero_final_stats(code, heroes, data['equipment'], loader, current_builds)
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

def display_about():
    """Section À Propos - Version native"""
    
    # Informations sur le jeu
    st.subheader("🎲 Jeu de Société")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Périples** © Bastien LIAUTY
        - Genre : RPG coopératif médiéval-fantastique
        - Joueurs : 1 à 4 joueurs
        - Version des règles : V3.0
        """)
    
    with col2:
        st.markdown("""
        **Statut :** Prototype en développement
        - 12 héros avec formes alternatives
        - 72 ennemis évolutifs
        - 52 équipements et 48 capacités spéciales
        """)

    # Informations techniques
    st.subheader("💻 Balance Workshop")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Développement :**
        - Code Python : Christophe Bidouj
        - Assistance IA : Claude AI (Anthropic)
        - Technologies : Python, Streamlit, Pydantic
        """)
    
    with col2:
        st.markdown("""
        **Fonctionnalités :**
        - Simulation de combats automatisés
        - Forge d'équipements personnalisés
        - Système de capacités et potions
        - **NOUVEAU** : 3 builds prédéfinis par héros
        """)

    # Objectifs et usage
    st.subheader("🎯 Objectifs")
    st.markdown("""
    Ce simulateur permet de tester et valider l'équilibrage des mécaniques de jeu :
    - **Combats** : Validation des règles et équilibrage selon le nombre de joueurs
    - **Équipements** : Test des builds personnalisés et impact sur les statistiques  
    - **Capacités** : Simulation des 48 capacités spéciales des héros
    - **Builds Prédéfinis** : 3 niveaux de difficulté (Facile/Normal/Difficile) avec équipements adaptés
    - **Métriques** : Analyse du taux de survie, durée de combat et utilisation des ressources
    """)

    # Avertissement usage
    st.info("""
    **📋 Usage autorisé :** Cet outil est destiné aux tests d'équilibrage pour l'équipe de développement du jeu Périples. 
    L'usage commercial ou la redistribution ne sont pas autorisés.
    """)

# === MAIN ===

def main():
    """Application principale"""
    init_app()
    apply_fantasy_theme()
    
    # Titre natif Streamlit
    st.title("⚔️ Périples Balance Workshop ⚔️")
    st.caption("🎲 **Périples** © **Bastien LIAUTY** | 💻 Dev Python : **Christophe Bidouj** | Simulateur d'équilibrage RPG dans l'univers fantasy")
    
    # Données avec cache
    try:
        data = load_data()
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
        st.stop()
    
    # Onglets
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏰 Sélection", "⚙️ Forge", "📜 Chroniques", "⚔️ Arène", "ℹ️ À Propos"])
    
    with tab1: 
        tab_selection(data)
    with tab2: 
        tab_forge(data)
    with tab3: 
        tab_combat(data)
    with tab4: 
        ui.components.sandbox_interface.main_sandbox_tab()
    with tab5: 
        display_about()

if __name__ == "__main__":
    main()