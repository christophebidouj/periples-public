"""
Module components centralisé pour le Simulateur Périples
Imports de tous les composants UI depuis les sous-modules
"""

# Import des composants héros
from ui.components.hero_components import (
    display_hero_card,
    display_team_recap,
    display_hero_base_stats,
    display_current_build_info,
    display_new_stats_preview
)

# Import des composants ennemis
from ui.components.enemy_components import (
    display_enemy_card
)

# Import des composants équipements
from ui.components.equipment_components import (
    display_equipment_card_native,
    display_equipment_selection_native
)

# Import des composants de combat
from ui.components.combat_components import (
    display_combat_result_banner,
    display_combat_metrics,
    display_heroes_individual_table,
    display_combat_log,
    display_combat_summary
)

# Import des éléments UI communs
from ui.components.ui_elements import (
    display_progress_indicators_with_reset,
    get_hero_icon,
    get_equipment_icon
)

# Export de tous les composants pour compatibilité
__all__ = [
    # Héros
    'display_hero_card',
    'display_team_recap', 
    'display_hero_base_stats',
    'display_current_build_info',
    'display_new_stats_preview',
    
    # Ennemis
    'display_enemy_card',
    
    # Équipements
    'display_equipment_card_native',
    'display_equipment_selection_native',
    
    # Combat
    'display_combat_result_banner',
    'display_combat_metrics',
    'display_heroes_individual_table',
    'display_combat_log',
    'display_combat_summary',
    
    # UI Elements
    'display_progress_indicators_with_reset',
    'get_hero_icon',
    'get_equipment_icon'
]