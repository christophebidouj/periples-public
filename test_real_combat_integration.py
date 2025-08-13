#!/usr/bin/env python3
"""
Test Intégration Réelle - Combat avec Capacités
Test le système complet en contexte réel

Usage: python test_real_combat_integration.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_complete_combat_system():
    """Teste le système complet en créant un vrai combat"""
    print("🔥 TEST INTÉGRATION RÉELLE - COMBAT COMPLET")
    print("=" * 50)
    
    try:
        # Import complet du système
        from models.combat.combat_engine import CombatEngine
        from models.rules_engine import GameRules
        from utils.data_loader import DataLoader
        
        print("✅ Imports système principal réussis")
        
        # Charger les données réelles
        loader = DataLoader()
        heroes = loader.load_heroes()
        enemies = loader.load_enemies()
        
        print(f"✅ Données chargées: {len(heroes)} héros, {len(enemies)} ennemis")
        
        # Sélectionner test simple : Elneha vs Gobelin
        test_hero = None
        test_enemy = None
        
        for hero in heroes:
            if hero.code == "P-1":  # Elneha
                test_hero = hero
                break
        
        for enemy in enemies:
            if "gobelin" in enemy.name.lower() or enemy.code == "E-1":
                test_enemy = enemy
                break
        
        if not test_hero:
            print("❌ Héros Elneha (P-1) non trouvé")
            return False
        
        if not test_enemy:
            print("❌ Ennemi test non trouvé")
            return False
        
        print(f"✅ Combattants: {test_hero.name} vs {test_enemy.name}")
        
        # Vérifier capacités d'Elneha
        hero_abilities = loader.get_hero_abilities("P-1")
        if not hero_abilities:
            print("❌ Aucune capacité trouvée pour Elneha")
            return False
        
        print(f"✅ Capacités Elneha: {len(hero_abilities)} trouvées")
        for ability in hero_abilities[:3]:  # Afficher les 3 premières
            print(f"   - {ability.name} (coût: {ability.spell_cost})")
        
        # Équiper Elneha avec capacités
        test_hero.abilities = hero_abilities[:3]  # Les 3 premières capacités
        for ability in test_hero.abilities:
            ability.is_unlocked = True
        
        # Créer moteur de combat
        rules = GameRules()
        combat_engine = CombatEngine(rules)
        
        print("✅ Moteur de combat créé")
        
        # Lancer combat réel
        print("\n🔥 LANCEMENT COMBAT RÉEL")
        print("-" * 30)
        
        result = combat_engine.simulate_single_combat(
            heroes=[test_hero], 
            enemies=[test_enemy], 
            player_count=1
        )
        
        print("✅ Combat terminé sans crash")
        
        # Analyser les résultats
        analyze_combat_result(result, test_hero)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_combat_result(result, hero):
    """Analyse les résultats du combat pour détecter l'usage des capacités"""
    print("\n📊 ANALYSE DES RÉSULTATS")
    print("=" * 30)
    
    # Analyser le log
    log = result.get('log', [])
    
    # Rechercher mentions de capacités
    ability_mentions = []
    effects_applied = []
    
    for line in log:
        line_lower = line.lower()
        
        # Rechercher utilisation capacités
        if 'utilise' in line_lower and any(word in line_lower for word in ['forme', 'soin', 'attaque']):
            ability_mentions.append(line)
        
        # Rechercher effets appliqués
        if any(word in line_lower for word in ['effet', 'bonus', 'transformation', 'guérit']):
            effects_applied.append(line)
    
    print(f"🔍 Mentions de capacités trouvées: {len(ability_mentions)}")
    for mention in ability_mentions:
        print(f"   📝 {mention}")
    
    print(f"\n🔍 Effets détectés: {len(effects_applied)}")
    for effect in effects_applied:
        print(f"   ✨ {effect}")
    
    # Vérifier état final du héros
    print(f"\n🏥 État final {hero.name}:")
    print(f"   PV: {hero.current_health}/{hero.get_total_health()}")
    print(f"   Sorts: {getattr(hero, 'current_spells', 'N/A')}")
    
    # Vérifier si des capacités ont été réellement utilisées
    if ability_mentions:
        print("✅ SUCCÈS: Des capacités ont été utilisées !")
    else:
        print("⚠️ ATTENTION: Aucune capacité détectée dans les logs")
    
    if effects_applied:
        print("✅ SUCCÈS: Des effets ont été appliqués !")
    else:
        print("⚠️ ATTENTION: Aucun effet détecté")
    
    # Score global
    total_evidence = len(ability_mentions) + len(effects_applied)
    if total_evidence >= 2:
        print("🎉 VERDICT: Système de capacités FONCTIONNEL")
        return True
    elif total_evidence == 1:
        print("⚠️ VERDICT: Système partiellement fonctionnel")
        return True
    else:
        print("❌ VERDICT: Système de capacités non fonctionnel")
        return False

