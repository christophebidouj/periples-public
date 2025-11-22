# ability_registry
"""
Registre central des capacités individuelles
Système de gestion des 48 capacités (8 héros × 6 capacités)
"""

from typing import Dict, Type, Optional, List
from .base_ability import BaseAbility

class AbilityRegistry:
    """Registre central pour toutes les capacités individuelles"""
    
    def __init__(self):
        """Initialise le registre vide"""
        self._abilities: Dict[str, Type[BaseAbility]] = {}
        self._instances_cache: Dict[str, BaseAbility] = {}
        
    def register(self, ability_class: Type[BaseAbility]):
        """
        Enregistre une classe de capacité dans le registre
        
        Args:
            ability_class: Classe héritant de BaseAbility
        """
        if not issubclass(ability_class, BaseAbility):
            raise ValueError(f"La classe {ability_class.__name__} doit hériter de BaseAbility")
            
        # Vérifier que la classe a les attributs requis
        required_attrs = ['hero_code', 'ability_number', 'name', 'description']
        for attr in required_attrs:
            if not hasattr(ability_class, attr):
                raise ValueError(f"La classe {ability_class.__name__} doit avoir l'attribut {attr}")
        
        key = f"{ability_class.hero_code}_{ability_class.ability_number}"
        self._abilities[key] = ability_class
        
        # Nettoyer le cache pour cette capacité
        if key in self._instances_cache:
            del self._instances_cache[key]
    
    def get_ability_class(self, hero_code: str, ability_number: int) -> Optional[Type[BaseAbility]]:
        """
        Récupère une classe de capacité par code héros et numéro
        
        Args:
            hero_code: Code du héros (P-1, P-2, etc.)
            ability_number: Numéro de capacité (1-6)
            
        Returns:
            Type[BaseAbility] ou None si non trouvée
        """
        key = f"{hero_code}_{ability_number}"
        return self._abilities.get(key)
    
    def get_ability_instance(self, hero_code: str, ability_number: int) -> Optional[BaseAbility]:
        """
        Récupère une instance de capacité (avec cache)
        
        Args:
            hero_code: Code du héros (P-1, P-2, etc.)
            ability_number: Numéro de capacité (1-6)
            
        Returns:
            BaseAbility ou None si non trouvée
        """
        key = f"{hero_code}_{ability_number}"
        
        # Vérifier le cache d'abord
        if key in self._instances_cache:
            return self._instances_cache[key]
            
        # Créer une nouvelle instance
        ability_class = self._abilities.get(key)
        if ability_class:
            try:
                instance = ability_class()
                self._instances_cache[key] = instance
                return instance
            except Exception as e:
                print(f"❌ Erreur création instance {key}: {e}")
                return None
        
        return None
    
    def get_hero_abilities(self, hero_code: str) -> List[BaseAbility]:
        """
        Récupère toutes les capacités d'un héros

        Args:
            hero_code: Code du héros (P-1, P-2, etc.)

        Returns:
            Liste des instances de capacités du héros
        """
        abilities = []

        # Capacités normales (1-6)
        for ability_number in range(1, 7):
            ability = self.get_ability_instance(hero_code, ability_number)
            if ability:
                abilities.append(ability)

        # NOUVEAU - Elneha capacités exclusives formes (101, 102)
        if hero_code == "P-1":
            for ability_number in [101, 102]:
                ability = self.get_ability_instance(hero_code, ability_number)
                if ability:
                    abilities.append(ability)

        return abilities
    
    def get_all_abilities(self) -> Dict[str, BaseAbility]:
        """
        Récupère toutes les capacités enregistrées
        
        Returns:
            Dict avec clé "hero_code_ability_number" et valeur instance
        """
        all_abilities = {}
        for key in self._abilities.keys():
            hero_code, ability_number = key.split('_')
            ability_number = int(ability_number)
            
            instance = self.get_ability_instance(hero_code, ability_number)
            if instance:
                all_abilities[key] = instance
                
        return all_abilities
    
    def get_registered_count(self) -> int:
        """
        Retourne le nombre de capacités enregistrées
        
        Returns:
            int: Nombre total de capacités
        """
        return len(self._abilities)
    
    def get_heroes_with_abilities(self) -> List[str]:
        """
        Retourne la liste des codes héros ayant des capacités enregistrées
        
        Returns:
            List[str]: Liste des codes héros
        """
        heroes = set()
        for key in self._abilities.keys():
            hero_code, _ = key.split('_')
            heroes.add(hero_code)
        return sorted(list(heroes))
    
    def is_registered(self, hero_code: str, ability_number: int) -> bool:
        """
        Vérifie si une capacité est enregistrée
        
        Args:
            hero_code: Code du héros
            ability_number: Numéro de capacité
            
        Returns:
            bool: True si la capacité existe
        """
        key = f"{hero_code}_{ability_number}"
        return key in self._abilities
    
    def unregister(self, hero_code: str, ability_number: int) -> bool:
        """
        Supprime une capacité du registre
        
        Args:
            hero_code: Code du héros
            ability_number: Numéro de capacité
            
        Returns:
            bool: True si supprimée, False si n'existait pas
        """
        key = f"{hero_code}_{ability_number}"
        
        removed = False
        if key in self._abilities:
            del self._abilities[key]
            removed = True
            
        if key in self._instances_cache:
            del self._instances_cache[key]
            
        return removed
    
    def clear(self):
        """Vide complètement le registre"""
        self._abilities.clear()
        self._instances_cache.clear()
    
    def get_debug_info(self) -> Dict:
        """
        Retourne des informations de debug sur le registre
        
        Returns:
            Dict: Informations détaillées sur l'état du registre
        """
        info = {
            'total_registered': len(self._abilities),
            'cached_instances': len(self._instances_cache),
            'heroes': {},
            'missing_abilities': []
        }
        
        # Analyser par héros
        for hero_code in ['P-1', 'P-2', 'P-3', 'P-4', 'P-5', 'P-6', 'P-7', 'P-8']:
            hero_abilities = []
            missing_abilities = []
            
            for ability_num in range(1, 7):
                key = f"{hero_code}_{ability_num}"
                if key in self._abilities:
                    ability_class = self._abilities[key]
                    hero_abilities.append({
                        'number': ability_num,
                        'name': getattr(ability_class, 'name', 'Unknown'),
                        'class': ability_class.__name__
                    })
                else:
                    missing_abilities.append(ability_num)
            
            info['heroes'][hero_code] = {
                'registered': len(hero_abilities),
                'abilities': hero_abilities,
                'missing': missing_abilities
            }
            
            # Ajouter aux capacités manquantes globales
            for missing_num in missing_abilities:
                info['missing_abilities'].append(f"{hero_code}_{missing_num}")
        
        return info
    
    def print_debug_info(self):
        """Affiche les informations de debug du registre"""
        info = self.get_debug_info()
        
        print("🔍 DEBUG - État du registre des capacités")
        print("=" * 50)
        print(f"📊 Total enregistré: {info['total_registered']}/48")
        print(f"💾 Instances en cache: {info['cached_instances']}")
        print()
        
        for hero_code, hero_info in info['heroes'].items():
            print(f"🎭 {hero_code}: {hero_info['registered']}/6 capacités")
            
            if hero_info['abilities']:
                for ability in hero_info['abilities']:
                    print(f"   ✅ {ability['number']}: {ability['name']} ({ability['class']})")
            
            if hero_info['missing']:
                missing_str = ', '.join(map(str, hero_info['missing']))
                print(f"   ❌ Manquantes: {missing_str}")
            print()
        
        if info['missing_abilities']:
            print(f"🚨 Capacités manquantes globales: {len(info['missing_abilities'])}")
            for missing in info['missing_abilities']:
                print(f"   - {missing}")

# Instance globale du registre
ABILITY_REGISTRY = AbilityRegistry()

# Fonction utilitaire pour décorateur
def register_ability(ability_class: Type[BaseAbility]):
    """
    Décorateur pour auto-enregistrer une capacité
    
    Args:
        ability_class: Classe de capacité à enregistrer
        
    Returns:
        La classe non modifiée (mais enregistrée)
    """
    ABILITY_REGISTRY.register(ability_class)
    return ability_class