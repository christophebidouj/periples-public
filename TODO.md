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

### Phase 4 - Effets Alternés (IMPLÉMENTÉE ✅ - Session du 2025-12-09)
**Capacités implémentées:**
- ✅ EA-6: `alternating_effects` - Bordalius (Tours pairs: 2 dégâts magiques tous / Tours impairs: stun 1 tour)
- ✅ EA-7: `alternating_effects` - Nécromancien (Tours pairs: 2 dégâts magiques tous / Tours impairs: stun 1 tour)
- ✅ EA-8: `alternating_effects` - Majere (Tours pairs: stun 1 tour / Tours impairs: 6 dégâts magiques tous)

**Mécanisme implémenté:**
- ✅ Compteur global de tours incrémenté au début de chaque tour d'ennemi
- ✅ Parser de paramètres even/odd depuis CSV
- ✅ Application automatique des effets selon parité du tour
- ✅ Support `damage_all` (dégâts AoE magiques) et `stun_temporary`

**Fichiers modifiés:**
- ✅ `models/enemy_ability_manager.py` - Méthode `_apply_alternating_effects()`
- ✅ `ui/components/sandbox_interface_v2.py` - Incrémentation compteur global ligne 1285

**Tests à effectuer (PRIORITÉ):**
- ⏳ E-56 Bordalius - Vérifier alternance dégâts pairs / stun impairs
- ⏳ E-62 Nécromancien - Vérifier alternance + immunité stun
- ⏳ E-87 Majere - Vérifier alternance inversée (stun pairs / dégâts impairs)

---

## 🚧 PHASES EN DÉVELOPPEMENT

### Phase 5 - Effets Périodiques (À IMPLÉMENTER)
**Capacités à implémenter:**
- ⬜ EA-9: `periodic_stun` - Stun périodique (tous les N tours pendant X tours)
- ⬜ EA-10: `periodic_damage` - Dégâts périodiques (tous les N tours)

**Ennemis concernés:**
- E-46: Dragon azur (EA-9: stun tous les 2 tours pendant 1 tour, EA-10: 4 dégâts magiques tous les 3 tours)
- E-47: Sosnen (EA-9: stun tous les 2 tours pendant 1 tour, EA-10: 4 dégâts magiques tous les 3 tours)

**Mécanisme:**
- Trigger: `after_attack`
- Suivre le compteur de tours pour chaque ennemi
- Vérifier si (tour_actuel % interval == 0)
- Appliquer l'effet si condition remplie

**Fichiers à modifier:**
```
models/enemy_ability_manager.py
  - Ajouter méthode _apply_periodic_stun()
  - Ajouter méthode _apply_periodic_damage()
  - Gérer compteur de tours par ennemi

models/character.py
  - Ajouter attribut turn_counter pour suivre les tours
```

**Tests à effectuer:**
- [ ] E-46 Dragon azur - Vérifier stun tous les 2 tours + dégâts tous les 3 tours
- [ ] E-47 Sosnen - Vérifier stun tous les 2 tours + dégâts tous les 3 tours

---

### Phase 6 - Conditions Spéciales (À IMPLÉMENTER)
**Capacités à implémenter:**
- ⬜ EA-11: `ability_check_stun` - Test de capacité au début du tour (Troll)

**Ennemis concernés:**
- E-55: Troll (EA-11: D20 + niveau capacité < 10 → stun)

**Mécanisme EA-11 (Troll):**
- Trigger: `on_turn_start`
- Lancer D20 + niveau_capacité du héros
- Si résultat < 10 → stun le héros
- Appliquer à un héros aléatoire

**Fichiers à modifier:**
```
models/enemy_ability_manager.py
  - Ajouter méthode _apply_ability_check_stun()
```

**Tests à effectuer:**
- [ ] E-55 Troll - Vérifier test de capacité + stun si échec

**Note:** E-71 Vouivre reste disponible comme ennemi standard, mais sa capacité EA-12 (attaques à distance) n'est pas implémentée car les mécaniques d'attaques à distance ne sont pas gérées dans l'application.

---

## 🧪 TESTS PRIORITAIRES À EFFECTUER DEMAIN

### Test Phase 4 - Effets Alternés (PRIORITÉ)

#### Test 1: E-56 Bordalius (Alternance dégâts/stun)
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
- `on_turn_start` - Au début de chaque tour de l'ennemi (stun récurrent, tests)
- `before_attack` - Juste avant l'attaque (attaques multiples)
- `after_attack` - Juste après l'attaque (effets alternés, périodiques)
- `on_receive_damage` - Quand l'ennemi reçoit des dégâts (seuils de vie)

### Effets implémentés:
- ✅ `immunity_stun` - Immunité au stun
- ✅ `block_hero_abilities` - Blocage capacités héros
- ✅ `extra_attacks` - Attaques multiples
- ✅ `stun_hero_permanent` - Stun permanent
- ✅ `stun_hero_temporary` - Stun temporaire

### Effets à implémenter:
- ⬜ `alternating_effects` - Effets alternés pairs/impairs
- ⬜ `periodic_stun` - Stun périodique
- ⬜ `periodic_damage` - Dégâts périodiques
- ⬜ `ability_check_stun` - Test de capacité

---

## 🎯 PRIORITÉS POUR LA PROCHAINE SESSION

### Priorité 1: Tests Phase 3 (URGENT)
1. Tester E-75 Basilic (stun permanent)
2. Tester E-79 Golem de pierre (stun temporaire récurrent)
3. Retester E-89 Démon majeur (blocage capacités)

### Priorité 2: Phase 4 - Effets Alternés
1. Implémenter `_apply_alternating_effects()` dans `enemy_ability_manager.py`
2. Parser paramètres `even:effet,odd:effet`
3. Tester E-37 Bordalius, E-60 Nécromancien, E-72 Majere

### Priorité 3: Phase 5 - Effets Périodiques
1. Implémenter `_apply_periodic_stun()` et `_apply_periodic_damage()`
2. Ajouter compteur de tours par ennemi
3. Tester E-46 Dragon azur, E-47 Sosnen

### Priorité 4: Phase 6 - Conditions Spéciales
1. Implémenter `_apply_ability_check_stun()` (Troll)
2. Tester E-55 Troll

---

## 📊 STATISTIQUES

**Capacités implémentées:** 8 / 11 (73%)
**Ennemis testés Phase 3:** 3 / 3 (100% - E-75, E-79, E-89)
**Ennemis à tester Phase 4:** 0 / 3 (0% - E-56, E-62, E-87)
**Phases complétées:** 4 / 6 (67%)

**Note:** EA-12 (ranged_only_threshold) retirée du développement - les attaques à distance ne sont pas gérées dans l'application.

**Prochaine étape:** Tests Phase 4 → Implémentation Phase 5

---

*Dernière mise à jour: 2025-12-10*
*Session: Mise à jour TODO - Retrait EA-12 (attaques à distance non gérées)*
*Développeur: Claude Sonnet 4.5*
