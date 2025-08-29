# 🎯 PLAN D'ACTION - MIGRATION CAPACITÉS PÉRIPLES
**Version : Claude-Ready Final - Août 2025**

## ⚠️ RÈGLES ABSOLUES CLAUDE

### 🚨 AVANT TOUT DÉVELOPPEMENT
1. **LIRE** ce plan complet (contexte + flux + API)
2. **VÉRIFIER** `Sorts.xlsx` pour données officielles
3. **TESTER** imports : `from models.character import Character`
4. **INTERDICTION** : Inventer valeurs numériques

### 📊 Sources données OBLIGATOIRES
- **Noms** : `ability_names.csv` 
- **Mécaniques** : `Sorts.xlsx` (coûts, limitations)
- **API** : `character.py` + `data_loader.py`

---

## 📈 ÉTAT ACTUEL (Mise à jour obligatoire)
**TOTAL** : 18/59 capacités (30%) - MAJ Décembre 2024
- **P-1 (Elneha)** : 6/6 ✅ Druide
- **P-2 (Liarie)** : 6/6 ⚠️ Erreur `magical_armor_bonus`
- **P-3 (Atucan)** : 6/6 ❌ IA trop restrictive

**Prochaine priorité** : Compléter debug_mode.py (BLOQUANT)

---

## 🔄 FLUX D'EXÉCUTION (À respecter)

### Utilisateur Streamlit
```
app.py → tabs[5] → create_debug_tab() → Test manuel
```

### Combat IA  
```
combat_engine.py → ability_manager.py → _try_individual_ability() 
→ ABILITY_REGISTRY → capacity.execute() → SpellManager
```

### Fichiers critiques
- `individual_abilities/base_ability.py` - Classe mère
- `individual_abilities/ability_registry.py` - Catalogue
- `individual_abilities/heroes/[hero].py` - Implémentations
- `debug_mode.py` - **À compléter en priorité**

---

## ⚙️ API VALIDÉE

### Character (Hero)
```python
hero.get_attack_damage_info()['damage_value']  # Dégâts
hero.current_spells                            # Sorts restants
hero.current_health                            # PV
hero.is_alive()                               # Statut
hero.apply_damage_with_parade(damage)         # Appliquer dégâts

# Validation défensive obligatoire
if not hasattr(user, 'current_spells'):
    return False, "current_spells manquant"
```

### Enemy (data_loader.py)
```python
enemy.get_damage_info(player_count)['damage_value']  # Dégâts
enemy.defense                                        # Défense
enemy.is_alive()                                    # Statut
enemy.stats_by_players[player_count]                # Stats variables
```

---

## 🔄 PROCESSUS (45 min par capacité)

### 1. Données sources (10 min)
- **ability_names.csv** : Nom capacité
- **Sorts.xlsx** : Coûts + limitations officiels
- **❌ Jamais inventer** de valeurs

### 2. Implémentation (15 min)
```python
class CapaciteName(BaseAbility):
    def __init__(self):
        super().__init__(spell_cost=VALEUR_SORTS_XLSX)  # Officielle
    
    def can_be_used(self, user, targets, combat_state):
        print(f"DEBUG: {self.name} - Vérification")
        if not hasattr(user, 'current_spells'):
            return False, "Attribut manquant"
        
    def execute(self, user, targets, combat_state):
        try:
            print(f"DEBUG: {self.name} - Exécution")
            # Implémentation avec logs
        except Exception as e:
            return {"success": False, "error": str(e)}
```

### 3. Test onglet debug (15 min) - SEULE VALIDATION
- Interface `tabs[5]` : sélection héros/capacité
- Configuration contexte test  
- Logs temps réel
- Validation avant/après

### 4. Documentation (5 min)
- Mise à jour section "État actuel"
- Ajout API validée
- Note flux si modifié

---

## 🛠️ PRIORITÉ #1 : COMPLÉTER DEBUG

### Statut actuel
```python
# app.py ligne ~X
with tabs[5]:
    create_debug_tab()  # Fonction INCOMPLÈTE
```

### Interface requise
```python
def create_debug_tab():
    st.header("🔧 Test Capacités Manuel")
    
    # Sélection
    hero_code = st.selectbox("Héros", ["P-1", "P-2", "P-3"])
    ability_num = st.selectbox("Capacité", [1, 2, 3, 4, 5, 6])
    
    # Configuration
    user_pv = st.number_input("PV", 1, 30, 15)
    user_sorts = st.number_input("Sorts", 0, 10, 5)
    nb_ennemis = st.selectbox("Ennemis", [1, 2, 3])
    
    # Test direct
    if st.button("🧪 TESTER"):
        # Créer contexte réel + exécuter + logs
```

**BLOQUANT** : Aucune capacité avant debug fonctionnel

---

## 📊 API VALIDÉE (Enrichissement continu)

### ✅ P-1 Elneha validée
**API utilisée** : `hero.current_spells`, `hero.apply_damage_with_parade()`
**Erreurs évitées** : Aucune

### ✅ P-2 Liarie partiellement validée  
**API utilisée** : `hero.get_total_damage()`
**Erreurs** : `magical_armor_bonus` n'existe pas
**À corriger** : Créer attribut ou adapter capacité

### ⚠️ P-3 Atucan problématique
**Problème** : IA jamais utilise Imposition des mains
**À revoir** : Seuils d'activation trop restrictifs

---

## 🎯 MISE À JOUR APRÈS CHAQUE CAPACITÉ

**Dans ce plan, section "État actuel" :**
1. Incrémenter compteur capacités
2. Marquer statut héros (✅/⚠️/❌)
3. Noter prochaine priorité
4. Ajouter API validée si nouvelle
5. Documenter flux si modifié

**Échec si oubli** : Capacité non terminée

---

## 🎯 OBJECTIF FINAL
**59/59 capacités** fonctionnelles via onglet debug validé