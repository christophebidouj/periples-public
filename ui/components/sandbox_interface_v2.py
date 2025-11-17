"""
Sandbox Interface V2 - Style Arène
Interface avec ciblage manuel, initiative et système Undo/Redo
RÉUTILISE l'architecture existante : TurnManager + CombatActions
"""

import streamlit as st
import random
from typing import List, Dict, Optional
from copy import deepcopy

from models.character import Character, Enemy
from models.combat.combat_engine import CombatEngine
from models.combat.turn_manager import TurnManager
from models.combat.combat_actions import CombatActions
from models.combat.spell_manager import SpellManager
from models.combat.initiative_manager import InitiativeManager
from models.rules_engine import GameRules
from utils.data_loader import DataLoader
from ui.components.ui_elements import get_hero_image_path, load_hero_image_base64, get_hero_icon
from ui.styling import get_hero_card_style

# === CSS STYLE ARÈNE ===
# ===tour par tour guidé ===

def apply_sandbox_v2_theme():
    """Applique le thème visuel de l'Arène"""
    st.markdown("""
    <style>
    /* === THÈME ARÈNE === */
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

    /* === GUIDANCE BANNER === */
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
    .guidance-config { background: linear-gradient(135deg, #3498db, #2980b9); }

    /* === CIBLAGE STYLE ARÈNE === */
    .target-card {
        background: linear-gradient(135deg, #34495e, #2c3e50);
        border: 2px solid #7f8c8d;
        border-radius: 10px;
        padding: 12px;
        margin: 8px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
    }

    .target-card:hover {
        border-color: #3498db;
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4);
    }

    .target-info {
        flex-grow: 1;
    }

    .target-stats {
        display: flex;
        gap: 15px;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# === INITIALISATION AVEC HISTORIQUE ===

def init_sandbox_state():
    """Initialise état Sandbox avec historique"""
    defaults = {
        'sandbox_v2_initialized': False,
        'sandbox_v2_heroes': [],
        'sandbox_v2_enemies': [],
        'sandbox_v2_phase': 'CONFIG',
        'sandbox_v2_combatants': [],
        'sandbox_v2_current_turn_index': 0,
        'sandbox_v2_round_number': 1,
        'sandbox_v2_log': [],
        'sandbox_v2_turn_manager': None,
        'sandbox_v2_adapter': None,
        'sandbox_v2_game_history': [],
        'sandbox_v2_history_index': -1,
        'sandbox_v2_action_state': None,  # Pour gérer le ciblage
        'sandbox_v2_current_actor': None,  # Personnage qui agit
        'sandbox_v2_last_selection': None,  # Mémoriser la dernière sélection
        'sandbox_v2_played_this_round': []  # Liste des IDs qui ont joué ce round (mode manuel)
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def save_game_state(description: str = "Action"):
    """Sauvegarde l'état pour Undo/Redo"""
    # Synchroniser les listes de héros/ennemis depuis les combattants avant de sauvegarder
    hero_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'hero']
    enemy_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'enemy']

    st.session_state.sandbox_v2_heroes = [c['character'] for c in hero_combatants]
    st.session_state.sandbox_v2_enemies = [c['character'] for c in enemy_combatants]

    state = {
        'combatants': deepcopy(st.session_state.sandbox_v2_combatants),
        'turn_index': st.session_state.sandbox_v2_current_turn_index,
        'round_number': st.session_state.sandbox_v2_round_number,
        'log': st.session_state.sandbox_v2_log.copy(),
        'played_this_round': st.session_state.sandbox_v2_played_this_round.copy(),
        'description': description
    }

    # Supprimer les états futurs si on est en train de refaire l'historique
    st.session_state.sandbox_v2_game_history = st.session_state.sandbox_v2_game_history[:st.session_state.sandbox_v2_history_index + 1]
    st.session_state.sandbox_v2_game_history.append(state)
    st.session_state.sandbox_v2_history_index += 1

def restore_previous_state():
    """Annuler - Restaure l'état précédent"""
    if st.session_state.sandbox_v2_history_index > 0:
        st.session_state.sandbox_v2_history_index -= 1
        state = st.session_state.sandbox_v2_game_history[st.session_state.sandbox_v2_history_index]

        st.session_state.sandbox_v2_combatants = deepcopy(state['combatants'])
        st.session_state.sandbox_v2_current_turn_index = state['turn_index']
        st.session_state.sandbox_v2_round_number = state['round_number']
        st.session_state.sandbox_v2_log = state['log'].copy()
        st.session_state.sandbox_v2_played_this_round = state.get('played_this_round', []).copy()

        # Synchroniser héros/ennemis depuis les combattants
        hero_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'hero']
        enemy_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'enemy']
        st.session_state.sandbox_v2_heroes = [c['character'] for c in hero_combatants]
        st.session_state.sandbox_v2_enemies = [c['character'] for c in enemy_combatants]

def restore_next_state():
    """Refaire - Restaure l'état suivant"""
    if st.session_state.sandbox_v2_history_index < len(st.session_state.sandbox_v2_game_history) - 1:
        st.session_state.sandbox_v2_history_index += 1
        state = st.session_state.sandbox_v2_game_history[st.session_state.sandbox_v2_history_index]

        st.session_state.sandbox_v2_combatants = deepcopy(state['combatants'])
        st.session_state.sandbox_v2_current_turn_index = state['turn_index']
        st.session_state.sandbox_v2_round_number = state['round_number']
        st.session_state.sandbox_v2_log = state['log'].copy()
        st.session_state.sandbox_v2_played_this_round = state.get('played_this_round', []).copy()

        # Synchroniser héros/ennemis depuis les combattants
        hero_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'hero']
        enemy_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'enemy']
        st.session_state.sandbox_v2_heroes = [c['character'] for c in hero_combatants]
        st.session_state.sandbox_v2_enemies = [c['character'] for c in enemy_combatants]

# === INTERFACE CIBLAGE MANUEL STYLÉE ===

