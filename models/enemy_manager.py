"""
EnemyManager - Gestion des ennemis personnalisés
VERSION 1.0 - Séparation Business Logic / UI

Responsabilités :
- CRUD des ennemis personnalisés (CE-X)
- Protection des ennemis officiels (E-X)
- Validation des données
- Génération automatique des codes

IMPORTANT : Ce module ne contient AUCUNE référence à Streamlit
"""

import pandas as pd
import os
from typing import List, Dict, Optional, Tuple
from models.character import Enemy


class EnemyManager:
    """Gestionnaire CRUD pour les ennemis personnalisés"""

    def __init__(self, csv_path: str = "data/custom_enemies.csv"):
        """
        Initialise le gestionnaire

        Args:
            csv_path: Chemin vers le CSV des ennemis personnalisés
        """
        self.csv_path = csv_path
        self._ensure_csv_exists()

    # === LECTURE ===

    def load_custom_enemies(self) -> List[Enemy]:
        """
        Charge tous les ennemis personnalisés depuis le CSV

        Returns:
            Liste des ennemis personnalisés (CE-X)
        """
        if not os.path.exists(self.csv_path):
            return []

        try:
            df = pd.read_csv(self.csv_path)

            if df.empty:
                return []

            enemies = []
            for _, row in df.iterrows():
                enemy = self._create_enemy_from_row(row)
                if enemy:
                    enemies.append(enemy)

            # Charger les capacités pour les ennemis avec ability_codes
            self._load_abilities_for_enemies(enemies)

            return enemies

        except Exception as e:
            print(f"❌ Erreur chargement ennemis personnalisés: {e}")
            return []

    def get_enemy_by_code(self, code: str) -> Optional[Enemy]:
        """
        Récupère un ennemi par son code

        Args:
            code: Code de l'ennemi (ex: CE-1)

        Returns:
            Enemy ou None si non trouvé
        """
        enemies = self.load_custom_enemies()
        return next((e for e in enemies if e.code == code), None)

    # === CRÉATION ===

    def create_enemy(self, data: Dict) -> Tuple[bool, str, Optional[Enemy]]:
        """
        Crée un nouvel ennemi personnalisé

        Args:
            data: Dictionnaire avec les données de l'ennemi
                {
                    'name': str,
                    'defense': int,
                    'damage_2j': int, 'health_2j': int, 'defense_2j': int,
                    'damage_3j': int, 'health_3j': int, 'defense_3j': int,
                    'damage_4j': int, 'health_4j': int, 'defense_4j': int,
                    'is_magical': bool,
                    'has_magical_damage': bool
                }

        Returns:
            Tuple (success: bool, message: str, enemy: Optional[Enemy])
        """
        # Validation
        is_valid, error_msg = self.validate_enemy_data(data)
        if not is_valid:
            return False, error_msg, None

        # Génération du code
        code = self.get_next_code()

        # Création de l'ennemi
        try:
            enemy = self._create_enemy_from_dict(code, data)

            # Sauvegarde
            enemies = self.load_custom_enemies()
            enemies.append(enemy)
            self._save_enemies_to_csv(enemies)

            return True, f"✅ Ennemi {code} - {data['name']} créé avec succès", enemy

        except Exception as e:
            return False, f"❌ Erreur création: {str(e)}", None

    # === MISE À JOUR ===

    def update_enemy(self, code: str, data: Dict) -> Tuple[bool, str]:
        """
        Met à jour un ennemi personnalisé

        Args:
            code: Code de l'ennemi à modifier (ex: CE-1)
            data: Nouvelles données (même structure que create_enemy)

        Returns:
            Tuple (success: bool, message: str)
        """
        # Protection ennemis officiels
        if self.is_official_enemy(code):
            return False, "❌ Impossible de modifier un ennemi officiel (E-X)"

        # Validation
        is_valid, error_msg = self.validate_enemy_data(data)
        if not is_valid:
            return False, error_msg

        # Chargement
        enemies = self.load_custom_enemies()

        # Recherche de l'ennemi
        enemy_index = next((i for i, e in enumerate(enemies) if e.code == code), None)
        if enemy_index is None:
            return False, f"❌ Ennemi {code} non trouvé"

        # Mise à jour
        try:
            updated_enemy = self._create_enemy_from_dict(code, data)
            enemies[enemy_index] = updated_enemy

            # Sauvegarde
            self._save_enemies_to_csv(enemies)

            return True, f"✅ Ennemi {code} - {data['name']} mis à jour avec succès"

        except Exception as e:
            return False, f"❌ Erreur mise à jour: {str(e)}"

    # === SUPPRESSION ===

    def delete_enemy(self, code: str) -> Tuple[bool, str]:
        """
        Supprime un ennemi personnalisé

        Args:
            code: Code de l'ennemi à supprimer (ex: CE-1)

        Returns:
            Tuple (success: bool, message: str)
        """
        # Protection ennemis officiels
        if self.is_official_enemy(code):
            return False, "❌ Impossible de supprimer un ennemi officiel (E-X)"

        # Chargement
        enemies = self.load_custom_enemies()

        # Recherche de l'ennemi
        enemy = next((e for e in enemies if e.code == code), None)
        if not enemy:
            return False, f"❌ Ennemi {code} non trouvé"

        # Suppression
        try:
            enemies = [e for e in enemies if e.code != code]
            self._save_enemies_to_csv(enemies)

            return True, f"✅ Ennemi {code} - {enemy.name} supprimé avec succès"

        except Exception as e:
            return False, f"❌ Erreur suppression: {str(e)}"

    # === GÉNÉRATION DE CODE ===

    def get_next_code(self) -> str:
        """
        Génère le prochain code CE-X disponible
        Réutilise les codes supprimés (comble les trous) avant d'incrémenter

        Returns:
            Code au format CE-X (ex: CE-1, CE-2, CE-15)
        """
        enemies = self.load_custom_enemies()

        if not enemies:
            return "CE-1"

        # Extraire les numéros des codes CE-X
        numbers = []
        for enemy in enemies:
            if enemy.code.startswith("CE-"):
                try:
                    num = int(enemy.code.split("-")[1])
                    numbers.append(num)
                except (IndexError, ValueError):
                    continue

        if not numbers:
            return "CE-1"

        # Trier les numéros
        numbers.sort()

        # Chercher le premier trou dans la séquence (code supprimé à réutiliser)
        for i in range(1, numbers[-1] + 1):
            if i not in numbers:
                return f"CE-{i}"

        # Aucun trou trouvé, utiliser le max + 1
        return f"CE-{numbers[-1] + 1}"

    # === VALIDATION ===

    def validate_enemy_data(self, data: Dict) -> Tuple[bool, str]:
        """
        Valide les données d'un ennemi

        Args:
            data: Dictionnaire avec les données à valider

        Returns:
            Tuple (is_valid: bool, error_message: str)
        """
        # Nom obligatoire
        if not data.get('name', '').strip():
            return False, "❌ Le nom de l'ennemi est obligatoire"

        # Defense doit être un entier positif
        try:
            defense = int(data.get('defense', 0))
            if defense < 0:
                return False, "❌ La Defense doit être positive"
            if defense > 20:
                return False, "⚠️ Defense > 20 est inhabituelle (max recommandé: 20)"
        except (TypeError, ValueError):
            return False, "❌ La Defense doit être un nombre entier"

        # Validation des stats pour chaque nombre de joueurs
        for player_count in [2, 3, 4]:
            prefix = f"{player_count}j"

            # Dégâts
            try:
                damage = int(data.get(f'damage_{prefix}', 0))
                if damage < 0:
                    return False, f"❌ Les dégâts ({player_count}J) doivent être positifs"
                if damage > 10:
                    return False, f"⚠️ Dégâts > 10 ({player_count}J) est inhabituel"
            except (TypeError, ValueError):
                return False, f"❌ Les dégâts ({player_count}J) doivent être un nombre entier"

            # Santé
            try:
                health = int(data.get(f'health_{prefix}', 1))
                if health <= 0:
                    return False, f"❌ La santé ({player_count}J) doit être > 0"
                if health > 100:
                    return False, f"⚠️ Santé > 100 ({player_count}J) est inhabituelle"
            except (TypeError, ValueError):
                return False, f"❌ La santé ({player_count}J) doit être un nombre entier"

            # Defense (parade)
            try:
                def_stat = int(data.get(f'defense_{prefix}', 0))
                if def_stat < 0:
                    return False, f"❌ La parade ({player_count}J) doit être positive"
                if def_stat > 10:
                    return False, f"⚠️ Parade > 10 ({player_count}J) est inhabituelle"
            except (TypeError, ValueError):
                return False, f"❌ La parade ({player_count}J) doit être un nombre entier"

        return True, ""

    # === UTILITAIRES ===

    @staticmethod
    def is_official_enemy(code: str) -> bool:
        """
        Vérifie si un code correspond à un ennemi officiel

        Args:
            code: Code de l'ennemi (ex: E-1, CE-2)

        Returns:
            True si ennemi officiel (E-X), False sinon
        """
        if not code or not isinstance(code, str):
            return False

        # Format E-X où X est un nombre
        if code.startswith("E-"):
            try:
                num = code.split("-")[1]
                return num.isdigit()
            except IndexError:
                return False

        return False

    # === MÉTHODES PRIVÉES ===

    def _ensure_csv_exists(self):
        """Crée le fichier CSV s'il n'existe pas"""
        if not os.path.exists(self.csv_path):
            # Créer le dossier data si nécessaire
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)

            # Créer un CSV vide avec les en-têtes
            df = pd.DataFrame(columns=[
                'Code', 'Nom', 'Defense',
                'Damage_2J', 'Health_2J', 'Defense_2J',
                'Damage_3J', 'Health_3J', 'Defense_3J',
                'Damage_4J', 'Health_4J', 'Defense_4J',
                'Is_Magical', 'Has_Magical_Damage',
                'Abilities'
            ])
            df.to_csv(self.csv_path, index=False)
            print(f"✅ Fichier {self.csv_path} créé")

    def _create_enemy_from_row(self, row) -> Optional[Enemy]:
        """Crée un Enemy depuis une ligne CSV"""
        try:
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

            # Parser la colonne Abilities (codes séparés par virgules)
            ability_codes = []
            abilities_str = row.get('Abilities', '')
            if pd.notna(abilities_str) and str(abilities_str).strip():
                ability_codes = [code.strip() for code in str(abilities_str).split(',') if code.strip()]

            enemy = Enemy(
                code=str(row['Code']),
                name=str(row['Nom']).capitalize(),
                defense=int(row['Defense']),
                stats_by_players=stats_by_players,
                is_magical=bool(row.get('Is_Magical', False)),
                has_magical_damage=bool(row.get('Has_Magical_Damage', False)),
                is_custom=True  # Marquer comme ennemi personnalisé
            )

            # Stocker les codes de capacités pour que DataLoader les charge
            enemy.ability_codes = ability_codes

            return enemy
        except Exception as e:
            print(f"⚠️ Erreur création ennemi depuis row: {e}")
            return None

    def _create_enemy_from_dict(self, code: str, data: Dict) -> Enemy:
        """Crée un Enemy depuis un dictionnaire de données"""
        stats_by_players = {
            2: {
                'damage': int(data['damage_2j']),
                'health': int(data['health_2j']),
                'defense': int(data['defense_2j'])
            },
            3: {
                'damage': int(data['damage_3j']),
                'health': int(data['health_3j']),
                'defense': int(data['defense_3j'])
            },
            4: {
                'damage': int(data['damage_4j']),
                'health': int(data['health_4j']),
                'defense': int(data['defense_4j'])
            }
        }

        enemy = Enemy(
            code=code,
            name=data['name'].strip().capitalize(),
            defense=int(data['defense']),
            stats_by_players=stats_by_players,
            is_magical=bool(data.get('is_magical', False)),
            has_magical_damage=bool(data.get('has_magical_damage', False)),
            is_custom=True  # Marquer comme ennemi personnalisé
        )

        # Stocker les codes de capacités si fournis
        if 'abilities' in data and data['abilities']:
            enemy.ability_codes = data['abilities']  # Liste de codes ['EA-1', 'EA-3']
        else:
            enemy.ability_codes = []

        return enemy

    def _save_enemies_to_csv(self, enemies: List[Enemy]):
        """Sauvegarde la liste des ennemis dans le CSV"""
        data = []

        for enemy in enemies:
            # Extraire les codes de capacités
            ability_codes = []
            if hasattr(enemy, 'abilities') and enemy.abilities:
                # Si l'ennemi a des objets EnemyAbility complets
                ability_codes = [ability.code for ability in enemy.abilities]
            elif hasattr(enemy, 'ability_codes') and enemy.ability_codes:
                # Si l'ennemi a juste les codes (cas intermédiaire)
                ability_codes = enemy.ability_codes

            row = {
                'Code': enemy.code,
                'Nom': enemy.name,
                'Defense': enemy.defense,
                'Damage_2J': enemy.stats_by_players[2]['damage'],
                'Health_2J': enemy.stats_by_players[2]['health'],
                'Defense_2J': enemy.stats_by_players[2]['defense'],
                'Damage_3J': enemy.stats_by_players[3]['damage'],
                'Health_3J': enemy.stats_by_players[3]['health'],
                'Defense_3J': enemy.stats_by_players[3]['defense'],
                'Damage_4J': enemy.stats_by_players[4]['damage'],
                'Health_4J': enemy.stats_by_players[4]['health'],
                'Defense_4J': enemy.stats_by_players[4]['defense'],
                'Is_Magical': enemy.is_magical,
                'Has_Magical_Damage': enemy.has_magical_damage,
                'Abilities': ','.join(ability_codes) if ability_codes else ''
            }
            data.append(row)

        df = pd.DataFrame(data)
        df.to_csv(self.csv_path, index=False)

    def _load_abilities_for_enemies(self, enemies: List[Enemy]):
        """
        Charge les objets EnemyAbility pour chaque ennemi ayant des ability_codes

        Args:
            enemies: Liste d'ennemis à enrichir avec les capacités
        """
        try:
            # Vérifier si le module enemy_ability est disponible
            from models.enemy_ability import EnemyAbility

            # Charger les données des capacités depuis le CSV
            abilities_csv_path = "data/enemy_abilities.csv"
            if not os.path.exists(abilities_csv_path):
                return

            df_abilities = pd.read_csv(abilities_csv_path)
            if df_abilities.empty:
                return

            # Créer un dictionnaire de lookup code -> EnemyAbility
            ability_lookup = {}
            for _, row in df_abilities.iterrows():
                try:
                    # Parse triggers (séparés par virgule)
                    triggers_str = str(row.get('triggers', ''))
                    triggers = [t.strip() for t in triggers_str.split(',') if t.strip()]

                    # Parse effects (séparés par virgule)
                    effects_str = str(row.get('effects', ''))
                    effects = [e.strip() for e in effects_str.split(',') if e.strip()]

                    # Parse parameters (format: key:value,key:value)
                    parameters_str = str(row.get('parameters', ''))
                    parameters = {}
                    if parameters_str and parameters_str != 'nan':
                        for param in parameters_str.split(','):
                            if ':' in param:
                                key, value = param.split(':', 1)
                                # Essayer de convertir en int si possible
                                try:
                                    parameters[key.strip()] = int(value.strip())
                                except ValueError:
                                    parameters[key.strip()] = value.strip()

                    ability = EnemyAbility(
                        code=str(row['code']),
                        name=str(row['name']),
                        description=str(row['description']),
                        triggers=triggers,
                        effects=effects,
                        parameters=parameters
                    )
                    ability_lookup[ability.code] = ability
                except Exception as e:
                    print(f"⚠️ Erreur création capacité {row.get('code', 'unknown')}: {e}")
                    continue

            # Attacher les capacités aux ennemis
            for enemy in enemies:
                if hasattr(enemy, 'ability_codes') and enemy.ability_codes:
                    enemy.abilities = []
                    for code in enemy.ability_codes:
                        if code in ability_lookup:
                            enemy.abilities.append(ability_lookup[code])
                        else:
                            print(f"⚠️ Capacité {code} non trouvée pour {enemy.code}")

        except ImportError:
            # Module enemy_ability non disponible, on skip silencieusement
            pass
        except Exception as e:
            print(f"⚠️ Erreur chargement capacités: {e}")
