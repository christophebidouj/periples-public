import streamlit as st
import time
import os
from typing import List, Dict

# Import des modules locaux
from models.character import Character, Enemy
from models.combat_engine import CombatEngine
from models.rules_engine import GameRules
from utils.data_loader import DataLoader

# === CONFIGURATION IMAGES ===
ENABLE_IMAGES = True  # Images compressées maintenant

# === CACHE STREAMLIT POUR IMAGES ===
@st.cache_data
def load_hero_image_base64(image_path: str) -> str:
    """Cache Streamlit pour les images - persiste entre rerun"""
    if not image_path or not os.path.exists(image_path):
        return None
    
    try:
        import base64
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# === FONCTIONS UTILITAIRES OPTIMISÉES ===

@st.cache_data(persist=True)
def get_image_as_base64_cached(image_path: str) -> str:
    """Version cachée de get_image_as_base64"""
    return get_image_as_base64(image_path)

def get_hero_image_path_simple(hero_name: str) -> str:
    """Retourne le chemin d'image d'un héros selon votre structure"""
    # Mapping exact selon vos noms de fichiers - TOUTES LES VARIANTES pour Stèphe
    hero_file_mapping = {
        "Atucan": "Atucan_-_Paladin.png",
        "Elneha": "Elneha_-_Druidesse.png", 
        "Kraor": "Kraor_-_Rodeur.png",
        "Lame": "Lame_-_Roublarde.png",
        "Liarie": "Liarie_-_Mage.png",
        "Raishi": "Raishi_-_Pugiliste.png",
        "Stèphe": "Stèphe_-_Barde.png",
        "Thordius": "Thordius_-_Barbare.png",
        "Ours": "Ours.png",
        "Ours S": "Ours_S.png",
        "Loup": "Loup.png",
        "Loup S": "Loup_S.png"
    }
    
    # Obtenir le nom de fichier exact
    filename = hero_file_mapping.get(hero_name)
    if filename:
        image_path = f"data/images/{filename}"
        if os.path.exists(image_path):
            return image_path
    
    # Fallback spécial pour Stèphe si problème d'accent
    if hero_name == "Stèphe":
        fallback_paths = [
            "data/images/Stephe_-_Barde.png",
            "data/images/Stèphe_-_Barde.png", 
            "data/images/Stéphe_-_Barde.png"
        ]
        for path in fallback_paths:
            if os.path.exists(path):
                return path
    
    return None  # Aucune image trouvée

@st.cache_data(persist=True)
def get_cached_build_info(hero_code: str, _loader) -> Dict:
    """Cache les informations de build pour éviter les recalculs"""
    hero_list = _loader.load_heroes()
    hero = next(h for h in hero_list if h.code == hero_code)
    return get_hero_build(hero, _loader)

def get_image_as_base64(image_path: str) -> str:
    """Convertit une image en base64 pour CSS background-image"""
    try:
        import base64
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def get_hero_icon(name: str) -> str:
    """Retourne icône héros"""
    icons = {"Elneha": "🐻", "Liarie": "🔮", "Atucan": "🛡️", "Kraor": "⚔️",
             "Thordius": "🪓", "Stèphe": "🎭", "Lame": "🗡️", "Raishi": "🏹"}
    return icons.get(name, "⚔️")

# === FONCTIONS PRINCIPALES ===

def init_app():
    """Initialise l'application"""
    # Configuration page
    st.set_page_config(page_title="Simulateur RPG", page_icon="⚔️", layout="wide")
    
    # Création dossier data si inexistant
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Initialisation session
    if 'selected_heroes' not in st.session_state:
        st.session_state.selected_heroes = []
    if 'selected_enemies' not in st.session_state:
        st.session_state.selected_enemies = []
    if 'custom_builds' not in st.session_state:
        st.session_state.custom_builds = {}

@st.cache_data
def load_data():
    """Charge les données du jeu - AVEC CACHE"""
    loader = DataLoader()
    
    # Vérification fichiers CSV
    missing_files = [f for f in ["heroes.csv", "enemies.csv", "equipment.csv"] 
                     if not os.path.exists(f"data/{f}")]
    
    if missing_files:
        st.info("🔄 Création fichiers données...")
        loader.create_csv_files()
        st.success("✅ Fichiers créés !")
        time.sleep(1)
        st.rerun()
    
    return {
        'heroes': loader.load_heroes(),
        'enemies': loader.load_enemies(),
        'equipment': loader.load_equipment(),
        'loader': loader
    }

