"""
Gestionnaire de thèmes visuels pour l'application Périples
Business logic pure - Aucune dépendance UI
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Theme:
    """Définition d'un thème visuel avec toutes ses couleurs"""
    name: str
    background: str
    text_primary: str
    title_color: str
    button_text_color: str  # Couleur du texte sur les boutons
    button_primary: str
    button_primary_hover: str
    button_secondary: str
    button_secondary_hover: str
    hero_color: str
    hero_color_light: str
    enemy_color: str
    enemy_color_light: str
    tab_background: str
    tab_active: str

    # Couleurs de boutons spécialisés
    button_success: str
    button_success_hover: str
    button_info: str
    button_info_hover: str
    button_warning: str
    button_warning_hover: str
    button_danger: str
    button_danger_hover: str
    button_magic: str
    button_magic_hover: str
    button_neutral: str
    button_neutral_hover: str
    button_gold: str
    button_gold_hover: str

    # Couleurs utilitaires
    gold: str
    silver: str
    bronze: str
    selected_border: str
    available_border: str


class ThemeManager:
    """Gestionnaire des thèmes disponibles - Business logic pure sans dépendance Streamlit"""

    THEMES: Dict[str, Theme] = {
        "Parchemin": Theme(
            name="Parchemin",
            # Couleurs principales (thème actuel - inchangé)
            background="#f4e4bc",
            text_primary="#3b2f1c",
            title_color="#4a4a4a",
            button_text_color="#f4e4bc",  # Beige sur bordeaux

            # Boutons principaux (bordeaux vif)
            button_primary="#800020",
            button_primary_hover="#a0002a",
            button_secondary="#6d001a",
            button_secondary_hover="#800020",

            # Équipes
            hero_color="#228b22",
            hero_color_light="#006400",
            enemy_color="#8b0000",
            enemy_color_light="#dc143c",

            # Onglets
            tab_background="#6b7280",
            tab_active="#d97706",

            # Boutons spécialisés (tons chauds et vifs)
            button_success="#228b22",
            button_success_hover="#32cd32",
            button_info="#4169e1",
            button_info_hover="#6495ed",
            button_warning="#ff8c00",
            button_warning_hover="#ffa500",
            button_danger="#dc143c",
            button_danger_hover="#ff1493",
            button_magic="#8a2be2",
            button_magic_hover="#9370db",
            button_neutral="#708090",
            button_neutral_hover="#778899",
            button_gold="#ffd700",
            button_gold_hover="#ffec8c",

            # Utilitaires
            gold="#d4af37",
            silver="#c0c0c0",
            bronze="#cd7f32",
            selected_border="#4a90e2",
            available_border="#5a9f5a"
        ),

        "Professionnel": Theme(
            name="Professionnel",
            # Couleurs principales (tons sombres professionnels)
            background="#1a1d2e",
            text_primary="#e8eaed",
            title_color="#b0b3b8",
            button_text_color="#ffffff",  # Blanc sur bordeaux sobre

            # Boutons principaux (bordeaux sobre)
            button_primary="#6b2737",
            button_primary_hover="#8b3347",
            button_secondary="#4a1a27",
            button_secondary_hover="#6b2737",

            # Équipes (bleu corporate / rouge brique)
            hero_color="#3a7ca5",
            hero_color_light="#5499c7",
            enemy_color="#c1666b",
            enemy_color_light="#d98880",

            # Onglets (gris bleuté professionnel)
            tab_background="#2c3e50",
            tab_active="#3498db",

            # Boutons spécialisés (palette corporate moderne)
            button_success="#2ecc71",
            button_success_hover="#58d68d",
            button_info="#3498db",
            button_info_hover="#5dade2",
            button_warning="#f39c12",
            button_warning_hover="#f8c471",
            button_danger="#e74c3c",
            button_danger_hover="#ec7063",
            button_magic="#9b59b6",
            button_magic_hover="#bb8fce",
            button_neutral="#95a5a6",
            button_neutral_hover="#b2babb",
            button_gold="#f1c40f",
            button_gold_hover="#f4d03f",

            # Utilitaires
            gold="#f39c12",
            silver="#bdc3c7",
            bronze="#d68910",
            selected_border="#3498db",
            available_border="#2ecc71"
        )
    }

    @staticmethod
    def get_theme(theme_name: str) -> Theme:
        """
        Récupère un thème par son nom

        Args:
            theme_name: Nom du thème ("Parchemin" ou "Professionnel")

        Returns:
            Theme: Instance du thème demandé, ou "Parchemin" par défaut
        """
        return ThemeManager.THEMES.get(theme_name, ThemeManager.THEMES["Parchemin"])

    @staticmethod
    def get_available_themes() -> list:
        """
        Retourne la liste des noms de thèmes disponibles

        Returns:
            list: Liste des noms de thèmes ["Parchemin", "Professionnel"]
        """
        return list(ThemeManager.THEMES.keys())

    @staticmethod
    def get_theme_display_names() -> Dict[str, str]:
        """
        Retourne un mapping nom -> nom avec emoji pour affichage UI

        Returns:
            Dict[str, str]: {"Parchemin": "🎲 Parchemin", "Professionnel": "💼 Professionnel"}
        """
        return {
            "Parchemin": "🎲 Parchemin",
            "Professionnel": "💼 Professionnel"
        }
