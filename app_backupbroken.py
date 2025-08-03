#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulateur de Combat Périples - Application principale Streamlit
===============================================================

🎲 Jeu de société : Périples © Bastien LIAUTY
💻 Simulateur Python : Christophe Bidouj
🤖 Développement assisté par IA : Claude AI (Anthropic)
📅 Version : V4+ Interface Complète + Système Capacités (Phase 1-2)
🎯 Objectif : Équilibrage RPG et analyse tactique pour le jeu Périples

Architecture :
- Interface gaming moderne avec expanders natifs (zones blanches éliminées)
- Système de builds hybrides (standard + custom)
- Journal de combat détaillé prioritaire sur les statistiques
- Récapitulatif "Formation de Guerre" essentiel (à préserver)

Modules principaux :
- models/ : Character, Enemy, Equipment, CombatEngine, RulesEngine
- ui/components/ : Interface modulaire optimisée
- utils/ : DataLoader, AbilitiesLoader, StatsAnalyzer
"""

import streamlit as st
import time
import os
from typing import List, Dict
from models.character import Character, Enemy
from models.combat_engine import CombatEngine
from models.rules_engine import GameRules
from utils.data_loader import DataLoader

# Import des modules UI refactorisés
from ui.styling import (
    apply_fantasy_theme, 
    get_combat_button_styles,
    get_waiting_combat_style,
    get_app_title_style,
    Colors
)

# Import des composants depuis la structure modulaire
from ui.components import (
    # Héros
    display_hero_card,
    display_team_recap,
    display_hero_base_stats,
    display_current_build_info,
    display_new_stats_preview,
    
    # Ennemis
    display_enemy_card,
    
    # Équipements (version native avec nouvelles couleurs)
    display_equipment_selection_native,
    
    # Combat
    display_combat_result_banner,
    display_combat_metrics,
    display_heroes_individual_table,
    display_combat_log,
    display_combat_summary,
    
    # UI Elements
    display_progress_indicators_with_reset,
    get_hero_icon
)

# === CONFIGURATION ===
ENABLE_IMAGES = True

# === AJOUT : Gestion des formes d'Elneha ===
def get_elneha_forms() -> List[str]:
    """Retourne les codes des différentes formes d'Elneha (exclusion mutuelle)"""
    return ['P-1', 'P-9', 'P-10', 'P-11', 'P-12']  # Elneha, Ours, Loup, Ours S, Loup S

def clean_elneha_forms_from_selection(new_hero_code: str):
    """
    Supprime les autres formes d'Elneha si on sélectionne une forme d'Elneha
    
    Args:
        new_hero_code: Code du héros qu'on va ajouter
    """
    elneha_forms = get_elneha_forms()
    
    # Si le nouveau héros n'est pas une forme d'Elneha, rien à faire
    if new_hero_code not in elneha_forms:
        return
    
    # Supprimer toutes les autres formes d'Elneha de la sélection
    current_selection = st.session_state.get('selected_heroes', [])
    cleaned_selection = [code for code in current_selection if code not in elneha_forms]
    st.session_state.selected_heroes = cleaned_selection

# === CACHE ET UTILITAIRES ===
@st.cache_data(persist=True)
def get_cached_build_info(hero_code: str, _loader) -> Dict:
    try:
        hero_list = _loader.load_heroes()
        hero = next(h for h in hero_list if h.code == hero_code)
        return get_hero_build(hero, _loader)
    except Exception as e:
        # Retour de fallback en cas d'erreur
        return {
            'hero_equipped': None,
            'equipment': [],
            'build_name': 'Build Standard',
            'is_custom': False,
            'stats': {'total': {'precision': 0, 'damage': 0, 'spells': 0, 'health': 0, 'defense': 0}}
        }

def get_equipment_categories(equipment):
    """Catégorise les équipements selon leur type depuis Excel"""
    weapons, armor, accessories = [], [], []
    for eq in equipment:
        eq_type = eq.type.lower().strip() if hasattr(eq, 'type') and eq.type else 'accessoire'
        if eq_type == 'arme':
            weapons.append(eq)
        elif eq_type == 'armure':
            armor.append(eq)
        else:
            accessories.append(eq)
    return weapons, armor, accessories

