"""
Gestionnaire d'initiative pour les combats
Extrait de sandbox_interface_v2.py pour séparer logique métier et UI
"""

import random
from typing import List, Dict, Any


class InitiativeManager:
    """Gestion de l'initiative selon les règles Périples"""

    @staticmethod
    def roll_initiative(combatants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Génère et trie les initiatives (D20) pour tous les combattants

        RÈGLE OFFICIELLE PÉRIPLES (page 26 du PDF):
        - Chaque combattant lance un dé à 20 faces
        - L'ordre de jeu est déterminé par ordre décroissant d'initiative
        - En cas d'égalité, les héros ont la priorité sur les ennemis

        Args:
            combatants: Liste de dictionnaires avec clés requises:
                - 'character': Instance de Character ou Enemy
                - 'faction': 'hero' ou 'enemy'
                - 'id': Identifiant unique
                La clé 'initiative' sera ajoutée

        Returns:
            Liste triée par initiative décroissante (même liste, modifiée in-place)

        Example:
            >>> combatants = [
            ...     {'character': hero1, 'faction': 'hero', 'id': 'hero_H-1'},
            ...     {'character': enemy1, 'faction': 'enemy', 'id': 'enemy_E-1-1'}
            ... ]
            >>> sorted_combatants = InitiativeManager.roll_initiative(combatants)
            >>> # combatants[0]['initiative'] existe maintenant
        """
        # Générer les jets d'initiative (D20)
        for combatant in combatants:
            roll = random.randint(1, 20)
            combatant['initiative'] = roll

        # Tri par initiative décroissante
        # En cas d'égalité : héros (faction='hero') avant ennemi (faction='enemy')
        combatants.sort(
            key=lambda x: (x['initiative'], 0 if x['faction'] == 'hero' else 1),
            reverse=True
        )

        return combatants

    @staticmethod
    def get_initiative_order_log(combatants: List[Dict[str, Any]]) -> List[str]:
        """
        Génère les messages de log pour l'ordre d'initiative

        Cette méthode sépare la génération des messages de leur affichage,
        permettant aux interfaces UI de formater comme elles le souhaitent.

        Args:
            combatants: Liste triée de combattants avec 'initiative' définie

        Returns:
            Liste de chaînes de caractères formatées pour le log

        Example:
            >>> log_lines = InitiativeManager.get_initiative_order_log(combatants)
            >>> # ['=== ORDRE D'INITIATIVE ===', '1. 🦸 Atucan: 18', '2. 👹 Gobelin: 12', ...]
        """
        log_lines = ["=== ORDRE D'INITIATIVE ==="]

        for i, combatant in enumerate(combatants, 1):
            name = combatant['character'].name
            initiative_value = combatant['initiative']
            faction_icon = "🦸" if combatant['faction'] == 'hero' else "👹"
            log_lines.append(f"{i}. {faction_icon} {name} : {initiative_value}")

        return log_lines

    @staticmethod
    def reroll_initiative(combatants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Regénère l'initiative pour tous les combattants

        Utile pour recommencer un combat ou un nouveau round avec nouvelle initiative.

        Args:
            combatants: Liste de combattants (avec ou sans 'initiative' existante)

        Returns:
            Liste triée par nouvelle initiative
        """
        # Réutiliser la logique de roll_initiative
        return InitiativeManager.roll_initiative(combatants)

    @staticmethod
    def get_turn_order_summary(combatants: List[Dict[str, Any]]) -> str:
        """
        Résumé compact de l'ordre des tours

        Args:
            combatants: Liste triée de combattants

        Returns:
            Chaîne formatée avec l'ordre des tours

        Example:
            >>> summary = InitiativeManager.get_turn_order_summary(combatants)
            >>> # "Atucan (18) > Gobelin (12) > Liarie (8)"
        """
        parts = []
        for combatant in combatants:
            name = combatant['character'].name
            initiative_value = combatant.get('initiative', '?')
            parts.append(f"{name} ({initiative_value})")

        return " > ".join(parts)
