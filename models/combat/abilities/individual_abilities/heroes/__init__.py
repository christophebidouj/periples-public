# heroes/__init__.py - Point d'entrée des capacités par héros
"""
Point d'entrée pour toutes les capacités individuelles des héros
Phase 3+: Elneha (6/6) + Liarie (6/6) + Atucan (6/6) + Kraor (4/6) = 22 capacités totales

Structure:
- Elneha (P-1): Druide transformations et soins (6 capacités)
- Liarie (P-2): Mage élémentaire offensive/défensive (6 capacités)
- Atucan (P-3): Paladin défensif protection/soins divins (6 capacités)
- Kraor (P-4): Chasseur tactique support/utility (4 capacités combat)
"""

# ========================================
# IMPORTS DES CAPACITÉS PAR HÉROS
# ========================================

# Import des capacités d'Elneha (P-1)
try:
    from .elneha import (
        ElnehaFormeOurs, ElnehaSoinMineur, ElnehaFormeLoup,
        ElnehaSoinMultiple, ElnehaOndeTonnante, ElnehaResurrection,
        get_elneha_abilities_count, get_elneha_abilities_summary
    )
    ELNEHA_LOADED = True
    print("✅ Capacités d'Elneha (P-1) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités d'Elneha: {e}")
    ELNEHA_LOADED = False

# Import des capacités de Liarie (P-2)
try:
    from .liarie import (
        LiarieEclairMagique, LiarieArmureDuMage, LiarieMurDeGlace,
        LiarieBouleDeFeu, LiarieVolDeVie, LiariePluieDeMetéores,
        get_liarie_abilities_count, get_liarie_abilities_summary,
        get_liarie_spell_costs, get_liarie_damage_output, get_liarie_tactical_analysis
    )
    LIARIE_LOADED = True
    print("✅ Capacités de Liarie (P-2) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités de Liarie: {e}")
    LIARIE_LOADED = False

# Import des capacités d'Atucan (P-3)
try:
    from .atucan import (
        AtucanImpositionDesMains, AtucanParade, AtucanChatimentDivin,
        AtucanAuraSacree, AtucanSoinSuperieur, AtucanJugementDernier,
        get_atucan_abilities_count, get_atucan_abilities_summary,
        get_atucan_spell_costs, get_atucan_tactical_analysis
    )
    ATUCAN_LOADED = True
    print("✅ Capacités d'Atucan (P-3) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités d'Atucan: {e}")
    ATUCAN_LOADED = False

# Import des capacités de Kraor (P-4) - NOUVEAU PHASE 3+
try:
    from .kraor import (
        KraorPiege, KraorPoison, KraorFlecheExplosive, KraorPluieDeFlèches,
        get_kraor_abilities_count, get_kraor_abilities_summary,
        get_kraor_spell_costs, get_kraor_combat_limitations, get_kraor_tactical_analysis,
        validate_kraor_implementation, get_kraor_debug_info
    )
    KRAOR_LOADED = True
    print("✅ Capacités de Kraor (P-4) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités de Kraor: {e}")
    KRAOR_LOADED = False

# Imports futurs (Phases 4+)
# try:
#     from .thordius import *
#     THORDIUS_LOADED = True
# except ImportError:
#     THORDIUS_LOADED = False

# ========================================
# EXPORTS PUBLICS
# ========================================

__all__ = []

# Elneha exports
if ELNEHA_LOADED:
    __all__.extend([
        'ElnehaFormeOurs', 'ElnehaSoinMineur', 'ElnehaFormeLoup',
        'ElnehaSoinMultiple', 'ElnehaOndeTonnante', 'ElnehaResurrection'
    ])

# Liarie exports
if LIARIE_LOADED:
    __all__.extend([
        'LiarieEclairMagique', 'LiarieArmureDuMage', 'LiarieMurDeGlace',
        'LiarieBouleDeFeu', 'LiarieVolDeVie', 'LiariePluieDeMetéores'
    ])

# Atucan exports
if ATUCAN_LOADED:
    __all__.extend([
        'AtucanImpositionDesMains', 'AtucanParade', 'AtucanChatimentDivin',
        'AtucanAuraSacree', 'AtucanSoinSuperieur', 'AtucanJugementDernier'
    ])

# Kraor exports - NOUVEAU
if KRAOR_LOADED:
    __all__.extend([
        'KraorPiege', 'KraorPoison', 'KraorFlecheExplosive', 'KraorPluieDeFlèches'
    ])

