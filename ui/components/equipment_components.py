"""
Composants équipements pour le Simulateur Périples
Cartes équipements natives compatible Streamlit 1.47.1
"""

import streamlit as st
from typing import List
from ui.components.ui_elements import get_equipment_icon

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
    
    # NOUVELLES COULEURS VALIDÉES (sans emojis colorés)
    if eq_type == 'arme':
        type_name = "Arme"
    elif eq_type == 'armure':
        type_name = "Armure"
    else:
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
            
            # Type avec couleur DIRECTE (sans emoji)
            if eq_type == 'arme':
                st.markdown(f"<span style='color: #d2691e; font-weight: bold;'>{type_name}</span>", unsafe_allow_html=True)
            elif eq_type == 'armure':
                st.markdown(f"<span style='color: #1e90ff; font-weight: bold;'>{type_name}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color: #8a2be2; font-weight: bold;'>{type_name}</span>", unsafe_allow_html=True)
            
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
    
    # Titre avec couleur selon le type (NOUVELLES COULEURS APPLIQUÉES)
    if "Armes" in category_name:
        st.markdown(f"<h4 style='color: #d2691e;'>{category_icon} {category_name}</h4>", unsafe_allow_html=True)
    elif "Armures" in category_name:
        st.markdown(f"<h4 style='color: #1e90ff;'>{category_icon} {category_name}</h4>", unsafe_allow_html=True)
    elif "Accessoires" in category_name:
        st.markdown(f"<h4 style='color: #8a2be2;'>{category_icon} {category_name}</h4>", unsafe_allow_html=True)
    else:
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