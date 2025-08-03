"""
Module des composants graphiques pour le Simulateur Périples
Version compatible Streamlit 1.47.1 - Composants natifs uniquement
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from models.character import Character, Enemy

# Import des styles depuis le module styling
from ui.styling import (
    get_hero_card_style, 
    get_enemy_card_style,
    get_team_recap_styles,
    get_combat_result_styles,
    get_forge_styles,
    style_combat_log_entry,
    Colors
)

def get_hero_icon(name: str) -> str:
    """Retourne l'icône emoji pour un héros donné"""
    icons = {"Elneha": "🐻", "Liarie": "🔮", "Atucan": "🛡️", "Kraor": "⚔️",
             "Thordius": "🪓", "Stèphe": "🎭", "Lame": "🗡️", "Raishi": "🏹"}
    return icons.get(name, "⚔️")

def get_equipment_icon(equipment_type: str, equipment_name: str) -> str:
    """Retourne l'icône appropriée pour un équipement"""
    # Icônes par type
    type_icons = {
        'arme': '⚔️',
        'armure': '🛡️', 
        'accessoire': '💍'
    }
    
    # Icônes spécifiques par nom (plus précises)
    specific_icons = {
        # Armes
        'épée': '⚔️', 'hache': '🪓', 'arc': '🏹', 'dague': '🗡️',
        'marteau': '🔨', 'lance': '🔱', 'bâton': '🪄', 'arbalète': '🏹',
        'espadon': '⚔️', 'glaive': '⚔️', 'cimeterre': '🗡️', 'rapière': '🗡️',
        'massue': '🔨', 'fléau': '🔨', 'poings': '👊', 'griffes': '🦅',
        
        # Armures  
        'armure': '🛡️', 'bouclier': '🛡️', 'casque': '⛑️', 'vêtement': '👕',
        'cotte': '🦺', 'plastron': '🦺', 'plates': '🛡️', 'cuir': '🦺',
        'mailles': '🦺', 'rondache': '🛡️', 'écu': '🛡️',
        
        # Accessoires
        'anneau': '💍', 'bague': '💍', 'collier': '📿', 'ceinture': '🔗',
        'gants': '🧤', 'bottes': '🥾', 'cape': '🦸', 'pierre': '💎',
        'potion': '🧪', 'parchemin': '📜', 'couronne': '👑', 'amulette': '🔮',
        'talisman': '🧿', 'phylactère': '📜', 'relique': '✨', 'cristal': '💎'
    }
    
    # Recherche dans le nom d'équipement
    name_lower = equipment_name.lower()
    for keyword, icon in specific_icons.items():
        if keyword in name_lower:
            return icon
    
    # Fallback sur le type
    return type_icons.get(equipment_type.lower(), '💍')

def load_hero_image_base64(image_path: str) -> str:
    """Charge une image héros en base64 pour affichage"""
    import os
    import base64
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def get_hero_image_path(hero_name: str) -> str:
    """Retourne le chemin vers l'image d'un héros"""
    import os
    hero_files = {
        "Atucan": "Atucan_-_Paladin.png", 
        "Elneha": "Elneha_-_Druidesse.png",
        "Kraor": "Kraor_-_Rodeur.png", 
        "Lame": "Lame_-_Roublarde.png",
        "Liarie": "Liarie_-_Mage.png", 
        "Raishi": "Raishi_-_Pugiliste.png",
        "Stèphe": "Stephe_-_Barde.png",  
        "Thordius": "Thordius_-_Barbare.png",
        "Loup": "Loup.png",
        "Ours": "Ours.png", 
        "Loup S": "Loup_S.png",
        "Ours S": "Ours_S.png"
    }
    filename = hero_files.get(hero_name)
    if filename:
        path = f"data/images/{filename}"
        return path if os.path.exists(path) else None
    return None

def display_hero_card(hero: Character, build_info: Dict, is_selected: bool, enable_images: bool = True):
    """
    Affiche une carte héros avec style gaming
    
    Args:
        hero: Objet Character
        build_info: Dictionnaire avec stats et équipements 
        is_selected: État de sélection
        enable_images: Activer les images de background
    """
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
        
        # Bouton d'action (callback géré par app.py)
        button_key = f"hero_btn_{hero.code}_{is_selected}"
        return st.button(button_text, key=button_key, type=button_type, use_container_width=True)