# ========================================
# STATISTIQUES GLOBALES PHASE 3+
# ========================================

def get_phase2_statistics() -> dict:
    """Retourne les statistiques complètes - MISE À JOUR PHASE 3+ avec Kraor"""
    
    elneha_count = get_elneha_abilities_count() if ELNEHA_LOADED else 0
    liarie_count = get_liarie_abilities_count() if LIARIE_LOADED else 0
    atucan_count = get_atucan_abilities_count() if ATUCAN_LOADED else 0
    kraor_count = get_kraor_abilities_count() if KRAOR_LOADED else 0  # NOUVEAU
    total_count = elneha_count + liarie_count + atucan_count + kraor_count  # Kraor ajouté
    
    heroes_completed = []
    if ELNEHA_LOADED and elneha_count == 6:
        heroes_completed.append("P-1 (Elneha)")
    if LIARIE_LOADED and liarie_count == 6:
        heroes_completed.append("P-2 (Liarie)")
    if ATUCAN_LOADED and atucan_count == 6:
        heroes_completed.append("P-3 (Atucan)")
    if KRAOR_LOADED and kraor_count == 4:  # Kraor a 4 capacités combat (pas 6)
        heroes_completed.append("P-4 (Kraor)")
    
    return {
        "phase": "3+",  # Mise à jour phase avec Kraor
        "heroes_completed": heroes_completed,
        "total_abilities": total_count,
        "elneha_abilities": elneha_count,
        "liarie_abilities": liarie_count,
        "atucan_abilities": atucan_count,
        "kraor_abilities": kraor_count,  # NOUVEAU
        "progress_percentage": round((total_count / 59) * 100, 1),  # /59 au lieu de /48
        "mechanical_abilities_estimate": total_count + 2,  # +2 legacy transformations
        "next_phase_target": 30,  # Phase 4 objectif avec Thordius
        "loading_status": {
            "elneha_loaded": ELNEHA_LOADED,
            "liarie_loaded": LIARIE_LOADED,
            "atucan_loaded": ATUCAN_LOADED,
            "kraor_loaded": KRAOR_LOADED  # NOUVEAU
        }
    }

def print_phase2_summary():
    """Affiche un résumé complet - MISE À JOUR PHASE 3+ avec Kraor"""
    stats = get_phase2_statistics()
    
    print("\n" + "="*60)
    print(f"📊 RÉSUMÉ PHASE 3+ - MIGRATION CAPACITÉS INDIVIDUELLES")
    print("="*60)
    
    print(f"🎯 Objectif Phase 3+: 22 capacités individuelles")
    print(f"✅ Réalisé: {stats['total_abilities']}/22 capacités")
    print(f"📈 Progression globale: {stats['progress_percentage']}% ({stats['total_abilities']}/59)")
    
    print(f"\n🎭 Héros complétés:")
    for hero in stats['heroes_completed']:
        print(f"   ✅ {hero}")
    
    print(f"\n📊 Détail par héros:")
    print(f"   🐻 Elneha (P-1): {stats['elneha_abilities']}/6 capacités")
    print(f"   🔮 Liarie (P-2): {stats['liarie_abilities']}/6 capacités")
    if ATUCAN_LOADED:
        print(f"   ⚔️ Atucan (P-3): {stats['atucan_abilities']}/6 capacités")
    if KRAOR_LOADED:
        print(f"   🏹 Kraor (P-4): {stats['kraor_abilities']}/4 capacités combat")  # NOUVEAU
    
    print(f"\n⚙️ Capacités mécaniques estimées: ~{stats['mechanical_abilities_estimate']}")
    print(f"🚀 Prochaine étape: Phase 4 vers {stats['next_phase_target']} capacités")
    
    # Afficher les résumés détaillés si disponibles
    if ELNEHA_LOADED:
        print(f"\n{get_elneha_abilities_summary()}")
    
    if LIARIE_LOADED:
        print(f"\n{get_liarie_abilities_summary()}")
    
    if ATUCAN_LOADED:
        print(f"\n{get_atucan_abilities_summary()}")
    
    if KRAOR_LOADED:  # NOUVEAU
        print(f"\n{get_kraor_abilities_summary()}")
    
    print("\n" + "="*60)
    if stats['total_abilities'] >= 22:
        print("🎉 PHASE 3+ TERMINÉE AVEC SUCCÈS !")
        print("📋 Prochaine étape: Implémenter P-5 Thordius pour Phase 4")
    elif stats['total_abilities'] >= 18:
        print("🎉 PHASE 3 PARTIELLEMENT TERMINÉE - Kraor en cours !")
        print("🏹 Finaliser Kraor pour compléter Phase 3+")
    elif stats['total_abilities'] >= 12:
        print("🎉 PHASE 2 TERMINÉE - Phase 3+ en cours !")
    else:
        print(f"⚠️ PHASE INCOMPLÈTE ({stats['total_abilities']}/22)")
    print("="*60)

