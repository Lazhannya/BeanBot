# Tasks: Discord DM Support for Slash Commands

**Input**: Design documents from `/specs/003-dm-support/`
**Prerequisites**: plan.md, spec.md, existing slash command implementation (002-slash-commands)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup & Analysis

**Purpose**: Analyze current implementation and prepare for DM support

- [x] T001 [P] Analyze current slash command registration in `main.py` to understand guild-only limitations
- [x] T002 [P] Research Discord.py global command registration patterns for DM support
- [x] T003 [P] Document current autocomplete function dependencies on guild context in `modules/reminder_system.py`
- [x] T004 Create DM support feature branch and documentation structure in `specs/003-dm-support/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core DM infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Implement global command registration system in `main.py` for DM support
- [x] T006 [P] Create DM context detection utility functions in `modules/reminder_system.py`
- [x] T007 [P] Adapt owner permission checking to work in DM context in `modules/reminder_system.py`
- [x] T008 Update command tree sync logic to register both guild and global commands in `main.py`

**Checkpoint**: DM infrastructure ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Basic DM Slash Commands (Priority: P1) 🎯 MVP

**Goal**: Enable core reminder slash commands to work in Discord DMs

**Independent Test**: Bot owner can use `/reminder test`, `/reminder status`, `/reminder list`, `/dog test`, `/dog status` in DMs with proper functionality and permission enforcement

### Implementation for User Story 1

- [ ] T009 [P] [US1] Enable `/reminder test` command for DM usage in `modules/reminder_system.py`
- [ ] T010 [P] [US1] Enable `/reminder status` command for DM usage in `modules/reminder_system.py`
- [ ] T011 [P] [US1] Enable `/reminder list` command for DM usage in `modules/reminder_system.py`
- [ ] T012 [P] [US1] Enable `/dog test` command for DM usage in `modules/reminder_system.py`
- [ ] T013 [P] [US1] Enable `/dog status` command for DM usage in `modules/reminder_system.py`
- [ ] T014 [US1] Implement DM-specific permission checking for owner-only commands in `modules/reminder_system.py`
- [ ] T015 [US1] Add clear permission denial messages for non-owner users in DMs in `modules/reminder_system.py`
- [ ] T016 [US1] Update command logging to include DM context information in `modules/reminder_system.py`

**Checkpoint**: Basic DM commands functional with proper permission enforcement

---

## Phase 4: User Story 2 - DM Autocomplete Support (Priority: P1)

**Goal**: Ensure all autocomplete functions work properly in DM context

**Independent Test**: All command parameters show proper autocomplete suggestions in DMs with <3 second response time

### Implementation for User Story 2

- [x] T017 [P] [US2] Adapt `reminder_name_autocomplete` function for DM context in `modules/reminder_system.py`
- [x] T018 [P] [US2] Adapt `schedule_label_autocomplete` function for DM context in `modules/reminder_system.py`
- [x] T019 [P] [US2] Adapt `timezone_autocomplete` function for DM context in `modules/reminder_system.py`
- [x] T020 [P] [US2] Adapt dog schedule autocomplete functions for DM context in `modules/reminder_system.py`
- [x] T021 [US2] Add graceful fallback handling for missing guild context in autocomplete in `modules/reminder_system.py`
- [x] T022 [US2] Implement performance monitoring for DM autocomplete responses in `modules/reminder_system.py`
- [x] T023 [US2] Add error handling for autocomplete failures specific to DM context in `modules/reminder_system.py`

**Checkpoint**: All autocomplete functions work reliably in DMs with proper error handling

---

## Phase 5: User Story 3 - DM Configuration Commands (Priority: P2)

**Goal**: Enable configuration commands to work in DMs for bot owner

**Independent Test**: Bot owner can use `/reminder reload`, `/reminder timeout`, `/dog timezone`, `/dog set-time` in DMs with proper persistence

### Implementation for User Story 3

- [ ] T024 [P] [US3] Enable `/reminder reload` command for DM usage with owner-only restriction in `modules/reminder_system.py`
- [ ] T025 [P] [US3] Enable `/reminder timeout` command for DM usage with owner-only restriction in `modules/reminder_system.py`
- [ ] T026 [P] [US3] Enable `/dog timezone` command for DM usage with owner-only restriction in `modules/reminder_system.py`
- [ ] T027 [P] [US3] Enable `/dog set-time` command for DM usage with owner-only restriction in `modules/reminder_system.py`
- [ ] T028 [US3] Verify configuration persistence works correctly when changes are made via DM in `modules/reminder_system.py`
- [ ] T029 [US3] Implement enhanced feedback messages for successful/failed configuration changes in DMs in `modules/reminder_system.py`
- [ ] T030 [US3] Add comprehensive logging for all DM configuration command usage in `modules/reminder_system.py`

**Checkpoint**: All configuration commands functional in DMs with proper persistence and feedback

---

## Phase 6: User Story 4 - Enhanced DM User Experience (Priority: P2)

**Goal**: Provide helpful guidance and clear error messages for DM users

**Independent Test**: DM users receive clear, helpful messages about capabilities and limitations with proper onboarding

### Implementation for User Story 4

- [ ] T031 [P] [US4] Update `/reminder help` command with DM-specific guidance in `modules/reminder_system.py`
- [ ] T032 [P] [US4] Update `/dog help` command with DM usage instructions in `modules/reminder_system.py`
- [ ] T033 [P] [US4] Create helpful messages for non-owner users explaining DM limitations in `modules/reminder_system.py`
- [ ] T034 [P] [US4] Enhance error messages to clearly indicate DM context when relevant in `modules/reminder_system.py`
- [ ] T035 [US4] Add hints about available functionality to DM command responses in `modules/reminder_system.py`
- [ ] T036 [US4] Implement welcome message system for first-time DM users in `modules/reminder_system.py`
- [ ] T037 [US4] Create DM onboarding flow with capability overview in `modules/reminder_system.py`

**Checkpoint**: Enhanced DM user experience with clear guidance and feedback

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, testing, and final validation

- [ ] T038 [P] Update `README.md` with DM usage section documenting all DM-compatible commands
- [ ] T039 [P] Add DM setup guide and troubleshooting section to `README.md`
- [ ] T040 [P] Document DM vs guild command differences in `README.md`
- [ ] T041 [P] Create comprehensive DM functionality test script in `test_dm_commands.py`
- [ ] T042 Test DM command registration and sync process across different Discord environments
- [ ] T043 Full regression test: Verify all guild functionality remains unchanged after DM implementation
- [ ] T044 Full DM feature test: Test all DM commands with various user contexts (owner/non-owner)
- [ ] T045 Performance test: Verify DM command response times meet Discord's 3-second interaction limit
- [ ] T046 Security audit: Verify owner-only restrictions are properly enforced in DM context

**Checkpoint**: All features complete, documented, and validated for DM functionality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories  
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Independent
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - May benefit from US1 completion for testing
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent  
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Benefits from US1-3 for comprehensive guidance

### Within Each User Story

- Commands marked [P] can be implemented in parallel (different command handlers)
- Core functionality before enhanced features
- Error handling after main implementation
- Logging and monitoring after functional implementation

### Parallel Opportunities

- **Setup tasks**: T001, T002, T003 can run in parallel
- **Foundational tasks**: T006, T007 can run in parallel  
- **US1 commands**: T009-T013 can run in parallel (different command methods)
- **US2 autocomplete**: T017-T020 can run in parallel (different autocomplete functions)
- **US3 config commands**: T024-T027 can run in parallel (different command methods)
- **US4 help/messages**: T031-T034 can run in parallel (different message types)
- **Polish documentation**: T038-T041 can run in parallel (different doc sections)

---

## Parallel Example: User Story 1

```bash
# Launch all basic commands for User Story 1 together:
Task: "Enable /reminder test command for DM usage in modules/reminder_system.py"
Task: "Enable /reminder status command for DM usage in modules/reminder_system.py"  
Task: "Enable /reminder list command for DM usage in modules/reminder_system.py"
Task: "Enable /dog test command for DM usage in modules/reminder_system.py"
Task: "Enable /dog status command for DM usage in modules/reminder_system.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1-2 Only)

