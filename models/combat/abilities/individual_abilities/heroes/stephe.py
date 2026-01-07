# stephe.py - Capacités individuelles de Stephe (P-6) - Support/Debuffer
"""
Capacités individuelles pour le héros Stephe (P-6)
Stephe est un support spécialisé dans les debuffs ennemis, les buffs alliés et les soins.
Ses capacités se concentrent sur l'affaiblissement des ennemis et le renforcement du groupe.

✅ DONNÉES OFFICIELLES Sorts.xlsx:
P-6-1: Soin léger (Coût: 1) - Debuff -4 DEF -2 HP max ennemi (permanent)
P-6-2: Bénédiction (Coût: 1, 2/combat) - AoE stun tous ennemis 1 tour
P-6-3: Protection divine (Coût: 0, 1/combat) - +2 précision +1 dégâts tous alliés
P-6-4: Purification (Coût: 1) - Rend allié invisible (non ciblable)
P-6-5: Guérison de groupe (Coût: 2) - Soigne jusqu'à 8 PV répartis
P-6-6: Miracle (Coût: 2, 1/combat) - Kill instantané ennemi <30 HP
"""

from typing import List, Dict, Any
from ..base_ability import BaseAbility
from ..ability_registry import register_ability
from models.combat.abilities.character_integration import CharacterAbilitiesIntegration


# ========================================
# CAPACITÉS STEPHE (P-6) - SUPPORT/DEBUFFER
# ========================================