# === FONCTIONS PRINCIPALES ===
def init_app():
    st.set_page_config(page_title="Simulateur RPG", page_icon="⚔️", layout="wide")
    if not os.path.exists("data"):
        os.makedirs("data")
    if 'selected_heroes' not in st.session_state:
        st.session_state.selected_heroes = []
    if 'selected_enemies' not in st.session_state:
        st.session_state.selected_enemies = []
    if 'custom_builds' not in st.session_state:
        st.session_state.custom_builds = {}

@st.cache_data
def load_data():
    loader = DataLoader()
    missing_files = [f for f in ["heroes.csv", "enemies.csv", "equipment.csv"] 
                     if not os.path.exists(f"data/{f}")]
    if missing_files:
        st.info("🔄 Création fichiers données...")
        loader.create_csv_files()
        st.success("✅ Fichiers créés !")
        time.sleep(1)
        st.rerun()
    return {'heroes': loader.load_heroes(), 'enemies': loader.load_enemies(), 
            'equipment': loader.load_equipment(), 'loader': loader}

def get_hero_build(hero: Character, loader: DataLoader) -> Dict:
    """Récupère les informations de build d'un héros (standard ou custom)"""
    if hero.code in st.session_state.custom_builds:
        custom_data = st.session_state.custom_builds[hero.code]
        equipment_codes = custom_data.get('equipment', [])
        all_equipment = loader.load_equipment()
        hero_equipment = [eq for eq in all_equipment if eq.code in equipment_codes]
        build_name = custom_data.get('name', 'Build Custom')
        is_custom = True
    else:
        hero_equipment = loader.get_hero_loadout(hero.code)
        build_name = "Build Standard"
        is_custom = False
    
    hero_copy = hero.model_copy()
    hero_copy.equip_items(hero_equipment, build_name)
    return {'hero_equipped': hero_copy, 'equipment': hero_equipment,
            'build_name': build_name, 'is_custom': is_custom, 'stats': hero_copy.get_stats_summary()}

def prepare_hero_details(selected_heroes: List[str], data: Dict) -> List[Dict]:
    """Prépare les détails des héros sélectionnés pour le récapitulatif"""
    hero_details = []
    
    for hero_code in selected_heroes:
        hero = next(h for h in data['heroes'] if h.code == hero_code)
        build_info = get_hero_build(hero, data['loader'])
        stats = build_info['stats']['total']
        
        hero_details.append({
            'hero': hero,
            'hero_equipped': build_info['hero_equipped'],
            'equipment': build_info['equipment'],
            'build_name': build_info['build_name'],
            'is_custom': build_info['is_custom'],
            'stats': build_info['stats'],
            # Ajout des données attendues par display_team_recap
            'name': hero.name,
            'icon': get_hero_icon(hero.name),
            'precision': stats['precision'],
            'damage': stats['damage'],
            'health': stats['health'],
            'parade': stats['parade'],
            'spells': stats['spells']
        })
    
    return hero_details

def prepare_enemy_details(selected_enemies: List[str], data: Dict) -> List[Dict]:
    """Prépare les détails des ennemis sélectionnés"""
    enemy_details = []
    
    for enemy_code in selected_enemies:
        enemy = next(e for e in data['enemies'] if e.code == enemy_code)
        # Extraction du numéro depuis le code (ex: "E-1" -> "1")
        enemy_number = enemy.code.split('-')[1] if '-' in enemy.code else enemy.code
        
        enemy_details.append({
            'name': enemy.name,
            'number': enemy_number,
            'health': enemy.stats_by_players.get(2, {}).get('health', 0),  # Par défaut 2J
            'damage': enemy.stats_by_players.get(2, {}).get('damage', 0),
            'defense': enemy.stats_by_players.get(2, {}).get('defense', 0),
            'is_magical': enemy.is_magical,
            'enemy_obj': enemy  # Garder l'objet original pour le combat
        })
    
    return enemy_details

def validate_team_selection(selected_heroes: List[str], selected_enemies: List[str]) -> tuple:
    """Valide la sélection d'équipes et retourne (is_valid, error_message)"""
    if len(selected_heroes) < 2:
        return False, "🔴 Sélectionnez au moins 2 héros"
    if len(selected_enemies) < 1:
        return False, "🔴 Sélectionnez au moins 1 ennemi"
    if len(selected_heroes) > 4:
        return False, "🔴 Maximum 4 héros autorisés"
    return True, ""

