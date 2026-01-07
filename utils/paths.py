"""
Module utilitaire pour la gestion robuste des chemins de fichiers
VERSION 1.0 - Portabilité maximale

Ce module garantit que tous les chemins sont résolus correctement
peu importe d'où l'application est lancée :
- Streamlit Cloud
- Exécutable standalone
- Script Python lancé depuis n'importe quel répertoire

Principe :
- Utilise __file__ pour localiser le répertoire du projet
- Fournit des chemins ABSOLUS basés sur la structure du projet
- Assure la compatibilité cross-platform (Windows, Linux, macOS)
"""

import os
from pathlib import Path

# === CHEMINS RACINE ===

# Répertoire racine du projet (où se trouve app.py)
# __file__ = F:\Python\periples\utils\paths.py
# parent = F:\Python\periples\utils
# parent.parent = F:\Python\periples
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Dossier principal des données
DATA_DIR = PROJECT_ROOT / "data"

# Sous-dossiers d'images
IMAGES_DIR = DATA_DIR / "images"
BESTIARY_DIR = IMAGES_DIR / "Images Bestiaire"


# === FONCTIONS UTILITAIRES ===

def get_data_path(filename: str) -> str:
    """
    Retourne le chemin absolu vers un fichier dans data/

    Args:
        filename: Nom du fichier (ex: "heroes.csv", "Sorts.xlsx")

    Returns:
        Chemin absolu vers le fichier (ex: "F:/Python/periples/data/heroes.csv")

    Exemple:
        >>> get_data_path("heroes.csv")
        "F:/Python/periples/data/heroes.csv"
    """
    return str(DATA_DIR / filename)


def get_image_path(filename: str) -> str:
    """
    Retourne le chemin absolu vers une image dans data/images/

    Args:
        filename: Nom du fichier image (ex: "Ours.jpg", "monstres.jpg")

    Returns:
        Chemin absolu vers l'image

    Exemple:
        >>> get_image_path("Ours.jpg")
        "F:/Python/periples/data/images/Ours.jpg"
    """
    return str(IMAGES_DIR / filename)


def get_bestiary_image_path(filename: str) -> str:
    """
    Retourne le chemin absolu vers une image du bestiaire

    Args:
        filename: Nom du fichier image (ex: "Gobelin.jpg", "Custom.jpg")

    Returns:
        Chemin absolu vers l'image du bestiaire

    Exemple:
        >>> get_bestiary_image_path("Gobelin.jpg")
        "F:/Python/periples/data/images/Images Bestiaire/Gobelin.jpg"
    """
    return str(BESTIARY_DIR / filename)


def get_data_dir() -> str:
    """
    Retourne le chemin absolu vers le dossier data/

    Returns:
        Chemin absolu vers data/ (ex: "F:/Python/periples/data")

    Exemple:
        >>> get_data_dir()
        "F:/Python/periples/data"
    """
    return str(DATA_DIR)


def ensure_data_dir_exists():
    """
    Crée le dossier data/ s'il n'existe pas

    Utilisé au démarrage pour garantir la structure de base
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    BESTIARY_DIR.mkdir(parents=True, exist_ok=True)


# === AUTO-INITIALISATION ===

# Créer les dossiers au chargement du module (sécurité)
ensure_data_dir_exists()
