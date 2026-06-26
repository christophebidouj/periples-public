# barbare.py - Capacités individuelles de Barbare (P-5) - Guerrier Berserker
"""
Capacités individuelles pour le héros Barbare (P-5)
Barbare est un guerrier berserker spécialisé dans les dégâts physiques bruts et la rage.
Ses capacités se concentrent sur l'augmentation de puissance et la survie en rage.

✅ DONNÉES OFFICIELLES Sorts.xlsx:
P-5-1: Coup de rage (Coût: 0) - +2 parade si pas d'armure/bouclier
P-5-2: Charge (Coût: 0, 1/combat) - +3 dégâts physiques permanent
P-5-3: Intimidation (Coût: 0, 2/combat) - Stun ennemi après attaque
P-5-4: Frappe puissante (Coût: 0) - Convertit parade en bonus dégâts
P-5-5: Cri de guerre (Coût: 0) - Critiques sur 18-19-20
P-5-6: Berserker (Coût: 0, 1/combat) - Continue à combattre même inconscient
"""

from typing import List, Dict, Any
from ..base_ability import BaseAbility
from ..ability_registry import register_ability
from models.combat.abilities.character_integration import CharacterAbilitiesIntegration


# ========================================
# CAPACITÉS BARBARE (P-5) - GUERRIER BERSERKER
# ========================================

@register_ability
class BarbareDefenseSansArmure(BaseAbility):
    """P-5-1: Défense sans armure - PASSIF : +2 parade permanents si pas d'armure/bouclier équipé"""

    hero_code = "P-5"
    ability_number = 1
    name = "Défense sans armure"
    description = "2 en parade si aucune armure ou bouclier n'est équipé"

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.parade_bonus = 2

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """
        Capacité PASSIVE INFORMATIVE - Affiche le statut du passif.
        Le buff est appliqué automatiquement au début du combat par auto_activate_defense_sans_armure().
        Cette fonction sert uniquement à informer l'utilisateur.
        """
        try:
            # Vérifier si le passif est actif
            is_active = False
            if hasattr(caster, 'temporary_buffs') and 'defense_sans_armure_active' in caster.temporary_buffs:
                is_active = True

            # Vérifier équipement pour afficher les raisons
            has_armor_or_shield = False
            if hasattr(caster, 'equipment') and caster.equipment:
                for item in caster.equipment:
                    if hasattr(item, 'type') and item.type == 'armure':
                        has_armor_or_shield = True
                        break

            # Afficher le statut
            if is_active:
                log.append(f"💪 PASSIF ACTIF : Défense sans armure (+{self.parade_bonus} jetons de parade permanents)")
                log.append(f"  ℹ️ Ce bonus est appliqué automatiquement au début du combat")
                if hasattr(caster, 'max_parade_tokens'):
                    log.append(f"  🛡️ Jetons de parade max: {caster.max_parade_tokens}")
            else:
                if has_armor_or_shield:
                    log.append(f"⚠️ PASSIF INACTIF : {caster.name} porte une armure/bouclier")
                    log.append(f"  ℹ️ Retirez votre armure pour activer ce bonus permanent (+{self.parade_bonus} parade)")
                else:
                    log.append(f"⚠️ PASSIF INACTIF : Défense sans armure non activée")

            # Retourner False pour ne pas consommer d'action
            return False

        except Exception as e:
            log.append(f"❌ Erreur Défense sans armure: {e}")
            return False

    def get_preview(self) -> str:
        return f"💪 {self.name} [PASSIF]: +{self.parade_bonus} parade permanents (Info)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]  # Cible soi-même


