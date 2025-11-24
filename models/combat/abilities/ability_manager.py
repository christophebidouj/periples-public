# ability_manager.py
"""
Gestionnaire principal des effets de capacités
VERSION NETTOYÉE - Système de capacités individuelles uniquement
"""

from typing import List, Dict, Any
from .persistent_effects import PersistentEffectsSystem

# Import du système de capacités individuelles
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
    VERSION NETTOYÉE: Support des capacités individuelles + effets persistants
    """
    
    def __init__(self, spell_manager):
        self.spell_manager = spell_manager
        
        # Système d'effets persistants (conservé)
        self.persistent_system = PersistentEffectsSystem()
        
        # Statistiques pour le suivi de migration
        self.individual_abilities_used = 0
        self.legacy_abilities_used = 0

    def apply_ability_effects(self, hero, ability, log: List[str], context: Dict[str, Any] = None):
        """
        Point d'entrée principal pour l'application des effets de capacités

        Returns:
            bool OU dict:
            - bool (legacy): True si succès, False sinon
            - dict (nouveau): {'success': bool, 'damage_dealt': int}
        """

        # Étape 1: Vérifier si une capacité individuelle existe
        if INDIVIDUAL_ABILITIES_AVAILABLE and hasattr(ability, 'ability_number'):
            individual_result = self._try_individual_ability(hero, ability, log, context)
            if individual_result is not None:
                return individual_result

        # Ancien système désactivé
        return {'success': False, 'damage_dealt': 0}
        
    def _try_individual_ability(self, hero, ability, log: List[str], context: Dict[str, Any] = None):
        """
        Tente d'exécuter une capacité individuelle
        
        Returns:
            bool si capacité individuelle exécutée, None si pas trouvée
        """
        try:
            # Récupérer la capacité individuelle depuis le registre
            individual_ability = get_ability(hero.code, ability.ability_number)
            
            if individual_ability:
                # SYNC INPUT: Copier uses_per_combat pour bénéficier des bonus équipement (Bâton de puissance)
                # Les individual abilities sont des singletons cachés qui conservent leur état
                if hasattr(ability, 'uses_per_combat') and hasattr(individual_ability, 'uses_per_combat'):
                    # Si la limite CSV est supérieure (bonus équipement), mettre à jour l'instance
                    ability_uses = getattr(ability, 'uses_per_combat', None)
                    individual_uses = getattr(individual_ability, 'uses_per_combat', None)

                    if ability_uses is not None and individual_uses is not None and ability_uses > individual_uses:
                        # Première utilisation avec bonus : initialiser avec la nouvelle limite
                        individual_ability.uses_per_combat = ability_uses
                        individual_ability.uses_remaining_combat = ability_uses

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

                # Initialiser le compteur de dégâts pour cette exécution
                individual_ability._damage_counter = {'total': 0}

                # Exécuter la capacité individuelle
                log.append(f"🔧 Utilisation de capacité individuelle: {individual_ability.name}")
                result = individual_ability.execute(hero, targets, context, log)

                # Récupérer les dégâts accumulés automatiquement par _apply_damage()
                damage_from_counter = individual_ability._damage_counter.get('total', 0)
                targets_hit = individual_ability._damage_counter.get('targets', [])

                # SYNC OUTPUT: Copier le compteur décrémenté vers l'objet CSV pour l'affichage UI
                # L'instance individual est la source de vérité (elle décrémente dans execute())
                if hasattr(ability, 'uses_remaining_combat') and hasattr(individual_ability, 'uses_remaining_combat'):
                    ability.uses_remaining_combat = individual_ability.uses_remaining_combat
                if hasattr(ability, 'uses_per_combat') and hasattr(individual_ability, 'uses_per_combat'):
                    ability.uses_per_combat = individual_ability.uses_per_combat

                # Normaliser le résultat (gérer bool ET dict)
                if isinstance(result, dict):
                    # Nouveau format avec dégâts explicites
                    success = result.get('success', False)
                    damage_dealt = result.get('damage_dealt', 0)
                    # Si pas de dégâts dans le dict, utiliser le compteur automatique
                    if damage_dealt == 0 and damage_from_counter > 0:
                        damage_dealt = damage_from_counter
                elif isinstance(result, bool):
                    # Format legacy (bool seulement) - utiliser compteur automatique
                    success = result
                    damage_dealt = damage_from_counter
                else:
                    # Fallback sécurité
                    success = False
                    damage_dealt = 0

                if success:
                    self.individual_abilities_used += 1
                    log.append(f"✅ Capacité individuelle {individual_ability.name} exécutée avec succès")
                else:
                    log.append(f"⚠️ Capacité individuelle {individual_ability.name} a échoué")

                return {'success': success, 'damage_dealt': damage_dealt, 'targets_hit': targets_hit}
            
        except Exception as e:
            log.append(f"❌ Erreur capacité individuelle {hero.code}-{ability.ability_number}: {str(e)}")
            # En cas d'erreur, pas de crash
        
        return None  # Pas de capacité individuelle trouvée
    
    def apply_turn_start_effects(self, hero, log: List[str]):
        """Applique les effets de début de tour (effets persistants)"""
        self.persistent_system.apply_turn_start_effects(hero, log)
    
    def apply_turn_end_effects(self, hero, log: List[str]):
        """Applique les effets de fin de tour"""
        self.persistent_system.apply_turn_end_effects(hero, log)
    
    def remove_expired_effects(self, hero, log: List[str]):
        """Supprime les effets expirés"""
        self.persistent_system.remove_expired_effects(hero, log)
    
    def get_effect_preview(self, ability) -> str:
        """
        Génère un aperçu des effets d'une capacité pour l'interface
        VERSION NETTOYÉE: Capacités individuelles + effets persistants uniquement
        """
        if not ability or not hasattr(ability, 'description'):
            return "Effet inconnu"
        
        # Prioriser les aperçus des capacités individuelles
        if INDIVIDUAL_ABILITIES_AVAILABLE and hasattr(ability, 'ability_number'):
            try:
                # Déterminer le code héros depuis le contexte ou un attribut
                hero_code = getattr(ability, 'hero_code', None)
                if hero_code:
                    individual_ability = get_ability(hero_code, ability.ability_number)
                    if individual_ability:
                        return individual_ability.get_preview()
            except Exception:
                pass  # Fallback sur effets persistants
        
        # Fallback sur effets persistants uniquement
        persistent_preview = self.persistent_system.get_persistent_preview(ability)
        return persistent_preview if persistent_preview else "Effet spécial"
    
    def get_active_effects_summary(self, hero) -> Dict[str, Any]:
        """Retourne un résumé des effets actifs sur un héros"""
        return {
            'persistent_effects': self.persistent_system.get_active_effects(hero),
            'temporary_buffs': getattr(hero, 'temporary_buffs', {}),
            'has_active_effects': self.persistent_system.has_active_effects(hero)
        }
    
    def get_migration_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques de migration vers les capacités individuelles
        """
        total_used = self.individual_abilities_used + self.legacy_abilities_used
        
        return {
            'individual_abilities_used': self.individual_abilities_used,
            'legacy_abilities_used': self.legacy_abilities_used,
            'total_abilities_used': total_used,
            'individual_system_available': INDIVIDUAL_ABILITIES_AVAILABLE,
            'migration_percentage': (self.individual_abilities_used / total_used * 100) if total_used > 0 else 0
        }