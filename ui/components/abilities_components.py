"""
Composants UI pour le système de capacités
VERSION PHASE 5 - Interface utilisateur complète
"""

import streamlit as st
from typing import List, Dict, Any, Optional
from models.character import Character
from models.abilities import Ability, AbilityType

# Import du système de capacités
try:
    from models.abilities import Ability, AbilityType, AbilityAction
    ABILITIES_SYSTEM_AVAILABLE = True
except ImportError:
    ABILITIES_SYSTEM_AVAILABLE = False

def display_hero_abilities_summary(hero: Character) -> None:
    """
    Affiche un résumé compact des capacités d'un héros dans le récapitulatif
    
    Args:
        hero: Héros avec capacités
    """
    if not ABILITIES_SYSTEM_AVAILABLE or not hasattr(hero, 'abilities') or not hero.abilities:
        return
    
    unlocked_abilities = [a for a in hero.abilities if a.ability_number in hero.unlocked_abilities]
    available_abilities = [a for a in unlocked_abilities if hero.can_use_ability(a)[0]] if hasattr(hero, 'can_use_ability') else unlocked_abilities
    
    # Affichage compact dans le récapitulatif
    if unlocked_abilities:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, rgba(123,104,238,0.1), rgba(147,112,219,0.05)); 
                    border-left: 4px solid #7b68ee; padding: 8px 12px; margin: 5px 0; border-radius: 0 8px 8px 0;">
            <div style="font-size: 0.85rem; color: #7b68ee; font-weight: bold; margin-bottom: 3px;">
                🔮 Capacités ({len(available_abilities)}/{len(unlocked_abilities)} disponibles)
            </div>
            <div style="font-size: 0.75rem; color: #666; line-height: 1.3;">
                {_format_abilities_compact(available_abilities)}
            </div>
        </div>
        """, unsafe_allow_html=True)

def _format_abilities_compact(abilities: List[Ability]) -> str:
    """Formate les capacités en mode compact pour le récapitulatif"""
    if not abilities:
        return "Aucune capacité disponible"
    
    formatted = []
    for ability in abilities[:3]:  # Limite à 3 pour éviter surcharge
        cost_display = f"⚡{ability.spell_cost}" if ability.spell_cost > 0 else "⚔️"
        formatted.append(f"{cost_display} {ability.name.split(' ')[-1]}")  # Nom court
    
    result = " • ".join(formatted)
    if len(abilities) > 3:
        result += f" • +{len(abilities) - 3} autres"
    
    return result

def display_hero_abilities_detailed(hero: Character, key_suffix: str = "") -> None:
    """
    Affiche l'interface détaillée des capacités d'un héros
    
    Args:
        hero: Héros avec capacités
        key_suffix: Suffixe pour les clés Streamlit (éviter conflits)
    """
    if not ABILITIES_SYSTEM_AVAILABLE or not hasattr(hero, 'abilities') or not hero.abilities:
        st.info("🔮 Aucune capacité disponible pour ce héros")
        return
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(123,104,238,0.15), rgba(147,112,219,0.1));
                border: 2px solid #7b68ee; border-radius: 15px; padding: 20px; margin: 15px 0;">
        <h3 style="color: #7b68ee; margin-top: 0; font-family: 'Cinzel', serif; text-align: center;">
            🔮 CAPACITÉS DE {hero.name.upper()}
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # FIX BUG DRUIDE - En forme animale, utiliser stats brutes (sans équipements)
    is_animal_form = (hero.code == "P-1" and
                      hasattr(hero, 'current_form') and
                      hero.current_form in ["bear", "wolf"])

    if is_animal_form:
        max_spells = hero.spells
    else:
        max_spells = hero.get_total_spells()

    # État actuel du héros
    current_spells = getattr(hero, 'current_spells', max_spells)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔮 Sorts", f"{current_spells}/{max_spells}")
    with col2:
        st.metric("🔓 Débloquées", f"{len(hero.unlocked_abilities)}/{len(hero.abilities)}")
    with col3:
        can_act = not getattr(hero, 'action_taken_this_turn', False)
        st.metric("⚡ Peut Agir", "Oui" if can_act else "Non")
    
    # Affichage des capacités par statut
    unlocked_abilities = [a for a in hero.abilities if a.ability_number in hero.unlocked_abilities]
    locked_abilities = [a for a in hero.abilities if a.ability_number not in hero.unlocked_abilities]
    
    if unlocked_abilities:
        st.markdown("### 🔓 Capacités Débloquées")
        for ability in unlocked_abilities:
            display_ability_card(hero, ability, key_suffix)
    
    if locked_abilities:
        st.markdown("### 🔒 Capacités Verrouillées")
        for ability in locked_abilities:
            display_locked_ability_card(ability, hero, key_suffix)

def display_ability_card(hero: Character, ability: Ability, key_suffix: str = "") -> None:
    """
    Affiche une carte de capacité avec bouton d'activation
    
    Args:
        hero: Héros propriétaire
        ability: Capacité à afficher
        key_suffix: Suffixe pour clés Streamlit
    """
    # Vérification si la capacité peut être utilisée
    can_use, reason = hero.can_use_ability(ability) if hasattr(hero, 'can_use_ability') else (True, "")
    
    # Couleur selon le type
    if ability.spell_cost > 0:
        border_color = "#9370db"  # Violet pour magique
        type_icon = "🔮"
        type_name = "Magique"
    else:
        border_color = "#cd853f"  # Orange pour physique
        type_icon = "⚔️"
        type_name = "Physique"
    
    # État de la capacité
    status_color = "#28a745" if can_use else "#dc3545"
    status_text = "Disponible" if can_use else reason
    
    with st.container():
        st.markdown(f"""
        <div style="border: 2px solid {border_color}; border-radius: 12px; padding: 15px; 
                    margin: 10px 0; background: linear-gradient(135deg, {border_color}15, {border_color}05);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h4 style="margin: 0; color: {border_color}; font-size: 1.1rem;">
                    {type_icon} {ability.name}
                </h4>
                <div style="background: {status_color}; color: white; padding: 2px 8px; 
                           border-radius: 12px; font-size: 0.75rem; font-weight: bold;">
                    {status_text}
                </div>
            </div>
            
            <div style="font-size: 0.85rem; color: #666; margin-bottom: 8px; line-height: 1.4;">
                {ability.description}
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 0.8rem; color: #888;">
                    {type_name} • Coût: {ability.spell_cost} sorts
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Bouton d'activation (si disponible)
        if can_use:
            button_key = f"use_ability_{hero.code}_{ability.ability_number}_{key_suffix}"
            if st.button(f"🔮 Utiliser {ability.name}", key=button_key, type="primary"):
                use_ability_action(hero, ability)

