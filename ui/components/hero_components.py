"""
Composants héros pour le Simulateur Périples
Cartes héros, récapitulatif d'équipe, statistiques
NOUVEAU : Sélecteurs de difficulté (Facile/Normal/Difficile)
AJOUT : Expander détails builds avec données pré-calculées (OPTIMISÉ)
VERSION MIGRÉE : Système basé sur équipements réels
CORRECTION : Selectbox désactivée (pas masquée) pour builds custom
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from models.character import Character

# Import des styles depuis le module styling
from ui.styling import (
    get_hero_card_style, 
    get_team_recap_styles,
    get_forge_styles,
    Colors
)

from ui.components.ui_elements import get_hero_icon, load_hero_image_base64, get_hero_image_path

@st.cache_data
def load_equipment_details_cache():
    """
    Charge et met en cache les détails de tous les équipements
    """
    try:
        df = pd.read_csv("data/equipment.csv")
        equipment_dict = {}
        
        for _, row in df.iterrows():
            code = row['Code']
            equipment_dict[code] = {
                'code': code,
                'name': row['Nom'],
                'type': row['Type'],
                'precision': row.get('Precision', 0),
                'physical_damage': row.get('Physical_Damage', 0),
                'magical_damage': row.get('Magical_Damage', 0),
                'defense': row.get('Defense', 0),
                'spells': row.get('Spells', 0),
                'health': row.get('Health', 0)
            }
        
        print(f"✅ {len(equipment_dict)} équipements mis en cache")
        return equipment_dict
    except Exception as e:
        print(f"❌ Erreur cache équipements: {e}")
        return {}

@st.cache_data
def load_abilities_details_cache(_loader):
    """
    Charge et met en cache les détails de toutes les capacités pour tous les héros
    """
    try:
        from ui.components.forge_abilities_components import get_abilities_for_hero
        
        hero_codes = ['P-1', 'P-2', 'P-3', 'P-4', 'P-5', 'P-6', 'P-7', 'P-8']
        abilities_dict = {}
        
        for hero_code in hero_codes:
            try:
                hero_abilities = get_abilities_for_hero(hero_code, _loader)
                abilities_dict[hero_code] = {}
                
                for ability in hero_abilities:
                    ability_num = getattr(ability, 'ability_number', None)
                    if ability_num:
                        abilities_dict[hero_code][ability_num] = {
                            'number': ability_num,
                            'name': getattr(ability, 'name', f'Capacité {ability_num}'),
                            'cost': getattr(ability, 'spell_cost', 0),
                            'description': getattr(ability, 'description', '')
                        }
            except Exception as e:
                print(f"⚠️ Erreur capacités {hero_code}: {e}")
                abilities_dict[hero_code] = {}
        
        total_abilities = sum(len(abilities) for abilities in abilities_dict.values())
        print(f"✅ {total_abilities} capacités mises en cache pour {len(abilities_dict)} héros")
        return abilities_dict
    except Exception as e:
        print(f"❌ Erreur cache capacités: {e}")
        return {}

def calculate_stats_from_equipment(hero: Character, equipment_codes: List[str], equipment_cache: Dict) -> Dict[str, int]:
    """
    NOUVEAU - Calcule les stats depuis les équipements au lieu d'utiliser get_hero_stats_by_difficulty()
    
    Args:
        hero: Héros de base
        equipment_codes: Liste des codes d'équipements
        equipment_cache: Cache des équipements
        
    Returns:
        Dict avec les stats totales
    """
    # Stats de base du héros
    total_stats = {
        'precision': hero.precision,
        'damage': hero.damage,
        'health': hero.health,
        'parade': 0,
        'spells': hero.spells
    }
    
    # Ajout des bonus d'équipements
    for code in equipment_codes:
        if code in equipment_cache:
            eq = equipment_cache[code]
            total_stats['precision'] += eq['precision']
            total_stats['damage'] += eq['physical_damage']
            total_stats['parade'] += eq['defense']
            total_stats['spells'] += eq['spells']
            total_stats['health'] += eq['health']
    
    return total_stats

def preload_hero_builds_for_all_difficulties(heroes_list: List, equipment_list: List, loader) -> Dict:
    """
    Pré-calcule les 3 builds (Facile/Normal/Difficile) pour tous les héros
    VERSION MIGRÉE : Calcul depuis équipements réels au lieu de stats hardcodées
    
    Returns:
        Dict: Structure {hero_code: [build_facile, build_normal, build_difficile]} avec détails complets
    """
    from hero_builds_data import get_build_name_by_difficulty, get_hero_detailed_build, get_abilities_for_level
    
    # Chargement des caches
    equipment_cache = load_equipment_details_cache()
    abilities_cache = load_abilities_details_cache(loader)
    
    preloaded_builds = {}
    difficulty_levels = ["🟢 Facile", "🔵 Normal", "🔴 Difficile"]
    
    for hero in heroes_list:
        hero_builds = []
        
        for difficulty in difficulty_levels:
            difficulty_clean = difficulty.replace("🟢 ", "").replace("🔵 ", "").replace("🔴 ", "")
            build_name = get_build_name_by_difficulty(difficulty_clean)
            
            # NOUVEAU - Récupération build détaillé depuis hero_builds_data
            detailed_build = get_hero_detailed_build(hero.code, difficulty_clean)
            
            # NOUVEAU - Calcul stats depuis équipements réels
            equipment_codes = detailed_build.get('equipment', [])
            stats = calculate_stats_from_equipment(hero, equipment_codes, equipment_cache)
            
            # === ÉQUIPEMENTS PRÉ-CALCULÉS ===
            equipment_details = []
            for code in equipment_codes:
                if code in equipment_cache:
                    equipment_details.append(equipment_cache[code])
            
            # === CAPACITÉS PRÉ-CALCULÉES ===
            abilities_details = []
            abilities_level = detailed_build.get('abilities_level', 1)
            abilities_numbers = get_abilities_for_level(hero.code, abilities_level)
            hero_abilities_cache = abilities_cache.get(hero.code, {})
            for ability_num in abilities_numbers:
                if ability_num in hero_abilities_cache:
                    abilities_details.append(hero_abilities_cache[ability_num])
            
            # === POTIONS PRÉ-CALCULÉES ===
            potions = detailed_build.get('potions', {'small': 0, 'large': 0})
            
            # Build info complet avec détails pré-calculés
            build_info = {
                'hero_equipped': hero,
                'equipment': [],
                'build_name': build_name,
                'is_custom': False,
                'stats': {'total': stats},
                'difficulty_level': difficulty_clean,
                # Détails pré-calculés
                'build_details': {
                    'equipment': equipment_details,
                    'abilities': abilities_details,
                    'potions': potions,
                    'has_custom_abilities': False
                }
            }
            hero_builds.append(build_info)
        
        preloaded_builds[hero.code] = hero_builds
    
    print(f"✅ Builds pré-calculés pour {len(preloaded_builds)} héros avec équipements réels")
    return preloaded_builds

def get_custom_build_details(hero_code: str, custom_build_data: Dict, equipment_cache: Dict, abilities_cache: Dict) -> Dict:
    """
    Calcule les détails d'un build custom en utilisant les caches
    """
    build_details = {
        'equipment': [],
        'abilities': [],
        'potions': {'small': 0, 'large': 0},
        'has_custom_abilities': False
    }
    
    # Équipements custom
    equipment_codes = custom_build_data.get('equipment', [])
    for code in equipment_codes:
        if code in equipment_cache:
            build_details['equipment'].append(equipment_cache[code])
    
    # Capacités custom
    if custom_build_data.get('abilities_custom', False):
        selected_abilities = custom_build_data.get('abilities', [])
        hero_abilities_cache = abilities_cache.get(hero_code, {})
        
        for ability_num in selected_abilities:
            if ability_num in hero_abilities_cache:
                build_details['abilities'].append(hero_abilities_cache[ability_num])
        
        build_details['has_custom_abilities'] = True
    
    # Potions custom
    potions = custom_build_data.get('potions', {})
    build_details['potions'] = {
        'small': potions.get('small', 0),
        'large': potions.get('large', 0)
    }
    
    return build_details

def display_build_details_expander(hero: Character, current_build_info: Dict):
    """
    Affiche l'expander avec les détails du build actuellement sélectionné
    OPTIMISÉ : Utilise les données pré-calculées, aucune requête
    """
    
    # Récupération des détails selon le type de build
    if current_build_info['is_custom']:
        # Build custom - calcul à la volée avec caches
        custom_builds = st.session_state.get('custom_builds', {})
        if hero.code in custom_builds:
            equipment_cache = load_equipment_details_cache()
            abilities_cache = load_abilities_details_cache(st.session_state.get('data_loader'))
            
            build_details = get_custom_build_details(
                hero.code, 
                custom_builds[hero.code], 
                equipment_cache, 
                abilities_cache
            )
        else:
            build_details = {'equipment': [], 'abilities': [], 'potions': {'small': 0, 'large': 0}, 'has_custom_abilities': False}
    else:
        # Build prédéfini - données déjà pré-calculées
        build_details = current_build_info.get('build_details', {
            'equipment': [], 'abilities': [], 'potions': {'small': 0, 'large': 0}, 'has_custom_abilities': False
        })
    
    # Titre de l'expander avec icône selon le type
    if current_build_info['is_custom']:
        expander_title = f"🔧 Détails {current_build_info['build_name']}"
        expander_color = "#8a2be2"
    else:
        difficulty = current_build_info['difficulty_level']
        if difficulty == "Facile":
            expander_title = f"🟢 Détails"
            expander_color = "#228b22"
        elif difficulty == "Difficile":
            expander_title = f"🔴 Détails"
            expander_color = "#dc143c"
        else:
            expander_title = f"🔵 Détails"
            expander_color = "#4169e1"
    
    with st.expander(expander_title, expanded=False):
        # Style du contenu
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {expander_color}15, {expander_color}05);
                    border-radius: 8px; padding: 12px; margin: 8px 0;">
        """, unsafe_allow_html=True)
        
        # === ÉQUIPEMENTS ===
        if build_details['equipment']:
            st.markdown("**⚔️ Équipements :**")

            equipment_by_type = {'arme': [], 'armure': [], 'accessoire': []}
            for eq in build_details['equipment']:
                eq_type = eq['type'].lower()
                if eq_type not in equipment_by_type:
                    eq_type = 'accessoire'
                equipment_by_type[eq_type].append(eq)

            type_icons = {'arme': '⚔️', 'armure': '🛡️', 'accessoire': '💍'}
            type_names = {'arme': 'Armes', 'armure': 'Armures', 'accessoire': 'Accessoires'}

            # Affichage vertical (une seule colonne)
            for eq_type, equipment in equipment_by_type.items():
                if equipment:
                    st.markdown(f"**{type_icons[eq_type]} {type_names[eq_type]}**")
                    for eq in equipment:
                        # Stats non-nulles
                        stats_parts = []
                        if eq['precision'] > 0:
                            stats_parts.append(f"🎯{eq['precision']}")
                        if eq['physical_damage'] > 0:
                            stats_parts.append(f"⚔️{eq['physical_damage']}")
                        if eq['magical_damage'] > 0:
                            stats_parts.append(f"✨{eq['magical_damage']}")
                        if eq['defense'] > 0:
                            stats_parts.append(f"🛡️{eq['defense']}")
                        if eq['spells'] > 0:
                            stats_parts.append(f"🔮{eq['spells']}")
                        if eq['health'] > 0:
                            stats_parts.append(f"❤️{eq['health']}")

                        stats_text = " • ".join(stats_parts) if stats_parts else "Pas de bonus"
                        st.caption(f"• **{eq['name']}**")
                        st.caption(f"  {stats_text}")
        else:
            st.info("🎒 Aucun équipement")
        
        st.markdown("---")
        
        # === CAPACITÉS ===
        if build_details['abilities']:
            st.markdown("**🔮 Capacités Spéciales :**")
            
            # Affichage en grille 2 colonnes
            cols = st.columns(2)
            for i, ability in enumerate(build_details['abilities']):
                with cols[i % 2]:
                    cost_text = f"({ability['cost']} 🔮)" if ability['cost'] > 0 else "(Gratuit)"
                    st.caption(f"• **{ability['name']}** {cost_text}")
        else:
            st.info("🔮 Aucune capacité spéciale")
        
        st.markdown("---")
        
        # === POTIONS ===
        potions = build_details['potions']
        total_potions = potions['small'] + potions['large']
        
        if total_potions > 0:
            st.markdown("**🧪 Potions de Santé :**")
            
            potion_parts = []
            if potions['small'] > 0:
                plural_s = "s" if potions['small'] > 1 else ""
                potion_parts.append(f"🩸 {potions['small']} Petite{plural_s} (4 PV chacune)")
            if potions['large'] > 0:
                potion_parts.append(f"❤️‍🩹 {potions['large']} Grande (PV max)")
            
            for part in potion_parts:
                st.caption(f"• {part}")
        else:
            st.info("🧪 Aucune potion")
        
        st.markdown("</div>", unsafe_allow_html=True)

