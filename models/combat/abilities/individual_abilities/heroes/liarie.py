# liarie.py - Capacités individuelles de Liarie (P-2)
"""
Capacités individuelles pour le héros Liarie (P-2)
Phase 2: Toutes les 6 capacités implémentées - VERSION CORRIGÉE SORTS.XLSX

Liarie est une mage spécialisée dans la magie offensive et défensive.
Ses capacités se concentrent sur les sorts élémentaires et la protection magique.

P-2-1: Éclair magique ✅
P-2-2: Armure du mage ✅ CORRIGÉ
P-2-3: Mur de glace ✅ CORRIGÉ MAJEUR
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
    """P-2-1: Éclair magique - 4 dégâts magiques répartis intelligemment"""
    
    hero_code = "P-2"
    ability_number = 1
    name = "Éclair magique"
    description = "Inflige 4 dégâts magiques répartis au choix entre les ennemis."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 1  # ✅ CORRECT selon Sorts.xlsx
        self.total_damage = 4
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Lance un éclair magique avec répartition intelligente des dégâts"""
        try:
            # Vérifier le coût en sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # Récupérer tous les ennemis vivants
            enemies = self._get_all_enemies(caster, context)
            
            if not enemies:
                log.append(f"⚡ {caster.name} lance un éclair magique mais il n'y a aucun ennemi !")
                return True
            
            # Version simple : répartition équitable d'abord
            remaining_damage = self.total_damage
            targets_hit = []
            
            # Trier ennemis par PV croissants pour prioriser les éliminations
            enemies_sorted = []
            for i, enemy in enumerate(enemies):
                enemies_sorted.append((enemy.current_health, i, enemy))
            enemies_sorted.sort()  # Tri par (PV, index) évite comparaison d'objets
            
            # Appliquer dégâts
            for health, _, enemy in enemies_sorted:
                if remaining_damage <= 0:
                    break
                    
                damage_to_apply = min(health, remaining_damage)
                damage_dealt = self._apply_damage(enemy, damage_to_apply, "magical", log)
                remaining_damage -= damage_to_apply
                targets_hit.append(f"{enemy.name} ({damage_to_apply})")
            
            # Log descriptif
            log.append(f"⚡ {caster.name} lance un éclair magique réparti !")
            log.append(f"   Cibles: {', '.join(targets_hit)}")
            log.append(f"   (Sans riposte)")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur éclair magique: {str(e)}")
            return False
    
    def _calculate_smart_distribution(self, enemies: List, total_damage: int) -> Dict:
        """
        Calcule la répartition optimale des dégâts pour maximiser les éliminations
        
        Stratégie:
        1. Prioriser l'élimination d'ennemis (finir ceux à faible PV)
        2. Répartir le reste efficacement
        3. Éviter le gaspillage (pas plus de PV restants)
        """
        distribution = {enemy: 0 for enemy in enemies}
        remaining_damage = total_damage
        
        # Trier ennemis par PV croissants (finir les plus faibles d'abord)
        sorted_enemies = sorted(enemies, key=lambda e: e.current_health)
        
        # Phase 1: Éliminer les ennemis qu'on peut finir
        for enemy in sorted_enemies:
            if remaining_damage <= 0:
                break
                
            health = enemy.current_health
            
            # Si on peut éliminer cet ennemi avec les dégâts restants
            if health <= remaining_damage:
                distribution[enemy] = health
                remaining_damage -= health
            else:
                # Sinon, infliger le maximum possible à cet ennemi
                distribution[enemy] = remaining_damage
                remaining_damage = 0
                break
        
        return distribution
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        """Vérifie si l'éclair magique peut être lancé"""
        if caster.code != "P-2":
            return False
        return caster.current_spells >= self.spell_cost
    
    def get_preview(self) -> str:
        """Aperçu des effets"""
        return f"⚡ {self.name}: {self.total_damage} dégâts magiques répartis intelligemment (Coût: {self.spell_cost} sort)"