@register_ability
class BarbareRageDeBerserker(BaseAbility):
    """P-5-2: Rage de berserker - +3 dégâts physiques permanent pour le combat"""

    hero_code = "P-5"
    ability_number = 2
    name = "Rage de berserker"
    description = "Plus 3 dégâts physique, pendant la durée du combat."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 1
        self.uses_remaining_combat = 1
        self.damage_bonus = 3

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Accorde +3 dégâts physiques permanent pour tout le combat"""
        try:
            # Initialiser temporary_buffs si nécessaire
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            # CORRECTION : Vérifier limitation via temporary_buffs (persiste avec undo/redo)
            if caster.temporary_buffs.get('barbare_rage_used', False):
                log.append(f"⚠️ Rage de berserker déjà utilisée ce combat")
                return False

            # Ajouter buff permanent de dégâts
            caster.temporary_buffs['barbare_charge_damage'] = {
                'type': 'permanent_combat',
                'damage_bonus': self.damage_bonus,
                'source': 'rage_berserker'
            }

            # Appliquer bonus dégâts directement sur current_attack
            if hasattr(caster, 'current_attack'):
                caster.current_attack += self.damage_bonus
            elif hasattr(caster, 'damage'):
                caster.damage += self.damage_bonus

            log.append(f"⚡ {caster.name} entre en RAGE DE BERSERKER ! (+{self.damage_bonus} dégâts permanent)")

            # CORRECTION : Marquer comme utilisée via temporary_buffs (persiste avec undo/redo)
            caster.temporary_buffs['barbare_rage_used'] = True

            # Décompter utilisation (pour l'affichage dans le preview)
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Rage de berserker: {e}")
            return False

    def get_preview(self) -> str:
        return f"⚡ {self.name}: +{self.damage_bonus} dégâts permanent ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


@register_ability
class BarbareChargeDeTaureau(BaseAbility):
    """P-5-3: Charge de taureau - Stun ennemi après attaque réussie"""

    hero_code = "P-5"
    ability_number = 3
    name = "Charge de taureau"
    description = "Après une attaque réussie, bloque l'action de cet ennemi."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 2
        self.uses_remaining_combat = 2
        self.stun_duration = 1

    def requires_successful_attack(self) -> bool:
        """Cette capacité nécessite une attaque réussie ce tour"""
        return True

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Stun la dernière cible attaquée pour 1 tour"""
        try:
            from models.combat.abilities.character_integration import CharacterAbilitiesIntegration

            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Charge de taureau déjà utilisée ({self.uses_per_combat} fois)")
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
                target, duration=self.stun_duration, source='barbare_charge_taureau', log=log
            )

            if stunned:
                log.append(f"🐂 {caster.name} CHARGE {target.name} !")
                log.append(f"   💫 {target.name} assommé pour {self.stun_duration} tour")
            else:
                log.append(f"🐂 {caster.name} CHARGE {target.name} !")
                log.append(f"   ⚠️ {target.name} résiste au stun (immunité)")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Charge de taureau: {e}")
            return False

    def get_preview(self) -> str:
        return f"🐂 {self.name}: Stun {self.stun_duration} tour (après attaque) ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        """Cible la dernière cible attaquée par le héros"""
        last_target = getattr(caster, 'last_attacked_target', None)
        if last_target and last_target.is_alive():
            return [last_target]
        return [e for e in all_enemies if e.is_alive()]


@register_ability
class BarbareTemerité(BaseAbility):
    """P-5-4: Témérité - Convertit parade en bonus dégâts"""

    hero_code = "P-5"
    ability_number = 4
    name = "Témérité"
    description = "Permet de convertir son score de parade, en bonus de dégâts. La parade ne peut pas être utilisée pendant ce tour."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Convertit parade actuelle en bonus dégâts pour prochaine attaque"""
        try:
            # Récupérer parade actuelle (current_parade_tokens ou current_defense)
            current_parade = 0
            if hasattr(caster, 'current_parade_tokens'):
                current_parade = caster.current_parade_tokens
            elif hasattr(caster, 'current_defense'):
                current_parade = caster.current_defense
            elif hasattr(caster, 'defense'):
                current_parade = caster.defense

            if current_parade <= 0:
                log.append(f"⚠️ {caster.name} n'a pas de parade à convertir")
                return False

            # Ajouter bonus dégâts pour prochaine attaque (utilise système existant)
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            caster.temporary_buffs['damage_bonus_next_attack'] = current_parade

            # Retirer parade temporairement
            if hasattr(caster, 'current_parade_tokens'):
                caster.current_parade_tokens = 0
            if hasattr(caster, 'current_defense'):
                caster.current_defense = 0

            # Marquer qu'on ne peut pas utiliser parade ce tour
            caster.temporary_buffs['frappe_puissante_active'] = {
                'parade_converted': current_parade,
                'duration': 1
            }

            log.append(f"💥 {caster.name} convertit {current_parade} parade en bonus dégâts !")

            return True

        except Exception as e:
            log.append(f"❌ Erreur Frappe puissante: {e}")
            return False

    def get_preview(self) -> str:
        return f"💥 {self.name}: Convertit parade en dégâts (Gratuit)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


