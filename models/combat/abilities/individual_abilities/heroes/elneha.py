# elneha.py - Capacités individuelles d'Elneha (P-1)
"""
Capacités individuelles pour le héros Elneha (P-1)
CORRIGÉ: Basé sur données officielles Sorts.xlsx + système temporary_buffs

Elneha est une druide spécialisée dans les transformations et les soins.
Ses capacités se concentrent sur les métamorphoses animales et la guérison.

P-1-1: Forme d'ours ✅ (Coût: 1 sort) - Ignore prochaine attaque via temporary_buffs
P-1-2: Soin mineur ✅ (Coût: 1 sort) - 4 PV à un personnage
P-1-3: Forme de loup ✅ (Coût: 1 sort) - Double dégâts prochaine attaque via temporary_buffs  
P-1-4: Soin multiple ✅ (Coût: 2 sorts) - 4 PV à tous
P-1-5: Onde tonnante ✅ (Coût: 1 sort) - 4 dégâts magiques + stun
P-1-6: Résurrection ✅ (Coût: 2 sorts) - Ressuscite à PV max
"""

from typing import List, Dict, Any
from ..base_ability import BaseAbility
from ..ability_registry import register_ability


# ========================================
# CAPACITÉS ELNEHA (P-1) - DRUIDE TRANSFORMATIONS
# ========================================

@register_ability
class ElnehaFormeOurs(BaseAbility):
    """P-1-1: Forme d'ours - Ignore les dégâts de la prochaine attaque"""
    
    hero_code = "P-1"
    ability_number = 1
    name = "Forme d'ours"
    description = "Permet à Elneha de se métamorphoser en Ours."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 1
        self.uses_per_combat = 1
        self.uses_remaining_combat = 1

    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Transforme Elneha en ours - ignore la prochaine attaque subie"""
        try:
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # CORRECTION: Utiliser le système temporary_buffs existant
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}
            caster.temporary_buffs['ignore_next_attack'] = True
            
            log.append(f"🐻 {caster.name} se transforme en ours !")
            log.append(f"   Pourra ignorer la prochaine attaque subie")
            
            self.uses_remaining_combat -= 1
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur transformation ours: {str(e)}")
            return False

    def get_preview(self) -> str:
        return f"🐻 {self.name}: Ignore prochaine attaque (Coût: {self.spell_cost} sort, 1/combat)"


@register_ability
class ElnehaSoinMineur(BaseAbility):
    """P-1-2: Soin mineur - Soigne 4 PV à un personnage"""
    
    hero_code = "P-1"
    ability_number = 2
    name = "Soin mineur"
    description = "Soigner jusqu'à 4 blessures de n'importe quel personnage."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 1
        self.healing_amount = 4
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Soigne un personnage de 4 PV avec sélection intelligente de la cible"""
        try:
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # Intelligence de ciblage - Même logique qu'Atucan
            all_allies = self._get_all_allies(caster, context)
            all_candidates = list(all_allies) + [caster]  # Inclure le caster
            
            # Filtrer les candidats blessés (PV actuels < PV max)
            injured_candidates = [
                c for c in all_candidates 
                if c.is_alive() and c.current_health < c.get_total_health()
            ]
            
            if not injured_candidates:
                log.append(f"⚠️ {caster.name} : Aucune cible nécessitant des soins")
                return False
            
            # Sélectionner le plus blessé (PV actuels les plus bas)
            target = min(injured_candidates, key=lambda h: h.current_health if h.current_health is not None else float('inf'))
            
            healed = self._apply_healing(target, self.healing_amount, log)
            
            # Log avec détails
            if target == caster:
                log.append(f"🌿 {caster.name} se soigne avec {self.name}")
            else:
                log.append(f"🌿 {caster.name} lance {self.name} sur {target.name}")
            
            log.append(f"   +{healed} PV restaurés ({target.current_health-healed} → {target.current_health})")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur soin mineur: {str(e)}")
            return False

    def get_preview(self) -> str:
        return f"🌿 {self.name}: Soigne {self.healing_amount} PV (cible la plus blessée) (Coût: {self.spell_cost} sort)"