@register_ability
class LiarieArmureDuMage(BaseAbility):
    """P-2-2: Armure du mage - Bouclier de parade permanent - VERSION CORRIGÉE"""
    
    hero_code = "P-2"
    ability_number = 2
    name = "Armure du mage"
    description = "Créer un bouclier de 2 de parade pendant toute la durée du combat."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 1  # ✅ Correct selon Sorts.xlsx
        self.parade_bonus = 2  # ✅ CORRIGÉ selon Sorts.xlsx (bouclier de 2)
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Active l'armure magique permanente"""
        try:
            # Vérifier le coût en sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # Vérifier si déjà actif pour éviter cumul (NON CUMULABLE)
            if hasattr(caster, 'temporary_buffs') and caster.temporary_buffs.get('armure_mage_active'):
                log.append(f"🛡️ {caster.name} a déjà une armure magique active !")
                return False
            
            # Marquer l'armure comme active pour éviter cumul
            if not hasattr(caster, 'temporary_buffs'):
                caster.temporary_buffs = {}
            caster.temporary_buffs['armure_mage_active'] = True
            
            # MÉCANIQUE SIMPLE: Augmenter max_parade_tokens de 2
            if not hasattr(caster, 'max_parade_tokens'):
                caster.max_parade_tokens = 0
            
            caster.max_parade_tokens += self.parade_bonus  # +2 permanent
            
            # Recharger jetons parade immédiatement avec nouveau maximum
            caster.current_parade_tokens = caster.max_parade_tokens
            
            log.append(f"🛡️ {caster.name} s'entoure d'une armure magique permanente !")
            log.append(f"   +{self.parade_bonus} jetons de parade maximum (durée du combat)")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur armure du mage: {str(e)}")
            return False
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        """Vérifie si l'armure du mage peut être activée"""
        if caster.code != "P-2":
            return False
        
        # Vérifier si déjà actif
        if hasattr(caster, 'temporary_buffs') and caster.temporary_buffs.get('armure_mage_active'):
            return False
            
        return caster.current_spells >= self.spell_cost
    
    def get_preview(self) -> str:
        """Aperçu des effets"""
        return f"🛡️ {self.name}: +{self.parade_bonus} jetons de parade permanent (Coût: {self.spell_cost} sort)"


@register_ability
class LiarieMurDeGlace(BaseAbility):
    """P-2-3: Mur de glace - Gèle les ennemis (effet stun) - VERSION CORRIGÉE"""
    
    hero_code = "P-2"
    ability_number = 3
    name = "Mur de glace"
    description = "Gêles les ennemis, leur faisant perdre leur action pendant 1 tour."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 1  # ✅ Correct selon Sorts.xlsx
        self.uses_per_combat = 2  # ✅ LIMITATION AJOUTÉE selon Sorts.xlsx
        self.uses_remaining_combat = 2  # Initialisé au maximum
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Lance un mur de glace qui gèle les ennemis"""
        try:
            # Vérifier le coût en sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # Vérifier les utilisations restantes
            if self.uses_remaining_combat <= 0:
                log.append(f"❄️ {caster.name} ne peut plus utiliser {self.name} (épuisé: {self.uses_per_combat}/combat)")
                return False
            
            # Récupérer tous les ennemis vivants
            enemies = self._get_all_enemies(caster, context)

            if not enemies:
                log.append(f"❄️ {caster.name} invoque un mur de glace mais il n'y a aucun ennemi !")
                self.uses_remaining_combat -= 1
                return True

            # Appliquer l'effet de gel (stun) à tous les ennemis
            frozen_count = 0
            for enemy in enemies:
                # Ajouter l'effet stun pour le prochain tour
                if not hasattr(enemy, 'status_effects'):
                    enemy.status_effects = {}
                enemy.status_effects['stunned'] = {
                    'duration': 1,
                    'source': 'liarie_blizzard'
                }
                frozen_count += 1

            log.append(f"❄️ {caster.name} invoque un {self.name} !")
            log.append(f"   🧊 {frozen_count} ennemi(s) gelé(s) - perdront leur prochaine action")

            # Décompter l'utilisation
            self.uses_remaining_combat -= 1
            remaining = self.uses_remaining_combat
            log.append(f"   📊 Utilisations restantes: {remaining}/{self.uses_per_combat}")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur mur de glace: {str(e)}")
            return False
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        """Vérifie si le mur de glace peut être invoqué"""
        if caster.code != "P-2":
            return False
        
        # Vérifier les utilisations restantes  
        if hasattr(self, 'uses_remaining_combat') and self.uses_remaining_combat is not None:
            if self.uses_remaining_combat <= 0:
                return False
        
        # Vérifier le coût en sorts
        return caster.current_spells >= self.spell_cost
    
    def get_preview(self) -> str:
        """Aperçu des effets"""
        remaining = getattr(self, 'uses_remaining_combat', self.uses_per_combat)
        return f"❄️ {self.name}: Gèle tous les ennemis (stun 1 tour) - {remaining}/{self.uses_per_combat} utilisations (Coût: {self.spell_cost} sort)"


@register_ability
class LiarieBouleDeFeu(BaseAbility):
    """P-2-4: Boule de feu - 6 dégâts magiques à tous sans riposte - VERSION CORRIGÉE"""
    
    hero_code = "P-2"
    ability_number = 4
    name = "Boule de feu"
    description = "Inflige 6 dégâts magiques à tous les adversaires."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 2  # ✅ Correct selon Sorts.xlsx
        self.damage_amount = 6  # ✅ Correct selon Sorts.xlsx
        self.uses_per_combat = 1  # ✅ LIMITATION AJOUTÉE selon Sorts.xlsx
        self.uses_remaining_combat = 1
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Lance une boule de feu explosive contre tous les ennemis"""
        try:
            # Vérifier le coût en sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # Vérifier les utilisations restantes
            if self.uses_remaining_combat <= 0:
                log.append(f"🔥 {caster.name} ne peut plus utiliser {self.name} (épuisé: {self.uses_per_combat}/combat)")
                return False
            
            # Récupérer tous les ennemis
            all_enemies = self._get_all_enemies(caster, context)
            
            if not all_enemies:
                log.append(f"🔥 {caster.name} lance une boule de feu mais il n'y a aucun ennemi !")
                self.uses_remaining_combat -= 1
                return True
            
            results = []
            
            for enemy in all_enemies:
                # Infliger dégâts de feu (sans riposte possible)
                damage_dealt = self._apply_damage(enemy, self.damage_amount, "magical", log)
                results.append(f"{enemy.name}: {damage_dealt} dégâts")
            
            log.append(f"🔥 {caster.name} lance une boule de feu explosive !")
            log.append(f"   Dégâts: " + ", ".join(results))
            log.append(f"   (Sans possibilité de riposte)")
            
            # Décompter l'utilisation
            self.uses_remaining_combat -= 1
            remaining = self.uses_remaining_combat
            log.append(f"   📊 Utilisations restantes: {remaining}/{self.uses_per_combat}")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur boule de feu: {str(e)}")
            return False
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        """Vérifie si la boule de feu peut être lancée"""
        if caster.code != "P-2":
            return False
        
        # Vérifier les utilisations restantes
        if hasattr(self, 'uses_remaining_combat') and self.uses_remaining_combat is not None:
            if self.uses_remaining_combat <= 0:
                return False
        
        return caster.current_spells >= self.spell_cost
    
    def get_preview(self) -> str:
        """Aperçu des effets"""
        remaining = getattr(self, 'uses_remaining_combat', self.uses_per_combat)
        return f"🔥 {self.name}: {self.damage_amount} dégâts magiques à tous - {remaining}/{self.uses_per_combat} utilisations (Coût: {self.spell_cost} sorts)"


