"""
Modèles de personnages pour le Simulateur Périples
VERSION INTÉGRÉE COMPLÈTE avec système d'effets de capacités
🛡️ Parade = jetons rechargeable à chaque tour (héros ET ennemis)
🩸 Potions de santé dans builds custom
🎭 O-4 (Lyre phoenix) : +4 sorts + attaques magiques pour Stèphe
🔮 Gestion sorts conforme aux règles officielles
⚡ Système d'effets persistants intégré
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
from .abilities import Ability, AbilityAction, AbilityType, AbilityManager

class VirtualAbility:
    """
    Capacité virtuelle pour invocations - Évite les contraintes Pydantic
    Compatible avec le système Ability mais sans validation stricte
    """
    def __init__(self, hero_code: str, name: str, description: str):
        self.hero_code = hero_code
        self.ability_number = 99  # Numéro spécial hors contraintes
        self.name = name
        self.spell_cost = 0
        self.description = description
        self.is_unlocked = True
        self.unique_id = f"{hero_code}_summon"
        self.prevents_attack = False
        self.target_type = "self"
        self.effects = []
    
    @property
    def ability_type(self):
        """Type physique car coût 0"""
        return AbilityType.PHYSICAL
    
    def can_use(self, current_spells: Optional[int]) -> tuple[bool, str]:
        """Toujours utilisable (pas de coût)"""
        return True, "Utilisable"
    
    def use_ability(self) -> bool:
        """Toujours réussit"""
        return True
    
    def reset_combat_uses(self):
        """Rien à reset pour invocation"""
        pass

class PotionType(Enum):
    """Types de potions de santé"""
    SMALL = "small"    # 🩸 Petite Potion - 4 PV
    LARGE = "large"    # ❤️‍🩹 Grande Potion - PV max

class HealthPotion(BaseModel):
    """Potion de santé consommable"""
    
    potion_type: PotionType
    quantity: int = Field(1, ge=0)
    
    @property
    def name(self) -> str:
        return "Petite Potion" if self.potion_type == PotionType.SMALL else "Grande Potion"
    
    @property
    def icon(self) -> str:
        return "🩸" if self.potion_type == PotionType.SMALL else "❤️‍🩹"
    
    @property
    def heal_amount(self) -> int:
        """4 PV pour petite, 0 pour grande (= PV max)"""
        return 4 if self.potion_type == PotionType.SMALL else 0
    
    @property
    def is_full_heal(self) -> bool:
        return self.potion_type == PotionType.LARGE
    
    def can_use(self) -> bool:
        return self.quantity > 0
    
    def use_potion(self) -> bool:
        """Consomme une potion"""
        if self.quantity > 0:
            self.quantity -= 1
            return True
        return False

class Character(BaseModel):
    """Héros avec système de jetons parade rechargeable + effets spéciaux + gestion sorts + effets persistants"""
    
    # Stats de base
    code: str
    name: str
    precision: int
    damage: int
    spells: int
    health: int
    current_health: Optional[int] = None
    
    # === STATS MODIFIABLES PAR CAPACITÉS ===
    current_attack: Optional[int] = None
    current_defense: Optional[int] = None
    current_precision: Optional[int] = None
    current_magical_damage: Optional[int] = None

    # Équipements
    equipped_items: List['Equipment'] = []
    build_name: Optional[str] = None
    
    # Combat
    current_spells: Optional[int] = None
    spells_used: int = 0
    
    # NOUVEAU - Gestion sorts conforme aux règles
    magic_abilities_used_this_turn: int = 0
    
    # Système de jetons parade
    max_parade_tokens: int = 0
    current_parade_tokens: int = 0
    
    # Capacités
    abilities: List[Ability] = Field(default_factory=list)
    unlocked_abilities: List[int] = Field(default_factory=list)
    
    # Potions
    health_potions: List[HealthPotion] = Field(default_factory=list)
    
    # État du tour
    action_taken_this_turn: bool = False
    ability_used_this_turn: Optional[Ability] = None
    can_attack_this_turn: bool = True
    attack_done_this_turn: bool = False  # NOUVEAU - Pour bloquer capacités magiques après attaque (règle p.24)
    potion_used_this_turn: bool = False
    
    # Système de formes pour Elneha
    current_form: Optional[str] = None  # "bear", "wolf", "human"
    
    # === NOUVEAUX ATTRIBUTS POUR SYSTÈME D'EFFETS ===
    # Effets persistants actifs
    active_persistent_effects: List[Any] = Field(default_factory=list)
    
    # Buffs temporaires (pour une action/attaque)
    temporary_buffs: Dict[str, Any] = Field(default_factory=dict)
    
    # Buffs permanents (pour tout le combat)
    permanent_buffs: Dict[str, Any] = Field(default_factory=dict)
    
    # Flags d'attaque spéciaux
    attack_flags: Dict[str, Any] = Field(default_factory=dict)
    
    # Debuffs subis
    debuffs: Dict[str, Any] = Field(default_factory=dict)
    
    # Effets de statut
    status_effects: Dict[str, Any] = Field(default_factory=dict)
    
    # Marques appliquées (pour systèmes comme Kraor)
    marks: Dict[str, Any] = Field(default_factory=dict)
    
    def model_post_init(self, __context):
        """Initialisation avec système d'effets"""
        if self.current_health is None:
            self.current_health = self.health
        
        if self.abilities and not self.unlocked_abilities:
            self.unlock_ability(1)
        
        if not self.health_potions:
            self.add_default_potions()
        
        # Initialiser parade selon équipements
        self._update_parade_from_equipment()
        
        # Initialiser forme pour Elneha
        if self.code == "P-1":
            self.current_form = "human"
        
        # NOUVEAU - Initialiser attributs sorts
        if not hasattr(self, 'magic_abilities_used_this_turn'):
            self.magic_abilities_used_this_turn = 0
        if not hasattr(self, 'spells_used'):
            self.spells_used = 0
        
        # INTÉGRATION - Ajouter attributs système d'effets
        self._add_required_attributes()
    
    def _add_required_attributes(self):
        """Ajoute les attributs nécessaires pour le système d'effets"""
        # Effets persistants actifs
        if not hasattr(self, 'active_persistent_effects'):
            self.active_persistent_effects = []
        
        # Buffs temporaires (pour une action/attaque)
        if not hasattr(self, 'temporary_buffs'):
            self.temporary_buffs = {}
        
        # Buffs permanents (pour tout le combat)
        if not hasattr(self, 'permanent_buffs'):
            self.permanent_buffs = {}
        
        # Flags d'attaque spéciaux
        if not hasattr(self, 'attack_flags'):
            self.attack_flags = {}
        
        # Debuffs subis
        if not hasattr(self, 'debuffs'):
            self.debuffs = {}
        
        # Effets de statut
        if not hasattr(self, 'status_effects'):
            self.status_effects = {}
        
        # Marques appliquées (pour systèmes comme Kraor)
        if not hasattr(self, 'marks'):
            self.marks = {}
    
    # === SYSTÈME OBJETS SPÉCIAUX ===
    
    def has_equipment(self, equipment_code: str) -> bool:
        """Vérifie si le héros porte un équipement spécifique"""
        return any(item.code == equipment_code for item in self.equipped_items)
    
    def get_special_equipment_effects(self) -> Dict[str, bool]:
        """Retourne les effets spéciaux actifs"""
        effects = {
            'lyre_phoenix': False,      # O-4 - Stèphe attaques magiques
            'gemme_pouvoir': False,     # O-1 - Elneha formes magiques  
            'baton_puissance': False,   # O-2 - Liarie +1 capacités
            'medaillon_appel': False    # O-3 - Kraor invocation Pet
        }
        
        # O-4 Lyre phoenix - Stèphe (P-6)
        if self.code == "P-6" and self.has_equipment("O-4"):
            effects['lyre_phoenix'] = True
        
        # O-1 Gemme de pouvoir - Elneha (P-1)  
        if self.code == "P-1" and self.has_equipment("O-1"):
            effects['gemme_pouvoir'] = True
        
        # O-2 Baton de puissance - Liarie (P-2)
        if self.code == "P-2" and self.has_equipment("O-2"):
            effects['baton_puissance'] = True
        
        # O-3 Médaillon d'appel - Kraor (P-4)
        if self.code == "P-4" and self.has_equipment("O-3"):
            effects['medaillon_appel'] = True
        
        return effects
    
    def has_magical_attacks(self) -> bool:
        """Vérifie si les attaques sont magiques (O-4 Lyre phoenix)"""
        effects = self.get_special_equipment_effects()
        return effects['lyre_phoenix']
    
    # === SYSTÈME DE FORMES (ELNEHA) ===
    
    def set_form(self, form: str):
        """Change la forme actuelle (pour Elneha)"""
        if self.code == "P-1":  # Seule Elneha peut changer de forme
            self.current_form = form
    
    def get_form_display(self) -> str:
        """Affichage de la forme actuelle"""
        if self.code != "P-1":
            return ""
        
        form_names = {
            "bear": "🐻 Forme d'ours",
            "wolf": "🐺 Forme de loup", 
            "human": "👤 Forme humaine"
        }
        return form_names.get(self.current_form, "👤 Forme humaine")
    
    def has_magical_form_attacks(self) -> bool:
        """O-1 Gemme de pouvoir : formes d'ours/loup → attaques magiques"""
        return (self.code == "P-1" and 
                self.has_equipment("O-1") and 
                self.current_form in ["bear", "wolf"])
    
    def get_form_status(self) -> Dict:
        """État des formes pour interface"""
        if self.code != "P-1":
            return {'has_forms': False}
        
        return {
            'has_forms': True,
            'current_form': self.current_form,
            'display_name': self.get_form_display(),
            'has_gemme_pouvoir': self.has_equipment("O-1"),
            'has_magical_attacks': self.has_magical_form_attacks()
        }
    
    # === SYSTÈME D'INVOCATION (KRAOR) ===
    
    def can_summon_pet(self) -> bool:
        """Vérifie si le héros peut invoquer un Pet"""
        return self.code == "P-4" and self.has_equipment("O-3")
    
    def summon_pet(self) -> Optional['Pet']:
        """Invoque un Pet selon l'objet équipé"""
        if not self.can_summon_pet():
            return None
        
        # Kraor avec O-3 Médaillon d'appel
        if self.code == "P-4" and self.has_equipment("O-3"):
            return Pet.create_kraor_pet(self)
        
        return None
    
    def get_summon_status(self) -> Dict:
        """État des capacités d'invocation"""
        return {
            'can_summon': self.can_summon_pet(),
            'summon_type': 'pet' if self.can_summon_pet() else None,
            'has_medaillon_appel': self.has_equipment("O-3") if self.code == "P-4" else False
        }
    
    # === SYSTÈME JETONS PARADE (VERSION AMÉLIORÉE) ===
    
    def _update_parade_from_equipment(self):
        """Met à jour la parade max selon les équipements"""
        self.max_parade_tokens = self.get_equipment_bonus('defense')
        # Parade actuelle = max au début du combat
        self.current_parade_tokens = self.max_parade_tokens
    
    def get_total_parade(self) -> int:
        """Version améliorée pour calculer la parade max avec bonus persistants + temporaires"""
        # Parade de base
        base_parade = self.get_equipment_bonus('defense')

        # Bonus persistants
        persistent_bonus = 0
        if hasattr(self, 'active_persistent_effects'):
            try:
                from models.combat.abilities.persistent_effects import PersistentEffectsSystem
                persistent_system = PersistentEffectsSystem()
                persistent_bonus = persistent_system.get_parade_bonus(self)
            except ImportError:
                pass

        # Buffs permanents
        permanent_bonus = 0
        if hasattr(self, 'permanent_buffs'):
            if self.permanent_buffs.get('defense_sans_armure', False):
                permanent_bonus += 1

        # NOUVEAU - Buffs temporaires (Parade d'Atucan, Armure du Mage de Liarie, etc.)
        temporary_bonus = 0
        if hasattr(self, 'temporary_buffs'):
            temporary_bonus = self.temporary_buffs.get('temporary_defense_bonus', 0)

            # ARMURE DU MAGE - Bonus permanent parade (calculé depuis max_parade_tokens modifié)
            if self.temporary_buffs.get('armure_mage_active', False):
                # Armure du Mage ajoute +2 à max_parade_tokens
                # On doit refléter ça dans l'affichage
                armure_bonus = self.max_parade_tokens - base_parade - persistent_bonus - permanent_bonus
                temporary_bonus += max(0, armure_bonus)  # S'assurer que c'est positif

        # PARADE D'ATUCAN - Si actif, utiliser max_parade_tokens directement
        if hasattr(self, 'temporary_buffs') and 'parade_original_max' in self.temporary_buffs:
            # Parade d'Atucan est actif, retourner la valeur modifiée directement
            return self.max_parade_tokens

        return base_parade + persistent_bonus + permanent_bonus + temporary_bonus
    
    def refresh_parade_tokens(self):
        """Version améliorée de refresh_parade_tokens qui gère les effets persistants"""
        # Recharge normale
        self.current_parade_tokens = self.max_parade_tokens
        
        # Appliquer effets persistants sur la parade
        if hasattr(self, 'active_persistent_effects'):
            try:
                from models.combat.abilities.persistent_effects import PersistentEffectsSystem
                persistent_system = PersistentEffectsSystem()
                persistent_system.apply_parade_refresh_effects(self)
            except ImportError:
                pass
    
    def consume_parade_tokens(self, damage: int) -> tuple[int, int]:
        """
        Consomme les jetons parade contre les dégâts
        
        Args:
            damage: Dégâts entrants
            
        Returns:
            tuple[int, int]: (dégâts bloqués, dégâts restants)
        """
        if damage <= 0:
            return 0, 0
        
        # Les jetons parade bloquent 1 dégât chacun
        blocked_damage = min(damage, self.current_parade_tokens)
        remaining_damage = damage - blocked_damage
        
        # Consommation des jetons
        self.current_parade_tokens -= blocked_damage
        
        return blocked_damage, remaining_damage
    
    def apply_damage_with_parade(self, damage: int, ignore_parade: bool = False) -> Dict:
        """
        Applique dégâts avec système parade à jetons

        Args:
            damage: Montant des dégâts
            ignore_parade: Si True, bypass complètement la parade (dégâts magiques)

        Returns:
            Dict avec détails de l'application des dégâts
        """
        # NOUVEAU : Vérifier esquive (Lame Attaque sournoise, Raishi Maîtrise absolue)
        dodge_negated = False
        if hasattr(self, 'temporary_buffs') and self.temporary_buffs:
            # Lame Attaque sournoise : Esquive 1 attaque
            if 'lame_dodge_ready' in self.temporary_buffs:
                dodge_data = self.temporary_buffs['lame_dodge_ready']
                if isinstance(dodge_data, dict) and dodge_data.get('charges', 0) > 0:
                    dodge_negated = True
                    dodge_data['charges'] -= 1
                    if dodge_data['charges'] <= 0:
                        self.temporary_buffs.pop('lame_dodge_ready', None)

            # Raishi Maîtrise absolue : Absorbe 2 attaques (permanent combat, auto-recharge)
            elif 'raishi_maitrise_charges' in self.temporary_buffs:
                maitrise_data = self.temporary_buffs['raishi_maitrise_charges']
                if isinstance(maitrise_data, dict) and maitrise_data.get('charges', 0) > 0:
                    dodge_negated = True
                    maitrise_data['charges'] -= 1
                    # ✅ NE PAS supprimer le buff - il se recharge automatiquement chaque tour
                    # Le buff reste actif tout le combat grâce à 'permanent_combat' + 'auto_recharge'
                elif isinstance(maitrise_data, int) and maitrise_data > 0:
                    # Legacy : charges directement en int
                    dodge_negated = True
                    self.temporary_buffs['raishi_maitrise_charges'] -= 1
                    # ✅ NE PAS supprimer le buff legacy non plus

        if dodge_negated:
            # Annuler complètement les dégâts (esquive parfaite)
            return {
                'total_damage': damage,
                'blocked_by_parade': 0,
                'health_damage': 0,
                'parade_tokens_used': 0,
                'parade_tokens_remaining': self.current_parade_tokens,
                'dodged': True  # Nouveau flag
            }

        # NOUVEAU : Vérifier buff aura_protection (Aura sacrée d'Atucan)
        aura_reduction = 0
        if hasattr(self, 'temporary_buffs') and 'aura_protection' in self.temporary_buffs:
            aura_info = self.temporary_buffs['aura_protection']
            if aura_info.get('type') == 'per_attack':
                aura_reduction = aura_info.get('damage_reduction', 0)
                damage = max(0, damage - aura_reduction)  # Réduire les dégâts AVANT parade

        if damage <= 0:
            return {
                'total_damage': damage + aura_reduction,  # Montant original
                'blocked_by_parade': 0,
                'health_damage': 0,
                'parade_tokens_used': 0,
                'parade_tokens_remaining': self.current_parade_tokens,
                'aura_reduction': aura_reduction  # Pour le log
            }

        if ignore_parade:
            # Bypass complet de la parade (dégâts magiques)
            blocked = 0
            remaining = damage
        else:
            # Logique normale avec parade
            blocked, remaining = self.consume_parade_tokens(damage)

        # Dégâts aux PV
        old_health = self.current_health
        self.current_health = max(0, self.current_health - remaining)
        actual_health_damage = old_health - self.current_health

        return {
            'total_damage': damage + aura_reduction,  # Montant original avant réduction aura
            'blocked_by_parade': blocked,
            'health_damage': actual_health_damage,
            'parade_tokens_used': blocked,
            'parade_tokens_remaining': self.current_parade_tokens,
            'aura_reduction': aura_reduction  # Pour le log
        }
    
    def get_parade_status(self) -> Dict:
        """État actuel du système parade"""
        return {
            'max_tokens': self.max_parade_tokens,
            'current_tokens': self.current_parade_tokens,
            'has_parade': self.max_parade_tokens > 0,
            'parade_percentage': round((self.current_parade_tokens / self.max_parade_tokens * 100), 1) if self.max_parade_tokens > 0 else 0
        }
    
    # === POTIONS ===
    
    def add_default_potions(self):
        """Ajoute 1 Petite Potion par défaut"""
        self.health_potions = [HealthPotion(potion_type=PotionType.SMALL, quantity=1)]
    
    def set_custom_potions(self, potions_config: List[Dict]):
        """Configure potions pour build custom"""
        self.health_potions = []
        
        for config in potions_config:
            potion_type = PotionType.SMALL if config['type'] == 'small' else PotionType.LARGE
            quantity = min(3, max(0, config['quantity']))
            
            if quantity > 0:
                potion = HealthPotion(potion_type=potion_type, quantity=quantity)
                self.health_potions.append(potion)
    
    def set_potions_from_selection(self, small_count: int = 0, large_count: int = 0):
        """Configuration simple depuis interface Forge"""
        self.health_potions = []
        
        small_count = min(3, max(0, small_count))
        if small_count > 0:
            small_potion = HealthPotion(potion_type=PotionType.SMALL, quantity=small_count)
            self.health_potions.append(small_potion)
        
        large_count = min(1, max(0, large_count))
        if large_count > 0:
            large_potion = HealthPotion(potion_type=PotionType.LARGE, quantity=large_count)
            self.health_potions.append(large_potion)
    
    def get_potion_by_type(self, potion_type: PotionType) -> Optional[HealthPotion]:
        """Trouve une potion utilisable du type demandé"""
        for potion in self.health_potions:
            if potion.potion_type == potion_type and potion.can_use():
                return potion
        return None
    
    def can_use_potion(self) -> tuple[bool, str]:
        """Vérifie si une potion peut être utilisée"""
        if self.is_at_full_health():
            return False, "Santé déjà au maximum"
        
        available = any(p.can_use() for p in self.health_potions)
        if not available:
            return False, "Aucune potion disponible"
        
        return True, "Potion utilisable"
    
    def use_health_potion(self) -> Dict:
        """Utilise automatiquement la meilleure potion"""
        result = {
            'success': False,
            'potion_used': None,
            'healing_done': 0,
            'message': '',
            'prevents_attack': False
        }
        
        can_use, reason = self.can_use_potion()
        if not can_use:
            result['message'] = reason
            return result
        
        # Choix intelligent
        potion_type = self._choose_best_potion()
        if not potion_type:
            result['message'] = "Aucune potion appropriée"
            return result
        
        # Utilisation
        potion = self.get_potion_by_type(potion_type)
        if not potion or not potion.use_potion():
            result['message'] = "Échec utilisation potion"
            return result
        
        # Soins
        if potion.is_full_heal:
            old_health = self.current_health
            self.current_health = self.get_total_health()
            healing = self.current_health - old_health
        else:
            healing = self.heal(potion.heal_amount)
        
        self.potion_used_this_turn = True
        
        result.update({
            'success': True,
            'potion_used': potion.name,
            'potion_icon': potion.icon,
            'healing_done': healing,
            'message': f"{potion.icon} {potion.name} utilisée : +{healing} PV"
        })
        
        return result
    
    def use_specific_potion(self, potion_type: PotionType, target: Optional['Character'] = None) -> Dict:
        """
        Utilise une potion spécifique du type demandé

        Args:
            potion_type: Type de potion à utiliser (SMALL ou LARGE)
            target: Cible de la potion (self par défaut, ou autre héros pour "faire boire")

        Returns:
            Dict avec détails de l'utilisation
        """
        result = {
            'success': False,
            'potion_used': None,
            'healing_done': 0,
            'message': '',
            'prevents_attack': False,
            'target_name': target.name if target else self.name
        }

        # Vérifier disponibilité de la potion
        potion = self.get_potion_by_type(potion_type)
        if not potion or not potion.can_use():
            result['message'] = f"{potion_type.value.capitalize()} potion non disponible"
            return result

        # Cible par défaut = soi-même
        if target is None:
            target = self

        # Vérifier si la cible peut bénéficier de la potion
        if target.is_at_full_health():
            result['message'] = f"{target.name} a déjà sa santé au maximum"
            return result

        # Consommer la potion
        if not potion.use_potion():
            result['message'] = "Échec utilisation potion"
            return result

        # Appliquer les soins sur la cible
        if potion.is_full_heal:
            old_health = target.current_health
            target.current_health = target.get_total_health()
            healing = target.current_health - old_health
        else:
            healing = target.heal(potion.heal_amount)

        # Marquer l'action comme effectuée pour le donneur
        self.potion_used_this_turn = True

        result.update({
            'success': True,
            'potion_used': potion.name,
            'potion_icon': potion.icon,
            'healing_done': healing,
            'message': f"{potion.icon} {potion.name} utilisée sur {target.name} : +{healing} PV"
        })

        return result

    def _choose_best_potion(self) -> Optional[PotionType]:
        """IA : Choisit la meilleure potion"""
        health_percent = (self.current_health / self.get_total_health()) * 100

        # Critique : Grande potion
        if health_percent < 25:
            if self.get_potion_by_type(PotionType.LARGE):
                return PotionType.LARGE

        # Normal : Petite potion
        if health_percent < 75:
            if self.get_potion_by_type(PotionType.SMALL):
                return PotionType.SMALL

        # Fallback
        for potion in self.health_potions:
            if potion.can_use():
                return potion.potion_type

        return None
    
    def get_potions_summary(self) -> Dict:
        """Résumé potions pour affichage interface"""
        small_total = sum(p.quantity for p in self.health_potions if p.potion_type == PotionType.SMALL)
        large_total = sum(p.quantity for p in self.health_potions if p.potion_type == PotionType.LARGE)
        total = small_total + large_total
        
        parts = []
        if small_total > 0:
            parts.append(f"🩸 {small_total} Petite{'s' if small_total > 1 else ''}")
        if large_total > 0:
            parts.append(f"❤️‍🩹 {large_total} Grande{'s' if large_total > 1 else ''}")
        
        return {
            'has_potions': total > 0,
            'total_count': total,
            'small_count': small_total,
            'large_count': large_total,
            'display_text': ", ".join(parts) if parts else "Aucune potion",
            'display_short': f"🧪 {total}" if total > 0 else "🧪 0"
        }
    
    def get_potions_for_forge_display(self) -> Dict:
        """Format spécial pour interface Forge"""
        summary = self.get_potions_summary()
        
        return {
            'small_count': summary['small_count'],
            'large_count': summary['large_count'],
            'total_display': summary['display_text'],
            'preview_text': f"🧪 Potions: {summary['display_text']}" if summary['has_potions'] else "🧪 Aucune potion sélectionnée"
        }
    
    # === SANTÉ ===
    
    def is_alive(self) -> bool:
        return self.current_health > 0
    
    def heal(self, heal_amount: int) -> int:
        """Soigne et retourne le montant réellement soigné"""
        if heal_amount <= 0:
            return 0
        
        max_health = self.get_total_health()
        old_health = self.current_health
        self.current_health = min(max_health, self.current_health + heal_amount)
        
        return self.current_health - old_health
    
    def is_at_full_health(self) -> bool:
        return self.current_health >= self.get_total_health()
    
    def reset_health(self):
        """MODIFIÉ - Reset santé + attributs sorts"""
        self.current_health = self.get_total_health()
        
        # NOUVEAU - Initialiser attributs sorts si pas encore fait
        if not hasattr(self, 'magic_abilities_used_this_turn'):
            self.magic_abilities_used_this_turn = 0
        if not hasattr(self, 'spells_used'):
            self.spells_used = 0
            
    def reset_current_stats(self):
        """Remet les stats à leur valeur de base (pour nouveau combat)"""
        self.current_attack = self.damage
        self.current_defense = self.max_parade_tokens  # ← Utilise la parade max
        self.current_precision = self.precision
        
        # Reset forme pour Elneha
        if self.code == "P-1":
            self.current_form = "human"
    
    # === ÉQUIPEMENTS ===
    
    def equip_items(self, items: List['Equipment'], build_name: str = None):
        self.equipped_items = items
        self.build_name = build_name
        if self.current_health == self.health:
            self.reset_health()
        # Mise à jour parade
        self._update_parade_from_equipment()
    
    def get_equipment_bonus(self, stat_type: str) -> int:
        total = 0
        for item in self.equipped_items:
            if stat_type == 'precision':
                total += item.precision if item.precision is not None else 0
            elif stat_type == 'physical_damage':
                total += item.physical_damage if item.physical_damage is not None else 0
            elif stat_type == 'magical_damage':
                total += item.magical_damage if item.magical_damage is not None else 0
            elif stat_type == 'defense':
                total += item.defense if item.defense is not None else 0
            elif stat_type == 'spells':
                total += item.spells if item.spells is not None else 0
            elif stat_type == 'health':
                total += item.health if item.health is not None else 0
        return total
    
    def get_total_damage(self) -> int:
        """Version améliorée de get_total_damage qui inclut les bonus d'effets"""
        
        # NOUVEAU - Utiliser current_attack si disponible (stats modifiées par capacités)
        base_attack = getattr(self, 'current_attack', self.damage)
        if base_attack is None:
            base_attack = 0
        
        # DÉgâts de base avec équipements
        base_damage = base_attack + self.get_equipment_bonus('physical_damage')
        
        # Bonus des effets persistants
        persistent_bonus = 0
        if hasattr(self, 'active_persistent_effects'):
            try:
                from models.combat.abilities.persistent_effects import PersistentEffectsSystem
                persistent_system = PersistentEffectsSystem()
                persistent_bonus = persistent_system.get_damage_bonus(self)
            except ImportError:
                pass
        
        # Bonus temporaires
        temp_bonus = 0
        if hasattr(self, 'temporary_buffs'):
            temp_bonus = self.temporary_buffs.get('damage_bonus_next_attack', 0)
        
        # Marques sur les ennemis (pour Kraor)
        mark_bonus = self._get_mark_damage_bonus()
        
        return base_damage + persistent_bonus + temp_bonus + mark_bonus

    # AJOUTER AUSSI - Méthode pour get_total_precision modifiée
    def get_total_precision(self) -> int:
        """Version améliorée incluant current_precision"""
        base_precision = getattr(self, 'current_precision', self.precision)
        if base_precision is None:
            base_precision = 0
        equipment_bonus = self.get_equipment_bonus('precision')
        return base_precision + equipment_bonus
    
    def _get_mark_damage_bonus(self) -> int:
        """Calcule le bonus de dégâts contre les ennemis marqués"""
        # Cette méthode sera appelée pendant une attaque pour vérifier
        # si la cible est marquée (implémentation dépend du contexte de combat)
        return 0  # Implémenté dans le moteur de combat
    
    def get_total_magical_damage(self) -> int:
        """Gère la conversion d'attaques pour O-4 Lyre phoenix"""
        base_magical = self.get_equipment_bonus('magical_damage')
        
        # O-4 Lyre phoenix : Stèphe attaques → magiques (conversion, pas addition)
        if self.has_magical_attacks():
            # Conversion : dégâts physiques deviennent magiques
            converted_damage = self.get_total_damage()
            return max(base_magical, converted_damage)  # Prendre le max pour éviter double comptage
        
        return base_magical
    
    def get_total_spells(self) -> int:
            """
            CORRIGÉ: Gère le bonus O-4 Lyre phoenix (+4 sorts) ET respecte current_spells des builds
            Priorité aux sorts calculés par Forge/builds par défaut/debug
            """
            # CORRECTION CRITIQUE: Respecter current_spells si configuré par un build
            if hasattr(self, 'current_spells') and self.current_spells is not None:
                # Utiliser les sorts calculés avec équipements (Forge, builds par défaut, debug)
                return self.current_spells
            
            # Fallback: Calcul automatique (sorts de base + équipements)
            base_spells = self.spells + self.get_equipment_bonus('spells')
            
            # O-4 Lyre phoenix : +4 sorts déjà dans equipment.csv (O-4 a Spells: 4)
            # Pas besoin de bonus supplémentaire ici
            return base_spells
    
    def get_total_health(self) -> int:
        return self.health + self.get_equipment_bonus('health')
    
    def get_attack_damage_info(self) -> Dict:
        """Infos sur le type de dégâts d'attaque (physique ou magique)"""
        # Priorité 1 : O-4 Lyre phoenix (toutes les attaques → magiques)
        if self.has_magical_attacks():
            return {
                'damage_type': 'magical',
                'damage_value': self.get_total_magical_damage(),
                'is_converted': True,
                'conversion_source': 'lyre_phoenix',
                'original_physical': self.get_total_damage()
            }
        
        # Priorité 2 : O-1 Gemme de pouvoir (formes d'ours/loup → magiques)
        elif self.has_magical_form_attacks():
            return {
                'damage_type': 'magical',
                'damage_value': self.get_total_damage(),  # Même valeur, type changé
                'is_converted': True,
                'conversion_source': 'gemme_pouvoir',
                'current_form': self.current_form,
                'form_display': self.get_form_display()
            }
        
        # Attaques normales (physiques)
        else:
            return {
                'damage_type': 'physical', 
                'damage_value': self.get_total_damage(),
                'is_converted': False,
                'magical_bonus': self.get_total_magical_damage()
            }
    
    def get_stats_summary(self) -> Dict:
        return {
            'base': {
                'precision': self.precision,
                'damage': self.damage,
                'spells': self.spells,
                'health': self.health,
                'parade': 0
            },
            'bonus': {
                'precision': self.get_equipment_bonus('precision'),
                'damage': self.get_equipment_bonus('physical_damage'),
                'magical_damage': self.get_equipment_bonus('magical_damage'),
                'parade': self.get_equipment_bonus('defense'),
                'spells': self.get_equipment_bonus('spells'),
                'health': self.get_equipment_bonus('health')
            },
            'total': {
                'precision': self.get_total_precision(),
                'damage': self.get_total_damage(),
                'magical_damage': self.get_total_magical_damage(),
                'parade': self.max_parade_tokens,
                'spells': self.get_total_spells(),
                'health': self.get_total_health()
            },
            'special_effects': self.get_special_equipment_effects(),
            'forms': self.get_form_status() if self.code == "P-1" else None
        }
    
    # === CAPACITÉS ===
    
    def add_abilities(self, abilities: List[Ability]):
        self.abilities = abilities
        if abilities and 1 not in self.unlocked_abilities:
            self.unlock_ability(1)
    
    def unlock_ability(self, ability_number: int) -> bool:
        if not (1 <= ability_number <= 6) or ability_number in self.unlocked_abilities:
            return ability_number in self.unlocked_abilities
        
        # Vérifie prérequis
        for i in range(1, ability_number):
            if i not in self.unlocked_abilities:
                return False
        
        self.unlocked_abilities.append(ability_number)
        
        # Met à jour la capacité
        for ability in self.abilities:
            if ability.ability_number == ability_number:
                ability.is_unlocked = True
                ability.reset_combat_uses()
        
        return True
    
    def get_available_abilities(self) -> List:
        """MODIFIÉ - Capacités utilisables + VirtualAbility pour invocation"""
        available = []
        current_spells = self.current_spells or self.get_total_spells()
        
        # Capacités normales (Ability Pydantic)
        for ability in self.abilities:
            if not ability.is_unlocked:
                continue
            
            # Exclusion Kraor
            if self.code == "P-4" and ability.ability_number in [1, 3]:
                continue
            
            can_use, _ = ability.can_use(current_spells)
            if can_use:
                available.append(ability)
        
        # NOUVEAU - VirtualAbility pour invocation
        if self.can_summon_pet():
            summon_ability = VirtualAbility(
                self.code,
                "Invoquer Pet",
                "Invoque un Pet allié avec le Médaillon d'appel"
            )
            available.append(summon_ability)
        
        return available
    
    def use_ability(self, ability) -> AbilityAction:
        """MODIFIÉ - Support VirtualAbility + Ability normale + limite capacités magiques"""
        action = AbilityAction(
            ability_id=ability.unique_id,
            ability_name=ability.name,
            user_name=self.name,
            prevents_attack=ability.prevents_attack
        )

        # Vérifier limite capacités magiques (règle p.24 - une seule capacité magique par tour)
        if ability.prevents_attack:  # Capacité magique
            if self.magic_abilities_used_this_turn >= 1:
                action.success = False
                action.message = "⚠️ Une seule capacité magique par tour autorisée !"
                return action

            # NOUVEAU - Vérifier si une attaque a déjà été effectuée ce tour (règle p.24)
            if self.attack_done_this_turn:
                action.success = False
                action.message = "⚠️ Impossible d'utiliser une capacité magique après avoir attaqué !"
                return action

        # Gestion des formes d'Elneha (capacités 1 et 3 seulement)
        if self.code == "P-1" and hasattr(ability, 'ability_number'):
            if ability.ability_number == 1:  # Forme d'ours
                self.set_form("bear")
                action.add_effect(f"Transformation en {self.get_form_display()}")
            elif ability.ability_number == 3:  # Forme de loup
                self.set_form("wolf")
                action.add_effect(f"Transformation en {self.get_form_display()}")
        
        # Consommation sorts (seulement pour Ability normales)
        if hasattr(ability, 'spell_cost') and ability.spell_cost > 0:
            current_spells = self.current_spells or self.get_total_spells()
            self.current_spells = current_spells - ability.spell_cost
            self.spells_used += ability.spell_cost
            action.spell_cost_paid = ability.spell_cost

        # Consommation utilisations (SEULEMENT pour Ability CSV normales, PAS individual abilities)
        # Les individual abilities (ability_number présent) gèrent leur propre compteur dans execute()
        if hasattr(ability, 'use_ability') and not hasattr(ability, 'ability_number'):
            ability.use_ability()
        
        # État tour
        self.ability_used_this_turn = ability
        if ability.prevents_attack:
            self.action_taken_this_turn = True
            self.can_attack_this_turn = False
            # Incrémenter compteur capacités magiques
            self.magic_abilities_used_this_turn += 1

        action.success = True
        return action
    
    # === SYSTÈME D'EFFETS - NOUVELLES MÉTHODES ===
    
    def check_attack_modifiers(self) -> Dict[str, Any]:
        """
        Vérifie les modificateurs d'attaque actifs
        À appeler avant de calculer une attaque
        
        Returns:
            Dict avec les modificateurs: damage_multiplier, damage_bonus, no_retaliation, etc.
        """
        modifiers = {
            'damage_multiplier': 1.0,
            'damage_bonus': 0,
            'no_retaliation': False,
            'auto_hit': False
        }
        
        if not hasattr(self, 'temporary_buffs'):
            return modifiers
        
        # Double dégâts
        if self.temporary_buffs.get('double_next_attack', False):
            modifiers['damage_multiplier'] = 2.0
        
        # Bonus de dégâts
        if 'damage_bonus_next_attack' in self.temporary_buffs:
            modifiers['damage_bonus'] = self.temporary_buffs['damage_bonus_next_attack']
        
        # Pas de riposte
        if self.temporary_buffs.get('no_retaliation', False):
            modifiers['no_retaliation'] = True
        
        # Flags d'attaque
        if hasattr(self, 'attack_flags'):
            if self.attack_flags.get('no_retaliation', False):
                modifiers['no_retaliation'] = True
                # Reset le flag après vérification
                self.attack_flags.pop('no_retaliation', None)
        
        return modifiers
    
    def enhance_hero_attack(self, target, damage_dealt: int):
        """
        Gestionnaire post-attaque pour les effets temporaires
        À appeler après une attaque réussie
        """
        if not hasattr(self, 'temporary_buffs'):
            return
        
        # Consommer les buffs d'attaque unique
        consumed_buffs = []

        # CORRIGÉ - Ne PAS consommer double_next_attack si c'est Forme de loup (géré par combat_actions)
        if 'double_next_attack' in self.temporary_buffs:
            # Vérifier si c'est Forme de loup d'Elneha (compteur personnalisé)
            is_wolf_form = self.temporary_buffs.get('elneha_wolf_remaining', 0) > 0
            if not is_wolf_form:
                consumed_buffs.append('double_next_attack')
        
        if 'damage_bonus_next_attack' in self.temporary_buffs:
            consumed_buffs.append('damage_bonus_next_attack')
        
        if 'ambidextre_active' in self.temporary_buffs:
            consumed_buffs.append('ambidextre_active')
        
        if 'furtive_active' in self.temporary_buffs:
            consumed_buffs.append('furtive_active')
        
        if 'point_faible_active' in self.temporary_buffs:
            consumed_buffs.append('point_faible_active')
        
        # Retirer les buffs consommés
        for buff in consumed_buffs:
            self.temporary_buffs.pop(buff, None)
    
    def get_character_effects_summary(self) -> Dict[str, Any]:
        """
        Génère un résumé complet des effets actifs sur un personnage
        Pour l'interface utilisateur
        """
        summary = {
            'persistent_effects': [],
            'temporary_buffs': [],
            'permanent_buffs': [],
            'debuffs': [],
            'status_effects': []
        }
        
        # Effets persistants
        if hasattr(self, 'active_persistent_effects'):
            try:
                from models.combat.abilities.persistent_effects import PersistentEffectsSystem
                persistent_system = PersistentEffectsSystem()
                summary['persistent_effects'] = persistent_system.get_active_effects(self)
            except ImportError:
                pass
        
        # Buffs temporaires
        if hasattr(self, 'temporary_buffs'):
            for buff_name, buff_value in self.temporary_buffs.items():
                summary['temporary_buffs'].append({
                    'name': buff_name,
                    'value': buff_value
                })
        
        # Buffs permanents
        if hasattr(self, 'permanent_buffs'):
            for buff_name, is_active in self.permanent_buffs.items():
                if is_active:
                    summary['permanent_buffs'].append(buff_name)
        
        # Debuffs
        if hasattr(self, 'debuffs'):
            for debuff_name, debuff_value in self.debuffs.items():
                summary['debuffs'].append({
                    'name': debuff_name,
                    'value': debuff_value
                })
        
        # Effets de statut
        if hasattr(self, 'status_effects'):
            for effect_name, duration in self.status_effects.items():
                summary['status_effects'].append({
                    'name': effect_name,
                    'duration': duration
                })
        
        return summary
    
    def cleanup_expired_effects(self):
        """
        Nettoie les effets expirés du personnage
        À appeler en fin de combat ou périodiquement
        """
        # Nettoyer buffs temporaires vides
        if hasattr(self, 'temporary_buffs'):
            empty_buffs = [k for k, v in self.temporary_buffs.items() if not v]
            for buff in empty_buffs:
                del self.temporary_buffs[buff]
        
        # Nettoyer effets de statut expirés
        if hasattr(self, 'status_effects'):
            expired_effects = [k for k, v in self.status_effects.items() if v <= 0]
            for effect in expired_effects:
                del self.status_effects[effect]
        
        # Nettoyer flags d'attaque
        if hasattr(self, 'attack_flags'):
            self.attack_flags.clear()
    
    # === MÉTHODES UTILITAIRES POUR EFFETS ===
    
    def apply_enemy_debuffs(self, stat_type: str) -> int:
        """
        Applique les debuffs d'un ennemi pour un type de stat
        À appeler lors du calcul des stats d'ennemi
        
        Args:
            stat_type: 'attack', 'precision', etc.
            
        Returns:
            int: Réduction à appliquer
        """
        if not hasattr(self, 'debuffs'):
            return 0
        
        reduction = 0
        
        if stat_type == 'attack' and 'attack_reduction' in self.debuffs:
            reduction += self.debuffs['attack_reduction']
        
        if stat_type == 'precision' and 'precision_reduction' in self.debuffs:
            reduction += self.debuffs['precision_reduction']
        
        return reduction
    
    def check_enemy_status_effects(self) -> Dict[str, Any]:
        """
        Vérifie les effets de statut d'un ennemi
        À appeler avant l'action d'un ennemi
        
        Returns:
            Dict: {can_act: bool, effects: List[str]}
        """
        status = {'can_act': True, 'effects': []}
        
        if not hasattr(self, 'status_effects'):
            return status
        
        # Stun
        if 'stunned' in self.status_effects:
            if self.status_effects['stunned'] > 0:
                status['can_act'] = False
                status['effects'].append('stunned')
                # Décrémenter la durée
                self.status_effects['stunned'] -= 1
                if self.status_effects['stunned'] <= 0:
                    del self.status_effects['stunned']
        
        return status
    
    # === COMBAT ===
    
    def reset_turn_state(self):
        """Reset état du tour"""
        self.action_taken_this_turn = False
        self.ability_used_this_turn = None
        self.can_attack_this_turn = True
        self.attack_done_this_turn = False
        self.potion_used_this_turn = False
        self.magic_abilities_used_this_turn = 0  # Reset compteur capacités magiques
    
    def start_new_combat(self):
        """MODIFIÉ - Prépare nouveau combat + reset stats"""
        self.reset_turn_state()
        self.current_spells = self.get_total_spells()
        self.spells_used = 0
        
        # NOUVEAU - Reset stats modifiables
        self.reset_current_stats()
        
        # NOUVEAU - Initialiser compteur capacités magiques
        self.magic_abilities_used_this_turn = 0
        
        # Reset capacités
        for ability in self.abilities:
            ability.reset_combat_uses()
        
        # O-2 Baton de puissance : +1 utilisation capacités magiques (Liarie)
        if self.code == "P-2" and self.has_equipment("O-2"):
            self._apply_baton_puissance_bonus()
        
        # Reset parade
        self.refresh_parade_tokens()
        
        # NOUVEAU - Initialiser attributs effets pour le combat
        self._add_required_attributes()
    
    def _apply_baton_puissance_bonus(self):
        """Applique le bonus O-2 Baton de puissance (+1 utilisation capacités magiques)"""
        for ability in self.abilities:
            if ability.spell_cost > 0 and ability.uses_per_combat is not None:
                # +1 utilisation pour les capacités magiques avec limitation
                ability.uses_remaining_combat = ability.uses_per_combat + 1
                ability.uses_per_combat += 1  # Modifier aussi la base pour reset_combat_uses()
    
    def start_hero_turn(self):
        """Version améliorée de start_hero_turn avec gestion des effets"""
        # Reset état du tour standard (inclut magic_abilities_used_this_turn)
        self.reset_turn_state()

        # NOUVEAU - Restaurer jetons de parade originaux (Parade d'Atucan)
        if hasattr(self, 'temporary_buffs') and 'parade_original_max' in self.temporary_buffs:
            self.max_parade_tokens = self.temporary_buffs['parade_original_max']
            self.temporary_buffs.pop('parade_original_max', None)

        # NOUVEAU - Nettoyer flags de capacités par tour + buffs temporaires de tour
        if hasattr(self, 'temporary_buffs'):
            self.temporary_buffs.pop('parade_used_this_turn', None)
            self.temporary_buffs.pop('parade_blocked_by_attack', None)  # NOUVEAU - Reset blocage Parade par attaque
            self.temporary_buffs.pop('cannot_attack_this_turn', None)
            self.temporary_buffs.pop('temporary_defense_bonus', None)  # Reset Parade d'Atucan (affichage)
            self.temporary_buffs.pop('attacks_this_turn', None)  # Reset compteur attaques Kraor
            self.temporary_buffs.pop('lame_ability_used_this_turn', None)  # Reset limitation 1 capacité/tour pour Lame

        # NOUVEAU - Retirer statut furtivité de Lame si expire à la fin du tour
        if hasattr(self, 'status_effects') and 'invisible' in self.status_effects:
            stealth_data = self.status_effects['invisible']
            # Vérifier si c'est la furtivité de Lame (source = lame_furtivite) et qu'elle expire en fin de tour
            if isinstance(stealth_data, dict) and stealth_data.get('source') == 'lame_furtivite':
                if stealth_data.get('expires_end_of_turn', False):
                    del self.status_effects['invisible']
                    # NOUVEAU - Aussi supprimer le buff d'esquive pour arrêter l'esquive
                    if hasattr(self, 'temporary_buffs') and 'lame_dodge_ready' in self.temporary_buffs:
                        dodge_data = self.temporary_buffs['lame_dodge_ready']
                        if isinstance(dodge_data, dict) and dodge_data.get('source') == 'furtivite':
                            self.temporary_buffs.pop('lame_dodge_ready', None)

        if hasattr(self, 'temporary_buffs'):
            # NOUVEAU - Réactiver Forme de loup si compteur actif (protection nouveau round)
            if self.temporary_buffs.get('elneha_wolf_remaining', 0) > 0:
                self.temporary_buffs['double_next_attack'] = True

            # NOUVEAU - Raishi Maîtrise absolue : Recharger 2 charges par tour (auto-recharge)
            if 'raishi_maitrise_charges' in self.temporary_buffs:
                maitrise = self.temporary_buffs['raishi_maitrise_charges']
                if isinstance(maitrise, dict) and maitrise.get('auto_recharge', False):
                    max_charges = maitrise.get('max_charges', 2)
                    maitrise['charges'] = max_charges  # Recharge complète à chaque tour

        # NOUVEAU - Kraor Pluie de flèches : Reset compteur attaques par tour
        if hasattr(self, 'attacks_this_turn'):
            self.attacks_this_turn = 0

        # Recharger jetons parade avec effets
        self.refresh_parade_tokens()
        
        # Appliquer effets de début de tour
        if hasattr(self, 'active_persistent_effects'):
            try:
                from models.combat.abilities.persistent_effects import PersistentEffectsSystem
                persistent_system = PersistentEffectsSystem()
                log = []  # Log temporaire pour les effets
                persistent_system.apply_turn_start_effects(self, log)
                # Note: log devrait être passé par le système de combat
            except ImportError:
                pass
    
    def get_combat_status(self) -> Dict:
        """État complet pour interface avec effets"""
        current_spells = self.current_spells or self.get_total_spells()
        
        base_status = {
            'health': {
                'current': self.current_health,
                'max': self.get_total_health(),
                'percentage': round((self.current_health / self.get_total_health()) * 100, 1)
            },
            'spells': {
                'current': current_spells,
                'max': self.get_total_spells(),
                'used': self.spells_used
            },
            'parade': self.get_parade_status(),
            'potions': self.get_potions_summary(),
            'turn_state': {
                'action_taken': self.action_taken_this_turn,
                'can_attack': self.can_attack_this_turn,
                'potion_used': self.potion_used_this_turn
            },
            'special_effects': self.get_special_equipment_effects()
        }
        
        # NOUVEAU - Ajouter résumé des effets
        try:
            effects_summary = self.get_character_effects_summary()
            base_status['effects'] = effects_summary
        except:
            base_status['effects'] = {
                'persistent_effects': [],
                'temporary_buffs': [],
                'permanent_buffs': [],
                'debuffs': [],
                'status_effects': []
            }
        
        return base_status

