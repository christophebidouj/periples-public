"""
Interface Mode Sandbox - Version Fonctionnelle V1
Contrôle manuel complet des combats pour tests et debug
"""

import streamlit as st
import random
from copy import deepcopy
from typing import List, Dict, Any

# === CONFIGURATION ===

def init_sandbox_state():
    """Initialise l'état du sandbox"""
    if 'sandbox_initialized' not in st.session_state:
        st.session_state.sandbox_initialized = False
        st.session_state.sandbox_state = 'CHECK_TEAMS'
        st.session_state.sandbox_combatants = []
        st.session_state.active_combatant_index = 0
        st.session_state.turn_number = 1
        st.session_state.action_selected = None
        st.session_state.target_selected = None
        st.session_state.combat_log = []
        
        # NOUVEAU - Historique pour Undo/Redo
        st.session_state.sandbox_history = []
        st.session_state.history_index = -1

def save_game_state(action_description: str = "Action"):
    """Sauvegarde l'état complet pour historique"""
    if 'sandbox_combatants' in st.session_state:
        game_state = {
            'combatants': deepcopy(st.session_state.sandbox_combatants),
            'active_index': st.session_state.active_combatant_index,
            'turn_number': st.session_state.turn_number,
            'combat_log': st.session_state.combat_log.copy(),
            'action_description': action_description
        }
        
        # Supprime l'historique futur si on était revenu en arrière
        st.session_state.sandbox_history = st.session_state.sandbox_history[:st.session_state.history_index + 1]
        st.session_state.sandbox_history.append(game_state)
        st.session_state.history_index += 1

# === VÉRIFICATION ÉQUIPES ===

def check_teams_configured() -> bool:
    """Vérifie si les équipes sont configurées dans l'onglet 1"""
    heroes = st.session_state.get('selected_heroes', [])
    enemies = st.session_state.get('selected_enemies', [])
    return len(heroes) >= 2 and len(enemies) >= 1