def display_enemy_card(enemy: Enemy, is_selected: bool, player_count: int):
    """
    Affiche une carte ennemi avec thème sombre
    
    Args:
        enemy: Objet Enemy
        is_selected: État de sélection  
        player_count: Nombre de joueurs pour les stats
    """
    stats = enemy.get_stats_for_players(player_count)
    number = enemy.code.split('-')[-1] if '-' in enemy.code else enemy.code
    magic_indicator = " ✨" if enemy.is_magical else ""
    
    # Détermination couleurs selon état
    if is_selected:
        border_color, bg_color, text_color = Colors.ERROR_RED, "#fff5f5", "#333"
        button_text, button_type = "✅ Sélectionné", "secondary"
    else:
        border_color, bg_color, text_color = Colors.ENEMY_RED, "#2c1810", "#fff"
        button_text, button_type = "➕ Ajouter", "primary"
    
    # Contenu de la carte
    content = f"""
    <h3 style="color: {border_color}; margin: 0 0 8px 0;">👹 #{number}{magic_indicator}</h3>
    <div style="margin: 8px 0;">{enemy.name}</div>
    <div style="font-family: monospace; font-weight: bold;">
        ❤️{stats["health"]} • ⚔️{stats["damage"]} • 🛡️{enemy.defense}
    </div>
    <div style="font-style: italic; color: {'#888' if is_selected else '#ffa500'}; margin: 5px 0;">
        {'Magique' if enemy.is_magical else 'Physique'}
    </div>
    """
    
    # Génération du HTML
    card_html = get_enemy_card_style(border_color, bg_color, text_color)
    card_html = card_html.replace("{content}", content)
    
    # Affichage dans conteneur
    with st.container():
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Bouton d'action
        button_key = f"enemy_{enemy.code}"
        return st.button(button_text, key=button_key, type=button_type, use_container_width=True)

def display_equipment_card_native(equipment, is_selected: bool):
    """
    Affiche une carte d'équipement NATIVE STREAMLIT (compatible 1.47.1)
    Style visuel proche des cartes ennemis mais avec composants natifs
    
    Args:
        equipment: Objet Equipment
        is_selected: Si l'équipement est sélectionné
        
    Returns:
        bool: True si la carte a été cliquée
    """
    # Détermination du type et couleurs
    eq_type = equipment.type.lower().strip() if hasattr(equipment, 'type') and equipment.type else 'accessoire'
    
    if eq_type == 'arme':
        color_emoji = "🟤"  # Marron
        type_name = "Arme"
    elif eq_type == 'armure':
        color_emoji = "🔵"  # Bleu
        type_name = "Armure"
    else:
        color_emoji = "🟣"  # Violet
        type_name = "Accessoire"
    
    # Icône spécifique
    equipment_icon = get_equipment_icon(eq_type, equipment.name)
    
    # Construction des bonus
    bonuses = []
    if equipment.precision > 0:
        bonuses.append(f"🎯+{equipment.precision}")
    if equipment.physical_damage > 0:
        bonuses.append(f"⚔️+{equipment.physical_damage}")
    if equipment.magical_damage > 0:
        bonuses.append(f"✨+{equipment.magical_damage}")
    if equipment.defense > 0:
        bonuses.append(f"🛡️+{equipment.defense}")
    if equipment.spells > 0:
        bonuses.append(f"🔮+{equipment.spells}")
    if equipment.health > 0:
        bonuses.append(f"❤️+{equipment.health}")
    
    bonus_text = " • ".join(bonuses) if bonuses else "Aucun bonus"
    
    # === AFFICHAGE NATIF STREAMLIT ===
    with st.container():
        # Container avec bordure simulée par colonnes
        col1, col2, col3 = st.columns([0.05, 0.9, 0.05])
        
        with col2:
            # Badge sélection
            if is_selected:
                st.success("✅ ÉQUIPÉ")
            else:
                st.markdown(f"<div style='height: 8px;'></div>", unsafe_allow_html=True)
            
            # En-tête avec icône et nom
            st.markdown(f"**{equipment_icon} {equipment.name[:18]}**")
            
            # Type avec couleur
            st.markdown(f"{color_emoji} _{type_name}_")
            
            # Stats en code block pour mise en forme
            if bonuses:
                st.code(bonus_text[:40] + ("..." if len(bonus_text) > 40 else ""))
            else:
                st.code("Aucun bonus")
            
            # Bouton d'action
            button_text = "✅ Équipé" if is_selected else "➕ Équiper"
            button_type = "secondary" if is_selected else "primary"
            
            return st.button(button_text, 
                           key=f"eq_native_{equipment.code}",
                           type=button_type,
                           use_container_width=True)

