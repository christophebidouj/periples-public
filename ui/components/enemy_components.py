"""
Composants ennemis pour le Simulateur Périples
Cartes ennemis et éléments liés
"""

import streamlit as st
from models.character import Enemy
from ui.styling import get_enemy_card_style, Colors

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