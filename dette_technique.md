# Dette Technique — Périples Balance Workshop

> Trace les incohérences, les choix de conception discutables, et les améliorations identifiées lors de la code review.
> **Pas de corrections prévues — état des lieux uniquement.**

---

## Format d'une entrée

| Champ | Description |
|---|---|
| **Fichier** | Fichier concerné |
| **Méthode** | Fonction ou classe concernée |
| **Sévérité** | 🔴 Bloquant / 🟠 Significatif / 🟡 Mineur |
| **Type** | Logique métier / Architecture / Performance / Lisibilité |
| **Description** | Ce que le code fait |
| **Problème** | Pourquoi c'est un problème |

---

## Entrées

---

### DT-001 — Pénalité de défaite sans contexte de campagne

| Champ | Détail |
|---|---|
| **Fichier** | `combat_engine.py` |
| **Méthode** | `_apply_defeat()` |
| **Sévérité** | 🟠 Significatif |
| **Type** | Logique métier |

**Description :**
En cas de défaite, la méthode retire 1 sort à chaque héros ayant encore des sorts disponibles. Cette logique est tirée directement des règles officielles V3.0 du jeu de société.

**Problème :**
L'application simule un **combat unique**. De plus, `simulate_single_combat()` n'est jamais appelée en production — le mode automatique a été remplacé par le mode manuel. Les données modifiées par `_apply_defeat()` sont immédiatement abandonnées. La méthode :
- Est trompeuse : donne l'impression que l'app gère une logique de campagne multi-combats
- Constitue un bug silencieux potentiel si une future feature relit ces données post-combat
- Implémente une règle de campagne dans un outil de simulation de combat unique, sans adaptation au contexte

---

### DT-002 — Fonction wrapper morte par inertie d'architecture

| Champ | Détail |
|---|---|
| **Fichier** | `combat_engine.py` |
| **Méthode** | `create_combat_engine_with_abilities()` |
| **Sévérité** | 🟡 Mineur |
| **Type** | Architecture / Lisibilité |

**Description :**
Fonction utilitaire qui modifie `rules.abilities_enabled` puis retourne un `CombatEngine(rules)` standard.

**Problème :**
✅ **Confirmé dead code** — aucun appel dans le projet.
La fonction n'apporte aucune valeur. Elle existe probablement parce qu'à une version précédente, `CombatEngine` acceptait `enable_abilities` comme paramètre direct. Quand l'architecture a changé, l'IA a adapté le contenu de la fonction sans supprimer la fonction elle-même.

---

### DT-003 — Import Streamlit dans la couche logique métier

| Champ | Détail |
|---|---|
| **Fichier** | `combat_engine.py` |
| **Méthode** | `simulate_single_combat()` |
| **Sévérité** | 🟠 Significatif |
| **Type** | Architecture |

**Description :**
`simulate_single_combat()` écrit directement dans `st.session_state` pour stocker les ennemis courants pour le ciblage tactique.

**Problème :**
✅ **Confirmé** — violation de la règle d'architecture du projet : `models/` ne doit jamais importer Streamlit.
- `combat_engine.py` est inutilisable hors Streamlit (tests unitaires impossibles)
- Couplage fort entre logique métier et framework UI

Note : `st.session_state.current_enemies` est lu à 5 endroits dans `sandbox_interface_v2.py` (via un dict `context`) et écrit à 1 endroit dans `combat_engine.py`. Coût de correction modéré.

---

### DT-004 — Code mort post-refactorisation dans `character.py`

| Champ | Détail |
|---|---|
| **Fichier** | `character.py` |
| **Méthode** | `set_form()` + lignes 1182-1188 |
| **Sévérité** | 🟡 Mineur |
| **Type** | Lisibilité |

**Description :**
Lors de la refactorisation du système de transformations d'Elneha, l'ancien code a été conservé par sécurité pendant la transition. Le nouveau système fonctionne via les `individual_abilities`.

**Problème :**
✅ **Confirmé dead code** — `set_form()` porte le tag `# LEGACY` et n'est appelée nulle part dans le projet.
Les lignes 1182-1188 sont commentées avec une note expliquant le conflit avec le nouveau système.

---

### DT-005 — Mode automatique mort mais non supprimé

| Champ | Détail |
|---|---|
| **Fichier** | `combat_engine.py`, `combat_actions.py`, `turn_manager.py` |
| **Méthode** | `simulate_single_combat()` + toute la chaîne IA |
| **Sévérité** | 🟠 Significatif |
| **Type** | Architecture / Lisibilité |