class ManualTargeting:
    """Interface UI pour ciblage manuel - Style Arène"""

    @staticmethod
    def select_enemy_for_hero_attack(
        hero: Character,
        enemies: List[Enemy],
        heroes: List[Character]
    ) -> Optional[Enemy]:
        """
        UI : Joueur choisit quel ennemi le héros attaque - Style Arène
        """
        alive_enemies = [e for e in enemies if e.is_alive()]

        if not alive_enemies:
            st.warning("❌ Aucun ennemi disponible !")
            return None

        st.markdown(f"""
        <div class="guidance-compact guidance-combat">
            🎯 {hero.name} attaque - Sélectionnez la cible
        </div>
        """, unsafe_allow_html=True)

        player_count = len([h for h in heroes if h.is_alive()])

        for enemy in alive_enemies:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                st.markdown(f"**{enemy.name}**")
            with col2:
                st.write(f"❤️ {enemy.current_health}/{enemy.max_health}")
            with col3:
                st.write(f"🛡️ {enemy.current_parade_tokens}")
            with col4:
                if st.button("🎯 Cibler", key=f"target_enemy_{enemy.name}_{id(enemy)}", type="primary", use_container_width=True):
                    return enemy

        return None

    @staticmethod
    def select_hero_for_enemy_attack(
        enemy: Enemy,
        heroes: List[Character]
    ) -> Optional[Character]:
        """
        UI : Joueur choisit quel héros l'ennemi attaque - Style Arène
        """
        alive_heroes = [h for h in heroes if h.is_alive()]

        if not alive_heroes:
            st.error("❌ Aucun héros vivant !")
            return None

        # Header compact (même style que héros)
        st.markdown(f"""
        <div class="guidance-compact guidance-combat">
            🎯 {enemy.name} attaque - Sélectionnez la cible
        </div>
        """, unsafe_allow_html=True)

        # Stats ennemi
        player_count = len(alive_heroes)
        stats = enemy.get_stats_for_players(player_count)
        st.write(f"**💥 Dégâts de l'attaque :** {stats['damage']}")

        st.markdown("---")

        # Liste héros avec cartes stylées
        for hero in alive_heroes:
            parade = hero.get_total_parade()
            damage_after_parade = max(0, stats['damage'] - parade)

            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

            with col1:
                st.write(f"**{hero.name}**")
            with col2:
                st.write(f"❤️ {hero.current_health}/{hero.get_total_health()}")
            with col3:
                st.write(f"🛡️ {parade}")
            with col4:
                if damage_after_parade > 0:
                    st.write(f"💔 -{damage_after_parade}")
                else:
                    st.write("✅ Bloqué")
            with col5:
                if st.button("🎯 Cibler", key=f"enemy_target_{hero.name}_{id(hero)}", type="primary", use_container_width=True):
                    return hero

        return None

# === ADAPTER TURNMANAGER POUR CIBLAGE MANUEL ===

class SandboxTurnManagerAdapter:
    """Adapter qui RÉUTILISE TurnManager existant avec ciblage manuel"""

    def __init__(self, turn_manager: TurnManager, combat_actions: CombatActions):
        self.turn_manager = turn_manager
        self.combat_actions = combat_actions

    def hero_turn_manual(
        self,
        hero: Character,
        enemies: List[Enemy],
        heroes: List[Character],
        player_count: int,
        log: List[str]
    ) -> bool:
        """Tour héros avec ciblage manuel - Retourne True si action effectuée"""
        hero.start_hero_turn()
        return False  # L'action sera gérée par les boutons de l'interface

    def enemy_turn_manual(
        self,
        enemy: Enemy,
        heroes: List[Character],
        player_count: int,
        log: List[str]
    ) -> Optional[Character]:
        """Tour ennemi avec ciblage manuel - Retourne la cible sélectionnée"""
        enemy.start_enemy_turn()
        target = ManualTargeting.select_hero_for_enemy_attack(enemy, heroes)
        return target

    def execute_enemy_attack(
        self,
        enemy: Enemy,
        target: Character,
        player_count: int,
        log: List[str]
    ):
        """Exécute l'attaque de l'ennemi sur la cible"""
        enemy_stats = enemy.get_stats_for_players(player_count)
        damage = enemy_stats['damage']

        damage_result = target.apply_damage_with_parade(damage)

        log.append(f"⚔️ {enemy.name} attaque {target.name} : {damage} dégâts")
        if damage_result['blocked_by_parade'] > 0:
            log.append(f"  🛡️ {damage_result['blocked_by_parade']} bloqués, {damage_result['health_damage']} aux PV")

        if not target.is_alive():
            log.append(f"💀 {target.name} est inconscient !")

# === CONFIGURATION COMBAT - RÉUTILISE LOGIQUE EXISTANTE ===

def configure_combat():
    """
    Configure combat - RÉUTILISE la logique de l'Arène pour charger correctement
    les héros avec leurs builds customisés et les ennemis
    """
    try:
        loader = DataLoader()

        heroes_codes = st.session_state.get('selected_heroes', [])
        enemies_codes = st.session_state.get('selected_enemies', [])

        if not heroes_codes or not enemies_codes:
            return False

        # Charger données
        heroes_data = loader.load_heroes()
        enemies_data = loader.load_enemies()
        equipment_data = loader.load_equipment()

        combatants = []
        player_count = len(heroes_codes)

        # === PRÉPARATION HÉROS avec builds customisés (LOGIQUE ARÈNE) ===
        current_builds = st.session_state.get('custom_builds', {})
        for hero_code in heroes_codes:
            hero_template = next((h for h in heroes_data if h.code == hero_code), None)
            if not hero_template:
                continue

            # DEEPCOPY pour avoir une instance unique par héros
            hero = deepcopy(hero_template)

            # Application build custom si existant, SINON build par défaut selon difficulté
            if hero_code in current_builds:
                # BUILD CUSTOM (Forge)
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
            else:
                # BUILD PAR DÉFAUT selon difficulté choisie (RÉUTILISE API existante)
                from hero_builds_data import get_hero_detailed_build

                # Récupérer difficulté choisie dans l'onglet Sélection
                hero_difficulties = st.session_state.get('hero_difficulties', {})
                difficulty_full = hero_difficulties.get(hero_code, "🔵 Normal")

                # Extraction du nom sans emoji (même logique que app.py)
                if "Facile" in difficulty_full:
                    difficulty = "Facile"
                elif "Difficile" in difficulty_full:
                    difficulty = "Difficile"
                else:
                    difficulty = "Normal"

                # Charger build détaillé depuis hero_builds_data.py
                build_config = get_hero_detailed_build(hero_code, difficulty)

                if build_config:
                    # Équipements
                    equipment_codes = build_config.get('equipment', [])
                    equipment_list = [eq for eq in equipment_data if eq.code in equipment_codes]
                    hero.equip_items(equipment_list, build_config.get('name', f'Build {difficulty}'))

                    # Potions
                    potions = build_config.get('potions', {})
                    if potions and hasattr(hero, 'set_potions_from_selection'):
                        hero.set_potions_from_selection(potions.get('small', 0), potions.get('large', 0))

                    # Capacités (abilities_level = nombre de capacités à débloquer)
                    abilities_level = build_config.get('abilities_level', 0)
                    if abilities_level > 0 and hasattr(hero, 'abilities'):
                        hero_abilities = loader.get_hero_abilities(hero_code)
                        if hero_abilities:
                            hero.add_abilities(hero_abilities)
                            # Débloquer capacités 1 à abilities_level
                            for num in range(1, min(abilities_level + 1, 7)):  # Max 6 capacités
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

        # === PRÉPARATION ENNEMIS (LOGIQUE ARÈNE) ===
        for idx, enemy_code in enumerate(enemies_codes):
            enemy_template = next((e for e in enemies_data if e.code == enemy_code), None)
            if enemy_template:
                # DEEPCOPY pour avoir une instance unique par ennemi
                enemy = deepcopy(enemy_template)
                enemy.initialize_for_combat(player_count)
                combatants.append({
                    'character': enemy,
                    'faction': 'enemy',
                    'initiative': 0,
                    'id': f"enemy_{enemy_code}_{idx}"  # ID unique avec index
                })

        st.session_state.sandbox_v2_combatants = combatants

        # Synchroniser les listes
        hero_combatants = [c for c in combatants if c['faction'] == 'hero']
        enemy_combatants = [c for c in combatants if c['faction'] == 'enemy']
        st.session_state.sandbox_v2_heroes = [c['character'] for c in hero_combatants]
        st.session_state.sandbox_v2_enemies = [c['character'] for c in enemy_combatants]

        # NOTE: On ne stocke plus sandbox_v2_initiative_enabled pour éviter les désynchronisations
        # On lit toujours directement depuis initiative_setting

        # Architecture existante
        rules = GameRules(
            ranged_attacks=True,
            magical_damage=True,
            criticals=True,
            abilities_enabled=True
        )

        spell_manager = SpellManager()
        combat_actions = CombatActions(spell_manager, rules)
        turn_manager = TurnManager(spell_manager, combat_actions)

        # Adapter
        st.session_state.sandbox_v2_turn_manager = turn_manager
        st.session_state.sandbox_v2_adapter = SandboxTurnManagerAdapter(
            turn_manager,
            combat_actions
        )

        # Initialiser sorts héros
        for hero_data in hero_combatants:
            spell_manager.initialize_spells(hero_data['character'])

        st.session_state.sandbox_v2_log = ["=== DÉBUT DU COMBAT ==="]

        # Sauvegarder l'état initial
        save_game_state("Début du combat")

        return True

    except Exception as e:
        st.error(f"❌ Erreur configuration: {e}")
        return False