def apply_fantasy_theme():
    """Applique le thème fantasy OPTIMISÉ"""
    st.markdown("""
    <style>
    /* Import de police fantasy - OPTIMISÉ */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&display=swap');
    
    /* Suppression bande blanche Streamlit */
    .stApp > header { background-color: transparent; }
    
    .stApp {
        background: #f4e4bc;
        background-attachment: fixed;
    }
    
    /* Force le thème */
    .stApp, .main, .block-container {
        background-color: transparent !important;
    }
    
    /* Titres SIMPLIFIÉS */
    h1, h2, h3 {
        font-family: 'Cinzel', serif !important;
        color: #3b2f1c !important;
    }
    
    h1 {
        text-align: center;
        font-size: 2.5rem !important;
        margin-bottom: 2rem;
        color: #8b4513 !important;
    }
    
    /* Onglets AVEC COULEURS DOUCES */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, #8fbc8f, #6b8e6b);
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #2d4a2d !important;
        font-weight: 600;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: rgba(255,255,255,0.4);
        color: #1a331a !important;
    }
    
    /* Container SIMPLIFIÉ */
    .main-container {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 2px solid rgba(139,69,19,0.3);
    }
    
    /* Personnalisation des boutons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    /* Bouton primaire vert doux */
    .stButton > button[kind="primary"] {
        background-color: #5a9f5a !important;
        border-color: #4a8f4a !important;
        color: white !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #4a8f4a !important;
        border-color: #3a7f3a !important;
    }
    
    /* Bouton secondaire bleu doux */
    .stButton > button[kind="secondary"] {
        background-color: #4a90e2 !important;
        border-color: #3a80d2 !important;
        color: white !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #3a80d2 !important;
        border-color: #2a70c2 !important;
    }
    
    </style>
    """, unsafe_allow_html=True)

def get_hero_build(hero: Character, loader: DataLoader) -> Dict:
    """Récupère infos build héros"""
    # Build custom ou standard
    if hero.code in st.session_state.custom_builds:
        custom_data = st.session_state.custom_builds[hero.code]
        equipment_codes = custom_data.get('equipment', [])
        custom_name = custom_data.get('name', 'Build Custom')
        
        all_equipment = loader.load_equipment()
        hero_equipment = [eq for eq in all_equipment if eq.code in equipment_codes]
        build_name = custom_name
        is_custom = True
    else:
        hero_equipment = loader.get_hero_loadout(hero.code)
        build_name = "Build Standard"
        is_custom = False
    
    # Application équipements
    hero_copy = hero.model_copy()
    hero_copy.equip_items(hero_equipment, build_name)
    
    return {
        'hero_equipped': hero_copy,
        'equipment': hero_equipment,
        'build_name': build_name,
        'is_custom': is_custom,
        'stats': hero_copy.get_stats_summary()
    }

