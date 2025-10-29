# Feature Specification: Discord DM Support for Slash Commands

## Feature Summary

**Feature**: Enable slash commands to work in Discord Direct Messages (DMs)
**Priority**: P2 (Enhancement)
**Effort**: Medium (3-5 days)

Enable the existing slash command system to work in Discord Direct Messages, allowing users to interact with BeanBot privately for reminder management.

## User Stories

### User Story 1: Basic DM Slash Commands (Priority: P1)
**As a** bot owner  
**I want** to use reminder slash commands in DMs  
**So that** I can manage reminders privately without cluttering server channels

**Acceptance Criteria:**
- [ ] `/reminder test` works in DMs with full functionality
- [ ] `/reminder status` displays system status in DMs  
- [ ] `/reminder list` shows configured reminders in DMs
- [ ] `/dog test` works in DMs for dog reminders
- [ ] `/dog status` displays dog reminder status in DMs
- [ ] Owner permission checks work correctly in DM context
- [ ] Non-owner users receive clear permission denial messages in DMs

**Definition of Done:**
- All basic view commands functional in DMs
- Permission system adapted for DM context
- Error handling provides clear DM-specific feedback

---

### User Story 2: DM Autocomplete Support (Priority: P1)
**As a** bot owner using DMs  
**I want** autocomplete to work for all command parameters  
**So that** I can efficiently select reminders and schedules without memorizing names

**Acceptance Criteria:**
- [ ] Reminder name autocomplete works in DMs
- [ ] Schedule label autocomplete functions in DM context
- [ ] Timezone autocomplete provides suggestions in DMs
- [ ] Dog schedule type autocomplete works in DMs
- [ ] Autocomplete gracefully handles missing guild context
- [ ] Performance remains under 3 seconds for autocomplete responses in DMs

**Definition of Done:**
- All autocomplete functions work in DMs
- No errors or timeouts in DM autocomplete
- Performance meets Discord's interaction response requirements

---

### User Story 3: DM Configuration Commands (Priority: P2)
**As a** bot owner  
**I want** to use configuration commands in DMs  
**So that** I can adjust settings privately without exposing configuration in public channels

**Acceptance Criteria:**
- [ ] `/reminder reload` works in DMs (owner only)
- [ ] `/reminder timeout` functions in DM context (owner only)
- [ ] `/dog timezone` allows timezone changes via DM (owner only)
- [ ] `/dog set-time` enables time configuration in DMs (owner only)
- [ ] Configuration changes persist correctly when made via DM
- [ ] Clear feedback provided for successful/failed configuration changes

**Definition of Done:**
- All configuration commands functional in DMs
- Owner-only restriction enforced in DM context
- Configuration persistence works identically to guild commands

---

### User Story 4: Enhanced DM User Experience (Priority: P2)
**As a** user trying to use DMs  
**I want** helpful guidance and clear error messages  
**So that** I understand DM capabilities and limitations

**Acceptance Criteria:**
- [ ] `/reminder help` provides DM-specific guidance
- [ ] `/dog help` includes DM usage instructions
- [ ] Non-owner users receive helpful messages explaining DM limitations
- [ ] Error messages clearly indicate DM context when relevant
- [ ] DM commands include hints about available functionality
- [ ] Welcome message when first DMing the bot with slash commands

**Definition of Done:**
- Help system updated for DM context
- Clear user feedback for all DM interactions
- Onboarding experience for new DM users

---

## Technical Requirements

### Functional Requirements
1. **Command Registration**: Global slash command registration for DM support
2. **Permission System**: Adapt existing owner checks for DM context
3. **Autocomplete**: All autocomplete functions must work without guild context
4. **Error Handling**: DM-specific error messages and graceful fallbacks
5. **Backward Compatibility**: Guild functionality must remain unchanged

### Non-Functional Requirements
1. **Performance**: DM command responses under 3 seconds
2. **Security**: Owner-only restrictions enforced in DMs
3. **Reliability**: No regression in existing guild functionality
4. **Usability**: Clear guidance for DM users

### Integration Requirements
1. **Discord API**: Proper global command registration and sync
2. **Configuration**: Existing config system must work in DM context
3. **Logging**: Comprehensive logging for DM command usage
4. **Documentation**: Updated README.md with DM usage instructions

## Dependencies

### Prerequisites
- ✅ Existing slash command implementation (002-slash-commands complete)
- ✅ Working autocomplete system
- ✅ Permission system with owner checks
- ✅ Command groups (ReminderGroup, DogGroup)

### External Dependencies
- Discord.py 2.6.4+ with DM slash command support
- Python 3.13 async/await compatibility
- Existing configuration system

## Constraints

### Technical Constraints
- Discord global command limit (100 global slash commands)
- Discord interaction response timeout (3 seconds)
- Missing guild context in DM autocomplete functions

### Business Constraints
- DM access limited to bot owner for security
- Must maintain backward compatibility with guild commands
- No breaking changes to existing functionality

### User Experience Constraints
- DM users may not understand command availability
- Autocomplete may have reduced performance in DMs
- Configuration changes in DMs should be clearly communicated

## Success Metrics

### Functional Metrics
- [ ] 100% of existing slash commands work in DMs
- [ ] 0% regression in guild command functionality
- [ ] <3 second response time for all DM interactions
- [ ] 100% autocomplete accuracy in DM context

### Quality Metrics
- [ ] Clear error messages for 100% of failure scenarios
- [ ] Help documentation covers DM usage
- [ ] Comprehensive logging for all DM interactions
- [ ] Zero security vulnerabilities introduced

## Implementation Notes

### Command Registration Strategy
```python
# Hybrid approach: Guild + Global commands
# Guild commands: Server-specific features
# Global commands: Core DM-compatible features
await bot.tree.sync()  # Sync guild commands
await bot.tree.sync(guild=None)  # Sync global commands for DMs
```

### DM Context Detection
```python
# Check if interaction is in DM
if interaction.guild is None:
    # DM-specific handling
    pass
```

### Permission Adaptation
```python
# Adapt owner checks for DM context
if interaction.guild is None:
    # DM context - check owner directly
    is_owner = interaction.user.id == bot.owner_id
else:
    # Guild context - existing logic
    is_owner = interaction.user.id == interaction.client.owner_id
```

## Future Enhancements

### Post-MVP Features
- DM-specific reminder storage (separate from guild reminders)
- Multi-user DM support with trusted user system
- DM notification preferences and settings
- Simplified DM interface for non-technical users

### Integration Opportunities
- Calendar integration for personal reminders in DMs
- Cross-platform reminder sync (Discord DM + external systems)
- Personal reminder analytics and insights