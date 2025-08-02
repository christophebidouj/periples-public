import streamlit as st
import time
import os
from typing import List, Dict
from models.character import Character, Enemy
from models.combat_engine import CombatEngine
from models.rules_engine import GameRules
from utils.data_loader import DataLoader

# === CONFIGURATION ===
ENABLE_IMAGES = True

# === CACHE ET UTILITAIRES ===
@st.cache_data
def load_hero_image_base64(image_path: str) -> str:
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        import base64
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

@st.cache_data(persist=True)
def get_cached_build_info(hero_code: str, _loader) -> Dict:
    hero_list = _loader.load_heroes()
    hero = next(h for h in hero_list if h.code == hero_code)
    return get_hero_build(hero, _loader)

def get_hero_image_path(hero_name: str) -> str:
    hero_files = {
        "Atucan": "Atucan_-_Paladin.png", "Elneha": "Elneha_-_Druidesse.png",
        "Kraor": "Kraor_-_Rodeur.png", "Lame": "Lame_-_Roublarde.png",
        "Liarie": "Liarie_-_Mage.png", "Raishi": "Raishi_-_Pugiliste.png",
        "Stèphe": "Stèphe_-_Barde.png", "Thordius": "Thordius_-_Barbare.png"
    }
    filename = hero_files.get(hero_name)
    if filename:
        path = f"data/images/{filename}"
        return path if os.path.exists(path) else None
    return None

def get_hero_icon(name: str) -> str:
    icons = {"Elneha": "🐻", "Liarie": "🔮", "Atucan": "🛡️", "Kraor": "⚔️",
             "Thordius": "🪓", "Stèphe": "🎭", "Lame": "🗡️", "Raishi": "🏹"}
    return icons.get(name, "⚔️")

def get_equipment_categories(equipment):
    """Catégorise les équipements selon leur type Excel - CORRIGÉ"""
    weapons, armor, accessories = [], [], []
    for eq in equipment:
        eq_type = eq.type.lower().strip() if hasattr(eq, 'type') and eq.type else 'accessoire'
        if eq_type == 'arme':
            weapons.append(eq)
        elif eq_type == 'armure':
            armor.append(eq)
        else:
            accessories.append(eq)
    return weapons, armor, accessories

# === FONCTIONS PRINCIPALES ===
def init_app():
    st.set_page_config(page_title="Simulateur RPG", page_icon="⚔️", layout="wide")
    if not os.path.exists("data"):
        os.makedirs("data")
    if 'selected_heroes' not in st.session_state:
        st.session_state.selected_heroes = []
    if 'selected_enemies' not in st.session_state:
        st.session_state.selected_enemies = []
    if 'custom_builds' not in st.session_state:
        st.session_state.custom_builds = {}

@st.cache_data
def load_data():
    loader = DataLoader()
    missing_files = [f for f in ["heroes.csv", "enemies.csv", "equipment.csv"] 
                     if not os.path.exists(f"data/{f}")]
    if missing_files:
        st.info("🔄 Création fichiers données...")
        loader.create_csv_files()
        st.success("✅ Fichiers créés !")
        time.sleep(1)
        st.rerun()
    return {'heroes': loader.load_heroes(), 'enemies': loader.load_enemies(), 
            'equipment': loader.load_equipment(), 'loader': loader}

