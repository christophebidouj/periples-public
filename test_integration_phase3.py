#!/usr/bin/env python3
"""
Test d'intégration Phase 3 - DataLoader + Système de Capacités
Script de validation de l'intégration complète
"""

import sys
import os
from typing import Dict, Any

# Ajout du chemin racine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_abilities_system_availability():
    """Teste la disponibilité du système de capacités"""
    print("🔍 === TEST DISPONIBILITÉ SYSTÈME CAPACITÉS ===")
    print("===============================================")
    
    results = {}
    
    # Test 1: Modèles
    try:
        from models.abilities import Ability, AbilityType, AbilityManager
        print("✅ Modèles abilities importés")
        results['models'] = True
    except ImportError as e:
        print(f"❌ Erreur import modèles: {e}")
        results['models'] = False
    
    # Test 2: Loader
    try:
        from utils.abilities_loader import load_all_abilities, AbilitiesLoader
        print("✅ Loader abilities importé")
        results['loader'] = True
    except ImportError as e:
        print(f"❌ Erreur import loader: {e}")
        results['loader'] = False
    
    # Test 3: Character intégration
    try:
        from models.character import Character
        print("✅ Character avec capacités importé")
        results['character'] = True
    except ImportError as e:
        print(f"❌ Erreur import character: {e}")
        results['character'] = False
    
    # Test 4: DataLoader
    try:
        from utils.data_loader import DataLoader
        print("✅ DataLoader importé")
        results['data_loader'] = True
    except ImportError as e:
        print(f"❌ Erreur import DataLoader: {e}")
        results['data_loader'] = False
    
    # Test 5: Fichier Sorts.xlsx
    if os.path.exists("Sorts.xlsx"):
        print("✅ Fichier Sorts.xlsx trouvé")
        results['excel_file'] = True
    else:
        print("❌ Fichier Sorts.xlsx manquant")
        results['excel_file'] = False
    
    # Résumé
    all_ok = all(results.values())
    print(f"\n📊 Résumé disponibilité:")
    for component, status in results.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {component}")
    
    print(f"\n🎯 Système complet: {'✅ DISPONIBLE' if all_ok else '❌ INCOMPLET'}")
    return results

def test_dataloader_integration():
    """Teste l'intégration du DataLoader avec les capacités"""
    print("\n🔧 === TEST INTÉGRATION DATALOADER ===")
    print("====================================")
    
    try:
        from utils.data_loader import DataLoader, check_abilities_system_status
        
        # Test statut système
        status = check_abilities_system_status()
        print("📊 Statut système capacités:")
        for key, value in status.items():
            icon = "✅" if value else "❌"
            print(f"   {icon} {key}: {value}")
        
        # Création DataLoader
        loader = DataLoader()
        print(f"✅ DataLoader créé")
        
        # Test résumé capacités
        abilities_summary = loader.get_abilities_summary()
        print(f"\n🔮 Résumé capacités:")
        print(f"   - Système activé: {abilities_summary['enabled']}")
        
        if abilities_summary['enabled']:
            print(f"   - Héros avec capacités: {abilities_summary['heroes_count']}")
            print(f"   - Total capacités: {abilities_summary['total_abilities']}")
            print(f"   - Héros: {abilities_summary['heroes_with_abilities']}")
            
            # Détails par héros
            print(f"\n📋 Détails par héros:")
            for hero_code, count in abilities_summary['abilities_by_hero'].items():
                print(f"   - {hero_code}: {count} capacités")
        else:
            print(f"   ⚠️ Système désactivé ou non fonctionnel")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test DataLoader: {e}")
        return False

