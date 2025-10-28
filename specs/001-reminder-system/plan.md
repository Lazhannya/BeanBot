# Implementation Plan: Modular Reminder System

**Branch**: `001-reminder-system` | **Date**: 2025-10-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-reminder-system/spec.md`

**Note**: This plan refactors the existing `dog_reminder.py` into a generalized, configurable reminder system while preserving existing functionality.

## Summary

Transform the existing dog-specific reminder module into a general-purpose, configurable reminder system that supports multiple independent reminders with different schedules, target users, escalation users, and timeout periods. The refactored module will maintain backward compatibility with existing dog reminder functionality while enabling easy addition of new reminders through simple configuration edits. The implementation follows Module-First Architecture principles with comprehensive error handling, logging, and the ability to dynamically reload configuration without bot restart.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: discord.py 2.x, python-dotenv, pytz (existing)  
**Storage**: In-memory with file-based configuration (Python dict/JSON for easy editing)  
**Testing**: Manual testing via Discord bot interactions (automated testing optional)  
**Target Platform**: Linux server (continuous operation)  
**Project Type**: Single project - Discord bot module  
**Performance Goals**: 
- Reminder delivery within 60 seconds of scheduled time
- Button interaction response < 2 seconds
- Support 10+ concurrent independent reminders
- Zero impact on other bot features

**Constraints**: 
- Must maintain existing dog reminder functionality
- Configuration changes without bot restart
- Discord API rate limits (managed by discord.py)
- Discord button interaction 15-minute timeout (requires custom timeout tracking)

**Scale/Scope**: 
- Personal use bot (small scale)
- 1-20 reminders maximum
- 2-5 users (target + escalation)
- Single timezone per bot instance

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Module-First Architecture**: Feature implemented as separate module with `setup(bot)` function?
  - ✅ Will refactor existing `dog_reminder.py` into generalized `reminder_system.py`
  - ✅ Maintains `setup(bot)` pattern for initialization
  - ✅ Module remains self-contained in `modules/` directory

- [x] **Simplicity**: Functions under 50 lines? Clear single responsibility? Self-documenting names?
  - ✅ Existing `dog_reminder.py` follows this pattern (functions 20-50 lines)
  - ✅ Will maintain clear function naming: `send_reminder()`, `handle_acknowledgment()`, `check_timeout()`
  - ✅ Configuration structure will be simple dict/JSON format

- [x] **Error Handling**: All async operations wrapped in try-except? Proper logging configured?
  - ✅ Existing module has comprehensive error handling
  - ✅ Module-level logger configured (`logger = logging.getLogger(__name__)`)
  - ✅ All Discord API calls wrapped in try-except with logging

- [x] **Expandability**: No unnecessary dependencies on other feature modules?
  - ✅ Module is independent (only depends on discord.py and standard library)
  - ✅ Configuration-driven approach enables easy reminder additions
  - ✅ No dependencies on `how_is.py` or other bot features

- [x] **Observability**: Module-level logger created? Key operations logged at appropriate levels?
  - ✅ Existing module has DEBUG, INFO, ERROR logging levels
  - ✅ Logs: delivery, acknowledgment, denial, timeout, escalation events
  - ✅ File-based logging to `reminder_system.log`

- [x] **Documentation**: Module docstring present? README updated? `.env` requirements documented?
  - ⚠️ Need to update README.md with new generalized reminder system
  - ⚠️ Need to document configuration structure
  - ✅ `.env` requirements unchanged (DISCORD_TOKEN only)

---

## Phase 0: Research & Outline

**Research Questions**: Document unknowns before design decisions.

### Research Topics

1. **Configuration Structure Design**
   - **Question**: What's the best Python data structure for easy editing while maintaining validation?
   - **Options**: JSON file, Python dict in config.py, TOML, YAML
   - **Criteria**: Easy hand-editing, validation support, backward compatibility with dog reminder
   - **Recommendation**: Python dict in `reminder_config.py` for code simplicity + optional JSON export

2. **Module Organization**
   - **Question**: How to organize modules/ folder while maintaining main.py simplicity?
   - **Current**: Root-level `dog_reminder.py`, `how_is.py`
   - **Target**: `modules/` folder with subdirectories?
   - **Recommendation**: Flat `modules/` folder, each file self-contained with `setup(bot)` function

3. **Backward Compatibility Strategy**
   - **Question**: How to preserve existing dog reminder functionality during refactor?
   - **Options**: Migration script, dual-mode support, configuration migration
   - **Recommendation**: Create `reminder_config.py` with dog reminder as first entry, refactor module to read config

4. **Button Persistence Pattern**
   - **Question**: How does discord.py handle button persistence across bot restarts?
   - **Finding**: `View(timeout=None)` keeps buttons active, but interaction handlers lost on restart
   - **Impact**: Current implementation works for continuous bot operation (no restart persistence needed)
   - **Decision**: Keep current pattern, document restart behavior in README

5. **Testing Strategy**
   - **Question**: How to test async Discord bot features without live bot?
   - **Options**: Manual testing, pytest-asyncio with mocks, integration testing
   - **Recommendation**: Manual testing via test commands (existing pattern: `!testreminderdog`)
   - **Rationale**: Simple, matches current workflow, sufficient for personal use scale

### Design Decisions

**Configuration Approach**: Python module with list of reminder dictionaries
```python
# reminder_config.py
REMINDERS = [
    {
        "name": "dog_walking",
        "schedules": [
            {"hour": 8, "minute": 0, "label": "morning"},
            {"hour": 13, "minute": 0, "label": "noon"},
            {"hour": 20, "minute": 0, "label": "evening"}
        ],
        "target_user_id": 343513966049492999,
        "escalation_user_id": 143474592529252353,
        "timeout_minutes": 60,
        "messages": {
            "morning": "Good morning! Have you fed and walked the dog yet?",
            "noon": "It's noon! Has the dog been fed and walked for lunch?",
            "evening": "Good evening! Have you fed and walked the dog yet?"
        },
        "timeout_message": "⚠️ OVERDUE ALERT: The dog is overdue for the {label} walk and feeding!"
    }
]

