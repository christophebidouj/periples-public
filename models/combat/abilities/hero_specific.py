"""
Gestionnaire des capacités spécifiques par héros
Mécaniques uniques qui ne peuvent pas être généralisées
"""

import random
import streamlit as st
from typing import List, Dict, Any, Optional

class HeroSpecificEffects:
    """Gestionnaire des capacités spécifiques à chaque héros"""
    
    def __init__(self, spell_manager):
        self.spell_manager = spell_manager
    
    def apply_specific_ability(self, hero, ability, log: List[str]) -> bool:
        """
        Point d'entrée pour appliquer une capacité spécifique à un héros
        
        Returns:
            bool: True si la capacité a été traitée
        """
        hero_code = hero.code
        ability_name = ability.name.lower()
        
        # Dispatching par héros
        if hero_code == 'P-1':  # Elneha
            return self._handle_elneha_abilities(hero, ability, log)
        elif hero_code == 'P-2':  # Liarie
            return self._handle_liarie_abilities(hero, ability, log)
        elif hero_code == 'P-4':  # Kraor
            return self._handle_kraor_abilities(hero, ability, log)
        elif hero_code == 'P-5':  # Thordius
            return self._handle_thordius_abilities(hero, ability, log)
        elif hero_code == 'P-6':  # Stephe
            return self._handle_stephe_abilities(hero, ability, log)
        elif hero_code == 'P-7':  # Lame
            return self._handle_lame_abilities(hero, ability, log)
        elif hero_code == 'P-8':  # Raishi
            return self._handle_raishi_abilities(hero, ability, log)
        
        return False
    
    # === ELNEHA (P-1) ===
    
    def _handle_elneha_abilities(self, hero, ability, log: List[str]) -> bool:
        """Capacités spécifiques d'Elneha"""
        ability_name = ability.name.lower()
        
        # Les transformations sont déjà gérées dans generic_effects
        # Aucune capacité vraiment spécifique pour Elneha actuellement
        return False
    
    # === LIARIE (P-2) ===
    
    def _handle_liarie_abilities(self, hero, ability, log: List[str]) -> bool:
        """Capacités spécifiques de Liarie"""
        ability_name = ability.name.lower()
        
        # Armure du mage sera gérée par persistent_effects
        # Autres capacités gérées par generic_effects
        return False
    
    # === KRAOR (P-4) ===
    
    def _handle_kraor_abilities(self, hero, ability, log: List[str]) -> bool:
        """Capacités spécifiques de Kraor"""
        ability_name = ability.name.lower()
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        if 'cueilleur' in ability_name or 'chasseur' in ability_name:
            return self._kraor_cueilleur_chasseur(hero, log)
        elif 'marque du chasseur' in ability_name:
            return self._kraor_marque_chasseur(hero, log)
        elif 'ambidextre' in ability_name:
            return self._kraor_ambidextre(hero, log)
        
        return False
    
    def _kraor_cueilleur_chasseur(self, hero, log: List[str]) -> bool:
        """Capacité Cueilleur/Chasseur : Choix entre potion OU dégâts"""
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        # IA simple : choisir selon la situation
        health_percent = (hero.current_health / hero.get_total_health()) * 100
        enemies = self._get_alive_enemies()
        
        if health_percent < 50 and self._can_gain_potion(hero):
            # Priorité récupération potion si blessé
            self._gain_health_potion(hero)
            log.append(f"  🧪 {combatant_name} récolte une potion de soin")
            return True
        elif enemies:
            # Sinon attaquer à distance
            target = enemies[0]
            damage = 4  # Dégâts fixes selon description
            
            # Jet d'attaque à distance
            attack_roll = random.randint(1, 20)
            total_attack = attack_roll + hero.get_total_precision()
            
            if total_attack >= target.defense:
                damage_result = target.apply_damage_with_parade(damage)
                log.append(f"  🏹 {combatant_name} (🎲 {attack_roll}+{hero.get_total_precision()}={total_attack}) → {target.name}: {damage_result['health_damage']} dégâts à distance")
                
                if not target.is_alive():
                    log.append(f"    💀 {target.name} vaincu !")
            else:
                log.append(f"  🏹 {combatant_name} (🎲 {attack_roll}+{hero.get_total_precision()}={total_attack}) manque {target.name}")
            
            return True
        
        return False
    
    def _kraor_marque_chasseur(self, hero, log: List[str]) -> bool:
        """Capacité Marque du chasseur : Tous +2 dégâts contre ennemi marqué"""
        combatant_name = getattr(hero, 'display_name', hero.name)
        enemies = self._get_alive_enemies()
        
        if not enemies:
            return False
        
        # Choisir le meilleur ennemi à marquer (plus de PV = meilleure cible)
        target = max(enemies, key=lambda e: e.current_health)
        
        # Marquer l'ennemi
        if not hasattr(target, 'marks'):
            target.marks = {}
        target.marks['chasseur'] = {
            'bonus_damage': 2,
            'marked_by': hero.code,
            'duration': 'combat'  # Jusqu'à la fin du combat
        }
        
        log.append(f"  🎯 {combatant_name} marque {target.name}")
        log.append(f"    → Tous les personnages infligent +2 dégâts à cette cible")
        
        return True
    
    def _kraor_ambidextre(self, hero, log: List[str]) -> bool:
        """Capacité Ambidextre : Double dégâts d'UNE attaque"""
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        # Marquer pour la prochaine attaque uniquement
        if not hasattr(hero, 'temporary_buffs'):
            hero.temporary_buffs = {}
        hero.temporary_buffs['double_next_attack'] = True
        hero.temporary_buffs['ambidextre_active'] = True
        
        log.append(f"  ⚔️ {combatant_name} - Ambidextre: Prochaine attaque doublée")
        
        return True
    
    # === THORDIUS (P-5) ===
    
    def _handle_thordius_abilities(self, hero, ability, log: List[str]) -> bool:
        """Capacités spécifiques de Thordius"""
        ability_name = ability.name.lower()
        
        # Les effets persistants (rage) sont gérés par persistent_effects
        # Défense sans armure sera géré différemment
        if 'défense sans armure' in ability_name:
            return self._thordius_defense_sans_armure(hero, log)
        elif 'critique brutal' in ability_name:
            return self._thordius_critique_brutal(hero, log)
        
        return False
    
    def _thordius_defense_sans_armure(self, hero, log: List[str]) -> bool:
        """Défense sans armure : Bonus de parade permanent"""
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        # Augmenter la parade max de façon permanente
        if not hasattr(hero, 'permanent_buffs'):
            hero.permanent_buffs = {}
        
        if 'defense_sans_armure' not in hero.permanent_buffs:
            hero.max_parade_tokens += 1
            hero.permanent_buffs['defense_sans_armure'] = True
            log.append(f"  🛡️ {combatant_name} - Défense sans armure: +1 parade permanente")
            return True
        
        return False
    
    def _thordius_critique_brutal(self, hero, log: List[str]) -> bool:
        """Critique brutal : 8 dégâts sans riposter"""
        combatant_name = getattr(hero, 'display_name', hero.name)
        enemies = self._get_alive_enemies()
        
        if not enemies:
            return False
        
        target = enemies[0]  # Premier ennemi
        damage = 8
        
        # Attaque automatique (pas de jet, toujours réussit selon description)
        damage_result = target.apply_damage_with_parade(damage)
        
        log.append(f"  💥 {combatant_name} - Critique brutal → {target.name}: {damage_result['health_damage']} dégâts (sans riposte)")
        
        if damage_result['blocked_by_parade'] > 0:
            log.append(f"    🛡️ {damage_result['blocked_by_parade']} bloqués par parade")
        
        if not target.is_alive():
            log.append(f"    💀 {target.name} vaincu !")
        
        # Marquer qu'il n'y a pas de riposte
        if not hasattr(hero, 'attack_flags'):
            hero.attack_flags = {}
        hero.attack_flags['no_retaliation'] = True
        
        return True
    
    # === STEPHE (P-6) ===
    
    def _handle_stephe_abilities(self, hero, ability, log: List[str]) -> bool:
        """Capacités spécifiques de Stephe"""
        ability_name = ability.name.lower()
        
        if 'mot de mort' in ability_name:
            return self._stephe_mot_de_mort(hero, log)
        
        return False
    
    def _stephe_mot_de_mort(self, hero, log: List[str]) -> bool:
        """Mot de mort : Tue instantanément un ennemi affaibli"""
        combatant_name = getattr(hero, 'display_name', hero.name)
        enemies = self._get_alive_enemies()
        
        if not enemies:
            return False
        
        # Chercher un ennemi éligible (≤ 50% PV)
        eligible_enemies = []
        for enemy in enemies:
            health_percent = (enemy.current_health / enemy.max_health) * 100
            if health_percent <= 50:
                eligible_enemies.append((enemy, health_percent))
        
        if eligible_enemies:
            # Cibler l'ennemi le plus affaibli
            eligible_enemies.sort(key=lambda x: x[1])
            target = eligible_enemies[0][0]
            
            # Mort instantanée
            target.current_health = 0
            log.append(f"  💀 {combatant_name} - Mot de mort: {target.name} tué instantanément")
            
            return True
        else:
            log.append(f"  ❌ {combatant_name} - Mot de mort: Aucun ennemi éligible (>50% PV)")
            return True  # Capacité utilisée même si sans effet
    
    # === LAME (P-7) ===
    
    def _handle_lame_abilities(self, hero, ability, log: List[str]) -> bool:
        """Capacités spécifiques de Lame"""
        ability_name = ability.name.lower()
        
        if 'attaque furtive' in ability_name:
            return self._lame_attaque_furtive(hero, log)
        elif 'vol à la tire' in ability_name:
            return self._lame_vol_a_la_tire(hero, log)
        elif 'bombe fumigène' in ability_name:
            return self._lame_bombe_fumigene(hero, log)
        
        return False
    
    def _lame_attaque_furtive(self, hero, log: List[str]) -> bool:
        """Attaque furtive : Double dégâts sans riposter"""
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        # Marquer pour la prochaine attaque
        if not hasattr(hero, 'temporary_buffs'):
            hero.temporary_buffs = {}
        hero.temporary_buffs['double_next_attack'] = True
        hero.temporary_buffs['no_retaliation'] = True
        hero.temporary_buffs['furtive_active'] = True
        
        log.append(f"  🗡️ {combatant_name} - Attaque furtive: Prochaine attaque doublée sans riposte")
        
        return True
    
    def _lame_vol_a_la_tire(self, hero, log: List[str]) -> bool:
        """Vol à la tire : Voler potion OU infliger dégâts"""
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        # IA : Priorité potion si blessé
        health_percent = (hero.current_health / hero.get_total_health()) * 100
        
        if health_percent < 70 and self._can_gain_potion(hero):
            # Voler une potion
            self._gain_health_potion(hero)
            log.append(f"  🧪 {combatant_name} vole une potion de soin")
            return True
        else:
            # Infliger 2 dégâts
            enemies = self._get_alive_enemies()
            if enemies:
                target = enemies[0]
                damage = 2
                
                # Attaque automatique
                damage_result = target.apply_damage_with_parade(damage)
                log.append(f"  🗡️ {combatant_name} attaque sournoisement {target.name}: {damage_result['health_damage']} dégâts")
                
                if not target.is_alive():
                    log.append(f"    💀 {target.name} vaincu !")
                
                return True
        
        return False
    
    def _lame_bombe_fumigene(self, hero, log: List[str]) -> bool:
        """Bombe fumigène : Stun + réduction précision permanente"""
        combatant_name = getattr(hero, 'display_name', hero.name)
        enemies = self._get_alive_enemies()
        
        if not enemies:
            return False
        
        affected_count = 0
        
        for enemy in enemies:
            # Stun pour ce tour
            if not hasattr(enemy, 'status_effects'):
                enemy.status_effects = {}
            enemy.status_effects['stunned'] = 1
            
            # Réduction précision permanente
            if not hasattr(enemy, 'debuffs'):
                enemy.debuffs = {}
            enemy.debuffs['precision_reduction'] = 3
            
            affected_count += 1
        
        log.append(f"  💨 {combatant_name} - Bombe fumigène: {affected_count} ennemis paralysés")
        log.append(f"    → -3 précision permanente pour tous")
        
        return True
    
    # === RAISHI (P-8) ===
    
    def _handle_raishi_abilities(self, hero, ability, log: List[str]) -> bool:
        """Capacités spécifiques de Raishi"""
        ability_name = ability.name.lower()
        
        if 'point faible' in ability_name:
            return self._raishi_point_faible(hero, log)
        
        # Zui quan est géré par persistent_effects
        return False
    
    def _raishi_point_faible(self, hero, log: List[str]) -> bool:
        """Point faible : +3 dégâts pour UNE attaque sans riposter"""
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        # Marquer pour la prochaine attaque
        if not hasattr(hero, 'temporary_buffs'):
            hero.temporary_buffs = {}
        hero.temporary_buffs['damage_bonus_next_attack'] = 3
        hero.temporary_buffs['no_retaliation'] = True
        hero.temporary_buffs['point_faible_active'] = True
        
        log.append(f"  🎯 {combatant_name} - Point faible: Prochaine attaque +3 dégâts sans riposte")
        
        return True
    
    # === MÉTHODES UTILITAIRES ===
    
    def _get_alive_enemies(self) -> List:
        """Récupère la liste des ennemis vivants"""
        current_enemies = st.session_state.get('current_enemies', [])
        return [e for e in current_enemies if e.is_alive()]
    
    def _can_gain_potion(self, hero) -> bool:
        """Vérifie si le héros peut gagner une potion"""
        if not hasattr(hero, 'health_potions'):
            return True
        
        # Limite arbitraire de 3 potions max
        total_potions = sum(potion.quantity for potion in hero.health_potions)
        return total_potions < 3
    
    def _gain_health_potion(self, hero):
        """Ajoute une potion de soin au héros"""
        from models.character import HealthPotion, PotionType
        
        if not hasattr(hero, 'health_potions'):
            hero.health_potions = []
        
        # Chercher une petite potion existante
        for potion in hero.health_potions:
            if potion.potion_type == PotionType.SMALL:
                potion.quantity += 1
                return
        
        # Créer une nouvelle petite potion
        new_potion = HealthPotion(potion_type=PotionType.SMALL, quantity=1)
        hero.health_potions.append(new_potion)
    
    def get_specific_preview(self, ability) -> Optional[str]:
        """Génère un aperçu pour les capacités spécifiques"""
        if not ability or not hasattr(ability, 'name'):
            return None
        
        ability_name = ability.name.lower()
        
        # Previews spécifiques
        if 'cueilleur' in ability_name or 'chasseur' in ability_name:
            return "🏹 Potion OU 4 dégâts distance"
        elif 'marque du chasseur' in ability_name:
            return "🎯 Marque: +2 dégâts pour tous"
        elif 'ambidextre' in ability_name:
            return "⚔️ x2 dégâts prochaine attaque"
        elif 'défense sans armure' in ability_name:
            return "🛡️ +1 parade permanente"
        elif 'critique brutal' in ability_name:
            return "💥 8 dégâts sans riposte"
        elif 'mot de mort' in ability_name:
            return "💀 Tue si <50% PV"
        elif 'attaque furtive' in ability_name:
            return "🗡️ x2 dégâts sans riposte"
        elif 'vol à la tire' in ability_name:
            return "🧪 Potion OU 2 dégâts"
        elif 'bombe fumigène' in ability_name:
            return "💨 Stun + -3 précision permanent"
        elif 'point faible' in ability_name:
            return "🎯 +3 dégâts sans riposte"
        
        return None