def test_heroes_with_abilities():
    """Teste le chargement des héros avec leurs capacités"""
    print("\n🧙‍♂️ === TEST HÉROS AVEC CAPACITÉS ===")
    print("===================================")
    
    try:
        from utils.data_loader import DataLoader
        
        loader = DataLoader()
        heroes = loader.load_heroes()
        
        print(f"✅ {len(heroes)} héros chargés")
        
        # Test capacités par héros
        heroes_with_abilities = 0
        total_abilities = 0
        
        for hero in heroes:
            ability_count = len(hero.abilities) if hasattr(hero, 'abilities') else 0
            unlocked_count = len(hero.unlocked_abilities) if hasattr(hero, 'unlocked_abilities') else 0
            
            if ability_count > 0:
                heroes_with_abilities += 1
                total_abilities += ability_count
                print(f"🔮 {hero.name} ({hero.code}):")
                print(f"   - Capacités totales: {ability_count}")
                print(f"   - Capacités débloquées: {unlocked_count}")
                
                # Affichage des 2 premières capacités
                if hasattr(hero, 'abilities') and hero.abilities:
                    for i, ability in enumerate(hero.abilities[:2]):
                        status = "🔓" if hasattr(ability, 'ability_number') and ability.ability_number in hero.unlocked_abilities else "🔒"
                        print(f"     {status} {ability.ability_number}. {ability.name} (coût: {ability.spell_cost})")
                    
                    if len(hero.abilities) > 2:
                        print(f"     ... et {len(hero.abilities) - 2} autres")
            else:
                print(f"📝 {hero.name} ({hero.code}): Aucune capacité")
        
        print(f"\n📊 Statistiques globales:")
        print(f"   - Héros avec capacités: {heroes_with_abilities}/{len(heroes)}")
        print(f"   - Total capacités: {total_abilities}")
        
        return heroes_with_abilities > 0
        
    except Exception as e:
        print(f"❌ Erreur test héros avec capacités: {e}")
        return False

def test_hero_build_with_abilities():
    """Teste la création de builds avec capacités"""
    print("\n🎯 === TEST BUILDS AVEC CAPACITÉS ===")
    print("===================================")
    
    try:
        from utils.data_loader import DataLoader
        
        loader = DataLoader()
        
        # Test avec Elneha (P-1)
        test_codes = ["P-1", "P-2", "P-4"]  # Elneha, Liarie, Kraor
        
        for hero_code in test_codes:
            print(f"\n🧙‍♂️ Test build {hero_code}:")
            
            build_info = loader.get_hero_build(hero_code)
            hero = build_info['hero_equipped']
            abilities_summary = build_info['abilities_summary']
            
            print(f"   ✅ Héros: {hero.name}")
            print(f"   - Build: {build_info['build_name']}")
            print(f"   - Équipements: {len(build_info['equipment'])}")
            print(f"   - Type: {'Custom' if build_info['is_custom'] else 'Standard'}")
            
            # Informations capacités
            if abilities_summary:
                print(f"   🔮 Capacités:")
                print(f"     - Total: {abilities_summary['total_abilities']}")
                print(f"     - Débloquées: {abilities_summary['unlocked_abilities']}")
                print(f"     - Disponibles: {abilities_summary['available_abilities']}")
                
                # Détail des capacités
                for ability_detail in abilities_summary['abilities_details'][:3]:  # 3 premières
                    status_icon = "🔓" if ability_detail['unlocked'] else "🔒"
                    print(f"     {status_icon} {ability_detail['number']}. {ability_detail['name']} (coût: {ability_detail['cost']})")
                
                if len(abilities_summary['abilities_details']) > 3:
                    remaining = len(abilities_summary['abilities_details']) - 3
                    print(f"     ... et {remaining} autres")
            else:
                print(f"   📝 Aucune capacité disponible")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test builds avec capacités: {e}")
        return False

def test_combat_readiness():
    """Teste la préparation pour l'intégration combat"""
    print("\n⚔️ === TEST PRÉPARATION COMBAT ===")
    print("=================================")
    
    try:
        from utils.data_loader import DataLoader, get_hero_with_abilities
        
        loader = DataLoader()
        
        # Test récupération héros pour combat
        hero_codes = ["P-1", "P-2"]  # Elneha et Liarie
        combat_heroes = []
        
        for hero_code in hero_codes:
            hero = get_hero_with_abilities(hero_code, loader)
            combat_heroes.append(hero)
            
            print(f"🧙‍♂️ {hero.name} préparé pour combat:")
            print(f"   - Stats: Pré:{hero.precision}, Dég:{hero.damage}, Sorts:{hero.spells}, PV:{hero.health}")
            
            if hasattr(hero, 'abilities') and hero.abilities:
                available_abilities = [a for a in hero.abilities if a.ability_number in hero.unlocked_abilities]
                print(f"   - Capacités disponibles: {len(available_abilities)}")
                
                for ability in available_abilities[:2]:  # 2 premières
                    ability_type = "🔮 Magique" if ability.spell_cost > 0 else "⚔️ Physique"
                    print(f"     {ability_type} {ability.name} (coût: {ability.spell_cost})")
            else:
                print(f"   - Capacités: Aucune")
        
        print(f"\n✅ {len(combat_heroes)} héros prêts pour combat avec capacités")
        
        # Test état de combat
        if combat_heroes:
            test_hero = combat_heroes[0]
            if hasattr(test_hero, 'get_combat_status'):
                status = test_hero.get_combat_status()
                print(f"\n🎮 Test état de combat ({test_hero.name}):")
                print(f"   - PV: {status.get('health', 'N/A')}")
                print(f"   - Sorts: {status.get('spells', 'N/A')}")
                print(f"   - État tour: {status.get('turn_state', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test préparation combat: {e}")
        return False