def get_all_heroes_summary() -> str:
    """Retourne un résumé de tous les héros implémentés - MISE À JOUR PHASE 3+ avec Kraor"""
    stats = get_phase2_statistics()
    
    summary = f"📚 HÉROS IMPLÉMENTÉS - PHASE 3+:\n\n"
    
    if ELNEHA_LOADED:
        summary += get_elneha_abilities_summary() + "\n"
    
    if LIARIE_LOADED:
        summary += get_liarie_abilities_summary() + "\n"
    
    if ATUCAN_LOADED:
        summary += get_atucan_abilities_summary() + "\n"
    
    if KRAOR_LOADED:  # NOUVEAU
        summary += get_kraor_abilities_summary() + "\n"
    
    summary += f"🔮 TOTAL: {stats['total_abilities']} capacités individuelles sur 59 ({stats['progress_percentage']}%)\n"
    
    return summary

def get_tactical_analysis() -> dict:
    """Analyse tactique des héros disponibles - MISE À JOUR PHASE 3+ avec Kraor"""
    analysis = {
        "phase": "3+",
        "heroes_available": [],
        "synergies": [],
        "combat_roles": {}
    }
    
    if ELNEHA_LOADED:
        analysis["heroes_available"].append("Elneha (P-1)")
        analysis["combat_roles"]["Elneha"] = {
            "primary": "Tank/Healer",
            "secondary": "Shapeshifter",
            "strengths": ["Transformations", "Area healing", "Resurrection"],
            "spell_costs": "1-2 sorts par capacité"
        }
    
    if LIARIE_LOADED:
        analysis["heroes_available"].append("Liarie (P-2)")
        analysis["combat_roles"]["Liarie"] = {
            "primary": "DPS/Control",
            "secondary": "Support",
            "strengths": ["High damage", "No retaliation", "Self-sustain"],
            "spell_costs": "1-4 sorts par capacité"
        }
    
    if ATUCAN_LOADED:
        analysis["heroes_available"].append("Atucan (P-3)")
        analysis["combat_roles"]["Atucan"] = {
            "primary": "Tank/Support",
            "secondary": "Divine DPS",
            "strengths": ["Defensive buffs", "Group healing", "Divine damage"],
            "spell_costs": "1-3 sorts par capacité"
        }
    
    if KRAOR_LOADED:  # NOUVEAU
        analysis["heroes_available"].append("Kraor (P-4)")
        analysis["combat_roles"]["Kraor"] = {
            "primary": "Utility/Support",
            "secondary": "Tactical DPS",
            "strengths": ["Zero spell costs", "Group damage boost", "Multi-target attacks", "Emergency healing"],
            "spell_costs": "0 sorts (toutes gratuites)"
        }
    
    # Synergies mises à jour avec Kraor
    synergies = []
    if ELNEHA_LOADED and LIARIE_LOADED:
        synergies.append("Elneha tank + Liarie DPS = équipe équilibrée")
        synergies.append("Soin multiple d'Elneha + Vol de vie de Liarie = sustain optimal")
    
    if ATUCAN_LOADED and ELNEHA_LOADED:
        synergies.append("Atucan parade + transformations Elneha = tank ultime")
        synergies.append("Double soins: Elneha shapeshifter + Atucan paladin")
    
    if ATUCAN_LOADED and LIARIE_LOADED:
        synergies.append("Atucan support + Liarie DPS = protection + dégâts")
        synergies.append("Châtiment divin + sorts sans riposte = combo magique")
    
    if KRAOR_LOADED and ELNEHA_LOADED:  # NOUVEAU
        synergies.append("Kraor marquage + transformations Elneha = DPS boosté")
        synergies.append("Soins Kraor + résurrection Elneha = support complet")
    
    if KRAOR_LOADED and LIARIE_LOADED:  # NOUVEAU
        synergies.append("Kraor multi-cible + Liarie AoE = contrôle battlefield")
        synergies.append("Kraor gratuit + Liarie coûteuse = équilibre sorts")
    
    if KRAOR_LOADED and ATUCAN_LOADED:  # NOUVEAU
        synergies.append("Kraor double attaque + Atucan buffs = DPS soutenu")
        synergies.append("Kraor tactique + Atucan défensif = support polyvalent")
    
    if ELNEHA_LOADED and LIARIE_LOADED and ATUCAN_LOADED and KRAOR_LOADED:  # NOUVEAU
        synergies.append("Quatuor complet: Tank (Elneha), DPS (Liarie), Support (Atucan), Utility (Kraor)")
        synergies.append("Soins quadruples: Naturels + Magiques + Divins + Tactiques")
        synergies.append("Économie sorts optimale: Kraor gratuit libère sorts pour les autres")
    
    analysis["synergies"] = synergies
    
    return analysis

