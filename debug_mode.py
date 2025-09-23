# debug_mode.py - Mode Debug Capacités pour Streamlit
import streamlit as st
import traceback
from typing import List, Dict, Any, Optional

def create_debug_tab():
    st.header("🔧 Mode Debug Capacités")
    st.markdown("Interface de test direct des capacités sans dépendre de l'IA")
    
    if not _test_imports():
        st.error("⚠️ Imports critiques défaillants - Impossible d'utiliser le mode debug")
        return
    
    _create_debug_interface()

def _test_imports() -> bool:
    try:
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        from models.character import Character, Enemy
        return True
    except ImportError as e:
        st.error(f"Erreur import: {e}")
        return False

def _create_debug_interface():
    try:
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        
        total_registered = ABILITY_REGISTRY.get_registered_count()
        st.info(f"📊 Capacités disponibles: {total_registered}/59")
        
        if total_registered == 0:
            st.warning("⚠️ Aucune capacité enregistrée")
            return
        
        heroes_data = _get_available_heroes_data()
        if not heroes_data:
            st.warning("⚠️ Aucun héros avec capacités trouvé")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            hero_names = {
                'P-1': 'P-1 Elneha',
                'P-2': 'P-2 Liarie', 
                'P-3': 'P-3 Atucan',
                'P-4': 'P-4 Kraor',
                'P-5': 'P-5 Thordius',
                'P-6': 'P-6 Stèphe',
                'P-7': 'P-7 Lame',
                'P-8': 'P-8 Raishi'
            }
            
            selected_hero_code = st.selectbox(
                "Héros", 
                options=list(heroes_data.keys()),
                format_func=lambda x: f"{hero_names.get(x, x)} ({len(heroes_data[x])} capacités)"
            )
        
        with col2:
            if selected_hero_code:
                abilities = heroes_data[selected_hero_code]
                ability_options = {f"{ab['name']} (#{ab['number']})": ab for ab in abilities}
                
                selected_ability_name = st.selectbox(
                    "Capacité", 
                    options=list(ability_options.keys())
                )
                selected_ability_data = ability_options[selected_ability_name]
        
        if selected_hero_code and selected_ability_name:
            _test_selected_ability(selected_hero_code, selected_ability_data)
    
    except Exception as e:
        st.error(f"💥 Erreur interface debug: {e}")
        st.code(traceback.format_exc())

