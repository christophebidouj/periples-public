#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Périples – Atelier d'Équilibrage - Version avec 8 Héros Principaux
🎲 Jeu : Périples © Bastien LIAUTY
💻 Code : Christophe Bidouj (assistance Claude AI)
VERSION FINALE MIGRÉE - Système de builds basé sur équipements réels
"""

import streamlit as st
import time
import os
import random
from typing import List, Dict
from models.character import Character, Enemy
from models.combat.combat_engine import CombatEngine
from models.rules_engine import GameRules
from utils.data_loader import DataLoader, cleanup_removed_heroes_from_session
from ui.styling import apply_fantasy_theme, get_combat_button_styles, get_waiting_combat_style
from ui.components import *
from ui.components.hero_components import preload_hero_builds_for_all_difficulties
from hero_builds_data import get_abilities_for_level
from ui.components.sandbox_interface_v2 import main_sandbox_v2, reset_combat_state
from ui.components.enemy_editor import main_enemy_editor

# Import des capacités et des potions
try:
    from ui.components.forge_abilities_components import (
        display_abilities_selection_section,
        get_abilities_for_hero,
        validate_abilities_selection,
        display_potions_selection_section,
        reset_forge_selections,
        load_build_selections_into_ui
    )
    FORGE_ABILITIES_AVAILABLE = True
except ImportError:
    FORGE_ABILITIES_AVAILABLE = False

# Configuration
ENABLE_IMAGES = True

# === FONCTIONS UTILITAIRES ===

def get_standard_equipment_codes(hero_code: str) -> List[str]:
    """Retourne les codes équipements standard pour un héros - VERSION 8 HÉROS"""
    standard_equipment = {
        'P-1': ['E-1', 'E-7', 'E-13'],   # Elneha
        'P-2': ['E-2', 'E-8', 'E-14'],   # Liarie
        'P-3': ['E-3', 'E-9', 'E-15'],   # Atucan
        'P-4': ['E-4', 'E-10', 'E-16'],  # Kraor
        'P-5': ['E-5', 'E-11', 'E-17'],  # Thordius
        'P-6': ['E-6', 'E-12', 'E-18'],  # Stephe
        'P-7': ['E-1', 'E-7', 'E-13'],   # Lame
        'P-8': ['E-2', 'E-8', 'E-14']    # Raishi
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

def safe_session_update(key: str, value):
    """Mise à jour sécurisée session state"""
    st.session_state[key] = value

def toggle_hero_selection(hero_code: str):
    """Toggle héros avec gestion propre - Version 8 héros"""
    selected = st.session_state.get('selected_heroes', [])
    
    if hero_code in selected:
        selected.remove(hero_code)
    else:
        # Nettoyage Elneha avant ajout (pas de formes multiples maintenant)
        if hero_code == 'P-1':  # Elneha principale
            selected = [code for code in selected if code != 'P-1']
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

def filter_heroes_to_main_8(heroes_list: List) -> List:
    """Filtre pour ne garder que les 8 héros principaux (P-1 à P-8)"""
    main_hero_codes = ['P-1', 'P-2', 'P-3', 'P-4', 'P-5', 'P-6', 'P-7', 'P-8']
    return [hero for hero in heroes_list if hero.code in main_hero_codes]

def get_hero_build_from_equipment(hero_code: str, heroes_list: List, equipment_list: List, loader, difficulty: str) -> Dict:
    """
    CORRIGÉ - Builds par défaut avec TOUTES les capacités (abilities_level ignoré)
    """
    from hero_builds_data import get_hero_detailed_build
    
    # Récupération build détaillé
    build_config = get_hero_detailed_build(hero_code, difficulty)
    
    # Héros de base
    hero = next(h for h in heroes_list if h.code == hero_code)
    hero_equipped = hero.model_copy()
    
    # Application équipements
    equipment_items = [eq for eq in equipment_list if eq.code in build_config.get('equipment', [])]
    hero_equipped.equip_items(equipment_items, build_config.get('name', 'Build Standard'))
    
    # 🔧 CORRECTION: Respecter le niveau de capacités du build
    try:
        hero_abilities = loader.get_hero_abilities(hero_code)
        if hero_abilities:
            # Récupérer le niveau de capacités depuis le build
            abilities_level = build_config.get('abilities_level', 1)
            
            # Utiliser la fonction qui respecte le niveau du build
            allowed_abilities = get_abilities_for_level(hero_code, abilities_level)
            
            # Filtrer seulement les capacités autorisées par le niveau
            selected_abilities = [a for a in hero_abilities if a.ability_number in allowed_abilities]
            
            if hasattr(hero_equipped, 'add_abilities') and selected_abilities:
                hero_equipped.add_abilities(selected_abilities)  # Capacités filtrées selon le niveau
                hero_equipped.unlocked_abilities = allowed_abilities.copy()
                for ability in hero_equipped.abilities:
                    if ability.ability_number in allowed_abilities:
                        ability.is_unlocked = True
    except Exception:
        pass
    
    # Application potions
    potions_config = build_config.get('potions', {'small': 1, 'large': 0})
    if hasattr(hero_equipped, 'set_potions_from_selection'):
        hero_equipped.set_potions_from_selection(
            potions_config.get('small', 0),
            potions_config.get('large', 0)
        )
    
    return {
        'hero_equipped': hero_equipped,
        'equipment': equipment_items,
        'build_name': build_config.get('name', 'Build Standard'),
        'is_custom': False,
        'difficulty_level': difficulty,
        'stats': hero_equipped.get_stats_summary(),
        'abilities_info': {
            'has_custom_abilities': False,
            'abilities_level': build_config.get('abilities_level', 1)  # Niveau réel du build
        }
    }

def get_hero_build_info(hero_code: str, heroes_list: List, equipment_list: List, loader, custom_builds_dict: Dict = None) -> Dict:
    """Build custom uniquement - inchangé"""
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

def get_hero_build_info_from_data(hero_code: str, build_data: Dict, heroes_list: List, equipment_list: List, loader) -> Dict:
    """
    NOUVEAU - Construit un héros depuis un build custom (depuis CSV)

    Args:
        hero_code: Code du héros
        build_data: {'name': '...', 'equipment': [...], 'abilities': [...], 'potions': {...}}
        heroes_list: Liste des héros
        equipment_list: Liste des équipements
        loader: DataLoader instance

    Returns:
        Dict avec hero_equipped, stats, etc.
    """
    hero = next(h for h in heroes_list if h.code == hero_code)
    hero_equipped = hero.model_copy()

    # Équipements
    equipment_items = [eq for eq in equipment_list if eq.code in build_data.get('equipment', [])]
    hero_equipped.equip_items(equipment_items, build_data.get('name', 'Build Custom'))

    # Capacités
    abilities = build_data.get('abilities', [])
    if abilities and build_data.get('abilities_custom'):
        try:
            hero_abilities = loader.get_hero_abilities(hero_code)
            if hero_abilities:
                selected_abilities = [a for a in hero_abilities if a.ability_number in abilities]
                if hasattr(hero_equipped, 'add_abilities') and selected_abilities:
                    hero_equipped.add_abilities(selected_abilities)
                    hero_equipped.unlocked_abilities = abilities.copy()
                    for ability in hero_equipped.abilities:
                        if ability.ability_number in abilities:
                            ability.is_unlocked = True
        except Exception:
            pass

    # Potions
    potions = build_data.get('potions', {})
    if potions and hasattr(hero_equipped, 'set_potions_from_selection'):
        hero_equipped.set_potions_from_selection(
            potions.get('small', 0),
            potions.get('large', 0)
        )

    return {
        'hero_equipped': hero_equipped,
        'equipment': equipment_items,
        'build_name': build_data.get('name', 'Build Custom'),
        'is_custom': True,
        'stats': hero_equipped.get_stats_summary(),
        'abilities_info': {
            'has_custom_abilities': build_data.get('abilities_custom', False),
            'abilities_level': len(abilities) if abilities else 0
        }
    }

def get_hero_final_stats(hero_code: str, heroes_list: List, equipment_list: List, loader, custom_builds_dict: Dict = None) -> Dict:
    """
    RÉVISÉ - Gère builds par défaut ET builds custom depuis CSV
    Priorité : selected_build_name > hero_difficulties > Normal par défaut
    """
    # Récupérer le build sélectionné pour ce héros
    selected_build_name = st.session_state.get('selected_build_name', {}).get(hero_code)

    # Détection du type de build
    is_default_build = selected_build_name in ['🟢 Facile', '🔵 Normal', '🔴 Difficile', '⚪ Vanilla', None]

    if not is_default_build and selected_build_name:
        # BUILD CUSTOM SÉLECTIONNÉ
        # Retirer le préfixe 🛠️ si présent
        build_name = selected_build_name.replace('🛠️ ', '')

        custom_builds_list = st.session_state.custom_builds.get(hero_code, [])
        build_data = next((b for b in custom_builds_list if b['name'] == build_name), None)

        if build_data:
            return get_hero_build_info_from_data(hero_code, build_data, heroes_list, equipment_list, loader)

    # BUILD PAR DÉFAUT (Facile/Normal/Difficile/Vanilla)
    if selected_build_name:
        # Extraire le nom de difficulté (sans emoji)
        if "Facile" in selected_build_name:
            difficulty = "Facile"
        elif "Difficile" in selected_build_name:
            difficulty = "Difficile"
        elif "Vanilla" in selected_build_name:
            difficulty = "Vanilla"
        else:
            difficulty = "Normal"
    else:
        # Fallback sur l'ancien système (hero_difficulties)
        difficulty = get_difficulty_level_name(hero_code)

    return get_hero_build_from_equipment(hero_code, heroes_list, equipment_list, loader, difficulty)

def prepare_teams_for_recap(hero_codes: List[str], enemy_codes: List[str], data, player_count: int):
    """Prépare données pour récapitulatif - MIGRÉ vers système équipements"""
    current_builds = st.session_state.get('custom_builds', {})
    
    # Données héros avec logique unifiée MIGRÉE
    heroes_data = []
    for code in hero_codes:
        build_info = get_hero_final_stats(code, data['heroes'], data['equipment'], data['loader'], current_builds)
        stats = build_info['stats']['total']
        
        heroes_data.append({
            'name': build_info['hero_equipped'].name,
            'icon': get_hero_icon(build_info['hero_equipped'].name),
            'build_name': build_info['build_name'],
            'is_custom': build_info['is_custom'],
            'difficulty_level': build_info.get('difficulty_level', 'Normal'),
            'precision': stats['precision'],
            'damage': stats['damage'],
            'health': stats['health'],
            'parade': stats['parade'],
            'spells': stats['spells']
        })
    
    # Données ennemis
    enemies_data = []
    for code in enemy_codes:
        enemy = next((e for e in data['enemies'] if e.code == code), None)
        if enemy is None:
            # Ennemi supprimé - ignorer silencieusement
            continue
        stats = enemy.get_stats_for_players(player_count)
        enemies_data.append({
            'code': enemy.code,  # Ajouté pour permettre la suppression depuis le récapitulatif
            'name': enemy.name,
            'number': enemy.code.split('-')[-1],
            'is_magical': enemy.is_magical,
            'health': stats['health'],
            'damage': stats['damage'],
            'defense': enemy.defense
        })
    
    return heroes_data, enemies_data

# === INITIALISATION ===

def init_app():
    """Configure Streamlit et session"""
    st.set_page_config(page_title="Périples – Atelier d'Équilibrage", page_icon="⚔️", layout="wide")
    os.makedirs("data", exist_ok=True)
    
    # NOUVEAU - Nettoyage automatique des pseudo-héros supprimés
    cleanup_removed_heroes_from_session()
    
    # Variables session avec valeurs par défaut
    defaults = {
        'selected_heroes': [],
        'selected_enemies': [],
        'custom_builds': {},  # NOUVEAU - Builds custom chargés depuis CSV (format: {hero_code: [build1, build2, ...]})
        'hero_difficulties': {},
        'hero_starting_health': {},  # Pourcentage de santé initiale par héros
        'selected_build_name': {},  # NOUVEAU - Build sélectionné par héros (défaut ou custom)
        'selected_theme': 'Professionnel',  # Thème par défaut
        'initiative_setting': True,  # Initiative D20 activée par défaut
        'criticals_setting': True,  # Critiques activés par défaut
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
        'heroes': filter_heroes_to_main_8(loader.load_heroes()),  # NOUVEAU - Filtrage à 8 héros
        'enemies': loader.load_all_enemies(),  # MODIFIÉ - Charge officiels + personnalisés
        'equipment': loader.load_equipment(),
        'custom_builds': loader.load_custom_builds(),  # NOUVEAU - Charge builds custom depuis CSV
        'loader': loader
    }

@st.cache_data
def get_preloaded_builds(_heroes_list, _equipment_list, _loader):
    """Cache les builds pré-calculés pour éviter de les recalculer à chaque interaction"""
    return preload_hero_builds_for_all_difficulties(_heroes_list, _equipment_list, _loader)

# === ONGLETS ===

def tab_selection(data):
    """Onglet sélection des équipes avec layout optimisé pour cartes héros"""
    # Configuration dans un expander
    # NOTE: Les initialisations session_state sont faites dans main() avant la création des onglets

    # Callbacks
    def on_initiative_change():
        st.session_state.initiative_setting = st.session_state.combat_initiative

    def on_criticals_change():
        st.session_state.criticals_setting = st.session_state.combat_criticals

    def on_theme_change():
        st.session_state.selected_theme = st.session_state.theme_selector

    heroes, enemies, loader = data['heroes'], data['enemies'], data['loader']
    nb_heroes = len(st.session_state.selected_heroes)
    nb_enemies = len(st.session_state.selected_enemies)

    # Tout sur une seule ligne : Config + Header + Progression + Reset
    col_theme, col_options, col_header, col_progress, col_reset = st.columns([1, 1, 2, 2, 1])

    with col_theme:
        from models.theme_manager import ThemeManager
        theme_display_names = ThemeManager.get_theme_display_names()
        available_themes = ThemeManager.get_available_themes()
        current_theme = st.session_state.get('selected_theme', 'Professionnel')
        current_index = available_themes.index(current_theme) if current_theme in available_themes else 0

        st.selectbox(
            "🎨 Thème",
            options=available_themes,
            index=current_index,
            format_func=lambda x: theme_display_names.get(x, x),
            key='theme_selector',
            on_change=on_theme_change
        )

    with col_options:
        st.checkbox(
            "🎯 Critiques",
            value=st.session_state.criticals_setting,
            key='combat_criticals',
            on_change=on_criticals_change
        )

        st.checkbox(
            "🎲 Initiative",
            value=st.session_state.initiative_setting,
            key='combat_initiative',
            on_change=on_initiative_change
        )

    with col_header:
        st.markdown("&nbsp;")  # Alignement vertical
        st.markdown("### 🏰 Sélection des Équipes")

    with col_progress:
        st.markdown("&nbsp;")  # Alignement vertical
        if nb_heroes < 2:
            st.warning(f"🎯 Sélectionnez au moins 2 héros ({nb_heroes}/2)")
        elif nb_enemies == 0:
            st.info("🎯 Maintenant sélectionnez vos ennemis")
        else:
            st.success(f"🎯 Prêt ! {nb_heroes} héros et {nb_enemies} ennemis")

    with col_reset:
        st.markdown("&nbsp;")  # Alignement vertical
        if nb_heroes > 0 or nb_enemies > 0:
            if st.button("🗑️ Reset",
                        key=f"reset_btn_{nb_heroes}_{nb_enemies}",
                        help=f"Effacer {nb_heroes} héros et {nb_enemies} ennemis sélectionnés",
                        use_container_width=True):
                safe_session_update('selected_heroes', [])
                safe_session_update('selected_enemies', [])
                safe_session_update('hero_difficulties', {})
                st.success("✅ Sélections effacées !")
                st.rerun()
    
    # === HÉROS - Layout optimisé ===
    st.subheader("🛡️ Héros Disponibles")
    
    # Info simplifiée
    if 'P-1' in st.session_state.selected_heroes:
        st.info("🐻 Elneha sélectionnée (formes d'animal gérées en combat)")
    
    # PRÉ-CALCUL DES BUILDS (mise en cache)
    preloaded_builds = get_preloaded_builds(heroes, data['equipment'], loader)
    
    # Grille héros 1 ligne x 8 colonnes
    current_builds = st.session_state.get('custom_builds', {})
    hero_changes = []

    # 8 héros sur une seule ligne
    cols = st.columns(8, gap="small")
    for hero_idx, hero in enumerate(heroes):
        is_selected = hero.code in st.session_state.selected_heroes

        with cols[hero_idx]:
            if display_hero_card(hero, is_selected, preloaded_builds, current_builds, ENABLE_IMAGES):
                hero_changes.append(hero.code)
    
    # Application des changements héros
    if hero_changes:
        for hero_code in hero_changes:
            toggle_hero_selection(hero_code)
        st.rerun()
    
    # === ENNEMIS - Layout optimisé ===
    st.subheader("👹 Ennemis")
    player_count = max(2, nb_heroes) if nb_heroes >= 2 else 2
    
    # Recherche compacte
    col_search, col_info = st.columns([1, 2])
    with col_search:
        search = st.text_input("Recherche", placeholder="Ex: 34, Dragon...", 
                              label_visibility="collapsed", key="enemy_search")
    with col_info:
        if search.strip():
            st.success("🎯 Recherche active")
        else:
            st.info("💡 Tapez un numéro ou nom pour chercher")
    
    # Filtrage
    if search.strip():
        term = search.lower()
        filtered = [e for e in enemies if term in e.code.split('-')[-1].lower() or term in e.name.lower()]
    else:
        filtered = enemies[:15]
    
    # Grille ennemis compacte
    if filtered:
        cols = st.columns(5, gap="small")
        enemy_changes = []
        
        for i, enemy in enumerate(filtered):
            is_selected = enemy.code in st.session_state.selected_enemies
            
            with cols[i % 5]:
                if display_enemy_card(enemy, is_selected, player_count):
                    enemy_changes.append(enemy.code)
        
        # Application des changements ennemis
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

        # Message incitatif pour lancer le Playtest
        st.markdown("---")
        st.success("""
        ✅ **Équipes prêtes !** Vos héros et ennemis sont sélectionnés.
        """)

        # Bouton pour basculer directement vers l'onglet Playtest
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Lancer le Playtest", type="primary", use_container_width=True):
                # Réinitialiser l'état du combat pour démarrer un combat frais
                reset_combat_state()
                # Naviguer vers l'onglet Playtest
                st.session_state.pending_navigation = "🎮 Playtest Manuel"
                st.rerun()

    else:
        # Message si sélection incomplète
        if nb_heroes < 2:
            st.info("ℹ️ Sélectionnez au moins **2 héros** pour commencer.")
        if nb_enemies == 0:
            st.info("ℹ️ Sélectionnez au moins **1 ennemi** pour commencer.")

def tab_forge(data):
    """Onglet forge des équipements - Version 8 héros MIGRÉE"""
    st.header("⚙️ Forge des Équipements")

    heroes, equipment = data['heroes'], data['equipment']

    # LIGNE COMPACTE : Héros + Sélecteur Build + Supprimer
    hero_options = {h.code: f"{get_hero_icon(h.name)} {h.name}" for h in heroes}

    col_hero, col_build, col_delete = st.columns([2, 2, 1])

    with col_hero:
        selected_code = st.selectbox(
            "Héros:",
            list(hero_options.keys()),
            format_func=lambda x: hero_options[x],
            key="forge_hero_selector",
            label_visibility="collapsed"
        )

    selected_hero = next(h for h in heroes if h.code == selected_code)

    # Liste des builds custom pour ce héros
    hero_custom_builds = st.session_state.custom_builds.get(selected_code, [])
    build_options = ["➕ Nouveau build"] + [b['name'] for b in hero_custom_builds]

    with col_build:
        selected_build = st.selectbox(
            "Build:",
            options=build_options,
            key=f"forge_build_selector_{selected_code}",
            label_visibility="collapsed"
        )

    # === SYNCHRONISATION BUILD → UI ===
    # Charger automatiquement les sélections du build SEULEMENT quand il change
    if FORGE_ABILITIES_AVAILABLE:
        # Clé pour tracker le dernier build sélectionné
        last_build_key = f"forge_last_build_{selected_code}"
        last_selected_build = st.session_state.get(last_build_key)

        # Synchroniser UNIQUEMENT si le build a changé
        if last_selected_build != selected_build:
            st.session_state[last_build_key] = selected_build

            if selected_build == "➕ Nouveau build":
                # Nouveau build : réinitialiser toutes les sélections
                reset_forge_selections(selected_code)
            else:
                # Build existant : charger ses sélections dans l'interface
                load_build_selections_into_ui(selected_code, selected_build)

    with col_delete:
        # Bouton supprimer uniquement si un build existant est sélectionné
        if selected_build != "➕ Nouveau build":
            if st.button("🗑️", key="forge_delete", use_container_width=True, help="Supprimer ce build"):
                data['loader'].delete_custom_build(selected_code, selected_build)
                # Recharger les builds
                st.session_state.custom_builds = data['loader'].load_custom_builds()
                st.success(f"✅ Build '{selected_build}' supprimé !")
                time.sleep(0.5)
                st.rerun()

    st.markdown("💡 *Les builds par défaut (Facile/Normal/Difficile/Vanilla) ne peuvent pas être modifiés.*")

    # Stats de base du héros
    st.subheader("📊 Statistiques")
    display_hero_base_stats(selected_hero)
    
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
            selected_abilities = display_abilities_selection_section(
                selected_code,
                hero_abilities,
                []  # Formulaire toujours vierge (pas de pré-remplissage)
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
            
            build_name = name.strip() or 'Build Custom'

            # Validation du nom
            reserved_names = ['Facile', 'Normal', 'Difficile', 'Vanilla', '🟢 Facile', '🔵 Normal', '🔴 Difficile', '⚪ Vanilla']
            if build_name in reserved_names:
                st.error("❌ Ce nom est réservé aux builds par défaut")
                st.stop()

            # Vérifier duplicata
            existing_builds = st.session_state.custom_builds.get(selected_code, [])
            if any(b['name'] == build_name for b in existing_builds):
                st.error(f"❌ Un build nommé '{build_name}' existe déjà")
                st.stop()

            build_data = {
                'name': build_name,
                'equipment': selected_eq,
                'abilities': selected_abilities if selected_abilities else [],
                'abilities_custom': len(selected_abilities) > 0,
                'potions': selected_potions
            }

            # Sauvegarde dans CSV
            try:
                data['loader'].save_custom_build(selected_code, build_data)
                # Recharger les builds
                st.session_state.custom_builds = data['loader'].load_custom_builds()
                st.success(f"✅ Build '{build_name}' sauvegardé !")
                time.sleep(0.5)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur lors de la sauvegarde: {e}")

def display_about():
    """Section À Propos - Version finale mise à jour"""

    # En-tête : Jeu de Société + Balance Workshop côte à côte
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎲 Jeu de Société")
        st.markdown("""
        **Périples** © Bastien LIAUTY
        - Genre : RPG coopératif médiéval-fantastique
        - Joueurs : 1 à 4 joueurs
        - Version des règles : V3.0

        **Données simulées :**
        - 8 héros jouables avec transformations
        - 72 ennemis évolutifs + **11 capacités ennemis**
        - 56 équipements + 4 objets spéciaux uniques
        - 48 capacités héros spéciales
        """)

    with col2:
        st.subheader("💻 Balance Workshop")
        st.markdown("""
        **Développement :**
        - Développeur : Christophe Bidouj
        - Assistance IA : Claude AI (Anthropic)
        - Technologies : Python, Streamlit, Pydantic

        **Modes de gestion des tours :**
        - 🎲 **Initiative (D20)** : Ordre automatique par jets de dés
        - 🎮 **Manuel** : Sélection libre de l'ordre de jeu
        - ↩️ **Undo/Redo** : Navigation dans l'historique
        - 📊 **Analyse avancée** : Métriques détaillées
        """)

    # Objectifs et usage (DÉPLACÉ EN HAUT)
    st.subheader("🎯 Objectifs de l'Atelier")
    st.markdown("""
    Cet **atelier d'équilibrage** permet de tester et valider les mécaniques de jeu :

    - **Équilibrage Multi-joueurs** : Validation de la scalabilité des ennemis (2J/3J/4J)
    - **Test de Builds** : Comparaison pré-définis vs personnalisés avec métriques détaillées
    - **Validation de Capacités** : Simulation complète des 48 capacités héros + 11 capacités ennemis
    - **Création de Contenu** : Forge d'équipements et ennemis personnalisés pour tests
    - **Analyse Stratégique** : Logs détaillés et statistiques pour optimisation tactique
    """)

    # Fonctionnalités principales
    st.subheader("⚙️ Fonctionnalités")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **🏰 Sélection & Configuration**
        - Builds héros pré-définis (Facile/Normal/Difficile)
        - **Builds personnalisés illimités** (CSV)
        - Configuration initiative & critiques
        - Sélection ennemis standards ou custom

        **⚙️ Forge d'Équipements**
        - Création d'équipements personnalisés
        - Édition des bonus et statistiques
        - Builds héros sur-mesure
        - Import/Export CSV
        """)

    with col2:
        st.markdown("""
        **⚔️ Gestion Ennemis**
        - **Création d'ennemis personnalisés**
        - Édition stats multi-joueurs (2J/3J/4J)
        - Association de capacités ennemis
        - Ennemis magiques et physiques

        **🎮 Playtest Manuel (Sandbox V2)**
        - Combats interactifs avec contrôle complet
        - Système de potions (petite/grande)
        - Ciblage manuel héros/ennemis
        - Logs de combat détaillés en temps réel
        """)

    # Systèmes avancés
    st.subheader("🔬 Systèmes Avancés")
    st.markdown("""
    **Capacités Héros (48 capacités)** : Soins, dégâts, buffs, invocations, transformations

    **Capacités Ennemis (11 types)** : Immunités, stun, attaques multiples, effets alternés/périodiques, blocages

    **Métriques de Combat** :
    - Taux de survie et durée de combat
    - Dégâts totaux infligés/reçus par combattant
    - Parade utilisée et sorts consommés
    - Soins reçus et capacités activées
    - Taux de critique et précision des attaques

    **Objets Spéciaux** : 4 objets uniques avec mécaniques complexes intégrées (Médaillon d'appel, etc.)
    """)

    # Avertissement usage
    st.info("""
    **📋 Usage autorisé :** Cet outil est destiné aux tests d'équilibrage pour l'équipe de développement du jeu Périples.
    L'usage commercial ou la redistribution ne sont pas autorisés.
    """)