# ========================================
# VALIDATION ET TESTS - MISE À JOUR KRAOR
# ========================================

def validate_phase2_implementation() -> bool:
    """Valide que toutes les capacités Phase 3+ sont correctement implémentées"""
    try:
        # Vérifier les compteurs
        elneha_count = get_elneha_abilities_count() if ELNEHA_LOADED else 0
        liarie_count = get_liarie_abilities_count() if LIARIE_LOADED else 0
        atucan_count = get_atucan_abilities_count() if ATUCAN_LOADED else 0
        kraor_count = get_kraor_abilities_count() if KRAOR_LOADED else 0  # NOUVEAU
        
        # Vérifications
        success = True
        
        if not ELNEHA_LOADED:
            print(f"❌ Elneha: Module non chargé")
            success = False
        elif elneha_count != 6:
            print(f"❌ Elneha: {elneha_count}/6 capacités")
            success = False
        
        if not LIARIE_LOADED:
            print(f"❌ Liarie: Module non chargé")
            success = False
        elif liarie_count != 6:
            print(f"❌ Liarie: {liarie_count}/6 capacités")
            success = False
        
        if not ATUCAN_LOADED:
            print(f"❌ Atucan: Module non chargé")
            success = False
        elif atucan_count != 6:
            print(f"❌ Atucan: {atucan_count}/6 capacités")
            success = False
        
        if not KRAOR_LOADED:  # NOUVEAU
            print(f"❌ Kraor: Module non chargé")
            success = False
        elif kraor_count != 4:  # Kraor a 4 capacités, pas 6
            print(f"❌ Kraor: {kraor_count}/4 capacités")
            success = False
        
        if success:
            total = elneha_count + liarie_count + atucan_count + kraor_count  # Kraor ajouté
            print(f"✅ Validation réussie: Elneha {elneha_count}/6, Liarie {liarie_count}/6, Atucan {atucan_count}/6, Kraor {kraor_count}/4")
            print(f"🎯 Total Phase 3+: {total}/22 capacités")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False

def get_loaded_heroes():
    """Retourne la liste des héros avec capacités chargées"""
    loaded = []
    
    if ELNEHA_LOADED:
        loaded.append("P-1 (Elneha)")
    if LIARIE_LOADED:
        loaded.append("P-2 (Liarie)")
    if ATUCAN_LOADED:
        loaded.append("P-3 (Atucan)")
    if KRAOR_LOADED:  # NOUVEAU
        loaded.append("P-4 (Kraor)")
    
    return loaded

def get_loaded_abilities_count():
    """Retourne le nombre de capacités individuelles chargées"""
    count = 0
    
    if ELNEHA_LOADED:
        count += get_elneha_abilities_count()
    if LIARIE_LOADED:
        count += get_liarie_abilities_count()
    if ATUCAN_LOADED:
        count += get_atucan_abilities_count()
    if KRAOR_LOADED:  # NOUVEAU
        count += get_kraor_abilities_count()
    
    return count

# ========================================
# INFORMATION DE CHARGEMENT - MISE À JOUR KRAOR
# ========================================

