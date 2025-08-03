"""
Tests du système de capacités pour le Simulateur Périples
Script de validation des modèles et du chargeur de données
"""

import sys
import os
from typing import List, Dict

# Ajout du chemin racine pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_abilities_models():
    """Test des modèles de capacités"""
    print("🔮 === TEST DES MODÈLES DE CAPACITÉS ===")
    
    try:
        from models.abilities import Ability, AbilityEffect, AbilityType, AbilityAction, AbilityManager
        print("✅ Import des modèles réussi")
    except ImportError as e:
        print(f"❌ Erreur d'import des modèles: {e}")
        return False
    
    # Test 1: Création d'une capacité physique
    print("\n📝 Test 1: Capacité physique")
    try:
        physical_ability = Ability(
            hero_code="P-1",
            ability_number=1,
            name="Coup Puissant",
            spell_cost=0,
            description="Une attaque physique puissante",
            is_unlocked=True
        )
        
        assert physical_ability.ability_type == AbilityType.PHYSICAL
        assert not physical_ability.prevents_attack
        print(f"✅ Capacité physique créée: {physical_ability.name}")
        print(f"   - Type: {physical_ability.ability_type.value}")
        print(f"   - Empêche attaque: {physical_ability.prevents_attack}")
        
    except Exception as e:
        print(f"❌ Erreur création capacité physique: {e}")
        return False
    
    # Test 2: Création d'une capacité magique
    print("\n📝 Test 2: Capacité magique")
    try:
        magical_ability = Ability(
            hero_code="P-2",
            ability_number=2,
            name="Boule de Feu",
            spell_cost=3,
            description="Lance une boule de feu qui inflige 5 dégâts",
            uses_per_combat=2,
            is_unlocked=True
        )
        
        assert magical_ability.ability_type == AbilityType.MAGICAL
        assert magical_ability.prevents_attack
        print(f"✅ Capacité magique créée: {magical_ability.name}")
        print(f"   - Coût: {magical_ability.spell_cost} sorts")
        print(f"   - Empêche attaque: {magical_ability.prevents_attack}")
        print(f"   - Utilisations: {magical_ability.uses_per_combat}/combat")
        
    except Exception as e:
        print(f"❌ Erreur création capacité magique: {e}")
        return False
    
    # Test 3: Vérification d'utilisation
    print("\n📝 Test 3: Vérification d'utilisation")
    try:
        # Test avec sorts suffisants
        can_use, reason = magical_ability.can_use(5)
        assert can_use == True
        print(f"✅ Peut utiliser avec 5 sorts: {can_use} ({reason})")
        
        # Test avec sorts insuffisants
        can_use, reason = magical_ability.can_use(1)
        assert can_use == False
        print(f"✅ Ne peut pas utiliser avec 1 sort: {can_use} ({reason})")
        
    except Exception as e:
        print(f"❌ Erreur vérification utilisation: {e}")
        return False
    
    # Test 4: Utilisation de capacité
    print("\n📝 Test 4: Utilisation de capacité")
    try:
        # Première utilisation
        success = magical_ability.use_ability()
        assert success == True
        assert magical_ability.uses_remaining_combat == 1
        print(f"✅ Première utilisation réussie, reste: {magical_ability.uses_remaining_combat}")
        
        # Deuxième utilisation
        success = magical_ability.use_ability()
        assert success == True
        assert magical_ability.uses_remaining_combat == 0
        print(f"✅ Deuxième utilisation réussie, reste: {magical_ability.uses_remaining_combat}")
        
        # Troisième utilisation (doit échouer)
        success = magical_ability.use_ability()
        assert success == False
        print(f"✅ Troisième utilisation échouée comme attendu")
        
    except Exception as e:
        print(f"❌ Erreur utilisation capacité: {e}")
        return False
    
    # Test 5: Reset des utilisations
    print("\n📝 Test 5: Reset des utilisations")
    try:
        magical_ability.reset_combat_uses()
        assert magical_ability.uses_remaining_combat == 2
        print(f"✅ Reset réussi, utilisations: {magical_ability.uses_remaining_combat}")
        
    except Exception as e:
        print(f"❌ Erreur reset utilisations: {e}")
        return False
    
    # Test 6: AbilityManager
    print("\n📝 Test 6: AbilityManager")
    try:
        abilities = [physical_ability, magical_ability]
        manager = AbilityManager(abilities)
        
        unlocked = manager.get_unlocked_abilities()
        available = manager.get_available_abilities(5)
        
        print(f"✅ Manager créé avec {len(abilities)} capacités")
        print(f"   - Débloquées: {len(unlocked)}")
        print(f"   - Disponibles avec 5 sorts: {len(available)}")
        
        stats = manager.get_stats_summary()
        print(f"   - Stats: {stats}")
        
    except Exception as e:
        print(f"❌ Erreur AbilityManager: {e}")
        return False
    
    print("\n✅ TOUS LES TESTS DES MODÈLES RÉUSSIS !")
    return True

