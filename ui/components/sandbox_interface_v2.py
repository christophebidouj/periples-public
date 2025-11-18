"""
Sandbox Interface V2 - Style Arène
Interface avec ciblage manuel, initiative et système Undo/Redo
RÉUTILISE l'architecture existante : TurnManager + CombatActions
"""

import streamlit as st
import random
from typing import List, Dict, Optional
from copy import deepcopy

from models.character import Character, Enemy, PotionType
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

def validate_character_state(char, context: str = ""):
    """
    Valide que tous les attributs critiques d'un Character sont présents et cohérents
    Utilisé pour vérifier l'intégrité après restore undo/redo

    Args:
        char: Character ou Enemy à valider
        context: Contexte pour les logs de débogage (ex: "après undo")

    Returns:
        tuple[bool, List[str]]: (is_valid, list_of_issues)
    """
    issues = []

    # Déterminer si c'est un Character (héros) ou Enemy
    is_hero = hasattr(char, 'abilities')

    # Attributs communs à tous (héros et ennemis)
    common_attrs = [
        'current_health',
        'current_parade_tokens'
    ]

    # Attributs spécifiques aux héros
    hero_attrs = [
        'current_spells',
        'spells_used',
        'magic_abilities_used_this_turn',
        'can_attack_this_turn',
        'attack_done_this_turn',
        'action_taken_this_turn',
        'potion_used_this_turn'
    ]

    # Validation des attributs communs
    for attr in common_attrs:
        if not hasattr(char, attr):
            issues.append(f"Attribut manquant: {attr}")

    # Validation des attributs spécifiques aux héros
    if is_hero:
        for attr in hero_attrs:
            if not hasattr(char, attr):
                issues.append(f"Attribut manquant: {attr}")

    # Vérifier cohérence des valeurs
    if hasattr(char, 'current_health') and char.current_health < 0:
        issues.append(f"Santé négative: {char.current_health}")

    if hasattr(char, 'current_spells') and char.current_spells is not None:
        if char.current_spells < 0:
            issues.append(f"Sorts négatifs: {char.current_spells}")

    if hasattr(char, 'current_parade_tokens') and char.current_parade_tokens < 0:
        issues.append(f"Jetons parade négatifs: {char.current_parade_tokens}")

    # Vérifier listes d'objets imbriqués
    if hasattr(char, 'health_potions'):
        for i, potion in enumerate(char.health_potions):
            if not hasattr(potion, 'quantity'):
                issues.append(f"Potion {i} manque l'attribut quantity")
            elif potion.quantity < 0:
                issues.append(f"Potion {i} a une quantité négative: {potion.quantity}")

    if hasattr(char, 'abilities'):
        for i, ability in enumerate(char.abilities):
            if not hasattr(ability, 'uses_remaining_combat'):
                issues.append(f"Capacité {i} manque l'attribut uses_remaining_combat")

    # Log de débogage si des problèmes sont détectés
    if issues and context:
        error_msg = f"⚠️ Validation {context} - {char.name}: {len(issues)} problème(s) détecté(s)"
        st.session_state.sandbox_v2_log.append(error_msg)

    return len(issues) == 0, issues

def ensure_character_attributes(char):
    """
    Garantit que tous les attributs requis sont présents sur un Character/Enemy
    Initialise les attributs manquants avec leurs valeurs par défaut

    Utilisé après restore undo/redo pour gérer les états sauvegardés AVANT
    l'ajout de nouveaux attributs au modèle
    """
    # Déterminer si c'est un Character (héros) ou Enemy
    # Les héros ont des abilities, les ennemis n'en ont pas
    is_hero = hasattr(char, 'abilities')

    if is_hero:
        # Attributs spécifiques aux héros (Character)
        default_attrs = {
            'attack_done_this_turn': False,
            'action_taken_this_turn': False,
            'potion_used_this_turn': False,
            'can_attack_this_turn': True,
            'magic_abilities_used_this_turn': 0
        }

        for attr, default_value in default_attrs.items():
            if not hasattr(char, attr):
                # Utiliser __dict__ pour éviter la validation Pydantic stricte
                char.__dict__[attr] = default_value
    # Les Enemy n'ont pas besoin de ces attributs spécifiques aux héros