@register_ability
class BarbareCritiqueBrutal(BaseAbility):
    """P-5-5: Critique brutal - Critiques sur 18-19-20 au lieu de 20 seul (PASSIF)"""

    hero_code = "P-5"
    ability_number = 5
    name = "Critique brutal"
    description = "Les 18 & 19 sur le jet de dé, sont également des réussites critiques."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Capacité PASSIVE INFORMATIVE - Affiche le statut du passif."""
        # Vérifier si le passif est actif
        is_active = hasattr(caster, 'temporary_buffs') and 'expanded_crit_range' in caster.temporary_buffs

        if is_active:
            log.append(f"ℹ️ {caster.name} - Critique brutal actif (Critiques: 18-19-20)")
        else:
            log.append(f"⚠️ {caster.name} - Critique brutal inactif (erreur d'activation)")

        return False  # Ne pas consommer d'action

    def get_preview(self) -> str:
        return f"🔥 {self.name}: PASSIF - Critiques 18-19-20 permanent"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


@register_ability
class BarbareRageInsatiable(BaseAbility):
    """P-5-6: Rage insatiable - Continue à combattre même inconscient"""

    hero_code = "P-5"
    ability_number = 6
    name = "Rage insatiable"
    description = "Tant qu'il est en rage, Barbare continue de combattre même s'il atteint le maximum de points de blessures."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 1
        self.uses_remaining_combat = 1

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Active le mode Berserker - permet de combattre même inconscient"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Berserker déjà utilisé ce combat")
                return False

            # Activer mode berserker
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            # Déverrouiller la capacité de rage (bouton apparaîtra dans l'interface)
            caster.temporary_buffs['berserker_unlocked'] = True

            # Activer rage par défaut
            caster.temporary_buffs['berserker_rage_active'] = True

            log.append(f"🔥💀 {caster.name} entre en MODE BERSERKER ! (Continue même inconscient)")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Berserker: {e}")
            return False

    def get_preview(self) -> str:
        return f"🔥💀 {self.name}: Survit même inconscient ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


# ========================================
# FONCTIONS D'AUTO-ACTIVATION (PASSIFS)
# ========================================

def auto_activate_defense_sans_armure(heroes: List, log: List[str]) -> bool:
    """
    Active automatiquement Défense sans armure si Barbare (P-5) est présent, vivant,
    et ne porte ni armure ni bouclier.
    Appelé au début du combat par l'interface UI.

    RÈGLE: Défense sans armure de Barbare est une capacité passive permanente qui s'active
    automatiquement dès le début du combat si les conditions sont remplies (pas d'armure/bouclier)
    et reste active tant que Barbare est vivant et ne change pas d'équipement.

    Args:
        heroes: Liste des héros participant au combat
        log: Liste de logs de combat (sera modifiée)

    Returns:
        bool: True si le buff a été activé, False sinon

    Effet:
        Ajoute +2 jetons de parade permanents à Barbare si pas d'armure/bouclier équipé
    """
    # Chercher Barbare (P-5) parmi les héros vivants
    barbare = next((h for h in heroes if h.code == "P-5" and h.is_alive()), None)

    if not barbare:
        return False

    # Vérifier équipement : aucune armure/bouclier
    has_armor_or_shield = False
    if hasattr(barbare, 'equipment') and barbare.equipment:
        for item in barbare.equipment:
            if hasattr(item, 'type') and item.type == 'armure':
                has_armor_or_shield = True
                break

    # Si armure/bouclier équipé, ne pas activer
    if has_armor_or_shield:
        log.append(f"⚠️ Défense sans armure inactive (Barbare porte une armure/bouclier)")
        return False

    # Initialiser temporary_buffs si nécessaire
    if not hasattr(barbare, 'temporary_buffs'):
        barbare.temporary_buffs = {}

    # Appliquer le buff permanent
    barbare.temporary_buffs['defense_sans_armure_active'] = {
        'parade_bonus': 2,
        'type': 'passive_permanent',
        'source': 'barbare_defense_sans_armure'
    }

    # Appliquer directement le bonus aux jetons de parade max
    if hasattr(barbare, 'max_parade_tokens'):
        barbare.max_parade_tokens += 2

    # Recharger les jetons de parade pour refléter la nouvelle valeur max
    if hasattr(barbare, 'current_parade_tokens') and hasattr(barbare, 'max_parade_tokens'):
        barbare.current_parade_tokens = barbare.max_parade_tokens

    # Logger l'activation
    log.append(f"💪 Défense sans armure de Barbare active (+2 jetons de parade permanents)")

    return True


def auto_activate_critique_brutal(heroes: List, log: List[str]) -> bool:
    """
    AUTO-ACTIVATION: Active automatiquement "Critique brutal" pour Barbare dès le début du combat.

    Critique brutal est un passif permanent qui élargit la plage de critique à 18-19-20
    au lieu de 20 seul. Cette capacité s'active automatiquement dès le début du combat
    et reste active tant que Barbare est vivant.

    Args:
        heroes: Liste des héros participant au combat
        log: Liste de logs de combat (sera modifiée)

    Returns:
        bool: True si le buff a été activé, False sinon

    Effet:
        Permet les critiques sur 18-19-20 au lieu de 20 seul
    """
    # Chercher Barbare (P-5) parmi les héros vivants
    barbare = next((h for h in heroes if h.code == "P-5" and h.is_alive()), None)

    if not barbare:
        return False

    # Initialiser temporary_buffs si nécessaire
    if not hasattr(barbare, 'temporary_buffs'):
        barbare.temporary_buffs = {}

    # Appliquer le buff permanent
    barbare.temporary_buffs['expanded_crit_range'] = {
        'type': 'passive_permanent',
        'critical_rolls': [18, 19, 20],
        'source': 'critique_brutal'
    }

    # Logger l'activation
    log.append(f"🔥 Critique brutal de Barbare actif (Critiques: 18-19-20)")

    return True
