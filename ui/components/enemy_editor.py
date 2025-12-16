"""
Enemy Editor - Interface de gestion des ennemis personnalisés
VERSION 2.0 - Formulaire compact + Couleurs adaptées au thème

Responsabilités :
- Formulaire de création d'ennemis (compact)
- Formulaire d'édition d'ennemis
- Liste des ennemis personnalisés
- Gestion des actions (Créer/Éditer/Supprimer)
- Invalidation du cache après modifications
"""

import streamlit as st
from typing import Dict, Optional
from models.enemy_manager import EnemyManager
from models.character import Enemy


def main_enemy_editor():
    """
    Point d'entrée principal de l'éditeur d'ennemis
    Affiche l'interface complète de gestion
    """
    # CSS personnalisé pour améliorer la lisibilité des inputs
    st.markdown("""
    <style>
    /* Inputs spécifiques à l'éditeur d'ennemis - Fond clair et texte très contrasté */
    [data-testid="stForm"] .stTextInput input,
    [data-testid="stForm"] .stNumberInput input {
        background-color: rgba(255, 255, 255, 0.25) !important;
        color: #1a1a1a !important;
        border: 2px solid #d4af37 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 0.5rem !important;
    }

    /* Placeholder plus visible */
    [data-testid="stForm"] .stTextInput input::placeholder {
        color: rgba(26, 26, 26, 0.5) !important;
        font-weight: 500 !important;
    }

    /* Focus state */
    [data-testid="stForm"] .stTextInput input:focus,
    [data-testid="stForm"] .stNumberInput input:focus {
        background-color: rgba(255, 255, 255, 0.35) !important;
        border-color: #ffd700 !important;
        box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.3) !important;
    }

    /* Labels plus visibles */
    [data-testid="stForm"] label {
        color: #3b2f1c !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* Checkboxes */
    [data-testid="stForm"] [data-testid="stCheckbox"] label {
        color: #3b2f1c !important;
        font-weight: 600 !important;
    }

    /* Style spécial pour les checkboxes de capacités (boutons toggle) */
    [data-testid="stCheckbox"][data-baseweb="checkbox"] {
        background: rgba(139, 69, 19, 0.1);
        border: 2px solid #d4af37;
        border-radius: 8px;
        padding: 8px;
        transition: all 0.2s ease;
    }

    [data-testid="stCheckbox"][data-baseweb="checkbox"]:hover {
        background: rgba(212, 175, 55, 0.2);
        border-color: #ffd700;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    /* Checkbox cochée (ON) */
    [data-testid="stCheckbox"] input:checked + div {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.3), rgba(255, 215, 0, 0.2)) !important;
    }

    /* Label des capacités plus gros */
    [data-testid="stCheckbox"] label p {
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        color: #8b6914 !important;
        margin: 0 !important;
    }

    /* Compact le formulaire */
    [data-testid="stForm"] > div {
        gap: 0.5rem !important;
    }

    /* Titres sections plus compacts */
    [data-testid="stForm"] h4 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Gestion des Ennemis Personnalisés")

    # Initialisation du gestionnaire
    manager = EnemyManager()

    # Initialisation du session state pour l'édition
    if 'editing_enemy_code' not in st.session_state:
        st.session_state.editing_enemy_code = None

    # Afficher formulaire (création ou édition)
    if st.session_state.editing_enemy_code:
        _display_edit_form(manager)
    else:
        _display_creation_form(manager)

    st.markdown("---")

    # Afficher liste des ennemis personnalisés
    _display_custom_enemies_list(manager)

    # Information sur les ennemis officiels
    st.info("ℹ️ Les ennemis officiels (E-1 à E-72) ne peuvent pas être modifiés. "
            "Seuls vos ennemis personnalisés (CE-X) peuvent être édités ou supprimés.")


def _display_enemy_abilities_selection(current_abilities: list = None) -> list:
    """
    Widget de sélection des capacités ennemies avec boutons ON/OFF

    Args:
        current_abilities: Liste des codes actuels (pour édition)

    Returns:
        Liste des codes sélectionnés (ex: ['EA-1', 'EA-3'])
    """
    from utils.data_loader import DataLoader

    loader = DataLoader()

    def translate_trigger(trigger: str) -> str:
        """Traduit un trigger technique en français naturel"""
        translations = {
            'on_combat_start': 'Au début du combat',
            'on_round_start': 'Au début du round',
            'on_turn_start': 'Au début du tour',
            'before_attack': 'Avant l\'attaque',
            'after_attack': 'Après l\'attaque',
            'on_receive_damage': 'Quand reçoit des dégâts'
        }
        return translations.get(trigger, trigger)

    def translate_effect(effect: str) -> str:
        """Traduit un effet technique en français naturel"""
        translations = {
            'immunity_stun': 'Immunité au Stun',
            'block_hero_abilities': 'Bloque les capacités des héros',
            'extra_attacks': 'Attaques supplémentaires',
            'stun_hero_permanent': 'Stun permanent',
            'stun_hero_temporary': 'Stun temporaire',
            'alternating_effects': 'Effets alternés',
            'damage_all_heroes': 'Dégâts à tous les héros',
            'periodic_stun': 'Stun périodique',
            'periodic_damage': 'Dégâts périodiques',
            'ability_check_stun': 'Test de capacité (Stun)',
            'player_scaled_damage': 'Dégâts selon nombre de joueurs'
        }
        return translations.get(effect, effect)

    try:
        # Charger toutes les capacités disponibles
        all_abilities = loader._load_enemy_abilities()

        if not all_abilities:
            st.warning("⚠️ Aucune capacité ennemi disponible")
            return []

        # Trier les capacités par code (EA-1, EA-2, ...)
        sorted_codes = sorted(all_abilities.keys())

        # Exclure EA-12 (non implémenté)
        sorted_codes = [code for code in sorted_codes if code != 'EA-12']

        selected = []

        # Afficher les boutons toggle en grille (6 par ligne)
        num_cols = 6
        num_abilities = len(sorted_codes)
        num_rows = (num_abilities + num_cols - 1) // num_cols

        for row_idx in range(num_rows):
            cols = st.columns(num_cols)

            for col_idx in range(num_cols):
                ability_idx = row_idx * num_cols + col_idx

                if ability_idx >= num_abilities:
                    break

                code = sorted_codes[ability_idx]
                ability = all_abilities[code]

                with cols[col_idx]:
                    # Traduire triggers et effets en français
                    triggers_fr = [translate_trigger(t) for t in ability.triggers]
                    effects_fr = [translate_effect(e) for e in ability.effects]

                    # Checkbox avec nom de la capacité et tooltip avec description complète traduite
                    is_selected = st.checkbox(
                        f"{ability.name}",
                        value=code in (current_abilities or []),
                        key=f"ability_{code}",
                        help=f"**{code} - {ability.name}**\n\n{ability.description}\n\n**Déclenchement :** {', '.join(triggers_fr)}\n**Effet :** {', '.join(effects_fr)}"
                    )

                    if is_selected:
                        selected.append(code)

        # Afficher résumé des capacités sélectionnées avec noms
        if selected:
            selected_names = [all_abilities[code].name for code in selected]
            st.info(f"✅ {len(selected)} capacité(s) sélectionnée(s) : {', '.join(selected_names)}")

        return selected

    except Exception as e:
        st.error(f"❌ Erreur chargement capacités: {e}")
        return []


def _display_creation_form(manager: EnemyManager):
    """
    Affiche le formulaire de création d'un nouvel ennemi (VERSION COMPACTE)

    Args:
        manager: Instance de EnemyManager
    """
    st.subheader("📝 Créer un nouvel ennemi")

    with st.form("enemy_creation_form", clear_on_submit=True):
        # Nom de l'ennemi (ligne 1 - toute la largeur)
        name = st.text_input(
            "Nom de l'ennemi",
            placeholder="Ex: Golem de pierre",
            help="Nom descriptif de l'ennemi"
        )

        # Defense séparée (propriété commune)
        st.markdown("#### 🎯 Propriété commune")
        col_def, col_spacer = st.columns([1, 3])
        with col_def:
            defense = st.number_input(
                "Defense (seuil de précision)",
                min_value=0,
                max_value=20,
                value=10,
                key="defense_main",
                help="Seuil de précision à dépasser pour toucher l'ennemi (commun à tous les nombres de joueurs)"
            )

        # Stats groupées en un seul bloc compact
        st.markdown("#### 📊 Stats par nombre de joueurs")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**2 Joueurs**")
            stats_2j = _render_stats_compact("2j")

        with col2:
            st.markdown("**3 Joueurs**")
            stats_3j = _render_stats_compact("3j")

        with col3:
            st.markdown("**4 Joueurs**")
            stats_4j = _render_stats_compact("4j")

        # Propriétés spéciales (alignées sous colonne 2 Joueurs)
        st.markdown("#### ⚡ Propriétés magiques")
        col1, col2, col3 = st.columns(3)

        with col1:
            is_magical = st.checkbox(
                "🔵 Créature magique",
                help="Réduit les dégâts physiques de moitié"
            )
            has_magical_damage = st.checkbox(
                "⚡ Dégâts magiques",
                help="Ignore la parade des héros"
            )

        with col2:
            st.write("")  # Spacer

        with col3:
            st.write("")  # Spacer

        # Section capacités spéciales
        st.markdown("#### ⚡ Capacités spéciales")
        selected_abilities = _display_enemy_abilities_selection(current_abilities=[])

        # Bouton de création (centré)
        col_spacer1, col_button, col_spacer2 = st.columns([1, 1, 1])
        with col_button:
            submitted = st.form_submit_button("➕ Créer l'ennemi", type="primary", use_container_width=True)

        if submitted:
            # Préparer les données
            data = {
                'name': name,
                'defense': defense,
                'damage_2j': stats_2j['damage'],
                'health_2j': stats_2j['health'],
                'defense_2j': stats_2j['defense'],
                'damage_3j': stats_3j['damage'],
                'health_3j': stats_3j['health'],
                'defense_3j': stats_3j['defense'],
                'damage_4j': stats_4j['damage'],
                'health_4j': stats_4j['health'],
                'defense_4j': stats_4j['defense'],
                'is_magical': is_magical,
                'has_magical_damage': has_magical_damage,
                'abilities': selected_abilities  # Liste des codes de capacités
            }

            # Créer l'ennemi
            success, message, enemy = manager.create_enemy(data)

            if success:
                st.success(message)
                # NOUVEAU - Recharger les ennemis dans session_state (sans cache clear)
                from utils.data_loader import DataLoader
                loader = DataLoader()
                st.session_state.all_enemies = loader.load_all_enemies()
                st.rerun()
            else:
                st.error(message)


def _display_edit_form(manager: EnemyManager):
    """
    Affiche le formulaire d'édition d'un ennemi existant (VERSION COMPACTE)

    Args:
        manager: Instance de EnemyManager
    """
    enemy_code = st.session_state.editing_enemy_code
    enemy = manager.get_enemy_by_code(enemy_code)

    if not enemy:
        st.error(f"❌ Ennemi {enemy_code} non trouvé")
        st.session_state.editing_enemy_code = None
        st.rerun()
        return

    st.subheader(f"✏️ Éditer {enemy_code} - {enemy.name}")

    # Bouton Annuler
    if st.button("❌ Annuler l'édition", use_container_width=True):
        st.session_state.editing_enemy_code = None
        st.rerun()

    # Extraire les codes de capacités actuelles
    current_ability_codes = []
    if hasattr(enemy, 'abilities') and enemy.abilities:
        current_ability_codes = [ability.code for ability in enemy.abilities]
    elif hasattr(enemy, 'ability_codes') and enemy.ability_codes:
        current_ability_codes = enemy.ability_codes

    with st.form("enemy_edit_form"):
        # Nom de l'ennemi (ligne 1 - toute la largeur)
        name = st.text_input(
            "Nom de l'ennemi",
            value=enemy.name,
            help="Nom descriptif de l'ennemi"
        )

        # Defense séparée (propriété commune)
        st.markdown("#### 🎯 Propriété commune")
        col_def, col_spacer = st.columns([1, 3])
        with col_def:
            defense = st.number_input(
                "Defense (seuil de précision)",
                min_value=0,
                max_value=20,
                value=enemy.defense,
                key="defense_edit",
                help="Seuil de précision à dépasser pour toucher l'ennemi (commun à tous les nombres de joueurs)"
            )

        # Stats groupées en un seul bloc compact
        st.markdown("#### 📊 Stats par nombre de joueurs")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**2 Joueurs**")
            stats_2j = _render_stats_compact(
                "2j",
                default_damage=enemy.stats_by_players[2]['damage'],
                default_health=enemy.stats_by_players[2]['health'],
                default_defense=enemy.stats_by_players[2]['defense']
            )

        with col2:
            st.markdown("**3 Joueurs**")
            stats_3j = _render_stats_compact(
                "3j",
                default_damage=enemy.stats_by_players[3]['damage'],
                default_health=enemy.stats_by_players[3]['health'],
                default_defense=enemy.stats_by_players[3]['defense']
            )

        with col3:
            st.markdown("**4 Joueurs**")
            stats_4j = _render_stats_compact(
                "4j",
                default_damage=enemy.stats_by_players[4]['damage'],
                default_health=enemy.stats_by_players[4]['health'],
                default_defense=enemy.stats_by_players[4]['defense']
            )

        # Propriétés spéciales (alignées sous colonne 2 Joueurs)
        st.markdown("#### ⚡ Propriétés")
        col1, col2, col3 = st.columns(3)

        with col1:
            is_magical = st.checkbox(
                "🔵 Créature magique",
                value=enemy.is_magical,
                help="Réduit les dégâts physiques de moitié"
            )
            has_magical_damage = st.checkbox(
                "⚡ Dégâts magiques",
                value=enemy.has_magical_damage,
                help="Ignore la parade des héros"
            )

        with col2:
            st.write("")  # Spacer

        with col3:
            st.write("")  # Spacer

        # Section capacités spéciales
        st.markdown("#### ⚡ Capacités spéciales")
        selected_abilities = _display_enemy_abilities_selection(current_abilities=current_ability_codes)

        # Bouton de sauvegarde (centré)
        col_spacer1, col_button, col_spacer2 = st.columns([1, 1, 1])
        with col_button:
            submitted = st.form_submit_button("💾 Sauvegarder", type="primary", use_container_width=True)

        if submitted:
            # Préparer les données
            data = {
                'name': name,
                'defense': defense,
                'damage_2j': stats_2j['damage'],
                'health_2j': stats_2j['health'],
                'defense_2j': stats_2j['defense'],
                'damage_3j': stats_3j['damage'],
                'health_3j': stats_3j['health'],
                'defense_3j': stats_3j['defense'],
                'damage_4j': stats_4j['damage'],
                'health_4j': stats_4j['health'],
                'defense_4j': stats_4j['defense'],
                'is_magical': is_magical,
                'has_magical_damage': has_magical_damage,
                'abilities': selected_abilities  # Liste des codes de capacités
            }

            # Mettre à jour l'ennemi
            success, message = manager.update_enemy(enemy_code, data)

            if success:
                st.success(message)
                st.session_state.editing_enemy_code = None
                # NOUVEAU - Recharger les ennemis dans session_state (sans cache clear)
                from utils.data_loader import DataLoader
                loader = DataLoader()
                st.session_state.all_enemies = loader.load_all_enemies()
                st.rerun()
            else:
                st.error(message)


def _display_custom_enemies_list(manager: EnemyManager):
    """
    Affiche la liste des ennemis personnalisés en grille compacte (VERSION 2.0)

    Args:
        manager: Instance de EnemyManager
    """
    st.subheader("📋 Ennemis personnalisés")

    enemies = manager.load_custom_enemies()

    if not enemies:
        st.info("Aucun ennemi personnalisé créé. Utilisez le formulaire ci-dessus pour en créer un.")
        return

    # Trier les ennemis par code (CE-1, CE-2, CE-3...)
    enemies.sort(key=lambda e: int(e.code.split('-')[1]) if e.code.startswith('CE-') else 0)

    # Barre de recherche compacte
    col_search, col_info = st.columns([1, 2])
    with col_search:
        search = st.text_input(
            "Recherche",
            placeholder="Ex: 5, Dragon...",
            label_visibility="collapsed",
            key="custom_enemy_search"
        )
    with col_info:
        if search.strip():
            st.success(f"🎯 Recherche active ({len(enemies)} total)")
        else:
            st.info(f"💡 {len(enemies)} ennemi(s) personnalisé(s)")

    # Filtrage par recherche
    if search.strip():
        term = search.lower()
        enemies = [e for e in enemies if term in e.code.split('-')[-1].lower() or term in e.name.lower()]

    # Message si aucun résultat après filtrage
    if not enemies and search.strip():
        st.warning(f"Aucun ennemi trouvé pour '{search}'. Essayez un autre terme de recherche.")
        return

    # Affichage en grille compacte - 6 cartes par ligne
    num_cols = 6
    num_enemies = len(enemies)
    num_rows = (num_enemies + num_cols - 1) // num_cols

    for row_idx in range(num_rows):
        cols = st.columns(num_cols)

        for col_idx in range(num_cols):
            enemy_idx = row_idx * num_cols + col_idx

            if enemy_idx >= num_enemies:
                break

            enemy = enemies[enemy_idx]

            with cols[col_idx]:
                # Carte compacte avec fond coloré
                stats_2j = enemy.stats_by_players[2]
                stats_3j = enemy.stats_by_players[3]
                stats_4j = enemy.stats_by_players[4]

                # Propriétés pour badge
                badges = []
                if enemy.is_magical:
                    badges.append("🔵")
                if enemy.has_magical_damage:
                    badges.append("⚡")
                badges_str = " ".join(badges) if badges else ""

                # Compter les capacités et créer tooltip avec noms uniquement
                ability_count = 0
                ability_details = ""
                if hasattr(enemy, 'abilities') and enemy.abilities:
                    ability_count = len(enemy.abilities)
                    # Tooltip avec noms uniquement (sans codes)
                    ability_details = ", ".join([a.name for a in enemy.abilities])
                elif hasattr(enemy, 'ability_codes') and enemy.ability_codes:
                    ability_count = len(enemy.ability_codes)
                    # Si on a juste les codes, les afficher (fallback)
                    ability_details = ", ".join(enemy.ability_codes)

                # Badge capacités avec tooltip
                abilities_badge = ""
                if ability_count > 0:
                    abilities_badge = f'<span title="{ability_details}" style="background: rgba(212,175,55,0.3); padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; margin-left: 4px; cursor: help;">⚡{ability_count}</span>'

                # Carte HTML compacte
                card_html = f"""
                <div style="border: 2px solid #d4af37; border-radius: 10px; padding: 12px;
                            background: linear-gradient(135deg, rgba(139, 69, 19, 0.1), rgba(210, 180, 140, 0.1));
                            margin-bottom: 10px; min-height: 200px; text-align: center;">
                    <div style="font-weight: bold; font-size: 0.85rem; color: #8b6914; margin-bottom: 3px;">
                        {enemy.code} {badges_str} {abilities_badge}
                    </div>
                    <div style="font-size: 1.1rem; color: #d4af37; margin-bottom: 10px; font-weight: 700;
                                text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.5);">
                        {enemy.name}
                    </div>
                    <div style="font-size: 0.9rem; color: #5a4a2a; line-height: 1.5;">
                        <strong>Def:</strong> {enemy.defense}<br/>
                        <strong>2J:</strong> {stats_2j['damage']}d/{stats_2j['health']}h/{stats_2j['defense']}p<br/>
                        <strong>3J:</strong> {stats_3j['damage']}d/{stats_3j['health']}h/{stats_3j['defense']}p<br/>
                        <strong>4J:</strong> {stats_4j['damage']}d/{stats_4j['health']}h/{stats_4j['defense']}p
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

                # Boutons d'action compacts (2 colonnes)
                col_action1, col_action2 = st.columns(2)

                with col_action1:
                    if st.button("✏️", key=f"edit_{enemy.code}", use_container_width=True, help="Éditer"):
                        st.session_state.editing_enemy_code = enemy.code
                        st.rerun()

                with col_action2:
                    if st.button("🗑️", key=f"delete_{enemy.code}", use_container_width=True, help="Supprimer"):
                        st.session_state[f'confirm_delete_{enemy.code}'] = True
                        st.rerun()

                # Confirmation de suppression (pleine largeur sous les boutons)
                if st.session_state.get(f'confirm_delete_{enemy.code}', False):
                    st.warning("⚠️ Confirmer ?", icon="⚠️")

                    col_confirm, col_cancel = st.columns(2)

                    with col_confirm:
                        if st.button("✅", key=f"confirm_yes_{enemy.code}", use_container_width=True, help="Oui"):
                            success, message = manager.delete_enemy(enemy.code)
                            if success:
                                st.success(message)
                                st.session_state.pop(f'confirm_delete_{enemy.code}', None)
                                from utils.data_loader import DataLoader
                                loader = DataLoader()
                                st.session_state.all_enemies = loader.load_all_enemies()
                                st.rerun()
                            else:
                                st.error(message)

                    with col_cancel:
                        if st.button("❌", key=f"confirm_no_{enemy.code}", use_container_width=True, help="Non"):
                            st.session_state.pop(f'confirm_delete_{enemy.code}', None)
                            st.rerun()