def reset_temporary_ui_flags():
    """
    Réinitialise tous les flags temporaires de l'interface utilisateur
    À appeler après chaque restore (undo/redo) pour éviter les états incohérents
    """
    st.session_state.sandbox_v2_action_state = None
    st.session_state.sandbox_v2_current_actor = None
    st.session_state.sandbox_v2_potion_type = None

    # Note: sandbox_v2_last_selection est conservé car il sert de mémorisation entre tours

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

        # NOUVEAU - Réinitialiser les flags temporaires de l'interface
        reset_temporary_ui_flags()

        # NOUVEAU - Garantir que tous les attributs requis sont présents (rétrocompatibilité)
        for combatant in st.session_state.sandbox_v2_combatants:
            char = combatant['character']
            ensure_character_attributes(char)

        # NOUVEAU - Valider l'intégrité de tous les combattants restaurés
        for combatant in st.session_state.sandbox_v2_combatants:
            char = combatant['character']
            is_valid, issues = validate_character_state(char, context="après undo")
            if not is_valid:
                # Log détaillé des problèmes détectés (pour débogage)
                for issue in issues:
                    st.session_state.sandbox_v2_log.append(f"  ↳ {issue}")

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

        # NOUVEAU - Réinitialiser les flags temporaires de l'interface
        reset_temporary_ui_flags()

        # NOUVEAU - Garantir que tous les attributs requis sont présents (rétrocompatibilité)
        for combatant in st.session_state.sandbox_v2_combatants:
            char = combatant['character']
            ensure_character_attributes(char)

        # NOUVEAU - Valider l'intégrité de tous les combattants restaurés
        for combatant in st.session_state.sandbox_v2_combatants:
            char = combatant['character']
            is_valid, issues = validate_character_state(char, context="après redo")
            if not is_valid:
                # Log détaillé des problèmes détectés (pour débogage)
                for issue in issues:
                    st.session_state.sandbox_v2_log.append(f"  ↳ {issue}")

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

    def __init__(self, turn_manager: TurnManager, combat_actions: CombatActions, spell_manager: SpellManager):
        self.turn_manager = turn_manager
        self.combat_actions = combat_actions
        self.spell_manager = spell_manager
        # NOUVEAU - AbilityEffectsManager pour exécuter les capacités
        self.ability_effects_manager = combat_actions.ability_effects_manager

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
        # Idem pour criticals_setting (source unique de vérité)

        # Lire le paramètre critiques depuis session_state
        criticals_enabled = st.session_state.get('criticals_setting', True)

        # Architecture existante
        rules = GameRules(
            ranged_attacks=True,
            magical_damage=True,
            criticals=criticals_enabled,  # Lecture dynamique depuis checkbox Onglet 1
            abilities_enabled=True
        )

        spell_manager = SpellManager()
        combat_actions = CombatActions(spell_manager, rules)
        turn_manager = TurnManager(spell_manager, combat_actions)

        # Adapter (AJOUT spell_manager pour accès aux capacités)
        st.session_state.sandbox_v2_turn_manager = turn_manager
        st.session_state.sandbox_v2_adapter = SandboxTurnManagerAdapter(
            turn_manager,
            combat_actions,
            spell_manager
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
            # Initialiser le tour du combattant (reset jetons parade + compteurs capacités magiques)
            char = current['character']
            if current['faction'] == 'hero':
                char.start_hero_turn()
            else:
                char.start_enemy_turn()
                # NOUVEAU - Vérifier status stunned pour ennemis
                if hasattr(char, 'check_enemy_status_effects'):
                    status = char.check_enemy_status_effects()
                    if not status['can_act']:
                        # Ennemi stunné - sauter son tour
                        stunned_turns = char.status_effects.get('stunned', 0)
                        st.session_state.sandbox_v2_log.append(f"😵 {char.name} est étourdi ! ({stunned_turns} tour(s) restant(s)) - Tour sauté")
                        iterations += 1
                        continue  # Passer au combattant suivant
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
            # RÉUTILISE CombatActions.enemy_attack() avec ciblage manuel
            adapter.combat_actions.enemy_attack(
                enemy=char,
                heroes=heroes_list,
                player_count=player_count,
                log=st.session_state.sandbox_v2_log,
                active_pets=[],  # Pas de pets dans Sandbox V2 pour l'instant
                manual_target=target
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

    # Vérifier si une capacité magique a déjà été utilisée ce tour (règle p.24)
    magic_already_used = (
        ability.prevents_attack and
        getattr(char, 'magic_abilities_used_this_turn', 0) >= 1
    )

    # NOUVEAU - Vérifier si une attaque a été effectuée (règle p.24 - blocage bidirectionnel)
    attack_already_done = getattr(char, 'attack_done_this_turn', False)
    blocked_by_attack = ability.prevents_attack and attack_already_done

    # NOUVEAU - Vérifier si Parade a déjà été utilisée ce tour (limitation 1/tour)
    parade_already_used = False
    if ability.name == "Parade" and hasattr(char, 'temporary_buffs'):
        parade_already_used = char.temporary_buffs.get('parade_used_this_turn', False)

    # NOUVEAU - Vérifier si Armure du Mage déjà utilisée (limitation 1/combat permanent)
    armure_mage_already_used = False
    if ability.name == "Armure du mage" and hasattr(char, 'temporary_buffs'):
        armure_mage_already_used = char.temporary_buffs.get('armure_mage_active', False)

    # NOUVEAU - Vérifier uses_per_combat générique (pour toutes les capacités)
    combat_uses_exhausted = False
    combat_uses_remaining = None
    if hasattr(ability, 'uses_per_combat') and hasattr(ability, 'uses_remaining_combat'):
        combat_uses_remaining = ability.uses_remaining_combat
        combat_uses_exhausted = (ability.uses_remaining_combat <= 0)

    is_available = can_use and has_spells and not magic_already_used and not blocked_by_attack and not parade_already_used and not armure_mage_already_used and not combat_uses_exhausted

    type_icon = "🔮" if ability.spell_cost > 0 else "⚔️"
    short_name = ability.name if len(ability.name) <= 15 else ability.name[:12] + "..."

    button_key = f"sandbox_ability_{combatant_id}_{ability_index}"

    # Label conditionnel selon la raison du blocage
    button_label = f"{type_icon} {short_name}\nCoût: {ability.spell_cost} ✨"

    # Ajouter indication uses_per_combat si disponible
    if combat_uses_remaining is not None:
        button_label = f"{type_icon} {short_name}\nCoût: {ability.spell_cost} ✨ • {combat_uses_remaining}/{ability.uses_per_combat} ⚡"

    if armure_mage_already_used:
        button_label = f"{type_icon} {short_name}\n✅ Active"
    elif parade_already_used:
        button_label = f"{type_icon} {short_name}\n⚠️ Déjà utilisée"
    elif combat_uses_exhausted:
        button_label = f"{type_icon} {short_name}\n❌ 0/{ability.uses_per_combat} restant"
    elif magic_already_used:
        button_label = f"{type_icon} {short_name}\n⚠️ Déjà utilisée"
    elif blocked_by_attack:
        button_label = f"{type_icon} {short_name}\n⚠️ Attaque faite"

    if st.button(
        button_label,
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

            # Marquer qu'une attaque a été effectuée (empêche d'attaquer à nouveau + bloquer capacités magiques)
            char.can_attack_this_turn = False
            char.attack_done_this_turn = True  # NOUVEAU - Empêche capacités magiques après attaque (règle p.24)

            st.session_state.sandbox_v2_action_state = None
            save_game_state(f"{char.name} attaque {target.name}")
            # NE PAS appeler next_turn() - le héros peut encore agir (boire potion, etc.)
            st.rerun()

        # Bouton annuler
        if st.button("❌ Annuler", key=f"cancel_targeting_{combatant_id}"):
            st.session_state.sandbox_v2_action_state = None
            st.rerun()
    else:
        # Afficher boutons d'action normaux
        # Attaque (désactivé si déjà attaqué ce tour)
        can_attack = char.can_attack_this_turn if hasattr(char, 'can_attack_this_turn') else True

        if can_attack:
            if st.button("⚔️ Attaquer", key=f"sandbox_attack_{combatant_id}", type="primary", use_container_width=True):
                st.session_state.sandbox_v2_action_state = 'SELECTING_TARGET_HERO'
                st.session_state.sandbox_v2_current_actor = char
                st.rerun()
        else:
            st.button("⚔️ Attaquer (déjà fait)", key=f"sandbox_attack_{combatant_id}", disabled=True, use_container_width=True)

        # Passer
        if st.button("⏭️ Passer le Tour", key=f"sandbox_skip_{combatant_id}", use_container_width=True):
            st.session_state.sandbox_v2_log.append(f"⏭️ {char.name} passe son tour")
            save_game_state(f"{char.name} passe son tour")
            next_turn()
            st.rerun()

    # Potions
    st.markdown("### 🧪 Potions")

    # État de sélection pour "faire boire"
    action_state = st.session_state.get('sandbox_v2_action_state', None)

    # MODE SÉLECTION: Faire boire une potion
    if action_state == 'GIVING_POTION':
        st.info("🤝 Sélectionnez le type de potion à donner:")

        potions_summary = char.get_potions_summary()
        potion_type_selected = st.session_state.get('sandbox_v2_potion_type', None)

        if potion_type_selected is None:
            # Étape 1: Choisir le type de potion
            col1, col2 = st.columns(2)

            with col1:
                small_count = potions_summary['small_count']
                if small_count > 0:
                    if st.button(f"🩸 Donner Petite\n{small_count}", key=f"give_small_{combatant_id}", use_container_width=True):
                        st.session_state.sandbox_v2_potion_type = PotionType.SMALL
                        st.rerun()
                else:
                    st.button(f"🩸 Petite\n0", disabled=True, use_container_width=True)

            with col2:
                large_count = potions_summary['large_count']
                if large_count > 0:
                    if st.button(f"❤️‍🩹 Donner Grande\n{large_count}", key=f"give_large_{combatant_id}", use_container_width=True):
                        st.session_state.sandbox_v2_potion_type = PotionType.LARGE
                        st.rerun()
                else:
                    st.button(f"❤️‍🩹 Grande\n0", disabled=True, use_container_width=True)

            if st.button("❌ Annuler", key=f"cancel_give_potion_{combatant_id}"):
                st.session_state.sandbox_v2_action_state = None
                st.rerun()
        else:
            # Étape 2: Choisir la cible
            st.info("👥 Sélectionnez le héros qui recevra la potion:")

            # Liste des héros vivants (sauf soi-même)
            all_combatants = st.session_state.sandbox_v2_combatants
            available_heroes = [
                c for c in all_combatants
                if c['faction'] == 'hero'
                and c['character'].is_alive()
                and c['character'].code != char.code
            ]

            if not available_heroes:
                st.warning("Aucun autre héros disponible")
                if st.button("❌ Annuler", key=f"cancel_no_target_{combatant_id}"):
                    st.session_state.sandbox_v2_action_state = None
                    st.session_state.sandbox_v2_potion_type = None
                    st.rerun()
            else:
                # Afficher boutons de sélection pour chaque héros
                for target_data in available_heroes:
                    target = target_data['character']
                    health_pct = round((target.current_health / target.get_total_health()) * 100, 1)

                    if st.button(
                        f"🎯 {target.name} ({target.current_health}/{target.get_total_health()} PV - {health_pct}%)",
                        key=f"give_to_{target_data['id']}",
                        use_container_width=True
                    ):
                        # Exécuter l'action
                        give_potion_to_ally_action(char, target, potion_type_selected)
                        st.session_state.sandbox_v2_action_state = None
                        st.session_state.sandbox_v2_potion_type = None
                        st.rerun()

                if st.button("❌ Annuler", key=f"cancel_targeting_potion_{combatant_id}"):
                    st.session_state.sandbox_v2_action_state = None
                    st.session_state.sandbox_v2_potion_type = None
                    st.rerun()

    # MODE NORMAL: Utiliser sur soi-même ou entrer en mode "faire boire"
    else:
        if hasattr(char, 'health_potions') and char.health_potions:
            potions_summary = char.get_potions_summary()

            # Boire soi-même
            st.caption("Boire soi-même:")
            col1, col2 = st.columns(2)

            with col1:
                small_count = potions_summary['small_count']
                if small_count > 0:
                    if st.button(f"🩸 Petite\n{small_count}", key=f"sandbox_potion_small_{combatant_id}", use_container_width=True):
                        use_small_potion_action(char)
                else:
                    st.button(f"🩸 Petite\n0", disabled=True, use_container_width=True)

            with col2:
                large_count = potions_summary['large_count']
                if large_count > 0:
                    if st.button(f"❤️‍🩹 Grande\n{large_count}", key=f"sandbox_potion_large_{combatant_id}", use_container_width=True):
                        use_large_potion_action(char)
                else:
                    st.button(f"❤️‍🩹 Grande\n0", disabled=True, use_container_width=True)

            # Faire boire à un allié
            st.caption("Ou donner à un allié:")
            has_any_potion = potions_summary['total_count'] > 0

            # Vérifier si une action a déjà été prise ce tour
            action_already_taken = (
                char.action_taken_this_turn or
                char.potion_used_this_turn or
                not char.can_attack_this_turn
            )

            # Le bouton "Faire Boire" est disponible seulement si:
            # - Le héros a des potions
            # - Aucune action n'a été prise ce tour
            if has_any_potion and not action_already_taken:
                if st.button("🤝 Faire Boire une Potion", key=f"give_potion_{combatant_id}", use_container_width=True):
                    st.session_state.sandbox_v2_action_state = 'GIVING_POTION'
                    st.session_state.sandbox_v2_current_actor = char
                    st.rerun()
            else:
                button_label = "🤝 Faire Boire une Potion"
                if action_already_taken:
                    button_label += " (Action déjà prise)"
                st.button(button_label, disabled=True, use_container_width=True)
        else:
            st.info("Aucune potion")

# === ACTIONS DE COMBAT ===

def use_ability_action(char: Character, ability):
    """
    Utilise une capacité - NE termine PAS le tour automatiquement
    RÉUTILISE AbilityEffectsManager pour exécuter les effets réels
    """
    if hasattr(char, 'use_ability'):
        # 1. Vérifications + consommation sorts (via Character.use_ability)
        action = char.use_ability(ability)

        if action.success:
            # 2. Préparer le contexte pour AbilityEffectsManager (RÉUTILISE pattern TurnManager)
            adapter = st.session_state.sandbox_v2_adapter
            heroes = [c['character'] for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'hero']
            enemies = [c['character'] for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'enemy']

            context = {
                'alive_enemies': [e for e in enemies if e.is_alive()],
                'current_enemies': [e for e in enemies if e.is_alive()],
                'heroes': heroes,
                'current_heroes': heroes,
                'spell_manager': adapter.spell_manager,
                'log': st.session_state.sandbox_v2_log,
                'player_count': len([h for h in heroes if h.is_alive()])
            }

            # 3. Exécuter les effets réels via AbilityEffectsManager (RÉUTILISE architecture)
            result = adapter.ability_effects_manager.apply_ability_effects(
                char, ability, st.session_state.sandbox_v2_log, context
            )

            # 4. Feedback utilisateur
            if result:
                st.success(f"✅ {ability.name} utilisée avec succès !")
            else:
                st.warning(f"⚠️ {ability.name} utilisée (vérifiez les logs pour détails)")

            # 5. Sauvegarder état pour undo/redo
            save_game_state(f"{char.name} utilise {ability.name}")

            # 6. Rafraîchir interface (les cartes afficheront les nouvelles stats)
            st.rerun()
        else:
            # Afficher le message d'erreur spécifique (ex: limite capacités magiques)
            st.error(action.message if action.message else f"❌ Impossible d'utiliser {ability.name}")
            st.session_state.sandbox_v2_log.append(f"❌ {char.name} : {action.message}")

def use_potion_action(char: Character):
    """Utilise une potion (sélection automatique)"""
    if hasattr(char, 'use_health_potion'):
        result = char.use_health_potion()
        if result['success']:
            st.session_state.sandbox_v2_log.append(f"🧪 {char.name} boit une potion: {result['message']}")
            save_game_state(f"{char.name} utilise potion")
            st.success(f"✅ {result['message']}")
        else:
            st.error(f"❌ {result['message']}")

def use_small_potion_action(char: Character):
    """Utilise une petite potion (4 PV) - NE termine PAS le tour"""
    if hasattr(char, 'use_specific_potion'):
        result = char.use_specific_potion(PotionType.SMALL)
        if result['success']:
            st.session_state.sandbox_v2_log.append(f"🩸 {char.name} boit une Petite Potion : +{result['healing_done']} PV")
            save_game_state(f"{char.name} utilise Petite Potion")
            # NE PAS appeler next_turn() - le héros peut encore agir
            st.rerun()  # Rafraîchir l'interface pour montrer les changements
        else:
            st.error(f"❌ {result['message']}")

def use_large_potion_action(char: Character):
    """Utilise une grande potion (100% PV) - NE termine PAS le tour"""
    if hasattr(char, 'use_specific_potion'):
        result = char.use_specific_potion(PotionType.LARGE)
        if result['success']:
            st.session_state.sandbox_v2_log.append(f"❤️‍🩹 {char.name} boit une Grande Potion : +{result['healing_done']} PV")
            save_game_state(f"{char.name} utilise Grande Potion")
            # NE PAS appeler next_turn() - le héros peut encore agir
            st.rerun()  # Rafraîchir l'interface pour montrer les changements
        else:
            st.error(f"❌ {result['message']}")

def give_potion_to_ally_action(giver: Character, target: Character, potion_type: PotionType):
    """
    Fait boire une potion à un allié

    Args:
        giver: Le héros qui donne la potion
        target: Le héros qui reçoit la potion
        potion_type: Type de potion (SMALL ou LARGE)
    """
    if hasattr(giver, 'use_specific_potion'):
        result = giver.use_specific_potion(potion_type, target=target)
        if result['success']:
            potion_name = "Petite Potion" if potion_type == PotionType.SMALL else "Grande Potion"
            icon = "🩸" if potion_type == PotionType.SMALL else "❤️‍🩹"

            st.session_state.sandbox_v2_log.append(
                f"🤝 {giver.name} donne une {potion_name} à {target.name} : +{result['healing_done']} PV"
            )
            save_game_state(f"{giver.name} donne potion à {target.name}")

            # Passer au tour suivant (action exclusive)
            next_turn()

            st.success(f"✅ {icon} {giver.name} a donné une {potion_name} à {target.name} (+{result['healing_done']} PV)")
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
    defense = hero.current_parade_tokens  # CORRIGÉ: Afficher jetons actuels, pas maximum
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
    defense = enemy.defense  # Seuil de défense (à battre pour toucher)
    parade_tokens = enemy.current_parade_tokens  # Jetons de parade (bloquent dégâts)
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

    # Préparer stats_content (CORRIGÉ : défense avec cible, parade avec bouclier)
    magic_indicator = " ✨" if enemy.is_magical else ""
    stats_content = f"""
    <div style="font-family: monospace; font-size: 1rem; margin-bottom: 5px; font-weight: bold; color: #f0f0f0;">
        ❤️ {current_hp}/{max_hp} • ⚔️ {damage} • 🎯 {defense} • 🛡️ {parade_tokens}{magic_indicator}
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

                # NOUVEAU - Vérifier si le combattant est étourdi (stunned)
                is_stunned = False
                if hasattr(character, 'status_effects') and character.status_effects:
                    is_stunned = character.status_effects.get('stunned', 0) > 0

                # Bouton "À son tour" si vivant et pas déjà en cours
                if character.is_alive() and not is_current:
                    # Désactiver si déjà joué OU étourdi
                    button_disabled = has_played or is_stunned
                    if is_stunned:
                        stunned_turns = character.status_effects.get('stunned', 0)
                        button_label = f"😵 Étourdi ({stunned_turns} tours)"
                    elif has_played:
                        button_label = "✅ A joué"
                    else:
                        button_label = "▶️ À son tour"

                    if st.button(
                        button_label,
                        key=f"select_{combatant_data['faction']}_{combatant_data['id']}",
                        type="secondary" if (has_played or is_stunned) else "primary",
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

    # Indicateurs de mode
    initiative_mode = st.session_state.get('initiative_setting', True)
    criticals_mode = st.session_state.get('criticals_setting', True)
    criticals_badge = "🎯 Critiques ON" if criticals_mode else "🎯 Critiques OFF"

    if initiative_mode:
        st.caption(f"✅ Ciblage manuel | 🎲 Initiative D20 | {criticals_badge} | Système Undo/Redo")
    else:
        st.caption(f"✅ Ciblage manuel | 🎮 Ordre Manuel | {criticals_badge} | Système Undo/Redo")

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