# === GÉNÉRATION INITIATIVE ===

def generate_initiative():
    """
    Génère l'ordre d'initiative CONFORME AUX RÈGLES (page 26 du PDF):
    - Chaque combattant lance un dé à 20 faces
    - Ordre de jeu décroissant par initiative
    - En cas d'égalité : héros a priorité sur ennemi

    REFACTORISÉ : Utilise InitiativeManager (logique métier séparée de l'UI)
    """
    # LOGIQUE MÉTIER : Déléguer la génération et le tri au InitiativeManager
    InitiativeManager.roll_initiative(st.session_state.sandbox_v2_combatants)

    # LOGIQUE UI : Générer les logs et les ajouter au session_state
    log_lines = InitiativeManager.get_initiative_order_log(st.session_state.sandbox_v2_combatants)
    st.session_state.sandbox_v2_log.extend(log_lines)

    # Indiquer le début du combat
    st.session_state.sandbox_v2_log.append("")
    st.session_state.sandbox_v2_log.append("=== ROUND 1 ===")

    # LOGIQUE UI : Sauvegarder l'état du jeu (système Undo/Redo)
    save_game_state("Initiative générée")

def organize_teams_without_initiative():
    """
    Organise les combattants par équipe (héros puis ennemis) sans jets d'initiative
    Utilisé quand la checkbox "Initiative" est décochée dans l'onglet Sélection

    RÈGLE : Pas de jets de dés, ordre manuel choisi par l'utilisateur
    - Héros d'abord (ordre de sélection)
    - Ennemis ensuite (ordre de sélection)
    - Pas de tri par initiative (initiative = 0 pour tous)
    """
    # Séparer héros et ennemis
    hero_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'hero']
    enemy_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'enemy']

    # Pas d'initiative, on laisse à 0 pour tous
    for combatant in hero_combatants + enemy_combatants:
        combatant['initiative'] = 0

    # Réorganiser : héros d'abord, puis ennemis
    st.session_state.sandbox_v2_combatants = hero_combatants + enemy_combatants

    # Log de début de combat (pas d'ordre d'initiative)
    st.session_state.sandbox_v2_log.append("")
    st.session_state.sandbox_v2_log.append("=== MODE MANUEL - Sélectionnez qui joue ===")
    st.session_state.sandbox_v2_log.append("=== ROUND 1 ===")

    # Pas de tour actuel défini au départ (l'utilisateur choisit)
    st.session_state.sandbox_v2_current_turn_index = -1

    # Sauvegarder l'état initial
    save_game_state("Début combat manuel")

# === AFFICHAGE STYLÉ ===

def display_guidance_banner():
    """Bannière de guidance selon la phase"""
    phase = st.session_state.sandbox_v2_phase

    if phase == 'CONFIG':
        st.markdown("""
        <div class="guidance-compact guidance-config">
            🔧 Configuration - Chargement des équipes
        </div>
        """, unsafe_allow_html=True)

    elif phase == 'INITIATIVE':
        # Ne pas afficher le message si on est en mode manuel
        initiative_enabled = st.session_state.get('initiative_setting', True)
        if initiative_enabled:
            st.markdown("""
            <div class="guidance-compact guidance-initiative">
                🎲 Initiative - Cliquez pour générer l'ordre des tours
            </div>
            """, unsafe_allow_html=True)

    elif phase == 'COMBAT':
        current = get_current_combatant()
        if current:
            name = current['character'].name
            faction = "Héros" if current['faction'] == 'hero' else "Ennemi"
            st.markdown(f"""
            <div class="guidance-compact guidance-combat">
                ⚔️ {name} ({faction}) - C'est votre tour !
            </div>
            """, unsafe_allow_html=True)

def get_current_combatant() -> Optional[Dict]:
    """Retourne le combattant actuel"""
    if (st.session_state.sandbox_v2_combatants and
        0 <= st.session_state.sandbox_v2_current_turn_index < len(st.session_state.sandbox_v2_combatants)):
        return st.session_state.sandbox_v2_combatants[st.session_state.sandbox_v2_current_turn_index]
    return None

def next_turn():
    """
    Passe au tour suivant EN SAUTANT les combattants morts (utilise is_alive())

    Comportement selon le mode :
    - MODE INITIATIVE : Passe automatiquement au combattant suivant dans l'ordre
    - MODE MANUEL : Réinitialise à -1 pour attendre une nouvelle sélection manuelle
    """
    if not st.session_state.sandbox_v2_combatants:
        return

    # Vérifier le mode (lire directement depuis initiative_setting)
    initiative_enabled = st.session_state.get('initiative_setting', True)

    if not initiative_enabled:
        # MODE MANUEL : Retour à "aucun tour actuel" après une action
        st.session_state.sandbox_v2_current_turn_index = -1
        return

    # MODE INITIATIVE : Passage automatique au tour suivant
    max_iterations = len(st.session_state.sandbox_v2_combatants) + 1
    iterations = 0

    while iterations < max_iterations:
        st.session_state.sandbox_v2_current_turn_index += 1

        # Si on a fait le tour de tous les combattants → nouveau round
        if st.session_state.sandbox_v2_current_turn_index >= len(st.session_state.sandbox_v2_combatants):
            st.session_state.sandbox_v2_current_turn_index = 0
            st.session_state.sandbox_v2_round_number += 1
            st.session_state.sandbox_v2_log.append(f"=== ROUND {st.session_state.sandbox_v2_round_number} ===")

        # Vérifier si le combattant actuel est vivant (API Character.is_alive())
        current = get_current_combatant()
        if current and current['character'].is_alive():
            return  # Combattant vivant trouvé !

        # Combattant mort, continuer la recherche
        iterations += 1

    # Sécurité : tous les combattants d'une faction sont morts (fin de combat gérée ailleurs)
    return