TIMEZONE = "Europe/Paris"
```

**Module Structure**: 
- Rename `dog_reminder.py` → `reminder_system.py` in `modules/` folder
- Move `how_is.py` → `modules/how_is.py`
- Update `main.py` to import from `modules/`

**State Management**: 
- Keep in-memory `pending_reminders` dict (current pattern works well)
- Key format: `{reminder_name}_{label}_{YYYYMMDD}`
- No persistence needed (restarts reset state, acceptable for use case)

**Dynamic Reload**: 
- Add `!reloadreminders` command to re-import config without bot restart
- Use `importlib.reload()` on `reminder_config` module

---

## Phase 1: Interface Design

### Data Model

**Reminder Configuration Schema**:
```python
{
    "name": str,              # Unique identifier (e.g., "dog_walking", "medication")
    "schedules": [            # List of times to send reminder
        {
            "hour": int,      # 0-23
            "minute": int,    # 0-59
            "label": str      # Human-readable label (e.g., "morning", "dose_1")
        }
    ],
    "target_user_id": int,    # Discord user ID to receive reminder
    "escalation_user_id": int,# Discord user ID to notify on timeout/denial
    "timeout_minutes": int,   # Minutes to wait before escalation
    "messages": {             # Label -> message text mapping
        str: str              # e.g., {"morning": "Good morning!..."}
    },
    "timeout_message": str,   # Escalation message (supports {label} placeholder)
    "denial_message": str     # Optional: custom denial escalation message
}
```

**Runtime State Schema**:
```python
pending_reminders = {
    "{name}_{label}_{date}": {
        "message_id": int,
        "user_id": int,
        "reminder_name": str,
        "schedule_label": str,
        "timestamp": datetime,
        "view": discord.ui.View
    }
}
```

### API Contracts

**Module Interface** (`reminder_system.py`):
```python
def setup(bot: commands.Bot) -> ReminderSystem:
    """
    Initialize reminder system module.
    
    Registers:
    - Background reminder loop task
    - Discord commands for configuration
    - Button interaction handlers
    
    Returns:
        ReminderSystem instance for testing/inspection
    """
    pass

class ReminderSystem:
    """Main reminder system controller"""
    
    def __init__(self, bot: commands.Bot):
        """Initialize with bot instance and load config"""
        pass
    
    async def start(self):
        """Start reminder loop (called from bot.on_ready)"""
        pass
    
    async def send_reminder(self, reminder_config: dict, schedule: dict):
        """Send single reminder with buttons"""
        pass
    
    async def check_reminder_timeout(self, reminder_id: str):
        """Check for timeout and send escalation"""
        pass
    
    def reload_config(self):
        """Reload reminder_config.py without restart"""
        pass