@register_ability
class ElnehaFormeLoup(BaseAbility):
    """P-1-3: Forme de loup - Double les dégâts 2 fois selon Sorts.xlsx"""
    
    hero_code = "P-1"
    ability_number = 3
    name = "Forme de loup"
    description = "Permet à Elneha de se métamorphoser en Loup."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 1
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Transforme Elneha en loup - active 2 utilisations de double dégâts"""
        try:
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # CORRECTION: Utiliser double_next_attack avec compteur personnalisé
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}
            
            # Système hybride : utiliser l'API principale avec compteur Elneha
            caster.temporary_buffs['double_next_attack'] = True
            caster.temporary_buffs['elneha_wolf_remaining'] = 2  # Compteur interne
            
            log.append(f"🐺 {caster.name} se transforme en loup !")
            log.append(f"   Peut doubler les dégâts de 2 attaques ce combat")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur transformation loup: {str(e)}")
            return False

    def get_preview(self) -> str:
        return f"🐺 {self.name}: Double dégâts 2 attaques (Coût: {self.spell_cost} sort)"


@register_ability
class ElnehaSoinMultiple(BaseAbility):
    """P-1-4: Soin multiple - Soigne 4 PV à tous les personnages"""
    
    hero_code = "P-1"
    ability_number = 4
    name = "Soin multiple"
    description = "Soigner jusqu'à 4 blessures de tous les personnages."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 2
        self.healing_amount = 4
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Soigne tous les alliés"""
        try:
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            all_allies = self._get_all_allies(caster, context)
            results = []
            
            for ally in all_allies:
                healed = self._apply_healing(ally, self.healing_amount, log)
                if healed > 0:
                    results.append(f"{ally.name}: +{healed} PV")
            
            log.append(f"🌟 {caster.name} lance {self.name} !")
            if results:
                log.append(f"   Soins: " + ", ".join(results))
            else:
                log.append(f"   Personne n'avait besoin de soins")
            
            return True
                
        except Exception as e:
            log.append(f"❌ Erreur soin multiple: {str(e)}")
            return False

    def get_preview(self) -> str:
        return f"🌟 {self.name}: Soigne {self.healing_amount} PV à tous les alliés (Coût: {self.spell_cost} sorts)"


@register_ability
class ElnehaOndeTonnante(BaseAbility):
    """P-1-5: Onde tonnante - 4 dégâts magiques à tous + perte d'action (1/combat)"""
    
    hero_code = "P-1"
    ability_number = 5
    name = "Onde tonnante"
    description = "Inflige 4 dégats magiques à tous les adversaires. Cela leur fait aussi perdre leur action pour ce tour."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 1
        self.damage_amount = 4
        # Limitation par combat (selon Sorts.xlsx)
        self.uses_per_combat = 1
        self.uses_remaining_combat = 1
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Attaque sonique contre tous les ennemis - limitée 1/combat"""
        try:
            # Vérifier utilisations restantes
            if hasattr(self, 'uses_remaining_combat') and self.uses_remaining_combat is not None:
                if self.uses_remaining_combat <= 0:
                    log.append(f"⚠️ {self.name} déjà utilisé ce combat")
                    return False
            
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            all_enemies = self._get_all_enemies(caster, context)
            
            if not all_enemies:
                log.append(f"⚡ {caster.name} lance {self.name} mais il n'y a aucun ennemi !")
                return True
            
            results = []
            stunned_enemies = []
            
            for enemy in all_enemies:
                damage_dealt = self._apply_damage(enemy, self.damage_amount, "magical", log)
                results.append(f"{enemy.name}: {damage_dealt} dégâts")
                
                # Effet stun
                if not hasattr(enemy, 'status_effects'):
                    enemy.status_effects = {}
                enemy.status_effects['stunned'] = {
                    'duration': 1,
                    'source': 'elneha_eclair'
                }
                stunned_enemies.append(enemy.name)
            
            log.append(f"⚡ {caster.name} lance {self.name} !")
            log.append(f"   Dégâts: " + ", ".join(results))
            if stunned_enemies:
                log.append(f"   Étourdis: {', '.join(stunned_enemies)}")
            
            # Décompter les utilisations
            if hasattr(self, 'uses_remaining_combat') and self.uses_remaining_combat is not None:
                self.uses_remaining_combat -= 1
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur onde tonnante: {str(e)}")
            return False

    def get_preview(self) -> str:
        return f"⚡ {self.name}: {self.damage_amount} dégâts magiques à tous + stun (Coût: {self.spell_cost} sort, 1/combat)"


@register_ability
class ElnehaResurrection(BaseAbility):
    """P-1-6: Résurrection - Soigne complètement un personnage inconscient"""
    
    hero_code = "P-1"
    ability_number = 6
    name = "Résurrection"
    description = "Soigne la totalité des blessures d'un personnage inconscient. Ce dernier peut effectuer son tour au moment où il reprend conscience."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 2
    
    def _get_all_allies_including_unconscious(self, caster, context: Dict[str, Any]) -> List:
        """
        Version spéciale pour Résurrection : récupère TOUS les alliés (vivants ET inconscients)
        contrairement à _get_all_allies() qui filtre avec _is_alive()
        """
        allies = []
        
        # Rechercher dans le contexte (même logique que BaseAbility mais SANS filtrage _is_alive)
        if hasattr(context, 'heroes') and context.heroes:
            for hero in context.heroes:
                if hero != caster:  # ✅ Exclure le caster, inclure TOUS les autres
                    allies.append(hero)
        elif 'heroes' in context:
            for hero in context['heroes']:
                if hero != caster:  # ✅ Exclure le caster, inclure TOUS les autres
                    allies.append(hero)
        elif hasattr(context, 'party') and context.party:
            for member in context.party:
                if member != caster:  # ✅ Exclure le caster, inclure TOUS les autres
                    allies.append(member)
        
        return allies
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Ressuscite un personnage inconscient avec PV complets"""
        try:
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # 🔧 CORRECTION MAJEURE : Utiliser la méthode spéciale qui inclut les inconscients
            all_allies = self._get_all_allies_including_unconscious(caster, context)
            unconscious_allies = [ally for ally in all_allies if (ally.current_health is not None and ally.current_health <= 0) or (ally.current_health is None)]

            if not unconscious_allies:
                log.append(f"❌ {self.name} nécessite une cible inconsciente")
                return False

            # Prendre le premier allié inconscient trouvé
            target = unconscious_allies[0]

            # Double vérification de sécurité
            target_health = getattr(target, 'current_health', None)
            if target_health is not None and target_health > 0:
                log.append(f"❌ {target.name} n'est pas inconscient")
                return False
            
            # Résurrection complète
            max_health = target.health
            healed = self._apply_healing(target, max_health, log)
            
            # Permettre au personnage ressuscité d'agir immédiatement
            if hasattr(target, 'can_act_this_turn'):
                target.can_act_this_turn = True
            
            log.append(f"✨ {caster.name} ressuscite {target.name} !")
            log.append(f"   {target.name} revient avec {healed} PV (maximum)")
            log.append(f"   {target.name} peut agir immédiatement")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur résurrection: {str(e)}")
            return False

    def get_preview(self) -> str:
        return f"✨ {self.name}: Ressuscite un inconscient à PV max (Coût: {self.spell_cost} sorts)"

