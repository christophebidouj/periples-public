# lame.py - Capacités individuelles de Lame (P-7) - Assassin
"""
Capacités individuelles pour le héros Lame (P-7)
Lame est un assassin spécialisé dans les dégâts burst, l'esquive et la furtivité.
Ses capacités se concentrent sur les dégâts massifs et la survie par l'esquive.

✅ DONNÉES OFFICIELLES Sorts.xlsx:
P-7-1: Furtivité (Coût: 0) - N'attaque pas ce tour, double dégâts tour suivant
P-7-2: Attaque sournoise (Coût: 0, 2/combat) - Esquive prochaine attaque adverse
P-7-3: Empoisonnement (Coût: 0) - "Pas utile en combat" → DÉSACTIVÉ
P-7-4: Paralysie (Coût: 0, 1/combat) - Tous ennemis paralysés 2 tours
P-7-5: Assassination (Coût: 0, 3/combat) - Dégâts attaque sur tous ennemis
P-7-6: Ombre mortelle (Coût: 0, 1/combat) - Furtivité permanente chaque tour
"""

from typing import List, Dict, Any
from ..base_ability import BaseAbility
from ..ability_registry import register_ability


# ========================================
# CAPACITÉS LAME (P-7) - ASSASSIN
# ========================================

@register_ability
class LameAttaqueFurtive(BaseAbility):
    """P-7-1: Attaque furtive - Esquive totale ce tour + double dégâts tour suivant"""

    hero_code = "P-7"
    ability_number = 1
    name = "Attaque furtive"
    description = "N'attaque pas ce tour. Esquive totale (ignore toutes attaques ennemies). Double dégâts le tour suivant sans avoir à jeter le dé."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.damage_multiplier = 2

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Active furtivité - empêche attaque ce tour, esquive totale, double dégâts tour suivant"""
        try:
            # NOUVEAU - Vérifier limitation 1 capacité par tour pour Lame
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            if caster.temporary_buffs.get('lame_ability_used_this_turn', False):
                log.append(f"⚠️ {caster.name} a déjà utilisé une capacité ce tour (limite: 1/tour)")
                return False

            # 1. Empêcher l'attaque ce tour
            caster.can_attack_this_turn = False

            # 2. NOUVEAU - Statut invisible (non-ciblable par les ennemis)
            # Pas besoin d'esquive - l'invisibilité empêche le ciblage
            if not hasattr(caster, 'status_effects'):
                caster.status_effects = {}

            caster.status_effects['invisible'] = {
                'type': 'untargetable',
                'expires_on_damage_dealt': True,  # Se termine si Lame inflige des dégâts
                'expires_end_of_turn': False,      # Ne se termine PAS à la fin du tour
                'duration_turns': 2,               # Dure 2 tours (tour actuel + prochain tour)
                'turns_remaining': 2,              # Compteur de tours restants
                'source': 'lame_furtivite'
            }

            # 3. Double dégâts tour suivant
            caster.temporary_buffs['double_next_attack'] = True

            # Marquer capacité utilisée ce tour
            caster.temporary_buffs['lame_ability_used_this_turn'] = True

            log.append(f"🌑 {caster.name} se faufile dans l'ombre...")
            log.append(f"   👻 INVISIBLE pendant 2 tours - Les ennemis ne peuvent pas le cibler")
            log.append(f"   ⚔️ Attaque bloquée ce tour, dégâts ×{self.damage_multiplier} au prochain tour")
            log.append(f"   ⚠️ Furtivité se termine : si attaque OU après 2 tours")

            return True

        except Exception as e:
            log.append(f"❌ Erreur Furtivité: {e}")
            return False

    def get_preview(self) -> str:
        return f"🌑 {self.name}: Esquive totale + ×{self.damage_multiplier} dégâts tour suivant (Gratuit)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


@register_ability
class LameDerobade(BaseAbility):
    """P-7-2: Dérobade - Esquive/ignore dégâts prochaine attaque adverse"""

    hero_code = "P-7"
    ability_number = 2
    name = "Dérobade"
    description = "Permet d'ignorer les dégâts reçus d'une attaque adverse."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 2
        self.uses_remaining_combat = 2

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Active esquive - prochaine attaque subie est annulée"""
        try:
            # NOUVEAU - Vérifier limitation 1 capacité par tour pour Lame
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            if caster.temporary_buffs.get('lame_ability_used_this_turn', False):
                log.append(f"⚠️ {caster.name} a déjà utilisé une capacité ce tour (limite: 1/tour)")
                return False

            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Attaque sournoise déjà utilisée ({self.uses_per_combat} fois)")
                return False

            caster.temporary_buffs['lame_dodge_ready'] = {
                'type': 'damage_negation',
                'charges': 1,  # Annule 1 attaque
                'source': 'attaque_sournoise'
            }

            # Marquer capacité utilisée ce tour
            caster.temporary_buffs['lame_ability_used_this_turn'] = True

            log.append(f"💨 {caster.name} prépare une esquive sournoise !")
            log.append(f"   🛡️ Prochaine attaque subie sera ignorée")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Attaque sournoise: {e}")
            return False

    def get_preview(self) -> str:
        return f"💨 {self.name}: Esquive prochaine attaque ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


# P-7-3: Empoisonnement - "Pas utile en combat"
# Cette capacité est automatiquement filtrée par data_loader.py


