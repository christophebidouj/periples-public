# TODO - Système de Capacités Ennemis

## 📊 Vue d'ensemble

Ce fichier trace l'avancement du développement et des tests du système de capacités ennemis pour Périples Balance Workshop.

---

## ✅ PHASES COMPLÉTÉES

### Phase 1 - Immunités et Blocages (TERMINÉE ✅)
**Capacités implémentées:**
- ✅ EA-1: `immunity_stun` - Ne peut pas être Stun (E-77 Manticore, E-85 Tarasque, E-46 Dragon azur, E-47 Sosnen)
- ✅ EA-2: `block_hero_abilities` - Bloque toutes les capacités des héros (E-89 Démon majeur)

### Phase 2 - Attaques Multiples (TERMINÉE ✅)
**Capacités implémentées:**
- ✅ EA-3: `extra_attacks` - Fait 2 attaques par tour (E-46 Dragon azur, E-47 Sosnen)

### Phase 3 - Stun Récurrent (TERMINÉE ✅ - Session du 2025-12-09)
**Capacités implémentées:**
- ✅ EA-4: `stun_hero_permanent` - Stun permanent jusqu'à fin du combat (E-75 Basilic)
- ✅ EA-5: `stun_hero_temporary` - Stun temporaire N tours (E-79 Golem de pierre)

**Bugs corrigés cette session:**
- ✅ Bug #1: Ajout indication visuelle stun sur carte héros (badge "😵 Assommé")
- ✅ Bug #2: Golem de pierre assommait un tour sur deux → Flag `_on_turn_start_triggered` mal réinitialisé
- ✅ Bug #3: Démon majeur ne bloquait pas capacités héros → Debuff non vérifié dans UI + héros non passés à `initialize_combat()`
- ✅ Bug #4: Stun héros ne se décrémentait pas en mode manuel → Restriction `faction == 'enemy'` dans bouton "Nouveau Round"

**Tests validés:**
- ✅ E-75 Basilic - Stun permanent + badge visuel
- ✅ E-79 Golem de pierre - Stun temporaire chaque tour + décompte correct
- ✅ E-89 Démon majeur - Blocage capacités héros fonctionnel

### Phase 4 - Effets Alternés (TERMINÉE ✅ - Session du 2025-12-10)
**Capacités implémentées:**
- ✅ EA-6: `alternating_effects` - Bordalius (Tours pairs: 2 dégâts magiques tous / Tours impairs: stun 1 tour)
- ✅ EA-7: `alternating_effects` - Nécromancien (Tours pairs: 2 dégâts magiques tous / Tours impairs: stun 1 tour)
- ✅ EA-8: `alternating_effects` - Majere (Tours pairs: stun 1 tour / Tours impairs: 6 dégâts magiques tous)

**Mécanisme implémenté:**
- ✅ Utilisation du numéro de round partagé (plus de compteur global)
- ✅ Parser de paramètres even/odd depuis CSV
- ✅ Application automatique des effets selon parité du round
- ✅ Support `damage_all` (dégâts AoE magiques) et `stun_temporary`

**Fichiers modifiés:**
- ✅ `models/enemy_ability_manager.py` - Méthode `_apply_alternating_effects()` avec round_number
- ✅ `ui/components/sandbox_interface_v2.py` - Passage round_number dans contexte + fix stun
- ✅ `models/character.py` - Stats ennemis figées (combat_player_count)
- ✅ `models/combat/combat_actions.py` - Utilisation get_combat_stats()
- ✅ `models/combat/turn_manager.py` - Utilisation get_combat_stats()

**Tests validés:**
- ✅ E-56 Bordalius - Alternance dégâts pairs / stun impairs fonctionnelle
- ✅ E-62 Nécromancien - Alternance + immunité stun validée
- ✅ E-87 Majere - Alternance inversée (stun pairs / dégâts impairs) validée

**Corrections majeures cette session:**
- ✅ Stats ennemis figées au début du combat (ne changent plus si héros meurent)
- ✅ Gestion stun : décrémentation au tour du personnage (non au round global)
- ✅ Effets alternés basés sur numéro de round (non compteur global partagé)
- ✅ Suppression auto-skip ennemis stunnés en mode initiative
- ✅ Autorisation sélection combattants stunnés en mode manuel

### Phase 5 - Effets Périodiques (TERMINÉE ✅ - Session précédente)
**Capacités implémentées:**
- ✅ EA-9: `periodic_stun` - Stun périodique tous les N rounds pendant X tours
- ✅ EA-10: `periodic_damage` - Dégâts périodiques tous les N rounds

**Ennemis concernés:**
- E-46: Dragon azur (EA-9: stun tous les 2 rounds pendant 1 tour, EA-10: 4 dégâts magiques tous les 3 rounds)
- E-47: Sosnen (EA-9: stun tous les 2 rounds pendant 1 tour, EA-10: 4 dégâts magiques tous les 3 rounds)

