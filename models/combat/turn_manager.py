"""
Gestionnaire des tours de combat (héros, ennemis, pets)
Extrait de combat_engine.py pour modularité
"""

class TurnManager:
    """Gestion des tours de combat et IA tactique"""
    
    def __init__(self, spell_manager, combat_actions):
        self.spell_manager = spell_manager
        self.combat_actions = combat_actions
    
    def heroes_turn(self, heroes: list, enemies: list, player_count: int, log: list, active_pets: list):
        """Phase héros + Pets avec recharge parade et capacités"""
        log.append("🛡️ Phase des Héros + Pets")
        
        # Héros + Pets agissent ensemble
        all_allies = heroes + active_pets
        
        for ally in [a for a in all_allies if a.is_alive()]:
            alive_enemies = [e for e in enemies if e.is_alive()]
            if not alive_enemies:
                break
            
            # Début tour allié (recharge parade + reset capacités magiques)
            ally.start_hero_turn()
            self.spell_manager.reset_magic_abilities_turn(ally)

            if ally.max_parade_tokens > 0:
                ally_name = getattr(ally, 'display_name', ally.name)
                log.append(f"🔄 {ally_name} recharge {ally.max_parade_tokens} jetons parade")

            # NOUVEAU - Log invisibilité automatique (Lame P-7-6 Assaut furieux)
            if hasattr(ally, 'status_effects') and 'invisible' in ally.status_effects:
                if ally.status_effects['invisible'].get('source') == 'ombre_mortelle':
                    ally_name = getattr(ally, 'display_name', ally.name)
                    log.append(f"🌑 {ally_name} redevient invisible (Assaut furieux)")
            
            # Logique différente pour héros vs Pets
            if hasattr(ally, 'owner_code'):  # C'est un Pet
                self.pet_turn(ally, alive_enemies, player_count, log)
            else:  # C'est un héros
                self.hero_turn(ally, alive_enemies, player_count, log, active_pets)
    
    def hero_turn(self, hero, alive_enemies: list, player_count: int, log: list, active_pets: list):
        """Tour d'un héros avec gestion invocations et sorts conformes + logique d'action corrigée"""
        
        # Potion d'abord si nécessaire
        self.combat_actions.try_health_potion(hero, log)
        
        # Logique d'action améliorée
        action_taken = False
        
        # Tentative 1 : Capacité (peut inclure invocation)
        ability_used = self.combat_actions.try_ability_with_summon(hero, alive_enemies, log, active_pets)
        if ability_used:
            action_taken = True
        
        # Tentative 2 : Attaque si aucune action prise et autorisée
        if not action_taken:
            can_attack = not hasattr(hero, 'can_attack_this_turn') or hero.can_attack_this_turn
            
            # Vérifier si capacité magique utilisée (bloque attaque)
            combatant_id = self.spell_manager.get_combatant_id(hero)
            magic_used_this_turn = self.spell_manager.combatant_magic_abilities_this_turn.get(combatant_id, 0)
            if magic_used_this_turn > 0:
                can_attack = False
                
            if can_attack and not getattr(hero, 'action_taken_this_turn', False):
                self.combat_actions.hero_attack(hero, alive_enemies, player_count, log)
                action_taken = True
        
        # Log si aucune action possible
        if not action_taken:
            combatant_name = getattr(hero, 'display_name', hero.name)
            log.append(f"⏸️ {combatant_name} ne peut pas agir ce tour")
    
    def pet_turn(self, pet, alive_enemies: list, player_count: int, log: list):
        """Tour d'un Pet (attaque automatique simple)"""
        if alive_enemies:
            # Pet attaque automatiquement le premier ennemi
            self.combat_actions.hero_attack(pet, alive_enemies, player_count, log)
    
    def enemies_turn(self, enemies: list, heroes: list, player_count: int, log: list, active_pets: list):
        """Phase ennemis avec recharge parade - ATTAQUENT L'ÉQUIPE + Pets"""
        log.append("👹 Phase des Ennemis")
        
        for enemy in [e for e in enemies if e.is_alive()]:
            alive_heroes = [h for h in heroes if h.is_alive()]
            alive_pets = [p for p in active_pets if p.is_alive()]
            all_targets = alive_heroes + alive_pets
            
            if not all_targets:
                break
            
            # Début tour ennemi (recharge parade)
            enemy.start_enemy_turn()
            if enemy.max_parade_tokens > 0:
                log.append(f"🔄 {enemy.name} recharge {enemy.max_parade_tokens} jetons parade")
            
            # NOUVEAU - Vérifier stun avant action
            from models.combat.abilities.character_integration import CharacterAbilitiesIntegration
            status = CharacterAbilitiesIntegration.check_enemy_status_effects(enemy)
            if not status['can_act']:
                log.append(f"😵 {enemy.name} est étourdi et ne peut pas agir")
                continue  # Skip ce tour
            
            # RÈGLE OFFICIELLE : Ennemis attaquent l'équipe (héros + pets)
            enemy_stats = enemy.get_stats_for_players(player_count)
            damage = enemy_stats['damage']
            
            # Les joueurs choisissent qui prend les dégâts (héros ou pets)
            target = self.heroes_distribute_damage(all_targets, damage, enemy.name, log)

            # Application dégâts avec système parade
            # Dégâts magiques ignorent la parade (règles officielles p.26)
            ignore_parade = getattr(enemy, 'has_magical_damage', False)
            damage_result = target.apply_damage_with_parade(damage, ignore_parade=ignore_parade)

            # Log détaillé avec nom approprié
            target_name = getattr(target, 'display_name', target.name)
            damage_emoji = "✨" if ignore_parade else "⚔️"
            log_parts = [f"{damage_emoji} {enemy.name} attaque l'équipe: {damage} dégâts → {target_name}"]
            
            if damage_result['blocked_by_parade'] > 0:
                log_parts.append(f"({damage_result['blocked_by_parade']} bloqués par parade)")
                log_parts.append(f"{damage_result['health_damage']} aux PV")
            else:
                log_parts.append(f"{damage_result['health_damage']} aux PV")
            
            log.append(' '.join(log_parts))
            
            # Jetons parade restants
            if target.max_parade_tokens > 0:
                log.append(f"  🛡️ {target_name}: {target.current_parade_tokens}/{target.max_parade_tokens} jetons restants")
            
            if not target.is_alive():
                log.append(f"💀 {target_name} tombe !")
                # Retirer Pet de la liste s'il meurt
                if hasattr(target, 'owner_code') and target in active_pets:
                    active_pets.remove(target)
        
    def heroes_distribute_damage(self, heroes: list, damage: int, enemy_name: str, log: list):
        """IA qui simule la décision tactique des JOUEURS pour répartir les dégâts"""
        if len(heroes) == 1:
            return heroes[0]
        
        # Évaluation tactique - simule des joueurs intelligents
        target_scores = []
        
        for hero in heroes:
            score = 0
            health_percent = (hero.current_health / hero.get_total_health()) * 100
            
            # 1. Priorité aux héros les moins blessés (plus de PV)
            score += health_percent * 0.4
            
            # 2. Priorité aux héros avec parade disponible
            if hasattr(hero, 'current_parade_tokens') and hero.current_parade_tokens > 0:
                parade_percent = (hero.current_parade_tokens / hero.max_parade_tokens) * 100
                score += parade_percent * 0.3
            
            # 3. Bonus si le héros a des potions (peut se soigner)
            if hasattr(hero, 'can_use_potion'):
                can_heal, _ = hero.can_use_potion()
                if can_heal:
                    score += 15
            
            # 4. Malus si héros critique (< 25% PV) - éviter de le tuer
            if health_percent < 25:
                score -= 30
            
            # 5. Bonus léger si héros a beaucoup de parade max (tank)
            if hasattr(hero, 'max_parade_tokens') and hero.max_parade_tokens > 2:
                score += 10
            
            target_scores.append((hero, score))
        
        # Les joueurs choisissent le héros avec le meilleur score (le plus apte à encaisser)
        target_scores.sort(key=lambda x: x[1], reverse=True)
        chosen_hero = target_scores[0][0]
        
        return chosen_hero