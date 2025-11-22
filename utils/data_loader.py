"""
DataLoader pour le Simulateur Périples
VERSION CONCISE - Code simplifié pour débutants Python
"""

import pandas as pd
import os
import random
from typing import List, Dict, Any
import streamlit as st

from models.character import Character, Enemy, Equipment

# Import du système de capacités (optionnel)
try:
    from utils.abilities_loader import load_all_abilities
    from models.abilities import Ability
    ABILITIES_AVAILABLE = True
except ImportError:
    ABILITIES_AVAILABLE = False

def safe_randint(min_val: int, max_val: int) -> int:
    """Version sécurisée de randint qui évite les crashes"""
    if min_val >= max_val:
        return min_val
    return random.randint(min_val, max_val)

class DataLoader:
    """Charge les données du jeu depuis Excel/CSV"""
    
    def __init__(self, data_folder: str = "data"):
        self.data_folder = data_folder
        self._create_folder_if_missing()
        
        # Cache pour les capacités
        self._abilities = None
        self._abilities_loaded = False
    
    def _create_folder_if_missing(self):
        """Crée le dossier data s'il n'existe pas"""
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
    
    # === CHARGEMENT PRINCIPAL ===
    
    def load_heroes(self) -> List[Character]:
        """Charge la liste des héros avec leurs capacités"""
        csv_file = os.path.join(self.data_folder, "heroes.csv")
        
        # Créer le CSV si absent
        if not os.path.exists(csv_file):
            self._create_csv_files()
        
        # Lire le CSV
        heroes = []
        try:
            df = pd.read_csv(csv_file)
            abilities_data = self._load_abilities()
            
            for _, row in df.iterrows():
                hero = self._create_hero_from_row(row)
                self._add_abilities_to_hero(hero, abilities_data)
                heroes.append(hero)
                
            print(f"✅ {len(heroes)} héros chargés")
            return heroes
            
        except Exception as e:
            print(f"❌ Erreur chargement héros: {e}")
            return self._create_default_heroes()
    
    def load_enemies(self) -> List[Enemy]:
        """Charge la liste des ennemis"""
        csv_file = os.path.join(self.data_folder, "enemies.csv")
        
        # Créer le CSV si absent
        if not os.path.exists(csv_file):
            self._create_csv_files()
        
        # Lire le CSV
        enemies = []
        try:
            df = pd.read_csv(csv_file)
            
            for _, row in df.iterrows():
                enemy = self._create_enemy_from_row(row)
                if enemy:
                    enemies.append(enemy)
            
            if len(enemies) == 0:
                return self._create_default_enemies()
                
            print(f"✅ {len(enemies)} ennemis chargés")
            return enemies
            
        except Exception as e:
            print(f"❌ Erreur chargement ennemis: {e}")
            return self._create_default_enemies()
    
    def load_equipment(self) -> List[Equipment]:
        """Charge la liste des équipements"""
        csv_file = os.path.join(self.data_folder, "equipment.csv")
        
        # Créer le CSV si absent
        if not os.path.exists(csv_file):
            self._create_csv_files()
        
        # Lire le CSV
        equipment = []
        try:
            df = pd.read_csv(csv_file)
            
            for _, row in df.iterrows():
                item = self._create_equipment_from_row(row)
                if item:
                    equipment.append(item)
            
            print(f"✅ {len(equipment)} équipements chargés")
            return equipment
            
        except Exception as e:
            print(f"❌ Erreur chargement équipements: {e}")
            return self._create_default_equipment()
    
    # === GESTION DES BUILDS ===
    
    def get_hero_build(self, hero_code: str) -> Dict:
        """Retourne le build complet d'un héros (équipement + capacités)"""
        equipment = self.load_equipment()
        
        # Priorité au build custom si il existe
        if hero_code in st.session_state.get('custom_builds', {}):
            return self._get_custom_build(hero_code, equipment)
        else:
            return self._get_standard_build(hero_code, equipment)
    
    def get_hero_loadout(self, hero_code: str) -> List[Equipment]:
        """Retourne seulement l'équipement d'un héros (pour compatibilité)"""
        build = self.get_hero_build(hero_code)
        return build.get('equipment', [])
    
    # === CAPACITÉS ===
    
    def get_hero_abilities(self, hero_code: str) -> List[Ability]:
        """
        Retourne les capacités d'un héros
        CRITIQUE: Retourne des COPIES pour éviter modification des instances cachées
        Fusionne les capacités de Sorts.xlsx ET de l'ability_registry (pour capacités exclusives)
        """
        from copy import deepcopy

        # Capacités depuis Sorts.xlsx (1-6)
        abilities_data = self._load_abilities()
        original_abilities = abilities_data.get(hero_code, [])
        abilities = [deepcopy(ability) for ability in original_abilities]

        # NOUVEAU - Ajouter capacités exclusives depuis ability_registry
        # Pour Elneha (P-1): capacités 101 et 102 (formes animales)
        try:
            from models.combat.abilities.individual_abilities.ability_registry import ABILITY_REGISTRY

            # Récupérer capacités du registre (inclut 101, 102 pour P-1)
            registry_abilities = ABILITY_REGISTRY.get_hero_abilities(hero_code)

            # Filtrer les capacités > 100 (capacités exclusives)
            exclusive_abilities = [deepcopy(a) for a in registry_abilities if a.ability_number > 100]

            # Fusionner avec les capacités Excel
            abilities.extend(exclusive_abilities)

        except Exception as e:
            # Si erreur, continuer avec les capacités Excel seulement
            print(f"⚠️ Impossible de charger capacités exclusives pour {hero_code}: {e}")

        return abilities
    
    def get_abilities_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des capacités disponibles"""
        abilities_data = self._load_abilities()
        
        if not abilities_data:
            return {'enabled': False, 'total_abilities': 0, 'heroes_count': 0}
        
        total = sum(len(abilities) for abilities in abilities_data.values())
        return {
            'enabled': True,
            'total_abilities': total,
            'heroes_count': len(abilities_data),
            'heroes_with_abilities': list(abilities_data.keys())
        }
    
    # === MÉTHODES PRIVÉES - CRÉATION D'OBJETS ===
    
    def _create_hero_from_row(self, row) -> Character:
        """Crée un héros depuis une ligne CSV"""
        return Character(
            code=str(row['Code']),
            name=str(row['Nom']),
            precision=int(row['Precision']),
            damage=int(row['Damage']),
            spells=int(row['Spells']),
            health=int(row['Health'])
        )
    
    def _create_enemy_from_row(self, row) -> Enemy:
        """Crée un ennemi depuis une ligne CSV"""
        try:
            # CORRECTION: Créer stats_by_players au bon format
            stats_by_players = {
                2: {
                    'damage': int(row['Damage_2J']),
                    'health': int(row['Health_2J']),
                    'defense': int(row['Defense_2J'])
                },
                3: {
                    'damage': int(row['Damage_3J']),
                    'health': int(row['Health_3J']),
                    'defense': int(row['Defense_3J'])
                },
                4: {
                    'damage': int(row['Damage_4J']),
                    'health': int(row['Health_4J']),
                    'defense': int(row['Defense_4J'])
                }
            }
            
            return Enemy(
                code=str(row['Code']),
                name=str(row['Nom']),
                defense=int(row['Defense']),
                stats_by_players=stats_by_players,
                is_magical=bool(row.get('Is_Magical', False)),
                has_magical_damage=bool(row.get('Has_Magical_Damage', False))
            )
        except Exception as e:
            print(f"⚠️ Erreur création ennemi {row.get('Nom', 'inconnu')}: {e}")
            return None
    
    def _create_equipment_from_row(self, row) -> Equipment:
        """Crée un équipement depuis une ligne CSV"""
        try:
            return Equipment(
                code=str(row['Code']),
                name=str(row['Nom']),
                type=str(row.get('Type', 'accessoire')),
                precision=int(row['Precision']),
                physical_damage=int(row['Physical_Damage']),
                magical_damage=int(row['Magical_Damage']),
                defense=int(row['Defense']),
                spells=int(row['Spells']),
                health=int(row['Health'])
            )
        except Exception as e:
            print(f"⚠️ Erreur création équipement {row.get('Nom', 'inconnu')}: {e}")
            return None
    
    # === MÉTHODES PRIVÉES - CAPACITÉS ===
    
    def _load_abilities(self) -> Dict[str, List[Ability]]:
        """Charge les capacités depuis Sorts.xlsx (avec cache)"""
        if self._abilities_loaded:
            return self._abilities or {}
        
        if not ABILITIES_AVAILABLE:
            print("⚠️ Système de capacités non disponible")
            self._abilities = {}
            self._abilities_loaded = True
            return {}
        
        # Chercher le fichier Sorts.xlsx
        sorts_file = self._find_file("Sorts.xlsx")
        if not sorts_file:
            print("⚠️ Fichier Sorts.xlsx non trouvé")
            self._abilities = {}
        else:
            try:
                self._abilities = load_all_abilities(sorts_file)
                total = sum(len(abs) for abs in self._abilities.values())
                print(f"✅ {total} capacités chargées depuis {sorts_file}")
            except Exception as e:
                print(f"❌ Erreur chargement capacités: {e}")
                self._abilities = {}
        
        self._abilities_loaded = True
        return self._abilities or {}
    
    def _add_abilities_to_hero(self, hero: Character, abilities_data: Dict):
        """Ajoute les capacités à un héros (filtre capacités hors-combat)"""
        hero_abilities = abilities_data.get(hero.code, [])
        if hero_abilities and hasattr(hero, 'add_abilities'):
            # FILTRER les capacités "Pas utile en combat"
            combat_abilities = [
                ability for ability in hero_abilities
                if not (hasattr(ability, 'description') and
                       'Pas utile en combat' in ability.description)
            ]
            hero.add_abilities(combat_abilities)
            excluded_count = len(hero_abilities) - len(combat_abilities)
            if excluded_count > 0:
                print(f"🔮 {hero.name}: {len(combat_abilities)} capacités ajoutées ({excluded_count} hors-combat exclues)")
            else:
                print(f"🔮 {hero.name}: {len(combat_abilities)} capacités ajoutées")
    
    # === MÉTHODES PRIVÉES - BUILDS ===
    
    def _get_custom_build(self, hero_code: str, equipment: List[Equipment]) -> Dict:
        """Retourne le build custom d'un héros"""
        custom_data = st.session_state.custom_builds[hero_code]
        equipment_codes = custom_data.get('equipment', [])
        hero_equipment = [eq for eq in equipment if eq.code in equipment_codes]
        
        return {
            'name': custom_data.get('name', 'Build Custom'),
            'equipment': hero_equipment,
            'is_custom': True,
            'abilities': self._get_abilities_info(hero_code)
        }
    
    def _get_standard_build(self, hero_code: str, equipment: List[Equipment]) -> Dict:
        """Retourne le build standard d'un héros"""
        hero_equipment = self._get_standard_equipment(hero_code, equipment)
        
        return {
            'name': 'Build Standard',
            'equipment': hero_equipment,
            'is_custom': False,
            'abilities': self._get_abilities_info(hero_code)
        }
    
    def _get_standard_equipment(self, hero_code: str, equipment: List[Equipment]) -> List[Equipment]:
        """Retourne l'équipement standard pour un héros - VERSION 8 HÉROS"""
        # Équipements par défaut pour chaque héros (P-9 à P-12 SUPPRIMÉS)
        standard_equipment = {
            'P-1': ['E-1', 'E-7', 'E-13'],   # Elneha
            'P-2': ['E-2', 'E-8', 'E-14'],   # Liarie
            'P-3': ['E-3', 'E-9', 'E-15'],   # Atucan
            'P-4': ['E-4', 'E-10', 'E-16'],  # Kraor
            'P-5': ['E-5', 'E-11', 'E-17'],  # Thordius
            'P-6': ['E-6', 'E-12', 'E-18'],  # Stephe
            'P-7': ['E-1', 'E-7', 'E-13'],   # Lame
            'P-8': ['E-2', 'E-8', 'E-14']    # Raishi
        }
        
        codes = standard_equipment.get(hero_code, [])
        return [eq for eq in equipment if eq.code in codes]
    
    def _get_abilities_info(self, hero_code: str) -> Dict:
        """Retourne les infos des capacités pour un héros"""
        hero_abilities = self.get_hero_abilities(hero_code)
        return {
            'enabled': ABILITIES_AVAILABLE,
            'count': len(hero_abilities),
            'details': [
                {
                    'number': ability.ability_number,
                    'name': ability.name,
                    'cost': ability.spell_cost,
                    'unlocked': ability.is_unlocked
                }
                for ability in hero_abilities
            ]
        }
    
    # === MÉTHODES PRIVÉES - FICHIERS ===
    
    def _find_file(self, filename: str) -> str:
        """Trouve un fichier dans plusieurs emplacements"""
        locations = [
            os.path.join(self.data_folder, filename),  # data/filename
            filename,                                   # racine/filename
            os.path.join(".", filename)                # ./filename
        ]
        
        for location in locations:
            if os.path.exists(location):
                return location
        
        return None
    
    def _create_csv_files(self):
        """Crée les fichiers CSV depuis Data_cards.xlsx"""
        excel_file = self._find_file("Data_cards.xlsx")
        
        if not excel_file:
            print("❌ Data_cards.xlsx non trouvé, utilisation des données par défaut")
            self._create_fallback_files()
            return
        
        try:
            print(f"📁 Import depuis {excel_file}")
            
            # Héros
            df = pd.read_excel(excel_file, sheet_name="Personnages")
            df.to_csv(os.path.join(self.data_folder, "heroes.csv"), index=False)
            print(f"✅ {len(df)} héros exportés")
            
            # Ennemis
            df = pd.read_excel(excel_file, sheet_name="Ennemis")
            df.to_csv(os.path.join(self.data_folder, "enemies.csv"), index=False)
            print(f"✅ {len(df)} ennemis exportés")
            
            # Équipements
            df = pd.read_excel(excel_file, sheet_name="Equipement")
            df.to_csv(os.path.join(self.data_folder, "equipment.csv"), index=False)
            print(f"✅ {len(df)} équipements exportés")
            
        except Exception as e:
            print(f"❌ Erreur import Excel: {e}")
            self._create_fallback_files()
    
    # === DONNÉES PAR DÉFAUT ===
    
    def _create_fallback_files(self):
        """Crée des fichiers CSV basiques si Excel absent - VERSION 8 HÉROS"""
        print("🔄 Création données par défaut...")
        
        # Héros par défaut (8 héros uniquement)
        heroes_data = {
            'Code': ['P-1', 'P-2', 'P-3', 'P-4', 'P-5', 'P-6', 'P-7', 'P-8'],
            'Nom': ['Elneha', 'Liarie', 'Atucan', 'Kraor', 'Thordius', 'Stephe', 'Lame', 'Raishi'],
            'Precision': [6, 0, 3, 5, 3, 4, 7, 8],
            'Damage': [2, 0, 2, 3, 3, 1, 4, 3],
            'Spells': [3, 10, 2, 1, 0, 4, 0, 0],
            'Health': [5, 6, 9, 7, 10, 4, 6, 5]
        }
        pd.DataFrame(heroes_data).to_csv(os.path.join(self.data_folder, "heroes.csv"), index=False)
        
        # Équipements par défaut
        equipment_data = {
            'Code': ['E-1', 'E-2', 'E-3', 'E-4', 'E-5', 'E-6'],
            'Nom': ['Épée', 'Arc', 'Bâton', 'Dague', 'Marteau', 'Armure'],
            'Type': ['arme', 'arme', 'arme', 'arme', 'arme', 'armure'],
            'Precision': [1, 3, 0, 2, 0, 0],
            'Physical_Damage': [2, 1, 0, 1, 3, 0],
            'Magical_Damage': [0, 0, 2, 0, 0, 0],
            'Defense': [0, 0, 0, 0, 0, 2],
            'Spells': [0, 0, 1, 0, 0, 0],
            'Health': [0, 0, 0, 0, 0, 1]
        }
        pd.DataFrame(equipment_data).to_csv(os.path.join(self.data_folder, "equipment.csv"), index=False)
        
        # Ennemis par défaut (8 au lieu de 2)
        enemies_data = {
            'Code': ['EN-1', 'EN-2', 'EN-3', 'EN-4', 'EN-5', 'EN-6', 'EN-7', 'EN-8'],
            'Nom': ['Gobelin', 'Orc', 'Squelette', 'Mage', 'Troll', 'Loup', 'Bandit', 'Dragon'],
            'Defense': [0, 1, 0, 0, 2, 0, 1, 3],
            'Damage_2J': [1, 2, 1, 2, 3, 2, 2, 4], 'Health_2J': [2, 4, 1, 3, 6, 3, 3, 8], 'Defense_2J': [0, 1, 0, 0, 2, 0, 1, 3],
            'Damage_3J': [1, 2, 1, 3, 4, 2, 2, 5], 'Health_3J': [3, 5, 2, 4, 8, 4, 4, 10], 'Defense_3J': [0, 1, 0, 0, 2, 0, 1, 3],
            'Damage_4J': [2, 3, 2, 4, 5, 3, 3, 6], 'Health_4J': [4, 6, 3, 5, 10, 5, 5, 12], 'Defense_4J': [1, 2, 0, 1, 3, 1, 2, 4],
            'Is_Magical': [False, False, False, True, False, False, False, True],
            'Has_Magical_Damage': [False, False, False, True, False, False, False, True]
        }
        pd.DataFrame(enemies_data).to_csv(os.path.join(self.data_folder, "enemies.csv"), index=False)
        
        print("✅ Fichiers par défaut créés")
    
    def _create_default_heroes(self) -> List[Character]:
        """Crée des héros par défaut en cas d'erreur - VERSION 8 HÉROS"""
        heroes_data = [
            {'code': 'P-1', 'name': 'Elneha', 'precision': 6, 'damage': 2, 'spells': 3, 'health': 5},
            {'code': 'P-2', 'name': 'Liarie', 'precision': 0, 'damage': 0, 'spells': 10, 'health': 6},
            {'code': 'P-3', 'name': 'Atucan', 'precision': 3, 'damage': 2, 'spells': 2, 'health': 9},
            {'code': 'P-4', 'name': 'Kraor', 'precision': 5, 'damage': 3, 'spells': 1, 'health': 7},
            {'code': 'P-5', 'name': 'Thordius', 'precision': 3, 'damage': 3, 'spells': 0, 'health': 10},
            {'code': 'P-6', 'name': 'Stephe', 'precision': 4, 'damage': 1, 'spells': 4, 'health': 4},
            {'code': 'P-7', 'name': 'Lame', 'precision': 7, 'damage': 4, 'spells': 0, 'health': 6},
            {'code': 'P-8', 'name': 'Raishi', 'precision': 8, 'damage': 3, 'spells': 0, 'health': 5}
        ]
        
        heroes = []
        abilities_data = self._load_abilities()
        
        for data in heroes_data:
            hero = Character(**data)
            self._add_abilities_to_hero(hero, abilities_data)
            heroes.append(hero)
        
        return heroes
    
    def _create_default_enemies(self) -> List[Enemy]:
        """Crée des ennemis par défaut en cas d'erreur"""
        enemies_data = [
            {
                'code': 'EN-1', 'name': 'Gobelin', 'defense': 0,
                'stats_by_players': {
                    2: {'damage': 1, 'health': 2, 'defense': 0},
                    3: {'damage': 1, 'health': 3, 'defense': 0},
                    4: {'damage': 2, 'health': 4, 'defense': 1}
                },
                'is_magical': False, 'has_magical_damage': False
            },
            {
                'code': 'EN-2', 'name': 'Orc', 'defense': 1,
                'stats_by_players': {
                    2: {'damage': 2, 'health': 4, 'defense': 1},
                    3: {'damage': 2, 'health': 5, 'defense': 1},
                    4: {'damage': 3, 'health': 6, 'defense': 2}
                },
                'is_magical': False, 'has_magical_damage': False
            },
            {
                'code': 'EN-3', 'name': 'Troll', 'defense': 2,
                'stats_by_players': {
                    2: {'damage': 3, 'health': 6, 'defense': 2},
                    3: {'damage': 4, 'health': 8, 'defense': 2},
                    4: {'damage': 5, 'health': 10, 'defense': 3}
                },
                'is_magical': False, 'has_magical_damage': False
            },
            {
                'code': 'EN-4', 'name': 'Mage Sombre', 'defense': 0,
                'stats_by_players': {
                    2: {'damage': 2, 'health': 3, 'defense': 0},
                    3: {'damage': 3, 'health': 4, 'defense': 0},
                    4: {'damage': 4, 'health': 5, 'defense': 1}
                },
                'is_magical': True, 'has_magical_damage': True
            }
        ]
        
        return [Enemy(**data) for data in enemies_data]
    
    def _create_default_equipment(self) -> List[Equipment]:
        """Crée des équipements par défaut en cas d'erreur"""
        equipment_data = [
            {'code': 'E-1', 'name': 'Épée', 'type': 'arme', 'precision': 1, 'physical_damage': 2, 'magical_damage': 0, 'defense': 0, 'spells': 0, 'health': 0},
            {'code': 'E-2', 'name': 'Arc', 'type': 'arme', 'precision': 3, 'physical_damage': 1, 'magical_damage': 0, 'defense': 0, 'spells': 0, 'health': 0},
            {'code': 'E-3', 'name': 'Armure', 'type': 'armure', 'precision': 0, 'physical_damage': 0, 'magical_damage': 0, 'defense': 2, 'spells': 0, 'health': 1}
        ]
        
        return [Equipment(**data) for data in equipment_data]