def display_hero_card(hero: Character, is_selected: bool, preloaded_builds: Dict, custom_builds_dict: Dict = None, enable_images: bool = True, show_button: bool = True):
    """
    Affiche une carte héros avec style gaming et sélecteur de difficulté
    Utilise les builds pré-calculés pour une réactivité immédiate avec callback
    VERSION MIGRÉE : Stats calculées depuis équipements réels
    CORRECTION : Selectbox désactivée (pas masquée) pour builds custom
    
    Args:
        hero: Objet Character
        is_selected: État de sélection
        preloaded_builds: Builds pré-calculés {hero_code: [facile, normal, difficile]} avec détails complets
        custom_builds_dict: Dictionnaire des builds custom
        enable_images: Activer les images de background
        show_button: Afficher le bouton ou pas (pour gestion externe)
    """
    current_custom_builds = custom_builds_dict or st.session_state.get('custom_builds', {})
    
    # Callback pour mise à jour immédiate de la difficulté
    def on_difficulty_change():
        """Callback exécuté immédiatement lors du changement de difficulté"""
        new_difficulty = st.session_state[f"difficulty_{hero.code}"]
        if 'hero_difficulties' not in st.session_state:
            st.session_state.hero_difficulties = {}
        st.session_state.hero_difficulties[hero.code] = new_difficulty
    
    # Variables communes
    difficulty_levels = ["🟢 Facile", "🔵 Normal", "🔴 Difficile"]
    current_difficulty = st.session_state.get('hero_difficulties', {}).get(hero.code, "🔵 Normal")
    has_custom_build = hero.code in current_custom_builds
    
    # Selectbox TOUJOURS présente - désactivée si build custom
    selectbox_key = f"difficulty_{hero.code}"
    selected_difficulty = st.selectbox(
        "Niveau :",
        options=difficulty_levels,
        index=difficulty_levels.index(current_difficulty),
        key=selectbox_key,
        on_change=on_difficulty_change,
        disabled=has_custom_build,  # ✅ Désactivée si custom
        label_visibility="collapsed"
    )
    
    # Détermination du build selon le type
    if has_custom_build:
        # BUILD CUSTOM - Créer build_info avec détails custom
        custom = current_custom_builds[hero.code]
        
        # Calcul détails custom avec caches
        equipment_cache = load_equipment_details_cache()
        abilities_cache = load_abilities_details_cache(st.session_state.get('data_loader'))
        custom_build_details = get_custom_build_details(hero.code, custom, equipment_cache, abilities_cache)
        
        # NOUVEAU - Calcul stats custom depuis équipements
        equipment_codes = custom.get('equipment', [])
        custom_stats = calculate_stats_from_equipment(hero, equipment_codes, equipment_cache)
        
        build_info = {
            'build_name': custom.get('name', 'Build Custom'),
            'is_custom': True,
            'stats': {'total': custom_stats},
            'difficulty_level': 'Custom',
            'build_details': custom_build_details
        }
    else:
        # BUILDS FIXES - Utiliser difficulté sélectionnée
        # Utiliser la valeur mise à jour par le callback
        updated_difficulty = st.session_state.get('hero_difficulties', {}).get(hero.code, "🔵 Normal")
        difficulty_index = difficulty_levels.index(updated_difficulty)
        
        # Récupération du build pré-calculé avec détails complets
        build_info = preloaded_builds[hero.code][difficulty_index]
    
    # Données pour l'affichage
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
        
        # OPTIMISÉ : Expander avec données pré-calculées
        display_build_details_expander(hero, build_info)
        
        # Bouton sélection héros - utilise use_container_width pour cohérence
        if show_button:
            button_key = f"hero_btn_{hero.code}_{is_selected}"
            result = st.button(button_text, key=button_key, type=button_type, use_container_width=True)
            return result

        return False

