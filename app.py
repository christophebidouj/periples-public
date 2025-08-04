#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Périples Balance Workshop
🎲 Jeu : Périples © Bastien LIAUTY
💻 Code : Christophe Bidouj (assistance Claude AI)
"""

import streamlit as st
import time
import os
from typing import List, Dict
from models.character import Character, Enemy
from models.combat_engine import CombatEngine
from models.rules_engine import GameRules
from utils.data_loader import DataLoader


# Import UI
from ui.styling import apply_fantasy_theme, get_combat_button_styles, get_waiting_combat_style, get_app_title_style
from ui.components import *

# Configuration
ENABLE_IMAGES = True

# === UTILITAIRES ===
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
    
    # Variables de session
    defaults = {'selected_heroes': [], 'selected_enemies': [], 'custom_builds': {}}
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

# CORRECTION BUG : Cache conditionnel avec hash des builds custom
def get_hero_build_info(hero_code: str, _loader, custom_builds_dict: Dict = None) -> Dict:
    """Calcule build d'un héros (SANS cache pour builds custom)"""
    hero = next(h for h in _loader.load_heroes() if h.code == hero_code)
    
    # Utilise custom_builds_dict passé en paramètre au lieu de session_state directement
    current_custom_builds = custom_builds_dict or st.session_state.get('custom_builds', {})
    
    # Build custom ou standard
    if hero_code in current_custom_builds:
        custom = current_custom_builds[hero_code]
        equipment = [eq for eq in _loader.load_equipment() if eq.code in custom.get('equipment', [])]
        build_name = custom.get('name', 'Build Custom')
        is_custom = True
    else:
        equipment = _loader.get_hero_loadout(hero_code)
        build_name = "Build Standard"
        is_custom = False
    
    # Héros équipé
    hero_equipped = hero.model_copy()
    hero_equipped.equip_items(equipment, build_name)
    
    return {
        'hero_equipped': hero_equipped,
        'equipment': equipment,
        'build_name': build_name,
        'is_custom': is_custom,
        'stats': hero_equipped.get_stats_summary()
    }

def prepare_heroes_for_recap(hero_codes: List[str], heroes: List[Character], loader) -> List[Dict]:
    """Prépare données héros pour récapitulatif"""
    result = []
    current_builds = st.session_state.get('custom_builds', {})
    
    for code in hero_codes:
        hero = next(h for h in heroes if h.code == code)
        build = get_hero_build_info(code, loader, current_builds)
        stats = build['stats']['total']
        
        result.append({
            'name': hero.name,
            'icon': get_hero_icon(hero.name),
            'build': build['build_name'],
            'is_custom': build['is_custom'],
            'precision': stats['precision'],
            'damage': stats['damage'],
            'health': stats['health'],
            'parade': stats['parade'],
            'spells': stats['spells']
        })
    return result

def prepare_enemies_for_recap(enemy_codes: List[str], enemies: List[Enemy], player_count: int) -> List[Dict]:
    """Prépare données ennemis pour récapitulatif"""
    result = []
    for code in enemy_codes:
        enemy = next(e for e in enemies if e.code == code)
        stats = enemy.get_stats_for_players(player_count)
        
        result.append({
            'name': enemy.name,
            'number': enemy.code.split('-')[-1],
            'is_magical': enemy.is_magical,
            'health': stats['health'],
            'damage': stats['damage'],
            'defense': enemy.defense
        })
    return result