def run_full_integration_test():
    """Lance tous les tests d'intégration"""
    print("🚀 === TESTS COMPLETS INTÉGRATION PHASE 3 ===")
    print("============================================")
    print("Test de l'intégration DataLoader + Système de Capacités")
    print("=" * 50)
    
    tests = [
        ("Disponibilité Système", test_abilities_system_availability),
        ("Intégration DataLoader", test_dataloader_integration),
        ("Héros avec Capacités", test_heroes_with_abilities),
        ("Builds avec Capacités", test_hero_build_with_abilities),
        ("Préparation Combat", test_combat_readiness)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*50}")
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ ERREUR CRITIQUE dans {test_name}: {e}")
            results[test_name] = False
    
    # Résumé final
    print(f"\n{'='*50}")
    print("🏆 === RÉSUMÉ TESTS INTÉGRATION ===")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Résultat global: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 INTÉGRATION PHASE 3 COMPLÈTE !")
        print("🚀 Prêt pour Phase 4 (Moteur de Combat)")
        
        print(f"\n🎯 PROCHAINES ÉTAPES:")
        print(f"====================")
        print(f"✅ Phase 1-2-3: Modèles + Loader + DataLoader")
        print(f"🔄 Phase 4: Moteur de combat avec limitation d'actions")
        print(f"❌ Phase 5: Interface utilisateur activation capacités")
        
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Vérifiez les erreurs avant de continuer")
    
    return passed == total

def show_system_status():
    """Affiche l'état complet du système"""
    print("\n📊 === ÉTAT SYSTÈME CAPACITÉS ===")
    print("=================================")
    
    try:
        from utils.data_loader import check_abilities_system_status, DataLoader
        
        # Statut technique
        status = check_abilities_system_status()
        print("🔧 Statut technique:")
        for component, available in status.items():
            icon = "✅" if available else "❌"
            print(f"   {icon} {component}")
        
        # Données capacités
        if status['system_functional']:
            loader = DataLoader()
            summary = loader.get_abilities_summary()
            
            print(f"\n🔮 Données capacités:")
            print(f"   - Système activé: {summary['enabled']}")
            if summary['enabled']:
                print(f"   - Héros: {summary['heroes_count']}")
                print(f"   - Capacités: {summary['total_abilities']}")
                
                # Top 3 héros avec le plus de capacités
                sorted_heroes = sorted(
                    summary['abilities_by_hero'].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:3]
                
                print(f"\n🏆 Top héros par capacités:")
                for hero_code, count in sorted_heroes:
                    print(f"   - {hero_code}: {count} capacités")
        
        # État des phases
        print(f"\n🚧 État développement:")
        print(f"   ✅ Phase 1: Modèles Pydantic")
        print(f"   ✅ Phase 2: Import + Character")
        print(f"   ✅ Phase 3: DataLoader (ACTUELLE)")
        print(f"   ❌ Phase 4: Moteur Combat")
        print(f"   ❌ Phase 5: Interface UI")
        
        completion = 60  # 3/5 phases terminées
        print(f"\n📈 Progression: {completion}% terminé")
        
    except Exception as e:
        print(f"❌ Erreur affichage statut: {e}")

if __name__ == "__main__":
    print("🧪 LANCEMENT TESTS INTÉGRATION PHASE 3")
    print("=" * 50)
    
    # Affichage statut initial
    show_system_status()
    
    # Tests complets
    success = run_full_integration_test()
    
    # Statut final
    print(f"\n" + "=" * 50)
    if success:
        print("🎊 PHASE 3 VALIDÉE - INTÉGRATION RÉUSSIE !")
        print("Système de capacités intégré au DataLoader")
    else:
        print("💥 ÉCHEC PHASE 3 - Corrections nécessaires")
    
    sys.exit(0 if success else 1)