"""
Composants équipements pour le Simulateur Périples
Option 1: st.expander() natifs + correction taille des noms
Solution 100% compatible Streamlit
"""

import streamlit as st
from typing import List
from ui.components.ui_elements import get_equipment_icon

def apply_expander_theme():
    """
    CSS minimal pour harmoniser les expanders avec le thème fantasy
    """
    st.markdown("""
    <style>
    /* Headers de sections d'équipements */
    .equipment-section-header {
        background: linear-gradient(135deg, rgba(139,69,19,0.1), rgba(244,228,188,0.6));
        border-radius: 12px;
        padding: 12px;
        margin: 15px 0 10px 0;
        text-align: center;
        border: 2px solid rgba(139,69,19,0.3);
    }
    
    .equipment-section-header h4 {
        margin: 0 !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 600 !important;
    }
    
    /* Léger styling des expanders pour harmonie */
    .streamlit-expanderHeader {
        font-family: 'Cinzel', serif !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def get_smart_name_display(equipment_name: str, max_length: int = 20) -> str:
    """
    Troncature intelligente des noms d'équipements
    
    Args:
        equipment_name: Nom complet de l'équipement
        max_length: Longueur maximale autorisée
        
    Returns:
        str: Nom affiché (tronqué intelligemment si nécessaire)
    """
    if len(equipment_name) <= max_length:
        return equipment_name
    
    # Troncature intelligente aux espaces si possible
    if ' ' in equipment_name[:max_length-3]:
        words = equipment_name.split(' ')
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
        return equipment_name[:max_length-3] + "..."

def display_equipment_card_expander(equipment, is_selected: bool):
    """
    Affiche un équipement avec st.expander() natif Streamlit
    
    Args:
        equipment: Objet Equipment
        is_selected: Si l'équipement est sélectionné
        
    Returns:
        bool: True si la carte a été cliquée
    """
    # Détermination du type et couleurs
    eq_type = equipment.type.lower().strip() if hasattr(equipment, 'type') and equipment.type else 'accessoire'
    
    # Couleurs d'équipements validées
    if eq_type == 'arme':
        type_name = "Arme"
        type_color = "#d2691e"
    elif eq_type == 'armure':
        type_name = "Armure"
        type_color = "#1e90ff"
    else:
        type_name = "Accessoire"
        type_color = "#8a2be2"
    
    # Icône spécifique
    equipment_icon = get_equipment_icon(eq_type, equipment.name)
    
    # Calcul des bonus
    bonuses = []
    if equipment.precision > 0:
        bonuses.append(('Précision', equipment.precision, '🎯'))
    if equipment.physical_damage > 0:
        bonuses.append(('Dégâts', equipment.physical_damage, '⚔️'))
    if equipment.magical_damage > 0:
        bonuses.append(('Magie', equipment.magical_damage, '✨'))
    if equipment.defense > 0:
        bonuses.append(('Parade', equipment.defense, '🛡️'))
    if equipment.spells > 0:
        bonuses.append(('Sorts', equipment.spells, '🔮'))
    if equipment.health > 0:
        bonuses.append(('PV', equipment.health, '❤️'))
    
    # Nom avec troncature intelligente (20 caractères max)
    name_display = get_smart_name_display(equipment.name, 20)
    
    # Badge de sélection dans le titre
    selection_badge = "✅ " if is_selected else ""
    
    # === EXPANDER NATIF STREAMLIT FERMÉ PAR DÉFAUT ===
    with st.expander(f"{selection_badge}{equipment_icon} {name_display}", expanded=False):
        
        # Type avec couleur
        st.markdown(f"<span style='color: {type_color}; font-weight: bold; font-size: 0.9rem;'>{type_name}</span>", 
                   unsafe_allow_html=True)
        
        # Métriques principales
        if bonuses:
            # Trier par valeur décroissante et prendre les 2 premiers
            top_bonuses = sorted(bonuses, key=lambda x: x[1], reverse=True)[:2]
            
            if len(top_bonuses) == 1:
                # Une seule métrique
                stat_name, value, icon = top_bonuses[0]
                st.metric(
                    label=f"{icon} {stat_name}",
                    value=f"+{value}",
                    delta=None
                )
            else:
                # Deux métriques en colonnes
                col1, col2 = st.columns(2)
                
                with col1:
                    stat_name, value, icon = top_bonuses[0]
                    st.metric(
                        label=f"{icon} {stat_name}",
                        value=f"+{value}",
                        delta=None
                    )
                
                with col2:
                    stat_name, value, icon = top_bonuses[1]
                    st.metric(
                        label=f"{icon} {stat_name}",
                        value=f"+{value}",
                        delta=None
                    )
            
            # Bonus supplémentaires en texte compact
            if len(bonuses) > 2:
                other_bonuses = [f"{icon}+{val}" for _, val, icon in bonuses[2:]]
                st.caption(" • ".join(other_bonuses))
        else:
            st.metric(
                label="📊 Bonus",
                value="Aucun",
                delta=None
            )
        
        # Bouton d'action
        button_text = "✅ Équipé" if is_selected else "➕ Équiper"
        button_type = "secondary" if is_selected else "primary"
        
        return st.button(button_text, 
                       key=f"eq_exp_{equipment.code}",
                       type=button_type,
                       use_container_width=True)

def display_equipment_selection_expanders(equipment_list: List, category_name: str, category_icon: str, key_prefix: str):
    """
    Section d'équipements avec expanders - 6 par ligne
    
    Args:
        equipment_list: Liste des équipements de la catégorie
        category_name: Nom de la catégorie
        category_icon: Icône de la catégorie  
        key_prefix: Préfixe pour les clés
        
    Returns:
        List: Codes des équipements sélectionnés
    """
    # Application du thème CSS minimal
    apply_expander_theme()
    
    selected_equipment = []
    
    # Couleur selon le type
    if "Armes" in category_name:
        header_color = "#d2691e"
    elif "Armures" in category_name:
        header_color = "#1e90ff"
    elif "Accessoires" in category_name:
        header_color = "#8a2be2"
    else:
        header_color = "#8b4513"
    
    # === HEADER THÉMATIQUE ===
    st.markdown(f"""
    <div class="equipment-section-header">
        <h4 style="color: {header_color};">{category_icon} {category_name}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Affichage en grille - 6 cartes par ligne
    if equipment_list:
        # Organisation en colonnes
        cols = st.columns(6)
        
        for i, equipment in enumerate(equipment_list):
            with cols[i % 6]:
                # Vérification si sélectionné (via session state)
                checkbox_key = f"{key_prefix}_{equipment.code}"
                is_selected = st.session_state.get(checkbox_key, False)
                
                # Affichage avec expander natif
                if display_equipment_card_expander(equipment, is_selected):
                    # Toggle de la sélection
                    new_state = not is_selected
                    st.session_state[checkbox_key] = new_state

                    if new_state:
                        selected_equipment.append(equipment.code)

                    # SUPPRIMÉ : st.rerun() causait retour au premier onglet
                    # Streamlit rerun automatiquement lors du prochain cycle
                
                # Si déjà sélectionné, l'ajouter à la liste
                if is_selected:
                    selected_equipment.append(equipment.code)
    else:
        # Message d'info
        st.info(f"Aucun équipement de type {category_name.lower()}")
    
    return selected_equipment

# Fonctions de compatibilité avec l'ancien système
def display_equipment_selection_native(equipment_list: List, category_name: str, category_icon: str, key_prefix: str):
    """Fonction de compatibilité - Redirige vers la version expanders"""
    return display_equipment_selection_expanders(equipment_list, category_name, category_icon, key_prefix)

def display_equipment_card_native(equipment, is_selected: bool):
    """Fonction de compatibilité - Redirige vers la version expanders"""
    return display_equipment_card_expander(equipment, is_selected)