# Afficher un résumé lors de l'import
def _print_loading_summary():
    """Affiche un résumé du chargement lors de l'import"""
    total_loaded = get_loaded_abilities_count()
    heroes_loaded = get_loaded_heroes()
    
    print(f"\n📦 Module héros chargé:")
    print(f"   🎭 Héros: {', '.join(heroes_loaded) if heroes_loaded else 'Aucun'}")
    print(f"   ⚡ Capacités: {total_loaded}/59 ({round(total_loaded/59*100, 1)}%)")
    
    if total_loaded >= 22:
        print(f"   🎉 Phase 3+ complète avec Kraor !")
    elif total_loaded >= 18:
        print(f"   🏹 Phase 3+ avec Kraor en cours...")
    elif total_loaded >= 12:
        print(f"   🎉 Phase 2 complète, Phase 3+ en cours...")
    elif total_loaded >= 2:
        print(f"   ⏳ Phase 2 en cours...")
    else:
        print(f"   🔧 Système en configuration...")

# Exécuter le résumé automatiquement
_print_loading_summary()

# ========================================
# EXPORTS FINAUX
# ========================================

# Ajouter les fonctions utilitaires aux exports
__all__.extend([
    'get_phase2_statistics', 'print_phase2_summary', 
    'get_all_heroes_summary', 'validate_phase2_implementation',
    'get_tactical_analysis', 'get_loaded_heroes', 'get_loaded_abilities_count'
])

def print_phase2_summary():
    """Affiche un résumé complet - MISE À JOUR PHASE 3+ avec Kraor"""
    stats = get_phase2_statistics()
    
    print("\n" + "="*60)
    print(f"📊 RÉSUMÉ PHASE 3+ - MIGRATION CAPACITÉS INDIVIDUELLES")
    print("="*60)
    
    print(f"🎯 Objectif Phase 3+: 22 capacités individuelles")
    print(f"✅ Réalisé: {stats['total_abilities']}/22 capacités")
    print(f"📈 Progression globale: {stats['progress_percentage']}% ({stats['total_abilities']}/59)")
    
    print(f"\n🎭 Héros complétés:")
    for hero in stats['heroes_completed']:
        print(f"   ✅ {hero}")
    
    print(f"\n📊 Détail par héros:")
    print(f"   🐻 Elneha (P-1): {stats['elneha_abilities']}/6 capacités")
    print(f"   🔮 Liarie (P-2): {stats['liarie_abilities']}/6 capacités")
    if ATUCAN_LOADED:
        print(f"   ⚔️ Atucan (P-3): {stats['atucan_abilities']}/6 capacités")
    if KRAOR_LOADED:
        print(f"   🏹 Kraor (P-4): {stats['kraor_abilities']}/4 capacités combat")  # NOUVEAU
    
    print(f"\n⚙️ Capacités mécaniques estimées: ~{stats['mechanical_abilities_estimate']}")
    print(f"🚀 Prochaine étape: Phase 4 vers {stats['next_phase_target']} capacités")
    
    # Afficher les résumés détaillés si disponibles
    if ELNEHA_LOADED:
        print(f"\n{get_elneha_abilities_summary()}")
    
    if LIARIE_LOADED:
        print(f"\n{get_liarie_abilities_summary()}")
    
    if ATUCAN_LOADED:
        print(f"\n{get_atucan_abilities_summary()}")
    
    if KRAOR_LOADED:  # NOUVEAU
        print(f"\n{get_kraor_abilities_summary()}")
    
    print("\n" + "="*60)
    if stats['total_abilities'] >= 22:
        print("🎉 PHASE 3+ TERMINÉE AVEC SUCCÈS !")
        print("📋 Prochaine étape: Implémenter P-5 Thordius pour Phase 4")
    elif stats['total_abilities'] >= 18:
        print("🎉 PHASE 3 PARTIELLEMENT TERMINÉE - Kraor en cours !")
        print("🏹 Finaliser Kraor pour compléter Phase 3+")
    elif stats['total_abilities'] >= 12:
        print("🎉 PHASE 2 TERMINÉE - Phase 3+ en cours !")
    else:
        print(f"⚠️ PHASE INCOMPLÈTE ({stats['total_abilities']}/22)")
    print("="*60)

def get_all_heroes_summary() -> str:
    """Retourne un résumé de tous les héros implémentés - MISE À JOUR PHASE 3+ avec Kraor"""
    stats = get_phase2_statistics()
    
    summary = f"📚 HÉROS IMPLÉMENTÉS - PHASE 3+:\n\n"
    
    if ELNEHA_LOADED:
        summary += get_elneha_abilities_summary() + "\n"
    
    if LIARIE_LOADED:
        summary += get_liarie_abilities_summary() + "\n"
    
    if ATUCAN_LOADED:
        summary += get_atucan_abilities_summary() + "\n"
    
    if KRAOR_LOADED:  # NOUVEAU
        summary += get_kraor_abilities_summary() + "\n"
    
    summary += f"🔮 TOTAL: {stats['total_abilities']} capacités individuelles sur 59 ({stats['progress_percentage']}%)\n"
    
    return summary

