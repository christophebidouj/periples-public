#!/usr/bin/env python3
"""
🚨 CORRECTION URGENTE - PHASE 2 FONDATIONS PYDANTIC
==================================================

Ajoute les attributs current_attack, current_defense, current_precision manquants
dans models/character.py pour supporter les effets mécaniques des capacités.

Ce script applique automatiquement les modifications nécessaires.

Usage: python fix_character_foundation.py
"""

import sys
import os
import re
from pathlib import Path

def backup_file(file_path):
    """Crée une sauvegarde du fichier"""
    backup_path = f"{file_path}.backup"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
        return True
    return False

def find_character_file():
    """Localise le fichier character.py"""
    possible_paths = [
        "models/character.py",
        "models/characters.py", 
        "./character.py",
        "../models/character.py"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Fichier Character trouvé: {path}")
            return path
    
    print("❌ Fichier character.py non trouvé")
    return None

def analyze_character_structure(file_path):
    """Analyse la structure du fichier Character"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analysis = {
        "has_pydantic": "BaseModel" in content or "from pydantic" in content,
        "has_current_health": "current_health" in content,
        "has_current_attack": "current_attack" in content,
        "has_current_defense": "current_defense" in content,
        "has_current_precision": "current_precision" in content,
        "has_optional_import": "Optional" in content,
        "line_count": len(content.split('\n'))
    }
    
    print(f"\n📊 ANALYSE DU FICHIER CHARACTER:")
    print(f"   📄 Lignes: {analysis['line_count']}")
    print(f"   🏗️ Pydantic: {analysis['has_pydantic']}")
    print(f"   ❤️ current_health: {analysis['has_current_health']}")
    print(f"   ⚔️ current_attack: {analysis['has_current_attack']}")
    print(f"   🛡️ current_defense: {analysis['has_current_defense']}")
    print(f"   🎯 current_precision: {analysis['has_current_precision']}")
    
    return analysis, content

def find_insertion_point(content):
    """Trouve où insérer les nouveaux attributs"""
    lines = content.split('\n')
    
    # Chercher après current_health
    for i, line in enumerate(lines):
        if 'current_health' in line and ':' in line:
            print(f"✅ Point d'insertion trouvé après current_health (ligne {i+1})")
            return i + 1
    
    # Alternative: chercher après health
    for i, line in enumerate(lines):
        if re.match(r'\s*health\s*:', line):
            print(f"✅ Point d'insertion trouvé après health (ligne {i+1})")
            return i + 1
    
    # Alternative: chercher dans la classe Character
    in_character_class = False
    for i, line in enumerate(lines):
        if 'class Character' in line:
            in_character_class = True
            continue
        
        if in_character_class and line.strip() == "":
            continue
            
        if in_character_class and ':' in line and not line.strip().startswith('#'):
            # Premier attribut trouvé
            print(f"✅ Point d'insertion trouvé dans classe Character (ligne {i+1})")
            return i + 1
    
    print("❌ Point d'insertion non trouvé")
    return None

def add_current_stats_attributes(content, insertion_point):
    """Ajoute les attributs current_* manquants"""
    lines = content.split('\n')
    
    # Les attributs à ajouter
    new_attributes = [
        "",  # Ligne vide pour la lisibilité
        "    # === STATS MODIFIABLES PAR CAPACITÉS ===",
        "    # Ajouté pour supporter les effets mécaniques des capacités",
        "    current_attack: Optional[int] = None",
        "    current_defense: Optional[int] = None", 
        "    current_precision: Optional[int] = None",
        "    current_magical_damage: Optional[int] = None"
    ]
    
    # Insérer les nouveaux attributs
    for i, attr in enumerate(new_attributes):
        lines.insert(insertion_point + i, attr)
    
    return '\n'.join(lines)

def fix_character_imports(content):
    """Vérifie et corrige les imports nécessaires"""
    if "from typing import" in content and "Optional" not in content:
        # Ajouter Optional aux imports existants
        content = content.replace(
            "from typing import",
            "from typing import Optional,"
        )
    elif "Optional" not in content:
        # Ajouter l'import complet
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from pydantic'):
                lines.insert(i, "from typing import Optional, List, Dict, Any")
                break
        content = '\n'.join(lines)
    
    return content

def apply_character_fix():
    """Applique la correction complète au fichier Character"""
    print("🔧 === CORRECTION PHASE 2 - FONDATIONS PYDANTIC ===")
    print("=" * 55)
    
    # 1. Localiser le fichier
    character_file = find_character_file()
    if not character_file:
        print("❌ Impossible de procéder sans le fichier character.py")
        return False
    
    # 2. Backup
    if not backup_file(character_file):
        print("❌ Impossible de créer une sauvegarde")
        return False
    
    # 3. Analyser le fichier
    analysis, content = analyze_character_structure(character_file)
    
    # 4. Vérifier si déjà corrigé
    if analysis["has_current_attack"] and analysis["has_current_defense"] and analysis["has_current_precision"]:
        print("✅ Les attributs current_* existent déjà !")
        print("✅ Pas besoin de modification")
        return True
    
    # 5. Trouver le point d'insertion
    insertion_point = find_insertion_point(content)
    if insertion_point is None:
        print("❌ Impossible de trouver où insérer les attributs")
        return False
    
    # 6. Corriger les imports
    content = fix_character_imports(content)
    
    # 7. Ajouter les attributs
    new_content = add_current_stats_attributes(content, insertion_point)
    
    # 8. Écrire le fichier modifié
    try:
        with open(character_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Fichier modifié avec succès: {character_file}")
        
        # 9. Vérifier la correction
        print("\n📊 VÉRIFICATION POST-MODIFICATION:")
        analysis_after, _ = analyze_character_structure(character_file)
        
        if analysis_after["has_current_attack"] and analysis_after["has_current_defense"]:
            print("✅ Correction réussie - Attributs ajoutés")
            print("\n🧪 TEST RECOMMANDÉ:")
            print("python -c \"from models.character import Character; print('✅ Import OK')\"")
            return True
        else:
            print("❌ Correction échouée - Restaurer le backup")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'écriture: {e}")
        return False

def main():
    """Point d'entrée principal"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        # Mode diagnostic seulement
        character_file = find_character_file()
        if character_file:
            analysis, _ = analyze_character_structure(character_file)
            
            missing = []
            if not analysis["has_current_attack"]:
                missing.append("current_attack")
            if not analysis["has_current_defense"]:
                missing.append("current_defense") 
            if not analysis["has_current_precision"]:
                missing.append("current_precision")
                
            if missing:
                print(f"\n❌ ATTRIBUTS MANQUANTS: {', '.join(missing)}")
                print("🔧 Pour corriger: python fix_character_foundation.py")
                return False
            else:
                print("\n✅ TOUS LES ATTRIBUTS SONT PRÉSENTS")
                return True
        return False
    
    else:
        # Mode correction
        success = apply_character_fix()
        return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)