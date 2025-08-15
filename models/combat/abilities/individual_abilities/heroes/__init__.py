# heroes_init
"""
Module des capacités individuelles par héros
Importe toutes les capacités des héros disponibles
"""

# Import des capacités d'Elneha (pilote)
try:
    from .elneha import ElnehaFormeOurs, ElnehaSoinMineur, ElnehaTransformationHelper
    ELNEHA_LOADED = True
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités d'Elneha: {e}")
    ELNEHA_LOADED = False

# Import des autres héros (sera ajouté progressivement)
# try:
#     from .liarie import *
#     LIARIE_LOADED = True
# except ImportError:
#     LIARIE_LOADED = False

# Exports disponibles
__all__ = []

if ELNEHA_LOADED:
    __all__.extend(['ElnehaFormeOurs', 'ElnehaSoinMineur', 'ElnehaTransformationHelper'])

# Information sur les capacités chargées
def get_loaded_heroes():
    """Retourne la liste des héros avec capacités chargées"""
    loaded = []
    if ELNEHA_LOADED:
        loaded.append("P-1 (Elneha)")
    return loaded

def get_loaded_abilities_count():
    """Retourne le nombre de capacités individuelles chargées"""
    count = 0
    if ELNEHA_LOADED:
        count += 2  # Forme d'ours + Soin mineur
    return count