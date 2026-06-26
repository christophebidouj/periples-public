# heroes/__init__.py - Point d'entrée des capacités par héros
"""
Point d'entrée pour toutes les capacités individuelles des héros
Phase 3+: Druide (6/6) + Mage (6/6) + Paladin (6/6) + Chasseur (4/6) = 22 capacités totales

Structure:
- Druide (P-1): Druide transformations et soins (6 capacités)
- Mage (P-2): Mage élémentaire offensive/défensive (6 capacités)
- Paladin (P-3): Paladin défensif protection/soins divins (6 capacités)
- Chasseur (P-4): Chasseur tactique support/utility (4 capacités combat)
"""

# ========================================
# IMPORTS DES CAPACITÉS PAR HÉROS
# ========================================

# Import des capacités d'Druide (P-1)
try:
    from .druide import (
        DruideFormeOurs, DruideSoinMineur, DruideFormeLoup,
        DruideSoinMultiple, DruideOndeTonnante, DruideResurrection,
        get_druide_abilities_count, get_druide_abilities_summary
    )
    DRUIDE_LOADED = True
    print("✅ Capacités d'Druide (P-1) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités d'Druide: {e}")
    DRUIDE_LOADED = False

# Import des capacités de Mage (P-2)
try:
    from .mage import (
        MageEclairMagique, MageArmureDuMage, MageMurDeGlace,
        MageBouleDeFeu, MageVolDeVie, MagePluieDeMetéores,
        get_mage_abilities_count, get_mage_abilities_summary,
        get_mage_spell_costs, get_mage_damage_output, get_mage_tactical_analysis
    )
    MAGE_LOADED = True
    print("✅ Capacités de Mage (P-2) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités de Mage: {e}")
    MAGE_LOADED = False

# Import des capacités d'Paladin (P-3)
try:
    from .paladin import (
        PaladinImpositionDesMains, PaladinSensDeLaJustice, PaladinChatimentDivin,
        PaladinAuraSacree, PaladinSoinSuperieur, PaladinJugementDernier,
        get_paladin_abilities_count, get_paladin_abilities_summary,
        get_paladin_spell_costs, get_paladin_tactical_analysis
    )
    PALADIN_LOADED = True
    print("✅ Capacités d'Paladin (P-3) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités d'Paladin: {e}")
    PALADIN_LOADED = False

# Import des capacités de Chasseur (P-4) - NOUVEAU PHASE 3+
try:
    from .chasseur import (
        ChasseurMarqueDuChasseur, ChasseurPluieDeProjectiles, ChasseurSoinMineur, ChasseurTirRapide,
        get_chasseur_abilities_count, get_chasseur_abilities_summary,
        get_chasseur_spell_costs, get_chasseur_combat_limitations, get_chasseur_tactical_analysis,
        validate_chasseur_implementation, get_chasseur_debug_info
    )
    CHASSEUR_LOADED = True
    print("✅ Capacités de Chasseur (P-4) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités de Chasseur: {e}")
    CHASSEUR_LOADED = False

# Import des capacités de Barbare (P-5) - NOUVEAU PHASE 4
try:
    from .barbare import (
        BarbareDefenseSansArmure, BarbareRageDeBerserker, BarbareChargeDeTaureau,
        BarbareTemerité, BarbareCritiqueBrutal, BarbareRageInsatiable
    )
    BARBARE_LOADED = True
    print("✅ Capacités de Barbare (P-5) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités de Barbare: {e}")
    BARBARE_LOADED = False

# Import des capacités de Barde (P-6) - NOUVEAU PHASE 4
try:
    from .barde import (
        BardeAffaiblissement, BardeAccordInterdit, BardeInspiration,
        BardeInvisibilite, BardeSoinMajeur, BardeMotDeMort
    )
    BARDE_LOADED = True
    print("✅ Capacités de Barde (P-6) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités de Barde: {e}")
    BARDE_LOADED = False