def display_hero_interface(combatant: Dict):
    """Interface héros - Style Arène avec layout 2 colonnes"""
    char = combatant['character']

    # Header héros style Arène
    current_hp = char.current_health
    max_hp = char.get_total_health()
    attack = char.get_total_damage()
    defense = char.get_total_parade()
    magic = char.get_total_spells()

    st.markdown(f"""
    <div class="hero-header">
        <div>
            <h3 style="margin: 0; color: white;">🦸 {char.name}</h3>
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

    # Layout 2 colonnes
    col_abilities, col_actions = st.columns([2, 1])

    with col_abilities:
        display_abilities_grid(char, combatant['id'])

    with col_actions:
        display_actions_and_potions(char, combatant['id'])

def display_enemy_interface(combatant: Dict):
    """Interface ennemi - Style Arène"""
    char = combatant['character']

    # Stats ennemis
    current_hp = char.current_health
    max_hp = char.max_health
    player_count = len([h for h in st.session_state.sandbox_v2_heroes if h.is_alive()])
    stats = char.get_stats_for_players(player_count)
    attack = stats['damage']
    defense = stats.get('defense', char.defense)

    st.markdown(f"""
    <div class="enemy-header">
        <div>
            <h3 style="margin: 0; color: white;">👹 {char.name}</h3>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Tour de l'ennemi - Vous le contrôlez</p>
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

    # Actions ennemi
    st.markdown("### ⚔️ Actions")

    # Vérifier si on est en mode sélection de cible pour l'ennemi
    if st.session_state.sandbox_v2_action_state == 'SELECTING_TARGET_ENEMY':
        # Afficher interface de ciblage
        hero_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'hero']
        heroes_list = [c['character'] for c in hero_combatants]

        adapter = st.session_state.sandbox_v2_adapter
        target = adapter.enemy_turn_manual(
            char,
            heroes_list,
            player_count,
            st.session_state.sandbox_v2_log
        )

        if target:
            adapter.execute_enemy_attack(
                char,
                target,
                player_count,
                st.session_state.sandbox_v2_log
            )
            st.session_state.sandbox_v2_action_state = None
            save_game_state(f"{char.name} attaque {target.name}")
            next_turn()
            st.rerun()

        # Bouton annuler
        if st.button("❌ Annuler", key=f"cancel_enemy_targeting_{combatant['id']}"):
            st.session_state.sandbox_v2_action_state = None
            st.rerun()
    else:
        # Afficher boutons d'action normaux
        col1, col2 = st.columns(2)

        with col1:
            if st.button("⚔️ Attaquer", key=f"sandbox_enemy_attack_{combatant['id']}", type="primary", use_container_width=True):
                st.session_state.sandbox_v2_action_state = 'SELECTING_TARGET_ENEMY'
                st.session_state.sandbox_v2_current_actor = char
                st.rerun()

        with col2:
            if st.button("⏭️ Passer le Tour", key=f"sandbox_enemy_skip_{combatant['id']}", use_container_width=True):
                st.session_state.sandbox_v2_log.append(f"⏭️ {char.name} passe son tour")
                save_game_state(f"{char.name} passe son tour")
                next_turn()
                st.rerun()

def display_abilities_grid(char: Character, combatant_id: str):
    """Grille capacités style Arène"""
    if not hasattr(char, 'abilities') or not char.abilities:
        st.markdown("### 🔮 Capacités Spéciales")
        st.info("Aucune capacité disponible")
        return

    st.markdown("### 🔮 Capacités Spéciales")

    # Grille 3x2
    for row in range(2):
        cols = st.columns(3)
        for col_idx in range(3):
            ability_index = row * 3 + col_idx

            with cols[col_idx]:
                if ability_index < len(char.abilities):
                    ability = char.abilities[ability_index]
                    display_ability_card(char, ability, combatant_id, ability_index)
                else:
                    st.markdown("""
                    <div style="background: #555; border: 2px dashed #777; border-radius: 10px;
                                padding: 15px; text-align: center; color: #999; min-height: 80px;
                                display: flex; align-items: center; justify-content: center;">
                        <strong>Vide</strong>
                    </div>
                    """, unsafe_allow_html=True)

def display_ability_card(char: Character, ability, combatant_id: str, ability_index: int):
    """Carte capacité cliquable style Arène"""
    can_use = ability.ability_number in getattr(char, 'unlocked_abilities', [])
    current_spells = getattr(char, 'current_spells', None)
    if current_spells is None:
        current_spells = char.get_total_spells() if hasattr(char, 'get_total_spells') else 0
    has_spells = ability.spell_cost <= current_spells

    is_available = can_use and has_spells

    type_icon = "🔮" if ability.spell_cost > 0 else "⚔️"
    short_name = ability.name if len(ability.name) <= 15 else ability.name[:12] + "..."

    button_key = f"sandbox_ability_{combatant_id}_{ability_index}"

    if st.button(
        f"{type_icon} {short_name}\nCoût: {ability.spell_cost} ✨",
        key=button_key,
        type="primary" if is_available else "secondary",
        disabled=not is_available,
        use_container_width=True
    ):
        if is_available:
            use_ability_action(char, ability)

def display_actions_and_potions(char: Character, combatant_id: str):
    """Colonne actions + potions style Arène"""
    st.markdown("### ⚡ Actions de Base")

    # Vérifier si on est en mode sélection de cible
    if st.session_state.sandbox_v2_action_state == 'SELECTING_TARGET_HERO':
        # Afficher interface de ciblage
        enemy_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'enemy']
        enemies_list = [c['character'] for c in enemy_combatants]
        hero_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'hero']
        heroes_list = [c['character'] for c in hero_combatants]

        target = ManualTargeting.select_enemy_for_hero_attack(
            char,
            enemies_list,
            heroes_list
        )

        if target:
            player_count = len([h for h in heroes_list if h.is_alive()])
            adapter = st.session_state.sandbox_v2_adapter
            adapter.combat_actions.hero_attack(char, [target], player_count, st.session_state.sandbox_v2_log)
            st.session_state.sandbox_v2_action_state = None
            save_game_state(f"{char.name} attaque {target.name}")
            next_turn()
            st.rerun()

        # Bouton annuler
        if st.button("❌ Annuler", key=f"cancel_targeting_{combatant_id}"):
            st.session_state.sandbox_v2_action_state = None
            st.rerun()
    else:
        # Afficher boutons d'action normaux
        # Attaque
        if st.button("⚔️ Attaquer", key=f"sandbox_attack_{combatant_id}", type="primary", use_container_width=True):
            st.session_state.sandbox_v2_action_state = 'SELECTING_TARGET_HERO'
            st.session_state.sandbox_v2_current_actor = char
            st.rerun()

        # Passer
        if st.button("⏭️ Passer le Tour", key=f"sandbox_skip_{combatant_id}", use_container_width=True):
            st.session_state.sandbox_v2_log.append(f"⏭️ {char.name} passe son tour")
            save_game_state(f"{char.name} passe son tour")
            next_turn()
            st.rerun()

    # Potions
    st.markdown("### 🧪 Potions")

    if hasattr(char, 'health_potions') and char.health_potions:
        potions_summary = char.get_potions_summary()

        col1, col2 = st.columns(2)

        with col1:
            small_count = potions_summary['small_count']
            if small_count > 0:
                if st.button(f"🩸 Soin\n{small_count}", key=f"sandbox_potion_small_{combatant_id}", use_container_width=True):
                    use_potion_action(char)
            else:
                st.button(f"🩸 Soin\n0", disabled=True, use_container_width=True)

        with col2:
            large_count = potions_summary['large_count']
            if large_count > 0:
                if st.button(f"❤️‍🩹 Vitesse\n{large_count}", key=f"sandbox_potion_large_{combatant_id}", use_container_width=True):
                    use_potion_action(char)
            else:
                st.button(f"❤️‍🩹 Vitesse\n0", disabled=True, use_container_width=True)
    else:
        st.info("Aucune potion")

