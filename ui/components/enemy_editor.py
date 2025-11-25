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

    st.title("⚔️ Gestion des Ennemis Personnalisés")

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


def _display_creation_form(manager: EnemyManager):
    """
    Affiche le formulaire de création d'un nouvel ennemi (VERSION COMPACTE)

    Args:
        manager: Instance de EnemyManager
    """
    st.subheader("📝 Créer un nouvel ennemi")

    with st.form("enemy_creation_form", clear_on_submit=True):
        # Informations générales (sur une seule ligne)
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            name = st.text_input(
                "Nom de l'ennemi",
                placeholder="Ex: Golem de pierre",
                help="Nom descriptif de l'ennemi"
            )

        with col2:
            defense = st.number_input(
                "Defense",
                min_value=0,
                max_value=20,
                value=10,
                help="Seuil de précision à dépasser"
            )

        with col3:
            st.write("")  # Spacer pour aligner

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
        st.markdown("#### ⚡ Propriétés")
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

        # Bouton de création
        submitted = st.form_submit_button("➕ Créer l'ennemi", use_container_width=True, type="primary")

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
                'has_magical_damage': has_magical_damage
            }

            # Créer l'ennemi
            success, message, enemy = manager.create_enemy(data)

            if success:
                st.success(message)
                # NOUVEAU - Invalider le cache pour recharger les ennemis
                st.cache_data.clear()
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

    with st.form("enemy_edit_form"):
        # Informations générales (sur une seule ligne)
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            name = st.text_input(
                "Nom de l'ennemi",
                value=enemy.name,
                help="Nom descriptif de l'ennemi"
            )

        with col2:
            defense = st.number_input(
                "Defense",
                min_value=0,
                max_value=20,
                value=enemy.defense,
                help="Seuil de précision à dépasser"
            )

        with col3:
            st.write("")  # Spacer

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

        # Bouton de sauvegarde
        submitted = st.form_submit_button("💾 Sauvegarder", use_container_width=True, type="primary")

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
                'has_magical_damage': has_magical_damage
            }

            # Mettre à jour l'ennemi
            success, message = manager.update_enemy(enemy_code, data)

            if success:
                st.success(message)
                st.session_state.editing_enemy_code = None
                # NOUVEAU - Invalider le cache pour recharger les ennemis
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(message)


def _display_custom_enemies_list(manager: EnemyManager):
    """
    Affiche la liste des ennemis personnalisés avec actions

    Args:
        manager: Instance de EnemyManager
    """
    st.subheader("📋 Mes ennemis personnalisés")

    enemies = manager.load_custom_enemies()

    if not enemies:
        st.info("Aucun ennemi personnalisé créé. Utilisez le formulaire ci-dessus pour en créer un.")
        return

    # Afficher chaque ennemi
    for enemy in enemies:
        with st.container():
            st.markdown(f"### {enemy.code} - {enemy.name}")

            # Infos rapides
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**Defense:** {enemy.defense}")

            with col2:
                stats_2j = enemy.stats_by_players[2]
                st.write(f"**2J:** {stats_2j['damage']}dmg / {stats_2j['health']}hp / {stats_2j['defense']}def")

            with col3:
                stats_4j = enemy.stats_by_players[4]
                st.write(f"**4J:** {stats_4j['damage']}dmg / {stats_4j['health']}hp / {stats_4j['defense']}def")

            # Propriétés spéciales
            properties = []
            if enemy.is_magical:
                properties.append("🔵 Magique")
            if enemy.has_magical_damage:
                properties.append("⚡ Dégâts magiques")

            if properties:
                st.write(" | ".join(properties))

            # Boutons d'action
            col1, col2, col3, col4 = st.columns([1, 1, 1, 3])

            with col1:
                if st.button("✏️ Éditer", key=f"edit_{enemy.code}", use_container_width=True):
                    st.session_state.editing_enemy_code = enemy.code
                    st.rerun()

            with col2:
                if st.button("🗑️ Supprimer", key=f"delete_{enemy.code}", use_container_width=True):
                    # Confirmation avant suppression
                    st.session_state[f'confirm_delete_{enemy.code}'] = True

            with col3:
                if st.button("👁️ Voir détails", key=f"preview_{enemy.code}", use_container_width=True):
                    _display_enemy_preview(enemy)

            # Confirmation de suppression
            if st.session_state.get(f'confirm_delete_{enemy.code}', False):
                st.warning(f"⚠️ Confirmer la suppression de **{enemy.code} - {enemy.name}** ?")

                col_confirm, col_cancel = st.columns(2)

                with col_confirm:
                    if st.button("✅ Oui, supprimer", key=f"confirm_yes_{enemy.code}", use_container_width=True):
                        success, message = manager.delete_enemy(enemy.code)
                        if success:
                            st.success(message)
                            st.session_state.pop(f'confirm_delete_{enemy.code}', None)
                            # NOUVEAU - Invalider le cache pour recharger les ennemis
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(message)

                with col_cancel:
                    if st.button("❌ Annuler", key=f"confirm_no_{enemy.code}", use_container_width=True):
                        st.session_state.pop(f'confirm_delete_{enemy.code}', None)
                        st.rerun()

            st.markdown("---")


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
        "⚔️ Dmg",
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
        "🛡️ Par",
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