def test_abilities_loader():
    """Test du chargeur de capacités"""
    print("\n🔮 === TEST DU CHARGEUR DE CAPACITÉS ===")
    
    try:
        from utils.abilities_loader import AbilitiesLoader, load_all_abilities
        print("✅ Import du chargeur réussi")
    except ImportError as e:
        print(f"❌ Erreur d'import du chargeur: {e}")
        return False
    
    # Test 1: Création du loader
    print("\n📝 Test 1: Création du loader")
    try:
        loader = AbilitiesLoader("Sorts.xlsx")
        print(f"✅ Loader créé pour: {loader.excel_path}")
        print(f"   - Héros mappés: {len(loader.hero_name_to_code)}")
        
    except Exception as e:
        print(f"❌ Erreur création loader: {e}")
        return False
    
    # Test 2: Parsing nom + numéro
    print("\n📝 Test 2: Parsing nom + numéro")
    try:
        test_cases = [
            ("Elneha1", "P-1", 1),
            ("Liarie2", "P-2", 2),
            ("Atucan 3", "P-3", 3),
            ("KRAOR4", "P-4", 4),
            ("Stèphe5", "P-6", 5)
        ]
        
        for input_name, expected_code, expected_num in test_cases:
            hero_code, ability_num = loader._extract_hero_and_number(input_name)
            assert hero_code == expected_code
            assert ability_num == expected_num
            print(f"✅ '{input_name}' → {hero_code}, capacité {ability_num}")
            
    except Exception as e:
        print(f"❌ Erreur parsing nom + numéro: {e}")
        return False
    
    # Test 3: Extraction nom de capacité
    print("\n📝 Test 3: Extraction nom de capacité")
    try:
        test_descriptions = [
            "Métamorphose en Ours\nSe transforme en ours puissant",
            "Soin Naturel: Récupère 3 points de vie grâce à la nature",
            "Lance un projectile magique qui inflige des dégâts",
            "Forme de Loup\nAugmente la vitesse et l'agilité"
        ]
        
        for desc in test_descriptions:
            name = loader._extract_ability_name(desc)
            print(f"✅ '{desc[:30]}...' → Nom: '{name}'")
            
    except Exception as e:
        print(f"❌ Erreur extraction nom: {e}")
        return False
    
    # Test 4: Parsing effets
    print("\n📝 Test 4: Parsing effets")
    try:
        test_descriptions = [
            "Soigne 3 points de vie",
            "Inflige 5 dégâts magiques",
            "Augmente les dégâts de +2",
            "Réduit la défense de l'ennemi"
        ]
        
        for desc in test_descriptions:
            effects = loader._parse_effects_from_description(desc)
            print(f"✅ '{desc}' → {len(effects)} effet(s): {[e.type for e in effects]}")
            
    except Exception as e:
        print(f"❌ Erreur parsing effets: {e}")
        return False
    
    # Test 5: Chargement fallback
    print("\n📝 Test 5: Chargement fallback")
    try:
        fallback_abilities = loader._create_fallback_abilities()
        total_abilities = sum(len(abilities) for abilities in fallback_abilities.values())
        
        print(f"✅ Capacités fallback créées:")
        for hero_code, abilities in fallback_abilities.items():
            print(f"   - {hero_code}: {len(abilities)} capacités")
            for ability in abilities:
                print(f"     * {ability.name} (coût: {ability.spell_cost})")
        
        print(f"   Total: {total_abilities} capacités")
        
    except Exception as e:
        print(f"❌ Erreur chargement fallback: {e}")
        return False
    
    # Test 6: Fonction utilitaire
    print("\n📝 Test 6: Fonction utilitaire load_all_abilities")
    try:
        # Ce test utilisera le fallback car Sorts.xlsx n'existe probablement pas
        abilities = load_all_abilities("fichier_inexistant.xlsx")
        
        print(f"✅ Fonction utilitaire fonctionne:")
        print(f"   - Héros chargés: {list(abilities.keys())}")
        print(f"   - Total capacités: {sum(len(abs) for abs in abilities.values())}")
        
    except Exception as e:
        print(f"❌ Erreur fonction utilitaire: {e}")
        return False
    
    print("\n✅ TOUS LES TESTS DU CHARGEUR RÉUSSIS !")
    return True