**Description :**
L'application disposait d'un mode "simulation automatique" où l'IA contrôlait les actions des héros. Ce mode a été remplacé par l'interface manuelle (`sandbox_interface_v2.py`).

**Problème :**
`simulate_single_combat()` n'est appelée **nulle part** dans le projet. Toute la chaîne qui en dépend est donc morte :
- `TurnManager.heroes_turn()` (appel IA des actions)
- `try_health_potion()` dans `combat_actions.py`
- `use_health_potion()` et `_choose_best_potion()` dans `character.py`
- `use_potion_action()` dans `sandbox_interface_v2.py`

Ces méthodes restent présentes et pourraient être réutilisées si un mode automatique était réintroduit, mais leur présence crée de la confusion sur ce qui est réellement exécuté.

---

### DT-006 — Double déclaration des attributs d'effets dans `Character`

| Champ | Détail |
|---|---|
| **Fichier** | `character.py` |
| **Méthode** | `model_post_init()` + `_add_required_attributes()` |
| **Sévérité** | 🟡 Mineur |
| **Type** | Lisibilité |

**Description :**
Les attributs du système d'effets (`temporary_buffs`, `permanent_buffs`, `debuffs`, etc.) sont déclarés deux fois : une fois comme champs Pydantic avec `Field(default_factory=dict)` (lignes 144-163), et une fois avec des guards `hasattr` dans `_add_required_attributes()` (lignes 194-222).

**Problème :**
Avec Pydantic, les champs déclarés sont **toujours initialisés** — le `hasattr` est donc superflu. Cette double déclaration est un vestige de l'ajout progressif du système d'effets : les `hasattr` ont été écrits avant que les champs Pydantic soient formalisés, et n'ont jamais été nettoyés.

---

### DT-007 — Duplication `consume_parade_tokens` / `get_parade_status` entre `Character` et `Enemy`

| Champ | Détail |
|---|---|
| **Fichier** | `character.py` |
| **Méthode** | `consume_parade_tokens()`, `get_parade_status()` |
| **Sévérité** | 🟡 Mineur |
| **Type** | Architecture |

**Description :**
Ces deux méthodes sont copiées à l'identique dans `Character` (lignes 553, 669) et `Enemy` (lignes 1807, 1890). La logique est strictement identique.

**Problème :**
`Enemy` hérite de `BaseModel` directement au lieu d'hériter d'une classe commune `Combatant`. Si un bug est corrigé sur l'une, il faut penser à l'autre. Correction propre : créer une classe `Combatant` dont hériteraient `Character` et `Enemy` — refactorisation structurelle non planifiée.

---

### DT-008 — `GameRules` généré depuis le PDF sans lien avec la logique active

| Champ | Détail |
|---|---|
| **Fichier** | `models/rules_engine.py` |
| **Méthode** | Classe `GameRules` entière |
| **Sévérité** | 🟠 Significatif |
| **Type** | Architecture / Lisibilité |

**Description :**
`GameRules` déclare 7 champs de configuration et 4 méthodes. En production, un seul champ est réellement lu par la logique active : `criticals` (dans `combat_actions.py`). Les autres champs (`ranged_attacks`, `magical_damage`, `initiative`, `element_system`, `capacities`) sont définis et parfois passés à `True` dans le sandbox, mais jamais lus. Les 4 méthodes (`get_active_rules`, `is_advanced_mode`, `get_difficulty_modifier`, `get_max_rounds_display`) ne sont appelées nulle part.

**Problème :**
Le fichier a été généré depuis le PDF de règles comme une liste de features futures, sans vérifier ce qui était réellement implémenté. `magical_damage` en est l'exemple le plus trompeur : la logique réelle utilise `enemy.has_magical_damage` (attribut sur l'objet), pas `rules.magical_damage`.

---

### DT-009 — Méthodes mortes dans `InitiativeManager`

| Champ | Détail |
|---|---|
| **Fichier** | `models/combat/initiative_manager.py` |
| **Méthode** | `reroll_initiative()` · `get_turn_order_summary()` |
| **Sévérité** | 🟡 Mineur |
| **Type** | Lisibilité |

**Description :**
`reroll_initiative` ne fait qu'appeler `roll_initiative` — wrapper inutile. `get_turn_order_summary` génère un résumé compact de l'ordre des tours. Aucune des deux n'est appelée dans le projet.

**Problème :**
Même pattern que DT-008 — méthodes utilitaires anticipatoires générées depuis les règles, jamais branchées.

---

### DT-010 — Rustine d'initialisation des capacités 101/102 d'Elneha

