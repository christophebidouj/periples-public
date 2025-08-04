#!/usr/bin/env python3
"""
DEBUG COMPLET - Identifier l'erreur Test 4
Version qui diagnostique tous les problèmes possibles
"""

import sys
import os
import traceback

# Ajout du chemin racine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_complete_test():
    """Debug complet avec toutes les vérifications"""
    print("🔍 === DIAGNOSTIC COMPLET ERREUR TEST 4 ===")
    
    # === ÉTAPE 1: VÉRIFICATION IMPORTS ===
    print("\n📦 ÉTAPE 1: Vérification des imports")
    
    # Test import Character
    try:
        print("🔄 Import Character...")
        from models.character import Character
        print("✅ Import Character réussi")
        
        # Inspection de la classe Character
        print(f"   - Classe: {Character}")
        character_methods = [m for m in dir(Character) if not m.startswith('_')]
        print(f"   - Méthodes: {character_methods}")
        
        # Vérification des méthodes critiques
        critical_methods = ['use_ability', 'add_abilities']
        for method in critical_methods:
            if hasattr(Character, method):
                print(f"   - ✅ {method}: PRÉSENT")
            else:
                print(f"   - ❌ {method}: MANQUANT")
                
    except ImportError as e:
        print(f"❌ Erreur import Character: {e}")
        print("💡 Solution: Vérifiez que models/character.py existe")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue Character: {e}")
        traceback.print_exc()
        return False
    
    # Test import Ability
    try:
        print("🔄 Import Ability...")
        from models.abilities import Ability, AbilityType
        print("✅ Import Ability réussi")
        
        ability_methods = [m for m in dir(Ability) if not m.startswith('_')]
        print(f"   - Méthodes Ability: {ability_methods}")
        
    except ImportError as e:
        print(f"❌ Erreur import Ability: {e}")
        return False
    
    # === ÉTAPE 2: CRÉATION HÉROS AVEC DEBUG ===
    print("\n🦸 ÉTAPE 2: Création héros avec debug complet")
    
    try:
        print("🔄 Création Character avec paramètres de base...")
        hero = Character(
            code="P-1",
            name="Elneha", 
            precision=6,
            damage=2,
            spells=3,
            health=5
        )
        
        print(f"✅ Character créé: {hero}")
        print(f"   - Type: {type(hero)}")
        
        # DIAGNOSTIC COMPLET DES ATTRIBUTS
        print("\n📊 Diagnostic attributs héros:")
        
        essential_attrs = ['code', 'name', 'precision', 'damage', 'spells', 'health']
        for attr in essential_attrs:
            if hasattr(hero, attr):
                value = getattr(hero, attr)
                print(f"   - ✅ {attr}: {value} ({type(value)})")
            else:
                print(f"   - ❌ {attr}: MANQUANT")
        
        # Attributs optionnels critiques pour les capacités
        optional_attrs = ['current_spells', 'abilities', 'unlocked_abilities']
        for attr in optional_attrs:
            if hasattr(hero, attr):
                value = getattr(hero, attr)
                print(f"   - 🔍 {attr}: {value} ({type(value)})")
            else:
                print(f"   - ⚠️ {attr}: MANQUANT (sera créé)")
        
        # TOUS les attributs disponibles
        all_attrs = [attr for attr in dir(hero) if not attr.startswith('_')]
        print(f"   - 📋 Tous attributs: {all_attrs}")
        
    except Exception as e:
        print(f"❌ Erreur création héros: {e}")
        print(f"   - Type erreur: {type(e).__name__}")
        traceback.print_exc()
        return False
    
    # === ÉTAPE 3: CRÉATION CAPACITÉS AVEC DEBUG ===
    print("\n🔮 ÉTAPE 3: Création capacités avec debug")
    
    try:
        print("🔄 Création Ability...")
        
        ability = Ability(
            hero_code="P-1",
            ability_number=1,
            name="Métamorphose Ours",
            spell_cost=2,
            description="Se transforme en ours",
            uses_per_combat=1,
            is_unlocked=True
        )
        
        print(f"✅ Ability créée: {ability}")
        print(f"   - Type: {type(ability)}")
        
        # DIAGNOSTIC ATTRIBUTS ABILITY
        print("\n📊 Diagnostic attributs capacité:")
        
        ability_attrs = [
            'hero_code', 'ability_number', 'name', 'spell_cost', 
            'uses_per_combat', 'uses_remaining_combat', 'is_unlocked',
            'description'
        ]
        
        for attr in ability_attrs:
            if hasattr(ability, attr):
                value = getattr(ability, attr)
                print(f"   - ✅ {attr}: {value} ({type(value)})")
            else:
                print(f"   - ❌ {attr}: MANQUANT")
        
        # CORRECTION CRITIQUE: Initialiser uses_remaining_combat
        print("\n🔧 Initialisation uses_remaining_combat...")
        if ability.uses_per_combat is not None and ability.uses_remaining_combat is None:
            ability.uses_remaining_combat = ability.uses_per_combat
            print(f"   - ✅ uses_remaining_combat initialisé: {ability.uses_remaining_combat}")
        else:
            print(f"   - ℹ️ uses_remaining_combat déjà: {ability.uses_remaining_combat}")
        
        # TEST MÉTHODES ABILITY
        print("\n🧪 Test des méthodes Ability...")
        
        # Test can_use
        if hasattr(ability, 'can_use'):
            try:
                can_use_result = ability.can_use(3)
                print(f"   - ✅ can_use(3): {can_use_result}")
            except Exception as can_use_error:
                print(f"   - ❌ Erreur can_use: {can_use_error}")
                traceback.print_exc()
        else:
            print("   - ❌ Méthode can_use: MANQUANTE")
        
        # Test use_ability
        if hasattr(ability, 'use_ability'):
            try:
                print("   - 🔄 Test use_ability()...")
                use_result = ability.use_ability()
                print(f"   - ✅ use_ability(): {use_result}")
                print(f"   - ✅ uses_remaining après: {ability.uses_remaining_combat}")
            except Exception as use_error:
                print(f"   - ❌ Erreur use_ability: {use_error}")
                traceback.print_exc()
        else:
            print("   - ❌ Méthode use_ability: MANQUANTE")
        
    except Exception as e:
        print(f"❌ Erreur création capacité: {e}")
        print(f"   - Type erreur: {type(e).__name__}")
        traceback.print_exc()
        return False
    
    # === ÉTAPE 4: INTÉGRATION HÉROS + CAPACITÉS ===
    print("\n🤝 ÉTAPE 4: Intégration héros + capacités")
    
    try:
        # CORRECTION: Initialiser current_spells sur le héros
        print("🔧 Initialisation current_spells héros...")
        if not hasattr(hero, 'current_spells') or hero.current_spells is None:
            hero.current_spells = hero.spells
            print(f"   - ✅ current_spells initialisé: {hero.current_spells}")
        else:
            print(f"   - ℹ️ current_spells déjà: {hero.current_spells}")
        
        # Test ajout capacités
        abilities_list = [ability]
        
        print("🔄 Test ajout capacités au héros...")
        if hasattr(hero, 'add_abilities'):
            print("   - 🔄 Utilisation hero.add_abilities()...")
            try:
                hero.add_abilities(abilities_list)
                print("   - ✅ add_abilities() réussi")
            except Exception as add_error:
                print(f"   - ❌ Erreur add_abilities: {add_error}")
                traceback.print_exc()
        else:
            print("   - ⚠️ add_abilities manquant, ajout manuel...")
            hero.abilities = abilities_list
            if not hasattr(hero, 'unlocked_abilities'):
                hero.unlocked_abilities = [1]
            print("   - ✅ Capacités ajoutées manuellement")
        
        # Vérification finale
        print("📊 État final héros + capacités:")
        if hasattr(hero, 'abilities'):
            print(f"   - ✅ hero.abilities: {len(hero.abilities)} capacité(s)")
            for i, ab in enumerate(hero.abilities):
                print(f"     [{i}] {ab.name} (coût: {ab.spell_cost})")
        else:
            print("   - ❌ hero.abilities: MANQUANT")
        
        print(f"   - ✅ hero.current_spells: {getattr(hero, 'current_spells', 'MANQUANT')}")
        
    except Exception as e:
        print(f"❌ Erreur intégration: {e}")
        print(f"   - Type erreur: {type(e).__name__}")
        traceback.print_exc()
        return False
    
    # === ÉTAPE 5: SIMULATION TEST 4 EXACT ===
    print("\n⚔️ ÉTAPE 5: Simulation exacte du Test 4 problématique")
    
    try:
        print("🎯 Reproduction exacte du code qui échoue...")
        
        # Code exact du test original
        if hasattr(hero, 'abilities') and hero.abilities:
            ability_test = hero.abilities[0]  # Première capacité
            
            # Initialiser current_spells si nécessaire (correction du test original)
            if not hasattr(hero, 'current_spells') or hero.current_spells is None:
                hero.current_spells = hero.spells
            
            initial_spells = hero.current_spells
            print(f"📊 État initial:")
            print(f"   - Sorts actuels: {hero.current_spells}")
            print(f"   - Capacité: {ability_test.name} (coût: {ability_test.spell_cost})")
            
            # Vérifier d'abord si on peut utiliser la capacité
            can_use, reason = ability_test.can_use(hero.current_spells)
            print(f"   - Peut utiliser: {can_use} ({reason})")
            
            # TEST AVEC MÉTHODE CHARACTER si elle existe
            if hasattr(hero, 'use_ability'):
                print("🔄 Test avec méthode Character.use_ability")
                try:
                    action = hero.use_ability(ability_test)
                    print(f"✅ Action créée: {type(action).__name__}")
                    
                    # Vérification robuste des propriétés
                    properties_to_check = [
                        'success', 'ability_name', 'spell_cost_paid', 
                        'prevents_attack', 'effects_applied', 'user_name'
                    ]
                    
                    for prop in properties_to_check:
                        if hasattr(action, prop):
                            value = getattr(action, prop)
                            print(f"   - {prop}: {value}")
                        else:
                            print(f"   - {prop}: NON DISPONIBLE")
                    
                except Exception as use_ability_error:
                    print(f"❌ ERREUR IDENTIFIÉE dans hero.use_ability(): {use_ability_error}")
                    print(f"   - Type: {type(use_ability_error).__name__}")
                    print("📋 Stack trace complète:")
                    traceback.print_exc()
                    print("\n💡 CAUSE PROBABLE: Problème dans l'implémentation de Character.use_ability()")
                    return False
                
            else:
                print("⚠️ hero.use_ability() MANQUANT - Test direct avec Ability")
                
                # Test direct avec la capacité
                if can_use:
                    success = ability_test.use_ability()
                    if success:
                        hero.current_spells -= ability_test.spell_cost
                        print(f"✅ Test direct réussi")
                        print(f"   - Sorts restants: {hero.current_spells}")
                        print(f"   - Uses restantes: {ability_test.uses_remaining_combat}")
                    else:
                        print(f"❌ Échec use_ability direct")
                        return False
                else:
                    print(f"⚠️ Capacité non utilisable: {reason}")
        else:
            print("❌ Pas de capacités sur le héros")
            return False
        
        print("\n🎉 TEST 4 SIMULÉ AVEC SUCCÈS !")
        return True
        
    except Exception as e:
        print(f"❌ ERREUR FINALE IDENTIFIÉE: {e}")
        print(f"   - Type: {type(e).__name__}")
        print(f"   - Message: {str(e)}")
        print("\n📋 Stack trace complète:")
        traceback.print_exc()
        
        # DIAGNOSTIC FINAL
        print(f"\n🔍 DIAGNOSTIC FINAL:")
        print(f"   - Le problème se situe probablement dans models/character.py")
        print(f"   - Méthode problématique: Character.use_ability() ou Ability.use_ability()")
        print(f"   - Vérifiez l'implémentation de ces méthodes")
        
        return False

if __name__ == "__main__":
    print("🚀 === DEBUG COMPLET TEST SYSTÈME CAPACITÉS ===")
    print("================================================")
    print("🎯 Objectif: Identifier la cause exacte de l'erreur Test 4")
    print("🔧 Stratégie: Diagnostic étape par étape avec corrections")
    print("================================================")
    
    success = debug_complete_test()
    
    print(f"\n{'='*60}")
    print("🏆 === RÉSULTAT DIAGNOSTIC ===")
    print(f"{'='*60}")
    
    if success:
        print("✅ DIAGNOSTIC RÉUSSI !")
        print("🎉 Le problème a été identifié et/ou corrigé")
        print("💡 Appliquez les corrections suggérées à votre code")
    else:
        print("❌ DIAGNOSTIC RÉVÈLE UN PROBLÈME")
        print("🔧 Consultez les messages d'erreur ci-dessus")
        print("💬 Partagez le résultat complet pour assistance")
    
    print(f"\n💡 PROCHAINES ÉTAPES:")
    print(f"1. Exécutez ce script de debug")
    print(f"2. Identifiez l'erreur exacte dans la sortie")
    print(f"3. Partagez la stack trace complète")
    print(f"4. Correction ciblée du problème")
    
    exit(0 if success else 1)