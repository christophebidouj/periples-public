"""
Éléments d'interface pour le Simulateur Périples
Gestion des icônes, images et composants visuels
VERSION SIMPLIFIÉE - JPG direct sans fallback
"""

import base64
import os
from typing import Optional

def get_hero_icon(hero_name: str) -> str:
    """Retourne l'icône correspondant au héros"""
    icon_mapping = {
        "Elneha": "🐻",
        "Liarie": "🔮", 
        "Atucan": "🛡️",
        "Kraor": "🏹",
        "Thordius": "⚔️",
        "Stephe": "🎵",  # Stephe le Barde - SANS ACCENT
        "Lame": "🗡️",
        "Raishi": "👊"
    }
    return icon_mapping.get(hero_name, "⚔️")

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

def get_hero_image_path(hero_name: str) -> Optional[str]:
    """Retourne le chemin vers l'image du héros - VERSION JPG DIRECT"""
    # Mapping direct vers les fichiers JPG - SANS ACCENT pour éviter les erreurs
    image_mapping = {
        "Elneha": "data/images/Elneha_-_Druidesse.jpg",
        "Liarie": "data/images/Liarie_-_Mage.jpg", 
        "Atucan": "data/images/Atucan_-_Paladin.jpg",
        "Kraor": "data/images/Kraor_-_Rodeur.jpg",
        "Thordius": "data/images/Thordius_-_Barbare.jpg",
        "Stephe": "data/images/Stephe_-_Barde.jpg",  # SANS ACCENT - Mapping direct
        "Lame": "data/images/Lame_-_Roublarde.jpg",
        "Raishi": "data/images/Raishi_-_Pugiliste.jpg"
    }
    
    return image_mapping.get(hero_name)

def load_hero_image_base64(image_path: str) -> Optional[str]:
    """Charge une image héros en base64 pour affichage"""
    try:
        if not image_path or not os.path.exists(image_path):
            return None
            
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode()
            return encoded_image
            
    except Exception as e:
        return None

def get_hero_background_style(hero_name: str, border_color: str) -> str:
    """Génère le style de background pour une carte héros"""
    image_path = get_hero_image_path(hero_name)
    
    if image_path:
        img_base64 = load_hero_image_base64(image_path)
        if img_base64:
            return f"background-image: url('data:image/jpeg;base64,{img_base64}');"
    
    # Fallback : dégradé coloré si pas d'image
    return f"background: linear-gradient(135deg, {border_color}33, {border_color}11);"

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
    import streamlit as st
    
    # CSS HYPER-AGRESSIF pour forcer le style BORDEAUX ROYAL sur TOUS les boutons
    st.markdown("""
    <style>
    /* FORCE le style BORDEAUX ROYAL sur TOUS les boutons */
    button[kind="secondary"], 
    button[data-testid*="baseButton"],
    div[data-testid="column"] button,
    .stButton > button {
        background: linear-gradient(135deg, #800020, #5d0015) !important;
        color: #f4e4bc !important;
        border: 2px solid #4d0012 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-family: 'Cinzel', serif !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7) !important;
        box-shadow: 0 4px 8px rgba(128,0,32,0.4) !important;
    }
    
    /* Force TOUT le contenu du bouton BORDEAUX */
    button[kind="secondary"] div,
    button[data-testid*="baseButton"] div,
    div[data-testid="column"] button div,
    .stButton > button > div {
        color: #f4e4bc !important;
        font-family: 'Cinzel', serif !important;
        font-weight: bold !important;
    }
    
    /* Hover BORDEAUX sur tout */
    button[kind="secondary"]:hover,
    button[data-testid*="baseButton"]:hover,
    div[data-testid="column"] button:hover,
    .stButton > button:hover {
        background: linear-gradient(135deg, #a0002a, #800020) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(128,0,32,0.6) !important;
    }
    
    /* Boutons primaires spécifiques */
    button[kind="primary"] {
        background: linear-gradient(135deg, #800020, #5d0015) !important;
        border: 2px solid #4d0012 !important;
    }
    
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #a0002a, #800020) !important;
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
            # Ajout d'un div wrapper pour forcer le style BORDEAUX
            st.markdown("""
            <div class="reset-wrapper">
            <style>
            .reset-wrapper button {
                background: linear-gradient(135deg, #800020, #5d0015) !important;
                color: #f4e4bc !important;
                border: 2px solid #4d0012 !important;
                border-radius: 8px !important;
                font-weight: bold !important;
                font-family: 'Cinzel', serif !important;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.7) !important;
                box-shadow: 0 4px 8px rgba(128,0,32,0.4) !important;
            }
            .reset-wrapper button div {
                color: #f4e4bc !important;
                font-family: 'Cinzel', serif !important;
                font-weight: bold !important;
            }
            .reset-wrapper button:hover {
                background: linear-gradient(135deg, #a0002a, #800020) !important;
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