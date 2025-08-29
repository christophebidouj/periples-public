# liarie.py - Capacités individuelles de Liarie (P-2)
"""
Capacités individuelles pour le héros Liarie (P-2)
Phase 2: Toutes les 6 capacités implémentées - VERSION CORRIGÉE

Liarie est une mage spécialisée dans la magie offensive et défensive.
Ses capacités se concentrent sur les sorts élémentaires et la protection magique.

P-2-1: Eclair magique ✅
P-2-2: Armure du mage ✅
P-2-3: Mur de glace ✅
P-2-4: Boule de feu ✅
P-2-5: Vol de vie ✅
P-2-6: Pluie de météores ✅
"""

from typing import List, Dict, Any
from ..base_ability import BaseAbility
from ..ability_registry import register_ability


# ========================================
# CAPACITÉS LIARIE (P-2) - MAGE ÉLÉMENTAIRE
# ========================================

@register_ability
class LiarieEclairMagique(BaseAbility):
    """P-2-1: Eclair magique - 4 dégâts magiques sans riposte"""
    
    hero_code = "P-2"
    ability_number = 1
    name = "Eclair magique"
    description = "Inflige 4 dégâts magiques à un ennemi, sans qu'il puisse riposter."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 1
        self.damage_amount = 4
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Lance un éclair magique contre un ennemi"""
        try:
            # Vérifier le coût en sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # FIX: Utiliser _get_all_enemies() au lieu de targets pour éviter l'auto-ciblage
            enemies = self._get_all_enemies(caster, context)
            
            if not enemies:
                log.append(f"⚡ {caster.name} lance un éclair magique mais il n'y a aucun ennemi !")
                return True
            
            target = enemies[0]  # Premier ennemi vivant
            
            # Infliger dégâts magiques (sans riposte possible)
            damage_dealt = self._apply_damage(target, self.damage_amount, "magical", log)
            
            log.append(f"⚡ {caster.name} lance un éclair magique sur {target.name} !")
            log.append(f"   (Sans possibilité de riposte)")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur éclair magique: {str(e)}")
            return False
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        """Vérifie si l'éclair magique peut être lancé"""
        if caster.code != "P-2":
            return False
        return caster.current_spells >= self.spell_cost
    
    def get_preview(self) -> str:
        """Aperçu des effets"""
        return f"⚡ {self.name}: {self.damage_amount} dégâts magiques sans riposte (Coût: {self.spell_cost} sort)"


@register_ability
class LiarieArmureDuMage(BaseAbility):
    """P-2-2: Armure du mage - Jeton de parade supplémentaire par tour"""
    
    hero_code = "P-2"
    ability_number = 2
    name = "Armure du mage"
    description = "Gagne un jeton de parade supplémentaire par tour."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 2
        self.parade_bonus = 1
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Active l'armure magique du mage"""
        try:
            # Vérifier le coût en sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # FIX: Utiliser attribut existant au lieu de magical_armor_bonus
            # Option A: Augmenter directement max_parade_tokens
            if hasattr(caster, 'max_parade_tokens'):
                caster.max_parade_tokens += self.parade_bonus
            else:
                # Fallback: créer l'attribut si absent
                caster.max_parade_tokens = self.parade_bonus
            
            # Option B: Utiliser système buff temporaire existant  
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}
            caster.temporary_buffs['armure_mage'] = self.parade_bonus
            
            # Recharger jetons parade immédiatement avec nouveau maximum
            if hasattr(caster, 'current_parade_tokens'):
                caster.current_parade_tokens = caster.max_parade_tokens
            
            log.append(f"🛡️ {caster.name} s'entoure d'une armure magique !")
            log.append(f"   +{self.parade_bonus} jeton de parade maximum")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur armure du mage: {str(e)}")
            return False
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        """Vérifie si l'armure du mage peut être activée"""
        if caster.code != "P-2":
            return False
        return caster.current_spells >= self.spell_cost
    
    def get_preview(self) -> str:
        """Aperçu des effets"""
        return f"🛡️ {self.name}: +{self.parade_bonus} jeton de parade par tour (Coût: {self.spell_cost} sorts)"


