import streamlit as st
import time
import os
from typing import List, Dict
from models.character import Character, Enemy
from models.combat_engine import CombatEngine
from models.rules_engine import GameRules
from utils.data_loader import DataLoader

# NOUVEAU : Import du module styling
from ui.styling import (
    apply_fantasy_theme, 
    get_hero_card_style, 
    get_enemy_card_style,
    get_team_recap_styles,
    get_combat_result_styles,
    get_combat_button_styles,
    get_forge_styles,
    get_waiting_combat_style,
    get_app_title_style,
    style_combat_log_entry,
    Colors
)

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
    """CORRIGÉ - Mapping exact selon vos fichiers"""
    hero_files = {
        "Atucan": "Atucan_-_Paladin.png", 
        "Elneha": "Elneha_-_Druidesse.png",
        "Kraor": "Kraor_-_Rodeur.png", 
        "Lame": "Lame_-_Roublarde.png",
        "Liarie": "Liarie_-_Mage.png", 
        "Raishi": "Raishi_-_Pugiliste.png",
        "Stèphe": "Stephe_-_Barde.png",  # CORRIGÉ: Stèphe → Stephe
        "Thordius": "Thordius_-_Barbare.png",
        # Héros étendus
        "Loup": "Loup.png",
        "Ours": "Ours.png", 
        "Loup S": "Loup_S.png",
        "Ours S": "Ours_S.png"
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
        border_color, button_text, button_type = Colors.SELECTED_BORDER, "✅ Sélectionné", "secondary"
    else:
        border_color, button_text, button_type = Colors.AVAILABLE_BORDER, "➕ Ajouter", "primary"
    
    # Image background - VERSION ORIGINALE
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
    
    # Utilisation du style extrait
    stats_content = f"""
    <div style="font-family: monospace; font-size: 1rem; margin-bottom: 5px; font-weight: bold; color: #f0f0f0;">
        🎯{stats["precision"]} • ⚔️{stats["damage"]} • ❤️{stats["health"]}{bonus_text}
    </div>"""
    
    build_content = f"""
    <div style="font-size: 0.9rem; font-style: italic; color: #e0e0e0;">
        {build_info["build_name"][:25]}{"..." if len(build_info["build_name"]) > 25 else ""}
    </div>"""
    
    card_html = get_hero_card_style(hero.name, border_color, background_style)
    card_html = card_html.replace("{stats_content}", stats_content)
    card_html = card_html.replace("{build_content}", build_content)
    
    with st.container():
        st.markdown(card_html, unsafe_allow_html=True)
        
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
        border_color, bg_color, text_color = Colors.ERROR_RED, "#fff5f5", "#333"
        button_text, button_type = "✅ Sélectionné", "secondary"
    else:
        border_color, bg_color, text_color = Colors.ENEMY_RED, "#2c1810", "#fff"
        button_text, button_type = "➕ Ajouter", "primary"
    
    content = f"""
    <h3 style="color: {border_color}; margin: 0 0 8px 0;">👹 #{number}{magic}</h3>
    <div style="margin: 8px 0;">{enemy.name}</div>
    <div style="font-family: monospace; font-weight: bold;">
        ❤️{stats["health"]} • ⚔️{stats["damage"]} • 🛡️{enemy.defense}
    </div>
    <div style="font-style: italic; color: {'#888' if is_selected else '#ffa500'}; margin: 5px 0;">
        {'Magique' if enemy.is_magical else 'Physique'}
    </div>
    """
    
    card_html = get_enemy_card_style(border_color, bg_color, text_color)
    card_html = card_html.replace("{content}", content)
    
    with st.container():
        st.markdown(card_html, unsafe_allow_html=True)
        
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
    
    # HÉROS - VOTRE VERSION: 6 par ligne
    st.subheader("🛡️ Héros Disponibles")
    st.markdown("*📋 = Standard • 🔧 = Personnalisé*")
    cols = st.columns(6)
    for i, hero in enumerate(heroes):
        build_info = get_cached_build_info(hero.code, loader)
        is_selected = hero.code in st.session_state.selected_heroes
        with cols[i % 6]:
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
        
        # Utilisation des styles extraits
        recap_styles = get_team_recap_styles()
        st.markdown(recap_styles['formation_header'], unsafe_allow_html=True)
        
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
            st.markdown(recap_styles['heroes_team_header'], unsafe_allow_html=True)
            
            for hero in selected_hero_details:
                build_badge = "🔧 Custom" if hero['is_custom'] else "📋 Standard"
                bonus_info = []
                if hero['parade'] > 0:
                    bonus_info.append(f"🛡️{hero['parade']}")
                if hero['spells'] > 0:
                    bonus_info.append(f"✨{hero['spells']}")
                bonus_text = f" • {' • '.join(bonus_info)}" if bonus_info else ""
                
                stats = f"🎯{hero['precision']} ⚔️{hero['damage']} ❤️{hero['health']}{bonus_text}"
                
                hero_card_html = recap_styles['hero_card'].format(
                    icon=hero['icon'],
                    name=hero['name'],
                    build_badge=build_badge,
                    stats=stats
                )
                st.markdown(hero_card_html, unsafe_allow_html=True)
        
        with col2:
            st.markdown(recap_styles['enemies_team_header'], unsafe_allow_html=True)
            
            for enemy in selected_enemy_details:
                magic_badge = "✨ Magique" if enemy['is_magical'] else "⚔️ Physique"
                stats = f"❤️{enemy['health']} ⚔️{enemy['damage']} 🛡️{enemy['defense']}"
                name_truncated = enemy['name'][:18]
                
                enemy_card_html = recap_styles['enemy_card'].format(
                    number=enemy['number'],
                    name=name_truncated,
                    magic_badge=magic_badge,
                    stats=stats
                )
                st.markdown(enemy_card_html, unsafe_allow_html=True)
        
        # Statistiques de bataille
        total_hero_health = sum(h['health'] for h in selected_hero_details)
        total_enemy_health = sum(e['health'] for e in selected_enemy_details)
        avg_hero_damage = sum(h['damage'] for h in selected_hero_details) / len(selected_hero_details)
        avg_enemy_damage = sum(e['damage'] for e in selected_enemy_details) / len(selected_enemy_details)
        
        battle_stats_html = recap_styles['battle_stats'].format(
            hero_health=total_hero_health,
            hero_dps=avg_hero_damage,
            enemy_health=total_enemy_health,
            enemy_dps=avg_enemy_damage
        )
        st.markdown(battle_stats_html, unsafe_allow_html=True)
    
    # Configuration et lancement
    st.subheader("⚙️ Configuration de Bataille")
    col1, col2 = st.columns(2)
    with col1:
        rules = {'ranged_attacks': True, 'magical_damage': True,
                'criticals': st.checkbox("🎯 Critiques", value=True, help="Échecs/Réussites critiques sur 1 et 20"),
                'initiative': st.checkbox("🎲 Initiative", value=True, help="Ordre de jeu aléatoire")}
        st.caption("🏹 Attaques distance et ✨ Dégâts magiques : activés automatiquement")
    with col2:
        st.info("⚔️ Combat détaillé avec journal complet des actions")
    
    # Bouton de lancement stylisé
    ready = nb_heroes >= 2 and nb_enemies > 0
    button_styles = get_combat_button_styles()
    
    if ready:
        st.markdown(button_styles['ready'], unsafe_allow_html=True)
        
        if st.button("⚔️ ENGAGER LE COMBAT ! ⚔️", type="primary", use_container_width=True,
                    help="Lancer la simulation de combat épique"):
            st.session_state['run_simulation'] = True
            st.session_state['simulation_config'] = {
                'hero_codes': st.session_state.selected_heroes,
                'enemy_codes': st.session_state.selected_enemies,
                'player_count': player_count, 'rules': rules
            }
            st.success("⚡ Combat engagé ! 👉 **Allez dans l'onglet 'Chroniques' pour voir le résultat** 👈")
            st.balloons()
        
        st.markdown(button_styles['close_div'], unsafe_allow_html=True)
    else:
        st.markdown(button_styles['disabled'], unsafe_allow_html=True)
        
        st.button("⚔️ FORMATION INCOMPLÈTE", disabled=True, use_container_width=True,
                 help="Sélectionnez au moins 2 héros et 1 ennemi")
        
        st.markdown(button_styles['close_div'], unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def tab_customization(data):
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.header("⚙️ Forge des Équipements")
    
    heroes, equipment = data['heroes'], data['equipment']
    forge_styles = get_forge_styles()
    
    # Sélection héros
    hero_options = {h.code: f"{get_hero_icon(h.name)} {h.name}" for h in heroes}
    selected_code = st.selectbox("Choisir un héros:", list(hero_options.keys()), 
                                format_func=lambda x: hero_options[x])
    selected_hero = next(h for h in heroes if h.code == selected_code)
    
    # Stats base avec style extrait
    hero_stats_html = forge_styles['hero_base_stats'].format(
        icon=get_hero_icon(selected_hero.name),
        name=selected_hero.name,
        stats=f"🎯 Précision: {selected_hero.precision} • ⚔️ Dégâts: {selected_hero.damage} • ❤️ PV: {selected_hero.health}"
    )
    st.subheader("📊 Statistiques de Base")
    st.markdown(hero_stats_html, unsafe_allow_html=True)
    
    # Build actuel avec style extrait
    current_build = get_hero_build(selected_hero, data['loader'])
    build_icon = "🔧" if current_build['is_custom'] else "📋"
    
    current_build_html = forge_styles['current_build'].format(
        icon=build_icon,
        name=current_build['build_name']
    )
    st.markdown(current_build_html, unsafe_allow_html=True)
    
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
        
        parade_text = f" • 🛡️ Parade: {temp_stats['parade']}" if temp_stats['parade'] > 0 else ""
        spells_text = f" • ✨ Sorts: {temp_stats['spells']}" if temp_stats['spells'] > 0 else ""
        stats_display = f"🎯 Précision: {temp_stats['precision']} • ⚔️ Dégâts: {temp_stats['damage']} • ❤️ PV: {temp_stats['health']}{parade_text}{spells_text}"
        
        new_stats_html = forge_styles['new_stats_preview'].format(stats=stats_display)
        st.markdown(new_stats_html, unsafe_allow_html=True)
        
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
        waiting_style = get_waiting_combat_style()
        st.markdown(waiting_style, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    config = st.session_state['simulation_config']
    heroes, enemies, loader = data['heroes'], data['enemies'], data['loader']
    combat_styles = get_combat_result_styles()
    
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
    
    # Affichage résultat avec styles extraits
    if result['winner'] == 'heroes':
        st.markdown(combat_styles['victory'], unsafe_allow_html=True)
    elif result['winner'] == 'enemies':
        st.markdown(combat_styles['defeat'], unsafe_allow_html=True)
    else:
        st.markdown(combat_styles['draw'], unsafe_allow_html=True)
    
    # Métriques ressources
    if 'resource_metrics' in result:
        st.subheader("📊 Bilan des Ressources")
        resource_metrics = result['resource_metrics']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            damage_card = combat_styles['metric_card'].format(
                bg_color="rgba(220,20,60,0.1)", border_color="#dc143c", color="#8b0000",
                icon="💔", title="Blessures", value=resource_metrics['total_damage_taken'], text_color="#b22222"
            )
            st.markdown(damage_card, unsafe_allow_html=True)
        
        with col2:
            spells_card = combat_styles['metric_card'].format(
                bg_color="rgba(138,43,226,0.1)", border_color="#8a2be2", color="#4b0082",
                icon="✨", title="Sorts", value=resource_metrics['total_spells_used'], text_color="#663399"
            )
            st.markdown(spells_card, unsafe_allow_html=True)
        
        with col3:
            avg_card = combat_styles['metric_card'].format(
                bg_color="rgba(255,165,0,0.1)", border_color="#ffa500", color="#ff8c00",
                icon="📈", title="Moyenne", value=resource_metrics['average_damage_per_hero'], text_color="#b8860b"
            )
            st.markdown(avg_card, unsafe_allow_html=True)
        
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
    
    # Log de combat avec styles extraits
    st.subheader("📜 Journal de Combat")
    log_lines = result['log']
    formatted_log = [style_combat_log_entry(line) for line in log_lines]
    
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
        if st.button("📋 Afficher Journal Brut", type="secondary", use_container_width=True):
            log_text = "\n".join(result['log'])
            st.code(log_text, language="text")
            st.info("💡 Utilisez Ctrl+A puis Ctrl+C pour copier le texte ci-dessus")
    
    st.session_state['run_simulation'] = False
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    init_app()
    apply_fantasy_theme()  # Utilisation du CSS extrait
    
    # Titre avec style extrait
    st.markdown(get_app_title_style(), unsafe_allow_html=True)
    
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