@register_ability
class StepheAffaiblissement(BaseAbility):
    """P-6-1: Affaiblissement (en réalité debuff) - Réduit DEF et HP max ennemi"""

    hero_code = "P-6"
    ability_number = 1
    name = "Affaiblissement"
    description = "Fait baisser la défense de 4 et la santé de 2, de l'ennemi ciblé pendant toute la durée du combat."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 1
        self.defense_reduction = 4
        self.health_reduction = 2

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Debuff permanent -4 DEF -2 HP max sur ennemi"""
        try:
            # Consommer coût sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False

            # Sélectionner ennemi cible (priorité PV élevés)
            enemies = self._get_all_enemies(caster, context)
            if not enemies:
                log.append(f"⚠️ Aucun ennemi à affaiblir")
                return False

            target = max(enemies, key=lambda e: e.current_health if e.current_health is not None else 0)

            # Initialiser debuffs si nécessaire
            if not hasattr(target, 'debuffs'):
                target.debuffs = {}

            # Appliquer debuff permanent défense
            target.debuffs['defense_reduction'] = self.defense_reduction
            # Modifier directement la défense de base
            target.defense = max(0, target.defense - self.defense_reduction)

            # Appliquer debuff permanent santé max
            target.debuffs['max_health_reduction'] = self.health_reduction

            # Modifier la santé max dans les stats selon les joueurs
            player_count = context.get('player_count', len(context.get('heroes', [])))
            if hasattr(target, 'stats_by_players'):
                for count, stats in target.stats_by_players.items():
                    if 'health' in stats:
                        stats['health'] = max(1, stats['health'] - self.health_reduction)

            # Ajuster max_health si présent
            if hasattr(target, 'max_health'):
                target.max_health = max(1, target.max_health - self.health_reduction)
                # Ajuster HP actuel si supérieur au nouveau max
                if hasattr(target, 'current_health') and target.current_health > target.max_health:
                    target.current_health = target.max_health

            log.append(f"🌙 {caster.name} affaiblit {target.name}")
            log.append(f"   ⬇️ Défense -{self.defense_reduction} (DEF: {target.defense}), Santé max -{self.health_reduction}")

            return True

        except Exception as e:
            log.append(f"❌ Erreur Soin léger: {e}")
            return False

    def get_preview(self) -> str:
        return f"🌙 {self.name}: -{self.defense_reduction} DEF -{self.health_reduction} HP max ennemi (Coût: {self.spell_cost})"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [e for e in all_enemies if self._is_alive(e)]


@register_ability
class StepheAccordInterdit(BaseAbility):
    """P-6-2: Accord interdit - Tous ennemis perdent action ce tour (AoE stun)"""

    hero_code = "P-6"
    ability_number = 2
    name = "Accord interdit"
    description = "Fait perdre aux adversaires leur action pour ce tour."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 1
        self.uses_per_combat = 2
        self.uses_remaining_combat = 2

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Stun AoE - Tous ennemis perdent leur action ce tour"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Bénédiction déjà utilisée ({self.uses_per_combat} fois)")
                return False

            # Consommer coût sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False

            # Appliquer stun à TOUS les ennemis
            enemies = self._get_all_enemies(caster, context)
            if not enemies:
                log.append(f"⚠️ Aucun ennemi à bénir")
                return False

            stunned_count = 0
            for enemy in enemies:
                # Effet stun (AVEC vérification immunité)
                if CharacterAbilitiesIntegration.apply_stun_with_immunity_check(
                    enemy, duration=1, source='stephe_benediction', log=log
                ):
                    stunned_count += 1

            log.append(f"✨ {caster.name} bénit le champ de bataille !")
            log.append(f"   😵 {stunned_count} ennemis perdent leur action ce tour")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Bénédiction: {e}")
            return False

    def get_preview(self) -> str:
        return f"✨ {self.name}: Stun AoE tous ennemis ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]  # Cible soi-même (effet AoE)


@register_ability
class StepheInspiration(BaseAbility):
    """P-6-3: Inspiration - +2 précision +1 dégâts tous alliés permanent"""

    hero_code = "P-6"
    ability_number = 3
    name = "Inspiration"
    description = "Fait gagner 2 de précision et 1 de dégât physique à tous les personnages pendant toute la durée du combat."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 1
        self.uses_remaining_combat = 1
        self.precision_bonus = 2
        self.damage_bonus = 1

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Buff permanent +2 précision +1 dégâts à tous les alliés"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Protection divine déjà utilisée ce combat")
                return False

            # Récupérer tous les alliés
            allies = self._get_all_allies(caster, context)
            if not allies:
                log.append(f"⚠️ Aucun allié à protéger")
                return False

            # Appliquer buff à tous les alliés
            buffed_count = 0
            for ally in allies:
                if not hasattr(ally, 'temporary_buffs'):
                    ally.temporary_buffs = {}

                ally.temporary_buffs['stephe_protection'] = {
                    'type': 'permanent_combat',
                    'precision': self.precision_bonus,
                    'damage': self.damage_bonus,
                    'source': 'protection_divine'
                }

                # Appliquer modifications directes sur current_* (utilisé par get_total_*)
                if hasattr(ally, 'current_precision'):
                    ally.current_precision += self.precision_bonus
                elif hasattr(ally, 'precision'):
                    ally.precision += self.precision_bonus

                if hasattr(ally, 'current_attack'):
                    ally.current_attack += self.damage_bonus
                elif hasattr(ally, 'damage'):
                    ally.damage += self.damage_bonus

                buffed_count += 1

            log.append(f"🛡️✨ {caster.name} invoque la Protection Divine !")
            log.append(f"   ⬆️ {buffed_count} alliés gagnent +{self.precision_bonus} précision +{self.damage_bonus} dégâts")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Protection divine: {e}")
            return False

    def get_preview(self) -> str:
        return f"🛡️✨ {self.name}: +{self.precision_bonus} PRE +{self.damage_bonus} DMG alliés ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]  # Cible soi-même (effet AoE alliés)


@register_ability
class StepheInvisibilite(BaseAbility):
    """P-6-4: Invisibilité - Rend allié invisible (ne peut être ciblé)"""

    hero_code = "P-6"
    ability_number = 4
    name = "Invisibilité"
    description = "Rend invisible l'un des personnages du groupe. Il ne peut alors plus être la cible d'une action ennemie."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 1

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Rend un allié invisible (ne peut être ciblé par ennemis)"""
        try:
            # Consommer coût sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False

            # Sélectionner allié cible (priorité plus blessé)
            allies = self._get_all_allies(caster, context)
            if not allies:
                log.append(f"⚠️ Aucun allié à purifier")
                return False

            # Prioriser allié le plus blessé (protection prioritaire)
            target = min(allies, key=lambda a: a.current_health if a.current_health is not None else float('inf'))

            # Appliquer invisibilité
            if not hasattr(target, 'status_effects'):
                target.status_effects = {}

            target.status_effects['invisible'] = {
                'type': 'untargetable',
                'duration': 'permanent_combat',  # Dure tout le combat
                'source': 'stephe_purification'
            }

            log.append(f"🌫️ {caster.name} purifie {target.name} - Invisible aux ennemis !")

            return True

        except Exception as e:
            log.append(f"❌ Erreur Purification: {e}")
            return False

    def get_preview(self) -> str:
        return f"🌫️ {self.name}: Rend allié invisible (Coût: {self.spell_cost})"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [h for h in all_heroes if self._is_alive(h)]