@register_ability
class LiarieVolDeVie(BaseAbility):
    """P-2-5: Vol de vie - 4 dégâts magiques + soins équivalents sans riposte"""
    
    hero_code = "P-2"
    ability_number = 5
    name = "Vol de vie"
    description = "Inflige 4 dégâts magiques à 1 ennemi, et soigne Liarie de 4 blessures."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 2  # ✅ Correct selon Sorts.xlsx
        self.damage_amount = 4  # ✅ Correct selon Sorts.xlsx
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Draine la vie d'un ennemi pour se soigner"""
        try:
            # Vérifier le coût en sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # Récupérer les ennemis
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
    """P-2-6: Pluie de météores - 10 dégâts magiques à tous + stun - VERSION CORRIGÉE"""
    
    hero_code = "P-2"
    ability_number = 6
    name = "Pluie de météores"
    description = "Inflige 10 dégâts magiques à tous les adversaires."
    
    def __init__(self):
        super().__init__(self.hero_code, self.ability_number, self.name, self.description)
        self.spell_cost = 2  # ✅ Correct selon Sorts.xlsx  
        self.damage_amount = 10  # ✅ Correct selon Sorts.xlsx
        self.uses_per_combat = 1  # ✅ LIMITATION AJOUTÉE selon Sorts.xlsx
        self.uses_remaining_combat = 1
    
    def execute(self, caster, targets: List, context: Dict[str, Any], log: List[str]) -> bool:
        """Invoque une pluie de météores dévastatrice"""
        try:
            # Vérifier le coût en sorts
            spell_manager = context.get('spell_manager')
            if not self._consume_spell_cost(caster, self.spell_cost, spell_manager, log):
                return False
            
            # Vérifier les utilisations restantes
            if self.uses_remaining_combat <= 0:
                log.append(f"☄️ {caster.name} ne peut plus utiliser {self.name} (épuisé: {self.uses_per_combat}/combat)")
                return False
            
            # Récupérer tous les ennemis
            all_enemies = self._get_all_enemies(caster, context)
            
            if not all_enemies:
                log.append(f"☄️ {caster.name} invoque une pluie de météores mais il n'y a aucun ennemi !")
                self.uses_remaining_combat -= 1
                return True
            
            results = []
            
            for enemy in all_enemies:
                # Infliger dégâts magiques massifs
                damage_dealt = self._apply_damage(enemy, self.damage_amount, "magical", log)
                results.append(f"{enemy.name}: {damage_dealt} dégâts")
            
            log.append(f"☄️ {caster.name} invoque une pluie de météores dévastatrice !")
            log.append(f"   Dégâts: " + ", ".join(results))
            
            # Décompter l'utilisation
            self.uses_remaining_combat -= 1
            remaining = self.uses_remaining_combat
            log.append(f"   📊 Utilisations restantes: {remaining}/{self.uses_per_combat}")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Erreur pluie de météores: {str(e)}")
            return False
    
    def can_execute(self, caster, context: Dict[str, Any]) -> bool:
        """Vérifie si la pluie de météores peut être invoquée"""
        if caster.code != "P-2":
            return False
        
        # Vérifier les utilisations restantes
        if hasattr(self, 'uses_remaining_combat') and self.uses_remaining_combat is not None:
            if self.uses_remaining_combat <= 0:
                return False
        
        return caster.current_spells >= self.spell_cost
    
    def get_preview(self) -> str:
        """Aperçu des effets"""
        remaining = getattr(self, 'uses_remaining_combat', self.uses_per_combat)
        return f"☄️ {self.name}: {self.damage_amount} dégâts magiques à tous - {remaining}/{self.uses_per_combat} utilisations (Coût: {self.spell_cost} sorts)"


