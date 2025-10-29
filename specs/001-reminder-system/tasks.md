---
description: "Task list for Modular Reminder System implementation"
---

# Tasks: Modular Reminder System

**Input**: Design documents from `/specs/001-reminder-system/`
**Prerequisites**: plan.md, spec.md
**Branch**: `001-reminder-system`

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

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

## Phase 1: Setup (Project Structure)

**Purpose**: Create project structure and foundational configuration

- [x] T001 Create `modules/` directory at repository root
- [x] T002 Create `reminder_config.py` at repository root with dog reminder configuration (schedules: 8:00, 13:00, 20:00; target_user_id: 343513966049492999; escalation_user_id: 143474592529252353; timeout: 60 minutes)
- [x] T003 Update `.gitignore` if needed to handle potential config variants

**Acceptance**: Directory structure exists, configuration file has complete dog reminder settings

---

## Phase 2: Foundational (Core Module Refactor)

**Purpose**: Core infrastructure that MUST be complete before user story features can work

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Copy `dog_reminder.py` to `modules/reminder_system.py`
- [x] T005 In `modules/reminder_system.py`, replace hardcoded config values with import from `reminder_config.py`
- [x] T006 In `modules/reminder_system.py`, rename `DogReminderView` class to `ReminderView` and generalize for any reminder
- [x] T007 In `modules/reminder_system.py`, update `_reminder_loop()` method to iterate through all reminders in `reminder_config.REMINDERS` list
- [x] T008 In `modules/reminder_system.py`, update `send_dog_reminder()` method to `send_reminder()` accepting reminder config dict and schedule dict as parameters
- [x] T009 Move `how_is.py` to `modules/how_is.py`
- [x] T010 Update `main.py` imports to use `from modules import reminder_system, how_is` pattern

**Checkpoint**: Foundation ready - module structure established, user story features can now be implemented

---

## Phase 3: User Story 1 - Basic Scheduled Reminder Delivery (Priority: P1) 🎯 MVP

**Goal**: Users receive scheduled reminders at configured times and can acknowledge them

**Independent Test**: Configure a reminder with specific time, wait for scheduled time, receive reminder message, click acknowledge button, verify reminder completes

### Implementation for User Story 1

- [x] T011 [US1] In `modules/reminder_system.py`, update `send_reminder()` to use config `messages` dict for message text lookup by schedule label
- [x] T012 [US1] In `modules/reminder_system.py`, update `send_reminder()` to format reminder_id as `{reminder_name}_{schedule_label}_{YYYYMMDD}`
- [x] T013 [US1] In `modules/reminder_system.py`, update `ReminderView.yes_button()` callback to use generalized reminder tracking (find by message_id, remove from pending_reminders)
- [x] T014 [US1] In `modules/reminder_system.py`, verify logging for delivery and acknowledgment events includes reminder name and schedule label
- [x] T015 [US1] Test reminder delivery: Add `!testreminder` command in `modules/reminder_system.py` accepting reminder name and optional schedule label parameters
- [x] T016 [US1] Regression test: Verify dog reminder works at 8:00, 13:00, 20:00 with acknowledge button functional

**Checkpoint**: Basic reminder delivery and acknowledgment works - delivers immediate value

---

## Phase 4: User Story 3 - Timeout and Automatic Escalation (Priority: P1)

**Goal**: Reminders that go unacknowledged trigger automatic escalation notification after timeout period

**Independent Test**: Configure reminder with short timeout, don't respond, verify escalation user receives notification after timeout expires

**Note**: US3 before US2 because timeout is P1 (critical) while denial is P2

### Implementation for User Story 3

- [x] T017 [US3] In `modules/reminder_system.py`, update `check_reminder_timeout()` to use config `escalation_user_id` instead of hardcoded owner ID
- [x] T018 [US3] In `modules/reminder_system.py`, update `check_reminder_timeout()` to use config `timeout_message` with `{label}` placeholder replacement
- [x] T019 [US3] In `modules/reminder_system.py`, update timeout tracking to use config `timeout_minutes` converted to seconds
- [x] T020 [US3] In `modules/reminder_system.py`, verify logging for timeout and escalation events includes reminder name, schedule label, and timeout duration
- [x] T021 [US3] Test timeout: Use `!settimeout` command to set short timeout (1 minute), trigger test reminder, wait, verify escalation message sent
- [x] T022 [US3] Regression test: Verify dog reminder timeout works after 60 minutes with correct escalation message to owner

