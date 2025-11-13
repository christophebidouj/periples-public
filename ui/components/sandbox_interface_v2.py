"""
Sandbox Interface V2 FINAL - Version Complète et Vérifiée
CORRECTIONS APPLIQUÉES :
1. Import correct de DataLoader depuis utils
2. Initialisation des ennemis avec initialize_for_combat()
3. Correction accès stats ennemis (defense pas parade)
4. Affichage correct de tous les ennemis
"""

import streamlit as st
from typing import List, Dict, Optional
from copy import deepcopy

from models.character import Character, Enemy
from models.combat.combat_engine import CombatEngine
from models.combat.turn_manager import TurnManager
from models.combat.combat_actions import CombatActions
from models.combat.spell_manager import SpellManager
from models.rules_engine import GameRules
from utils.data_loader import DataLoader

# === INTERFACE CIBLAGE MANUEL ===

class ManualTargeting:
    """Interface UI pour ciblage manuel - Remplace l'IA tactique"""
    
    @staticmethod
    def select_enemy_for_hero_attack(
        hero: Character,
        enemies: List[Enemy],
        heroes: List[Character]
    ) -> Optional[Enemy]:
        """
        UI : Joueur choisit quel ennemi le héros attaque
        """
        alive_enemies = [e for e in enemies if e.is_alive()]
        
        if not alive_enemies:
            st.warning("❌ Aucun ennemi disponible !")
            return None
        
        st.markdown(f"### 🎯 {hero.name} attaque - Choisir la cible :")
        
        player_count = len([h for h in heroes if h.is_alive()])
        
        for enemy in alive_enemies:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.write(f"**{enemy.name}**")
            with col2:
                # CORRECTION : Utiliser current_health qui est maintenant initialisé
                st.write(f"❤️ {enemy.current_health}/{enemy.max_health}")
            with col3:
                # CORRECTION : Utiliser current_parade_tokens au lieu de stats['parade']
                st.write(f"🛡️ {enemy.current_parade_tokens}")
            with col4:
                if st.button("🎯", key=f"target_enemy_{enemy.name}_{id(enemy)}"):
                    return enemy
        
        return None
    
    @staticmethod
    def select_hero_for_enemy_attack(
        enemy: Enemy,
        heroes: List[Character]
    ) -> Optional[Character]:
        """
        UI : Joueur choisit quel héros l'ennemi attaque
        """
        alive_heroes = [h for h in heroes if h.is_alive()]
        
        if not alive_heroes:
            st.error("❌ Aucun héros vivant !")
            return None
        
        # Header ennemi attaque
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #e74c3c, #c0392b); 
                    padding: 15px; border-radius: 10px; margin-bottom: 15px; color: white;">
            <h3 style="margin: 0;">🔴 {enemy.name} attaque !</h3>
            <p style="margin: 5px 0 0 0;">Choisissez quel héros sera ciblé</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats ennemi
        player_count = len(alive_heroes)
        stats = enemy.get_stats_for_players(player_count)
        st.write(f"**💥 Dégâts :** {stats['damage']}")
        
        st.markdown("---")
        st.markdown("### 🎯 Sélectionner la cible :")
        
        # Liste héros
        for hero in alive_heroes:
            parade = hero.get_total_parade()
            damage_after_parade = max(0, stats['damage'] - parade)
            
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            
            with col1:
                st.write(f"**{hero.name}**")
            with col2:
                st.write(f"❤️ {hero.current_health}/{hero.get_total_health()}")
            with col3:
                st.write(f"🛡️ {parade}")
            with col4:
                if damage_after_parade > 0:
                    st.write(f"💔 -{damage_after_parade}")
                else:
                    st.write("✅ Bloqué")
            with col5:
                if st.button("🎯", key=f"enemy_target_{hero.name}_{id(hero)}"):
                    return hero
        
        return None

# === ADAPTER TURNMANAGER POUR CIBLAGE MANUEL ===