# === MAIN ===

def main():
    """Application principale MIGRÉE"""
    init_app()

    # Gérer la navigation différée (avant la création des widgets)
    if 'pending_navigation' in st.session_state:
        st.session_state.main_navigation = st.session_state.pending_navigation
        del st.session_state.pending_navigation

    # Appliquer le thème sélectionné
    selected_theme = st.session_state.get('selected_theme', 'Professionnel')
    apply_fantasy_theme(selected_theme)

    # Titre natif Streamlit
    st.title("⚔️ Périples – Atelier d'Équilibrage ⚔️")
    st.caption("🎲 **Périples** © **Bastien LIAUTY** | 💻 Développeur : **Christophe Bidouj** | Simulateur d'équilibrage du jeu de société Périples")
    
    # Données avec cache
    try:
        data = load_data()
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
        st.stop()

    # NOUVEAU - Stocker les ennemis dans session_state pour rechargement dynamique
    # Initialisation au premier chargement
    if 'all_enemies' not in st.session_state:
        st.session_state.all_enemies = data['enemies']

    # Remplacer data['enemies'] par session_state pour utilisation dynamique
    data['enemies'] = st.session_state.all_enemies

    # NOUVEAU - Nettoyage automatique des ennemis supprimés
    from utils.data_loader import cleanup_removed_enemies_from_session
    valid_enemy_codes = [e.code for e in data['enemies']]
    cleanup_removed_enemies_from_session(valid_enemy_codes)

    # NOUVEAU - Charger les builds custom depuis CSV dans session_state
    if 'custom_builds' not in st.session_state or not st.session_state.custom_builds:
        st.session_state.custom_builds = data['custom_builds']

    # NOTE: Toutes les initialisations session_state sont faites dans init_app()

    # FIX : Utiliser st.radio() au lieu de st.tabs() pour mémoriser l'onglet actif
    # st.tabs() ne garde pas en mémoire l'onglet actif entre les reruns (limitation Streamlit)

    # Navigation par onglets avec mémorisation
    tabs_list = ["🏰 Sélection", "🎮 Playtest Manuel", "⚙️ Forge", "⚔️ Gestion Ennemis", "ℹ️ À Propos"]

    # Initialiser la navigation avec le premier onglet par défaut
    if 'main_navigation' not in st.session_state:
        st.session_state.main_navigation = tabs_list[0]

    # Radio buttons pour la navigation (Streamlit gère automatiquement la valeur via la clé)
    selected_tab = st.radio(
        "Navigation",
        tabs_list,
        horizontal=True,
        label_visibility="collapsed",
        key="main_navigation"
    )

    st.markdown("---")  # Séparateur visuel

    # Affichage du contenu selon l'onglet actif
    if selected_tab == "🏰 Sélection":
        tab_selection(data)
    elif selected_tab == "🎮 Playtest Manuel":
        main_sandbox_v2()
    elif selected_tab == "⚙️ Forge":
        tab_forge(data)
    elif selected_tab == "⚔️ Gestion Ennemis":
        main_enemy_editor()
    elif selected_tab == "ℹ️ À Propos":
        display_about()

if __name__ == "__main__":
    main()