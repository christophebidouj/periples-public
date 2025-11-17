# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Périples Balance Workshop** is a combat simulation tool for the board game "Périples" (© Bastien LIAUTY). It tests game balance with authentic equipment data, hero abilities, and enemies that scale to player count.

## Running the Application

```bash
# Start the Streamlit application
streamlit run app.py

# The app runs on http://localhost:8501 by default
```

**No automated tests** - Testing is done directly in the final Streamlit application.

## ⚠️ CRITICAL RULE: Zero Code Duplication

**Before writing ANY code, you MUST:**

1. Search for existing implementations using `project_knowledge_search`
2. Read `documentation architecture périples.md` for API reference
3. Check `Regle absolue verification architecture.md` for architectural rules
4. **Verify compliance with official game rules in `Livre de règles V3.0.pdf`** - All features must follow the official Périples V3.0 rules, NO invented mechanics
5. Verify the functionality doesn't already exist
6. **Explain your plan and ask for user validation** - Before coding, describe what you intend to do and wait for user approval to ensure the request is correctly understood

**Key principle:** REUSE existing architecture through wrappers/adapters, NEVER duplicate logic.

### Example - DO NOT Duplicate

```python
# ❌ WRONG - Creating new combat logic
class NewCombatManager:
    def process_turn(self): ...  # This already exists in TurnManager

# ✅ RIGHT - Reuse with adapter pattern
class SandboxAdapter:
    def __init__(self, turn_manager: TurnManager):
        self.turn_manager = turn_manager  # Reuse existing logic
```

## Architecture Overview

The codebase follows strict separation between business logic (`models/`) and UI (`ui/`).

### Core Combat System (Refactored - Modular)

The combat system has been extracted into modular components:

```
models/combat/
├── initiative_manager.py    # Initiative rolls and turn order (D20 rolls)
├── turn_manager.py          # Turn management and tactical AI
├── combat_actions.py        # Attack/ability/potion actions
├── spell_manager.py         # Spell cost tracking
├── combat_engine.py         # Combat orchestrator
└── combat_logger.py         # Combat logging
```

**Always reuse these components** - DO NOT recreate combat logic in UI files.

### Key Classes and Their Responsibilities

**Character (models/character.py)**
- Heroes with stats, equipment, abilities, health, parade tokens
- Key APIs: `start_hero_turn()`, `get_total_health()`, `apply_damage_with_parade()`, `is_alive()`

**Enemy (models/character.py)**
- Enemies with multi-player scaling
- Key method: `initialize_for_combat(player_count)` - MUST be called before combat

**InitiativeManager (models/combat/initiative_manager.py)**
- Pure business logic for initiative system
- `roll_initiative(combatants)` - Generates D20 rolls and sorts by initiative
- `get_initiative_order_log(combatants)` - Formats log messages
- Follows official rules: page 26 of PDF, heroes have priority on ties

**TurnManager (models/combat/turn_manager.py)**
- Manages hero and enemy turns
- Contains tactical AI for distributing damage
- Key methods: `heroes_turn()`, `enemies_turn()`, `hero_turn()`, `pet_turn()`

**CombatActions (models/combat/combat_actions.py)**
- Executes concrete actions
- Key methods: `hero_attack()`, `try_ability_with_summon()`, `try_health_potion()`

**SpellManager (models/combat/spell_manager.py)**
- Tracks spell costs and availability
- MUST call `initialize_spells(character)` before combat
- Manages magical ability limitations

### UI Architecture

UI components are in `ui/components/` and should ONLY handle:
- Streamlit widgets and display
- User input collection
- Calling business logic from `models/`

**Sandbox Interfaces:**
- `sandbox_interface.py` - Original sandbox (V1) with initiative
- `sandbox_interface_v2.py` - Manual control sandbox with initiative and undo/redo

Both interfaces REUSE the combat logic via adapters - they do NOT duplicate it.

#### Sandbox V2 - Combat Display Modes

Sandbox V2 has **two distinct display modes** controlled by the `initiative_setting` checkbox in the Selection tab (Onglet 1):

**1. Initiative Mode (`display_combat_status()`)** - Location: `ui/components/sandbox_interface_v2.py:1260`
- **When:** Initiative checkbox is ENABLED
- **Display:** All combatants in a **single grid** following D20 initiative order
- **Layout:** Max **8 cards per row** (auto-wraps to multiple rows if needed)
- **Order:** Mixed heroes/enemies sorted by initiative value (highest to lowest)
- **No titles:** Cards displayed without "Héros" / "Ennemis" section headers
- **Data source:** `st.session_state.sandbox_v2_combatants` (already sorted by `InitiativeManager`)

