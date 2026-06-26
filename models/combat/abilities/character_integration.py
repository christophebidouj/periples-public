"""
Extensions et intégrations pour le modèle Character
Modifications nécessaires pour supporter le système d'effets de capacités
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

class CharacterAbilitiesIntegration:
    """
    Classe utilitaire pour intégrer le système d'effets avec le modèle Character
    
    Cette classe fournit les méthodes et attributs supplémentaires nécessaires
    pour que Character.py supporte pleinement le système d'effets de capacités
    """
    
    @staticmethod
    def add_required_attributes(character):
        """
        Ajoute les attributs nécessaires au Character pour le système d'effets
        À appeler dans character.__post_init__ ou start_new_combat
        """
        # Effets persistants actifs
        if not hasattr(character, 'active_persistent_effects'):
            character.active_persistent_effects = []
        
        # Buffs temporaires (pour une action/attaque)
        if not hasattr(character, 'temporary_buffs'):
            character.temporary_buffs = {}
        
        # Buffs permanents (pour tout le combat)
        if not hasattr(character, 'permanent_buffs'):
            character.permanent_buffs = {}
        
        # Flags d'attaque spéciaux
        if not hasattr(character, 'attack_flags'):
            character.attack_flags = {}
        
        # Debuffs subis
        if not hasattr(character, 'debuffs'):
            character.debuffs = {}
        
        # Effets de statut
        if not hasattr(character, 'status_effects'):
            character.status_effects = {}
        
        # Marques appliquées (pour systèmes comme Chasseur)
        if not hasattr(character, 'marks'):
            character.marks = {}
    
    @staticmethod
    def enhance_refresh_parade_tokens(character):
        """
        Version améliorée de refresh_parade_tokens qui gère les effets persistants
        À intégrer dans Character.refresh_parade_tokens()
        """
        # Recharge normale
        character.current_parade_tokens = character.max_parade_tokens
        
        # Appliquer effets persistants sur la parade
        if hasattr(character, 'active_persistent_effects'):
            from .persistent_effects import PersistentEffectsSystem
            persistent_system = PersistentEffectsSystem()
            persistent_system.apply_parade_refresh_effects(character)
    
    @staticmethod
    def enhance_get_total_damage(character) -> int:
        """
        Version améliorée de get_total_damage qui inclut les bonus d'effets
        À intégrer dans Character.get_total_damage()
        """
        # Dégâts de base
        base_damage = character.damage + character.get_equipment_bonus('physical_damage')
        
        # Bonus des effets persistants
        persistent_bonus = 0
        if hasattr(character, 'active_persistent_effects'):
            from .persistent_effects import PersistentEffectsSystem
            persistent_system = PersistentEffectsSystem()
            persistent_bonus = persistent_system.get_damage_bonus(character)
        
        # Bonus temporaires
        temp_bonus = 0
        if hasattr(character, 'temporary_buffs'):
            temp_bonus = character.temporary_buffs.get('damage_bonus_next_attack', 0)
        
        # Marques sur les ennemis (pour Chasseur)
        mark_bonus = CharacterAbilitiesIntegration._get_mark_damage_bonus(character)
        
        return base_damage + persistent_bonus + temp_bonus + mark_bonus
    
    @staticmethod
    def enhance_get_total_parade(character) -> int:
        """
        Version améliorée pour calculer la parade max avec bonus persistants
        À utiliser pour mettre à jour max_parade_tokens
        """
        # Parade de base
        base_parade = character.get_equipment_bonus('defense')
        
        # Bonus persistants
        persistent_bonus = 0
        if hasattr(character, 'active_persistent_effects'):
            from .persistent_effects import PersistentEffectsSystem
            persistent_system = PersistentEffectsSystem()
            persistent_bonus = persistent_system.get_parade_bonus(character)
        
        # Buffs permanents
        permanent_bonus = 0
        if hasattr(character, 'permanent_buffs'):
            if character.permanent_buffs.get('defense_sans_armure', False):
                permanent_bonus += 1
        
        return base_parade + persistent_bonus + permanent_bonus
    
    @staticmethod
    def enhance_start_hero_turn(character):
        """
        Version améliorée de start_hero_turn avec gestion des effets
        À intégrer dans Character.start_hero_turn()
        """
        # Reset état du tour standard
        character.reset_turn_state()
        character.magic_abilities_used_this_turn = 0

        # NOUVEAU - Reset compteur de relances pour Sens de la justice (Paladin P-3-2 passif)
        if hasattr(character, 'temporary_buffs') and 'sens_de_la_justice_active' in character.temporary_buffs:
            character.temporary_buffs['sens_de_la_justice_active']['rerolls_used_this_turn'] = 0

        # Recharger jetons parade avec effets
        CharacterAbilitiesIntegration.enhance_refresh_parade_tokens(character)
        
        # Appliquer effets de début de tour
        if hasattr(character, 'active_persistent_effects'):
            from .persistent_effects import PersistentEffectsSystem
            persistent_system = PersistentEffectsSystem()
            log = []  # Log temporaire pour les effets
            persistent_system.apply_turn_start_effects(character, log)
            # Note: log devrait être passé par le système de combat
    
    @staticmethod
    def enhance_hero_attack(character, target, damage_dealt: int):
        """
        Gestionnaire post-attaque pour les effets temporaires
        À appeler après une attaque réussie
        """
        if not hasattr(character, 'temporary_buffs'):
            return
        
        # Consommer les buffs d'attaque unique
        consumed_buffs = []

        if 'double_next_attack' in character.temporary_buffs:
            consumed_buffs.append('double_next_attack')

        if 'damage_bonus_next_attack' in character.temporary_buffs:
            consumed_buffs.append('damage_bonus_next_attack')

        if 'meditation_damage_boost' in character.temporary_buffs:
            consumed_buffs.append('meditation_damage_boost')

        if 'ambidextre_active' in character.temporary_buffs:
            consumed_buffs.append('ambidextre_active')
        
        if 'furtive_active' in character.temporary_buffs:
            consumed_buffs.append('furtive_active')
        
        if 'point_faible_active' in character.temporary_buffs:
            consumed_buffs.append('point_faible_active')
        
        # Retirer les buffs consommés
        for buff in consumed_buffs:
            character.temporary_buffs.pop(buff, None)
    
    @staticmethod
    def check_attack_modifiers(character) -> Dict[str, Any]:
        """
        Vérifie les modificateurs d'attaque actifs
        À appeler avant de calculer une attaque

        Returns:
            Dict avec les modificateurs: damage_multiplier, damage_bonus, no_retaliation, ignore_parade, etc.
        """
        modifiers = {
            'damage_multiplier': 1.0,
            'damage_bonus': 0,
            'no_retaliation': False,
            'auto_hit': False,
            'ignore_parade': False
        }

        if not hasattr(character, 'temporary_buffs'):
            return modifiers

        # NOUVEAU - Roublard Attaque furtive (P-7-1) : Auto-hit + ×2 dégâts one-time
        if character.temporary_buffs.get('attaque_furtive_next_attack', {}).get('damage_multiplier', 1.0) > 1.0:
            furtive_buff = character.temporary_buffs['attaque_furtive_next_attack']
            modifiers['damage_multiplier'] = furtive_buff['damage_multiplier']

        # NOUVEAU - Roublard Assaut furieux (P-7-6) : Auto-hit + ×2 dégâts permanent
        elif character.temporary_buffs.get('assaut_furieux_permanent', {}).get('damage_multiplier', 1.0) > 1.0:
            assaut_buff = character.temporary_buffs['assaut_furieux_permanent']
            modifiers['damage_multiplier'] = assaut_buff['damage_multiplier']

        # Double dégâts (legacy - Druide Forme de loup)
        elif character.temporary_buffs.get('double_next_attack', False):
            modifiers['damage_multiplier'] = 2.0

        # NOUVEAU - Pugiliste Méditation : Dégâts ×1.5 (si pas déjà un autre multiplicateur)
        if modifiers['damage_multiplier'] == 1.0 and 'meditation_damage_boost' in character.temporary_buffs:
            meditation_data = character.temporary_buffs['meditation_damage_boost']
            if isinstance(meditation_data, dict):
                modifiers['damage_multiplier'] = meditation_data.get('damage_multiplier', 1.5)

        # Bonus de dégâts (legacy + Barbare Frappe puissante)
        if 'damage_bonus_next_attack' in character.temporary_buffs:
            modifiers['damage_bonus'] = character.temporary_buffs['damage_bonus_next_attack']

        # NOUVEAU - Pugiliste Art martial : Ignore parade ennemis
        if 'ignore_parade' in character.temporary_buffs:
            modifiers['ignore_parade'] = True

        # Pas de riposte
        if character.temporary_buffs.get('no_retaliation', False):
            modifiers['no_retaliation'] = True

        # Flags d'attaque
        if hasattr(character, 'attack_flags'):
            if character.attack_flags.get('no_retaliation', False):
                modifiers['no_retaliation'] = True
                # Reset le flag après vérification
                character.attack_flags.pop('no_retaliation', None)

        return modifiers
    
    @staticmethod
    def _get_mark_damage_bonus(character) -> int:
        """Calcule le bonus de dégâts contre les ennemis marqués"""
        # Cette méthode sera appelée pendant une attaque pour vérifier
        # si la cible est marquée (implémentation dépend du contexte de combat)
        return 0  # Implémenté dans le moteur de combat
    
    @staticmethod
    def apply_enemy_debuffs(enemy, stat_type: str) -> int:
        """
        Applique les debuffs d'un ennemi pour un type de stat
        À appeler lors du calcul des stats d'ennemi
        
        Args:
            enemy: Ennemi concerné
            stat_type: 'attack', 'precision', etc.
            
        Returns:
            int: Réduction à appliquer
        """
        if not hasattr(enemy, 'debuffs'):
            return 0
        
        reduction = 0
        
        if stat_type == 'attack' and 'attack_reduction' in enemy.debuffs:
            reduction += enemy.debuffs['attack_reduction']
        
        if stat_type == 'precision' and 'precision_reduction' in enemy.debuffs:
            reduction += enemy.debuffs['precision_reduction']
        
        return reduction
    
    @staticmethod
    def check_enemy_status_effects(enemy) -> Dict[str, Any]:
        """
        Vérifie les effets de statut d'un ennemi
        À appeler avant l'action d'un ennemi
        
        Returns:
            Dict: {can_act: bool, effects: List[str]}
        """
        status = {'can_act': True, 'effects': []}

        if not hasattr(enemy, 'status_effects'):
            return status

        # Stun - Gérer format dict {'duration': X, 'source': Y}
        if 'stunned' in enemy.status_effects:
            stunned_data = enemy.status_effects['stunned']
            # Support ancien format (int) et nouveau format (dict)
            if isinstance(stunned_data, dict):
                duration = stunned_data.get('duration', 0)
                if duration > 0:
                    status['can_act'] = False
                    status['effects'].append('stunned')
                    # Décrémenter la durée
                    stunned_data['duration'] = duration - 1
                    if stunned_data['duration'] <= 0:
                        del enemy.status_effects['stunned']
            else:
                # Ancien format int (rétrocompatibilité)
                if stunned_data > 0:
                    status['can_act'] = False
                    status['effects'].append('stunned')
                    enemy.status_effects['stunned'] -= 1
                    if enemy.status_effects['stunned'] <= 0:
                        del enemy.status_effects['stunned']

        return status

    @staticmethod
    def apply_stun_with_immunity_check(target, duration: int, source: str, log: List[str]) -> bool:
        """
        Applique un stun sur une cible AVEC vérification d'immunité

        Args:
            target: Cible à étourdir (Enemy ou Character)
            duration: Durée du stun en tours
            source: Source du stun (ex: 'druide_eclair', 'pugiliste_combo')
            log: Liste de logs pour messages

        Returns:
            bool: True si le stun a été appliqué, False si immunisé
        """
        # Vérifier immunité au stun (capacités ennemis)
        if hasattr(target, 'status_effects') and target.status_effects.get('immunity_stun'):
            target_name = getattr(target, 'name', 'Cible')
            log.append(f"  🛡️ {target_name} est immunisé au Stun !")
            return False

        # Appliquer le stun
        if not hasattr(target, 'status_effects'):
            target.status_effects = {}

        target.status_effects['stunned'] = {
            'duration': duration,
            'source': source
        }

        return True

    @staticmethod
    def get_character_effects_summary(character) -> Dict[str, Any]:
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
        if hasattr(character, 'active_persistent_effects'):
            from .persistent_effects import PersistentEffectsSystem
            persistent_system = PersistentEffectsSystem()
            summary['persistent_effects'] = persistent_system.get_active_effects(character)
        
        # Buffs temporaires
        if hasattr(character, 'temporary_buffs'):
            for buff_name, buff_value in character.temporary_buffs.items():
                summary['temporary_buffs'].append({
                    'name': buff_name,
                    'value': buff_value
                })
        
        # Buffs permanents
        if hasattr(character, 'permanent_buffs'):
            for buff_name, is_active in character.permanent_buffs.items():
                if is_active:
                    summary['permanent_buffs'].append(buff_name)
        
        # Debuffs
        if hasattr(character, 'debuffs'):
            for debuff_name, debuff_value in character.debuffs.items():
                summary['debuffs'].append({
                    'name': debuff_name,
                    'value': debuff_value
                })
        
        # Effets de statut
        if hasattr(character, 'status_effects'):
            for effect_name, duration in character.status_effects.items():
                summary['status_effects'].append({
                    'name': effect_name,
                    'duration': duration
                })
        
        return summary
    
    @staticmethod
    def cleanup_expired_effects(character):
        """
        Nettoie les effets expirés du personnage
        À appeler en fin de combat ou périodiquement
        """
        # Nettoyer buffs temporaires vides
        if hasattr(character, 'temporary_buffs'):
            empty_buffs = [k for k, v in character.temporary_buffs.items() if not v]
            for buff in empty_buffs:
                del character.temporary_buffs[buff]
        
        # Nettoyer effets de statut expirés
        if hasattr(character, 'status_effects'):
            expired_effects = [k for k, v in character.status_effects.items() if v <= 0]
            for effect in expired_effects:
                del character.status_effects[effect]
        
        # Nettoyer flags d'attaque
        if hasattr(character, 'attack_flags'):
            character.attack_flags.clear()

# === EXEMPLES D'INTÉGRATION ===

class CharacterIntegrationExamples:
    """
    Exemples de code pour intégrer ces méthodes dans character.py
    """
    
    @staticmethod
    def example_character_post_init():
        """
        Exemple d'intégration dans Character.__post_init__
        """
        return """
        def model_post_init(self, __context):
            # Code existant...
            
            # NOUVEAU - Initialiser système d'effets
            from models.combat.abilities.character_integration import CharacterAbilitiesIntegration
            CharacterAbilitiesIntegration.add_required_attributes(self)
        """
    
    @staticmethod
    def example_refresh_parade_tokens():
        """
        Exemple d'intégration dans Character.refresh_parade_tokens
        """
        return """
        def refresh_parade_tokens(self):
            # NOUVEAU - Version améliorée avec effets persistants
            from models.combat.abilities.character_integration import CharacterAbilitiesIntegration
            CharacterAbilitiesIntegration.enhance_refresh_parade_tokens(self)
        """
    
    @staticmethod
    def example_get_total_damage():
        """
        Exemple d'intégration dans Character.get_total_damage
        """
        return """
        def get_total_damage(self) -> int:
            # NOUVEAU - Version avec bonus d'effets
            from models.combat.abilities.character_integration import CharacterAbilitiesIntegration
            return CharacterAbilitiesIntegration.enhance_get_total_damage(self)
        """
    
    @staticmethod
    def example_start_hero_turn():
        """
        Exemple d'intégration dans Character.start_hero_turn
        """
        return """
        def start_hero_turn(self):
            # NOUVEAU - Version avec effets persistants
            from models.combat.abilities.character_integration import CharacterAbilitiesIntegration
            CharacterAbilitiesIntegration.enhance_start_hero_turn(self)
        """