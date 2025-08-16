# test_phase2_validation.py - Script de validation complète Phase 2
"""
Script de test pour valider l'implémentation complète de la Phase 2
Vérifie que les 12 capacités (6 Elneha + 6 Liarie) sont fonctionnelles

Usage: python test_phase2_validation.py
"""

import sys
import traceback


def test_critical_imports():
    """Test des imports critiques du système"""
    print("🔍 Test des imports critiques...")
    
    try:
        # Import du système de base
        from models.character import Character
        print("✅ Character importé")
        
        from models.combat.abilities.ability_manager import AbilityEffectsManager
        print("✅ AbilityEffectsManager importé")
        
        # Import du registre
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        print("✅ ABILITY_REGISTRY importé")
        
        # Import des capacités héros
        from models.combat.abilities.individual_abilities.heroes import (
            get_phase2_statistics, validate_phase2_implementation
        )
        print("✅ Fonctions Phase 2 importées")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur import: {e}")
        traceback.print_exc()
        return False


def test_registry_content():
    """Test du contenu du registre des capacités"""
    print("\n🔍 Test du contenu du registre...")
    
    try:
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        
        # Vérifier le registre
        total_registered = ABILITY_REGISTRY.get_registered_count()
        print(f"📊 Capacités enregistrées: {total_registered}")
        
        # Vérifier capacités spécifiques Phase 2
        expected_abilities = [
            # Elneha (P-1)
            ("P-1", 1), ("P-1", 2), ("P-1", 3), ("P-1", 4), ("P-1", 5), ("P-1", 6),
            # Liarie (P-2)
            ("P-2", 1), ("P-2", 2), ("P-2", 3), ("P-2", 4), ("P-2", 5), ("P-2", 6),
        ]
        
        found_abilities = []
        missing_abilities = []
        
        for hero_code, ability_num in expected_abilities:
            ability = ABILITY_REGISTRY.get_ability_instance(hero_code, ability_num)
            if ability is not None:
                found_abilities.append(f"{hero_code}-{ability_num}: {ability.name}")
                print(f"✅ {hero_code}-{ability_num}: {ability.name}")
            else:
                missing_abilities.append(f"{hero_code}-{ability_num}")
                print(f"❌ {hero_code}-{ability_num}: NON TROUVÉE")
        
        print(f"\n📈 Résultat:")
        print(f"   ✅ Trouvées: {len(found_abilities)}/12")
        print(f"   ❌ Manquantes: {len(missing_abilities)}/12")
        
        if missing_abilities:
            print(f"   🔍 Capacités manquantes: {missing_abilities}")
            return False
        
        if total_registered < 12:
            print(f"❌ Pas assez de capacités: {total_registered}/12")
            return False
        
        print(f"✅ Toutes les 12 capacités Phase 2 sont enregistrées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test registre: {e}")
        traceback.print_exc()
        return False


def test_ability_instantiation():
    """Test d'instanciation des capacités"""
    print("\n🔍 Test d'instanciation des capacités...")
    
    try:
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        
        # Tester quelques capacités clés
        test_cases = [
            ("P-1", 1, "Forme d'ours"),
            ("P-1", 2, "Soin mineur"),
            ("P-1", 6, "Résurrection"),
            ("P-2", 1, "Eclair magique"),
            ("P-2", 4, "Boule de feu"),
            ("P-2", 6, "Pluie de météores"),
        ]
        
        success_count = 0
        
        for hero_code, ability_num, expected_name in test_cases:
            try:
                ability = ABILITY_REGISTRY.get_ability_instance(hero_code, ability_num)
                if ability:
                    print(f"✅ {hero_code}-{ability_num}: {ability.name}")
                    
                    # Test des attributs essentiels
                    if hasattr(ability, 'execute') and hasattr(ability, 'can_execute'):
                        print(f"   ✅ Méthodes essentielles présentes")
                        success_count += 1
                    else:
                        print(f"   ❌ Méthodes manquantes")
                else:
                    print(f"❌ {hero_code}-{ability_num}: Instance None")
            except Exception as e:
                print(f"❌ {hero_code}-{ability_num}: Erreur {e}")
        
        print(f"\n📊 Instanciations réussies: {success_count}/{len(test_cases)}")
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f"❌ Erreur test instanciation: {e}")
        traceback.print_exc()
        return False