def _test_selected_ability(hero_code: str, ability_data: Dict):
    """Teste la capacité sélectionnée"""
    st.subheader(f"🧪 Test: {ability_data['name']}")
    
    # Informations capacité
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Héros:** {hero_code}")
        st.write(f"**Numéro:** {ability_data['number']}")
    
    with col2:
        # Récupérer instance pour infos détaillées
        try:
            from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
            ability_instance = ABILITY_REGISTRY.get_ability_instance(hero_code, ability_data['number'])
            
            if ability_instance:
                st.write(f"**Coût sorts:** {ability_instance.spell_cost}")
                
                # Afficher limitations par combat
                if hasattr(ability_instance, 'uses_per_combat'):
                    st.write(f"**Utilisations/combat:** {ability_instance.uses_per_combat}")
                    if hasattr(ability_instance, 'uses_remaining_combat'):
                        st.write(f"**Restantes:** {ability_instance.uses_remaining_combat}")
                elif hasattr(ability_instance, 'limitation') and ability_instance.limitation:
                    st.write(f"**Limitation:** {ability_instance.limitation}")
                else:
                    st.write("**Utilisations:** Illimitée")
            else:
                st.error("⚠️ Impossible de créer l'instance")
                return
        
        except Exception as e:
            st.error(f"Erreur récupération instance: {e}")
            return
    
    # Configuration du test
    st.subheader("⚙️ Configuration Test")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Utilisateur**")
        user_max_health = st.number_input("PV max", 1, 30, 15, key="user_max_health")
        user_current_health = st.number_input("PV actuels", 0, user_max_health, user_max_health, key="user_current_health")
        user_spells = st.number_input("Sorts", 0, 10, 5, key="user_spells")
        user_precision = st.number_input("Précision", 1, 15, 8, key="user_precision")
    
    with col2:
        st.write("**Alliés**")
        ally_count = st.number_input("Nombre", 0, 3, 1, key="ally_count")
        ally_max_health = st.number_input("PV max alliés", 1, 30, 10, key="ally_max_health")
        
        # FIX CRITIQUE : Permettre 0 PV pour tester Résurrection
        ally_current_health = st.number_input(
            "PV actuels alliés", 
            min_value=0,  # CHANGÉ : 1 → 0 pour permettre alliés inconscients
            max_value=ally_max_health, 
            value=ally_max_health, 
            key="ally_current_health",
            help="⚠️ 0 PV = Inconscient (pour tester Résurrection)"
        )
        
        # Ajout statut visuel
        if ally_current_health == 0:
            st.warning("💀 **Alliés INCONSCIENTS** - Parfait pour tester Résurrection !")
        elif ally_current_health < ally_max_health:
            st.info(f"🩹 **Alliés BLESSÉS** ({ally_current_health}/{ally_max_health} PV)")
        else:
            st.success("💚 **Alliés en PLEINE SANTÉ**")
    
    with col3:
        st.write("**Ennemis**")
        enemy_count = st.number_input("Nombre", 0, 5, 2, key="enemy_count")
        
        # Configuration PV individuels si plusieurs ennemis
        enemy_health_values = []
        if enemy_count > 1:
            st.write("*PV individuels :*")
            for i in range(enemy_count):
                health = st.number_input(
                    f"Ennemi {i+1} PV", 
                    min_value=1, 
                    max_value=50, 
                    value=3,  # Valeur par défaut pour tests répartition
                    key=f"enemy_{i}_health"
                )
                enemy_health_values.append(health)
        else:
            # Un seul ennemi : champ global
            if enemy_count > 0:
                enemy_health = st.number_input("PV ennemis", 1, 50, 20, key="enemy_health")
                enemy_health_values = [enemy_health]
            else:
                enemy_health_values = []

    # Suggestion de configuration selon la capacité
    if ability_instance and ability_instance.name.lower() == "résurrection":
        st.info("💡 **Suggestion pour Résurrection:** Configurez les alliés avec 0 PV actuels !")
    
    # Bouton de test principal
    if st.button("🧪 TESTER CAPACITÉ", type="primary"):
        _execute_ability_test(
            ability_instance, hero_code,
            user_max_health, user_current_health, user_spells, user_precision,
            ally_count, ally_max_health, ally_current_health,
            enemy_count, enemy_health_values
        )

