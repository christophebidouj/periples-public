"""
Module de gestion du styling et des thèmes pour le Simulateur Périples
Version flexible avec système de classes pour boutons
"""

import streamlit as st
from typing import Dict
from models.theme_manager import ThemeManager

def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """
    Convertit une couleur hexadécimale en rgba avec transparence

    Args:
        hex_color: Couleur au format #RRGGBB
        alpha: Valeur de transparence (0.0 à 1.0)

    Returns:
        str: Couleur au format rgba(r, g, b, alpha)
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"

def apply_fantasy_theme(theme_name: str = "Parchemin"):
    """
    Applique le thème fantasy avec système de thèmes dynamique

    Args:
        theme_name: Nom du thème à appliquer ("Parchemin" ou "Professionnel")
    """
    theme = ThemeManager.get_theme(theme_name)

    # Générer les ombres basées sur les couleurs du thème
    shadow_primary = hex_to_rgba(theme.button_primary, 0.4)
    shadow_primary_hover = hex_to_rgba(theme.button_primary, 0.6)
    shadow_success = hex_to_rgba(theme.button_success, 0.4)
    shadow_success_hover = hex_to_rgba(theme.button_success, 0.6)
    shadow_info = hex_to_rgba(theme.button_info, 0.4)
    shadow_info_hover = hex_to_rgba(theme.button_info, 0.6)
    shadow_warning = hex_to_rgba(theme.button_warning, 0.4)
    shadow_warning_hover = hex_to_rgba(theme.button_warning, 0.6)
    shadow_danger = hex_to_rgba(theme.button_danger, 0.4)
    shadow_danger_hover = hex_to_rgba(theme.button_danger, 0.6)
    shadow_magic = hex_to_rgba(theme.button_magic, 0.4)
    shadow_magic_hover = hex_to_rgba(theme.button_magic, 0.6)
    shadow_neutral = hex_to_rgba(theme.button_neutral, 0.4)
    shadow_neutral_hover = hex_to_rgba(theme.button_neutral, 0.6)
    shadow_gold = hex_to_rgba(theme.button_gold, 0.4)
    shadow_gold_hover = hex_to_rgba(theme.button_gold, 0.6)

    # Couleurs tooltips - Thèmes à fond clair (Parchemin, Parchemin V2) vs thèmes sombres
    if theme_name == "Parchemin":
        tooltip_bg = "#f5ead6"
        tooltip_text = "#3b2f1c"
        tooltip_border = "none"
        tooltip_shadow = "0 2px 8px rgba(0, 0, 0, 0.15)"
    elif theme_name == "Parchemin V2":
        # Tooltips adaptés au fond beige avec les couleurs du thème V2
        tooltip_bg = "#d4c4a4"  # Beige plus foncé pour contraste
        tooltip_text = theme.text_primary
        tooltip_border = f"2px solid {theme.title_color}"
        tooltip_shadow = f"0 2px 8px {hex_to_rgba(theme.title_color, 0.3)}"
    else:
        # Fond distinct basé sur tab_background pour meilleure visibilité
        tooltip_bg = theme.tab_background
        tooltip_text = theme.text_primary
        # Bordure subtile avec la couleur du thème
        tooltip_border = f"2px solid {theme.title_color}"
        tooltip_shadow = f"0 2px 8px {hex_to_rgba(theme.title_color, 0.4)}"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&display=swap');

    /* === FOND GÉNÉRAL === */
    .stApp > header {{ background-color: transparent; }}
    .stApp {{ background: {theme.background}; }}
    
    /* === TYPOGRAPHIE === */
    h1, h2, h3 {{
        font-family: 'Cinzel', serif !important;
        color: {theme.text_primary} !important;
    }}

    h1 {{
        text-align: center;
        font-size: 2.5rem !important;
        color: {theme.text_primary} !important;  /* Utilise text_primary au lieu de title_color */
    }}

    /* Force le titre principal Streamlit */
    [data-testid="stHeader"] h1 {{
        color: {theme.text_primary} !important;
    }}

    /* === OVERRIDE CIBLÉ (sans écraser les couleurs inline du log) === */
    /* On ne force PAS les couleurs pour les éléments avec style inline */
    /* Les composants Streamlit spécifiques sont ciblés plus bas */

    /* === COMPOSANTS STREAMLIT NATIFS === */

    /* Expanders (expandables) */
    .stExpander {{
        border: 1px solid {theme.title_color} !important;
        background-color: rgba(255,255,255,0.05) !important;
    }}

    .stExpander summary {{
        color: {theme.text_primary} !important;
        font-weight: bold !important;
    }}

    .stExpander summary span, .stExpander summary p, .stExpander summary div {{
        color: {theme.text_primary} !important;
    }}

    .stExpander > div {{
        color: {theme.text_primary} !important;
    }}

    .stExpander [data-testid="stMarkdownContainer"] {{
        color: {theme.text_primary} !important;
    }}

    /* Force tous les spans dans les expanders (SAUF ceux avec couleur inline) */
    .stExpander span:not([style*="color"]) {{
        color: {theme.text_primary} !important;
    }}

    /* Force tous les paragraphes et divs dans les expanders (SAUF ceux avec couleur inline) */
    .stExpander p:not([style*="color"]),
    .stExpander div:not([style*="color"]) {{
        color: {theme.text_primary} !important;
    }}

    /* Inputs (text, number, etc.) */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {{
        background-color: rgba(0,0,0,0.3) !important;
        color: {theme.text_primary} !important;
        border: 1px solid {theme.title_color} !important;
        font-weight: 500 !important;
        padding: 0.25rem 0.5rem !important;
        min-height: 2rem !important;
    }}

    /* Largeur réduite des zones de saisie */
    .stTextInput, .stNumberInput {{
        max-width: 400px !important;
    }}

    /* Selectbox - Conteneur */
    .stSelectbox > div > div {{
        background-color: rgba(255,255,255,0.1) !important;
        color: {theme.text_primary} !important;
        border: 1px solid {theme.title_color} !important;
    }}

    /* Selectbox - Menu déroulant (options) */
    [data-baseweb="select"] {{
        color: {theme.text_primary} !important;
    }}

    /* Selectbox - Popover du menu */
    [data-baseweb="popover"] {{
        background-color: {theme.background} !important;
    }}

    /* Selectbox - Liste des options */
    ul[role="listbox"] {{
        background-color: {theme.background} !important;
        border: 2px solid {theme.title_color} !important;
    }}

    /* Selectbox - Options individuelles */
    [role="option"] {{
        background-color: {theme.background} !important;
        color: {theme.text_primary} !important;
    }}

    /* Selectbox - Option survolée */
    [role="option"]:hover {{
        background: linear-gradient(135deg, rgba(70, 70, 70, 0.5), rgba(50, 50, 50, 0.4)) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }}

    /* Selectbox - Option sélectionnée */
    [aria-selected="true"] {{
        background: linear-gradient(135deg, rgba(90, 90, 90, 0.6), rgba(70, 70, 70, 0.5)) !important;
        color: #ffffff !important;
        font-weight: bold !important;
    }}

    /* Containers et colonnes (SAUF éléments avec couleur inline) */
    .stContainer:not([style*="color"]),
    [data-testid="stVerticalBlock"] > div:not([style*="color"]) {{
        color: {theme.text_primary} !important;
    }}

    /* Divs de contenu (SAUF éléments avec couleur inline) */
    [data-testid="stMarkdownContainer"] p:not([style*="color"]) {{
        color: {theme.text_primary} !important;
    }}

    /* Labels et captions */
    label, .stCaption {{
        color: {theme.text_primary} !important;
    }}

    /* Success/Info/Warning/Error messages */
    .stSuccess, .stInfo, .stWarning, .stError {{
        color: {theme.text_primary} !important;
    }}

    /* Tooltips (help text au survol) */
    .stTooltipIcon {{
        color: {theme.text_primary} !important;
    }}

    [data-testid="stTooltipHoverTarget"] {{
        color: {theme.text_primary} !important;
    }}

    /* Tooltip container - bordure uniquement sur le conteneur principal */
    [role="tooltip"] {{
        background-color: {tooltip_bg} !important;
        color: {tooltip_text} !important;
        border: {tooltip_border} !important;
        padding: 8px 12px !important;
        box-shadow: {tooltip_shadow} !important;
        border-radius: 6px !important;
    }}

    /* Tout le contenu du tooltip - pas de bordure pour éviter les doublons */
    [role="tooltip"] * {{
        color: {tooltip_text} !important;
        background-color: transparent !important;
        border: none !important;
    }}

    /* Tooltips Streamlit natifs - fond et texte seulement */
    .stTooltipContent, .stTooltipInner {{
        background-color: transparent !important;
        color: {tooltip_text} !important;
        border: none !important;
    }}

    /* Force tous les éléments dans les tooltips */
    [data-baseweb="tooltip"] {{
        background-color: {tooltip_bg} !important;
        color: {tooltip_text} !important;
        border: {tooltip_border} !important;
        box-shadow: {tooltip_shadow} !important;
        border-radius: 6px !important;
    }}

    [data-baseweb="tooltip"] * {{
        color: {tooltip_text} !important;
        background-color: transparent !important;
        border: none !important;
    }}

    /* === ONGLETS SOBRES === */
    .stTabs [data-baseweb="tab-list"] {{
        background: {theme.tab_background};
        border-radius: 10px;
        padding: 4px;
    }}

    .stTabs [data-baseweb="tab"] {{
        color: #ffffff !important;
        font-weight: 600;
        font-family: 'Cinzel', serif;
        border-radius: 6px;
        margin: 2px;
    }}

    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background: {theme.tab_active};
        color: #ffffff !important;
        font-weight: 700;
    }}
    
    /* === CONTENEURS === */
    .main-container {{
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
    }}

    /* === SYSTÈME DE BOUTONS FLEXIBLE === */

    /* Bouton par défaut (ombre adaptée au thème) */
    .stButton > button:not([class*="btn-"]) {{
        background: linear-gradient(135deg, {theme.button_primary}, {theme.button_secondary});
        color: {theme.button_text_color} !important;
        border: 2px solid {theme.button_secondary};
        border-radius: 8px;
        font-weight: bold;
        font-family: 'Cinzel', serif;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
        box-shadow: 0 4px 8px {shadow_primary};
        transition: all 0.3s ease;
    }}

    .stButton > button:not([class*="btn-"]):hover {{
        background: linear-gradient(135deg, {theme.button_primary_hover}, {theme.button_primary});
        transform: translateY(-2px);
        box-shadow: 0 6px 12px {shadow_primary_hover};
    }}
    
    /* Classes spécifiques pour différents types de boutons */

    /* Boutons verts (succès/validation) */
    .btn-success {{
        background: linear-gradient(135deg, {theme.button_success}, {theme.hero_color}) !important;
        color: #ffffff !important;
        border: 2px solid {theme.hero_color_light} !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-family: 'Cinzel', serif !important;
        box-shadow: 0 4px 8px {shadow_success} !important;
        transition: all 0.3s ease !important;
    }}

    .btn-success:hover {{
        background: linear-gradient(135deg, {theme.button_success_hover}, {theme.button_success}) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px {shadow_success_hover} !important;
    }}

    /* Boutons bleus (info/neutre) */
    .btn-info {{
        background: linear-gradient(135deg, {theme.button_info}, #1e3a8a) !important;
        color: #ffffff !important;
        border: 2px solid #1e40af !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-family: 'Cinzel', serif !important;
        box-shadow: 0 4px 8px {shadow_info} !important;
        transition: all 0.3s ease !important;
    }}

    .btn-info:hover {{
        background: linear-gradient(135deg, {theme.button_info_hover}, {theme.button_info}) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px {shadow_info_hover} !important;
    }}

    /* Boutons orange (avertissement) */
    .btn-warning {{
        background: linear-gradient(135deg, {theme.button_warning}, #ff7f50) !important;
        color: #ffffff !important;
        border: 2px solid #ff6347 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-family: 'Cinzel', serif !important;
        box-shadow: 0 4px 8px {shadow_warning} !important;
        transition: all 0.3s ease !important;
    }}

    .btn-warning:hover {{
        background: linear-gradient(135deg, {theme.button_warning_hover}, {theme.button_warning}) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px {shadow_warning_hover} !important;
    }}

    /* Boutons rouges (danger/suppression) */
    .btn-danger {{
        background: linear-gradient(135deg, {theme.button_danger}, {theme.enemy_color}) !important;
        color: #ffffff !important;
        border: 2px solid #660000 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-family: 'Cinzel', serif !important;
        box-shadow: 0 4px 8px {shadow_danger} !important;
        transition: all 0.3s ease !important;
    }}

    .btn-danger:hover {{
        background: linear-gradient(135deg, {theme.button_danger_hover}, {theme.button_danger}) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px {shadow_danger_hover} !important;
    }}

    /* Boutons violets (capacités magiques) */
    .btn-magic {{
        background: linear-gradient(135deg, {theme.button_magic}, #4b0082) !important;
        color: #ffffff !important;
        border: 2px solid #2e0054 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-family: 'Cinzel', serif !important;
        box-shadow: 0 4px 8px {shadow_magic} !important;
        transition: all 0.3s ease !important;
    }}

    .btn-magic:hover {{
        background: linear-gradient(135deg, {theme.button_magic_hover}, {theme.button_magic}) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px {shadow_magic_hover} !important;
    }}

    /* Boutons gris (désactivé/neutre) */
    .btn-neutral {{
        background: linear-gradient(135deg, {theme.button_neutral}, #2f4f4f) !important;
        color: #ffffff !important;
        border: 2px solid #1c3333 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-family: 'Cinzel', serif !important;
        box-shadow: 0 4px 8px {shadow_neutral} !important;
        transition: all 0.3s ease !important;
    }}

    .btn-neutral:hover {{
        background: linear-gradient(135deg, {theme.button_neutral_hover}, {theme.button_neutral}) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px {shadow_neutral_hover} !important;
    }}

    /* Boutons dorés (premium/spécial) */
    .btn-gold {{
        background: linear-gradient(135deg, {theme.button_gold}, #b8860b) !important;
        color: #000000 !important;
        border: 2px solid #8b7500 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-family: 'Cinzel', serif !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.3) !important;
        box-shadow: 0 4px 8px {shadow_gold} !important;
        transition: all 0.3s ease !important;
    }}

    .btn-gold:hover {{
        background: linear-gradient(135deg, {theme.button_gold_hover}, {theme.button_gold}) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px {shadow_gold_hover} !important;
    }}
    
    /* Application des classes aux boutons Streamlit selon leur type */
    button[kind="primary"] {{
        background: linear-gradient(135deg, {theme.button_primary}, {theme.button_secondary}) !important;
        color: {theme.button_text_color} !important;
        border: 2px solid {theme.button_secondary} !important;
    }}

    button[kind="secondary"] {{
        background: linear-gradient(135deg, {theme.button_secondary}, {theme.button_secondary_hover}) !important;
        color: {theme.button_text_color} !important;
        border: 2px solid {theme.button_secondary_hover} !important;
    }}

    button[kind="primary"]:hover {{
        background: linear-gradient(135deg, {theme.button_primary_hover}, {theme.button_primary}) !important;
        color: {theme.button_text_color} !important;
    }}

    button[kind="secondary"]:hover {{
        background: linear-gradient(135deg, {theme.button_primary}, {theme.button_secondary}) !important;
        color: {theme.button_text_color} !important;
    }}

    /* Gestion des boutons désactivés */
    button:disabled,
    .stButton > button:disabled {{
        background: linear-gradient(135deg, #cccccc, #999999) !important;
        color: #666666 !important;
        border: 2px solid #888888 !important;
        opacity: 0.6 !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: none !important;
    }}

    /* Désactivation de la bordure de focus sur tous les boutons */
    button:focus,
    button:active,
    .stButton > button:focus,
    .stButton > button:active,
    button:focus-visible,
    .stButton > button:focus-visible {{
        outline: none !important;
        box-shadow: 0 4px 8px {shadow_primary} !important;
    }}

    /* Override spécifique pour les boutons avec classes */
    .btn-success:focus, .btn-success:active {{
        outline: none !important;
        box-shadow: 0 4px 8px {shadow_success} !important;
    }}

    .btn-info:focus, .btn-info:active {{
        outline: none !important;
        box-shadow: 0 4px 8px {shadow_info} !important;
    }}

    .btn-warning:focus, .btn-warning:active {{
        outline: none !important;
        box-shadow: 0 4px 8px {shadow_warning} !important;
    }}

    .btn-danger:focus, .btn-danger:active {{
        outline: none !important;
        box-shadow: 0 4px 8px {shadow_danger} !important;
    }}

    .btn-magic:focus, .btn-magic:active {{
        outline: none !important;
        box-shadow: 0 4px 8px {shadow_magic} !important;
    }}

    .btn-neutral:focus, .btn-neutral:active {{
        outline: none !important;
        box-shadow: 0 4px 8px {shadow_neutral} !important;
    }}

    .btn-gold:focus, .btn-gold:active {{
        outline: none !important;
        box-shadow: 0 4px 8px {shadow_gold} !important;
    }}

    /* === BOUTONS DE CARTES (responsive, harmonisé avec les cartes) === */

    /* Conteneur pour harmoniser largeur boutons avec cartes (max 260px, responsive) */
    .card-width-button-container {{
        width: 100%;
        max-width: 260px;
        margin: 0 auto;
        display: block;
    }}

    /* Boutons prennent 100% du conteneur (donc max 260px comme les cartes) */
    .card-width-button-container .stButton > button {{
        width: 100% !important;
        margin: 0 !important;
        display: block !important;
    }}

    /* === HARMONISATION HAUTEUR BOUTON RESET === */
    /* Augmente la hauteur des boutons use_container_width pour harmoniser avec bandeau */
    .stButton > button[style*="width"],
    button[style*="width: 100%"],
    button[data-testid*="baseButton"][style*="width"] {{
        min-height: 72px !important;
        padding-top: 20px !important;
        padding-bottom: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # FIX SPÉCIFIQUE PARCHEMIN - Inputs visibles (text_primary est foncé sur ce thème)
    if theme_name == "Parchemin":
        st.markdown("""
        <style>
        /* Inputs lisibles sur fond clair Parchemin */
        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea {
            background-color: rgba(139, 0, 26, 0.15) !important;
            color: #3b2f1c !important;
            font-weight: 500 !important;
        }

        /* Texte des boutons BLANC pour Parchemin */
        .stButton > button,
        button[kind="primary"],
        button[kind="secondary"] {
            color: #ffffff !important;
        }
        </style>
        """, unsafe_allow_html=True)

def create_button_with_class(label: str, button_class: str = "", key: str = None, **kwargs) -> bool:
    """
    Crée un bouton avec une classe CSS spécifique

    Args:
        label: Texte du bouton
        button_class: Classe CSS à appliquer (success, info, warning, danger, magic, neutral, gold)
        key: Clé unique du bouton
        **kwargs: Arguments additionnels pour st.button

    Returns:
        bool: True si le bouton est cliqué
    """
    # Injection du style de classe via HTML si nécessaire
    if button_class:
        st.markdown(f"""
        <style>
        div[data-testid="stButton"] button[key="{key}"] {{
            /* Classe {button_class} sera appliquée automatiquement par le CSS global */
        }}
        </style>
        """, unsafe_allow_html=True)

    return st.button(label, key=key, **kwargs)

def apply_custom_button_style(container_class: str, width: str = "260px", center: bool = True):
    """
    Applique un style personnalisé aux boutons dans un conteneur spécifique

    Args:
        container_class: Classe CSS unique du conteneur
        width: Largeur des boutons (ex: "260px", "100%", "auto")
        center: Centre le bouton dans son conteneur

    Usage:
        apply_custom_button_style("card-button-container", "260px")
        with st.container():
            st.markdown('<div class="card-button-container">', unsafe_allow_html=True)
            st.button("Mon bouton", key="btn1")
            st.markdown('</div>', unsafe_allow_html=True)
    """
    center_style = "margin-left: auto; margin-right: auto; display: block;" if center else ""
    st.markdown(f"""
    <style>
    .{container_class} .stButton > button {{
        width: {width} !important;
        {center_style}
        max-width: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

def get_hero_card_style(hero_name: str, border_color: str, background_style: str) -> str:
    """Génère le style CSS pour une carte héros - responsive 100%"""
    return f"""
    <div style="width: 100%; height: 370px; border-radius: 15px; overflow: hidden;
                box-shadow: 0 6px 12px rgba(0,0,0,0.3); border: 3px solid {border_color};
                {background_style} background-size: cover; background-position: center top;
                display: flex; flex-direction: column; justify-content: flex-end; color: white; margin: 10px auto;">
        <div style="background: linear-gradient(to top, rgba(0, 0, 0, 0.85), transparent 70%); padding: 15px;">
            <div style="background: rgba(0,0,0,0.6); border-radius: 5px; padding: 4px 8px; margin: 0 0 10px 0; text-align: center; display: inline-block;">
                <strong style="font-size: 18px; color: yellow; text-shadow: 2px 2px black;">{hero_name}</strong>
            </div>
            {{stats_content}}
            {{build_content}}
        </div>
    </div>
    """

def get_enemy_card_style(border_color: str, bg_color: str, text_color: str) -> str:
    """Génère le style CSS pour une carte ennemi"""
    return f"""
    <div style="border: 3px solid {border_color}; border-radius: 12px; padding: 15px;
                background-color: {bg_color}; margin: 8px 0; text-align: center; color: {text_color};">
        {{content}}
    </div>
    """

def get_team_recap_styles() -> Dict[str, str]:
    """Retourne les styles pour le récapitulatif des équipes"""
    return {
        'formation_header': """
        <div style="background: linear-gradient(135deg, rgba(139,69,19,0.08), rgba(160,82,45,0.08));
                    border: 2px solid rgba(139,69,19,0.3); border-radius: 20px; padding: 25px; margin: 20px 0;">
            <h3 style="text-align: center; color: #8b4513; font-family: 'Cinzel', serif; margin-bottom: 20px;">
                ⚔️ FORMATION DE GUERRE ⚔️
            </h3>
        </div>
        """,
        
        'heroes_team_header': """
        <div style="background: linear-gradient(135deg, rgba(34,139,34,0.12), rgba(0,100,0,0.08));
                    border: 3px solid #228b22; border-radius: 15px; padding: 20px; margin: 10px;">
            <h4 style="color: #006400; text-align: center; font-family: 'Cinzel', serif; margin-bottom: 15px;">
                🛡️ TEAM HEROS
            </h4>
        </div>
        """,
        
        'enemies_team_header': """
        <div style="background: linear-gradient(135deg, rgba(139,0,0,0.12), rgba(220,20,60,0.08));
                    border: 3px solid #8b0000; border-radius: 15px; padding: 20px; margin: 10px;">
            <h4 style="color: #8b0000; text-align: center; font-family: 'Cinzel', serif; margin-bottom: 15px;">
                👹 TEAM MONSTRES
            </h4>
        </div>
        """,
        
        'hero_card': """
        <div style="background: rgba(255,255,255,0.7); border-radius: 10px; padding: 15px; margin: 8px 0;
                    border-left: 4px solid #228b22; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: #006400; font-size: 1.1rem;">{icon} {name}</strong>
                    <div style="font-size: 0.85rem; color: #666; font-style: italic;">{build_badge}</div>
                </div>
                <div style="text-align: right; font-family: monospace; font-size: 0.9rem; color: #2e8b57;">
                    {stats}
                </div>
            </div>
        </div>
        """,
        
        'enemy_card': """
        <div style="background: rgba(255,255,255,0.7); border-radius: 10px; padding: 15px; margin: 8px 0;
                    border-left: 4px solid #8b0000; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: #8b0000; font-size: 1.1rem;">👹 #{number} {name}</strong>
                    <div style="font-size: 0.85rem; color: #666; font-style: italic;">{magic_badge}</div>
                </div>
                <div style="text-align: right; font-family: monospace; font-size: 0.9rem; color: #b22222;">
                    {stats}
                </div>
            </div>
        </div>
        """,
        
        'battle_stats': """
        <div style="background: linear-gradient(135deg, rgba(212,175,55,0.1), rgba(255,215,0,0.1));
                    border: 2px solid #d4af37; border-radius: 12px; padding: 15px; margin: 15px 0; text-align: center;">
            <h5 style="color: #8b4513; margin: 0 0 10px 0; font-family: 'Cinzel', serif;">📊 PRONOSTIC DE BATAILLE</h5>
            <div style="display: flex; justify-content: space-around; font-weight: bold;">
                <div style="color: #006400;">
                    💚 Héros: {hero_health} PV • {hero_dps:.1f} DPS
                </div>
                <div style="color: #8b0000;">
                    ❤️ Ennemis: {enemy_health} PV • {enemy_dps:.1f} DPS
                </div>
            </div>
        </div>
        """
    }

def get_combat_result_styles() -> Dict[str, str]:
    """Retourne les styles pour les résultats de combat"""
    return {
        'victory': """
        <div style="background: linear-gradient(135deg, rgba(34,139,34,0.2), rgba(0,100,0,0.2));
                    border: 4px solid #228b22; border-radius: 15px; padding: 30px; text-align: center; margin: 20px 0;">
            <h1 style="color: #006400; margin: 0; font-family: 'Cinzel', serif; font-size: 2.5rem;">
                🏆 VICTOIRE HÉROÏQUE ! 🏆
            </h1>
        </div>
        """,
        
        'defeat': """
        <div style="background: linear-gradient(135deg, rgba(220,20,60,0.2), rgba(139,0,0,0.2));
                    border: 4px solid #dc143c; border-radius: 15px; padding: 30px; text-align: center; margin: 20px 0;">
            <h1 style="color: #8b0000; margin: 0; font-family: 'Cinzel', serif; font-size: 2.5rem;">
                💀 DÉFAITE TRAGIQUE 💀
            </h1>
        </div>
        """,
        
        'draw': """
        <div style="background: linear-gradient(135deg, rgba(255,165,0,0.2), rgba(255,140,0,0.2));
                    border: 4px solid #ffa500; border-radius: 15px; padding: 30px; text-align: center; margin: 20px 0;">
            <h1 style="color: #ff8c00; margin: 0; font-family: 'Cinzel', serif; font-size: 2.5rem;">
                ⚔️ COMBAT INDÉCIS ⚔️
            </h1>
        </div>
        """,
        
        'metric_card': """
        <div style="text-align: center; padding: 15px; background: {bg_color}; border-radius: 10px; border: 2px solid {border_color};">
            <h3 style="color: {color}; margin: 0;">{icon} {title}</h3>
            <p style="font-size: 2rem; font-weight: bold; color: {text_color}; margin: 5px 0;">{value}</p>
        </div>
        """
    }

def get_combat_button_styles() -> Dict[str, str]:
    """Retourne les styles pour les boutons de combat"""
    return {
        'ready': """
        <div style="text-align: center; margin: 25px 0;">
            <div style="background: linear-gradient(135deg, #800020, #5d0015); 
                        border-radius: 50px; padding: 3px; display: inline-block;
                        box-shadow: 0 8px 25px rgba(128,0,32,0.5);">
        """,
        
        'disabled': """
        <div style="text-align: center; margin: 25px 0;">
            <div style="background: linear-gradient(135deg, #cccccc, #999999); 
                        border-radius: 50px; padding: 3px; display: inline-block; opacity: 0.6;">
        """,
        
        'close_div': "</div></div>"
    }

def get_forge_styles(theme_name: str = "Parchemin") -> Dict[str, str]:
    """
    Retourne les styles pour l'onglet forge adaptés au thème

    Args:
        theme_name: Nom du thème à utiliser

    Returns:
        Dict[str, str]: Templates HTML stylisés
    """
    theme = ThemeManager.get_theme(theme_name)

    # Générer les couleurs rgba avec transparence
    gold_bg1 = hex_to_rgba(theme.gold, 0.1)
    gold_bg2 = hex_to_rgba(theme.gold, 0.05)
    info_bg1 = hex_to_rgba(theme.button_info, 0.1)
    info_bg2 = hex_to_rgba(theme.button_info, 0.05)
    success_bg1 = hex_to_rgba(theme.button_success, 0.15)
    success_bg2 = hex_to_rgba(theme.button_success, 0.1)

    return {
        'hero_base_stats': f"""
        <div style="background: linear-gradient(135deg, {gold_bg1}, {gold_bg2});
                    border: 2px solid {theme.gold}; border-radius: 10px; padding: 15px; margin: 10px 0;">
            <h4 style="color: {theme.title_color}; margin: 0;">{{icon}} {{name}}</h4>
            <p style="font-family: monospace; font-size: 1.1rem; margin: 5px 0; color: {theme.text_primary};">
                {{stats}}
            </p>
        </div>
        """,

        'current_build': f"""
        <div style="background: linear-gradient(135deg, {info_bg1}, {info_bg2});
                    border: 2px solid {theme.button_info}; border-radius: 10px; padding: 12px; margin: 10px 0;">
            <p style="margin: 0; color: {theme.button_info}; font-weight: bold;">
                {{icon}} Build actuel: {{name}}
            </p>
        </div>
        """,

        'new_stats_preview': f"""
        <div style="background: linear-gradient(135deg, {success_bg1}, {success_bg2});
                    border: 3px solid {theme.button_success}; border-radius: 12px; padding: 20px; margin: 15px 0;">
            <h4 style="color: {theme.button_success}; margin: 0 0 10px 0;">⚡ Nouvelles Statistiques</h4>
            <div style="font-family: monospace; font-size: 1.2rem; margin: 0; color: {theme.text_primary}; font-weight: bold;">
                {{stats}}
            </div>
        </div>
        """
    }

def get_waiting_combat_style() -> str:
    """Style pour l'état d'attente de combat"""
    return """
    <div style="background: linear-gradient(135deg, rgba(255,165,0,0.1), rgba(255,140,0,0.1));
                border: 2px solid #ffa500; border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0;">
        <h3 style="color: #ff8c00; margin: 0;">🏰 En Attente de Combat</h3>
        <p style="color: #b8860b; margin: 10px 0;">Configurez votre combat dans l'onglet Sélection</p>
    </div>
    """

def get_native_app_title():
    """Version native Streamlit - simple et efficace"""
    st.title("⚔️ Périples – Atelier d'Équilibrage ⚔️")
    st.caption("🎲 Simulateur d'équilibrage RPG dans l'univers fantasy")

def style_combat_log_entry(line: str) -> str:
    """Applique le style approprié à une ligne de log de combat"""
    if "Round" in line and "---" in line:
        return f"<div style='color: #8b4513; font-weight: bold; font-size: 18px; margin: 15px 0;'>{line}</div>"
    elif "Phase des Héros" in line:
        return f"<div style='color: #228b22; font-weight: bold; margin: 10px 0; padding: 8px; background: rgba(34,139,34,0.1); border-radius: 5px;'>🛡️ {line}</div>"
    elif "Phase des Ennemis" in line:
        return f"<div style='color: #dc143c; font-weight: bold; margin: 10px 0; padding: 8px; background: rgba(220,20,60,0.1); border-radius: 5px;'>👹 {line}</div>"
    elif "VICTOIRE" in line or "🏆" in line:
        return f"<div style='color: #006400; font-weight: bold; font-size: 20px; margin: 15px 0; padding: 12px; background: rgba(34,139,34,0.2); border-radius: 8px; text-align: center;'>{line}</div>"
    elif "DÉFAITE" in line or "💀" in line:
        return f"<div style='color: #8b0000; font-weight: bold; font-size: 20px; margin: 15px 0; padding: 12px; background: rgba(139,0,0,0.2); border-radius: 8px; text-align: center;'>{line}</div>"
    elif "CRITIQUE" in line or "⚡" in line:
        return f"<div style='color: #ff8c00; font-weight: bold; background: rgba(255,215,0,0.2); padding: 8px; border-radius: 8px; margin: 8px 0;'>{line}</div>"
    else:
        return f"<div style='color: #3b2f1c; margin: 2px 0;'>{line}</div>"

# CONSTANTES DE COULEURS - Version sobre avec nouvelles options
class Colors:
    """Constantes de couleurs pour cohérence du thème sobre avec système flexible"""
    
    # Couleurs principales
    BACKGROUND = "#f4e4bc"
    TEXT_PRIMARY = "#3b2f1c" 
    TITLE_COLOR = "#5a5a5a"
    
    # Couleurs des équipes
    HERO_GREEN = "#228b22"
    HERO_GREEN_LIGHT = "#006400"
    ENEMY_RED = "#8b0000"
    ENEMY_RED_LIGHT = "#dc143c"
    
    # États des cartes
    SELECTED_BORDER = "#4a90e2"
    AVAILABLE_BORDER = "#5a9f5a"
    
    # Couleurs utilitaires
    WARNING_ORANGE = "#ffa500"
    SUCCESS_GREEN = "#228b22"
    ERROR_RED = "#dc143c"
    INFO_BLUE = "#4682b4"
    
    # Couleurs de statut
    GOLD = "#d4af37"
    SILVER = "#c0c0c0"
    BRONZE = "#cd7f32"
    
    # Onglets sobres
    TAB_BACKGROUND = "#6b7280"
    TAB_ACTIVE = "#d97706"
    
    # Système de boutons flexible
    BUTTON_BORDEAUX = "#800020"
    BUTTON_SUCCESS = "#228b22"
    BUTTON_INFO = "#4169e1"
    BUTTON_WARNING = "#ff8c00"
    BUTTON_DANGER = "#dc143c"
    BUTTON_MAGIC = "#8a2be2"
    BUTTON_NEUTRAL = "#708090"
    BUTTON_GOLD = "#ffd700"
    
    # Couleurs d'équipements
    EQUIPMENT_WEAPONS = "#d2691e"
    EQUIPMENT_ARMOR = "#1e90ff"
    EQUIPMENT_ACCESSORIES = "#8a2be2"

# Utilitaires pour l'application des classes CSS
def get_button_classes():
    """Retourne la liste des classes de boutons disponibles"""
    return {
        'success': 'Vert (succès/validation)',
        'info': 'Bleu (information/neutre)',
        'warning': 'Orange (avertissement)',
        'danger': 'Rouge (danger/suppression)',
        'magic': 'Violet (capacités magiques)',
        'neutral': 'Gris (neutre/désactivé)',
        'gold': 'Doré (premium/spécial)'
    }