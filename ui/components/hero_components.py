"""
Composants héros pour le Simulateur Périples
Cartes héros, récapitulatif d'équipe, statistiques
AJOUT : Gestion des transformations d'Elneha (état désactivé)
"""

import streamlit as st
from typing import List, Dict, Any
from models.character import Character

# Import des styles depuis le module styling
from ui.styling import (
    get_hero_card_style, 
    get_team_recap_styles,
    get_forge_styles,
    Colors
)

from ui.components.ui_elements import get_hero_icon, load_hero_image_base64, get_hero_image_path

def display_hero_card(hero: Character, build_info: Dict, is_selected: bool, enable_images: bool = True, show_button: bool = True):
    """
    Affiche une carte héros avec style gaming
    
    Args:
        hero: Objet Character
        build_info: Dictionnaire avec stats et équipements 
        is_selected: État de sélection
        enable_images: Activer les images de background
        show_button: NOUVEAU - Afficher le bouton ou pas (pour gestion externe)
    """
    stats = build_info['stats']['total']
    hero_icon = get_hero_icon(hero.name)
    
    # Détermination des couleurs selon l'état (SIMPLE)
    if is_selected:
        border_color = Colors.SELECTED_BORDER
        button_text, button_type = "✅ Sélectionné", "secondary"
    else:
        border_color = Colors.AVAILABLE_BORDER
        button_text, button_type = "➕ Ajouter", "primary"
    
    # Gestion du background image
    background_style = ""
    if enable_images:
        image_path = get_hero_image_path(hero.name)
        if image_path:
            img_base64 = load_hero_image_base64(image_path)
            if img_base64:
                background_style = f"background-image: url('data:image/png;base64,{img_base64}');"
    
    if not background_style:
        background_style = f"background: linear-gradient(135deg, {border_color}33, {border_color}11);"
    
    # Construction des informations bonus
    bonus_parts = []
    if stats["parade"] > 0:
        bonus_parts.append(f"🛡️{stats['parade']}")
    if stats["spells"] > 0:
        bonus_parts.append(f"✨{stats['spells']}")
    bonus_text = f" • {' • '.join(bonus_parts)}" if bonus_parts else ""
    
    # Contenu des stats
    stats_content = f"""
    <div style="font-family: monospace; font-size: 1rem; margin-bottom: 5px; font-weight: bold; color: #f0f0f0;">
        🎯{stats["precision"]} • ⚔️{stats["damage"]} • ❤️{stats["health"]}{bonus_text}
    </div>"""
    
    # Contenu du build
    build_name_display = build_info["build_name"][:25]
    if len(build_info["build_name"]) > 25:
        build_name_display += "..."
        
    build_content = f"""
    <div style="font-size: 0.9rem; font-style: italic; color: #e0e0e0;">
        {build_name_display}
    </div>"""
    
    # Génération du HTML avec styles
    card_html = get_hero_card_style(hero.name, border_color, background_style)
    card_html = card_html.replace("{stats_content}", stats_content)
    card_html = card_html.replace("{build_content}", build_content)
    
    # Affichage dans conteneur Streamlit
    with st.container():
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Bouton SEULEMENT si demandé
        if show_button:
            button_key = f"hero_btn_{hero.code}_{is_selected}"
            return st.button(button_text, key=button_key, type=button_type, use_container_width=True)
        
        return False  # Pas de bouton = pas de clic

