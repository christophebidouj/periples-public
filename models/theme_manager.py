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
            # Palette harmonisée avec fond beige
            background="#e8d4a8",
            text_primary="#2a1f12",  # Brun très foncé pour lisibilité sur fond clair
            title_color="#5a4a3a",  # Brun moyen pour titres
            button_text_color="#2a1f12",  # Brun foncé sur boutons jaunes

            # Boutons principaux (tons jaune/or plus clairs)
            button_primary="#e8b830",
            button_primary_hover="#f5c84d",
            button_secondary="#d4a017",
            button_secondary_hover="#e8b830",

            # Équipes (couleurs adaptées au fond clair)
            hero_color="#1a6b1a",  # Vert forêt foncé
            hero_color_light="#228b22",  # Vert plus vif
            enemy_color="#8b0000",  # Rouge foncé
            enemy_color_light="#b22222",  # Rouge vif

            # Onglets (tons chauds pour harmonie avec beige)
            tab_background="#8b7355",  # Brun clair
            tab_active="#d97706",  # Orange/or vif

            # Boutons spécialisés (palette chaude adaptée au fond clair)
            button_success="#1a7a1a",  # Vert foncé
            button_success_hover="#228b22",
            button_info="#1e5a8e",  # Bleu foncé
            button_info_hover="#2674b3",
            button_warning="#cc7000",  # Orange foncé
            button_warning_hover="#e67e00",
            button_danger="#b30000",  # Rouge vif foncé
            button_danger_hover="#cc0000",
            button_magic="#6b2e8a",  # Violet foncé
            button_magic_hover="#8b3eaa",
            button_neutral="#5a5a5a",  # Gris foncé
            button_neutral_hover="#707070",
            button_gold="#b8860b",  # Or foncé
            button_gold_hover="#daa520",

            # Utilitaires (adaptés au fond clair)
            gold="#b8860b",  # Or foncé
            silver="#708090",  # Gris ardoise
            bronze="#8b4513",  # Brun cuivré
            selected_border="#1e5a8e",  # Bleu foncé
            available_border="#1a7a1a"  # Vert foncé
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
        ),

        "Fantasy": Theme(
            name="Fantasy",
            # Couleurs principales (tons violets mystiques)
            background="#1a1225",
            text_primary="#e8e6f0",
            title_color="#b8a3d9",
            button_text_color="#ffffff",  # Blanc sur violet

            # Boutons principaux (violet magenta)
            button_primary="#6b2e8a",
            button_primary_hover="#8b3eaa",
            button_secondary="#4a1d5f",
            button_secondary_hover="#6b2e8a",

            # Équipes (bleu électrique / magenta)
            hero_color="#5b7bdb",
            hero_color_light="#7b9aed",
            enemy_color="#c74375",
            enemy_color_light="#d76395",

            # Onglets (violet profond)
            tab_background="#2d1b3d",
            tab_active="#9b59b6",

            # Boutons spécialisés (palette fantasy vibrante)
            button_success="#8e44ad",
            button_success_hover="#a569bd",
            button_info="#5b7bdb",
            button_info_hover="#7b9aed",
            button_warning="#e67e22",
            button_warning_hover="#f39c12",
            button_danger="#c74375",
            button_danger_hover="#d76395",
            button_magic="#9b59b6",
            button_magic_hover="#bb8fce",
            button_neutral="#7f8c8d",
            button_neutral_hover="#95a5a6",
            button_gold="#f1c40f",
            button_gold_hover="#f4d03f",

            # Utilitaires
            gold="#f1c40f",
            silver="#bdc3c7",
            bronze="#cd7f32",
            selected_border="#9b59b6",
            available_border="#8e44ad"
        ),

        "Nature": Theme(
            name="Nature",
            # Couleurs principales (tons verts forestiers)
            background="#1a2618",
            text_primary="#e8f0e6",
            title_color="#a3c9a0",
            button_text_color="#ffffff",  # Blanc sur vert

            # Boutons principaux (vert forêt)
            button_primary="#2d5a3d",
            button_primary_hover="#3a7a4d",
            button_secondary="#1e3a27",
            button_secondary_hover="#2d5a3d",

            # Équipes (vert vif / orange terreux)
            hero_color="#4a9b5f",
            hero_color_light="#5ebc75",
            enemy_color="#c76e3a",
            enemy_color_light="#d98850",

            # Onglets (vert sombre)
            tab_background="#2d4a2d",
            tab_active="#27ae60",

            # Boutons spécialisés (palette nature harmonieuse)
            button_success="#27ae60",
            button_success_hover="#2ecc71",
            button_info="#16a085",
            button_info_hover="#1abc9c",
            button_warning="#d68910",
            button_warning_hover="#f39c12",
            button_danger="#c0392b",
            button_danger_hover="#e74c3c",
            button_magic="#8e44ad",
            button_magic_hover="#9b59b6",
            button_neutral="#7f8c8d",
            button_neutral_hover="#95a5a6",
            button_gold="#f39c12",
            button_gold_hover="#f8c471",

            # Utilitaires
            gold="#d4af37",
            silver="#95a5a6",
            bronze="#cd7f32",
            selected_border="#27ae60",
            available_border="#4a9b5f"
        ),

        "Azur": Theme(
            name="Azur",
            # Couleurs principales (tons bleus clairs et cyan)
            background="#0a1628",
            text_primary="#e6f4ff",
            title_color="#a3d5ff",
            button_text_color="#ffffff",  # Blanc sur bleu

            # Boutons principaux (bleu azure)
            button_primary="#1e5a8e",
            button_primary_hover="#2674b3",
            button_secondary="#134074",
            button_secondary_hover="#1e5a8e",

            # Équipes (cyan vif / orange corail)
            hero_color="#00b4d8",
            hero_color_light="#48cae4",
            enemy_color="#ff6b35",
            enemy_color_light="#ff8c61",

            # Onglets (bleu marine)
            tab_background="#1a2f4a",
            tab_active="#00b4d8",

            # Boutons spécialisés (palette bleu harmonieuse)
            button_success="#06d6a0",
            button_success_hover="#1ae5b0",
            button_info="#00b4d8",
            button_info_hover="#48cae4",
            button_warning="#ffa500",
            button_warning_hover="#ffb733",
            button_danger="#ef476f",
            button_danger_hover="#f77593",
            button_magic="#8b7fb8",
            button_magic_hover="#9d91c7",
            button_neutral="#64748b",
            button_neutral_hover="#94a3b8",
            button_gold="#fbbf24",
            button_gold_hover="#fcd34d",

            # Utilitaires
            gold="#fbbf24",
            silver="#cbd5e1",
            bronze="#fb923c",
            selected_border="#00b4d8",
            available_border="#06d6a0"
        ),

        "Médiéval": Theme(
            name="Médiéval",
            # Couleurs principales (fond sombre médiéval - parchemin ancien brûlé)
            background="#1a1410",
            text_primary="#e8dcc8",
            title_color="#c9b896",
            button_text_color="#f5ead6",

            # Boutons principaux (bordeaux médiéval)
            button_primary="#6b2737",
            button_primary_hover="#8b3347",
            button_secondary="#4a1a27",
            button_secondary_hover="#6b2737",

            # Équipes (bleu royal / rouge brique)
            hero_color="#4a7bc8",
            hero_color_light="#6a9be8",
            enemy_color="#a83832",
            enemy_color_light="#c85850",

            # Onglets (brun médiéval)
            tab_background="#3a2f1e",
            tab_active="#8b6f47",

            # Boutons spécialisés (palette médiévale chaleureuse)
            button_success="#4a7a3e",
            button_success_hover="#5a9a4e",
            button_info="#4169a3",
            button_info_hover="#5589c3",
            button_warning="#d4a017",
            button_warning_hover="#e8b830",
            button_danger="#a83832",
            button_danger_hover="#c85850",
            button_magic="#6b4a8e",
            button_magic_hover="#8b6aae",
            button_neutral="#6b5d4f",
            button_neutral_hover="#8b7d6f",
            button_gold="#d4a017",
            button_gold_hover="#e8b830",

            # Utilitaires
            gold="#d4a017",
            silver="#b8b8b8",
            bronze="#b87333",
            selected_border="#8b6f47",
            available_border="#4a7a3e"
        )
    }

    @staticmethod
    def get_theme(theme_name: str) -> Theme:
        """
        Récupère un thème par son nom

        Args:
            theme_name: Nom du thème ("Professionnel", "Parchemin V2", etc.)

        Returns:
            Theme: Instance du thème demandé, ou "Professionnel" par défaut
        """
        return ThemeManager.THEMES.get(theme_name, ThemeManager.THEMES["Professionnel"])

    @staticmethod
    def get_available_themes() -> list:
        """
        Retourne la liste des noms de thèmes disponibles (triée alphabétiquement)

        Returns:
            list: Liste des noms de thèmes ["Azur", "Fantasy", "Médiéval", ...]
        """
        return sorted(list(ThemeManager.THEMES.keys()))

    @staticmethod
    def get_theme_display_names() -> Dict[str, str]:
        """
        Retourne un mapping nom -> nom avec emoji pour affichage UI

        Returns:
            Dict[str, str]: {"Azur": "🌊 Azur", "Fantasy": "✨ Fantasy", ...}
        """
        return {
            "Azur": "🌊 Azur",
            "Fantasy": "✨ Fantasy",
            "Médiéval": "⚔️ Médiéval",
            "Nature": "🌿 Nature",
            "Parchemin": "📜 Parchemin",
            "Professionnel": "💼 Professionnel"
        }