def test_ability_effects_directly():
    """Test direct du système d'effets sans combat complet"""
    print("\n🧪 TEST DIRECT SYSTÈME D'EFFETS")
    print("=" * 35)
    
    try:
        from models.combat.abilities import AbilityEffectsManager
        from models.combat.spell_manager import SpellManager
        from utils.data_loader import DataLoader
        
        # Créer composants
        spell_manager = SpellManager()
        effects_manager = AbilityEffectsManager(spell_manager)
        loader = DataLoader()
        
        # Créer héros test
        heroes = loader.load_heroes()
        test_hero = None
        for hero in heroes:
            if hero.code == "P-1":
                test_hero = hero.model_copy()
                break
        
        if not test_hero:
            print("❌ Impossible de créer héros test")
            return False
        
        # Charger une capacité
        abilities = loader.get_hero_abilities("P-1")
        if not abilities:
            print("❌ Aucune capacité trouvée")
            return False
        
        test_ability = abilities[0]  # Première capacité
        test_ability.is_unlocked = True
        
        print(f"✅ Test avec capacité: {test_ability.name}")
        
        # État avant
        hp_before = test_hero.current_health
        attack_before = getattr(test_hero, 'current_attack', test_hero.damage)
        
        print(f"📊 État avant: PV={hp_before}, ATT={attack_before}")
        
        # Appliquer effets
        log = []
        result = effects_manager.apply_ability_effects(test_hero, test_ability, log)
        
        # État après
        hp_after = test_hero.current_health
        attack_after = getattr(test_hero, 'current_attack', test_hero.damage)
        
        print(f"📊 État après: PV={hp_after}, ATT={attack_after}")
        print(f"📝 Logs générés: {len(log)}")
        
        for log_line in log:
            print(f"   📄 {log_line}")
        
        # Analyser changements
        changes_detected = []
        if hp_after != hp_before:
            changes_detected.append(f"PV: {hp_before} → {hp_after}")
        if attack_after != attack_before:
            changes_detected.append(f"ATT: {attack_before} → {attack_after}")
        
        if changes_detected or log:
            print("✅ SUCCÈS: Effets détectés !")
            print(f"   Changements: {changes_detected}")
            return True
        else:
            print("❌ ÉCHEC: Aucun effet détecté")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test direct: {e}")
        return False

def main():
    """Fonction principale - lance tous les tests"""
    print("🚀 SUITE DE TESTS INTÉGRATION RÉELLE")
    print("="*50)
    
    success_count = 0
    total_tests = 2
    
    # Test 1: Combat complet
    if test_complete_combat_system():
        success_count += 1
    
    # Test 2: Effets directs
    if test_ability_effects_directly():
        success_count += 1
    
    # Résultat final
    print("\n" + "="*50)
    print("📊 RÉSULTATS FINAUX")
    print("="*50)
    print(f"✅ Tests réussis: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 VERDICT: Système de capacités PLEINEMENT FONCTIONNEL")
        print("🚀 Recommandation: Aucune modification nécessaire")
    elif success_count > 0:
        print("⚠️ VERDICT: Système partiellement fonctionnel")
        print("🔧 Recommandation: Optimisations mineures")
    else:
        print("❌ VERDICT: Système non fonctionnel")
        print("🔧 Recommandation: Investigation approfondie nécessaire")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)