def _display_enemy_preview(enemy: Enemy):
    """
    Affiche une prévisualisation détaillée d'un ennemi

    Args:
        enemy: Instance de Enemy à prévisualiser
    """
    with st.expander(f"📊 Détails de {enemy.code} - {enemy.name}", expanded=True):
        st.markdown(f"**Code:** {enemy.code}")
        st.markdown(f"**Nom:** {enemy.name}")
        st.markdown(f"**Defense (seuil):** {enemy.defense}")

        st.markdown("---")

        # Stats par nombre de joueurs
        st.markdown("**Stats par nombre de joueurs**")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**2 Joueurs**")
            stats = enemy.stats_by_players[2]
            st.write(f"Dégâts: {stats['damage']}")
            st.write(f"Santé: {stats['health']}")
            st.write(f"Parade: {stats['defense']}")

        with col2:
            st.markdown("**3 Joueurs**")
            stats = enemy.stats_by_players[3]
            st.write(f"Dégâts: {stats['damage']}")
            st.write(f"Santé: {stats['health']}")
            st.write(f"Parade: {stats['defense']}")

        with col3:
            st.markdown("**4 Joueurs**")
            stats = enemy.stats_by_players[4]
            st.write(f"Dégâts: {stats['damage']}")
            st.write(f"Santé: {stats['health']}")
            st.write(f"Parade: {stats['defense']}")

        st.markdown("---")

        # Propriétés spéciales
        st.markdown("**Propriétés spéciales**")
        if enemy.is_magical:
            st.success("🔵 Créature magique - Réduit les dégâts physiques de moitié")
        else:
            st.info("Créature normale - Sensible aux dégâts physiques")

        if enemy.has_magical_damage:
            st.warning("⚡ Possède des dégâts magiques - Ignore la parade des héros")
        else:
            st.info("Dégâts physiques - Bloqués par la parade")


def _render_stats_compact(prefix: str,
                          default_damage: int = 2,
                          default_health: int = 10,
                          default_defense: int = 0) -> Dict[str, int]:
    """
    Widget compact pour saisir les stats d'un ennemi (VERSION COMPACTE)

    Args:
        prefix: Préfixe pour les clés (ex: "2j")
        default_damage: Valeur par défaut des dégâts
        default_health: Valeur par défaut de la santé
        default_defense: Valeur par défaut de la parade

    Returns:
        Dict avec les valeurs saisies {'damage': int, 'health': int, 'defense': int}
    """
    damage = st.number_input(
        "⚔️ Damage",
        min_value=0,
        max_value=20,
        value=default_damage,
        key=f"damage_{prefix}",
        label_visibility="visible"
    )

    health = st.number_input(
        "❤️ HP",
        min_value=1,
        max_value=200,
        value=default_health,
        key=f"health_{prefix}",
        label_visibility="visible"
    )

    defense_stat = st.number_input(
        "🛡️ Parade",
        min_value=0,
        max_value=10,
        value=default_defense,
        key=f"defense_{prefix}",
        label_visibility="visible"
    )

    return {
        'damage': damage,
        'health': health,
        'defense': defense_stat
    }
