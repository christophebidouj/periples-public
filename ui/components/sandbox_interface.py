"""
Interface Mode Sandbox - Version Prototype Exacte
Layout compact 2 colonnes avec zones entièrement cliquables
"""

import streamlit as st
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional
from models.character import Character, Enemy

# === CSS SANDBOX PROTOTYPE ===

def apply_sandbox_theme():
    """Applique le thème sombre sandbox identique au prototype"""
    st.markdown("""
    <style>
    /* === THÈME SOMBRE PROTOTYPE === */
    .prototype-container {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        border: 2px solid #7f8c8d;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        color: white;
    }
    
    .hero-header {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .enemy-header {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .stats-badges {
        display: flex;
        gap: 10px;
    }
    
    .stat-badge {
        background: rgba(0,0,0,0.3);
        padding: 8px 12px;
        border-radius: 8px;
        text-align: center;
        min-width: 50px;
    }
    
    .stat-badge.health { background: #e74c3c; }
    .stat-badge.attack { background: #f39c12; }
    .stat-badge.defense { background: #3498db; }
    .stat-badge.magic { background: #9b59b6; }
    
    /* === CAPACITÉS PROTOTYPE === */
    .abilities-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
        margin-bottom: 15px;
    }
    
    .ability-card-clickable {
        background: linear-gradient(135deg, #9b59b6, #8e44ad);
        border: 2px solid #7d3c98;
        border-radius: 10px;
        padding: 12px;
        color: white;
        text-align: left;
        position: relative;
        min-height: 80px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .ability-card-clickable:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(155, 89, 182, 0.4);
    }
    
    .ability-card-disabled {
        background: linear-gradient(135deg, #7f8c8d, #95a5a6);
        border: 2px solid #6c7b7d;
        color: #bdc3c7;
        opacity: 0.6;
        cursor: not-allowed;
    }
    
    .ability-badge {
        position: absolute;
        top: 8px;
        right: 8px;
        background: rgba(0,0,0,0.4);
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .ability-badge.available { background: #27ae60; }
    .ability-badge.unavailable { background: #e74c3c; }
    
    /* === ACTIONS ET POTIONS COMPACTES === */
    .actions-column {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    .action-button {
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.2s ease;
        border: none;
        color: white;
    }
    
    .action-attack { background: linear-gradient(135deg, #e74c3c, #c0392b); }
    .action-defend { background: linear-gradient(135deg, #3498db, #2980b9); }
    .action-skip { background: linear-gradient(135deg, #95a5a6, #7f8c8d); }
    
    .potions-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
        margin-top: 10px;
    }
    
    .potion-card {
        background: #34495e;
        border: 2px solid #7f8c8d;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        min-height: 60px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .potion-card.active {
        background: #e91e63;
        border-color: #ad1457;
        color: white;
    }
    
    .potion-card.inactive {
        background: #555;
        color: #999;
        cursor: not-allowed;
    }
    
    .potion-count {
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 4px;
    }
    
    /* === GUIDANCE COMPACTE === */
    .guidance-compact {
        background: linear-gradient(135deg, #f39c12, #e67e22);
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    .guidance-combat { background: linear-gradient(135deg, #e74c3c, #c0392b); }
    .guidance-initiative { background: linear-gradient(135deg, #f1c40f, #f39c12); }
    </style>
    """, unsafe_allow_html=True)

# === CONFIGURATION ET ÉTAT ===