```

**Discord Commands Interface**:
```python
# Existing commands (preserved for compatibility)
!dogtimezone [timezone]     # View/set timezone
!dogstatus                  # View reminder status
!testreminderdog [label]    # Test dog reminder

# New commands (generalized)
!reminderstatus             # View all active reminders
!testreminder <name> [label]# Test any reminder
!reloadreminders            # Reload config without restart
!listreminders              # List all configured reminders
```

### Module Organization

**Target Structure**:
```
BeanBot/
├── main.py                          # Bot orchestration
├── reminder_config.py               # NEW: Reminder configuration
├── modules/
│   ├── reminder_system.py          # RENAMED from dog_reminder.py
│   └── how_is.py                   # MOVED from root
├── .env
├── README.md
└── specs/
```

**Migration Steps**:
1. Create `modules/` directory
2. Create `reminder_config.py` with dog reminder config
3. Copy `dog_reminder.py` → `modules/reminder_system.py`
4. Refactor `reminder_system.py` to read from config
5. Move `how_is.py` → `modules/how_is.py`
6. Update `main.py` imports
7. Test dog reminder functionality (regression test)
8. Document in README.md

### Quick Start Guide

**Adding a New Reminder** (after implementation):
```python
# 1. Edit reminder_config.py
REMINDERS.append({
    "name": "medication",
    "schedules": [
        {"hour": 9, "minute": 0, "label": "morning_dose"},
        {"hour": 21, "minute": 0, "label": "evening_dose"}
    ],
    "target_user_id": 123456789,
    "escalation_user_id": 987654321,
    "timeout_minutes": 30,
    "messages": {
        "morning_dose": "Time for morning medication!",
        "evening_dose": "Time for evening medication!"
    },
    "timeout_message": "⚠️ MEDICATION ALERT: {label} was not taken!"
})

# 2. Reload bot or use command
!reloadreminders
```

**Testing Changes**:
```bash
# Test specific reminder
!testreminder medication morning_dose

# Check status
!reminderstatus

# View configuration
!listreminders
```

---

## Phase 2: Implementation Tasks

### Task Breakdown

**Task 1: Create Project Structure** (Priority: P0 - Foundation)
- Create `modules/` directory
- Create `reminder_config.py` with dog reminder config
- Update `.gitignore` if needed (exclude sensitive config variants)
- **Acceptance**: Directory exists, config file has dog reminder data
- **Estimated Effort**: 15 minutes

**Task 2: Refactor Module Core** (Priority: P1 - Critical Path)
- Copy `dog_reminder.py` → `modules/reminder_system.py`
- Replace hardcoded config with `reminder_config.py` import
- Generalize `send_reminder()` to accept config dict
- Update `_reminder_loop()` to iterate through all reminders in config
- Rename `DogReminderView` → `ReminderView` and generalize
- **Acceptance**: Module reads config, sends first reminder correctly
- **Estimated Effort**: 2 hours

**Task 3: Update Button Handlers** (Priority: P1 - Critical Path)
- Generalize button callback messages (use config `messages` dict)
- Update escalation notifications (use config `escalation_user_id`)
- Update reminder ID format to include reminder name
- **Acceptance**: Buttons work with generalized config
- **Estimated Effort**: 1 hour

**Task 4: Generalize Discord Commands** (Priority: P2 - Important)
- Keep existing `!dog*` commands for backward compatibility
- Add `!reminderstatus` (shows all reminders)
- Add `!testreminder <name> [label]` (test any reminder)
- Add `!listreminders` (show config)
- Update `!dogtimezone` to affect global timezone
- **Acceptance**: All commands functional, backward compatible
- **Estimated Effort**: 1.5 hours

**Task 5: Implement Config Reload** (Priority: P2 - Important)
- Add `reload_config()` method using `importlib.reload()`
- Add `!reloadreminders` command (owner only)
- Handle reload errors gracefully
- **Acceptance**: Config changes apply without bot restart
- **Estimated Effort**: 45 minutes

**Task 6: Move Modules to Folder** (Priority: P1 - Critical Path)
- Move `how_is.py` → `modules/how_is.py`
- Update `main.py` imports (`from modules import reminder_system, how_is`)
- Test all features after move
- **Acceptance**: Bot starts, all modules load correctly
- **Estimated Effort**: 30 minutes

**Task 7: Update Documentation** (Priority: P2 - Important)
- Update `README.md` with reminder system documentation
- Document `reminder_config.py` structure
- Add "Adding New Reminders" guide
- Document behavior on bot restart (buttons stop working)
- Update `.env` example if needed
- **Acceptance**: README has complete reminder system docs
- **Estimated Effort**: 1 hour

**Task 8: Regression Testing** (Priority: P1 - Critical Path)
- Test dog reminder still works at 8:00, 13:00, 20:00
- Test acknowledge button (Yes)
- Test denial button (No) → owner notification
- Test timeout → owner notification after 60 minutes
- Test timezone command
- Test status command
- **Acceptance**: All existing functionality preserved
- **Estimated Effort**: 2 hours (includes wait time for timeout test)

**Task 9: Add Second Reminder (Validation)** (Priority: P2 - Important)
- Add test reminder to `reminder_config.py`
- Use `!testreminder` to verify
- Verify both reminders coexist without interference
- **Acceptance**: Two independent reminders work simultaneously
- **Estimated Effort**: 30 minutes

### Task Dependencies

```
Task 1 (Structure) → Task 2 (Refactor Core)
                  ↘ Task 6 (Move Modules)
                  
