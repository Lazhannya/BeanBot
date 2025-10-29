# Implementation Plan: Discord Slash Commands with Autocomplete

**Branch**: `002-slash-commands` | **Date**: 2025-10-29 | **Spec**: [spec.md](./spec.md)
**Input**: User request to convert `!` prefix commands to `/` slash commands with autocomplete functionality

## Summary

Convert the existing BeanBot reminder system from legacy Discord text commands (`!testreminder`, `!reminderstatus`, etc.) to modern Discord slash commands (`/reminder test`, `/reminder status`, etc.) while adding intelligent autocomplete functionality for reminder names, schedule labels, and other parameters. The implementation will preserve all existing functionality while providing a significantly improved user experience through Discord's native slash command interface, parameter validation, and contextual autocomplete suggestions.

## Technical Context

**Language/Version**: Python 3.13+ (current environment)  
**Primary Dependencies**: discord.py 2.6.4 (already installed), existing reminder system  
**Storage**: Existing in-memory with file-based configuration (no changes needed)  
**Testing**: Manual testing via Discord slash command interface  
**Target Platform**: Linux server (continuous operation)  
**Project Type**: Single project - Discord bot feature enhancement  
**Performance Goals**: 
- Slash command registration within 5 seconds of bot startup
- Autocomplete response within 1 second
- All slash commands respond within Discord's 3-second interaction limit
- Zero impact on existing reminder functionality

**Constraints**: 
- Must maintain backward compatibility with existing `!` commands during transition
- Discord slash command limits (25 autocomplete options, 3-second response time)
- Discord API rate limits for command registration
- Existing module structure must be preserved

**Scale/Scope**: 
- Personal use bot (small scale)
- 10-15 slash commands total
- 2-5 command groups (`/reminder`, `/dog`)
- Single Discord server or small number of servers

## Constitution Check

*GATE: Must pass before implementation.*

- [x] **Module-First Architecture**: Enhancement implemented within existing `reminder_system.py` module?
  - ✅ Will enhance existing `modules/reminder_system.py` without breaking module structure
  - ✅ Maintains `setup(bot)` pattern for initialization
  - ✅ Module remains self-contained in `modules/` directory

- [x] **Simplicity**: Functions under 50 lines? Clear single responsibility? Self-documenting names?
  - ✅ Slash command functions will follow same 20-50 line pattern as existing commands
  - ✅ Clear function naming: `test_reminder_slash()`, `reminder_name_autocomplete()`
  - ✅ Autocomplete logic will be simple filtering of existing config data

- [x] **Error Handling**: All async operations wrapped in try-except? Proper logging configured?
  - ✅ Existing module has comprehensive error handling pattern
  - ✅ Module-level logger already configured and will be used for slash commands
  - ✅ All Discord API calls will follow existing try-except pattern

- [x] **Expandability**: No unnecessary dependencies on other feature modules?
  - ✅ Enhancement is self-contained within reminder system module
  - ✅ Uses existing configuration structure without modifications
  - ✅ No new dependencies on other modules

- [x] **Observability**: Module-level logger used? Key operations logged at appropriate levels?
  - ✅ Existing logger will be extended for slash command events
  - ✅ Will log: command invocations, autocomplete usage, registration events
  - ✅ Maintains existing file-based logging pattern

- [x] **Documentation**: Module docstring present? README updated? `.env` requirements documented?
  - ⚠️ Need to update README.md with slash command documentation
  - ⚠️ Need to document migration path from `!` to `/` commands
  - ✅ `.env` requirements unchanged (DISCORD_TOKEN only)

---

## Phase 0: Research & Technical Analysis

### Discord.py Slash Command Implementation

**Key Technical Requirements**:

1. **Command Tree Registration**:
```python
@bot.tree.command(name="test", description="Test a reminder")
@app_commands.describe(reminder="Name of the reminder to test")
async def test_reminder(interaction: discord.Interaction, reminder: str):
    pass
```

2. **Autocomplete Implementation**:
```python
@test_reminder.autocomplete('reminder')
async def reminder_autocomplete(interaction: discord.Interaction, current: str):
    return [app_commands.Choice(name=r['name'], value=r['name']) for r in reminders][:25]
```

3. **Command Groups**:
```python
class ReminderGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="reminder", description="Reminder management commands")
```

### Integration Strategy

**Backward Compatibility Approach**:
- Keep existing `@bot.command()` decorators during transition
- Add new `@bot.tree.command()` decorators alongside
- Both command types will call the same underlying functions
- Gradual migration path for users