# Import des capacités de Roublard (P-7) - NOUVEAU PHASE 4
try:
    from .roublard import (
        RoublardAttaqueFurtive, RoublardDerobade, RoublardBombeFumigene,
        RoublardAttaqueTournoyante, RoublardAssautFurieux
    )
    ROUBLARD_LOADED = True
    print("✅ Capacités de Roublard (P-7) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités de Roublard: {e}")
    ROUBLARD_LOADED = False

# Import des capacités de Pugiliste (P-8) - NOUVEAU PHASE 4
try:
    from .pugiliste import (
        PugilistePointFaible, PugilisteAttaquesMultiples, PugilistePurification,
        PugilisteDelugeDeCups, PugilistePaumeOuverte, PugilisteZuiQuan
    )
    PUGILISTE_LOADED = True
    print("✅ Capacités de Pugiliste (P-8) chargées avec succès")
except ImportError as e:
    print(f"⚠️ Impossible de charger les capacités de Pugiliste: {e}")
    PUGILISTE_LOADED = False

# ========================================
# EXPORTS PUBLICS
# ========================================

__all__ = []

# Druide exports
if DRUIDE_LOADED:
    __all__.extend([
        'DruideFormeOurs', 'DruideSoinMineur', 'DruideFormeLoup',
        'DruideSoinMultiple', 'DruideOndeTonnante', 'DruideResurrection'
    ])

# Mage exports
if MAGE_LOADED:
    __all__.extend([
        'MageEclairMagique', 'MageArmureDuMage', 'MageMurDeGlace',
        'MageBouleDeFeu', 'MageVolDeVie', 'MagePluieDeMetéores'
    ])

# Paladin exports
if PALADIN_LOADED:
    __all__.extend([
        'PaladinImpositionDesMains', 'PaladinSensDeLaJustice', 'PaladinChatimentDivin',
        'PaladinAuraSacree', 'PaladinSoinSuperieur', 'PaladinJugementDernier'
    ])

# Chasseur exports - NOUVEAU
if CHASSEUR_LOADED:
    __all__.extend([
        'ChasseurMarqueDuChasseur', 'ChasseurPluieDeProjectiles', 'ChasseurSoinMineur', 'ChasseurTirRapide'
    ])

# Barbare exports - NOUVEAU PHASE 4
if BARBARE_LOADED:
    __all__.extend([
        'BarbareDefenseSansArmure', 'BarbareRageDeBerserker', 'BarbareChargeDeTaureau',
        'BarbareTemerité', 'BarbareCritiqueBrutal', 'BarbareRageInsatiable'
    ])

# Barde exports - NOUVEAU PHASE 4
if BARDE_LOADED:
    __all__.extend([
        'BardeAffaiblissement', 'BardeAccordInterdit', 'BardeInspiration',
        'BardeInvisibilite', 'BardeSoinMajeur', 'BardeMotDeMort'
    ])

# Roublard exports - NOUVEAU PHASE 4
if ROUBLARD_LOADED:
    __all__.extend([
        'RoublardAttaqueFurtive', 'RoublardDerobade', 'RoublardBombeFumigene',
        'RoublardAttaqueTournoyante', 'RoublardAssautFurieux'
    ])

# Pugiliste exports - NOUVEAU PHASE 4
if PUGILISTE_LOADED:
    __all__.extend([
        'PugilistePointFaible', 'PugilisteAttaquesMultiples', 'PugilistePurification',
        'PugilisteDelugeDeCups', 'PugilistePaumeOuverte', 'PugilisteZuiQuan'
    ])

# ========================================
# STATISTIQUES GLOBALES PHASE 3+
# ========================================

