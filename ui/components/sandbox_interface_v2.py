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
from ui.components.combat_stats_tracker import CombatStatsTracker
from ui.components.combat_stats_analyzer import analyze_combat_results, generate_balance_recommendations
from ui.components.combat_results_display import display_combat_results_panel
from models.combat.abilities.individual_abilities.heroes.atucan import auto_activate_aura_sacree

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

def prepare_new_combat():
    """
    Prépare un nouveau combat en réinitialisant les données du combat précédent
    SANS réinitialiser la phase ni vider les combattants (ils seront recréés juste après)
    À appeler AVANT de générer l'initiative ou d'organiser les équipes
    """
    # Réinitialiser l'historique et les logs
    st.session_state.sandbox_v2_game_history = []
    st.session_state.sandbox_v2_history_index = -1
    st.session_state.sandbox_v2_log = []
    st.session_state.sandbox_v2_round_number = 1
    st.session_state.sandbox_v2_played_this_round = []
    st.session_state.sandbox_v2_current_turn_index = 0
    st.session_state.sandbox_v2_action_state = None
    st.session_state.sandbox_v2_current_actor = None

    # Réinitialiser les stats modifiées des ennemis
    if 'enemy_overrides' in st.session_state:
        del st.session_state.enemy_overrides

    # Supprimer résultat du combat précédent
    if 'sandbox_v2_combat_result' in st.session_state:
        del st.session_state.sandbox_v2_combat_result

    # Réinitialiser les compteurs des individual abilities (singleton cache)
    from models.combat.abilities.individual_abilities import reset_all_combat_uses
    reset_all_combat_uses()

def reset_combat_state():
    """
    Réinitialise COMPLÈTEMENT tous les états du combat (retour à CONFIG)
    À appeler uniquement pour le bouton "Reset Combat" ou "Nouveau Combat"
    """
    # Préparer un nouveau combat (reset partiel)
    prepare_new_combat()

    # Reset complet : retour à la phase CONFIG et vidage des combattants
    st.session_state.sandbox_v2_phase = 'CONFIG'
    st.session_state.sandbox_v2_combatants = []

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
            # NOUVEAU - Vérifier invisibilité (Lame Furtivité, Stephe Purification)
            # FIX: status_effects['invisible'] est un dict, pas un booléen
            is_invisible = hasattr(hero, 'status_effects') and 'invisible' in hero.status_effects

            # CORRIGÉ : Utiliser jetons actuels (pas maximum) pour calcul correct après Parade
            parade = hero.current_parade_tokens
            damage_after_parade = max(0, stats['damage'] - parade)

            # FIX BUG ELNEHA - En forme animale, utiliser stats brutes (sans équipements)
            is_animal_form = (hero.code == "P-1" and
                              hasattr(hero, 'current_form') and
                              hero.current_form in ["bear", "wolf"])

            if is_animal_form:
                # Stats de la forme animale (brutes, sans équipements)
                max_hp = hero.health
            else:
                # Stats normales (avec équipements)
                max_hp = hero.get_total_health()

            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

            with col1:
                if is_invisible:
                    st.write(f"**{hero.name}** 🌫️ *(Invisible)*")
                else:
                    st.write(f"**{hero.name}**")
            with col2:
                st.write(f"❤️ {hero.current_health}/{max_hp}")
            with col3:
                st.write(f"🛡️ {parade}")
            with col4:
                if is_invisible:
                    st.write("🌫️ Invisible")
                elif damage_after_parade > 0:
                    st.write(f"💔 -{damage_after_parade}")
                else:
                    st.write("✅ Bloqué")
            with col5:
                # NOUVEAU - Désactiver bouton si invisible
                if st.button("🎯 Cibler", key=f"enemy_target_{hero.name}_{id(hero)}", type="primary", use_container_width=True, disabled=is_invisible):
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

        # NOUVEAU - Log invisibilité automatique (Lame P-7-6 Assaut furieux)
        if hasattr(hero, 'status_effects') and 'invisible' in hero.status_effects:
            if hero.status_effects['invisible'].get('source') == 'ombre_mortelle':
                hero_name = getattr(hero, 'display_name', hero.name)
                log.append(f"🌑 {hero_name} redevient invisible (Assaut furieux)")

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
        enemies_data = loader.load_all_enemies()  # Charger tous les ennemis (officiels + personnalisés)
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
                    # get_hero_abilities() retourne déjà des deepcopy (instances fraîches)
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
                        # get_hero_abilities() retourne déjà des deepcopy (instances fraîches)
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

                # NOUVEAU : Appliquer les overrides de stats si présents
                if 'enemy_overrides' in st.session_state:
                    if enemy_code in st.session_state.enemy_overrides:
                        overrides = st.session_state.enemy_overrides[enemy_code]

                        # Override PV
                        if 'max_health' in overrides:
                            enemy.max_health = overrides['max_health']
                            enemy.current_health = overrides['max_health']

                        # Override dégâts - Modifier stats_by_players pour tous les player_count
                        if 'damage' in overrides:
                            new_damage = overrides['damage']
                            for pc in enemy.stats_by_players.keys():
                                if 'damage' in enemy.stats_by_players[pc]:
                                    enemy.stats_by_players[pc]['damage'] = new_damage

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

        # Initialiser log
        st.session_state.sandbox_v2_log = ["=== DÉBUT DU COMBAT ==="]

        # NOUVEAU - Activation automatique Aura sacrée d'Atucan (BUSINESS LOGIC)
        heroes = [c['character'] for c in hero_combatants]
        auto_activate_aura_sacree(heroes, st.session_state.sandbox_v2_log)

        # Sauvegarder l'état initial
        save_game_state("Début du combat")

        # Initialiser le tracker de statistiques
        tracker = CombatStatsTracker()
        tracker.initialize_combat(
            heroes=st.session_state.sandbox_v2_heroes,
            enemies=st.session_state.sandbox_v2_enemies,
            combatants=combatants  # CORRIGÉ: Passer les combattants pour IDs corrects
        )
        st.session_state.sandbox_v2_stats_tracker = tracker

        # Snapshot initial des PV (tour 0)
        tracker.snapshot_hp(
            turn_number=0,
            combatants=st.session_state.sandbox_v2_combatants
        )

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

    # NOUVEAU - Log effets persistants actifs (Aura sacrée, etc.)
    log_active_persistent_effects()

    # LOGIQUE UI : Sauvegarder l'état du jeu (système Undo/Redo)
    save_game_state("Initiative générée")

def log_active_persistent_effects():
    """
    Log tous les effets persistants actifs au début du round.
    Appelé juste après "=== ROUND X ===" pour afficher les auras/buffs permanents.

    Structure attendue dans le log:
        === ROUND X ===
        ✨ Aura sacrée d'Atucan active (-1 blessure/attaque pour tous)
        [autres effets persistants futurs...]
        🛡️ Phase des Héros + Pets

    Vérifie:
        - Aura sacrée d'Atucan (tant qu'il est vivant)
        - Autres effets persistants peuvent être ajoutés ici
    """
    combatants = st.session_state.sandbox_v2_combatants
    heroes = [c['character'] for c in combatants if c['faction'] == 'hero' and c['character'].is_alive()]

    # Vérifier Aura sacrée d'Atucan (P-3)
    atucan = next((h for h in heroes if h.code == "P-3"), None)
    if atucan and atucan.is_alive():
        # Vérifier si l'aura est effectivement active sur au moins un héros
        aura_active = any(
            hasattr(h, 'temporary_buffs') and 'aura_protection' in h.temporary_buffs
            for h in heroes
        )
        if aura_active:
            st.session_state.sandbox_v2_log.append("✨ Aura sacrée d'Atucan active (-1 blessure/attaque pour tous)")

    # Espace réservé pour d'autres effets persistants futurs
    # Exemple: buffs de groupe, malédictions permanentes, etc.

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

    # NOUVEAU - Log effets persistants actifs (Aura sacrée, etc.)
    log_active_persistent_effects()

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

