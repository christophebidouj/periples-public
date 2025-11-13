# Plan de Développement Sandbox - Vérifié Conforme aux Règles Officielles

**Date de création** : 28 octobre 2025  
**Version** : 1.0  
**Statut** : Vérifié et validé avec le Livre de règles V3.0

---

## 🎯 Objectif Stratégique

Développer l'interface Sandbox comme environnement de production final pour :
1. Tester les capacités des héros dans un contexte réel de combat
2. Corriger les bugs dans un environnement connecté
3. Éviter le développement "à l'aveugle" du mode Debug

---

## 📜 RÈGLES OFFICIELLES - Référence Stricte

### **Structure des Tours de Jeu**

Les combats se déroulent en **succession de tours**, alternant joueurs et ennemis.

#### **Tour des JOUEURS (ordre libre)**
1. **Début de tour** : Poser jetons parade sur chaque personnage (= score parade)
2. **Choisir** quel personnage va agir
3. **Action 1** : Utiliser une capacité OU boire une potion
4. **Action 2** : Attaquer, lancer un sort, OU faire boire une potion à un allié
5. **Répéter** étapes 2-4 pour chaque personnage
6. → **Passer au tour des ennemis**

#### **Tour des ENNEMIS**
1. **Début de tour** : Poser jetons parade sur chaque ennemi (= score parade)
2. Pour chaque ennemi (jeton d'attaque non retourné) :
   - **🎮 LE JOUEUR CHOISIT** lequel de ses personnages l'ennemi va attaquer
   - Infliger dégâts physiques à ce personnage (- score parade)
   - Retourner le jeton d'attaque de l'ennemi
3. **Répéter** pour tous les ennemis
4. → **Nouveau tour joueurs**

#### **Condition de fin**
- **Victoire** : Dernier ennemi vaincu → continuer la lecture
- **Défaite** : Tous les personnages inconscients → malus de défaite

### **Règles Avancées (optionnelles)**
- ⚔️ **Corps à corps** : Ne cibler que le premier ennemi
- 🏹 **À distance** : Cibler n'importe quel ennemi
- ✨ **Dégâts magiques** : Ignorent la parade
- 🔮 **Créature magique** : Divise dégâts physiques par 2
- 🎲 **Critiques** : 
  - 20 = double les dégâts
  - 1 = contre-attaque immédiate (ignore parade)
- 🎯 **Initiative** : Ordre aléatoire (D20 pour chaque combattant)

---

## ⚠️ ERREUR CRITIQUE IDENTIFIÉE

### **Dans le plan précédent :**
❌ **"Actions ennemies intelligentes"**
- Impliquait un système d'IA de ciblage automatique
- Contredit les règles officielles

### **Règle correcte :**
✅ **Le JOUEUR choisit** quelle cible chaque ennemi attaque
- Aucune décision automatique
- Aucune IA de ciblage
- Le joueur contrôle TOUT, même pendant le tour ennemi

---

## 🚀 PLAN CORRIGÉ - Version Conforme

### **Phase 1 : Connexion Combat Réel** ⚡

**Objectif** : Connecter le Sandbox au vrai système de combat

#### **1.1 Intégrer CombatActions + AbilityEffectsManager**
- Utiliser les vrais calculs de dégâts
- Appliquer les effets réels des capacités
- Connecter le système existant `combat_actions.py`

#### **1.2 Ajouter SpellManager**
- Gérer les coûts en sorts
- Vérifier disponibilité avant utilisation
- Appliquer les effets des sorts
- Récupération après repos

#### **1.3 Système de Ciblage MANUEL par le Joueur**

**Tour Joueur :**
- Interface pour sélectionner ennemi/allié cible
- Pour attaques, sorts, potions
- Validation de cible valide

**Tour Ennemi :**
- **CRITIQUE** : Interface demandant au joueur "Qui attaque cet ennemi ?"
- Boutons de sélection pour chaque héros vivant
- Affichage clair de l'ennemi qui attaque
- Confirmation avant application des dégâts

**Exemple d'interface attendue :**
```
┌─────────────────────────────────────┐
│  🔴 Goule 1 attaque !               │
│                                      │
│  Choisissez la cible :              │
│  [ ] Elneha (HP: 45/50, Parade: 2)  │
│  [ ] Liarie (HP: 30/35, Parade: 0)  │
│  [ ] Atucan (HP: 55/60, Parade: 3)  │
│                                      │
│  [Confirmer le ciblage]             │
└─────────────────────────────────────┘
```

#### **1.4 Appliquer Vraiment les Dégâts/Soins**
- Calcul correct : `max(0, Dégâts_attaquant - Parade_cible)`
- Mise à jour `current_health` en temps réel
- Gestion des dégâts magiques (ignorent parade)
- Détection inconscience (HP ≤ 0)

#### **1.5 Mise à Jour Visuelle Immédiate**
- Barres HP dynamiques
- Compteurs de sorts actualisés
- Affichage buffs/debuffs actifs
- Cooldowns capacités
- États (normal, transformé, inconscient)

---

### **Phase 2 : Boucle Gameplay Complète** 🔄

**Objectif** : Expérience jouable du début à la fin

#### **2.1 Structure de Tour Correcte**

**Début de Tour Joueurs :**
```python
def start_player_turn():
    # Restaurer jetons parade
    for hero in heroes:
        hero.current_parade = hero.base_parade
    
    # Le joueur choisit l'ordre d'action
    # Interface permet de sélectionner quel héros agit
```

**Actions du Héros :**
```python
def hero_action_phase(hero):
    # Action 1 : Capacité OU Potion
    if use_ability:
        apply_ability_effects(hero, ability, target)
    elif use_potion:
        apply_potion_effect(hero)
    
    # Action 2 : Attaque, Sort, OU Potion à allié
    if attack:
        apply_attack(hero, enemy_target)
    elif cast_spell:
        apply_spell(hero, spell, target)
    elif give_potion:
        apply_potion_to_ally(hero, ally_target)
```

**Début de Tour Ennemis :**
```python
def start_enemy_turn():
    # Restaurer jetons parade
    for enemy in enemies:
        enemy.current_parade = enemy.base_parade
    
    # Pour chaque ennemi vivant
    for enemy in alive_enemies:
        # JOUEUR CHOISIT LA CIBLE
        hero_target = ask_player_choose_target(enemy, heroes)
        
        # Appliquer dégâts
        apply_enemy_attack(enemy, hero_target)
        
        # Marquer ennemi comme ayant agi
        enemy.has_attacked_this_turn = True
```

#### **2.2 Détection Fin de Combat**
```python
def check_combat_end():
    all_enemies_dead = all(e.current_health <= 0 for e in enemies)
    all_heroes_unconscious = all(h.current_health <= 0 for h in heroes)
    
    if all_enemies_dead:
        return "VICTORY"
    elif all_heroes_unconscious:
        return "DEFEAT"
    else:
        return "ONGOING"
```

#### **2.3 Gestion des Effets Persistants**
```python
def process_persistent_effects(character):
    for effect in character.active_effects:
        # Appliquer effet (dégâts sur durée, buffs, etc.)
        apply_effect(character, effect)
        
        # Décrémenter durée
        effect.remaining_turns -= 1
        
        # Retirer si expiré
        if effect.remaining_turns <= 0:
            remove_effect(character, effect)
```

#### **2.4 Tour des Ennemis - Contrôle Joueur**

**Interface critique** : Demander au joueur de choisir la cible

```python
def enemy_attack_phase(enemy):
    st.markdown(f"### 🔴 {enemy.name} attaque !")
    st.markdown("**Choisissez quel héros sera ciblé :**")
    
    # Boutons pour chaque héros vivant
    for hero in alive_heroes:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"{hero.name}")
        with col2:
            st.write(f"HP: {hero.current_health}/{hero.max_health}")
        with col3:
            if st.button("Cibler", key=f"target_{hero.id}"):
                apply_enemy_attack(enemy, hero)
                return
```

#### **2.5 Logs Détaillés**
- Actions effectuées
- Dégâts infligés avec calcul détaillé
  - Ex: "Goule 1 attaque Elneha : 8 dégâts - 2 parade = 6 HP perdus"
- Effets appliqués/retirés
- Changements d'état

#### **2.6 Validation des Actions**
```python
def can_use_ability(character, ability):
    # Vérifier coût en sorts
    if ability.spell_cost > character.current_spells:
        return False, "Sorts insuffisants"
    
    # Vérifier cooldown
    if ability.current_cooldown > 0:
        return False, f"Cooldown: {ability.current_cooldown} tours"
    
    # Vérifier cible valide
    if not is_valid_target(ability, target):
        return False, "Cible invalide"
    
    return True, "OK"
```

---

### **Phase 3 : Polish & Tests** ✨

**Objectif** : Interface production-ready

#### **3.1 Tester avec P-1, P-2, P-3**
- **P-1 Elneha** (6 capacités) :
  - Transformations (Loup, Ours, Aigle)
  - Soins (Soin Naturel, Régénération)
  - Résurrection (Renaissance)
- **P-2 Liarie** (6 capacités) :
  - Sorts élémentaires
  - Dégâts magiques
- **P-3 Atucan** (6 capacités) :
  - Capacités paladin
  - Soins divins

#### **3.2 Corriger les Bugs Découverts**
- Dans environnement de combat réel
- Avec boucle gameplay complète
- Tests de chaque capacité individuellement
- Tests d'interactions entre capacités

#### **3.3 Améliorer UX**
- **Feedback visuel clair** :
  - Animations de dégâts
  - Indicateurs d'effets actifs
  - Surbrillance du personnage actif
- **Indications d'état** :
  - Qui peut agir ?
  - Quelles actions sont disponibles ?
  - Quelles cibles sont valides ?
- **Transitions fluides** :
  - Entre les tours
  - Lors des changements d'état

#### **3.4 Documentation Utilisateur**
- Guide d'utilisation du Sandbox
- Tutoriel rapide
- Explication des icônes et indicateurs

---

## 🎮 POINTS CRITIQUES D'IMPLÉMENTATION

### **1. Pas d'IA de Décision**
❌ Aucun calcul automatique de "meilleure cible"  
❌ Aucune "stratégie ennemie"  
❌ Aucun ciblage intelligent  
✅ **Le joueur contrôle TOUT**, même les choix des ennemis

### **2. Interface de Ciblage Ennemi**
**Obligatoire** : Demander au joueur pour CHAQUE attaque ennemie
- Affichage clair de l'ennemi qui attaque
- Liste des héros vivants avec leurs stats
- Boutons de sélection
- Confirmation avant application

### **3. Ordre Libre des Héros**
Le joueur peut faire agir ses héros dans l'ordre qu'il veut :
- Sélection manuelle du héros actif
- Pas d'ordre imposé
- Interface permet de choisir

### **4. Double Action par Héros**
Chaque héros a **2 actions** :
1. Capacité OU Potion
2. Attaque, Sort, OU Potion à allié

### **5. Jetons Parade**
- Restaurés en **début de chaque tour** (joueurs ET ennemis)
- Valeur = score de parade du personnage/ennemi
- Soustraits des dégâts physiques reçus

---

## 📊 CHECKLIST DE CONFORMITÉ

Avant de valider chaque phase, vérifier :

- [ ] **Règle 1** : Le joueur choisit TOUTES les cibles (héros ET ennemis)
- [ ] **Règle 2** : Tour des joueurs = ordre libre choisi par le joueur
- [ ] **Règle 3** : Tour des ennemis = joueur décide qui est attaqué
- [ ] **Règle 4** : Jetons parade restaurés chaque tour
- [ ] **Règle 5** : 2 actions par héros (capacité/potion + attaque/sort/potion allié)
- [ ] **Règle 6** : Dégâts = Attaque - Parade (minimum 0)
- [ ] **Règle 7** : Victoire = tous ennemis vaincus
- [ ] **Règle 8** : Défaite = tous héros inconscients
- [ ] **Règle 9** : Pas de ciblage automatique/intelligent
- [ ] **Règle 10** : Interface demande confirmation avant chaque action critique

---

## 🔄 MÉTHODOLOGIE DE DÉVELOPPEMENT

### **Approche Itérative**
1. Implémenter une fonctionnalité
2. Tester immédiatement dans le Sandbox
3. Corriger les bugs identifiés
4. Valider la conformité aux règles
5. Passer à la fonctionnalité suivante

### **Tests Continus**
- Tester après chaque modification
- Utiliser les capacités P-1 à P-3 existantes
- Vérifier la cohérence avec les règles officielles

### **Documentation**
- Mettre à jour ce document si découverte de nouvelles règles
- Documenter les bugs et leurs corrections
- Garder trace des décisions de design

---

## 📝 NOTES IMPORTANTES

### **Différence avec Mode Debug**
- **Mode Debug** : Environnement isolé, tests limités, déconnecté
- **Mode Sandbox** : Environnement de production, boucle complète, tests réels

### **Avantages de cette Approche**
✅ Tests dans contexte réel  
✅ Détection précoce des bugs  
✅ Pas de "développement à l'aveugle"  
✅ Interface finale dès le début  
✅ Corrections efficaces  

### **Risques à Éviter**
❌ Ne pas réinventer un système de combat différent  
❌ Ne pas ajouter de logique de ciblage automatique  
❌ Ne pas dévier des règles officielles  
❌ Ne pas supposer comment le jeu fonctionne  

---

## 🎯 PROCHAINES ÉTAPES

1. **Immédiat** : Commencer Phase 1.3 - Système de ciblage manuel
2. **Court terme** : Compléter Phase 1 (connexion combat réel)
3. **Moyen terme** : Phase 2 (boucle gameplay)
4. **Long terme** : Phase 3 (polish & tests)

---

## 📚 RÉFÉRENCES

- **Livre de règles V3.0** - Pages 25-26 (Tours de jeu)
- **Livre de règles V3.0** - Page 30 (Résumé des règles)
- **Plan-d-action.md** - Méthodologie générale du projet
- **documentation_architecture_périples.md** - Architecture technique

---

**Document créé le** : 28 octobre 2025  
**Dernière mise à jour** : 28 octobre 2025  
**Statut** : ✅ Vérifié et validé avec règles officielles V3.0