# === FONCTION UTILITAIRE ===

def get_hero_with_abilities(hero_code: str, loader: DataLoader) -> Character:
    """Récupère un héros avec ses capacités intégrées"""
    heroes = loader.load_heroes()
    return next((h for h in heroes if h.code == hero_code), None)

# === FONCTION DE NETTOYAGE SESSION STATE ===

def cleanup_removed_heroes_from_session():
    """
    Nettoie le session_state des codes héros supprimés (P-9, P-10, P-11, P-12)
    À appeler au démarrage de l'application pour éviter les erreurs
    """
    removed_codes = ['P-9', 'P-10', 'P-11', 'P-12']
    
    # Nettoyage selected_heroes
    if 'selected_heroes' in st.session_state:
        old_selected = st.session_state.selected_heroes.copy()
        st.session_state.selected_heroes = [code for code in old_selected if code not in removed_codes]
        
        removed_count = len(old_selected) - len(st.session_state.selected_heroes)
        if removed_count > 0:
            print(f"🧹 Session cleanup: {removed_count} pseudo-héros supprimés de la sélection")
    
    # Nettoyage hero_difficulties
    if 'hero_difficulties' in st.session_state:
        for code in removed_codes:
            if code in st.session_state.hero_difficulties:
                del st.session_state.hero_difficulties[code]
                print(f"🧹 Session cleanup: Difficulté {code} supprimée")
    
    # Nettoyage custom_builds
    if 'custom_builds' in st.session_state:
        for code in removed_codes:
            if code in st.session_state.custom_builds:
                build_name = st.session_state.custom_builds[code].get('name', 'Build Custom')
                del st.session_state.custom_builds[code]
                print(f"🧹 Session cleanup: Build custom '{build_name}' ({code}) supprimé")