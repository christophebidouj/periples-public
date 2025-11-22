"""
Affichage des résultats de combat, statistiques et recommandations
"""

from typing import Dict, List
import streamlit as st
from models.character import Character, Enemy


def display_combat_results_panel(stats: Dict, analysis: Dict,
                                 recommendations: List[Dict],
                                 heroes: List[Character],
                                 enemies: List[Enemy]):
    """Affiche le panneau complet de résultats de combat"""

    victory = analysis['victory']
    duration = analysis['duration_rounds']
    balance_score = analysis['balance_score']

    # === BANNIÈRE RÉSULTAT ===
    if victory:
        st.success(f"🏆 **VICTOIRE DES HÉROS** - Combat terminé au tour {duration}")
    else:
        st.error(f"💀 **DÉFAITE DES HÉROS** - Combat terminé au tour {duration}")

    st.markdown("---")

    # === RÉSUMÉ COMBAT (Expander collapsé) ===
    with st.expander("📊 Résumé du Combat", expanded=False):
        display_combat_summary(analysis, balance_score)

    # === DÉTAILS HÉROS (Expanders collapsés) ===
    if stats['heroes']:
        st.markdown("### 🦸 Détails Héros")
        for hero_code, hero_stats in stats['heroes'].items():
            display_hero_details_expander(hero_stats)

    # === DÉTAILS ENNEMIS (Expanders collapsés) ===
    if stats['enemies']:
        st.markdown("### 👹 Détails Ennemis")
        for enemy_code, enemy_stats in stats['enemies'].items():
            display_enemy_details_expander(enemy_stats)

    # === MÉTRIQUES D'ÉQUILIBRAGE (Expander collapsé) ===
    with st.expander("⚖️ Métriques d'Équilibrage", expanded=False):
        display_balance_metrics(analysis)

    st.markdown("---")

    # === RECOMMANDATIONS D'ÉQUILIBRAGE (Toujours visibles) ===
    if recommendations:
        display_balance_recommendations(recommendations, enemies, balance_score)


def display_combat_summary(analysis: Dict, balance_score: float):
    """Affiche le résumé global du combat"""

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("⏱️ Durée", f"{analysis['duration_rounds']} tours")
        st.metric("🦸 Héros survivants",
                 f"{analysis['heroes']['surviving']}/{analysis['heroes']['total']}")

    with col2:
        st.metric("❤️ PV finaux moyens",
                 f"{analysis['heroes']['avg_hp_percent']:.0f}%")
        st.metric("✨ Sorts utilisés",
                 f"{analysis['heroes']['spells_usage_percent']:.0f}%")

    with col3:
        st.metric("👹 Ennemis éliminés",
                 f"{analysis['enemies']['eliminated']}/{analysis['enemies']['total']}")

        # Score avec couleur
        if balance_score >= 7:
            score_color = "🟢"
        elif balance_score >= 5:
            score_color = "🟡"
        else:
            score_color = "🔴"

        st.metric("⚖️ Score équilibrage",
                 f"{score_color} {balance_score:.1f}/10")

    # Potions
    small = analysis['heroes']['small_potions_used']
    large = analysis['heroes']['large_potions_used']
    if small > 0 or large > 0:
        st.info(f"🧪 Potions utilisées : {small} petites, {large} grandes")