**Mécanisme implémenté:**
- ✅ Trigger: `after_attack`
- ✅ Utilisation du round_number partagé (comme alternating_effects)
- ✅ Vérification périodique: `round_number % interval == 0`
- ✅ Sélection héros aléatoire pour stun périodique
- ✅ Dégâts AoE pour periodic_damage

**Fichiers modifiés:**
- ✅ `models/enemy_ability_manager.py` - Méthodes `_apply_periodic_stun()` et `_apply_periodic_damage()`

**Tests validés:**
- ✅ E-46 Dragon azur - Stun tous les 2 rounds + dégâts tous les 3 rounds fonctionnels
- ✅ E-47 Sosnen - Stun tous les 2 rounds + dégâts tous les 3 rounds fonctionnels

### Phase 6 - Conditions Spéciales (TERMINÉE ✅ - Session du 2025-12-15)
**Capacités implémentées:**
- ✅ EA-11: `ability_check_stun` - Test de capacité au début du tour (Troll)

**Ennemis concernés:**
- E-73: Troll (EA-11: D20 + niveau capacité < 10 → stun)

**Mécanisme EA-11 (Troll):**
- Trigger: `on_round_start` (début de chaque round, avant tous les tours)
- Teste TOUS les héros vivants individuellement
- Lancer D20 + niveau_capacité (nombre de capacités débloquées 1-6) pour chaque héros
- Si résultat < threshold (10) → stun le héros pour 1 tour
- Sinon, le héros résiste
- Les capacités spéciales (101, 102) ne comptent pas dans le niveau

**Fichiers modifiés:**
- ✅ `models/enemy_ability_manager.py` - Méthode `_apply_ability_check_stun()` ajoutée + logs nettoyés
- ✅ `models/enemy_ability.py` - Nouveau trigger `ON_ROUND_START` ajouté
- ✅ `data/enemy_abilities.csv` - EA-11 trigger changé de `on_turn_start` → `on_round_start`
- ✅ `ui/components/sandbox_interface_v2.py` - Trigger `on_round_start` appelé en mode initiative ET manuel (Round 1 + rounds suivants) + logs nettoyés

**Tests validés:**
- ✅ E-73 Troll - Test de capacité + stun fonctionnels en mode initiative et manuel
- ✅ Logs propres et concis (suppression de tous les logs de debug 🔍)
- ✅ Trigger `on_round_start` déclenché dès le Round 1 en mode manuel

**Note:** E-83 Vouivre reste disponible comme ennemi standard, mais sa capacité EA-12 (attaques à distance) n'est pas implémentée car les mécaniques d'attaques à distance ne sont pas gérées dans l'application.

---

## 🚧 PHASES EN DÉVELOPPEMENT

---

## 🧪 TESTS PHASE 4 - EFFECTUÉS ET VALIDÉS ✅

### Test Phase 4 - Effets Alternés (COMPLÉTÉ)

#### Test 1: E-56 Bordalius (Alternance dégâts/stun) ✅
**Objectif:** Vérifier que Bordalius alterne entre dégâts AoE (tours pairs) et stun (tours impairs)

**Procédure:**
1. Lancer SandboxV2 avec 2+ héros vs E-56 Bordalius
2. **Tour 1 du Bordalius (impair):**
   - Attaquer avec Bordalius
   - **Vérifier:** Log "😵 Bordalius (tour impair) assomme [héros] pour 1 tour(s) !" APRÈS l'attaque
   - **Vérifier:** Un héros est stunné
3. **Tour 2 du Bordalius (pair):**
   - Attaquer avec Bordalius
   - **Vérifier:** Log "💥 Bordalius (tour pair) inflige 2 dégâts magiques à tous les héros !"
   - **Vérifier:** Tous les héros vivants perdent 2 PV
4. **Tour 3 du Bordalius (impair):**
   - **Vérifier:** Retour au stun
5. **Continuer l'alternance** sur 5-6 tours

**Critères de succès:**
- ✅ Tours impairs (1, 3, 5...) = Stun 1 héros pour 1 tour
- ✅ Tours pairs (2, 4, 6...) = 2 dégâts magiques à tous
- ✅ Alternance régulière et prévisible

---

#### Test 2: E-62 Nécromancien (Alternance + immunité)
**Objectif:** Vérifier l'alternance ET l'immunité au stun

**Procédure:**
1. Lancer SandboxV2 avec héros ayant capacité stun vs E-62 Nécromancien
2. **Vérifier immunité:**
   - Tenter de stunner le Nécromancien avec une capacité héros
   - **Vérifier:** Le stun n'a aucun effet (immunité EA-1)
3. **Vérifier alternance (même que Bordalius):**
   - Tours impairs → stun 1 héros
   - Tours pairs → 2 dégâts magiques à tous

**Critères de succès:**
- ✅ Nécromancien ne peut pas être stunné
- ✅ Alternance identique à Bordalius

---

#### Test 3: E-87 Majere (Alternance inversée)
**Objectif:** Vérifier l'alternance inversée (stun pairs / dégâts impairs)