| Champ | Détail |
|---|---|
| **Fichier** | `character.py` |
| **Méthode** | `start_new_combat()` |
| **Sévérité** | 🟡 Mineur |
| **Type** | Architecture |

**Description :**
`start_new_combat` ajoute 101 et 102 dans `unlocked_abilities` alors qu'Elneha est en forme humaine. Ces capacités sont pourtant exclusives à leurs formes (ours/loup) et protégées par `can_use_ability()` dans chaque classe. Deux mécanismes font la même chose.

**Problème :**
`unlocked_abilities` est censé être la source de vérité sur ce qui est disponible en UI, mais la vraie barrière est dans `can_use_ability()`. Le guard défensif dans `start_new_combat` est redondant. `start_new_combat` ne devrait pas avoir à connaître les numéros 101 et 102.

---

### DT-011 — Copie de logique `Character` dans `Enemy` sans adaptation au contexte

| Champ | Détail |
|---|---|
| **Fichier** | `character.py` |
| **Méthode** | `Enemy.is_alive()` |
| **Sévérité** | 🟡 Mineur |
| **Type** | Logique métier / Lisibilité |

**Description :**
`Enemy.is_alive()` contient un check `berserker_rage_active` dans `temporary_buffs` avec le commentaire "Berserker rage (Thordius P-5-6)". La rage du berserker est une capacité du héros Thordius — elle lui permet de continuer à attaquer même à 0 PV.

