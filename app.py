#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Périples Balance Workshop - Version Complète
🎲 Jeu : Périples © Bastien Liauty
💻 Code : Christophe Bidouj (assistance Claude AI)
NOUVEAU : Intégration potions + boutons compacts Forge
"""

import streamlit as st
import time
import os
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
        validate_abilities_selection,
        display_potions_selection_section,  # NOUVEAU
        get_forge_selections_summary        # NOUVEAU
    )
    FORGE_ABILITIES_AVAILABLE = True
except ImportError:
    FORGE_ABILITIES_AVAILABLE = False

# Configuration
ENABLE_IMAGES = True

# === UTILITAIRES SIMPLES ===
def get_elneha_forms() -> List[str]:
    """Formes d'Elneha (exclusion mutuelle)"""
    return ['P-1', 'P-9', 'P-10', 'P-11', 'P-12']

def clean_elneha_forms(new_hero_code: str):
    """Supprime autres formes d'Elneha si on en sélectionne une"""
    if new_hero_code in get_elneha_forms():
        current = st.session_state.get('selected_heroes', [])
        st.session_state.selected_heroes = [code for code in current if code not in get_elneha_forms()]

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
    
    # Variables session
    defaults = {
        'selected_heroes': [], 
        'selected_enemies': [], 
        'custom_builds': {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

@st.cache_data
def load_data():
    """Charge toutes les données"""
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
    """
    Calcule build d'un héros AVEC SUPPORT CAPACITÉS ET POTIONS
    NOUVEAU : Intégration potions dans les builds custom
    """
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
        # NOUVEAU - Support potions
        custom_potions = custom.get('potions', {})
    else:
        equipment = _loader.get_hero_loadout(hero_code)
        build_name = "Build Standard"
        is_custom = False
        custom_abilities = []
        abilities_custom = False
        custom_potions = {}
    
    # Héros équipé
    hero_equipped = hero.model_copy()
    hero_equipped.equip_items(equipment, build_name)
    
    # NOUVEAU - Application potions custom
    if custom_potions and is_custom:
        try:
            small_count = custom_potions.get('small', 0)
            large_count = custom_potions.get('large', 0)
            if hasattr(hero_equipped, 'set_potions_from_selection'):
                hero_equipped.set_potions_from_selection(small_count, large_count)
        except Exception as e:
            print(f"⚠️ Erreur potions custom {hero_code}: {e}")
    
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
            print(f"⚠️ Erreur capacités custom {hero_code}: {e}")
    
    # Résultat avec infos capacités ET potions
    result = {
        'hero_equipped': hero_equipped,
        'equipment': equipment,
        'build_name': build_name,
        'is_custom': is_custom,
        'stats': hero_equipped.get_stats_summary()
    }
    
    # Info capacités
    if custom_abilities and abilities_custom:
        try:
            hero_abilities = _loader.get_hero_abilities(hero_code)
            selected_ability_objects = [a for a in hero_abilities if a.ability_number in custom_abilities]
            result['abilities_info'] = {
                'has_custom_abilities': True,
                'selected_count': len(custom_abilities),
                'selected_names': [a.name for a in selected_ability_objects],
                'total_spell_cost': sum(a.spell_cost for a in selected_ability_objects)
            }
        except:
            result['abilities_info'] = {'has_custom_abilities': False}
    else:
        result['abilities_info'] = {'has_custom_abilities': False}
    
    # NOUVEAU - Info potions
    if custom_potions and is_custom:
        potions_summary = hero_equipped.get_potions_summary() if hasattr(hero_equipped, 'get_potions_summary') else {}
        result['potions_info'] = {
            'has_custom_potions': potions_summary.get('has_potions', False),
            'display_text': potions_summary.get('display_text', 'Aucune potion'),
            'total_count': potions_summary.get('total_count', 0)
        }
    else:
        result['potions_info'] = {'has_custom_potions': False, 'display_text': 'Potions standard'}
    
    return result

def prepare_teams_for_recap(hero_codes: List[str], enemy_codes: List[str], data, player_count: int):
    """Prépare données pour récapitulatif"""
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

# === ONGLET À PROPOS - VERSION FINALE RÉORGANISÉE ===
def display_about():
    """Section À Propos avec design gaming élégant - RÉORGANISATION ESTHÉTIQUE FINALE"""
    
    # TITRE PRINCIPAL - Centré et imposant
    st.markdown("""
    <div style="background: linear-gradient(135deg, #8b4513, #d4af37, #8b4513);
                border: 4px solid #d4af37; border-radius: 25px; padding: 30px; margin: 25px 0;
                text-align: center; box-shadow: 0 8px 32px rgba(139,69,19,0.3);">
        <h1 style="color: #fff; font-family: 'Cinzel', serif; margin: 0; font-size: 2.5rem; 
                   text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
            ⚔️ PÉRIPLES BALANCE WORKSHOP ⚔️
        </h1>
        <h3 style="color: #f4f4f4; margin: 15px 0 5px 0; font-style: italic;">
            Simulateur RPG Professionnel • Version V5+ Capacités & Potions
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # SECTION 1 - INFORMATIONS PROJET (2 colonnes équilibrées)
    st.markdown("""
    <div style="margin: 30px 0 20px 0;">
        <h2 style="text-align: center; color: #8b4513; font-family: 'Cinzel', serif; margin-bottom: 25px;">
            📋 INFORMATIONS PROJET
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(139,69,19,0.1), rgba(244,228,188,0.8));
                    border: 3px solid #8b4513; border-radius: 15px; padding: 20px; margin: 10px 0;
                    min-height: 200px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h3 style="color: #8b4513; margin-top: 0; text-align: center; font-family: 'Cinzel', serif;">
                    🎲 JEU DE SOCIÉTÉ
                </h3>
                <div style="line-height: 1.6; font-size: 0.95rem;">
                    <strong style="color: #8b4513;">Périples</strong> © <strong style="color: #228b22;">Bastien Liauty</strong><br>
                    <strong>Version :</strong> V3.0 (2025)<br>
                    <strong>Genre :</strong> RPG coopératif médiéval-fantastique<br>
                    <strong>Joueurs :</strong> 1 à 4 joueurs<br>
                    <strong>Statut :</strong> Prototype en développement
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(70,130,180,0.1), rgba(244,228,188,0.8));
                    border: 3px solid #4682b4; border-radius: 15px; padding: 20px; margin: 10px 0;
                    min-height: 200px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h3 style="color: #4682b4; margin-top: 0; text-align: center; font-family: 'Cinzel', serif;">
                    💻 BALANCE WORKSHOP
                </h3>
                <div style="line-height: 1.6; font-size: 0.95rem;">
                    <strong>Dev Python :</strong><strong style="color: #4682b4;"> Christophe Bidouj</strong><br>
                    <strong>Assistance IA :</strong> Claude AI (Anthropic)<br>
                    <strong>Technologies :</strong> Python + Streamlit + Pydantic<br>
                    <strong>Version :</strong> V5+ Capacités + Potions<br>
                    <strong>Statut :</strong> En développement actif
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # SECTION 2 - ARSENAL DES FONCTIONNALITÉS (3 colonnes harmonieuses)
    st.markdown("""
    <div style="margin: 40px 0 20px 0;">
        <h2 style="text-align: center; color: #8b4513; font-family: 'Cinzel', serif; margin-bottom: 25px;">
            ⚡ ARSENAL DES FONCTIONNALITÉS
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(34,139,34,0.1), rgba(244,228,188,0.8));
                    border: 3px solid #228b22; border-radius: 15px; padding: 18px; margin: 10px 0;
                    min-height: 240px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h4 style="color: #228b22; margin-top: 0; text-align: center; font-family: 'Cinzel', serif;">
                    🛡️ SÉLECTION
                </h4>
                <div style="line-height: 1.5; font-size: 0.9rem;">
                    • <strong>12 héros</strong> + formes Elneha<br>
                    • <strong>72 ennemis</strong> évolutifs<br>
                    • <strong>Interface par cartes</strong> intuitive<br>
                    • <strong>Récap "Formation de Guerre"</strong><br>
                    • <strong>Recherche intelligente</strong> par nom/numéro
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(220,20,60,0.1), rgba(244,228,188,0.8));
                    border: 3px solid #dc143c; border-radius: 15px; padding: 18px; margin: 10px 0;
                    min-height: 240px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h4 style="color: #dc143c; margin-top: 0; text-align: center; font-family: 'Cinzel', serif;">
                    ⚔️ COMBAT
                </h4>
                <div style="line-height: 1.5; font-size: 0.9rem;">
                    • <strong>Moteur règles V3.0</strong> officiel<br>
                    • <strong>IA tactique intelligente</strong><br>
                    • <strong>Journal action par action</strong><br>
                    • <strong>Métriques d'équilibrage</strong> RPG<br>
                    • <strong>Validation stratégies</strong> complètes
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(138,43,226,0.1), rgba(244,228,188,0.8));
                    border: 3px solid #8a2be2; border-radius: 15px; padding: 18px; margin: 10px 0;
                    min-height: 240px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h4 style="color: #8a2be2; margin-top: 0; text-align: center; font-family: 'Cinzel', serif;">
                    🛠️ FORGE
                </h4>
                <div style="line-height: 1.5; font-size: 0.9rem;">
                    • <strong>52 équipements</strong> catégorisés<br>
                    • <strong>48 capacités</strong> (6 par héros)<br>
                    • <strong>🧪 Potions santé custom</strong><br>
                    • <strong>Builds hybrides</strong> sauvegardables<br>
                    • <strong>Système d'Orchestration des Capacités</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # SECTION 3 - INNOVATIONS TECHNIQUES V5+ (Section mise en valeur)
    st.markdown("""
    <div style="margin: 40px 0 20px 0;">
        <h2 style="text-align: center; color: #8b4513; font-family: 'Cinzel', serif; margin-bottom: 25px;">
            🚀 INNOVATIONS TECHNIQUES V5+
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255,140,0,0.1), rgba(244,228,188,0.8));
                    border: 3px solid #ff8c00; border-radius: 15px; padding: 20px; margin: 10px 0;">
            <h4 style="color: #ff8c00; margin-top: 0; text-align: center; font-family: 'Cinzel', serif;">
                🎯 ORCHESTRATION DES CAPACITÉS
            </h4>
            <div style="line-height: 1.5; font-size: 0.9rem;">
                • <strong>IA tactique avancée</strong> : priorités hiérarchiques<br>
                • <strong>Protection builds custom</strong> : respect absolu des choix<br>
                • <strong>Comportements émergents</strong> : Clerc, Mage, Tank, Hybride naturels<br>
                • <strong>Règles officielles</strong> : Capacités magiques empêchent l'attaque physique etc<br>
                • <strong>Interface intuitive</strong> : grille 3x2 expanders natifs
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(220,20,60,0.1), rgba(244,228,188,0.8));
                    border: 3px solid #dc143c; border-radius: 15px; padding: 20px; margin: 10px 0;">
            <h4 style="color: #dc143c; margin-top: 0; text-align: center; font-family: 'Cinzel', serif;">
                🧪 SYSTÈME DE POTIONS
            </h4>
            <div style="line-height: 1.5; font-size: 0.9rem;">
                • <strong>Intégration builds custom</strong> : 0-3 🩸 + 0-1 ❤️‍🩹<br>
                • <strong>IA utilisation intelligente</strong> : automatique si PV < 50%<br>
                • <strong>Interface cohérente</strong> : même style que capacités<br>
                • <strong>Aperçu temps réel</strong> : dans section "Nouveau Build"<br>
                • <strong>Validation robuste</strong> : limites et fallbacks intégrés
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # SECTION 4 - MÉTRIQUES PROJET (Bilan impressionnant)
    st.markdown("""
    <div style="margin: 40px 0 20px 0;">
        <h2 style="text-align: center; color: #8b4513; font-family: 'Cinzel', serif; margin-bottom: 25px;">
            📊 MÉTRIQUES PROJET
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Métriques en 4 colonnes compactes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🧙‍♂️ Héros",
            value="12",
            delta="+ 4 formes Elneha"
        )
    
    with col2:
        st.metric(
            label="👹 Ennemis",
            value="72",
            delta="Stats évolutives"
        )
    
    with col3:
        st.metric(
            label="⚔️ Équipements",
            value="52",
            delta="3 catégories"
        )
    
    with col4:
        st.metric(
            label="🔮 Capacités",
            value="48",
            delta="6 par héros"
        )
    
    # FOOTER - Remerciements et Statut
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(212,175,55,0.1), rgba(244,228,188,0.8));
                border: 2px solid #d4af37; border-radius: 15px; padding: 25px; margin: 30px 0;
                text-align: center;">
        <h4 style="color: #8b4513; margin-top: 0; font-family: 'Cinzel', serif;">
            🏆 SIMULATEUR RPG PROFESSIONNEL COMPLET
        </h4>
        <div style="line-height: 1.6; font-size: 0.95rem; color: #666;">
            <strong>Architecture modulaire • Code Python • Interface jeu de société</strong><br>
            Prêt pour l'équilibrage professionnel du jeu de société Périples<br><br>
            <em style="color: #8b4513;">"Conçu avec expertise, assisté par Claude AI."</em>
        </div>
    </div>
    """, unsafe_allow_html=True)