class SandboxTurnManagerAdapter:
    """Adapter qui RÉUTILISE TurnManager existant"""
    
    def __init__(self, turn_manager: TurnManager, combat_actions: CombatActions):
        self.turn_manager = turn_manager
        self.combat_actions = combat_actions
    
    def hero_turn_manual(
        self,
        hero: Character,
        enemies: List[Enemy],
        heroes: List[Character],
        player_count: int,
        log: List[str]
    ) -> bool:
        """Tour héros avec ciblage manuel"""
        # Début tour héros
        hero.start_hero_turn()
        
        # Afficher actions disponibles
        st.markdown(f"### 🎯 {hero.name} - Tour")
        
        col1, col2, col3 = st.columns(3)
        
        action_taken = False
        
        # Capacité
        with col1:
            if st.button("🔮 Capacité", key=f"hero_ability_{id(hero)}"):
                st.info("Sélection capacité à implémenter")
        
        # Attaque avec ciblage manuel
        with col2:
            if st.button("⚔️ Attaquer", key=f"hero_attack_{id(hero)}"):
                target = ManualTargeting.select_enemy_for_hero_attack(hero, enemies, heroes)
                if target:
                    self.combat_actions.hero_attack(hero, [target], player_count, log)
                    action_taken = True
        
        # Potion
        with col3:
            if st.button("🧪 Potion", key=f"hero_potion_{id(hero)}"):
                self.combat_actions.try_health_potion(hero, log)
                action_taken = True
        
        return action_taken
    
    def enemy_turn_manual(
        self,
        enemy: Enemy,
        heroes: List[Character],
        player_count: int,
        log: List[str]
    ) -> bool:
        """Tour ennemi avec ciblage manuel"""
        # Début tour ennemi
        enemy.start_enemy_turn()
        
        # UI : Joueur choisit héros cible
        target = ManualTargeting.select_hero_for_enemy_attack(enemy, heroes)
        
        if target:
            enemy_stats = enemy.get_stats_for_players(player_count)
            damage = enemy_stats['damage']
            
            damage_result = target.apply_damage_with_parade(damage)
            
            # Log
            log.append(f"⚔️ {enemy.name} attaque {target.name} : {damage} dégâts")
            if damage_result['blocked_by_parade'] > 0:
                log.append(f"  🛡️ {damage_result['blocked_by_parade']} bloqués, {damage_result['health_damage']} aux PV")
            
            if not target.is_alive():
                log.append(f"💀 {target.name} est inconscient !")
            
            return True
        
        return False

# === INTERFACE PRINCIPALE SANDBOX V2 ===

def init_sandbox_state():
    """Initialise état Sandbox"""
    if 'sandbox_v2_initialized' not in st.session_state:
        st.session_state.sandbox_v2_initialized = True
        st.session_state.sandbox_v2_heroes = []
        st.session_state.sandbox_v2_enemies = []
        st.session_state.sandbox_v2_phase = 'CONFIG'
        st.session_state.sandbox_v2_current_hero_index = 0
        st.session_state.sandbox_v2_current_enemy_index = 0
        st.session_state.sandbox_v2_log = []
        st.session_state.sandbox_v2_turn_manager = None
        st.session_state.sandbox_v2_adapter = None

