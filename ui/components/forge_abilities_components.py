"""
Composants capacités + potions pour l'onglet Forge
VERSION CONCISE - Code simple et accessible débutants Python
"""

import streamlit as st
from typing import List, Dict, Optional

# === RÉCUPÉRATION CAPACITÉS ===

def get_abilities_for_hero(hero_code: str, loader) -> List:
    """Récupère les capacités d'un héros avec fallbacks"""
    # Méthode 1: DataLoader
    try:
        if hasattr(loader, 'get_hero_abilities'):
            abilities = loader.get_hero_abilities(hero_code)
            if abilities:
                return abilities
    except:
        pass
    
    # Méthode 2: abilities_loader direct
    try:
        from utils.abilities_loader import load_all_abilities
        all_abilities = load_all_abilities()
        return all_abilities.get(hero_code, [])
    except:
        pass
    
    # Méthode 3: Capacités de test
    return create_test_abilities_for_hero(hero_code)

def create_test_abilities_for_hero(hero_code: str) -> List:
    """Crée des capacités de test simples"""
    try:
        from models.abilities import Ability, AbilityEffect, TargetType
        
        # Données de test par héros
        test_data = {
            'P-1': [{'name': 'Forme d\'Ours', 'cost': 0}, {'name': 'Soin Naturel', 'cost': 1}],
            'P-2': [{'name': 'Projectile Magique', 'cost': 1}, {'name': 'Bouclier Magique', 'cost': 1}],
            'P-3': [{'name': 'Soin Proportionnel', 'cost': 1}, {'name': 'Soin Majeur', 'cost': 2}]
        }
        
        # Capacités par défaut
        default_data = [
            {'name': 'Capacité 1', 'cost': 0}, {'name': 'Capacité 2', 'cost': 1},
            {'name': 'Capacité 3', 'cost': 1}, {'name': 'Capacité 4', 'cost': 2},
            {'name': 'Capacité 5', 'cost': 2}, {'name': 'Capacité 6', 'cost': 3}
        ]
        
        abilities_data = test_data.get(hero_code, default_data)
        abilities = []
        
        for i, data in enumerate(abilities_data, 1):
            ability = Ability(
                hero_code=hero_code,
                ability_number=i,
                name=data['name'],
                spell_cost=data['cost'],
                description=f"Description {data['name']}",
                effects=[AbilityEffect(type="test", description=data['name'])],
                target_type=TargetType.SELF,
                is_unlocked=True
            )
            abilities.append(ability)
        
        return abilities
    except:
        return []

# === INTERFACE CAPACITÉS ===

def display_abilities_selection_section(hero_code: str, abilities: List, current_selection: List[int] = None) -> List[int]:
    """Interface sélection capacités avec état persistant"""
    if not current_selection:
        current_selection = []
    
    # Clé de session
    session_key = f"forge_abilities_{hero_code}"
    if session_key not in st.session_state:
        st.session_state[session_key] = list(current_selection)
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(138,43,226,0.1), rgba(244,228,188,0.6));
                border-radius: 12px; padding: 12px; margin: 15px 0; text-align: center;
                border: 2px solid rgba(138,43,226,0.3);">
        <h4 style="margin: 0; color: #8a2be2;">🔮 Capacités Disponibles</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if not abilities:
        st.warning(f"🔮 Aucune capacité pour {hero_code}")
        if st.button("🧪 Créer Capacités Test"):
            test_abilities = create_test_abilities_for_hero(hero_code)
            if test_abilities:
                st.session_state[f'test_abilities_{hero_code}'] = test_abilities
                st.success("✅ Capacités test créées !")
                st.rerun()
        return []
    
    selected = st.session_state[session_key]
    
    # Grille 3x2 pour 6 capacités
    cols_row1 = st.columns(3)
    cols_row2 = st.columns(3)
    all_cols = cols_row1 + cols_row2
    
    for i, ability in enumerate(abilities[:6]):
        if i < len(all_cols):
            with all_cols[i]:
                ability_num = getattr(ability, 'ability_number', i + 1)
                is_selected = ability_num in selected
                
                if display_ability_card(ability, is_selected, hero_code, ability_num):
                    # Toggle sélection
                    if ability_num in selected:
                        selected.remove(ability_num)
                        st.success("➖ Capacité retirée")
                    else:
                        selected.append(ability_num)
                        st.success("➕ Capacité ajoutée")
                    
                    st.session_state[session_key] = selected
                    st.rerun()
    
    # Récapitulatif
    if selected:
        display_abilities_summary(abilities, selected)
    else:
        st.info("💡 Cliquez sur '➕ CHOISIR' pour sélectionner")
    
    return selected