def get_phase2_statistics() -> dict:
    """Retourne les statistiques complètes - MISE À JOUR PHASE 4 avec 8 héros"""

    druide_count = get_druide_abilities_count() if DRUIDE_LOADED else 0
    mage_count = get_mage_abilities_count() if MAGE_LOADED else 0
    paladin_count = get_paladin_abilities_count() if PALADIN_LOADED else 0
    chasseur_count = get_chasseur_abilities_count() if CHASSEUR_LOADED else 0
    barbare_count = 6 if BARBARE_LOADED else 0  # NOUVEAU PHASE 4
    barde_count = 6 if BARDE_LOADED else 0      # NOUVEAU PHASE 4
    roublard_count = 5 if ROUBLARD_LOADED else 0          # NOUVEAU PHASE 4 (5 capacités, P-7-3 désactivée)
    pugiliste_count = 6 if PUGILISTE_LOADED else 0      # NOUVEAU PHASE 4
    total_count = druide_count + mage_count + paladin_count + chasseur_count + barbare_count + barde_count + roublard_count + pugiliste_count
    
    heroes_completed = []
    if DRUIDE_LOADED and druide_count == 6:
        heroes_completed.append("P-1 (Druide)")
    if MAGE_LOADED and mage_count == 6:
        heroes_completed.append("P-2 (Mage)")
    if PALADIN_LOADED and paladin_count == 6:
        heroes_completed.append("P-3 (Paladin)")
    if CHASSEUR_LOADED and chasseur_count == 4:
        heroes_completed.append("P-4 (Chasseur)")
    if BARBARE_LOADED and barbare_count == 6:  # NOUVEAU
        heroes_completed.append("P-5 (Barbare)")
    if BARDE_LOADED and barde_count == 6:  # NOUVEAU
        heroes_completed.append("P-6 (Barde)")
    if ROUBLARD_LOADED and roublard_count == 5:  # NOUVEAU (5 car P-7-3 désactivée)
        heroes_completed.append("P-7 (Roublard)")
    if PUGILISTE_LOADED and pugiliste_count == 6:  # NOUVEAU
        heroes_completed.append("P-8 (Pugiliste)")

    return {
        "phase": "4",  # PHASE 4 COMPLÈTE avec 8 héros
        "heroes_completed": heroes_completed,
        "total_abilities": total_count,
        "druide_abilities": druide_count,
        "mage_abilities": mage_count,
        "paladin_abilities": paladin_count,
        "chasseur_abilities": chasseur_count,
        "barbare_abilities": barbare_count,  # NOUVEAU
        "barde_abilities": barde_count,      # NOUVEAU
        "roublard_abilities": roublard_count,          # NOUVEAU
        "pugiliste_abilities": pugiliste_count,      # NOUVEAU
        "progress_percentage": round((total_count / 59) * 100, 1),
        "mechanical_abilities_estimate": total_count + 2,
        "next_phase_target": 59,  # Phase 5 objectif = toutes capacités
        "loading_status": {
            "druide_loaded": DRUIDE_LOADED,
            "mage_loaded": MAGE_LOADED,
            "paladin_loaded": PALADIN_LOADED,
            "chasseur_loaded": CHASSEUR_LOADED,
            "barbare_loaded": BARBARE_LOADED,  # NOUVEAU
            "barde_loaded": BARDE_LOADED,      # NOUVEAU
            "roublard_loaded": ROUBLARD_LOADED,          # NOUVEAU
            "pugiliste_loaded": PUGILISTE_LOADED       # NOUVEAU
        }
    }

def print_phase2_summary():
    """Affiche un résumé complet - MISE À JOUR PHASE 3+ avec Chasseur"""
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
    print(f"   🐻 Druide (P-1): {stats['druide_abilities']}/6 capacités")
    print(f"   🔮 Mage (P-2): {stats['mage_abilities']}/6 capacités")
    if PALADIN_LOADED:
        print(f"   ⚔️ Paladin (P-3): {stats['paladin_abilities']}/6 capacités")
    if CHASSEUR_LOADED:
        print(f"   🏹 Chasseur (P-4): {stats['chasseur_abilities']}/4 capacités combat")  # NOUVEAU
    
    print(f"\n⚙️ Capacités mécaniques estimées: ~{stats['mechanical_abilities_estimate']}")
    print(f"🚀 Prochaine étape: Phase 4 vers {stats['next_phase_target']} capacités")
    
    # Afficher les résumés détaillés si disponibles
    if DRUIDE_LOADED:
        print(f"\n{get_druide_abilities_summary()}")
    
    if MAGE_LOADED:
        print(f"\n{get_mage_abilities_summary()}")
    
    if PALADIN_LOADED:
        print(f"\n{get_paladin_abilities_summary()}")
    
    if CHASSEUR_LOADED:  # NOUVEAU
        print(f"\n{get_chasseur_abilities_summary()}")
    
    print("\n" + "="*60)
    if stats['total_abilities'] >= 22:
        print("🎉 PHASE 3+ TERMINÉE AVEC SUCCÈS !")
        print("📋 Prochaine étape: Implémenter P-5 Barbare pour Phase 4")
    elif stats['total_abilities'] >= 18:
        print("🎉 PHASE 3 PARTIELLEMENT TERMINÉE - Chasseur en cours !")
        print("🏹 Finaliser Chasseur pour compléter Phase 3+")
    elif stats['total_abilities'] >= 12:
        print("🎉 PHASE 2 TERMINÉE - Phase 3+ en cours !")
    else:
        print(f"⚠️ PHASE INCOMPLÈTE ({stats['total_abilities']}/22)")
    print("="*60)

