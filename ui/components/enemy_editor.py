"""
Enemy Editor - Interface de gestion des ennemis personnalisés
VERSION 1.0 - Composant Streamlit

Responsabilités :
- Formulaire de création d'ennemis
- Formulaire d'édition d'ennemis
- Liste des ennemis personnalisés
- Gestion des actions (Créer/Éditer/Supprimer)
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
    st.title("⚔️ Gestion des Ennemis Personnalisés")
    st.markdown("---")

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
    Affiche le formulaire de création d'un nouvel ennemi

    Args:
        manager: Instance de EnemyManager
    """
    st.subheader("📝 Créer un nouvel ennemi")

    with st.form("enemy_creation_form", clear_on_submit=True):
        # Informations générales
        st.markdown("**Informations générales**")
        col1, col2 = st.columns([2, 1])

        with col1:
            name = st.text_input(
                "Nom de l'ennemi",
                placeholder="Ex: Golem de pierre",
                help="Nom descriptif de l'ennemi"
            )

        with col2:
            defense = st.number_input(
                "Defense (seuil)",
                min_value=0,
                max_value=20,
                value=10,
                help="Seuil de précision à dépasser pour toucher l'ennemi"
            )

        st.markdown("---")

        # Stats pour chaque nombre de joueurs
        stats_2j = _render_stats_inputs("2 joueurs", "2j")
        stats_3j = _render_stats_inputs("3 joueurs", "3j")
        stats_4j = _render_stats_inputs("4 joueurs", "4j")

        st.markdown("---")

        # Propriétés spéciales
        st.markdown("**Propriétés spéciales**")
        col1, col2 = st.columns(2)

        with col1:
            is_magical = st.checkbox(
                "Créature magique",
                help="Les créatures magiques réduisent les dégâts physiques de moitié"
            )

        with col2:
            has_magical_damage = st.checkbox(
                "Possède des dégâts magiques",
                help="Cet ennemi inflige des dégâts magiques (ignorent la parade)"
            )

        # Bouton de création
        submitted = st.form_submit_button("➕ Créer l'ennemi personnalisé", use_container_width=True)

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
                st.rerun()
            else:
                st.error(message)


def _display_edit_form(manager: EnemyManager):
    """
    Affiche le formulaire d'édition d'un ennemi existant

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
        # Informations générales
        st.markdown("**Informations générales**")
        col1, col2 = st.columns([2, 1])

        with col1:
            name = st.text_input(
                "Nom de l'ennemi",
                value=enemy.name,
                help="Nom descriptif de l'ennemi"
            )

        with col2:
            defense = st.number_input(
                "Defense (seuil)",
                min_value=0,
                max_value=20,
                value=enemy.defense,
                help="Seuil de précision à dépasser pour toucher l'ennemi"
            )

        st.markdown("---")

        # Stats pour chaque nombre de joueurs
        stats_2j = _render_stats_inputs(
            "2 joueurs", "2j",
            default_damage=enemy.stats_by_players[2]['damage'],
            default_health=enemy.stats_by_players[2]['health'],
            default_defense=enemy.stats_by_players[2]['defense']
        )
        stats_3j = _render_stats_inputs(
            "3 joueurs", "3j",
            default_damage=enemy.stats_by_players[3]['damage'],
            default_health=enemy.stats_by_players[3]['health'],
            default_defense=enemy.stats_by_players[3]['defense']
        )
        stats_4j = _render_stats_inputs(
            "4 joueurs", "4j",
            default_damage=enemy.stats_by_players[4]['damage'],
            default_health=enemy.stats_by_players[4]['health'],
            default_defense=enemy.stats_by_players[4]['defense']
        )

        st.markdown("---")

        # Propriétés spéciales
        st.markdown("**Propriétés spéciales**")
        col1, col2 = st.columns(2)

        with col1:
            is_magical = st.checkbox(
                "Créature magique",
                value=enemy.is_magical,
                help="Les créatures magiques réduisent les dégâts physiques de moitié"
            )

        with col2:
            has_magical_damage = st.checkbox(
                "Possède des dégâts magiques",
                value=enemy.has_magical_damage,
                help="Cet ennemi inflige des dégâts magiques (ignorent la parade)"
            )

        # Bouton de sauvegarde
        submitted = st.form_submit_button("💾 Sauvegarder les modifications", use_container_width=True)

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


def _render_stats_inputs(label: str, prefix: str,
                         default_damage: int = 2,
                         default_health: int = 10,
                         default_defense: int = 0) -> Dict[str, int]:
    """
    Widget réutilisable pour saisir les stats d'un ennemi

    Args:
        label: Label à afficher (ex: "2 joueurs")
        prefix: Préfixe pour les clés (ex: "2j")
        default_damage: Valeur par défaut des dégâts
        default_health: Valeur par défaut de la santé
        default_defense: Valeur par défaut de la parade

    Returns:
        Dict avec les valeurs saisies {'damage': int, 'health': int, 'defense': int}
    """
    st.markdown(f"**Stats pour {label}**")
    col1, col2, col3 = st.columns(3)

    with col1:
        damage = st.number_input(
            "Dégâts",
            min_value=0,
            max_value=20,
            value=default_damage,
            key=f"damage_{prefix}",
            help="Dégâts infligés aux héros"
        )

    with col2:
        health = st.number_input(
            "Santé",
            min_value=1,
            max_value=200,
            value=default_health,
            key=f"health_{prefix}",
            help="Points de vie de l'ennemi"
        )

    with col3:
        defense_stat = st.number_input(
            "Parade",
            min_value=0,
            max_value=10,
            value=default_defense,
            key=f"defense_{prefix}",
            help="Jetons de parade (bloquent les dégâts)"
        )

    return {
        'damage': damage,
        'health': health,
        'defense': defense_stat
    }
