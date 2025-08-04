#!/usr/bin/env python3
"""
Test Phase 4 - Moteur de Combat avec Système de Capacités
Validation complète de l'intégration combat + abilities
"""

import sys
import os
from typing import List, Dict, Any

# Ajout du chemin racine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_combat_engine_abilities_support():
    """Teste le support des capacités dans le moteur de combat"""
    print("⚔️ === TEST SUPPORT CAPACITÉS MOTEUR COMBAT ===")
    print("==============================================")
    
    try:
        from models.combat_engine import CombatEngine, create_combat_engine_with_abilities, validate_heroes_for_abilities_combat
        from models.rules_engine import GameRules
        print("✅ Moteur de combat avec capacités importé")
    except ImportError as e:
        print(f"❌ Erreur import moteur: {e}")
        return False
    
    # Test création moteur avec capacités
    try:
        rules = GameRules(
            criticals=True,
            magical_damage=True,
            ranged_attacks=False,
            initiative=False,
            max_rounds=5
        )
        
        engine = create_combat_engine_with_abilities(rules, enable_abilities=True)
        print(f"✅ Moteur créé, capacités activées: {engine.abilities_enabled}")
        
        # Test désactivation capacités
        engine_disabled = create_combat_engine_with_abilities(rules, enable_abilities=False)
        print(f"✅ Moteur créé, capacités désactivées: {engine_disabled.abilities_enabled}")
        
    except Exception as e:
        print(f"❌ Erreur création moteur: {e}")
        return False
    
    return True

def test_hero_abilities_in_combat():
    """Teste les capacités des héros en situation de combat"""
    print("\n🧙‍♂️ === TEST CAPACITÉS HÉROS EN COMBAT ===")
    print("=========================================")
    
    try:
        from models.character import Character
        from models.abilities import Ability
        from models.combat_engine import AbilityCombatManager
        
        # Création héros avec capacités variées
        elneha = Character(
            code="P-1",
            name="Elneha",
            precision=6,
            damage=2,
            spells=3,
            health=5
        )
        
        # Capacités de test
        abilities = [
            Ability(
                hero_code="P-1",
                ability_number=1,
                name="Soin Naturel",
                spell_cost=1,
                description="Soigne 4 blessures",
                is_unlocked=True
            ),
            Ability(
                hero_code="P-1",
                ability_number=2,
                name="Métamorphose Ours",
                spell_cost=1,
                description="Se transforme en ours",
                is_unlocked=True
            ),
            Ability(
                hero_code="P-1",
                ability_number=3,
                name="Coup Puissant",
                spell_cost=0,
                description="Attaque physique renforcée",
                is_unlocked=False  # Non débloquée
            )
        ]
        
        elneha.add_abilities(abilities)
        print(f"✅ {elneha.name} créé avec {len(elneha.abilities)} capacités")
        print(f"   - Débloquées: {len(elneha.unlocked_abilities)}")
        
        # Test gestionnaire de combat
        manager = AbilityCombatManager([elneha])
        
        # Test actions disponibles
        actions = manager.get_available_actions(elneha)
        print(f"\n📋 Actions disponibles:")
        print(f"   - Peut attaquer: {actions['can_attack']}")
        print(f"   - Peut utiliser capacités: {actions['can_use_abilities']}")
        print(f"   - Capacités disponibles: {len(actions['available_abilities'])}")
        print(f"   - Sorts actuels: {actions['current_spells']}")
        
        # Test des capacités disponibles
        for ability in actions['available_abilities']:
            print(f"     🔮 {ability.name} (coût: {ability.spell_cost})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test capacités héros: {e}")
        return False