class Pet(Character):
    """Pet invoqué avec système de jetons parade + héritage Character + gestion sorts + effets"""
    
    owner_code: str  # Code du héros qui l'a invoqué (ex: "P-4")
    owner_name: str  # Nom du héros qui l'a invoqué (ex: "Kraor")
    pet_type: str = "summoned"  # Type de Pet pour extensions futures
    
    # NOUVEAU - Attributs sorts pour Pets
    magic_abilities_used_this_turn: int = 0
    spells_used: int = 0
    current_spells: int = 0  # Pets n'ont pas de sorts
    
    @property
    def display_name(self) -> str:
        """Nom d'affichage du Pet"""
        return f"Minion de {self.owner_name}"
    
    @classmethod
    def create_kraor_pet(cls, owner: 'Character') -> 'Pet':
        """Crée le Pet de Kraor selon les stats définies"""
        return cls(
            code=f"{owner.code}_pet",
            name="Pet Invoqué",
            owner_code=owner.code,
            owner_name=owner.name,
            # Stats du Pet selon règles : Précision 4, Dégâts magiques 4, Parade 0, Santé 15
            precision=4,
            damage=0,  # Pas de dégâts physiques
            spells=0,  # Pas de sorts
            health=15,
            current_health=15,
            # Parade = 0 selon règles
            max_parade_tokens=0,
            current_parade_tokens=0,
            # NOUVEAU - Attributs sorts pour Pets
            magic_abilities_used_this_turn=0,
            spells_used=0,
            current_spells=0,
            # Équipement spécial pour dégâts magiques
            equipped_items=[]  # On ajoutera un équipement virtuel pour les dégâts magiques
        )
    
    def get_total_magical_damage(self) -> int:
        """Pet de Kraor fait 4 dégâts magiques"""
        if self.owner_code == "P-4":
            return 4
        return super().get_total_magical_damage()
    
    def get_attack_damage_info(self) -> Dict:
        """Pet attaque toujours en magique"""
        if self.owner_code == "P-4":
            return {
                'damage_type': 'magical',
                'damage_value': 4,
                'is_converted': False,
                'pet_attack': True
            }
        return super().get_attack_damage_info()
    
    def get_available_abilities(self) -> List:
        """Pets n'ont pas de capacités spéciales (pour l'instant)"""
        return []
    
        
    def start_hero_turn(self):
        """NOUVEAU - Début du tour Pet avec effets"""
        # Reset compteur capacités magiques par tour
        self.magic_abilities_used_this_turn = 0
        
        # Recharger jetons parade (si le Pet en a)
        if hasattr(self, 'refresh_parade_tokens'):
            self.refresh_parade_tokens()

