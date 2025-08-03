"""
Composants ennemis pour le Simulateur Périples
Version expanders natifs - Même stratégie que les équipements
Fini les zones blanches pour les monstres aussi !
"""

import streamlit as st
from models.character import Enemy
from ui.styling import Colors

def apply_enemy_expander_theme():
    """
    CSS minimal pour harmoniser les expanders d'ennemis avec le thème fantasy
    """
    st.markdown("""
    <style>
    /* Styling spécifique pour les expanders d'ennemis */
    .streamlit-expanderHeader {
        font-family: 'Cinzel', serif !important;
        font-weight: 600 !important;
    }
    
    /* Headers de sections ennemis */
    .enemy-section-header {
        background: linear-gradient(135deg, rgba(139,0,0,0.1), rgba(244,228,188,0.6));
        border-radius: 12px;
        padding: 12px;
        margin: 15px 0 10px 0;
        text-align: center;
        border: 2px solid rgba(139,0,0,0.3);
    }
    
    .enemy-section-header h4 {
        margin: 0 !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 600 !important;
        color: #8b0000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def get_smart_enemy_name_display(enemy_name: str, max_length: int = 18) -> str:
    """
    Troncature intelligente des noms d'ennemis
    
    Args:
        enemy_name: Nom complet de l'ennemi
        max_length: Longueur maximale autorisée
        
    Returns:
        str: Nom affiché (tronqué intelligemment si nécessaire)
    """
    if len(enemy_name) <= max_length:
        return enemy_name
    
    # Troncature intelligente aux espaces si possible
    if ' ' in enemy_name[:max_length-3]:
        words = enemy_name.split(' ')
        result = words[0]
        for word in words[1:]:
            if len(result + ' ' + word) <= max_length-3:
                result += ' ' + word
            else:
                result += '...'
                break
        return result
    else:
        # Pas d'espace, troncature simple
        return enemy_name[:max_length-3] + "..."

def display_enemy_card_expander(enemy: Enemy, is_selected: bool, player_count: int):
    """
    Affiche une carte ennemi avec st.expander() natif
    
    Args:
        enemy: Objet Enemy
        is_selected: État de sélection  
        player_count: Nombre de joueurs pour les stats
        
    Returns:
        bool: True si la carte a été cliquée
    """
    stats = enemy.get_stats_for_players(player_count)
    number = enemy.code.split('-')[-1] if '-' in enemy.code else enemy.code
    magic_indicator = " ✨" if enemy.is_magical else ""
    
    # Nom avec troncature intelligente
    name_display = get_smart_enemy_name_display(enemy.name, 18)
    
    # Badge de sélection dans le titre
    selection_badge = "✅ " if is_selected else ""
    
    # === EXPANDER NATIF STREAMLIT FERMÉ PAR DÉFAUT ===
    with st.expander(f"{selection_badge}👹 #{number} {name_display}{magic_indicator}", expanded=False):
        
        # Type d'ennemi avec couleur
        enemy_type = "✨ Magique" if enemy.is_magical else "⚔️ Physique"
        type_color = "#8a2be2" if enemy.is_magical else "#dc143c"
        st.markdown(f"<span style='color: {type_color}; font-weight: bold; font-size: 0.9rem;'>{enemy_type}</span>", 
                   unsafe_allow_html=True)
        
        # Métriques des stats principales
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="❤️ Points de Vie",
                value=stats["health"],
                delta=None
            )
        
        with col2:
            st.metric(
                label="⚔️ Dégâts",
                value=stats["damage"],
                delta=None
            )
        
        # Défense en métrique unique
        st.metric(
            label="🛡️ Défense",
            value=enemy.defense,
            delta=None
        )
        
        # Informations supplémentaires
        if enemy.has_magical_damage:
            st.caption("💫 Possède des dégâts magiques")
        
        # Mode de jeu affiché
        st.caption(f"📊 Stats pour {player_count} joueur{'s' if player_count > 1 else ''}")
        
        # Bouton d'action
        button_text = "✅ Sélectionné" if is_selected else "➕ Ajouter"
        button_type = "secondary" if is_selected else "primary"
        
        return st.button(button_text, 
                       key=f"enemy_exp_{enemy.code}",
                       type=button_type,
                       use_container_width=True)

def display_enemy_section_expanders(enemies: list, player_count: int, search_term: str = ""):
    """
    Affiche la section complète des ennemis avec expanders
    
    Args:
        enemies: Liste des ennemis à afficher
        player_count: Nombre de joueurs
        search_term: Terme de recherche pour filtrage
        
    Returns:
        list: Liste des codes d'ennemis sélectionnés
    """
    # Application du thème CSS minimal
    apply_enemy_expander_theme()
    
    selected_enemies = []
    
    # === HEADER THÉMATIQUE ENNEMIS ===
    st.markdown("""
    <div class="enemy-section-header">
        <h4>👹 Ennemis Disponibles</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Info mode joueurs
    if player_count >= 2:
        st.info(f"🎯 Mode {player_count} joueurs (stats adaptées automatiquement)")
    
    # Filtrage des ennemis selon la recherche
    if search_term.strip():
        term = search_term.strip().lower()
        filtered_enemies = [e for e in enemies if term in e.code.split('-')[-1].lower() or term in e.name.lower()]
        
        if filtered_enemies:
            st.write(f"**{len(filtered_enemies)} ennemis trouvés :**")
        else:
            st.warning(f"Aucun ennemi trouvé pour '{search_term}'")
            return []
    else:
        # Affichage limité par défaut
        filtered_enemies = enemies[:15]
        st.info("💡 Tapez un numéro ou nom dans la recherche pour trouver d'autres ennemis")
    
    # Affichage en grille - 5 ennemis par ligne (comme avant)
    if filtered_enemies:
        cols = st.columns(5)
        
        for i, enemy in enumerate(filtered_enemies):
            with cols[i % 5]:
                # Vérification si sélectionné (via session state global)
                is_selected = enemy.code in st.session_state.get('selected_enemies', [])
                
                # Affichage avec expander natif
                if display_enemy_card_expander(enemy, is_selected, player_count):
                    # Toggle de la sélection dans session state global
                    if 'selected_enemies' not in st.session_state:
                        st.session_state.selected_enemies = []
                    
                    if is_selected:
                        st.session_state.selected_enemies.remove(enemy.code)
                    else:
                        st.session_state.selected_enemies.append(enemy.code)
                    
                    st.rerun()
                
                # Ajouter à la liste si sélectionné
                if is_selected:
                    selected_enemies.append(enemy.code)
    
    return selected_enemies

# Fonction de compatibilité avec l'ancien système
def display_enemy_card(enemy: Enemy, is_selected: bool, player_count: int):
    """Fonction de compatibilité - Redirige vers la version expander"""
    return display_enemy_card_expander(enemy, is_selected, player_count)