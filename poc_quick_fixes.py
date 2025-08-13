#!/usr/bin/env python3
"""
Corrections rapides pour POC Capacités
Solutions temporaires si le POC révèle des problèmes mineurs

Usage: python poc_quick_fixes.py [--apply]
"""

import os
import sys
from pathlib import Path

def create_missing_init_files():
    """Crée les fichiers __init__.py manquants"""
    print("🔧 Création des fichiers __init__.py manquants...")
    
    directories = [
        "models/combat/abilities",
        "models/combat",
        "models"
    ]
    
    for directory in directories:
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            os.makedirs(directory, exist_ok=True)
            with open(init_file, 'w') as f:
                f.write(f'"""Module {directory.replace("/", ".")}"""\n')
            print(f"✅ Créé: {init_file}")

def create_minimal_ability_manager():
    """Crée un AbilityEffectsManager minimal si manquant"""
    manager_file = "models/combat/abilities/ability_manager.py"
    
    if not os.path.exists(manager_file):
        print("🔧 Création AbilityEffectsManager minimal...")
        
        content = '''"""
AbilityEffectsManager minimal pour POC
Version simplifiée pour tests rapides
"""

class AbilityEffectsManager:
    """Gestionnaire minimal des effets de capacités pour POC"""
    
    def __init__(self):
        self.active_effects = {}
    
    def apply_ability_effects(self, caster, ability, targets, log):
        """Applique les effets d'une capacité - Version POC"""
        if not hasattr(ability, 'effects') and hasattr(ability, 'effect_type'):
            # Fallback pour capacités simplifiées du POC
            return self._apply_simple_effect(caster, ability, targets, log)
        
        results = []
        
        if hasattr(ability, 'effects'):
            for effect in ability.effects:
                result = self._apply_single_effect(caster, effect, targets, log)
                results.append(result)
        
        return results
    
    def _apply_simple_effect(self, caster, ability, targets, log):
        """Applique un effet simple (fallback POC)"""
        if ability.effect_type == "heal":
            return self._apply_healing(targets[0] if targets else caster, ability.value)
        elif ability.effect_type == "buff":
            return self._apply_stat_boost(targets[0] if targets else caster, "attack", ability.value)
        elif ability.effect_type == "debuff":
            return self._apply_stat_debuff(targets[0] if targets else caster, "defense", ability.value)
        
        return {"success": False, "message": "Effet non reconnu"}
    
    def _apply_single_effect(self, caster, effect, targets, log):
        """Applique un effet Pydantic"""
        if effect.type == "heal":
            target = targets[0] if targets else caster
            return self._apply_healing(target, effect.value)
        elif effect.type == "buff":
            target = targets[0] if targets else caster
            return self._apply_stat_boost(target, "attack", effect.value)
        elif effect.type == "debuff":
            target = targets[0] if targets else caster
            return self._apply_stat_debuff(target, "defense", effect.value)
        
        return {"success": False, "message": f"Effet {effect.type} non implémenté"}
    
    def _apply_healing(self, target, amount):
        """Applique un soin"""
        if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
            old_hp = target.current_hp
            target.current_hp = min(target.max_hp, target.current_hp + amount)
            healed = target.current_hp - old_hp
            return {
                "success": True, 
                "message": f"Soigné {healed} PV",
                "value": healed
            }
        return {"success": False, "message": "Cible invalide pour soin"}
    
    def _apply_stat_boost(self, target, stat, amount):
        """Applique un bonus de statistique"""
        stat_attr = f"current_{stat}"
        if hasattr(target, stat_attr):
            old_value = getattr(target, stat_attr)
            setattr(target, stat_attr, old_value + amount)
            return {
                "success": True,
                "message": f"+{amount} {stat}",
                "value": amount
            }
        return {"success": False, "message": f"Stat {stat} non trouvée"}
    
    def _apply_stat_debuff(self, target, stat, amount):
        """Applique un malus de statistique"""
        stat_attr = f"current_{stat}"
        if hasattr(target, stat_attr):
            old_value = getattr(target, stat_attr)
            setattr(target, stat_attr, max(0, old_value - amount))
            return {
                "success": True,
                "message": f"-{amount} {stat}",
                "value": -amount
            }
        return {"success": False, "message": f"Stat {stat} non trouvée"}
    
    # Méthodes spécifiques pour compatibilité POC
    def apply_healing_effect(self, target, ability):
        """Méthode spécifique soin"""
        amount = getattr(ability, 'value', 3)
        return self._apply_healing(target, amount)
    
    def apply_stat_boost(self, target, ability):
        """Méthode spécifique boost"""
        amount = getattr(ability, 'value', 2)
        return self._apply_stat_boost(target, "attack", amount)
    
    def apply_debuff_effect(self, target, ability):
        """Méthode spécifique debuff"""
        amount = getattr(ability, 'value', 1)
        return self._apply_stat_debuff(target, "defense", amount)
'''
        
        os.makedirs(os.path.dirname(manager_file), exist_ok=True)
        with open(manager_file, 'w') as f:
            f.write(content)
        print(f"✅ Créé: {manager_file}")

