"""
Chargeur de capacités SIMPLIFIÉ pour le Simulateur Périples
VERSION SIMPLE - Utilise ability_names.csv pour les vrais noms
"""

import pandas as pd
import os
from typing import List, Dict, Optional
from models.abilities import Ability, AbilityEffect, TargetType

class AbilitiesLoader:
    """
    Chargeur simple des capacités depuis Sorts.xlsx + ability_names.csv
    CODE SIMPLIFIÉ pour débutants Python
    """
    
    def __init__(self):
        self.sorts_file = "data/Sorts.xlsx"
        self.names_file = "data/ability_names.csv"
        self.names_cache = {}  # Cache des noms élégants
    
    def load_abilities_from_excel(self) -> Dict[str, List[Ability]]:
        """
        Charge toutes les capacités avec les vrais noms élégants
        FONCTION PRINCIPALE - Simple et claire
        
        Returns:
            Dict[str, List[Ability]]: Capacités organisées par code de héros
        """
        print(f"📖 Chargement des capacités...")
        
        # Étape 1: Charger les noms élégants
        if not self._load_names_cache():
            print("⚠️ Utilisation des noms par défaut")
        
        # Étape 2: Charger les données Sorts.xlsx
        if not os.path.exists(self.sorts_file):
            print(f"❌ {self.sorts_file} non trouvé, utilisation capacités test")
            return self._create_test_abilities()
        
        try:
            # Lecture Excel simple
            df = pd.read_excel(self.sorts_file, sheet_name='Capacités')
            
            abilities_by_hero = {}
            loaded_count = 0
            
            # Traitement ligne par ligne
            for index, row in df.iterrows():
                if index == 0:  # Skip en-tête
                    continue
                
                ability = self._parse_ability_row(row)
                if ability:
                    # Organiser par héros
                    if ability.hero_code not in abilities_by_hero:
                        abilities_by_hero[ability.hero_code] = []
                    
                    abilities_by_hero[ability.hero_code].append(ability)
                    loaded_count += 1
            
            print(f"✅ {loaded_count} capacités chargées pour {len(abilities_by_hero)} héros")
            return abilities_by_hero
            
        except Exception as e:
            print(f"❌ Erreur lecture Excel: {e}")
            return self._create_test_abilities()
    
    def _load_names_cache(self) -> bool:
        """
        Charge les noms élégants depuis ability_names.csv
        FONCTION SIMPLE - Cache en mémoire
        
        Returns:
            bool: True si chargé avec succès
        """
        if not os.path.exists(self.names_file):
            print(f"⚠️ {self.names_file} non trouvé")
            return False
        
        try:
            df = pd.read_csv(self.names_file)
            
            # Création cache : (hero_code, ability_number) → nom
            for _, row in df.iterrows():
                key = (row['hero_code'], int(row['ability_number']))
                self.names_cache[key] = row['generated_name']
            
            print(f"✅ {len(self.names_cache)} noms élégants chargés")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lecture noms: {e}")
            return False
    
    def _get_elegant_name(self, hero_code: str, ability_number: int, fallback: str) -> str:
        """
        Récupère le nom élégant depuis le cache
        FONCTION SIMPLE - Lookup avec fallback
        
        Args:
            hero_code: Code du héros (P-1, P-2, etc.)
            ability_number: Numéro capacité (1-6)
            fallback: Nom par défaut si pas trouvé
            
        Returns:
            str: Nom élégant ou fallback
        """
        key = (hero_code, ability_number)
        return self.names_cache.get(key, fallback)
    
    def _parse_ability_row(self, row) -> Optional[Ability]:
        """
        Parse une ligne Excel en objet Ability
        FONCTION SIMPLE - Extraction données de base
        
        Args:
            row: Ligne DataFrame pandas
            
        Returns:
            Optional[Ability]: Capacité créée ou None
        """
        # Colonnes Excel : [Nom+Numéro, Coût, Description, Limitations]
        if len(row) < 3:
            return None
        
        # Colonne 1: Extraction héros + numéro
        name_and_number = str(row.iloc[0]).strip()
        if not name_and_number or name_and_number.lower() in ['nom', 'nan']:
            return None
        
        hero_code, ability_number = self._parse_hero_info(name_and_number)
        if not hero_code:
            return None
        
        # Colonne 2: Coût en sorts
        spell_cost = self._safe_int(row.iloc[1], 0)
        
        # Colonne 3: Description
        description = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
        
        # Colonne 4: Limitations (optionnel) - CONVERSION AUTOMATIQUE JOUR → COMBAT
        uses_per_combat = self._parse_limitations(row.iloc[3] if len(row) > 3 else None)
        
        # NOM ÉLÉGANT depuis CSV ou fallback
        elegant_name = self._get_elegant_name(hero_code, ability_number, f"Capacité {ability_number}")
        
        # Création objet Ability
        ability = Ability(
            hero_code=hero_code,
            ability_number=ability_number,
            name=elegant_name,  # ✅ VRAI NOM ÉLÉGANT
            spell_cost=spell_cost,
            description=description,
            uses_per_combat=uses_per_combat,
            effects=self._create_simple_effects(description),
            target_type=self._guess_target_type(description),
            is_unlocked=(ability_number == 1)  # Première capacité débloquée
        )
        
        return ability
    
    def _parse_hero_info(self, name_and_number: str) -> tuple[str, int]:
        """
        Parse "Elneha 1" → ("P-1", 1)
        FONCTION SIMPLE - Mapping de base
        """
        import re
        
        text = name_and_number.lower().strip()
        
        # Mapping simple
        heroes = {
            'elneha': 'P-1', 'liarie': 'P-2', 'atucan': 'P-3', 'kraor': 'P-4',
            'thordius': 'P-5', 'stephe': 'P-6', 'stèphe': 'P-6', 'lame': 'P-7', 'raishi': 'P-8'
        }
        
        # Cas spéciaux formes
        specials = {'ours': ('P-9', 1), 'loup': ('P-10', 1), 'ours s': ('P-11', 1), 'loup s': ('P-12', 1)}
        if text in specials:
            return specials[text]
        
        # Extraction numéro
        numbers = re.findall(r'\d+', text)
        if not numbers:
            return None, None
        
        ability_num = int(numbers[0])
        hero_name = re.sub(r'\d+', '', text).strip()
        
        hero_code = heroes.get(hero_name)
        if hero_code and 1 <= ability_num <= 6:
            return hero_code, ability_num
        
        return None, None
    
    def _parse_limitations(self, limitation_text) -> Optional[int]:
        """
        Parse limitations et convertit tout en "par combat"
        "2 / combat" → 2
        "1 / jour" → 1 (conversion automatique)
        
        FONCTION SIMPLE - Regex basique avec conversion jour→combat
        """
        if not limitation_text or pd.isna(limitation_text):
            return None
        
        import re
        text = str(limitation_text).lower()
        
        # Recherche limitations par combat
        combat_match = re.search(r'(\d+)\s*/\s*combat', text)
        if combat_match:
            return int(combat_match.group(1))
        
        # Recherche limitations par jour - CONVERSION AUTOMATIQUE
        day_match = re.search(r'(\d+)\s*/\s*jour', text)
        if day_match:
            # CONVERSION : 1/jour devient 1/combat pour notre système
            uses_per_day = int(day_match.group(1))
            print(f"🔄 Conversion {uses_per_day}/jour → {uses_per_day}/combat")
            return uses_per_day
        
        return None
    
    def _create_simple_effects(self, description: str) -> List[AbilityEffect]:
        """
        Crée effets simples depuis description
        FONCTION SIMPLE - Détection mots-clés de base
        """
        effects = []
        desc = description.lower()
        
        # Détection soin
        if 'soin' in desc or 'guéri' in desc:
            # Extraction valeur soin
            import re
            heal_match = re.search(r'(\d+)\s*blessures?', desc)
            heal_value = int(heal_match.group(1)) if heal_match else 2
            
            effects.append(AbilityEffect(
                type="heal",
                value=heal_value,
                description=f"Soigne {heal_value} PV"
            ))
        
        # Détection dégâts
        elif 'dégât' in desc or 'inflige' in desc:
            import re
            damage_match = re.search(r'(\d+)\s*dégâts?', desc)
            damage_value = int(damage_match.group(1)) if damage_match else 3
            
            effect_type = "magical_damage" if "magique" in desc else "damage"
            effects.append(AbilityEffect(
                type=effect_type,
                value=damage_value,
                description=f"Inflige {damage_value} dégâts"
            ))
        
        # Effets génériques
        else:
            effects.append(AbilityEffect(
                type="special",
                description=description[:50] + "..." if len(description) > 50 else description
            ))
        
        return effects
    
    def _guess_target_type(self, description: str) -> TargetType:
        """
        Devine le type de cible depuis description
        FONCTION SIMPLE - Mots-clés basiques
        """
        desc = description.lower()
        
        if 'tous les adversaires' in desc or 'tous les ennemis' in desc:
            return TargetType.ALL_ENEMIES
        elif 'tous les personnages' in desc:
            return TargetType.ALL_ALLIES
        elif 'adversaire' in desc or 'ennemi' in desc:
            return TargetType.ENEMY
        elif 'personnage' in desc:
            return TargetType.ALLY
        else:
            return TargetType.SELF
    
    def _safe_int(self, value, default: int) -> int:
        """Conversion sécurisée en int"""
        if pd.isna(value):
            return default
        try:
            return int(float(value))
        except:
            return default
    
    def _create_test_abilities(self) -> Dict[str, List[Ability]]:
        """
        Capacités de test si pas de fichier Excel
        FONCTION SIMPLE - Données minimales pour tests
        """
        print("🔄 Utilisation capacités de test...")
        
        test_abilities = {
            'P-1': [  # Elneha
                Ability(
                    hero_code='P-1', ability_number=1, name='Forme d\'Ours', spell_cost=1,
                    description='Se métamorphose en Ours pour plus de défense',
                    effects=[AbilityEffect(type="transformation", description="Forme d'ours")],
                    target_type=TargetType.SELF, is_unlocked=True
                ),
                Ability(
                    hero_code='P-1', ability_number=2, name='Soin Naturel', spell_cost=1,
                    description='Soigne 4 blessures d\'un personnage', uses_per_combat=2,
                    effects=[AbilityEffect(type="heal", value=4, description="Soin 4 PV")],
                    target_type=TargetType.ALLY, is_unlocked=False
                )
            ],
            'P-3': [  # Atucan
                Ability(
                    hero_code='P-3', ability_number=1, name='Soin Proportionnel', spell_cost=1,
                    description='Soigne la moitié des PV max du personnage', uses_per_combat=1,
                    effects=[AbilityEffect(type="heal", description="Soin proportionnel")],
                    target_type=TargetType.ALLY, is_unlocked=True
                )
            ]
        }
        
        return test_abilities