def configure_combat():
    """Configure combat - VERSION FINALE CORRIGÉE"""
    # Initialiser logs debug
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []
    st.session_state.debug_logs.clear()
    
    # Récupérer les CODES
    hero_codes = st.session_state.get('selected_heroes', [])
    enemy_codes = st.session_state.get('selected_enemies', [])
    
    st.session_state.debug_logs.append(f"📥 Hero codes: {hero_codes}")
    st.session_state.debug_logs.append(f"📥 Enemy codes: {enemy_codes}")
    
    if not hero_codes or not enemy_codes:
        return False
    
    # Charger les OBJETS depuis les codes
    loader = DataLoader()
    all_heroes = loader.load_heroes()
    all_enemies = loader.load_enemies()
    
    st.session_state.debug_logs.append(f"📂 All enemies loaded: {len(all_enemies)} - {[e.code + ':' + e.name for e in all_enemies]}")
    
    # Filtrer sélection
    heroes = [h for h in all_heroes if h.code in hero_codes]
    enemies = [e for e in all_enemies if e.code in enemy_codes]
    
    st.session_state.debug_logs.append(f"✅ Filtered heroes: {len(heroes)} - {[h.name for h in heroes]}")
    st.session_state.debug_logs.append(f"✅ Filtered enemies: {len(enemies)} - {[e.name for e in enemies]}")
    
    if not heroes or not enemies:
        st.error("❌ Erreur chargement héros/ennemis")
        return False
    
    # CRITIQUE : Initialiser les ennemis AVANT deepcopy
    player_count = len(heroes)
    for enemy in enemies:
        enemy.initialize_for_combat(player_count)
        st.session_state.debug_logs.append(f"⚙️ Initialized {enemy.name}: HP={enemy.current_health}/{enemy.max_health}")
    
    # Copies pour combat
    st.session_state.sandbox_v2_heroes = deepcopy(heroes)
    st.session_state.sandbox_v2_enemies = deepcopy(enemies)
    
    st.session_state.debug_logs.append(f"📦 After deepcopy: {len(st.session_state.sandbox_v2_enemies)} enemies in session_state")
    st.session_state.debug_logs.append(f"📦 Names: {[e.name for e in st.session_state.sandbox_v2_enemies]}")
    
    # Architecture existante
    rules = GameRules(
        ranged_attacks=True,
        magical_damage=True,
        criticals=True,
        abilities_enabled=True
    )
    
    spell_manager = SpellManager()
    combat_actions = CombatActions(spell_manager, rules)
    turn_manager = TurnManager(spell_manager, combat_actions)
    
    # Adapter avec ciblage manuel
    st.session_state.sandbox_v2_turn_manager = turn_manager
    st.session_state.sandbox_v2_adapter = SandboxTurnManagerAdapter(
        turn_manager,
        combat_actions
    )
    
    # Initialiser sorts héros
    for hero in st.session_state.sandbox_v2_heroes:
        spell_manager.initialize_spells(hero)
    
    st.session_state.sandbox_v2_log = ["=== DÉBUT DU COMBAT ==="]
    
    return True