**2. Manual Mode (`display_combat_status_team_mode()`)** - Location: `ui/components/sandbox_interface_v2.py:1308`
- **When:** Initiative checkbox is DISABLED
- **Display:** All combatants in a **single grid** with manual selection
- **Layout:** Max **7 cards per row** (auto-wraps to multiple rows if needed)
- **Order:** Heroes first, then enemies (not sorted by initiative)
- **No titles:** Cards displayed without separate section headers
- **Interactive:** Each card has "▶️ À son tour" button for manual turn selection
- **Data source:** `st.session_state.sandbox_v2_combatants` (organized by `organize_teams_without_initiative()`)

**When to modify these functions:**
- Changing card layout per row (8 vs 7 limit)
- Altering card display order logic
- Adding/removing visual separators between factions
- Modifying grid responsiveness or breakpoints

## Development Workflow

### Adding New Functionality

1. **Search first:** Use `project_knowledge_search` to find existing APIs
2. **Check documentation:** Read `documentation architecture périples.md`
3. **Verify rules:** Consult `tour de combat.md` for official game rules (page 26 for initiative)
4. **Reuse or adapt:** Use existing classes via wrappers/adapters
5. **Business logic first:** Implement in `models/`, THEN create UI in `ui/components/`

### Refactoring Business Logic from UI

When you find business logic mixed in UI files:

1. Create a new module in `models/combat/` or appropriate location
2. Extract ONLY the business logic (calculations, game rules, state management)
3. Leave UI-specific code (Streamlit widgets, session_state, display formatting) in UI files
4. Import and use the new business logic module from the UI

**Example:** The recent initiative refactoring:
- **Before:** Initiative generation mixed with Streamlit session_state in `sandbox_interface_v2.py`
- **After:** `InitiativeManager` handles D20 rolls and sorting, UI file calls it and manages display

### Code Organization Principles

**Business Logic (`models/`):**
- Game rules enforcement
- Calculations (damage, healing, stats)
- State transitions
- Data validation
- NO Streamlit imports

**UI (`ui/components/`):**
- Streamlit widgets
- Session state management
- Display formatting
- User input handling
- Calls business logic from `models/`

## Important Game Rules

The application strictly follows **Périples V3.0 official rules** from `tour de combat.md`:

- **Initiative:** D20 rolls, descending order, heroes prioritized on ties (page 26)
- **Turn structure:** Heroes phase → Enemies phase (alternating)
- **Parade tokens:** Reset at start of each combatant's turn
- **No invented mechanics:** Only implement what's in the official rules PDF

## Data Loading

**DataLoader (utils/data_loader.py)**
- Loads heroes, enemies, equipment from CSV files
- Uses `@st.cache_data` for performance
- Always use deepcopy of Character/Enemy instances for combat to avoid state pollution

## Common Patterns

### Creating Character Instances for Combat

```python
# Load data
loader = DataLoader()
all_heroes = loader.load_heroes()
all_enemies = loader.load_enemies()

# Filter by codes
heroes = [h for h in all_heroes if h.code in hero_codes]
enemies = [e for e in all_enemies if e.code in enemy_codes]

# CRITICAL: Initialize enemies for combat
player_count = len(heroes)
for enemy in enemies:
    enemy.initialize_for_combat(player_count)

# Create deep copies for isolation
combat_heroes = deepcopy(heroes)
combat_enemies = deepcopy(enemies)
```

### Using Initiative System

```python
from models.combat.initiative_manager import InitiativeManager

# Prepare combatants list
combatants = [
    {'character': hero, 'faction': 'hero', 'initiative': 0, 'id': 'hero_H-1'},
    {'character': enemy, 'faction': 'enemy', 'initiative': 0, 'id': 'enemy_E-1'}
]

# Business logic: Generate and sort
InitiativeManager.roll_initiative(combatants)

# UI logic: Get formatted logs
log_lines = InitiativeManager.get_initiative_order_log(combatants)
st.session_state.combat_log.extend(log_lines)
```

### Using Combat Components

```python
from models.combat.turn_manager import TurnManager
from models.combat.combat_actions import CombatActions
from models.combat.spell_manager import SpellManager
from models.rules_engine import GameRules

# Setup
rules = GameRules(ranged_attacks=True, magical_damage=True, criticals=True)
spell_manager = SpellManager()
combat_actions = CombatActions(spell_manager, rules)
turn_manager = TurnManager(spell_manager, combat_actions)

# Initialize spells for each hero
for hero in heroes:
    spell_manager.initialize_spells(hero)

# Execute turns (delegates to turn_manager)
turn_manager.heroes_turn(heroes, enemies, player_count, log, active_pets)
turn_manager.enemies_turn(enemies, heroes, player_count, log, active_pets)
```