def get_tactical_analysis() -> dict:
    """Analyse tactique des héros disponibles - MISE À JOUR PHASE 3+ avec Kraor"""
    analysis = {
        "phase": "3+",
        "heroes_available": [],
        "synergies": [],
        "combat_roles": {}
    }
    
    if ELNEHA_LOADED:
        analysis["heroes_available"].append("Elneha (P-1)")
        analysis["combat_roles"]["Elneha"] = {
            "primary": "Tank/Healer",
            "secondary": "Shapeshifter",
            "strengths": ["Transformations", "Area healing", "Resurrection"],
            "spell_costs": "1-2 sorts par capacité"
        }
    
    if LIARIE_LOADED:
        analysis["heroes_available"].append("Liarie (P-2)")
        analysis["combat_roles"]["Liarie"] = {
            "primary": "DPS/Control",
            "secondary": "Support",
            "strengths": ["High damage", "No retaliation", "Self-sustain"],
            "spell_costs": "1-4 sorts par capacité"
        }
    
    if ATUCAN_LOADED:
        analysis["heroes_available"].append("Atucan (P-3)")
        analysis["combat_roles"]["Atucan"] = {
            "primary": "Tank/Support",
            "secondary": "Divine DPS",
            "strengths": ["Defensive buffs", "Group healing", "Divine damage"],
            "spell_costs": "1-3 sorts par capacité"
        }
    
    if KRAOR_LOADED:  # NOUVEAU
        analysis["heroes_available"].append("Kraor (P-4)")
        analysis["combat_roles"]["Kraor"] = {
            "primary": "Utility/Support",
            "secondary": "Tactical DPS",
            "strengths": ["Zero spell costs", "Group damage boost", "Multi-target attacks", "Emergency healing"],
            "spell_costs": "0 sorts (toutes gratuites)"
        }
    
    # Synergies mises à jour avec Kraor
    synergies = []
    if ELNEHA_LOADED and LIARIE_LOADED:
        synergies.append("Elneha tank + Liarie DPS = équipe équilibrée")
        synergies.append("Soin multiple d'Elneha + Vol de vie de Liarie = sustain optimal")
    
    if ATUCAN_LOADED and ELNEHA_LOADED:
        synergies.append("Atucan parade + transformations Elneha = tank ultime")
        synergies.append("Double soins: Elneha shapeshifter + Atucan paladin")
    
    if ATUCAN_LOADED and LIARIE_LOADED:
        synergies.append("Atucan support + Liarie DPS = protection + dégâts")
        synergies.append("Châtiment divin + sorts sans riposte = combo magique")
    
    if KRAOR_LOADED and ELNEHA_LOADED:  # NOUVEAU
        synergies.append("Kraor marquage + transformations Elneha = DPS boosté")
        synergies.append("Soins Kraor + résurrection Elneha = support complet")
    
    if KRAOR_LOADED and LIARIE_LOADED:  # NOUVEAU
        synergies.append("Kraor multi-cible + Liarie AoE = contrôle battlefield")
        synergies.append("Kraor gratuit + Liarie coûteuse = équilibre sorts")
    
    if KRAOR_LOADED and ATUCAN_LOADED:  # NOUVEAU
        synergies.append("Kraor double attaque + Atucan buffs = DPS soutenu")
        synergies.append("Kraor tactique + Atucan défensif = support polyvalent")
    
    if ELNEHA_LOADED and LIARIE_LOADED and ATUCAN_LOADED and KRAOR_LOADED:  # NOUVEAU
        synergies.append("Quatuor complet: Tank (Elneha), DPS (Liarie), Support (Atucan), Utility (Kraor)")
        synergies.append("Soins quadruples: Naturels + Magiques + Divins + Tactiques")
        synergies.append("Économie sorts optimale: Kraor gratuit libère sorts pour les autres")
    
    analysis["synergies"] = synergies
    
    return analysis

# ========================================
# VALIDATION ET TESTS - MISE À JOUR KRAOR
# ========================================