def display_hero_card_fantasy(hero: Character, build_info: Dict, is_selected: bool):
    """Version avec option images ON/OFF"""
    stats = build_info['stats']['total']
    custom_icon = "🔧" if build_info['is_custom'] else "📋"
    hero_icon = get_hero_icon(hero.name)
    
    # Couleurs selon sélection - BOUTONS VERTS
    if is_selected:
        border_color = "#4a90e2"  # Bleu doux
        box_shadow = "0 8px 16px rgba(74,144,226,0.3)"
        button_text = "✅ Sélectionné"
        button_type = "secondary"
    else:
        border_color = "#5a9f5a"  # Vert doux
        box_shadow = "0 6px 12px rgba(0,0,0,0.3)"
        button_text = "➕ Ajouter"
        button_type = "primary"
    
    # Images conditionnelles
    background_style = ""
    if ENABLE_IMAGES:
        image_path = get_hero_image_path_simple(hero.name)
        if image_path:
            img_base64 = load_hero_image_base64(image_path)
            if img_base64:
                background_style = f"background-image: url('data:image/png;base64,{img_base64}');"
    
    if not background_style:
        # Dégradé coloré par héros
        background_style = f"background: linear-gradient(135deg, {border_color}33, {border_color}11);"
    
    # Stats bonus
    bonus_parts = []
    if stats["parade"] > 0:
        bonus_parts.append(f"🛡️{stats['parade']}")
    if stats["spells"] > 0:
        bonus_parts.append(f"✨{stats['spells']}")
    
    bonus_text = f" • {' • '.join(bonus_parts)}" if bonus_parts else ""
    
    # Carte fluide
    with st.container():
        st.markdown(f"""
        <div style="
            position: relative;
            width: 260px;
            height: 370px;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: {box_shadow};
            border: 3px solid {border_color};
            {background_style}
            background-size: cover;
            background-position: center top;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            color: white;
            margin: 10px auto;
        ">
            <div style="
                background: linear-gradient(to top, rgba(0, 0, 0, 0.85), transparent 70%);
                padding: 15px;
            ">
                <div style="background: rgba(0,0,0,0.6); border-radius: 5px; padding: 4px 8px; margin: 0 0 10px 0; text-align: center; display: inline-block;">
                    <strong style="font-size: 18px; color: yellow; text-shadow: 2px 2px black;">{hero.name}</strong>
                </div>
                <div style="font-family: monospace; font-size: 1rem; margin-bottom: 5px; font-weight: bold; color: #f0f0f0; text-shadow: 1px 1px 2px rgba(0,0,0,0.7);">
                    🎯{stats["precision"]} • ⚔️{stats["damage"]} • ❤️{stats["health"]}{bonus_text}
                </div>
                <div style="font-size: 0.9rem; font-style: italic; color: #e0e0e0; text-shadow: 1px 1px 2px rgba(0,0,0,0.6);">
                    {build_info["build_name"][:25]}{"..." if len(build_info["build_name"]) > 25 else ""}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Bouton avec clé unique pour éviter double-clic
        button_key = f"hero_btn_{hero.code}_{is_selected}"  # Clé qui change selon l'état
        if st.button(button_text, key=button_key, type=button_type, use_container_width=True):
            if is_selected:
                st.session_state.selected_heroes.remove(hero.code)
            else:
                st.session_state.selected_heroes.append(hero.code)
            st.rerun()

def display_enemy_card_fantasy(enemy: Enemy, is_selected: bool, player_count: int):
    """Affiche carte ennemi style sombre fantasy - version robuste"""
    stats = enemy.get_stats_for_players(player_count)
    number = enemy.code.split('-')[-1] if '-' in enemy.code else enemy.code
    magic = " ✨" if enemy.is_magical else ""
    
    # Couleurs selon sélection
    if is_selected:
        border_color = "#dc3545"
        bg_color = "#fff5f5"
        text_color = "#333"
        button_text = "✅ Sélectionné"
        button_type = "secondary"
    else:
        border_color = "#8b0000"
        bg_color = "#2c1810"
        text_color = "#fff"
        button_text = "➕ Ajouter"
        button_type = "primary"
    
    # Container avec style robuste
    with st.container():
        # En-tête ennemi
        st.markdown(f"""
        <div style="
            border: 3px solid {border_color};
            border-radius: 12px;
            padding: 15px;
            background-color: {bg_color};
            margin: 8px 0;
            text-align: center;
            color: {text_color};
        ">
            <h3 style="color: {border_color}; margin: 0 0 8px 0;">👹 #{number}{magic}</h3>
            <div style="margin: 8px 0;">{enemy.name}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats principales
        st.markdown(f"""
        <div style="text-align: center; font-family: monospace; font-weight: bold; color: {text_color};">
            ❤️{stats["health"]} • ⚔️{stats["damage"]} • 🛡️{enemy.defense}
        </div>
        """, unsafe_allow_html=True)
        
        # Type d'ennemi
        enemy_type = "Magique" if enemy.is_magical else "Physique"
        type_color = "#ffa500" if not is_selected else "#888"
        st.markdown(f"""
        <div style="text-align: center; font-style: italic; color: {type_color}; margin: 5px 0;">
            {enemy_type}
        </div>
        """, unsafe_allow_html=True)
        
        # Bouton sélection
        if st.button(button_text, key=f"enemy_{enemy.code}", type=button_type, use_container_width=True):
            if is_selected:
                st.session_state.selected_enemies.remove(enemy.code)
            else:
                st.session_state.selected_enemies.append(enemy.code)
            st.rerun()

def tab_selection(data):
    """Onglet sélection équipes avec style fantasy - VERSION OPTIMISÉE"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.header("🏰 Sélection des Équipes")
    
    heroes = data['heroes']
    enemies = data['enemies']
    loader = data['loader']
    
    # Indicateur progression
    nb_heroes = len(st.session_state.selected_heroes)
    nb_enemies = len(st.session_state.selected_enemies)
    
    if nb_heroes < 2:
        st.warning(f"🎯 Sélectionnez au moins 2 héros ({nb_heroes}/2)")
    elif nb_enemies == 0:
        st.info("🎯 Maintenant sélectionnez vos ennemis")
    else:
        st.success(f"🎯 Prêt ! {nb_heroes} héros et {nb_enemies} ennemis")
    
    # === SECTION HÉROS OPTIMISÉE ===
    st.subheader("🛡️ Héros Disponibles")
    st.markdown("*📋 = Standard • 🔧 = Personnalisé*")
    
    # Grille responsive pour les héros - AVEC CACHE - 6 PAR LIGNE
    cols = st.columns(6)
    for i, hero in enumerate(heroes):
        # CACHE le build_info pour éviter les recalculs
        build_info = get_cached_build_info(hero.code, loader)
        is_selected = hero.code in st.session_state.selected_heroes
        
        with cols[i % 6]:
            display_hero_card_fantasy(hero, build_info, is_selected)
    
    # === SECTION ENNEMIS ===
    st.subheader("👹 Ennemis")
    
    # Calcul auto nombre joueurs
    player_count = max(2, nb_heroes) if nb_heroes >= 2 else 2
    if nb_heroes >= 2:
        st.info(f"🎯 Mode {player_count} joueurs (auto)")
    
    # Recherche ennemis
    search = st.text_input("🔍 Recherche:", placeholder="Ex: 34, Dragon...")
    
    # Filtrage
    if search.strip():
        term = search.strip().lower()
        filtered = []
        for enemy in enemies:
            num = enemy.code.split('-')[-1] if '-' in enemy.code else enemy.code
            if term in num.lower() or term in enemy.name.lower():
                filtered.append(enemy)
    else:
        filtered = enemies[:15]
        st.info("💡 Tapez un numéro ou nom pour chercher")
    
    # Affichage ennemis en grille
    if filtered:
        st.write(f"**{len(filtered)} ennemis trouvés:**")
        cols = st.columns(5)
        
        for i, enemy in enumerate(filtered):
            is_selected = enemy.code in st.session_state.selected_enemies
            with cols[i % 5]:
                display_enemy_card_fantasy(enemy, is_selected, player_count)
    
    # === RÉCAPITULATIF DES ÉQUIPES ===
    if nb_heroes >= 2 and nb_enemies > 0:
        st.subheader("⚔️ Récapitulatif du Combat")
        
        # Récupération des noms pour affichage
        selected_hero_names = []
        for code in st.session_state.selected_heroes:
            hero = next(h for h in heroes if h.code == code)
            build_info = get_cached_build_info(code, loader)
            build_icon = "🔧" if build_info['is_custom'] else "📋"
            selected_hero_names.append(f"{get_hero_icon(hero.name)} {hero.name} {build_icon}")
        
        selected_enemy_names = []
        for code in st.session_state.selected_enemies:
            enemy = next(e for e in enemies if e.code == code)
            number = enemy.code.split('-')[-1] if '-' in enemy.code else enemy.code
            magic = " ✨" if enemy.is_magical else ""
            selected_enemy_names.append(f"👹 #{number}{magic} {enemy.name[:20]}")
        
        # Tableau récapitulatif avec style
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(34,139,34,0.1), rgba(0,100,0,0.1));
                border: 2px solid #228b22;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
            ">
                <h4 style="color: #006400; margin: 0 0 10px 0;">🛡️ HÉROS ({nb_heroes})</h4>
                <div style="font-size: 0.9rem; color: #2e8b57;">
                    {"<br>".join(selected_hero_names)}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="
                text-align: center;
                font-size: 2rem;
                font-weight: bold;
                color: #8b4513;
                margin: 40px 0;
                font-family: 'Cinzel', serif;
            ">
                ⚔️<br>VS<br>👹
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(139,0,0,0.1), rgba(220,20,60,0.1));
                border: 2px solid #8b0000;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
            ">
                <h4 style="color: #8b0000; margin: 0 0 10px 0;">👹 ENNEMIS ({nb_enemies})</h4>
                <div style="font-size: 0.9rem; color: #b22222;">
                    {"<br>".join(selected_enemy_names)}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Configuration et lancement
    st.subheader("⚙️ Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        rules = {
            'ranged_attacks': True,
            'magical_damage': True,
            'criticals': st.checkbox("🎯 Critiques"),
            'initiative': st.checkbox("🎲 Initiative")
        }
        st.caption("🏹 Attaques distance et ✨ Dégâts magiques : activés automatiquement")
    
    with col2:
        st.info("⚔️ Combat détaillé avec log complet")
    
    # Bouton lancement
    ready = nb_heroes >= 2 and nb_enemies > 0
    
    if st.button("🚀 Lancer Combat", type="primary", disabled=not ready, use_container_width=True):
        if ready:
            st.session_state['run_simulation'] = True
            st.session_state['simulation_config'] = {
                'hero_codes': st.session_state.selected_heroes,
                'enemy_codes': st.session_state.selected_enemies,
                'player_count': player_count,
                'rules': rules
            }
            st.success("✅ Combat configuré ! → Onglet Résultats")
    
    st.markdown('</div>', unsafe_allow_html=True)

def tab_customization(data):
    """Onglet customisation builds avec style fantasy"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.header("⚙️ Forge des Équipements")
    
    heroes = data['heroes']
    equipment = data['equipment']
    
    # Sélection héros avec style
    hero_options = {h.code: f"{get_hero_icon(h.name)} {h.name}" for h in heroes}
    selected_code = st.selectbox("Choisir un héros:", list(hero_options.keys()), 
                                format_func=lambda x: hero_options[x])
    selected_hero = next(h for h in heroes if h.code == selected_code)
    
    # Stats base avec style
    st.subheader("📊 Statistiques de Base")
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(212,175,55,0.1), rgba(139,69,19,0.1));
        border: 2px solid #d4af37;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    ">
        <h4 style="color: #8b4513; margin: 0; font-family: 'Cinzel', serif;">{get_hero_icon(selected_hero.name)} {selected_hero.name}</h4>
        <p style="font-family: monospace; font-size: 1.1rem; margin: 5px 0; color: #3b2f1c;">
            🎯 Précision: {selected_hero.precision} • ⚔️ Dégâts: {selected_hero.damage} • ❤️ PV: {selected_hero.health}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Build actuel avec style
    current_build = get_hero_build(selected_hero, data['loader'])
    build_icon = "🔧" if current_build['is_custom'] else "📋"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(70,130,180,0.1), rgba(30,144,255,0.1));
        border: 2px solid #4682b4;
        border-radius: 10px;
        padding: 12px;
        margin: 10px 0;
    ">
        <p style="margin: 0; color: #2c5aa0; font-weight: bold;">
            {build_icon} Build actuel: {current_build['build_name']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Boutons gestion avec style - TAILLE FIXE
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 Reset Build", key="reset_build", use_container_width=True):
            if selected_code in st.session_state.custom_builds:
                del st.session_state.custom_builds[selected_code]
                st.rerun()
    with col2:
        if current_build['is_custom'] and st.button("🗑️ Supprimer", key="delete_build", use_container_width=True):
            del st.session_state.custom_builds[selected_code]
            st.rerun()
    
    # Sélection équipements avec style fantasy
    st.subheader("⚔️ Sélection d'Équipements")
    
    # Catégories CORRIGÉES - avec debug
    weapons = [eq for eq in equipment if eq.physical_damage > 0 or eq.magical_damage > 0]
    armor = [eq for eq in equipment if eq.defense > 0 and eq.physical_damage == 0 and eq.magical_damage == 0]
    accessories = [eq for eq in equipment if eq.precision > 0 or eq.spells > 0 or eq.health > 0]
    
    # DEBUG TEMPORAIRE - décommentez pour voir les catégories
    # st.write(f"DEBUG Armes: {[w.name for w in weapons]}")
    # st.write(f"DEBUG Armures: {[a.name for a in armor]}")  
    # st.write(f"DEBUG Accessoires: {[acc.name for acc in accessories]}")
    
    selected_eq = []
    
    # Layout horizontal ORIGINAL avec COMPACTAGE
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(220,20,60,0.1), rgba(139,0,0,0.1));
            border: 2px solid #dc143c;
            border-radius: 10px;
            padding: 15px;
            margin: 5px 0;
        ">
            <h4 style="color: #8b0000; margin: 0 0 10px 0; font-family: 'Cinzel', serif;">⚔️ Armes</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # COMPACTAGE - 2 colonnes pour les armes
        weapon_cols = st.columns(2)
        for i, weapon in enumerate(weapons):
            with weapon_cols[i % 2]:
                if st.checkbox(weapon.name[:15], key=f"w_{weapon.code}"):
                    selected_eq.append(weapon.code)
                st.caption(f"✨ {weapon.get_bonus_description()}")
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(70,130,180,0.1), rgba(25,25,112,0.1));
            border: 2px solid #4682b4;
            border-radius: 10px;
            padding: 15px;
            margin: 5px 0;
        ">
            <h4 style="color: #191970; margin: 0 0 10px 0; font-family: 'Cinzel', serif;">🛡️ Armures</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # COMPACTAGE - 2 colonnes pour les armures
        armor_cols = st.columns(2)
        for i, armor_item in enumerate(armor):
            with armor_cols[i % 2]:
                if st.checkbox(armor_item.name[:15], key=f"a_{armor_item.code}"):
                    selected_eq.append(armor_item.code)
                st.caption(f"✨ {armor_item.get_bonus_description()}")
    
    with col3:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(138,43,226,0.1), rgba(75,0,130,0.1));
            border: 2px solid #8a2be2;
            border-radius: 10px;
            padding: 15px;
            margin: 5px 0;
        ">
            <h4 style="color: #4b0082; margin: 0 0 10px 0; font-family: 'Cinzel', serif;">💍 Accessoires</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # COMPACTAGE - 2 colonnes pour les accessoires  
        acc_cols = st.columns(2)
        for i, acc in enumerate(accessories):
            with acc_cols[i % 2]:
                if st.checkbox(acc.name[:15], key=f"acc_{acc.code}"):
                    selected_eq.append(acc.code)
                st.caption(f"✨ {acc.get_bonus_description()}")
    
    # Aperçu et sauvegarde avec style
    if selected_eq:
        st.subheader("💾 Forge du Nouveau Build")
        
        # Preview stats avec style
        temp_hero = selected_hero.model_copy()
        temp_eq = [eq for eq in equipment if eq.code in selected_eq]
        temp_hero.equip_items(temp_eq, "Custom")
        temp_stats = temp_hero.get_stats_summary()['total']
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(34,139,34,0.15), rgba(0,100,0,0.15));
            border: 3px solid #228b22;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        ">
            <h4 style="color: #006400; margin: 0 0 10px 0; font-family: 'Cinzel', serif;">⚡ Nouvelles Statistiques</h4>
            <div style="font-family: monospace; font-size: 1.2rem; margin: 0; color: #2e8b57; font-weight: bold;">
                🎯 Précision: {temp_stats['precision']} • ⚔️ Dégâts: {temp_stats['damage']} • ❤️ PV: {temp_stats['health']}{"" if temp_stats['parade'] == 0 else f" • 🛡️ Parade: {temp_stats['parade']}"}{"" if temp_stats['spells'] == 0 else f" • ✨ Sorts: {temp_stats['spells']}"}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Nom custom avec style
        name = st.text_input("🏷️ Nom du Build:", placeholder="Ex: Paladin Destructeur, Mage de Guerre...")
        
        if st.button("💾 Forger ce Build", type="primary", use_container_width=True):
            st.session_state.custom_builds[selected_code] = {
                'equipment': selected_eq,
                'name': name.strip() if name.strip() else 'Build Forgé'
            }
            st.success("✅ Build forgé avec succès !")
            st.balloons()
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def tab_results(data):
    """Onglet résultats avec style fantasy"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.header("📜 Chroniques du Combat")
    
    if not st.session_state.get('run_simulation', False):
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(255,165,0,0.1), rgba(255,140,0,0.1));
            border: 2px solid #ffa500;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        ">
            <h3 style="color: #ff8c00; margin: 0; font-family: 'Cinzel', serif;">🏰 En Attente de Combat</h3>
            <p style="color: #b8860b; margin: 10px 0;">Configurez votre combat dans l'onglet Sélection</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    config = st.session_state['simulation_config']
    heroes = data['heroes']
    enemies = data['enemies']
    loader = data['loader']
    
    # Préparation équipes
    selected_heroes = []
    for code in config['hero_codes']:
        hero = next(h for h in heroes if h.code == code)
        build_info = get_hero_build(hero, loader)
        selected_heroes.append(build_info['hero_equipped'])
    
    selected_enemies = [e for e in enemies if e.code in config['enemy_codes']]
    
    # Simulation
    game_rules = GameRules(**config['rules'])
    engine = CombatEngine(game_rules)
    
    with st.spinner("⚔️ Combat épique en cours..."):
        result = engine.simulate_single_combat(selected_heroes, selected_enemies, config['player_count'])
    
    # Affichage résultat avec style fantasy épique
    if result['winner'] == 'heroes':
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(34,139,34,0.2), rgba(0,100,0,0.2));
            border: 4px solid #228b22;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin: 20px 0;
            box-shadow: 0 8px 16px rgba(34,139,34,0.3);
        ">
            <h1 style="color: #006400; margin: 0; font-family: 'Cinzel', serif; font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                🏆 VICTOIRE HÉROÏQUE ! 🏆
            </h1>
            <p style="color: #2e8b57; font-size: 1.2rem; margin: 10px 0;">Les héros triomphent dans un combat légendaire !</p>
        </div>
        """, unsafe_allow_html=True)
    elif result['winner'] == 'enemies':
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(220,20,60,0.2), rgba(139,0,0,0.2));
            border: 4px solid #dc143c;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin: 20px 0;
            box-shadow: 0 8px 16px rgba(220,20,60,0.3);
        ">
            <h1 style="color: #8b0000; margin: 0; font-family: 'Cinzel', serif; font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                💀 DÉFAITE TRAGIQUE 💀
            </h1>
            <p style="color: #b22222; font-size: 1.2rem; margin: 10px 0;">Les ténèbres ont vaincu nos héros...</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(255,165,0,0.2), rgba(255,140,0,0.2));
            border: 4px solid #ffa500;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin: 20px 0;
            box-shadow: 0 8px 16px rgba(255,165,0,0.3);
        ">
            <h1 style="color: #ff8c00; margin: 0; font-family: 'Cinzel', serif; font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                ⚔️ COMBAT INDÉCIS ⚔️
            </h1>
            <p style="color: #b8860b; font-size: 1.2rem; margin: 10px 0;">Un affrontement épique sans vainqueur !</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Métriques ressources avec style fantasy
    if 'resource_metrics' in result:
        st.subheader("📊 Bilan des Ressources")
        
        # Container principal pour métriques
        resource_metrics = result['resource_metrics']
        
        # Métriques globales avec style
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background: rgba(220,20,60,0.1); border-radius: 10px; border: 2px solid #dc143c;">
                <h3 style="color: #8b0000; margin: 0; font-family: 'Cinzel', serif;">💔 Blessures</h3>
                <p style="font-size: 2rem; font-weight: bold; color: #b22222; margin: 5px 0;">{resource_metrics['total_damage_taken']}</p>
                <p style="color: #8b0000; margin: 0; font-size: 0.9rem;">Total infligé</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background: rgba(138,43,226,0.1); border-radius: 10px; border: 2px solid #8a2be2;">
                <h3 style="color: #4b0082; margin: 0; font-family: 'Cinzel', serif;">✨ Sorts</h3>
                <p style="font-size: 2rem; font-weight: bold; color: #663399; margin: 5px 0;">{resource_metrics['total_spells_used']}</p>
                <p style="color: #4b0082; margin: 0; font-size: 0.9rem;">Utilisés</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background: rgba(255,165,0,0.1); border-radius: 10px; border: 2px solid #ffa500;">
                <h3 style="color: #ff8c00; margin: 0; font-family: 'Cinzel', serif;">📈 Moyenne</h3>
                <p style="font-size: 2rem; font-weight: bold; color: #b8860b; margin: 5px 0;">{resource_metrics['average_damage_per_hero']}</p>
                <p style="color: #ff8c00; margin: 0; font-size: 0.9rem;">Blessures/héros</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Tableau détaillé par héros avec style
        st.markdown("#### 🎯 Bilan Individuel des Héros")
        heroes_metrics = []
        for hero_data in resource_metrics['heroes_individual']:
            blessures = hero_data['damage_taken']
            
            # Évaluation difficulté avec style
            if blessures == 0:
                difficulty = "😊 Très facile"
                diff_color = "#28a745"
            elif blessures <= 2:
                difficulty = "🙂 Normal"
                diff_color = "#17a2b8"
            elif blessures <= 4:
                difficulty = "😰 Difficile"
                diff_color = "#ffc107"
            else:
                difficulty = "😵 Trop difficile"
                diff_color = "#dc3545"
            
            heroes_metrics.append({
                "Héros": f"{get_hero_icon(hero_data['name'])} {hero_data['name']} ({hero_data['build']})",
                "Blessures": f"{blessures}",
                "Difficulté": difficulty,
                "PV Restants": f"{hero_data['health_remaining']} ({hero_data['health_percentage']}%)",
                "Sorts Utilisés": hero_data['spells_used'],
                "Statut": "🟢 Vivant" if hero_data['is_alive'] else "💀 KO"
            })
        
        if heroes_metrics:
            import pandas as pd
            df_metrics = pd.DataFrame(heroes_metrics)
            st.dataframe(df_metrics, use_container_width=True, hide_index=True)
    
    # Log de combat avec style parchemin
    st.subheader("📜 Parchemin de Combat Détaillé")
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(139,69,19,0.1), rgba(160,82,45,0.1));
        border: 3px solid #8b4513;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: inset 0 0 20px rgba(139,69,19,0.1);
    ">
        <h4 style="color: #654321; margin: 0 0 15px 0; font-family: 'Cinzel', serif;">
            💡 Cœur du Projet : Analyse Tactique Round par Round
        </h4>
    """, unsafe_allow_html=True)
    
    # Traitement du log pour style fantasy
    log_lines = result['log']
    formatted_log = []
    
    for line in log_lines:
        # Coloration selon type de ligne avec style fantasy
        if "Round" in line and "---" in line:
            formatted_log.append(f"<div style='color: #8b4513; font-weight: bold; font-size: 18px; margin: 15px 0; font-family: \"Cinzel\", serif; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>{line}</div>")
        elif "Phase des Héros" in line:
            formatted_log.append(f"<div style='color: #228b22; font-weight: bold; margin: 10px 0; padding: 8px; background: rgba(34,139,34,0.1); border-radius: 5px; border-left: 4px solid #228b22;'>🛡️ {line}</div>")
        elif "Phase des Ennemis" in line:
            formatted_log.append(f"<div style='color: #dc143c; font-weight: bold; margin: 10px 0; padding: 8px; background: rgba(220,20,60,0.1); border-radius: 5px; border-left: 4px solid #dc143c;'>👹 {line}</div>")
        elif "VICTOIRE" in line or "🏆" in line:
            formatted_log.append(f"<div style='color: #006400; font-weight: bold; font-size: 20px; margin: 15px 0; padding: 12px; background: rgba(34,139,34,0.2); border-radius: 8px; text-align: center; box-shadow: 0 4px 8px rgba(34,139,34,0.2);'>{line}</div>")
        elif "DÉFAITE" in line or "💀" in line:
            formatted_log.append(f"<div style='color: #8b0000; font-weight: bold; font-size: 20px; margin: 15px 0; padding: 12px; background: rgba(139,0,0,0.2); border-radius: 8px; text-align: center; box-shadow: 0 4px 8px rgba(139,0,0,0.2);'>{line}</div>")
        elif "CRITIQUE" in line or "⚡" in line:
            formatted_log.append(f"<div style='color: #ff8c00; font-weight: bold; background: linear-gradient(135deg, rgba(255,215,0,0.2), rgba(255,140,0,0.2)); padding: 8px 12px; border-radius: 8px; margin: 8px 0; border: 2px solid #ffd700; box-shadow: 0 2px 4px rgba(255,215,0,0.3);'>{line}</div>")
        elif "vaincu" in line or "tombe" in line:
            formatted_log.append(f"<div style='color: #8b0000; font-style: italic; margin: 5px 0; padding: 5px 10px; background: rgba(139,0,0,0.05); border-radius: 4px;'>💀 {line}</div>")
        elif "attaque" in line:
            formatted_log.append(f"<div style='color: #654321; margin: 3px 0; padding: 3px 8px; background: rgba(139,69,19,0.05); border-radius: 3px;'>⚔️ {line}</div>")
        else:
            formatted_log.append(f"<div style='color: #3b2f1c; margin: 2px 0; padding: 2px 5px;'>{line}</div>")
    
    # Affichage du log formaté avec scroll style parchemin
    log_html = "<div style='max-height: 500px; overflow-y: auto; padding: 15px; background: rgba(244,228,188,0.3); border-radius: 10px; border: 1px solid rgba(139,69,19,0.2); font-family: monospace;'>"
    log_html += "".join(formatted_log)
    log_html += "</div>"
    
    st.markdown(log_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Actions avec style
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎲 Rejouer le Combat", type="primary", use_container_width=True):
            st.session_state['run_simulation'] = True
            st.rerun()
    with col2:
        if st.button("📋 Copier le Parchemin", type="secondary", use_container_width=True):
            # Reconstitution du log text pour copie
            log_text = "\n".join(result['log'])
            st.code(log_text, language="text")
    
    # Reset flag
    st.session_state['run_simulation'] = False
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Application principale avec thème fantasy"""
    # Initialisation
    init_app()
    
    # Application du thème fantasy
    apply_fantasy_theme()
    
    # Titre principal avec style
    st.markdown("""
    <h1 style="
        text-align: center;
        font-family: 'Cinzel', serif;
        color: #8b4513;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
        font-size: 3rem;
    ">
        ⚔️ Simulateur des Périples ⚔️
    </h1>
    <p style="
        text-align: center;
        font-style: italic;
        color: #6f4f27;
        margin-bottom: 2rem;
        font-size: 1.2rem;
    ">
        Outil d'équilibrage RPG dans l'univers fantasy
    </p>
    """, unsafe_allow_html=True)
    
    # Chargement données
    try:
        data = load_data()
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
        st.stop()
    
    # Interface onglets
    tab1, tab2, tab3 = st.tabs(["🏰 Sélection", "⚙️ Forge", "📜 Chroniques"])
    
    with tab1:
        tab_selection(data)
    with tab2:
        tab_customization(data)
    with tab3:
        tab_results(data)

if __name__ == "__main__":
    main()