def apply_fantasy_theme():
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
    </style>
    """, unsafe_allow_html=True)

def get_hero_build(hero: Character, loader: DataLoader) -> Dict:
    if hero.code in st.session_state.custom_builds:
        custom_data = st.session_state.custom_builds[hero.code]
        equipment_codes = custom_data.get('equipment', [])
        all_equipment = loader.load_equipment()
        hero_equipment = [eq for eq in all_equipment if eq.code in equipment_codes]
        build_name = custom_data.get('name', 'Build Custom')
        is_custom = True
    else:
        hero_equipment = loader.get_hero_loadout(hero.code)
        build_name = "Build Standard"
        is_custom = False
    
    hero_copy = hero.model_copy()
    hero_copy.equip_items(hero_equipment, build_name)
    return {'hero_equipped': hero_copy, 'equipment': hero_equipment,
            'build_name': build_name, 'is_custom': is_custom, 'stats': hero_copy.get_stats_summary()}

def display_hero_card(hero: Character, build_info: Dict, is_selected: bool):
    stats = build_info['stats']['total']
    hero_icon = get_hero_icon(hero.name)
    
    if is_selected:
        border_color, button_text, button_type = "#4a90e2", "✅ Sélectionné", "secondary"
    else:
        border_color, button_text, button_type = "#5a9f5a", "➕ Ajouter", "primary"
    
    # Image background
    background_style = ""
    if ENABLE_IMAGES:
        image_path = get_hero_image_path(hero.name)
        if image_path:
            img_base64 = load_hero_image_base64(image_path)
            if img_base64:
                background_style = f"background-image: url('data:image/png;base64,{img_base64}');"
    if not background_style:
        background_style = f"background: linear-gradient(135deg, {border_color}33, {border_color}11);"
    
    # Stats bonus
    bonus_parts = []
    if stats["parade"] > 0:
        bonus_parts.append(f"🛡️{stats['parade']}")
    if stats["spells"] > 0:
        bonus_parts.append(f"✨{stats['spells']}")
    bonus_text = f" • {' • '.join(bonus_parts)}" if bonus_parts else ""
    
    with st.container():
        st.markdown(f"""
        <div style="width: 260px; height: 370px; border-radius: 15px; overflow: hidden;
                    box-shadow: 0 6px 12px rgba(0,0,0,0.3); border: 3px solid {border_color};
                    {background_style} background-size: cover; background-position: center top;
                    display: flex; flex-direction: column; justify-content: flex-end; color: white; margin: 10px auto;">
            <div style="background: linear-gradient(to top, rgba(0, 0, 0, 0.85), transparent 70%); padding: 15px;">
                <div style="background: rgba(0,0,0,0.6); border-radius: 5px; padding: 4px 8px; margin: 0 0 10px 0; text-align: center; display: inline-block;">
                    <strong style="font-size: 18px; color: yellow; text-shadow: 2px 2px black;">{hero.name}</strong>
                </div>
                <div style="font-family: monospace; font-size: 1rem; margin-bottom: 5px; font-weight: bold; color: #f0f0f0;">
                    🎯{stats["precision"]} • ⚔️{stats["damage"]} • ❤️{stats["health"]}{bonus_text}
                </div>
                <div style="font-size: 0.9rem; font-style: italic; color: #e0e0e0;">
                    {build_info["build_name"][:25]}{"..." if len(build_info["build_name"]) > 25 else ""}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(button_text, key=f"hero_btn_{hero.code}_{is_selected}", type=button_type, use_container_width=True):
            if is_selected:
                st.session_state.selected_heroes.remove(hero.code)
            else:
                st.session_state.selected_heroes.append(hero.code)
            st.rerun()

