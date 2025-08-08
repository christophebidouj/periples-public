# Données détaillées des builds par héros et difficulté
# Version avec système de niveaux de capacités séquentielles (1-6)
# Basé sur le fichier Excel "Build persos.xlsx"

HERO_BUILDS_DETAILED = {
    "P-1": {  # Elneha
        "Facile": {
            "equipment": ["O-32", "O-29", "O-1", "O-39"],  # Vétement de cuir, Rondache de bois, Gemme de pouvoir, Couronne de santé
            "abilities_level": 6,  # Niveau max de capacités (1-6 acquises)
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": ["O-32"],  # Vétement de cuir
            "abilities_level": 3,  # Capacités 1-3 acquises
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": [],  # Aucun équipement
            "abilities_level": 1,  # Seule la capacité 1 acquise
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔴 Build Spartiate"
        }
    },
    "P-2": {  # Liarie
        "Facile": {
            "equipment": ["O-42", "O-2"],  # Pierre de mémoire, Baton de puissance
            "abilities_level": 6,
            "potions": {"small": 0, "large": 1},  # Potion de soin
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": [],  # Aucun équipement
            "abilities_level": 3,
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": [],  # Aucun équipement
            "abilities_level": 1,
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔴 Build Spartiate"
        }
    },
    "P-3": {  # Atucan
        "Facile": {
            "equipment": ["O-73", "O-36", "O-31", "O-41"],  # Marteau du juste, Armure de plate, Bouclier de fer, Ceinture de parade
            "abilities_level": 6,
            "potions": {"small": 0, "large": 0},
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": ["O-9", "O-35", "O-30"],  # Marteau de guerre, Armure de cuir, Bouclier de bois
            "abilities_level": 3,
            "potions": {"small": 0, "large": 0},
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": ["O-35"],  # Armure de cuir
            "abilities_level": 1,
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔴 Build Spartiate"
        }
    },
    "P-4": {  # Kraor
        "Facile": {
            "equipment": ["O-11", "O-22", "O-35", "O-3", "O-40"],  # Arc long, Hache de combat, Armure de cuir, Médaillon d'appel, Bague d'impact
            "abilities_level": 6,
            "potions": {"small": 0, "large": 0},
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": ["O-11", "O-22", "O-35"],  # Arc long, Hache de combat, Armure de cuir
            "abilities_level": 3,
            "potions": {"small": 0, "large": 0},
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": ["O-22"],  # Hache de combat
            "abilities_level": 1,
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔴 Build Spartiate"
        }
    },
    "P-5": {  # Thordius
        "Facile": {
            "equipment": ["O-75", "O-38", "O-41"],  # Implacable, Gants de précision, Ceinture de parade
            "abilities_level": 6,
            "potions": {"small": 0, "large": 1},  # Potion de soin
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": ["O-21"],  # Espadon
            "abilities_level": 3,
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": ["O-20"],  # Epée longue
            "abilities_level": 1,
            "potions": {"small": 0, "large": 0},
            "name": "🔴 Build Spartiate"
        }
    },
    "P-6": {  # Stèphe
        "Facile": {
            "equipment": ["O-24", "O-32", "O-29", "O-28", "O-4"],  # Epée bâtarde, Vêtement de cuir, Rondache de bois, Arbalète légère, Lyre phoenix
            "abilities_level": 6,
            "potions": {"small": 0, "large": 0},
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": ["O-20", "O-32", "O-29"],  # Epée longue, Vêtement de cuir, Rondache de bois
            "abilities_level": 3,
            "potions": {"small": 0, "large": 0},
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": ["O-19"],  # Epée courte
            "abilities_level": 1,
            "potions": {"small": 0, "large": 0},
            "name": "🔴 Build Spartiate"
        }
    },
    "P-7": {  # Lame
        "Facile": {
            "equipment": ["O-78", "O-35", "O-30", "O-28"],  # Dagues jumelles, Armure de cuir, Bouclier de bois, Arbalète légère
            "abilities_level": 6,
            "potions": {"small": 0, "large": 1},  # Potion de soin
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": ["O-19", "O-35"],  # Epée courte, Armure de cuir
            "abilities_level": 3,
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": ["O-18"],  # Dague
            "abilities_level": 1,
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔴 Build Spartiate"
        }
    },
    "P-8": {  # Raishi
        "Facile": {
            "equipment": ["O-77", "O-35", "O-29", "O-38"],  # Poings de feu, Armure de cuir, Rondache de bois, Gants de précision
            "abilities_level": 6,
            "potions": {"small": 0, "large": 1},  # Potion de soin
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": ["O-26", "O-35"],  # Bâton de combat, Armure de cuir
            "abilities_level": 3,
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": [],  # Aucun équipement
            "abilities_level": 1,
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔴 Build Spartiate"
        }
    }
}

# Mapping héros code → nom pour référence
HERO_CODE_MAPPING = {
    "P-1": "Elneha",
    "P-2": "Liarie", 
    "P-3": "Atucan",
    "P-4": "Kraor",
    "P-5": "Thordius",
    "P-6": "Stèphe",
    "P-7": "Lame",
    "P-8": "Raishi"
}

def get_hero_detailed_build(hero_code: str, difficulty: str) -> dict:
    """
    Retourne la configuration détaillée d'un héros pour un niveau de difficulté
    
    Args:
        hero_code: Code du héros (ex: "P-1")
        difficulty: Niveau de difficulté ("Facile", "Normal", "Difficile")
        
    Returns:
        dict: Configuration avec equipment, abilities_level, potions, name
    """
    # Nettoyage de la difficulté (enlever emoji si présent)
    clean_difficulty = difficulty.replace("🟢 ", "").replace("🔵 ", "").replace("🔴 ", "")
    
    return HERO_BUILDS_DETAILED.get(hero_code, {}).get(clean_difficulty, {
        "equipment": [],
        "abilities_level": 1,
        "potions": {"small": 0, "large": 0},
        "name": "🔵 Build Standard"
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

def get_abilities_for_level(hero_code: str, abilities_level: int) -> list:
    """
    Retourne la liste des numéros de capacités acquises selon le niveau
    
    Args:
        hero_code: Code du héros (ex: "P-1")
        abilities_level: Niveau de capacité (1-6)
        
    Returns:
        list: Liste des numéros de capacités acquises [1, 2, 3, ...]
    """
    if abilities_level <= 0:
        return []
    
    # Max 6 capacités par héros
    max_abilities = min(abilities_level, 6)
    return list(range(1, max_abilities + 1))