def get_all_heroes_summary() -> str:
    """Retourne un résumé de tous les héros implémentés - MISE À JOUR PHASE 3+ avec Chasseur"""
    stats = get_phase2_statistics()
    
    summary = f"📚 HÉROS IMPLÉMENTÉS - PHASE 3+:\n\n"
    
    if DRUIDE_LOADED:
        summary += get_druide_abilities_summary() + "\n"
    
    if MAGE_LOADED:
        summary += get_mage_abilities_summary() + "\n"
    
    if PALADIN_LOADED:
        summary += get_paladin_abilities_summary() + "\n"
    
    if CHASSEUR_LOADED:  # NOUVEAU
        summary += get_chasseur_abilities_summary() + "\n"
    
    summary += f"🔮 TOTAL: {stats['total_abilities']} capacités individuelles sur 59 ({stats['progress_percentage']}%)\n"
    
    return summary

def get_tactical_analysis() -> dict:
    """Analyse tactique des héros disponibles - MISE À JOUR PHASE 3+ avec Chasseur"""
    analysis = {
        "phase": "3+",
        "heroes_available": [],
        "synergies": [],
        "combat_roles": {}
    }
    
    if DRUIDE_LOADED:
        analysis["heroes_available"].append("Druide (P-1)")
        analysis["combat_roles"]["Druide"] = {
            "primary": "Tank/Healer",
            "secondary": "Shapeshifter",
            "strengths": ["Transformations", "Area healing", "Resurrection"],
            "spell_costs": "1-2 sorts par capacité"
        }
    
    if MAGE_LOADED:
        analysis["heroes_available"].append("Mage (P-2)")
        analysis["combat_roles"]["Mage"] = {
            "primary": "DPS/Control",
            "secondary": "Support",
            "strengths": ["High damage", "No retaliation", "Self-sustain"],
            "spell_costs": "1-4 sorts par capacité"
        }
    
    if PALADIN_LOADED:
        analysis["heroes_available"].append("Paladin (P-3)")
        analysis["combat_roles"]["Paladin"] = {
            "primary": "Tank/Support",
            "secondary": "Divine DPS",
            "strengths": ["Defensive buffs", "Group healing", "Divine damage"],
            "spell_costs": "1-3 sorts par capacité"
        }
    
    if CHASSEUR_LOADED:  # NOUVEAU
        analysis["heroes_available"].append("Chasseur (P-4)")
        analysis["combat_roles"]["Chasseur"] = {
            "primary": "Utility/Support",
            "secondary": "Tactical DPS",
            "strengths": ["Zero spell costs", "Group damage boost", "Multi-target attacks", "Emergency healing"],
            "spell_costs": "0 sorts (toutes gratuites)"
        }
    
    # Synergies mises à jour avec Chasseur
    synergies = []
    if DRUIDE_LOADED and MAGE_LOADED:
        synergies.append("Druide tank + Mage DPS = équipe équilibrée")
        synergies.append("Soin multiple d'Druide + Vol de vie de Mage = sustain optimal")
    
    if PALADIN_LOADED and DRUIDE_LOADED:
        synergies.append("Paladin parade + transformations Druide = tank ultime")
        synergies.append("Double soins: Druide shapeshifter + Paladin paladin")
    
    if PALADIN_LOADED and MAGE_LOADED:
        synergies.append("Paladin support + Mage DPS = protection + dégâts")
        synergies.append("Châtiment divin + sorts sans riposte = combo magique")
    
    if CHASSEUR_LOADED and DRUIDE_LOADED:  # NOUVEAU
        synergies.append("Chasseur marquage + transformations Druide = DPS boosté")
        synergies.append("Soins Chasseur + résurrection Druide = support complet")
    
    if CHASSEUR_LOADED and MAGE_LOADED:  # NOUVEAU
        synergies.append("Chasseur multi-cible + Mage AoE = contrôle battlefield")
        synergies.append("Chasseur gratuit + Mage coûteuse = équilibre sorts")
    
    if CHASSEUR_LOADED and PALADIN_LOADED:  # NOUVEAU
        synergies.append("Chasseur double attaque + Paladin buffs = DPS soutenu")
        synergies.append("Chasseur tactique + Paladin défensif = support polyvalent")
    
    if DRUIDE_LOADED and MAGE_LOADED and PALADIN_LOADED and CHASSEUR_LOADED:  # NOUVEAU
        synergies.append("Quatuor complet: Tank (Druide), DPS (Mage), Support (Paladin), Utility (Chasseur)")
        synergies.append("Soins quadruples: Naturels + Magiques + Divins + Tactiques")
        synergies.append("Économie sorts optimale: Chasseur gratuit libère sorts pour les autres")
    
    analysis["synergies"] = synergies
    
    return analysis

