# ability_manager.py
"""
Gestionnaire principal des effets de capacités
VERSION MISE À JOUR - Support des capacités individuelles + système modulaire existant
"""

from typing import List, Dict, Any
from .persistent_effects import PersistentEffectsSystem
from .generic_effects import GenericEffectsHandler
from .hero_specific import HeroSpecificEffects

# NOUVEAU - Import du système de capacités individuelles
try:
    from .individual_abilities import ABILITY_REGISTRY, get_ability
    INDIVIDUAL_ABILITIES_AVAILABLE = True
    print("✅ Système de capacités individuelles chargé")
except ImportError as e:
    INDIVIDUAL_ABILITIES_AVAILABLE = False
    print(f"⚠️ Capacités individuelles non disponibles: {e}")

class AbilityEffectsManager:
    """
    Orchestrateur principal pour tous les effets de capacités
    NOUVEAU: Support des capacités individuelles + délégation aux modules spécialisés existants
    """
    
    def __init__(self, spell_manager):
        self.spell_manager = spell_manager
        
        # Modules spécialisés existants (PRÉSERVÉS)
        self.persistent_system = PersistentEffectsSystem()
        self.generic_handler = GenericEffectsHandler(spell_manager)
        self.hero_specific = HeroSpecificEffects(spell_manager)
        
        # NOUVEAU - Statistiques pour le suivi de migration
        self.individual_abilities_used = 0
        self.legacy_abilities_used = 0
    