@register_ability
class LiarieMurDeGlace(BaseAbility):
    """P-2-3: Mur de glace - 2 dégâts magiques + recul en première ligne"""
    
    hero_code = "P-2"
    ability_number = 3
    name = "Mur de glace"
    description = "Inflige 2 dégâts magiques aux adversaires situés dans le groupe de tête, et les fait reculer d'un rang."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 2
        self.damage_amount = 2
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Crée un mur de glace qui repousse les ennemis en première ligne"""
        try:
            # Vérifier le coût en sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # Récupérer les ennemis en première ligne
            front_line_enemies = self._get_front_line_enemies(context)
            
            if not front_line_enemies:
                log.append(f"❄️ {caster.name} crée un mur de glace mais aucun ennemi n'est en première ligne !")
                return True
            
            results = []
            pushed_back = []
            
            for enemy in front_line_enemies:
                # Infliger dégâts de glace
                damage_dealt = self._apply_damage(enemy, self.damage_amount, "magical", log)
                results.append(f"{enemy.name}: {damage_dealt} dégâts")
                
                # Effet de recul
                if self._push_back_enemy(enemy, context):
                    pushed_back.append(enemy.name)
            
            log.append(f"❄️ {caster.name} dresse un mur de glace !")
            if results:
                log.append(f"   Dégâts: " + ", ".join(results))
            if pushed_back:
                log.append(f"   Repoussés: {', '.join(pushed_back)}")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur mur de glace: {str(e)}")
            return False
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        """Vérifie si le mur de glace peut être créé"""
        if caster.code != "P-2":
            return False
        return caster.current_spells >= self.spell_cost
    
    def get_preview(self) -> str:
        """Aperçu des effets"""
        return f"❄️ {self.name}: {self.damage_amount} dégâts + recul première ligne (Coût: {self.spell_cost} sorts)"
    
    def _get_front_line_enemies(self, context: Dict[str, Any]) -> List:
        """Récupère les ennemis en première ligne"""
        all_enemies = self._get_all_enemies(None, context)
        
        # Logique simplifiée: les 2 premiers ennemis sont en première ligne
        return all_enemies[:2] if len(all_enemies) >= 2 else all_enemies
    
    def _push_back_enemy(self, enemy, context: Dict[str, Any]) -> bool:
        """Repousse un ennemi d'un rang vers l'arrière"""
        # Marquer l'ennemi comme repoussé
        if hasattr(enemy, 'position'):
            enemy.position += 1
            return True
        elif hasattr(enemy, 'is_pushed_back'):
            enemy.is_pushed_back = True
            return True
        
        # Stocker l'effet dans le contexte
        if 'pushed_enemies' not in context:
            context['pushed_enemies'] = set()
        context['pushed_enemies'].add(id(enemy))
        
        return True


@register_ability
class LiarieBouleDeFeu(BaseAbility):
    """P-2-4: Boule de feu - 3 dégâts magiques à tous sans riposte"""
    
    hero_code = "P-2"
    ability_number = 4
    name = "Boule de feu"
    description = "Inflige 3 dégâts magiques à tous les ennemis du combat, sans qu'ils puissent riposter."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 3
        self.damage_amount = 3
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Lance une boule de feu explosive contre tous les ennemis"""
        try:
            # Vérifier le coût en sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # Récupérer tous les ennemis
            all_enemies = self._get_all_enemies(caster, context)
            
            if not all_enemies:
                log.append(f"🔥 {caster.name} lance une boule de feu mais il n'y a aucun ennemi !")
                return True
            
            results = []
            
            for enemy in all_enemies:
                # Infliger dégâts de feu (sans riposte possible)
                damage_dealt = self._apply_damage(enemy, self.damage_amount, "magical", log)
                results.append(f"{enemy.name}: {damage_dealt} dégâts")
            
            log.append(f"🔥 {caster.name} lance une boule de feu explosive !")
            log.append(f"   Dégâts: " + ", ".join(results))
            log.append(f"   (Sans possibilité de riposte)")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur boule de feu: {str(e)}")
            return False
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        """Vérifie si la boule de feu peut être lancée"""
        if caster.code != "P-2":
            return False
        return caster.current_spells >= self.spell_cost
    
    def get_preview(self) -> str:
        """Aperçu des effets"""
        return f"🔥 {self.name}: {self.damage_amount} dégâts magiques à tous sans riposte (Coût: {self.spell_cost} sorts)"


@register_ability
class LiarieVolDeVie(BaseAbility):
    """P-2-5: Vol de vie - 3 dégâts magiques + soins équivalents sans riposte"""
    
    hero_code = "P-2"
    ability_number = 5
    name = "Vol de vie"
    description = "Inflige 3 dégâts magiques à un ennemi et soigne autant de blessures au personnage qui utilise ce sort, sans que l'ennemi puisse riposter."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 2
        self.damage_amount = 3
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Draine la vie d'un ennemi pour se soigner"""
        try:
            # Vérifier le coût en sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # FIX: Utiliser _get_all_enemies() au lieu de targets
            enemies = self._get_all_enemies(caster, context)
            
            if not enemies:
                log.append(f"🩸 {caster.name} tente de drainer la vie mais il n'y a aucun ennemi !")
                return True
            
            target = enemies[0]  # Premier ennemi vivant
            
            # Infliger dégâts magiques (sans riposte)
            damage_dealt = self._apply_damage(target, self.damage_amount, "magical", log)
            
            # Soigner le lanceur du même montant que les dégâts infligés
            healed = self._apply_healing(caster, damage_dealt, log)
            
            log.append(f"🩸 {caster.name} draine la vie de {target.name} !")
            log.append(f"   {damage_dealt} dégâts → +{healed} PV pour {caster.name}")
            log.append(f"   (Sans possibilité de riposte)")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur vol de vie: {str(e)}")
            return False
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        """Vérifie si le vol de vie peut être lancé"""
        if caster.code != "P-2":
            return False
        return caster.current_spells >= self.spell_cost
    
    def get_preview(self) -> str:
        """Aperçu des effets"""
        return f"🩸 {self.name}: {self.damage_amount} dégâts + soins équivalents sans riposte (Coût: {self.spell_cost} sorts)"


