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
class RaishiArtMartial(BaseAbility):
    """P-8-1: Art martial - Ignore parade ennemis (permanent passif)"""

    hero_code = "P-8"
    ability_number = 1
    name = "Art martial"
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
class RaishiMeditation(BaseAbility):
    """P-8-2: Méditation - Double dégâts sur même cible après attaque"""

    hero_code = "P-8"
    ability_number = 2
    name = "Méditation"
    description = "Permet d'infliger une deuxième fois les dégâts, après une attaque réussie, sur la même cible. Les dégâts sont les mêmes que ceux de l'attaque."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 2
        self.uses_remaining_combat = 2

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Prochaine attaque inflige dégâts 2× sur même cible"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Méditation déjà utilisée ({self.uses_per_combat} fois)")
                return False

            # Ajouter buff double frappe
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            caster.temporary_buffs['meditation_double_hit'] = {
                'type': 'next_attack',
                'multiplier': 2,  # Attaque 2 fois
                'same_target': True,
                'source': 'raishi_meditation'
            }

            log.append(f"🧘 {caster.name} médite...")
            log.append(f"   💥 Prochaine attaque frappe 2× la même cible")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Méditation: {e}")
            return False

    def get_preview(self) -> str:
        return f"🧘 {self.name}: Attaque 2× même cible ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


@register_ability
class RaishiCoupCritique(BaseAbility):
    """P-8-3: Coup critique (en réalité auto-soin) - Soigne 4 PV, empêche attaque"""

    hero_code = "P-8"
    ability_number = 3
    name = "Coup critique"
    description = "Permet de soigner jusqu'à quatre de ses blessures. Ne peut être cumulé avec une attaque, si utilisé ce tour."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 1
        self.uses_remaining_combat = 1
        self.heal_amount = 4

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Soigne 4 PV sur soi-même, empêche attaque ce tour"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Coup critique déjà utilisé ce combat")
                return False

            # Soigner avec API officielle
            actual_healing = self._apply_healing(caster, self.heal_amount, log)

            # Empêcher attaque ce tour
            caster.can_attack_this_turn = False

            log.append(f"💚 {caster.name} se concentre pour se soigner")
            log.append(f"   ⚔️ Attaque bloquée ce tour")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Coup critique: {e}")
            return False

    def get_preview(self) -> str:
        return f"💚 {self.name}: Soins {self.heal_amount} PV (pas d'attaque) ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


@register_ability
class RaishiEsquiveParfaite(BaseAbility):
    """P-8-4: Esquive parfaite - Dégâts attaque sur tous ennemis"""

    hero_code = "P-8"
    ability_number = 4
    name = "Esquive parfaite"
    description = "Inflige les dégâts d'une attaque réussie sur un adversaire, à tous les ennemis."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 2
        self.uses_remaining_combat = 2

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Prochaine attaque cible TOUS les ennemis (multi-target)"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Esquive parfaite déjà utilisée ({self.uses_per_combat} fois)")
                return False

            # Ajouter buff multi-attaque
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            caster.temporary_buffs['esquive_parfaite_ready'] = {
                'type': 'multi_target',
                'applies_to': 'next_attack',
                'source': 'raishi_esquive_parfaite'
            }

            log.append(f"💫 {caster.name} prépare une Esquive parfaite !")
            log.append(f"   ⚔️ Prochaine attaque touchera TOUS les ennemis")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Esquive parfaite: {e}")
            return False

    def get_preview(self) -> str:
        return f"💫 {self.name}: Attaque multi-cible ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


@register_ability
class RaishiCombo(BaseAbility):
    """P-8-5: Combo - Stun ennemi 3 tours après attaque"""

    hero_code = "P-8"
    ability_number = 5
    name = "Combo"
    description = "Après une attaque réussie, empêche cet ennemi d'agir pendant 3 tours."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 2
        self.uses_remaining_combat = 2
        self.stun_duration = 3

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Stun un ennemi pour 3 tours (combo puissant)"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Combo déjà utilisé ({self.uses_per_combat} fois)")
                return False

            # Sélectionner ennemi cible
            enemies = self._get_all_enemies(caster, context)
            if not enemies:
                log.append(f"⚠️ Aucun ennemi pour Combo")
                return False

            # Prioriser ennemi avec plus de PV (plus rentable)
            target = max(enemies, key=lambda e: e.current_health)

            # Appliquer stun longue durée
            if not hasattr(target, 'status_effects'):
                target.status_effects = {}

            target.status_effects['stunned'] = {
                'duration': self.stun_duration,
                'source': 'raishi_combo'
            }

            log.append(f"💥🥊 {caster.name} enchaîne un COMBO sur {target.name} !")
            log.append(f"   😵 {target.name} neutralisé pour {self.stun_duration} tours")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Combo: {e}")
            return False

    def get_preview(self) -> str:
        return f"💥🥊 {self.name}: Stun ennemi {self.stun_duration} tours ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [e for e in all_enemies if self._is_alive(e)]


@register_ability
class RaishiMaitriseAbsolue(BaseAbility):
    """P-8-6: Maîtrise absolue - Absorbe 2 attaques sans dégâts permanent"""

    hero_code = "P-8"
    ability_number = 6
    name = "Maîtrise absolue"
    description = "Permet d'être ciblé par deux attaques ennemies et d'en ignorer les dégâts, pendant toute la durée du combat."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 1
        self.uses_remaining_combat = 1
        self.charges = 2

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Active bouclier - absorbe 2 attaques sans dégâts pour tout le combat"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Maîtrise absolue déjà utilisée ce combat")
                return False

            # Activer bouclier avec charges
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            caster.temporary_buffs['raishi_maitrise_charges'] = {
                'type': 'permanent_combat',
                'charges': self.charges,
                'damage_negation': True,
                'source': 'maitrise_absolue'
            }

            log.append(f"🛡️✨ {caster.name} atteint la MAÎTRISE ABSOLUE !")
            log.append(f"   💫 {self.charges} attaques seront absorbées sans dégâts")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Maîtrise absolue: {e}")
            return False

    def get_preview(self) -> str:
        return f"🛡️✨ {self.name}: Absorbe {self.charges} attaques ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]