def display_ability_card(ability, is_selected: bool, hero_code: str, ability_number: int) -> bool:
    """Carte capacité avec expander natif"""
    # Infos capacité
    name = getattr(ability, 'name', 'Capacité')
    cost = getattr(ability, 'spell_cost', 0)
    desc = getattr(ability, 'description', 'Description')
    
    # Type et couleur
    if cost > 0:
        type_icon = "🔮"
        color = "#8a2be2"
        type_name = "Magique"
    else:
        type_icon = "⚔️"
        color = "#d2691e"
        type_name = "Physique"
    
    # Badge sélection
    badge = "✅ " if is_selected else ""
    
    # Nom court pour titre
    short_name = name[:15] + "..." if len(name) > 15 else name
    
    with st.expander(f"{badge}{type_icon} {short_name}", expanded=False):
        st.markdown(f"<span style='color: {color}; font-weight: bold;'>{type_name}</span>", 
                   unsafe_allow_html=True)
        
        st.metric("⚡ Coût", f"{cost} sorts" if cost > 0 else "Gratuit")
        
        desc_short = desc[:60] + "..." if len(desc) > 60 else desc
        st.caption(desc_short)
        
        if is_selected:
            st.success("✅ Sélectionnée")
        
        # Bouton
        button_text = "➖ Retirer" if is_selected else "➕ Choisir"
        button_type = "secondary" if is_selected else "primary"
        key = f"ability_{hero_code}_{ability_number}_{is_selected}"
        
        return st.button(button_text, key=key, type=button_type, use_container_width=True)

def display_abilities_summary(abilities: List, selected_numbers: List[int]):
    """Récapitulatif capacités sélectionnées"""
    if not selected_numbers:
        return
    
    # Récupération capacités sélectionnées
    selected_abilities = []
    for ability in abilities:
        ability_num = getattr(ability, 'ability_number', None)
        if ability_num in selected_numbers:
            selected_abilities.append(ability)
    
    if not selected_abilities:
        return
    
    # Calcul coût total
    total_cost = 0
    names = []
    
    for ability in selected_abilities:
        cost = getattr(ability, 'spell_cost', 0)
        name = getattr(ability, 'name', 'Capacité')
        total_cost += cost
        names.append(name)
    
    # Affichage
    names_display = ", ".join(names[:3])
    if len(names) > 3:
        names_display += f" (+{len(names) - 3} autres)"
    
    st.info(f"🎯 **Sélectionnées ({len(selected_abilities)}/6)** : {names_display}")
    
    if total_cost > 0:
        st.caption(f"💫 Coût total : {total_cost} sorts")

# === INTERFACE POTIONS ===

def display_potions_selection_section(hero_code: str) -> Dict[str, int]:
    """Interface sélection potions"""
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(220,20,60,0.1), rgba(244,228,188,0.6));
                border-radius: 12px; padding: 12px; margin: 15px 0; text-align: center;
                border: 2px solid rgba(220,20,60,0.3);">
        <h4 style="margin: 0; color: #dc143c;">🧪 Potions de Santé</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Clés session
    key_small = f"forge_potion_small_{hero_code}"
    key_large = f"forge_potion_large_{hero_code}"
    
    current_small = st.session_state.get(key_small, 0)
    current_large = st.session_state.get(key_large, 0)
    
    # Grille 2 colonnes
    col1, col2 = st.columns(2)
    
    with col1:
        if display_potion_card("small", current_small, hero_code):
            # Logique Petites : 0→1→2→3→0
            if current_small == 0:
                new_count = 1
            elif current_small < 3:
                new_count = current_small + 1
            else:
                new_count = 0
            
            st.session_state[key_small] = new_count
            st.rerun()
    
    with col2:
        if display_potion_card("large", current_large, hero_code):
            # Logique Grande : 0→1→0
            new_count = 1 if current_large == 0 else 0
            st.session_state[key_large] = new_count
            st.rerun()
    
    # Récapitulatif
    total = current_small + current_large
    if total > 0:
        display_potions_summary(current_small, current_large)
    else:
        st.info("💡 Cliquez pour ajouter des potions")
    
    return {'small': current_small, 'large': current_large}