# === ONGLETS PRINCIPAUX ===
def tab_selection(data):
    """Onglet sélection équipes"""
    st.header("🏰 Sélection des Équipes")
    
    heroes, enemies, loader = data['heroes'], data['enemies'], data['loader']
    nb_heroes = len(st.session_state.selected_heroes)
    nb_enemies = len(st.session_state.selected_enemies)
    
    # Reset avec indicateurs
    if display_progress_indicators_with_reset(nb_heroes, nb_enemies):
        st.session_state.selected_heroes = []
        st.session_state.selected_enemies = []
        st.success("✅ Sélections effacées !")
        st.rerun()
    
    # === HÉROS ===
    st.subheader("🛡️ Héros Disponibles")
    
    # Info Elneha
    selected_elneha = [c for c in st.session_state.selected_heroes if c in get_elneha_forms()]
    if selected_elneha:
        hero_name = next(h.name for h in heroes if h.code == selected_elneha[0])
        st.info(f"🐻 {hero_name} sélectionnée (forme d'Elneha)")
    
    # Grille héros 6 par ligne
    cols = st.columns(6)
    current_builds = st.session_state.get('custom_builds', {})
    
    for i, hero in enumerate(heroes):
        build = get_hero_build_info(hero.code, loader, current_builds)
        is_selected = hero.code in st.session_state.selected_heroes
        
        with cols[i % 6]:
            if display_hero_card(hero, build, is_selected, ENABLE_IMAGES):
                if is_selected:
                    st.session_state.selected_heroes.remove(hero.code)
                else:
                    clean_elneha_forms(hero.code)
                    st.session_state.selected_heroes.append(hero.code)
                st.rerun()
    
    # === ENNEMIS ===
    st.subheader("👹 Ennemis")
    player_count = max(2, nb_heroes) if nb_heroes >= 2 else 2
    
    # Recherche
    col1, col2 = st.columns([1, 3])
    with col1:
        search = st.text_input("Recherche", placeholder="Ex: 34, Dragon...", label_visibility="collapsed")
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
        for i, enemy in enumerate(filtered):
            is_selected = enemy.code in st.session_state.selected_enemies
            
            with cols[i % 5]:
                if display_enemy_card(enemy, is_selected, player_count):
                    if is_selected:
                        st.session_state.selected_enemies.remove(enemy.code)
                    else:
                        st.session_state.selected_enemies.append(enemy.code)
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
            st.session_state['run_simulation'] = True
            st.session_state['simulation_config'] = {
                'hero_codes': st.session_state.selected_heroes,
                'enemy_codes': st.session_state.selected_enemies,
                'player_count': player_count,
                'rules': rules
            }
            st.success("⚡ Combat engagé ! 👉 Allez dans 'Chroniques' 👈")
            st.balloons()
    else:
        st.button("⚔️ FORMATION INCOMPLÈTE", disabled=True, use_container_width=True)