1. Complete Phase 1: Setup & Analysis
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Basic DM Commands)
4. Complete Phase 4: User Story 2 (DM Autocomplete)  
5. **STOP and VALIDATE**: Test core DM functionality independently
6. Deploy/demo MVP DM support

### Incremental Delivery

1. Complete Setup + Foundational → DM infrastructure ready
2. Add User Story 1 → Test basic DM commands → Deploy/Demo (MVP!)
3. Add User Story 2 → Test autocomplete in DMs → Deploy/Demo
4. Add User Story 3 → Test configuration in DMs → Deploy/Demo
5. Add User Story 4 → Test enhanced UX → Deploy/Demo
6. Each story adds DM value without breaking existing functionality

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Basic Commands)
   - Developer B: User Story 2 (Autocomplete)
   - Developer C: User Story 3 (Configuration)
3. Stories complete independently and integrate seamlessly

---

## Command Tree Structure

**Current Guild Commands** (preserved):
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

**New Global Commands** (for DM support):
```
Same structure as above, but registered globally for DM access
Owner-only restrictions enforced in DM context
Enhanced error messaging for DM limitations
```

---

## Task Count Summary

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 4 tasks  
- **Phase 3 (US1 - P1)**: 8 tasks
- **Phase 4 (US2 - P1)**: 7 tasks
- **Phase 5 (US3 - P2)**: 7 tasks
- **Phase 6 (US4 - P2)**: 7 tasks
- **Phase 7 (Polish)**: 9 tasks

**Total**: 46 tasks

**By User Story**:
- US1 (Basic DM Commands): 8 tasks
- US2 (DM Autocomplete): 7 tasks  
- US3 (DM Configuration): 7 tasks
- US4 (Enhanced DM UX): 7 tasks
- Infrastructure: 8 tasks (Setup + Foundational)
- Polish: 9 tasks

**Parallel Opportunities**: 26 tasks marked [P] can run concurrently within their phases

---

## Notes

- [P] tasks = different files/functions, no dependencies
- [Story] label maps task to specific user story for traceability  
- Each user story should be independently completable and testable
- DM implementation preserves all existing guild functionality
- Owner permission enforcement is critical for DM security
- Global command registration required for DM slash command support
- All autocomplete functions must handle missing guild context gracefully