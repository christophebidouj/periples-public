"""
Module de gestion du styling et des thèmes pour le Simulateur Périples
Version avec boutons bordeaux royal (#800020) - Harmonie parfaite
"""

import streamlit as st
from typing import Dict

def apply_fantasy_theme():
    """Applique le thème fantasy médiéval avec fonts Google et couleurs bordeaux"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&display=swap');
    .stApp > header { background-color: transparent; }
    .stApp { background: #f4e4bc; }
    h1, h2, h3 { font-family: 'Cinzel', serif !important; color: #3b2f1c !important; }
    h1 { text-align: center; font-size: 2.5rem !important; color: #8b4513 !important; }
    .stTabs [data-baseweb="tab-list"] { background: linear-gradient(135deg, #8fbc8f, #6b8e6b); border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: #2d4a2d !important; font-weight: 600; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background: rgba(255,255,255,0.4); }
    .main-container { background: rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; margin: 10px 0; }
    
    /* NOUVEAUX BOUTONS BORDEAUX ROYAL - Application globale */
    .stButton > button {
        background: linear-gradient(135deg, #800020, #5d0015) !important;
        color: #f4e4bc !important;
        border: 2px solid #4d0012 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-family: 'Cinzel', serif !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7) !important;
        box-shadow: 0 4px 8px rgba(128,0,32,0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #a0002a, #800020) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(128,0,32,0.6) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
        box-shadow: 0 3px 6px rgba(128,0,32,0.4) !important;
    }
    
    /* Boutons spécifiques selon le type */
    button[kind="primary"] {
        background: linear-gradient(135deg, #800020, #5d0015) !important;
        border: 2px solid #4d0012 !important;
    }
    
    button[kind="secondary"] {
        background: linear-gradient(135deg, #6d001a, #4d0012) !important;
        border: 2px solid #330009 !important;
    }
    
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #a0002a, #800020) !important;
    }
    
    button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #800020, #5d0015) !important;
    }
    </style>
    """, unsafe_allow_html=True)

def get_hero_card_style(hero_name: str, border_color: str, background_style: str) -> str:
    """Génère le style CSS pour une carte héros"""
    return f"""
    <div style="width: 260px; height: 370px; border-radius: 15px; overflow: hidden;
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
    """Retourne les styles pour les boutons de combat - VERSION BORDEAUX ROYAL"""
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

def get_forge_styles() -> Dict[str, str]:
    """Retourne les styles pour l'onglet forge"""
    return {
        'hero_base_stats': """
        <div style="background: linear-gradient(135deg, rgba(212,175,55,0.1), rgba(139,69,19,0.1));
                    border: 2px solid #d4af37; border-radius: 10px; padding: 15px; margin: 10px 0;">
            <h4 style="color: #8b4513; margin: 0;">{icon} {name}</h4>
            <p style="font-family: monospace; font-size: 1.1rem; margin: 5px 0; color: #3b2f1c;">
                {stats}
            </p>
        </div>
        """,
        
        'current_build': """
        <div style="background: linear-gradient(135deg, rgba(70,130,180,0.1), rgba(30,144,255,0.1));
                    border: 2px solid #4682b4; border-radius: 10px; padding: 12px; margin: 10px 0;">
            <p style="margin: 0; color: #2c5aa0; font-weight: bold;">
                {icon} Build actuel: {name}
            </p>
        </div>
        """,
        
        'new_stats_preview': """
        <div style="background: linear-gradient(135deg, rgba(34,139,34,0.15), rgba(0,100,0,0.15));
                    border: 3px solid #228b22; border-radius: 12px; padding: 20px; margin: 15px 0;">
            <h4 style="color: #006400; margin: 0 0 10px 0;">⚡ Nouvelles Statistiques</h4>
            <div style="font-family: monospace; font-size: 1.2rem; margin: 0; color: #2e8b57; font-weight: bold;">
                {stats}
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

def get_app_title_style() -> str:
    """Style pour le titre principal de l'application"""
    return """
    <h1 style="text-align: center; font-family: 'Cinzel', serif; color: #8b4513; font-size: 3rem; margin-bottom: 2rem;">
        ⚔️ Simulateur Périples ⚔️
    </h1>
    <p style="text-align: center; font-style: italic; color: #6f4f27; margin-bottom: 2rem; font-size: 1.2rem;">
        Outil d'équilibrage RPG dans l'univers fantasy
    </p>
    """

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

# CONSTANTES DE COULEURS - Centralisation avec nouveaux bordeaux
class Colors:
    """Constantes de couleurs pour cohérence du thème"""
    
    # Couleurs principales
    BACKGROUND = "#f4e4bc"
    TEXT_PRIMARY = "#3b2f1c" 
    TITLE_COLOR = "#8b4513"
    
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
    
    # NOUVEAUX BOUTONS BORDEAUX ROYAL
    BUTTON_PRIMARY = "#800020"
    BUTTON_PRIMARY_HOVER = "#a0002a"
    BUTTON_SECONDARY = "#6d001a"
    BUTTON_BORDER = "#4d0012"
    
    # Couleurs d'équipements (validées selon harmonie)
    EQUIPMENT_WEAPONS = "#d2691e"    # Orange chocolat
    EQUIPMENT_ARMOR = "#1e90ff"      # Bleu ciel profond
    EQUIPMENT_ACCESSORIES = "#8a2be2" # Violet bleu