# === ACTIONS DE COMBAT ===

def use_ability_action(char: Character, ability):
    """Utilise une capacité"""
    if hasattr(char, 'use_ability'):
        action = char.use_ability(ability)
        if action.success:
            st.session_state.sandbox_v2_log.append(f"🔮 {char.name} utilise {ability.name}")
            save_game_state(f"{char.name} utilise {ability.name}")
            next_turn()
            st.success(f"✅ {ability.name} utilisée !")
            st.rerun()
        else:
            st.error(f"❌ Impossible d'utiliser {ability.name}")

def use_potion_action(char: Character):
    """Utilise une potion"""
    if hasattr(char, 'use_health_potion'):
        result = char.use_health_potion()
        if result['success']:
            st.session_state.sandbox_v2_log.append(f"🧪 {char.name} boit une potion: {result['message']}")
            save_game_state(f"{char.name} utilise potion")
            st.success(f"✅ {result['message']}")
        else:
            st.error(f"❌ {result['message']}")

# === AFFICHAGE STATUS COMBAT ===

def display_hero_combat_card(hero: Character, is_current_turn: bool = False):
    """
    Affiche une carte héros pour le combat avec format "carte à collectionner"
    RÉUTILISE get_hero_card_style() de ui.styling (même format que premier onglet)

    Args:
        hero: Personnage héros
        is_current_turn: True si c'est le tour de ce héros
    """
    # Récupérer stats en temps réel (RÉUTILISE APIs Character)
    current_hp = hero.current_health
    max_hp = hero.get_total_health()
    attack = hero.get_total_damage()
    defense = hero.get_total_parade()
    magic = hero.get_total_spells()
    is_alive = hero.is_alive()

    # Détermination border color selon l'état
    if is_current_turn:
        border_color = "#FFD700"  # Doré pour tour actuel
    elif not is_alive:
        border_color = "#666"  # Gris pour mort
    else:
        border_color = "#27ae60"  # Vert pour vivant en attente

    # Récupérer image (RÉUTILISE API ui_elements.py)
    image_path = get_hero_image_path(hero.name)
    background_style = ""
    if image_path:
        img_base64 = load_hero_image_base64(image_path)
        if img_base64:
            background_style = f"background-image: url('data:image/jpeg;base64,{img_base64}');"

    # Fallback background si pas d'image
    if not background_style:
        background_style = f"background: linear-gradient(135deg, {border_color}33, {border_color}11);"

    # Préparer stats_content (même format que premier onglet)
    stats_content = f"""
    <div style="font-family: monospace; font-size: 1rem; margin-bottom: 5px; font-weight: bold; color: #f0f0f0;">
        ❤️ {current_hp}/{max_hp} • ⚔️ {attack} • 🛡️ {defense} • ✨ {magic}
    </div>"""

    # Préparer build_content (remplacé par status pour le combat)
    if is_current_turn:
        build_content = '<div style="font-size: 1.1rem; font-weight: bold; color: #FFD700; text-shadow: 2px 2px 4px black;">⚡ C\'EST SON TOUR</div>'
    elif not is_alive:
        build_content = '<div style="font-size: 1.1rem; font-weight: bold; color: #ff4444; text-shadow: 2px 2px 4px black;">💀 INCONSCIENT</div>'
    else:
        build_content = '<div style="font-size: 0.9rem; font-style: italic; color: #90EE90;">✓ Prêt</div>'

    # RÉUTILISE le style existant (même format que premier onglet)
    card_html = get_hero_card_style(hero.name, border_color, background_style)
    card_html = card_html.replace("{stats_content}", stats_content)
    card_html = card_html.replace("{build_content}", build_content)

    st.markdown(card_html, unsafe_allow_html=True)