def display_equipment_selection_native(equipment_list: List, category_name: str, category_icon: str, key_prefix: str):
    """
    Affiche une section d'équipements NATIVE STREAMLIT - 6 par ligne
    
    Args:
        equipment_list: Liste des équipements de la catégorie
        category_name: Nom de la catégorie
        category_icon: Icône de la catégorie  
        key_prefix: Préfixe pour les clés
        
    Returns:
        List: Codes des équipements sélectionnés
    """
    selected_equipment = []
    
    st.markdown(f"#### {category_icon} {category_name}")
    
    # Affichage en grille - 6 cartes par ligne
    if equipment_list:
        # Organisation en colonnes
        cols = st.columns(6)
        
        for i, equipment in enumerate(equipment_list):
            with cols[i % 6]:
                # Vérification si sélectionné (via session state)
                checkbox_key = f"{key_prefix}_{equipment.code}"
                is_selected = st.session_state.get(checkbox_key, False)
                
                # Affichage de la carte native
                if display_equipment_card_native(equipment, is_selected):
                    # Toggle de la sélection
                    new_state = not is_selected
                    st.session_state[checkbox_key] = new_state
                    
                    if new_state:
                        selected_equipment.append(equipment.code)
                    
                    st.rerun()
                
                # Si déjà sélectionné, l'ajouter à la liste
                if is_selected:
                    selected_equipment.append(equipment.code)
    else:
        st.info(f"Aucun équipement de type {category_name.lower()}")
    
    return selected_equipment

