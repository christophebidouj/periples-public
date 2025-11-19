# thordius.py - Capacités individuelles de Thordius (P-5) - Guerrier Berserker
"""
Capacités individuelles pour le héros Thordius (P-5)
Thordius est un guerrier berserker spécialisé dans les dégâts physiques bruts et la rage.
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


# ========================================
# CAPACITÉS THORDIUS (P-5) - GUERRIER BERSERKER
# ========================================

@register_ability
class ThordiusCoupDeRage(BaseAbility):
    """P-5-1: Coup de rage - +2 parade si pas d'armure/bouclier équipé"""

    hero_code = "P-5"
    ability_number = 1
    name = "Coup de rage"
    description = "2 en parade si aucune armure ou bouclier n'est équipé"

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.parade_bonus = 2

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Accorde +2 parade si Thordius ne porte ni armure ni bouclier"""
        try:
            # Vérifier équipement
            has_armor = False
            has_shield = False

            if hasattr(caster, 'equipment') and caster.equipment:
                for item in caster.equipment:
                    if hasattr(item, 'type'):
                        if item.type == 'Armure':
                            has_armor = True
                        elif item.type == 'Bouclier':
                            has_shield = True

            # Si équipé, refuser
            if has_armor or has_shield:
                log.append(f"⚠️ {caster.name} porte une armure ou un bouclier - Coup de rage impossible")
                return False

            # Ajouter bonus parade temporaire
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            caster.temporary_buffs['thordius_rage_parade'] = {
                'type': 'defense',
                'bonus': self.parade_bonus,
                'duration': 1  # Ce tour uniquement
            }

            # Appliquer bonus parade directement
            if hasattr(caster, 'defense'):
                caster.defense += self.parade_bonus

            log.append(f"💪 {caster.name} utilise Coup de rage (+{self.parade_bonus} parade ce tour)")

            return True

        except Exception as e:
            log.append(f"❌ Erreur Coup de rage: {e}")
            return False

    def get_preview(self) -> str:
        return f"💪 {self.name}: +{self.parade_bonus} parade si pas d'armure/bouclier (Gratuit)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]  # Cible soi-même


@register_ability
class ThordiusCharge(BaseAbility):
    """P-5-2: Charge - +3 dégâts physiques permanent pour le combat"""

    hero_code = "P-5"
    ability_number = 2
    name = "Charge"
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
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Charge déjà utilisée ce combat")
                return False

            # Ajouter buff permanent
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            caster.temporary_buffs['thordius_charge_damage'] = {
                'type': 'permanent_combat',
                'damage_bonus': self.damage_bonus,
                'source': 'charge'
            }

            # Appliquer bonus dégâts directement
            if hasattr(caster, 'damage'):
                caster.damage += self.damage_bonus

            log.append(f"⚡ {caster.name} charge ! (+{self.damage_bonus} dégâts permanent)")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Charge: {e}")
            return False

    def get_preview(self) -> str:
        return f"⚡ {self.name}: +{self.damage_bonus} dégâts permanent ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


@register_ability
class ThordiusIntimidation(BaseAbility):
    """P-5-3: Intimidation - Stun ennemi après attaque réussie"""

    hero_code = "P-5"
    ability_number = 3
    name = "Intimidation"
    description = "Après une attaque réussie, bloque l'action de cet ennemi."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 2
        self.uses_remaining_combat = 2

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Stun un ennemi (bloque son action pour 1 tour)"""
        try:
            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Intimidation déjà utilisée ({self.uses_per_combat} fois)")
                return False

            # Sélectionner ennemi cible
            enemies = self._get_all_enemies(caster, context)
            if not enemies:
                log.append(f"⚠️ Aucun ennemi à intimider")
                return False

            # Prioriser ennemi avec plus de PV
            target = max(enemies, key=lambda e: e.current_health)

            # Appliquer stun
            if not hasattr(target, 'status_effects'):
                target.status_effects = {}

            target.status_effects['stunned'] = {
                'duration': 1,
                'source': 'thordius_intimidation'
            }

            log.append(f"😱 {caster.name} intimide {target.name} - Action bloquée !")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Intimidation: {e}")
            return False

    def get_preview(self) -> str:
        return f"😱 {self.name}: Stun ennemi 1 tour ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [e for e in all_enemies if self._is_alive(e)]


@register_ability
class ThordiusFrappePuissante(BaseAbility):
    """P-5-4: Frappe puissante - Convertit parade en bonus dégâts"""

    hero_code = "P-5"
    ability_number = 4
    name = "Frappe puissante"
    description = "Permet de convertir son score de parade, en bonus de dégâts. La parade ne peut pas être utilisée pendant ce tour."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Convertit parade actuelle en bonus dégâts pour prochaine attaque"""
        try:
            # Récupérer parade actuelle
            current_parade = 0
            if hasattr(caster, 'defense'):
                current_parade = caster.defense
            elif hasattr(caster, 'precision'):
                # Certains héros utilisent precision pour parade
                current_parade = caster.precision

            if current_parade <= 0:
                log.append(f"⚠️ {caster.name} n'a pas de parade à convertir")
                return False

            # Ajouter bonus dégâts
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            caster.temporary_buffs['damage_bonus_next_attack'] = current_parade

            # Retirer parade temporairement
            if hasattr(caster, 'defense'):
                caster.defense = 0

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
class ThordiusCriDeGuerre(BaseAbility):
    """P-5-5: Cri de guerre - Critiques sur 18-19-20 au lieu de 20 seul"""

    hero_code = "P-5"
    ability_number = 5
    name = "Cri de guerre"
    description = "Les 18 & 19 sur le jet de dé, sont également des réussites critiques."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Élargit la plage de critique à 18-19-20 pour tout le combat"""
        try:
            # Ajouter buff permanent
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            # Vérifier si déjà actif
            if 'expanded_crit_range' in caster.temporary_buffs:
                log.append(f"⚠️ Cri de guerre déjà actif")
                return False

            caster.temporary_buffs['expanded_crit_range'] = {
                'type': 'permanent_combat',
                'critical_rolls': [18, 19, 20],
                'source': 'cri_de_guerre'
            }

            log.append(f"🔥 {caster.name} pousse un CRI DE GUERRE ! (Critiques: 18-19-20)")

            return True

        except Exception as e:
            log.append(f"❌ Erreur Cri de guerre: {e}")
            return False

    def get_preview(self) -> str:
        return f"🔥 {self.name}: Critiques 18-19-20 permanent (Gratuit)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


@register_ability
class ThordiusBerserker(BaseAbility):
    """P-5-6: Berserker - Continue à combattre même inconscient"""

    hero_code = "P-5"
    ability_number = 6
    name = "Berserker"
    description = "Tant qu'il est en rage, Thordius continue de combattre même s'il atteint le maximum de points de blessures."

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
