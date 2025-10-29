---
description: "Task list for Discord Slash Commands with Autocomplete implementation"
---

# Tasks: Discord Slash Commands with Autocomplete

**Input**: User request to convert `!` prefix commands to `/` slash commands with autocomplete functionality
**Prerequisites**: Existing reminder system implementation in `/modules/reminder_system.py`
**Branch**: `002-slash-commands`

**Organization**: Tasks are organized by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **BeanBot**: Feature modules in `modules/` folder
- **Configuration**: `reminder_config.py` at repository root
- **Main orchestration**: `main.py` at repository root
- Each feature MUST be a separate module with a `setup(bot)` function

---

## Phase 1: Setup (Slash Command Infrastructure)

**Purpose**: Set up Discord slash command infrastructure and registration

- [x] T001 Create new branch `002-slash-commands` from current main branch
- [x] T002 Update `main.py` to enable slash command tree synchronization with Discord API
- [x] T003 Add slash command permissions configuration in `main.py` (guild-specific vs global commands)

**Acceptance**: Branch exists, bot can register slash commands with Discord

---

## Phase 2: Foundational (Core Slash Command Conversion)

**Purpose**: Core infrastructure for slash commands that MUST be complete before user story features can work

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 In `modules/reminder_system.py`, create slash command group `/reminder` as the main command group
- [x] T005 In `modules/reminder_system.py`, implement autocomplete functions for reminder names using `reminder_config.REMINDERS`
- [x] T006 In `modules/reminder_system.py`, implement autocomplete functions for schedule labels based on selected reminder
- [x] T007 In `modules/reminder_system.py`, create utility function to sync slash commands on module setup

**Checkpoint**: Foundation ready - slash command infrastructure established, autocomplete framework implemented

---

## Phase 3: User Story 1 - Basic Reminder Management Commands (Priority: P1) 🎯 MVP

**Goal**: Users can test and manage reminders using modern Discord slash commands with intelligent autocomplete

**Independent Test**: Use `/reminder test` with autocomplete to select reminder name and schedule, verify reminder delivery with buttons

### Implementation for User Story 1

- [x] T008 [US1] Convert `!testreminder` to `/reminder test` slash command in `modules/reminder_system.py`
- [x] T009 [US1] Add autocomplete for reminder name parameter in `/reminder test` command
- [x] T010 [US1] Add autocomplete for schedule label parameter in `/reminder test` command (filtered by selected reminder)
- [x] T011 [US1] Convert `!reminderstatus` to `/reminder status` slash command in `modules/reminder_system.py`
- [x] T012 [US1] Convert `!listreminders` to `/reminder list` slash command in `modules/reminder_system.py`
- [x] T013 [US1] Add parameter descriptions and help text to all User Story 1 slash commands

**Checkpoint**: Basic reminder management works with modern Discord UI - delivers immediate value

---

## Phase 4: User Story 2 - Configuration Management Commands (Priority: P1)

**Goal**: Administrators can manage reminder system configuration using slash commands with intelligent autocomplete

**Independent Test**: Use `/reminder reload` to reload configuration, verify changes take effect without bot restart

### Implementation for User Story 2

- [x] T014 [US2] Convert `!reloadreminders` to `/reminder reload` slash command in `modules/reminder_system.py`
- [x] T015 [US2] Convert `!settimeout` to `/reminder timeout` slash command with autocomplete for reminder names in `modules/reminder_system.py`
- [x] T016 [US2] Add validation and error handling for `/reminder timeout` command parameters
- [x] T017 [US2] Add parameter descriptions and help text for all User Story 2 slash commands

**Checkpoint**: Configuration management modernized - administrators have intuitive command interface

---

## Phase 5: User Story 3 - Legacy Dog Commands Modernization (Priority: P2)

**Goal**: Legacy dog-specific commands are converted to slash commands while maintaining backward compatibility

**Independent Test**: Use `/dog test` and other dog commands, verify they work identically to original `!` commands

### Implementation for User Story 3

- [x] T018 [US3] Convert `!testreminderdog` to `/dog test` slash command with autocomplete for time labels in `modules/reminder_system.py`
- [x] T019 [US3] Convert `!dogstatus` to `/dog status` slash command in `modules/reminder_system.py`
- [x] T020 [US3] Convert `!dogtimezone` to `/dog timezone` slash command with timezone validation in `modules/reminder_system.py`
- [x] T021 [US3] Convert `!setdogreminder` to `/dog set-reminder` slash command with autocomplete in `modules/reminder_system.py`
- [x] T022 [US3] Convert `!setdogowner` to `/dog set-owner` slash command with user parameter in `modules/reminder_system.py`
- [x] T023 [US3] Convert `!setremindertime` to `/dog set-time` slash command with autocomplete for reminder types in `modules/reminder_system.py`