**Procédure:**
1. Lancer SandboxV2 avec 2+ héros vs E-87 Majere
2. **Tour 1 de Majere (impair):**
   - **Vérifier:** Log "💥 Majere (tour impair) inflige 6 dégâts magiques à tous les héros !"
   - **Vérifier:** Tous les héros perdent 6 PV
3. **Tour 2 de Majere (pair):**
   - **Vérifier:** Log "😵 Majere (tour pair) assomme [héros] pour 1 tour(s) !"
   - **Vérifier:** Un héros est stunné
4. **Continuer l'alternance**
5. **Vérifier immunité:** Majere ne peut pas être stunné

**Critères de succès:**
- ✅ Tours pairs (2, 4, 6...) = Stun 1 héros
- ✅ Tours impairs (1, 3, 5...) = 6 dégâts magiques à tous
- ✅ INVERSÉ par rapport à Bordalius/Nécromancien
- ✅ Immunité au stun fonctionnelle

---

## 📝 TESTS DE NON-RÉGRESSION

Après chaque modification, s'assurer que les phases précédentes fonctionnent toujours:

### Checklist de non-régression:
- [ ] E-77 Manticore - Immunité au stun toujours fonctionnelle
- [ ] E-85 Tarasque - Immunité au stun toujours fonctionnelle
- [ ] E-46 Dragon azur - 2 attaques + immunité toujours fonctionnels
- [ ] E-47 Sosnen - 2 attaques toujours fonctionnelles
- [ ] Capacités héros qui stun - Toujours bloquées par immunité ennemie
- [ ] Système de stun unifié - Héros ET ennemis utilisent bien `status_effects['stunned']`

---

## 🐛 BUGS CONNUS

Aucun bug connu actuellement. Les corrections majeures ont été appliquées:
- ✅ Immunité au stun respectée
- ✅ Trigger `on_turn_start` au bon moment
- ✅ Système de stun unifié
- ✅ Interface héros stunné fonctionnelle

---

## 📂 ARCHITECTURE DU SYSTÈME

### Fichiers clés:
```
models/
  ├── enemy_ability.py           # Classe EnemyAbility
  ├── enemy_ability_manager.py   # Gestionnaire d'exécution des capacités
  └── character.py                # Modèles Character et Enemy

ui/components/
  └── sandbox_interface_v2.py     # Intégration UI + triggers + vérification stun

data/
  └── enemy_abilities.csv         # Configuration capacités (triggers, effets, params)

utils/
  └── data_loader.py              # Mapping ennemis → capacités (ENEMY_ABILITY_MAPPING)
```

### Triggers disponibles:
- `on_combat_start` - Une seule fois au début du combat (immunités, blocages)
- `on_round_start` - Au début de chaque round, avant tous les tours (tests capacités Troll)
- `on_turn_start` - Au début de chaque tour de l'ennemi (stun récurrent)
- `before_attack` - Juste avant l'attaque (attaques multiples)
- `after_attack` - Juste après l'attaque (effets alternés, périodiques)
- `on_receive_damage` - Quand l'ennemi reçoit des dégâts (seuils de vie)

### Effets implémentés:
- ✅ `immunity_stun` - Immunité au stun
- ✅ `block_hero_abilities` - Blocage capacités héros
- ✅ `extra_attacks` - Attaques multiples
- ✅ `stun_hero_permanent` - Stun permanent
- ✅ `stun_hero_temporary` - Stun temporaire
- ✅ `alternating_effects` - Effets alternés pairs/impairs
- ✅ `periodic_stun` - Stun périodique
- ✅ `periodic_damage` - Dégâts périodiques
- ✅ `ability_check_stun` - Test de capacité

### Tous les effets sont implémentés ! ✅

---

## 🎯 PRIORITÉS POUR LA PROCHAINE SESSION

### Priorité 1: Phase 5 - Effets Périodiques
1. Implémenter `_apply_periodic_stun()` et `_apply_periodic_damage()`
2. Utiliser le compteur de tour existant (les rounds)
3. Tester E-46 Dragon azur, E-47 Sosnen

### Priorité 2: Phase 6 - Conditions Spéciales
1. Implémenter `_apply_ability_check_stun()` (Troll)
2. Tester E-73 Troll

---

## 📊 STATISTIQUES

**Capacités implémentées:** 11 / 11 (100%) ✅
**Ennemis testés Phase 3:** 3 / 3 (100% - E-75, E-79, E-89) ✅
**Ennemis testés Phase 4:** 3 / 3 (100% - E-56, E-62, E-87) ✅
**Ennemis testés Phase 5:** 2 / 2 (100% - E-46, E-47) ✅
**Ennemis testés Phase 6:** 1 / 1 (100% - E-73) ✅
**Phases complétées:** 6 / 6 (100%) ✅

**Note:** EA-12 (ranged_only_threshold) retirée du développement - les attaques à distance ne sont pas gérées dans l'application.

**Système de capacités ennemis:** COMPLET ✅

---

*Dernière mise à jour: 2025-12-15*
*Session: Phase 6 TERMINÉE ET TESTÉE - Nettoyage logs debug + fix trigger Round 1 mode manuel*
*Développeur: Claude Sonnet 4.5*
