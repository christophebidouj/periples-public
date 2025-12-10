# raishi.py - Capacités individuelles de Raishi (P-8) - Moine
"""
Capacités individuelles pour le héros Raishi (P-8)
Raishi est un moine spécialisé dans les arts martiaux, la défense parfaite et les combos.
Ses capacités se concentrent sur la précision, l'esquive et les enchaînements.

✅ DONNÉES OFFICIELLES Sorts.xlsx:
P-8-1: Art martial (Coût: 0) - Ignore parade ennemis (permanent passif)
P-8-2: Méditation (Coût: 0, 2/combat) - Double dégâts sur même cible après attaque
P-8-3: Coup critique (Coût: 0, 1/combat) - Soigne 4 PV, empêche attaque ce tour
P-8-4: Esquive parfaite (Coût: 0, 2/combat) - Dégâts attaque sur tous ennemis
P-8-5: Combo (Coût: 0, 2/combat) - Stun ennemi 3 tours après attaque
P-8-6: Maîtrise absolue (Coût: 0, 1/combat) - Absorbe 2 attaques sans dégâts
"""

from typing import List, Dict, Any
from ..base_ability import BaseAbility
from ..ability_registry import register_ability


# ========================================
# CAPACITÉS RAISHI (P-8) - MOINE
# ========================================