def display_teams_not_configured():
    """Interface si équipes non configurées"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255,165,0,0.1), rgba(255,140,0,0.1));
                border: 3px solid #ffa500; border-radius: 15px; padding: 25px; margin: 20px 0; text-align: center;">
        <h2 style="color: #ff8c00; margin-top: 0;">🎮 Mode Sandbox - Configuration Requise</h2>
        <p style="font-size: 1.1rem; margin: 15px 0;">
            Pour utiliser le Mode Sandbox, vous devez d'abord configurer vos équipes.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📋 **Étapes Requises :**")
    st.markdown("""
    1. **🏰 Allez dans l'onglet "Sélection"**
    2. **🛡️ Choisissez au moins 2 héros**
    3. **👹 Sélectionnez au moins 1 ennemi**
    4. **🔄 Revenez ici pour commencer le Mode Sandbox**
    """)
    
    st.info("💡 **Le Mode Sandbox vous permet de contrôler manuellement tous les personnages pour tester des scénarios spécifiques.**")

# === PRÉPARATION COMBAT ===

def prepare_sandbox_combatants():
    """Prépare les combattants avec équipements et capacités"""
    try:
        # Récupération données depuis l'app principale
        heroes_codes = st.session_state.get('selected_heroes', [])
        enemies_codes = st.session_state.get('selected_enemies', [])
        
        # Chargement des données
        from utils.data_loader import DataLoader
        loader = DataLoader()
        
        heroes_data = loader.load_heroes()
        enemies_data = loader.load_enemies()
        
        combatants = []
        
        # Préparation héros avec builds custom
        current_builds = st.session_state.get('custom_builds', {})
        for hero_code in heroes_codes:
            hero = next((h for h in heroes_data if h.code == hero_code), None)
            if hero:
                # Application build custom si existe
                if hero_code in current_builds:
                    build = current_builds[hero_code]
                    equipment_codes = build.get('equipment', [])
                    equipment_list = [eq for eq in loader.load_equipment() if eq.code in equipment_codes]
                    hero.equip_items(equipment_list, build.get('name', 'Build Custom'))
                    
                    # Application potions custom
                    potions = build.get('potions', {})
                    if potions and hasattr(hero, 'set_potions_from_selection'):
                        hero.set_potions_from_selection(potions.get('small', 0), potions.get('large', 0))
                    
                    # Application capacités custom
                    abilities = build.get('abilities', [])
                    if abilities and hasattr(hero, 'abilities'):
                        hero_abilities = loader.get_hero_abilities(hero_code)
                        if hero_abilities:
                            hero.add_abilities(hero_abilities)
                            for num in abilities:
                                hero.unlock_ability(num)
                
                # Reset santé et sorts
                hero.reset_health()
                if hasattr(hero, 'start_new_combat'):
                    hero.start_new_combat()
                
                combatants.append({
                    'character': hero,
                    'faction': 'hero',
                    'id': f"hero_{hero_code}",
                    'initiative': 0
                })
        
        # Préparation ennemis
        player_count = len(heroes_codes)
        for enemy_code in enemies_codes:
            enemy = next((e for e in enemies_data if e.code == enemy_code), None)
            if enemy:
                enemy.initialize_for_combat(player_count)
                combatants.append({
                    'character': enemy,
                    'faction': 'enemy',
                    'id': f"enemy_{enemy_code}",
                    'initiative': 0
                })
        
        return combatants
    
    except Exception as e:
        st.error(f"❌ Erreur préparation combattants: {e}")
        return []

def generate_initiative_order():
    """Génère l'ordre d'initiative"""
    for combatant in st.session_state.sandbox_combatants:
        base_initiative = 10  # Base par défaut
        roll = random.randint(1, 20)
        combatant['initiative'] = base_initiative + roll
        combatant['initiative_detail'] = f"({base_initiative} + {roll})"
    
    # Tri par initiative décroissante
    st.session_state.sandbox_combatants.sort(key=lambda x: x['initiative'], reverse=True)
    
    # Log initiative
    st.session_state.combat_log.append("=== ORDRE D'INITIATIVE ===")
    for i, combatant in enumerate(st.session_state.sandbox_combatants):
        name = combatant['character'].name
        init_val = combatant['initiative']
        detail = combatant['initiative_detail']
        st.session_state.combat_log.append(f"{i+1}. {name}: {init_val} {detail}")
    
    # Sauvegarde état initial
    save_game_state("Génération initiative")

# === INTERFACE GUIDANCE ===

def display_guidance_banner():
    """Bannière de guidance contextuelle"""
    state = st.session_state.sandbox_state
    
    # Bannière selon l'état
    if state == 'INITIATIVE':
        banner_html = """
        <div style="background: linear-gradient(135deg, #4682b4, #5f9ea0); border-radius: 15px; padding: 20px; margin: 15px 0; text-align: center;">
            <h3 style="color: white; margin: 0;">🎲 Génération de l'Initiative</h3>
            <p style="color: #f0f8ff; margin: 10px 0;">L'ordre des tours est déterminé par un jet d'initiative</p>
        </div>
        """
    elif state == 'WAITING_ACTION':
        active = get_active_combatant()
        if active:
            name = active['character'].name
            faction = active['faction']
            
            if faction == 'hero':
                color = "#228b22"
                icon = "🛡️"
                faction_text = "Héros"
            else:
                color = "#dc143c"
                icon = "👹"
                faction_text = "Ennemi"
            
            banner_html = f"""
            <div style="background: linear-gradient(135deg, {color}, {color}dd); border-radius: 15px; padding: 20px; margin: 15px 0; text-align: center;">
                <h3 style="color: white; margin: 0;">{icon} Vous contrôlez {name} ({faction_text})</h3>
                <p style="color: #f0f8ff; margin: 10px 0;">Choisissez une action dans le panneau de contrôle</p>
                <div style="background: rgba(255,255,255,0.2); border-radius: 20px; padding: 5px 15px; display: inline-block;">
                    <small>Étape 3/5 - Sélection Action</small>
                </div>
            </div>
            """
        else:
            banner_html = """
            <div style="background: linear-gradient(135deg, #666, #888); border-radius: 15px; padding: 20px; margin: 15px 0; text-align: center;">
                <h3 style="color: white; margin: 0;">⏳ Préparation en cours...</h3>
            </div>
            """
    else:
        banner_html = """
        <div style="background: linear-gradient(135deg, #8b4513, #d4af37); border-radius: 15px; padding: 20px; margin: 15px 0; text-align: center;">
            <h3 style="color: white; margin: 0;">🎮 Mode Sandbox</h3>
            <p style="color: #f4e4bc; margin: 10px 0;">Contrôle manuel complet des combats</p>
        </div>
        """
    
    st.markdown(banner_html, unsafe_allow_html=True)

def display_breadcrumb():
    """Fil d'Ariane avec étapes"""
    steps = {
        'CHECK_TEAMS': ('🔧', 'Setup', 'secondary'),
        'INITIATIVE': ('🎲', 'Initiative', 'secondary'),
        'WAITING_ACTION': ('⚔️', 'Action', 'primary'),
        'TARGET_SELECTION': ('🎯', 'Cible', 'secondary'),
        'CONFIRM_ACTION': ('✅', 'Confirmer', 'secondary')
    }
    
    current_state = st.session_state.sandbox_state
    
    cols = st.columns(5)
    for i, (state, (icon, name, _)) in enumerate(steps.items()):
        with cols[i]:
            if state == current_state:
                st.markdown(f"""
                <div style="background: #ffd700; color: #000; padding: 8px; border-radius: 8px; text-align: center; font-weight: bold;">
                    {icon} {name}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: #666; color: #ccc; padding: 8px; border-radius: 8px; text-align: center;">
                    {icon} {name}
                </div>
                """, unsafe_allow_html=True)

