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

**Available Commands** (owner only):
- `!testreminder <name> [schedule]` - Test a reminder immediately
- `!reminderstatus` - View all configured and pending reminders
- `!listreminders` - List all configured reminders with schedules
- `!reloadreminders` - Reload configuration after editing `reminder_config.py`
- `!dogtimezone [timezone]` - View or set timezone (e.g., "America/New_York")
- `!settimeout <minutes>` - Set timeout duration for reminders

**Backward Compatible Commands:**
- `!dogstatus` - View dog reminder status
- `!testreminderdog [morning|noon|evening]` - Test dog reminder
- `!setdogreminder [user_id]` - View/set dog reminder recipient
- `!setdogowner [user_id]` - View/set escalation user

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
!reloadreminders
```

Test your new reminder:
```
!testreminder medication morning_dose
```

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