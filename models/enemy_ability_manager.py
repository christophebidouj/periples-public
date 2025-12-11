"""
Gestionnaire d'exécution des capacités ennemis
Applique les effets au bon moment selon les triggers
"""

from typing import List, Dict, Any, Optional
from models.enemy_ability import EnemyAbility, EnemyAbilityTrigger, EnemyAbilityEffect
from models.character import Enemy, Character
import random


class EnemyAbilityManager:
    """Gère l'exécution des capacités ennemis pendant le combat"""

    def __init__(self):
        """Initialise le gestionnaire"""
        # Note: Le compteur global n'est plus utilisé - chaque ennemi a son propre compteur individuel

    def initialize_combat(self, enemies: List[Enemy], heroes: List[Character], log: List[str]):
        """
        Initialise les capacités au début du combat
        Applique les flags permanents (immunités, blocages)

        Args:
            enemies: Liste des ennemis
            heroes: Liste des héros (nécessaire pour blocage capacités)
            log: Log de combat
        """
        for enemy in enemies:
            if hasattr(enemy, 'abilities') and enemy.abilities:
                self.execute_trigger(
                    trigger=EnemyAbilityTrigger.ON_COMBAT_START.value,
                    enemy=enemy,
                    context={'heroes': heroes, 'log': log}
                )

    def execute_trigger(self, trigger: str, enemy: Enemy, context: Dict[str, Any]):
        """
        Exécute toutes les capacités de l'ennemi qui matchent le trigger

        Args:
            trigger: Moment d'activation (on_combat_start, before_attack, etc.)
            enemy: Ennemi concerné
            context: Contexte du combat (heroes, log, etc.)
        """
        log = context.get('log', [])

        # DEBUG : Trace l'appel du trigger
        if trigger == 'on_round_start':
            log.append(f"🔍 execute_trigger appelé pour {enemy.code} {enemy.name} avec trigger '{trigger}'")

        if not hasattr(enemy, 'abilities') or not enemy.abilities:
            if trigger == 'on_round_start':
                log.append(f"🔍 → Ennemi {enemy.code} n'a PAS de capacités")
            return

        if trigger == 'on_round_start':
            log.append(f"🔍 → Ennemi {enemy.code} a {len(enemy.abilities)} capacité(s)")

        for ability in enemy.abilities:
            if ability.has_trigger(trigger) and ability.active:
                if trigger == 'on_round_start':
                    log.append(f"🔍 → Exécution de {ability.code} ({ability.name})")
                self._execute_ability(ability, enemy, context)
            elif trigger == 'on_round_start':
                log.append(f"🔍 → {ability.code} ne matche pas le trigger (triggers: {ability.triggers})")

    def _execute_ability(self, ability: EnemyAbility, enemy: Enemy, context: Dict[str, Any]):
        """
        Exécute une capacité spécifique

        Args:
            ability: Capacité à exécuter
            enemy: Ennemi concerné
            context: Contexte du combat
        """
        log = context.get('log', [])

        # Exécuter chaque effet de la capacité
        for effect in ability.effects:
            if effect == EnemyAbilityEffect.IMMUNITY_STUN.value:
                self._apply_immunity_stun(enemy, log)

            elif effect == EnemyAbilityEffect.BLOCK_HERO_ABILITIES.value:
                self._apply_block_hero_abilities(enemy, context, log)

            elif effect == EnemyAbilityEffect.EXTRA_ATTACKS.value:
                self._apply_extra_attacks(enemy, ability, log)

            elif effect == EnemyAbilityEffect.STUN_HERO_PERMANENT.value:
                self._apply_stun_hero_permanent(enemy, ability, context, log)

            elif effect == EnemyAbilityEffect.STUN_HERO_TEMPORARY.value:
                self._apply_stun_hero_temporary(enemy, ability, context, log)

            elif effect == EnemyAbilityEffect.ALTERNATING_EFFECTS.value:
                self._apply_alternating_effects(enemy, ability, context, log)

            elif effect == EnemyAbilityEffect.PERIODIC_STUN.value:
                self._apply_periodic_stun(enemy, ability, context, log)

            elif effect == EnemyAbilityEffect.PERIODIC_DAMAGE.value:
                self._apply_periodic_damage(enemy, ability, context, log)

            elif effect == EnemyAbilityEffect.ABILITY_CHECK_STUN.value:
                self._apply_ability_check_stun(enemy, ability, context, log)

    # === NIVEAU 1 - FLAGS PERMANENTS ===

    def _apply_immunity_stun(self, enemy: Enemy, log: List[str]):
        """
        Applique l'immunité au stun
        Marque l'ennemi comme immunisé dans ses status_effects
        """
        if not hasattr(enemy, 'status_effects'):
            enemy.status_effects = {}

        enemy.status_effects['immunity_stun'] = True
        log.append(f"🛡️ {enemy.name} est immunisé au Stun")

    def _apply_block_hero_abilities(self, enemy: Enemy, context: Dict[str, Any], log: List[str]):
        """
        Bloque toutes les capacités des héros
        Applique un debuff sur tous les héros présents
        """
        heroes = context.get('heroes', [])

        for hero in heroes:
            if not hasattr(hero, 'debuffs'):
                hero.debuffs = {}

            hero.debuffs['abilities_blocked'] = {
                'source': enemy.code,
                'source_name': enemy.name
            }

        log.append(f"🚫 {enemy.name} bloque toutes les capacités des héros !")

    # === NIVEAU 2 - ATTAQUES MULTIPLES ===

    def _apply_extra_attacks(self, enemy: Enemy, ability: EnemyAbility, log: List[str]):
        """
        Configure le nombre d'attaques pour ce tour
        Stocke temporairement le nombre d'attaques dans l'ennemi
        """
        num_attacks = ability.get_parameter('attacks', 2)

        # Stocker dans un attribut temporaire pour ce tour
        if not hasattr(enemy, 'current_turn_attacks'):
            enemy.current_turn_attacks = num_attacks
        else:
            enemy.current_turn_attacks = num_attacks

        log.append(f"⚡ {enemy.name} préparera {num_attacks} attaques ce tour !")

    # === NIVEAU 3 - STUN RÉCURRENT ===

    def _apply_stun_hero_permanent(self, enemy: Enemy, ability: EnemyAbility, context: Dict[str, Any], log: List[str]):
        """
        Stun un héros aléatoire jusqu'à la fin du combat
        Le héros ne peut plus agir pour le reste du combat
        """
        heroes = context.get('heroes', [])
        alive_heroes = [h for h in heroes if h.is_alive()]

        if not alive_heroes:
            return

        # Sélectionner un héros aléatoire qui n'est pas déjà stunné
        available_heroes = [
            h for h in alive_heroes
            if not (hasattr(h, 'status_effects') and h.status_effects.get('stunned'))
        ]

        if not available_heroes:
            return  # Tous les héros sont déjà stun

        target = random.choice(available_heroes)

        # Appliquer le stun permanent (RÉUTILISE structure existante 'stunned')
        if not hasattr(target, 'status_effects'):
            target.status_effects = {}

        target.status_effects['stunned'] = {
            'duration': 999,  # Valeur très élevée = permanent
            'source': enemy.code,
            'source_name': enemy.name
        }

        target_name = getattr(target, 'display_name', target.name)
        log.append(f"🔒 {enemy.name} assomme {target_name} jusqu'à la fin du combat !")

    def _apply_stun_hero_temporary(self, enemy: Enemy, ability: EnemyAbility, context: Dict[str, Any], log: List[str]):
        """
        Stun un héros aléatoire pendant N tours
        Le héros ne pourra pas agir pendant N tours
        """
        heroes = context.get('heroes', [])
        alive_heroes = [h for h in heroes if h.is_alive()]

        if not alive_heroes:
            return

        # Sélectionner un héros aléatoire
        target = random.choice(alive_heroes)

        # Durée du stun (en tours)
        duration = ability.get_parameter('duration', 1)

        # Appliquer le stun temporaire (RÉUTILISE structure existante 'stunned')
        if not hasattr(target, 'status_effects'):
            target.status_effects = {}

        target.status_effects['stunned'] = {
            'duration': duration,
            'source': enemy.code,
            'source_name': enemy.name
        }

        target_name = getattr(target, 'display_name', target.name)
        log.append(f"😵 {enemy.name} assomme {target_name} pour {duration} tour(s) !")

    # === NIVEAU 4 - EFFETS ALTERNÉS ===

    def _apply_alternating_effects(self, enemy: Enemy, ability: EnemyAbility, context: Dict[str, Any], log: List[str]):
        """
        Applique des effets qui alternent selon le numéro du tour (pair/impair)

        Format des paramètres : "even:effect:value,odd:effect:value"
        Exemples :
        - "even:damage_all:2:magical,odd:stun_temporary:1"
        - "even:stun_temporary:1,odd:damage_all:6:magical"
        """
        heroes = context.get('heroes', [])
        if not heroes:
            return

        # Récupérer les paramètres even et odd
        # Le CSV est parsé comme: {"even": "damage_all:2:magical", "odd": "stun_temporary:1"}
        even_params = ability.get_parameter('even', '')
        odd_params = ability.get_parameter('odd', '')

        if not even_params and not odd_params:
            log.append(f"⚠️ {enemy.name} - Paramètres alternating_effects manquants")
            return

        # Parser les effets pairs et impairs
        # Format: "effect:value:type" ou "effect:value"
        even_effect = even_params.split(':') if even_params else None
        odd_effect = odd_params.split(':') if odd_params else None

        # Déterminer quel effet appliquer selon le numéro du ROUND
        # Le round est partagé par tous les combattants (héros ET ennemis)
        round_number = context.get('round_number', 1)
        is_even_turn = (round_number % 2 == 0)
        effect_to_apply = even_effect if is_even_turn else odd_effect

        if not effect_to_apply:
            return

        effect_type = effect_to_apply[0]

        # Appliquer l'effet correspondant
        if effect_type == 'damage_all':
            # Dégâts à tous les héros
            damage = int(effect_to_apply[1]) if len(effect_to_apply) > 1 else 0
            damage_type = effect_to_apply[2] if len(effect_to_apply) > 2 else 'magical'

            alive_heroes = [h for h in heroes if h.is_alive()]
            if alive_heroes:
                for hero in alive_heroes:
                    hero.current_health = max(0, hero.current_health - damage)

                turn_type = "pair" if is_even_turn else "impair"
                log.append(f"💥 {enemy.name} (tour {turn_type}) inflige {damage} dégâts magiques à tous les héros !")

        elif effect_type == 'stun_temporary':
            # Stunner un héros aléatoire
            duration = int(effect_to_apply[1]) if len(effect_to_apply) > 1 else 1

            alive_heroes = [h for h in heroes if h.is_alive()]
            # Ne stunner que les héros non déjà stunnés
            available_heroes = [
                h for h in alive_heroes
                if not (hasattr(h, 'status_effects') and h.status_effects.get('stunned'))
            ]

            if available_heroes:
                import random
                target = random.choice(available_heroes)

                if not hasattr(target, 'status_effects'):
                    target.status_effects = {}

                target.status_effects['stunned'] = {
                    'duration': duration,
                    'source': enemy.code,
                    'source_name': enemy.name
                }

                target_name = getattr(target, 'display_name', target.name)
                turn_type = "pair" if is_even_turn else "impair"
                log.append(f"😵 {enemy.name} (tour {turn_type}) assomme {target_name} pour {duration} tour(s) !")

    # === NIVEAU 5 - EFFETS PÉRIODIQUES ===

    def _apply_periodic_stun(self, enemy: Enemy, ability: EnemyAbility, context: Dict[str, Any], log: List[str]):
        """
        Stun un héros aléatoire tous les N rounds pendant X tours

        Exemple: Dragon azur - Stun tous les 2 rounds pendant 1 tour
        Paramètres: interval:2,duration:1
        """
        heroes = context.get('heroes', [])
        if not heroes:
            return

        # Récupérer les paramètres
        interval = ability.get_parameter('interval', 2)  # Tous les N rounds
        duration = ability.get_parameter('duration', 1)  # Pendant X tours

        # Utiliser le round_number partagé (comme alternating_effects)
        round_number = context.get('round_number', 1)

        # Vérifier si c'est le bon round pour appliquer l'effet
        if round_number % interval != 0:
            return  # Pas le bon round

        # Sélectionner un héros aléatoire vivant qui n'est pas déjà stunné
        alive_heroes = [h for h in heroes if h.is_alive()]
        available_heroes = [
            h for h in alive_heroes
            if not (hasattr(h, 'status_effects') and h.status_effects.get('stunned'))
        ]

        if not available_heroes:
            return  # Aucun héros disponible

        import random
        target = random.choice(available_heroes)

        # Appliquer le stun
        if not hasattr(target, 'status_effects'):
            target.status_effects = {}

        target.status_effects['stunned'] = {
            'duration': duration,
            'source': enemy.code,
            'source_name': enemy.name
        }

        target_name = getattr(target, 'display_name', target.name)
        log.append(f"🌀 {enemy.name} (round {round_number}) assomme {target_name} pour {duration} tour(s) ! (périodique tous les {interval} rounds)")

    def _apply_periodic_damage(self, enemy: Enemy, ability: EnemyAbility, context: Dict[str, Any], log: List[str]):
        """
        Inflige des dégâts à tous les héros tous les N rounds

        Exemple: Dragon azur - 4 dégâts magiques tous les 3 rounds
        Paramètres: interval:3,damage:4,type:magical
        """
        heroes = context.get('heroes', [])
        if not heroes:
            return

        # Récupérer les paramètres
        interval = ability.get_parameter('interval', 3)  # Tous les N rounds
        damage = ability.get_parameter('damage', 4)      # Montant des dégâts
        damage_type = ability.get_parameter('type', 'magical')  # Type de dégâts

        # Utiliser le round_number partagé
        round_number = context.get('round_number', 1)

        # Vérifier si c'est le bon round pour appliquer l'effet
        if round_number % interval != 0:
            return  # Pas le bon round

        # Appliquer les dégâts à tous les héros vivants
        alive_heroes = [h for h in heroes if h.is_alive()]
        if not alive_heroes:
            return

        for hero in alive_heroes:
            hero.current_health = max(0, hero.current_health - damage)

        damage_emoji = "✨" if damage_type == "magical" else "⚔️"
        log.append(f"{damage_emoji} {enemy.name} (round {round_number}) inflige {damage} dégâts {damage_type}s à tous les héros ! (périodique tous les {interval} rounds)")

    # === NIVEAU 6 - CONDITIONS SPÉCIALES ===

    def _apply_ability_check_stun(self, enemy: Enemy, ability: EnemyAbility, context: Dict[str, Any], log: List[str]):
        """
        Test de capacité au début du round : D20 + niveau capacité < threshold → stun

        Exemple: Troll - Teste TOUS les héros vivants, ceux qui échouent (< 10) sont stunnés 1 tour
        Niveau de capacité = nombre de capacités débloquées (1-6, exclut capacités spéciales)
        Paramètres: threshold:10
        """
        # DEBUG : Log IMMÉDIAT pour tracer l'exécution
        log.append(f"🔍 _apply_ability_check_stun DEBUT - {enemy.name}")

        import random

        heroes = context.get('heroes', [])
        log.append(f"🔍 → {len(heroes)} héros dans le contexte")
        if not heroes:
            return

        # Récupérer le seuil (par défaut 10)
        threshold = ability.get_parameter('threshold', 10)
        log.append(f"🔍 → Seuil: {threshold}")

        # Tester TOUS les héros vivants
        alive_heroes = [h for h in heroes if h.is_alive()]
        log.append(f"🔍 → {len(alive_heroes)} héros vivants")

        if not alive_heroes:
            log.append(f"🔍 → AUCUN héros vivant, arrêt")
            return

        # Log d'introduction (format Option 1)
        log.append(f"🧌 {enemy.name} teste les capacités des héros (seuil: {threshold})...")

        # Tester chaque héros individuellement
        results = []
        log.append(f"🔍 → Début boucle test héros")

        for target in alive_heroes:
            try:
                target_name = getattr(target, 'display_name', target.name)
                log.append(f"🔍 → Test {target_name}...")

                # Lancer D20 + niveau de capacité
                d20_roll = random.randint(1, 20)
                unlocked = getattr(target, 'unlocked_abilities', [])
                # Compter SEULEMENT les capacités normales (1-6), exclure capacités spéciales (101, 102, etc.)
                ability_level = len([a for a in unlocked if 1 <= a <= 6])
                total = d20_roll + ability_level

                log.append(f"🔍   D20={d20_roll}, Niv={ability_level}, Total={total}")

                # Vérifier si le test échoue (< threshold)
                if total < threshold:
                    log.append(f"🔍   {total} < {threshold} → ÉCHEC, application stun")

                    # Appliquer le stun pour 1 tour
                    if not hasattr(target, 'status_effects'):
                        target.status_effects = {}

                    target.status_effects['stunned'] = {
                        'duration': 1,
                        'source': enemy.code,
                        'source_name': enemy.name
                    }

                    # Format: • Nom (D20: X + Niv: Y = Total) → Résultat
                    results.append(f"  • {target_name} (D20: {d20_roll} + Niv: {ability_level} = {total}) → 😵 Assommé(e) 1 tour")
                else:
                    log.append(f"🔍   {total} ≥ {threshold} → RÉUSSITE")
                    # Test réussi - pas de stun
                    results.append(f"  • {target_name} (D20: {d20_roll} + Niv: {ability_level} = {total}) → ✅ Résiste")

            except Exception as e:
                # Protection contre les erreurs
                log.append(f"⚠️ Erreur test {getattr(target, 'name', 'inconnu')}: {str(e)}")

        log.append(f"🔍 → Fin boucle, {len(results)} résultats")

        # Ajouter tous les résultats au log
        log.append(f"🔍 → Ajout des résultats au log...")
        for result in results:
            log.append(result)

        log.append(f"🔍 _apply_ability_check_stun FIN")

    # === HELPERS ===

    def reset_combat(self):
        """Reset l'état du manager pour un nouveau combat"""
        # Note: Les compteurs individuels des ennemis sont gérés dans Enemy.individual_turn_counter
        pass