def tab_forge(data):
    """
    Onglet forge équipements + capacités + potions - VERSION ÉTENDUE
    NOUVEAU : Interface potions + boutons compacts
    """
    st.header("⚙️ Forge des Équipements")
    
    heroes, equipment = data['heroes'], data['equipment']
    
    # Sélection héros avec clé unique
    hero_options = {h.code: f"{get_hero_icon(h.name)} {h.name}" for h in heroes}
    selected_code = st.selectbox(
        "Héros:", 
        list(hero_options.keys()), 
        format_func=lambda x: hero_options[x],
        key="forge_hero_selectbox"
    )
    selected_hero = next(h for h in heroes if h.code == selected_code)
    
    # Stats actuelles
    st.subheader("📊 Statistiques")
    display_hero_base_stats(selected_hero)
    
    # Build actuel + BOUTONS COMPACTS
    current_builds = st.session_state.get('custom_builds', {})
    current_build = get_hero_build_info(selected_code, data['loader'], current_builds)
    
    # NOUVEAU - Layout compact pour build + boutons
    col_build, col_buttons = st.columns([3, 1])
    
    with col_build:
        display_current_build_info(current_build)
    
    with col_buttons:
        # Boutons compacts verticaux
        if st.button("🔄 Reset", use_container_width=True, key="forge_reset_compact"):
            if selected_code in st.session_state.custom_builds:
                del st.session_state.custom_builds[selected_code]
                st.rerun()
        
        if current_build['is_custom'] and st.button("🗑️ Suppr.", use_container_width=True, key="forge_delete_compact"):
            del st.session_state.custom_builds[selected_code]
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
    hero_abilities = []
    
    if FORGE_ABILITIES_AVAILABLE:
        # Récupération robuste des capacités
        hero_abilities = get_abilities_for_hero(selected_code, data['loader'])
        
        # Fallback : capacités de test
        if not hero_abilities and f'test_abilities_{selected_code}' in st.session_state:
            hero_abilities = st.session_state[f'test_abilities_{selected_code}']
            st.info("🧪 Utilisation des capacités de test")
        
        if hero_abilities:
            # Capacités actuellement sélectionnées
            current_abilities = []
            if selected_code in st.session_state.get('custom_builds', {}):
                current_abilities = st.session_state.custom_builds[selected_code].get('abilities', [])
            
            # Interface de sélection
            selected_abilities = display_abilities_selection_section(
                selected_code, 
                hero_abilities, 
                current_abilities
            )
        else:
            st.warning(f"🔮 Aucune capacité trouvée pour {selected_hero.name}")
            
            # Bouton avec clé unique
            if st.button("🔧 Charger Capacités de Test", 
                        help="Crée des capacités de test pour ce héros",
                        key=f"forge_test_abilities_{selected_code}"):
                try:
                    from ui.components.forge_abilities_components import create_test_abilities_for_hero
                    test_abilities = create_test_abilities_for_hero(selected_code)
                    if test_abilities:
                        st.session_state[f'test_abilities_{selected_code}'] = test_abilities
                        st.success("✅ Capacités de test créées !")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur création test: {e}")
    else:
        st.error("❌ Système de capacités non disponible - Vérifiez les imports")
    
    # === NOUVEAU - POTIONS ===
    st.subheader("🧪 Potions de Santé")
    
    selected_potions = {'small': 0, 'large': 0}
    
    if FORGE_ABILITIES_AVAILABLE:
        try:
            # Récupération sélection actuelle
            current_potions = {'small': 0, 'large': 0}
            if selected_code in st.session_state.get('custom_builds', {}):
                current_potions = st.session_state.custom_builds[selected_code].get('potions', {'small': 0, 'large': 0})
            
            # Interface de sélection potions
            selected_potions = display_potions_selection_section(selected_code)
            
        except Exception as e:
            st.error(f"❌ Erreur interface potions: {e}")
            st.info("🧪 Interface potions non disponible")
    else:
        st.info("🧪 Interface potions nécessite le système de capacités")
    
    # === NOUVEAU BUILD - TOUJOURS VISIBLE AVEC POTIONS ===
    st.subheader("💾 Nouveau Build")
    
    # Aperçu équipements (si sélectionnés)
    if selected_eq:
        temp_hero = selected_hero.model_copy()
        temp_eq = [eq for eq in equipment if eq.code in selected_eq]
        temp_hero.equip_items(temp_eq, "Custom")
        display_new_stats_preview(temp_hero.get_stats_summary()['total'])
    
    # Aperçu capacités sélectionnées (si sélectionnées)
    if selected_abilities and hero_abilities:
        selected_ability_objects = []
        for ability in hero_abilities:
            ability_number = getattr(ability, 'ability_number', None)
            if ability_number in selected_abilities:
                selected_ability_objects.append(ability)
        
        if selected_ability_objects:
            ability_names = []
            total_spell_cost = 0
            
            for ability in selected_ability_objects:
                ability_name = getattr(ability, 'name', 'Capacité')
                spell_cost = getattr(ability, 'spell_cost', 0)
                ability_names.append(ability_name)
                total_spell_cost += spell_cost
            
            # Affichage de l'aperçu capacités
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(138,43,226,0.15), rgba(147,112,219,0.1));
                        border: 3px solid #8a2be2; border-radius: 12px; padding: 15px; margin: 15px 0;">
                <h4 style="color: #8a2be2; margin-top: 0;">🔮 Capacités Intégrées</h4>
                <div style="font-size: 1.1rem; line-height: 1.5; color: #333;">
                    <strong>📜 Sélectionnées :</strong> {', '.join(ability_names)}<br>
                    <strong>⚡ Coût total :</strong> {total_spell_cost} sorts<br>
                    <strong>🔢 Numéros :</strong> {', '.join(map(str, sorted(selected_abilities)))}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # NOUVEAU - Aperçu potions sélectionnées (si sélectionnées)
    total_potions = selected_potions.get('small', 0) + selected_potions.get('large', 0)
    if total_potions > 0:
        potion_parts = []
        if selected_potions.get('small', 0) > 0:
            potion_parts.append(f"🩸 {selected_potions['small']} Petite{'s' if selected_potions['small'] > 1 else ''}")
        if selected_potions.get('large', 0) > 0:
            potion_parts.append(f"❤️‍🩹 {selected_potions['large']} Grande")
        
        potions_display = ", ".join(potion_parts)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(220,20,60,0.15), rgba(139,0,0,0.1));
                    border: 3px solid #dc143c; border-radius: 12px; padding: 15px; margin: 15px 0;">
            <h4 style="color: #dc143c; margin-top: 0;">🧪 Potions Intégrées</h4>
            <div style="font-size: 1.1rem; line-height: 1.5; color: #333;">
                <strong>🧪 Sélectionnées :</strong> {potions_display}<br>
                <strong>💚 Total :</strong> {total_potions} potion{'s' if total_potions > 1 else ''}<br>
                <strong>⚡ Utilisation :</strong> Automatique par IA si PV < 50%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Message d'aide si rien n'est sélectionné
    if not selected_eq and not selected_abilities and total_potions == 0:
        st.info("💡 **Sélectionnez des équipements, capacités et/ou potions** ci-dessus pour créer un build custom")
    
    # Zone de sauvegarde - TOUJOURS VISIBLE
    col_name, col_save = st.columns([3, 1])
    
    with col_name:
        name = st.text_input("🏷️ Nom du build:", 
                           placeholder="Ex: Tank Ultime, Mage DPS...",
                           key=f"forge_build_name_{selected_code}")
    
    with col_save:
        # Bouton actif seulement si quelque chose est sélectionné
        has_selection = bool(selected_eq or selected_abilities or total_potions > 0)
        button_text = "💾 Sauvegarder" if has_selection else "💾 Rien à sauver"
        
        if st.button(button_text, 
                    type="primary" if has_selection else "secondary", 
                    use_container_width=True,
                    disabled=not has_selection,
                    key=f"forge_save_btn_{selected_code}"):
            
            build_data = {
                'equipment': selected_eq,
                'name': name.strip() or 'Build Custom'
            }
            
            # Ajout capacités avec validation
            if selected_abilities:
                build_data['abilities'] = selected_abilities
                build_data['abilities_custom'] = True
            
            # NOUVEAU - Ajout potions
            if total_potions > 0:
                build_data['potions'] = selected_potions
            
            # Sauvegarde dans session state
            st.session_state.custom_builds[selected_code] = build_data
            
            # Message de succès détaillé
            success_parts = [f"✅ Build '{build_data['name']}' sauvegardé !"]
            if selected_eq:
                success_parts.append(f"⚔️ {len(selected_eq)} équipements")
            if selected_abilities:
                success_parts.append(f"🔮 {len(selected_abilities)} capacités")
            if total_potions > 0:
                success_parts.append(f"🧪 {total_potions} potions")
            
            st.success(" • ".join(success_parts))
            st.balloons()
            time.sleep(0.5)
            st.rerun()
    
    # Récapitulatif du build actuel (si custom existe)
    if current_build['is_custom']:
        st.markdown("---")
        st.markdown("### 🔧 Build Actuel Custom")
        
        # Équipements du build actuel
        if current_build['equipment']:
            eq_names = [eq.name for eq in current_build['equipment']]
            st.info(f"⚔️ **Équipements actuels:** {', '.join(eq_names)}")
        
        # Capacités du build actuel
        abilities_info = current_build.get('abilities_info', {})
        if abilities_info.get('has_custom_abilities', False):
            ability_names = abilities_info.get('selected_names', [])
            total_cost = abilities_info.get('total_spell_cost', 0)
            st.info(f"🔮 **Capacités actuelles:** {', '.join(ability_names)} (Coût: {total_cost} sorts)")
        
        # NOUVEAU - Potions du build actuel
        potions_info = current_build.get('potions_info', {})
        if potions_info.get('has_custom_potions', False):
            st.info(f"🧪 **Potions actuelles:** {potions_info.get('display_text', 'Aucune')}")

def tab_combat(data):
    """Onglet résultats combat"""
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
    st.session_state['run_simulation'] = False

# === MAIN ===
def main():
    """Application principale"""
    init_app()
    apply_fantasy_theme()
    
    # Titre
    st.markdown(get_app_title_style(), unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; font-size: 0.8rem; color: #666; margin-bottom: 20px;">
        🎲 <strong style="color: #8b4513;">Périples</strong> © <strong style="color: #228b22;">Bastien Liauty</strong> | 
        💻 Dev Python : <strong style="color: #4682b4;">Christophe Bidouj</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Données
    try:
        data = load_data()
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

# Exécution
if __name__ == "__main__":
    main()