**Checkpoint**: Timeout escalation works - ensures accountability for unacknowledged reminders

---

## Phase 5: User Story 2 - Reminder Denial (Priority: P2)

**Goal**: Users can explicitly deny reminders, triggering immediate escalation notification

**Independent Test**: Receive reminder, click deny button, verify escalation user receives denial notification immediately

### Implementation for User Story 2

- [x] T023 [US2] In `modules/reminder_system.py`, update `ReminderView.no_button()` callback to use config `escalation_user_id` instead of hardcoded owner ID
- [x] T024 [US2] In `modules/reminder_system.py`, update denial escalation message to use reminder name and schedule label from pending_reminders tracking
- [x] T025 [US2] In `modules/reminder_system.py`, add support for optional config `denial_message` field (fallback to default if not present)
- [x] T026 [US2] In `modules/reminder_system.py`, verify logging for denial and denial-escalation events includes complete reminder context
- [x] T027 [US2] Test denial: Trigger test reminder, click "No" button, verify immediate escalation notification sent
- [x] T028 [US2] Regression test: Verify dog reminder denial button sends escalation to owner with correct message

**Checkpoint**: Denial escalation works - enables proactive status communication

---

## Phase 6: User Story 4 - Easy Reminder Configuration (Priority: P2)

**Goal**: Bot administrators can add/edit reminders via simple config file edits without bot restart

**Independent Test**: Edit `reminder_config.py` to add new reminder, reload config, verify new reminder fires at scheduled time

### Implementation for User Story 4

- [x] T029 [P] [US4] In `modules/reminder_system.py`, implement `reload_config()` method using `importlib.reload(reminder_config)` and reassign `self.reminders` from reloaded config
- [x] T030 [P] [US4] In `modules/reminder_system.py`, add graceful error handling in `reload_config()` for invalid config (log error, keep existing config, notify user)
- [x] T031 [US4] In `modules/reminder_system.py`, add `!reloadreminders` Discord command (owner only) that calls `reload_config()` and confirms success/failure
- [x] T032 [P] [US4] In `modules/reminder_system.py`, add `!reminderstatus` Discord command showing all active reminders with pending count
- [x] T033 [P] [US4] In `modules/reminder_system.py`, add `!listreminders` Discord command displaying all configured reminders from config
- [x] T034 [US4] Add second test reminder to `reminder_config.py` (medication example: morning/evening doses)
- [x] T035 [US4] Test config reload: Edit config to add reminder, run `!reloadreminders`, use `!testreminder` to verify new reminder works
- [x] T036 [US4] Test independence: Verify both dog_walking and medication reminders coexist without interference

**Checkpoint**: Configuration system complete - easy to add/modify reminders without code changes

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [x] T037 [P] Update `README.md` with "Reminder System" section documenting the feature
- [x] T038 [P] In `README.md`, document `reminder_config.py` structure with example reminder configuration
- [x] T039 [P] In `README.md`, add "Adding New Reminders" guide with step-by-step instructions
- [x] T040 [P] In `README.md`, document bot restart behavior (pending reminders cleared, buttons stop working)
- [x] T041 [P] In `reminder_config.py`, add comprehensive comments explaining each config field and format requirements
- [x] T042 [P] In `modules/reminder_system.py`, add module docstring explaining purpose, setup, and configuration
- [x] T043 Verify all constitution gates: Module-First Architecture, functions <50 lines, comprehensive error handling, module logger, observability
- [x] T044 Full regression test: Run through all dog reminder scenarios (morning/noon/evening delivery, acknowledge, deny, timeout)
- [x] T045 Full feature test: Test all four user stories end-to-end with both dog_walking and medication reminders
- [x] T046 Review logs for completeness: Verify all events logged with timestamps, user info, and reminder context

