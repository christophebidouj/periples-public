# ═══════════════════════════════════════════════════════════
# 📁 STRUCTURE DE FICHIERS ISOLÉE
# ═══════════════════════════════════════════════════════════

# 1. Créer un nouveau fichier : sandbox_interface.py
# 2. Modifier SEULEMENT l'onglet 4 dans votre fichier principal
# 3. Aucun impact sur le reste du code

# ═══════════════════════════════════════════════════════════
# 📄 Nouveau fichier : sandbox_interface.py
# ═══════════════════════════════════════════════════════════

"""
sandbox_interface.py
Interface sandbox isolée - Développement parallèle
"""

import streamlit as st
import random
from copy import deepcopy

# ═══════════════════════════════════════════════════════════
# 🎮 INTERFACE SANDBOX COMPLÈTE
# ═══════════════════════════════════════════════════════════

def render_sandbox_tab():
    """Interface principale du mode sandbox"""
    
    # Vérification des équipes configurées
    if not check_teams_configured():
        render_sandbox_redirect()
        return
    
    # Initialisation du mode sandbox
    if 'sandbox_state' not in st.session_state:
        initialize_sandbox_mode()
    
    # Interface principale
    render_guidance_banner()
    
    col_control, col_battlefield = st.columns([1, 2])
    
    with col_control:
        render_character_control_panel()
    
    with col_battlefield:
        render_battlefield_overview()
    
    # Contrôles additionnels
    render_history_controls()
    
    # Debug info (peut être supprimé plus tard)
    render_debug_info()


def check_teams_configured():
    """Vérifie si les équipes sont configurées"""
    return (
        'hero_team' in st.session_state and 
        'enemy_team' in st.session_state and
        len(st.session_state.hero_team) > 0 and
        len(st.session_state.enemy_team) > 0
    )


def render_sandbox_redirect():
    """Message de redirection si équipes non configurées"""
    st.warning("⚠️ **Mode Sandbox - Équipes non configurées**")
    st.info("""
    **Pour utiliser le Mode Sandbox :**
    1. 🛡️ Allez dans l'onglet **"Configuration des Équipes"**
    2. ⚔️ Configurez vos héros et ennemis
    3. 🎮 Revenez ici pour le combat manuel
    """)
    
    st.markdown("---")
    st.caption("💡 Le Mode Sandbox vous permet de contrôler tous les personnages manuellement")


def initialize_sandbox_mode():
    """Initialise l'état du mode sandbox - ISOLATION COMPLÈTE"""
    
    # État sandbox complètement séparé
    st.session_state.sandbox_state = {
        'phase': 'SETUP',
        'active_combatant_index': 0,
        'turn_number': 1,
        'combat_ended': False,
        'winner': None,
        'initialized': True
    }
    
    # Historique isolé
    st.session_state.sandbox_history = []
    st.session_state.history_index = -1
    
    # COPIE ISOLÉE des équipes (pas de modification des originaux)
    heroes = deepcopy(st.session_state.get('hero_team', []))
    enemies = deepcopy(st.session_state.get('enemy_team', []))
    
    # Préparation des combattants SANDBOX uniquement
    st.session_state.sandbox_combatants = prepare_sandbox_combatants(heroes, enemies)
    
    # Génération initiative
    generate_initiative_order()


def prepare_sandbox_combatants(heroes, enemies):
    """Prépare les combattants UNIQUEMENT pour le sandbox"""
    
    all_combatants = []
    
    # Héros - Structure sandbox isolée
    for i, hero in enumerate(heroes):
        combatant = {
            'character': hero,  # Référence au character original
            'faction': 'hero',
            'sandbox_id': f'hero_{i}',  # ID unique sandbox
            'current_hp': getattr(hero, 'hp', 100),
            'max_hp': getattr(hero, 'hp', 100),
            'is_alive': True,
            'status_effects': [],
            # Placeholders pour futures intégrations
            'equipment_applied': False,
            'abilities_remaining': {},
            'combat_log': []
        }
        all_combatants.append(combatant)
    
    # Ennemis - Même structure
    for i, enemy in enumerate(enemies):
        combatant = {
            'character': enemy,
            'faction': 'enemy',
            'sandbox_id': f'enemy_{i}',
            'current_hp': getattr(enemy, 'hp', 100),
            'max_hp': getattr(enemy, 'hp', 100),
            'is_alive': True,
            'status_effects': [],
            'equipment_applied': False,
            'abilities_remaining': {},
            'combat_log': []
        }
        all_combatants.append(combatant)
    
    return all_combatants


