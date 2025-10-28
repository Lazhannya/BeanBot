"""
Reminder Configuration for BeanBot

This file defines all reminders that the bot will send. Each reminder can have:
- Multiple schedules (different times of day)
- A target user who receives the reminder
- An escalation user who receives notifications if reminder is denied or times out
- Customizable timeout duration
- Custom messages for each schedule
- Custom timeout/denial messages

To add a new reminder:
1. Add a new dict to the REMINDERS list
2. Run !reloadreminders command in Discord (or restart bot)
3. Test with !testreminder <reminder_name> <schedule_label>

Example reminder structure:
{
    "name": "unique_identifier",          # Used in commands and logs
    "schedules": [                         # List of times to send reminder
        {"hour": 9, "minute": 0, "label": "morning"},
        {"hour": 21, "minute": 0, "label": "evening"}
    ],
    "target_user_id": 123456789,          # Discord user ID who receives reminder
    "escalation_user_id": 987654321,      # Discord user ID who receives alerts
    "timeout_minutes": 60,                 # Minutes before escalation if no response
    "messages": {                          # Message text for each schedule label
        "morning": "Morning reminder text!",
        "evening": "Evening reminder text!"
    },
    "timeout_message": "⚠️ Alert: {label} reminder timed out!",  # {label} is replaced
    "denial_message": "⚠️ Alert: {label} reminder was denied!"   # Optional, defaults to generic message
}
"""

# Global timezone for all reminders (uses pytz timezone names)
TIMEZONE = "Europe/Paris"

# List of all reminders
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
        "timeout_message": "⚠️ OVERDUE ALERT: The dog is overdue for the {label} walk and feeding! No response received within {timeout} minutes.",
        "denial_message": "⚠️ Alert: The dog hasn't been taken care of for the {label} session!"
    },
    # Example second reminder (can be activated by changing user IDs to real ones)
    # {
    #     "name": "medication",
    #     "schedules": [
    #         {"hour": 9, "minute": 0, "label": "morning_dose"},
    #         {"hour": 21, "minute": 0, "label": "evening_dose"}
    #     ],
    #     "target_user_id": 123456789,  # Replace with actual Discord user ID
    #     "escalation_user_id": 987654321,  # Replace with actual Discord user ID
    #     "timeout_minutes": 30,
    #     "messages": {
    #         "morning_dose": "🏥 Good morning! Time to take your morning medication.",
    #         "evening_dose": "🏥 Good evening! Time to take your evening medication."
    #     },
    #     "timeout_message": "⚠️ MEDICATION ALERT: {label} medication was not taken! No response received within {timeout} minutes.",
    #     "denial_message": "⚠️ MEDICATION ALERT: {label} medication was explicitly declined!"
    # }
]