def validate_phase2_implementation() -> bool:
    """Valide que toutes les capacités Phase 3+ sont correctement implémentées"""
    try:
        # Vérifier les compteurs
        elneha_count = get_elneha_abilities_count() if ELNEHA_LOADED else 0
        liarie_count = get_liarie_abilities_count() if LIARIE_LOADED else 0
        atucan_count = get_atucan_abilities_count() if ATUCAN_LOADED else 0
        kraor_count = get_kraor_abilities_count() if KRAOR_LOADED else 0  # NOUVEAU
        
        # Vérifications
        success = True
        
        if not ELNEHA_LOADED:
            print(f"❌ Elneha: Module non chargé")
            success = False
        elif elneha_count != 6:
            print(f"❌ Elneha: {elneha_count}/6 capacités")
            success = False
        
        if not LIARIE_LOADED:
            print(f"❌ Liarie: Module non chargé")
            success = False
        elif liarie_count != 6:
            print(f"❌ Liarie: {liarie_count}/6 capacités")
            success = False
        
        if not ATUCAN_LOADED:
            print(f"❌ Atucan: Module non chargé")
            success = False
        elif atucan_count != 6:
            print(f"❌ Atucan: {atucan_count}/6 capacités")
            success = False
        
        if not KRAOR_LOADED:  # NOUVEAU
            print(f"❌ Kraor: Module non chargé")
            success = False
        elif kraor_count != 4:  # Kraor a 4 capacités, pas 6
            print(f"❌ Kraor: {kraor_count}/4 capacités")
            success = False
        
        if success:
            total = elneha_count + liarie_count + atucan_count + kraor_count  # Kraor ajouté
            print(f"✅ Validation réussie: Elneha {elneha_count}/6, Liarie {liarie_count}/6, Atucan {atucan_count}/6, Kraor {kraor_count}/4")
            print(f"🎯 Total Phase 3+: {total}/22 capacités")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False

def get_loaded_heroes():
    """Retourne la liste des héros avec capacités chargées"""
    loaded = []
    
    if ELNEHA_LOADED:
        loaded.append("P-1 (Elneha)")
    if LIARIE_LOADED:
        loaded.append("P-2 (Liarie)")
    if ATUCAN_LOADED:
        loaded.append("P-3 (Atucan)")
    if KRAOR_LOADED:  # NOUVEAU
        loaded.append("P-4 (Kraor)")
    
    return loaded

def get_loaded_abilities_count():
    """Retourne le nombre de capacités individuelles chargées"""
    count = 0
    
    if ELNEHA_LOADED:
        count += get_elneha_abilities_count()
    if LIARIE_LOADED:
        count += get_liarie_abilities_count()
    if ATUCAN_LOADED:
        count += get_atucan_abilities_count()
    if KRAOR_LOADED:  # NOUVEAU
        count += get_kraor_abilities_count()
    
    return count

# ========================================
# INFORMATION DE CHARGEMENT - MISE À JOUR KRAOR
# ========================================

# Afficher un résumé lors de l'import
def _print_loading_summary():
    """Affiche un résumé du chargement lors de l'import"""
    total_loaded = get_loaded_abilities_count()
    heroes_loaded = get_loaded_heroes()
    
    print(f"\n📦 Module héros chargé:")
    print(f"   🎭 Héros: {', '.join(heroes_loaded) if heroes_loaded else 'Aucun'}")
    print(f"   ⚡ Capacités: {total_loaded}/59 ({round(total_loaded/59*100, 1)}%)")
    
    if total_loaded >= 22:
        print(f"   🎉 Phase 3+ complète avec Kraor !")
    elif total_loaded >= 18:
        print(f"   🏹 Phase 3+ avec Kraor en cours...")
    elif total_loaded >= 12:
        print(f"   🎉 Phase 2 complète, Phase 3+ en cours...")
    elif total_loaded >= 2:
        print(f"   ⏳ Phase 2 en cours...")
    else:
        print(f"   🔧 Système en configuration...")

# Exécuter le résumé automatiquement
_print_loading_summary()

# ========================================
# EXPORTS FINAUX
# ========================================

# Ajouter les fonctions utilitaires aux exports
__all__.extend([
    'get_phase2_statistics', 'print_phase2_summary', 
    'get_all_heroes_summary', 'validate_phase2_implementation',
    'get_tactical_analysis', 'get_loaded_heroes', 'get_loaded_abilities_count'
])