@register_ability
class StepheSoinMajeur(BaseAbility):
    """P-6-5: Soin majeur - Soigne jusqu'à 8 PV répartis"""

    hero_code = "P-6"
    ability_number = 5
    name = "Soin majeur"
    description = "Soigner jusqu'à 8 blessures entre les personnages."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 2
        self.max_healing = 8

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Soigne jusqu'à 8 PV répartis entre alliés blessés"""
        try:
            # Consommer coût sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False

            # Récupérer alliés blessés
            allies = self._get_all_allies(caster, context)
            wounded_allies = [a for a in allies if a.current_health is not None and a.current_health < a.get_total_health()]

            if not wounded_allies:
                log.append(f"⚠️ Aucun allié blessé à soigner")
                return False

            # Trier par PV actuels (plus blessés en premier)
            wounded_allies.sort(key=lambda a: a.current_health if a.current_health is not None else 0)

            # Répartir soins (priorité aux plus blessés)
            remaining_healing = self.max_healing
            healed_count = 0
            total_healing = 0

            log.append(f"💚 {caster.name} invoque Guérison de groupe ({self.max_healing} PV max)")

            for ally in wounded_allies:
                if remaining_healing <= 0:
                    break

                # Calculer soins nécessaires
                max_hp = ally.get_total_health()
                missing_hp = max_hp - ally.current_health
                heal_amount = min(missing_hp, remaining_healing)

                if heal_amount > 0:
                    actual_healing = self._apply_healing(ally, heal_amount, log)
                    remaining_healing -= actual_healing
                    total_healing += actual_healing
                    healed_count += 1

            log.append(f"   💖 {healed_count} alliés soignés ({total_healing} PV total)")

            return True

        except Exception as e:
            log.append(f"❌ Erreur Guérison de groupe: {e}")
            return False

    def get_preview(self) -> str:
        return f"💚 {self.name}: Soins {self.max_healing} PV répartis (Coût: {self.spell_cost})"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]  # Cible soi-même (effet AoE alliés)


@register_ability
class StepheMotDeMort(BaseAbility):
    """P-6-6: Mot de mort - Kill instantané ennemi <30 HP"""

    hero_code = "P-6"
    ability_number = 6
    name = "Mot de mort"
    description = "Utilise 2 pour tuer n'importe quel ennemi instantanément qui possède moins de 30 de santé."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 2
        self.uses_per_combat = 1
        self.uses_remaining_combat = 1
        self.hp_threshold = 30

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Kill instantané d'un ennemi ayant moins de 30 HP"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Miracle déjà utilisé ce combat")
                return False

            # Consommer coût sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False

            # Trouver ennemis éligibles (<30 HP)
            enemies = self._get_all_enemies(caster, context)
            eligible_enemies = [e for e in enemies if e.current_health is not None and e.current_health < self.hp_threshold]

            if not eligible_enemies:
                log.append(f"⚠️ Aucun ennemi <{self.hp_threshold} HP pour Miracle")
                # Ne pas décompter si aucune cible valide
                return False

            # Prioriser ennemi avec plus de PV (dans la limite)
            target = max(eligible_enemies, key=lambda e: e.current_health if e.current_health is not None else 0)

            # Kill instantané
            target.current_health = 0

            log.append(f"⚡✨ {caster.name} invoque un MIRACLE !")
            log.append(f"   💀 {target.name} est terrassé instantanément !")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Miracle: {e}")
            return False

    def get_preview(self) -> str:
        return f"⚡✨ {self.name}: Kill instantané ennemi <{self.hp_threshold} HP ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [e for e in all_enemies if self._is_alive(e) and e.current_health is not None and e.current_health < self.hp_threshold]
