# diagnostic_capacites
"""
Script de diagnostic des capacités - Version mise à jour
Compatible avec le système de capacités individuelles + ancien système
"""

import sys
import os
from typing import List, Dict, Any

def test_imports():
    """Teste les imports critiques"""
    print("🔍 Test des imports critiques...")
    
    try:
        from models.character import Character
        print("   ✅ models.character.Character")
    except Exception as e:
        print(f"   ❌ models.character.Character: {e}")
        return False
    
    try:
        from models.combat.abilities.ability_manager import AbilityEffectsManager
        print("   ✅ AbilityEffectsManager")
    except Exception as e:
        print(f"   ❌ AbilityEffectsManager: {e}")
        return False
    
    try:
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        print("   ✅ ABILITY_REGISTRY (nouveau système)")
    except Exception as e:
        print(f"   ⚠️ ABILITY_REGISTRY non disponible: {e}")
    
    return True

def load_abilities_data():
    """Charge les données des capacités depuis ability_names.csv"""
    try:
        import pandas as pd
        df = pd.read_csv("ability_names.csv")
        return df
    except Exception as e:
        print(f"⚠️ Impossible de charger ability_names.csv: {e}")
        return None

def analyze_individual_abilities():
    """Analyse les capacités individuelles enregistrées"""
    print("\n📊 ANALYSE DES CAPACITÉS INDIVIDUELLES")
    print("=" * 60)
    
    try:
        from models.combat.abilities.individual_abilities import ABILITY_REGISTRY
        
        # Statistiques générales
        total_registered = ABILITY_REGISTRY.get_registered_count()
        print(f"📝 Capacités individuelles enregistrées: {total_registered}/48")
        
        if total_registered > 0:
            # Détails par héros
            heroes_with_abilities = ABILITY_REGISTRY.get_heroes_with_abilities()
            print(f"🎭 Héros avec capacités: {', '.join(heroes_with_abilities)}")
            
            # Debug détaillé
            debug_info = ABILITY_REGISTRY.get_debug_info()
            for hero_code, hero_info in debug_info['heroes'].items():
                if hero_info['registered'] > 0:
                    print(f"\n🎭 {hero_code}: {hero_info['registered']}/6 capacités")
                    for ability in hero_info['abilities']:
                        print(f"   ✅ {ability['number']}: {ability['name']}")
        
        return total_registered
        
    except ImportError:
        print("❌ Système de capacités individuelles non disponible")
        return 0

def simulate_ability_effects():
    """Simule l'application d'effets de capacités"""
    print("\n🧪 SIMULATION D'EFFETS DE CAPACITÉS")
    print("=" * 60)
    
    try:
        from models.combat.abilities.ability_manager import AbilityEffectsManager
        from models.character import Character
        
        # Créer un personnage de test
        test_hero = Character(
            code="P-1",
            name="Elneha Test",
            precision=5,
            damage=3,
            spells=4,
            health=10
        )
        
        # Créer une capacité de test simple
        class TestAbility:
            def __init__(self, name, description, ability_number=1):
                self.name = name
                self.description = description
                self.ability_number = ability_number
                self.hero_code = "P-1"
        
        # Simuler un spell_manager simple
        class MockSpellManager:
            pass
        
        spell_manager = MockSpellManager()
        ability_manager = AbilityEffectsManager(spell_manager)
        
        # Test avec capacité de transformation
        transform_ability = TestAbility("Forme d'ours test", "Permet à Elneha de se métamorphoser en Ours.")
        log = []
        
        print("🔧 Test application d'effet...")
        result = ability_manager.apply_ability_effects(test_hero, transform_ability, log)
        
        print(f"   Résultat: {'✅ Succès' if result else '❌ Échec'}")
        if log:
            print("   Logs générés:")
            for log_entry in log:
                print(f"     {log_entry}")
        
        # Statistiques de migration
        stats = ability_manager.get_migration_stats()
        print(f"\n📈 Statistiques de migration:")
        print(f"   🔧 Capacités individuelles utilisées: {stats['individual_abilities_used']}")
        print(f"   🔄 Ancien système utilisé: {stats['legacy_abilities_used']}")
        print(f"   📊 Système individuel disponible: {stats['individual_system_available']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur simulation: {e}")
        return False

def analyze_legacy_system():
    """Analyse le système legacy pour comparaison"""
    print("\n🔄 ANALYSE DU SYSTÈME LEGACY")
    print("=" * 60)
    
    # Charger les données des capacités
    df = load_abilities_data()
    if df is None:
        print("❌ Impossible d'analyser le système legacy sans ability_names.csv")
        return 0
    
    total_abilities = len(df)
    print(f"📋 Total capacités définies: {total_abilities}")
    
    # Analyse par héros
    heroes = df['hero_code'].unique()
    print(f"🎭 Héros: {', '.join(sorted(heroes))}")
    
    for hero in sorted(heroes):
        hero_abilities = df[df['hero_code'] == hero]
        print(f"   {hero}: {len(hero_abilities)} capacités")
    
    return total_abilities

def generate_comparison_report():
    """Génère un rapport de comparaison entre ancien et nouveau système"""
    print("\n📊 RAPPORT DE COMPARAISON")
    print("=" * 60)
    
    # Analyser les deux systèmes
    individual_count = analyze_individual_abilities()
    legacy_count = analyze_legacy_system()
    
    print(f"\n📈 PROGRESSION DE LA MIGRATION:")
    print(f"   📝 Capacités définies (legacy): {legacy_count}")
    print(f"   🔧 Capacités individuelles: {individual_count}")
    
    if legacy_count > 0:
        percentage = (individual_count / legacy_count) * 100
        print(f"   📊 Progression: {percentage:.1f}%")
        
        # Estimation capacités mécaniques
        mechanical_estimate = 2 + individual_count  # 2 transformations existantes + nouvelles
        print(f"   ⚙️ Capacités mécaniques estimées: ~{mechanical_estimate}")
    
    return individual_count, legacy_count

def main():
    """Fonction principale du diagnostic"""
    print("🏥 DIAGNOSTIC DES CAPACITÉS - PÉRIPLES BALANCE WORKSHOP")
    print("=" * 60)
    print("Version: Compatible système individuel + legacy")
    print("Date: Phase 1 de migration\n")
    
    # Tests d'intégrité
    if not test_imports():
        print("\n❌ ÉCHEC: Imports critiques défaillants")
        sys.exit(1)
    
    # Simulation des effets
    simulation_ok = simulate_ability_effects()
    
    # Rapport de comparaison
    individual_count, legacy_count = generate_comparison_report()
    
    # Résumé final
    print(f"\n🎯 RÉSUMÉ FINAL")
    print("=" * 60)
    
    if simulation_ok:
        print("✅ Système fonctionnel")
    else:
        print("⚠️ Problèmes détectés dans la simulation")
    
    print(f"📊 Capacités individuelles: {individual_count}/48")
    
    if individual_count >= 2:
        print("🎉 PHASE 1 VALIDÉE - Infrastructure opérationnelle")
    else:
        print("⚠️ Phase 1 incomplète")
    
    print(f"🚀 Prêt pour Phase 2: Migration vers {individual_count + 10} capacités")

if __name__ == "__main__":
    main()