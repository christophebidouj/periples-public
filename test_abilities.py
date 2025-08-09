#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test des capacités - Périples Balance Workshop
Test automatisé de chaque capacité pour analyser ses effets réels en combat
"""

import sys
import os
import pandas as pd
from typing import Dict, List, Any
import time

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports du projet
from utils.abilities_loader import AbilitiesLoader, load_all_abilities
from utils.data_loader import DataLoader
from models.character import Character, Enemy
from models.combat_engine import CombatEngine
from models.rules_engine import GameRules

class AbilityTester:
    """Testeur automatisé des capacités"""
    
    def __init__(self):
        self.loader = DataLoader()
        self.abilities_loader = AbilitiesLoader()
        self.heroes = []
        self.enemies = []
        self.equipment = []
        self.abilities_by_hero = {}
        
        print("🧪 === TESTEUR DE CAPACITÉS PÉRIPLES ===")
        self._load_data()
    
    def _load_data(self):
        """Charge toutes les données nécessaires"""
        print("📊 Chargement des données...")
        
        try:
            # Charger héros, ennemis, équipements
            self.heroes = self.loader.load_heroes()
            self.enemies = self.loader.load_enemies()
            self.equipment = self.loader.load_equipment()
            
            # Charger capacités directement depuis CSV
            self.abilities_by_hero = self._load_abilities_from_csv()
            
            print(f"✅ Données chargées:")
            print(f"  • {len(self.heroes)} héros")
            print(f"  • {len(self.enemies)} ennemis")
            print(f"  • {len(self.equipment)} équipements")
            print(f"  • {len(self.abilities_by_hero)} héros avec capacités")
            
        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            sys.exit(1)
    
    def _load_abilities_from_csv(self) -> Dict[str, List]:
        """Charge les capacités directement depuis ability_names.csv"""
        from models.abilities import Ability, AbilityEffect, TargetType
        
        abilities_by_hero = {}
        
        try:
            # Lire le CSV
            df = pd.read_csv("data/ability_names.csv")
            
            for _, row in df.iterrows():
                hero_code = row['hero_code']
                ability_number = int(row['ability_number'])
                name = row['generated_name']
                description = row['clean_description']
                
                # Filtrer seulement les héros P-1 à P-8 ET capacités 1-6
                if hero_code not in ['P-1', 'P-2', 'P-3', 'P-4', 'P-5', 'P-6', 'P-7', 'P-8']:
                    continue
                
                if ability_number < 1 or ability_number > 7:
                    continue  # Skip capacités hors limites Pydantic (maintenant 1-7)
                
                # Déterminer coût en sorts (estimation basique)
                spell_cost = 1 if any(word in description.lower() for word in ['magique', 'sort', 'magie']) else 0
                
                # Déterminer limitations d'usage
                uses_per_combat = None
                if 'combat' in description.lower():
                    if '1' in description and 'fois' in description.lower():
                        uses_per_combat = 1
                    elif '2' in description and 'fois' in description.lower():
                        uses_per_combat = 2
                
                # Créer la capacité
                ability = Ability(
                    hero_code=hero_code,
                    ability_number=ability_number,
                    name=name,
                    spell_cost=spell_cost,
                    description=description,
                    uses_per_combat=uses_per_combat,
                    effects=self._create_effects_from_description(description),
                    target_type=self._guess_target_from_description(description),
                    is_unlocked=False
                )
                
                # Organiser par héros
                if hero_code not in abilities_by_hero:
                    abilities_by_hero[hero_code] = []
                
                abilities_by_hero[hero_code].append(ability)
            
            print(f"📋 Capacités CSV chargées:")
            for hero_code, abilities in abilities_by_hero.items():
                print(f"  • {hero_code}: {len(abilities)} capacités")
            
            return abilities_by_hero
            
        except Exception as e:
            print(f"❌ Erreur lecture CSV: {e}")
            return {}
    
    def _create_effects_from_description(self, description: str) -> List:
        """Crée des effets basés sur la description"""
        from models.abilities import AbilityEffect
        
        effects = []
        desc_lower = description.lower()
        
        # Détection soins
        if any(word in desc_lower for word in ['soin', 'soigne', 'guérit', 'récupère']):
            # Extraire valeur si possible
            import re
            numbers = re.findall(r'\d+', description)
            heal_value = int(numbers[0]) if numbers else 3
            
            effects.append(AbilityEffect(
                type="heal",
                value=heal_value,
                description=f"Soigne {heal_value} PV"
            ))
        
        # Détection dégâts
        elif any(word in desc_lower for word in ['dégât', 'attaque', 'inflige', 'frappe']):
            import re
            numbers = re.findall(r'\d+', description)
            damage_value = int(numbers[0]) if numbers else 3
            
            damage_type = "magical_damage" if "magique" in desc_lower else "damage"
            effects.append(AbilityEffect(
                type=damage_type,
                value=damage_value,
                description=f"Inflige {damage_value} dégâts"
            ))
        
        # Transformations
        elif any(word in desc_lower for word in ['forme', 'transformation', 'métamorphose']):
            effects.append(AbilityEffect(
                type="transformation",
                description="Transformation de forme"
            ))
        
        # Invocation
        elif any(word in desc_lower for word in ['invoque', 'appel', 'créature']):
            effects.append(AbilityEffect(
                type="summon",
                description="Invoque une créature"
            ))
        
        # Effet générique
        else:
            effects.append(AbilityEffect(
                type="special",
                description=description[:50] + "..." if len(description) > 50 else description
            ))
        
        return effects
    
    def _guess_target_from_description(self, description: str):
        """Devine le type de cible"""
        from models.abilities import TargetType
        
        desc_lower = description.lower()
        
        if any(phrase in desc_lower for phrase in ['tous les adversaires', 'tous les ennemis']):
            return TargetType.ALL_ENEMIES
        elif any(phrase in desc_lower for phrase in ['tous les personnages', 'toute l\'équipe']):
            return TargetType.ALL_ALLIES
        elif any(word in desc_lower for word in ['adversaire', 'ennemi', 'cible']):
            return TargetType.ENEMY
        elif any(word in desc_lower for word in ['allié', 'personnage', 'équipier']):
            return TargetType.ALLY
        else:
            return TargetType.SELF
    
    def create_test_hero(self, hero_code: str, ability_number: int) -> Character:
        """Crée un héros de test avec une capacité spécifique"""
        base_hero = next((h for h in self.heroes if h.code == hero_code), None)
        if not base_hero:
            return None
        
        # Copier le héros
        test_hero = base_hero.model_copy()
        
        # Ajouter les capacités du héros
        if hero_code in self.abilities_by_hero:
            test_hero.add_abilities(self.abilities_by_hero[hero_code])
        
        # Déverrouiller seulement la capacité testée + ses prérequis
        test_hero.unlocked_abilities = []
        
        # Déverrouiller toutes les capacités de 1 jusqu'à celle testée (prérequis séquentiels)
        for i in range(1, ability_number + 1):
            test_hero.unlock_ability(i)
        
        # Préparer pour combat
        test_hero.start_new_combat()
        
        return test_hero
    
    def create_test_enemy(self) -> Enemy:
        """Crée un ennemi de test standard"""
        # Utiliser le premier ennemi disponible
        base_enemy = self.enemies[0].model_copy()
        base_enemy.initialize_for_combat(2)  # Pour 2 joueurs
        return base_enemy
    
    def test_ability_effect(self, hero_code: str, ability_number: int) -> Dict[str, Any]:
        """Test une capacité spécifique et analyse ses effets"""
        
        # Créer héros de test
        test_hero = self.create_test_hero(hero_code, ability_number)
        if not test_hero:
            return {'error': f'Héros {hero_code} non trouvé'}
        
        # Trouver la capacité
        ability = next((a for a in test_hero.abilities if a.ability_number == ability_number and a.is_unlocked), None)
        if not ability:
            return {'error': f'Capacité {ability_number} non trouvée pour {hero_code}'}
        
        # État initial du héros
        initial_state = {
            'health': test_hero.current_health,
            'spells': test_hero.get_total_spells(),
            'form': getattr(test_hero, 'current_form', None)
        }
        
        # Créer ennemi de test
        test_enemy = self.create_test_enemy()
        initial_enemy_health = test_enemy.current_health
        
        # Test en combat réel
        rules = GameRules(criticals=False, initiative=False)
        engine = CombatEngine(rules)
        
        # Simuler utilisation capacité
        effects_detected = self._simulate_ability_usage(test_hero, ability, test_enemy, engine)
        
        # Analyser les changements
        final_state = {
            'health': test_hero.current_health,
            'spells': engine.spell_manager.get_current_spells(test_hero),
            'form': getattr(test_hero, 'current_form', None)
        }
        
        final_enemy_health = test_enemy.current_health
        
        # Déterminer les effets réels
        real_effects = []
        
        # Soins
        if final_state['health'] > initial_state['health']:
            heal_amount = final_state['health'] - initial_state['health']
            real_effects.append(f"Soigne {heal_amount} PV")
        
        # Dégâts à l'ennemi
        if final_enemy_health < initial_enemy_health:
            damage_dealt = initial_enemy_health - final_enemy_health
            real_effects.append(f"Inflige {damage_dealt} dégâts à l'ennemi")
        
        # Consommation de sorts
        if final_state['spells'] < initial_state['spells']:
            spells_used = initial_state['spells'] - final_state['spells']
            real_effects.append(f"Consomme {spells_used} sorts")
        
        # Transformation (Elneha)
        if initial_state['form'] != final_state['form']:
            real_effects.append(f"Transformation: {initial_state['form']} → {final_state['form']}")
        
        # Effets spéciaux détectés
        real_effects.extend(effects_detected)
        
        return {
            'hero_code': hero_code,
            'hero_name': test_hero.name,
            'ability_number': ability_number,
            'ability_name': ability.name,
            'spell_cost': ability.spell_cost,
            'description': ability.description,
            'uses_per_combat': ability.uses_per_combat,
            'real_effects': real_effects if real_effects else ['Aucun effet détectable'],
            'prevents_attack': ability.prevents_attack,
            'target_type': ability.target_type.value,
            'initial_state': initial_state,
            'final_state': final_state,
            'enemy_damage_dealt': initial_enemy_health - final_enemy_health
        }
    
    def _simulate_ability_usage(self, hero: Character, ability, enemy: Enemy, engine: CombatEngine) -> List[str]:
        """Simule l'utilisation d'une capacité et détecte les effets spéciaux"""
        special_effects = []
        
        # Vérifier si c'est une capacité d'invocation
        if hero.code == "P-4" and hasattr(hero, 'can_summon_pet') and hero.can_summon_pet():
            if getattr(ability, 'ability_number', 0) == 99:  # VirtualAbility pour invocation
                special_effects.append("Invoque un Pet (Précision 4, Dégâts magiques 4, Santé 15)")
        
        # Utiliser la capacité via le héros
        try:
            action = hero.use_ability(ability)
            if action.success:
                # Analyser les effets appliqués
                for effect in action.effects_applied:
                    special_effects.append(f"Effet: {effect}")
        except Exception as e:
            special_effects.append(f"Erreur lors de l'utilisation: {e}")
        
        # Vérifier les effets sur les statistiques d'attaque
        if hasattr(hero, 'get_attack_damage_info'):
            attack_info = hero.get_attack_damage_info()
            if attack_info.get('is_converted'):
                source = attack_info.get('conversion_source', 'inconnu')
                if source == 'lyre_phoenix':
                    special_effects.append("Conversion attaques → magiques (Lyre phoenix)")
                elif source == 'gemme_pouvoir':
                    form = attack_info.get('form_display', '')
                    special_effects.append(f"Attaques magiques en {form} (Gemme de pouvoir)")
        
        return special_effects
    
    def test_all_abilities(self) -> List[Dict[str, Any]]:
        """Test toutes les capacités de tous les héros"""
        results = []
        total_abilities = 0
        
        print("\n🔬 === DÉBUT DES TESTS ===")
        
        for hero_code, abilities_list in self.abilities_by_hero.items():
            hero_name = next((h.name for h in self.heroes if h.code == hero_code), hero_code)
            print(f"\n👤 Testeur {hero_name} ({hero_code})...")
            
            for ability in abilities_list:
                total_abilities += 1
                print(f"  🔮 Test capacité {ability.ability_number}: {ability.name}")
                
                try:
                    result = self.test_ability_effect(hero_code, ability.ability_number)
                    results.append(result)
                    
                    # Affichage rapide du résultat
                    if 'error' in result:
                        print(f"    ❌ {result['error']}")
                    else:
                        effects_summary = ", ".join(result['real_effects'][:2])  # 2 premiers effets
                        if len(result['real_effects']) > 2:
                            effects_summary += "..."
                        print(f"    ✅ Effets: {effects_summary}")
                
                except Exception as e:
                    error_result = {
                        'hero_code': hero_code,
                        'ability_number': ability.ability_number,
                        'error': f'Exception: {e}'
                    }
                    results.append(error_result)
                    print(f"    💥 Exception: {e}")
        
        print(f"\n📊 Tests terminés: {len(results)} capacités testées")
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """Génère un rapport détaillé des tests"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"test_abilities_report_{timestamp}.txt"
        
        # Protection division par zéro
        if not results:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== RAPPORT DE TEST DES CAPACITÉS PÉRIPLES ===\n")
                f.write(f"Généré le: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("AUCUNE CAPACITÉ TESTÉE - Problème de chargement des données\n")
            return filename
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=== RAPPORT DE TEST DES CAPACITÉS PÉRIPLES ===\n")
            f.write(f"Généré le: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total capacités testées: {len(results)}\n\n")
            
            # Statistiques
            successful_tests = [r for r in results if 'error' not in r]
            failed_tests = [r for r in results if 'error' in r]
            
            f.write(f"📊 STATISTIQUES:\n")
            f.write(f"  • Tests réussis: {len(successful_tests)}\n")
            f.write(f"  • Tests échoués: {len(failed_tests)}\n")
            f.write(f"  • Taux de réussite: {len(successful_tests)/len(results)*100:.1f}%\n\n")
            
            # Capacités par héros
            heroes_stats = {}
            for result in successful_tests:
                hero_name = result.get('hero_name', 'Inconnu')
                if hero_name not in heroes_stats:
                    heroes_stats[hero_name] = 0
                heroes_stats[hero_name] += 1
            
            f.write("📋 CAPACITÉS PAR HÉROS:\n")
            for hero_name, count in heroes_stats.items():
                f.write(f"  • {hero_name}: {count} capacités\n")
            f.write("\n")
            
            # Détail des capacités
            f.write("🔬 DÉTAIL DES TESTS:\n\n")
            
            current_hero = None
            for result in results:
                hero_name = result.get('hero_name', 'Inconnu')
                
                # Séparateur par héros
                if hero_name != current_hero:
                    f.write(f"{'='*60}\n")
                    f.write(f"👤 {hero_name} ({result.get('hero_code', 'N/A')})\n")
                    f.write(f"{'='*60}\n\n")
                    current_hero = hero_name
                
                if 'error' in result:
                    f.write(f"❌ Capacité {result.get('ability_number', 'N/A')}: ERREUR\n")
                    f.write(f"   Erreur: {result['error']}\n\n")
                    continue
                
                f.write(f"🔮 Capacité {result['ability_number']}: {result['ability_name']}\n")
                f.write(f"   Coût: {result['spell_cost']} sorts\n")
                f.write(f"   Type: {'Magique' if result['spell_cost'] > 0 else 'Physique'}\n")
                f.write(f"   Empêche attaque: {'Oui' if result['prevents_attack'] else 'Non'}\n")
                f.write(f"   Cible: {result['target_type']}\n")
                
                if result['uses_per_combat']:
                    f.write(f"   Utilisations/combat: {result['uses_per_combat']}\n")
                
                f.write(f"   Description: {result['description']}\n")
                f.write(f"   \n")
                f.write(f"   🎯 EFFETS RÉELS DÉTECTÉS:\n")
                for effect in result['real_effects']:
                    f.write(f"     • {effect}\n")
                
                if result['enemy_damage_dealt'] > 0:
                    f.write(f"   💥 Dégâts infligés à l'ennemi: {result['enemy_damage_dealt']}\n")
                
                f.write("\n")
            
            # Échecs
            if failed_tests:
                f.write(f"{'='*60}\n")
                f.write(f"❌ TESTS ÉCHOUÉS\n")
                f.write(f"{'='*60}\n\n")
                
                for result in failed_tests:
                    f.write(f"• {result.get('hero_code', 'N/A')} - Capacité {result.get('ability_number', 'N/A')}\n")
                    f.write(f"  Erreur: {result['error']}\n\n")
        
        return filename
    
    def run_full_test(self):
        """Lance le test complet et génère le rapport"""
        print("🚀 Lancement du test complet des capacités...")
        
        # Test toutes les capacités
        results = self.test_all_abilities()
        
        # Générer rapport
        print(f"\n📝 Génération du rapport...")
        report_file = self.generate_report(results)
        
        print(f"✅ Rapport généré: {report_file}")
        print(f"📊 Résumé:")
        
        successful = [r for r in results if 'error' not in r]
        failed = [r for r in results if 'error' in r]
        
        print(f"  • {len(successful)} capacités testées avec succès")
        print(f"  • {len(failed)} échecs")
        
        if results:  # Protection division par zéro
            print(f"  • Taux de réussite: {len(successful)/len(results)*100:.1f}%")
        else:
            print(f"  • Aucune capacité testée - Vérifier les données")
        
        # Aperçu des effets les plus courants
        all_effects = []
        for result in successful:
            all_effects.extend(result['real_effects'])
        
        if all_effects:
            print(f"\n🔍 Aperçu des effets détectés:")
            effects_count = {}
            for effect in all_effects:
                key = effect.split()[0] if effect.split() else effect
                effects_count[key] = effects_count.get(key, 0) + 1
            
            for effect, count in sorted(effects_count.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  • {effect}: {count} occurrences")
        else:
            print(f"\n⚠️ Aucun effet détecté - Problème de chargement des capacités")

def main():
    """Fonction principale"""
    try:
        tester = AbilityTester()
        tester.run_full_test()
        
        print(f"\n🎉 Test terminé avec succès !")
        
    except Exception as e:
        print(f"💥 Erreur fatale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()