@register_ability
class RaishiPointFaible(BaseAbility):
    """P-8-1: Point faible - Ignore parade ennemis (permanent passif)"""

    hero_code = "P-8"
    ability_number = 1
    name = "Point faible"
    description = "Ignore la parade des ennemis."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Active capacité passive - ignore parade ennemis pour tout le combat"""
        try:
            # Ajouter buff permanent
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            # Vérifier si déjà actif
            if 'ignore_parade' in caster.temporary_buffs:
                log.append(f"⚠️ Art martial déjà actif")
                return False

            caster.temporary_buffs['ignore_parade'] = {
                'type': 'permanent_combat',
                'source': 'raishi_art_martial'
            }

            log.append(f"🥋 {caster.name} maîtrise l'Art martial !")
            log.append(f"   🎯 Ignore la parade des ennemis (permanent)")

            return True

        except Exception as e:
            log.append(f"❌ Erreur Art martial: {e}")
            return False

    def get_preview(self) -> str:
        return f"🥋 {self.name}: Ignore parade ennemis permanent (Gratuit)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


@register_ability
class RaishiAttaquesMultiples(BaseAbility):
    """P-8-2: Attaques multiples - Dégâts x1.5 sur prochaine attaque"""

    hero_code = "P-8"
    ability_number = 2
    name = "Attaques multiples"
    description = "La prochaine attaque inflige 150% des dégâts normaux (×1.5)."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 2
        self.uses_remaining_combat = 2
        self.damage_multiplier = 1.5

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Prochaine attaque inflige x1.5 dégâts"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Méditation déjà utilisée ({self.uses_per_combat} fois)")
                return False

            # Ajouter buff multiplicateur de dégâts
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            caster.temporary_buffs['meditation_damage_boost'] = {
                'type': 'next_attack',
                'damage_multiplier': self.damage_multiplier,
                'source': 'raishi_meditation'
            }

            log.append(f"🧘 {caster.name} médite profondément...")
            log.append(f"   💥 Prochaine attaque: dégâts ×{self.damage_multiplier}")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Méditation: {e}")
            return False

    def get_preview(self) -> str:
        return f"🧘 {self.name}: Dégâts ×{self.damage_multiplier} ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


@register_ability
class RaishiPurification(BaseAbility):
    """P-8-3: Purification (AUTO-SOIN UNIQUEMENT) - Soigne 4 PV sur soi-même, empêche attaque"""

    hero_code = "P-8"
    ability_number = 3
    name = "Purification"
    description = "Permet de soigner jusqu'à quatre de ses blessures. Ne peut être cumulé avec une attaque, si utilisé ce tour."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 1
        self.uses_remaining_combat = 1
        self.heal_amount = 4

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Soigne 4 PV sur soi-même UNIQUEMENT (ne peut pas soigner les autres), empêche attaque ce tour"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Coup critique déjà utilisé ce combat")
                return False

            # IMPORTANT: AUTO-SOIN UNIQUEMENT - ignore les targets, soigne toujours le caster
            # Cette capacité ne peut PAS soigner d'autres héros, seulement Raishi
            actual_healing = self._apply_healing(caster, self.heal_amount, log)

            # Empêcher attaque ce tour
            caster.can_attack_this_turn = False

            log.append(f"💚 {caster.name} se concentre pour se soigner (auto-soin uniquement)")
            log.append(f"   ⚔️ Attaque bloquée ce tour")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Coup critique: {e}")
            return False

    def get_preview(self) -> str:
        return f"💚 {self.name}: Auto-soin {self.heal_amount} PV (pas d'attaque) ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        # AUTO-CIBLAGE UNIQUEMENT - retourne toujours le caster (Raishi ne peut soigner que lui-même)
        return [caster]


@register_ability
class RaishiDelugeDeCups(BaseAbility):
    """P-8-4: Déluge de coups - 1 jet de toucher, si réussi applique sur tous ennemis"""

    hero_code = "P-8"
    ability_number = 4
    name = "Déluge de coups"
    description = "Un seul jet de toucher est effectué. Si l'attaque réussit, les dégâts sont appliqués à tous les ennemis."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 2
        self.uses_remaining_combat = 2

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Prochaine attaque: 1 seul jet de toucher, si réussi applique dégâts à TOUS les ennemis"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Esquive parfaite déjà utilisée ({self.uses_per_combat} fois)")
                return False

            # Ajouter buff multi-attaque avec jet unique
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            caster.temporary_buffs['esquive_parfaite_ready'] = {
                'type': 'multi_target',
                'applies_to': 'next_attack',
                'single_roll': True,  # NOUVEAU: 1 seul jet pour tous les ennemis
                'source': 'raishi_esquive_parfaite'
            }

            log.append(f"💫 {caster.name} prépare une Esquive parfaite !")
            log.append(f"   ⚔️ 1 jet de toucher → Si réussi: dégâts sur TOUS les ennemis")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Esquive parfaite: {e}")
            return False

    def get_preview(self) -> str:
        return f"💫 {self.name}: 1 jet → tous ennemis ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


@register_ability
class RaishiPaumeOuverte(BaseAbility):
    """P-8-5: Paume ouverte - Stun ennemi 3 tours après attaque"""

    hero_code = "P-8"
    ability_number = 5
    name = "Paume ouverte"
    description = "Après une attaque réussie, empêche cet ennemi d'agir pendant 3 tours."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 2
        self.uses_remaining_combat = 2
        self.stun_duration = 3

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Active Paume ouverte - Prochaine attaque réussie assomme l'ennemi 3 tours"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ {self.name} déjà utilisé ({self.uses_per_combat} fois)")
                return False

            # Ajouter buff pour prochaine attaque
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            caster.temporary_buffs['combo_ready'] = {
                'type': 'next_attack',
                'stun_duration': self.stun_duration,
                'source': 'raishi_paume_ouverte'
            }

            log.append(f"🥋 {caster.name} active {self.name} !")
            log.append(f"   ⚡ Prochaine attaque réussie assomme l'ennemi {self.stun_duration} tours")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Combo: {e}")
            return False

    def get_preview(self) -> str:
        return f"💥🥊 {self.name}: Prochaine attaque stun {self.stun_duration} tours ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


@register_ability
class RaishiZuiQuan(BaseAbility):
    """P-8-6: Zui quan - Absorbe 2 attaques par tour (recharge automatique)"""

    hero_code = "P-8"
    ability_number = 6
    name = "Zui quan"
    description = "Ignore les dégâts de 2 attaques ennemies par tour (recharge automatique chaque tour), pendant toute la durée du combat."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 1
        self.uses_remaining_combat = 1
        self.charges_per_turn = 2

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Active bouclier permanent - absorbe 2 attaques par tour (auto-recharge)"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Maîtrise absolue déjà utilisée ce combat")
                return False

            # Activer bouclier avec recharge automatique
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            caster.temporary_buffs['raishi_maitrise_charges'] = {
                'type': 'permanent_combat',
                'charges': self.charges_per_turn,
                'max_charges': self.charges_per_turn,  # NOUVEAU: Pour recharge auto
                'auto_recharge': True,  # NOUVEAU: Indicateur de recharge par tour
                'damage_negation': True,
                'source': 'maitrise_absolue'
            }

            log.append(f"🛡️✨ {caster.name} atteint la MAÎTRISE ABSOLUE !")
            log.append(f"   💫 Ignore {self.charges_per_turn} attaques par tour (permanent, auto-recharge)")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Maîtrise absolue: {e}")
            return False

    def get_preview(self) -> str:
        return f"🛡️✨ {self.name}: Ignore {self.charges_per_turn} attaques/tour ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]