# ========================================
# FONCTIONS UTILITAIRES ET STATISTIQUES
# ========================================

def get_liarie_abilities_count() -> int:
    """Retourne le nombre de capacités de Liarie enregistrées"""
    return 6


def get_liarie_abilities_summary() -> str:
    """Retourne un résumé des capacités de Liarie - VERSION CORRIGÉE"""
    return """
    🎭 LIARIE (P-2) - 6 capacités corrigées selon Sorts.xlsx:
    ✅ P-2-1: Éclair magique (4 dégâts magiques répartis, coût 1)
    ✅ P-2-2: Armure du mage (+2 parade permanent, coût 1)
    ✅ P-2-3: Mur de glace (gel/stun tous ennemis, coût 1, 2/combat)
    ✅ P-2-4: Boule de feu (6 dégâts à tous, coût 2, 1/combat)
    ✅ P-2-5: Vol de vie (4 dégâts + soins équivalents, coût 2)
    ✅ P-2-6: Pluie de météores (10 dégâts à tous, coût 2, 1/combat)
    """


def get_liarie_spell_costs() -> dict:
    """Retourne les coûts en sorts des capacités de Liarie selon Sorts.xlsx"""
    return {
        "Éclair magique": 1,     # ✅ Correct
        "Armure du mage": 1,     # ✅ Correct
        "Mur de glace": 1,       # ✅ Correct
        "Boule de feu": 2,       # ✅ Correct
        "Vol de vie": 2,         # ✅ Correct
        "Pluie de météores": 2   # ✅ Correct
    }


def get_liarie_damage_output() -> dict:
    """Retourne les dégâts potentiels des sorts offensifs selon Sorts.xlsx"""
    return {
        "Éclair magique": {"distributed": 4, "type": "magical"},
        "Mur de glace": {"all_enemies": "stun", "type": "magical", "limitation": "2/combat"},
        "Boule de feu": {"all_enemies": 6, "type": "magical", "limitation": "1/combat"},
        "Vol de vie": {"single": 4, "type": "magical", "healing": 4},
        "Pluie de météores": {"all_enemies": 10, "type": "magical", "limitation": "1/combat"}
    }


def get_liarie_tactical_analysis() -> dict:
    """Analyse tactique des capacités de Liarie selon données officielles"""
    return {
        "role": "Mage élémentaire - DPS/Support/Control",
        "strengths": [
            "Dégâts magiques excellents (sans riposte)",
            "Contrôle de zone (stun avec Mur de glace)", 
            "Auto-sustain avec Vol de vie",
            "Protection permanente avec Armure du mage",
            "Ultimates puissants avec limitations"
        ],
        "spell_efficiency": {
            "low_cost_versatile": ["Éclair magique", "Armure du mage", "Mur de glace"],
            "medium_cost_power": ["Boule de feu", "Vol de vie", "Pluie de météores"]
        },
        "combat_strategy": {
            "early": "Armure du mage + Mur de glace (contrôle)",
            "mid": "Éclair magique + Vol de vie (damage/heal)",
            "late": "Boule de feu / Pluie de météores (finisher)"
        },
        "limitations": {
            "Mur de glace": "2/combat",
            "Boule de feu": "1/combat", 
            "Pluie de météores": "1/combat"
        }
    }