def is_enemy_stunned(enemy) -> tuple:
    """
    Vérifie si un ennemi est étourdi (stunned) SANS décrémenter le compteur

    Fonction centralisée utilisée par :
    - display_enemy_interface() : Bloquer les actions si stunné
    - display_enemy_combat_card() : Afficher badge "😵 Étourdi (X tours)"
    - Mode manuel : Désactiver bouton "▶️ À son tour"

    Returns:
        (is_stunned, turns_remaining): (bool, int)
        - is_stunned: True si l'ennemi a stunned > 0
        - turns_remaining: Nombre de tours restants (0 si pas stunné)
    """
    if hasattr(enemy, 'status_effects') and enemy.status_effects:
        stunned_data = enemy.status_effects.get('stunned', None)
        if stunned_data:
            # stunned peut être un dict {'duration': X} ou un int (legacy)
            if isinstance(stunned_data, dict):
                stunned_turns = stunned_data.get('duration', 0)
            else:
                stunned_turns = stunned_data
            return (stunned_turns > 0, stunned_turns)
    return (False, 0)

def next_turn():
    """
    Passe au tour suivant EN SAUTANT les combattants morts (utilise is_alive())

    Comportement selon le mode :
    - MODE INITIATIVE : Passe automatiquement au combattant suivant dans l'ordre
    - MODE MANUEL : Réinitialise à -1 pour attendre une nouvelle sélection manuelle
    """
    if not st.session_state.sandbox_v2_combatants:
        return

    # Enregistrer la fin du tour du combattant actuel (pour stats)
    current_turn_index = st.session_state.get('sandbox_v2_current_turn_index', -1)
    if current_turn_index >= 0 and current_turn_index < len(st.session_state.sandbox_v2_combatants):
        current = st.session_state.sandbox_v2_combatants[current_turn_index]
        combatant_id = current['id']
        turn_number = st.session_state.get('sandbox_v2_round_number', 1)

        # Tracker stats
        tracker = st.session_state.get('sandbox_v2_stats_tracker')
        if tracker:
            tracker.record_turn_end(combatant_id, turn_number)

            # Snapshot des PV après chaque tour pour courbe d'évolution
            tracker.snapshot_hp(
                turn_number=turn_number,
                combatants=st.session_state.sandbox_v2_combatants
            )

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

            # NOUVEAU - Log effets persistants actifs (Aura sacrée, etc.)
            log_active_persistent_effects()

            # CRITIQUE : Décrémenter les compteurs stunned (même logique que mode manuel)
            for combatant in st.session_state.sandbox_v2_combatants:
                char = combatant['character']
                if combatant['faction'] == 'enemy' and hasattr(char, 'status_effects'):
                    if 'stunned' in char.status_effects:
                        stunned_data = char.status_effects['stunned']
                        # Gérer format dict ou int (legacy)
                        if isinstance(stunned_data, dict):
                            duration = stunned_data.get('duration', 0)
                            if duration > 0:
                                stunned_data['duration'] = duration - 1
                                if stunned_data['duration'] <= 0:
                                    del char.status_effects['stunned']
                                    st.session_state.sandbox_v2_log.append(f"✅ {char.name} n'est plus étourdi")
                        else:
                            # Legacy: stunned est un int
                            if stunned_data > 0:
                                char.status_effects['stunned'] -= 1
                                if char.status_effects['stunned'] <= 0:
                                    del char.status_effects['stunned']
                                    st.session_state.sandbox_v2_log.append(f"✅ {char.name} n'est plus étourdi")

                # NOUVEAU : Décrémenter Aura sacrée (pour tous les personnages)
                if combatant['faction'] == 'hero' and hasattr(char, 'temporary_buffs'):
                    if 'aura_protection' in char.temporary_buffs:
                        aura = char.temporary_buffs['aura_protection']
                        if 'rounds_remaining' in aura:
                            aura['rounds_remaining'] -= 1
                            if aura['rounds_remaining'] <= 0:
                                del char.temporary_buffs['aura_protection']
                                st.session_state.sandbox_v2_log.append(f"✨ Aura sacrée de {char.name} a expiré")

                    # NOUVEAU : Recharger Raishi Maîtrise absolue (au début de chaque round pour TOUS les héros)
                    if 'raishi_maitrise_charges' in char.temporary_buffs:
                        maitrise = char.temporary_buffs['raishi_maitrise_charges']
                        if isinstance(maitrise, dict) and maitrise.get('auto_recharge', False):
                            max_charges = maitrise.get('max_charges', 2)
                            old_charges = maitrise.get('charges', 0)
                            maitrise['charges'] = max_charges  # Recharge complète à chaque round
                            if old_charges < max_charges:
                                st.session_state.sandbox_v2_log.append(f"🛡️✨ {char.name} - Maîtrise absolue rechargée ({max_charges} charges)")

                # NOUVEAU : Décrémenter compteur furtivité de Lame au début du round (pour tous les héros)
                if combatant['faction'] == 'hero' and hasattr(char, 'status_effects'):
                    if 'invisible' in char.status_effects:
                        stealth_data = char.status_effects['invisible']
                        # Vérifier si c'est la furtivité de Lame avec compteur de tours
                        if isinstance(stealth_data, dict) and stealth_data.get('source') == 'lame_furtivite':
                            if 'turns_remaining' in stealth_data:
                                stealth_data['turns_remaining'] -= 1
                                # Si compteur atteint 0, supprimer la furtivité
                                if stealth_data['turns_remaining'] <= 0:
                                    del char.status_effects['invisible']
                                    st.session_state.sandbox_v2_log.append(f"🌑 {char.name} redevient visible (furtivité expirée)")

        # Vérifier si le combattant actuel est vivant (API Character.is_alive())
        current = get_current_combatant()
        if current and current['character'].is_alive():
            char = current['character']

            # Vérifier stun SANS décrémenter (déjà fait dans main_sandbox_v2)
            if current['faction'] == 'enemy':
                is_stunned_here, _ = is_enemy_stunned(char)
                if is_stunned_here:
                    # Ennemi stunné - sauter SANS décrémenter (déjà fait dans main_sandbox_v2)
                    iterations += 1
                    continue  # Passer au combattant suivant

            # Initialiser le tour du combattant (reset jetons parade + compteurs capacités magiques)
            if current['faction'] == 'hero':
                char.start_hero_turn()

                # NOUVEAU - Log invisibilité automatique (Lame P-7-6 Assaut furieux)
                if hasattr(char, 'status_effects') and 'invisible' in char.status_effects:
                    if char.status_effects['invisible'].get('source') == 'ombre_mortelle':
                        char_name = getattr(char, 'display_name', char.name)
                        st.session_state.sandbox_v2_log.append(f"🌑 {char_name} redevient invisible (Assaut furieux)")
            else:
                char.start_enemy_turn()

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

    # FIX BUG 1 (bis): En forme animale, utiliser stats brutes (même logique que display_hero_combat_card)
    is_animal_form = (char.code == "P-1" and
                      hasattr(char, 'current_form') and
                      char.current_form in ["bear", "wolf"])

    if is_animal_form:
        # Stats de la forme animale (brutes, sans équipements)
        max_hp = char.health
        precision = char.precision
        attack = char.damage
        magic = char.spells
        defense = char.max_parade_tokens  # FIX: Parade brute (sans équipements)
    else:
        # Stats normales (avec équipements)
        max_hp = char.get_total_health()
        precision = char.get_total_precision()
        attack = char.get_total_damage()
        magic = char.get_total_spells()
        defense = char.get_total_parade()

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
            <div class="stat-badge precision">
                <div style="font-size: 0.8rem;">🎯 PRE</div>
                <div style="font-weight: bold;">{precision}</div>
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

    # CRITIQUE : Vérifier stun AVANT d'afficher les actions (fonction centralisée)
    is_stunned, stunned_turns = is_enemy_stunned(char)

    # Stats ennemis (RÉUTILISE APIs Enemy)
    current_hp = char.current_health
    max_hp = char.max_health
    player_count = len([h for h in st.session_state.sandbox_v2_heroes if h.is_alive()])
    stats = char.get_stats_for_players(player_count)
    attack = stats['damage']
    defense = char.defense  # Seuil HIT (à battre pour toucher) - TOUJOURS utiliser l'attribut direct
    parade_tokens = char.current_parade_tokens

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
            <div class="stat-badge precision">
                <div style="font-size: 0.8rem;">🎯 HIT</div>
                <div style="font-weight: bold;">{defense}</div>
            </div>
            <div class="stat-badge defense">
                <div style="font-size: 0.8rem;">🛡️ DEF</div>
                <div style="font-weight: bold;">{parade_tokens}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Si l'ennemi est étourdi, bloquer les actions et passer automatiquement le tour
    if is_stunned:
        st.markdown("### 😵 Étourdi !")
        st.warning(f"**{char.name}** est étourdi pour encore **{stunned_turns} tour(s)** ! Son tour est automatiquement sauté.")

        # Bouton pour passer manuellement (mode manuel) ou auto-skip (mode initiative)
        if st.button("⏭️ Sauter le tour (Étourdi)", key=f"sandbox_enemy_stunned_{combatant['id']}", type="secondary", use_container_width=True):
            # Décrémenter le compteur via check_enemy_status_effects()
            if hasattr(char, 'check_enemy_status_effects'):
                status = char.check_enemy_status_effects()
                stunned_after = char.status_effects.get('stunned', 0) if hasattr(char, 'status_effects') else 0
                st.session_state.sandbox_v2_log.append(f"😵 {char.name} est étourdi ! ({stunned_turns} → {stunned_after} tour(s)) - Tour sauté")

            save_game_state(f"{char.name} étourdi - tour sauté")
            next_turn()
            st.rerun()
        return  # NE PAS afficher les actions d'attaque

    # Actions ennemi (seulement si NON stunné)
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
            attack_result = adapter.combat_actions.enemy_attack(
                enemy=char,
                heroes=heroes_list,
                player_count=player_count,
                log=st.session_state.sandbox_v2_log,
                active_pets=[],  # Pas de pets dans Sandbox V2 pour l'instant
                manual_target=target
            )

            # Track enemy attack stats
            if 'sandbox_v2_stats_tracker' in st.session_state and attack_result:
                tracker = st.session_state.sandbox_v2_stats_tracker
                tracker.record_attack(
                    char, target, attack_result['hit'], attack_result['damage'],
                    is_critical=False, is_fail=False
                )
                # Track damage taken by hero (TOUJOURS si hit, même si parade bloque tout)
                if attack_result['hit']:
                    parade_used = attack_result.get('parade_used', 0)
                    damage = attack_result['damage']
                    # Appeler record_damage_taken même si damage=0 (parade peut avoir bloqué tout)
                    tracker.record_damage_taken(
                        target,
                        damage,
                        parade_used=parade_used
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
            if st.button("⏭️ Fin du Tour", key=f"sandbox_enemy_skip_{combatant['id']}", use_container_width=True):
                st.session_state.sandbox_v2_log.append(f"⏭️ {char.name} termine son tour")
                save_game_state(f"{char.name} termine son tour")
                next_turn()
                st.rerun()

def display_abilities_grid(char: Character, combatant_id: str):
    """Grille capacités style Arène - Gère formes animales Elneha"""
    if not hasattr(char, 'abilities') or not char.abilities:
        st.markdown("### 🔮 Capacités Spéciales")
        st.info("Aucune capacité disponible")
        return

    # CAS SPÉCIAL ELNEHA : Filtrer capacités selon forme
    abilities_to_display = char.abilities
    is_elneha_animal_form = (char.code == "P-1" and
                             hasattr(char, 'current_form') and
                             char.current_form in ["bear", "wolf"])

    if is_elneha_animal_form:
        # En forme animale : Bouton désactivation + capacité exclusive
        abilities_to_display = []

        if char.current_form == "bear":
            # Bouton pour désactiver (P-1-1) + Capacité exclusive (101)
            for a in char.abilities:
                if a.ability_number in [1, 101]:
                    abilities_to_display.append(a)
        elif char.current_form == "wolf":
            # Bouton pour désactiver (P-1-3) + Capacité exclusive (102)
            for a in char.abilities:
                if a.ability_number in [3, 102]:
                    abilities_to_display.append(a)

        if abilities_to_display:
            st.markdown("### 🔮 Forme Animale")

            # Affichage dynamique sans grille fixe - seulement les capacités disponibles
            cols = st.columns(len(abilities_to_display))
            for idx, ability in enumerate(abilities_to_display):
                with cols[idx]:
                    original_index = char.abilities.index(ability) if ability in char.abilities else idx
                    display_ability_card(char, ability, combatant_id, original_index)
        else:
            st.markdown("### 🔮 Capacités Spéciales")
            st.warning("⚠️ Capacités de forme manquantes")

        return  # Sortir ici pour éviter d'afficher la grille 3x2 en dessous

    # Forme humaine : capacités normales (1-6)
    # Exclure les capacités exclusives (101, 102) de l'affichage normal
    abilities_to_display = [a for a in char.abilities if a.ability_number <= 100]
    st.markdown("### 🔮 Capacités Spéciales")

    # Grille 3x2 pour forme humaine seulement
    for row in range(2):
        cols = st.columns(3)
        for col_idx in range(3):
            ability_index = row * 3 + col_idx

            with cols[col_idx]:
                if ability_index < len(abilities_to_display):
                    ability = abilities_to_display[ability_index]
                    # Trouver l'index original pour le key unique
                    original_index = char.abilities.index(ability) if ability in char.abilities else ability_index
                    display_ability_card(char, ability, combatant_id, original_index)
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
        # FIX BUG ELNEHA - En forme animale, utiliser stats brutes (sans équipements)
        is_animal_form = (char.code == "P-1" and
                          hasattr(char, 'current_form') and
                          char.current_form in ["bear", "wolf"])

        if is_animal_form:
            current_spells = char.spells
        else:
            current_spells = char.get_total_spells() if hasattr(char, 'get_total_spells') else 0

    # FIX BUG 2: Retour forme humaine ne coûte PAS de sorts
    is_transformation = (char.code == "P-1" and ability.ability_number in [1, 3])
    current_form = getattr(char, 'current_form', 'human') if is_transformation else None
    is_reverting_to_human = (
        is_transformation and (
            (ability.ability_number == 1 and current_form == "bear") or
            (ability.ability_number == 3 and current_form == "wolf")
        )
    )

    # Ne pas vérifier le coût en sorts pour le retour en forme humaine
    has_spells = is_reverting_to_human or (ability.spell_cost <= current_spells)

    # Vérifier si une capacité magique a déjà été utilisée ce tour (règle p.24)
    prevents_attack = getattr(ability, 'prevents_attack', False)
    magic_already_used = (
        prevents_attack and
        getattr(char, 'magic_abilities_used_this_turn', 0) >= 1
    )

    # NOUVEAU - Vérifier si une attaque a été effectuée (règle p.24 - blocage bidirectionnel)
    attack_already_done = getattr(char, 'attack_done_this_turn', False)
    blocked_by_attack = prevents_attack and attack_already_done

    # NOUVEAU - Vérifier si Parade a déjà été utilisée ce tour (limitation 1/tour)
    parade_already_used = False
    parade_blocked_by_attack = False
    if ability.name == "Parade" and hasattr(char, 'temporary_buffs'):
        parade_already_used = char.temporary_buffs.get('parade_used_this_turn', False)
        parade_blocked_by_attack = char.temporary_buffs.get('parade_blocked_by_attack', False)

    # NOUVEAU - Vérifier si Armure du Mage déjà utilisée (limitation 1/combat permanent)
    armure_mage_already_used = False
    if ability.name == "Armure du mage" and hasattr(char, 'temporary_buffs'):
        armure_mage_already_used = char.temporary_buffs.get('armure_mage_active', False)

    # NOUVEAU - Vérifier uses_per_combat générique (pour toutes les capacités)
    combat_uses_exhausted = False
    combat_uses_remaining = None
    if (hasattr(ability, 'uses_per_combat') and hasattr(ability, 'uses_remaining_combat') and
        ability.uses_per_combat is not None and ability.uses_remaining_combat is not None):
        combat_uses_remaining = ability.uses_remaining_combat
        combat_uses_exhausted = (ability.uses_remaining_combat <= 0)

    # NOUVEAU - Aura sacrée d'Atucan : Capacité automatique (toujours désactivée)
    is_aura_sacree = (ability.name == "Aura sacrée")

    # NOUVEAU - Désactiver capacités "Pas utile en combat"
    not_useful_in_combat = False
    if hasattr(ability, 'description') and ability.description:
        not_useful_in_combat = "Pas utile en combat" in ability.description or "pas utile en combat" in ability.description

    # NOUVEAU - Lame (P-7): Limitation 1 capacité par tour
    lame_ability_already_used = False
    if char.code == "P-7" and hasattr(char, 'temporary_buffs'):
        lame_ability_already_used = char.temporary_buffs.get('lame_ability_used_this_turn', False)

    # NOUVEAU - Elneha transformations : Bloquer si action déjà prise
    transformation_blocked_by_action = False
    is_transformation = (char.code == "P-1" and ability.ability_number in [1, 3])
    if is_transformation:
        # Vérifier si on est déjà dans la forme correspondante (pour permettre le retour)
        current_form = getattr(char, 'current_form', 'human')
        is_form_active = (
            (ability.ability_number == 1 and current_form == "bear") or
            (ability.ability_number == 3 and current_form == "wolf")
        )

        # Si forme active, TOUJOURS permettre le retour (ne pas bloquer)
        if is_form_active:
            transformation_blocked_by_action = False
        else:
            # Sinon, bloquer transformation si une action a déjà été prise ce tour
            transformation_blocked_by_action = (
                getattr(char, 'action_taken_this_turn', False) or
                getattr(char, 'potion_used_this_turn', False) or
                not getattr(char, 'can_attack_this_turn', True)
            )

    is_available = can_use and has_spells and not magic_already_used and not blocked_by_attack and not parade_already_used and not parade_blocked_by_attack and not armure_mage_already_used and not combat_uses_exhausted and not not_useful_in_combat and not lame_ability_already_used and not transformation_blocked_by_action and not is_aura_sacree

    type_icon = "🔮" if ability.spell_cost > 0 else "⚔️"
    short_name = ability.name if len(ability.name) <= 15 else ability.name[:12] + "..."

    button_key = f"sandbox_ability_{combatant_id}_{ability_index}"

    # NOUVEAU - Elneha transformations : Modifier label si forme active
    is_form_active = False
    if is_transformation:
        current_form = getattr(char, 'current_form', 'human')
        if ability.ability_number == 1 and current_form == "bear":
            is_form_active = True
            short_name = "Redevenir humain"
            type_icon = "👤"
        elif ability.ability_number == 3 and current_form == "wolf":
            is_form_active = True
            short_name = "Redevenir humain"
            type_icon = "👤"

    # Label conditionnel selon la raison du blocage
    button_label = f"{type_icon} {short_name}\n• {ability.spell_cost} ✨"

    # Ajouter indication uses_per_combat si disponible
    if combat_uses_remaining is not None:
        button_label = f"{type_icon} {short_name}\n• {ability.spell_cost} ✨ • {combat_uses_remaining}/{ability.uses_per_combat} ⚡"

    # NOUVEAU - Elneha transformations : Label spécial si forme active (retour gratuit)
    if is_form_active:
        button_label = f"{type_icon} {short_name}\n• Gratuit"

    if is_aura_sacree:
        button_label = f"✨ {short_name}\n⚡ Automatique - Active"
    elif not_useful_in_combat:
        button_label = f"{type_icon} {short_name}\n🚫 Hors combat"
    elif armure_mage_already_used:
        button_label = f"{type_icon} {short_name}\n✅ Active"
    elif lame_ability_already_used:
        button_label = f"{type_icon} {short_name}\n⚠️ 1 capacité/tour"
    elif parade_already_used:
        button_label = f"{type_icon} {short_name}\n⚠️ Déjà utilisée"
    elif parade_blocked_by_attack:
        button_label = f"{type_icon} {short_name}\n⚠️ Attaque faite"
    elif combat_uses_exhausted:
        button_label = f"{type_icon} {short_name}\n❌ 0/{ability.uses_per_combat} restant"
    elif magic_already_used:
        button_label = f"{type_icon} {short_name}\n⚠️ Déjà utilisée"
    elif blocked_by_attack:
        button_label = f"{type_icon} {short_name}\n⚠️ Attaque faite"
    elif transformation_blocked_by_action:
        button_label = f"{type_icon} {short_name}\n⚠️ Action déjà prise"

    # Tooltip avec description de la capacité
    tooltip_text = ability.description if hasattr(ability, 'description') else None

    if st.button(
        button_label,
        key=button_key,
        type="primary" if is_available else "secondary",
        disabled=not is_available,
        use_container_width=True,
        help=tooltip_text  # Affiche la description au survol
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

            # NOUVEAU - Vérifier buffs multi-cibles (Kraor, Lame, Raishi)
            attack_all = hasattr(char, 'temporary_buffs') and (
                'attack_all_enemies' in char.temporary_buffs or
                'assassination_ready' in char.temporary_buffs or
                'esquive_parfaite_ready' in char.temporary_buffs
            )

            if attack_all:
                # Attaquer TOUS les ennemis vivants
                alive_enemies = [e for e in enemies_list if e.is_alive()]

                # NOUVEAU - Raishi Esquive parfaite : 1 jet unique pour tous (single_roll)
                # NOTE: Esquive parfaite devrait faire 1 seul jet de toucher, et si réussi,
                # appliquer les dégâts à tous les ennemis. L'implémentation actuelle fait
                # un jet par ennemi pour simplifier, mais le concept reste "attaque multi-cible"
                esquive_single_roll = False
                if 'esquive_parfaite_ready' in char.temporary_buffs:
                    esquive_data = char.temporary_buffs['esquive_parfaite_ready']
                    if isinstance(esquive_data, dict):
                        esquive_single_roll = esquive_data.get('single_roll', False)

                if esquive_single_roll:
                    st.session_state.sandbox_v2_log.append(f"⚔️ {char.name} déclenche Esquive parfaite ! (1 jet → tous ennemis)")
                else:
                    st.session_state.sandbox_v2_log.append(f"⚔️ {char.name} déclenche une attaque multi-cible !")

                for enemy in alive_enemies:
                    attack_result = adapter.combat_actions.hero_attack(char, [enemy], player_count, st.session_state.sandbox_v2_log)

                    # Track attack stats
                    if 'sandbox_v2_stats_tracker' in st.session_state and attack_result:
                        tracker = st.session_state.sandbox_v2_stats_tracker
                        tracker.record_attack(
                            char, enemy, attack_result['hit'], attack_result['damage'],
                            attack_result['critical'], attack_result['critical_fail']
                        )
                        # Track damage taken by enemy (TOUJOURS si hit, même si parade bloque tout)
                        if attack_result['hit']:
                            tracker.record_damage_taken(
                                enemy,
                                attack_result['damage'],
                                parade_used=attack_result.get('parade_used', 0)
                            )

                # Consommer les buffs multi-cibles
                if hasattr(char, 'temporary_buffs'):
                    char.temporary_buffs.pop('attack_all_enemies', None)
                    char.temporary_buffs.pop('assassination_ready', None)
                    char.temporary_buffs.pop('esquive_parfaite_ready', None)

                save_game_state(f"{char.name} attaque multi-cible ({len(alive_enemies)} ennemis)")
            else:
                # Attaque normale (cible unique)
                # NOTE: Méditation (Raishi P-8-2) gérée automatiquement par combat_actions.py
                # La 2e frappe (dégâts / 2) est déclenchée automatiquement après l'attaque réussie
                attack_result = adapter.combat_actions.hero_attack(char, [target], player_count, st.session_state.sandbox_v2_log)

                # Track attack stats
                if 'sandbox_v2_stats_tracker' in st.session_state and attack_result:
                    tracker = st.session_state.sandbox_v2_stats_tracker
                    tracker.record_attack(
                        char, target, attack_result['hit'], attack_result['damage'],
                        attack_result['critical'], attack_result['critical_fail']
                    )
                    # Track damage taken by target (TOUJOURS si hit, même si parade bloque tout)
                    if attack_result['hit']:
                        tracker.record_damage_taken(
                            target,
                            attack_result['damage'],
                            parade_used=attack_result.get('parade_used', 0)
                        )

                save_game_state(f"{char.name} attaque {target.name}")

            # Marquer qu'une attaque a été effectuée
            # NOUVEAU - Kraor Pluie de flèches : Permettre 2 attaques si buff actif
            has_double_attacks = hasattr(char, 'temporary_buffs') and 'double_attacks_permanent' in char.temporary_buffs

            if has_double_attacks:
                # Compter les attaques ce tour dans temporary_buffs (dict flexible)
                if not hasattr(char, 'temporary_buffs'):
                    char.temporary_buffs = {}

                attacks_count = char.temporary_buffs.get('attacks_this_turn', 0)
                char.temporary_buffs['attacks_this_turn'] = attacks_count + 1

                # Bloquer après 2 attaques
                if char.temporary_buffs['attacks_this_turn'] >= 2:
                    char.can_attack_this_turn = False
                # Sinon, permettre une 2ème attaque
            else:
                # Comportement normal : bloquer après 1 attaque
                char.can_attack_this_turn = False

            char.attack_done_this_turn = True  # NOUVEAU - Empêche capacités magiques après attaque (règle p.24)

            # NOUVEAU - Si Atucan attaque, désactiver Parade pour ce tour (règle inverse de Parade)
            if hasattr(char, 'code') and char.code == "P-3":  # Atucan
                if not hasattr(char, 'temporary_buffs'):
                    char.temporary_buffs = {}
                char.temporary_buffs['parade_blocked_by_attack'] = True

            st.session_state.sandbox_v2_action_state = None
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
                # Vérifier si attack_all_enemies est actif (Kraor capacité 4)
                attack_all = hasattr(char, 'temporary_buffs') and 'attack_all_enemies' in char.temporary_buffs

                if attack_all:
                    # Attaque multi-cible : pas besoin de sélectionner une cible
                    enemy_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'enemy']
                    enemies_list = [c['character'] for c in enemy_combatants]
                    hero_combatants = [c for c in st.session_state.sandbox_v2_combatants if c['faction'] == 'hero']
                    heroes_list = [c['character'] for c in hero_combatants]
                    player_count = len([h for h in heroes_list if h.is_alive()])
                    adapter = st.session_state.sandbox_v2_adapter

                    # Attaquer TOUS les ennemis vivants
                    alive_enemies = [e for e in enemies_list if e.is_alive()]
                    st.session_state.sandbox_v2_log.append(f"💥 {char.name} déclenche une attaque ciblant TOUS les ennemis !")
                    for enemy in alive_enemies:
                        attack_result = adapter.combat_actions.hero_attack(char, [enemy], player_count, st.session_state.sandbox_v2_log)

                        # Track attack stats
                        if 'sandbox_v2_stats_tracker' in st.session_state and attack_result:
                            tracker = st.session_state.sandbox_v2_stats_tracker
                            tracker.record_attack(
                                char, enemy, attack_result['hit'], attack_result['damage'],
                                attack_result['critical'], attack_result['critical_fail']
                            )
                            # Track damage taken by enemy (TOUJOURS si hit, même si parade bloque tout)
                            if attack_result['hit']:
                                tracker.record_damage_taken(
                                    enemy,
                                    attack_result['damage'],
                                    parade_used=attack_result.get('parade_used', 0)
                                )

                    # Consommer le buff
                    char.temporary_buffs.pop('attack_all_enemies', None)

                    # Marquer attaque effectuée
                    char.can_attack_this_turn = False
                    char.attack_done_this_turn = True

                    save_game_state(f"{char.name} attaque multi-cible ({len(alive_enemies)} ennemis)")
                    st.rerun()
                else:
                    # Attaque normale : sélectionner une cible
                    st.session_state.sandbox_v2_action_state = 'SELECTING_TARGET_HERO'
                    st.session_state.sandbox_v2_current_actor = char
                    st.rerun()
        else:
            st.button("⚔️ Attaquer (déjà fait)", key=f"sandbox_attack_{combatant_id}", disabled=True, use_container_width=True)

        # Passer
        if st.button("⏭️ Fin du Tour", key=f"sandbox_skip_{combatant_id}", use_container_width=True):
            st.session_state.sandbox_v2_log.append(f"⏭️ {char.name} termine son tour")
            save_game_state(f"{char.name} termine son tour")
            next_turn()
            st.rerun()

    # NOUVEAU - Bouton Rage pour Thordius (P-5) si Berserker débloqué
    if hasattr(char, 'code') and char.code == "P-5":
        berserker_unlocked = hasattr(char, 'temporary_buffs') and char.temporary_buffs.get('berserker_unlocked', False)

        if berserker_unlocked:
            rage_active = char.temporary_buffs.get('berserker_rage_active', False)

            st.markdown("### 🔥 Mode Berserker")
            if st.button(
                f"{'🔥 DÉSACTIVER RAGE' if rage_active else '⚔️ ACTIVER RAGE'}",
                key=f"toggle_rage_{combatant_id}",
                type="primary" if rage_active else "secondary",
                use_container_width=True
            ):
                char.temporary_buffs['berserker_rage_active'] = not rage_active
                new_state = "activée" if not rage_active else "désactivée"
                st.session_state.sandbox_v2_log.append(f"🔥 {char.name} - Rage {new_state}")
                save_game_state(f"{char.name} - Rage {new_state}")
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

                    # FIX BUG ELNEHA - En forme animale, utiliser stats brutes (sans équipements)
                    is_target_animal_form = (target.code == "P-1" and
                                             hasattr(target, 'current_form') and
                                             target.current_form in ["bear", "wolf"])

                    if is_target_animal_form:
                        # Stats de la forme animale (brutes, sans équipements)
                        target_max_hp = target.health
                    else:
                        # Stats normales (avec équipements)
                        target_max_hp = target.get_total_health()

                    health_pct = round((target.current_health / target_max_hp) * 100, 1)

                    if st.button(
                        f"🎯 {target.name} ({target.current_health}/{target_max_hp} PV - {health_pct}%)",
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
        # NOUVEAU - Elneha formes animales : Bloquer toutes les potions
        is_elneha_animal = (char.code == "P-1" and
                           hasattr(char, 'current_form') and
                           char.current_form in ["bear", "wolf"])

        if is_elneha_animal:
            st.warning("⚠️ Potions indisponibles en forme animale")
        elif hasattr(char, 'health_potions') and char.health_potions:
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

            # Track ability usage (gérer format dict ET bool)
            if 'sandbox_v2_stats_tracker' in st.session_state:
                spell_cost = getattr(ability, 'spell_cost', 0)

                # Normaliser result (peut être dict ou bool)
                if isinstance(result, dict):
                    success = result.get('success', False)
                    damage_dealt = result.get('damage_dealt', 0)
                elif isinstance(result, bool):
                    success = result
                    damage_dealt = 0
                else:
                    success = False
                    damage_dealt = 0

                st.session_state.sandbox_v2_stats_tracker.record_ability_used(
                    char, ability.name, success, spell_cost, damage_dealt
                )

                # Track damage taken by targets (pour capacités offensives)
                if isinstance(result, dict) and 'targets_hit' in result:
                    for target, damage in result['targets_hit']:
                        # Les capacités magiques ignorent la parade (règles officielles)
                        st.session_state.sandbox_v2_stats_tracker.record_damage_taken(
                            target,
                            damage,
                            parade_used=0
                        )

            # 4. Feedback utilisateur (gérer format dict ET bool)
            success_flag = result.get('success', False) if isinstance(result, dict) else result
            if success_flag:
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

            # Track potion usage
            if 'sandbox_v2_stats_tracker' in st.session_state:
                st.session_state.sandbox_v2_stats_tracker.record_potion_used(
                    char, 'small', result['healing_done']
                )

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

            # Track potion usage
            if 'sandbox_v2_stats_tracker' in st.session_state:
                st.session_state.sandbox_v2_stats_tracker.record_potion_used(
                    char, 'large', result['healing_done']
                )

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

    # NOUVEAU - En forme animale, utiliser stats brutes (sans équipements)
    is_animal_form = (hero.code == "P-1" and
                      hasattr(hero, 'current_form') and
                      hero.current_form in ["bear", "wolf"])

    if is_animal_form:
        # Stats de la forme animale (brutes, sans équipements)
        max_hp = hero.health
        precision = hero.precision
        attack = hero.damage
        magic = hero.spells  # FIX BUG 1: Sorts bruts de la forme (sans équipements)
    else:
        # Stats normales (avec équipements)
        max_hp = hero.get_total_health()
        precision = hero.get_total_precision()
        attack = hero.get_total_damage()
        magic = hero.get_total_spells()  # FIX BUG 1: Déplacé dans le else

    defense = hero.current_parade_tokens  # CORRIGÉ: Afficher jetons actuels, pas maximum
    is_alive = hero.is_alive()

    # Détermination border color selon l'état
    if is_current_turn:
        border_color = "#FFD700"  # Doré pour tour actuel
    elif not is_alive:
        border_color = "#666"  # Gris pour mort
    else:
        border_color = "#27ae60"  # Vert pour vivant en attente

    # Récupérer image (RÉUTILISE API ui_elements.py)
    # Pour Elneha, passer la forme actuelle pour afficher l'image correcte
    current_form = getattr(hero, 'current_form', None) if hero.code == "P-1" else None
    image_path = get_hero_image_path(hero.name, current_form)
    background_style = ""
    if image_path:
        img_base64 = load_hero_image_base64(image_path)
        if img_base64:
            background_style = f"background-image: url('data:image/jpeg;base64,{img_base64}');"

    # Fallback background si pas d'image
    if not background_style:
        background_style = f"background: linear-gradient(135deg, {border_color}33, {border_color}11);"

    # Préparer stats_content (2 stats par ligne pour meilleure lisibilité)
    stats_content = f"""
    <div style="font-family: monospace; font-size: 0.85rem; margin-bottom: 5px; font-weight: bold; color: #f0f0f0; line-height: 1.5;">
        ❤️ {current_hp}/{max_hp} PV 🎯 {precision} PRE<br/>
        ⚔️ {attack} ATT 🛡️ {defense} DEF<br/>
        ✨ {magic} MAG
    </div>"""

    # NOUVEAU - Vérifier buff Forme de loup (RÉUTILISE temporary_buffs API)
    wolf_form_active = False
    wolf_remaining = 0
    if hasattr(hero, 'temporary_buffs') and hero.temporary_buffs:
        wolf_remaining = hero.temporary_buffs.get('elneha_wolf_remaining', 0)
        wolf_form_active = wolf_remaining > 0

    # NOUVEAU - Vérifier buff Pluie de flèches (Kraor P-4-6)
    pluie_active = False
    if hasattr(hero, 'temporary_buffs') and hero.temporary_buffs:
        pluie_active = 'double_attacks_permanent' in hero.temporary_buffs

    # NOUVEAU - Vérifier rage Berserker (Thordius P-5-6)
    rage_active = False
    if hasattr(hero, 'temporary_buffs') and hero.temporary_buffs:
        rage_active = hero.temporary_buffs.get('berserker_rage_active', False)

    # Préparer build_content (remplacé par status pour le combat)
    if is_current_turn:
        build_content = '<div style="font-size: 1.1rem; font-weight: bold; color: #FFD700; text-shadow: 2px 2px 4px black;">⚡ C\'EST SON TOUR</div>'
    elif not is_alive and rage_active:
        # NOUVEAU : Badge Rage active même inconscient
        build_content = '<div style="font-size: 1rem; font-weight: bold; color: #FF0000; text-shadow: 2px 2px 4px black;">🔥💀 RAGE<br/>(IMMORTEL)</div>'
    elif not is_alive:
        build_content = '<div style="font-size: 1.1rem; font-weight: bold; color: #ff4444; text-shadow: 2px 2px 4px black;">💀 INCONSCIENT</div>'
    elif rage_active:
        # NOUVEAU : Badge Rage active
        build_content = '<div style="font-size: 1rem; font-weight: bold; color: #FF0000; text-shadow: 2px 2px 4px black;">🔥 RAGE ACTIVE</div>'
    elif wolf_form_active:
        # NOUVEAU : Badge Forme de loup avec compteur et indication x2 dégâts
        build_content = f'<div style="font-size: 1rem; font-weight: bold; color: #FF4500; text-shadow: 2px 2px 4px black;">🐺 LOUP ×2 ATK<br/>({wolf_remaining} rest.)</div>'
    elif pluie_active:
        # NOUVEAU : Badge Pluie de flèches (2 attaques par tour)
        build_content = '<div style="font-size: 1rem; font-weight: bold; color: #00CED1; text-shadow: 2px 2px 4px black;">🏹 PLUIE<br/>(2 ATK/tour)</div>'
    else:
        build_content = '&nbsp;'  # Espace invisible - pas de label par défaut

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

    # Préparer stats_content (2 stats par ligne pour meilleure lisibilité)
    magic_line = "<br/>        ✨ MAG" if enemy.is_magical else ""
    stats_content = f"""
    <div style="font-family: monospace; font-size: 0.85rem; margin-bottom: 5px; font-weight: bold; color: #f0f0f0; line-height: 1.5;">
        ❤️ {current_hp}/{max_hp} PV ⚔️ {damage} ATT<br/>
        🎯 {defense} HIT 🛡️ {parade_tokens} DEF{magic_line}
    </div>"""

    # Vérifier si l'ennemi est étourdi (RÉUTILISE fonction centralisée)
    is_stunned, stunned_turns = is_enemy_stunned(enemy)

    # NOUVEAU - Vérifier si l'ennemi est marqué par Kraor (Piège)
    is_marked_by_kraor = False
    if hasattr(enemy, 'status_effects') and enemy.status_effects:
        is_marked_by_kraor = 'kraor_marked' in enemy.status_effects

    # Préparer build_content (remplacé par status pour le combat)
    if is_current_turn:
        build_content = '<div style="font-size: 1.1rem; font-weight: bold; color: #FFD700; text-shadow: 2px 2px 4px black;">⚡ C\'EST SON TOUR</div>'
    elif not is_alive:
        build_content = '<div style="font-size: 1.1rem; font-weight: bold; color: #ff4444; text-shadow: 2px 2px 4px black;">💀 MORT</div>'
    elif is_stunned:
        # NOUVEAU : Badge visuel pour ennemi étourdi (cohérent avec mode manuel)
        build_content = f'<div style="font-size: 1.1rem; font-weight: bold; color: #9370DB; text-shadow: 2px 2px 4px black;">😵 Étourdi ({stunned_turns} tours)</div>'
    elif is_marked_by_kraor:
        # NOUVEAU : Badge visuel pour ennemi marqué par Kraor (Piège +2 dégâts groupe)
        build_content = '<div style="font-size: 1rem; font-weight: bold; color: #FF6347; text-shadow: 2px 2px 4px black;">🎯 MARQUÉ<br/>+2 dégâts groupe</div>'
    else:
        build_content = '&nbsp;'  # Espace invisible - pas de label par défaut

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

    # Construction du HTML colorisé (ordre chronologique normal)
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
        overflow-y: auto;
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

        # TOUJOURS créer 8 colonnes pour largeur constante (colonnes vides si moins de cartes)
        cols = st.columns(max_cards_per_row)

        # Afficher chaque carte dans les colonnes nécessaires
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

        # TOUJOURS créer 7 colonnes pour largeur constante (colonnes vides si moins de cartes)
        cols = st.columns(max_cards_per_row)

        # Afficher chaque carte dans les colonnes nécessaires
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

                # Vérifier si l'ennemi est étourdi (RÉUTILISE fonction centralisée)
                is_stunned, stunned_turns = is_enemy_stunned(character) if combatant_data['faction'] == 'enemy' else (False, 0)

                # Bouton "À son tour" si vivant et pas déjà en cours
                if character.is_alive() and not is_current:
                    # Désactiver si déjà joué OU étourdi
                    button_disabled = has_played or is_stunned
                    if is_stunned:
                        button_label = f"😵 Étourdi ({stunned_turns} tours)"
                    elif has_played:
                        button_label = "✅ A joué"
                    else:
                        button_label = "▶️ À son tour"

                    # Bouton simple avec use_container_width pour cohérence
                    button_key = f"select_{combatant_data['faction']}_{combatant_data['id']}"
                    if st.button(
                        button_label,
                        key=button_key,
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

                # NOUVEAU - Log invisibilité automatique (Lame P-7-6 Assaut furieux)
                if hasattr(char, 'status_effects') and 'invisible' in char.status_effects:
                    if char.status_effects['invisible'].get('source') == 'ombre_mortelle':
                        char_name = getattr(char, 'display_name', char.name)
                        st.session_state.sandbox_v2_log.append(f"🌑 {char_name} redevient invisible (Assaut furieux)")
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

    st.title("🎮 Playtest Manuel")

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

    # NOUVEAU : Avertissement si overrides actifs
    if st.session_state.get('enemy_overrides'):
        modified_count = len(st.session_state.enemy_overrides)
        st.warning(f"⚙️ {modified_count} ennemi(s) avec stats modifiées (recommandations d'équilibrage appliquées)")

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
                # FIX : Préparer nouveau combat (reset données précédentes sans vider les combattants)
                prepare_new_combat()

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
                # FIX : Préparer nouveau combat (reset données précédentes sans vider les combattants)
                prepare_new_combat()

                organize_teams_without_initiative()
                st.session_state.sandbox_v2_phase = 'COMBAT'
                st.rerun()

        return

    # === PHASES VICTORY / DEFEAT ===
    elif phase in ['VICTORY', 'DEFEAT']:
        # Utiliser le vrai tracker qui a collecté les stats pendant le combat
        tracker = st.session_state.get('sandbox_v2_stats_tracker')

        if tracker:
            # Analyser les stats collectées
            analysis = analyze_combat_results(tracker.get_stats())

            # Afficher récapitulatif compact et utile
            from ui.components.combat_summary_compact import display_compact_combat_summary
            display_compact_combat_summary(
                tracker.get_stats(),
                analysis,
                st.session_state.sandbox_v2_log
            )
        else:
            # Fallback si pas de tracker (ne devrait pas arriver)
            if phase == 'VICTORY':
                st.success("🏆 **VICTOIRE !**")
            else:
                st.error("💀 **DÉFAITE**")
            st.warning("⚠️ Statistiques de combat non disponibles")

            st.markdown("---")

            # Bouton pour nouveau combat
            if st.button("🔄 Nouveau Combat", type="primary", use_container_width=True):
                # FIX : Reset complet pour nouveau combat propre
                reset_combat_state()
                st.rerun()

        # Note : Le log sera affiché en bas (section commune)
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

        # Détection fin de combat
        if not alive_heroes:
            # IMPORTANT : Enregistrer le tour du combattant actuel avant de finaliser
            current = get_current_combatant()
            tracker = st.session_state.get('sandbox_v2_stats_tracker')
            if tracker and current:
                tracker.record_turn_end(current['id'], st.session_state.sandbox_v2_round_number)

            # Snapshot final des PV avant de finaliser
            if tracker:
                tracker.snapshot_hp(
                    turn_number=st.session_state.sandbox_v2_round_number,
                    combatants=st.session_state.sandbox_v2_combatants
                )

            # Finaliser le tracker
            if tracker:
                tracker.finalize_combat(
                    victory=False,
                    end_round=st.session_state.sandbox_v2_round_number,
                    heroes=[c['character'] for c in hero_combatants],
                    enemies=[c['character'] for c in enemy_combatants]
                )

            st.session_state.sandbox_v2_phase = 'DEFEAT'
            st.rerun()

        if not alive_enemies:
            # IMPORTANT : Enregistrer le tour du combattant actuel avant de finaliser
            current = get_current_combatant()
            tracker = st.session_state.get('sandbox_v2_stats_tracker')
            if tracker and current:
                tracker.record_turn_end(current['id'], st.session_state.sandbox_v2_round_number)

            # Snapshot final des PV avant de finaliser
            if tracker:
                tracker.snapshot_hp(
                    turn_number=st.session_state.sandbox_v2_round_number,
                    combatants=st.session_state.sandbox_v2_combatants
                )

            # Finaliser le tracker
            if tracker:
                tracker.finalize_combat(
                    victory=True,
                    end_round=st.session_state.sandbox_v2_round_number,
                    heroes=[c['character'] for c in hero_combatants],
                    enemies=[c['character'] for c in enemy_combatants]
                )

            st.session_state.sandbox_v2_phase = 'VICTORY'
            st.rerun()

        # Tour actuel
        current = get_current_combatant()
        if current:
            # VÉRIFICATION : Sauter si mort (sécurité - normalement géré par next_turn())
            if not current['character'].is_alive():
                st.session_state.sandbox_v2_log.append(f"⏭️ {current['character'].name} est inconscient, passage au tour suivant")
                next_turn()
                st.rerun()
                return

            # VÉRIFICATION : Sauter si ennemi étourdi (mode initiative)
            if current['faction'] == 'enemy' and initiative_enabled:
                # Vérifier si l'ennemi est étourdi SANS décrémenter (décrémentation au nouveau round)
                is_stunned, stunned_turns = is_enemy_stunned(current['character'])
                if is_stunned:
                    # Ennemi étourdi - sauter son tour (stun sera décrémenté au prochain round)
                    st.session_state.sandbox_v2_log.append(
                        f"😵 {current['character'].name} est étourdi ! Tour sauté ({stunned_turns} tour(s) restant(s))"
                    )
                    next_turn()
                    st.rerun()
                    return

            # Afficher interface seulement si vivant ET non-stunné
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
    if st.session_state.sandbox_v2_log and phase in ['COMBAT', 'VICTORY', 'DEFEAT']:
        # Expanded par défaut si combat terminé pour garder le log visible
        is_expanded = (phase in ['VICTORY', 'DEFEAT'])
        with st.expander("📜 Journal de Combat (Historique complet)", expanded=is_expanded):
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
                # NOUVEAU - Décrémenter les compteurs stunned de tous les ennemis
                for combatant in st.session_state.sandbox_v2_combatants:
                    char = combatant['character']
                    if combatant['faction'] == 'enemy' and hasattr(char, 'status_effects'):
                        if 'stunned' in char.status_effects:
                            stunned_data = char.status_effects['stunned']
                            # Gérer format dict ou int (legacy)
                            if isinstance(stunned_data, dict):
                                duration = stunned_data.get('duration', 0)
                                if duration > 0:
                                    stunned_data['duration'] = duration - 1
                                    if stunned_data['duration'] <= 0:
                                        del char.status_effects['stunned']
                                        st.session_state.sandbox_v2_log.append(f"✅ {char.name} n'est plus étourdi")
                            else:
                                # Legacy: stunned est un int
                                if stunned_data > 0:
                                    char.status_effects['stunned'] -= 1
                                    if char.status_effects['stunned'] <= 0:
                                        del char.status_effects['stunned']
                                        st.session_state.sandbox_v2_log.append(f"✅ {char.name} n'est plus étourdi")

                    # NOUVEAU : Décrémenter Aura sacrée (pour tous les personnages)
                    if combatant['faction'] == 'hero' and hasattr(char, 'temporary_buffs'):
                        if 'aura_protection' in char.temporary_buffs:
                            aura = char.temporary_buffs['aura_protection']
                            if 'rounds_remaining' in aura:
                                aura['rounds_remaining'] -= 1
                                if aura['rounds_remaining'] <= 0:
                                    del char.temporary_buffs['aura_protection']
                                    st.session_state.sandbox_v2_log.append(f"✨ Aura sacrée de {char.name} a expiré")

                        # NOUVEAU : Recharger Raishi Maîtrise absolue (au début de chaque round pour TOUS les héros)
                        if 'raishi_maitrise_charges' in char.temporary_buffs:
                            maitrise = char.temporary_buffs['raishi_maitrise_charges']
                            if isinstance(maitrise, dict) and maitrise.get('auto_recharge', False):
                                max_charges = maitrise.get('max_charges', 2)
                                old_charges = maitrise.get('charges', 0)
                                maitrise['charges'] = max_charges  # Recharge complète à chaque round
                                if old_charges < max_charges:
                                    st.session_state.sandbox_v2_log.append(f"🛡️✨ {char.name} - Maîtrise absolue rechargée ({max_charges} charges)")

                    # NOUVEAU : Décrémenter compteur furtivité de Lame au début du round (pour tous les héros)
                    if combatant['faction'] == 'hero' and hasattr(char, 'status_effects'):
                        if 'invisible' in char.status_effects:
                            stealth_data = char.status_effects['invisible']
                            # Vérifier si c'est la furtivité de Lame avec compteur de tours
                            if isinstance(stealth_data, dict) and stealth_data.get('source') == 'lame_furtivite':
                                if 'turns_remaining' in stealth_data:
                                    stealth_data['turns_remaining'] -= 1
                                    # Si compteur atteint 0, supprimer la furtivité
                                    if stealth_data['turns_remaining'] <= 0:
                                        del char.status_effects['invisible']
                                        st.session_state.sandbox_v2_log.append(f"🌑 {char.name} redevient visible (furtivité expirée)")

                # Réinitialiser la liste des joueurs
                st.session_state.sandbox_v2_played_this_round = []
                # Incrémenter le numéro de round
                st.session_state.sandbox_v2_round_number += 1
                # Réinitialiser l'index de tour
                st.session_state.sandbox_v2_current_turn_index = -1
                # Log
                st.session_state.sandbox_v2_log.append("")
                st.session_state.sandbox_v2_log.append(f"=== ROUND {st.session_state.sandbox_v2_round_number} ===")

                # NOUVEAU - Log effets persistants actifs (Aura sacrée, etc.)
                log_active_persistent_effects()

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
                # Utilise la fonction centralisée de reset
                reset_combat_state()
                st.rerun()

if __name__ == "__main__":
    main_sandbox_v2()