def display_enemy_card(enemy: Enemy, is_selected: bool, player_count: int):
    stats = enemy.get_stats_for_players(player_count)
    number = enemy.code.split('-')[-1] if '-' in enemy.code else enemy.code
    magic = " ✨" if enemy.is_magical else ""
    
    if is_selected:
        border_color, bg_color, text_color = "#dc3545", "#fff5f5", "#333"
        button_text, button_type = "✅ Sélectionné", "secondary"
    else:
        border_color, bg_color, text_color = "#8b0000", "#2c1810", "#fff"
        button_text, button_type = "➕ Ajouter", "primary"
    
    with st.container():
        st.markdown(f"""
        <div style="border: 3px solid {border_color}; border-radius: 12px; padding: 15px;
                    background-color: {bg_color}; margin: 8px 0; text-align: center; color: {text_color};">
            <h3 style="color: {border_color}; margin: 0 0 8px 0;">👹 #{number}{magic}</h3>
            <div style="margin: 8px 0;">{enemy.name}</div>
            <div style="font-family: monospace; font-weight: bold;">
                ❤️{stats["health"]} • ⚔️{stats["damage"]} • 🛡️{enemy.defense}
            </div>
            <div style="font-style: italic; color: {'#888' if is_selected else '#ffa500'}; margin: 5px 0;">
                {'Magique' if enemy.is_magical else 'Physique'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(button_text, key=f"enemy_{enemy.code}", type=button_type, use_container_width=True):
            if is_selected:
                st.session_state.selected_enemies.remove(enemy.code)
            else:
                st.session_state.selected_enemies.append(enemy.code)
            st.rerun()

def tab_selection(data):
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.header("🏰 Sélection des Équipes")
    
    heroes, enemies, loader = data['heroes'], data['enemies'], data['loader']
    nb_heroes, nb_enemies = len(st.session_state.selected_heroes), len(st.session_state.selected_enemies)
    
    # Indicateur progression
    if nb_heroes < 2:
        st.warning(f"🎯 Sélectionnez au moins 2 héros ({nb_heroes}/2)")
    elif nb_enemies == 0:
        st.info("🎯 Maintenant sélectionnez vos ennemis")
    else:
        st.success(f"🎯 Prêt ! {nb_heroes} héros et {nb_enemies} ennemis")
    
    # HÉROS
    st.subheader("🛡️ Héros Disponibles")
    st.markdown("*📋 = Standard • 🔧 = Personnalisé*")
    cols = st.columns(4)
    for i, hero in enumerate(heroes):
        build_info = get_cached_build_info(hero.code, loader)
        is_selected = hero.code in st.session_state.selected_heroes
        with cols[i % 4]:
            display_hero_card(hero, build_info, is_selected)
    
    # ENNEMIS
    st.subheader("👹 Ennemis")
    player_count = max(2, nb_heroes) if nb_heroes >= 2 else 2
    if nb_heroes >= 2:
        st.info(f"🎯 Mode {player_count} joueurs (auto)")
    
    search = st.text_input("🔍 Recherche:", placeholder="Ex: 34, Dragon...")
    if search.strip():
        term = search.strip().lower()
        filtered = [e for e in enemies if term in e.code.split('-')[-1].lower() or term in e.name.lower()]
    else:
        filtered = enemies[:15]
        st.info("💡 Tapez un numéro ou nom pour chercher")
    
    if filtered:
        st.write(f"**{len(filtered)} ennemis trouvés:**")
        cols = st.columns(5)
        for i, enemy in enumerate(filtered):
            is_selected = enemy.code in st.session_state.selected_enemies
            with cols[i % 5]:
                display_enemy_card(enemy, is_selected, player_count)
    
    # RÉCAPITULATIF ÉLÉGANT DES ÉQUIPES - ESSENTIEL AU PROJET
    if nb_heroes >= 2 and nb_enemies > 0:
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(139,69,19,0.08), rgba(160,82,45,0.08));
                    border: 2px solid rgba(139,69,19,0.3); border-radius: 20px; padding: 25px; margin: 20px 0;">
            <h3 style="text-align: center; color: #8b4513; font-family: 'Cinzel', serif; margin-bottom: 20px;">
                ⚔️ FORMATION DE GUERRE ⚔️
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Récupération des détails des héros
        selected_hero_details = []
        for code in st.session_state.selected_heroes:
            hero = next(h for h in heroes if h.code == code)
            build_info = get_cached_build_info(code, loader)
            stats = build_info['stats']['total']
            
            selected_hero_details.append({
                'name': hero.name,
                'icon': get_hero_icon(hero.name),
                'build': build_info['build_name'],
                'is_custom': build_info['is_custom'],
                'precision': stats['precision'],
                'damage': stats['damage'],
                'health': stats['health'],
                'parade': stats['parade'],
                'spells': stats['spells']
            })
        
        # Récupération des détails des ennemis
        selected_enemy_details = []
        for code in st.session_state.selected_enemies:
            enemy = next(e for e in enemies if e.code == code)
            number = enemy.code.split('-')[-1] if '-' in enemy.code else enemy.code
            stats = enemy.get_stats_for_players(player_count)
            
            selected_enemy_details.append({
                'name': enemy.name,
                'number': number,
                'is_magical': enemy.is_magical,
                'health': stats['health'],
                'damage': stats['damage'],
                'defense': enemy.defense
            })
        
        # Affichage côte à côte
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(34,139,34,0.12), rgba(0,100,0,0.08));
                        border: 3px solid #228b22; border-radius: 15px; padding: 20px; margin: 10px;">
                <h4 style="color: #006400; text-align: center; font-family: 'Cinzel', serif; margin-bottom: 15px;">
                    🛡️ TEAM HEROS
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            for hero in selected_hero_details:
                build_badge = "🔧 Custom" if hero['is_custom'] else "📋 Standard"
                bonus_info = []
                if hero['parade'] > 0:
                    bonus_info.append(f"🛡️{hero['parade']}")
                if hero['spells'] > 0:
                    bonus_info.append(f"✨{hero['spells']}")
                bonus_text = f" • {' • '.join(bonus_info)}" if bonus_info else ""
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.7); border-radius: 10px; padding: 15px; margin: 8px 0;
                            border-left: 4px solid #228b22; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: #006400; font-size: 1.1rem;">{hero['icon']} {hero['name']}</strong>
                            <div style="font-size: 0.85rem; color: #666; font-style: italic;">{build_badge}</div>
                        </div>
                        <div style="text-align: right; font-family: monospace; font-size: 0.9rem; color: #2e8b57;">
                            🎯{hero['precision']} ⚔️{hero['damage']} ❤️{hero['health']}{bonus_text}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(139,0,0,0.12), rgba(220,20,60,0.08));
                        border: 3px solid #8b0000; border-radius: 15px; padding: 20px; margin: 10px;">
                <h4 style="color: #8b0000; text-align: center; font-family: 'Cinzel', serif; margin-bottom: 15px;">
                    👹 TEAM MONSTRES
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            for enemy in selected_enemy_details:
                magic_badge = "✨ Magique" if enemy['is_magical'] else "⚔️ Physique"
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.7); border-radius: 10px; padding: 15px; margin: 8px 0;
                            border-left: 4px solid #8b0000; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: #8b0000; font-size: 1.1rem;">👹 #{enemy['number']} {enemy['name'][:18]}</strong>
                            <div style="font-size: 0.85rem; color: #666; font-style: italic;">{magic_badge}</div>
                        </div>
                        <div style="text-align: right; font-family: monospace; font-size: 0.9rem; color: #b22222;">
                            ❤️{enemy['health']} ⚔️{enemy['damage']} 🛡️{enemy['defense']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Statistiques de bataille
        total_hero_health = sum(h['health'] for h in selected_hero_details)
        total_enemy_health = sum(e['health'] for e in selected_enemy_details)
        avg_hero_damage = sum(h['damage'] for h in selected_hero_details) / len(selected_hero_details)
        avg_enemy_damage = sum(e['damage'] for e in selected_enemy_details) / len(selected_enemy_details)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(212,175,55,0.1), rgba(255,215,0,0.1));
                    border: 2px solid #d4af37; border-radius: 12px; padding: 15px; margin: 15px 0; text-align: center;">
            <h5 style="color: #8b4513; margin: 0 0 10px 0; font-family: 'Cinzel', serif;">📊 PRONOSTIC DE BATAILLE</h5>
            <div style="display: flex; justify-content: space-around; font-weight: bold;">
                <div style="color: #006400;">
                    💚 Héros: {total_hero_health} PV • {avg_hero_damage:.1f} DPS
                </div>
                <div style="color: #8b0000;">
                    ❤️ Ennemis: {total_enemy_health} PV • {avg_enemy_damage:.1f} DPS
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Configuration et lancement
    st.subheader("⚙️ Configuration de Bataille")
    col1, col2 = st.columns(2)
    with col1:
        rules = {'ranged_attacks': True, 'magical_damage': True,
                'criticals': st.checkbox("🎯 Critiques", help="Échecs/Réussites critiques sur 1 et 20"),
                'initiative': st.checkbox("🎲 Initiative", help="Ordre de jeu aléatoire")}
        st.caption("🏹 Attaques distance et ✨ Dégâts magiques : activés automatiquement")
    with col2:
        st.info("⚔️ Combat détaillé avec journal complet des actions")
    
    # Bouton de lancement stylisé
    ready = nb_heroes >= 2 and nb_enemies > 0
    
    if ready:
        st.markdown("""
        <div style="text-align: center; margin: 25px 0;">
            <div style="background: linear-gradient(135deg, #ff6b35, #f7931e); 
                        border-radius: 50px; padding: 3px; display: inline-block;
                        box-shadow: 0 8px 25px rgba(255,107,53,0.4);">
        """, unsafe_allow_html=True)
        
        if st.button("⚔️ ENGAGER LE COMBAT ! ⚔️", type="primary", use_container_width=True,
                    help="Lancer la simulation de combat épique"):
            st.session_state['run_simulation'] = True
            st.session_state['simulation_config'] = {
                'hero_codes': st.session_state.selected_heroes,
                'enemy_codes': st.session_state.selected_enemies,
                'player_count': player_count, 'rules': rules
            }
            st.success("⚡ Combat engagé ! Consultez l'onglet Chroniques pour voir l'épopée !")
            st.balloons()
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; margin: 25px 0;">
            <div style="background: linear-gradient(135deg, #cccccc, #999999); 
                        border-radius: 50px; padding: 3px; display: inline-block; opacity: 0.6;">
        """, unsafe_allow_html=True)
        
        st.button("⚔️ FORMATION INCOMPLÈTE", disabled=True, use_container_width=True,
                 help="Sélectionnez au moins 2 héros et 1 ennemi")
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def tab_customization(data):
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.header("⚙️ Forge des Équipements")
    
    heroes, equipment = data['heroes'], data['equipment']
    
    # Sélection héros
    hero_options = {h.code: f"{get_hero_icon(h.name)} {h.name}" for h in heroes}
    selected_code = st.selectbox("Choisir un héros:", list(hero_options.keys()), 
                                format_func=lambda x: hero_options[x])
    selected_hero = next(h for h in heroes if h.code == selected_code)
    
    # Stats base
    st.subheader("📊 Statistiques de Base")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(212,175,55,0.1), rgba(139,69,19,0.1));
                border: 2px solid #d4af37; border-radius: 10px; padding: 15px; margin: 10px 0;">
        <h4 style="color: #8b4513; margin: 0;">{get_hero_icon(selected_hero.name)} {selected_hero.name}</h4>
        <p style="font-family: monospace; font-size: 1.1rem; margin: 5px 0; color: #3b2f1c;">
            🎯 Précision: {selected_hero.precision} • ⚔️ Dégâts: {selected_hero.damage} • ❤️ PV: {selected_hero.health}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Build actuel
    current_build = get_hero_build(selected_hero, data['loader'])
    build_icon = "🔧" if current_build['is_custom'] else "📋"
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(70,130,180,0.1), rgba(30,144,255,0.1));
                border: 2px solid #4682b4; border-radius: 10px; padding: 12px; margin: 10px 0;">
        <p style="margin: 0; color: #2c5aa0; font-weight: bold;">
            {build_icon} Build actuel: {current_build['build_name']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Boutons gestion
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
    
    # Sélection équipements
    st.subheader("⚔️ Sélection d'Équipements")
    weapons, armor, accessories = get_equipment_categories(equipment)
    selected_eq = []
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### ⚔️ Armes")
        for weapon in weapons:
            if st.checkbox(weapon.name, key=f"w_{weapon.code}"):
                selected_eq.append(weapon.code)
            st.caption(f"✨ {weapon.get_bonus_description()}")
    
    with col2:
        st.markdown("#### 🛡️ Armures")
        for armor_item in armor:
            if st.checkbox(armor_item.name, key=f"a_{armor_item.code}"):
                selected_eq.append(armor_item.code)
            st.caption(f"✨ {armor_item.get_bonus_description()}")
    
    with col3:
        st.markdown("#### 💍 Accessoires")
        for acc in accessories:
            if st.checkbox(acc.name, key=f"acc_{acc.code}"):
                selected_eq.append(acc.code)
            st.caption(f"✨ {acc.get_bonus_description()}")
    
    # Aperçu et sauvegarde
    if selected_eq:
        st.subheader("💾 Forge du Nouveau Build")
        temp_hero = selected_hero.model_copy()
        temp_eq = [eq for eq in equipment if eq.code in selected_eq]
        temp_hero.equip_items(temp_eq, "Custom")
        temp_stats = temp_hero.get_stats_summary()['total']
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(34,139,34,0.15), rgba(0,100,0,0.15));
                    border: 3px solid #228b22; border-radius: 12px; padding: 20px; margin: 15px 0;">
            <h4 style="color: #006400; margin: 0 0 10px 0;">⚡ Nouvelles Statistiques</h4>
            <div style="font-family: monospace; font-size: 1.2rem; margin: 0; color: #2e8b57; font-weight: bold;">
                🎯 Précision: {temp_stats['precision']} • ⚔️ Dégâts: {temp_stats['damage']} • ❤️ PV: {temp_stats['health']}
                {"" if temp_stats['parade'] == 0 else f" • 🛡️ Parade: {temp_stats['parade']}"}
                {"" if temp_stats['spells'] == 0 else f" • ✨ Sorts: {temp_stats['spells']}"}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("🏷️ Nom du Build:", placeholder="Ex: Paladin Destructeur...")
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
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.header("📜 Chroniques du Combat")
    
    if not st.session_state.get('run_simulation', False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255,165,0,0.1), rgba(255,140,0,0.1));
                    border: 2px solid #ffa500; border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0;">
            <h3 style="color: #ff8c00; margin: 0;">🏰 En Attente de Combat</h3>
            <p style="color: #b8860b; margin: 10px 0;">Configurez votre combat dans l'onglet Sélection</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    config = st.session_state['simulation_config']
    heroes, enemies, loader = data['heroes'], data['enemies'], data['loader']
    
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
    
    # Affichage résultat
    if result['winner'] == 'heroes':
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(34,139,34,0.2), rgba(0,100,0,0.2));
                    border: 4px solid #228b22; border-radius: 15px; padding: 30px; text-align: center; margin: 20px 0;">
            <h1 style="color: #006400; margin: 0; font-family: 'Cinzel', serif; font-size: 2.5rem;">
                🏆 VICTOIRE HÉROÏQUE ! 🏆
            </h1>
        </div>
        """, unsafe_allow_html=True)
    elif result['winner'] == 'enemies':
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(220,20,60,0.2), rgba(139,0,0,0.2));
                    border: 4px solid #dc143c; border-radius: 15px; padding: 30px; text-align: center; margin: 20px 0;">
            <h1 style="color: #8b0000; margin: 0; font-family: 'Cinzel', serif; font-size: 2.5rem;">
                💀 DÉFAITE TRAGIQUE 💀
            </h1>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255,165,0,0.2), rgba(255,140,0,0.2));
                    border: 4px solid #ffa500; border-radius: 15px; padding: 30px; text-align: center; margin: 20px 0;">
            <h1 style="color: #ff8c00; margin: 0; font-family: 'Cinzel', serif; font-size: 2.5rem;">
                ⚔️ COMBAT INDÉCIS ⚔️
            </h1>
        </div>
        """, unsafe_allow_html=True)
    
    # Métriques ressources
    if 'resource_metrics' in result:
        st.subheader("📊 Bilan des Ressources")
        resource_metrics = result['resource_metrics']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background: rgba(220,20,60,0.1); border-radius: 10px; border: 2px solid #dc143c;">
                <h3 style="color: #8b0000; margin: 0;">💔 Blessures</h3>
                <p style="font-size: 2rem; font-weight: bold; color: #b22222; margin: 5px 0;">{resource_metrics['total_damage_taken']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background: rgba(138,43,226,0.1); border-radius: 10px; border: 2px solid #8a2be2;">
                <h3 style="color: #4b0082; margin: 0;">✨ Sorts</h3>
                <p style="font-size: 2rem; font-weight: bold; color: #663399; margin: 5px 0;">{resource_metrics['total_spells_used']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background: rgba(255,165,0,0.1); border-radius: 10px; border: 2px solid #ffa500;">
                <h3 style="color: #ff8c00; margin: 0;">📈 Moyenne</h3>
                <p style="font-size: 2rem; font-weight: bold; color: #b8860b; margin: 5px 0;">{resource_metrics['average_damage_per_hero']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Tableau héros
        st.markdown("#### 🎯 Bilan Individuel")
        heroes_metrics = []
        for hero_data in resource_metrics['heroes_individual']:
            blessures = hero_data['damage_taken']
            if blessures == 0:
                difficulty = "😊 Très facile"
            elif blessures <= 2:
                difficulty = "🙂 Normal"
            elif blessures <= 4:
                difficulty = "😰 Difficile"
            else:
                difficulty = "😵 Trop difficile"
            
            heroes_metrics.append({
                "Héros": f"{get_hero_icon(hero_data['name'])} {hero_data['name']} ({hero_data['build']})",
                "Blessures": f"{blessures}",
                "Difficulté": difficulty,
                "PV Restants": f"{hero_data['health_remaining']} ({hero_data['health_percentage']}%)",
                "Sorts": hero_data['spells_used'],
                "Statut": "🟢 Vivant" if hero_data['is_alive'] else "💀 KO"
            })
        
        if heroes_metrics:
            import pandas as pd
            df_metrics = pd.DataFrame(heroes_metrics)
            st.dataframe(df_metrics, use_container_width=True, hide_index=True)
    
    # Log de combat
    st.subheader("📜 Journal de Combat")
    log_lines = result['log']
    formatted_log = []
    
    for line in log_lines:
        if "Round" in line and "---" in line:
            formatted_log.append(f"<div style='color: #8b4513; font-weight: bold; font-size: 18px; margin: 15px 0;'>{line}</div>")
        elif "Phase des Héros" in line:
            formatted_log.append(f"<div style='color: #228b22; font-weight: bold; margin: 10px 0; padding: 8px; background: rgba(34,139,34,0.1); border-radius: 5px;'>🛡️ {line}</div>")
        elif "Phase des Ennemis" in line:
            formatted_log.append(f"<div style='color: #dc143c; font-weight: bold; margin: 10px 0; padding: 8px; background: rgba(220,20,60,0.1); border-radius: 5px;'>👹 {line}</div>")
        elif "VICTOIRE" in line or "🏆" in line:
            formatted_log.append(f"<div style='color: #006400; font-weight: bold; font-size: 20px; margin: 15px 0; padding: 12px; background: rgba(34,139,34,0.2); border-radius: 8px; text-align: center;'>{line}</div>")
        elif "DÉFAITE" in line or "💀" in line:
            formatted_log.append(f"<div style='color: #8b0000; font-weight: bold; font-size: 20px; margin: 15px 0; padding: 12px; background: rgba(139,0,0,0.2); border-radius: 8px; text-align: center;'>{line}</div>")
        elif "CRITIQUE" in line or "⚡" in line:
            formatted_log.append(f"<div style='color: #ff8c00; font-weight: bold; background: rgba(255,215,0,0.2); padding: 8px; border-radius: 8px; margin: 8px 0;'>{line}</div>")
        else:
            formatted_log.append(f"<div style='color: #3b2f1c; margin: 2px 0;'>{line}</div>")
    
    log_html = "<div style='max-height: 500px; overflow-y: auto; padding: 15px; background: rgba(244,228,188,0.3); border-radius: 10px; font-family: monospace;'>"
    log_html += "".join(formatted_log)
    log_html += "</div>"
    st.markdown(log_html, unsafe_allow_html=True)
    
    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎲 Rejouer le Combat", type="primary", use_container_width=True):
            st.session_state['run_simulation'] = True
            st.rerun()
    with col2:
        if st.button("📋 Copier le Journal", type="secondary", use_container_width=True):
            log_text = "\n".join(result['log'])
            st.code(log_text, language="text")
    
    st.session_state['run_simulation'] = False
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    init_app()
    apply_fantasy_theme()
    
    st.markdown("""
    <h1 style="text-align: center; font-family: 'Cinzel', serif; color: #8b4513; font-size: 3rem; margin-bottom: 2rem;">
        ⚔️ Simulateur Périples ⚔️
    </h1>
    <p style="text-align: center; font-style: italic; color: #6f4f27; margin-bottom: 2rem; font-size: 1.2rem;">
        Outil d'équilibrage RPG dans l'univers fantasy
    </p>
    """, unsafe_allow_html=True)
    
    try:
        data = load_data()
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
        st.stop()
    
    tab1, tab2, tab3 = st.tabs(["🏰 Sélection", "⚙️ Forge", "📜 Chroniques"])
    
    with tab1:
        tab_selection(data)
    with tab2:
        tab_customization(data)
    with tab3:
        tab_results(data)

if __name__ == "__main__":
    main()