# === FONCTIONS UTILITAIRES SIMPLES ===

def load_all_abilities(excel_path: str = "data/Sorts.xlsx") -> Dict[str, List[Ability]]:
    """
    Fonction utilitaire simple pour charger toutes les capacités
    
    Returns:
        Dict[str, List[Ability]]: Capacités par héros avec vrais noms
    """
    loader = AbilitiesLoader()
    return loader.load_abilities_from_excel()

def get_abilities_summary(abilities_by_hero: Dict[str, List[Ability]]) -> str:
    """
    Résumé simple des capacités chargées
    
    Returns:
        str: Résumé lisible
    """
    if not abilities_by_hero:
        return "Aucune capacité chargée"
    
    total = sum(len(abilities) for abilities in abilities_by_hero.values())
    heroes_count = len(abilities_by_hero)
    
    return f"{total} capacités pour {heroes_count} héros"

# === TEST SIMPLE ===

def test_loader():
    """Test rapide du loader simplifié"""
    print("🧪 === TEST LOADER SIMPLIFIÉ ===")
    
    try:
        abilities = load_all_abilities()
        
        if not abilities:
            print("❌ Aucune capacité chargée")
            return False
        
        print(f"✅ Résumé: {get_abilities_summary(abilities)}")
        
        # Affichage exemple capacités avec vrais noms
        for hero_code, hero_abilities in list(abilities.items())[:2]:  # 2 premiers héros
            print(f"\n🧙‍♂️ {hero_code}:")
            for ability in hero_abilities[:3]:  # 3 premières capacités
                print(f"  • {ability.name} (coût: {ability.spell_cost})")
                if ability.uses_per_combat:
                    print(f"    Limite: {ability.uses_per_combat}/combat")
        
        return True
    
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

if __name__ == "__main__":
    test_loader()