def display_progress_indicators_with_reset(nb_heroes: int, nb_enemies: int):
    """
    Affiche les indicateurs de progression avec bouton reset discret THÉMATIQUE
    Version AGGRESSIVE - Force le style contre Streamlit récalcitrant
    
    Args:
        nb_heroes: Nombre de héros sélectionnés
        nb_enemies: Nombre d'ennemis sélectionnés
        
    Returns:
        bool: True si reset demandé
    """
    # CSS HYPER-AGRESSIF pour forcer le style
    st.markdown("""
    <style>
    /* FORCE le style sur TOUS les boutons avec "Reset" dans le texte */
    button[kind="secondary"], 
    button[data-testid*="baseButton"],
    div[data-testid="column"] button,
    .stButton > button {
        background: linear-gradient(135deg, #8b4513, #654321) !important;
        color: #f4e4bc !important;
        border: 2px solid #5d2f02 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-family: 'Cinzel', serif !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
        box-shadow: 0 3px 8px rgba(139,69,19,0.3) !important;
    }
    
    /* Force TOUT le contenu du bouton */
    button[kind="secondary"] div,
    button[data-testid*="baseButton"] div,
    div[data-testid="column"] button div,
    .stButton > button > div {
        color: #f4e4bc !important;
        font-family: 'Cinzel', serif !important;
        font-weight: bold !important;
    }
    
    /* Hover sur tout */
    button[kind="secondary"]:hover,
    button[data-testid*="baseButton"]:hover,
    div[data-testid="column"] button:hover,
    .stButton > button:hover {
        background: linear-gradient(135deg, #a0522d, #8b4513) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 12px rgba(139,69,19,0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Organisation en colonnes pour layout discret
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Indicateurs de progression habituels
        if nb_heroes < 2:
            st.warning(f"🎯 Sélectionnez au moins 2 héros ({nb_heroes}/2)")
        elif nb_enemies == 0:
            st.info("🎯 Maintenant sélectionnez vos ennemis")
        else:
            st.success(f"🎯 Prêt ! {nb_heroes} héros et {nb_enemies} ennemis")
    
    with col2:
        # Bouton reset thématique - FORCE le style
        if nb_heroes > 0 or nb_enemies > 0:
            # Ajout d'un div wrapper pour forcer le style
            st.markdown("""
            <div class="reset-wrapper">
            <style>
            .reset-wrapper button {
                background: linear-gradient(135deg, #8b4513, #654321) !important;
                color: #f4e4bc !important;
                border: 2px solid #5d2f02 !important;
                border-radius: 8px !important;
                font-weight: bold !important;
                font-family: 'Cinzel', serif !important;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
                box-shadow: 0 3px 8px rgba(139,69,19,0.3) !important;
            }
            .reset-wrapper button div {
                color: #f4e4bc !important;
                font-family: 'Cinzel', serif !important;
                font-weight: bold !important;
            }
            .reset-wrapper button:hover {
                background: linear-gradient(135deg, #a0522d, #8b4513) !important;
                transform: translateY(-2px) !important;
            }
            </style>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🗑️ Reset", 
                        key=f"reset_btn_{nb_heroes}_{nb_enemies}",
                        help=f"Effacer {nb_heroes} héros et {nb_enemies} ennemis sélectionnés",
                        use_container_width=True):
                return True
        else:
            # Espace vide pour maintenir l'alignement
            st.empty()
    
    return False

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

def display_combat_result_banner(winner: str):
    """
    Affiche la bannière de résultat de combat
    
    Args:
        winner: 'heroes', 'enemies', ou 'draw'
    """
    combat_styles = get_combat_result_styles()
    
    if winner == 'heroes':
        st.markdown(combat_styles['victory'], unsafe_allow_html=True)
    elif winner == 'enemies':
        st.markdown(combat_styles['defeat'], unsafe_allow_html=True)
    else:
        st.markdown(combat_styles['draw'], unsafe_allow_html=True)

def display_combat_metrics(resource_metrics: Dict[str, Any]):
    """
    Affiche les métriques de ressources du combat
    
    Args:
        resource_metrics: Dictionnaire avec les métriques calculées
    """
    st.subheader("📊 Bilan des Ressources")
    combat_styles = get_combat_result_styles()
    
    # Métriques principales en 3 colonnes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        damage_card = combat_styles['metric_card'].format(
            bg_color="rgba(220,20,60,0.1)", 
            border_color="#dc143c", 
            color="#8b0000",
            icon="💔", 
            title="Blessures", 
            value=resource_metrics['total_damage_taken'], 
            text_color="#b22222"
        )
        st.markdown(damage_card, unsafe_allow_html=True)
    
    with col2:
        spells_card = combat_styles['metric_card'].format(
            bg_color="rgba(138,43,226,0.1)", 
            border_color="#8a2be2", 
            color="#4b0082",
            icon="✨", 
            title="Sorts", 
            value=resource_metrics['total_spells_used'], 
            text_color="#663399"
        )
        st.markdown(spells_card, unsafe_allow_html=True)
    
    with col3:
        avg_card = combat_styles['metric_card'].format(
            bg_color="rgba(255,165,0,0.1)", 
            border_color="#ffa500", 
            color="#ff8c00",
            icon="📈", 
            title="Moyenne", 
            value=resource_metrics['average_damage_per_hero'], 
            text_color="#b8860b"
        )
        st.markdown(avg_card, unsafe_allow_html=True)

def display_heroes_individual_table(resource_metrics: Dict[str, Any]):
    """
    Affiche le tableau détaillé des performances individuelles des héros
    
    Args:
        resource_metrics: Métriques contenant heroes_individual
    """
    st.markdown("#### 🎯 Bilan Individuel")
    
    heroes_metrics = []
    for hero_data in resource_metrics['heroes_individual']:
        blessures = hero_data['damage_taken']
        
        # Évaluation de la difficulté selon les critères utilisateur
        if blessures == 0:
            difficulty = "😊 Très facile"
        elif blessures <= 2:
            difficulty = "🙂 Normal"
        elif blessures <= 4:
            difficulty = "😰 Difficile"
        else:
            difficulty = "😵 Trop difficile"
        
        # Construction de la ligne de données
        heroes_metrics.append({
            "Héros": f"{get_hero_icon(hero_data['name'])} {hero_data['name']} ({hero_data['build']})",
            "Blessures": f"{blessures}",
            "Difficulté": difficulty,
            "PV Restants": f"{hero_data['health_remaining']} ({hero_data['health_percentage']}%)",
            "Sorts": hero_data['spells_used'],
            "Statut": "🟢 Vivant" if hero_data['is_alive'] else "💀 KO"
        })
    
    # Affichage du tableau si données disponibles
    if heroes_metrics:
        df_metrics = pd.DataFrame(heroes_metrics)
        st.dataframe(df_metrics, use_container_width=True, hide_index=True)

def display_combat_log(log_lines: List[str]):
    """
    Affiche le journal de combat avec styles formatés
    Version finale - Journal visible directement, pas de boutons problématiques
    
    Args:
        log_lines: Liste des lignes de log du combat
    """
    st.subheader("📜 Journal de Combat")
    
    # Application des styles à chaque ligne
    formatted_log = [style_combat_log_entry(line) for line in log_lines]
    
    # Construction du conteneur HTML avec scroll
    log_html = """
    <div style='max-height: 500px; overflow-y: auto; padding: 15px; 
                background: rgba(244,228,188,0.3); border-radius: 10px; 
                font-family: monospace;'>
    """
    log_html += "".join(formatted_log)
    log_html += "</div>"
    
    st.markdown(log_html, unsafe_allow_html=True)
    
    # Info utilisateur pour copie manuelle si besoin
    st.info("💡 Pour copier le journal : sélectionnez le texte ci-dessus avec la souris puis Ctrl+C")

def display_combat_summary(result: Dict[str, Any]):
    """
    Affiche un résumé final du combat - Version simplifiée sans boutons
    
    Args:
        result: Dictionnaire des résultats de combat
    """
    st.subheader("🎯 Résumé du Combat")
    
    # Informations basiques du combat
    combat_info = f"""
    <div style="background: linear-gradient(135deg, rgba(212,175,55,0.1), rgba(255,215,0,0.1));
                border: 2px solid #d4af37; border-radius: 12px; padding: 15px; margin: 15px 0;">
        <h5 style="color: #8b4513; margin: 0 0 10px 0; font-family: 'Cinzel', serif;">📊 STATISTIQUES GÉNÉRALES</h5>
        <div style="font-family: monospace; font-weight: bold;">
            ⏱️ Durée: {result.get('rounds', 'N/A')} rounds<br>
            🏆 Vainqueur: {result.get('winner', 'Indéterminé').title()}<br>
            ⚔️ Survivants héros: {result.get('heroes_remaining', 0)}<br>
            👹 Survivants ennemis: {result.get('enemies_remaining', 0)}
        </div>
    </div>
    """
    st.markdown(combat_info, unsafe_allow_html=True)
    
    # Instructions pour relancer un combat
    st.info("🔄 Pour un nouveau combat : modifiez votre sélection dans l'onglet 'Sélection' et relancez")

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

def display_equipment_selection(equipment_list: List, category_name: str, category_icon: str, key_prefix: str):
    """
    Affiche une section de sélection d'équipements par catégorie - VERSION ORIGINALE CHECKBOXES
    
    Args:
        equipment_list: Liste des équipements de la catégorie
        category_name: Nom de la catégorie (ex: "Armes")
        category_icon: Icône de la catégorie (ex: "⚔️")
        key_prefix: Préfixe pour les clés des checkboxes
    
    Returns:
        List: Codes des équipements sélectionnés
    """
    selected_equipment = []
    
    st.markdown(f"#### {category_icon} {category_name}")
    
    for equipment in equipment_list:
        checkbox_key = f"{key_prefix}_{equipment.code}"
        if st.checkbox(equipment.name, key=checkbox_key):
            selected_equipment.append(equipment.code)
        st.caption(f"✨ {equipment.get_bonus_description()}")
    
    return selected_equipment