def init_sandbox_state():
    """Initialise l'état du sandbox"""
    defaults = {
        'sandbox_initialized': False,
        'sandbox_phase': 'CONFIG',  
        'sandbox_combatants': [],
        'sandbox_current_turn_index': 0,
        'sandbox_round_number': 1,
        'sandbox_selected_action': None,
        'sandbox_selected_target': None,
        'sandbox_combat_log': [],
        'sandbox_game_history': [],
        'sandbox_history_index': -1
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def save_game_state(description: str = "Action"):
    """Sauvegarde pour historique Undo/Redo"""
    state = {
        'combatants': deepcopy(st.session_state.sandbox_combatants),
        'turn_index': st.session_state.sandbox_current_turn_index,
        'round_number': st.session_state.sandbox_round_number,
        'log': st.session_state.sandbox_combat_log.copy(),
        'description': description
    }
    
    st.session_state.sandbox_game_history = st.session_state.sandbox_game_history[:st.session_state.sandbox_history_index + 1]
    st.session_state.sandbox_game_history.append(state)
    st.session_state.sandbox_history_index += 1

# === PRÉPARATION ÉQUIPES ===

def prepare_combatants_for_sandbox():
    """Prépare les combattants depuis l'onglet Sélection"""
    try:
        from utils.data_loader import DataLoader
        loader = DataLoader()
        
        heroes_codes = st.session_state.get('selected_heroes', [])
        enemies_codes = st.session_state.get('selected_enemies', [])
        
        if not heroes_codes or not enemies_codes:
            return []
        
        heroes_data = loader.load_heroes()
        enemies_data = loader.load_enemies()
        equipment_data = loader.load_equipment()
        
        combatants = []
        
        # Préparation héros avec builds
        current_builds = st.session_state.get('custom_builds', {})
        for hero_code in heroes_codes:
            hero = next((h for h in heroes_data if h.code == hero_code), None)
            if not hero:
                continue
                
            # Application build custom
            if hero_code in current_builds:
                build = current_builds[hero_code]
                equipment_codes = build.get('equipment', [])
                equipment_list = [eq for eq in equipment_data if eq.code in equipment_codes]
                hero.equip_items(equipment_list, build.get('name', 'Build Custom'))
                
                # Potions
                potions = build.get('potions', {})
                if potions and hasattr(hero, 'set_potions_from_selection'):
                    hero.set_potions_from_selection(potions.get('small', 0), potions.get('large', 0))
                
                # Capacités
                abilities = build.get('abilities', [])
                if abilities and hasattr(hero, 'abilities'):
                    hero_abilities = loader.get_hero_abilities(hero_code)
                    if hero_abilities:
                        hero.add_abilities(hero_abilities)
                        for num in abilities:
                            hero.unlock_ability(num)
            
            # Initialisation combat
            hero.reset_health()
            if hasattr(hero, 'start_new_combat'):
                hero.start_new_combat()
            
            combatants.append({
                'character': hero,
                'faction': 'hero',
                'initiative': 0,
                'id': f"hero_{hero_code}"
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
                    'initiative': 0,
                    'id': f"enemy_{enemy_code}"
                })
        
        return combatants
        
    except Exception as e:
        st.error(f"❌ Erreur préparation: {e}")
        return []

# === GUIDANCE PROTOTYPE ===

def display_guidance_banner_prototype():
    """Bannière guidance compacte style prototype"""
    phase = st.session_state.sandbox_phase
    
    if phase == 'CONFIG':
        st.markdown("""
        <div class="guidance-compact">
            🔧 Configuration - Sélectionnez vos équipes dans l'onglet "Sélection"
        </div>
        """, unsafe_allow_html=True)
        
    elif phase == 'INITIATIVE':
        st.markdown("""
        <div class="guidance-compact guidance-initiative">
            🎲 Initiative - Génération de l'ordre des tours
        </div>
        """, unsafe_allow_html=True)
        
    elif phase == 'COMBAT':
        current = get_current_combatant()
        if current:
            name = current['character'].name
            st.markdown(f"""
            <div class="guidance-compact guidance-combat">
                ⚔️ {name} - C'est votre tour, choisissez une action
            </div>
            """, unsafe_allow_html=True)

# === INTERFACE PROTOTYPE EXACTE ===

def display_hero_interface_prototype(combatant: Dict):
    """Interface héros EXACTE du prototype - Layout 2 colonnes"""
    char = combatant['character']
    
    # === HEADER HÉROS STYLE PROTOTYPE ===
    current_hp = getattr(char, 'current_health', char.health)
    max_hp = char.get_total_health() if hasattr(char, 'get_total_health') else char.health
    attack = char.get_total_damage() if hasattr(char, 'get_total_damage') else char.damage
    defense = char.get_total_parade() if hasattr(char, 'get_total_parade') else 0
    magic = char.get_total_spells() if hasattr(char, 'get_total_spells') else char.spells
    
    st.markdown(f"""
    <div class="hero-header">
        <div>
            <h3 style="margin: 0; color: white;">🏹 {char.name} l'Archère</h3>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">C'est votre tour - Choisissez une action</p>
        </div>
        <div class="stats-badges">
            <div class="stat-badge health">
                <div style="font-size: 0.8rem;">❤️ PV</div>
                <div style="font-weight: bold;">{current_hp}/{max_hp}</div>
            </div>
            <div class="stat-badge attack">
                <div style="font-size: 0.8rem;">⚔️ ATT</div>
                <div style="font-weight: bold;">{attack}</div>
            </div>
            <div class="stat-badge defense">
                <div style="font-size: 0.8rem;">🛡️ DEF</div>
                <div style="font-weight: bold;">{defense}</div>
            </div>
            <div class="stat-badge magic">
                <div style="font-size: 0.8rem;">✨ MAG</div>
                <div style="font-weight: bold;">{magic}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # === LAYOUT 2 COLONNES PROTOTYPE ===
    col_abilities, col_actions = st.columns([2, 1])
    
    with col_abilities:
        display_abilities_prototype_grid(char, combatant['id'])
    
    with col_actions:
        display_actions_and_potions_prototype(char, combatant['id'])

def display_enemy_interface_prototype(combatant: Dict):
    """Interface ennemi style prototype"""
    char = combatant['character']
    
    # Stats ennemis
    current_hp = getattr(char, 'current_health', 100)
    max_hp = getattr(char, 'max_health', 100)
    player_count = len([c for c in st.session_state.sandbox_combatants if c['faction'] == 'hero'])
    stats = char.get_stats_for_players(player_count)
    attack = stats['damage']
    defense = stats.get('defense', char.defense)
    
    st.markdown(f"""
    <div class="enemy-header">
        <div>
            <h3 style="margin: 0; color: white;">👹 {char.name}</h3>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Vous contrôlez cet ennemi</p>
        </div>
        <div class="stats-badges">
            <div class="stat-badge health">
                <div style="font-size: 0.8rem;">❤️ PV</div>
                <div style="font-weight: bold;">{current_hp}/{max_hp}</div>
            </div>
            <div class="stat-badge attack">
                <div style="font-size: 0.8rem;">⚔️ ATT</div>
                <div style="font-weight: bold;">{attack}</div>
            </div>
            <div class="stat-badge defense">
                <div style="font-size: 0.8rem;">🛡️ DEF</div>
                <div style="font-weight: bold;">{defense}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Actions ennemis (simples)
    st.markdown("### ⚔️ Actions Ennemi")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⚔️ Attaquer", key=f"sandbox_enemy_attack_{combatant['id']}", use_container_width=True):
            enemy_attack_action(char)
    
    with col2:
        if st.button("🛡️ Défendre", key=f"sandbox_enemy_defend_{combatant['id']}", use_container_width=True):
            enemy_defend_action(char)
    
    with col3:
        if st.button("⏭️ Passer", key=f"sandbox_enemy_skip_{combatant['id']}", use_container_width=True):
            skip_turn_action()

def display_abilities_prototype_grid(char: Character, combatant_id: str):
    """Grille capacités 3x2 EXACTE du prototype avec cartes cliquables"""
    if not hasattr(char, 'abilities') or not char.abilities:
        st.markdown("### 🔮 Capacités Spéciales (6 disponibles)")
        st.info("Aucune capacité disponible")
        return
    
    st.markdown("### 🔮 Capacités Spéciales (6 disponibles)")
    
    # Grille 3x2 avec cartes entièrement cliquables
    for row in range(2):
        cols = st.columns(3)
        for col_idx in range(3):
            ability_index = row * 3 + col_idx
            
            with cols[col_idx]:
                if ability_index < len(char.abilities):
                    ability = char.abilities[ability_index]
                    display_clickable_ability_card(char, ability, combatant_id, ability_index)
                else:
                    # Emplacement vide
                    st.markdown("""
                    <div style="background: #555; border: 2px dashed #777; border-radius: 10px; 
                                padding: 15px; text-align: center; color: #999; min-height: 80px;
                                display: flex; align-items: center; justify-content: center;">
                        <strong>Vide</strong>
                    </div>
                    """, unsafe_allow_html=True)

def display_clickable_ability_card(char: Character, ability, combatant_id: str, ability_index: int):
    """Carte capacité ENTIÈREMENT CLIQUABLE comme le prototype"""
    # Vérification disponibilité
    can_use = ability.ability_number in getattr(char, 'unlocked_abilities', [])
    current_spells = getattr(char, 'current_spells', char.get_total_spells())
    has_spells = ability.spell_cost <= current_spells
    
    is_available = can_use and has_spells
    
    # Badge et couleurs selon disponibilité
    if is_available:
        badge_text = f"{ability.spell_cost}/1"
        badge_class = "available"
        button_type = "primary"
        disabled = False
    else:
        badge_text = "0/1"
        badge_class = "unavailable"
        button_type = "secondary"
        disabled = True
    
    # Type d'icône
    type_icon = "🔮" if ability.spell_cost > 0 else "⚔️"
    
    # Nom et description courts
    short_name = ability.name if len(ability.name) <= 15 else ability.name[:12] + "..."
    short_desc = ability.description[:40] + "..." if len(ability.description) > 40 else ability.description
    
    # Bouton ENTIER qui ressemble à la carte prototype
    button_key = f"sandbox_ability_card_{combatant_id}_{ability_index}"
    
    if st.button(
        f"""
{type_icon} {short_name}
Coût: {ability.spell_cost} Action
{short_desc}
        """.strip(),
        key=button_key,
        type=button_type,
        disabled=disabled,
        use_container_width=True,
        help=f"Badge: {badge_text}"
    ):
        if is_available:
            use_ability_action(char, ability)

def display_actions_and_potions_prototype(char: Character, combatant_id: str):
    """Colonne droite: Actions + Potions EXACTE du prototype"""
    
    # === ACTIONS DE BASE EMPILÉES ===
    st.markdown("### ⚡ Actions de Base")
    
    # Attaque
    if st.button("❌ Attaque Basique", key=f"sandbox_action_attack_{combatant_id}", 
                type="primary", use_container_width=True):
        st.session_state.sandbox_selected_action = 'attack'
        st.success("⚔️ Attaque sélectionnée")
    
    # Défense
    if st.button("🛡️ Se Défendre", key=f"sandbox_action_defend_{combatant_id}", 
                use_container_width=True):
        st.session_state.sandbox_selected_action = 'defend'
        st.info("🛡️ Défense sélectionnée")
    
    # Passer
    if st.button("📋 Passer le Tour", key=f"sandbox_action_skip_{combatant_id}", 
                use_container_width=True):
        skip_turn_action()
    
    # === POTIONS GRILLE 2x2 ===
    st.markdown("### 🧪 Potions (équipées)")
    
    if hasattr(char, 'health_potions') and char.health_potions:
        potions_summary = char.get_potions_summary()
        
        # Grille 2x2 comme le prototype
        col1, col2 = st.columns(2)
        
        with col1:
            # Soin (en haut à gauche)
            small_count = potions_summary['small_count']
            if small_count > 0:
                if st.button(f"🩸 Soin\n{small_count}", 
                           key=f"sandbox_potion_soin_{combatant_id}",
                           use_container_width=True):
                    use_potion_action(char, 'small')
            else:
                st.button(f"🩸 Soin\n0", disabled=True, use_container_width=True)
            
            # Vide (en bas à gauche)
            st.button("🫙 Vide\n0", disabled=True, use_container_width=True)
        
        with col2:
            # Force (en haut à droite - placeholder)
            st.button("💪 Force\n1", disabled=True, use_container_width=True)
            
            # Vitesse (en bas à droite)
            large_count = potions_summary['large_count']
            if large_count > 0:
                if st.button(f"❤️‍🩹 Vitesse\n{large_count}", 
                           key=f"sandbox_potion_vitesse_{combatant_id}",
                           use_container_width=True):
                    use_potion_action(char, 'large')
            else:
                st.button("❤️‍🩹 Vitesse\n0", disabled=True, use_container_width=True)
    else:
        st.info("Aucune potion équipée")

# === ACTIONS DE COMBAT ===

def use_ability_action(char: Character, ability):
    """Utilise une capacité"""
    if hasattr(char, 'use_ability'):
        action = char.use_ability(ability)
        if action.success:
            st.session_state.sandbox_combat_log.append(f"🔮 {char.name} utilise {ability.name}")
            save_game_state(f"{char.name} utilise {ability.name}")
            next_turn()
            st.success(f"✅ {ability.name} utilisée !")
            st.rerun()
        else:
            st.error(f"❌ Impossible d'utiliser {ability.name}")

def use_potion_action(char: Character, potion_type: str):
    """Utilise une potion"""
    if hasattr(char, 'use_health_potion'):
        result = char.use_health_potion()
        if result['success']:
            st.session_state.sandbox_combat_log.append(f"🧪 {char.name} boit une potion: {result['message']}")
            save_game_state(f"{char.name} utilise potion")
            st.success(f"✅ Potion utilisée ! {result['message']}")
        else:
            st.error(f"❌ {result['message']}")

def enemy_attack_action(char: Enemy):
    """Action d'attaque pour ennemi"""
    st.session_state.sandbox_combat_log.append(f"⚔️ {char.name} attaque")
    save_game_state(f"{char.name} attaque")
    next_turn()
    st.success(f"⚔️ {char.name} attaque !")
    st.rerun()

def enemy_defend_action(char: Enemy):
    """Action de défense pour ennemi"""
    st.session_state.sandbox_combat_log.append(f"🛡️ {char.name} se défend")
    save_game_state(f"{char.name} se défend")
    next_turn()
    st.info(f"🛡️ {char.name} se défend !")
    st.rerun()

def skip_turn_action():
    """Passe le tour"""
    current = get_current_combatant()
    if current:
        char_name = current['character'].name
        st.session_state.sandbox_combat_log.append(f"⏭️ {char_name} passe son tour")
        save_game_state(f"{char_name} passe son tour")
        next_turn()
        st.info(f"⏭️ {char_name} passe son tour")
        st.rerun()

def next_turn():
    """Passe au tour suivant"""
    if not st.session_state.sandbox_combatants:
        return
    
    st.session_state.sandbox_current_turn_index = (st.session_state.sandbox_current_turn_index + 1) % len(st.session_state.sandbox_combatants)
    
    if st.session_state.sandbox_current_turn_index == 0:
        st.session_state.sandbox_round_number += 1
        st.session_state.sandbox_combat_log.append(f"=== ROUND {st.session_state.sandbox_round_number} ===")

# === UTILITAIRES ===

def get_current_combatant() -> Optional[Dict]:
    """Retourne le combattant actuel"""
    if (st.session_state.sandbox_combatants and 
        0 <= st.session_state.sandbox_current_turn_index < len(st.session_state.sandbox_combatants)):
        return st.session_state.sandbox_combatants[st.session_state.sandbox_current_turn_index]
    return None

def check_teams_configured() -> bool:
    """Vérifie si les équipes sont configurées"""
    heroes = st.session_state.get('selected_heroes', [])
    enemies = st.session_state.get('selected_enemies', [])
    return len(heroes) >= 2 and len(enemies) >= 1

def generate_initiative():
    """Génère l'ordre d'initiative"""
    for combatant in st.session_state.sandbox_combatants:
        roll = random.randint(1, 20)
        combatant['initiative'] = roll
    
    # Tri par initiative décroissante
    st.session_state.sandbox_combatants.sort(key=lambda x: x['initiative'], reverse=True)
    
    # Log
    st.session_state.sandbox_combat_log.append("=== ORDRE D'INITIATIVE ===")
    for i, c in enumerate(st.session_state.sandbox_combatants):
        name = c['character'].name
        init = c['initiative']
        st.session_state.sandbox_combat_log.append(f"{i+1}. {name}: {init}")
    
    save_game_state("Initiative générée")

def restore_previous_state():
    """Restaure l'état précédent"""
    if st.session_state.sandbox_history_index > 0:
        st.session_state.sandbox_history_index -= 1
        state = st.session_state.sandbox_game_history[st.session_state.sandbox_history_index]
        
        st.session_state.sandbox_combatants = deepcopy(state['combatants'])
        st.session_state.sandbox_current_turn_index = state['turn_index']
        st.session_state.sandbox_round_number = state['round_number']
        st.session_state.sandbox_combat_log = state['log'].copy()

def restore_next_state():
    """Restaure l'état suivant"""
    if st.session_state.sandbox_history_index < len(st.session_state.sandbox_game_history) - 1:
        st.session_state.sandbox_history_index += 1
        state = st.session_state.sandbox_game_history[st.session_state.sandbox_history_index]
        
        st.session_state.sandbox_combatants = deepcopy(state['combatants'])
        st.session_state.sandbox_current_turn_index = state['turn_index']
        st.session_state.sandbox_round_number = state['round_number']
        st.session_state.sandbox_combat_log = state['log'].copy()

def reset_sandbox():
    """Reset complet du sandbox"""
    keys_to_reset = [
        'sandbox_initialized', 'sandbox_phase', 'sandbox_combatants',
        'sandbox_current_turn_index', 'sandbox_round_number', 
        'sandbox_selected_action', 'sandbox_selected_target',
        'sandbox_combat_log', 'sandbox_game_history', 'sandbox_history_index'
    ]
    
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

# === INTERFACE PRINCIPALE PROTOTYPE ===

def main_sandbox_tab():
    """Interface principale Mode Sandbox - Version Prototype Exacte"""
    # Application du thème prototype
    apply_sandbox_theme()
    
    st.title("🎮 Mode Sandbox")
    st.caption("Interface Capacités Héros - Mode Sandbox")
    
    # Initialisation
    init_sandbox_state()
    
    # Vérification configuration
    if not check_teams_configured():
        st.markdown("""
        <div class="guidance-compact">
            🔧 Configuration Requise - Allez dans l'onglet Sélection pour configurer vos équipes (2+ héros, 1+ ennemi)
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📋 **Étapes Requises :**")
        st.markdown("1. **🏰 Onglet \"Sélection\"** → Choisir 2+ héros et 1+ ennemi")
        st.markdown("2. **🔄 Revenir ici** → Le Mode Sandbox se configurera automatiquement")  
        st.markdown("3. **🎮 Jouer** → Contrôlez manuellement tous les personnages")
        return
    
    # Phase selon l'état
    phase = st.session_state.sandbox_phase
    
    if phase == 'CONFIG':
        # Préparation des combattants
        combatants = prepare_combatants_for_sandbox()
        if combatants:
            st.session_state.sandbox_combatants = combatants
            st.session_state.sandbox_phase = 'INITIATIVE'
            st.rerun()
        else:
            st.error("❌ Erreur préparation des équipes")
            return
    
    elif phase == 'INITIATIVE':
        # Interface guidance prototype
        display_guidance_banner_prototype()
        
        st.info("🎲 **Génération de l'ordre d'initiative**")
        # Bouton EXEMPT bordeaux
        if st.button("🎲 Générer Initiative et Commencer", key="sandbox_generate_initiative", type="primary", use_container_width=True):
            generate_initiative()
            st.session_state.sandbox_phase = 'COMBAT'
            st.session_state.sandbox_current_turn_index = 0
            st.rerun()
    
    elif phase == 'COMBAT':
        # Interface guidance prototype
        display_guidance_banner_prototype()
        
        current = get_current_combatant()
        if current:
            # Interface PROTOTYPE selon faction
            if current['faction'] == 'hero':
                display_hero_interface_prototype(current)
            else:
                display_enemy_interface_prototype(current)
    
    # Journal de combat (toujours visible mais compact)
    if st.session_state.sandbox_combat_log:
        st.markdown("### 📜 **Journal de Combat**")
        with st.expander("Voir les dernières actions", expanded=False):
            for line in st.session_state.sandbox_combat_log[-10:]:
                st.text(line)
    
    # Contrôles historique avec boutons EXEMPTS bordeaux
    if st.session_state.sandbox_game_history:
        st.markdown("### 🕒 **Historique**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            can_undo = st.session_state.sandbox_history_index > 0
            if st.button("⏪ Annuler", key="sandbox_undo", disabled=not can_undo, use_container_width=True):
                restore_previous_state()
                st.rerun()
        
        with col2:
            can_redo = st.session_state.sandbox_history_index < len(st.session_state.sandbox_game_history) - 1
            if st.button("⏩ Refaire", key="sandbox_redo", disabled=not can_redo, use_container_width=True):
                restore_next_state()
                st.rerun()
        
        with col3:
            if st.button("🔄 Reset Combat", key="sandbox_reset", use_container_width=True):
                reset_sandbox()
                st.rerun()

# Point d'entrée principal
if __name__ == "__main__":
    main_sandbox_tab()