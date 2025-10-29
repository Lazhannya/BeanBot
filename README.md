# 🌱 BeanBot

A silly personal Discord bot for messing around with coding and having fun with friends!

## 🌟 Overview

BeanBot is a personal-use Discord bot created for fun and learning purposes. This is a playground for experimenting with Discord.py, trying out new ideas, and generally adding some entertainment to your Discord server!

## 🤖 Features

Current features (always growing!):
- **Reminder System**: Configurable scheduled reminders with acknowledgment, denial, and timeout escalation
- Tells people what they are
- Tells dad jokes when unwanted phrases are said

### 📋 Reminder System

The reminder system sends scheduled notifications to specific users and tracks responses:

**Key Features:**
- ✅ Scheduled reminders at specific times (e.g., 8:00 AM, 1:00 PM, 8:00 PM)
- ✅ Interactive buttons: Acknowledge or Deny
- ✅ Automatic escalation if no response within timeout period
- ✅ Escalation notifications on denial
- ✅ Easy configuration via Python file (no code changes needed)
- ✅ Multiple independent reminders supported
- ✅ Dynamic reload without bot restart

**🚀 Slash Commands** (Modern Interface - Recommended):

**General Reminder Commands:**
- `/reminder test` - Test a reminder delivery with autocomplete
- `/reminder status` - Check reminder system status
- `/reminder list` - List all configured reminders
- `/reminder reload` - Reload reminder configuration (owner only)
- `/reminder timeout` - Set timeout for a reminder (owner only)
- `/reminder help` - Show help for reminder commands

**Dog-Specific Commands:**
- `/dog test` - Test dog reminder at specific time with autocomplete
- `/dog status` - Check dog reminder status
- `/dog timezone` - View or set timezone with autocomplete suggestions
- `/dog set-reminder` - Set dog reminder user (owner only)
- `/dog set-owner` - Set dog owner/escalation user (owner only)
- `/dog set-time` - Set reminder times for morning/noon/evening (owner only)
- `/dog help` - Show help for dog commands

**🎯 Autocomplete Features:**
- **Reminder Names**: Type to see all available reminders
- **Schedule Labels**: See schedule options for selected reminder
- **Timezones**: Common timezone suggestions (America/New_York, Europe/London, etc.)
- **Dog Schedule Types**: Morning, noon, evening options
- **User Selection**: Pick users from server member list

**📱 Migration Guide (Legacy → Slash Commands):**
- `!testreminder` → `/reminder test`
- `!reminderstatus` → `/reminder status`
- `!listreminders` → `/reminder list`
- `!reloadreminders` → `/reminder reload`
- `!settimeout` → `/reminder timeout`
- `!dogstatus` → `/dog status`
- `!testreminderdog` → `/dog test`
- `!dogtimezone` → `/dog timezone`
- `!setdogreminder` → `/dog set-reminder`
- `!setdogowner` → `/dog set-owner`
- `!setremindertime` → `/dog set-time`

**Legacy Commands** (Still supported for backward compatibility):
All `!` commands continue to work but slash commands provide better UX with autocomplete

**💡 Using Slash Commands:**

Slash commands provide a modern Discord interface with autocomplete:

1. **Start typing**: Type `/reminder` or `/dog` and Discord shows available commands
2. **Autocomplete magic**: Start typing parameters and see suggestions:
   - Reminder names are filtered as you type
   - Schedules update based on selected reminder
   - Timezone suggestions appear for common zones
3. **Guided input**: Discord shows required/optional parameters
4. **Ephemeral help**: Help commands are private (only you see them)

**Example Usage:**
```
/reminder test <tab>  # Shows all reminder names
/reminder test dog_walking <tab>  # Shows morning, noon, evening
/dog timezone <tab>  # Shows America/New_York, Europe/London, etc.
```

**How It Works:**
1. Bot sends reminder at scheduled time with Yes/No buttons
2. User clicks "Yes" → Reminder completed (no further action)
3. User clicks "No" → Escalation user immediately notified
4. No response within timeout → Escalation user notified after timeout expires

**Adding New Reminders:**

Edit `reminder_config.py` and add a new reminder dict to the `REMINDERS` list:

```python
REMINDERS.append({
    "name": "medication",  # Unique identifier
    "schedules": [
        {"hour": 9, "minute": 0, "label": "morning_dose"},
        {"hour": 21, "minute": 0, "label": "evening_dose"}
    ],
    "target_user_id": 123456789,  # Discord user ID to receive reminders
    "escalation_user_id": 987654321,  # Discord user ID for alerts
    "timeout_minutes": 30,  # Time before escalation if no response
    "messages": {
        "morning_dose": "🏥 Time for morning medication!",
        "evening_dose": "🏥 Time for evening medication!"
    },
    "timeout_message": "⚠️ MEDICATION ALERT: {label} was not taken!",
    "denial_message": "⚠️ {label} medication was declined!"
})
```

Then reload the bot configuration:
```
/reminder reload
```

Test your new reminder (with autocomplete):
```
/reminder test
```
Select "medication" from the autocomplete list, then "morning_dose" from the schedule list.

**Bot Restart Behavior:**
- Pending reminders are cleared on restart (in-memory only)
- Button interactions stop working after restart (Discord limitation)
- Reminders will resume at next scheduled time
- No data is persisted (lightweight, stateless design)

**Configuration Structure:**

See `reminder_config.py` for detailed configuration documentation. Each reminder supports:
- Multiple schedules with custom labels
- Custom messages per schedule
- Configurable timeout periods
- Separate target and escalation users
- Timezone support (global setting)

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- Discord Bot Token from [Discord Developer Portal](https://discord.com/developers/applications)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/lazhannya/BeanBot.git
   cd BeanBot
   ```

2. Set up a virtual environment in the project directory:
   ```bash
   python -m venv .
   source bin/activate  # On Windows: .\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install discord.py python-dotenv
   ```

4. Create a `.env` file in the project root:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

5. Run the bot:
   ```bash
   python main.py
   ```

## 🎮 Usage

Current commands and interactions:
- Ask "What am I?" for a personalized (silly) response
- More features coming as experimentation continues!

## 🧪 Development

BeanBot is designed to be a sandbox for learning and experimenting with Discord.py. Feel free to:

- Add new commands
- Implement new Discord API features
- Try out different bot behaviors
- Test random ideas

No strict roadmap - just fun and learning!

## 📝 License

This project is open for personal learning and entertainment purposes. Have fun with it!

## 🐾 About

Created by [Lazhannya](https://github.com/lazhannya) for personal amusement and coding practice. This is a playground project for experimenting with Discord bot development.

> "Beep boop, I'm still learning!" - BeanBot