def test_character_integration():
    """Test de l'intégration des capacités dans Character"""
    print("\n🔮 === TEST INTÉGRATION CHARACTER ===")
    
    try:
        from models.character import Character
        from models.abilities import Ability
        print("✅ Import des modèles Character et Ability réussi")
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    
    # Test 1: Création d'un héros
    print("\n📝 Test 1: Création d'un héros")
    try:
        hero = Character(
            code="P-1",
            name="Elneha",
            precision=6,
            damage=2,
            spells=3,
            health=5
        )
        
        print(f"✅ Héros créé: {hero.name}")
        print(f"   - Code: {hero.code}")
        print(f"   - Stats: Pré:{hero.precision}, Dég:{hero.damage}, Sorts:{hero.spells}, PV:{hero.health}")
        
    except Exception as e:
        print(f"❌ Erreur création héros: {e}")
        return False
    
    # Test 2: Ajout de capacités
    print("\n📝 Test 2: Ajout de capacités")
    try:
        abilities = [
            Ability(
                hero_code="P-1",
                ability_number=1,
                name="Métamorphose Ours",
                spell_cost=2,
                description="Se transforme en ours",
                uses_per_combat=1
            ),
            Ability(
                hero_code="P-1",
                ability_number=2,
                name="Soin Naturel",
                spell_cost=1,
                description="Récupère des points de vie"
            )
        ]
        
        hero.add_abilities(abilities)
        
        print(f"✅ {len(abilities)} capacités ajoutées")
        print(f"   - Total capacités: {len(hero.abilities)}")
        print(f"   - Capacités débloquées: {hero.unlocked_abilities}")
        
    except Exception as e:
        print(f"❌ Erreur ajout capacités: {e}")
        return False
    
    # Test 3: Déblocage de capacités
    print("\n📝 Test 3: Déblocage de capacités")
    try:
        # La capacité 1 devrait être auto-débloquée
        assert 1 in hero.unlocked_abilities
        print(f"✅ Capacité 1 auto-débloquée")
        
        # Déblocage capacité 2
        success = hero.unlock_ability(2)
        assert success == True
        assert 2 in hero.unlocked_abilities
        print(f"✅ Capacité 2 débloquée manuellement")
        
        # Tentative déblocage capacité 4 (devrait échouer - pas séquentiel)
        success = hero.unlock_ability(4)
        assert success == False
        print(f"✅ Capacité 4 correctement refusée (pas séquentiel)")
        
    except Exception as e:
        print(f"❌ Erreur déblocage capacités: {e}")
        return False
    
    # Test 4: Capacités disponibles
    print("\n📝 Test 4: Capacités disponibles")
    try:
        unlocked = hero.get_unlocked_abilities()
        available = hero.get_available_abilities()
        
        print(f"✅ Capacités débloquées: {len(unlocked)}")
        for ability in unlocked:
            print(f"   - {ability.name} (coût: {ability.spell_cost})")
        
        print(f"✅ Capacités disponibles: {len(available)}")
        for ability in available:
            can_use, reason = hero.can_use_ability(ability)
            print(f"   - {ability.name}: {can_use} ({reason})")
        
    except Exception as e:
        print(f"❌ Erreur capacités disponibles: {e}")
        return False
    
    # Test 5: Utilisation de capacité
    print("\n📝 Test 5: Utilisation de capacité")
    try:
        # Préparation combat
        hero.start_new_combat()
        initial_spells = hero.current_spells
        
        print(f"✅ Combat démarré, sorts: {initial_spells}")
        
        # Utilisation d'une capacité
        ability_to_use = hero.get_ability_by_number(1)  # Métamorphose Ours
        action = hero.use_ability(ability_to_use)
        
        print(f"✅ Utilisation capacité: {action.success}")
        print(f"   - Capacité: {action.ability_name}")
        print(f"   - Coût payé: {action.spell_cost_paid}")
        print(f"   - Empêche attaque: {action.prevents_attack}")
        print(f"   - Sorts restants: {hero.current_spells}")
        print(f"   - Effets: {action.effects_applied}")
        
        # Vérification état du tour
        print(f"✅ État du tour:")
        print(f"   - Action prise: {hero.action_taken_this_turn}")
        print(f"   - Peut attaquer: {hero.can_attack_this_turn}")
        
    except Exception as e:
        print(f"❌ Erreur utilisation capacité: {e}")
        return False
    
    # Test 6: État de combat complet
    print("\n📝 Test 6: État de combat complet")
    try:
        combat_status = hero.get_combat_status()
        abilities_summary = hero.get_abilities_summary()
        
        print(f"✅ État de combat:")
        print(f"   - PV: {combat_status['health']}")
        print(f"   - Sorts: {combat_status['spells']}")
        print(f"   - Tour: {combat_status['turn_state']}")
        
        print(f"✅ Résumé capacités:")
        print(f"   - {abilities_summary}")
        
    except Exception as e:
        print(f"❌ Erreur état de combat: {e}")
        return False
    
    # Test 7: Reset et repos
    print("\n📝 Test 7: Reset et repos")
    try:
        # Reset du tour
        hero.reset_turn_state()
        assert hero.action_taken_this_turn == False
        assert hero.can_attack_this_turn == True
        print(f"✅ Reset du tour réussi")
        
        # Repos complet
        hero.rest()
        assert hero.current_spells == hero.get_total_spells()
        print(f"✅ Repos réussi, sorts récupérés: {hero.current_spells}")
        
    except Exception as e:
        print(f"❌ Erreur reset et repos: {e}")
        return False
    
    print("\n✅ TOUS LES TESTS D'INTÉGRATION CHARACTER RÉUSSIS !")
    return True