# ========================================
# VALIDATION ET TESTS - MISE À JOUR CHASSEUR
# ========================================

def validate_phase2_implementation() -> bool:
    """Valide que toutes les capacités Phase 3+ sont correctement implémentées"""
    try:
        # Vérifier les compteurs
        druide_count = get_druide_abilities_count() if DRUIDE_LOADED else 0
        mage_count = get_mage_abilities_count() if MAGE_LOADED else 0
        paladin_count = get_paladin_abilities_count() if PALADIN_LOADED else 0
        chasseur_count = get_chasseur_abilities_count() if CHASSEUR_LOADED else 0  # NOUVEAU
        
        # Vérifications
        success = True
        
        if not DRUIDE_LOADED:
            print(f"❌ Druide: Module non chargé")
            success = False
        elif druide_count != 6:
            print(f"❌ Druide: {druide_count}/6 capacités")
            success = False
        
        if not MAGE_LOADED:
            print(f"❌ Mage: Module non chargé")
            success = False
        elif mage_count != 6:
            print(f"❌ Mage: {mage_count}/6 capacités")
            success = False
        
        if not PALADIN_LOADED:
            print(f"❌ Paladin: Module non chargé")
            success = False
        elif paladin_count != 6:
            print(f"❌ Paladin: {paladin_count}/6 capacités")
            success = False
        
        if not CHASSEUR_LOADED:  # NOUVEAU
            print(f"❌ Chasseur: Module non chargé")
            success = False
        elif chasseur_count != 4:  # Chasseur a 4 capacités, pas 6
            print(f"❌ Chasseur: {chasseur_count}/4 capacités")
            success = False
        
        if success:
            total = druide_count + mage_count + paladin_count + chasseur_count  # Chasseur ajouté
            print(f"✅ Validation réussie: Druide {druide_count}/6, Mage {mage_count}/6, Paladin {paladin_count}/6, Chasseur {chasseur_count}/4")
            print(f"🎯 Total Phase 3+: {total}/22 capacités")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False

