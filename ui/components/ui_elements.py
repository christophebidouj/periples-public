"""
Éléments d'interface pour le Simulateur Périples
Gestion des icônes, images et composants visuels
VERSION PROPRE - Sans forçage CSS brutal
"""

import streamlit as st
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

def get_hero_image_path(hero_name: str, current_form: Optional[str] = None) -> Optional[str]:
    """
    Retourne le chemin vers l'image du héros - VERSION JPG DIRECT

    Args:
        hero_name: Nom du héros
        current_form: Forme actuelle (pour Elneha uniquement) : "bear", "wolf", "human"

    Returns:
        Chemin vers l'image appropriée
    """
    # CAS SPÉCIAL ELNEHA : Images selon forme de transformation
    if hero_name == "Elneha" and current_form:
        if current_form == "bear":
            return "data/images/Ours.jpg"
        elif current_form == "wolf":
            return "data/images/Loup.jpg"
        # Si current_form == "human" ou autre, utiliser l'image par défaut

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

def create_styled_button(label: str, button_type: str = "default", key: str = None, disabled: bool = False, **kwargs):
    """
    Crée un bouton avec style spécifique sans forçage CSS brutal
    
    Args:
        label: Texte du bouton
        button_type: Type de bouton (success, info, warning, danger, magic, neutral, gold)
        key: Clé unique du bouton
        disabled: État désactivé
        **kwargs: Arguments additionnels pour st.button
    
    Returns:
        bool: True si le bouton est cliqué
    """
    # Application douce du style via data attributes
    if button_type != "default":
        st.markdown(f"""
        <style>
        div[data-testid="stButton"] button[data-button-type="{button_type}"] {{
            /* Le style sera appliqué par les classes CSS du thème principal */
        }}
        </style>
        """, unsafe_allow_html=True)
    
    # Bouton natif Streamlit avec attributs personnalisés
    if key:
        button_key = f"{button_type}_{key}"
    else:
        button_key = key
    
    return st.button(label, key=button_key, disabled=disabled, **kwargs)

def display_progress_indicators_with_reset(nb_heroes: int, nb_enemies: int):
    """
    Affiche les indicateurs de progression avec bouton reset PROPRE
    
    Args:
        nb_heroes: Nombre de héros sélectionnés
        nb_enemies: Nombre d'ennemis sélectionnés
        
    Returns:
        bool: True si reset demandé
    """
    
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
        # Bouton reset propre - utilise le thème par défaut
        if nb_heroes > 0 or nb_enemies > 0:
            if st.button("🗑️ Reset", 
                        key=f"reset_btn_{nb_heroes}_{nb_enemies}",
                        help=f"Effacer {nb_heroes} héros et {nb_enemies} ennemis sélectionnés",
                        use_container_width=True,
                        type="secondary"):  # Type Streamlit natif
                return True
        else:
            # Espace vide pour maintenir l'alignement
            st.empty()
    
    return False

def create_button_with_custom_style(label: str, style_class: str, key: str, **kwargs):
    """
    Alternative pour boutons avec styles personnalisés via CSS ciblé
    """
    # CSS ciblé sur la clé spécifique
    st.markdown(f"""
    <style>
    div[data-testid="stButton"] button[data-key="{key}"] {{
        /* Style appliqué selon la classe {style_class} */
    }}
    </style>
    """, unsafe_allow_html=True)
    
    return st.button(label, key=key, **kwargs)

def apply_button_theme_classes():
    """
    Applique les classes de thème aux boutons existants
    Version non-agressive qui respecte les types Streamlit
    """
    st.markdown("""
    <style>
    /* Styles appliqués selon les attributs data des boutons */
    button[data-button-type="success"] {
        background: linear-gradient(135deg, #228b22, #006400) !important;
        color: white !important;
        border: 2px solid #004d00 !important;
    }
    
    button[data-button-type="info"] {
        background: linear-gradient(135deg, #4169e1, #1e3a8a) !important;
        color: white !important;
        border: 2px solid #1e40af !important;
    }
    
    button[data-button-type="warning"] {
        background: linear-gradient(135deg, #ff8c00, #ff7f50) !important;
        color: white !important;
        border: 2px solid #ff6347 !important;
    }
    
    button[data-button-type="danger"] {
        background: linear-gradient(135deg, #dc143c, #8b0000) !important;
        color: white !important;
        border: 2px solid #660000 !important;
    }
    
    button[data-button-type="magic"] {
        background: linear-gradient(135deg, #8a2be2, #4b0082) !important;
        color: white !important;
        border: 2px solid #2e0054 !important;
    }
    
    button[data-button-type="neutral"] {
        background: linear-gradient(135deg, #708090, #2f4f4f) !important;
        color: white !important;
        border: 2px solid #1c3333 !important;
    }
    
    button[data-button-type="gold"] {
        background: linear-gradient(135deg, #ffd700, #b8860b) !important;
        color: black !important;
        border: 2px solid #8b7500 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Constantes pour les types de boutons
class ButtonTypes:
    """Types de boutons disponibles pour le système flexible"""
    DEFAULT = "default"
    SUCCESS = "success"
    INFO = "info" 
    WARNING = "warning"
    DANGER = "danger"
    MAGIC = "magic"
    NEUTRAL = "neutral"
    GOLD = "gold"