def display_enemy_combat_card(enemy: Enemy, is_current_turn: bool = False):
    """
    Affiche une carte ennemi pour le combat avec format "carte à collectionner"
    RÉUTILISE get_hero_card_style() de ui.styling (même format 260x370px que héros)

    Args:
        enemy: Personnage ennemi
        is_current_turn: True si c'est le tour de cet ennemi
    """
    # Calculer player_count depuis héros vivants (RÉUTILISE pattern existant)
    hero_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'hero']
    heroes = [c['character'] for c in hero_combatants]
    player_count = len([h for h in heroes if h.is_alive()])

    # Récupérer stats en temps réel (RÉUTILISE APIs Enemy)
    current_hp = enemy.current_health
    max_hp = enemy.max_health
    stats = enemy.get_stats_for_players(player_count)
    damage = stats['damage']
    defense = enemy.defense
    is_alive = enemy.is_alive()

    # Détermination border color selon l'état
    if is_current_turn:
        border_color = "#FFD700"  # Doré pour tour actuel
    elif not is_alive:
        border_color = "#666"  # Gris pour mort
    else:
        border_color = "#e74c3c"  # Rouge pour vivant en attente

    # Charger image monstres.jpg (RÉUTILISE même approche que héros avec chemin relatif portable)
    import base64
    import os
    monster_image_path = "data/images/monstres.jpg"
    background_style = ""

    if os.path.exists(monster_image_path):
        try:
            with open(monster_image_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
                background_style = f"background-image: url('data:image/jpeg;base64,{img_base64}');"
        except Exception as e:
            # Fallback: gradient rouge si erreur de lecture
            background_style = "background: linear-gradient(135deg, #8b0000, #4a0000);"
    else:
        # Fallback: gradient rouge si image non disponible
        background_style = "background: linear-gradient(135deg, #8b0000, #4a0000);"

    # Préparer stats_content (adapté pour ennemis)
    magic_indicator = " ✨" if enemy.is_magical else ""
    stats_content = f"""
    <div style="font-family: monospace; font-size: 1rem; margin-bottom: 5px; font-weight: bold; color: #f0f0f0;">
        ❤️ {current_hp}/{max_hp} • ⚔️ {damage} • 🛡️ {defense}{magic_indicator}
    </div>"""

    # Préparer build_content (remplacé par status pour le combat)
    if is_current_turn:
        build_content = '<div style="font-size: 1.1rem; font-weight: bold; color: #FFD700; text-shadow: 2px 2px 4px black;">⚡ C\'EST SON TOUR</div>'
    elif not is_alive:
        build_content = '<div style="font-size: 1.1rem; font-weight: bold; color: #ff4444; text-shadow: 2px 2px 4px black;">💀 MORT</div>'
    else:
        build_content = '<div style="font-size: 0.9rem; font-style: italic; color: #ff6666;">✓ En attente</div>'

    # RÉUTILISE le style existant (même format que cartes héros)
    card_html = get_hero_card_style(enemy.name, border_color, background_style)
    card_html = card_html.replace("{stats_content}", stats_content)
    card_html = card_html.replace("{build_content}", build_content)

    st.markdown(card_html, unsafe_allow_html=True)

def display_recent_actions():
    """
    Affiche une zone de notification avec les dernières actions du combat
    Zone toujours visible pour donner un retour immédiat à l'utilisateur

    N'affiche rien si seules des lignes d'initialisation (initiative, début de combat)
    sont présentes. Affiche uniquement quand des ACTIONS réelles ont eu lieu.
    """
    if not st.session_state.sandbox_v2_log:
        return

    def is_initialization_line(line: str) -> bool:
        """Détecte si une ligne est de l'initialisation (initiative, séparateurs)"""
        line = line.strip()
        if not line:
            return True
        # Séparateurs de rounds et sections
        if line.startswith("==="):
            return True
        # Lignes d'ordre d'initiative : "N. 🦸/👹 Nom : chiffre"
        import re
        if re.match(r'^\d+\.\s*[🦸👹]\s+.+\s*:\s*\d+$', line):
            return True
        return False

    # Récupérer les 3 dernières lignes d'ACTION (pas d'initialisation)
    action_lines = []
    for line in reversed(st.session_state.sandbox_v2_log):
        # Filtrer les lignes d'initialisation
        if not is_initialization_line(line):
            action_lines.append(line)
        # Arrêter après 3 lignes d'action
        if len(action_lines) >= 3:
            break

    # Si aucune action réelle, ne rien afficher
    if not action_lines:
        return

    # Inverser pour afficher dans l'ordre chronologique
    action_lines = list(reversed(action_lines))

    # Construire le HTML stylé pour la zone de notification
    lines_html = ""
    for line in action_lines:
        lines_html += f"<div style='padding: 4px 0; font-family: monospace; font-size: 0.95rem;'>{line}</div>"

    notification_html = f"""
    <div style="
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a7b 100%);
        border-left: 5px solid #4a9eff;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    ">
        <div style="
            font-weight: bold;
            color: #4a9eff;
            margin-bottom: 8px;
            font-size: 1rem;
            display: flex;
            align-items: center;
        ">
            📢 Dernières actions
        </div>
        <div style="color: #e0e0e0;">
            {lines_html}
        </div>
    </div>
    """

    st.markdown(notification_html, unsafe_allow_html=True)

def display_combat_log_colored():
    """
    Affiche le journal de combat avec formatage coloré et scrollable
    - Container scrollable avec hauteur fixe
    - Couleurs par type d'action pour meilleure lisibilité
    - Style terminal/arène cohérent avec le thème
    """
    if not st.session_state.sandbox_v2_log:
        st.info("Aucune action de combat pour le moment")
        return

    def colorize_line(line: str) -> str:
        """Applique couleur selon le type de ligne"""
        line_stripped = line.strip()

        # Liste des 8 héros de Périples
        HERO_NAMES = ["Atucan", "Liarie", "Kraor", "Elneha", "Vahid", "Vega", "Ayana", "Myla"]

        # Ligne vide
        if not line_stripped:
            return '<div style="height: 5px;"></div>'

        # Séparateurs de rounds (=== ROUND X ===)
        if line_stripped.startswith("==="):
            return f'<div style="color: #f1c40f; font-weight: bold; margin: 10px 0 5px 0; font-size: 1.05rem;">{line_stripped}</div>'

        # Lignes d'initiative (numéro au début avec icônes)
        if line_stripped and line_stripped[0].isdigit() and ("🦸" in line_stripped or "👹" in line_stripped):
            return f'<div style="color: #f1c40f; padding-left: 10px;">{line_stripped}</div>'

        # PRIORITÉ HAUTE : Lignes indentées (détails d'action) - AVANT les emojis d'attaque
        if line.startswith("  ") or line.startswith("    "):
            return f'<div style="color: #17a2b8; padding-left: 20px; font-size: 0.95rem;">{line_stripped}</div>'

        # Capacités magiques (violet) - Priorité haute car contient souvent noms
        if "🔮" in line_stripped:
            return f'<div style="color: #9b59b6;">{line_stripped}</div>'

        # Potions (bleu) - Priorité haute
        if "🧪" in line_stripped:
            return f'<div style="color: #3498db;">{line_stripped}</div>'

        # Passer tour (orange) - Priorité haute
        if "⏭️" in line_stripped:
            return f'<div style="color: #f39c12;">{line_stripped}</div>'

        # Dégâts bloqués par parade (cyan, indenté)
        if "🛡️" in line_stripped:
            return f'<div style="color: #17a2b8; padding-left: 20px; font-size: 0.95rem;">{line_stripped}</div>'

        # Mort/KO (gris)
        if "💀" in line_stripped:
            return f'<div style="color: #95a5a6; font-weight: bold;">{line_stripped}</div>'

        # Attaques : Détecter si c'est un héros ou un ennemi qui attaque
        if "⚔️" in line_stripped or "✨" in line_stripped or "💥" in line_stripped or "🐾" in line_stripped:
            text_after_emoji = line_stripped.split(' ', 1)[1] if ' ' in line_stripped else line_stripped

            text_cleaned = text_after_emoji
            for prefix in ["CRITIQUE ! ", "ÉCHEC ! ", "CRITIQUE! ", "ÉCHEC! "]:
                if text_cleaned.startswith(prefix):
                    text_cleaned = text_cleaned[len(prefix):]
                    break

            if " attaque " in text_cleaned:
                before_attaque = text_cleaned.split(" attaque ")[0].strip()
                attacker_name = before_attaque.split("[")[0].strip() if "[" in before_attaque else before_attaque
            elif "[" in text_cleaned and "→" in text_cleaned:
                attacker_name = text_cleaned.split("[")[0].strip()
            elif "→" in text_cleaned:
                attacker_name = text_cleaned.split("→")[0].strip()
            else:
                attacker_name = text_cleaned.split()[0] if text_cleaned else ""

            is_hero_action = any(hero_name in attacker_name for hero_name in HERO_NAMES)

            if is_hero_action:
                return f'<div style="color: #27ae60;">{line_stripped}</div>'  # Vert pour héros
            else:
                return f'<div style="color: #e74c3c;">{line_stripped}</div>'  # Rouge pour ennemis

        # Ligne par défaut (blanc/gris clair)
        return f'<div style="color: #e0e0e0;">{line_stripped}</div>'

    # Construction du HTML colorisé
    log_html = ""
    for line in st.session_state.sandbox_v2_log:
        log_html += colorize_line(line)

    # Container scrollable avec style Arène
    scrollable_log = f"""
    <div style="
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 2px solid #0f3460;
        border-radius: 10px;
        padding: 15px 20px;
        height: 400px;
        overflow-y: scroll;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        line-height: 1.6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    ">
        {log_html}
    </div>
    """

    st.markdown(scrollable_log, unsafe_allow_html=True)

def display_combat_status():
    """
    MODE INITIATIVE ACTIVÉE - Affiche tous les combattants dans l'ordre d'initiative (D20)
    - Grille horizontale avec max 8 cartes par ligne
    - Ordre : celui de sandbox_v2_combatants (déjà trié par InitiativeManager)
    - Pas de séparation héros/ennemis (ordre d'initiative respecté)
    RÉUTILISE display_hero_combat_card() et display_enemy_combat_card()
    """
    # Récupérer tous les combattants dans l'ordre d'initiative (source de vérité unique)
    all_combatants = st.session_state.sandbox_v2_combatants

    # Déterminer quel combattant a le tour actuel
    current_combatant = get_current_combatant()
    current_character_id = current_combatant['id'] if current_combatant else None

    if not all_combatants:
        st.warning("Aucun combattant trouvé")
        return

    # === GRILLE AVEC MAX 8 CARTES PAR LIGNE ===
    max_cards_per_row = 8
    total_combatants = len(all_combatants)

    # Calculer nombre de lignes nécessaires
    num_rows = (total_combatants + max_cards_per_row - 1) // max_cards_per_row

    # Parcourir ligne par ligne
    for row_idx in range(num_rows):
        # Calculer indices pour cette ligne
        start_idx = row_idx * max_cards_per_row
        end_idx = min(start_idx + max_cards_per_row, total_combatants)
        row_combatants = all_combatants[start_idx:end_idx]

        # Créer colonnes pour cette ligne
        cols = st.columns(len(row_combatants))

        # Afficher chaque carte
        for col_idx, combatant_data in enumerate(row_combatants):
            with cols[col_idx]:
                character = combatant_data['character']
                is_current = (combatant_data['id'] == current_character_id)

                # Afficher carte selon le type (héros ou ennemi)
                if combatant_data['faction'] == 'hero':
                    display_hero_combat_card(character, is_current_turn=is_current)
                else:
                    display_enemy_combat_card(character, is_current_turn=is_current)

def display_combat_status_team_mode():
    """
    MODE MANUEL - Affiche tous les combattants en grille unique (héros et ennemis mélangés)
    - Grille horizontale avec max 7 cartes par ligne
    - Ordre : héros d'abord, puis ennemis (ordre de sandbox_v2_combatants)
    - Boutons "▶️ À son tour" pour sélection manuelle
    RÉUTILISE display_hero_combat_card() et display_enemy_combat_card()
    """
    # Récupérer tous les combattants (ordre: héros puis ennemis)
    all_combatants = st.session_state.sandbox_v2_combatants

    # Déterminer quel combattant a le tour actuel (si défini)
    current_combatant = get_current_combatant()
    current_character_id = current_combatant['id'] if current_combatant else None

    if not all_combatants:
        st.warning("Aucun combattant trouvé")
        return

    # === GRILLE AVEC MAX 7 CARTES PAR LIGNE ===
    max_cards_per_row = 7
    total_combatants = len(all_combatants)

    # Calculer nombre de lignes nécessaires
    num_rows = (total_combatants + max_cards_per_row - 1) // max_cards_per_row

    # Parcourir ligne par ligne
    for row_idx in range(num_rows):
        # Calculer indices pour cette ligne
        start_idx = row_idx * max_cards_per_row
        end_idx = min(start_idx + max_cards_per_row, total_combatants)
        row_combatants = all_combatants[start_idx:end_idx]

        # Créer colonnes pour cette ligne
        cols = st.columns(len(row_combatants))

        # Afficher chaque carte
        for col_idx, combatant_data in enumerate(row_combatants):
            with cols[col_idx]:
                character = combatant_data['character']
                is_current = (combatant_data['id'] == current_character_id)

                # Afficher carte selon le type (héros ou ennemi)
                if combatant_data['faction'] == 'hero':
                    display_hero_combat_card(character, is_current_turn=is_current)
                else:
                    display_enemy_combat_card(character, is_current_turn=is_current)

                # Vérifier si le combattant a déjà joué ce round
                has_played = combatant_data['id'] in st.session_state.sandbox_v2_played_this_round

                # Bouton "À son tour" si vivant et pas déjà en cours
                if character.is_alive() and not is_current:
                    # Désactiver si déjà joué
                    button_disabled = has_played
                    button_label = "✅ A joué" if has_played else "▶️ À son tour"

                    if st.button(
                        button_label,
                        key=f"select_{combatant_data['faction']}_{combatant_data['id']}",
                        type="secondary" if has_played else "primary",
                        disabled=button_disabled,
                        use_container_width=True
                    ):
                        if not button_disabled:
                            select_combatant_manually(combatant_data['id'])

def select_combatant_manually(combatant_id: str):
    """
    Sélectionne manuellement un combattant pour son tour
    Utilisé en mode sans initiative
    """
    # Trouver l'index du combattant sélectionné
    for idx, combatant in enumerate(st.session_state.sandbox_v2_combatants):
        if combatant['id'] == combatant_id:
            st.session_state.sandbox_v2_current_turn_index = idx

            # Initialiser le tour du combattant (jetons de parade)
            char = combatant['character']
            if combatant['faction'] == 'hero':
                char.start_hero_turn()
            else:
                char.start_enemy_turn()

            # Marquer comme ayant joué ce round (mode manuel)
            if combatant_id not in st.session_state.sandbox_v2_played_this_round:
                st.session_state.sandbox_v2_played_this_round.append(combatant_id)

            # Log
            name = char.name
            faction = "🦸" if combatant['faction'] == 'hero' else "👹"
            st.session_state.sandbox_v2_log.append(f"{faction} {name} commence son tour")

            # Sauvegarder l'état
            save_game_state(f"{name} sélectionné")

            st.rerun()
            break

def display_initiative_order():
    """Affiche l'ordre d'initiative (ordre décroissant, mélangé héros/ennemis)"""
    st.markdown("### 🎲 Ordre d'Initiative")

    for i, c in enumerate(st.session_state.sandbox_v2_combatants):
        name = c['character'].name
        init = c['initiative']
        faction_icon = "🦸" if c['faction'] == 'hero' else "👹"

        # Highlight le combattant actuel
        if i == st.session_state.sandbox_v2_current_turn_index:
            st.markdown(f"**➡️ {i+1}. {faction_icon} {name} : {init} ⬅️**")
        else:
            st.write(f"{i+1}. {faction_icon} {name} : {init}")

# === INTERFACE PRINCIPALE ===

def main_sandbox_v2():
    """Interface principale Sandbox V2 - Style Arène"""
    apply_sandbox_v2_theme()

    st.title("🎮 Sandbox V2")

    # Indicateur de mode
    initiative_mode = st.session_state.get('initiative_setting', True)
    if initiative_mode:
        st.caption("✅ Ciblage manuel | 🎲 Initiative D20 | Système Undo/Redo")
    else:
        st.caption("✅ Ciblage manuel | 🎮 Ordre Manuel | Système Undo/Redo")

    init_sandbox_state()

    # Vérification configuration
    if not st.session_state.get('selected_heroes') or not st.session_state.get('selected_enemies'):
        st.markdown("""
        <div class="guidance-compact guidance-config">
            ⚙️ Configuration requise - Allez dans "Sélection" pour choisir vos équipes
        </div>
        """, unsafe_allow_html=True)
        st.info("📋 Allez dans l'onglet **Sélection** pour choisir 2+ héros et 1+ ennemi")
        return

    # DÉTECTION CHANGEMENT DE SÉLECTION
    current_selection = {
        'heroes': tuple(st.session_state.get('selected_heroes', [])),
        'enemies': tuple(st.session_state.get('selected_enemies', []))
    }

    # Si la sélection a changé depuis la dernière configuration, revenir à CONFIG
    if st.session_state.sandbox_v2_last_selection is not None:
        if st.session_state.sandbox_v2_last_selection != current_selection:
            st.info("🔄 Sélection modifiée - Rechargement des équipes...")
            st.session_state.sandbox_v2_phase = 'CONFIG'
            st.session_state.sandbox_v2_game_history = []
            st.session_state.sandbox_v2_history_index = -1
            st.session_state.sandbox_v2_combatants = []

    # Mémoriser la sélection actuelle
    st.session_state.sandbox_v2_last_selection = current_selection

    # Phase actuelle
    phase = st.session_state.sandbox_v2_phase

    # Bannière de guidance
    display_guidance_banner()

    # === PHASE CONFIG ===
    if phase == 'CONFIG':
        if configure_combat():
            st.session_state.sandbox_v2_phase = 'INITIATIVE'
            st.rerun()
        else:
            st.error("❌ Erreur de configuration")
        return

    # === PHASE INITIATIVE ===
    elif phase == 'INITIATIVE':
        # Lire directement depuis initiative_setting (source unique de vérité)
        initiative_enabled = st.session_state.get('initiative_setting', True)

        if initiative_enabled:
            # MODE INITIATIVE ACTIVÉE : Jets de dés D20
            st.info("🎲 Cliquez pour générer l'ordre d'initiative et commencer le combat")

            # Bouton génération initiative
            if st.button("🎲 Générer Initiative et Commencer", type="primary", use_container_width=True):
                generate_initiative()
                st.session_state.sandbox_v2_phase = 'COMBAT'
                st.session_state.sandbox_v2_current_turn_index = 0
                st.rerun()
        else:
            # MODE MANUEL : Pas d'initiative, organisation par équipe
            st.info("🎮 Mode manuel activé - Vous choisirez l'ordre de jeu")
            st.write("Les combattants sont organisés par équipe : héros puis ennemis.")

            # Bouton pour commencer le combat en mode manuel
            if st.button("▶️ Commencer le Combat (Mode Manuel)", type="primary", use_container_width=True):
                organize_teams_without_initiative()
                st.session_state.sandbox_v2_phase = 'COMBAT'
                st.rerun()

        return

    # === PHASE COMBAT ===
    elif phase == 'COMBAT':
        # Lire directement depuis initiative_setting (source unique de vérité)
        initiative_enabled = st.session_state.get('initiative_setting', True)

        if initiative_enabled:
            # MODE INITIATIVE : Afficher ordre d'initiative et cartes dans l'ordre des jets
            with st.expander("🎲 Ordre d'Initiative", expanded=False):
                display_initiative_order()

            # Status combat avec ordre d'initiative
            display_combat_status()
        else:
            # MODE MANUEL : Afficher cartes par équipe avec boutons de sélection
            display_combat_status_team_mode()

        st.markdown("---")

        # Vérifier victoire/défaite - Depuis combattants
        hero_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'hero']
        enemy_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'enemy']

        alive_heroes = [c['character'] for c in hero_combatants if c['character'].is_alive()]
        alive_enemies = [c['character'] for c in enemy_combatants if c['character'].is_alive()]

        if not alive_heroes:
            st.error("💀 DÉFAITE - Tous les héros sont tombés !")
            if st.button("🔄 Recommencer", type="primary"):
                st.session_state.sandbox_v2_phase = 'CONFIG'
                st.rerun()
            return

        if not alive_enemies:
            st.success("🎉 VICTOIRE - Tous les ennemis sont vaincus !")
            if st.button("🔄 Nouveau Combat", type="primary"):
                st.session_state.sandbox_v2_phase = 'CONFIG'
                st.rerun()
            return

        # Tour actuel
        current = get_current_combatant()
        if current:
            # VÉRIFICATION : Sauter si mort (sécurité - normalement géré par next_turn())
            if not current['character'].is_alive():
                st.session_state.sandbox_v2_log.append(f"⏭️ {current['character'].name} est inconscient, passage au tour suivant")
                next_turn()
                st.rerun()
                return

            # Afficher interface seulement si vivant
            if current['faction'] == 'hero':
                display_hero_interface(current)
            else:
                display_enemy_interface(current)
        else:
            # Aucun tour actuel : En mode manuel, inviter l'utilisateur à sélectionner
            if not initiative_enabled:
                st.info("🎮 Sélectionnez un combattant pour jouer son tour (cliquez sur '▶️ À son tour')")

    # === DERNIÈRES ACTIONS (toujours visible) ===
    display_recent_actions()

    # === JOURNAL DE COMBAT (historique complet) ===
    if st.session_state.sandbox_v2_log and phase == 'COMBAT':
        with st.expander("📜 Journal de Combat (Historique complet)", expanded=False):
            display_combat_log_colored()

    # === BOUTON NOUVEAU ROUND (MODE MANUEL) ===
    if phase == 'COMBAT' and not initiative_enabled:
        # Afficher le bouton seulement si au moins un combattant a joué
        if st.session_state.sandbox_v2_played_this_round:
            st.markdown("---")
            # Compter combien de combattants vivants ont joué
            alive_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['character'].is_alive()]
            played_count = len(st.session_state.sandbox_v2_played_this_round)
            total_alive = len(alive_combatants)

            st.markdown(f"**Round {st.session_state.sandbox_v2_round_number}** - {played_count}/{total_alive} combattants ont joué")

            if st.button("🔄 Nouveau Round", type="primary", use_container_width=True):
                # Réinitialiser la liste des joueurs
                st.session_state.sandbox_v2_played_this_round = []
                # Incrémenter le numéro de round
                st.session_state.sandbox_v2_round_number += 1
                # Réinitialiser l'index de tour
                st.session_state.sandbox_v2_current_turn_index = -1
                # Log
                st.session_state.sandbox_v2_log.append("")
                st.session_state.sandbox_v2_log.append(f"=== ROUND {st.session_state.sandbox_v2_round_number} ===")
                # Sauvegarder
                save_game_state(f"Nouveau round {st.session_state.sandbox_v2_round_number}")
                st.rerun()

    # === CONTRÔLES UNDO/REDO ===
    if st.session_state.sandbox_v2_game_history and phase == 'COMBAT':
        st.markdown("---")
        st.markdown("### 🕒 Historique")

        col1, col2, col3 = st.columns(3)

        with col1:
            can_undo = st.session_state.sandbox_v2_history_index > 0
            if st.button("⏪ Annuler", disabled=not can_undo, use_container_width=True):
                restore_previous_state()
                st.rerun()

        with col2:
            can_redo = st.session_state.sandbox_v2_history_index < len(st.session_state.sandbox_v2_game_history) - 1
            if st.button("⏩ Refaire", disabled=not can_redo, use_container_width=True):
                restore_next_state()
                st.rerun()

        with col3:
            if st.button("🔄 Reset Combat", use_container_width=True):
                st.session_state.sandbox_v2_phase = 'CONFIG'
                st.session_state.sandbox_v2_game_history = []
                st.session_state.sandbox_v2_history_index = -1
                st.rerun()

if __name__ == "__main__":
    main_sandbox_v2()