def display_team_recap(selected_hero_details: List[Dict], selected_enemy_details: List[Dict], player_count: int):
    """
    Affiche le récapitulatif "Formation de Guerre"
    Fonctionnalité préservée selon guidelines du projet
    
    Args:
        selected_hero_details: Liste des détails des héros sélectionnés
        selected_enemy_details: Liste des détails des ennemis sélectionnés
        player_count: Nombre de joueurs pour le contexte
    """
    # Styles pour le récapitulatif
    recap_styles = get_team_recap_styles()
    
    # En-tête principal de formation
    st.markdown("---")
    st.markdown(recap_styles['formation_header'], unsafe_allow_html=True)
    
    # Organisation en deux colonnes
    col1, col2 = st.columns([1, 1])
    
    # === COLONNE HÉROS ===
    with col1:
        st.markdown(recap_styles['heroes_team_header'], unsafe_allow_html=True)
        
        for hero in selected_hero_details:
            # Badge du type de build
            build_badge = "🔧 Custom" if hero['is_custom'] else "📋 Standard"
            
            # Construction des bonus additionnels
            bonus_info = []
            if hero['parade'] > 0:
                bonus_info.append(f"🛡️{hero['parade']}")
            if hero['spells'] > 0:
                bonus_info.append(f"✨{hero['spells']}")
            bonus_text = f" • {' • '.join(bonus_info)}" if bonus_info else ""
            
            # Statistiques complètes
            stats = f"🎯{hero['precision']} ⚔️{hero['damage']} ❤️{hero['health']}{bonus_text}"
            
            # Génération de la carte héros
            hero_card_html = recap_styles['hero_card'].format(
                icon=hero['icon'],
                name=hero['name'],
                build_badge=build_badge,
                stats=stats
            )
            st.markdown(hero_card_html, unsafe_allow_html=True)
    
    # === COLONNE ENNEMIS ===
    with col2:
        st.markdown(recap_styles['enemies_team_header'], unsafe_allow_html=True)
        
        for enemy in selected_enemy_details:
            # Badge type de dégâts
            magic_badge = "✨ Magique" if enemy['is_magical'] else "⚔️ Physique"
            
            # Statistiques ennemis
            stats = f"❤️{enemy['health']} ⚔️{enemy['damage']} 🛡️{enemy['defense']}"
            
            # Troncature du nom si nécessaire
            name_truncated = enemy['name'][:18]
            
            # Génération de la carte ennemi
            enemy_card_html = recap_styles['enemy_card'].format(
                number=enemy['number'],
                name=name_truncated,
                magic_badge=magic_badge,
                stats=stats
            )
            st.markdown(enemy_card_html, unsafe_allow_html=True)
    
    # === STATISTIQUES DE BATAILLE ===
    # Calculs des métriques globales
    total_hero_health = sum(h['health'] for h in selected_hero_details)
    total_enemy_health = sum(e['health'] for e in selected_enemy_details)
    avg_hero_damage = sum(h['damage'] for h in selected_hero_details) / len(selected_hero_details)
    avg_enemy_damage = sum(e['damage'] for e in selected_enemy_details) / len(selected_enemy_details)
    
    # Affichage du pronostic
    battle_stats_html = recap_styles['battle_stats'].format(
        hero_health=total_hero_health,
        hero_dps=avg_hero_damage,
        enemy_health=total_enemy_health,
        enemy_dps=avg_enemy_damage
    )
    st.markdown(battle_stats_html, unsafe_allow_html=True)

def display_hero_base_stats(hero: Character):
    """
    Affiche les statistiques de base d'un héros pour la forge
    
    Args:
        hero: Objet Character
    """
    forge_styles = get_forge_styles()
    
    hero_stats_html = forge_styles['hero_base_stats'].format(
        icon=get_hero_icon(hero.name),
        name=hero.name,
        stats=f"🎯 Précision: {hero.precision} • ⚔️ Dégâts: {hero.damage} • ❤️ PV: {hero.health}"
    )
    st.markdown(hero_stats_html, unsafe_allow_html=True)

def display_current_build_info(build_info: Dict):
    """
    Affiche les informations du build actuellement équipé
    
    Args:
        build_info: Dictionnaire avec les infos du build
    """
    forge_styles = get_forge_styles()
    
    build_icon = "🔧" if build_info['is_custom'] else "📋"
    current_build_html = forge_styles['current_build'].format(
        icon=build_icon,
        name=build_info['build_name']
    )
    st.markdown(current_build_html, unsafe_allow_html=True)

def display_new_stats_preview(temp_stats: Dict[str, int]):
    """
    Affiche l'aperçu des nouvelles statistiques avec équipements
    
    Args:
        temp_stats: Dictionnaire des stats temporaires calculées
    """
    forge_styles = get_forge_styles()
    
    # Construction de l'affichage des stats
    parade_text = f" • 🛡️ Parade: {temp_stats['parade']}" if temp_stats['parade'] > 0 else ""
    spells_text = f" • ✨ Sorts: {temp_stats['spells']}" if temp_stats['spells'] > 0 else ""
    
    stats_display = (f"🎯 Précision: {temp_stats['precision']} • "
                     f"⚔️ Dégâts: {temp_stats['damage']} • "
                     f"❤️ PV: {temp_stats['health']}{parade_text}{spells_text}")
    
    new_stats_html = forge_styles['new_stats_preview'].format(stats=stats_display)
    st.markdown(new_stats_html, unsafe_allow_html=True)