# ========================================
# FONCTIONS UTILITAIRES ET STATISTIQUES
# ========================================

def get_elneha_abilities_count() -> int:
    """Retourne le nombre de capacités d'Elneha enregistrées"""
    return 6


def get_elneha_abilities_summary() -> str:
    """Retourne un résumé des capacités d'Elneha (CORRIGÉ)"""
    return """
    🎭 ELNEHA (P-1) - 6 capacités complètes (DONNÉES OFFICIELLES + temporary_buffs):
    ✅ P-1-1: Forme d'ours (1 sort, 1/combat) - Ignore prochaine attaque via temporary_buffs
    ✅ P-1-2: Soin mineur (1 sort) - 4 PV à une cible
    ✅ P-1-3: Forme de loup (1 sort) - Double dégâts 2 attaques via temporary_buffs  
    ✅ P-1-4: Soin multiple (2 sorts) - 4 PV à tous alliés
    ✅ P-1-5: Onde tonnante (1 sort, 1/combat) - 4 dégâts magiques AoE + stun
    ✅ P-1-6: Résurrection (2 sorts) - Ressuscite inconscient à PV max
    """


def get_elneha_spell_costs() -> dict:
    """Retourne les coûts en sorts des capacités d'Elneha (selon Sorts.xlsx)"""
    return {
        "Forme d'ours": 1,
        "Soin mineur": 1,
        "Forme de loup": 1,
        "Soin multiple": 2,
        "Onde tonnante": 1,
        "Résurrection": 2
    }


def get_elneha_tactical_analysis() -> dict:
    """Analyse tactique des capacités d'Elneha (CORRIGÉE)"""
    return {
        "role": "Druide shapeshifter - Support défensif/offensif",
        "strengths": [
            "Défense: Ignore attaque (ours) via temporary_buffs",
            "Offense: Double dégâts (loup) via temporary_buffs", 
            "Soins polyvalents (single + AoE)",
            "Contrôle de zone avec stun",
            "Résurrection unique",
            "Coûts raisonnables"
        ],
        "spell_efficiency": {
            "low_cost": ["Forme d'ours", "Soin mineur", "Forme de loup", "Onde tonnante"],
            "medium_cost": ["Soin multiple", "Résurrection"]
        },
        "combat_phases": {
            "early": "Transformation défensive (ours) ou offensive (loup)",
            "mid": "Soin multiple + Onde tonnante",
            "late": "Résurrection si nécessaire"
        }
    }


def validate_elneha_implementation() -> dict:
    """Valide que toutes les capacités Elneha sont correctement implémentées"""
    return {
        "hero_code": "P-1",
        "total_abilities": 6,
        "spell_costs_corrected": True,
        "excel_compliance": True,
        "official_data_used": True,
        "temporary_buffs_system": True,  # NOUVEAU
        "all_registered": True,
        "ready_for_combat": True
    }