**Autocomplete Data Sources**:
- Reminder names: `reminder_config.REMINDERS` list
- Schedule labels: Dynamic based on selected reminder
- Timezones: Static list of common timezones
- Users: Discord server member list (for admin commands)

---

## Phase 1: Interface Design

### Slash Command Structure

**Command Groups**:

1. **`/reminder` Group** (Primary commands):
   - `/reminder test <reminder> [schedule]` - Test reminder delivery
   - `/reminder status` - Show system status
   - `/reminder list` - List all configured reminders
   - `/reminder reload` - Reload configuration (admin only)
   - `/reminder timeout <reminder> <minutes>` - Set timeout (admin only)

2. **`/dog` Group** (Legacy compatibility):
   - `/dog test [time]` - Test dog reminder
   - `/dog status` - Dog reminder status
   - `/dog timezone [zone]` - View/set timezone
   - `/dog set-reminder <user>` - Set dog reminder user (admin only)
   - `/dog set-owner <user>` - Set dog owner (admin only)
   - `/dog set-time <type> <hour> [minute]` - Set reminder time (admin only)

### Autocomplete Specifications

**Reminder Name Autocomplete**:
```python
async def reminder_name_autocomplete(interaction: discord.Interaction, current: str):
    reminders = reminder_config.REMINDERS
    choices = [
        app_commands.Choice(name=r['name'], value=r['name'])
        for r in reminders
        if current.lower() in r['name'].lower()
    ]
    return choices[:25]  # Discord limit
```

**Schedule Label Autocomplete** (Contextual):
```python
async def schedule_label_autocomplete(interaction: discord.Interaction, current: str):
    # Get reminder name from current interaction
    reminder_name = get_focused_reminder_name(interaction)
    if not reminder_name:
        return []
    
    reminder = find_reminder_by_name(reminder_name)
    if not reminder:
        return []
        
    choices = [
        app_commands.Choice(name=s['label'], value=s['label'])
        for s in reminder['schedules']
        if current.lower() in s['label'].lower()
    ]
    return choices[:25]
```

### Parameter Validation

**Input Validation Patterns**:
- Reminder names: Must exist in configuration
- Schedule labels: Must exist for the specified reminder  
- Timeout values: Must be positive integers
- User parameters: Must be valid Discord users
- Timezone values: Must be valid pytz timezone strings

---

## Phase 2: Implementation Tasks

### Migration Strategy

**Phase 2A: Core Infrastructure** (Sequential - 2-3 hours)
1. Set up slash command tree in `main.py`
2. Create command groups in `reminder_system.py`
3. Implement basic autocomplete framework
4. Test command registration

**Phase 2B: Primary Commands** (Parallel - 4-5 hours)
1. Convert `/reminder` group commands
2. Implement reminder name autocomplete
3. Implement schedule label autocomplete
4. Add parameter validation

**Phase 2C: Legacy Commands** (Parallel - 3-4 hours)  
1. Convert `/dog` group commands
2. Implement timezone autocomplete
3. Add user parameter support
4. Preserve exact legacy functionality

**Phase 2D: Enhancement** (Sequential - 2-3 hours)
1. Add contextual help commands
2. Implement advanced error handling
3. Add usage analytics logging
4. Performance optimization

### File Organization

**Modified Files**:
- `main.py`: Add slash command tree setup and sync
- `modules/reminder_system.py`: Add all slash command implementations
- `README.md`: Document new slash commands
- No new files needed (enhancement of existing module)

**Code Structure**:
```
modules/reminder_system.py:
├── Existing functions (preserved)
├── Slash command groups
│   ├── ReminderGroup class
│   └── DogGroup class  
├── Slash command implementations
│   ├── test_reminder_slash()
│   ├── reminder_status_slash()
│   └── ...
├── Autocomplete functions
│   ├── reminder_name_autocomplete()
│   ├── schedule_label_autocomplete()
│   └── timezone_autocomplete()
└── Helper functions
    ├── get_focused_parameter()
    └── validate_parameters()
```

---

## Phase 3: Testing Strategy

### Manual Testing Approach

**Slash Command Testing**:
1. Use Discord's built-in slash command interface
2. Test autocomplete by typing partial matches
3. Verify parameter validation with invalid inputs
4. Compare slash command output to legacy command output
5. Test permission restrictions on admin commands

**Regression Testing**:
1. Verify all existing `!` commands still work
2. Ensure identical functionality between `!` and `/` versions
3. Test reminder delivery and button interactions remain unchanged
4. Verify configuration reload affects both command types

