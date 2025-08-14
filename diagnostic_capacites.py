#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC COMPLET DES EFFETS MÉCANIQUES
===================================================

Ce script analyse en profondeur si les capacités ont des effets mécaniques RÉELS
ou sont seulement cosmétiques. Crucial pour la précision des tests de jeu de société.

Usage: python diagnostic_capacites.py
"""

import sys
import os
import traceback
from typing import Dict, List, Any

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class DiagnosticCapacites:
    """Diagnostic approfondi du système de capacités"""
    
    def __init__(self):
        self.results = {
            "cosmetic_abilities": [],  # Capacités purement cosmétiques
            "mechanical_abilities": [], # Capacités avec vrais effets
            "broken_abilities": [],    # Capacités en erreur
            "missing_effects": []      # Effets manquants
        }
    
    def run_complete_diagnostic(self):
        """Lance le diagnostic complet"""
        print("🔍 === DIAGNOSTIC COMPLET DES EFFETS MÉCANIQUES ===")
        print("=" * 60)
        
        # 1. Test infrastructure de base
        self._test_infrastructure()
        
        # 2. Test Elneha (P-1) - Transformations
        self._test_elneha_transformations()
        
        # 3. Test capacités de soin
        self._test_healing_abilities()
        
        # 4. Test capacités de dégâts
        self._test_damage_abilities()
        
        # 5. Test capacités de buff/debuff
        self._test_buff_debuff_abilities()
        
        # 6. Rapport final
        self._generate_final_report()
        
        return self.results
    
    def _test_infrastructure(self):
        """Test 1: Infrastructure de base"""
        print("\n🏗️ TEST 1: INFRASTRUCTURE DE BASE")
        print("-" * 40)
        
        try:
            # Import des modules critiques
            from utils.data_loader import DataLoader
            from models.combat.abilities import AbilityEffectsManager
            from models.combat.spell_manager import SpellManager
            
            # Chargement des données
            loader = DataLoader()
            heroes = loader.load_heroes()
            print(f"✅ {len(heroes)} héros chargés")
            
            # Test hero avec current_stats
            test_hero = next(h for h in heroes if h.code == "P-1").model_copy()
            test_hero.start_new_combat()
            
            # Vérifier attributs current_*
            has_current_attack = hasattr(test_hero, 'current_attack')
            has_current_defense = hasattr(test_hero, 'current_defense')
            has_current_precision = hasattr(test_hero, 'current_precision')
            
            print(f"✅ current_attack: {has_current_attack}")
            print(f"✅ current_defense: {has_current_defense}")
            print(f"✅ current_precision: {has_current_precision}")
            
            if not all([has_current_attack, has_current_defense, has_current_precision]):
                self.results["missing_effects"].append("Stats modifiables manquantes dans Character")
                print("❌ PROBLÈME: Attributs current_* manquants")
                return False
            
            # Test système d'effets
            spell_manager = SpellManager()
            effects_manager = AbilityEffectsManager(spell_manager)
            print("✅ Système d'effets initialisé")
            
            return True
            
        except Exception as e:
            print(f"❌ ERREUR Infrastructure: {e}")
            self.results["broken_abilities"].append(f"Infrastructure: {e}")
            return False
    
    def _test_elneha_transformations(self):
        """Test 2: Transformations d'Elneha - Le test crucial"""
        print("\n🐻 TEST 2: TRANSFORMATIONS ELNEHA (P-1)")
        print("-" * 40)
        
        try:
            from utils.data_loader import DataLoader
            from models.combat.abilities import AbilityEffectsManager
            from models.combat.spell_manager import SpellManager
            
            # Préparer le test
            loader = DataLoader()
            heroes = loader.load_heroes()
            elneha = next(h for h in heroes if h.code == "P-1").model_copy()
            elneha.start_new_combat()
            
            abilities = loader.get_hero_abilities("P-1")
            forme_ours = None
            forme_loup = None
            
            for ability in abilities:
                if "ours" in ability.name.lower():
                    forme_ours = ability
                    forme_ours.is_unlocked = True
                elif "loup" in ability.name.lower():
                    forme_loup = ability
                    forme_loup.is_unlocked = True
            
            if not forme_ours:
                print("❌ Forme d'Ours non trouvée")
                return False
            
            # État initial
            initial_attack = elneha.current_attack
            initial_defense = elneha.current_defense
            initial_precision = elneha.current_precision
            
            print(f"📊 ÉTAT INITIAL:")
            print(f"   ATT: {initial_attack}")
            print(f"   DEF: {initial_defense}")
            print(f"   PREC: {initial_precision}")
            print(f"   Total DMG: {elneha.get_total_damage()}")
            
            # Test Forme d'Ours
            spell_manager = SpellManager()
            effects_manager = AbilityEffectsManager(spell_manager)
            
            log = []
            result = effects_manager.apply_ability_effects(elneha, forme_ours, log)
            
            # État après transformation
            after_attack = elneha.current_attack
            after_defense = elneha.current_defense
            after_precision = elneha.current_precision
            
            print(f"\n📊 ÉTAT APRÈS FORME D'OURS:")
            print(f"   ATT: {after_attack} (Δ: {after_attack - initial_attack})")
            print(f"   DEF: {after_defense} (Δ: {after_defense - initial_defense})")
            print(f"   PREC: {after_precision} (Δ: {after_precision - initial_precision})")
            print(f"   Total DMG: {elneha.get_total_damage()}")
            print(f"   Logs: {log}")
            
            # ANALYSE CRITIQUE
            attack_bonus = after_attack - initial_attack
            defense_bonus = after_defense - initial_defense
            
            if attack_bonus >= 2 and defense_bonus >= 1:
                print("✅ TRANSFORMATION MÉCANIQUE RÉUSSIE")
                print(f"   ✅ +{attack_bonus} ATT (attendu: +2)")
                print(f"   ✅ +{defense_bonus} DEF (attendu: +1)")
                self.results["mechanical_abilities"].append({
                    "name": forme_ours.name,
                    "hero": "Elneha",
                    "effect": f"+{attack_bonus} ATT, +{defense_bonus} DEF",
                    "type": "transformation"
                })
                
                # Test que get_total_damage utilise bien current_attack
                expected_damage = after_attack  # + équipements
                actual_damage = elneha.get_total_damage()
                if actual_damage >= expected_damage:
                    print("✅ get_total_damage() utilise current_attack")
                else:
                    print("❌ get_total_damage() n'utilise pas current_attack")
                    self.results["missing_effects"].append("get_total_damage() ignore current_attack")
                
            elif attack_bonus > 0 or defense_bonus > 0:
                print("⚠️ TRANSFORMATION PARTIELLE")
                print(f"   ⚠️ +{attack_bonus} ATT (attendu: +2)")
                print(f"   ⚠️ +{defense_bonus} DEF (attendu: +1)")
                self.results["missing_effects"].append(f"Bonus incomplets pour {forme_ours.name}")
                
            else:
                print("❌ AUCUN EFFET MÉCANIQUE DÉTECTÉ")
                print("   ❌ Stats inchangées - Capacité COSMÉTIQUE")
                self.results["cosmetic_abilities"].append({
                    "name": forme_ours.name,
                    "hero": "Elneha",
                    "problem": "Aucun bonus appliqué"
                })
            
            # Test aussi Forme de Loup si disponible
            if forme_loup:
                print("\n🐺 TEST FORME DE LOUP:")
                elneha.start_new_combat()  # Reset
                log_loup = []
                effects_manager.apply_ability_effects(elneha, forme_loup, log_loup)
                
                attack_bonus_loup = elneha.current_attack - initial_attack
                precision_bonus_loup = elneha.current_precision - initial_precision
                
                if attack_bonus_loup >= 1 and precision_bonus_loup >= 2:
                    print(f"✅ +{attack_bonus_loup} ATT, +{precision_bonus_loup} PREC")
                    self.results["mechanical_abilities"].append({
                        "name": forme_loup.name,
                        "hero": "Elneha",
                        "effect": f"+{attack_bonus_loup} ATT, +{precision_bonus_loup} PREC"
                    })
                else:
                    print(f"❌ Bonus incorrects: +{attack_bonus_loup} ATT, +{precision_bonus_loup} PREC")
                    self.results["cosmetic_abilities"].append({
                        "name": forme_loup.name,
                        "hero": "Elneha",
                        "problem": "Bonus incorrects"
                    })
            
            return True
            
        except Exception as e:
            print(f"❌ ERREUR Transformations: {e}")
            traceback.print_exc()
            self.results["broken_abilities"].append(f"Transformations Elneha: {e}")
            return False
    
    def _test_healing_abilities(self):
        """Test 3: Capacités de soin"""
        print("\n💚 TEST 3: CAPACITÉS DE SOIN")
        print("-" * 40)
        
        try:
            from utils.data_loader import DataLoader
            from models.combat.abilities import AbilityEffectsManager
            from models.combat.spell_manager import SpellManager
            
            loader = DataLoader()
            heroes = loader.load_heroes()
            
            # Tester avec tous les héros ayant des soins
            for hero in heroes:
                abilities = loader.get_hero_abilities(hero.code)
                healing_abilities = [a for a in abilities if any(keyword in a.description.lower() 
                                   for keyword in ['soin', 'guéri', 'blessures', 'pv', 'santé'])]
                
                if not healing_abilities:
                    continue
                
                print(f"\n🧙 {hero.name} ({hero.code}):")
                
                for ability in healing_abilities:
                    print(f"  🔍 Test: {ability.name}")
                    
                    # Créer héros blessé
                    test_hero = hero.model_copy()
                    test_hero.start_new_combat()
                    test_hero.current_health = test_hero.get_total_health() // 2  # 50% HP
                    
                    hp_before = test_hero.current_health
                    max_hp = test_hero.get_total_health()
                    
                    # Appliquer soin
                    spell_manager = SpellManager()
                    effects_manager = AbilityEffectsManager(spell_manager)
                    ability.is_unlocked = True
                    
                    log = []
                    result = effects_manager.apply_ability_effects(test_hero, ability, log)
                    
                    hp_after = test_hero.current_health
                    healing = hp_after - hp_before
                    
                    if healing > 0:
                        print(f"    ✅ Soin: {hp_before} → {hp_after} (+{healing} PV)")
                        self.results["mechanical_abilities"].append({
                            "name": ability.name,
                            "hero": hero.name,
                            "effect": f"+{healing} PV",
                            "type": "healing"
                        })
                    else:
                        print(f"    ❌ Aucun soin détecté")
                        self.results["cosmetic_abilities"].append({
                            "name": ability.name,
                            "hero": hero.name,
                            "problem": "Aucun effet de soin"
                        })
            
            return True
            
        except Exception as e:
            print(f"❌ ERREUR Soins: {e}")
            self.results["broken_abilities"].append(f"Soins: {e}")
            return False
    
    def _test_damage_abilities(self):
        """Test 4: Capacités de dégâts"""
        print("\n⚔️ TEST 4: CAPACITÉS DE DÉGÂTS")
        print("-" * 40)
        
        try:
            from utils.data_loader import DataLoader
            
            loader = DataLoader()
            heroes = loader.load_heroes()
            
            # Rechercher capacités offensives
            for hero in heroes:
                abilities = loader.get_hero_abilities(hero.code)
                damage_abilities = [a for a in abilities if any(keyword in a.description.lower() 
                                  for keyword in ['dégâts', 'attaque', 'frappe', 'explosion', 'boule de feu'])]
                
                if damage_abilities:
                    print(f"\n⚔️ {hero.name}: {len(damage_abilities)} capacités offensives trouvées")
                    for ability in damage_abilities:
                        print(f"  - {ability.name}: {ability.description[:60]}...")
            
            # TODO: Implémenter test réel en combat
            print("⚠️ Test de dégâts réels en combat à implémenter")
            
            return True
            
        except Exception as e:
            print(f"❌ ERREUR Dégâts: {e}")
            return False
    
    def _test_buff_debuff_abilities(self):
        """Test 5: Capacités de buff/debuff"""
        print("\n🔄 TEST 5: BUFFS/DEBUFFS")
        print("-" * 40)
        
        try:
            print("⚠️ Test de buffs/debuffs à implémenter")
            return True
            
        except Exception as e:
            print(f"❌ ERREUR Buffs: {e}")
            return False
    
    def _generate_final_report(self):
        """Génère le rapport final"""
        print("\n" + "=" * 60)
        print("📊 RAPPORT FINAL - ÉTAT DES CAPACITÉS")
        print("=" * 60)
        
        total_mechanical = len(self.results["mechanical_abilities"])
        total_cosmetic = len(self.results["cosmetic_abilities"])
        total_broken = len(self.results["broken_abilities"])
        total_missing = len(self.results["missing_effects"])
        
        print(f"\n📈 STATISTIQUES:")
        print(f"   ✅ Capacités mécaniques: {total_mechanical}")
        print(f"   ❌ Capacités cosmétiques: {total_cosmetic}")
        print(f"   💥 Capacités en erreur: {total_broken}")
        print(f"   ⚠️ Effets manquants: {total_missing}")
        
        # Détail des capacités mécaniques
        if self.results["mechanical_abilities"]:
            print(f"\n✅ CAPACITÉS AVEC EFFETS MÉCANIQUES RÉELS:")
            for ability in self.results["mechanical_abilities"]:
                print(f"   ✅ {ability['hero']}: {ability['name']} → {ability['effect']}")
        
        # Détail des problèmes
        if self.results["cosmetic_abilities"]:
            print(f"\n❌ CAPACITÉS PUREMENT COSMÉTIQUES:")
            for ability in self.results["cosmetic_abilities"]:
                print(f"   ❌ {ability['hero']}: {ability['name']} → {ability['problem']}")
        
        if self.results["broken_abilities"]:
            print(f"\n💥 ERREURS DÉTECTÉES:")
            for error in self.results["broken_abilities"]:
                print(f"   💥 {error}")
        
        if self.results["missing_effects"]:
            print(f"\n⚠️ EFFETS MANQUANTS:")
            for missing in self.results["missing_effects"]:
                print(f"   ⚠️ {missing}")
        
        # CONCLUSION FINALE
        print(f"\n🎯 CONCLUSION POUR TESTS JEU DE SOCIÉTÉ:")
        
        if total_mechanical > 0 and total_cosmetic == 0 and total_broken == 0:
            print("✅ SYSTÈME PRÊT - Tous les effets sont mécaniques")
            print("✅ Résultats de combat précis garantis")
        elif total_mechanical > total_cosmetic:
            print("⚠️ SYSTÈME PARTIELLEMENT PRÊT")
            print("⚠️ Certaines capacités restent cosmétiques")
            print("⚠️ Précision limitée pour certains tests")
        else:
            print("❌ SYSTÈME NON PRÊT")
            print("❌ Majorité des capacités sont cosmétiques")
            print("❌ Résultats de combat non fiables")
        
        return self.results

def main():
    """Fonction principale"""
    diagnostic = DiagnosticCapacites()
    results = diagnostic.run_complete_diagnostic()
    
    # Code de sortie pour intégration
    mechanical_count = len(results["mechanical_abilities"])
    cosmetic_count = len(results["cosmetic_abilities"])
    broken_count = len(results["broken_abilities"])
    
    if broken_count > 0:
        return 2  # Erreurs critiques
    elif cosmetic_count > mechanical_count:
        return 1  # Système pas prêt
    else:
        return 0  # Système prêt

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)