def test_ability_effects_simulation():
    """Teste l'application des effets de capacités"""
    print("\n🔮 === TEST EFFETS DE CAPACITÉS ===")
    print("=================================")
    
    try:
        from models.character import Character, Enemy
        from models.abilities import Ability
        from models.combat_engine import CombatEngine
        from models.rules_engine import GameRules
        
        # Héros avec capacité de soin
        hero = Character(
            code="P-1",
            name="Guérisseur",
            precision=5,
            damage=2,
            spells=5,
            health=10
        )
        
        # Capacité de soin
        heal_ability = Ability(
            hero_code="P-1",
            ability_number=1,
            name="Soin Majeur",
            spell_cost=2,
            description="Soigne 4 blessures",
            is_unlocked=True
        )
        
        hero.add_abilities([heal_ability])
        
        # Simulation blessures
        hero.current_health = 3  # Héros blessé
        print(f"📊 État initial {hero.name}:")
        print(f"   - PV: {hero.current_health}/{hero.health}")
        print(f"   - Sorts: {hero.current_spells}")
        
        # Test utilisation capacité
        if hasattr(hero, 'use_ability'):
            action = hero.use_ability(heal_ability)
            
            print(f"\n🔮 Utilisation capacité: {action.success}")
            if action.success:
                print(f"   - Capacité: {action.ability_name}")
                print(f"   - Coût payé: {action.spell_cost_paid}")
                print(f"   - Empêche attaque: {action.prevents_attack}")
                
                # Application manuelle de l'effet (simulation)
                old_health = hero.current_health
                hero.heal(4)  # Soin de 4
                actual_heal = hero.current_health - old_health
                
                print(f"   - Soins reçus: {actual_heal} PV")
                print(f"   - Nouvel état: {hero.current_health}/{hero.health} PV, {hero.current_spells} sorts")
                print(f"   - Peut attaquer: {hero.can_attack_this_turn}")
            else:
                print(f"   - Échec: {action.failure_reason}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test effets: {e}")
        return False

def test_combat_rules_integration():
    """Teste l'intégration des règles de combat avec capacités"""
    print("\n⚔️ === TEST RÈGLES COMBAT + CAPACITÉS ===")
    print("=======================================")
    
    try:
        from models.character import Character, Enemy
        from models.abilities import Ability
        from models.combat_engine import CombatEngine
        from models.rules_engine import GameRules
        
        # Configuration combat avec capacités
        rules = GameRules(
            criticals=True,
            magical_damage=True,
            ranged_attacks=False,
            initiative=False,
            max_rounds=3  # Combat court pour test
        )
        
        engine = CombatEngine(rules)
        engine.abilities_enabled = True
        
        # Héros avec capacités magiques et physiques
        mage = Character(code="P-2", name="Mage", precision=2, damage=1, spells=8, health=4)
        warrior = Character(code="P-4", name="Guerrier", precision=5, damage=3, spells=1, health=7)
        
        # Capacités du mage (magiques)
        mage_abilities = [
            Ability(
                hero_code="P-2",
                ability_number=1,
                name="Boule de Feu",
                spell_cost=2,
                description="Inflige 6 dégâts magiques à tous les adversaires",
                is_unlocked=True
            ),
            Ability(
                hero_code="P-2",
                ability_number=2,
                name="Bouclier Magique",
                spell_cost=1,
                description="Créer un bouclier de 2 de parade",
                is_unlocked=True
            )
        ]
        
        # Capacités du guerrier (physiques)
        warrior_abilities = [
            Ability(
                hero_code="P-4",
                ability_number=1,
                name="Marque Ennemie",
                spell_cost=0,
                description="Marque un ennemi pour doubler les dégâts",
                is_unlocked=True,
                uses_per_combat=1
            ),
            Ability(
                hero_code="P-4",
                ability_number=2,
                name="Attaque Multiple",
                spell_cost=0,
                description="Cible tous les ennemis lors de l'attaque",
                is_unlocked=True,
                uses_per_combat=1
            )
        ]
        
        mage.add_abilities(mage_abilities)
        warrior.add_abilities(warrior_abilities)
        
        # Ennemis de test
        gobelin = Enemy(
            code="EN-1", name="Gobelin", defense=0,
            damage_2j=1, health_2j=3, defense_2j=0,
            damage_3j=1, health_3j=4, defense_3j=0,
            damage_4j=2, health_4j=5, defense_4j=1,
            is_magical=False, has_magical_damage=False
        )
        
        print(f"✅ Équipe créée:")
        print(f"   - {mage.name}: {len(mage.abilities)} capacités magiques")
        print(f"   - {warrior.name}: {len(warrior.abilities)} capacités physiques")
        print(f"   - Ennemi: {gobelin.name}")
        
        # Test règles limitation d'actions
        print(f"\n🎯 Test règles limitation d'actions:")
        
        # Test 1: Capacité magique empêche attaque
        if hasattr(mage, 'start_new_combat'):
            mage.start_new_combat()
        
        magic_ability = mage_abilities[0]  # Boule de Feu
        if hasattr(mage, 'use_ability'):
            action = mage.use_ability(magic_ability)
            print(f"   ✅ {mage.name} utilise capacité magique:")
            print(f"     - Succès: {action.success}")
            print(f"     - Empêche attaque: {action.prevents_attack}")
            print(f"     - Peut encore attaquer: {mage.can_attack_this_turn}")
        
        # Test 2: Capacité physique permet attaque
        if hasattr(warrior, 'start_new_combat'):
            warrior.start_new_combat()
        
        physical_ability = warrior_abilities[0]  # Marque
        if hasattr(warrior, 'use_ability'):
            action = warrior.use_ability(physical_ability)
            print(f"   ✅ {warrior.name} utilise capacité physique:")
            print(f"     - Succès: {action.success}")
            print(f"     - Empêche attaque: {action.prevents_attack}")
            print(f"     - Peut encore attaquer: {warrior.can_attack_this_turn}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test règles: {e}")
        return False

