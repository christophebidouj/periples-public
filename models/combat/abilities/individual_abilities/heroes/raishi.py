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
    """P-8-1: Point faible - Ignore parade ennemis (PASSIF)"""

    hero_code = "P-8"
    ability_number = 1
    name = "Point faible"
    description = "Ignore la parade des ennemis."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Capacité PASSIVE INFORMATIVE - Affiche le statut du passif."""
        # Vérifier si le passif est actif
        is_active = hasattr(caster, 'temporary_buffs') and 'ignore_parade' in caster.temporary_buffs

        if is_active:
            log.append(f"ℹ️ {caster.name} - Point faible actif (Ignore parade ennemis)")
        else:
            log.append(f"⚠️ {caster.name} - Point faible inactif (erreur d'activation)")

        return False  # Ne pas consommer d'action

    def get_preview(self) -> str:
        return f"🥋 {self.name}: PASSIF - Ignore parade ennemis permanent"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


@register_ability
class RaishiAttaquesMultiples(BaseAbility):
    """P-8-2: Attaques multiples - 2e frappe avec dégâts / 2 après attaque réussie"""

    hero_code = "P-8"
    ability_number = 2
    name = "Attaques multiples"
    description = "Après une attaque réussie, effectue une 2e frappe avec dégâts divisés par 2."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 2
        self.uses_remaining_combat = 2
        self.second_hit_multiplier = 0.5

    def requires_successful_attack(self) -> bool:
        """Cette capacité nécessite une attaque réussie ce tour"""
        return True

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Effectue une 2e frappe avec dégâts / 2 sur la dernière cible attaquée"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Attaques multiples déjà utilisée ({self.uses_per_combat} fois)")
                return False

            # CRITIQUE - Vérifier que le héros a attaqué ce tour et que la cible existe
            last_target = getattr(caster, 'last_attacked_target', None)
            if not last_target:
                log.append(f"⚠️ {caster.name} doit d'abord réussir une attaque ce tour !")
                return False

            if not last_target.is_alive():
                log.append(f"⚠️ La cible attaquée ({last_target.name}) est déjà vaincue")
                return False

            target = last_target

            # Calculer les dégâts de la 2e frappe (dégâts de base / 2)
            attack_info = caster.get_attack_damage_info()
            base_damage = attack_info['damage_value']
            damage_type = attack_info['damage_type']
            meditation_damage = int(base_damage * self.second_hit_multiplier)

            # Appliquer la 2e frappe (respecte parade)
            damage_result = target.apply_damage_with_parade(
                meditation_damage,
                ignore_parade=(damage_type == 'magical'),
                is_magical_damage=(damage_type == 'magical')
            )

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            log.append(f"🧘 {caster.name} enchaîne avec une 2e FRAPPE !")
            log.append(f"   💥 {damage_result['health_damage']} dégâts sur {target.name} (dégâts / 2)")

            if damage_result['blocked_by_parade'] > 0:
                log.append(f"   🛡️ {damage_result['blocked_by_parade']} bloqués par parade")

            if not target.is_alive():
                log.append(f"💀 {target.name} vaincu par la 2e frappe !")

            return True

        except Exception as e:
            log.append(f"❌ Erreur Attaques multiples: {e}")
            return False

    def get_preview(self) -> str:
        return f"🧘 {self.name}: 2e frappe (dégâts / 2) (après attaque) ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        """Cible la dernière cible attaquée par le héros"""
        last_target = getattr(caster, 'last_attacked_target', None)
        if last_target and last_target.is_alive():
            return [last_target]
        return [e for e in all_enemies if e.is_alive()]


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

    def requires_successful_attack(self) -> bool:
        """Cette capacité nécessite une attaque réussie ce tour"""
        return True

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Stun la dernière cible attaquée pour 3 tours"""
        try:
            from models.combat.abilities.character_integration import CharacterAbilitiesIntegration

            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ {self.name} déjà utilisé ({self.uses_per_combat} fois)")
                return False

            # CRITIQUE - Vérifier que le héros a attaqué ce tour et que la cible existe
            last_target = getattr(caster, 'last_attacked_target', None)
            if not last_target:
                log.append(f"⚠️ {caster.name} doit d'abord réussir une attaque ce tour !")
                return False

            if not last_target.is_alive():
                log.append(f"⚠️ La cible attaquée ({last_target.name}) est déjà vaincue")
                return False

            target = last_target

            # Appliquer le stun (avec vérification d'immunité)
            stunned = CharacterAbilitiesIntegration.apply_stun_with_immunity_check(
                target, duration=self.stun_duration, source='raishi_paume_ouverte', log=log
            )

            if stunned:
                log.append(f"🥋 {caster.name} frappe de sa PAUME OUVERTE {target.name} !")
                log.append(f"   💫 {target.name} assommé pour {self.stun_duration} tours")
            else:
                log.append(f"🥋 {caster.name} frappe de sa PAUME OUVERTE {target.name} !")
                log.append(f"   ⚠️ {target.name} résiste au stun (immunité)")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur {self.name}: {e}")
            return False

    def get_preview(self) -> str:
        return f"🥋 {self.name}: Stun {self.stun_duration} tours (après attaque) ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        """Cible la dernière cible attaquée par le héros"""
        last_target = getattr(caster, 'last_attacked_target', None)
        if last_target and last_target.is_alive():
            return [last_target]
        return [e for e in all_enemies if e.is_alive()]


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



# ========================================
# FONCTIONS D'AUTO-ACTIVATION (PASSIFS)
# ========================================

def auto_activate_point_faible(heroes: List, log: List[str]) -> bool:
    """
    AUTO-ACTIVATION: Active automatiquement "Point faible" pour Raishi dès le début du combat.

    Point faible est un passif permanent qui permet à Raishi d'ignorer la parade des ennemis.
    Cette capacité s'active automatiquement dès le début du combat et reste active tant que
    Raishi est vivant.

    Args:
        heroes: Liste des héros participant au combat
        log: Liste de logs de combat (sera modifiée)

    Returns:
        bool: True si le buff a été activé, False sinon

    Effet:
        Ignore la parade des ennemis lors des attaques
    """
    # Chercher Raishi (P-8) parmi les héros vivants
    raishi = next((h for h in heroes if h.code == "P-8" and h.is_alive()), None)

    if not raishi:
        return False

    # Initialiser temporary_buffs si nécessaire
    if not hasattr(raishi, 'temporary_buffs'):
        raishi.temporary_buffs = {}

    # Appliquer le buff permanent
    raishi.temporary_buffs['ignore_parade'] = {
        'type': 'passive_permanent',
        'source': 'raishi_point_faible'
    }

    # Logger l'activation
    log.append(f"🥋 Point faible de Raishi actif (Ignore parade ennemis)")

    return True
