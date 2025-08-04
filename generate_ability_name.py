"""
Générateur de noms élégants pour les capacités
CODE SIMPLE pour débutants Python - Lit Sorts.xlsx et génère des noms automatiquement
"""

import pandas as pd
import os
import re

def generate_ability_name(description):
    """
    Génère un nom élégant depuis une description
    CODE SIMPLE - Règles basiques de transformation
    
    Args:
        description: Description de la capacité
        
    Returns:
        str: Nom généré
    """
    if not description or pd.isna(description):
        return "Capacité Inconnue"
    
    desc = str(description).lower().strip()
    
    # === RÈGLES SIMPLES DE GÉNÉRATION ===
    
    # Soins
    if "soigne" in desc or "soin" in desc:
        if "4 blessures" in desc:
            return "Soin Mineur"
        elif "8 blessures" in desc:
            return "Soin Majeur"
        elif "totalité" in desc:
            return "Guérison Complète"
        elif "proportionnel" in desc or "moitié" in desc:
            return "Soin Proportionnel"
        elif "tous les personnages" in desc:
            return "Soin de Groupe"
        else:
            return "Soin Naturel"
    
    # Métamorphoses
    elif "métamorphose" in desc or "transforme" in desc:
        if "ours" in desc:
            if "supérieur" in desc:
                return "Forme d'Ours Supérieur"
            else:
                return "Forme d'Ours"
        elif "loup" in desc:
            if "supérieur" in desc:
                return "Forme de Loup Supérieur"
            else:
                return "Forme de Loup"
        else:
            return "Métamorphose"
    
    # Attaques magiques
    elif "dégâts magiques" in desc or "inflige" in desc:
        if "tous les adversaires" in desc:
            return "Explosion Magique"
        elif "répartis" in desc:
            return "Projectile Magique"
        else:
            return "Attaque Magique"
    
    # Boucliers/Protection
    elif "bouclier" in desc or "parade" in desc:
        return "Bouclier Magique"
    
    # Gel/Contrôle
    elif "gel" in desc or "gêle" in desc:
        return "Gel Ennemi"
    
    # Marque
    elif "marque" in desc:
        return "Marque Ennemie"
    
    # Défense
    elif "défense" in desc or "doubler" in desc:
        return "Défense Renforcée"
    
    # Expertise
    elif "expertise" in desc or "pas utile" in desc:
        return "Expertise Combat"
    
    # Capacités génériques selon première action trouvée
    elif "attaque" in desc:
        return "Attaque Spéciale"
    elif "résistance" in desc:
        return "Résistance"
    elif "améliore" in desc:
        return "Amélioration"
    
    # === GÉNÉRATION PAR DÉFAUT ===
    # Prend les 2 premiers mots importants de la description
    words = desc.replace(",", "").replace(".", "").split()
    important_words = []
    
    # Mots importants (pas les articles/prépositions)
    skip_words = ["de", "du", "des", "le", "la", "les", "un", "une", "et", "ou", "à", "au", "aux", "pour", "sur", "avec", "dans", "par"]
    
    for word in words:
        if len(word) > 2 and word not in skip_words:
            important_words.append(word.capitalize())
            if len(important_words) >= 2:
                break
    
    if important_words:
        return " ".join(important_words)
    else:
        return "Capacité Mystérieuse"

