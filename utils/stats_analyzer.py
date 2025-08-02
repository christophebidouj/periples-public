from typing import Dict, List, Any, Tuple
import pandas as pd

class StatsAnalyzer:
    """Analyseur de statistiques de combat pour l'équilibrage RPG"""
    
    @staticmethod
    def analyze_rpg_balance(results: Dict[str, Any], heroes_count: int) -> Dict[str, Any]:
        """Analyse selon les standards RPG/D&D - Focus sur survie et attrition"""
        
        stats = results['stats']
        win_rate = (stats['hero_wins'] / stats['total_combats']) * 100
        avg_survivors = stats['average_survivors']
        avg_rounds = stats['average_rounds']
        
        # 1. SURVIE (priorité absolue - les héros ne doivent pas mourir)
        survival_rate = (avg_survivors / heroes_count) * 100 if heroes_count > 0 else 0
        
        if survival_rate < 90:
            survival_status = {
                "level": "CRITIQUE", 
                "color": "🔴", 
                "message": "Trop de morts - frustrant pour les joueurs",
                "recommendation": "URGENT: Réduire drastiquement la difficulté"
            }
        elif survival_rate < 95:
            survival_status = {
                "level": "PROBLÉMATIQUE", 
                "color": "🟠", 
                "message": "Risque de TPK (Total Party Kill) trop élevé",
                "recommendation": "Réduire dégâts ennemis ou augmenter défense héros"
            }
        elif survival_rate > 99:
            survival_status = {
                "level": "TROP FACILE", 
                "color": "🔵", 
                "message": "Pas assez de tension dramatique",
                "recommendation": "Augmenter légèrement la difficulté"
            }
        else:
            survival_status = {
                "level": "OPTIMAL", 
                "color": "🟢", 
                "message": "Parfait - tension sans frustration",
                "recommendation": "Maintenir cet équilibrage"
            }
        
        # 2. ATTRITION (état des héros survivants)
        # Estimation: plus il y a de survivants, moins ils sont individuellement blessés
        estimated_health_remaining = min(85, survival_rate * 0.8)
        
        if estimated_health_remaining > 70:
            attrition_status = {
                "level": "FAIBLE", 
                "color": "🔵", 
                "message": "Héros peu entamés - manque de challenge",
                "recommendation": "Augmenter dégâts ennemis pour plus d'attrition"
            }
        elif estimated_health_remaining > 50:
            attrition_status = {
                "level": "OPTIMALE", 
                "color": "🟢", 
                "message": "Héros blessés mais opérationnels - parfait",
                "recommendation": "Équilibrage idéal pour l'attrition"
            }
        elif estimated_health_remaining > 30:
            attrition_status = {
                "level": "ÉLEVÉE", 
                "color": "🟡", 
                "message": "Héros très affaiblis mais vivants",
                "recommendation": "Acceptable mais surveiller la frustration"
            }
        else:
            attrition_status = {
                "level": "CRITIQUE", 
                "color": "🔴", 
                "message": "Héros en état critique - trop dur",
                "recommendation": "Réduire dégâts ou augmenter soins disponibles"
            }
        
        # 3. DURÉE DE COMBAT (tactique vs tedieux)
        if avg_rounds < 3:
            duration_status = {
                "level": "TRÈS COURT", 
                "color": "🔴", 
                "message": "Combat expédié - pas de tactique possible",
                "recommendation": "Augmenter PV ou réduire dégâts pour rallonger"
            }
        elif avg_rounds < 6:
            duration_status = {
                "level": "COURT", 
                "color": "🟡", 
                "message": "Rapide mais acceptable",
                "recommendation": "Peut être allongé pour plus de tactique"
            }
        elif avg_rounds <= 12:
            duration_status = {
                "level": "OPTIMAL", 
                "color": "🟢", 
                "message": "Durée parfaite - épique et tactique",
                "recommendation": "Durée idéale pour l'engagement"
            }
        elif avg_rounds <= 18:
            duration_status = {
                "level": "LONG", 
                "color": "🟡", 
                "message": "Combat épique mais commence à traîner",
                "recommendation": "Acceptable pour boss, trop long pour mobs"
            }
        else:
            duration_status = {
                "level": "TROP LONG", 
                "color": "🔴", 
                "message": "Risque d'ennui et lassitude",
                "recommendation": "Augmenter dégâts pour accélérer"
            }
        
        # 4. SCORE GLOBAL RPG (pondéré selon l'importance D&D)
        rpg_score = StatsAnalyzer._calculate_rpg_score(survival_rate, avg_rounds, estimated_health_remaining)
        
        # 5. ÉVALUATION GLOBALE
        global_assessment = StatsAnalyzer._get_global_assessment(rpg_score, survival_status, duration_status)
        
        return {
            'survival_analysis': survival_status,
            'attrition_analysis': attrition_status, 
            'duration_analysis': duration_status,
            'rpg_score': rpg_score,
            'global_assessment': global_assessment,
            'recommendations': StatsAnalyzer._generate_rpg_recommendations(survival_status, duration_status, attrition_status),
            'raw_metrics': {
                'survival_rate': survival_rate,
                'estimated_health': estimated_health_remaining,
                'avg_rounds': avg_rounds,
                'win_rate': win_rate
            }
        }
    
    @staticmethod
    def _calculate_rpg_score(survival_rate: float, avg_rounds: float, health_remaining: float) -> int:
        """Calcule le score RPG pondéré (survie = priorité absolue)"""
        score = 0
        
        # SURVIE = 60% du score (priorité absolue en RPG)
        if 95 <= survival_rate <= 98:
            score += 60  # Parfait
        elif 90 <= survival_rate < 95:
            score += 45  # Acceptable
        elif 85 <= survival_rate < 90:
            score += 25  # Problématique
        elif survival_rate >= 99:
            score += 40  # Trop facile mais pas dramatique
        # < 85% = 0 points (inacceptable)
        
        # DURÉE = 25% du score
        if 6 <= avg_rounds <= 12:
            score += 25  # Optimal
        elif 4 <= avg_rounds < 6 or 12 < avg_rounds <= 16:
            score += 18  # Bon
        elif 3 <= avg_rounds < 4 or 16 < avg_rounds <= 20:
            score += 10  # Acceptable
        # Autres = 0 points
        
        # ATTRITION = 15% du score
        if 40 <= health_remaining <= 65:
            score += 15  # Parfait équilibre
        elif 30 <= health_remaining < 40 or 65 < health_remaining <= 75:
            score += 10  # Bon
        elif health_remaining > 75:
            score += 5   # Trop facile
        # < 30% = 0 points (trop dur)
        
        return min(100, max(0, score))
    
    @staticmethod
    def _get_global_assessment(score: int, survival_status: Dict, duration_status: Dict) -> Dict[str, str]:
        """Évaluation globale du système"""
        
        # La survie prime sur tout
        if survival_status['level'] == 'CRITIQUE':
            return {
                "level": "INACCEPTABLE",
                "color": "🔴",
                "message": "Système déséquilibré - trop de morts de héros",
                "action": "Révision majeure nécessaire"
            }
        
        if score >= 85:
            return {
                "level": "EXCELLENT",
                "color": "🟢", 
                "message": "Équilibrage RPG exemplaire - prêt pour publication",
                "action": "Maintenir ces paramètres"
            }
        elif score >= 70:
            return {
                "level": "TRÈS BON",
                "color": "🟢",
                "message": "Bon équilibrage avec ajustements mineurs",
                "action": "Peaufinage recommandé"
            }
        elif score >= 55:
            return {
                "level": "CORRECT",
                "color": "🟡",
                "message": "Fonctionnel mais perfectible", 
                "action": "Ajustements recommandés"
            }
        elif score >= 40:
            return {
                "level": "PROBLÉMATIQUE",
                "color": "🟠",
                "message": "Déséquilibres importants",
                "action": "Modifications nécessaires"
            }
        else:
            return {
                "level": "CRITIQUE",
                "color": "🔴",
                "message": "Système mal équilibré",
                "action": "Refonte complète requise"
            }
    
    @staticmethod
    def _generate_rpg_recommendations(survival_status: Dict, duration_status: Dict, attrition_status: Dict) -> List[Dict]:
        """Génère des recommandations spécifiques RPG avec priorités"""
        recommendations = []
        
        # PRIORITÉ 1: Survie (critique pour l'expérience RPG)
        if survival_status['level'] in ['CRITIQUE', 'PROBLÉMATIQUE']:
            recommendations.append({
                'priority': 'URGENT',
                'category': '🛡️ Survie des héros',
                'action': survival_status['recommendation'],
                'impact': 'Éviter la frustration et l\'abandon des joueurs',
                'specifics': [
                    "Réduire dégâts ennemis de 10-20%",
                    "Augmenter PV héros de 15-25%", 
                    "Ajouter objets de soins",
                    "Réduire nombre d'ennemis par combat"
                ]
            })
        
        # PRIORITÉ 2: Durée (impact sur le plaisir tactique)
        if duration_status['level'] in ['TRÈS COURT', 'TROP LONG']:
            priority = 'IMPORTANT' if duration_status['level'] == 'TROP LONG' else 'MOYEN'
            recommendations.append({
                'priority': priority,
                'category': '⏱️ Durée de combat',
                'action': duration_status['recommendation'],
                'impact': 'Optimiser l\'engagement et éviter l\'ennui',
                'specifics': [
                    "Ajuster PV ennemis ±20%",
                    "Modifier dégâts héros ±15%",
                    "Réviser initiative et ordre de jeu"
                ] if duration_status['level'] == 'TROP LONG' else [
                    "Augmenter PV ennemis +30-50%",
                    "Réduire dégâts héros -15%",
                    "Ajouter mécaniques défensives"
                ]
            })
        
        # PRIORITÉ 3: Attrition (finesse de l'équilibrage)
        if attrition_status['level'] in ['FAIBLE', 'CRITIQUE']:
            recommendations.append({
                'priority': 'MOYEN' if attrition_status['level'] == 'FAIBLE' else 'IMPORTANT',
                'category': '💔 Gestion de l\'attrition',
                'action': attrition_status['recommendation'],
                'impact': 'Créer la tension dramatique appropriée',
                'specifics': [
                    "Ajuster dégâts ennemis ±10%",
                    "Réviser disponibilité des soins",
                    "Équilibrer défenses vs attaques"
                ]
            })
        
        # Recommandation de maintenance si tout va bien
        if not recommendations:
            recommendations.append({
                'priority': 'MAINTENANCE',
                'category': '✅ Équilibrage optimal',
                'action': 'Surveiller lors des modifications futures',
                'impact': 'Maintenir la qualité de l\'expérience',
                'specifics': [
                    "Tester avec différents groupes de joueurs",
                    "Vérifier l\'équilibrage sur toute la campagne",
                    "Documenter ces paramètres comme référence"
                ]
            })
        
        return recommendations
    
    @staticmethod
    def analyze_balance_legacy(win_rate: float) -> Dict[str, str]:
        """Ancienne analyse basée uniquement sur le taux de victoire (gardée pour compatibilité)"""
        
        if win_rate > 70:
            return {
                "status": "too_easy",
                "color": "success", 
                "icon": "🟢",
                "message": "Combat trop facile pour les héros",
                "recommendation": "Augmenter la difficulté des ennemis ou réduire les stats des héros",
                "priority": "high"
            }
        elif win_rate < 30:
            return {
                "status": "too_hard",
                "color": "error",
                "icon": "🔴",
                "message": "Combat trop difficile pour les héros", 
                "recommendation": "Réduire la difficulté des ennemis ou améliorer les héros",
                "priority": "high"
            }
        elif win_rate < 40:
            return {
                "status": "hard",
                "color": "warning",
                "icon": "🟠",
                "message": "Combat difficile mais acceptable",
                "recommendation": "Surveiller l'équilibrage, possibilité d'ajustement léger",
                "priority": "medium"
            }
        elif win_rate > 60:
            return {
                "status": "easy",
                "color": "info",
                "icon": "🔵",
                "message": "Combat facile mais acceptable",
                "recommendation": "Surveiller l'équilibrage, possibilité d'ajustement léger",
                "priority": "medium"
            }
        else:
            return {
                "status": "balanced",
                "color": "success",
                "icon": "🟡",
                "message": "Combat bien équilibré",
                "recommendation": "Équilibrage optimal, maintenir ces paramètres",
                "priority": "low"
            }
    
    @staticmethod
    def compare_rpg_configurations(results_a: Dict[str, Any], results_b: Dict[str, Any], 
                                  heroes_count: int,
                                  config_a_name: str = "Configuration A", 
                                  config_b_name: str = "Configuration B") -> Dict[str, Any]:
        """Compare deux configurations selon les critères RPG"""
        
        analysis_a = StatsAnalyzer.analyze_rpg_balance(results_a, heroes_count)
        analysis_b = StatsAnalyzer.analyze_rpg_balance(results_b, heroes_count)
        
        metrics_a = analysis_a['raw_metrics']
        metrics_b = analysis_b['raw_metrics']
        
        comparison = {
            'survival_diff': metrics_b['survival_rate'] - metrics_a['survival_rate'],
            'rounds_diff': metrics_b['avg_rounds'] - metrics_a['avg_rounds'],
            'health_diff': metrics_b['estimated_health'] - metrics_a['estimated_health'],
            'score_diff': analysis_b['rpg_score'] - analysis_a['rpg_score'],
            'better_config': None,
            'improvements': [],
            'analysis_a': analysis_a,
            'analysis_b': analysis_b
        }
        
        # Détermination de la meilleure configuration
        if analysis_b['rpg_score'] > analysis_a['rpg_score']:
            comparison['better_config'] = config_b_name
            comparison['improvements'] = [
                f"Score RPG: +{comparison['score_diff']} points",
                f"Survie: {comparison['survival_diff']:+.1f}%",
                f"Durée: {comparison['rounds_diff']:+.1f} rounds"
            ]
        elif analysis_a['rpg_score'] > analysis_b['rpg_score']:
            comparison['better_config'] = config_a_name
            comparison['improvements'] = [
                f"Score RPG: +{-comparison['score_diff']} points", 
                f"Survie: {-comparison['survival_diff']:+.1f}%",
                f"Durée: {-comparison['rounds_diff']:+.1f} rounds"
            ]
        else:
            comparison['better_config'] = "Configurations équivalentes"
            comparison['improvements'] = ["Performances similaires"]
        
        return comparison
    
    @staticmethod
    def generate_rpg_report(results: Dict[str, Any], heroes_count: int) -> str:
        """Génère un rapport textuel complet selon les standards RPG"""
        
        analysis = StatsAnalyzer.analyze_rpg_balance(results, heroes_count)
        stats = results['stats']
        
        report = f"""
=== RAPPORT D'ÉQUILIBRAGE RPG ===

📊 MÉTRIQUES PRINCIPALES:
- Combats simulés: {stats['total_combats']}
- Taux de victoire: {analysis['raw_metrics']['win_rate']:.1f}%
- Taux de survie: {analysis['raw_metrics']['survival_rate']:.1f}%
- Durée moyenne: {stats['average_rounds']:.1f} rounds
- État estimé des héros: {analysis['raw_metrics']['estimated_health']:.1f}% PV

🎯 ÉVALUATION GLOBALE: {analysis['global_assessment']['level']}
{analysis['global_assessment']['message']}

🛡️ SURVIE: {analysis['survival_analysis']['level']} {analysis['survival_analysis']['color']}
{analysis['survival_analysis']['message']}

⏱️ DURÉE: {analysis['duration_analysis']['level']} {analysis['duration_analysis']['color']}
{analysis['duration_analysis']['message']}

💔 ATTRITION: {analysis['attrition_analysis']['level']} {analysis['attrition_analysis']['color']}
{analysis['attrition_analysis']['message']}

📈 SCORE RPG: {analysis['rpg_score']}/100

💡 RECOMMANDATIONS PRIORITAIRES:
"""
        
        for i, rec in enumerate(analysis['recommendations'], 1):
            report += f"\n{i}. [{rec['priority']}] {rec['category']}"
            report += f"\n   Action: {rec['action']}"
            report += f"\n   Impact: {rec['impact']}"
            if 'specifics' in rec:
                report += f"\n   Détails: {', '.join(rec['specifics'][:2])}..."
            report += "\n"
        
        return report.strip()