## Configuration Parameters (Initiative & Critiques)

The application uses **global configuration parameters** synchronized between the Selection tab (Onglet 1) and all combat interfaces (including Sandbox V2).

### Initiative Setting

**Checkbox location:** `app.py:459-464` (Onglet Sélection)
**Storage:** `st.session_state.initiative_setting` (Boolean)
**Default value:** `True`

**How it works:**
1. User toggles "🎲 Initiative" checkbox in Selection tab
2. Callback `on_initiative_change()` saves value to `initiative_setting`
3. Sandbox V2 reads this value to determine display mode:
   - `True` → Initiative mode with D20 rolls
   - `False` → Manual mode with turn selection buttons

**Where it's used:**
- `sandbox_interface_v2.py:1504` - Choose between initiative/manual mode
- `sandbox_interface_v2.py:1532` - Display appropriate combat status

### Criticals Setting

**Checkbox location:** `app.py:453-458` (Onglet Sélection)
**Storage:** `st.session_state.criticals_setting` (Boolean)
**Default value:** `True`

**How it works:**
1. User toggles "🎯 Critiques" checkbox in Selection tab
2. Callback `on_criticals_change()` saves value to `criticals_setting`
3. Sandbox V2 reads this value when creating `GameRules`:
   - `True` → Critical hits (Nat 20 = 2x damage) and critical failures (Nat 1) are active
   - `False` → Critical mechanics are completely disabled

**Where it's used:**
- `sandbox_interface_v2.py:491` - Read setting from session_state
- `sandbox_interface_v2.py:497` - Pass to `GameRules(criticals=...)`
- `sandbox_interface_v2.py:1456` - Display "🎯 Critiques ON/OFF" badge in UI
- `models/combat/combat_actions.py:59` - Check `if self.rules.criticals and attack_roll == 20`
- `models/combat/combat_actions.py:87` - Check `if self.rules.criticals and attack_roll == 1`

**Important:** The critical mechanics are controlled by the `GameRules.criticals` parameter. When `False`, the code paths for critical hits and failures are never executed, ensuring the mechanic is truly disabled.

### Pattern for Adding New Global Settings

To add a new global setting that syncs between Selection tab and combat interfaces:

1. **Initialize in app.py** (before checkboxes):
   ```python
   if 'my_setting' not in st.session_state:
       st.session_state.my_setting = True  # default value
   ```

2. **Create callback in app.py**:
   ```python
   def on_my_setting_change():
       st.session_state.my_setting = st.session_state.combat_my_setting
   ```

3. **Add checkbox in app.py**:
   ```python
   st.checkbox(
       "⚙️ My Setting",
       value=st.session_state.my_setting,
       key='combat_my_setting',
       on_change=on_my_setting_change
   )
   ```

4. **Read in Sandbox V2** (`configure_combat()` or `main_sandbox_v2()`):
   ```python
   my_setting_enabled = st.session_state.get('my_setting', True)
   ```

5. **Use in business logic** (pass to GameRules or use directly)

### Potion System

The potion system allows heroes to heal themselves or allies during combat.

**Two Potion Types:**
- **Petite Potion (Small):** Heals 4 PV - Icon: 🩸
- **Grande Potion (Large):** Heals 100% PV (full heal) - Icon: ❤️‍🩹

**Character Model API (models/character.py):**

```python
from models.character import PotionType

# Use a specific potion on self
result = hero.use_specific_potion(PotionType.SMALL)
# Returns: {'success': bool, 'potion_used': str, 'healing_done': int, 'message': str}

# Give a potion to another hero
result = hero.use_specific_potion(PotionType.LARGE, target=other_hero)
# target parameter allows giving potions to allies
```

**Turn Management - Multiple Actions Per Turn:**

In Sandbox V2, heroes can perform **multiple actions in a single turn**. The player controls when to end the turn.

**Actions that DO NOT end the turn:**
1. **⚔️ Attaquer (Attack):**
   - Does NOT end the turn
   - Marks `can_attack_this_turn = False` to prevent multiple attacks
   - Button becomes "⚔️ Attaquer (déjà fait)" and is disabled after use
   - Hero can still use abilities or drink potions after attacking

