"""
Chargeur de capacités pour le Simulateur Périples
Import et parsing du fichier Sorts.xlsx selon les règles officielles
"""

import pandas as pd
import os
import re
from typing import List, Dict, Optional, Tuple
from models.abilities import Ability, AbilityEffect, TargetType

class AbilitiesLoader:
    """
    Chargeur des capacités depuis le fichier Sorts.xlsx
    
    Structure Excel attendue :
    - Colonne 1 : Nom héros + numéro (ex: "Elneha1", "Liarie2")
    - Colonne 2 : Coût en sorts (0 = physique, 1+ = magique)
    - Colonne 3 : Description détaillée
    - Colonne 4 : Utilisations par combat (optionnel)
    """
    
    def __init__(self, excel_path: str = "Sorts.xlsx"):
        self.excel_path = excel_path
        
        # Mapping des noms de héros vers leurs codes
        self.hero_name_to_code = {
            'elneha': 'P-1',
            'liarie': 'P-2', 
            'atucan': 'P-3',
            'kraor': 'P-4',
            'thordius': 'P-5',
            'stephe': 'P-6',
            'stèphe': 'P-6',  # Variante avec accent
            'lame': 'P-7',
            'raishi': 'P-8',
            'ours': 'P-9',     # Héros étendus si présents
            'loup': 'P-10',
            'ours s': 'P-11',
            'loup s': 'P-12'
        }
    
    def load_abilities_from_excel(self) -> Dict[str, List[Ability]]:
        """
        Charge toutes les capacités depuis le fichier Excel
        
        Returns:
            Dict[str, List[Ability]]: Capacités organisées par code de héros
        """
        if not os.path.exists(self.excel_path):
            print(f"❌ Fichier {self.excel_path} non trouvé")
            return self._create_fallback_abilities()
        
        try:
            print(f"📖 Lecture du fichier {self.excel_path}...")
            df = pd.read_excel(self.excel_path)
            
            abilities_by_hero = {}
            success_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    ability = self._parse_ability_row(row, index + 1)
                    if ability:
                        hero_code = ability.hero_code
                        if hero_code not in abilities_by_hero:
                            abilities_by_hero[hero_code] = []
                        abilities_by_hero[hero_code].append(ability)
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    print(f"⚠️ Erreur ligne {index + 1}: {e}")
                    error_count += 1
                    continue
            
            # Tri des capacités par numéro pour chaque héros
            for hero_code in abilities_by_hero:
                abilities_by_hero[hero_code].sort(key=lambda a: a.ability_number)
            
            print(f"✅ Chargement terminé : {success_count} capacités, {error_count} erreurs")
            print(f"📊 Héros avec capacités : {list(abilities_by_hero.keys())}")
            
            return abilities_by_hero
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement du fichier Excel: {e}")
            print("💡 Vérifiez que openpyxl est installé (pip install openpyxl)")
            return self._create_fallback_abilities()
    
    def _parse_ability_row(self, row, line_number: int) -> Optional[Ability]:
        """
        Parse une ligne Excel en objet Ability
        
        Args:
            row: Ligne pandas
            line_number: Numéro de ligne pour debug
            
        Returns:
            Optional[Ability]: Capacité parsée ou None si erreur
        """
        try:
            # Vérification que la ligne a au moins 3 colonnes
            if len(row) < 3:
                print(f"⚠️ Ligne {line_number}: Pas assez de colonnes ({len(row)} < 3)")
                return None
            
            # === PARSING COLONNE 1: Nom + Numéro ===
            name_and_number = str(row.iloc[0]).strip()
            if pd.isna(row.iloc[0]) or not name_and_number:
                print(f"⚠️ Ligne {line_number}: Colonne 1 vide")
                return None
            
            hero_code, ability_number = self._extract_hero_and_number(name_and_number)
            
            # === PARSING COLONNE 2: Coût en sorts ===
            spell_cost = self._safe_int(row.iloc[1], 0)
            
            # === PARSING COLONNE 3: Description ===
            description = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
            if not description:
                print(f"⚠️ Ligne {line_number}: Description vide")
                description = f"Capacité {ability_number}"
            
            # === PARSING COLONNE 4: Utilisations par combat (optionnel) ===
            uses_per_combat = None
            if len(row) > 3 and pd.notna(row.iloc[3]):
                uses_per_combat = self._safe_int(row.iloc[3], None)
            
            # === EXTRACTION DES MÉTADONNÉES ===
            ability_name = self._extract_ability_name(description)
            effects = self._parse_effects_from_description(description)
            target_type = self._determine_target_type(description)
            
            # === CRÉATION DE L'OBJET ABILITY ===
            ability = Ability(
                hero_code=hero_code,
                ability_number=ability_number,
                name=ability_name,
                spell_cost=spell_cost,
                description=description,
                uses_per_combat=uses_per_combat,
                effects=effects,
                target_type=target_type
            )
            
            return ability
            
        except Exception as e:
            print(f"⚠️ Erreur parsing ligne {line_number}: {e}")
            return None
    
    def _extract_hero_and_number(self, name_and_number: str) -> Tuple[str, int]:
        """
        Extrait le code héros et le numéro depuis une chaîne comme 'Elneha1' ou 'Liarie 2'
        
        Args:
            name_and_number: Chaîne contenant nom + numéro
            
        Returns:
            Tuple[str, int]: (code_hero, numero_capacite)
            
        Raises:
            ValueError: Si le parsing échoue
        """
        # Nettoyage de la chaîne
        cleaned = name_and_number.strip().lower()
        
        # Extraction du nombre à la fin
        number_match = re.search(r'(\d+)$', cleaned)
        if not number_match:
            raise ValueError(f"Numéro de capacité non trouvé dans: '{name_and_number}'")
        
        ability_number = int(number_match.group(1))
        if not (1 <= ability_number <= 6):
            raise ValueError(f"Numéro de capacité invalide: {ability_number} (doit être 1-6)")
        
        # Extraction du nom du héros
        hero_name = re.sub(r'\d+$', '', cleaned).strip()
        hero_name = re.sub(r'\s+', ' ', hero_name)  # Normalise les espaces
        
        # Recherche du code correspondant
        hero_code = self.hero_name_to_code.get(hero_name)
        if not hero_code:
            # Tentative avec recherche partielle
            for name, code in self.hero_name_to_code.items():
                if name in hero_name or hero_name in name:
                    hero_code = code
                    break
            
            if not hero_code:
                available_names = list(self.hero_name_to_code.keys())
                raise ValueError(f"Héros non reconnu: '{hero_name}'. Noms disponibles: {available_names}")
        
        return hero_code, ability_number
    
    def _extract_ability_name(self, description: str) -> str:
        """
        Extrait le nom de la capacité depuis la description
        
        Args:
            description: Description complète de la capacité
            
        Returns:
            str: Nom de la capacité
        """
        if not description:
            return "Capacité"
        
        lines = description.split('\n')
        first_line = lines[0].strip()
        
        # Si la première ligne est courte et sans ':', c'est probablement le nom
        if len(first_line) <= 50 and ':' not in first_line and '.' not in first_line[:20]:
            return first_line
        
        # Cherche un motif "Nom:" au début
        name_match = re.match(r'^([^:]+):', first_line)
        if name_match:
            return name_match.group(1).strip()
        
        # Cherche des mots-clés indicateurs de noms
        for keyword in ['forme', 'métamorphose', 'invocation', 'sort', 'attaque', 'soin']:
            if keyword in first_line.lower():
                # Extrait jusqu'à 3 mots autour du mot-clé
                words = first_line.split()
                for i, word in enumerate(words):
                    if keyword in word.lower():
                        start = max(0, i-1)
                        end = min(len(words), i+3)
                        return ' '.join(words[start:end]).strip('.,!?')
        
        # Prend les 4 premiers mots en dernier recours
        words = first_line.split()[:4]
        name = ' '.join(words).strip('.,!?')
        
        return name if len(name) <= 30 else "Capacité"
    
    def _parse_effects_from_description(self, description: str) -> List[AbilityEffect]:
        """
        Parse les effets depuis la description textuelle
        
        Args:
            description: Description de la capacité
            
        Returns:
            List[AbilityEffect]: Liste des effets détectés
        """
        effects = []
        desc_lower = description.lower()
        
        # Détection des effets de soin
        heal_keywords = ['soigne', 'guérit', 'récupère', 'restaure', 'rend', 'vie']
        if any(keyword in desc_lower for keyword in heal_keywords):
            # Essaie d'extraire la valeur
            heal_value = self._extract_number_near_keywords(description, heal_keywords)
            effects.append(AbilityEffect(
                type="heal",
                value=heal_value,
                description="Effet de soin détecté"
            ))
        
        # Détection des effets de dégâts
        damage_keywords = ['dégâts', 'dégats', 'blesse', 'attaque', 'frappe', 'touche']
        if any(keyword in desc_lower for keyword in damage_keywords):
            damage_value = self._extract_number_near_keywords(description, damage_keywords)
            effects.append(AbilityEffect(
                type="damage",
                value=damage_value,
                description="Effet de dégâts détecté"
            ))
        
        # Détection des buffs
        buff_keywords = ['bonus', 'augmente', 'améliore', '+', 'renforce', 'boost']
        if any(keyword in desc_lower for keyword in buff_keywords):
            buff_value = self._extract_number_near_keywords(description, buff_keywords)
            effects.append(AbilityEffect(
                type="buff",
                value=buff_value,
                description="Effet de bonus détecté"
            ))
        
        # Détection des debuffs
        debuff_keywords = ['malus', 'réduit', 'diminue', '-', 'affaiblit', 'pénalité']
        if any(keyword in desc_lower for keyword in debuff_keywords):
            debuff_value = self._extract_number_near_keywords(description, debuff_keywords)
            effects.append(AbilityEffect(
                type="debuff",
                value=debuff_value,
                description="Effet de malus détecté"
            ))
        
        # Si aucun effet spécifique détecté, marquer comme spécial
        if not effects:
            effects.append(AbilityEffect(
                type="special",
                description="Effet spécial - voir description"
            ))
        
        return effects
    
    def _extract_number_near_keywords(self, text: str, keywords: List[str]) -> Optional[int]:
        """
        Extrait un nombre proche de mots-clés dans le texte
        
        Args:
            text: Texte à analyser
            keywords: Liste de mots-clés
            
        Returns:
            Optional[int]: Nombre trouvé ou None
        """
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword in text_lower:
                # Cherche des nombres autour du mot-clé
                keyword_pos = text_lower.find(keyword)
                
                # Examine 20 caractères avant et après
                start = max(0, keyword_pos - 20)
                end = min(len(text), keyword_pos + len(keyword) + 20)
                context = text[start:end]
                
                # Cherche tous les nombres dans le contexte
                numbers = re.findall(r'\d+', context)
                if numbers:
                    # Prend le premier nombre trouvé
                    return int(numbers[0])
        
        return None
    
    def _determine_target_type(self, description: str) -> TargetType:
        """
        Détermine le type de cible depuis la description
        
        Args:
            description: Description de la capacité
            
        Returns:
            TargetType: Type de ciblage déterminé
        """
        desc_lower = description.lower()
        
        # Détection ciblage allié(s)
        ally_keywords = ['allié', 'allies', 'équipe', 'compagnon', 'camarade']
        if any(keyword in desc_lower for keyword in ally_keywords):
            # Vérification si c'est tous les alliés
            if any(word in desc_lower for word in ['tous', 'toute', 'entière', 'groupe']):
                return TargetType.ALL_ALLIES
            return TargetType.ALLY
        
        # Détection ciblage ennemi(s)
        enemy_keywords = ['ennemi', 'ennemis', 'adversaire', 'monstre', 'cible']
        if any(keyword in desc_lower for keyword in enemy_keywords):
            # Vérification si c'est tous les ennemis
            if any(word in desc_lower for word in ['tous', 'toute', 'entier']):
                return TargetType.ALL_ENEMIES
            return TargetType.ENEMY
        
        # Détection ciblage libre
        any_keywords = ['choix', 'cible au choix', 'n\'importe', 'selon']
        if any(keyword in desc_lower for keyword in any_keywords):
            return TargetType.ANY
        
        # Par défaut, ciblage personnel
        return TargetType.SELF
    
    def _safe_int(self, value, default: Optional[int] = 0) -> Optional[int]:
        """
        Convertit une valeur en entier de manière sécurisée
        
        Args:
            value: Valeur à convertir
            default: Valeur par défaut si conversion impossible
            
        Returns:
            Optional[int]: Entier converti ou valeur par défaut
        """
        if pd.isna(value) or value == '' or value is None:
            return default
        
        try:
            # Tente d'abord une conversion directe
            return int(float(value))
        except (ValueError, TypeError):
            # Si échec, essaie d'extraire un nombre de la chaîne
            if isinstance(value, str):
                numbers = re.findall(r'\d+', str(value))
                if numbers:
                    return int(numbers[0])
            return default
    
    def _create_fallback_abilities(self) -> Dict[str, List[Ability]]:
        """
        Crée des capacités par défaut si le fichier Excel n'est pas disponible
        
        Returns:
            Dict[str, List[Ability]]: Capacités de test
        """
        print("🔄 Création de capacités par défaut pour les tests...")
        
        fallback_abilities = {
            'P-1': [  # Elneha
                Ability(
                    hero_code='P-1',
                    ability_number=1,
                    name='Métamorphose Ours',
                    spell_cost=2,
                    description='Se transforme en ours, gagne +2 dégâts et +1 parade',
                    effects=[AbilityEffect(type="buff", value=2, description="Bonus dégâts et parade")]
                ),
                Ability(
                    hero_code='P-1', 
                    ability_number=2,
                    name='Soin Naturel',
                    spell_cost=1,
                    description='Récupère 3 points de vie',
                    effects=[AbilityEffect(type="heal", value=3, description="Soin de 3 PV")]
                )
            ],
            'P-2': [  # Liarie
                Ability(
                    hero_code='P-2',
                    ability_number=1, 
                    name='Projectile Magique',
                    spell_cost=1,
                    description='Lance un projectile magique qui inflige 3 dégâts',
                    effects=[AbilityEffect(type="damage", value=3, description="Dégâts magiques")]
                )
            ]
        }
        
        print("✅ Capacités par défaut créées pour P-1 (Elneha) et P-2 (Liarie)")
        return fallback_abilities
    
    def validate_abilities_data(self, abilities_by_hero: Dict[str, List[Ability]]) -> bool:
        """
        Valide la cohérence des données de capacités chargées
        
        Args:
            abilities_by_hero: Données à valider
            
        Returns:
            bool: True si les données sont valides
        """
        issues = []
        
        for hero_code, abilities in abilities_by_hero.items():
            # Vérification du code héros
            if not hero_code.startswith('P-'):
                issues.append(f"Code héros invalide: {hero_code}")
                continue
            
            # Vérification du nombre de capacités
            if len(abilities) > 6:
                issues.append(f"{hero_code}: Trop de capacités ({len(abilities)} > 6)")
            
            # Vérification de l'unicité des numéros
            numbers = [a.ability_number for a in abilities]
            if len(set(numbers)) != len(numbers):
                issues.append(f"{hero_code}: Numéros de capacités dupliqués")
            
            # Vérification des coûts
            for ability in abilities:
                if ability.spell_cost < 0:
                    issues.append(f"{hero_code}: Coût négatif pour {ability.name}")
        
        if issues:
            print("⚠️ Problèmes détectés dans les données:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
        print("✅ Validation des données réussie")
        return True

# Fonction utilitaire pour intégration facile
def load_all_abilities(excel_path: str = "Sorts.xlsx") -> Dict[str, List[Ability]]:
    """
    Fonction utilitaire pour charger toutes les capacités
    
    Args:
        excel_path: Chemin vers le fichier Excel
        
    Returns:
        Dict[str, List[Ability]]: Capacités par héros
    """
    loader = AbilitiesLoader(excel_path)
    abilities = loader.load_abilities_from_excel()
    loader.validate_abilities_data(abilities)
    return abilities