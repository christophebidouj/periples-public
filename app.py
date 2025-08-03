import streamlit as st
import time
import os
from typing import List, Dict
from models.character import Character, Enemy
from models.combat_engine import CombatEngine
from models.rules_engine import GameRules
from utils.data_loader import DataLoader

# Import des modules UI refactorisés
from ui.styling import (
    apply_fantasy_theme, 
    get_combat_button_styles,
    get_waiting_combat_style,
    get_app_title_style,
    Colors
)

# Import des composants depuis la structure modulaire
from ui.components import (
    # Héros
    display_hero_card,
    display_team_recap,
    display_hero_base_stats,
    display_current_build_info,
    display_new_stats_preview,
    
    # Ennemis
    display_enemy_card,
    
    # Équipements (version native avec nouvelles couleurs)
    display_equipment_selection_native,
    
    # Combat
    display_combat_result_banner,
    display_combat_metrics,
    display_heroes_individual_table,
    display_combat_log,
    display_combat_summary,
    
    # UI Elements
    display_progress_indicators_with_reset,
    get_hero_icon
)

# === CONFIGURATION ===
ENABLE_IMAGES = True

# === CACHE ET UTILITAIRES ===
@st.cache_data(persist=True)
def get_cached_build_info(hero_code: str, _loader) -> Dict:
    hero_list = _loader.load_heroes()
    hero = next(h for h in hero_list if h.code == hero_code)
    return get_hero_build(hero, _loader)

def get_equipment_categories(equipment):
    """Catégorise les équipements selon leur type Excel"""
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
    """Récupère les informations de build d'un héros (standard ou custom)"""
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

def prepare_hero_details(selected_hero_codes: List[str], heroes: List[Character], loader) -> List[Dict]:
    """Prépare les détails des héros sélectionnés pour le récapitulatif"""
    selected_hero_details = []
    for code in selected_hero_codes:
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
    return selected_hero_details

def prepare_enemy_details(selected_enemy_codes: List[str], enemies: List[Enemy], player_count: int) -> List[Dict]:
    """Prépare les détails des ennemis sélectionnés pour le récapitulatif"""
    selected_enemy_details = []
    for code in selected_enemy_codes:
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
    return selected_enemy_details