def display_potion_card(potion_type: str, current_count: int, hero_code: str) -> bool:
    """Carte potion avec logique corrigée"""
    # Configuration type
    if potion_type == "small":
        icon = "🩸"
        name = "Petite Potion"
        heal = "Soigne 4 PV"
        limit = "Max 3"
        color = "#dc143c"
        max_count = 3
    else:
        icon = "❤️‍🩹"
        name = "Grande Potion"
        heal = "Soigne totalement"
        limit = "Max 1"
        color = "#8b0000"
        max_count = 1
    
    # Badge et bouton
    if current_count > 0:
        badge = f"✅ x{current_count} "
        if current_count >= max_count:
            button_text = "➖ Retirer"
            button_type = "secondary"
        else:
            button_text = f"➕ Ajouter ({current_count}/{max_count})"
            button_type = "primary"
    else:
        badge = ""
        button_text = "➕ Ajouter"
        button_type = "primary"
    
    with st.expander(f"{badge}{icon} {name}", expanded=False):
        st.markdown(f"<span style='color: {color}; font-weight: bold;'>Potion de Santé</span>", 
                   unsafe_allow_html=True)
        
        col_heal, col_limit = st.columns(2)
        with col_heal:
            st.metric("💚 Effet", heal)
        with col_limit:
            st.metric("📊 Limite", limit)
        
        if current_count > 0:
            st.success(f"✅ {current_count} sélectionnée{'s' if current_count > 1 else ''}")
        
        key = f"potion_{potion_type}_{hero_code}_{current_count}"
        return st.button(button_text, key=key, type=button_type, use_container_width=True)

def display_potions_summary(small_count: int, large_count: int):
    """Récapitulatif potions"""
    total = small_count + large_count
    
    parts = []
    if small_count > 0:
        parts.append(f"🩸 {small_count} Petite{'s' if small_count > 1 else ''}")
    if large_count > 0:
        parts.append(f"❤️‍🩹 {large_count} Grande")
    
    summary = ", ".join(parts)
    st.info(f"🧪 **Potions ({total})** : {summary}")
    
    # Conseils
    if small_count > 0 and large_count > 0:
        st.caption("💡 Combinaison équilibrée")
    elif small_count == 3:
        st.caption("💡 Maximum Petites - Cliquez pour retirer")
    elif small_count >= 2:
        st.caption("💡 Stratégie soins fréquents")

# === UTILITAIRES ===

def validate_abilities_selection(selected_numbers: List[int], max_abilities: int = 6) -> Dict:
    """Valide sélection capacités"""
    validation = {
        'valid': True,
        'count': len(selected_numbers),
        'messages': []
    }
    
    if len(selected_numbers) > max_abilities:
        validation['valid'] = False
        validation['messages'].append(f"Max {max_abilities} capacités")
    
    invalid = [n for n in selected_numbers if not (1 <= n <= 6)]
    if invalid:
        validation['valid'] = False
        validation['messages'].append(f"Numéros invalides: {invalid}")
    
    if len(selected_numbers) != len(set(selected_numbers)):
        validation['valid'] = False
        validation['messages'].append("Doublons détectés")
    
    return validation

def get_forge_selections_summary(hero_code: str, abilities: List, selected_abilities: List[int], 
                                potions: Dict[str, int]) -> Dict:
    """Résumé complet sélections pour aperçu"""
    summary = {
        'has_selections': False,
        'abilities_count': len(selected_abilities),
        'potions_count': potions.get('small', 0) + potions.get('large', 0),
        'abilities_names': [],
        'abilities_cost': 0,
        'potions_text': ""
    }
    
    # Capacités
    if selected_abilities and abilities:
        for ability in abilities:
            ability_num = getattr(ability, 'ability_number', None)
            if ability_num in selected_abilities:
                name = getattr(ability, 'name', 'Capacité')
                cost = getattr(ability, 'spell_cost', 0)
                summary['abilities_names'].append(name)
                summary['abilities_cost'] += cost
    
    # Potions
    if potions.get('small', 0) > 0 or potions.get('large', 0) > 0:
        parts = []
        if potions.get('small', 0) > 0:
            parts.append(f"🩸 {potions['small']}")
        if potions.get('large', 0) > 0:
            parts.append(f"❤️‍🩹 {potions['large']}")
        summary['potions_text'] = ", ".join(parts)
    
    summary['has_selections'] = summary['abilities_count'] > 0 or summary['potions_count'] > 0
    return summary