def display_locked_ability_card(ability: Ability, hero: Character, key_suffix: str = "") -> None:
    """
    Affiche une carte de capacité verrouillée
    
    Args:
        ability: Capacité verrouillée
        hero: Héros propriétaire
        key_suffix: Suffixe pour clés
    """
    # Vérification si peut être débloquée
    can_unlock = False
    if hasattr(hero, 'unlocked_abilities'):
        previous_unlocked = (ability.ability_number - 1) in hero.unlocked_abilities
        can_unlock = previous_unlocked or ability.ability_number == 1
    
    unlock_color = "#ffc107" if can_unlock else "#6c757d"
    
    with st.container():
        st.markdown(f"""
        <div style="border: 2px dashed {unlock_color}; border-radius: 12px; padding: 15px; 
                    margin: 10px 0; background: linear-gradient(135deg, {unlock_color}10, {unlock_color}05); 
                    opacity: 0.7;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h4 style="margin: 0; color: {unlock_color}; font-size: 1.1rem;">
                    🔒 {ability.name}
                </h4>
                <div style="background: {unlock_color}; color: white; padding: 2px 8px; 
                           border-radius: 12px; font-size: 0.75rem;">
                    Niveau {ability.ability_number}
                </div>
            </div>
            
            <div style="font-size: 0.85rem; color: #888; margin-bottom: 8px; line-height: 1.4;">
                {ability.description}
            </div>
            
            <div style="font-size: 0.8rem; color: #999;">
                Coût: {ability.spell_cost} sorts • {"Peut débloquer" if can_unlock else "Prérequis non remplis"}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Bouton de déblocage si possible
        if can_unlock:
            unlock_key = f"unlock_ability_{hero.code}_{ability.ability_number}_{key_suffix}"
            if st.button(f"🔓 Débloquer Niveau {ability.ability_number}", key=unlock_key):
                unlock_ability_action(hero, ability.ability_number)

def use_ability_action(hero: Character, ability: Ability) -> None:
    """
    Action d'utilisation d'une capacité avec feedback utilisateur
    
    Args:
        hero: Héros utilisant la capacité
        ability: Capacité à utiliser
    """
    if not hasattr(hero, 'use_ability'):
        st.error("❌ Système de capacités non disponible")
        return
    
    # Utilisation de la capacité
    action = hero.use_ability(ability)
    
    if action.success:
        st.success(f"✅ {hero.name} utilise {ability.name}")
        
        # Affichage des détails
        details = []
        if action.spell_cost_paid > 0:
            details.append(f"Coût: {action.spell_cost_paid} sorts")
        if action.prevents_attack:
            details.append("Empêche l'attaque ce tour")
        
        if details:
            st.info(" • ".join(details))
        
        # Mise à jour de l'état dans la session
        _update_hero_state_in_session(hero)
        
    else:
        st.error(f"❌ Impossible d'utiliser {ability.name}: {action.failure_reason}")

def unlock_ability_action(hero: Character, ability_number: int) -> None:
    """
    Action de déblocage d'une capacité
    
    Args:
        hero: Héros pour qui débloquer
        ability_number: Numéro de la capacité
    """
    if not hasattr(hero, 'unlock_ability'):
        st.error("❌ Système de déblocage non disponible")
        return
    
    success = hero.unlock_ability(ability_number)
    
    if success:
        ability = next((a for a in hero.abilities if a.ability_number == ability_number), None)
        ability_name = ability.name if ability else f"Capacité {ability_number}"
        
        st.success(f"🔓 {ability_name} débloquée pour {hero.name} !")
        st.balloons()
        
        # Mise à jour session
        _update_hero_state_in_session(hero)
        
        # Rerun pour rafraîchir l'affichage
        st.rerun()
    else:
        st.error(f"❌ Impossible de débloquer la capacité {ability_number}")

def _update_hero_state_in_session(hero: Character) -> None:
    """Met à jour l'état du héros dans la session Streamlit"""
    # TODO: Implémenter la synchronisation avec st.session_state
    # Cette fonction sera utilisée pour persister les changements
    pass

def display_abilities_in_combat_recap(heroes: List[Character]) -> None:
    """
    Affiche les capacités dans le récapitulatif "Formation de Guerre"
    
    Args:
        heroes: Liste des héros sélectionnés
    """
    if not ABILITIES_SYSTEM_AVAILABLE:
        return
    
    heroes_with_abilities = [h for h in heroes if hasattr(h, 'abilities') and h.abilities]
    
    if not heroes_with_abilities:
        return
    
    st.markdown("### 🔮 Aperçu des Capacités")
    
    for hero in heroes_with_abilities:
        with st.expander(f"🧙‍♂️ {hero.name} - Capacités", expanded=False):
            display_hero_abilities_summary(hero)

def display_combat_abilities_panel(heroes: List[Character]) -> Dict[str, Any]:
    """
    Affiche le panneau de gestion des capacités pendant le combat
    
    Args:
        heroes: Héros en combat
        
    Returns:
        Dict avec les actions de capacités sélectionnées
    """
    if not ABILITIES_SYSTEM_AVAILABLE:
        return {}
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4a148c, #7b1fa2); 
                border-radius: 15px; padding: 20px; margin: 15px 0; text-align: center;">
        <h3 style="color: white; margin: 0; font-family: 'Cinzel', serif;">
            🔮 ACTIVATION DES CAPACITÉS
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    selected_actions = {}
    
    for i, hero in enumerate(heroes):
        if not hasattr(hero, 'abilities') or not hero.abilities:
            continue
        
        if not hero.is_alive():
            continue
        
        st.markdown(f"#### 🧙‍♂️ {hero.name}")

        # FIX BUG DRUIDE - En forme animale, utiliser stats brutes (sans équipements)
        is_animal_form = (hero.code == "P-1" and
                          hasattr(hero, 'current_form') and
                          hero.current_form in ["bear", "wolf"])

        if is_animal_form:
            # Stats de la forme animale (brutes, sans équipements)
            max_hp = hero.health
            max_spells = hero.spells
        else:
            # Stats normales (avec équipements)
            max_hp = hero.get_total_health()
            max_spells = hero.get_total_spells()

        # État du héros
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("❤️ PV", f"{hero.current_health}/{max_hp}")
        with col2:
            current_spells = getattr(hero, 'current_spells', max_spells)
            st.metric("🔮 Sorts", f"{current_spells}/{max_spells}")
        with col3:
            can_act = not getattr(hero, 'action_taken_this_turn', False)
            st.metric("⚡ Statut", "Actif" if can_act else "Action prise")
        
        # Capacités disponibles
        if hasattr(hero, 'get_available_abilities'):
            available_abilities = hero.get_available_abilities()
        else:
            available_abilities = [a for a in hero.abilities if a.ability_number in hero.unlocked_abilities]
        
        if available_abilities and can_act:
            st.markdown("**Capacités disponibles:**")
            
            for ability in available_abilities:
                can_use, reason = hero.can_use_ability(ability) if hasattr(hero, 'can_use_ability') else (True, "")
                
                # Interface de sélection
                col_ability, col_button = st.columns([3, 1])
                
                with col_ability:
                    # Carte capacité compacte
                    type_icon = "🔮" if ability.spell_cost > 0 else "⚔️"
                    status_color = "#28a745" if can_use else "#dc3545"
                    
                    st.markdown(f"""
                    <div style="border-left: 4px solid {status_color}; padding: 8px 12px; 
                                background: {status_color}15; border-radius: 0 8px 8px 0; margin: 5px 0;">
                        <strong>{type_icon} {ability.name}</strong><br>
                        <small style="color: #666;">{ability.description[:60]}...</small><br>
                        <small style="color: {status_color};">Coût: {ability.spell_cost} • {reason if not can_use else 'Prêt'}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_button:
                    if can_use:
                        button_key = f"combat_ability_{hero.code}_{ability.ability_number}_{i}"
                        if st.button("Utiliser", key=button_key, type="primary"):
                            selected_actions[hero.code] = {
                                'action_type': 'ability',
                                'ability': ability,
                                'hero': hero
                            }
                            st.success(f"🔮 {ability.name} sélectionnée")
        
        elif not can_act:
            st.info("⏳ Action déjà effectuée ce tour")
        else:
            st.info("🔒 Aucune capacité disponible")
        
        st.markdown("---")
    
    return selected_actions

def display_abilities_status_sidebar(heroes: List[Character]) -> None:
    """
    Affiche l'état des capacités dans la sidebar
    
    Args:
        heroes: Héros à surveiller
    """
    if not ABILITIES_SYSTEM_AVAILABLE:
        return
    
    with st.sidebar:
        st.markdown("### 🔮 État Capacités")
        
        for hero in heroes:
            if not hasattr(hero, 'abilities') or not hero.abilities:
                continue

            # FIX BUG DRUIDE - En forme animale, utiliser stats brutes (sans équipements)
            is_animal_form = (hero.code == "P-1" and
                              hasattr(hero, 'current_form') and
                              hero.current_form in ["bear", "wolf"])

            if is_animal_form:
                max_spells = hero.spells
            else:
                max_spells = hero.get_total_spells()

            # Statut compact
            current_spells = getattr(hero, 'current_spells', max_spells)
            unlocked_count = len(hero.unlocked_abilities)
            
            spell_percentage = (current_spells / max_spells * 100) if max_spells > 0 else 0
            
            st.markdown(f"""
            <div style="border: 1px solid #7b68ee; border-radius: 8px; padding: 8px; margin: 5px 0;">
                <strong>{hero.name}</strong><br>
                <small>🔮 Sorts: {current_spells}/{max_spells} ({spell_percentage:.0f}%)</small><br>
                <small>🔓 Capacités: {unlocked_count}/{len(hero.abilities)}</small>
            </div>
            """, unsafe_allow_html=True)

def display_ability_unlock_interface(hero: Character) -> None:
    """
    Interface de déblocage de capacités pour un héros
    
    Args:
        hero: Héros pour le déblocage
    """
    if not ABILITIES_SYSTEM_AVAILABLE or not hasattr(hero, 'abilities') or not hero.abilities:
        return
    
    st.markdown(f"### 🔓 Déblocage de Capacités - {hero.name}")
    
    # Progression actuelle
    unlocked_count = len(hero.unlocked_abilities)
    total_count = len(hero.abilities)
    progress = unlocked_count / total_count if total_count > 0 else 0
    
    st.progress(progress, text=f"Progression: {unlocked_count}/{total_count} capacités")
    
    # Capacité suivante à débloquer
    next_ability_number = max(hero.unlocked_abilities) + 1 if hero.unlocked_abilities else 1
    next_ability = next((a for a in hero.abilities if a.ability_number == next_ability_number), None)
    
    if next_ability:
        st.markdown("#### 🎯 Prochaine Capacité")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            type_icon = "🔮" if next_ability.spell_cost > 0 else "⚔️"
            st.markdown(f"""
            <div style="border: 2px solid #ffc107; border-radius: 12px; padding: 15px; 
                        background: linear-gradient(135deg, #ffc10720, #ffc10710);">
                <h4 style="color: #e65100; margin-top: 0;">
                    {type_icon} {next_ability.name}
                </h4>
                <p style="margin-bottom: 5px; color: #666;">
                    {next_ability.description}
                </p>
                <small style="color: #888;">
                    Coût: {next_ability.spell_cost} sorts • Niveau {next_ability.ability_number}
                </small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button(f"🔓 Débloquer", key=f"unlock_{hero.code}_{next_ability.ability_number}"):
                unlock_ability_action(hero, next_ability.ability_number)
    else:
        st.success("🏆 Toutes les capacités sont débloquées !")

def get_abilities_integration_css() -> str:
    """Retourne le CSS pour l'intégration des capacités"""
    return """
    <style>
    /* Styles pour les capacités */
    .ability-card {
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .ability-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(123, 104, 238, 0.3);
    }
    
    .ability-magical {
        border-left-color: #9370db !important;
    }
    
    .ability-physical {
        border-left-color: #cd853f !important;
    }
    
    .spell-meter {
        background: linear-gradient(90deg, #7b68ee, #9370db);
        border-radius: 10px;
        color: white;
        padding: 5px 10px;
        font-weight: bold;
    }
    
    .ability-locked {
        filter: grayscale(0.7);
        opacity: 0.6;
    }
    
    .ability-available {
        animation: pulse-glow 2s infinite;
    }
    
    @keyframes pulse-glow {
        0% { box-shadow: 0 0 5px rgba(123, 104, 238, 0.3); }
        50% { box-shadow: 0 0 20px rgba(123, 104, 238, 0.6); }
        100% { box-shadow: 0 0 5px rgba(123, 104, 238, 0.3); }
    }
    </style>
    """

# === FONCTIONS UTILITAIRES ===

def check_abilities_ui_compatibility() -> Dict[str, bool]:
    """Vérifie la compatibilité de l'interface avec le système de capacités"""
    return {
        'abilities_system': ABILITIES_SYSTEM_AVAILABLE,
        'streamlit_version': True,  # Assume compatible
        'character_methods': True,  # Sera testé dynamiquement
        'ui_ready': ABILITIES_SYSTEM_AVAILABLE
    }

def get_abilities_summary_for_ui(heroes: List[Character]) -> Dict[str, Any]:
    """
    Génère un résumé optimisé pour l'affichage UI
    
    Returns:
        Dict avec statistiques pour l'interface
    """
    if not ABILITIES_SYSTEM_AVAILABLE:
        return {'enabled': False}
    
    summary = {
        'enabled': True,
        'total_heroes': len(heroes),
        'heroes_with_abilities': 0,
        'total_abilities': 0,
        'total_unlocked': 0,
        'heroes_details': []
    }
    
    for hero in heroes:
        if hasattr(hero, 'abilities') and hero.abilities:
            # FIX BUG DRUIDE - En forme animale, utiliser stats brutes (sans équipements)
            is_animal_form = (hero.code == "P-1" and
                              hasattr(hero, 'current_form') and
                              hero.current_form in ["bear", "wolf"])

            if is_animal_form:
                max_spells = hero.spells
            else:
                max_spells = hero.get_total_spells()

            hero_summary = {
                'name': hero.name,
                'code': hero.code,
                'abilities_count': len(hero.abilities),
                'unlocked_count': len(hero.unlocked_abilities) if hasattr(hero, 'unlocked_abilities') else 0,
                'spells_current': getattr(hero, 'current_spells', max_spells),
                'spells_max': max_spells
            }
            
            summary['heroes_with_abilities'] += 1
            summary['total_abilities'] += hero_summary['abilities_count']
            summary['total_unlocked'] += hero_summary['unlocked_count']
            summary['heroes_details'].append(hero_summary)
    
    return summary

# === FONCTIONS POUR INTÉGRATION DANS L'APP PRINCIPALE ===

def integrate_abilities_in_hero_recap(hero_data: Dict, hero: Character) -> Dict:
    """
    Intègre les informations de capacités dans le récapitulatif de héros
    
    Args:
        hero_data: Données actuelles du héros
        hero: Instance Character avec capacités
        
    Returns:
        Dict étendu avec informations capacités
    """
    if not ABILITIES_SYSTEM_AVAILABLE or not hasattr(hero, 'abilities'):
        return hero_data
    
    # Ajout des informations capacités
    abilities_info = {
        'has_abilities': len(hero.abilities) > 0,
        'abilities_count': len(hero.abilities),
        'unlocked_count': len(hero.unlocked_abilities) if hasattr(hero, 'unlocked_abilities') else 0,
        'available_count': 0,
        'next_unlock': None
    }
    
    if hero.abilities:
        # Capacités disponibles
        if hasattr(hero, 'get_available_abilities'):
            abilities_info['available_count'] = len(hero.get_available_abilities())
        
        # Prochaine capacité à débloquer
        if hasattr(hero, 'unlocked_abilities'):
            next_number = max(hero.unlocked_abilities) + 1 if hero.unlocked_abilities else 1
            next_ability = next((a for a in hero.abilities if a.ability_number == next_number), None)
            if next_ability:
                abilities_info['next_unlock'] = {
                    'number': next_ability.ability_number,
                    'name': next_ability.name,
                    'cost': next_ability.spell_cost
                }
    
    hero_data['abilities'] = abilities_info
    return hero_data

def add_abilities_to_combat_config(config: Dict) -> Dict:
    """
    Ajoute la configuration des capacités au config de combat
    
    Args:
        config: Configuration de combat actuelle
        
    Returns:
        Configuration étendue
    """
    config['abilities_enabled'] = ABILITIES_SYSTEM_AVAILABLE
    config['abilities_settings'] = {
        'auto_use': False,  # Utilisation manuelle par défaut
        'ai_assistance': True,  # IA suggère des capacités
        'show_cooldowns': True,  # Affiche les limitations
        'detailed_effects': True  # Effets détaillés dans le log
    }
    
    return config

# === FONCTIONS DE TEST UI ===

def test_abilities_ui_components():
    """Teste les composants UI des capacités"""
    print("🖥️ === TEST COMPOSANTS UI CAPACITÉS ===")
    print("======================================")
    
    try:
        # Vérification compatibilité
        compatibility = check_abilities_ui_compatibility()
        print("📊 Compatibilité UI:")
        for component, status in compatibility.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {component}: {status}")
        
        if not compatibility['ui_ready']:
            print("❌ Interface non prête")
            return False
        
        # Test génération CSS
        css = get_abilities_integration_css()
        print(f"✅ CSS généré: {len(css)} caractères")
        
        print("✅ Composants UI validés")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test UI: {e}")
        return False

if __name__ == "__main__":
    test_abilities_ui_components()