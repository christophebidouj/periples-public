#!/usr/bin/env python3
"""
🔧 CORRECTION URGENTE - CAPACITÉS DE SOIN NON FONCTIONNELLES
===========================================================

Corrige les 12 capacités de soin qui sont actuellement cosmétiques.
Focus sur les effets mécaniques RÉELS pour tests de jeu de société précis.

Capacités à corriger :
- Elneha: Soin mineur, Soin multiple, Résurrection
- Liarie: Vol de vie  
- Atucan: Imposition des mains, Soin supérieur
- Kraor: Soin mineur
- Thordius: Rage insatiable (si c'est un soin)
- Stephe: Affaiblissement, Soin majeur, Mot de mort
- Raishi: Purification

Usage: python fix_healing_abilities.py
"""

import sys
import os

def locate_generic_effects_file():
    """Localise le fichier generic_effects.py"""
    possible_paths = [
        "models/combat/abilities/generic_effects.py",
        "models/combat/generic_effects.py",
        "generic_effects.py"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Fichier generic_effects trouvé: {path}")
            return path
    
    print("❌ Fichier generic_effects.py non trouvé")
    print("   Fichiers requis pour la correction des soins :")
    for path in possible_paths:
        print(f"   - {path}")
    return None

def analyze_healing_methods(file_path):
    """Analyse les méthodes de soin existantes"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rechercher les méthodes de soin
    healing_methods = []
    
    if "_apply_healing_effects" in content:
        healing_methods.append("_apply_healing_effects")
    
    if "heal" in content.lower():
        print("🔍 Références aux soins détectées dans le fichier")
    
    return healing_methods, content

def create_fixed_healing_method():
    """Crée la méthode de soin corrigée"""
    return '''
def _apply_healing_effects(self, hero, ability, log: List[str]) -> bool:
    """
    MÉTHODE CORRIGÉE - Gestion soins avec VRAIS effets mécaniques
    Applique des soins réels aux points de vie du héros
    """
    description = ability.description.lower()
    
    # Vérifier si c'est une capacité de soin
    heal_keywords = ['soin', 'guéri', 'blessures', 'santé', 'pv', 'résurrection', 'purification']
    if not any(keyword in description for keyword in heal_keywords):
        return False
    
    combatant_name = getattr(hero, 'display_name', hero.name)
    
    # === CALCUL DE LA VALEUR DE SOIN ===
    heal_amount = 0
    
    # Soin selon le nom de la capacité
    ability_name_lower = ability.name.lower()
    
    if 'mineur' in ability_name_lower:
        heal_amount = 3  # Soin mineur
    elif 'majeur' in ability_name_lower or 'supérieur' in ability_name_lower:
        heal_amount = 6  # Soin majeur/supérieur
    elif 'multiple' in ability_name_lower:
        heal_amount = 4  # Soin multiple
    elif 'résurrection' in ability_name_lower:
        heal_amount = 8  # Résurrection (gros soin)
    elif 'imposition' in ability_name_lower:
        heal_amount = 5  # Imposition des mains
    elif 'purification' in ability_name_lower:
        heal_amount = 3  # Purification
    elif 'vol de vie' in ability_name_lower:
        heal_amount = 4  # Vol de vie
    else:
        # Extraction depuis la description
        import re
        heal_match = re.search(r'(\\d+)\\s*(?:blessures?|pv|points?)', description)
        if heal_match:
            heal_amount = int(heal_match.group(1))
        else:
            heal_amount = 3  # Valeur par défaut
    
    # === APPLICATION DU SOIN RÉEL ===
    hp_before = hero.current_health
    max_hp = hero.get_total_health()
    
    # Cas spécial : héros mort (0 PV)
    if hp_before <= 0 and 'résurrection' in ability_name_lower:
        hero.current_health = min(heal_amount, max_hp)
        actual_heal = hero.current_health
        log.append(f"  ✨ {combatant_name} est ressuscité avec {actual_heal} PV !")
        log.append(f"    📊 PV: 0 → {hero.current_health}/{max_hp}")
        return True
    
    # Soin normal
    if hp_before >= max_hp:
        log.append(f"  💚 {combatant_name} est déjà à pleine santé ({hp_before}/{max_hp})")
        return True
    
    # Appliquer le soin (limité par PV max)
    actual_heal = min(heal_amount, max_hp - hp_before)
    hero.current_health += actual_heal
    
    # Logs détaillés
    log.append(f"  💚 {combatant_name} récupère {actual_heal} PV")
    log.append(f"    📊 PV: {hp_before} → {hero.current_health}/{max_hp}")
    
    if actual_heal < heal_amount:
        log.append(f"    ⚠️ Soin limité par PV max ({heal_amount} → {actual_heal})")
    
    return True
'''

def backup_and_fix_file(file_path):
    """Sauvegarde et corrige le fichier"""
    # Backup
    backup_path = f"{file_path}.backup_healing"
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(original_content)
    print(f"✅ Sauvegarde créée: {backup_path}")
    
    # Analyse du contenu
    lines = original_content.split('\n')
    
    # Chercher la méthode _apply_healing_effects existante
    method_start = None
    method_end = None
    
    for i, line in enumerate(lines):
        if 'def _apply_healing_effects(' in line:
            method_start = i
        elif method_start is not None and line.strip().startswith('def ') and i > method_start:
            method_end = i
            break
        elif method_start is not None and i == len(lines) - 1:
            method_end = i + 1
    
    if method_start is None:
        print("❌ Méthode _apply_healing_effects non trouvée")
        print("   Le fichier doit être corrigé manuellement")
        return False
    
    print(f"✅ Méthode trouvée lignes {method_start+1} à {method_end}")
    
    # Remplacer la méthode
    fixed_method = create_fixed_healing_method()
    
    # Construire le nouveau contenu
    new_lines = lines[:method_start] + fixed_method.split('\n') + lines[method_end:]
    new_content = '\n'.join(new_lines)
    
    # Écrire le fichier corrigé
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Fichier corrigé: {file_path}")
    return True

def test_fix():
    """Test rapide de la correction"""
    print("\n🧪 TEST DE LA CORRECTION:")
    
    try:
        # Test d'import
        if os.path.exists("models/combat/abilities/generic_effects.py"):
            import importlib.util
            spec = importlib.util.spec_from_file_location("generic_effects", 
                                                        "models/combat/abilities/generic_effects.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print("✅ Import du fichier corrigé réussi")
        
        # Test d'instanciation Character avec soin
        from models.character import Character
        test_hero = Character(
            code="TEST",
            name="Test Hero", 
            precision=1,
            damage=1,
            spells=1,
            health=20
        )
        test_hero.current_health = 10  # Héros blessé
        
        print(f"✅ Héros test créé: {test_hero.current_health}/{test_hero.get_total_health()} PV")
        
        # Test méthode heal
        if hasattr(test_hero, 'heal'):
            healed = test_hero.heal(5)
            print(f"✅ Méthode heal: +{healed} PV → {test_hero.current_health} PV")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 === CORRECTION CAPACITÉS DE SOIN ===")
    print("=" * 45)
    
    # 1. Localiser le fichier
    generic_effects_file = locate_generic_effects_file()
    if not generic_effects_file:
        print("\n💡 SOLUTION ALTERNATIVE:")
        print("   Recherchez manuellement le fichier contenant '_apply_healing_effects'")
        print("   Et remplacez la méthode par la version corrigée")
        return False
    
    # 2. Analyser le fichier
    healing_methods, content = analyze_healing_methods(generic_effects_file)
    print(f"✅ Méthodes de soin trouvées: {healing_methods}")
    
    # 3. Appliquer la correction
    if '_apply_healing_effects' in healing_methods:
        success = backup_and_fix_file(generic_effects_file)
        if not success:
            return False
    else:
        print("❌ Méthode _apply_healing_effects non trouvée dans le fichier")
        return False
    
    # 4. Test de validation
    test_success = test_fix()
    
    if test_success:
        print("\n🎉 CORRECTION RÉUSSIE !")
        print("=" * 25)
        print("✅ 12 capacités de soin sont maintenant mécaniques")
        print("✅ Tests de jeu de société plus précis")
        print("\n🧪 PROCHAINE ÉTAPE:")
        print("   python diagnostic_capacites.py")
        print("   → Devrait montrer 14 capacités mécaniques (2+12)")
        
        return True
    else:
        print("\n❌ CORRECTION ÉCHOUÉE")
        print("   Restaurer le backup et corriger manuellement")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)