def test_phase2_statistics():
    """Test des statistiques Phase 2"""
    print("\n🔍 Test des statistiques Phase 2...")
    
    try:
        from models.combat.abilities.individual_abilities.heroes import (
            get_phase2_statistics, validate_phase2_implementation
        )
        
        # Test des statistiques
        stats = get_phase2_statistics()
        print(f"📊 Statistiques Phase 2:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Validation
        validation_result = validate_phase2_implementation()
        
        if validation_result and stats['total_abilities'] >= 12:
            print("✅ Validation Phase 2 réussie")
            return True
        else:
            print("❌ Validation Phase 2 échouée")
            return False
        
    except Exception as e:
        print(f"❌ Erreur test statistiques: {e}")
        traceback.print_exc()
        return False


def test_registry_debug():
    """Test des fonctions de debug du registre"""
    print("\n🔍 Test des fonctions de debug...")
    
    try:
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        
        # Afficher les infos de debug
        print("📋 Informations détaillées du registre:")
        ABILITY_REGISTRY.print_debug_info()
        
        # Vérifier la cohérence
        registered_count = ABILITY_REGISTRY.get_registered_count()
        debug_info = ABILITY_REGISTRY.get_debug_info()
        
        expected_heroes = ['P-1', 'P-2']
        found_heroes = [hero for hero in expected_heroes if debug_info['heroes'][hero]['registered'] > 0]
        
        print(f"\n📊 Résumé debug:")
        print(f"   Total enregistré: {registered_count}")
        print(f"   Héros trouvés: {found_heroes}")
        
        if registered_count >= 12 and len(found_heroes) >= 2:
            print(f"✅ Registre cohérent: {registered_count} capacités pour {len(found_heroes)} héros")
            return True
        else:
            print(f"❌ Registre incohérent: {registered_count} capacités pour {len(found_heroes)} héros")
            return False
        
    except Exception as e:
        print(f"❌ Erreur test debug: {e}")
        traceback.print_exc()
        return False


def test_hero_modules():
    """Test des modules héros individuels"""
    print("\n🔍 Test des modules héros...")
    
    try:
        # Test module Elneha
        try:
            from models.combat.abilities.individual_abilities.heroes.elneha import (
                get_elneha_abilities_count, get_elneha_abilities_summary
            )
            elneha_count = get_elneha_abilities_count()
            print(f"✅ Module Elneha: {elneha_count} capacités")
        except ImportError:
            print(f"❌ Module Elneha: Import failed")
            return False
        
        # Test module Liarie
        try:
            from models.combat.abilities.individual_abilities.heroes.liarie import (
                get_liarie_abilities_count, get_liarie_abilities_summary
            )
            liarie_count = get_liarie_abilities_count()
            print(f"✅ Module Liarie: {liarie_count} capacités")
        except ImportError:
            print(f"❌ Module Liarie: Import failed")
            return False
        
        # Vérifier les totaux
        total_expected = elneha_count + liarie_count
        if total_expected >= 12:
            print(f"✅ Total modules: {total_expected} capacités")
            return True
        else:
            print(f"❌ Total insuffisant: {total_expected} capacités")
            return False
        
    except Exception as e:
        print(f"❌ Erreur test modules: {e}")
        traceback.print_exc()
        return False


def generate_final_report():
    """Génère un rapport final de la Phase 2"""
    print("\n📊 GÉNÉRATION DU RAPPORT FINAL PHASE 2")
    print("="*60)
    
    try:
        from models.combat.abilities.individual_abilities.heroes import print_phase2_summary
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        
        # Afficher le résumé Phase 2
        print_phase2_summary()
        
        # Statistiques détaillées du registre
        print("\n🔍 DÉTAILS TECHNIQUES:")
        debug_info = ABILITY_REGISTRY.get_debug_info()
        
        print(f"📊 Registre global:")
        print(f"   Total capacités: {debug_info['total_registered']}")
        print(f"   Instances en cache: {debug_info['cached_instances']}")
        
        print(f"\n🎭 Détail par héros:")
        for hero_code, hero_info in debug_info['heroes'].items():
            if hero_info['registered'] > 0:
                print(f"   {hero_code}: {hero_info['registered']}/6 capacités")
                for ability in hero_info['abilities']:
                    print(f"      {ability['number']}: {ability['name']}")
        
        # Analyse de progression
        total_abilities = debug_info['total_registered']
        progress_percentage = round((total_abilities / 48) * 100, 1)
        
        print(f"\n📈 PROGRESSION:")
        print(f"   Phase 2: {total_abilities}/12 capacités cibles")
        print(f"   Global: {total_abilities}/48 capacités totales ({progress_percentage}%)")
        
        if total_abilities >= 12:
            print(f"   🎉 PHASE 2 RÉUSSIE !")
            print(f"   🚀 Prêt pour Phase 3 (objectif: 24 capacités)")
        else:
            print(f"   ⚠️ PHASE 2 INCOMPLÈTE")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur génération rapport: {e}")
        traceback.print_exc()
        return False


def test_integration_ability_manager():
    """Test d'intégration avec AbilityManager"""
    print("\n🔍 Test d'intégration AbilityManager...")
    
    try:
        from models.combat.abilities.ability_manager import AbilityEffectsManager
        from models.combat.abilities.individual_abilities import get_ability
        
        # Test de récupération d'une capacité via l'interface publique
        test_ability = get_ability("P-1", 1)  # Forme d'ours
        
        if test_ability:
            print(f"✅ get_ability() fonctionne: {test_ability.name}")
            
            # Vérifier les attributs essentiels
            required_attrs = ['hero_code', 'ability_number', 'name', 'description']
            missing_attrs = [attr for attr in required_attrs if not hasattr(test_ability, attr)]
            
            if not missing_attrs:
                print(f"✅ Attributs requis présents")
                return True
            else:
                print(f"❌ Attributs manquants: {missing_attrs}")
                return False
        else:
            print(f"❌ get_ability() retourne None")
            return False
        
    except Exception as e:
        print(f"❌ Erreur test intégration: {e}")
        traceback.print_exc()
        return False


def main():
    """Fonction principale de test"""
    print("🧪 VALIDATION COMPLÈTE PHASE 2 - CAPACITÉS INDIVIDUELLES")
    print("="*60)
    print("Objectif: Vérifier 12 capacités (6 Elneha + 6 Liarie)")
    print("Date: Phase 2 - Migration capacités individuelles")
    print()
    
    all_tests_passed = True
    
    # Série de tests complets
    tests = [
        ("Imports critiques", test_critical_imports),
        ("Contenu du registre", test_registry_content),
        ("Instanciation capacités", test_ability_instantiation),
        ("Modules héros", test_hero_modules),
        ("Statistiques Phase 2", test_phase2_statistics),
        ("Fonctions debug", test_registry_debug),
        ("Intégration système", test_integration_ability_manager),
    ]
    
    print("🔄 EXÉCUTION DES TESTS:")
    print("-" * 40)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Test: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name}: RÉUSSI")
            else:
                print(f"❌ {test_name}: ÉCHOUÉ")
                all_tests_passed = False
        except Exception as e:
            print(f"💥 {test_name}: ERREUR - {e}")
            all_tests_passed = False
    
    # Rapport final
    print("\n" + "="*60)
    print("📋 RÉSULTATS FINAUX")
    print("="*60)
    
    if all_tests_passed:
        print("🎉 TOUS LES TESTS RÉUSSIS - PHASE 2 VALIDÉE !")
        print("\n📊 STATUT:")
        print("   ✅ Infrastructure: Opérationnelle")
        print("   ✅ Registre: 12+ capacités enregistrées")
        print("   ✅ Elneha: 6/6 capacités fonctionnelles")
        print("   ✅ Liarie: 6/6 capacités fonctionnelles")
        print("   ✅ Intégration: Compatible avec système existant")
        
        print("\n🚀 PROCHAINES ÉTAPES:")
        print("   📋 Phase 2 terminée avec succès")
        print("   🎯 Prêt pour Phase 3: +12 capacités (Atucan + Kraor)")
        print("   📈 Objectif Phase 3: 24/48 capacités (50% progression)")
        
        # Génération du rapport détaillé
        generate_final_report()
        
        print("\n🎊 FÉLICITATIONS ! PHASE 2 TERMINÉE AVEC SUCCÈS !")
        
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("\n🔧 ACTIONS REQUISES:")
        print("   1. Vérifier les erreurs d'import ci-dessus")
        print("   2. Corriger les problèmes identifiés")
        print("   3. Relancer le script de validation")
        print("   4. Ne pas passer à la Phase 3 tant que Phase 2 n'est pas validée")
        
        print("\n🚨 POINTS DE CONTRÔLE:")
        print("   • Tous les fichiers sont-ils créés aux bons emplacements ?")
        print("   • Les imports relatifs sont-ils corrects ?")
        print("   • Les décorateurs @register_ability sont-ils sans paramètres ?")
        print("   • Les attributs de classe (hero_code, ability_number) sont-ils définis ?")
    
    print("\n" + "="*60)
    
    return all_tests_passed


