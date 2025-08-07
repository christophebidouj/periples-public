"""
Composants héros pour le Simulateur Périples
Cartes héros, récapitulatif d'équipe, statistiques
NOUVEAU : Sélecteurs de difficulté (Facile/Normal/Difficile)
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

def preload_hero_builds_for_all_difficulties(heroes_list: List, equipment_list: List, loader) -> Dict:
    """
    Pré-calcule les 3 builds (Facile/Normal/Difficile) pour tous les héros
    
    Returns:
        Dict: Structure {hero_code: [build_facile, build_normal, build_difficile]}
    """
    from hero_builds_data import get_hero_stats_by_difficulty, get_build_name_by_difficulty
    
    preloaded_builds = {}
    difficulty_levels = ["🟢 Facile", "🔵 Normal", "🔴 Difficile"]
    
    for hero in heroes_list:
        hero_builds = []
        
        for difficulty in difficulty_levels:
            stats = get_hero_stats_by_difficulty(hero.code, difficulty)
            build_name = get_build_name_by_difficulty(difficulty)
            
            build_info = {
                'hero_equipped': hero,
                'equipment': [],
                'build_name': build_name,
                'is_custom': False,
                'stats': {'total': stats},
                'difficulty_level': difficulty.replace("🟢 ", "").replace("🔵 ", "").replace("🔴 ", "")
            }
            hero_builds.append(build_info)
        
        preloaded_builds[hero.code] = hero_builds
    
    return preloaded_builds

def display_hero_card(hero: Character, is_selected: bool, preloaded_builds: Dict, custom_builds_dict: Dict = None, enable_images: bool = True, show_button: bool = True):
    """
    Affiche une carte héros avec style gaming et sélecteur de difficulté
    Utilise les builds pré-calculés pour une réactivité immédiate avec callback
    
    Args:
        hero: Objet Character
        is_selected: État de sélection
        preloaded_builds: Builds pré-calculés {hero_code: [facile, normal, difficile]}
        custom_builds_dict: Dictionnaire des builds custom
        enable_images: Activer les images de background
        show_button: Afficher le bouton ou pas (pour gestion externe)
    """
    current_custom_builds = custom_builds_dict or st.session_state.get('custom_builds', {})
    
    # Callback pour mise à jour immédiate de la difficulté
    def on_difficulty_change():
        """Callback exécuté immédiatement lors du changement de difficulté"""
        new_difficulty = st.session_state[f"difficulty_{hero.code}"]
        if 'hero_difficulties' not in st.session_state:
            st.session_state.hero_difficulties = {}
        st.session_state.hero_difficulties[hero.code] = new_difficulty
    
    # Vérifier si le héros a un build custom
    if hero.code in current_custom_builds:
        # BUILD CUSTOM - Utiliser la logique existante
        custom = current_custom_builds[hero.code]
        build_info = {
            'build_name': custom.get('name', 'Build Custom'),
            'is_custom': True,
            'stats': {'total': {'precision': 6, 'damage': 3, 'health': 8, 'parade': 1, 'spells': 4}},  # Placeholder
            'difficulty_level': 'Custom'
        }
        
        # Pas de selectbox pour les builds custom
        selected_difficulty = None
    else:
        # BUILDS FIXES - Selectbox avec callback
        difficulty_levels = ["🟢 Facile", "🔵 Normal", "🔴 Difficile"]
        current_difficulty = st.session_state.get('hero_difficulties', {}).get(hero.code, "🔵 Normal")
        
        # Selectbox avec callback immédiat
        selectbox_key = f"difficulty_{hero.code}"
        selected_difficulty = st.selectbox(
            "Niveau :",
            options=difficulty_levels,
            index=difficulty_levels.index(current_difficulty),
            key=selectbox_key,
            on_change=on_difficulty_change,
            label_visibility="collapsed"
        )
        
        # Utiliser la valeur mise à jour par le callback
        updated_difficulty = st.session_state.get('hero_difficulties', {}).get(hero.code, "🔵 Normal")
        difficulty_index = difficulty_levels.index(updated_difficulty)
        
        # Récupération du build pré-calculé avec la nouvelle difficulté
        build_info = preloaded_builds[hero.code][difficulty_index]
    
    # Données pour l'affichage
    stats = build_info['stats']['total']
    hero_icon = get_hero_icon(hero.name)
    
    # Détermination des couleurs selon l'état
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
        
        # Bouton sélection héros
        if show_button:
            button_key = f"hero_btn_{hero.code}_{is_selected}"
            return st.button(button_text, key=button_key, type=button_type, use_container_width=True)
        
        return False

def display_team_recap(heroes_details, enemies_details, player_count):
    """Affiche le récapitulatif des équipes avec niveaux de difficulté"""
    st.markdown("## 🛡️ Forces en Présence")

    col1, col2 = st.columns(2)

    # === HÉROS ===
    with col1:
        st.markdown("### 🧙 ÉQUIPE HÉROS")

        for h in heroes_details:
            # Récupération du niveau de difficulté
            difficulty_level = h.get('difficulty_level', 'Normal')
            difficulty_color = {
                'Facile': '🟢',
                'Normal': '🔵', 
                'Difficile': '🔴'
            }.get(difficulty_level, '🔵')
            
            # Affichage avec niveau
            header_text = f"✅ {h['name']} {difficulty_color} — ⚔️ {h['damage']} | ❤️ {h['health']} | 🛡️ {h['parade']} | ✨ {h['spells']}"
            
            with st.expander(header_text, expanded=True):
                st.write(f"**Niveau :** {difficulty_color} {difficulty_level}")
                st.write(f"**Build :** {h['build_name']}")
                if h.get('is_custom'):
                    st.write("*Build personnalisé*")

    # === MONSTRES ===
    with col2:
        st.markdown("### 👹 ÉQUIPE MONSTRES")

        for e in enemies_details:
            header_text = f"👾 {e['name']} — ❤️ {e['health']} | ⚔️ {e['damage']} | 🛡️ {e['defense']}"
            
            with st.expander(header_text, expanded=True):
                st.write(f"**Numéro :** #{e['number']}")
                if e.get('is_magical'):
                    st.write("🔮 *Créature magique*")

    # Info joueurs
    st.markdown(f"<p style='color:#888;'>👥 Nombre de joueurs : <strong>{player_count}</strong></p>", unsafe_allow_html=True)

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