**Checkpoint**: All features complete, documented, and validated

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational (Phase 2) completion
  - Phase 3 (US1 - P1): Can start immediately after Phase 2
  - Phase 4 (US3 - P1): Can start after Phase 3 or in parallel
  - Phase 5 (US2 - P2): Can start after Phase 3 or in parallel
  - Phase 6 (US4 - P2): Can start after Phase 3 or in parallel
- **Polish (Phase 7)**: Depends on all user stories (Phase 3-6) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational - No dependencies on other stories (MVP)
- **User Story 3 (P1)**: Depends on US1 (needs reminder delivery working) - Independent test criteria
- **User Story 2 (P2)**: Depends on US1 (needs reminder delivery working) - Independent test criteria
- **User Story 4 (P2)**: Depends on US1 (needs base system working) - Independent test criteria

### Critical Path

**Sequential (MVP)**: T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013 → T014 → T015 → T016 (US1 complete - MVP ready)

**Full Feature**: MVP path + T017-T022 (US3) + T023-T028 (US2) + T029-T036 (US4) + T037-T046 (Polish)

### Parallel Opportunities

**Phase 1 (Setup)**: T001, T002, T003 can run sequentially (fast, <30 min total)

**Phase 2 (Foundational)**: Must run sequentially due to file dependencies (T004-T010)

**Phase 3 (US1)**: T011-T014 can run in parallel (all editing same file but different functions), then T015-T016 sequentially

**Phase 4 (US3)**: T017-T020 can run in parallel (different functions), then T021-T022 sequentially

**Phase 5 (US2)**: T023-T026 can run in parallel (different functions), then T027-T028 sequentially

**Phase 6 (US4)**: T029-T030 parallel, T032-T033 parallel, then T031, then T034-T036 sequentially

**Phase 7 (Polish)**: T037-T042 all parallel (different files), then T043-T046 sequentially

**Multi-Story Parallelism**: After US1 complete (T016), US3 (T017-T022), US2 (T023-T028), and US4 (T029-T036) can all run in parallel if team capacity allows

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Deliver First**: User Story 1 only (T001-T016)
- Basic reminder delivery and acknowledgment
- Preserves existing dog reminder functionality
- Delivers immediate value (automated scheduled notifications)
- ~4-5 hours of work

**Test Criteria**: Dog reminder sends at 8:00/13:00/20:00, user can acknowledge, buttons disable after response

### Incremental Delivery

**Iteration 1 (MVP)**: US1 - Basic delivery + acknowledgment (T001-T016)

**Iteration 2**: + US3 - Timeout escalation (T017-T022)
- Adds accountability layer
- ~2 hours additional work

**Iteration 3**: + US2 - Denial escalation (T023-T028)
- Adds explicit denial workflow
- ~1.5 hours additional work

**Iteration 4**: + US4 - Easy configuration (T029-T036)
- Enables multi-reminder use cases
- ~2 hours additional work

**Iteration 5**: Polish & Documentation (T037-T046)
- Production-ready feature
- ~2 hours additional work

**Total Estimated Effort**: ~11-12 hours across 5 iterations

### Testing Strategy

**Manual Testing** (no automated tests - matches project pattern):
- Use `!testreminder` command for instant validation
- Use `!settimeout 1` for fast timeout testing (avoid 60-minute waits)
- Test each user story independently using test commands
- Full regression suite before merge (T044-T045)

**Regression Priority**: Dog reminder functionality MUST work identically after refactor (existing user dependency)

---

## Task Count Summary

- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundational)**: 7 tasks
- **Phase 3 (US1 - P1)**: 6 tasks
- **Phase 4 (US3 - P1)**: 6 tasks
- **Phase 5 (US2 - P2)**: 6 tasks
- **Phase 6 (US4 - P2)**: 8 tasks
- **Phase 7 (Polish)**: 10 tasks

**Total**: 46 tasks

**By User Story**:
- US1 (Basic Delivery): 6 tasks
- US3 (Timeout): 6 tasks
- US2 (Denial): 6 tasks
- US4 (Configuration): 8 tasks
- Infrastructure: 10 tasks (Setup + Foundational)
- Polish: 10 tasks

**Parallel Opportunities**: 15 tasks marked [P] can run concurrently within their phases

**MVP Task Count**: 16 tasks (T001-T016) - approximately 35% of total work delivers core functionality
