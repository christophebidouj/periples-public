import pandas as pd
import os
from typing import List, Dict, Any
import streamlit as st

# Import relatif correct pour ta structure
from models.character import Character, Enemy, Equipment

class DataLoader:
    """Chargeur de données depuis les fichiers CSV avec import Excel automatique"""
    
    def __init__(self, data_path: str = "data"):
        self.data_path = data_path
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Crée le dossier data s'il n'existe pas"""
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
    
    def load_heroes(self) -> List[Character]:
        """Charge la liste des héros depuis le CSV"""
        try:
            csv_path = os.path.join(self.data_path, "heroes.csv")
            
            if not os.path.exists(csv_path):
                print(f"⚠️ Fichier {csv_path} non trouvé, création des données")
                self.create_csv_files()
            
            df = pd.read_csv(csv_path)
            heroes = []
            
            for _, row in df.iterrows():
                try:
                    hero = Character(
                        code=str(row['Code']),
                        name=str(row['Nom']),
                        precision=int(row['Precision']),
                        damage=int(row['Damage']),
                        spells=int(row['Spells']),
                        health=int(row['Health'])
                    )
                    heroes.append(hero)
                except Exception as e:
                    print(f"⚠️ Erreur lors du chargement du héros ligne {_}: {e}")
                    continue
            
            print(f"✅ {len(heroes)} héros chargés depuis {csv_path}")
            return heroes
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des héros: {e}")
            return self._create_default_heroes()
    
    def load_enemies(self) -> List[Enemy]:
        """Charge la liste des ennemis depuis le CSV"""
        try:
            csv_path = os.path.join(self.data_path, "enemies.csv")
            
            if not os.path.exists(csv_path):
                print(f"⚠️ Fichier {csv_path} non trouvé, création des données")
                self.create_csv_files()
            
            df = pd.read_csv(csv_path)
            enemies = []
            
            for _, row in df.iterrows():
                try:
                    # Construction du dictionnaire des stats par nombre de joueurs
                    stats_by_players = {
                        2: {
                            "damage": int(row['Damage_2J']),
                            "health": int(row['Health_2J']),
                            "defense": int(row['Defense_2J'])
                        },
                        3: {
                            "damage": int(row['Damage_3J']),
                            "health": int(row['Health_3J']), 
                            "defense": int(row['Defense_3J'])
                        },
                        4: {
                            "damage": int(row['Damage_4J']),
                            "health": int(row['Health_4J']),
                            "defense": int(row['Defense_4J'])
                        }
                    }
                    
                    # Conversion des booléens
                    is_magical = str(row['Is_Magical']).lower() in ['true', '1', 'oui', 'yes']
                    has_magical_damage = str(row['Has_Magical_Damage']).lower() in ['true', '1', 'oui', 'yes']
                    
                    enemy = Enemy(
                        code=str(row['Code']),
                        name=str(row['Nom']),
                        defense=int(row['Defense']),
                        stats_by_players=stats_by_players,
                        is_magical=is_magical,
                        has_magical_damage=has_magical_damage
                    )
                    enemies.append(enemy)
                    
                except Exception as e:
                    print(f"⚠️ Erreur lors du chargement de l'ennemi ligne {_}: {e}")
                    continue
            
            print(f"✅ {len(enemies)} ennemis chargés depuis {csv_path}")
            return enemies
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des ennemis: {e}")
            return self._create_default_enemies()
    
    def load_equipment(self) -> List[Equipment]:
        """Charge la liste des équipements depuis le CSV avec support Type"""
        try:
            csv_path = os.path.join(self.data_path, "equipment.csv")
            
            if not os.path.exists(csv_path):
                print(f"⚠️ Fichier {csv_path} non trouvé, création des données")
                self.create_csv_files()
            
            df = pd.read_csv(csv_path)
            equipment_list = []
            
            for _, row in df.iterrows():
                try:
                    equipment = Equipment(
                        code=str(row['Code']),
                        name=str(row['Nom']),
                        type=str(row.get('Type', 'accessoire')),  # AJOUT avec fallback
                        precision=int(row['Precision']),
                        physical_damage=int(row['Physical_Damage']),
                        magical_damage=int(row['Magical_Damage']),
                        defense=int(row['Defense']),
                        spells=int(row['Spells']),
                        health=int(row['Health'])
                    )
                    equipment_list.append(equipment)
                    
                except Exception as e:
                    print(f"⚠️ Erreur lors du chargement de l'équipement ligne {_}: {e}")
                    continue
            
            print(f"✅ {len(equipment_list)} équipements chargés depuis {csv_path}")
            return equipment_list
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des équipements: {e}")
            return self._create_default_equipment()
    
    def get_hero_build(self, hero_code: str) -> Dict:
        """
        CORRIGÉ - Retourne le build d'un héros avec priorisation Custom > Standard
        Un seul build par héros : custom remplace le standard s'il existe
        """
        # Chargement des équipements
        try:
            csv_path = os.path.join(self.data_path, "equipment.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                equipment = []
                for _, row in df.iterrows():
                    equipment.append(Equipment(
                        code=str(row['Code']),
                        name=str(row['Nom']),
                        type=str(row.get('Type', 'accessoire')),
                        precision=int(row['Precision']),
                        physical_damage=int(row['Physical_Damage']),
                        magical_damage=int(row['Magical_Damage']),
                        defense=int(row['Defense']),
                        spells=int(row['Spells']),
                        health=int(row['Health'])
                    ))
            else:
                equipment = []
        except Exception as e:
            print(f"⚠️ Erreur chargement équipements pour hero_build: {e}")
            equipment = []
        
        # PRIORISATION : Custom > Standard
        if hero_code in st.session_state.get('custom_builds', {}):
            # BUILD CUSTOM TROUVÉ - Il remplace le standard
            custom_data = st.session_state.custom_builds[hero_code]
            equipment_codes = custom_data.get('equipment', [])
            hero_equipment = [eq for eq in equipment if eq.code in equipment_codes]
            build_name = custom_data.get('name', 'Build Custom')
            is_custom = True
        else:
            # FALLBACK : Build standard uniquement si pas de custom
            hero_equipment = self._get_standard_loadout(hero_code, equipment)
            build_name = "Build Standard"
            is_custom = False
        
        # Création du héros équipé
        heroes = self.load_heroes()
        hero = next(h for h in heroes if h.code == hero_code)
        
        hero_copy = hero.model_copy()
        hero_copy.equip_items(hero_equipment, build_name)
        
        return {
            'hero_equipped': hero_copy, 
            'equipment': hero_equipment,
            'build_name': build_name, 
            'is_custom': is_custom, 
            'stats': hero_copy.get_stats_summary()
        }
    
    def _get_standard_loadout(self, hero_code: str, equipment: List[Equipment]) -> List[Equipment]:
        """Retourne l'équipement standard d'un héros (fonction privée)"""
        # Builds optimisés par héros selon leur profil
        loadouts = {
            # Héros de base
            'P-1': ['O-23', 'O-32'],  # Elneha (Druide): Hache guerre + Vêtement cuir
            'P-2': ['O-42', 'O-59'],  # Liarie (Mage): Pierre mémoire + Potion magie  
            'P-3': ['O-31', 'O-36'],  # Atucan (Tank): Bouclier fer + Armure plates
            'P-4': ['O-83', 'O-34'],  # Kraor (DPS): Épée Olestrin + Armure cuir
            'P-5': ['O-23', 'O-39'],  # Thordius (Berserker): Hache guerre + Couronne santé
            
            # Héros étendus
            'P-6': ['O-13', 'O-42'],  # Stèphe (Barde): Luth + Pierre mémoire
            'P-7': ['O-78', 'O-32'],  # Lame (Assassin): Dagues jumelles + Vêtement cuir
            'P-8': ['O-40', 'O-27'],  # Raishi (Archer): Bague impact + Arbalète
            'P-9': ['O-75', 'O-82'],  # Ours (Tank): Implacable + Armure Jaron
            'P-10': ['O-21', 'O-35'],  # Loup (Guerrier): Espadon + Armure cuir
            'P-11': ['O-73', 'O-85'],  # Ours S (Paladin): Marteau juste + Don élus
            'P-12': ['O-77', 'O-41']   # Loup S (Moine): Poings feu + Ceinture parade
        }
        
        hero_equipment_codes = loadouts.get(hero_code, [])
        return [eq for eq in equipment if eq.code in hero_equipment_codes]
    
    def get_hero_loadout(self, hero_code: str) -> List[Equipment]:
        """DÉPRÉCIÉ - Utilisez get_hero_build() à la place"""
        print("⚠️ get_hero_loadout() est déprécié, utilisez get_hero_build()")
        return self.get_hero_build(hero_code)['equipment']
    
    def get_build_templates(self) -> dict:
        """Retourne les templates de builds disponibles"""
        return {
            "🐻 Druide": {
                "description": "Focus corps à corps et polyvalence",
                "equipment_codes": ['O-23', 'O-32'],  # Hache + Vêtement
                "bonus_description": "+2 Précision, +3 Dégâts, +1 Défense"
            },
            "⚔️ Guerrier": {
                "description": "Équilibré entre attaque et défense", 
                "equipment_codes": ['O-83', 'O-34', 'O-30'],  # Épée + Armure + Bouclier
                "bonus_description": "+3 Précision, +3 Dégâts, +2 Défense"
            },
            "🛡️ Tank": {
                "description": "Maximum de défense et points de vie",
                "equipment_codes": ['O-31', 'O-36', 'O-39'],  # Bouclier + Armure + Couronne
                "bonus_description": "+4 Défense, +2 PV"
            },
            "🗡️ Berserker": {
                "description": "Maximum de dégâts, peu de défense",
                "equipment_codes": ['O-75', 'O-23'],  # Implacable + Hache guerre
                "bonus_description": "+2 Précision, +9 Dégâts"
            },
            "🔮 Mage": {
                "description": "Focus sorts et dégâts magiques",
                "equipment_codes": ['O-42', 'O-59', 'O-73'],  # Pierre + Potion + Marteau juste
                "bonus_description": "+8 Sorts, +4 Précision, +2 Dégâts magiques"
            },
            "🎭 Support": {
                "description": "Soins et soutien d'équipe",
                "equipment_codes": ['O-85', 'O-56', 'O-13'],  # Don élus + Potion vigueur + Luth
                "bonus_description": "+4 PV, +1 Sort"
            }
        }
    
    def import_from_excel(self, excel_path: str = "Data_cards.xlsx") -> bool:
        """Importe toutes les données depuis Data_cards.xlsx vers les fichiers CSV"""
        try:
            print(f"📖 Lecture du fichier {excel_path}...")
            
            # Lecture des feuilles Excel
            heroes_df = pd.read_excel(excel_path, sheet_name='Personnages')
            enemies_df = pd.read_excel(excel_path, sheet_name='Ennemis')  
            equipment_df = pd.read_excel(excel_path, sheet_name='Equipement')
            
            print(f"✅ Données lues :")
            print(f"   • {len(heroes_df)} héros")
            print(f"   • {len(enemies_df)} ennemis") 
            print(f"   • {len(equipment_df)} équipements")
            
            # === CONVERSION HEROES AVEC NOMS EXACTS ===
            heroes_csv_data = []
            
            for _, row in heroes_df.iterrows():
                try:
                    # Fonction helper pour convertir en int avec fallback
                    def safe_int(value, default=0):
                        if pd.isna(value) or value == '' or value is None:
                            return default
                        try:
                            return int(float(value))  # float d'abord au cas où c'est "3.0"
                        except (ValueError, TypeError):
                            return default
                    
                    heroes_csv_data.append([
                        str(row['Code']),
                        str(row['Nom']),
                        safe_int(row['Préci'], 0),
                        safe_int(row['Dégâts'], 0),
                        safe_int(row['Sort'], 0),
                        safe_int(row['Santé'], 1)
                    ])
                except Exception as e:
                    print(f"⚠️ Erreur héros ligne {_}: {e} - Données: {dict(row)}")
                    continue
            
            # === CONVERSION ENEMIES AVEC NOMS EXACTS ===
            enemies_csv_data = []
            
            for _, row in enemies_df.iterrows():
                try:
                    # Fonction helper pour convertir en int avec fallback
                    def safe_int(value, default=0):
                        if pd.isna(value) or value == '' or value is None:
                            return default
                        try:
                            return int(float(value))  # float d'abord au cas où c'est "3.0"
                        except (ValueError, TypeError):
                            return default
                    
                    # Conversion des booléens
                    is_magical = str(row.get('Magique', 'Non')).lower() in ['oui', 'yes', 'true', '1', 'vrai']
                    has_magical_damage = str(row.get('Dégats M.', 'Non')).lower() in ['oui', 'yes', 'true', '1', 'vrai']
                    
                    enemies_csv_data.append([
                        str(row['Code']),
                        str(row['Nom']),
                        safe_int(row['Défense'], 10),
                        safe_int(row['Dégâts 2J'], 1),
                        safe_int(row['Santé 2J'], 5),
                        safe_int(row['Parade 2J'], 0),
                        safe_int(row['Dégâts 3J'], 2),
                        safe_int(row['Santé 3J'], 7),
                        safe_int(row['Parade 3J'], 0),
                        safe_int(row['Dégâts 4J'], 3),
                        safe_int(row['Santé 4J'], 10),
                        safe_int(row['Parade 4J'], 1),
                        is_magical,
                        has_magical_damage
                    ])
                except Exception as e:
                    print(f"⚠️ Erreur ennemi ligne {_}: {e} - Données: {dict(row)}")
                    continue
            
            # === CONVERSION EQUIPMENT AVEC NOMS EXACTS ET TYPE ===
            equipment_csv_data = []
            
            for _, row in equipment_df.iterrows():
                try:
                    # Fonction helper pour convertir en int avec fallback
                    def safe_int(value, default=0):
                        if pd.isna(value) or value == '' or value is None:
                            return default
                        try:
                            return int(float(value))  # float d'abord au cas où c'est "3.0"
                        except (ValueError, TypeError):
                            return default
                    
                    equipment_csv_data.append([
                        str(row['Code']),
                        str(row['Nom']),
                        str(row.get('Type', 'accessoire')),  # AJOUT colonne Type
                        safe_int(row['Précis.'], 0),
                        safe_int(row['Dég. P'], 0),
                        safe_int(row['Dég. M'], 0),
                        safe_int(row['Parade '], 0),  # Note l'espace dans "Parade "
                        safe_int(row['Sort'], 0),
                        safe_int(row['Santé'], 0)
                    ])
                except Exception as e:
                    print(f"⚠️ Erreur équipement ligne {_}: {e} - Données: {dict(row)}")
                    continue
            
            # === SAUVEGARDE CSV ===
            print("💾 Sauvegarde des fichiers CSV...")
            
            # Heroes CSV
            heroes_df_csv = pd.DataFrame(heroes_csv_data, 
                                       columns=["Code", "Nom", "Precision", "Damage", "Spells", "Health"])
            heroes_path = os.path.join(self.data_path, "heroes.csv")
            heroes_df_csv.to_csv(heroes_path, index=False)
            print(f"✅ {heroes_path} créé avec {len(heroes_csv_data)} héros")
            
            # Enemies CSV
            enemies_df_csv = pd.DataFrame(enemies_csv_data, columns=[
                "Code", "Nom", "Defense", "Damage_2J", "Health_2J", "Defense_2J",
                "Damage_3J", "Health_3J", "Defense_3J", "Damage_4J", "Health_4J", "Defense_4J",
                "Is_Magical", "Has_Magical_Damage"
            ])
            enemies_path = os.path.join(self.data_path, "enemies.csv")
            enemies_df_csv.to_csv(enemies_path, index=False)
            print(f"✅ {enemies_path} créé avec {len(enemies_csv_data)} ennemis")
            
            # Equipment CSV AVEC TYPE
            equipment_df_csv = pd.DataFrame(equipment_csv_data, columns=[
                "Code", "Nom", "Type", "Precision", "Physical_Damage", "Magical_Damage", "Defense", "Spells", "Health"  # AJOUT Type
            ])
            equipment_path = os.path.join(self.data_path, "equipment.csv")
            equipment_df_csv.to_csv(equipment_path, index=False)
            print(f"✅ {equipment_path} créé avec {len(equipment_csv_data)} équipements")
            
            print(f"\n🎯 Import Excel terminé avec succès !")
            return True
            
        except FileNotFoundError:
            print(f"❌ Fichier {excel_path} non trouvé")
            return False
            
        except Exception as e:
            print(f"❌ Erreur lors de l'import Excel: {e}")
            print(f"💡 Vérifiez que openpyxl est installé (pip install openpyxl)")
            return False
    
    def create_csv_files(self):
        """Crée les fichiers CSV - essaie Excel en premier, sinon données par défaut"""
        
        print("🔄 Création des fichiers de données...")
        
        # Liste des emplacements possibles pour le fichier Excel
        possible_excel_paths = [
            "Data_cards.xlsx",  # Racine
            "data/Data_cards.xlsx",  # Dans le dossier data
            "data_cards.xlsx",  # Racine avec nom différent
            "data/data_cards.xlsx"  # Dans data avec nom différent
        ]
        
        excel_file = None
        for filepath in possible_excel_paths:
            if os.path.exists(filepath):
                excel_file = filepath
                break
        
        if excel_file:
            print(f"📁 {excel_file} détecté, import en cours...")
            if self.import_from_excel(excel_file):
                print("✅ Import Excel réussi - toutes les données sont disponibles !")
                return
            else:
                print("⚠️ Échec de l'import Excel, utilisation des données par défaut...")
        else:
            print("📁 Aucun fichier Excel trouvé, création des données par défaut...")
            print(f"💡 Emplacements recherchés : {', '.join(possible_excel_paths)}")
        
        # Fallback : Création des données par défaut (échantillon de test)
        self._create_fallback_data()
    
    def _create_fallback_data(self):
        """Crée des données par défaut si Excel n'est pas disponible"""
        
        print("🔄 Création des données par défaut...")
        
        # === HEROES CSV (Échantillon) ===
        heroes_data = [
            ["P-1", "Elneha", 6, 2, 3, 5],
            ["P-2", "Liarie", 0, 0, 10, 6],
            ["P-3", "Atucan", 3, 2, 2, 9],
            ["P-4", "Kraor", 5, 3, 0, 8],
            ["P-5", "Thordius", 3, 3, 0, 10],
            ["P-6", "Stèphe", 5, 2, 2, 7],
            ["P-7", "Lame", 5, 3, 0, 8],
            ["P-8", "Raishi", 6, 2, 0, 8]
        ]
        
        heroes_df = pd.DataFrame(heroes_data, columns=["Code", "Nom", "Precision", "Damage", "Spells", "Health"])
        heroes_path = os.path.join(self.data_path, "heroes.csv")
        heroes_df.to_csv(heroes_path, index=False)
        print(f"✅ {heroes_path} créé avec {len(heroes_data)} héros (échantillon)")
        
        # === ENEMIES CSV (Échantillon) ===
        enemies_data = [
            ["E-1", "Okkoto 1", 10, 1, 8, 0, 2, 10, 1, 2, 12, 2, False, False],
            ["E-2", "Okkoto 2", 12, 1, 9, 0, 2, 11, 1, 2, 13, 2, False, False],
            ["E-3", "Ecureuil infesté 1", 10, 1, 3, 0, 2, 6, 0, 2, 10, 1, False, False],
            ["E-7", "Ours géant", 12, 3, 10, 1, 2, 15, 3, 4, 20, 2, False, False],
            ["E-34", "Dragon azur", 16, 5, 65, 1, 6, 80, 2, 7, 99, 3, True, False],
            ["E-46", "Troll", 14, 5, 30, 2, 6, 35, 3, 7, 40, 4, False, False]
        ]
        
        enemies_df = pd.DataFrame(enemies_data, columns=[
            "Code", "Nom", "Defense", "Damage_2J", "Health_2J", "Defense_2J",
            "Damage_3J", "Health_3J", "Defense_3J", "Damage_4J", "Health_4J", "Defense_4J",
            "Is_Magical", "Has_Magical_Damage"
        ])
        enemies_path = os.path.join(self.data_path, "enemies.csv")
        enemies_df.to_csv(enemies_path, index=False)
        print(f"✅ {enemies_path} créé avec {len(enemies_data)} ennemis (échantillon)")
        
        # === EQUIPMENT CSV (Échantillon AVEC TYPE) ===
        equipment_data = [
            ["O-5", "Dague", "arme", 2, 1, 0, 0, 0, 0],
            ["O-7", "Epée longue", "arme", 2, 2, 0, 0, 0, 0],
            ["O-11", "Arc long", "arme", 3, 2, 0, 0, 0, 0],
            ["O-23", "Hache de guerre", "arme", 2, 3, 0, 0, 0, 0],
            ["O-31", "Bouclier de fer", "armure", 0, 0, 0, 2, 0, 0],
            ["O-32", "Vêtement de cuir", "armure", 0, 0, 0, 1, 0, 0],
            ["O-38", "Gants de précision", "accessoire", 4, 0, 0, 0, 0, 0],
            ["O-42", "Pierre de mémoire", "accessoire", 0, 0, 0, 0, 2, 0],
            ["O-75", "Implacable", "arme", 0, 6, 0, 0, 0, 0],
            ["O-83", "Epée d'Olestrin", "arme", 3, 3, 0, 0, 0, 0]
        ]
        
        equipment_df = pd.DataFrame(equipment_data, columns=[
            "Code", "Nom", "Type", "Precision", "Physical_Damage", "Magical_Damage", "Defense", "Spells", "Health"
        ])
        equipment_path = os.path.join(self.data_path, "equipment.csv")
        equipment_df.to_csv(equipment_path, index=False)
        print(f"✅ {equipment_path} créé avec {len(equipment_data)} équipements (échantillon)")
        
        print(f"\n💡 Données par défaut créées. Pour avoir toutes les données :")
        print(f"   1. Placez Data_cards.xlsx dans le dossier racine")
        print(f"   2. Installez openpyxl : pip install openpyxl")
        print(f"   3. Relancez l'application")
    
    def _create_default_heroes(self) -> List[Character]:
        """Crée des héros par défaut si le CSV n'existe pas"""
        heroes_data = [
            {"code": "P-1", "name": "Elneha", "precision": 6, "damage": 2, "spells": 3, "health": 5},
            {"code": "P-2", "name": "Liarie", "precision": 0, "damage": 0, "spells": 10, "health": 6},
            {"code": "P-3", "name": "Atucan", "precision": 3, "damage": 2, "spells": 2, "health": 9},
            {"code": "P-4", "name": "Kraor", "precision": 5, "damage": 3, "spells": 0, "health": 8}
        ]
        return [Character(**hero_data) for hero_data in heroes_data]
    
    def _create_default_enemies(self) -> List[Enemy]:
        """Crée des ennemis par défaut si le CSV n'existe pas"""
        enemies_data = [
            {
                "code": "E-1", "name": "Okkoto 1", "defense": 10,
                "stats_by_players": {
                    2: {"damage": 1, "health": 8, "defense": 0},
                    3: {"damage": 2, "health": 10, "defense": 1}, 
                    4: {"damage": 2, "health": 12, "defense": 2}
                }
            }
        ]
        return [Enemy(**enemy_data) for enemy_data in enemies_data]
    
    def _create_default_equipment(self) -> List[Equipment]:
        """Crée des équipements par défaut si le CSV n'existe pas"""
        equipment_data = [
            {"code": "O-5", "name": "Dague", "type": "arme", "precision": 2, "physical_damage": 1, "magical_damage": 0, "defense": 0, "spells": 0, "health": 0}
        ]
        return [Equipment(**eq_data) for eq_data in equipment_data]