def load_sorts_and_generate_names():
    """
    Charge Sorts.xlsx et génère les noms de capacités
    FONCTION PRINCIPALE - Simple et claire
    
    Returns:
        pd.DataFrame: DataFrame avec les noms générés
    """
    sorts_file = "data/Sorts.xlsx"
    
    # Vérification fichier
    if not os.path.exists(sorts_file):
        print(f"❌ Fichier {sorts_file} non trouvé")
        return None
    
    print(f"📖 Lecture de {sorts_file}...")
    
    try:
        # Lecture Excel - feuille "Capacités" 
        df = pd.read_excel(sorts_file, sheet_name='Capacités')
        print(f"✅ {len(df)} lignes trouvées")
        
        # Création colonnes pour résultats
        df['hero_code'] = ''
        df['ability_number'] = 0
        df['generated_name'] = ''
        df['clean_description'] = ''
        
        # Traitement ligne par ligne
        generated_count = 0
        
        for index, row in df.iterrows():
            # Skip ligne d'en-tête
            if index == 0:
                continue
            
            # Extraction nom + numéro (colonne 1)
            name_and_number = str(row.iloc[0]).strip()
            if not name_and_number or name_and_number.lower() in ['nom', 'nan']:
                continue
            
            # Extraction description (colonne 3)
            description = str(row.iloc[2]).strip() if len(row) > 2 else ""
            
            # Parsing héros et numéro
            hero_code, ability_num = parse_hero_and_number(name_and_number)
            if not hero_code:
                continue
            
            # Génération du nom élégant
            generated_name = generate_ability_name(description)
            
            # Sauvegarde dans DataFrame
            df.loc[index, 'hero_code'] = hero_code
            df.loc[index, 'ability_number'] = ability_num
            df.loc[index, 'generated_name'] = generated_name
            df.loc[index, 'clean_description'] = description
            
            generated_count += 1
            print(f"✅ {hero_code}-{ability_num}: {generated_name}")
        
        print(f"\n🎯 {generated_count} noms de capacités générés !")
        return df
        
    except Exception as e:
        print(f"❌ Erreur lecture Excel: {e}")
        return None

def parse_hero_and_number(name_and_number):
    """
    Parse le nom + numéro pour extraire code héros et numéro capacité
    FONCTION SIMPLE - Gère "Elneha 1", "Atucan2", "Ours", etc.
    
    Args:
        name_and_number: Texte comme "Elneha 1"
        
    Returns:
        tuple: (code_héros, numéro) ou (None, None) si erreur
    """
    text = name_and_number.lower().strip()
    
    # Mapping noms → codes
    hero_mapping = {
        'elneha': 'P-1',
        'liarie': 'P-2',
        'atucan': 'P-3', 
        'kraor': 'P-4',
        'thordius': 'P-5',
        'stephe': 'P-6',
        'stèphe': 'P-6',
        'lame': 'P-7',
        'raishi': 'P-8'
    }
    
    # Cas spéciaux (formes Elneha)
    special_cases = {
        'ours': ('P-9', 1),
        'loup': ('P-10', 1),
        'ours s': ('P-11', 1),
        'loup s': ('P-12', 1)
    }
    
    if text in special_cases:
        return special_cases[text]
    
    # Extraction numéro
    numbers = re.findall(r'\d+', text)
    if not numbers:
        return None, None
    
    ability_num = int(numbers[0])
    
    # Extraction nom héros (retire les numéros)
    hero_name = re.sub(r'\d+', '', text).strip()
    
    if hero_name in hero_mapping:
        return hero_mapping[hero_name], ability_num
    else:
        return None, None

def save_ability_names_csv(df):
    """
    Sauvegarde les noms générés dans un CSV
    FONCTION SIMPLE - Export facile à lire
    
    Args:
        df: DataFrame avec les noms générés
    """
    if df is None:
        return False
    
    # Filtrage lignes valides uniquement
    valid_rows = df[df['hero_code'] != ''].copy()
    
    if len(valid_rows) == 0:
        print("❌ Aucune capacité valide à sauvegarder")
        return False
    
    # Sélection colonnes importantes
    export_df = valid_rows[['hero_code', 'ability_number', 'generated_name', 'clean_description']].copy()
    
    # Tri par héros puis numéro
    export_df = export_df.sort_values(['hero_code', 'ability_number'])
    
    # Sauvegarde CSV
    output_file = "data/ability_names.csv"
    export_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"💾 {len(export_df)} noms sauvegardés dans {output_file}")
    return True

def main():
    """
    FONCTION PRINCIPALE - Execute tout le processus
    """
    print("🚀 === GÉNÉRATEUR DE NOMS DE CAPACITÉS ===")
    print("==========================================")
    
    # Étape 1: Lecture et génération
    df = load_sorts_and_generate_names()
    
    if df is None:
        print("❌ Échec du processus")
        return
    
    # Étape 2: Sauvegarde CSV
    success = save_ability_names_csv(df)
    
    if success:
        print("\n🎉 SUCCÈS ! Noms de capacités générés avec succès")
        print("📄 Fichier créé: data/ability_names.csv")
        print("✅ Prêt à utiliser dans le simulateur")
    else:
        print("❌ Erreur lors de la sauvegarde")

# === EXECUTION ===
if __name__ == "__main__":
    main()