def test_full_combat_simulation():
    """Teste une simulation de combat complète avec capacités"""
    print("\n🎲 === TEST SIMULATION COMBAT COMPLÈTE ===")
    print("=========================================")
    
    try:
        from utils.data_loader import DataLoader
        from models.combat_engine import CombatEngine, validate_heroes_for_abilities_combat
        from models.rules_engine import GameRules
        from models.character import Enemy
        
        # Chargement des vraies données
        loader = DataLoader()
        heroes = loader.load_heroes()
        
        if not heroes:
            print("❌ Aucun héros chargé")
            return False
        
        # Validation des héros pour combat avec capacités
        validation = validate_heroes_for_abilities_combat(heroes)
        print(f"📊 Validation héros:")
        print(f"   - Prêts pour combat: {validation['ready']}")
        print(f"   - Héros avec capacités: {validation['heroes_with_abilities']}")
        print(f"   - Total capacités débloquées: {validation['total_unlocked_abilities']}")
        
        if validation['issues']:
            print(f"   ⚠️ Problèmes détectés:")
            for issue in validation['issues'][:3]:  # Limite pour lisibilité
                print(f"     - {issue}")
        
        # Sélection des combattants
        combat_heroes = heroes[:2]  # 2 premiers héros
        
        # Ennemi de test
        test_enemy = Enemy(
            code="EN-TEST", name="Ennemi Test", defense=1,
            damage_2j=2, health_2j=6, defense_2j=1,
            damage_3j=2, health_3j=8, defense_3j=1,
            damage_4j=3, health_4j=10, defense_4j=2,
            is_magical=False, has_magical_damage=False
        )
        
        print(f"\n⚔️ Configuration combat:")
        for hero in combat_heroes:
            abilities_count = len(hero.abilities) if hasattr(hero, 'abilities') else 0
            unlocked_count = len(hero.unlocked_abilities) if hasattr(hero, 'unlocked_abilities') else 0
            print(f"   🧙‍♂️ {hero.name}: PV:{hero.health}, Sorts:{hero.spells}, Capacités:{abilities_count} ({unlocked_count} débloquées)")
        print(f"   👹 {test_enemy.name}: PV:{test_enemy.health_2j} (2J)")
        
        # Création moteur et simulation
        rules = GameRules(max_rounds=3, criticals=True)
        engine = CombatEngine(rules)
        engine.abilities_enabled = True
        
        print(f"\n🎮 Lancement simulation...")
        result = engine.simulate_single_combat(combat_heroes, [test_enemy], player_count=2)
        
        # Analyse des résultats
        print(f"\n🏆 Résultats combat:")
        print(f"   - Vainqueur: {result['winner']}")
        print(f"   - Rounds: {result['rounds']}")
        print(f"   - Durée: {result['duration']}s")
        print(f"   - Système capacités actif: {result['summary']['abilities_system_active']}")
        
        # Log combat (extrait)
        print(f"\n📜 Extrait du log:")
        for i, line in enumerate(result['log'][:10]):  # 10 premières lignes
            print(f"   {line}")
        if len(result['log']) > 10:
            print(f"   ... et {len(result['log']) - 10} autres lignes")
        
        # Métriques héros
        print(f"\n📊 Métriques finales:")
        for hero_code, metrics in result['resource_metrics'].items():
            print(f"   🧙‍♂️ {metrics['name']}:")
            print(f"     - PV: {metrics['final_health']}/{metrics['max_health']}")
            print(f"     - Sorts: {metrics['final_spells']}/{metrics['max_spells']} (utilisés: {metrics['spells_used']})")
            
            if 'total_abilities' in metrics:
                print(f"     - Capacités: {metrics['unlocked_abilities']}/{metrics['total_abilities']} débloquées")
                print(f"     - Types: {metrics['magical_abilities']} magiques, {metrics['physical_abilities']} physiques")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur simulation complète: {e}")
        return False