def get_loaded_heroes():
    """Retourne la liste des héros avec capacités chargées"""
    loaded = []

    if DRUIDE_LOADED:
        loaded.append("P-1 (Druide)")
    if MAGE_LOADED:
        loaded.append("P-2 (Mage)")
    if PALADIN_LOADED:
        loaded.append("P-3 (Paladin)")
    if CHASSEUR_LOADED:
        loaded.append("P-4 (Chasseur)")
    if BARBARE_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-5 (Barbare)")
    if BARDE_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-6 (Barde)")
    if ROUBLARD_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-7 (Roublard)")
    if PUGILISTE_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-8 (Pugiliste)")

    return loaded

def get_loaded_abilities_count():
    """Retourne le nombre de capacités individuelles chargées"""
    count = 0

    if DRUIDE_LOADED:
        count += get_druide_abilities_count()
    if MAGE_LOADED:
        count += get_mage_abilities_count()
    if PALADIN_LOADED:
        count += get_paladin_abilities_count()
    if CHASSEUR_LOADED:
        count += get_chasseur_abilities_count()
    if BARBARE_LOADED:  # NOUVEAU PHASE 4
        count += 6
    if BARDE_LOADED:  # NOUVEAU PHASE 4
        count += 6
    if ROUBLARD_LOADED:  # NOUVEAU PHASE 4
        count += 5  # P-7-3 désactivée
    if PUGILISTE_LOADED:  # NOUVEAU PHASE 4
        count += 6

    return count

# ========================================
# INFORMATION DE CHARGEMENT - MISE À JOUR CHASSEUR
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
        print(f"   🎉 Phase 3+ complète avec Chasseur !")
    elif total_loaded >= 18:
        print(f"   🏹 Phase 3+ avec Chasseur en cours...")
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
    """Affiche un résumé complet - MISE À JOUR PHASE 3+ avec Chasseur"""
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
    print(f"   🐻 Druide (P-1): {stats['druide_abilities']}/6 capacités")
    print(f"   🔮 Mage (P-2): {stats['mage_abilities']}/6 capacités")
    if PALADIN_LOADED:
        print(f"   ⚔️ Paladin (P-3): {stats['paladin_abilities']}/6 capacités")
    if CHASSEUR_LOADED:
        print(f"   🏹 Chasseur (P-4): {stats['chasseur_abilities']}/4 capacités combat")  # NOUVEAU
    
    print(f"\n⚙️ Capacités mécaniques estimées: ~{stats['mechanical_abilities_estimate']}")
    print(f"🚀 Prochaine étape: Phase 4 vers {stats['next_phase_target']} capacités")
    
    # Afficher les résumés détaillés si disponibles
    if DRUIDE_LOADED:
        print(f"\n{get_druide_abilities_summary()}")
    
    if MAGE_LOADED:
        print(f"\n{get_mage_abilities_summary()}")
    
    if PALADIN_LOADED:
        print(f"\n{get_paladin_abilities_summary()}")
    
    if CHASSEUR_LOADED:  # NOUVEAU
        print(f"\n{get_chasseur_abilities_summary()}")
    
    print("\n" + "="*60)
    if stats['total_abilities'] >= 22:
        print("🎉 PHASE 3+ TERMINÉE AVEC SUCCÈS !")
        print("📋 Prochaine étape: Implémenter P-5 Barbare pour Phase 4")
    elif stats['total_abilities'] >= 18:
        print("🎉 PHASE 3 PARTIELLEMENT TERMINÉE - Chasseur en cours !")
        print("🏹 Finaliser Chasseur pour compléter Phase 3+")
    elif stats['total_abilities'] >= 12:
        print("🎉 PHASE 2 TERMINÉE - Phase 3+ en cours !")
    else:
        print(f"⚠️ PHASE INCOMPLÈTE ({stats['total_abilities']}/22)")
    print("="*60)

def get_all_heroes_summary() -> str:
    """Retourne un résumé de tous les héros implémentés - MISE À JOUR PHASE 3+ avec Chasseur"""
    stats = get_phase2_statistics()
    
    summary = f"📚 HÉROS IMPLÉMENTÉS - PHASE 3+:\n\n"
    
    if DRUIDE_LOADED:
        summary += get_druide_abilities_summary() + "\n"
    
    if MAGE_LOADED:
        summary += get_mage_abilities_summary() + "\n"
    
    if PALADIN_LOADED:
        summary += get_paladin_abilities_summary() + "\n"
    
    if CHASSEUR_LOADED:  # NOUVEAU
        summary += get_chasseur_abilities_summary() + "\n"
    
    summary += f"🔮 TOTAL: {stats['total_abilities']} capacités individuelles sur 59 ({stats['progress_percentage']}%)\n"
    
    return summary