def generate_initiative_order():
    """Génère l'ordre d'initiative - Version sandbox simple"""
    
    combatants = st.session_state.sandbox_combatants
    
    # Initiative basique : agilité + dé 20
    for combatant in combatants:
        char = combatant['character']
        base_agility = getattr(char, 'agilite', 10)
        roll = random.randint(1, 20)
        combatant['initiative_roll'] = base_agility + roll
        combatant['initiative_detail'] = f"{base_agility} + {roll}"
    
    # Tri par initiative décroissante
    combatants.sort(key=lambda x: x['initiative_roll'], reverse=True)
    
    # Mise à jour et passage en mode action
    st.session_state.sandbox_combatants = combatants
    st.session_state.sandbox_state['phase'] = 'WAITING_ACTION'
    
    # Message d'initiative
    st.success("🎯 **Ordre d'initiative généré !**")


def render_guidance_banner():
    """Bannière de guidance contextuelle"""
    
    state = st.session_state.sandbox_state
    phase = state['phase']
    
    if phase == 'SETUP':
        st.info("🎮 **Mode Sandbox** - Initialisation en cours...")
        return
    
    if phase in ['WAITING_ACTION', 'TARGET_SELECTION', 'CONFIRM_ACTION']:
        active_combatant = get_active_combatant()
        faction = active_combatant['faction']
        char_name = getattr(active_combatant['character'], 'nom', 'Inconnu')
        
        # Style selon faction
        if faction == 'hero':
            emoji = "🛡️"
            color = "#2d5a27"
            faction_text = "Héros"
        else:
            emoji = "👹"
            color = "#5a2727"
            faction_text = "Ennemi"
        
        # Message selon phase
        if phase == 'WAITING_ACTION':
            message = f"{emoji} **Vous contrôlez {char_name} ({faction_text})** - Choisissez une action"
            help_text = "💡 Sélectionnez une action dans le panneau de contrôle"
        elif phase == 'TARGET_SELECTION':
            message = f"{emoji} **{char_name}** - Sélectionnez une cible"
            help_text = "🎯 Cliquez sur 'Cibler' sous un personnage"
        elif phase == 'CONFIRM_ACTION':
            message = f"{emoji} **{char_name}** - Confirmez votre action"
            help_text = "✅ Vérifiez et confirmez l'exécution"
        
        # Affichage avec style
        banner_style = f"background-color: {color}; color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;"
        st.markdown(f'<div style="{banner_style}">{message}</div>', unsafe_allow_html=True)
        st.caption(help_text)


def get_active_combatant():
    """Retourne le combattant actuellement actif"""
    active_index = st.session_state.sandbox_state['active_combatant_index']
    return st.session_state.sandbox_combatants[active_index]


def render_character_control_panel():
    """Panneau de contrôle du personnage actif"""
    
    st.subheader("🎯 Contrôles")
    
    phase = st.session_state.sandbox_state['phase']
    
    if phase == 'WAITING_ACTION':
        render_action_menu()
    elif phase == 'TARGET_SELECTION':
        render_target_selection_help()
    elif phase == 'CONFIRM_ACTION':
        render_action_confirmation()
    else:
        st.info("⏳ En attente...")