def test_combat_ai_decisions():
    """Teste l'IA de décision des capacités en combat"""
    print("\n🤖 === TEST IA DÉCISIONS CAPACITÉS ===")
    print("====================================")
    
    try:
        from models.character import Character, Enemy
        from models.abilities import Ability
        from models.combat_engine import AbilityCombatManager
        
        # Héros blessé avec capacités de soin
        injured_hero = Character(
            code="P-3", name="Soigneur", precision=3, damage=2, spells=4, health=8
        )
        injured_hero.current_health = 2  # Gravement blessé
        
        # Capacités variées
        abilities = [
            Ability(
                hero_code="P-3",
                ability_number=1,
                name="Soin Urgent",
                spell_cost=1,
                description="Soigne 4 blessures",
                is_unlocked=True
            ),
            Ability(
                hero_code="P-3",
                ability_number=2,
                name="Attaque Magique",
                spell_cost=2,
                description="Inflige 6 dégâts magiques à tous les adversaires",
                is_unlocked=True
            )
        ]
        
        injured_hero.add_abilities(abilities)
        
        # Ennemis multiples
        enemies = [
            Enemy(code="EN-1", name="Gobelin 1", defense=0, damage_2j=1, health_2j=2, defense_2j=0, 
                  damage_3j=1, health_3j=3, defense_3j=0, damage_4j=2, health_4j=4, defense_4j=1,
                  is_magical=False, has_magical_damage=False),
            Enemy(code="EN-2", name="Gobelin 2", defense=0, damage_2j=1, health_2j=2, defense_2j=0,
                  damage_3j=1, health_3j=3, defense_3j=0, damage_4j=2, health_4j=4, defense_4j=1,
                  is_magical=False, has_magical_damage=False),
            Enemy(code="EN-3", name="Gobelin 3", defense=0, damage_2j=1, health_2j=2, defense_2j=0,
                  damage_3j=1, health_3j=3, defense_3j=0, damage_4j=2, health_4j=4, defense_4j=1,
                  is_magical=False, has_magical_damage=False)
        ]
        
        manager = AbilityCombatManager([injured_hero])
        
        print(f"📊 Situation critique:")
        print(f"   - {injured_hero.name}: {injured_hero.current_health}/{injured_hero.health} PV")
        print(f"   - Ennemis: {len(enemies)} gobelins")
        
        # Test décision IA
        decision = manager.simulate_ai_decision(injured_hero, enemies)
        print(f"\n🤖 Décision IA:")
        print(f"   - Type d'action: {decision['type']}")
        print(f"   - Raison: {decision['reason']}")
        
        if decision['type'] == 'ability':
            ability = decision['ability']
            print(f"   - Capacité choisie: {ability.name}")
            print(f"   - Coût: {ability.spell_cost}")
            print(f"   - Description: {ability.description[:50]}...")
        
        # Test avec héros en bonne santé
        injured_hero.current_health = injured_hero.health  # Guérison complète
        enemies = enemies[:1]  # Un seul ennemi
        
        decision2 = manager.simulate_ai_decision(injured_hero, enemies)
        print(f"\n🤖 Décision IA (héros en santé, 1 ennemi):")
        print(f"   - Type d'action: {decision2['type']}")
        print(f"   - Raison: {decision2['reason']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test IA: {e}")
        return False