**Checkpoint**: Legacy functionality preserved with modern interface - backward compatibility maintained

---

## Phase 6: User Story 4 - Enhanced Autocomplete Features (Priority: P2)

**Goal**: Advanced autocomplete features that provide intelligent suggestions and validation

**Independent Test**: Test autocomplete responses are contextual, accurate, and provide helpful suggestions

### Implementation for User Story 4

- [x] T024 [P] [US4] Implement dynamic autocomplete that filters schedule labels based on selected reminder name in `modules/reminder_system.py`
- [x] T025 [P] [US4] Add timezone autocomplete with common timezone suggestions in `modules/reminder_system.py`
- [x] T026 [P] [US4] Implement user autocomplete for owner/target user selection commands in `modules/reminder_system.py`
- [x] T027 [US4] Add validation messages for invalid parameter combinations in slash commands
- [x] T028 [US4] Implement error handling for autocomplete failures (config unavailable, etc.)

**Checkpoint**: Enhanced user experience - intelligent autocomplete provides guided command usage

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [x] T029 [P] Update `README.md` with slash commands section documenting all new `/reminder` and `/dog` commands
- [x] T030 [P] In `README.md`, add autocomplete usage guide with screenshots or examples
- [x] T031 [P] In `README.md`, document migration from `!` commands to `/` commands for existing users
- [x] T032 [P] Add comprehensive logging for all slash command invocations in `modules/reminder_system.py`
- [x] T033 [P] Create slash command help system with `/reminder help` and `/dog help` commands
- [x] T034 Implement slash command permissions (owner-only vs public commands) in `modules/reminder_system.py`
- [x] T035 Test slash command registration and sync process across different Discord servers
- [x] T036 Full regression test: Verify all legacy functionality works through new slash commands
- [x] T037 Full feature test: Test all autocomplete scenarios with various reminder configurations
- [x] T038 Performance test: Verify slash command response times meet Discord's 3-second interaction limit

**Checkpoint**: All features complete, documented, and validated with modern Discord interface

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational (Phase 2) completion
  - Phase 3 (US1 - P1): Can start immediately after Phase 2
  - Phase 4 (US2 - P1): Can start after Phase 3 or in parallel
  - Phase 5 (US3 - P2): Can start after Phase 3 or in parallel  
  - Phase 6 (US4 - P2): Can start after Phase 3 or in parallel
- **Polish (Phase 7)**: Depends on all user stories (Phase 3-6) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational - No dependencies on other stories (MVP)
- **User Story 2 (P1)**: Depends on US1 (needs basic slash command structure) - Independent test criteria
- **User Story 3 (P2)**: Depends on US1 (needs slash command patterns) - Independent test criteria
- **User Story 4 (P2)**: Depends on US1 (needs base commands for enhancement) - Independent test criteria

### Critical Path

**Sequential (MVP)**: T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013 (US1 complete - MVP ready)

**Full Feature**: MVP path + T014-T017 (US2) + T018-T023 (US3) + T024-T028 (US4) + T029-T038 (Polish)

### Parallel Opportunities

**Phase 1 (Setup)**: T001, T002, T003 can run sequentially (fast, <1 hour total)

**Phase 2 (Foundational)**: T005, T006 can run in parallel (different functions), others sequential

**Phase 3 (US1)**: T008-T010 can run in parallel (different commands), T011-T012 can run in parallel, then T013

**Phase 4 (US2)**: T014-T016 can run in parallel (different commands), then T017

**Phase 5 (US3)**: T018-T020 can run in parallel, T021-T023 can run in parallel (different commands)

**Phase 6 (US4)**: T024-T026 all parallel (different autocomplete functions), then T027-T028 sequentially

**Phase 7 (Polish)**: T029-T033 all parallel (different files), then T034-T038 sequentially

**Multi-Story Parallelism**: After US1 complete (T013), US2 (T014-T017), US3 (T018-T023), and US4 (T024-T028) can all run in parallel

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Deliver First**: User Story 1 only (T001-T013)
- Basic slash commands for reminder testing and status
- Core autocomplete functionality for reminder names and schedules
- Modern Discord interface for essential operations
- ~6-8 hours of work