# === GESTION COMBATTANTS ===

def get_active_combatant():
    """Retourne le combattant actif"""
    if st.session_state.sandbox_combatants:
        index = st.session_state.active_combatant_index
        if 0 <= index < len(st.session_state.sandbox_combatants):
            return st.session_state.sandbox_combatants[index]
    return None

def next_combatant():
    """Passe au combattant suivant"""
    if st.session_state.sandbox_combatants:
        st.session_state.active_combatant_index = (st.session_state.active_combatant_index + 1) % len(st.session_state.sandbox_combatants)
        
        # Nouveau tour si on revient au premier
        if st.session_state.active_combatant_index == 0:
            st.session_state.turn_number += 1
        
        # Reset états d'action
        st.session_state.action_selected = None
        st.session_state.target_selected = None
        st.session_state.sandbox_state = 'WAITING_ACTION'

def display_combatant_cards():
    """Affiche les cartes de tous les combattants"""
    if not st.session_state.sandbox_combatants:
        return
    
    st.markdown("### ⚔️ Champ de Bataille")
    
    # Séparation par faction
    heroes = [c for c in st.session_state.sandbox_combatants if c['faction'] == 'hero']
    enemies = [c for c in st.session_state.sandbox_combatants if c['faction'] == 'enemy']
    
    if heroes:
        st.markdown("**🛡️ Équipe des Héros**")
        display_faction_cards(heroes)
    
    if enemies:
        st.markdown("**👹 Équipe Ennemie**")
        display_faction_cards(enemies)

def display_faction_cards(combatants: List[Dict]):
    """Affiche les cartes d'une faction"""
    cols = st.columns(min(len(combatants), 4))
    
    for i, combatant in enumerate(combatants):
        with cols[i % len(cols)]:
            display_single_combatant_card(combatant)

def display_single_combatant_card(combatant: Dict):
    """Carte individuelle d'un combattant"""
    char = combatant['character']
    is_active = st.session_state.active_combatant_index == st.session_state.sandbox_combatants.index(combatant)
    faction = combatant['faction']
    
    # Couleurs selon faction et état
    if is_active:
        border_color = "#ffd700"
        bg_color = "#4a4a2a"
        active_indicator = "⭐ "
    elif faction == 'hero':
        border_color = "#228b22"
        bg_color = "#1a3a1a"
        active_indicator = ""
    else:
        border_color = "#dc143c"
        bg_color = "#3a1a1a"
        active_indicator = ""
    
    # Stats de santé
    if hasattr(char, 'current_health'):
        current_hp = char.current_health
        max_hp = char.get_total_health() if hasattr(char, 'get_total_health') else char.health
    else:
        current_hp = getattr(char, 'health', 100)
        max_hp = getattr(char, 'health', 100)
    
    hp_percentage = (current_hp / max_hp * 100) if max_hp > 0 else 0
    
    # Couleur barre de vie
    if hp_percentage > 60:
        hp_color = "#28a745"
    elif hp_percentage > 30:
        hp_color = "#ffc107"
    else:
        hp_color = "#dc3545"
    
    # Card HTML
    card_html = f"""
    <div style="border: 2px solid {border_color}; background-color: {bg_color}; padding: 15px; 
                border-radius: 10px; margin: 10px 0; transition: all 0.3s ease;">
        <h4 style="margin: 0 0 10px 0; color: white;">{active_indicator}{char.name}</h4>
        
        <div style="background-color: #333; border-radius: 4px; overflow: hidden; margin-bottom: 10px;">
            <div style="background-color: {hp_color}; height: 8px; width: {hp_percentage}%; transition: width 0.3s ease;"></div>
        </div>
        
        <p style="margin: 5px 0; color: #ccc; font-size: 0.9rem;">💚 PV: {current_hp}/{max_hp}</p>
        <p style="margin: 0; font-size: 0.8rem; color: #aaa;">🎯 Initiative: {combatant.get('initiative', 0)}</p>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

# === CONTRÔLES D'ACTION ===

def display_action_controls():
    """Panneau de contrôle des actions"""
    if st.session_state.sandbox_state != 'WAITING_ACTION':
        st.info("⏳ En attente d'action...")
        return
    
    active = get_active_combatant()
    if not active:
        return
    
    char = active['character']
    st.markdown(f"### 🎯 Contrôles - {char.name}")
    
    # Actions de base
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⚔️ Attaquer", use_container_width=True, type="primary"):
            st.session_state.action_selected = 'attack'
            st.session_state.sandbox_state = 'TARGET_SELECTION'
            st.rerun()
    
    with col2:
        # Capacités (si disponibles)
        if hasattr(char, 'get_available_abilities'):
            available_abilities = char.get_available_abilities()
            if available_abilities:
                if st.button(f"✨ Capacités ({len(available_abilities)})", use_container_width=True):
                    st.session_state.action_selected = 'ability'
                    # Interface capacités (à développer)
                    st.info("🔮 Sélection de capacités à implémenter")
            else:
                st.button("✨ Pas de capacités", disabled=True, use_container_width=True)
        else:
            st.button("✨ Capacités", disabled=True, use_container_width=True)
    
    with col3:
        if st.button("⏭️ Passer le tour", use_container_width=True):
            save_game_state(f"{char.name} passe son tour")
            st.session_state.combat_log.append(f"⏭️ {char.name} passe son tour")
            next_combatant()
            st.rerun()

# === HISTORIQUE ===

def display_history_controls():
    """Contrôles d'historique Undo/Redo"""
    st.markdown("### 📚 Historique")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        can_undo = st.session_state.history_index > 0
        if st.button("⏪ Annuler", disabled=not can_undo, use_container_width=True):
            restore_previous_state()
            st.rerun()
    
    with col2:
        can_redo = st.session_state.history_index < len(st.session_state.sandbox_history) - 1
        if st.button("⏩ Refaire", disabled=not can_redo, use_container_width=True):
            restore_next_state()
            st.rerun()
    
    with col3:
        st.metric("Tour", st.session_state.turn_number)
    
    with col4:
        if st.button("🔄 Reset Combat", use_container_width=True):
            reset_sandbox()
            st.rerun()

