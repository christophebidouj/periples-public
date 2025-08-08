# Données détaillées des builds par héros et difficulté
# Version avec équipements, capacités et potions complètes
# Basé sur le fichier Excel "Build persos.xlsx"

HERO_BUILDS_DETAILED = {
    "P-1": {  # Elneha
        "Facile": {
            "equipment": ["O-32", "O-29", "O-42"],  # Vêtement de cuir, Rondache de bois, Gemme de pouvoir (MISSING), Couronne de santé
            "abilities": [1, 2, 3],  # Capacités de base (à ajuster selon les données réelles)
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": ["O-32"],  # Vêtement de cuir
            "abilities": [1, 2],
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": [],  # Aucun équipement
            "abilities": [1],
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔴 Build Spartiate"
        }
    },
    "P-2": {  # Liarie
        "Facile": {
            "equipment": ["O-42"],  # Pierre de mémoire, Baton de puissance (MISSING)
            "abilities": [1, 2, 3, 4],
            "potions": {"small": 0, "large": 1},  # Potion de soin
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": [],  # Aucun équipement
            "abilities": [1, 2],
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": [],  # Aucun équipement
            "abilities": [1],
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔴 Build Spartiate"
        }
    },
    "P-3": {  # Atucan
        "Facile": {
            "equipment": ["O-73", "O-36", "O-31", "O-41"],  # Marteau du juste, Armure de plates, Bouclier de fer, Ceinture de parade
            "abilities": [1, 2, 3],
            "potions": {"small": 0, "large": 0},
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": ["O-9", "O-35", "O-30"],  # Marteau de guerre, Armure de cuir, Bouclier de bois
            "abilities": [1, 2],
            "potions": {"small": 0, "large": 0},
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": ["O-35"],  # Armure de cuir
            "abilities": [1],
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔴 Build Spartiate"
        }
    },
    "P-4": {  # Kraor
        "Facile": {
            "equipment": ["O-11", "O-22", "O-35", "O-40"],  # Arc long, Hache de combat, Armure de cuir, Médaillon d'appel (MISSING), Bague d'impact
            "abilities": [1, 2, 3],
            "potions": {"small": 0, "large": 0},
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": ["O-11", "O-22", "O-35"],  # Arc long, Hache de combat, Armure de cuir
            "abilities": [1, 2],
            "potions": {"small": 0, "large": 0},
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": ["O-22"],  # Hache de combat
            "abilities": [1],
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔴 Build Spartiate"
        }
    },
    "P-5": {  # Thordius
        "Facile": {
            "equipment": ["O-75", "O-38", "O-41"],  # Implacable, Gants de précision, Ceinture de parade
            "abilities": [1, 2],
            "potions": {"small": 0, "large": 1},  # Potion de soin
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": ["O-21"],  # Espadon
            "abilities": [1],
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": ["O-20"],  # Epée longue
            "abilities": [],
            "potions": {"small": 0, "large": 0},
            "name": "🔴 Build Spartiate"
        }
    },
    "P-6": {  # Stèphe
        "Facile": {
            "equipment": ["O-24", "O-32", "O-29", "O-28"],  # Epée bâtarde, Vêtement de cuir, Rondache de bois, Arbalète légère, Lyre phoenix (MISSING)
            "abilities": [1, 2, 3, 4],
            "potions": {"small": 0, "large": 0},
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": ["O-20", "O-32", "O-29"],  # Epée longue, Vêtement de cuir, Rondache de bois
            "abilities": [1, 2],
            "potions": {"small": 0, "large": 0},
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": ["O-19"],  # Epée courte
            "abilities": [1],
            "potions": {"small": 0, "large": 0},
            "name": "🔴 Build Spartiate"
        }
    },
    "P-7": {  # Lame
        "Facile": {
            "equipment": ["O-78", "O-35", "O-30", "O-28"],  # Dagues jumelles, Armure de cuir, Bouclier de bois, Arbalète légère
            "abilities": [1, 2, 3],
            "potions": {"small": 0, "large": 1},  # Potion de soin
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": ["O-19", "O-35"],  # Epée courte, Armure de cuir
            "abilities": [1, 2],
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": ["O-18"],  # Dague
            "abilities": [1],
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔴 Build Spartiate"
        }
    },
    "P-8": {  # Raishi
        "Facile": {
            "equipment": ["O-77", "O-35", "O-29", "O-38"],  # Poings de feu, Armure de cuir, Rondache de bois, Gants de précision
            "abilities": [1, 2, 3],
            "potions": {"small": 0, "large": 1},  # Potion de soin
            "name": "🟢 Build Renforcé"
        },
        "Normal": {
            "equipment": ["O-26", "O-35"],  # Bâton de combat, Armure de cuir
            "abilities": [1, 2],
            "potions": {"small": 1, "large": 0},  # Potion de guérison
            "name": "🔵 Build Standard"
        },
        "Difficile": {
            "equipment": [],  # Aucun équipement
            "abilities": [1],
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

# Items manquants à corriger/ajouter dans equipment.csv
MISSING_EQUIPMENT_ITEMS = [
    "Gemme de pouvoir",  # P-1 Facile
    "Baton de puissance",  # P-2 Facile  
    "Médaillon d'appel",  # P-4 Facile
    "Lyre phoenix"  # P-6 Facile
]

def get_hero_detailed_build(hero_code: str, difficulty: str) -> dict:
    """
    Retourne la configuration détaillée d'un héros pour un niveau de difficulté
    
    Args:
        hero_code: Code du héros (ex: "P-1")
        difficulty: Niveau de difficulté ("Facile", "Normal", "Difficile")
        
    Returns:
        dict: Configuration avec equipment, abilities, potions, name
    """
    # Nettoyage de la difficulté (enlever emoji si présent)
    clean_difficulty = difficulty.replace("🟢 ", "").replace("🔵 ", "").replace("🔴 ", "")
    
    return HERO_BUILDS_DETAILED.get(hero_code, {}).get(clean_difficulty, {
        "equipment": [],
        "abilities": [1],
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

def get_hero_stats_by_difficulty(hero_code: str, difficulty: str) -> dict:
    """
    FONCTION DE COMPATIBILITÉ - À REMPLACER par le calcul depuis les équipements
    Retourne les stats temporaires pour maintenir la compatibilité
    """
    # TODO: Remplacer par le calcul depuis get_hero_detailed_build()
    # Cette fonction sera supprimée une fois le système intégré
    
    temp_stats = {
        "P-1": {"Facile": {"precision": 8, "damage": 4, "health": 7, "parade": 2, "spells": 5},
                "Normal": {"precision": 6, "damage": 2, "health": 5, "parade": 0, "spells": 3},
                "Difficile": {"precision": 4, "damage": 1, "health": 3, "parade": 0, "spells": 1}},
        "P-2": {"Facile": {"precision": 2, "damage": 2, "health": 8, "parade": 1, "spells": 12},
                "Normal": {"precision": 0, "damage": 0, "health": 6, "parade": 0, "spells": 10},
                "Difficile": {"precision": 0, "damage": 0, "health": 4, "parade": 0, "spells": 8}},
        "P-3": {"Facile": {"precision": 5, "damage": 4, "health": 11, "parade": 3, "spells": 4},
                "Normal": {"precision": 3, "damage": 2, "health": 9, "parade": 1, "spells": 2},
                "Difficile": {"precision": 2, "damage": 1, "health": 7, "parade": 0, "spells": 1}},
        "P-4": {"Facile": {"precision": 7, "damage": 5, "health": 9, "parade": 1, "spells": 3},
                "Normal": {"precision": 5, "damage": 3, "health": 7, "parade": 0, "spells": 1},
                "Difficile": {"precision": 3, "damage": 2, "health": 5, "parade": 0, "spells": 0}},
        "P-5": {"Facile": {"precision": 5, "damage": 5, "health": 12, "parade": 2, "spells": 2},
                "Normal": {"precision": 3, "damage": 3, "health": 10, "parade": 1, "spells": 0},
                "Difficile": {"precision": 2, "damage": 2, "health": 8, "parade": 0, "spells": 0}},
        "P-6": {"Facile": {"precision": 6, "damage": 3, "health": 6, "parade": 1, "spells": 6},
                "Normal": {"precision": 4, "damage": 1, "health": 4, "parade": 0, "spells": 4},
                "Difficile": {"precision": 2, "damage": 0, "health": 3, "parade": 0, "spells": 2}},
        "P-7": {"Facile": {"precision": 9, "damage": 6, "health": 8, "parade": 1, "spells": 2},
                "Normal": {"precision": 7, "damage": 4, "health": 6, "parade": 0, "spells": 0},
                "Difficile": {"precision": 5, "damage": 3, "health": 4, "parade": 0, "spells": 0}},
        "P-8": {"Facile": {"precision": 10, "damage": 5, "health": 7, "parade": 1, "spells": 2},
                "Normal": {"precision": 8, "damage": 3, "health": 5, "parade": 0, "spells": 0},
                "Difficile": {"precision": 6, "damage": 2, "health": 3, "parade": 0, "spells": 0}}
    }
    
    clean_difficulty = difficulty.replace("🟢 ", "").replace("🔵 ", "").replace("🔴 ", "")
    return temp_stats.get(hero_code, {}).get(clean_difficulty, {
        "precision": 1, "damage": 1, "health": 3, "parade": 0, "spells": 0
    })