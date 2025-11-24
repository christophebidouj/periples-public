"""
Affichage compact et utile du récapitulatif de combat
Focus sur métriques d'équilibrage, pas sur PV finaux
"""

import streamlit as st
import pandas as pd
from typing import Dict, List
from models.character import Character, Enemy


def display_compact_combat_summary(stats: Dict, analysis: Dict, log: List[str]):
    """
    Affiche un récapitulatif compact avec SEULEMENT les métriques utiles pour l'équilibrage

    Args:
        stats: Statistiques brutes du combat
        analysis: Analyse du combat (métriques calculées)
        log: Log de combat complet
    """
    victory = analysis['victory']
    duration = analysis['duration_rounds']
    balance_score = analysis.get('balance_score', 5.0)

    # === BANNIÈRE RÉSULTAT ===
    if victory:
        st.success(f"🏆 **VICTOIRE** - Combat terminé au tour {duration}")
    else:
        st.error(f"💀 **DÉFAITE** - Combat terminé au tour {duration}")

    st.markdown("---")

    # === MÉTRIQUES CLÉS (3 colonnes) ===
    col1, col2, col3 = st.columns(3)

    with col1:
        score_emoji = "🟢" if balance_score >= 7 else "🟡" if balance_score >= 5 else "🔴"
        st.metric("⚖️ Score Équilibrage", f"{score_emoji} {balance_score:.1f}/10")

    with col2:
        st.metric("💪 Héros survivants",
                 f"{analysis['heroes']['surviving']}/{analysis['heroes']['total']}")

    with col3:
        st.metric("❤️ PV moyens finaux",
                 f"{analysis['heroes']['avg_hp_percent']:.0f}%")

    st.markdown("---")

    # === LOG DE COMBAT (TOUJOURS ACCESSIBLE) ===
    with st.expander("📜 **Log de Combat** (Essentiel pour analyse)", expanded=True):
        st.markdown("*Conseil : Gardez le log ouvert pour analyser le déroulement du combat*")
        for line in log:
            st.text(line)

    st.markdown("---")

    # === MÉTRIQUES D'ÉQUILIBRAGE (Tableaux compacts) ===
    st.markdown("## ⚖️ **Métriques d'Équilibrage**")

    # HÉROS - Tableau compact
    st.markdown("### 🦸 **Héros - Analyse de Performance**")
    heroes_data = []
    total_hero_damage = sum(h.get('damage_dealt', 0) for h in stats['heroes'].values())
    total_hero_damage_received = sum(h.get('damage_taken', 0) for h in stats['heroes'].values())

    for hero_code, hero_stats in stats['heroes'].items():
        damage_dealt = hero_stats.get('damage_dealt', 0)
        damage_taken = hero_stats.get('damage_taken', 0)
        attacks_made = hero_stats.get('attacks_made', 0)
        attacks_hit = hero_stats.get('attacks_hit', 0)
        turns_played = hero_stats.get('turns_played', 0)

        # Calculs
        precision = (attacks_hit / attacks_made * 100) if attacks_made > 0 else 0
        dps = (damage_dealt / turns_played) if turns_played > 0 else 0
        contribution = (damage_dealt / total_hero_damage * 100) if total_hero_damage > 0 else 0
        tank_ratio = (damage_taken / total_hero_damage_received * 100) if total_hero_damage_received > 0 else 0

        heroes_data.append({
            'Héros': hero_stats['name'],
            'Dégâts': damage_dealt,
            'Reçus': damage_taken,
            'Précision': f"{precision:.0f}%",
            'DPS': f"{dps:.1f}",
            'Contribution': f"{contribution:.0f}%",
            'Tank': f"{tank_ratio:.0f}%",
            'Tours': turns_played,
            'Vivant': '✅' if hero_stats.get('survived', False) else '💀'
        })

    df_heroes = pd.DataFrame(heroes_data)
    st.dataframe(df_heroes, use_container_width=True, hide_index=True)

    st.caption("**Légendes**: Dégâts=infligés | Reçus=encaissés | DPS=dégâts/tour | Contribution=% dégâts équipe | Tank=% dégâts absorbés")

    # ENNEMIS - Tableau compact
    st.markdown("### 👹 **Ennemis - Analyse de Dangerosité**")
    enemies_data = []

    for enemy_code, enemy_stats in stats['enemies'].items():
        damage_dealt = enemy_stats.get('damage_dealt', 0)
        damage_taken = enemy_stats.get('damage_taken', 0)
        turns_played = enemy_stats.get('turns_played', 0)

        # Calculs
        dps = (damage_dealt / turns_played) if turns_played > 0 else 0
        danger_rating = (damage_dealt / max(damage_taken, 1)) * turns_played

        enemies_data.append({
            'Ennemi': enemy_stats['name'],
            'Dégâts': damage_dealt,
            'Reçus': damage_taken,
            'DPS': f"{dps:.1f}",
            'Danger Rating': f"{danger_rating:.1f}",
            'Tours survécus': turns_played,
            'Éliminé': '✅' if not enemy_stats.get('survived', True) else '⚠️ Vivant'
        })

    df_enemies = pd.DataFrame(enemies_data)
    st.dataframe(df_enemies, use_container_width=True, hide_index=True)

    st.caption("**Danger Rating** = (Dégâts / Dégâts reçus) × Tours. Plus élevé = ennemi trop fort pour son niveau.")

    st.markdown("---")

    # === ANALYSE RAPIDE ===
    st.markdown("## 🎯 **Analyse Rapide**")

    # Identifier le meilleur DPS héros
    best_dps_hero = max(heroes_data, key=lambda x: float(x['DPS'].replace(',', '.')))
    st.info(f"⚔️ **Meilleur DPS**: {best_dps_hero['Héros']} ({best_dps_hero['DPS']} dégâts/tour)")

    # Identifier le tank principal
    main_tank = max(heroes_data, key=lambda x: float(x['Tank'].replace('%', '')))
    st.info(f"🛡️ **Tank principal**: {main_tank['Héros']} ({main_tank['Tank']} des dégâts encaissés)")

    # Identifier l'ennemi le plus dangereux
    if enemies_data:
        most_dangerous = max(enemies_data, key=lambda x: float(x['Danger Rating'].replace(',', '.')))
        danger_value = float(most_dangerous['Danger Rating'].replace(',', '.'))

        if danger_value > 3.0:
            st.warning(f"⚠️ **Ennemi trop fort**: {most_dangerous['Ennemi']} (Danger Rating: {most_dangerous['Danger Rating']}) - Réduire ses stats")
        elif danger_value < 1.0:
            st.success(f"✅ **Ennemi équilibré**: {most_dangerous['Ennemi']} (Danger Rating: {most_dangerous['Danger Rating']})")

    # Utilisation des ressources
    spells_used = analysis['heroes'].get('spells_usage_percent', 0)
    if spells_used < 30:
        st.info(f"✨ **Sorts peu utilisés** ({spells_used:.0f}%) - Combat peut-être trop court ou facile")
    elif spells_used > 80:
        st.warning(f"✨ **Sorts très utilisés** ({spells_used:.0f}%) - Combat intense, héros en difficulté")

    st.markdown("---")

    # === RECOMMANDATIONS ===
    if balance_score < 6:
        st.warning("⚠️ **Combat déséquilibré** - Ajustements recommandés (voir onglet Résultats pour détails)")
    elif balance_score >= 8:
        st.success("✅ **Combat bien équilibré** - Bon niveau de difficulté")

    st.info("📊 **Pour analyse détaillée, visualisations et export CSV** → Allez dans l'onglet **'Résultats'**")