# === ONGLET À PROPOS ===
def display_about():
    """Affiche section À Propos avec design gaming élégant"""
    
    # En-tête principal élégant
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
        <div style="width: 80px; height: 3px; background: #d4af37; margin: 10px auto; border-radius: 2px;"></div>
    </div>
    """, unsafe_allow_html=True)

    # Conteneur jeu de société
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(34,139,34,0.15), rgba(0,100,0,0.08));
                    border: 3px solid #228b22; border-radius: 20px; padding: 25px; margin: 15px 0;
                    box-shadow: 0 6px 20px rgba(34,139,34,0.2);">
            <h2 style="color: #006400; margin-top: 0; font-family: 'Cinzel', serif; 
                       border-bottom: 2px solid #228b22; padding-bottom: 10px;">
                🎲 JEU DE SOCIÉTÉ
            </h2>
            <div style="font-size: 1.1rem; line-height: 1.6;">
                <p style="margin: 15px 0;"><strong style="color: #8b4513;">Périples</strong> © <strong style="color: #228b22;">Bastien LIAUTY</strong></p>
                <p style="margin: 10px 0;"><span style="color: #666;">📖 Version :</span> <strong>V3.0</strong> (2025)</p>
                <p style="margin: 10px 0;"><span style="color: #666;">🏰 Genre :</span> RPG coopératif médiéval-fantastique</p>
                <p style="margin: 10px 0;"><span style="color: #666;">👥 Joueurs :</span> <strong>1 à 4 joueurs</strong></p>
                <p style="margin: 10px 0;"><span style="color: #666;">⚡ Statut :</span> <strong style="color: #ff6b35;">Prototype en développement</strong></p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Objectifs
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(139,0,0,0.15), rgba(220,20,60,0.08));
                    border: 3px solid #8b0000; border-radius: 20px; padding: 25px; margin: 15px 0;
                    box-shadow: 0 6px 20px rgba(139,0,0,0.2);">
            <h2 style="color: #8b0000; margin-top: 0; font-family: 'Cinzel', serif;
                       border-bottom: 2px solid #8b0000; padding-bottom: 10px;">
                🎯 OBJECTIFS STRATÉGIQUES
            </h2>
            <div style="font-size: 1.05rem; line-height: 1.7;">
                <div style="margin: 12px 0; padding: 8px 15px; background: rgba(139,0,0,0.1); border-radius: 10px;">
                    <strong>⚖️</strong> Équilibrage des statistiques des ennemis
                </div>
                <div style="margin: 12px 0; padding: 8px 15px; background: rgba(139,0,0,0.1); border-radius: 10px;">
                    <strong>📋</strong> Validation des règles de combat
                </div>
                <div style="margin: 12px 0; padding: 8px 15px; background: rgba(139,0,0,0.1); border-radius: 10px;">
                    <strong>⚔️</strong> Optimisation des équipements
                </div>
                <div style="margin: 12px 0; padding: 8px 15px; background: rgba(139,0,0,0.1); border-radius: 10px;">
                    <strong>🧠</strong> Analyse tactique approfondie
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Balance Workshop - Style technologique
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(70,130,180,0.15), rgba(100,149,237,0.08));
                    border: 3px solid #4682b4; border-radius: 20px; padding: 25px; margin: 15px 0;
                    box-shadow: 0 6px 20px rgba(70,130,180,0.2);">
            <h2 style="color: #2e4b6b; margin-top: 0; font-family: 'Cinzel', serif;
                       border-bottom: 2px solid #4682b4; padding-bottom: 10px;">
                💻 BALANCE WORKSHOP
            </h2>
            <div style="font-size: 1.1rem; line-height: 1.6;">
                <p style="margin: 15px 0;"><span style="color: #666; display: inline-block; width: 140px;">👨‍💻 Dev Python :</span> <strong style="color: #4682b4;">Christophe Bidouj</strong></p>
                <p style="margin: 10px 0;"><span style="color: #666; display: inline-block; width: 140px;">🧠 Assistance IA :</span> <strong>Claude AI</strong> (Anthropic)</p>
                <p style="margin: 10px 0;"><span style="color: #666; display: inline-block; width: 140px;">🛠️ Technologies :</span> <strong>Python + Streamlit + Pydantic</strong></p>
                <p style="margin: 10px 0;"><span style="color: #666; display: inline-block; width: 140px;">📦 Version :</span> <strong style="color: #4682b4;">V4+ avec À Propos</strong></p>
                <p style="margin: 10px 0;"><span style="color: #666; display: inline-block; width: 140px;">🚀 Statut :</span> <strong style="color: #32cd32;">En développement actif</strong></p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Séparateur
    st.markdown("""
    <div style="text-align: center; margin: 40px 0 30px 0;">
        <div style="display: inline-block; width: 60px; height: 4px; background: linear-gradient(90deg, #8b4513, #d4af37, #8b4513); border-radius: 2px;"></div>
        <span style="margin: 0 20px; font-size: 1.5rem; color: #d4af37;">⚔️</span>
        <div style="display: inline-block; width: 60px; height: 4px; background: linear-gradient(90deg, #8b4513, #d4af37, #8b4513); border-radius: 2px;"></div>
    </div>
    """, unsafe_allow_html=True)

    # Fonctionnalités - 3 cards avec hauteur fixe
    st.markdown("""
    <h2 style="text-align: center; color: #8b4513; font-family: 'Cinzel', serif; margin-bottom: 25px;">
        ⚡ ARSENAL DES FONCTIONNALITÉS ⚡
    </h2>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(34,139,34,0.12), rgba(0,100,0,0.06));
                    border: 2px solid #228b22; border-radius: 15px; padding: 20px; 
                    text-align: center; min-height: 180px; display: flex; 
                    flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-size: 2.5rem; margin-bottom: 10px;">🛡️</div>
                <h3 style="color: #006400; margin: 10px 0; font-family: 'Cinzel', serif; font-size: 1.3rem;">SÉLECTION</h3>
            </div>
            <div style="font-size: 0.95rem; line-height: 1.5; color: #333;">
                • 12 héros + formes Elneha<br>
                • 72 ennemis évolutifs<br>
                • Interface par cartes<br>
                • Récap "Formation de Guerre"
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(139,0,0,0.12), rgba(220,20,60,0.06));
                    border: 2px solid #8b0000; border-radius: 15px; padding: 20px; 
                    text-align: center; min-height: 180px; display: flex; 
                    flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-size: 2.5rem; margin-bottom: 10px;">⚔️</div>
                <h3 style="color: #8b0000; margin: 10px 0; font-family: 'Cinzel', serif; font-size: 1.3rem;">COMBAT</h3>
            </div>
            <div style="font-size: 0.95rem; line-height: 1.5; color: #333;">
                • Moteur règles V3.0<br>
                • Journal action par action<br>
                • Métriques d'équilibrage<br>
                • Validation stratégies
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(70,130,180,0.12), rgba(100,149,237,0.06));
                    border: 2px solid #4682b4; border-radius: 15px; padding: 20px; 
                    text-align: center; min-height: 180px; display: flex; 
                    flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-size: 2.5rem; margin-bottom: 10px;">🛠️</div>
                <h3 style="color: #2e4b6b; margin: 10px 0; font-family: 'Cinzel', serif; font-size: 1.3rem;">FORGE</h3>
            </div>
            <div style="font-size: 0.95rem; line-height: 1.5; color: #333;">
                • 52 équipements catégorisés<br>
                • Builds hybrides custom<br>
                • Stats en temps réel<br>
                • Sauvegarde configurations
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Section progression avec espacement
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <h2 style="text-align: center; color: #8b4513; font-family: 'Cinzel', serif; 
               margin: 40px 0 25px 0;">
        🚀 PROGRESSION DU DÉVELOPPEMENT 🚀
    </h2>
    """, unsafe_allow_html=True)

    progress_data = [
        ("Interface Utilisateur", 100, "#228b22", "🎨"),
        ("Moteur de Combat", 90, "#ff8c00", "⚔️"),
        ("Système d'Équipements", 100, "#4682b4", "🛠️"),
        ("Système de Capacités", 60, "#8a2be2", "✨")
    ]

    for name, value, color, icon in progress_data:
        st.markdown(f"""
        <div style="margin: 15px 0; padding: 15px; 
                    background: rgba(139,69,19,0.06); 
                    border-radius: 12px; 
                    border: 1px solid rgba(139,69,19,0.2);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: bold; font-size: 1.1rem; color: #8b4513;">
                    {icon} {name}
                </span>
                <span style="color: {color}; font-weight: bold; font-size: 1.2rem;">{value}%</span>
            </div>
            <div style="background: #f0f0f0; border-radius: 10px; height: 8px; overflow: hidden;
                        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(90deg, {color}, {color}dd); 
                           height: 8px; border-radius: 10px; width: {value}%; 
                           transition: width 0.3s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Footer style parchemin royal avec espacement
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(139,69,19,0.1), rgba(212,175,55,0.1));
                border: 3px solid #d4af37; border-radius: 20px; padding: 25px; 
                text-align: center; margin: 30px 0 20px 0;
                box-shadow: 0 8px 32px rgba(139,69,19,0.2);">
        <div style="border-bottom: 2px solid #d4af37; padding-bottom: 15px; margin-bottom: 15px;">
            <h3 style="color: #8b4513; margin: 0; font-family: 'Cinzel', serif;">
                📜 DÉCLARATION ROYALE 📜
            </h3>
        </div>
        <p style="margin: 10px 0; color: #666; font-size: 1rem; line-height: 1.6;">
            <strong style="color: #8b4513;">Périples</strong> © <strong style="color: #228b22;">Bastien LIAUTY</strong> - Tous droits réservés<br>
            Balance Workshop forgé par <strong style="color: #4682b4;">Christophe Bidouj</strong> 
            avec l'assistance de <strong style="color: #8a2be2;">Claude AI</strong><br>
        </p>
        <div style="margin: 15px 0; padding: 12px; background: rgba(139,69,19,0.1); 
                    border-radius: 10px; border-left: 4px solid #d4af37;">
            <em style="color: #8b4513; font-size: 0.9rem;">
                Usage autorisé exclusivement pour le développement et les tests d'équilibrage
            </em>
        </div>
        <p style="margin: 10px 0 0 0; color: #999; font-size: 0.85rem;">
            <strong>Version V4+ • Interface Optimisée • Août 2025</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