def display_about_section():
    """Affiche la section À Propos avec style professionnel"""
    
    # En-tête principal avec style gaming
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(139,69,19,0.1), rgba(212,175,55,0.1));
                border: 3px solid #d4af37; border-radius: 20px; padding: 25px; margin: 20px 0;
                text-align: center;">
        <h2 style="color: #8b4513; font-family: 'Cinzel', serif; margin: 0;">
            ⚔️ Simulateur de Combat Périples ⚔️
        </h2>
        <p style="color: #666; font-size: 1.1rem; margin: 10px 0 0 0;">
            Outil professionnel d'équilibrage RPG
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Colonnes pour organisation
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Informations sur le jeu
        st.markdown("""
        <div style="background: rgba(34,139,34,0.08); border-left: 4px solid #228b22; 
                    padding: 20px; border-radius: 10px; margin: 10px 0;">
            <h3 style="color: #006400; margin-top: 0;">🎲 Jeu de Société</h3>
            <p><strong>Périples</strong> © Bastien LIAUTY</p>
            <p><strong>Version des règles :</strong> V3.0 (Janvier 2025)</p>
            <p><strong>Genre :</strong> RPG coopératif médiéval-fantastique</p>
            <p><strong>Joueurs :</strong> 1 à 4 joueurs</p>
            <p><strong>Statut :</strong> Prototype en développement</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Objectif du simulateur
        st.markdown("""
        <div style="background: rgba(139,0,0,0.08); border-left: 4px solid #8b0000; 
                    padding: 20px; border-radius: 10px; margin: 10px 0;">
            <h3 style="color: #8b0000; margin-top: 0;">🎯 Objectif</h3>
            <p>Outil d'analyse et d'équilibrage pour :</p>
            <ul>
                <li>Tests de balance des personnages</li>
                <li>Validation des règles de combat</li>
                <li>Optimisation des équipements</li>
                <li>Analyse tactique approfondie</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Informations techniques
        st.markdown("""
        <div style="background: rgba(70,130,180,0.08); border-left: 4px solid #4682b4; 
                    padding: 20px; border-radius: 10px; margin: 10px 0;">
            <h3 style="color: #2e4b6b; margin-top: 0;">💻 Simulateur Python</h3>
            <p><strong>Développeur Principal :</strong> Christophe Bidouj</p>
            <p><strong>Développement assisté par IA :</strong> Claude AI (Anthropic)</p>
            <p><strong>Technologies :</strong> Python, Streamlit, Pydantic</p>
            <p><strong>Version :</strong> V4+ Interface + Capacités</p>
            <p><strong>Statut :</strong> En développement actif</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Public cible
        st.markdown("""
        <div style="background: rgba(138,43,226,0.08); border-left: 4px solid #8a2be2; 
                    padding: 20px; border-radius: 10px; margin: 10px 0;">
            <h3 style="color: #663399; margin-top: 0;">👥 Public Cible</h3>
            <ul>
                <li><strong>Équipe d'équilibrage</strong> du jeu Périples</li>
                <li><strong>Testeurs avancés</strong> et analystes</li>
                <li><strong>Créateur du jeu</strong> pour validation</li>
            </ul>
            <p style="margin-top: 15px;"><em>Usage strictement limité au développement et tests d'équilibrage</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Fonctionnalités principales
    st.subheader("⚡ Fonctionnalités Principales")
    
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    
    with col_feat1:
        st.markdown("""
        **🛡️ Sélection d'Équipes**
        - 12 héros avec formes d'Elneha
        - 72 ennemis avec stats évolutives
        - Interface intuitive par cartes
        - Récapitulatif "Formation de Guerre"
        """)
    
    with col_feat2:
        st.markdown("""
        **⚔️ Simulation de Combat**
        - Moteur fidèle aux règles V3.0
        - Journal détaillé action par action
        - Métriques d'équilibrage avancées
        - Validation des stratégies
        """)
    
    with col_feat3:
        st.markdown("""
        **🛠️ Forge d'Équipements**
        - 52 équipements catégorisés
        - Builds hybrides (standard + custom)
        - Aperçu stats en temps réel
        - Sauvegarde des configurations
        """)
    
    st.markdown("---")
    
    # État du développement
    st.subheader("🚀 État du Développement")
    
    # Barres de progression avec style
    progress_data = [
        ("Interface Utilisateur", 100, "#228b22"),
        ("Moteur de Combat", 90, "#ff8c00"),
        ("Système d'Équipements", 100, "#4682b4"),
        ("Système de Capacités", 60, "#8a2be2"),
        ("Règles Avancées", 70, "#dc143c")
    ]
    
    for feature, progress, color in progress_data:
        st.markdown(f"""
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: bold;">{feature}</span>
                <span style="color: {color}; font-weight: bold;">{progress}%</span>
            </div>
            <div style="background: #f0f0f0; border-radius: 10px; height: 10px;">
                <div style="background: {color}; height: 10px; border-radius: 10px; width: {progress}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Footer professionnel
    st.markdown("""
    <div style="background: rgba(105,105,105,0.1); border-radius: 10px; padding: 20px; 
                text-align: center; margin: 20px 0;">
        <p style="margin: 0; color: #666; font-size: 0.9rem;">
            <strong>Périples</strong> © Bastien LIAUTY - Tous droits réservés<br>
            Simulateur développé par <strong>Christophe Bidouj</strong> avec assistance <strong>Claude AI</strong><br>
            <em>Usage autorisé : Développement et tests d'équilibrage uniquement</em>
        </p>
        <p style="margin: 10px 0 0 0; color: #999; font-size: 0.8rem;">
            Version V4+ • Interface Optimisée • Août 2025
        </p>
    </div>
    """, unsafe_allow_html=True)

# === INTERFACE PRINCIPALE ===
def main():
    init_app()
    apply_fantasy_theme()
    
    # Chargement des données
    data = load_data()
    
    # TITRE PRINCIPAL avec style
    title_html = get_app_title_style()
    st.markdown(title_html, unsafe_allow_html=True)
    
    # AFFICHAGE CRÉDITS DÉVELOPPEMENT
    st.markdown("""
    <div style="text-align: center; font-size: 0.8rem; color: #666; margin-bottom: 20px;">
        🎲 Jeu Périples © Bastien LIAUTY | 
        💻 Simulateur Python : Christophe Bidouj
    </div>
    """, unsafe_allow_html=True)
    
    # ONGLETS PRINCIPAUX
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Sélection des Équipes", 
        "🛠️ Forge des Équipements", 
        "📊 Chroniques de Combat",
        "ℹ️ À Propos"
    ])
    
    # === ONGLET 1: SÉLECTION DES ÉQUIPES ===
    with tab1:
        st.header("🎯 Sélection des Équipes")
        
        # INDICATEURS DE PROGRESSION avec reset
        nb_heroes = len(st.session_state.selected_heroes)
        nb_enemies = len(st.session_state.selected_enemies)
        display_progress_indicators_with_reset(nb_heroes, nb_enemies)
        
        # === SECTION HÉROS ===
        st.subheader("🛡️ Héros Disponibles")
        
        # Affichage des héros en grille 4 par ligne
        heroes_per_row = 4
        heroes = data['heroes']
        
        for i in range(0, len(heroes), heroes_per_row):
            row_heroes = heroes[i:i + heroes_per_row]
            cols = st.columns(heroes_per_row)
            
            for j, hero in enumerate(row_heroes):
                with cols[j]:
                    # Vérifier si le héros est sélectionné
                    is_selected = hero.code in st.session_state.selected_heroes
                    
                    # Afficher la carte héros
                    build_info = get_hero_build(hero, data['loader'])
                    display_hero_card(hero, build_info, is_selected, ENABLE_IMAGES, False)
                    
                    # Boutons de sélection
                    if is_selected:
                        if st.button(f"❌ Retirer", key=f"remove_hero_{hero.code}", 
                                   help=f"Retirer {hero.name} de l'équipe"):
                            st.session_state.selected_heroes.remove(hero.code)
                            st.rerun()
                    else:
                        if st.button(f"✅ Sélectionner", key=f"add_hero_{hero.code}",
                                   help=f"Ajouter {hero.name} à l'équipe"):
                            # Gestion des formes d'Elneha (exclusion mutuelle)
                            clean_elneha_forms_from_selection(hero.code)
                            
                            if len(st.session_state.selected_heroes) < 4:
                                st.session_state.selected_heroes.append(hero.code)
                                st.rerun()
                            else:
                                st.warning("🔴 Maximum 4 héros autorisés")
        
        st.markdown("---")
        
        # === SECTION ENNEMIS ===
        st.subheader("👹 Ennemis Disponibles")
        
        # Recherche d'ennemis
        col_search, col_players = st.columns([3, 1])
        with col_search:
            search_term = st.text_input("🔍 Rechercher un ennemi (nom ou numéro)", 
                                       placeholder="Ex: Okkoto, E-1, Loup...")
        
        with col_players:
            player_count = st.selectbox("👥 Mode joueurs", [2, 3, 4], index=0, 
                                      help="Ajuste les stats des ennemis selon le nombre de joueurs")
        
        # Filtrage des ennemis
        enemies = data['enemies']
        if search_term:
            search_lower = search_term.lower()
            enemies = [e for e in enemies if search_lower in e.name.lower() or search_lower in e.code.lower()]
        
        # Affichage des ennemis en expanders (5 par ligne)
        enemies_per_row = 5
        
        for i in range(0, len(enemies), enemies_per_row):
            row_enemies = enemies[i:i + enemies_per_row]
            cols = st.columns(enemies_per_row)
            
            for j, enemy in enumerate(row_enemies):
                with cols[j]:
                    # Vérifier si l'ennemi est sélectionné
                    is_selected = enemy.code in st.session_state.selected_enemies
                    
                    # Afficher la carte ennemi
                    display_enemy_card(enemy, player_count, is_selected)
                    
                    # Boutons de sélection
                    if is_selected:
                        if st.button(f"❌", key=f"remove_enemy_{enemy.code}", 
                                   help=f"Retirer {enemy.name}"):
                            st.session_state.selected_enemies.remove(enemy.code)
                            st.rerun()
                    else:
                        if st.button(f"✅", key=f"add_enemy_{enemy.code}",
                                   help=f"Ajouter {enemy.name}"):
                            st.session_state.selected_enemies.append(enemy.code)
                            st.rerun()
        
        st.markdown("---")
        
        # === RÉCAPITULATIF FORMATION DE GUERRE (ESSENTIEL) ===
        if st.session_state.selected_heroes or st.session_state.selected_enemies:
            hero_details = prepare_hero_details(st.session_state.selected_heroes, data)
            enemy_details = prepare_enemy_details(st.session_state.selected_enemies, data)
            
            # Afficher le récapitulatif complet
            display_team_recap(hero_details, enemy_details, player_count)
            
            # Validation et bouton de combat
            is_valid, error_msg = validate_team_selection(
                st.session_state.selected_heroes, 
                st.session_state.selected_enemies
            )
            
            if error_msg:
                st.warning(error_msg)
            
            if is_valid:
                # Style du bouton de combat
                combat_button_style = get_combat_button_styles()
                st.markdown(combat_button_style, unsafe_allow_html=True)
                
                if st.button("⚔️ LANCER LE COMBAT ⚔️", 
                           key="launch_combat", 
                           help="Démarrer la simulation de combat"):
                    
                    # Préparation du combat
                    with st.spinner("🎲 Préparation du combat..."):
                        heroes_for_combat = [detail['hero_equipped'] for detail in hero_details]
                        enemies_for_combat = []
                        
                        for enemy_detail in enemy_details:
                            enemy = enemy_detail['enemy_obj']  # Récupérer l'objet Enemy original
                            enemy_copy = enemy.model_copy()
                            enemy_copy.adjust_for_player_count(player_count)
                            enemies_for_combat.append(enemy_copy)
                        
                        # Lancement du combat
                        rules = GameRules()
                        engine = CombatEngine(rules)
                        result = engine.simulate_combat(heroes_for_combat, enemies_for_combat)
                        
                        # Stockage du résultat
                        st.session_state.last_combat_result = result
                        st.session_state.last_hero_details = hero_details
                        st.session_state.last_enemy_details = enemy_details
                        st.session_state.last_player_count = player_count
                    
                    st.success("✅ Combat terminé ! Consultez l'onglet 'Chroniques de Combat'")
                    time.sleep(1)
                    st.rerun()
    
    # === ONGLET 2: FORGE DES ÉQUIPEMENTS ===
    with tab2:
        st.header("🛠️ Forge des Équipements")
        
        if not st.session_state.selected_heroes:
            st.info("🎯 Sélectionnez d'abord des héros dans l'onglet 'Sélection' pour configurer leurs équipements")
        else:
            # Sélection du héros à équiper
            hero_codes = st.session_state.selected_heroes
            hero_names = [next(h.name for h in data['heroes'] if h.code == code) for code in hero_codes]
            hero_options = [f"{code} - {name}" for code, name in zip(hero_codes, hero_names)]
            
            selected_hero_option = st.selectbox("🎯 Héros à équiper", hero_options)
            selected_hero_code = selected_hero_option.split(" - ")[0]
            selected_hero = next(h for h in data['heroes'] if h.code == selected_hero_code)
            
            # Affichage des stats de base du héros
            col1, col2 = st.columns([1, 2])
            
            with col1:
                display_hero_base_stats(selected_hero)
            
            with col2:
                # Informations du build actuel
                current_build_info = get_hero_build(selected_hero, data['loader'])
                display_current_build_info(current_build_info)
            
            st.markdown("---")
            
            # === SÉLECTION D'ÉQUIPEMENTS ===
            st.subheader("⚔️ Sélection d'Équipements")
            
            # Catégorisation des équipements
            weapons, armor, accessories = get_equipment_categories(data['equipment'])
            
            # Interface de sélection native avec expanders
            selected_equipment_codes = display_equipment_selection_native(
                weapons, armor, accessories, selected_hero_code
            )
            
            # === APERÇU DES NOUVELLES STATS ===
            if selected_equipment_codes:
                st.markdown("---")
                st.subheader("📊 Aperçu du Nouveau Build")
                
                # Nom du build custom
                custom_build_name = st.text_input("🏷️ Nom du build", 
                                                value=f"Build {selected_hero.name} Custom",
                                                help="Donnez un nom à votre configuration d'équipements")
                
                # Calcul et affichage des nouvelles stats
                preview_equipment = [eq for eq in data['equipment'] if eq.code in selected_equipment_codes]
                display_new_stats_preview(selected_hero, preview_equipment, custom_build_name)
                
                # Bouton de sauvegarde
                if st.button("💾 Sauvegarder ce Build", 
                           help="Sauvegarder cette configuration d'équipements"):
                    st.session_state.custom_builds[selected_hero_code] = {
                        'equipment': selected_equipment_codes,
                        'name': custom_build_name
                    }
                    st.success(f"✅ Build '{custom_build_name}' sauvegardé pour {selected_hero.name} !")
                    time.sleep(1)
                    st.rerun()
            
            # === GESTION DES BUILDS SAUVEGARDÉS ===
            if selected_hero_code in st.session_state.custom_builds:
                st.markdown("---")
                st.subheader("🗂️ Build Sauvegardé")
                
                custom_data = st.session_state.custom_builds[selected_hero_code]
                st.info(f"📁 Build actuel : **{custom_data['name']}**")
                
                if st.button("🗑️ Supprimer le Build Custom", 
                           help="Revenir au build standard"):
                    del st.session_state.custom_builds[selected_hero_code]
                    st.success(f"✅ Build custom supprimé, retour au build standard")
                    time.sleep(1)
                    st.rerun()
    
    # === ONGLET 3: CHRONIQUES DE COMBAT ===
    with tab3:
        st.header("📊 Chroniques de Combat")
        
        if 'last_combat_result' not in st.session_state:
            st.info("🎯 Aucun combat disponible. Lancez un combat depuis l'onglet 'Sélection' !")
        else:
            result = st.session_state.last_combat_result
            hero_details = st.session_state.last_hero_details
            enemy_details = st.session_state.last_enemy_details
            player_count = st.session_state.last_player_count
            
            # Bannière de résultat
            display_combat_result_banner(result)
            
            st.markdown("---")
            
            # Métriques de combat
            display_combat_metrics(result, hero_details, enemy_details, player_count)
            
            st.markdown("---")
            
            # Tableaux individuels des héros
            display_heroes_individual_table(result, hero_details)
            
            st.markdown("---")
            
            # Journal de combat détaillé
            st.subheader("📜 Journal de Combat Détaillé")
            display_combat_log(result)
            
            st.markdown("---")
            
            # Résumé final
            display_combat_summary(result)
    
    # === ONGLET 4: À PROPOS ===
    with tab4:
        display_about_section()

if __name__ == "__main__":
    main()