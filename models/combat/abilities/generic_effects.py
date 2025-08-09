"""
Gestionnaire des effets génériques de capacités
Effets standards réutilisables : soins, dégâts, transformations, buffs simples
"""

import random
import re
import streamlit as st
from typing import List, Dict, Any, Optional

class GenericEffectsHandler:
    """Gestionnaire des effets génériques réutilisables"""
    
    def __init__(self, spell_manager):
        self.spell_manager = spell_manager
    
    def apply_generic_effects(self, hero, ability, log: List[str]) -> bool:
        """
        Point d'entrée pour appliquer tous les effets génériques
        
        Returns:
            bool: True si des effets ont été appliqués
        """
        effects_applied = False
        
        # Ordre d'application des effets
        if self._apply_transformation_effects(hero, ability, log):
            effects_applied = True
        
        if self._apply_healing_effects(hero, ability, log):
            effects_applied = True
        
        if self._apply_damage_effects(hero, ability, log):
            effects_applied = True
        
        if self._apply_simple_buffs(hero, ability, log):
            effects_applied = True
        
        if self._apply_debuff_effects(hero, ability, log):
            effects_applied = True
        
        if self._apply_multiple_attacks(hero, ability, log):
            effects_applied = True
        
        if self._apply_special_mechanics(hero, ability, log):
            effects_applied = True
        
        return effects_applied
    
    def _apply_transformation_effects(self, hero, ability, log: List[str]) -> bool:
        """Gestion des transformations (Elneha formes)"""
        if hero.code != "P-1":
            return False
        
        if not hasattr(ability, 'ability_number'):
            return False
        
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        if ability.ability_number == 1:  # Forme d'ours
            hero.set_form("bear")
            log.append(f"  🐻 {combatant_name} se transforme en ours")
            return True
        elif ability.ability_number == 3:  # Forme de loup
            hero.set_form("wolf")
            log.append(f"  🐺 {combatant_name} se transforme en loup")
            return True
        
        return False
    
    def _apply_healing_effects(self, hero, ability, log: List[str]) -> bool:
        """Gestion des soins"""
        description = ability.description.lower()
        
        if not any(keyword in description for keyword in ['soin', 'guéri', 'blessures']):
            return False
        
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        # Extraction valeur de soin
        heal_amount = self._extract_heal_amount(description, ability.name)
        if heal_amount <= 0:
            return False
        
        # Déterminer la cible
        target_type = getattr(ability, 'target_type', 'self')
        
        if target_type == 'self' or 'self' in description:
            # Soin sur soi-même
            actual_heal = hero.heal(heal_amount)
            if actual_heal > 0:
                log.append(f"  💚 {combatant_name} récupère {actual_heal} PV")
                return True
        
        elif target_type == 'ally' or 'personnage' in description:
            # Soin sur un allié (choisir le plus blessé)
            target = self._choose_healing_target()
            if target:
                target_name = getattr(target, 'display_name', target.name)
                actual_heal = target.heal(heal_amount)
                if actual_heal > 0:
                    log.append(f"  💚 {combatant_name} soigne {target_name}: +{actual_heal} PV")
                    return True
        
        elif target_type == 'all_allies' or 'tous les personnages' in description:
            # Soin sur tous les alliés
            allies = self._get_all_allies()
            total_healed = 0
            healed_targets = []
            
            for ally in allies:
                actual_heal = ally.heal(heal_amount)
                if actual_heal > 0:
                    total_healed += actual_heal
                    ally_name = getattr(ally, 'display_name', ally.name)
                    healed_targets.append(f"{ally_name}({actual_heal})")
            
            if total_healed > 0:
                targets_str = ", ".join(healed_targets)
                log.append(f"  💚 {combatant_name} soigne l'équipe: {targets_str}")
                return True
        
        return False
    
    def _apply_damage_effects(self, hero, ability, log: List[str]) -> bool:
        """Gestion des dégâts aux ennemis"""
        description = ability.description.lower()
        
        if not any(word in description for word in ['dégât', 'inflige', 'dégâts']):
            return False
        
        # Extraction des dégâts
        damage_amount = self._extract_damage_amount(description, ability.name)
        if damage_amount <= 0:
            return False
        
        # Type de dégâts
        damage_type = "magiques" if "magique" in description else "physiques"
        
        # Récupérer les ennemis vivants
        alive_enemies = self._get_alive_enemies()
        if not alive_enemies:
            return False
        
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        # Déterminer le ciblage
        target_type = getattr(ability, 'target_type', 'enemy')
        
        if target_type == 'all_enemies' or 'tous les adversaires' in description or 'tous les ennemis' in description:
            return self._apply_aoe_damage(hero, ability, damage_amount, damage_type, alive_enemies, log)
        else:
            return self._apply_single_target_damage(hero, ability, damage_amount, damage_type, alive_enemies, log)
    
    def _apply_aoe_damage(self, hero, ability, damage: int, damage_type: str, enemies: List, log: List[str]) -> bool:
        """Applique des dégâts de zone"""
        combatant_name = getattr(hero, 'display_name', hero.name)
        log.append(f"  ⚡ {combatant_name} attaque tous les ennemis: {damage} dégâts {damage_type}")
        
        targets_hit = []
        for enemy in enemies:
            damage_result = enemy.apply_damage_with_parade(damage)
            hit_info = f"{enemy.name}({damage_result['health_damage']})"
            
            if damage_result['blocked_by_parade'] > 0:
                hit_info += f"[{damage_result['blocked_by_parade']}🛡️]"
            
            targets_hit.append(hit_info)
            
            if not enemy.is_alive():
                log.append(f"    💀 {enemy.name} vaincu !")
        
        if targets_hit:
            log.append(f"    → {', '.join(targets_hit)}")
        
        return True
    
    def _apply_single_target_damage(self, hero, ability, damage: int, damage_type: str, enemies: List, log: List[str]) -> bool:
        """Applique des dégâts sur une cible unique"""
        # Ciblage tactique selon type de capacité
        spell_cost = getattr(ability, 'spell_cost', 0)
        
        if spell_cost > 0:
            # Capacité MAGIQUE = attaque à distance = choix tactique
            target = self._choose_damage_target_tactical(enemies)
            targeting_reason = "ciblage tactique"
        else:
            # Capacité PHYSIQUE = corps à corps = premier ennemi obligatoire
            target = enemies[0]
            targeting_reason = "corps à corps"
        
        # Application des dégâts
        damage_result = target.apply_damage_with_parade(damage)
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        log.append(f"  ⚡ {combatant_name} → {target.name}: {damage} dégâts {damage_type} ({targeting_reason})")
        
        if damage_result['blocked_by_parade'] > 0:
            log.append(f"    🛡️ {damage_result['blocked_by_parade']} bloqués par parade, {damage_result['health_damage']} aux PV")
        else:
            log.append(f"    💥 {damage_result['health_damage']} aux PV")
        
        # Jetons parade restants
        if target.max_parade_tokens > 0:
            log.append(f"    🛡️ {target.name}: {target.current_parade_tokens}/{target.max_parade_tokens} jetons restants")
        
        if not target.is_alive():
            log.append(f"    💀 {target.name} vaincu !")
        
        return True
    
    def _apply_simple_buffs(self, hero, ability, log: List[str]) -> bool:
        """Gestion des buffs simples (non-persistants)"""
        description = ability.description.lower()
        combatant_name = getattr(hero, 'display_name', hero.name)
        effects_applied = False
        
        # Bonus de parade temporaire (ce tour seulement)
        if 'jeton de parade supplémentaire ce tour' in description:
            if hasattr(hero, 'max_parade_tokens'):
                hero.current_parade_tokens += 1
                log.append(f"  🛡️ {combatant_name} gagne +1 jeton parade ce tour")
                effects_applied = True
        
        # Double dégâts pour UNE attaque (non-persistant)
        if 'double les dégâts d\'une attaque' in description:
            # Marquer pour la prochaine attaque
            if not hasattr(hero, 'temporary_buffs'):
                hero.temporary_buffs = {}
            hero.temporary_buffs['double_next_attack'] = True
            log.append(f"  ⚔️ {combatant_name} - Prochaine attaque doublée")
            effects_applied = True
        
        return effects_applied
    
    def _apply_debuff_effects(self, hero, ability, log: List[str]) -> bool:
        """Gestion des debuffs sur les ennemis"""
        description = ability.description.lower()
        combatant_name = getattr(hero, 'display_name', hero.name)
        
        # Réduction d'attaque
        if 'perd' in description and 'points d\'attaque' in description:
            enemies = self._get_alive_enemies()
            if enemies:
                target = enemies[0]  # Premier ennemi pour le debuff
                reduction = self._extract_number_from_text(description, 'perd')
                
                # Marquer le debuff sur l'ennemi
                if not hasattr(target, 'debuffs'):
                    target.debuffs = {}
                target.debuffs['attack_reduction'] = reduction
                
                log.append(f"  🔻 {combatant_name} affaiblit {target.name}: -{reduction} points d'attaque")
                return True
        
        # Réduction de précision
        if 'précision est réduite' in description:
            enemies = self._get_alive_enemies()
            if enemies:
                reduction = self._extract_number_from_text(description, 'réduite de')
                affected_count = 0
                
                for enemy in enemies:
                    if not hasattr(enemy, 'debuffs'):
                        enemy.debuffs = {}
                    enemy.debuffs['precision_reduction'] = reduction
                    affected_count += 1
                
                log.append(f"  🎯 {combatant_name} réduit la précision de {affected_count} ennemis: -{reduction}")
                return True
        
        return False
    
    def _apply_multiple_attacks(self, hero, ability, log: List[str]) -> bool:
        """Gestion des attaques multiples"""
        description = ability.description.lower()
        
        if not ('attaque' in description and ('consécutive' in description or 'fois' in description)):
            return False
        
        # Extraction du nombre d'attaques
        attack_count = self._extract_attack_count(description)
        if attack_count <= 1:
            return False
        
        combatant_name = getattr(hero, 'display_name', hero.name)
        alive_enemies = self._get_alive_enemies()
        
        if not alive_enemies:
            return False
        
        log.append(f"  ⚔️ {combatant_name} effectue {attack_count} attaques consécutives")
        
        # Simuler les attaques multiples
        hits = 0
        total_damage = 0
        
        for i in range(attack_count):
            if not alive_enemies:  # Plus d'ennemis vivants
                break
            
            target = alive_enemies[0]  # Premier ennemi
            attack_roll = random.randint(1, 20)
            total_attack = attack_roll + hero.get_total_precision()
            
            if total_attack >= target.defense:
                damage = hero.get_total_damage()
                damage_result = target.apply_damage_with_parade(damage)
                
                hits += 1
                total_damage += damage_result['health_damage']
                
                log.append(f"    Attaque {i+1}: Touché! (🎲 {attack_roll}+{hero.get_total_precision()}={total_attack}) → {damage_result['health_damage']} dégâts")
                
                if not target.is_alive():
                    log.append(f"    💀 {target.name} vaincu !")
                    alive_enemies = [e for e in alive_enemies if e.is_alive()]
            else:
                log.append(f"    Attaque {i+1}: Raté (🎲 {attack_roll}+{hero.get_total_precision()}={total_attack} vs {target.defense})")
        
        # Résumé
        if hits > 0:
            log.append(f"  📊 Bilan: {hits}/{attack_count} attaques réussies, {total_damage} dégâts total")
        
        return True
    
    def _apply_special_mechanics(self, hero, ability, log: List[str]) -> bool:
        """Gestion des mécaniques spéciales génériques"""
        description = ability.description.lower()
        combatant_name = getattr(hero, 'display_name', hero.name)
        effects_applied = False
        
        # Empêcher d'agir (stun générique)
        if 'empêche d\'agir' in description or 'perdent leur action' in description:
            enemies = self._get_alive_enemies()
            if enemies:
                # Marquer les ennemis comme stunned
                stunned_count = 0
                for enemy in enemies:
                    if not hasattr(enemy, 'status_effects'):
                        enemy.status_effects = {}
                    enemy.status_effects['stunned'] = 1  # 1 tour
                    stunned_count += 1
                
                log.append(f"  😵 {combatant_name} paralyse {stunned_count} ennemis")
                effects_applied = True
        
        # Reculer d'un rang (positionnement)
        if 'reculer d\'un rang' in description:
            log.append(f"  ↩️ {combatant_name} fait reculer les ennemis")
            effects_applied = True
        
        # Effets "sans riposter"
        if 'sans qu\'il puisse riposter' in description or 'sans qu\'ils puissent riposter' in description:
            # Marquer que l'attaque ne déclenche pas de riposte
            if not hasattr(hero, 'attack_flags'):
                hero.attack_flags = {}
            hero.attack_flags['no_retaliation'] = True
            log.append(f"  🚫 {combatant_name} - Attaque sans riposte possible")
            effects_applied = True
        
        return effects_applied
    
    # === MÉTHODES UTILITAIRES ===
    
    def _extract_heal_amount(self, description: str, ability_name: str) -> int:
        """Extrait la valeur de soin depuis la description"""
        # Recherche pattern "X blessures"
        heal_match = re.search(r'(\d+)\s*blessures?', description)
        if heal_match:
            return int(heal_match.group(1))
        
        # Cas spéciaux par nom
        name_lower = ability_name.lower()
        if 'mineur' in name_lower:
            return 2
        elif 'majeur' in name_lower or 'supérieur' in name_lower:
            return 6
        elif 'multiple' in name_lower:
            return 4
        
        # Recherche autres patterns
        if 'totalité' in description or 'inconscient' in description:
            return 999  # Soin complet
        
        return 3  # Valeur par défaut
    
    def _extract_damage_amount(self, description: str, ability_name: str) -> int:
        """Extrait la valeur de dégâts depuis la description"""
        # Recherche pattern "X dégâts"
        damage_match = re.search(r'(\d+)\s*dégâts?', description)
        if damage_match:
            return int(damage_match.group(1))
        
        # Cas spéciaux
        name_lower = ability_name.lower()
        if 'brutal' in name_lower or 'critique' in name_lower:
            return 8
        elif 'tournoyante' in name_lower:
            return 3
        elif 'projectiles' in name_lower:
            return 2
        
        return 3  # Valeur par défaut
    
    def _extract_attack_count(self, description: str) -> int:
        """Extrait le nombre d'attaques multiples"""
        # Recherche "X attaques"
        attack_match = re.search(r'(\d+)\s*attaques?', description)
        if attack_match:
            return int(attack_match.group(1))
        
        # Recherche "attaquer X fois"
        fois_match = re.search(r'attaquer\s+(\w+)\s+fois', description)
        if fois_match:
            word = fois_match.group(1).lower()
            numbers = {'deux': 2, 'trois': 3, 'quatre': 4}
            return numbers.get(word, 1)
        
        return 1
    
    def _extract_number_from_text(self, text: str, context: str) -> int:
        """Extrait un nombre depuis le texte dans un contexte donné"""
        pattern = rf'{context}.*?(\d+)'
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
        return 1
    
    def _choose_healing_target(self):
        """Choisit la meilleure cible pour un soin (plus blessé)"""
        allies = self._get_all_allies()
        if not allies:
            return None
        
        # Trier par pourcentage de santé (plus blessé en premier)
        wounded_allies = []
        for ally in allies:
            if ally.is_alive() and not ally.is_at_full_health():
                health_percent = (ally.current_health / ally.get_total_health()) * 100
                wounded_allies.append((ally, health_percent))
        
        if wounded_allies:
            wounded_allies.sort(key=lambda x: x[1])  # Plus blessé en premier
            return wounded_allies[0][0]
        
        return None
    
    def _choose_damage_target_tactical(self, enemies: List):
        """Choisit la meilleure cible pour les dégâts (tactique)"""
        if len(enemies) == 1:
            return enemies[0]
        
        # Priorité aux ennemis affaiblis
        scores = []
        for enemy in enemies:
            score = 0
            health_percent = (enemy.current_health / enemy.max_health) * 100
            
            if health_percent < 30:
                score += 50  # Finir les mourants
            elif health_percent < 60:
                score += 20
            
            if getattr(enemy, 'is_magical', False):
                score += 30  # Priorité aux mages
            
            scores.append((enemy, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0]
    
    def _get_alive_enemies(self) -> List:
        """Récupère la liste des ennemis vivants"""
        current_enemies = st.session_state.get('current_enemies', [])
        return [e for e in current_enemies if e.is_alive()]
    
    def _get_all_allies(self) -> List:
        """Récupère tous les alliés (héros + pets)"""
        allies = []
        
        # Héros depuis la simulation
        heroes = st.session_state.get('current_heroes', [])
        if heroes:
            allies.extend(heroes)
        
        # Pets actifs
        active_pets = st.session_state.get('active_pets', [])
        if active_pets:
            allies.extend(active_pets)
        
        return allies
    
    def get_generic_preview(self, ability) -> Optional[str]:
        """Génère un aperçu des effets génériques d'une capacité"""
        if not ability or not hasattr(ability, 'description'):
            return None
        
        description = ability.description.lower()
        ability_name = ability.name.lower()
        effects = []
        
        # Soins
        heal_amount = self._extract_heal_amount(description, ability_name)
        if heal_amount > 0 and ('soin' in description or 'guéri' in description):
            if heal_amount == 999:
                effects.append("💚 Soin complet")
            else:
                effects.append(f"💚 Soin {heal_amount} PV")
        
        # Dégâts
        damage_amount = self._extract_damage_amount(description, ability_name)
        if damage_amount > 0 and any(word in description for word in ['dégât', 'inflige']):
            damage_type = "magiques" if "magique" in description else "physiques"
            if 'tous les adversaires' in description:
                effects.append(f"⚡ {damage_amount} dégâts {damage_type} (AoE)")
            else:
                effects.append(f"⚡ {damage_amount} dégâts {damage_type}")
        
        # Transformations
        if 'ours' in description:
            effects.append("🐻 Forme d'ours")
        elif 'loup' in description:
            effects.append("🐺 Forme de loup")
        
        # Attaques multiples
        attack_count = self._extract_attack_count(description)
        if attack_count > 1:
            effects.append(f"⚔️ {attack_count} attaques")
        
        # Buffs simples
        if 'jeton de parade' in description:
            effects.append("🛡️ +1 parade")
        if 'double les dégâts' in description:
            effects.append("⚔️ x2 dégâts")
        
        # Debuffs
        if 'perd' in description and 'attaque' in description:
            effects.append("🔻 Réduit attaque")
        if 'précision est réduite' in description:
            effects.append("🎯 Réduit précision")
        
        # Effets spéciaux
        if 'empêche d\'agir' in description:
            effects.append("😵 Stun")
        if 'sans qu\'il puisse riposter' in description:
            effects.append("🚫 Sans riposte")
        
        return " | ".join(effects) if effects else None