**Test Criteria**: `/reminder test` works with autocomplete, `/reminder status` shows system state, `/reminder list` displays configuration

### Incremental Delivery

**Iteration 1 (MVP)**: US1 - Basic slash commands + autocomplete (T001-T013)

**Iteration 2**: + US2 - Configuration management (T014-T017)
- Adds admin slash commands for system management
- ~2 hours additional work

**Iteration 3**: + US3 - Legacy command modernization (T018-T023)
- Preserves backward compatibility with modern interface
- ~3 hours additional work

**Iteration 4**: + US4 - Enhanced autocomplete (T024-T028)
- Advanced autocomplete features and validation
- ~2 hours additional work

**Iteration 5**: Polish & Documentation (T029-T038)
- Production-ready slash command system
- ~3 hours additional work

**Total Estimated Effort**: ~16-18 hours across 5 iterations

### Testing Strategy

**Manual Testing** (Discord slash commands):
- Use Discord's built-in slash command interface for testing
- Verify autocomplete suggestions appear correctly
- Test parameter validation and error messages
- Ensure backward compatibility with existing functionality

**Regression Priority**: All existing reminder functionality MUST work through slash commands

---

## Technical Implementation Notes

### Discord.py Slash Command Patterns

```python
# Basic slash command
@bot.tree.command(name="test", description="Test a reminder")
async def test_reminder(interaction: discord.Interaction, reminder: str, schedule: str = None):
    pass

# Slash command with autocomplete
@bot.tree.command(name="test", description="Test a reminder")
@app_commands.describe(
    reminder="Name of the reminder to test",
    schedule="Schedule label to test (optional)"
)
async def test_reminder(interaction: discord.Interaction, reminder: str, schedule: str = None):
    pass

# Autocomplete function
@test_reminder.autocomplete('reminder')
async def reminder_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=r['name'], value=r['name']) 
        for r in reminder_config.REMINDERS 
        if current.lower() in r['name'].lower()
    ][:25]  # Discord limit
```

### Command Group Structure

```
/reminder
  ├── test [reminder] [schedule]     # Test reminder delivery
  ├── status                         # Show system status
  ├── list                          # List all reminders  
  ├── reload                        # Reload configuration
  └── timeout [reminder] [minutes]   # Set timeout

/dog
  ├── test [time]                   # Test dog reminder
  ├── status                        # Dog reminder status
  ├── timezone [zone]               # Set timezone
  ├── set-reminder [user]           # Set dog reminder user
  ├── set-owner [user]             # Set dog owner
  └── set-time [type] [hour] [min]  # Set reminder time
```

---

## Task Count Summary

- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundational)**: 4 tasks
- **Phase 3 (US1 - P1)**: 6 tasks
- **Phase 4 (US2 - P1)**: 4 tasks
- **Phase 5 (US3 - P2)**: 6 tasks
- **Phase 6 (US4 - P2)**: 5 tasks
- **Phase 7 (Polish)**: 10 tasks

**Total**: 38 tasks

**By User Story**:
- US1 (Basic Commands): 6 tasks
- US2 (Configuration): 4 tasks  
- US3 (Legacy Migration): 6 tasks
- US4 (Enhanced Autocomplete): 5 tasks
- Infrastructure: 7 tasks (Setup + Foundational)
- Polish: 10 tasks

**Parallel Opportunities**: 12 tasks marked [P] can run concurrently within their phases

**MVP Task Count**: 13 tasks (T001-T013) - approximately 34% of total work delivers core slash command functionality

---

## Autocomplete Implementation Details

### Reminder Name Autocomplete
- Source: `reminder_config.REMINDERS` list
- Filter: Case-insensitive substring matching
- Limit: 25 choices (Discord maximum)

### Schedule Label Autocomplete  
- Source: Selected reminder's `schedules` list
- Filter: Dynamic based on reminder parameter
- Context-aware: Only shows labels for the selected reminder

### Timezone Autocomplete
- Source: Common timezone list (pytz.common_timezones)
- Filter: Starts-with matching for performance
- Popular choices first: UTC, America/New_York, Europe/London, etc.

### User Autocomplete
- Source: Discord server members (for owner/target selection)
- Filter: Username and display name matching
- Security: Respects Discord privacy settings