def get_tactical_analysis() -> dict:
    """Analyse tactique des héros disponibles - MISE À JOUR PHASE 3+ avec Chasseur"""
    analysis = {
        "phase": "3+",
        "heroes_available": [],
        "synergies": [],
        "combat_roles": {}
    }
    
    if DRUIDE_LOADED:
        analysis["heroes_available"].append("Druide (P-1)")
        analysis["combat_roles"]["Druide"] = {
            "primary": "Tank/Healer",
            "secondary": "Shapeshifter",
            "strengths": ["Transformations", "Area healing", "Resurrection"],
            "spell_costs": "1-2 sorts par capacité"
        }
    
    if MAGE_LOADED:
        analysis["heroes_available"].append("Mage (P-2)")
        analysis["combat_roles"]["Mage"] = {
            "primary": "DPS/Control",
            "secondary": "Support",
            "strengths": ["High damage", "No retaliation", "Self-sustain"],
            "spell_costs": "1-4 sorts par capacité"
        }
    
    if PALADIN_LOADED:
        analysis["heroes_available"].append("Paladin (P-3)")
        analysis["combat_roles"]["Paladin"] = {
            "primary": "Tank/Support",
            "secondary": "Divine DPS",
            "strengths": ["Defensive buffs", "Group healing", "Divine damage"],
            "spell_costs": "1-3 sorts par capacité"
        }
    
    if CHASSEUR_LOADED:  # NOUVEAU
        analysis["heroes_available"].append("Chasseur (P-4)")
        analysis["combat_roles"]["Chasseur"] = {
            "primary": "Utility/Support",
            "secondary": "Tactical DPS",
            "strengths": ["Zero spell costs", "Group damage boost", "Multi-target attacks", "Emergency healing"],
            "spell_costs": "0 sorts (toutes gratuites)"
        }
    
    # Synergies mises à jour avec Chasseur
    synergies = []
    if DRUIDE_LOADED and MAGE_LOADED:
        synergies.append("Druide tank + Mage DPS = équipe équilibrée")
        synergies.append("Soin multiple d'Druide + Vol de vie de Mage = sustain optimal")
    
    if PALADIN_LOADED and DRUIDE_LOADED:
        synergies.append("Paladin parade + transformations Druide = tank ultime")
        synergies.append("Double soins: Druide shapeshifter + Paladin paladin")
    
    if PALADIN_LOADED and MAGE_LOADED:
        synergies.append("Paladin support + Mage DPS = protection + dégâts")
        synergies.append("Châtiment divin + sorts sans riposte = combo magique")
    
    if CHASSEUR_LOADED and DRUIDE_LOADED:  # NOUVEAU
        synergies.append("Chasseur marquage + transformations Druide = DPS boosté")
        synergies.append("Soins Chasseur + résurrection Druide = support complet")
    
    if CHASSEUR_LOADED and MAGE_LOADED:  # NOUVEAU
        synergies.append("Chasseur multi-cible + Mage AoE = contrôle battlefield")
        synergies.append("Chasseur gratuit + Mage coûteuse = équilibre sorts")
    
    if CHASSEUR_LOADED and PALADIN_LOADED:  # NOUVEAU
        synergies.append("Chasseur double attaque + Paladin buffs = DPS soutenu")
        synergies.append("Chasseur tactique + Paladin défensif = support polyvalent")
    
    if DRUIDE_LOADED and MAGE_LOADED and PALADIN_LOADED and CHASSEUR_LOADED:  # NOUVEAU
        synergies.append("Quatuor complet: Tank (Druide), DPS (Mage), Support (Paladin), Utility (Chasseur)")
        synergies.append("Soins quadruples: Naturels + Magiques + Divins + Tactiques")
        synergies.append("Économie sorts optimale: Chasseur gratuit libère sorts pour les autres")
    
    analysis["synergies"] = synergies
    
    return analysis