def render_action_menu():
    """Menu des actions disponibles"""
    
    active_combatant = get_active_combatant()
    char_name = getattr(active_combatant['character'], 'nom', 'Inconnu')
    
    st.write(f"**Actions pour {char_name} :**")
    
    # Action Attaquer
    if st.button("⚔️ Attaquer", use_container_width=True, help="Attaque de base"):
        st.session_state.sandbox_state['selected_action'] = 'attack'
        st.session_state.sandbox_state['action_details'] = 'Attaque de base'
        st.session_state.sandbox_state['phase'] = 'TARGET_SELECTION'
        st.rerun()
    
    # Capacités (placeholder pour l'intégration future)
    if st.button("✨ Capacités", disabled=True, use_container_width=True, 
                help="Capacités spéciales (en développement)"):
        st.info("🔧 Système de capacités en cours de développement")
    
    # Passer le tour
    if st.button("⏭️ Passer le tour", use_container_width=True, help="Passer au personnage suivant"):
        next_combatant()
        st.success(f"⏭️ Tour passé !")
        st.rerun()


def render_target_selection_help():
    """Aide pour la sélection de cible"""
    
    st.info("🎯 **Sélection de cible**")
    st.write("Cliquez sur 'Cibler' sous un personnage dans la vue d'ensemble.")
    
    # Bouton retour
    if st.button("↩️ Retour aux actions", use_container_width=True):
        cancel_action()
        st.rerun()


def render_action_confirmation():
    """Confirmation d'action"""
    
    st.success("✅ **Action prête à exécuter**")
    
    # Détails de l'action
    action_details = st.session_state.sandbox_state.get('action_details', 'Action inconnue')
    target_index = st.session_state.sandbox_state.get('selected_target', -1)
    
    if target_index >= 0:
        target = st.session_state.sandbox_combatants[target_index]
        target_name = getattr(target['character'], 'nom', 'Inconnu')
        
        st.write(f"**Action :** {action_details}")
        st.write(f"**Cible :** {target_name}")
        st.write(f"**PV cible :** {target['current_hp']}/{target['max_hp']}")
    
    # Boutons confirmation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Confirmer", use_container_width=True, type="primary"):
            execute_sandbox_action()
            st.rerun()
    
    with col2:
        if st.button("❌ Annuler", use_container_width=True):
            cancel_action()
            st.rerun()


def render_battlefield_overview():
    """Vue d'ensemble du champ de bataille"""
    
    st.subheader("⚔️ Champ de Bataille")
    
    # Séparation par faction
    heroes = [c for c in st.session_state.sandbox_combatants if c['faction'] == 'hero']
    enemies = [c for c in st.session_state.sandbox_combatants if c['faction'] == 'enemy']
    
    # Affichage héros
    if heroes:
        st.write("**🛡️ Équipe des Héros**")
        render_combatant_cards(heroes)
    
    st.divider()
    
    # Affichage ennemis
    if enemies:
        st.write("**👹 Équipe Ennemie**")
        render_combatant_cards(enemies)


def render_combatant_cards(combatants):
    """Affiche les cartes des combattants"""
    
    # Calcul du nombre de colonnes
    num_cols = min(len(combatants), 3)
    cols = st.columns(num_cols) if num_cols > 1 else [st]
    
    for i, combatant in enumerate(combatants):
        with cols[i % len(cols)]:
            render_single_combatant_card(combatant, i)


