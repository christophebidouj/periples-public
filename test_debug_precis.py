#!/usr/bin/env python3
"""
Test Debug Précis - Analyser l'état interne exact
Vérifier pourquoi les effets ne sont pas appliqués

Usage: python debug_test_precise.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_step_by_step():
    """Test étape par étape pour comprendre le problème"""
    print("🔍 DEBUG ÉTAPE PAR ÉTAPE")
    print("=" * 40)
    
    try:
        from utils.data_loader import DataLoader
        from models.combat.abilities import AbilityEffectsManager
        from models.combat.spell_manager import SpellManager
        
        # Charger données
        loader = DataLoader()
        heroes = loader.load_heroes()
        test_hero = next(h for h in heroes if h.code == "P-1")
        test_hero = test_hero.model_copy()
        
        print(f"✅ Héros créé: {test_hero.name}")
        print(f"📊 Stats initiales: ATT={test_hero.damage}, current_attack={getattr(test_hero, 'current_attack', 'N/A')}")
        
        # Charger capacité
        abilities = loader.get_hero_abilities("P-1")
        forme_ours = abilities[0]  # Première capacité
        forme_ours.is_unlocked = True
        
        print(f"✅ Capacité: {forme_ours.name}")
        
        # Étape 1: Vérifier état initial
        print(f"\n🔍 ÉTAPE 1: État initial")
        print(f"   active_persistent_effects: {getattr(test_hero, 'active_persistent_effects', 'ABSENT')}")
        print(f"   current_form: {getattr(test_hero, 'current_form', 'ABSENT')}")
        print(f"   get_total_damage(): {test_hero.get_total_damage()}")
        
        # Étape 2: Créer système d'effets
        spell_manager = SpellManager()
        effects_manager = AbilityEffectsManager(spell_manager)
        
        print(f"\n🔍 ÉTAPE 2: Système d'effets créé")
        
        # Étape 3: Appliquer capacité
        log = []
        print(f"\n🔍 ÉTAPE 3: Application de la capacité")
        
        result = effects_manager.apply_ability_effects(test_hero, forme_ours, log)
        
        print(f"   Résultat apply_ability_effects: {result}")
        print(f"   Logs générés: {log}")
        
        # Étape 4: Vérifier changements
        print(f"\n🔍 ÉTAPE 4: État après application")
        print(f"   active_persistent_effects: {getattr(test_hero, 'active_persistent_effects', 'ABSENT')}")
        print(f"   current_form: {getattr(test_hero, 'current_form', 'ABSENT')}")
        print(f"   current_attack: {getattr(test_hero, 'current_attack', 'ABSENT')}")
        print(f"   get_total_damage(): {test_hero.get_total_damage()}")
        
        # Étape 5: Tester manuellement get_damage_bonus
        print(f"\n🔍 ÉTAPE 5: Test manuel bonus")
        try:
            from models.combat.abilities.persistent_effects import PersistentEffectsSystem
            persistent_system = PersistentEffectsSystem()
            bonus = persistent_system.get_damage_bonus(test_hero)
            print(f"   get_damage_bonus(): {bonus}")
        except Exception as e:
            print(f"   Erreur get_damage_bonus: {e}")
        
        # Étape 6: Analyser pourquoi ça ne marche pas
        print(f"\n🔍 ÉTAPE 6: Diagnostic détaillé")
        
        # Test 1: La capacité est-elle reconnue comme transformation ?
        from models.combat.abilities.generic_effects import GenericEffectsHandler
        generic_handler = GenericEffectsHandler(spell_manager)
        
        log_transformation = []
        transformation_result = generic_handler._apply_transformation_effects(test_hero, forme_ours, log_transformation)
        print(f"   _apply_transformation_effects: {transformation_result}")
        print(f"   Logs transformation: {log_transformation}")
        
        # Test 2: La forme a-t-elle changé ?
        print(f"   Forme après transformation: {getattr(test_hero, 'current_form', 'ABSENT')}")
        
        # Test 3: Y a-t-il des effets persistants ?
        effects_count = len(getattr(test_hero, 'active_persistent_effects', []))
        print(f"   Nombre d'effets persistants: {effects_count}")
        
        if effects_count > 0:
            for effect in test_hero.active_persistent_effects:
                print(f"      - {effect.name}: {effect.effect_type}")
        
        # CONCLUSION
        print(f"\n📊 DIAGNOSTIC FINAL:")
        if transformation_result and log_transformation:
            print("✅ Le système de transformation FONCTIONNE")
            if 'se transforme en ours' in str(log_transformation):
                print("✅ La transformation est détectée et loggée")
            else:
                print("❌ La transformation n'est pas correctement loggée")
        else:
            print("❌ Le système de transformation NE FONCTIONNE PAS")
        
        attack_before = test_hero.damage
        attack_after = getattr(test_hero, 'current_attack', test_hero.damage)
        
        if attack_after > attack_before:
            print(f"✅ Les bonus de stats SONT appliqués: {attack_before} → {attack_after}")
            return True
        else:
            print(f"❌ Les bonus de stats NE SONT PAS appliqués: reste à {attack_after}")
            
            # Investiguer pourquoi
            print("\n🔧 INVESTIGATION:")
            print("   Cause probable: _apply_transformation_effects ne modifie pas current_attack")
            print("   Solution: Les transformations d'Elneha utilisent set_form() mais pas de bonus stats")
            print("   → Le problème est dans generic_effects.py ligne _apply_transformation_effects")
            
            return False
    
    except Exception as e:
        print(f"❌ Erreur debug: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    print("🐛 DEBUG PRÉCIS DU SYSTÈME DE CAPACITÉS")
    print("="*50)
    
    success = debug_step_by_step()
    
    print("\n" + "="*50)
    if success:
        print("🎉 RÉSULTAT: Système partiellement fonctionnel")
        print("💡 ACTION: Optimisations mineures nécessaires")
    else:
        print("❌ RÉSULTAT: Problème identifié dans generic_effects.py")
        print("🔧 ACTION: Correction _apply_transformation_effects requise")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)