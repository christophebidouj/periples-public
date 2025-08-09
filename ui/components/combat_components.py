"""
Composants de combat pour le Simulateur Périples
Résultats, métriques, logs et analyses de combat
VERSION AVEC SUPPORT STATUS COLORÉ
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from ui.styling import get_combat_result_styles, style_combat_log_entry
from ui.components.ui_elements import get_hero_icon

def display_combat_result_banner(winner: str):
    """
    Affiche la bannière de résultat de combat
    
    Args:
        winner: 'heroes', 'enemies', ou 'draw'
    """
    combat_styles = get_combat_result_styles()
    
    if winner == 'heroes':
        st.markdown(combat_styles['victory'], unsafe_allow_html=True)
    elif winner == 'enemies':
        st.markdown(combat_styles['defeat'], unsafe_allow_html=True)
    else:
        st.markdown(combat_styles['draw'], unsafe_allow_html=True)

def display_combat_metrics(resource_metrics: Dict[str, Any]):
    """
    Affiche les métriques de ressources du combat
    
    Args:
        resource_metrics: Dictionnaire avec les métriques calculées
    """
    st.subheader("📊 Bilan des Ressources")
    combat_styles = get_combat_result_styles()
    
    # Métriques principales en 3 colonnes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        damage_card = combat_styles['metric_card'].format(
            bg_color="rgba(220,20,60,0.1)", 
            border_color="#dc143c", 
            color="#8b0000",
            icon="💔", 
            title="Blessures", 
            value=resource_metrics['total_damage_taken'], 
            text_color="#b22222"
        )
        st.markdown(damage_card, unsafe_allow_html=True)
    
    with col2:
        spells_card = combat_styles['metric_card'].format(
            bg_color="rgba(138,43,226,0.1)", 
            border_color="#8a2be2", 
            color="#4b0082",
            icon="✨", 
            title="Sorts", 
            value=resource_metrics['total_spells_used'], 
            text_color="#663399"
        )
        st.markdown(spells_card, unsafe_allow_html=True)
    
    with col3:
        avg_card = combat_styles['metric_card'].format(
            bg_color="rgba(255,165,0,0.1)", 
            border_color="#ffa500", 
            color="#ff8c00",
            icon="📈", 
            title="Moyenne", 
            value=resource_metrics['average_damage_per_hero'], 
            text_color="#b8860b"
        )
        st.markdown(avg_card, unsafe_allow_html=True)

def display_heroes_individual_table(resource_metrics: Dict[str, Any]):
    """
    Affiche le tableau détaillé des performances individuelles des héros
    
    Args:
        resource_metrics: Métriques contenant heroes_individual
    """
    st.markdown("#### 🎯 Bilan Individuel")
    
    heroes_metrics = []
    for hero_data in resource_metrics['heroes_individual']:
        blessures = hero_data['damage_taken']
        
        # Évaluation de la difficulté selon les critères utilisateur
        if blessures == 0:
            difficulty = "😊 Très facile"
        elif blessures <= 2:
            difficulty = "🙂 Normal"
        elif blessures <= 4:
            difficulty = "😰 Difficile"
        else:
            difficulty = "😵 Trop difficile"
        
        # Construction de la ligne de données
        heroes_metrics.append({
            "Héros": f"{get_hero_icon(hero_data['name'])} {hero_data['name']} ({hero_data['build']})",
            "Blessures": f"{blessures}",
            "Difficulté": difficulty,
            "PV Restants": f"{hero_data['health_remaining']} ({hero_data['health_percentage']}%)",
            "Sorts": hero_data['spells_used'],
            "Statut": "🟢 Vivant" if hero_data['is_alive'] else "💀 KO"
        })
    
    # Affichage du tableau si données disponibles
    if heroes_metrics:
        df_metrics = pd.DataFrame(heroes_metrics)
        st.dataframe(df_metrics, use_container_width=True, hide_index=True)

def display_combat_log(log_lines: List[str]):
    """
    Affiche le journal de combat avec styles formatés + SUPPORT STATUS COLORÉ
    
    Args:
        log_lines: Liste des lignes de log du combat
    """
    st.subheader("📜 Journal de Combat")
    
    # Traitement spécial des lignes avec fond coloré
    formatted_lines = []
    
    for line in log_lines:
        # NOUVEAU - Détection et style spécial pour les lignes STATUS
        if "**📊 📊 STATUS:" in line:
            # Nettoyer la ligne des marqueurs spéciaux
            clean_line = line.replace("**📊 📊 STATUS:", "STATUS:").replace("📊 📊**", "")
            
            # Style avec fond bleu clair et bordure
            status_styled = f"""
            <div style='background: linear-gradient(135deg, rgba(33, 150, 243, 0.15), rgba(25, 118, 210, 0.1)); 
                       border-left: 5px solid #2196f3; 
                       border-radius: 8px;
                       padding: 12px 16px; 
                       margin: 12px 0; 
                       font-family: "SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace; 
                       font-size: 13px; 
                       color: #1565c0; 
                       font-weight: bold;
                       box-shadow: 0 2px 4px rgba(33, 150, 243, 0.1);">
                📊 {clean_line}
            </div>
            """
            formatted_lines.append(status_styled)
        
        # Styles existants pour les autres lignes importantes
        elif "=== ROUND" in line:
            round_styled = f"""
            <div style='background: linear-gradient(135deg, rgba(139, 69, 19, 0.12), rgba(160, 82, 45, 0.08)); 
                       border: 2px solid #8b4513; 
                       border-radius: 10px;
                       padding: 12px; 
                       margin: 15px 0; 
                       text-align: center; 
                       font-weight: bold; 
                       font-size: 16px; 
                       color: #8b4513;
                       font-family: "Cinzel", serif;'>
                {line}
            </div>
            """
            formatted_lines.append(round_styled)
        
        elif "🛡️ Phase des Héros" in line:
            heroes_phase_styled = f"""
            <div style='background: linear-gradient(135deg, rgba(34, 139, 34, 0.12), rgba(0, 100, 0, 0.08)); 
                       border-left: 4px solid #228b22; 
                       border-radius: 6px;
                       padding: 10px 12px; 
                       margin: 8px 0; 
                       font-weight: bold; 
                       color: #006400;'>
                {line}
            </div>
            """
            formatted_lines.append(heroes_phase_styled)
        
        elif "👹 Phase des Ennemis" in line:
            enemies_phase_styled = f"""
            <div style='background: linear-gradient(135deg, rgba(220, 20, 60, 0.12), rgba(139, 0, 0, 0.08)); 
                       border-left: 4px solid #dc143c; 
                       border-radius: 6px;
                       padding: 10px 12px; 
                       margin: 8px 0; 
                       font-weight: bold; 
                       color: #8b0000;'>
                {line}
            </div>
            """
            formatted_lines.append(enemies_phase_styled)
        
        elif "🏆" in line or "VICTOIRE" in line:
            victory_styled = f"""
            <div style='background: linear-gradient(135deg, rgba(34, 139, 34, 0.2), rgba(0, 100, 0, 0.15)); 
                       border: 3px solid #228b22; 
                       border-radius: 10px;
                       padding: 15px; 
                       margin: 15px 0; 
                       text-align: center; 
                       font-weight: bold; 
                       font-size: 18px; 
                       color: #006400;'>
                {line}
            </div>
            """
            formatted_lines.append(victory_styled)
        
        elif "💀 DÉFAITE" in line or "DÉFAITE" in line:
            defeat_styled = f"""
            <div style='background: linear-gradient(135deg, rgba(220, 20, 60, 0.2), rgba(139, 0, 0, 0.15)); 
                       border: 3px solid #dc143c; 
                       border-radius: 10px;
                       padding: 15px; 
                       margin: 15px 0; 
                       text-align: center; 
                       font-weight: bold; 
                       font-size: 18px; 
                       color: #8b0000;'>
                {line}
            </div>
            """
            formatted_lines.append(defeat_styled)
        
        elif "CRITIQUE" in line and "⚡" in line:
            critical_styled = f"""
            <div style='background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 140, 0, 0.15)); 
                       border-left: 4px solid #ffd700; 
                       border-radius: 6px;
                       padding: 8px 12px; 
                       margin: 5px 0; 
                       font-weight: bold; 
                       color: #ff8c00;'>
                {line}
            </div>
            """
            formatted_lines.append(critical_styled)
        
        # Lignes normales avec style par défaut
        else:
            # Utilise la fonction de style existante pour les autres lignes
            formatted_lines.append(style_combat_log_entry(line))
    
    # Construction du conteneur HTML avec scroll
    log_html = """
    <div style='max-height: 600px; overflow-y: auto; padding: 15px; 
                background: rgba(244,228,188,0.3); 
                border: 1px solid rgba(139,69,19,0.2);
                border-radius: 10px; 
                font-family: monospace;'>
    """
    log_html += "".join(formatted_lines)
    log_html += "</div>"
    
    st.markdown(log_html, unsafe_allow_html=True)
    
    # Info utilisateur pour copie manuelle si besoin
    st.info("💡 Pour copier le journal : sélectionnez le texte ci-dessus avec la souris puis Ctrl+C")

def display_combat_summary(result: Dict[str, Any]):
    """
    Affiche un résumé final du combat - Version simplifiée sans boutons
    
    Args:
        result: Dictionnaire des résultats de combat
    """
    st.subheader("🎯 Résumé du Combat")
    
    # Informations basiques du combat
    combat_info = f"""
    <div style="background: linear-gradient(135deg, rgba(212,175,55,0.1), rgba(255,215,0,0.1));
                border: 2px solid #d4af37; border-radius: 12px; padding: 15px; margin: 15px 0;">
        <h5 style="color: #8b4513; margin: 0 0 10px 0; font-family: 'Cinzel', serif;">📊 STATISTIQUES GÉNÉRALES</h5>
        <div style="font-family: monospace; font-weight: bold;">
            ⏱️ Durée: {result.get('rounds', 'N/A')} rounds<br>
            🏆 Vainqueur: {result.get('winner', 'Indéterminé').title()}<br>
            ⚔️ Survivants héros: {result.get('heroes_remaining', 0)}<br>
            👹 Survivants ennemis: {result.get('enemies_remaining', 0)}
        </div>
    </div>
    """
    st.markdown(combat_info, unsafe_allow_html=True)
    
    # Instructions pour relancer un combat
    st.info("🔄 Pour un nouveau combat : modifiez votre sélection dans l'onglet 'Sélection' et relancez")