2. **🔮 Utiliser une capacité (Use ability):**
   - Does NOT end the turn
   - Abilities with `prevents_attack = True` will set `can_attack_this_turn = False`
   - Hero can still drink potions after using ability

3. **🩸/❤️‍🩹 Boire une potion (Drink potion self):**
   - Buttons: "🩸 Petite" and "❤️‍🩹 Grande"
   - Does NOT end the turn
   - Marks `potion_used_this_turn = True`
   - Hero can attack or use abilities after drinking

**Actions that END the turn:**
1. **⏭️ Passer le Tour (Skip turn):**
   - Explicitly ends the turn
   - Player chooses when they're done

2. **🤝 Faire Boire une Potion (Give potion to ally):**
   - **Exclusive action:** Ends the turn immediately
   - **Cannot be used if any action was already taken this turn**
   - Workflow:
     1. Click "Faire Boire" button
     2. Select potion type (Petite or Grande)
     3. Select target ally
     4. Turn ends automatically

**Strategic Combinations:**

Heroes can combine actions in a single turn:
- ⚔️ Attack an enemy → 🩸 Drink a potion (heal after taking retaliation damage)
- 🩸 Drink a potion → ⚔️ Attack an enemy (heal before engaging)
- 🔮 Use ability → 🩸 Drink a potion
- 🩸 Drink multiple potions (as long as they have them)

**Action Restrictions:**

The "Faire Boire" button is disabled if:
- `char.action_taken_this_turn == True` (hero used an ability that prevents attack)
- `char.potion_used_this_turn == True` (hero already drank a potion)
- `char.can_attack_this_turn == False` (hero already attacked)

The "Attaquer" button is disabled if:
- `char.can_attack_this_turn == False` (hero already attacked this turn)

**UI Implementation (ui/components/sandbox_interface_v2.py):**

```python
# Import PotionType
from models.character import Character, Enemy, PotionType

# Action functions
def use_small_potion_action(char: Character):
    """Drink small potion - does NOT end turn"""
    result = char.use_specific_potion(PotionType.SMALL)
    save_game_state(...)
    st.rerun()  # Refresh interface, turn stays active

def use_large_potion_action(char: Character):
    """Drink large potion - does NOT end turn"""
    result = char.use_specific_potion(PotionType.LARGE)
    save_game_state(...)
    st.rerun()  # Refresh interface, turn stays active

def give_potion_to_ally_action(giver: Character, target: Character, potion_type: PotionType):
    """Give potion to ally - ENDS TURN"""
    result = giver.use_specific_potion(potion_type, target=target)
    next_turn()  # Exclusive action - turn ends
    st.rerun()

def use_ability_action(char: Character, ability):
    """Use ability - does NOT end turn"""
    action = char.use_ability(ability)
    save_game_state(...)
    st.rerun()  # Refresh interface, turn stays active

# Attack action
adapter.combat_actions.hero_attack(char, [target], player_count, log)
char.can_attack_this_turn = False  # Prevent multiple attacks
save_game_state(...)
st.rerun()  # Refresh interface, turn stays active
```

**Location:** Potion buttons are displayed in the hero action panel (lines 908-1032 in `sandbox_interface_v2.py`)

## Git Workflow

**Branch naming:** All development branches must start with `claude/` and end with the session ID.

**Example:** `claude/feature-name-01XvfABCDEF123456789`

This is enforced by git hooks - pushes to incorrectly named branches will fail with HTTP 403.

## Session Context

The application uses `st.session_state` extensively for managing UI state. When creating new interfaces:
- Initialize session state variables in an `init_*_state()` function
- Use clear, namespaced keys (e.g., `sandbox_v2_heroes`, `sandbox_v2_phase`)
- Check for existing state before initializing

## Key Files Reference

- `tour de combat.md` - Official game rules (authoritative source)
- `documentation architecture périples.md` - Detailed API documentation
- `Regle absolue verification architecture.md` - Zero-duplication architectural rules
- `hero_builds_data.py` - Hero build definitions (3 difficulty levels per hero)
- `data/heroes.csv` - 8 playable heroes
- `data/enemies.csv` - 72 scalable enemies
- `data/equipment.csv` - 56 equipment items + 4 special objects
- `data/ability_names.csv` - 48 official ability names

## Remember

1. **Search before coding** - Functionality often already exists
2. **Separate business logic from UI** - Keep `models/` pure
3. **Follow official rules** - Consult `tour de combat.md`
4. **Test in the app** - No unit tests, validate directly in Streamlit
5. **Reuse through adapters** - Wrapper pattern over duplication