def create_minimal_init_abilities():
    """Crée le __init__.py du module abilities"""
    init_file = "models/combat/abilities/__init__.py"
    
    content = '''"""
Module abilities - POC Version
"""

from .ability_manager import AbilityEffectsManager

__all__ = ['AbilityEffectsManager']
'''
    
    os.makedirs(os.path.dirname(init_file), exist_ok=True)
    with open(init_file, 'w') as f:
        f.write(content)
    print(f"✅ Créé/Mis à jour: {init_file}")

def fix_character_imports():
    """Correction pour les imports Character si nécessaire"""
    character_file = "models/character.py"
    
    if os.path.exists(character_file):
        print("✅ models/character.py existe déjà")
    else:
        print("⚠️ models/character.py manquant - Le POC utilisera des classes simplifiées")

def apply_all_fixes():
    """Applique toutes les corrections"""
    print("🔧 APPLICATION DES CORRECTIONS RAPIDES POC")
    print("=" * 50)
    
    create_missing_init_files()
    create_minimal_ability_manager()
    create_minimal_init_abilities()
    fix_character_imports()
    
    print("\n✅ Corrections appliquées!")
    print("🧪 Vous pouvez maintenant relancer: python test_poc_abilities.py")

def check_issues():
    """Vérifie les problèmes potentiels sans les corriger"""
    print("🔍 DIAGNOSTIC DES PROBLÈMES POTENTIELS")
    print("=" * 50)
    
    issues = []
    
    # Vérifier structure directories
    required_dirs = ["models", "models/combat", "models/combat/abilities"]
    for directory in required_dirs:
        if not os.path.exists(directory):
            issues.append(f"❌ Répertoire manquant: {directory}")
        else:
            print(f"✅ Répertoire présent: {directory}")
    
    # Vérifier fichiers clés
    key_files = [
        "models/__init__.py",
        "models/combat/__init__.py", 
        "models/combat/abilities/__init__.py",
        "models/combat/abilities/ability_manager.py"
    ]
    
    for file_path in key_files:
        if not os.path.exists(file_path):
            issues.append(f"❌ Fichier manquant: {file_path}")
        else:
            print(f"✅ Fichier présent: {file_path}")
    
    if issues:
        print("\n⚠️ PROBLÈMES DÉTECTÉS:")
        for issue in issues:
            print(f"  {issue}")
        print("\n🔧 Pour corriger: python poc_quick_fixes.py --apply")
    else:
        print("\n🎉 Aucun problème détecté - POC devrait fonctionner!")

def main():
    """Fonction principale"""
    if len(sys.argv) > 1 and sys.argv[1] == "--apply":
        apply_all_fixes()
    else:
        check_issues()

if __name__ == "__main__":
    main()