def display_team_recap(heroes_details, enemies_details, player_count):
    """Affiche le récapitulatif des équipes avec niveaux de difficulté"""
    st.markdown("## 🛡️ Forces en Présence")

    col1, col2 = st.columns(2)

    # === HÉROS ===
    with col1:
        st.markdown("### 🧙 ÉQUIPE HÉROS")

        for h in heroes_details:
            # Récupération du niveau de difficulté
            difficulty_level = h.get('difficulty_level', 'Normal')
            difficulty_color = {
                'Facile': '🟢',
                'Normal': '🔵', 
                'Difficile': '🔴'
            }.get(difficulty_level, '🔵')
            
            # Affichage avec niveau
            header_text = f"✅ {h['name']} {difficulty_color} — ⚔️ {h['damage']} | ❤️ {h['health']} | 🛡️ {h['parade']} | ✨ {h['spells']}"

            with st.expander(header_text, expanded=False):
                st.write(f"**Niveau :** {difficulty_color} {difficulty_level}")
                st.write(f"**Build :** {h['build_name']}")
                if h.get('is_custom'):
                    st.write("*Build personnalisé*")

    # === MONSTRES ===
    with col2:
        st.markdown("### 👹 ÉQUIPE MONSTRES")

        for e in enemies_details:
            header_text = f"👾 {e['name']} — ❤️ {e['health']} | ⚔️ {e['damage']} | 🛡️ {e['defense']}"

            with st.expander(header_text, expanded=False):
                st.write(f"**Numéro :** #{e['number']}")
                if e.get('is_magical'):
                    st.write("🔮 *Créature magique*")

    # Info joueurs
    st.markdown(f"<p style='color:#888;'>👥 Nombre de joueurs : <strong>{player_count}</strong></p>", unsafe_allow_html=True)

def display_hero_base_stats(hero: Character):
    """
    Affiche les statistiques de base d'un héros pour la forge

    Args:
        hero: Objet Character
    """
    current_theme = st.session_state.get('selected_theme', 'Parchemin')
    forge_styles = get_forge_styles(current_theme)

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
    current_theme = st.session_state.get('selected_theme', 'Parchemin')
    forge_styles = get_forge_styles(current_theme)

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
    current_theme = st.session_state.get('selected_theme', 'Parchemin')
    forge_styles = get_forge_styles(current_theme)

    # Construction de l'affichage des stats
    parade_text = f" • 🛡️ Parade: {temp_stats['parade']}" if temp_stats['parade'] > 0 else ""
    spells_text = f" • ✨ Sorts: {temp_stats['spells']}" if temp_stats['spells'] > 0 else ""

    stats_display = (f"🎯 Précision: {temp_stats['precision']} • "
                     f"⚔️ Dégâts: {temp_stats['damage']} • "
                     f"❤️ PV: {temp_stats['health']}{parade_text}{spells_text}")

    new_stats_html = forge_styles['new_stats_preview'].format(stats=stats_display)
    st.markdown(new_stats_html, unsafe_allow_html=True)