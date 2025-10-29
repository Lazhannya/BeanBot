# Feature Specification: Webhook Mention Notifications

## Overview

**Feature**: Restore webhook functionality to send POST requests when bot is mentioned
**Priority**: P1 (Critical - Lost functionality)
**Status**: Implementation Required

Restore the webhook notification system that was lost during DM support implementation. The bot should send HTTP POST requests to the configured n8n webhook endpoint whenever it is mentioned in guilds or DMs.

## User Stories

### User Story 1: Guild Mention Webhooks (Priority: P1) 🎯
**As a** system administrator  
**I want** the bot to send webhook notifications when mentioned in guild channels  
**So that** I can process mentions through n8n automation workflows  

**Acceptance Criteria:**
- Bot detects when it is mentioned in any guild channel
- Sends POST request to configured webhook URL with message data
- Includes user information, message content, and channel context
- Works for all message types (regular messages, replies, threads)
- Handles errors gracefully without affecting bot functionality

**Independent Test:** Mention bot in guild channel, verify webhook receives POST with correct data structure

### User Story 2: DM Mention Webhooks (Priority: P1) 🎯  
**As a** system administrator  
**I want** the bot to send webhook notifications when mentioned in DMs  
**So that** I can process DM mentions through the same n8n automation workflows  

**Acceptance Criteria:**
- Bot detects when it is mentioned in direct message channels
- Sends POST request to webhook URL with DM-specific context
- Includes user information and message content (no guild data for DMs)
- Maintains privacy and security for DM interactions
- Integrates with existing DM permission system

**Independent Test:** Mention bot in DM, verify webhook receives POST with DM-specific data structure

### User Story 3: Enhanced Webhook Data (Priority: P2)
**As a** n8n workflow developer  
**I want** rich webhook data with comprehensive context  
**So that** I can create sophisticated mention processing workflows  

**Acceptance Criteria:**
- Webhook payload includes timestamp and bot metadata
- Guild context includes server name and channel details
- User context includes display name and roles (for guilds)
- Message context includes any attachments or embeds
- Structured JSON format for easy parsing

**Independent Test:** Verify webhook payload contains all specified fields with correct data types

## Technical Requirements

### Webhook Payload Structure
```json
{
    "user": {
        "id": "string",
        "username": "string", 
        "display_name": "string",
        "roles": ["string"] // guild only
    },
    "message": {
        "content": "string",
        "id": "string",
        "timestamp": "ISO8601",
        "attachments": ["url"],
        "embeds": [{}]
    },
    "context": {
        "type": "guild|dm",
        "guild": {
            "id": "string",
            "name": "string"  
        }, // null for DMs
        "channel": {
            "id": "string",
            "name": "string",
            "type": "string"
        }
    },
    "bot": {
        "id": "string",
        "mention_detected": "boolean"
    }
}
```

### Integration Points
- **Environment**: WEBHOOK_URL from .env file
- **Event**: on_message handler in main.py
- **Mention Detection**: Discord bot user mention parsing
- **HTTP Client**: aiohttp (already available in project)
- **Error Handling**: Graceful failure without disrupting bot functionality

### Security & Privacy
- DM webhooks contain no guild information
- User roles only included for guild messages
- Webhook URL should be configurable and secure
- No sensitive bot token information in webhooks
- Rate limiting consideration for webhook requests

## Constraints

- Must not interfere with existing DM support functionality
- Must not impact reminder system performance
- Should handle webhook endpoint being temporarily unavailable
- Must work with existing message processing pipeline
- Should be easily testable and debuggable

## Success Criteria

- [ ] Bot mentions in guilds trigger webhook POST requests
- [ ] Bot mentions in DMs trigger webhook POST requests  
- [ ] Webhook payload follows specified JSON structure
- [ ] Error handling prevents bot crashes on webhook failures
- [ ] Performance impact is minimal (< 100ms additional latency)
- [ ] Integration testing confirms n8n workflow compatibility