# CORRECTION ability_manager.py - Ligne ~30-60
# Remplacer la méthode apply_ability_effects()

    def apply_ability_effects(self, hero, ability, log: List[str], context: Dict[str, Any] = None) -> bool:
        
        # NOUVEAU - Étape 1: Vérifier si une capacité individuelle existe
        if INDIVIDUAL_ABILITIES_AVAILABLE and hasattr(ability, 'ability_number'):
            individual_result = self._try_individual_ability(hero, ability, log, context)
            if individual_result is not None:
                return individual_result
        
        # DÉSACTIVÉ - Ancien système
        # return self._apply_legacy_system(hero, ability, log)
        return False
        
    def _try_individual_ability(self, hero, ability, log: List[str], context: Dict[str, Any] = None):
        """
        NOUVEAU - Tente d'exécuter une capacité individuelle
        
        Returns:
            bool si capacité individuelle exécutée, None si pas trouvée
        """
        try:
            # Récupérer la capacité individuelle depuis le registre
            individual_ability = get_ability(hero.code, ability.ability_number)
            
            if individual_ability:
                # Préparer le contexte pour l'exécution
                base_context = {
                    'spell_manager': self.spell_manager,
                    'hero': hero,
                    'ability': ability
                }
                context = {**base_context, **(context or {})}
                
                # Déterminer les cibles (pour l'instant, le lanceur par défaut)
                # TODO: Améliorer le système de ciblage dans les prochaines versions
                targets = [hero]
                
                # Exécuter la capacité individuelle
                log.append(f"🔧 Utilisation de capacité individuelle: {individual_ability.name}")
                success = individual_ability.execute(hero, targets, context, log)
                
                if success:
                    self.individual_abilities_used += 1
                    log.append(f"✅ Capacité individuelle {individual_ability.name} exécutée avec succès")
                else:
                    log.append(f"⚠️ Capacité individuelle {individual_ability.name} a échoué")
                
                return success
            
        except Exception as e:
            log.append(f"❌ Erreur capacité individuelle {hero.code}-{ability.ability_number}: {str(e)}")
            # En cas d'erreur, continuer avec l'ancien système (pas de crash)
        
        return None  # Pas de capacité individuelle trouvée
    
    def _apply_legacy_system(self, hero, ability, log: List[str]) -> bool:
        """
        Applique l'ancien système modulaire (PRÉSERVÉ INTÉGRALEMENT)
        GenericEffects + HeroSpecific + PersistentEffects
        """
        effects_applied = False
        
        # 1. Vérifier si c'est une capacité spécifique à un héros
        if self._is_hero_specific_ability(hero, ability):
            if self.hero_specific.apply_specific_ability(hero, ability, log):
                effects_applied = True
        
        # 2. Appliquer les effets génériques
        if self.generic_handler.apply_generic_effects(hero, ability, log):
            effects_applied = True
        
        # 3. Gérer les effets persistants
        if self._activates_persistent_effect(ability):
            self.persistent_system.activate_persistent_effect(hero, ability, log)
            effects_applied = True
        
        if effects_applied:
            self.legacy_abilities_used += 1
        
        return effects_applied
    
    def _is_hero_specific_ability(self, hero, ability) -> bool:
        """
        Détermine si une capacité nécessite un traitement spécifique
        PRÉSERVÉ - Liste des capacités avec traitement spécial
        """
        # Capacités nécessitant un traitement héros-spécifique
        hero_specifics = [
            ('P-1', 'forme d\'ours'),      # Elneha transformation ours
            ('P-1', 'forme de loup'),     # Elneha transformation loup  
            ('P-1', 'métamorphose'),      # Autres transformations Elneha
            ('P-4', 'marquer'),           # Kraor marquage
            ('P-6', 'rage de berserker'), # Stephe rage
            ('P-7', 'furtivité'),         # Lame furtivité
            ('P-8', 'technique')          # Raishi techniques
        ]
        
        description_lower = ability.description.lower()
        return any(hero.code == code and specific in description_lower 
                  for code, specific in hero_specifics)
    
    def _activates_persistent_effect(self, ability) -> bool:
        """
        Détermine si une capacité active un effet persistant
        PRÉSERVÉ - Détection des effets persistants
        """
        description = ability.description.lower()
        name = ability.name.lower()
        
        # Mots-clés indiquant un effet persistant
        persistent_keywords = [
            'par tour', 'tant que', 'jusqu\'à ', 'à chaque tour',
            'de façon cumulative', 'reste actif', 'armure du mage',
            'rage de berserker', 'rage insatiable', 'témérité'
        ]
        
        return any(keyword in description or keyword in name for keyword in persistent_keywords)
    
    def apply_turn_start_effects(self, hero, log: List[str]):
        """Applique les effets de début de tour (effets persistants) - PRÉSERVÉ"""
        self.persistent_system.apply_turn_start_effects(hero, log)
    
    def apply_turn_end_effects(self, hero, log: List[str]):
        """Applique les effets de fin de tour - PRÉSERVÉ"""
        self.persistent_system.apply_turn_end_effects(hero, log)
    
    def remove_expired_effects(self, hero, log: List[str]):
        """Supprime les effets expirés - PRÉSERVÉ"""
        self.persistent_system.remove_expired_effects(hero, log)
    
    def get_effect_preview(self, ability) -> str:
        """
        Génère un aperçu des effets d'une capacité pour l'interface
        NOUVEAU: Priorise les aperçus des capacités individuelles
        """
        if not ability or not hasattr(ability, 'description'):
            return "Effet inconnu"
        
        # NOUVEAU - Essayer d'abord les capacités individuelles
        if INDIVIDUAL_ABILITIES_AVAILABLE and hasattr(ability, 'ability_number'):
            try:
                # Déterminer le code héros depuis le contexte ou un attribut
                hero_code = getattr(ability, 'hero_code', None)
                if hero_code:
                    individual_ability = get_ability(hero_code, ability.ability_number)
                    if individual_ability:
                        return individual_ability.get_preview()
            except Exception:
                pass  # Fallback sur l'ancien système
        
        # Fallback sur l'ancien système (PRÉSERVÉ)
        preview_parts = []
        
        # Effets génériques
        generic_preview = self.generic_handler.get_generic_preview(ability)
        if generic_preview:
            preview_parts.append(generic_preview)
        
        # Effets spécifiques
        specific_preview = self.hero_specific.get_specific_preview(ability)
        if specific_preview:
            preview_parts.append(specific_preview)
        
        # Effets persistants
        persistent_preview = self.persistent_system.get_persistent_preview(ability)
        if persistent_preview:
            preview_parts.append(persistent_preview)
        
        return " | ".join(preview_parts) if preview_parts else "Effet spécial"
    
    def get_active_effects_summary(self, hero) -> Dict[str, Any]:
        """Retourne un résumé des effets actifs sur un héros - PRÉSERVÉ"""
        return {
            'persistent_effects': self.persistent_system.get_active_effects(hero),
            'temporary_buffs': getattr(hero, 'temporary_buffs', {}),
            'has_active_effects': self.persistent_system.has_active_effects(hero)
        }
    
    def get_migration_stats(self) -> Dict[str, Any]:
        """
        NOUVEAU - Retourne les statistiques de migration vers les capacités individuelles
        """
        total_used = self.individual_abilities_used + self.legacy_abilities_used
        
        return {
            'individual_abilities_used': self.individual_abilities_used,
            'legacy_abilities_used': self.legacy_abilities_used,
            'total_abilities_used': total_used,
            'individual_system_available': INDIVIDUAL_ABILITIES_AVAILABLE,
            'migration_percentage': (self.individual_abilities_used / total_used * 100) if total_used > 0 else 0
        }