class Enemy(BaseModel):
    """Modèle ennemi avec système de jetons parade rechargeable + effets"""
    code: str
    name: str
    defense: int  # Seuil à dépasser pour toucher
    stats_by_players: Dict[int, Dict[str, int]]  # Contient parade + santé + dégâts
    is_magical: bool = False
    has_magical_damage: bool = False
    current_health: Optional[int] = None
    max_health: Optional[int] = None
    
    # Système jetons parade
    max_parade_tokens: int = 0
    current_parade_tokens: int = 0
    
    # === NOUVEAUX ATTRIBUTS POUR SYSTÈME D'EFFETS ===
    # Debuffs subis
    debuffs: Dict[str, Any] = Field(default_factory=dict)
    
    # Effets de statut
    status_effects: Dict[str, Any] = Field(default_factory=dict)
    
    # Marques appliquées
    marks: Dict[str, Any] = Field(default_factory=dict)
    
    def get_stats_for_players(self, player_count: int) -> Dict[str, int]:
        return self.stats_by_players.get(player_count, self.stats_by_players[4])
    
    def initialize_for_combat(self, player_count: int):
        """Initialise santé ET parade + effets"""
        stats = self.get_stats_for_players(player_count)
        
        # Santé
        self.max_health = stats['health']
        self.current_health = stats['health']
        
        # Parade (Defense_Xj dans le CSV)
        # Note: Assume que 'defense' dans stats est en fait la parade
        self.max_parade_tokens = stats.get('defense', 0)
        self.current_parade_tokens = self.max_parade_tokens
        
        # NOUVEAU - Initialiser attributs effets
        if not hasattr(self, 'debuffs'):
            self.debuffs = {}
        if not hasattr(self, 'status_effects'):
            self.status_effects = {}
        if not hasattr(self, 'marks'):
            self.marks = {}
    
    def is_alive(self) -> bool:
        # NOUVEAU - Berserker rage (Thordius P-5-6) : Continue à combattre même inconscient
        if hasattr(self, 'temporary_buffs') and self.temporary_buffs.get('berserker_rage_active', False):
            return True  # Rage active = immortel

        return self.current_health > 0

    # === SYSTÈME JETONS PARADE ===
    
    def refresh_parade_tokens(self):
        """Recharge tous les jetons parade (début de tour)"""
        self.current_parade_tokens = self.max_parade_tokens
    
    def consume_parade_tokens(self, damage: int) -> tuple[int, int]:
        """
        Consomme les jetons parade contre les dégâts
        
        Args:
            damage: Dégâts entrants
            
        Returns:
            tuple[int, int]: (dégâts bloqués, dégâts restants)
        """
        if damage <= 0:
            return 0, 0
        
        # Les jetons parade bloquent 1 dégât chacun
        blocked_damage = min(damage, self.current_parade_tokens)
        remaining_damage = damage - blocked_damage
        
        # Consommation des jetons
        self.current_parade_tokens -= blocked_damage
        
        return blocked_damage, remaining_damage
    
    def apply_damage_with_parade(self, damage: int, ignore_parade: bool = False) -> Dict:
        """
        Applique dégâts avec système parade à jetons

        Args:
            damage: Montant des dégâts
            ignore_parade: Si True, bypass complètement la parade (dégâts magiques)

        Returns:
            Dict avec détails de l'application des dégâts
        """
        # NOUVEAU : Vérifier buff aura_protection (Aura sacrée d'Atucan) - Les ennemis n'ont pas ce buff normalement
        aura_reduction = 0
        if hasattr(self, 'temporary_buffs') and 'aura_protection' in self.temporary_buffs:
            aura_info = self.temporary_buffs['aura_protection']
            if aura_info.get('type') == 'per_attack':
                aura_reduction = aura_info.get('damage_reduction', 0)
                damage = max(0, damage - aura_reduction)

        if damage <= 0:
            return {
                'total_damage': damage + aura_reduction,
                'blocked_by_parade': 0,
                'health_damage': 0,
                'parade_tokens_used': 0,
                'parade_tokens_remaining': self.current_parade_tokens,
                'aura_reduction': aura_reduction
            }

        if ignore_parade:
            # Bypass complet de la parade (dégâts magiques)
            blocked = 0
            remaining = damage
        else:
            # Logique normale avec parade
            blocked, remaining = self.consume_parade_tokens(damage)
        
        # Dégâts aux PV
        old_health = self.current_health
        self.current_health = max(0, self.current_health - remaining)
        actual_health_damage = old_health - self.current_health

        return {
            'total_damage': damage + aura_reduction,  # Montant original avant réduction aura
            'blocked_by_parade': blocked,
            'health_damage': actual_health_damage,
            'parade_tokens_used': blocked,
            'parade_tokens_remaining': self.current_parade_tokens,
            'aura_reduction': aura_reduction  # Pour le log
        }

    def get_parade_status(self) -> Dict:
        """État actuel du système parade"""
        return {
            'max_tokens': self.max_parade_tokens,
            'current_tokens': self.current_parade_tokens,
            'has_parade': self.max_parade_tokens > 0,
            'parade_percentage': round((self.current_parade_tokens / self.max_parade_tokens * 100), 1) if self.max_parade_tokens > 0 else 0
        }
    
    def start_enemy_turn(self):
        """Début du tour ennemi (recharge parade)"""
        self.refresh_parade_tokens()
    
    # === MÉTHODES POUR EFFETS SUR ENNEMIS ===
    
    def apply_debuff(self, debuff_type: str, value: int):
        """Applique un debuff à l'ennemi"""
        if not hasattr(self, 'debuffs'):
            self.debuffs = {}
        self.debuffs[debuff_type] = value
    
    def apply_status_effect(self, effect_type: str, duration: int):
        """Applique un effet de statut à l'ennemi"""
        if not hasattr(self, 'status_effects'):
            self.status_effects = {}
        self.status_effects[effect_type] = duration
    
    def apply_mark(self, mark_type: str, mark_data: Dict):
        """Applique une marque à l'ennemi"""
        if not hasattr(self, 'marks'):
            self.marks = {}
        self.marks[mark_type] = mark_data
    
    def get_effective_attack(self) -> int:
        """Attaque effective avec debuffs"""
        base_stats = self.get_stats_for_players(4)  # Utiliser stats pour 4 joueurs par défaut
        base_attack = base_stats.get('damage', 0)
        
        reduction = 0
        if hasattr(self, 'debuffs') and 'attack_reduction' in self.debuffs:
            reduction = self.debuffs['attack_reduction']
        
        return max(0, base_attack - reduction)
    
    def get_effective_precision(self) -> int:
        """Précision effective avec debuffs"""
        # Les ennemis n'ont pas de stat précision dans le CSV actuel
        # Utiliser la defense comme base (règles simplifiées)
        base_precision = 10  # Valeur par défaut
        
        reduction = 0
        if hasattr(self, 'debuffs') and 'precision_reduction' in self.debuffs:
            reduction = self.debuffs['precision_reduction']
        
        return max(0, base_precision - reduction)
    
    def is_stunned(self) -> bool:
        """Vérifie si l'ennemi est stunned"""
        if not hasattr(self, 'status_effects'):
            return False
        return self.status_effects.get('stunned', 0) > 0
    
    def tick_status_effects(self):
        """Décremente la durée des effets de statut"""
        if not hasattr(self, 'status_effects'):
            return
        
        expired_effects = []
        for effect_name, duration in self.status_effects.items():
            if duration > 0:
                self.status_effects[effect_name] = duration - 1
                if self.status_effects[effect_name] <= 0:
                    expired_effects.append(effect_name)
        
        # Supprimer les effets expirés
        for effect in expired_effects:
            del self.status_effects[effect]

