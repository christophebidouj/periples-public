# Données fixes des builds par héros et difficulté
# Version temporaire avec données d'exemple - à remplacer par les vraies données

HERO_BUILDS = {
    "P-1": {  # Elneha
        "Facile": {"precision": 8, "damage": 4, "health": 7, "parade": 2, "spells": 5},
        "Normal": {"precision": 6, "damage": 2, "health": 5, "parade": 0, "spells": 3},
        "Difficile": {"precision": 4, "damage": 1, "health": 3, "parade": 0, "spells": 1}
    },
    "P-2": {  # Liarie
        "Facile": {"precision": 2, "damage": 2, "health": 8, "parade": 1, "spells": 12},
        "Normal": {"precision": 0, "damage": 0, "health": 6, "parade": 0, "spells": 10},
        "Difficile": {"precision": 0, "damage": 0, "health": 4, "parade": 0, "spells": 8}
    },
    "P-3": {  # Atucan
        "Facile": {"precision": 5, "damage": 4, "health": 11, "parade": 3, "spells": 4},
        "Normal": {"precision": 3, "damage": 2, "health": 9, "parade": 1, "spells": 2},
        "Difficile": {"precision": 2, "damage": 1, "health": 7, "parade": 0, "spells": 1}
    },
    "P-4": {  # Kraor
        "Facile": {"precision": 7, "damage": 5, "health": 9, "parade": 1, "spells": 3},
        "Normal": {"precision": 5, "damage": 3, "health": 7, "parade": 0, "spells": 1},
        "Difficile": {"precision": 3, "damage": 2, "health": 5, "parade": 0, "spells": 0}
    },
    "P-5": {  # Thordius
        "Facile": {"precision": 5, "damage": 5, "health": 12, "parade": 2, "spells": 2},
        "Normal": {"precision": 3, "damage": 3, "health": 10, "parade": 1, "spells": 0},
        "Difficile": {"precision": 2, "damage": 2, "health": 8, "parade": 0, "spells": 0}
    },
    "P-6": {  # Stephe
        "Facile": {"precision": 6, "damage": 3, "health": 6, "parade": 1, "spells": 6},
        "Normal": {"precision": 4, "damage": 1, "health": 4, "parade": 0, "spells": 4},
        "Difficile": {"precision": 2, "damage": 0, "health": 3, "parade": 0, "spells": 2}
    },
    "P-7": {  # Lame
        "Facile": {"precision": 9, "damage": 6, "health": 8, "parade": 1, "spells": 2},
        "Normal": {"precision": 7, "damage": 4, "health": 6, "parade": 0, "spells": 0},
        "Difficile": {"precision": 5, "damage": 3, "health": 4, "parade": 0, "spells": 0}
    },
    "P-8": {  # Raishi
        "Facile": {"precision": 10, "damage": 5, "health": 7, "parade": 1, "spells": 2},
        "Normal": {"precision": 8, "damage": 3, "health": 5, "parade": 0, "spells": 0},
        "Difficile": {"precision": 6, "damage": 2, "health": 3, "parade": 0, "spells": 0}
    },
    "P-9": {  # Ours
        "Facile": {"precision": 8, "damage": 4, "health": 7, "parade": 2, "spells": 5},
        "Normal": {"precision": 6, "damage": 2, "health": 5, "parade": 0, "spells": 3},
        "Difficile": {"precision": 4, "damage": 1, "health": 3, "parade": 0, "spells": 1}
    },
    "P-10": {  # Loup
        "Facile": {"precision": 8, "damage": 4, "health": 7, "parade": 2, "spells": 5},
        "Normal": {"precision": 6, "damage": 2, "health": 5, "parade": 0, "spells": 3},
        "Difficile": {"precision": 4, "damage": 1, "health": 3, "parade": 0, "spells": 1}
    },
    "P-11": {  # Ours S.
        "Facile": {"precision": 8, "damage": 4, "health": 7, "parade": 2, "spells": 5},
        "Normal": {"precision": 6, "damage": 2, "health": 5, "parade": 0, "spells": 3},
        "Difficile": {"precision": 4, "damage": 1, "health": 3, "parade": 0, "spells": 1}
    },
    "P-12": {  # Loup S.
        "Facile": {"precision": 8, "damage": 4, "health": 7, "parade": 2, "spells": 5},
        "Normal": {"precision": 6, "damage": 2, "health": 5, "parade": 0, "spells": 3},
        "Difficile": {"precision": 4, "damage": 1, "health": 3, "parade": 0, "spells": 1}
    }
}

def get_hero_stats_by_difficulty(hero_code: str, difficulty: str) -> dict:
    """
    Retourne les stats d'un héros pour un niveau de difficulté donné
    
    Args:
        hero_code: Code du héros (ex: "P-1")
        difficulty: Niveau de difficulté ("Facile", "Normal", "Difficile")
        
    Returns:
        dict: Dictionnaire avec les stats {precision, damage, health, parade, spells}
    """
    # Nettoyage de la difficulté (enlever emoji si présent)
    clean_difficulty = difficulty.replace("🟢 ", "").replace("🔵 ", "").replace("🔴 ", "")
    
    # Retourne les stats ou des valeurs par défaut
    return HERO_BUILDS.get(hero_code, {}).get(clean_difficulty, {
        "precision": 1, "damage": 1, "health": 3, "parade": 0, "spells": 0
    })

def get_build_name_by_difficulty(difficulty: str) -> str:
    """
    Retourne le nom du build selon la difficulté
    
    Args:
        difficulty: Niveau de difficulté avec ou sans emoji
        
    Returns:
        str: Nom du build avec emoji coloré
    """
    clean_difficulty = difficulty.replace("🟢 ", "").replace("🔵 ", "").replace("🔴 ", "")
    
    build_names = {
        "Facile": "🟢 Build Renforcé",
        "Normal": "🔵 Build Standard", 
        "Difficile": "🔴 Build Spartiate"
    }
    
    return build_names.get(clean_difficulty, "🔵 Build Standard")