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
        AtucanImpositionDesMains, AtucanSensDeLaJustice, AtucanChatimentDivin,
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
        KraorMarqueDuChasseur, KraorPluieDeProjectiles, KraorSoinMineur, KraorTirRapide,
        get_kraor_abilities_count, get_kraor_abilities_summary,
        get_kraor_spell_costs, get_kraor_combat_limitations, get_kraor_tactical_analysis,
        validate_kraor_implementation, get_kraor_debug_info
    )
    KRAOR_LOADED = True
    print("✅ Capacités de Kraor (P-4) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités de Kraor: {e}")
    KRAOR_LOADED = False

# Import des capacités de Thordius (P-5) - NOUVEAU PHASE 4
try:
    from .thordius import (
        ThordiusDefenseSansArmure, ThordiusRageDeBerserker, ThordiusChargeDeTaureau,
        ThordiusTemerité, ThordiusCritiqueBrutal, ThordiusRageInsatiable
    )
    THORDIUS_LOADED = True
    print("✅ Capacités de Thordius (P-5) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités de Thordius: {e}")
    THORDIUS_LOADED = False

# Import des capacités de Stephe (P-6) - NOUVEAU PHASE 4
try:
    from .stephe import (
        StepheAffaiblissement, StepheAccordInterdit, StepheInspiration,
        StepheInvisibilite, StepheSoinMajeur, StepheMotDeMort
    )
    STEPHE_LOADED = True
    print("✅ Capacités de Stephe (P-6) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités de Stephe: {e}")
    STEPHE_LOADED = False

# Import des capacités de Lame (P-7) - NOUVEAU PHASE 4
try:
    from .lame import (
        LameAttaqueFurtive, LameDerobade, LameBombeFumigene,
        LameAttaqueTournoyante, LameAssautFurieux
    )
    LAME_LOADED = True
    print("✅ Capacités de Lame (P-7) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités de Lame: {e}")
    LAME_LOADED = False

# Import des capacités de Raishi (P-8) - NOUVEAU PHASE 4
try:
    from .raishi import (
        RaishiPointFaible, RaishiAttaquesMultiples, RaishiPurification,
        RaishiDelugeDeCups, RaishiPaumeOuverte, RaishiZuiQuan
    )
    RAISHI_LOADED = True
    print("✅ Capacités de Raishi (P-8) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités de Raishi: {e}")
    RAISHI_LOADED = False

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
        'AtucanImpositionDesMains', 'AtucanSensDeLaJustice', 'AtucanChatimentDivin',
        'AtucanAuraSacree', 'AtucanSoinSuperieur', 'AtucanJugementDernier'
    ])

# Kraor exports - NOUVEAU
if KRAOR_LOADED:
    __all__.extend([
        'KraorMarqueDuChasseur', 'KraorPluieDeProjectiles', 'KraorSoinMineur', 'KraorTirRapide'
    ])

# Thordius exports - NOUVEAU PHASE 4
if THORDIUS_LOADED:
    __all__.extend([
        'ThordiusDefenseSansArmure', 'ThordiusRageDeBerserker', 'ThordiusChargeDeTaureau',
        'ThordiusTemerité', 'ThordiusCritiqueBrutal', 'ThordiusRageInsatiable'
    ])

# Stephe exports - NOUVEAU PHASE 4
if STEPHE_LOADED:
    __all__.extend([
        'StepheAffaiblissement', 'StepheAccordInterdit', 'StepheInspiration',
        'StepheInvisibilite', 'StepheSoinMajeur', 'StepheMotDeMort'
    ])

# Lame exports - NOUVEAU PHASE 4
if LAME_LOADED:
    __all__.extend([
        'LameAttaqueFurtive', 'LameDerobade', 'LameBombeFumigene',
        'LameAttaqueTournoyante', 'LameAssautFurieux'
    ])

# Raishi exports - NOUVEAU PHASE 4
if RAISHI_LOADED:
    __all__.extend([
        'RaishiPointFaible', 'RaishiAttaquesMultiples', 'RaishiPurification',
        'RaishiDelugeDeCups', 'RaishiPaumeOuverte', 'RaishiZuiQuan'
    ])

# ========================================
# STATISTIQUES GLOBALES PHASE 3+
# ========================================