def render_single_combatant_card(combatant, display_index):
    """Carte individuelle d'un combattant"""
    
    char = combatant['character']
    char_name = getattr(char, 'nom', f'Combattant {display_index + 1}')
    is_active = is_combatant_active(combatant)
    faction = combatant['faction']
    
    # Styles selon l'état
    if is_active:
        border_color = "#ffd700"  # Or pour actif
        background = "#4a4a2a"
        active_indicator = "⭐ "
    elif faction == 'hero':
        border_color = "#28a745"  # Vert héros
        background = "#1a3a1a"
        active_indicator = ""
    else:
        border_color = "#dc3545"  # Rouge ennemi
        background = "#3a1a1a"
        active_indicator = ""
    
    # État de vie
    current_hp = combatant['current_hp']
    max_hp = combatant['max_hp']
    hp_percentage = (current_hp / max_hp * 100) if max_hp > 0 else 0
    
    # Couleur barre de vie
    if hp_percentage > 60:
        hp_color = "#28a745"
    elif hp_percentage > 30:
        hp_color = "#ffc107"
    else:
        hp_color = "#dc3545"
    
    # Contenu de la carte
    card_content = f"""
    <div style="
        border: 2px solid {border_color};
        background-color: {background};
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    ">
        <h4 style="margin: 0 0 0.5rem 0; color: white;">
            {active_indicator}{char_name}
        </h4>
        <div style="
            background-color: #333;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 0.5rem;
        ">
            <div style="
                background-color: {hp_color};
                height: 8px;
                width: {hp_percentage}%;
                transition: width 0.3s ease;
            "></div>
        </div>
        <p style="margin: 0.2rem 0; color: #ccc; font-size: 0.9rem;">
            💚 PV: {current_hp}/{max_hp}
        </p>
        <p style="margin: 0; font-size: 0.8rem; color: #aaa;">
            🎯 Initiative: {combatant.get('initiative_roll', 0)}
        </p>
    </div>
    """
    
    st.markdown(card_content, unsafe_allow_html=True)
    
    # Bouton ciblage si en sélection
    phase = st.session_state.sandbox_state['phase']
    if phase == 'TARGET_SELECTION':
        combatant_index = st.session_state.sandbox_combatants.index(combatant)
        button_key = f"target_{combatant['sandbox_id']}"
        
        if st.button(f"🎯 Cibler", key=button_key, use_container_width=True):
            st.session_state.sandbox_state['selected_target'] = combatant_index
            st.session_state.sandbox_state['phase'] = 'CONFIRM_ACTION'
            st.rerun()


def is_combatant_active(combatant):
    """Vérifie si le combattant est actuellement actif"""
    active_index = st.session_state.sandbox_state['active_combatant_index']
    current_active = st.session_state.sandbox_combatants[active_index]
    return current_active['sandbox_id'] == combatant['sandbox_id']


def next_combatant():
    """Passe au combattant suivant"""
    
    active_index = st.session_state.sandbox_state['active_combatant_index']
    total_combatants = len(st.session_state.sandbox_combatants)
    
    # Recherche du prochain combattant vivant
    next_index = (active_index + 1) % total_combatants
    
    # Si on revient au début, nouveau tour
    if next_index == 0:
        st.session_state.sandbox_state['turn_number'] += 1
    
    st.session_state.sandbox_state['active_combatant_index'] = next_index
    st.session_state.sandbox_state['phase'] = 'WAITING_ACTION'
    
    # Nettoyage des actions en cours
    cancel_action(silent=True)


def cancel_action(silent=False):
    """Annule l'action en cours"""
    
    # Nettoyage des états d'action
    keys_to_remove = ['selected_action', 'action_details', 'selected_target']
    for key in keys_to_remove:
        if key in st.session_state.sandbox_state:
            del st.session_state.sandbox_state[key]
    
    # Retour à l'état d'attente
    st.session_state.sandbox_state['phase'] = 'WAITING_ACTION'
    
    if not silent:
        st.info("Action annulée")