**Performance Testing**:
1. Measure slash command registration time on bot startup
2. Test autocomplete response times with large reminder configs
3. Verify all commands respond within Discord's 3-second limit
4. Test concurrent slash command usage

### Test Scenarios

**Basic Functionality**:
- `/reminder test dog_walking morning` → Should send test reminder
- `/reminder status` → Should show system status identical to `!reminderstatus`
- `/dog test morning` → Should send dog reminder identical to `!testreminderdog morning`

**Autocomplete Scenarios**:
- Type `/reminder test d` → Should suggest `dog_walking`  
- Select `dog_walking`, focus schedule → Should suggest `morning`, `noon`, `evening`
- Type `/dog timezone E` → Should suggest `Europe/Paris`, `Europe/London`, etc.

**Error Handling**:
- `/reminder test invalid_reminder` → Should show helpful error message
- `/reminder timeout dog_walking -5` → Should reject negative timeout
- Admin commands by non-owner → Should show permission error

---

## Phase 4: Deployment Strategy

### Rollout Plan

**Stage 1**: Development and Testing
- Implement on development branch
- Test with single Discord server
- Verify command registration and functionality

**Stage 2**: Backward Compatible Deployment  
- Deploy with both `!` and `/` commands active
- Monitor usage patterns and error rates
- Gather user feedback on slash command experience

**Stage 3**: Migration Period
- Add deprecation notices to `!` commands (optional)
- Promote slash command usage in documentation
- Continue supporting both interfaces

**Stage 4**: Full Slash Command Adoption (Future)
- Eventually remove `!` commands if desired
- Full migration to slash-only interface

### Risk Mitigation

**Command Registration Issues**:
- Implement fallback to `!` commands if slash registration fails
- Add detailed logging for registration process
- Handle Discord API rate limits gracefully

**User Experience Issues**:
- Maintain both interfaces during transition
- Provide clear migration documentation
- Monitor for user confusion or errors

**Performance Issues**:
- Implement autocomplete caching if needed
- Add timeout handling for slow responses
- Monitor Discord interaction limits

---

## Phase 5: Success Metrics

### Technical Metrics

- **Registration Success**: 100% successful slash command registration
- **Response Time**: <1s autocomplete, <3s command execution  
- **Error Rate**: <5% failed interactions
- **Coverage**: 100% feature parity with existing commands

### User Experience Metrics

- **Discoverability**: Users can find commands through Discord UI
- **Usability**: Reduced user errors through parameter validation
- **Efficiency**: Faster command completion with autocomplete
- **Adoption**: Usage shift from `!` to `/` commands over time

### Observability

**Logging Requirements**:
- All slash command invocations with parameters
- Autocomplete usage patterns and performance
- Registration success/failure events
- Error conditions with full context

**Monitoring**:
- Command usage statistics (slash vs legacy)
- Performance metrics for autocomplete response times  
- User error patterns and validation failures
- Discord API interaction success rates

---

## Notes & Considerations

### Discord API Limitations

- **Autocomplete Limit**: Maximum 25 suggestions per parameter
- **Response Time**: 3-second limit for slash command responses
- **Registration Rate**: Limited number of command updates per hour
- **Parameter Types**: Limited to Discord's supported parameter types

### Implementation Decisions

- **Backward Compatibility**: Maintain both `!` and `/` commands during transition
- **Command Organization**: Logical grouping (`/reminder`, `/dog`) for clarity
- **Autocomplete Strategy**: Dynamic filtering with configuration reload support
- **Error Handling**: Leverage Discord's built-in parameter validation plus custom validation

### Future Enhancements (Out of Scope)

- Context menu commands (right-click actions)
- Slash command permissions 2.0 (per-server configuration)  
- Interactive components in slash command responses
- Multi-language command descriptions
- Voice command integration

---

**Plan Complete**: Ready for task generation and implementation.

## Technical Requirements

### Discord.py Integration

**Required Imports**:
```python
from discord import app_commands
from discord.ext import commands
import discord
```

**Bot Setup Changes**:
```python
# In main.py
intents = discord.Intents.default()
intents.message_content = True  # Still needed for legacy commands
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
```

**Module Integration**:
```python
# In modules/reminder_system.py
def setup(bot: commands.Bot) -> ReminderSystem:
    reminder_system = ReminderSystem(bot)
    
    # Register legacy commands (existing code)
    # ... existing command registrations
    
    # Register slash commands (new)
    bot.tree.add_command(ReminderGroup(reminder_system))
    bot.tree.add_command(DogGroup(reminder_system))
    
    return reminder_system
```