# ========================================
# VALIDATION ET TESTS - MISE À JOUR CHASSEUR
# ========================================

def validate_phase2_implementation() -> bool:
    """Valide que toutes les capacités Phase 3+ sont correctement implémentées"""
    try:
        # Vérifier les compteurs
        druide_count = get_druide_abilities_count() if DRUIDE_LOADED else 0
        mage_count = get_mage_abilities_count() if MAGE_LOADED else 0
        paladin_count = get_paladin_abilities_count() if PALADIN_LOADED else 0
        chasseur_count = get_chasseur_abilities_count() if CHASSEUR_LOADED else 0  # NOUVEAU
        
        # Vérifications
        success = True
        
        if not DRUIDE_LOADED:
            print(f"❌ Druide: Module non chargé")
            success = False
        elif druide_count != 6:
            print(f"❌ Druide: {druide_count}/6 capacités")
            success = False
        
        if not MAGE_LOADED:
            print(f"❌ Mage: Module non chargé")
            success = False
        elif mage_count != 6:
            print(f"❌ Mage: {mage_count}/6 capacités")
            success = False
        
        if not PALADIN_LOADED:
            print(f"❌ Paladin: Module non chargé")
            success = False
        elif paladin_count != 6:
            print(f"❌ Paladin: {paladin_count}/6 capacités")
            success = False
        
        if not CHASSEUR_LOADED:  # NOUVEAU
            print(f"❌ Chasseur: Module non chargé")
            success = False
        elif chasseur_count != 4:  # Chasseur a 4 capacités, pas 6
            print(f"❌ Chasseur: {chasseur_count}/4 capacités")
            success = False
        
        if success:
            total = druide_count + mage_count + paladin_count + chasseur_count  # Chasseur ajouté
            print(f"✅ Validation réussie: Druide {druide_count}/6, Mage {mage_count}/6, Paladin {paladin_count}/6, Chasseur {chasseur_count}/4")
            print(f"🎯 Total Phase 3+: {total}/22 capacités")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False

def get_loaded_heroes():
    """Retourne la liste des héros avec capacités chargées"""
    loaded = []

    if DRUIDE_LOADED:
        loaded.append("P-1 (Druide)")
    if MAGE_LOADED:
        loaded.append("P-2 (Mage)")
    if PALADIN_LOADED:
        loaded.append("P-3 (Paladin)")
    if CHASSEUR_LOADED:
        loaded.append("P-4 (Chasseur)")
    if BARBARE_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-5 (Barbare)")
    if BARDE_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-6 (Barde)")
    if ROUBLARD_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-7 (Roublard)")
    if PUGILISTE_LOADED:  # NOUVEAU PHASE 4
        loaded.append("P-8 (Pugiliste)")

    return loaded

def get_loaded_abilities_count():
    """Retourne le nombre de capacités individuelles chargées"""
    count = 0

    if DRUIDE_LOADED:
        count += get_druide_abilities_count()
    if MAGE_LOADED:
        count += get_mage_abilities_count()
    if PALADIN_LOADED:
        count += get_paladin_abilities_count()
    if CHASSEUR_LOADED:
        count += get_chasseur_abilities_count()
    if BARBARE_LOADED:  # NOUVEAU PHASE 4
        count += 6
    if BARDE_LOADED:  # NOUVEAU PHASE 4
        count += 6
    if ROUBLARD_LOADED:  # NOUVEAU PHASE 4
        count += 5  # P-7-3 désactivée
    if PUGILISTE_LOADED:  # NOUVEAU PHASE 4
        count += 6

    return count

# ========================================
# INFORMATION DE CHARGEMENT - MISE À JOUR CHASSEUR
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
        print(f"   🎉 Phase 3+ complète avec Chasseur !")
    elif total_loaded >= 18:
        print(f"   🏹 Phase 3+ avec Chasseur en cours...")
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