def _test_transformation(hero_code: str, form_type: str, user_max_health: int, user_current_health: int,
                        user_spells: int, user_precision: int, enemy_count: int, enemy_health_values: List[int]):
    """Teste les mécaniques de transformation"""
    st.subheader(f"🔍 Test Transformation: {form_type.title()}")
    
    try:
        from models.character import Character, Enemy
        
        # Créer utilisateur
        user = Character(
            code=hero_code,
            name="TestUser",
            health=user_max_health,
            damage=4,  # Dégâts de base
            precision=user_precision,
            spells=user_spells,
            defense=1
        )
        user.current_health = user_current_health
        user.current_spells = user_spells
        
        # Créer ennemi cible pour test
        if enemy_count > 0:
            enemy_health = enemy_health_values[0] if enemy_health_values else 20
            enemy = Enemy(
                code="TEST-TARGET",
                name="TestTarget",
                defense=3,  # Défense notable pour voir l'effet loup
                stats_by_players={
                    2: {'damage': 3, 'health': enemy_health, 'defense': 3}
                },
                is_magical=False,
                has_magical_damage=False
            )
            enemy.initialize_for_combat(2)
        else:
            st.warning("⚠️ Créez au moins 1 ennemi pour tester les attaques")
            return
        
        # Appliquer transformation
        _apply_transformation(user, form_type)
        
        with st.expander("📊 Comparaison Avant/Après Transformation", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**État Normal**")
                st.write(f"Attaque: 4 (base)")
                st.write(f"Forme: 👤 Humaine")
                st.write(f"Défense: Standard")
                
            with col2:
                st.write(f"**État {form_type.title()}**")
                current_form = getattr(user, 'current_form', 'humaine')
                form_display = user.get_form_display() if hasattr(user, 'get_form_display') else current_form
                
                st.write(f"Attaque: 4 (base)")
                st.write(f"Forme: {form_display}")
                
                if form_type == "ours":
                    st.write(f"**Effet:** Ignore prochaine attaque subie")
                elif form_type == "loup":
                    st.write(f"**Effet:** Double dégâts prochaine attaque")
            
            with col3:
                st.write("**Avantage**")
                if form_type == "ours":
                    st.write(f"🛡️ **Défensif**")
                    st.write(f"Évite 1 attaque complètement")
                elif form_type == "loup":
                    st.write(f"⚔️ **Offensif**") 
                    st.write(f"4 → 8 dégâts (1 attaque)")
        
        # Affichage des buffs temporaires
        if hasattr(user, 'temporary_buffs') and user.temporary_buffs:
            st.write("**🔮 Buffs Temporaires Actifs:**")
            for buff_name, buff_value in user.temporary_buffs.items():
                if buff_value:
                    st.write(f"• **{buff_name}:** {buff_value}")
        
        # Simulation d'effet
        if st.button(f"📋 Voir Effet {form_type.title()}", key=f"effect_{form_type}"):
            _simulate_attack(user, enemy, form_type)
        
        st.success(f"🎉 Test {form_type.title()} terminé")
    
    except Exception as e:
        st.error(f"💥 Erreur test transformation: {e}")
        st.code(traceback.format_exc())

def _apply_transformation(user, form_type: str):
    """Applique la transformation au personnage selon les vraies mécaniques"""
    # Initialiser temporary_buffs si nécessaire
    if not hasattr(user, 'temporary_buffs'):
        user.temporary_buffs = {}
    
    # Initialiser current_form si nécessaire
    if not hasattr(user, 'current_form'):
        user.current_form = 'humaine'
    
    if form_type == "ours":
        # Vraie mécanique : ignore la prochaine attaque subie
        user.temporary_buffs['ignore_next_attack'] = True
        user.current_form = 'ours'
        st.info(f"🐻 Transformation Ours: Ignore la prochaine attaque subie")
    
    elif form_type == "loup":
        # Vraie mécanique : double les dégâts de la prochaine attaque
        user.temporary_buffs['double_damage_next_attack'] = 2
        user.current_form = 'loup'  
        st.info(f"🐺 Transformation Loup: Double dégâts de la prochaine attaque")

def _simulate_attack(user, enemy, form_type: str):
    """Simule les effets des transformations selon les vraies mécaniques"""
    st.write("**⚔️ Simulation transformation:**")
    
    if form_type == "ours":
        # Forme ours: ignore attaque subie (défensif)
        st.write(f"• 🐻 **Forme d'Ours activée**")
        st.write(f"• 🛡️ **Effet:** Ignore la prochaine attaque subie")
        st.write(f"• ⚠️ **Usage:** Défensif - active avant de subir une attaque")
        
        if hasattr(user, 'temporary_buffs') and user.temporary_buffs.get('ignore_next_attack'):
            st.success("✅ Buff 'ignore_next_attack' actif dans temporary_buffs")
        else:
            st.warning("⚠️ Buff non détecté")
    
    elif form_type == "loup":
        # Forme loup: double dégâts prochaine attaque (offensif)
        base_damage = getattr(user, 'damage', 4)
        doubled_damage = base_damage * 2
        
        st.write(f"• 🐺 **Forme de Loup activée**")
        st.write(f"• ⚔️ **Effet:** Prochaine attaque {base_damage} → {doubled_damage} dégâts")
        st.write(f"• ⚠️ **Usage:** Offensif - active avant d'attaquer")
        
        if hasattr(user, 'temporary_buffs') and user.temporary_buffs.get('double_damage_next_attack'):
            st.success("✅ Buff 'double_damage_next_attack' actif dans temporary_buffs")
        else:
            st.warning("⚠️ Buff non détecté")
        
        # Simulation calcul dégâts doublés
        final_damage = max(0, doubled_damage - enemy.defense)
        st.write(f"• 📊 **Calcul:** {doubled_damage} (loup x2) - {enemy.defense} DEF = {final_damage} dégâts")

def _execute_ability_test(ability_instance, hero_code: str, 
                         user_max_health: int, user_current_health: int, user_spells: int, user_precision: int,
                         ally_count: int, ally_max_health: int, ally_current_health: int,
                         enemy_count: int, enemy_health_values: List[int]):
    st.subheader("🔍 Exécution du Test")
    
    try:
        _reset_ability_for_new_test(ability_instance)
        
        user, allies, enemies, combat_state = _create_test_context(
            hero_code, user_max_health, user_current_health, user_spells, user_precision,
            ally_count, ally_max_health, ally_current_health, enemy_count, enemy_health_values
        )
        
        from models.combat.spell_manager import SpellManager
        from models.combat.abilities import AbilityEffectsManager
        
        spell_manager = SpellManager()
        user.current_spells = user_spells
        spell_manager.initialize_spells(user)
        
        # 🔧 NOUVEAU: Forcer les sorts dans SpellManager ET sur le Character pour le debug
        combatant_id = spell_manager.get_combatant_id(user)
        spell_manager.combatant_spells[combatant_id] = user_spells
        # CORRECTION CRITIQUE: Synchroniser aussi le Character
        user.current_spells = user_spells
        user.__dict__['current_spells'] = user_spells
        st.info(f"🔧 DEBUG FORCE: Sorts forcés à {user_spells} dans SpellManager ET Character")

        for ally in allies:
            spell_manager.initialize_spells(ally)
        
        execution_log = []
        
        context = {
            'alive_enemies': enemies,
            'current_enemies': enemies,
            'enemies': enemies,
            'heroes': [user] + allies,
            'current_heroes': [user] + allies,
            'spell_manager': spell_manager,
            'log': execution_log,
            'player_count': len([user] + allies)
        }
        
        ability_effects_manager = AbilityEffectsManager(spell_manager)
        ability_effects_manager._current_alive_enemies = enemies
        ability_effects_manager._current_heroes = [user] + allies
        
        with st.expander("📋 Phase 1: État AVANT", expanded=True):
            st.write("**Contexte:**")
            st.write(f"- Sorts disponibles: {getattr(user, 'current_spells', user.spells)}/{ability_instance.spell_cost}")
            st.write(f"- PV utilisateur: {user.current_health}/{user.health}")
            st.write(f"- SpellManager initialisé: User sorts = {spell_manager.get_current_spells(user)}")
            
            st.write("**Context Debug:**")
            st.write(f"- Heroes: {len(context['heroes'])}")
            st.write(f"- Enemies: {len(context['alive_enemies'])}")
            
            st.write("**État AVANT exécution:**")
            _display_entities_state_enhanced(user, allies, enemies, spell_manager)
        
        with st.expander("⚡ Phase 2: Exécution", expanded=True):
            try:
                can_use, reason = spell_manager.can_use_magical_ability(user, ability_instance)
                if not can_use:
                    st.error(f"⚠️ Ne peut pas utiliser {ability_instance.name}: {reason}")
                    result = False
                else:
                    result = ability_effects_manager.apply_ability_effects(
                        user, ability_instance, execution_log, context
                    )
                    
                    if result:
                        st.success("✅ apply_ability_effects() retourné True")
                        user.action_taken_this_turn = True
                    else:
                        st.warning("⚠️ apply_ability_effects() retourné False")
                
                if execution_log:
                    st.write("**Logs d'exécution:**")
                    for log_entry in execution_log:
                        st.write(f"• {log_entry}")
                
            except Exception as e:
                st.error(f"⚠️ Erreur apply_ability_effects(): {e}")
                result = False
        
        with st.expander("🎯 Phase 3: État APRÈS", expanded=True):
            st.write("**État APRÈS exécution:**")
            _display_entities_state_enhanced(user, allies, enemies, spell_manager)
            
            st.write("**Capacité utilisée:**")
            if hasattr(ability_instance, 'uses_per_combat') and ability_instance.uses_per_combat is not None:
                remaining = getattr(ability_instance, 'uses_remaining_combat', None)
                if remaining is None:
                    remaining = getattr(ability_instance, 'uses_remaining', ability_instance.uses_per_combat)
                
                st.write(f"- **{ability_instance.name}:** {remaining}/{ability_instance.uses_per_combat} utilisations restantes")
                
                if remaining == ability_instance.uses_per_combat:
                    st.warning("⚠️ Utilisation non décomptée - vérifier l'implémentation")
            else:
                st.write(f"- **{ability_instance.name}:** Utilisations illimitées")
            
            # 🆕 NOUVEAU: Afficher les temporary_buffs après exécution
            if hasattr(user, 'temporary_buffs') and user.temporary_buffs:
                st.write("**Buffs temporaires actifs:**")
                for buff_name, buff_value in user.temporary_buffs.items():
                    if buff_value:
                        st.write(f"- **{buff_name}:** {buff_value}")
            
            # 🆕 AUTO-SIMULATION EFFETS TRANSFORMATIONS P-1
            if hero_code == "P-1" and hasattr(user, 'temporary_buffs') and user.temporary_buffs:
                if user.temporary_buffs.get('ignore_next_attack'):
                    st.write("**🐻 Simulation défense Forme d'Ours:**")
                    if enemies:
                        try:
                            # API officielle Enemy
                            enemy_damage = enemies[0].get_damage_info(2)['damage_value']
                        except (AttributeError, KeyError):
                            # Fallback debug
                            enemy_damage = getattr(enemies[0], 'damage', 3)
                        
                        st.write(f"• Ennemi attaquerait : {enemy_damage} dégâts")
                        st.write(f"• 🛡️ **Forme d'Ours :** Attaque ignorée !")
                        st.write(f"• Résultat : {user.current_health}/{user.get_total_health()} PV (inchangé)")
                    else:
                        st.write("• 🛡️ **Forme d'Ours active** : Ignore la prochaine attaque subie")
                
                if user.temporary_buffs.get('double_damage_next_attack'):
                    st.write("**🐺 Simulation attaque Forme de Loup:**")
                    if enemies:
                        base_damage = getattr(user, 'damage', 4)
                        doubled_damage = base_damage * 2
                        final_damage = max(0, doubled_damage - enemies[0].defense)
                        st.write(f"• Attaque normale : {base_damage} dégâts")
                        st.write(f"• 🐺 **Forme de Loup :** {base_damage} x2 = {doubled_damage} dégâts")
                        st.write(f"• Calcul final : {doubled_damage} - {enemies[0].defense} DEF = {final_damage} dégâts")
                    else:
                        st.write("• 🐺 **Forme de Loup active** : Double les dégâts de la prochaine attaque")
            
            if combat_state.get("logs"):
                st.write("**Logs générés:**")
                for log in combat_state["logs"]:
                    st.write(f"• {log}")
        
        st.success("🎉 Test terminé")
    
    except Exception as e:
        st.error(f"💥 Erreur critique durant test: {e}")
        st.code(traceback.format_exc())

def _simulate_bear_defense(user, enemy):
    """Teste l'effet défensif de la forme d'ours"""
    if not enemy:
        st.warning("⚠️ Aucun ennemi disponible pour simuler l'attaque")
        return
    
    st.write("**🐻 Simulation défense Forme d'Ours:**")
    
    # Calcul attaque normale de l'ennemi
    enemy_damage = enemy.get_damage_info(2)['damage_value']
    
    st.write(f"• Ennemi attaque : {enemy_damage} dégâts")
    st.write(f"• 🛡️ **Forme d'Ours :** Attaque ignorée !")
    st.write(f"• Résultat : {user.current_health}/{user.get_total_health()} PV (inchangé)")
    
    # Simulation consommation du buff
    if hasattr(user, 'temporary_buffs') and user.temporary_buffs.get('ignore_next_attack'):
        user.temporary_buffs['ignore_next_attack'] = False
        st.info("ℹ️ Buff 'ignore_next_attack' consommé (en combat réel)")

def _simulate_wolf_attack(user, enemy):
    """Teste l'effet offensif de la forme de loup"""
    if not enemy:
        st.warning("⚠️ Aucun ennemi disponible pour attaquer")
        return
    
    st.write("**🐺 Simulation attaque Forme de Loup:**")
    
    base_damage = getattr(user, 'damage', 4)
    doubled_damage = base_damage * 2
    final_damage = max(0, doubled_damage - enemy.defense)
    original_enemy_health = enemy.current_health
    
    st.write(f"• Attaque normale : {base_damage} dégâts")
    st.write(f"• 🐺 **Forme de Loup :** {base_damage} x2 = {doubled_damage} dégâts")
    st.write(f"• Calcul final : {doubled_damage} - {enemy.defense} DEF = {final_damage} dégâts")
    
    # Appliquer les dégâts
    enemy.current_health = max(0, enemy.current_health - final_damage)
    st.write(f"• Ennemi : {original_enemy_health} → {enemy.current_health} PV")
    
    # Simulation consommation du buff
    if hasattr(user, 'temporary_buffs') and user.temporary_buffs.get('double_damage_next_attack'):
        user.temporary_buffs['double_damage_next_attack'] = False
        st.info("ℹ️ Buff 'double_damage_next_attack' consommé (en combat réel)")

def _display_entities_state_enhanced(user, allies, enemies, spell_manager=None):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Utilisateur:**")
        max_health = user.get_total_health()
        current_health = min(user.current_health, max_health)
        
        if current_health <= 0:
            st.write(f"💀 **PV: {current_health}/{max_health} (INCONSCIENT)**")
        else:
            st.write(f"PV: {current_health}/{max_health}")
        
        if spell_manager:
            current_spells = spell_manager.get_current_spells(user)
            max_spells = user.get_total_spells()
        else:
            current_spells = getattr(user, 'current_spells', None) or user.get_total_spells()
            max_spells = user.get_total_spells()
            
        st.write(f"Sorts: {current_spells}/{max_spells}")
        st.write(f"Précision: {user.get_total_precision()}")
        
        base_attack = getattr(user, 'damage', 0)
        current_attack = getattr(user, 'current_attack', base_attack)
        if current_attack != base_attack:
            st.write(f"**Attaque: {current_attack}** (base: {base_attack})")
        else:
            st.write(f"Attaque: {current_attack}")
        
        current_parade = getattr(user, 'current_parade_tokens', 0)
        max_parade = getattr(user, 'max_parade_tokens', 0)
        if max_parade > 0:
            st.write(f"**Parade: {current_parade}/{max_parade}** 🛡️")
        
        if user.code == "P-1" and hasattr(user, 'current_form'):
            form_display = user.get_form_display() if hasattr(user, 'get_form_display') else user.current_form
            st.write(f"**Forme: {form_display}**")
    
    with col2:
        st.write("**Alliés:**")
        for i, ally in enumerate(allies):
            max_health = ally.get_total_health()
            current_health = min(ally.current_health, max_health)
            
            if current_health <= 0:
                st.write(f"💀 **Allié {i+1}: {current_health}/{max_health} PV (INCONSCIENT)**")
            else:
                st.write(f"Allié {i+1}: {current_health}/{max_health} PV")
            
            current_attack = getattr(ally, 'current_attack', getattr(ally, 'damage', 0))
            current_parade = getattr(ally, 'current_parade_tokens', 0)
            max_parade = getattr(ally, 'max_parade_tokens', 0)
            
            attack_display = f"ATT: {current_attack}"
            if max_parade > 0:
                attack_display += f", 🛡️{current_parade}/{max_parade}"
            
            st.write(f"  {attack_display}")
    
    with col3:
        st.write("**Ennemis:**")
        for i, enemy in enumerate(enemies):
            if enemy.current_health <= 0:
                st.write(f"💀 **Ennemi {i+1}: {enemy.current_health}/{enemy.max_health} PV (MORT)**")
            else:
                st.write(f"Ennemi {i+1}: {enemy.current_health}/{enemy.max_health} PV")
            st.write(f"  DEF: {getattr(enemy, 'defense', 0)}")

def _create_test_context(hero_code: str, user_max_health: int, user_current_health: int, user_spells: int, user_precision: int,
                        ally_count: int, ally_max_health: int, ally_current_health: int, 
                        enemy_count: int, enemy_health_values: List[int]):
    from models.character import Character, Enemy
    
    user = Character(
        code=hero_code,
        name="TestUser", 
        precision=user_precision,
        damage=4,
        spells=user_spells, 
        health=user_max_health
    )
    user.current_health = user_current_health
    user.current_spells = user_spells
    
    allies = []
    for i in range(ally_count):
        ally = Character(
            code="P-1",
            name=f"Ally{i+1}", 
            precision=6,
            damage=2, 
            spells=3,
            health=ally_max_health
        )
        ally.current_health = ally_current_health
        ally.current_spells = ally.spells
        allies.append(ally)
    
    enemies = []
    for i in range(enemy_count):
        # Utiliser la valeur PV individuelle
        individual_health = enemy_health_values[i] if i < len(enemy_health_values) else 20
        
        enemy = Enemy(
            code=f"TEST-{i+1}",
            name=f"Enemy{i+1}", 
            defense=2,
            stats_by_players={
                2: {'damage': 3, 'health': individual_health, 'defense': 1},
                3: {'damage': 3, 'health': individual_health, 'defense': 1}, 
                4: {'damage': 3, 'health': individual_health, 'defense': 1}
            },
            is_magical=False,
            has_magical_damage=False
        )
        enemy.initialize_for_combat(2)
        enemies.append(enemy)
    
    combat_state = {
        "aliases": [user] + allies,
        "enemies": enemies,
        "turn": 1,
        "logs": []
    }
    
    return user, allies, enemies, combat_state

def _get_available_heroes_data() -> Dict[str, List[Dict]]:
    try:
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        
        debug_info = ABILITY_REGISTRY.get_debug_info()
        heroes_data = {}
        
        for hero_code, hero_info in debug_info['heroes'].items():
            if hero_info['registered'] > 0:
                heroes_data[hero_code] = hero_info['abilities']
        
        return heroes_data
    
    except Exception as e:
        st.error(f"Erreur récupération héros: {e}")
        return {}

def _reset_ability_for_new_test(ability_instance):
    if not ability_instance:
        return
    
    if hasattr(ability_instance, 'uses_per_combat') and ability_instance.uses_per_combat is not None:
        ability_instance.uses_remaining_combat = ability_instance.uses_per_combat
        st.info(f"🔄 Réinitialisation {ability_instance.name}: {ability_instance.uses_remaining_combat}/{ability_instance.uses_per_combat}")
    
    if hasattr(ability_instance, 'combat_used'):
        ability_instance.combat_used = False

def _determine_targets(ability_instance, user, allies, enemies):
    ability_name = ability_instance.name.lower()
    
    if any(word in ability_name for word in ["soin", "guérison", "résurrection", "aura", "bouclier"]):
        return [user] + allies
    elif any(word in ability_name for word in ["attaque", "dégât", "châtiment", "jugement", "projectile"]):
        return enemies if enemies else [user]
    else:
        return [user] + allies + enemies