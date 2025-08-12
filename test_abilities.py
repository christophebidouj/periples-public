#!/usr/bin/env python3
"""
Tests mécaniques des capacités - Périples Balance Workshop
Vérifie que chaque capacité produit des effets réels, pas juste des logs
"""

import sys
import os
import random
from typing import Dict, List, Any, Optional
import pandas as pd

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_loader import DataLoader
from models.character import Character, Enemy
from models.combat.combat_engine import CombatEngine
from models.rules_engine import GameRules
from models.abilities import Ability

class AbilityMechanicsTest:
    """Testeur des mécaniques réelles des capacités"""
    
    def __init__(self):
        self.loader = DataLoader()
        self.heroes = []
        self.enemies = []
        self.equipment = []
        self.abilities_by_hero = {}
        self.test_results = []
        
        print("🔬 === TESTEUR MÉCANIQUES CAPACITÉS ===")
        self._load_data()
    
    def _load_data(self):
        """Charge données complètes"""
        try:
            self.heroes = self.loader.load_heroes()
            self.enemies = self.loader.load_enemies()
            self.equipment = self.loader.load_equipment()
            self.abilities_by_hero = self._load_abilities_from_csv()
            
            print(f"✅ Données chargées: {len(self.heroes)} héros, {len(self.abilities_by_hero)} héros avec capacités")
        except Exception as e:
            print(f"❌ Erreur: {e}")
            sys.exit(1)
    
    def _load_abilities_from_csv(self) -> Dict[str, List]:
        """Charge capacités depuis CSV"""
        abilities_by_hero = {}
        
        try:
            df = pd.read_csv("data/ability_names.csv")
            
            for _, row in df.iterrows():
                hero_code = row['hero_code']
                ability_number = int(row['ability_number'])
                name = row['generated_name']
                description = row['clean_description']
                
                # Filtrer héros P-1 à P-8, capacités 1-6
                if hero_code not in ['P-1', 'P-2', 'P-3', 'P-4', 'P-5', 'P-6', 'P-7', 'P-8']:
                    continue
                if not (1 <= ability_number <= 6):
                    continue
                
                # Coût en sorts
                spell_cost = 1 if any(word in description.lower() for word in ['magique', 'sort', 'magie']) else 0
                
                ability = Ability(
                    hero_code=hero_code,
                    ability_number=ability_number,
                    name=name,
                    spell_cost=spell_cost,
                    description=description,
                    effects=[],
                    is_unlocked=False
                )
                
                if hero_code not in abilities_by_hero:
                    abilities_by_hero[hero_code] = []
                abilities_by_hero[hero_code].append(ability)
            
            return abilities_by_hero
        except Exception as e:
            print(f"❌ Erreur CSV: {e}")
            return {}
    
    def test_ability_mechanics(self, hero_code: str, ability_number: int) -> Dict[str, Any]:
        """
        Test complet des mécaniques d'une capacité
        Vérifie les effets RÉELS, pas juste les logs
        """
        # Créer héros de test
        test_hero = self._create_test_hero(hero_code, ability_number)
        if not test_hero:
            return {'error': f'Héros {hero_code} non trouvé'}
        
        # Trouver la capacité
        ability = next((a for a in test_hero.abilities 
                       if a.ability_number == ability_number and a.is_unlocked), None)
        if not ability:
            return {'error': f'Capacité {ability_number} non trouvée'}
        
        # États initiaux
        initial_state = self._capture_hero_state(test_hero)
        
        # Créer environnement de test
        test_enemies = [self._create_test_enemy() for _ in range(2)]
        test_allies = [self._create_allied_hero() for _ in range(2)]
        
        initial_enemies_state = [self._capture_enemy_state(e) for e in test_enemies]
        initial_allies_state = [self._capture_hero_state(a) for a in test_allies]
        
        # Appliquer la capacité avec système complet
        mechanics_detected = self._apply_ability_with_full_system(
            test_hero, ability, test_enemies, test_allies
        )
        
        # États finaux
        final_state = self._capture_hero_state(test_hero)
        final_enemies_state = [self._capture_enemy_state(e) for e in test_enemies]
        final_allies_state = [self._capture_hero_state(a) for a in test_allies]
        
        # Analyser changements mécaniques
        real_mechanics = self._analyze_mechanical_changes(
            initial_state, final_state,
            initial_enemies_state, final_enemies_state,
            initial_allies_state, final_allies_state,
            ability
        )
        
        return {
            'hero_code': hero_code,
            'hero_name': test_hero.name,
            'ability_number': ability_number,
            'ability_name': ability.name,
            'description': ability.description,
            'spell_cost': ability.spell_cost,
            'detected_mechanics': mechanics_detected,
            'real_mechanics': real_mechanics,
            'has_real_effects': len(real_mechanics) > 0,
            'mechanics_score': self._calculate_mechanics_score(real_mechanics, ability)
        }
    
    def _create_test_hero(self, hero_code: str, ability_number: int) -> Optional[Character]:
        """Crée héros de test configuré"""
        base_hero = next((h for h in self.heroes if h.code == hero_code), None)
        if not base_hero:
            return None
        
        test_hero = base_hero.model_copy()
        
        # Ajouter capacités
        if hero_code in self.abilities_by_hero:
            test_hero.add_abilities(self.abilities_by_hero[hero_code])
        
        # Déverrouiller capacités 1 → ability_number
        for i in range(1, ability_number + 1):
            test_hero.unlock_ability(i)
        
        # Préparer pour combat
        test_hero.start_new_combat()
        
        # Blesser légèrement pour tester soins
        test_hero.current_health = max(1, test_hero.current_health - 5)
        
        return test_hero
    
    def _create_test_enemy(self) -> Enemy:
        """Crée ennemi de test"""
        enemy = self.enemies[0].model_copy()
        enemy.initialize_for_combat(2)
        # Blesser légèrement
        enemy.current_health = max(1, enemy.current_health - 3)
        return enemy
    
    def _create_allied_hero(self) -> Character:
        """Crée héros allié pour tests de soin de groupe"""
        ally = self.heroes[1].model_copy()
        ally.start_new_combat()
        # Blesser pour tester soins
        ally.current_health = max(1, ally.current_health - 4)
        return ally
    
    def _capture_hero_state(self, hero: Character) -> Dict:
        """Capture état complet d'un héros"""
        return {
            'health': hero.current_health,
            'max_health': hero.get_total_health(),
            'spells': getattr(hero, 'current_spells', hero.get_total_spells()),
            'parade_tokens': getattr(hero, 'current_parade_tokens', 0),
            'max_parade_tokens': getattr(hero, 'max_parade_tokens', 0),
            'form': getattr(hero, 'current_form', None),
            'temporary_buffs': getattr(hero, 'temporary_buffs', {}),
            'permanent_buffs': getattr(hero, 'permanent_buffs', {}),
            'persistent_effects': getattr(hero, 'active_persistent_effects', []),
            'potions': self._count_potions(hero),
            'total_damage': hero.get_total_damage(),
            'total_precision': hero.get_total_precision()
        }
    
    def _capture_enemy_state(self, enemy: Enemy) -> Dict:
        """Capture état ennemi"""
        return {
            'health': enemy.current_health,
            'max_health': enemy.max_health,
            'parade_tokens': getattr(enemy, 'current_parade_tokens', 0),
            'debuffs': getattr(enemy, 'debuffs', {}),
            'status_effects': getattr(enemy, 'status_effects', {}),
            'marks': getattr(enemy, 'marks', {})
        }
    
    def _count_potions(self, hero: Character) -> int:
        """Compte potions totales"""
        if not hasattr(hero, 'health_potions'):
            return 0
        return sum(potion.quantity for potion in hero.health_potions)
    
    def _apply_ability_with_full_system(self, hero: Character, ability: Ability, 
                                      enemies: List[Enemy], allies: List[Character]) -> List[str]:
        """
        Applique capacité avec système complet (moteur de combat)
        Retourne mécaniques détectées pendant l'application
        """
        mechanics_log = []
        
        try:
            # Simuler contexte combat complet
            rules = GameRules(criticals=False, initiative=False)
            engine = CombatEngine(rules)
            
            # Mettre ennemis/alliés dans session pour ciblage
            import streamlit as st
            if 'current_enemies' not in st.session_state:
                st.session_state.current_enemies = []
            if 'current_heroes' not in st.session_state:
                st.session_state.current_heroes = []
            
            st.session_state.current_enemies = enemies
            st.session_state.current_heroes = allies + [hero]
            
            # Initialiser sorts dans moteur
            engine.spell_manager.initialize_spells(hero)
            
            # Utiliser capacité via moteur combat
            success = engine.combat_actions.use_ability(hero, ability, mechanics_log)
            
            if success:
                mechanics_log.append("Capacité utilisée avec succès")
            else:
                mechanics_log.append("Échec utilisation capacité")
                
        except Exception as e:
            mechanics_log.append(f"Erreur système: {e}")
        
        return mechanics_log
    
    def _analyze_mechanical_changes(self, initial_hero: Dict, final_hero: Dict,
                                  initial_enemies: List[Dict], final_enemies: List[Dict],
                                  initial_allies: List[Dict], final_allies: List[Dict],
                                  ability: Ability) -> List[str]:
        """
        Analyse COMPLÈTE des changements mécaniques
        Retourne liste des effets mécaniques réels détectés
        """
        mechanics = []
        
        # === EFFETS SUR LE HÉROS ===
        
        # Soins
        if final_hero['health'] > initial_hero['health']:
            heal_amount = final_hero['health'] - initial_hero['health']
            mechanics.append(f"SOIN: +{heal_amount} PV")
        
        # Transformations (Elneha)
        if initial_hero['form'] != final_hero['form']:
            mechanics.append(f"TRANSFORMATION: {initial_hero['form']} → {final_hero['form']}")
        
        # Consommation sorts
        if final_hero['spells'] < initial_hero['spells']:
            used = initial_hero['spells'] - final_hero['spells']
            mechanics.append(f"SORTS: -{used} consommés")
        
        # Parade modifiée
        if final_hero['parade_tokens'] != initial_hero['parade_tokens']:
            diff = final_hero['parade_tokens'] - initial_hero['parade_tokens']
            mechanics.append(f"PARADE: {'+' if diff > 0 else ''}{diff} jetons")
        
        # Buffs temporaires
        new_buffs = set(final_hero['temporary_buffs'].keys()) - set(initial_hero['temporary_buffs'].keys())
        for buff in new_buffs:
            mechanics.append(f"BUFF_TEMP: {buff}")
        
        # Buffs permanents
        new_permanent = set(final_hero['permanent_buffs'].keys()) - set(initial_hero['permanent_buffs'].keys())
        for buff in new_permanent:
            mechanics.append(f"BUFF_PERM: {buff}")
        
        # Effets persistants
        new_effects = len(final_hero['persistent_effects']) - len(initial_hero['persistent_effects'])
        if new_effects > 0:
            mechanics.append(f"EFFET_PERSISTANT: +{new_effects}")
        
        # Potions gagnées
        if final_hero['potions'] > initial_hero['potions']:
            gained = final_hero['potions'] - initial_hero['potions']
            mechanics.append(f"POTIONS: +{gained}")
        
        # Changements stats
        if final_hero['total_damage'] != initial_hero['total_damage']:
            diff = final_hero['total_damage'] - initial_hero['total_damage']
            mechanics.append(f"DÉGÂTS: {'+' if diff > 0 else ''}{diff}")
        
        # === EFFETS SUR LES ENNEMIS ===
        
        for i, (init_enemy, final_enemy) in enumerate(zip(initial_enemies, final_enemies)):
            enemy_name = f"Ennemi{i+1}"
            
            # Dégâts infligés
            if final_enemy['health'] < init_enemy['health']:
                damage = init_enemy['health'] - final_enemy['health']
                mechanics.append(f"DÉGÂTS_ENNEMI: {damage} à {enemy_name}")
            
            # Debuffs appliqués
            new_debuffs = set(final_enemy['debuffs'].keys()) - set(init_enemy['debuffs'].keys())
            for debuff in new_debuffs:
                value = final_enemy['debuffs'][debuff]
                mechanics.append(f"DEBUFF: {debuff} -{value} sur {enemy_name}")
            
            # Effets de statut
            new_status = set(final_enemy['status_effects'].keys()) - set(init_enemy['status_effects'].keys())
            for status in new_status:
                duration = final_enemy['status_effects'][status]
                mechanics.append(f"STATUS: {status} ({duration} tours) sur {enemy_name}")
            
            # Marques
            new_marks = set(final_enemy['marks'].keys()) - set(init_enemy['marks'].keys())
            for mark in new_marks:
                mechanics.append(f"MARQUE: {mark} sur {enemy_name}")
            
            # Parade réduite
            if final_enemy['parade_tokens'] < init_enemy['parade_tokens']:
                reduced = init_enemy['parade_tokens'] - final_enemy['parade_tokens']
                mechanics.append(f"PARADE_RÉDUITE: -{reduced} sur {enemy_name}")
        
        # === EFFETS SUR LES ALLIÉS ===
        
        for i, (init_ally, final_ally) in enumerate(zip(initial_allies, final_allies)):
            ally_name = f"Allié{i+1}"
            
            # Soins sur alliés
            if final_ally['health'] > init_ally['health']:
                heal = final_ally['health'] - init_ally['health']
                mechanics.append(f"SOIN_ALLIÉ: +{heal} PV à {ally_name}")
            
            # Buffs partagés
            new_buffs = set(final_ally['temporary_buffs'].keys()) - set(init_ally['temporary_buffs'].keys())
            for buff in new_buffs:
                mechanics.append(f"BUFF_ALLIÉ: {buff} sur {ally_name}")
        
        return mechanics
    
    def _calculate_mechanics_score(self, mechanics: List[str], ability: Ability) -> int:
        """
        Calcule score de mécaniques (0-100)
        100 = Capacité avec effets mécaniques complets
        0 = Capacité sans effets mécaniques
        """
        if not mechanics:
            return 0
        
        score = 0
        
        # Points par type d'effet mécanique
        effect_points = {
            'SOIN': 15,
            'DÉGÂTS_ENNEMI': 20,
            'TRANSFORMATION': 10,
            'BUFF_TEMP': 10,
            'BUFF_PERM': 15,
            'DEBUFF': 15,
            'STATUS': 10,
            'MARQUE': 10,
            'EFFET_PERSISTANT': 20,
            'PARADE': 5,
            'SORTS': 5,  # Consommation normale
            'POTIONS': 5
        }
        
        for mechanic in mechanics:
            for effect_type, points in effect_points.items():
                if effect_type in mechanic:
                    score += points
                    break
        
        # Bonus pour capacités complexes (multiples effets)
        if len(mechanics) >= 3:
            score += 10
        if len(mechanics) >= 5:
            score += 10
        
        # Malus si que consommation sorts (effet minimal)
        if len(mechanics) == 1 and 'SORTS:' in mechanics[0]:
            score = max(5, score)
        
        return min(100, score)
    
    def test_all_abilities(self) -> List[Dict]:
        """Test toutes les capacités"""
        results = []
        
        print("\n🔬 === DÉBUT TESTS MÉCANIQUES ===")
        
        for hero_code, abilities_list in self.abilities_by_hero.items():
            hero_name = next((h.name for h in self.heroes if h.code == hero_code), hero_code)
            print(f"\n👤 Test {hero_name} ({hero_code})...")
            
            for ability in abilities_list:
                print(f"  🔮 Capacité {ability.ability_number}: {ability.name}")
                
                try:
                    result = self.test_ability_mechanics(hero_code, ability.ability_number)
                    results.append(result)
                    
                    if 'error' in result:
                        print(f"    ❌ {result['error']}")
                    else:
                        score = result['mechanics_score']
                        mechanics_count = len(result['real_mechanics'])
                        
                        if score >= 80:
                            print(f"    ✅ Score: {score}/100 ({mechanics_count} mécaniques)")
                        elif score >= 50:
                            print(f"    🟡 Score: {score}/100 ({mechanics_count} mécaniques)")
                        else:
                            print(f"    🔴 Score: {score}/100 ({mechanics_count} mécaniques)")
                
                except Exception as e:
                    error_result = {
                        'hero_code': hero_code,
                        'ability_number': ability.ability_number,
                        'error': f'Exception: {e}',
                        'mechanics_score': 0
                    }
                    results.append(error_result)
                    print(f"    💥 Exception: {e}")
        
        print(f"\n📊 Tests terminés: {len(results)} capacités")
        return results
    
    def generate_mechanics_report(self, results: List[Dict]) -> str:
        """Génère rapport détaillé des mécaniques"""
        import time
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"test_mechanics_report_{timestamp}.txt"
        
        if not results:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== RAPPORT MÉCANIQUES CAPACITÉS ===\n")
                f.write("AUCUN TEST EFFECTUÉ\n")
            return filename
        
        # Analyse des résultats
        successful_tests = [r for r in results if 'error' not in r]
        failed_tests = [r for r in results if 'error' in r]
        
        # Calculs statistiques
        scores = [r['mechanics_score'] for r in successful_tests]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        high_quality = [r for r in successful_tests if r['mechanics_score'] >= 80]
        medium_quality = [r for r in successful_tests if 50 <= r['mechanics_score'] < 80]
        low_quality = [r for r in successful_tests if r['mechanics_score'] < 50]
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=== RAPPORT MÉCANIQUES CAPACITÉS PÉRIPLES ===\n")
            f.write(f"Généré le: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total capacités testées: {len(results)}\n\n")
            
            # Statistiques globales
            f.write("📊 STATISTIQUES GLOBALES:\n")
            f.write(f"  • Tests réussis: {len(successful_tests)}\n")
            f.write(f"  • Tests échoués: {len(failed_tests)}\n")
            f.write(f"  • Score moyen: {avg_score:.1f}/100\n")
            f.write(f"  • Qualité élevée (≥80): {len(high_quality)}\n")
            f.write(f"  • Qualité moyenne (50-79): {len(medium_quality)}\n")
            f.write(f"  • Qualité faible (<50): {len(low_quality)}\n\n")
            
            # Analyse par héros
            f.write("📋 ANALYSE PAR HÉROS:\n")
            heroes_stats = {}
            for result in successful_tests:
                hero_name = result.get('hero_name', 'Inconnu')
                if hero_name not in heroes_stats:
                    heroes_stats[hero_name] = {'count': 0, 'total_score': 0, 'capacities': []}
                
                heroes_stats[hero_name]['count'] += 1
                heroes_stats[hero_name]['total_score'] += result['mechanics_score']
                heroes_stats[hero_name]['capacities'].append(result)
            
            for hero_name, stats in heroes_stats.items():
                avg_score = stats['total_score'] / stats['count']
                f.write(f"  • {hero_name}: {stats['count']} capacités, score moyen {avg_score:.1f}\n")
            f.write("\n")
            
            # Détail par qualité
            f.write("🏆 CAPACITÉS HAUTE QUALITÉ (≥80):\n")
            for result in sorted(high_quality, key=lambda x: x['mechanics_score'], reverse=True):
                f.write(f"  • {result['hero_name']} - {result['ability_name']} (Score: {result['mechanics_score']})\n")
                for mechanic in result['real_mechanics']:
                    f.write(f"    → {mechanic}\n")
                f.write("\n")
            
            f.write("🟡 CAPACITÉS QUALITÉ MOYENNE (50-79):\n")
            for result in sorted(medium_quality, key=lambda x: x['mechanics_score'], reverse=True):
                f.write(f"  • {result['hero_name']} - {result['ability_name']} (Score: {result['mechanics_score']})\n")
                if result['real_mechanics']:
                    f.write(f"    → {', '.join(result['real_mechanics'][:3])}\n")
                f.write("\n")
            
            f.write("🔴 CAPACITÉS QUALITÉ FAIBLE (<50):\n")
            for result in sorted(low_quality, key=lambda x: x['mechanics_score']):
                f.write(f"  • {result['hero_name']} - {result['ability_name']} (Score: {result['mechanics_score']})\n")
                f.write(f"    Description: {result.get('description', 'N/A')}\n")
                if result['real_mechanics']:
                    f.write(f"    Mécaniques: {', '.join(result['real_mechanics'])}\n")
                else:
                    f.write(f"    ❌ AUCUNE MÉCANIQUE DÉTECTÉE\n")
                f.write("\n")
            
            # Échecs
            if failed_tests:
                f.write("❌ TESTS ÉCHOUÉS:\n")
                for result in failed_tests:
                    f.write(f"  • {result.get('hero_code', 'N/A')} - Capacité {result.get('ability_number', 'N/A')}\n")
                    f.write(f"    Erreur: {result['error']}\n\n")
        
        return filename
    
    def run_full_mechanics_test(self):
        """Lance test complet des mécaniques"""
        print("🚀 === LANCEMENT TESTS MÉCANIQUES COMPLETS ===")
        
        # Tests
        results = self.test_all_abilities()
        
        # Rapport
        print(f"\n📝 Génération rapport...")
        report_file = self.generate_mechanics_report(results)
        
        # Résumé
        successful = [r for r in results if 'error' not in r]
        failed = [r for r in results if 'error' in r]
        
        if successful:
            scores = [r['mechanics_score'] for r in successful]
            avg_score = sum(scores) / len(scores)
            high_quality = len([r for r in successful if r['mechanics_score'] >= 80])
            
            print(f"✅ Rapport: {report_file}")
            print(f"📊 Résultats:")
            print(f"  • {len(successful)} capacités testées")
            print(f"  • Score moyen: {avg_score:.1f}/100")
            print(f"  • Haute qualité: {high_quality}/{len(successful)}")
            print(f"  • Échecs: {len(failed)}")
        else:
            print(f"❌ Aucun test réussi")

def main():
    """Fonction principale"""
    try:
        tester = AbilityMechanicsTest()
        tester.run_full_mechanics_test()
        print(f"\n🎉 Tests mécaniques terminés !")
    except Exception as e:
        print(f"💥 Erreur fatale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()