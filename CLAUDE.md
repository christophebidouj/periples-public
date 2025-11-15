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