Task 2 (Core) → Task 3 (Buttons) → Task 8 (Regression)
             ↘ Task 4 (Commands)
             ↘ Task 5 (Reload)
             
Task 6 (Modules) → Task 8 (Regression)

Task 7 (Docs) - Independent (can run parallel)

Task 8 (Regression) → Task 9 (Validation)
```

**Critical Path**: Task 1 → Task 2 → Task 3 → Task 6 → Task 8 → Task 9  
**Parallel Work**: Task 7 (Docs) can be done anytime after Task 2

### Testing Strategy

**Unit-Level Testing** (Manual):
- `!testreminder dog_walking morning` - Verify reminder sends
- `!testreminder dog_walking noon` - Verify multiple schedules work
- Click "Yes" button - Verify ephemeral response, buttons disable, reminder removed
- Click "No" button - Verify escalation message sent, buttons disable
- Wait 60+ minutes - Verify timeout escalation (or use `!settimeout 1` for faster test)

**Integration Testing**:
- Bot restart - Verify modules load from `modules/` folder
- Add second reminder to config - Verify both run independently
- `!reloadreminders` - Verify config changes apply
- Timezone change - Verify affects all reminders

**Regression Testing** (Critical):
- Existing dog reminder must work identically to current behavior
- All times: 8:00, 13:00, 20:00
- User IDs: 343513966049492999 (target), 143474592529252353 (escalation)
- Timeout: 60 minutes
- All button interactions
- All existing commands

---

## Phase 3: Validation Checklist

### Pre-Merge Validation

- [ ] **Functionality**: All P1 user stories implemented and tested
  - [ ] US-1.1: Scheduled reminder delivery works
  - [ ] US-1.3: Timeout escalation works (60+ minute wait test)
  - [ ] US-1.2: Denial escalation works (optional P2, include if time permits)
  - [ ] US-1.4: Easy configuration via `reminder_config.py`

- [ ] **Regression**: Dog reminder functionality 100% preserved
  - [ ] Morning reminder (8:00) sends correctly
  - [ ] Noon reminder (13:00) sends correctly  
  - [ ] Evening reminder (20:00) sends correctly
  - [ ] Yes button works (acknowledges)
  - [ ] No button works (sends escalation)
  - [ ] Timeout works (1 hour, sends escalation)
  - [ ] All existing commands functional

- [ ] **Code Quality**: Constitution principles upheld
  - [ ] All functions < 50 lines
  - [ ] Module-level logger used throughout
  - [ ] All async Discord calls wrapped in try-except
  - [ ] Error messages logged with `exc_info=True`
  - [ ] Module docstring present
  - [ ] Functions have clear, self-documenting names

- [ ] **Documentation**: Complete and accurate
  - [ ] `README.md` updated with reminder system docs
  - [ ] `reminder_config.py` structure documented with comments
  - [ ] "Adding New Reminders" guide included
  - [ ] Bot restart behavior documented
  - [ ] Example configurations provided

- [ ] **Architecture**: Module-First principles followed
  - [ ] `reminder_system.py` in `modules/` folder
  - [ ] `setup(bot)` function present and correct
  - [ ] No dependencies on other feature modules
  - [ ] `main.py` only imports and calls `setup()`

### Success Criteria Validation

From `spec.md`:

- [ ] **SC-1**: Reminders delivered within 60 seconds of scheduled time
  - Test: Use `!testreminder` and check timestamp in logs
  
- [ ] **SC-2**: User can acknowledge via button click
  - Test: Click "Yes" button, verify ephemeral message and button disable

- [ ] **SC-3**: Timeout escalation sent within 60 seconds after timeout period
  - Test: Wait 60+ minutes (or use `!settimeout 1`), verify escalation message

- [ ] **SC-4**: Escalation user receives clear notification
  - Test: Check escalation user DMs for clear, actionable messages

- [ ] **SC-5**: User can deny and trigger immediate escalation (P2 optional)
  - Test: Click "No" button, verify immediate escalation message

- [ ] **SC-6**: Adding new reminder requires only config file edit
  - Test: Add test reminder to `reminder_config.py`, use `!reloadreminders`, verify works

- [ ] **SC-7**: Reminders operate independently (no crosstalk)
  - Test: Run two reminders simultaneously, verify separate tracking

- [ ] **SC-8**: Module loads without errors on bot startup
  - Test: Restart bot, check logs for clean module initialization

- [ ] **SC-9**: Error logging captures all failures
  - Test: Review logs after test session, verify all errors logged with context

- [ ] **SC-10**: Configuration changes apply via reload command
  - Test: Edit config, run `!reloadreminders`, verify changes active

---

## Phase 4: Deployment & Rollback

### Deployment Plan

**Pre-Deployment**:
1. Commit all changes to `001-reminder-system` branch
2. Run full regression test suite
3. Verify dog reminder config in `reminder_config.py` matches existing hardcoded values
4. Review logs for any unexpected errors

**Deployment Steps**:
1. Announce maintenance window (if applicable)
2. Stop bot process
3. Merge `001-reminder-system` branch to `main`
4. Pull changes on server
5. Verify file structure (`modules/` folder exists, config file present)
6. Start bot process
7. Monitor logs for clean startup
8. Run `!reminderstatus` to verify system loaded
9. Run `!testreminder dog_walking morning` to verify functionality

**Post-Deployment**:
1. Monitor first scheduled reminder (8:00 next day)
2. Verify button interactions work
3. Check escalation notifications (if timeout occurs naturally)
4. Document any issues in GitHub issues

### Rollback Plan

**Rollback Triggers**:
- Dog reminder stops working
- Bot fails to start
- Module errors in logs
- Button interactions fail

**Rollback Steps**:
1. Stop bot process
2. Checkout previous commit: `git checkout <previous-main-commit>`
3. Restart bot process
4. Verify dog reminder works with old code
5. Post mortem: Review logs, identify failure cause
6. Fix in branch, re-test before re-deployment

**Data Preservation**:
- No database/persistent state (in-memory only)
- Rollback is safe (no data loss)
- Pending reminders will be lost (acceptable, will resend next scheduled time)

---

## Notes & Open Questions

### Implementation Notes
- **Backward Compatibility**: Existing `!dog*` commands preserved for user familiarity
- **Performance**: No performance concerns (10-20 reminders, 1-minute poll loop)
- **Button Timeout**: Discord buttons expire after 15 minutes of inactivity (Discord limitation), our custom timeout tracking handles escalation
- **Restart Behavior**: Bot restart clears pending reminders and button handlers (documented, acceptable)

### Open Questions
- [ ] **Q**: Should `reminder_config.py` be git-ignored for privacy?
  - **A**: TBD - Consider `.env` pattern, maybe `reminder_config.example.py` in git
  
- [ ] **Q**: Should we support more complex schedules (weekly, monthly)?
  - **A**: Out of scope for v1, simple daily schedules sufficient per spec

- [ ] **Q**: Should timeout be per-reminder or global?
  - **A**: Per-reminder (already in config schema) for flexibility

### Future Enhancements (Out of Scope)
- Button persistence across bot restarts (requires database)
- Web UI for configuration editing
- Reminder history/analytics
- Recurring patterns (weekly/monthly schedules)
- Multiple target users per reminder
- Custom button labels per reminder

---

**Plan Complete**: Ready for implementation. Start with Task 1 (Create Structure).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
