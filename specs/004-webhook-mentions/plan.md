# Implementation Plan: Webhook Mention Notifications

## Feature Overview

**Feature**: Restore webhook functionality for bot mention notifications
**Priority**: P1 (Critical - Lost functionality during DM implementation)
**Status**: Ready for Implementation

This feature restores the webhook notification system that sends POST requests to a configured n8n endpoint when the bot is mentioned in guilds or DMs.

## Current State Analysis

### Existing Implementation
- ✅ Discord bot with message event handling (main.py)
- ✅ HTTP client capability (aiohttp in modules/how_is.py)
- ✅ Environment configuration (WEBHOOK_URL in .env)
- ✅ Message processing pipeline (on_message event)
- ✅ DM support infrastructure (from 003-dm-support)

### Missing Functionality
- ❌ Bot mention detection logic
- ❌ Webhook POST request implementation
- ❌ Mention-specific data payload construction
- ❌ Error handling for webhook failures
- ❌ Integration with existing message processing

## Technical Stack

### Core Technologies
- **Discord.py 2.6.4**: Bot framework with message events
- **Python 3.13**: Runtime environment with async/await
- **aiohttp**: HTTP client for webhook POST requests (already available)

### Key Components
- `main.py`: Message event handler integration
- `modules/webhook_handler.py`: New webhook functionality module
- `.env`: Configuration (WEBHOOK_URL already present)

## Architecture

### Mention Detection Strategy
```python
# In on_message handler
async def on_message(message):
    # Existing functionality preserved
    
    # Add mention detection
    if bot.user.mentioned_in(message):
        await webhook_handler.send_mention_notification(message)
    
    # Continue with existing processing
```

### Webhook Module Design
```python
# modules/webhook_handler.py
class WebhookHandler:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    async def send_mention_notification(self, message):
        payload = self.build_payload(message)
        await self.send_webhook(payload)
    
    def build_payload(self, message):
        # Construct JSON payload with user, message, context
        
    async def send_webhook(self, payload):
        # HTTP POST with aiohttp, error handling
```

### Data Flow
1. **Message Received** → on_message event fired
2. **Mention Check** → bot.user.mentioned_in(message)  
3. **Payload Construction** → Extract user, message, context data
4. **Webhook Send** → HTTP POST to n8n endpoint
5. **Error Handling** → Log failures, continue bot operation
6. **Continue Processing** → Normal message processing pipeline

## Implementation Strategy

### Phase 1: Core Infrastructure
- Create webhook handler module
- Implement basic mention detection
- Set up HTTP POST functionality

### Phase 2: Guild Integration
- Integrate mention detection in on_message handler
- Implement guild-specific payload construction
- Add comprehensive error handling

### Phase 3: DM Integration  
- Extend mention detection for DM context
- Implement DM-specific payload construction
- Ensure integration with existing DM permissions

### Phase 4: Enhancement & Testing
- Add comprehensive logging and monitoring
- Implement payload validation and testing
- Performance optimization and error recovery

## File Structure

```
/home/vitruvia/workspace/BeanBot/
├── main.py                          # Updated on_message handler
├── modules/
│   ├── webhook_handler.py           # New webhook functionality
│   ├── reminder_system.py           # Unchanged
│   └── how_is.py                   # Reference for aiohttp pattern
├── .env                            # WEBHOOK_URL configuration (existing)
└── test_webhook_mentions.py        # New testing script
```

## Key Design Decisions

### Mention Detection Approach
**Decision**: Use Discord.py built-in `bot.user.mentioned_in(message)`
- Reliable mention detection across all message types
- Handles @bot mentions and replies
- Works in both guilds and DMs

### HTTP Implementation
**Decision**: Follow existing aiohttp pattern from how_is.py
- Consistent with existing codebase architecture
- Async/await compatibility with Discord.py
- Proven error handling pattern

### Data Privacy in DMs
**Decision**: DM webhooks contain minimal context
- No guild information for privacy
- User roles omitted in DM context
- Channel type clearly marked as "dm"

### Error Handling Strategy
**Decision**: Graceful degradation on webhook failures
- Webhook failures never crash the bot
- Comprehensive logging for debugging
- Continue normal message processing

## Dependencies

### Internal Dependencies
- Existing message processing pipeline (main.py)
- DM support infrastructure (003-dm-support)
- Environment configuration (.env)

### External Dependencies
- aiohttp (already installed for how_is.py)
- Discord.py 2.6.4 (existing)
- n8n webhook endpoint (external service)

## Risk Assessment

### Low Risk
- ✅ Additive feature (no breaking changes to existing functionality)
- ✅ aiohttp already proven in codebase
- ✅ Discord.py mention detection is reliable

### Medium Risk
- ⚠️ Webhook endpoint availability dependency
- ⚠️ Performance impact of additional HTTP requests
- ⚠️ Error handling complexity for network failures

### Mitigation Strategies
- Implement circuit breaker pattern for webhook failures
- Add request timeout and retry logic
- Monitor webhook response times and success rates

## Success Criteria

### Functional Requirements
- [ ] Bot mentions in guilds trigger webhook notifications
- [ ] Bot mentions in DMs trigger webhook notifications
- [ ] Webhook payload structure matches specification
- [ ] Error handling prevents bot disruption

### Quality Requirements
- [ ] No performance regression in message processing
- [ ] Webhook requests complete within 5 seconds
- [ ] 99.9% reliability for webhook delivery attempts

### Integration Requirements
- [ ] Compatible with existing DM support (003-dm-support)
- [ ] No interference with reminder system functionality
- [ ] Seamless integration with n8n workflow processing

## Rollout Plan

### MVP (Minimum Viable Product)
- Basic mention detection in guilds and DMs
- Core webhook payload with essential data
- Basic error handling and logging

### Full Feature
- Complete payload structure with all specified fields
- Advanced error handling and retry logic
- Performance monitoring and optimization

### Future Enhancements
- Webhook payload customization options
- Multiple webhook endpoint support
- Enhanced mention context (message threads, etc.)