class Equipment(BaseModel):
    """Modèle équipement"""
    code: str
    name: str
    type: str = "accessoire"
    precision: int = 0
    physical_damage: int = 0
    magical_damage: int = 0
    defense: int = 0
    spells: int = 0
    health: int = 0
    
    def get_stat_bonus(self, stat_type: str) -> int:
        """Retourne le bonus pour un type de stat spécifique"""
        if stat_type == 'precision':
            return self.precision
        elif stat_type == 'physical_damage':
            return self.physical_damage
        elif stat_type == 'magical_damage':
            return self.magical_damage
        elif stat_type == 'defense':
            return self.defense
        elif stat_type == 'spells':
            return self.spells
        elif stat_type == 'health':
            return self.health
        return 0
    
    def is_special_object(self) -> bool:
        """Vérifie si c'est un objet spécial (O-1 à O-4)"""
        return self.code.startswith('O-')
    
    
    def get_equipment_summary(self) -> Dict[str, Any]:
        """Résumé de l'équipement pour l'interface"""
        stats = []
        if self.precision > 0:
            stats.append(f"Précision +{self.precision}")
        if self.physical_damage > 0:
            stats.append(f"Dégâts +{self.physical_damage}")
        if self.magical_damage > 0:
            stats.append(f"Magie +{self.magical_damage}")
        if self.defense > 0:
            stats.append(f"Parade +{self.defense}")
        if self.spells > 0:
            stats.append(f"Sorts +{self.spells}")
        if self.health > 0:
            stats.append(f"Santé +{self.health}")
        
        return {
            'name': self.name,
            'type': self.type,
            'code': self.code,
            'is_special': self.is_special_object(),
            'stats_text': ", ".join(stats) if stats else "Aucun bonus",
            'stats_count': len(stats)
        }