**Problème :**
`Enemy` ne déclare pas de champ `temporary_buffs` (ses champs d'effets sont `debuffs`, `status_effects`, `marks`). `hasattr(self, 'temporary_buffs')` est donc **toujours `False`** sur un ennemi — le check ne se déclenche jamais. Dead code.

Le pattern a été copié de `Character` dans `Enemy` sans adaptation au contexte. Le commentaire lui-même ("Thordius P-5-6") révèle que la logique ciblait le héros, pas l'ennemi.

---

### DT-012 — `is_special_object()` ne filtre pas les vrais objets spéciaux

| Champ | Détail |
|---|---|
| **Fichier** | `character.py` |
| **Méthode** | `Equipment.is_special_object()` |
| **Sévérité** | 🟡 Mineur |
| **Type** | Logique métier / Lisibilité |

**Description :**
Le docstring indique `"Vérifie si c'est un objet spécial (O-1 à O-4)"` mais l'implémentation fait `return self.code.startswith('O-')`, ce qui retourne `True` pour tous les équipements du projet sans exception (O-5, O-11, O-35, etc.).

**Problème :**
Le docstring et le code ne correspondent pas. La méthode devrait être `return self.code in ('O-1', 'O-2', 'O-3', 'O-4')` pour correspondre à l'intention. En l'état, `is_special` est toujours `True` dans `get_equipment_summary()`, ce qui rend le champ inutile.

---

### DT-013 — `TurnManager` quasi-mort et logique de tours manuels dans l'UI

| Champ | Détail |
|---|---|
| **Fichier** | `models/combat/turn_manager.py` · `ui/components/sandbox_interface_v2.py` |
| **Méthode** | `TurnManager` entier · gestion tours dans sandbox |
| **Sévérité** | 🟠 Significatif |
| **Type** | Architecture |

**Description :**
`TurnManager` est instancié dans `SandboxTurnManagerAdapter` mais aucune de ses méthodes de gestion de tours n'est appelée en production. `heroes_turn`, `enemies_turn`, `hero_turn`, `pet_turn`, `heroes_distribute_damage` sont toutes du dead code.

La gestion des tours en mode manuel est entièrement dans `sandbox_interface_v2.py`. `SandboxTurnManagerAdapter` appelle directement `hero.start_hero_turn()` et `enemy.start_enemy_turn()` — `TurnManager` n'intervient pas. `enemy_ability_manager` aurait pu être passé directement à l'adaptateur sans instancier `TurnManager`.

**Problème :**
Double problème : `TurnManager` est quasi-mort et instancié inutilement, et la logique de tours (logique métier) se trouve dans le fichier UI le plus volumineux du projet (4726 lignes). La solution propre serait un `ManualTurnManager` dans `models/` gérant le pointeur de tour et l'état des actions.

---

### DT-014 — Matching textuel fragile dans `_identify_persistent_effect`

| Champ | Détail |
|---|---|
| **Fichier** | `models/combat/abilities/persistent_effects.py` |
| **Méthode** | `_identify_persistent_effect()` |
| **Sévérité** | 🟠 Significatif |
| **Type** | Logique métier / Robustesse |

**Description :**
`_identify_persistent_effect` identifie quel effet persistant correspond à une capacité en faisant un matching textuel sur `ability.name.lower()`. Un dict hard-codé mappe des chaînes comme `'zui quan'` → `'zui_quan'` ou `'invisibilité'` → `'invisibilite'`.

**Problème :**
`ability.unique_id` est disponible sur chaque capacité et constitue un identifiant stable. Un mapping `"P-8_2" → 'zui_quan'` ne casse jamais. En l'état, si un nom de capacité change dans le CSV ou l'Excel source, le matching échoue silencieusement — l'effet persistant n'est plus activé, sans erreur levée.

L'IA a optimisé pour la lisibilité immédiate du code au détriment de la robustesse à la maintenance.

---

### DT-015 — `safe_randint` mal placée et import mort

| Champ | Détail |
|---|---|
| **Fichier** | `utils/data_loader.py` · `models/combat/combat_logger.py` |
| **Méthode** | `safe_randint()` |
| **Sévérité** | 🟡 Mineur |
| **Type** | Architecture / Lisibilité |

**Description :**
`safe_randint` est une fonction utilitaire de calcul définie dans `data_loader.py` — une couche de chargement de données. Elle est importée dans `combat_logger.py` (ligne 162) mais n'est jamais appelée dans la fonction qui l'importe.

**Problème :**
Double problème : mauvais emplacement (une fonction de calcul dans la couche données) et import mort dans `combat_logger.py`. La fonction aurait sa place dans un module utilitaire dédié dans `models/` ou `utils/`.

---

### DT-016 — Champs `effects` et `target_type` peuplés par heuristiques, jamais consommés en combat

| Champ | Détail |
|---|---|
| **Fichier** | `utils/abilities_loader.py` |
| **Méthode** | `_create_simple_effects()` · `_guess_target_type()` |
| **Sévérité** | 🟡 Mineur |
| **Type** | Architecture / Lisibilité |

**Description :**
`_create_simple_effects` détecte des mots-clés dans la description ("soin", "dégât"...) pour créer des `AbilityEffect`. `_guess_target_type` fait de même pour déterminer le `TargetType`. Ces deux champs sont peuplés sur chaque objet `Ability` au chargement.

**Problème :**
Le moteur de combat (`AbilityEffectsManager`) appelle `BaseAbility.execute()` — il ignore complètement `Ability.effects` et `Ability.target_type`. Ces champs ne sont lus qu'à un seul endroit hors du loader : `enemy_editor.py:211` pour un affichage UI. Jamais pour du calcul.

L'IA a "complété" l'objet `Ability` de façon exhaustive par réflexe, sans vérifier si ces champs étaient réellement consommés. Les heuristiques produisent des résultats approximatifs pour des données inutilisées.

---

## Suivi

| ID | Fichier | Sévérité | Statut |
|---|---|---|---|
| DT-001 | `combat_engine.py` | 🟠 Significatif | ✅ Confirmé |
| DT-002 | `combat_engine.py` | 🟡 Mineur | ✅ Confirmé dead code |
| DT-003 | `combat_engine.py` | 🟠 Significatif | ✅ Confirmé |
| DT-004 | `character.py` | 🟡 Mineur | ✅ Confirmé dead code |
| DT-005 | `combat_engine.py` + chaîne | 🟠 Significatif | ✅ Confirmé |
| DT-006 | `character.py` | 🟡 Mineur | ✅ Confirmé |
| DT-007 | `character.py` | 🟡 Mineur | ✅ Confirmé |
| DT-008 | `rules_engine.py` | 🟠 Significatif | ✅ Corrigé — fichier nettoyé, seuls `criticals` et `max_rounds` conservés |
| DT-009 | `initiative_manager.py` | 🟡 Mineur | ✅ Confirmé dead code |
| DT-010 | `character.py` | 🟡 Mineur | ✅ Confirmé |
| DT-011 | `character.py` | 🟡 Mineur | ✅ Confirmé dead code |
| DT-012 | `character.py` | 🟡 Mineur | ✅ Confirmé |
| DT-013 | `sandbox_interface_v2.py` | 🟠 Significatif | ✅ Confirmé |
| DT-014 | `persistent_effects.py` | 🟠 Significatif | ✅ Confirmé |
| DT-015 | `data_loader.py` · `combat_logger.py` | 🟡 Mineur | ✅ Confirmé |
| DT-016 | `abilities_loader.py` | 🟡 Mineur | ✅ Confirmé |

---

*Dernière mise à jour : session review 5 H17 — 2026-05-31*