def execute_sandbox_action():
    """Exécute l'action sélectionnée - VERSION BASIQUE"""
    
    action = st.session_state.sandbox_state.get('selected_action')
    target_index = st.session_state.sandbox_state.get('selected_target')
    
    if action == 'attack' and target_index is not None:
        # Récupération attaquant et cible
        attacker = get_active_combatant()
        target = st.session_state.sandbox_combatants[target_index]
        
        attacker_name = getattr(attacker['character'], 'nom', 'Attaquant')
        target_name = getattr(target['character'], 'nom', 'Cible')
        
        # CALCUL TEMPORAIRE - Sera remplacé par le vrai moteur
        base_damage = getattr(attacker['character'], 'force', 10)
        damage_roll = random.randint(1, 6)
        total_damage = base_damage + damage_roll
        
        # Application des dégâts
        target['current_hp'] = max(0, target['current_hp'] - total_damage)
        
        # Vérification mort
        if target['current_hp'] <= 0:
            target['is_alive'] = False
            death_msg = f"💀 {target_name} est vaincu !"
        else:
            death_msg = ""
        
        # Messages de résultat
        st.success(f"⚔️ **{attacker_name}** attaque **{target_name}** !")
        st.info(f"🎲 Dégâts: {base_damage} (Force) + {damage_roll} (Dé) = **{total_damage}**")
        
        if death_msg:
            st.error(death_msg)
        
        # Log dans l'historique du combattant
        log_entry = f"Tour {st.session_state.sandbox_state['turn_number']}: Attaque {target_name} ({total_damage} dégâts)"
        attacker['combat_log'].append(log_entry)
    
    # Nettoyage et passage au suivant
    cancel_action(silent=True)
    next_combatant()


def render_history_controls():
    """Contrôles d'historique - Structure de base"""
    
    st.subheader("📚 Historique & Contrôles")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Placeholder pour undo
        st.button("⏪ Annuler", disabled=True, help="Historique (prochaine version)")
    
    with col2:
        # Placeholder pour redo
        st.button("⏩ Refaire", disabled=True, help="Historique (prochaine version)")
    
    with col3:
        # Info tour actuel
        turn_num = st.session_state.sandbox_state.get('turn_number', 1)
        st.metric("Tour", turn_num)
    
    with col4:
        # Reset combat
        if st.button("🔄 Reset", help="Redémarre le combat"):
            reset_sandbox_combat()
            st.rerun()


def reset_sandbox_combat():
    """Reset complet du combat sandbox"""
    
    # Suppression de tous les états sandbox
    keys_to_remove = ['sandbox_state', 'sandbox_combatants', 'sandbox_history', 'history_index']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("🔄 Combat réinitialisé !")


def render_debug_info():
    """Informations de debug (optionnel - peut être supprimé)"""
    
    with st.expander("🔧 Debug Info (Développement)"):
        
        if 'sandbox_state' in st.session_state:
            debug_data = {
                'Phase': st.session_state.sandbox_state['phase'],
                'Combattant actif': st.session_state.sandbox_state['active_combatant_index'],
                'Tour': st.session_state.sandbox_state['turn_number'],
                'Total combattants': len(st.session_state.sandbox_combatants),
            }
            
            # Actions en cours
            if 'selected_action' in st.session_state.sandbox_state:
                debug_data['Action sélectionnée'] = st.session_state.sandbox_state['selected_action']
            if 'selected_target' in st.session_state.sandbox_state:
                debug_data['Cible sélectionnée'] = st.session_state.sandbox_state['selected_target']
            
            st.json(debug_data)
        else:
            st.write("État sandbox non initialisé")


# ═══════════════════════════════════════════════════════════
# 🎯 POINT D'ENTRÉE PRINCIPAL
# ═══════════════════════════════════════════════════════════

def main_sandbox_tab():
    """Point d'entrée principal pour l'onglet sandbox"""
    
    st.title("🎮 Mode Sandbox")
    st.caption("Contrôlez tous les personnages manuellement pour tester les mécaniques de combat")
    
    render_sandbox_tab()


# ═══════════════════════════════════════════════════════════
# 📝 MODIFICATION FICHIER PRINCIPAL - ONGLET 4 UNIQUEMENT
# ═══════════════════════════════════════════════════════════

"""
Dans votre fichier principal, modifiez SEULEMENT la section de l'onglet 4 :

# Import du module sandbox
import sandbox_interface

# Dans la section des onglets
if selected_tab == "Mode Sandbox":  # ou le nom de votre onglet 4
    sandbox_interface.main_sandbox_tab()

# Ou si vous utilisez des elif :
elif selected_tab == "Mode Sandbox":
    sandbox_interface.main_sandbox_tab()

C'EST TOUT ! Aucune autre modification nécessaire.
"""