def get_phase2_statistics() -> dict:
    """Retourne les statistiques complètes - MISE À JOUR PHASE 4 avec 8 héros"""

    elneha_count = get_elneha_abilities_count() if ELNEHA_LOADED else 0
    liarie_count = get_liarie_abilities_count() if LIARIE_LOADED else 0
    atucan_count = get_atucan_abilities_count() if ATUCAN_LOADED else 0
    kraor_count = get_kraor_abilities_count() if KRAOR_LOADED else 0
    thordius_count = 6 if THORDIUS_LOADED else 0  # NOUVEAU PHASE 4
    stephe_count = 6 if STEPHE_LOADED else 0      # NOUVEAU PHASE 4
    lame_count = 5 if LAME_LOADED else 0          # NOUVEAU PHASE 4 (5 capacités, P-7-3 désactivée)
    raishi_count = 6 if RAISHI_LOADED else 0      # NOUVEAU PHASE 4
    total_count = elneha_count + liarie_count + atucan_count + kraor_count + thordius_count + stephe_count + lame_count + raishi_count
    
    heroes_completed = []
    if ELNEHA_LOADED and elneha_count == 6:
        heroes_completed.append("P-1 (Elneha)")
    if LIARIE_LOADED and liarie_count == 6:
        heroes_completed.append("P-2 (Liarie)")
    if ATUCAN_LOADED and atucan_count == 6:
        heroes_completed.append("P-3 (Atucan)")
    if KRAOR_LOADED and kraor_count == 4:
        heroes_completed.append("P-4 (Kraor)")
    if THORDIUS_LOADED and thordius_count == 6:  # NOUVEAU
        heroes_completed.append("P-5 (Thordius)")
    if STEPHE_LOADED and stephe_count == 6:  # NOUVEAU
        heroes_completed.append("P-6 (Stephe)")
    if LAME_LOADED and lame_count == 5:  # NOUVEAU (5 car P-7-3 désactivée)
        heroes_completed.append("P-7 (Lame)")
    if RAISHI_LOADED and raishi_count == 6:  # NOUVEAU
        heroes_completed.append("P-8 (Raishi)")

    return {
        "phase": "4",  # PHASE 4 COMPLÈTE avec 8 héros
        "heroes_completed": heroes_completed,
        "total_abilities": total_count,
        "elneha_abilities": elneha_count,
        "liarie_abilities": liarie_count,
        "atucan_abilities": atucan_count,
        "kraor_abilities": kraor_count,
        "thordius_abilities": thordius_count,  # NOUVEAU
        "stephe_abilities": stephe_count,      # NOUVEAU
        "lame_abilities": lame_count,          # NOUVEAU
        "raishi_abilities": raishi_count,      # NOUVEAU
        "progress_percentage": round((total_count / 59) * 100, 1),
        "mechanical_abilities_estimate": total_count + 2,
        "next_phase_target": 59,  # Phase 5 objectif = toutes capacités
        "loading_status": {
            "elneha_loaded": ELNEHA_LOADED,
            "liarie_loaded": LIARIE_LOADED,
            "atucan_loaded": ATUCAN_LOADED,
            "kraor_loaded": KRAOR_LOADED,
            "thordius_loaded": THORDIUS_LOADED,  # NOUVEAU
            "stephe_loaded": STEPHE_LOADED,      # NOUVEAU
            "lame_loaded": LAME_LOADED,          # NOUVEAU
            "raishi_loaded": RAISHI_LOADED       # NOUVEAU
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
    if KRAOR_LOADED:
        loaded.append("P-4 (Kraor)")
    if THORDIUS_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-5 (Thordius)")
    if STEPHE_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-6 (Stephe)")
    if LAME_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-7 (Lame)")
    if RAISHI_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-8 (Raishi)")

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
    if KRAOR_LOADED:
        count += get_kraor_abilities_count()
    if THORDIUS_LOADED:  # NOUVEAU PHASE 4
        count += 6
    if STEPHE_LOADED:  # NOUVEAU PHASE 4
        count += 6
    if LAME_LOADED:  # NOUVEAU PHASE 4
        count += 5  # P-7-3 désactivée
    if RAISHI_LOADED:  # NOUVEAU PHASE 4
        count += 6

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
    if KRAOR_LOADED:
        loaded.append("P-4 (Kraor)")
    if THORDIUS_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-5 (Thordius)")
    if STEPHE_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-6 (Stephe)")
    if LAME_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-7 (Lame)")
    if RAISHI_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-8 (Raishi)")

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
    if KRAOR_LOADED:
        count += get_kraor_abilities_count()
    if THORDIUS_LOADED:  # NOUVEAU PHASE 4
        count += 6
    if STEPHE_LOADED:  # NOUVEAU PHASE 4
        count += 6
    if LAME_LOADED:  # NOUVEAU PHASE 4
        count += 5  # P-7-3 désactivée
    if RAISHI_LOADED:  # NOUVEAU PHASE 4
        count += 6

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