def tab_selection(data):
    """Onglet de sélection des équipes"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.header("🏰 Sélection des Équipes")
    
    heroes, enemies, loader = data['heroes'], data['enemies'], data['loader']
    nb_heroes, nb_enemies = len(st.session_state.selected_heroes), len(st.session_state.selected_enemies)
    
    # === INDICATEURS AVEC RESET DISCRET ===
    reset_clicked = display_progress_indicators_with_reset(nb_heroes, nb_enemies)
    
    # Gestion du reset
    if reset_clicked:
        st.session_state.selected_heroes = []
        st.session_state.selected_enemies = []
        st.success("✅ Sélections effacées !")
        st.rerun()
    
    # === SECTION HÉROS ===
    st.subheader("🛡️ Héros Disponibles")
    st.markdown("*📋 = Standard • 🔧 = Personnalisé*")
    
    # Affichage des cartes héros - 6 par ligne
    cols = st.columns(6)
    for i, hero in enumerate(heroes):
        build_info = get_cached_build_info(hero.code, loader)
        is_selected = hero.code in st.session_state.selected_heroes
        
        with cols[i % 6]:
            if display_hero_card(hero, build_info, is_selected, ENABLE_IMAGES):
                if is_selected:
                    st.session_state.selected_heroes.remove(hero.code)
                else:
                    st.session_state.selected_heroes.append(hero.code)
                st.rerun()
    
    # === SECTION ENNEMIS ===
    st.subheader("👹 Ennemis")
    player_count = max(2, nb_heroes) if nb_heroes >= 2 else 2
    if nb_heroes >= 2:
        st.info(f"🎯 Mode {player_count} joueurs (auto)")
    
    # Recherche d'ennemis
    search = st.text_input("🔍 Recherche:", placeholder="Ex: 34, Dragon...")
    if search.strip():
        term = search.strip().lower()
        filtered = [e for e in enemies if term in e.code.split('-')[-1].lower() or term in e.name.lower()]
    else:
        filtered = enemies[:15]
        st.info("💡 Tapez un numéro ou nom pour chercher")
    
    # Affichage des cartes ennemis - 5 par ligne
    if filtered:
        st.write(f"**{len(filtered)} ennemis trouvés:**")
        cols = st.columns(5)
        for i, enemy in enumerate(filtered):
            is_selected = enemy.code in st.session_state.selected_enemies
            
            with cols[i % 5]:
                if display_enemy_card(enemy, is_selected, player_count):
                    if is_selected:
                        st.session_state.selected_enemies.remove(enemy.code)
                    else:
                        st.session_state.selected_enemies.append(enemy.code)
                    st.rerun()
    
    # === RÉCAPITULATIF FORMATION DE GUERRE (ESSENTIEL) ===
    if nb_heroes >= 2 and nb_enemies > 0:
        selected_hero_details = prepare_hero_details(st.session_state.selected_heroes, heroes, loader)
        selected_enemy_details = prepare_enemy_details(st.session_state.selected_enemies, enemies, player_count)
        display_team_recap(selected_hero_details, selected_enemy_details, player_count)
    
    # === CONFIGURATION ET LANCEMENT ===
    st.subheader("⚙️ Configuration de Bataille")
    col1, col2 = st.columns(2)
    
    with col1:
        rules = {
            'ranged_attacks': True, 
            'magical_damage': True,
            'criticals': st.checkbox("🎯 Critiques", value=True, 
                                   help="Échecs/Réussites critiques sur 1 et 20"),
            'initiative': st.checkbox("🎲 Initiative", value=True, 
                                    help="Ordre de jeu aléatoire")
        }
        st.caption("🏹 Attaques distance et ✨ Dégâts magiques : activés automatiquement")
    
    with col2:
        st.info("⚔️ Combat détaillé avec journal complet des actions")
    
    # Bouton de lancement avec styles
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
                'player_count': player_count, 
                'rules': rules
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
    """Onglet de customisation avec nouveaux composants modulaires"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.header("⚙️ Forge des Équipements")
    
    heroes, equipment = data['heroes'], data['equipment']
    
    # Sélection du héros
    hero_options = {h.code: f"{get_hero_icon(h.name)} {h.name}" for h in heroes}
    selected_code = st.selectbox("Choisir un héros:", list(hero_options.keys()), 
                                format_func=lambda x: hero_options[x])
    selected_hero = next(h for h in heroes if h.code == selected_code)
    
    # Affichage des stats de base
    st.subheader("📊 Statistiques de Base")
    display_hero_base_stats(selected_hero)
    
    # Affichage du build actuel
    current_build = get_hero_build(selected_hero, data['loader'])
    display_current_build_info(current_build)
    
    # Boutons de gestion des builds
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
    
    # === SÉLECTION D'ÉQUIPEMENTS - NOUVEAUX COMPOSANTS MODULAIRES ===
    st.subheader("⚔️ Sélection d'Équipements")
    st.info("🎨 Nouvelles couleurs appliquées ! Armes (orange), Armures (bleu), Accessoires (violet)")
    
    weapons, armor, accessories = get_equipment_categories(equipment)
    
    selected_eq = []
    
    # Nouveaux composants avec couleurs intégrées - 6 par ligne
    weapon_selection = display_equipment_selection_native(weapons, "Armes", "⚔️", "w")
    selected_eq.extend(weapon_selection)
    
    st.markdown("---")  # Séparateur visuel
    
    armor_selection = display_equipment_selection_native(armor, "Armures", "🛡️", "a")
    selected_eq.extend(armor_selection)
    
    st.markdown("---")  # Séparateur visuel
    
    accessory_selection = display_equipment_selection_native(accessories, "Accessoires", "💍", "acc")
    selected_eq.extend(accessory_selection)
    
    # === APERÇU DU NOUVEAU BUILD ===
    if selected_eq:
        st.subheader("💾 Forge du Nouveau Build")
        
        # Calcul des nouvelles statistiques
        temp_hero = selected_hero.model_copy()
        temp_eq = [eq for eq in equipment if eq.code in selected_eq]
        temp_hero.equip_items(temp_eq, "Custom")
        temp_stats = temp_hero.get_stats_summary()['total']
        
        # Affichage de l'aperçu
        display_new_stats_preview(temp_stats)
        
        # Sauvegarde du build
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
    """Onglet des résultats de combat avec composants modulaires"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.header("📜 Chroniques du Combat")
    
    # Vérification si simulation à lancer
    if not st.session_state.get('run_simulation', False):
        waiting_style = get_waiting_combat_style()
        st.markdown(waiting_style, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Récupération de la configuration
    config = st.session_state['simulation_config']
    heroes, enemies, loader = data['heroes'], data['enemies'], data['loader']
    
    # === PRÉPARATION DES ÉQUIPES ===
    selected_heroes = []
    for code in config['hero_codes']:
        hero = next(h for h in heroes if h.code == code)
        build_info = get_hero_build(hero, loader)
        selected_heroes.append(build_info['hero_equipped'])
    
    selected_enemies = [e for e in enemies if e.code in config['enemy_codes']]
    
    # === SIMULATION DU COMBAT ===
    game_rules = GameRules(**config['rules'])
    engine = CombatEngine(game_rules)
    
    with st.spinner("⚔️ Combat épique en cours..."):
        result = engine.simulate_single_combat(selected_heroes, selected_enemies, config['player_count'])
    
    # === AFFICHAGE DU RÉSULTAT - COMPOSANTS MODULAIRES ===
    # Bannière de résultat
    display_combat_result_banner(result['winner'])
    
    # === MÉTRIQUES DE RESSOURCES ===
    if 'resource_metrics' in result:
        # Métriques principales
        display_combat_metrics(result['resource_metrics'])
        
        # Tableau individuel
        display_heroes_individual_table(result['resource_metrics'])
    
    # === JOURNAL DE COMBAT ===
    display_combat_log(result['log'])
    
    # === RÉSUMÉ FINAL ===
    display_combat_summary(result)
    
    # Reset automatique de la simulation pour éviter les reruns
    st.session_state['run_simulation'] = False
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Fonction principale de l'application - Version refactorisée avec structure modulaire"""
    init_app()
    apply_fantasy_theme()
    
    # Titre principal avec style
    st.markdown(get_app_title_style(), unsafe_allow_html=True)
    
    # Chargement des données
    try:
        data = load_data()
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
        st.stop()
    
    # Navigation par onglets
    tab1, tab2, tab3 = st.tabs(["🏰 Sélection", "⚙️ Forge", "📜 Chroniques"])
    
    with tab1:
        tab_selection(data)
    
    with tab2:
        tab_customization(data)
    
    with tab3:
        tab_results(data)

if __name__ == "__main__":
    main()