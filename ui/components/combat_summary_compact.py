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

    # === BANNIÈRE RÉSULTAT ===
    if victory:
        st.success(f"🏆 **VICTOIRE** - Combat terminé au tour {duration}")
    else:
        st.error(f"💀 **DÉFAITE** - Combat terminé au tour {duration}")

    st.markdown("---")

    # === LOG DE COMBAT (TOUJOURS ACCESSIBLE) ===
    with st.expander("📜 Log de Combat", expanded=False):
        for line in log:
            st.text(line)

    st.markdown("---")

    # === MÉTRIQUES D'ÉQUILIBRAGE (Tableaux compacts) ===
    st.markdown("## ⚖️ **Métriques d'Équilibrage**")

    # HÉROS - Tableau compact
    st.markdown("### 🦸 **Héros - Analyse de Performance**")
    heroes_data = []
    total_hero_damage = sum(h.get('damage_dealt', 0) for h in stats['heroes'].values())
    # Tanking total = PV encaissés + dégâts absorbés par parade
    total_hero_tanking = sum(
        h.get('damage_taken', 0) + h.get('parade_tokens_used', 0)
        for h in stats['heroes'].values()
    )

    for hero_code, hero_stats in stats['heroes'].items():
        damage_dealt = hero_stats.get('damage_dealt', 0)
        damage_taken = hero_stats.get('damage_taken', 0)
        parade_absorbed = hero_stats.get('parade_tokens_used', 0)
        attacks_made = hero_stats.get('attacks_made', 0)
        attacks_hit = hero_stats.get('attacks_hit', 0)
        turns_played = hero_stats.get('turns_played', 0)

        # Calculs
        precision = (attacks_hit / attacks_made * 100) if attacks_made > 0 else 0
        dpt = (damage_dealt / turns_played) if turns_played > 0 else 0
        contribution = (damage_dealt / total_hero_damage * 100) if total_hero_damage > 0 else 0
        # Tank basé sur tanking total (PV + Parade)
        total_tanking = damage_taken + parade_absorbed
        tank_ratio = (total_tanking / total_hero_tanking * 100) if total_hero_tanking > 0 else 0

        # Affichage Précision : "−" si aucune attaque physique, sinon %
        if attacks_made == 0:
            precision_display = "−"
        else:
            precision_display = f"{precision:.0f}%"

        heroes_data.append({
            'Héros': hero_stats['name'],
            'Dégâts': damage_dealt,
            'Reçus': damage_taken,
            'Parade Abs.': parade_absorbed,
            'Précision': precision_display,
            'DPT': f"{dpt:.1f}",
            'Contribution': f"{contribution:.0f}%",
            'Tank': f"{tank_ratio:.0f}%",
            'Tours': turns_played,
            'Vivant': '✅' if hero_stats.get('survived', False) else '💀'
        })

    df_heroes = pd.DataFrame(heroes_data)
    st.dataframe(df_heroes, use_container_width=True, hide_index=True)

    st.caption("**Légendes**: Dégâts=infligés | Reçus=encaissés en PV | **Parade Abs.**=dégâts bloqués par jetons de parade | **DPT**=Dégâts Par Tour (physiques + capacités) | Précision=% réussite attaques PHYSIQUES de base **(− = aucune attaque physique)** | Contribution=% dégâts équipe | **Tank**=% tanking total (PV + Parade)")

    # ENNEMIS - Tableau compact
    st.markdown("### 👹 **Ennemis - Analyse de Dangerosité**")
    enemies_data = []

    for enemy_code, enemy_stats in stats['enemies'].items():
        damage_dealt = enemy_stats.get('damage_dealt', 0)
        damage_taken = enemy_stats.get('damage_taken', 0)
        turns_played = enemy_stats.get('turns_played', 0)

        # Calculs
        dpt = (damage_dealt / turns_played) if turns_played > 0 else 0
        danger_rating = (damage_dealt / max(damage_taken, 1)) * turns_played

        enemies_data.append({
            'Ennemi': enemy_stats['name'],
            'Dégâts': damage_dealt,
            'Reçus': damage_taken,
            'DPT': f"{dpt:.1f}",
            'Danger Rating': f"{danger_rating:.1f}",
            'Tours survécus': turns_played,
            'Éliminé': '✅' if not enemy_stats.get('survived', True) else '⚠️ Vivant'
        })

    df_enemies = pd.DataFrame(enemies_data)
    st.dataframe(df_enemies, use_container_width=True, hide_index=True)

    st.caption("**Danger Rating** = (Dégâts / Dégâts reçus) × Tours. Plus élevé = ennemi trop fort pour son niveau.")

    st.markdown("---")

    # === VISUALISATIONS ===
    st.markdown("## 📊 **Visualisations**")

    # 1. COURBE D'ÉVOLUTION PV
    st.markdown("### 💚 **Évolution des PV pendant le combat**")

    # Transformer hp_history en DataFrame pour st.line_chart
    hp_history = stats.get('hp_history', {})
    if hp_history:
        # Créer un DataFrame avec une colonne par combattant
        hp_data = {}
        for combatant_id, turns_data in hp_history.items():
            # Extraire le nom du combattant depuis les stats
            if combatant_id.startswith('hero_'):
                code = combatant_id.replace('hero_', '')
                name = stats['heroes'].get(code, {}).get('name', code)
            elif combatant_id.startswith('enemy_'):
                # Pour les ennemis, format est "enemy_CODE_INDEX"
                parts = combatant_id.replace('enemy_', '').split('_')
                code = '_'.join(parts[:-1]) if len(parts) > 1 else parts[0]
                # CORRIGÉ: Utiliser directement le nom sans ajouter l'index (déjà dans le nom)
                name = stats['enemies'].get(code, {}).get('name', code)
            else:
                name = combatant_id

            hp_data[name] = turns_data

        if hp_data:
            df_hp = pd.DataFrame(hp_data)
            st.line_chart(df_hp, height=300)
            st.caption("📈 _Suivi des points de vie de tous les combattants tour par tour_")
    else:
        st.info("Aucune donnée d'historique PV disponible")

    # 2. HISTOGRAMMES DÉGÂTS
    st.markdown("### ⚔️ **Comparaison des dégâts**")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Dégâts infligés par héros**")
        hero_damage_data = {h['Héros']: h['Dégâts'] for h in heroes_data}
        df_hero_dmg = pd.DataFrame.from_dict(hero_damage_data, orient='index', columns=['Dégâts'])
        st.bar_chart(df_hero_dmg, height=250)

    with col2:
        st.markdown("**Dégâts encaissés (PV + Parade)**")
        hero_tanking_data = {
            h['Héros']: h['Reçus'] + h['Parade Abs.']
            for h in heroes_data
        }
        df_hero_tank = pd.DataFrame.from_dict(hero_tanking_data, orient='index', columns=['Tanking Total'])
        st.bar_chart(df_hero_tank, height=250)

    st.caption("📊 _Histogrammes comparatifs pour identifier déséquilibres de contribution et tanking_")

    st.markdown("---")

    # === ANALYSE D'ÉQUILIBRAGE ===
    st.markdown("## 🎯 **Détection de Déséquilibres**")
    st.caption("ℹ️ _Indicateur automatique, pas vérité absolue. Alertes sur anomalies potentielles - à vous de décider si elles sont problématiques._")

    warnings_found = []
    successes_found = []

    # 1. HÉROS MORTS = Problème grave
    dead_heroes = [h for h in heroes_data if h['Vivant'] == '💀']
    if dead_heroes and victory:
        warnings_found.append(f"⚠️ **Victoire coûteuse** : {len(dead_heroes)} héros mort(s) - Combat trop difficile")
    elif dead_heroes and not victory:
        warnings_found.append(f"⚠️ **Défaite avec pertes** : Ennemis probablement trop forts")

    # 2. CONTRIBUTION DÉSÉQUILIBRÉE (un héros fait tout)
    contributions = [float(h['Contribution'].replace('%', '')) for h in heroes_data]
    max_contribution = max(contributions) if contributions else 0
    if max_contribution > 60 and len(heroes_data) > 1:
        dominant_hero = max(heroes_data, key=lambda x: float(x['Contribution'].replace('%', '')))
        warnings_found.append(f"⚠️ **Déséquilibre de puissance** : {dominant_hero['Héros']} fait {dominant_hero['Contribution']} des dégâts (>60%) - Autres héros sous-utilisés")

    # 3. ENNEMIS TROP DANGEREUX
    if enemies_data:
        dangerous_enemies = [e for e in enemies_data if float(e['Danger Rating'].replace(',', '.')) > 3.0]
        if dangerous_enemies:
            for enemy in dangerous_enemies:
                warnings_found.append(f"⚠️ **Ennemi surévalué** : {enemy['Ennemi']} (Danger: {enemy['Danger Rating']}) - Trop résistant ou trop de dégâts")

    # 4. COMBAT TROP COURT OU TROP LONG
    if duration < 2:
        warnings_found.append(f"⚠️ **Combat trop court** ({duration} tour) - Ennemis peut-être trop faibles")
    elif duration > 6:
        warnings_found.append(f"⚠️ **Combat trop long** ({duration} tours) - Manque de dégâts ou ennemis trop résistants")

    # 5. SUCCÈS : Combat équilibré
    if not dead_heroes and victory and 2 <= duration <= 6:
        successes_found.append(f"✅ **Combat équilibré** : Victoire sans pertes en {duration} tours")
    if max_contribution < 50 and len(heroes_data) > 1:
        successes_found.append(f"✅ **Bonne répartition** : Aucun héros ne domine (max {max_contribution:.0f}%)")

    # Affichage
    if warnings_found:
        for warning in warnings_found:
            st.warning(warning)

    if successes_found:
        for success in successes_found:
            st.success(success)

    if not warnings_found and not successes_found:
        st.info("ℹ️ Pas de déséquilibre majeur détecté - Analysez les tableaux pour affiner")