# === ONGLETS PRINCIPAUX ===
def tab_selection(data):
    """Onglet sélection équipes"""
    st.header("🏰 Sélection des Équipes")

    heroes, enemies, loader = data['heroes'], data['enemies'], data['loader']
    nb_heroes = len(st.session_state.selected_heroes)
    nb_enemies = len(st.session_state.selected_enemies)

    # Indicateurs avec reset
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
    search = st.text_input("🔍 Recherche:", placeholder="Ex: 34, Dragon...")
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
        hero_details = prepare_heroes_for_recap(st.session_state.selected_heroes, heroes, loader)
        enemy_details = prepare_enemies_for_recap(st.session_state.selected_enemies, enemies, player_count)
        display_team_recap(hero_details, enemy_details, player_count)

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
    """Onglet forge équipements"""
    st.header("⚙️ Forge des Équipements")

    heroes, equipment = data['heroes'], data['equipment']

    # Sélection héros
    hero_options = {h.code: f"{get_hero_icon(h.name)} {h.name}" for h in heroes}
    selected_code = st.selectbox("Héros:", list(hero_options.keys()), format_func=lambda x: hero_options[x])
    selected_hero = next(h for h in heroes if h.code == selected_code)

    # Stats actuelles
    st.subheader("📊 Statistiques")
    display_hero_base_stats(selected_hero)

    # CORRECTION BUG : Passer les builds custom explicitement
    current_builds = st.session_state.get('custom_builds', {})
    current_build = get_hero_build_info(selected_code, data['loader'], current_builds)
    display_current_build_info(current_build)

    # Gestion builds
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset", use_container_width=True):
            if selected_code in st.session_state.custom_builds:
                del st.session_state.custom_builds[selected_code]
                st.rerun()
    with col2:
        if current_build['is_custom'] and st.button("🗑️ Supprimer", use_container_width=True):
            del st.session_state.custom_builds[selected_code]
            st.rerun()

    # Sélection équipements
    st.subheader("⚔️ Équipements")
    weapons, armor, accessories = get_equipment_categories(equipment)

    selected_eq = []
    selected_eq.extend(display_equipment_selection_native(weapons, "Armes", "⚔️", "w"))
    selected_eq.extend(display_equipment_selection_native(armor, "Armures", "🛡️", "a"))
    selected_eq.extend(display_equipment_selection_native(accessories, "Accessoires", "💍", "acc"))

    # Nouveau build
    if selected_eq:
        st.subheader("💾 Nouveau Build")

        # Calcul stats avec builds custom temporaires
        temp_hero = selected_hero.model_copy()
        temp_eq = [eq for eq in equipment if eq.code in selected_eq]
        temp_hero.equip_items(temp_eq, "Custom")
        display_new_stats_preview(temp_hero.get_stats_summary()['total'])

        # Sauvegarde
        name = st.text_input("🏷️ Nom:", placeholder="Ex: Tank Ultime...")
        if st.button("💾 Sauvegarder", type="primary", use_container_width=True):
            # CORRECTION BUG : Sauvegarde + invalidation cache + rerun forcé
            st.session_state.custom_builds[selected_code] = {
                'equipment': selected_eq,
                'name': name.strip() or 'Build Custom'
            }
            st.success("✅ Build sauvegardé !")
            st.balloons()
            # FORCER le rechargement immédiat
            time.sleep(0.5)  # Petite pause pour voir le message
            st.rerun()