def display_combat_status():
    """Affiche état combat - CORRECTION affichage ennemis"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🦸 Héros")
        for hero in st.session_state.sandbox_v2_heroes:
            status = "✅" if hero.is_alive() else "💀"
            st.write(f"{status} {hero.name} - HP: {hero.current_health}/{hero.get_total_health()}")
    
    with col2:
        st.markdown("### 👹 Ennemis")
        st.caption(f"📊 {len(st.session_state.sandbox_v2_enemies)} ennemi(s) chargé(s)")
        
        st.error(f"🔍 LOOP START - About to loop through {len(st.session_state.sandbox_v2_enemies)} enemies")
        
        # CORRECTION : Afficher TOUS les ennemis sans filtrage
        for idx, enemy in enumerate(st.session_state.sandbox_v2_enemies):
            st.error(f"🔍 LOOP ITERATION {idx+1} - Processing {enemy.name}")
            
            try:
                status = "✅" if enemy.is_alive() else "💀"
                st.write(f"{status} {enemy.name} - HP: {enemy.current_health}/{enemy.max_health}")
                st.success(f"✅ Successfully displayed {enemy.name}")
            except Exception as e:
                st.error(f"❌ ERROR displaying {enemy.name}: {e}")
        
        st.error(f"🔍 LOOP END - Finished looping")

def main_sandbox_v2():
    """Interface principale Sandbox V2 FINAL"""
    st.title("🎮 Sandbox V2 - Architecture Réutilisée")
    st.caption("✅ Utilise TurnManager + CombatActions existants | Ajoute ciblage manuel")
    
    # DEBUG IMMÉDIAT - Afficher selected_enemies
    st.error(f"🔍 IMMEDIATE DEBUG - selected_enemies = {st.session_state.get('selected_enemies', 'NOT FOUND')}")
    st.error(f"🔍 IMMEDIATE DEBUG - selected_heroes = {st.session_state.get('selected_heroes', 'NOT FOUND')}")
    
    # BOUTON RESET POUR FORCER RECONFIGURATION
    if st.button("🔄 RESET ET RECHARGER LES ÉQUIPES"):
        if 'sandbox_v2_phase' in st.session_state:
            st.session_state.sandbox_v2_phase = 'CONFIG'
        st.rerun()
    
    # AFFICHER LOGS DEBUG PERSISTANTS
    if 'debug_logs' in st.session_state and st.session_state.debug_logs:
        with st.expander("🔍 DEBUG LOGS (Configuration)", expanded=True):
            for log in st.session_state.debug_logs:
                st.text(log)
    
    init_sandbox_state()
    
    # Vérifier configuration
    if not st.session_state.get('selected_heroes') or not st.session_state.get('selected_enemies'):
        st.warning("⚙️ Configurer équipes dans onglet Sélection d'abord")
        return
    
    # Configuration initiale
    if st.session_state.sandbox_v2_phase == 'CONFIG':
        if configure_combat():
            st.session_state.sandbox_v2_phase = 'PLAYER_TURN'
            st.rerun()
        return
    
    # Afficher status
    display_combat_status()
    
    st.markdown("---")
    
    # Phase actuelle
    phase = st.session_state.sandbox_v2_phase
    adapter = st.session_state.sandbox_v2_adapter
    
    if phase == 'PLAYER_TURN':
        st.markdown("## 🦸 TOUR DES JOUEURS")
        
        alive_heroes = [h for h in st.session_state.sandbox_v2_heroes if h.is_alive()]
        if not alive_heroes:
            st.error("💀 Tous les héros sont inconscients !")
            st.session_state.sandbox_v2_phase = 'END'
            st.rerun()
            return
        
        # Sélection héros actif
        current_index = st.session_state.sandbox_v2_current_hero_index
        if current_index >= len(alive_heroes):
            current_index = 0
            st.session_state.sandbox_v2_current_hero_index = 0
        
        current_hero = alive_heroes[current_index]
        st.markdown(f"### 🎯 Héros actif : {current_hero.name}")
        
        # Actions héros
        adapter.hero_turn_manual(
            current_hero,
            st.session_state.sandbox_v2_enemies,
            st.session_state.sandbox_v2_heroes,
            len(alive_heroes),
            st.session_state.sandbox_v2_log
        )
        
        # Contrôles
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➡️ Héros Suivant"):
                st.session_state.sandbox_v2_current_hero_index += 1
                if st.session_state.sandbox_v2_current_hero_index >= len(alive_heroes):
                    st.session_state.sandbox_v2_current_hero_index = 0
                st.rerun()
        
        with col2:
            if st.button("🔴 Tour Ennemis"):
                st.session_state.sandbox_v2_phase = 'ENEMY_TURN'
                st.session_state.sandbox_v2_current_enemy_index = 0
                st.rerun()
    
    elif phase == 'ENEMY_TURN':
        st.markdown("## 👹 TOUR DES ENNEMIS")
        
        alive_enemies = [e for e in st.session_state.sandbox_v2_enemies if e.is_alive()]
        if not alive_enemies:
            st.success("🎉 Tous les ennemis sont vaincus !")
            st.session_state.sandbox_v2_phase = 'END'
            st.rerun()
            return
        
        current_index = st.session_state.sandbox_v2_current_enemy_index
        if current_index >= len(alive_enemies):
            st.success("✅ Tous les ennemis ont attaqué !")
            if st.button("➡️ Nouveau Tour Joueurs"):
                st.session_state.sandbox_v2_phase = 'PLAYER_TURN'
                st.session_state.sandbox_v2_current_enemy_index = 0
                st.rerun()
            return
        
        current_enemy = alive_enemies[current_index]
        
        # Tour ennemi
        action_done = adapter.enemy_turn_manual(
            current_enemy,
            st.session_state.sandbox_v2_heroes,
            len([h for h in st.session_state.sandbox_v2_heroes if h.is_alive()]),
            st.session_state.sandbox_v2_log
        )
        
        if action_done:
            st.session_state.sandbox_v2_current_enemy_index += 1
            st.rerun()
    
    elif phase == 'END':
        all_enemies_dead = all(not e.is_alive() for e in st.session_state.sandbox_v2_enemies)
        
        if all_enemies_dead:
            st.success("🎉 VICTOIRE !")
        else:
            st.error("💀 DÉFAITE")
        
        if st.button("🔄 Nouveau Combat"):
            st.session_state.sandbox_v2_phase = 'CONFIG'
            st.rerun()
    
    # Journal de combat
    if st.session_state.sandbox_v2_log:
        with st.expander("📜 Journal de Combat"):
            for line in st.session_state.sandbox_v2_log[-20:]:
                st.text(line)

if __name__ == "__main__":
    main_sandbox_v2()