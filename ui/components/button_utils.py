"""
Utilitaires pour la gestion des boutons colorés
Système flexible pour éviter les conflits avec Streamlit
"""

import streamlit as st
from typing import Optional

class ButtonStyle:
    """Classes de styles disponibles pour les boutons"""
    DEFAULT = ""           # Bordeaux par défaut
    SUCCESS = "btn-success"    # Vert
    INFO = "btn-info"         # Bleu  
    WARNING = "btn-warning"   # Orange
    DANGER = "btn-danger"     # Rouge
    MAGIC = "btn-magic"       # Violet
    NEUTRAL = "btn-neutral"   # Gris
    GOLD = "btn-gold"         # Doré

def create_button(label: str, 
                 style: str = ButtonStyle.DEFAULT, 
                 key: str = None, 
                 disabled: bool = False,
                 use_container_width: bool = False,
                 help_text: str = None) -> bool:
    """
    Crée un bouton avec style personnalisé de manière propre
    
    Args:
        label: Texte du bouton
        style: Style du bouton (utiliser ButtonStyle.*)
        key: Clé unique pour le bouton
        disabled: Bouton désactivé
        use_container_width: Utilise toute la largeur du conteneur
        help_text: Texte d'aide au survol
    
    Returns:
        bool: True si le bouton est cliqué
    """
    
    # Application du style via classes CSS si nécessaire
    if style and style != ButtonStyle.DEFAULT:
        # Injection CSS ciblée pour ce bouton spécifique
        st.markdown(f"""
        <style>
        div[data-testid="stButton"] > button[data-key="{key}"] {{
            /* Style sera appliqué via la classe {style} définie dans styling.py */
        }}
        </style>
        """, unsafe_allow_html=True)
    
    # Créer le bouton natif Streamlit
    return st.button(
        label=label,
        key=key,
        disabled=disabled,
        use_container_width=use_container_width,
        help=help_text
    )

def success_button(label: str, key: str = None, **kwargs) -> bool:
    """Bouton vert de succès"""
    return create_button(label, ButtonStyle.SUCCESS, key, **kwargs)

def info_button(label: str, key: str = None, **kwargs) -> bool:
    """Bouton bleu d'information"""
    return create_button(label, ButtonStyle.INFO, key, **kwargs)

def warning_button(label: str, key: str = None, **kwargs) -> bool:
    """Bouton orange d'avertissement"""
    return create_button(label, ButtonStyle.WARNING, key, **kwargs)

def danger_button(label: str, key: str = None, **kwargs) -> bool:
    """Bouton rouge de danger"""
    return create_button(label, ButtonStyle.DANGER, key, **kwargs)

def magic_button(label: str, key: str = None, **kwargs) -> bool:
    """Bouton violet pour capacités magiques"""
    return create_button(label, ButtonStyle.MAGIC, key, **kwargs)

def neutral_button(label: str, key: str = None, **kwargs) -> bool:
    """Bouton gris neutre"""
    return create_button(label, ButtonStyle.NEUTRAL, key, **kwargs)

def gold_button(label: str, key: str = None, **kwargs) -> bool:
    """Bouton doré premium"""
    return create_button(label, ButtonStyle.GOLD, key, **kwargs)

def apply_button_css_injection(button_key: str, css_class: str):
    """
    Injecte du CSS spécifique pour un bouton donné
    
    Args:
        button_key: Clé du bouton à cibler
        css_class: Classe CSS à appliquer
    """
    st.markdown(f"""
    <style>
    /* Application de la classe {css_class} au bouton {button_key} */
    button[data-testid="baseButton-secondary"][key="{button_key}"],
    button[data-testid="baseButton-primary"][key="{button_key}"],
    div[data-testid="stButton"] > button[key="{button_key}"] {{
        /* Les styles seront hérités de la classe {css_class} définie dans styling.py */
    }}
    </style>
    """, unsafe_allow_html=True)