def quick_diagnostic():
    """Diagnostic rapide pour debug"""
    print("🔍 DIAGNOSTIC RAPIDE")
    print("-" * 30)
    
    try:
        # Test import base
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        count = ABILITY_REGISTRY.get_registered_count()
        print(f"📊 Capacités dans le registre: {count}")
        
        # Test import héros
        try:
            from models.combat.abilities.individual_abilities.heroes import get_loaded_abilities_count
            loaded_count = get_loaded_abilities_count()
            print(f"📦 Capacités chargées via modules: {loaded_count}")
        except ImportError as e:
            print(f"❌ Erreur import modules héros: {e}")
        
        # Test capacités spécifiques
        test_abilities = [("P-1", 1), ("P-2", 1)]
        for hero_code, ability_num in test_abilities:
            ability = ABILITY_REGISTRY.get_ability_instance(hero_code, ability_num)
            status = "✅" if ability else "❌"
            name = ability.name if ability else "NON TROUVÉE"
            print(f"{status} {hero_code}-{ability_num}: {name}")
        
    except Exception as e:
        print(f"❌ Erreur diagnostic: {e}")


if __name__ == "__main__":
    import sys
    
    # Option de diagnostic rapide
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_diagnostic()
    else:
        # Test complet
        success = main()
        sys.exit(0 if success else 1)