def restore_previous_state():
    """Restaure l'état précédent"""
    if st.session_state.history_index > 0:
        st.session_state.history_index -= 1
        state = st.session_state.sandbox_history[st.session_state.history_index]
        
        st.session_state.sandbox_combatants = deepcopy(state['combatants'])
        st.session_state.active_combatant_index = state['active_index']
        st.session_state.turn_number = state['turn_number']
        st.session_state.combat_log = state['combat_log'].copy()
        st.session_state.sandbox_state = 'WAITING_ACTION'

def restore_next_state():
    """Restaure l'état suivant"""
    if st.session_state.history_index < len(st.session_state.sandbox_history) - 1:
        st.session_state.history_index += 1
        state = st.session_state.sandbox_history[st.session_state.history_index]
        
        st.session_state.sandbox_combatants = deepcopy(state['combatants'])
        st.session_state.active_combatant_index = state['active_index']
        st.session_state.turn_number = state['turn_number']
        st.session_state.combat_log = state['combat_log'].copy()
        st.session_state.sandbox_state = 'WAITING_ACTION'

def reset_sandbox():
    """Reset complet du sandbox"""
    keys_to_remove = ['sandbox_initialized', 'sandbox_state', 'sandbox_combatants', 
                      'active_combatant_index', 'turn_number', 'action_selected', 
                      'target_selected', 'combat_log', 'sandbox_history', 'history_index']
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

# === INTERFACE PRINCIPALE ===

def main_sandbox_tab():
    """Point d'entrée principal du Mode Sandbox"""
    st.title("🎮 Mode Sandbox")
    st.caption("Contrôle manuel complet des combats pour tests et validation")
    
    # Initialisation
    init_sandbox_state()
    
    # Vérification équipes
    if not check_teams_configured():
        display_teams_not_configured()
        return
    
    # Guidance
    display_guidance_banner()
    display_breadcrumb()
    
    # États du sandbox
    if st.session_state.sandbox_state == 'CHECK_TEAMS':
        # Préparation des combattants
        st.session_state.sandbox_combatants = prepare_sandbox_combatants()
        if st.session_state.sandbox_combatants:
            st.session_state.sandbox_state = 'INITIATIVE'
            st.rerun()
        else:
            st.error("❌ Erreur préparation des combattants")
            return
    
    elif st.session_state.sandbox_state == 'INITIATIVE':
        st.info("🎲 **Génération de l'ordre d'initiative...**")
        if st.button("🎲 Générer Initiative", type="primary"):
            generate_initiative_order()
            st.session_state.sandbox_state = 'WAITING_ACTION'
            st.rerun()
    
    elif st.session_state.sandbox_state in ['WAITING_ACTION', 'TARGET_SELECTION']:
        # Interface principale
        col_control, col_battlefield = st.columns([1, 2])
        
        with col_control:
            display_action_controls()
            st.markdown("---")
            display_history_controls()
        
        with col_battlefield:
            display_combatant_cards()
    
    # Combat Log (toujours visible)
    if st.session_state.combat_log:
        st.markdown("### 📜 Journal de Combat")
        with st.expander("Voir le journal", expanded=False):
            for line in st.session_state.combat_log[-10:]:  # 10 dernières lignes
                st.text(line)

# Point d'entrée
if __name__ == "__main__":
    main_sandbox_tab()