def display_hero_details_expander(hero_stats: Dict):
    """Affiche les détails d'un héros dans un expander"""

    name = hero_stats['name']
    survived = hero_stats['survived']
    final_hp = hero_stats['final_health']
    max_hp = hero_stats['max_health']

    if survived:
        header = f"✅ {name} - {final_hp}/{max_hp} PV restants"
    else:
        death_turn = hero_stats['death_turn']
        header = f"💀 {name} - Inconscient au tour {death_turn}"

    with st.expander(header, expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Offensive**")
            st.write(f"⚔️ Dégâts infligés : {hero_stats['damage_dealt']}")
            st.write(f"🎯 Attaques : {hero_stats['attacks_hit']}/{hero_stats['attacks_made']}")
            if hero_stats['attacks_made'] > 0:
                hit_rate = (hero_stats['attacks_hit'] / hero_stats['attacks_made'] * 100)
                st.write(f"   Taux réussite : {hit_rate:.0f}%")
            st.write(f"💥 Critiques : {hero_stats['criticals']}")
            st.write(f"❌ Échecs crit. : {hero_stats['critical_fails']}")

        with col2:
            st.markdown("**Défensive**")
            st.write(f"💔 Dégâts subis : {hero_stats['damage_taken']}")
            st.write(f"🛡️ Parades utilisées : {hero_stats['parade_tokens_used']}")

            st.markdown("**Ressources**")
            st.write(f"✨ Sorts dépensés : {hero_stats['spells_spent']}/{hero_stats['initial_spells']}")
            st.write(f"💚 Soins reçus : {hero_stats['healing_received']} PV")

        # Capacités utilisées
        if hero_stats['abilities_used']:
            st.markdown("**Capacités**")
            abilities_text = ", ".join(hero_stats['abilities_used'])
            st.write(f"🔮 {abilities_text}")

        # Potions
        small = hero_stats['potions_used']['small']
        large = hero_stats['potions_used']['large']
        if small > 0 or large > 0:
            st.write(f"🧪 Potions : {small} petites, {large} grandes")


def display_enemy_details_expander(enemy_stats: Dict):
    """Affiche les détails d'un ennemi dans un expander"""

    name = enemy_stats['name']
    survived = enemy_stats['survived']
    final_hp = enemy_stats['final_health']
    max_hp = enemy_stats['max_health']

    if survived:
        header = f"✅ {name} - Survivant ({final_hp}/{max_hp} PV)"
    else:
        death_turn = enemy_stats['death_turn']
        header = f"💀 {name} - Éliminé au tour {death_turn}"

    with st.expander(header, expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"⚔️ Dégâts infligés : {enemy_stats['damage_dealt']}")
            st.write(f"🎯 Attaques effectuées : {enemy_stats['attacks_made']}")

        with col2:
            st.write(f"💔 Dégâts subis : {enemy_stats['damage_taken']}")
            if not survived:
                st.write(f"⏱️ Éliminé au tour : {enemy_stats['death_turn']}")


def display_balance_metrics(analysis: Dict):
    """Affiche les métriques avancées d'équilibrage"""

    st.markdown("**Ratios d'efficacité**")

    hero_dmg = analysis['heroes']['total_damage_dealt']
    enemy_dmg = analysis['enemies']['total_damage_dealt']

    if enemy_dmg > 0:
        ratio = hero_dmg / enemy_dmg
        st.write(f"📊 Ratio dégâts héros/ennemis : {ratio:.2f}")

    spells_spent = analysis['heroes']['total_spells_spent']
    if spells_spent > 0 and hero_dmg > 0:
        efficiency = hero_dmg / spells_spent
        st.write(f"✨ Efficacité magique : {efficiency:.1f} dégâts/sort")

    # Indicateurs de difficulté
    st.markdown("**Indicateurs de difficulté**")

    survival_rate = analysis['heroes']['survival_rate']
    avg_hp = analysis['heroes']['avg_hp_percent']

    if avg_hp < 30:
        st.warning(f"⚠️ Combat intense : PV moyens finaux à {avg_hp:.0f}%")
    if survival_rate < 70:
        st.warning(f"⚠️ Pertes importantes : {survival_rate:.0f}% de survie")


def display_balance_recommendations(recommendations: List[Dict],
                                   enemies: List[Enemy],
                                   balance_score: float):
    """Affiche les recommandations d'équilibrage avec boutons Appliquer"""

    st.markdown("## ⚖️ Recommandations d'Équilibrage")

    # Analyse du score
    if balance_score >= 8:
        st.success("✅ Combat bien équilibré ! Ajustements optionnels ci-dessous.")
    elif balance_score >= 6:
        st.info("🔵 Combat acceptable. Suggestions d'amélioration :")
    elif balance_score >= 4:
        st.warning("🟡 Combat déséquilibré. Ajustements recommandés :")
    else:
        st.error("🔴 Combat très déséquilibré. Ajustements fortement recommandés :")

    st.markdown("---")

    # Afficher chaque recommandation
    for idx, rec in enumerate(recommendations, 1):
        display_recommendation_card(rec, idx, enemies)


def display_recommendation_card(rec: Dict, idx: int, enemies: List[Enemy]):
    """Affiche une carte de recommandation avec bouton Appliquer"""

    st.markdown(f"### 💡 Option {idx}")

    if rec['type'] == 'adjust_stats':
        display_adjust_stats_recommendation(rec, idx, enemies)
    elif rec['type'] == 'remove_enemy':
        display_remove_enemy_recommendation(rec, idx)
    elif rec['type'] == 'add_enemy':
        display_add_enemy_recommendation(rec, idx)


def display_adjust_stats_recommendation(rec: Dict, idx: int, enemies: List[Enemy]):
    """Affiche une recommandation d'ajustement de stats"""

    direction = "Augmenter" if rec['direction'] == 'increase' else "Réduire"
    st.markdown(f"**{direction} la résistance des ennemis**")

    st.info(f"📝 {rec['reason']}")

    # Détails des ajustements
    st.markdown("**Ajustements proposés :**")

    for adj in rec['adjustments']:
        hp_change = adj['hp_new'] - adj['hp_old']
        dmg_change = adj['damage_new'] - adj['damage_old']

        hp_arrow = "→" if hp_change >= 0 else "→"
        dmg_arrow = "→" if dmg_change >= 0 else "→"

        st.write(f"👹 **{adj['enemy_name']}**")
        st.write(f"   PV : {adj['hp_old']} {hp_arrow} {adj['hp_new']} ({hp_change:+d})")
        st.write(f"   Dégâts : {adj['damage_old']} {dmg_arrow} {adj['damage_new']} ({dmg_change:+d})")

    # Prédiction
    st.markdown("**🎲 Combat attendu :**")
    st.write(f"⏱️ Durée estimée : ~{rec['estimated_duration']} tours")
    st.write(f"❤️ PV finaux moyens : ~{rec['estimated_hp']:.0f}%")

    # Bouton Appliquer
    if st.button(f"✅ Appliquer Option {idx}", key=f"apply_rec_{idx}", type="primary"):
        apply_stat_adjustments(rec['adjustments'])
        st.success(f"✅ Option {idx} appliquée ! Relancez un combat pour tester.")
        st.rerun()


def display_remove_enemy_recommendation(rec: Dict, idx: int):
    """Affiche une recommandation de retrait d'ennemi"""

    st.markdown(f"**Retirer un ennemi**")

    st.info(f"📝 {rec['reason']}")

    st.write(f"➖ **{rec['enemy_name']}**")
    st.write(f"   PV : {rec['enemy_hp']}")
    st.write(f"   Dégâts : {rec['enemy_damage']}")

    # Prédiction
    st.markdown("**🎲 Combat attendu :**")
    st.write(f"⏱️ Durée estimée : ~{rec['estimated_duration']} tours")
    st.write(f"❤️ PV finaux moyens : ~{rec['estimated_hp']:.0f}%")

    # Bouton Appliquer
    if st.button(f"✅ Appliquer Option {idx}", key=f"apply_rec_{idx}", type="primary"):
        apply_enemy_removal(rec['enemy_code'])
        st.success(f"✅ Option {idx} appliquée ! {rec['enemy_name']} retiré de la sélection.")
        st.rerun()


def display_add_enemy_recommendation(rec: Dict, idx: int):
    """Affiche une recommandation d'ajout d'ennemi"""

    st.markdown(f"**Ajouter un ennemi**")

    st.info(f"📝 {rec['reason']}")

    st.write(f"➕ **{rec['enemy_name']}**")
    st.write(f"   PV : {rec['enemy_hp']}")
    st.write(f"   Dégâts : {rec['enemy_damage']}")

    # Prédiction
    st.markdown("**🎲 Combat attendu :**")
    st.write(f"⏱️ Durée estimée : ~{rec['estimated_duration']} tours")
    st.write(f"❤️ PV finaux moyens : ~{rec['estimated_hp']:.0f}%")

    # Bouton Appliquer
    if st.button(f"✅ Appliquer Option {idx}", key=f"apply_rec_{idx}", type="primary"):
        apply_enemy_addition(rec['enemy_code'])
        st.success(f"✅ Option {idx} appliquée ! {rec['enemy_name']} ajouté à la sélection.")
        st.rerun()


def apply_stat_adjustments(adjustments: List[Dict]):
    """Applique les ajustements de stats aux ennemis (sauvegarde dans session_state)"""

    if 'enemy_overrides' not in st.session_state:
        st.session_state.enemy_overrides = {}

    for adj in adjustments:
        enemy_code = adj['enemy_code']

        if enemy_code not in st.session_state.enemy_overrides:
            st.session_state.enemy_overrides[enemy_code] = {}

        st.session_state.enemy_overrides[enemy_code]['max_health'] = adj['hp_new']
        st.session_state.enemy_overrides[enemy_code]['base_damage'] = adj['damage_new']


def apply_enemy_removal(enemy_code: str):
    """Retire un ennemi de la sélection"""

    if 'selected_enemies' in st.session_state:
        if enemy_code in st.session_state.selected_enemies:
            st.session_state.selected_enemies.remove(enemy_code)


def apply_enemy_addition(enemy_code: str):
    """Ajoute un ennemi à la sélection"""

    if 'selected_enemies' not in st.session_state:
        st.session_state.selected_enemies = []

    if enemy_code not in st.session_state.selected_enemies:
        st.session_state.selected_enemies.append(enemy_code)