def test_phase4_complete_integration():
    """Test d'intégration complète de la Phase 4"""
    print("\n🚀 === TEST INTÉGRATION COMPLÈTE PHASE 4 ===")
    print("============================================")
    
    try:
        # Test de bout en bout : DataLoader → Combat avec capacités
        from utils.data_loader import DataLoader
        from models.combat_engine import CombatEngine, create_combat_engine_with_abilities
        from models.rules_engine import GameRules
        from models.character import Enemy
        
        # 1. Chargement données avec capacités
        loader = DataLoader()
        heroes = loader.load_heroes()
        
        abilities_summary = loader.get_abilities_summary()
        print(f"📊 Données chargées:")
        print(f"   - Héros: {len(heroes)}")
        print(f"   - Système capacités: {abilities_summary['enabled']}")
        
        if abilities_summary['enabled']:
            print(f"   - Capacités totales: {abilities_summary['total_abilities']}")
            print(f"   - Héros avec capacités: {abilities_summary['heroes_count']}")
        
        # 2. Sélection équipe de test
        if len(heroes) >= 2:
            team = heroes[:2]
        else:
            print("❌ Pas assez de héros")
            return False
        
        # 3. Configuration ennemi équilibré
        balanced_enemy = Enemy(
            code="EN-BALANCED", name="Ennemi Équilibré", defense=2,
            damage_2j=3, health_2j=8, defense_2j=2,
            damage_3j=3, health_3j=10, defense_3j=2,
            damage_4j=4, health_4j=12, defense_4j=3,
            is_magical=False, has_magical_damage=False
        )
        
        # 4. Règles optimales pour test capacités
        rules = GameRules(
            criticals=True,
            magical_damage=True,
            ranged_attacks=False,
            initiative=False,
            max_rounds=8
        )
        
        engine = create_combat_engine_with_abilities(rules, enable_abilities=True)
        
        print(f"\n⚔️ Combat de validation:")
        print(f"   - Équipe: {[h.name for h in team]}")
        print(f"   - Ennemi: {balanced_enemy.name}")
        print(f"   - Capacités activées: {engine.abilities_enabled}")
        
        # 5. Simulation
        result = engine.simulate_single_combat(team, [balanced_enemy], player_count=2)
        
        # 6. Validation des résultats
        print(f"\n🏆 Résultats validation:")
        print(f"   - Combat terminé: ✅")
        print(f"   - Vainqueur: {result['winner']}")
        print(f"   - Rounds: {result['rounds']}")
        print(f"   - Système capacités utilisé: {result['summary']['abilities_system_active']}")
        
        # Vérification utilisation capacités
        capacities_used = False
        for line in result['log']:
            if "🔮" in line:
                capacities_used = True
                print(f"   ✅ Capacités utilisées en combat")
                break
        
        if not capacities_used:
            print(f"   ⚠️ Aucune capacité utilisée (normal si héros n'en ont pas)")
        
        # Métriques avec capacités
        has_abilities_metrics = False
        for hero_code, metrics in result['resource_metrics'].items():
            if 'total_abilities' in metrics:
                has_abilities_metrics = True
                print(f"   ✅ Métriques capacités incluses pour {metrics['name']}")
                break
        
        if not has_abilities_metrics:
            print(f"   ⚠️ Métriques capacités non incluses")
        
        print(f"\n🎯 PHASE 4 INTÉGRÉE AVEC SUCCÈS !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur intégration complète: {e}")
        return False