def create_contextual_button(context: str, label: str, key: str = None, **kwargs) -> bool:
    """
    Crée un bouton selon le contexte d'usage
    
    Args:
        context: Contexte ('combat', 'forge', 'selection', 'abilities', 'potions')
        label: Texte du bouton
        key: Clé unique
        **kwargs: Arguments additionnels
    
    Returns:
        bool: True si cliqué
    """
    
    context_styles = {
        'combat': ButtonStyle.DANGER,      # Rouge pour combat
        'forge': ButtonStyle.WARNING,      # Orange pour forge
        'selection': ButtonStyle.SUCCESS,  # Vert pour sélection
        'abilities': ButtonStyle.MAGIC,    # Violet pour capacités
        'potions': ButtonStyle.INFO,       # Bleu pour potions
        'reset': ButtonStyle.NEUTRAL,      # Gris pour reset
        'premium': ButtonStyle.GOLD        # Doré pour premium
    }
    
    style = context_styles.get(context, ButtonStyle.DEFAULT)
    return create_button(label, style, key, **kwargs)

def demo_button_styles():
    """Fonction de démonstration des différents styles de boutons"""
    st.subheader("🎨 Démonstration des Styles de Boutons")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Styles de base :**")
        
        if create_button("Bordeaux (défaut)", ButtonStyle.DEFAULT, "demo_default"):
            st.success("Bouton bordeaux cliqué !")
            
        if success_button("Succès (vert)", "demo_success"):
            st.success("Bouton vert cliqué !")
            
        if info_button("Information (bleu)", "demo_info"):
            st.info("Bouton bleu cliqué !")
            
        if warning_button("Avertissement (orange)", "demo_warning"):
            st.warning("Bouton orange cliqué !")
    
    with col2:
        st.write("**Styles spécialisés :**")
        
        if danger_button("Danger (rouge)", "demo_danger"):
            st.error("Bouton rouge cliqué !")
            
        if magic_button("Magie (violet)", "demo_magic"):
            st.success("Bouton violet cliqué !")
            
        if neutral_button("Neutre (gris)", "demo_neutral"):
            st.info("Bouton gris cliqué !")
            
        if gold_button("Premium (doré)", "demo_gold"):
            st.balloons()
            st.success("Bouton doré cliqué !")
    
    st.write("**Contextuels :**")
    cols = st.columns(4)
    
    with cols[0]:
        if create_contextual_button('combat', '⚔️ Combat', 'demo_combat'):
            st.info("Combat !")
    
    with cols[1]:
        if create_contextual_button('forge', '🔨 Forge', 'demo_forge'):
            st.info("Forge !")
    
    with cols[2]:
        if create_contextual_button('abilities', '🔮 Capacités', 'demo_abilities'):
            st.info("Capacités !")
    
    with cols[3]:
        if create_contextual_button('potions', '🧪 Potions', 'demo_potions'):
            st.info("Potions !")

# Exemples d'usage pour la documentation
USAGE_EXAMPLES = """
# Exemples d'usage des boutons colorés

## Import
```python
from ui.components.button_utils import ButtonStyle, create_button, success_button, danger_button
```

## Usage simple
```python
# Bouton vert de succès
if success_button("✅ Valider", "btn_validate"):
    st.success("Validé !")

# Bouton rouge de danger  
if danger_button("🗑️ Supprimer", "btn_delete"):
    st.error("Supprimé !")

# Bouton personnalisé
if create_button("🔮 Magie", ButtonStyle.MAGIC, "btn_magic", use_container_width=True):
    st.info("Sort lancé !")
```

## Usage contextuel
```python
# Selon le contexte
if create_contextual_button('combat', '⚔️ Attaque', 'btn_attack'):
    handle_attack()

if create_contextual_button('forge', '🔨 Équiper', 'btn_equip'):
    handle_equipment()
```
"""