@register_ability
class LiariePluieDeMetéores(BaseAbility):
    """P-2-6: Pluie de météores - 6 dégâts magiques à tous + stun"""
    
    hero_code = "P-2"
    ability_number = 6
    name = "Pluie de météores"
    description = "Inflige 6 dégâts magiques à tous les adversaires présents lors du combat et les empêche d'agir le tour suivant."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 4  # Sort ultime très coûteux
        self.damage_amount = 6
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Invoque une pluie de météores dévastatrice"""
        try:
            # Vérifier le coût en sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # Récupérer tous les ennemis
            all_enemies = self._get_all_enemies(caster, context)
            
            if not all_enemies:
                log.append(f"☄️ {caster.name} invoque une pluie de météores mais il n'y a aucun ennemi !")
                return True
            
            results = []
            stunned_enemies = []
            
            for enemy in all_enemies:
                # Infliger dégâts magiques massifs
                damage_dealt = self._apply_damage(enemy, self.damage_amount, "magical", log)
                results.append(f"{enemy.name}: {damage_dealt} dégâts")
                
                # Effet d'étourdissement pour le tour suivant
                if hasattr(enemy, 'is_stunned'):
                    enemy.is_stunned = True
                    stunned_enemies.append(enemy.name)
                else:
                    # Stocker l'effet de stun dans le contexte
                    if 'stunned_entities' not in context:
                        context['stunned_entities'] = set()
                    context['stunned_entities'].add(id(enemy))
                    stunned_enemies.append(enemy.name)
            
            log.append(f"☄️ {caster.name} invoque une pluie de météores dévastatrice !")
            log.append(f"   Dégâts: " + ", ".join(results))
            if stunned_enemies:
                log.append(f"   Tous étourdis pour le prochain tour !")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur pluie de météores: {str(e)}")
            return False
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        """Vérifie si la pluie de météores peut être invoquée"""
        if caster.code != "P-2":
            return False
        return caster.current_spells >= self.spell_cost
    
    def get_preview(self) -> str:
        """Aperçu des effets"""
        return f"☄️ {self.name}: {self.damage_amount} dégâts magiques à tous + stun (Coût: {self.spell_cost} sorts)"


# ========================================
# FONCTIONS UTILITAIRES ET STATISTIQUES
# ========================================

def get_liarie_abilities_count() -> int:
    """Retourne le nombre de capacités de Liarie enregistrées"""
    return 6


def get_liarie_abilities_summary() -> str:
    """Retourne un résumé des capacités de Liarie"""
    return """
    🎭 LIARIE (P-2) - 6 capacités complètes:
    ✅ P-2-1: Eclair magique (4 dégâts magiques sans riposte, coût 1)
    ✅ P-2-2: Armure du mage (+1 parade par tour, coût 2)
    ✅ P-2-3: Mur de glace (2 dégâts + recul première ligne, coût 2)
    ✅ P-2-4: Boule de feu (3 dégâts à tous sans riposte, coût 3)
    ✅ P-2-5: Vol de vie (3 dégâts + soins équivalents, coût 2)
    ✅ P-2-6: Pluie de météores (6 dégâts à tous + stun, coût 4)
    """


def get_liarie_spell_costs() -> dict:
    """Retourne les coûts en sorts des capacités de Liarie"""
    return {
        "Eclair magique": 1,
        "Armure du mage": 2,
        "Mur de glace": 2,
        "Boule de feu": 3,
        "Vol de vie": 2,
        "Pluie de météores": 4
    }


def get_liarie_damage_output() -> dict:
    """Retourne les dégâts potentiels des sorts offensifs de Liarie"""
    return {
        "Eclair magique": {"single": 4, "type": "magical"},
        "Mur de glace": {"front_line": 2, "type": "magical"},
        "Boule de feu": {"all_enemies": 3, "type": "magical"},
        "Vol de vie": {"single": 3, "type": "magical", "healing": 3},
        "Pluie de météores": {"all_enemies": 6, "type": "magical", "ultimate": True}
    }


def get_liarie_tactical_analysis() -> dict:
    """Analyse tactique des capacités de Liarie"""
    return {
        "role": "Mage élémentaire - DPS/Support",
        "strengths": [
            "Excellents dégâts magiques",
            "Capacités sans riposte", 
            "Contrôle de zone (stun, recul)",
            "Auto-sustain avec Vol de vie",
            "Protection avec Armure du mage"
        ],
        "spell_efficiency": {
            "low_cost": ["Eclair magique"],
            "medium_cost": ["Armure du mage", "Mur de glace", "Vol de vie"],
            "high_cost": ["Boule de feu", "Pluie de météores"]
        },
        "combat_phases": {
            "early": "Eclair magique + Armure du mage",
            "mid": "Boule de feu + Vol de vie",
            "late": "Pluie de météores (finishing move)"
        }
    }