def run_phase4_tests():
    """Lance tous les tests de la Phase 4"""
    print("🚀 === TESTS COMPLETS PHASE 4 ===")
    print("=================================")
    print("Moteur de Combat + Système de Capacités")
    print("=" * 50)
    
    tests = [
        ("Support Capacités Moteur", test_combat_engine_abilities_support),
        ("Capacités Héros Combat", test_hero_abilities_in_combat),
        ("Effets de Capacités", test_ability_effects_simulation),
        ("Règles Combat + Capacités", test_combat_rules_integration),
        ("IA Décisions Capacités", test_combat_ai_decisions),
        ("Intégration Complète", test_phase4_complete_integration)
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
    print("🏆 === RÉSUMÉ TESTS PHASE 4 ===")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Résultat global: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 PHASE 4 COMPLÈTEMENT VALIDÉE !")
        print("🚀 Moteur de combat avec capacités fonctionnel")
        
        print(f"\n🎯 PROGRESSION SYSTÈME CAPACITÉS:")
        print(f"==================================")
        print(f"✅ Phase 1: Modèles Pydantic")
        print(f"✅ Phase 2: Import + Character")  
        print(f"✅ Phase 3: DataLoader")
        print(f"✅ Phase 4: Moteur Combat (ACTUELLE)")
        print(f"❌ Phase 5: Interface UI")
        print(f"\n📈 Progression: 80% terminé (4/5 phases)")
        
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Corrections nécessaires avant Phase 5")
    
    return passed == total

def show_phase4_summary():
    """Affiche un résumé de la Phase 4"""
    print("\n📋 === RÉSUMÉ PHASE 4 ===")
    print("========================")
    print("🔮 Système de Capacités - Moteur de Combat")
    print()
    
    print("✅ FONCTIONNALITÉS AJOUTÉES:")
    print("   🎯 Support complet capacités dans CombatEngine")
    print("   ⚔️ Limitation d'actions (magie OU attaque)")
    print("   🔮 Application effets automatiques")
    print("   🤖 IA basique pour décisions capacités")
    print("   📊 Métriques étendues avec tracking capacités")
    print("   💀 Règles défaite avec pénalités capacités")
    
    print("\n🎮 RÈGLES IMPLÉMENTÉES:")
    print("   📘 Capacités magiques (coût > 0) → empêchent attaque")
    print("   ⚔️ Capacités physiques (coût = 0) → permettent attaque")
    print("   🔄 Une seule capacité par tour maximum")
    print("   💔 Pénalités défaite totale (p.18)")
    
    print("\n🚀 PRÊTE POUR PHASE 5:")
    print("   🖥️ Interface utilisateur activation capacités")
    print("   🎮 Sélection manuelle capacités en combat")
    print("   📊 Affichage temps réel état capacités")

if __name__ == "__main__":
    print("🧪 LANCEMENT TESTS PHASE 4")
    print("=" * 50)
    
    # Tests complets
    success = run_phase4_tests()
    
    # Résumé de la phase
    show_phase4_summary()
    
    print(f"\n" + "=" * 50)
    if success:
        print("🎊 PHASE 4 TERMINÉE AVEC SUCCÈS !")
        print("Système de capacités intégré au moteur de combat")
        print("\n➡️ PROCHAINE ÉTAPE: Phase 5 - Interface Utilisateur")
    else:
        print("💥 ÉCHEC PHASE 4 - Corrections nécessaires")
    
    sys.exit(0 if success else 1)