def tab_combat(data):
    """Onglet résultats combat"""
    st.header("📜 Chroniques du Combat")

    if not st.session_state.get('run_simulation', False):
        st.markdown(get_waiting_combat_style(), unsafe_allow_html=True)
        return

    # Préparation combat
    config = st.session_state['simulation_config']
    heroes, enemies, loader = data['heroes'], data['enemies'], data['loader']

    # Équipes finales avec builds custom
    selected_heroes = []
    current_builds = st.session_state.get('custom_builds', {})
    
    for code in config['hero_codes']:
        hero = next(h for h in heroes if h.code == code)
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

    # Titre et crédits
    st.markdown(get_app_title_style(), unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; font-size: 0.8rem; color: #666; margin-bottom: 20px;">
        🎲 <strong style="color: #8b4513;">Périples</strong> © <strong style="color: #228b22;">Bastien LIAUTY</strong> | 💻 Dev Python : <strong style="color: #4682b4;">Christophe Bidouj</strong>
    </div>
    """, unsafe_allow_html=True)

    # Données
    try:
        data = load_data()
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
        st.stop()

    # Onglets principaux
    tab1, tab2, tab3, tab4 = st.tabs(["🏰 Sélection", "⚙️ Forge", "📜 Chroniques", "ℹ️ À Propos"])

    with tab1: tab_selection(data)
    with tab2: tab_forge(data)
    with tab3: tab_combat(data)
    with tab4: display_about()

# Exécution
if __name__ == "__main__":
    main()