def test_complete_workflow():
    """Test du workflow complet avec loader + character"""
    print("\n🔮 === TEST WORKFLOW COMPLET ===")
    
    try:
        from utils.abilities_loader import load_all_abilities
        from models.character import Character
        print("✅ Import complet réussi")
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    
    # Test 1: Chargement des capacités
    print("\n📝 Test 1: Chargement capacités")
    try:
        abilities_data = load_all_abilities("Sorts.xlsx")  # Utilisera le fallback
        
        print(f"✅ Capacités chargées:")
        for hero_code, abilities in abilities_data.items():
            print(f"   - {hero_code}: {len(abilities)} capacités")
        
    except Exception as e:
        print(f"❌ Erreur chargement: {e}")
        return False
    
    # Test 2: Création héros avec capacités
    print("\n📝 Test 2: Héros avec capacités du loader")
    try:
        # Création d'Elneha
        elneha = Character(
            code="P-1",
            name="Elneha",
            precision=6,
            damage=2,
            spells=3,
            health=5
        )
        
        # Ajout des capacités chargées
        if "P-1" in abilities_data:
            elneha.add_abilities(abilities_data["P-1"])
            print(f"✅ Elneha créée avec {len(elneha.abilities)} capacités")
            
            for ability in elneha.abilities:
                print(f"   - {ability.name} (coût: {ability.spell_cost}, type: {ability.ability_type.value})")
        else:
            print("⚠️ Pas de capacités pour P-1 dans les données chargées")
        
    except Exception as e:
        print(f"❌ Erreur création héros: {e}")
        return False
    
    # Test 3: Simulation mini-combat
    print("\n📝 Test 3: Simulation mini-combat")
    try:
        if elneha.abilities:
            # Préparation
            elneha.start_new_combat()
            print(f"✅ Combat démarré")
            print(f"   - PV: {elneha.current_health}/{elneha.get_total_health()}")
            print(f"   - Sorts: {elneha.current_spells}/{elneha.get_total_spells()}")
            
            # Tour 1: Utilisation capacité
            available = elneha.get_available_abilities()
            if available:
                ability = available[0]
                action = elneha.use_ability(ability)
                
                print(f"✅ Tour 1 - Capacité utilisée:")
                print(f"   - {action.ability_name}")
                print(f"   - Succès: {action.success}")
                print(f"   - Empêche attaque: {action.prevents_attack}")
                
                # Simulation attaque si possible
                if elneha.can_attack_this_turn:
                    print(f"   - Peut encore attaquer ce tour")
                else:
                    print(f"   - Ne peut plus attaquer ce tour")
            
            # Tour 2: Reset et nouveau tour
            elneha.reset_turn_state()
            print(f"✅ Tour 2 - État reseté")
            
            # Repos final
            elneha.rest()
            print(f"✅ Repos effectué, sorts: {elneha.current_spells}")
        
    except Exception as e:
        print(f"❌ Erreur simulation combat: {e}")
        return False
    
    print("\n✅ WORKFLOW COMPLET TESTÉ AVEC SUCCÈS !")
    return True

def run_all_tests():
    """Execute tous les tests"""
    print("🧪 === LANCEMENT DE TOUS LES TESTS ===")
    print("Tests du système de capacités pour Périples")
    print("=" * 50)
    
    tests = [
        ("Modèles de Capacités", test_abilities_models),
        ("Chargeur de Capacités", test_abilities_loader),
        ("Intégration Character", test_character_integration),
        ("Workflow Complet", test_complete_workflow)
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
    print("🏆 === RÉSUMÉ DES TESTS ===")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Résultat global: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT RÉUSSIS !")
        print("🚀 Le système de capacités est prêt pour l'intégration !")
    else:
        print("⚠️ Certains tests ont échoué, vérifiez les erreurs ci-dessus")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)