@register_ability
class LameBombeFumigene(BaseAbility):
    """P-7-4: Bombe fumigène - Tous ennemis paralysés 2 tours"""

    hero_code = "P-7"
    ability_number = 4
    name = "Bombe fumigène"
    description = "Utilise une ressource pour empêcher les actions de tous adversaires pendant deux tours."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 1
        self.uses_remaining_combat = 1
        self.stun_duration = 2

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Paralyse tous les ennemis pour 2 tours (AoE stun)"""
        try:
            # NOUVEAU - Vérifier limitation 1 capacité par tour pour Lame
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            if caster.temporary_buffs.get('lame_ability_used_this_turn', False):
                log.append(f"⚠️ {caster.name} a déjà utilisé une capacité ce tour (limite: 1/tour)")
                return False

            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Paralysie déjà utilisée ce combat")
                return False

            # Appliquer paralysie à TOUS les ennemis
            enemies = self._get_all_enemies(caster, context)
            if not enemies:
                log.append(f"⚠️ Aucun ennemi à paralyser")
                return False

            paralyzed_count = 0
            for enemy in enemies:
                if not hasattr(enemy, 'status_effects'):
                    enemy.status_effects = {}

                enemy.status_effects['stunned'] = {
                    'duration': self.stun_duration,
                    'source': 'lame_paralysie'
                }
                paralyzed_count += 1

            # Marquer capacité utilisée ce tour
            caster.temporary_buffs['lame_ability_used_this_turn'] = True

            log.append(f"🕷️ {caster.name} empoisonne TOUS les ennemis !")
            log.append(f"   😵 {paralyzed_count} ennemis paralysés pour {self.stun_duration} tours")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Paralysie: {e}")
            return False

    def get_preview(self) -> str:
        return f"🕷️ {self.name}: Stun AoE {self.stun_duration} tours ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]  # Cible soi-même (effet AoE)


@register_ability
class LameAttaqueTournoyante(BaseAbility):
    """P-7-5: Attaque tournoyante - Dégâts attaque sur tous les ennemis"""

    hero_code = "P-7"
    ability_number = 5
    name = "Attaque tournoyante"
    description = "Inflige les dégâts d'une attaque réussie sur tous les ennemis."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 3
        self.uses_remaining_combat = 3

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Prochaine attaque cible TOUS les ennemis (multi-target)"""
        try:
            # NOUVEAU - Vérifier limitation 1 capacité par tour pour Lame
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            if caster.temporary_buffs.get('lame_ability_used_this_turn', False):
                log.append(f"⚠️ {caster.name} a déjà utilisé une capacité ce tour (limite: 1/tour)")
                return False

            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Assassination déjà utilisée ({self.uses_per_combat} fois)")
                return False

            caster.temporary_buffs['assassination_ready'] = {
                'type': 'multi_target',
                'applies_to': 'next_attack',
                'source': 'lame_assassination'
            }

            # Marquer capacité utilisée ce tour
            caster.temporary_buffs['lame_ability_used_this_turn'] = True

            log.append(f"🗡️ {caster.name} prépare une Assassination !")
            log.append(f"   ⚔️ Prochaine attaque touchera TOUS les ennemis")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Assassination: {e}")
            return False

    def get_preview(self) -> str:
        return f"🗡️ {self.name}: Attaque multi-cible ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]


@register_ability
class LameAssautFurieux(BaseAbility):
    """P-7-6: Assaut furieux - Furtivité permanente chaque tour"""

    hero_code = "P-7"
    ability_number = 6
    name = "Assaut furieux"
    description = "Permet d'utiliser l'attaque furtive à tous les tours, au lieu d'un sur deux, pendant toute la durée du combat."

    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 0
        self.uses_per_combat = 1
        self.uses_remaining_combat = 1

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Active furtivité permanente - appliqué automatiquement chaque tour"""
        try:
            # NOUVEAU - Vérifier limitation 1 capacité par tour pour Lame
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}

            if caster.temporary_buffs.get('lame_ability_used_this_turn', False):
                log.append(f"⚠️ {caster.name} a déjà utilisé une capacité ce tour (limite: 1/tour)")
                return False

            # Vérifier limitation
            if self.uses_remaining_combat <= 0:
                log.append(f"⚠️ Ombre mortelle déjà utilisée ce combat")
                return False

            caster.temporary_buffs['permanent_stealth'] = {
                'type': 'permanent_combat',
                'damage_multiplier': 2,
                'auto_apply': True,  # S'applique chaque début de tour
                'source': 'ombre_mortelle'
            }

            # Marquer capacité utilisée ce tour
            caster.temporary_buffs['lame_ability_used_this_turn'] = True

            log.append(f"👤💀 {caster.name} devient l'OMBRE MORTELLE !")
            log.append(f"   🌑 Furtivité automatique chaque tour (×2 dégâts permanent)")

            # Décompter utilisation
            self.uses_remaining_combat -= 1

            return True

        except Exception as e:
            log.append(f"❌ Erreur Ombre mortelle: {e}")
            return False

    def get_preview(self) -> str:
        return f"👤💀 {self.name}: Furtivité permanente ({self.uses_remaining_combat}/{self.uses_per_combat} rest.)"

    def get_targets(self, caster, all_heroes: List, all_enemies: List, context: Dict[str, Any]) -> List:
        return [caster]
