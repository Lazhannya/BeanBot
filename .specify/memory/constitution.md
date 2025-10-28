<!--
Sync Impact Report:
- Version: 0.0.0 → 1.0.0 (Initial constitution establishment)
- Ratified: 2025-10-28
- Modified principles: N/A (initial creation)
- Added sections: Core Principles (5), Code Quality Standards, Development Workflow, Governance
- Removed sections: N/A
- Templates requiring updates:
  ✅ plan-template.md - Constitution Check section aligned with new principles
  ✅ spec-template.md - Requirements structure compatible with module-first approach
  ✅ tasks-template.md - Task organization supports modular development
- Follow-up TODOs: None
-->

# BeanBot Constitution

## Core Principles

### I. Module-First Architecture (NON-NEGOTIABLE)

Every new feature MUST be implemented as a separate Python module and imported into
`main.py`. The `main.py` file serves exclusively as the orchestration layer and MUST NOT
contain feature-specific logic beyond basic message routing and event handling.

**Rationale**: Maintaining `main.py` as a clean orchestration layer ensures the codebase
remains readable, testable, and maintainable as the bot grows. Feature isolation in
modules prevents the main file from becoming unwieldy and makes individual features
easier to debug, test, and remove if needed.

**Requirements**:
- Each feature module MUST have a `setup(bot)` function that returns an instance or
  configures the feature
- Feature modules MUST be self-contained with their own error handling and logging
- Module names MUST be descriptive and snake_case (e.g., `dog_reminder.py`, `how_is.py`)
- No business logic in `main.py` beyond imports, bot initialization, and basic routing

### II. Simplicity and Readability (NON-NEGOTIABLE)

Code MUST be as simple as possible while meeting requirements. Prioritize clarity over
cleverness. Every function and class MUST have a clear, single responsibility.

**Rationale**: BeanBot is a personal/learning project where understanding the code is
more valuable than premature optimization. Simple code is easier to debug, extend, and
learn from.

**Requirements**:
- Functions SHOULD be under 50 lines when possible
- Complex logic MUST be broken into smaller, well-named helper functions
- Variable and function names MUST be self-documenting
- Avoid nested callbacks; use async/await patterns consistently
- Comments MUST explain "why," not "what" (code should be self-explanatory)
- Use docstrings for all public functions and classes

### III. Robustness Through Error Handling

All bot operations MUST include comprehensive error handling. Failures in one feature
MUST NOT crash the entire bot or affect other features.

**Rationale**: A Discord bot runs continuously and interacts with external services
(Discord API, external APIs, user input). Robust error handling ensures uptime and
user experience remain stable even when individual features encounter issues.

**Requirements**:
- All async operations MUST be wrapped in try-except blocks
- Errors MUST be logged with context (module name, operation, relevant IDs)
- Failed operations SHOULD fail gracefully with user-friendly error messages when
  appropriate
- Each module MUST maintain its own logger instance
- Critical failures (bot token issues, connection errors) MAY terminate the bot with
  clear error messages

### IV. Modular Expandability

The architecture MUST support easy addition of new features without modifying existing
module internals. Feature dependencies SHOULD be minimal.

**Rationale**: BeanBot is designed as a playground for experimentation. New features
should be addable with minimal friction and without risk of breaking existing
functionality.

**Requirements**:
- New features MUST follow the Module-First Architecture pattern
- Feature modules SHOULD NOT directly import or depend on other feature modules unless
  absolutely necessary
- Shared utilities (if needed) MUST be placed in a dedicated `utils.py` module
- Configuration (tokens, IDs, settings) MUST be managed through environment variables
  or a dedicated config module
- Feature modules MUST register their commands/events through the bot instance, not
  global state

### V. Observability and Debugging

All features MUST implement logging at appropriate levels (DEBUG, INFO, WARNING, ERROR).
State changes, user interactions, and errors MUST be logged with sufficient context for
debugging.

**Rationale**: As a bot running asynchronously and reacting to external events, being
able to trace what happened when (especially errors or unexpected behavior) is critical
for maintenance and improvement.

**Requirements**:
- Each module MUST create its own logger: `logger = logging.getLogger(__name__)`
- User commands and interactions SHOULD log at INFO level
- State changes (reminder sent, database updated) MUST log at INFO level
- Detailed execution flow MAY log at DEBUG level
- Errors MUST log at ERROR level with full exception details (`exc_info=True`)
- Log files MUST be gitignored but log configuration SHOULD be documented

## Code Quality Standards

### Python Standards
- **Version**: Python 3.12+ required
- **Style**: Follow PEP 8 naming conventions; use formatters (black, autopep8)
  recommended but not enforced
- **Type hints**: Encouraged but not mandatory; use where they improve clarity
- **Async**: Use async/await consistently; avoid blocking operations in event handlers

### Discord.py Best Practices
- Always check bot permissions before attempting operations
- Use Intents appropriately (only request what's needed)
- Handle rate limiting gracefully (discord.py handles most, but be aware)
- Store sensitive data (tokens, IDs) in `.env` files, never in code
- Follow Discord API Terms of Service

### Documentation
- README.md MUST be kept up-to-date with new features and setup instructions
- Each module SHOULD have a module-level docstring explaining its purpose
- Complex features MAY have additional documentation in a `docs/` directory
- Configuration requirements MUST be documented (environment variables, setup steps)

## Development Workflow

### Adding New Features
1. Create a new Python module file (e.g., `feature_name.py`)
2. Implement the feature with proper error handling and logging
3. Add a `setup(bot)` function to initialize the feature
4. Import and initialize in `main.py`
5. Update README.md with feature description and any new dependencies
6. Test the feature in a development Discord server before deployment

### Modifying Existing Features
1. Changes MUST be made within the feature's module file
2. If changes affect other features, document the dependencies
3. Maintain backward compatibility when possible; document breaking changes
4. Test thoroughly before deployment

### Deployment
- Test all changes in a development environment first
- Use git branches for experimental features
- Keep the main branch stable and deployable
- Document deployment steps and dependencies in DEPLOYMENT.md if it exists

## Governance

This constitution defines the architectural and quality standards for BeanBot. All code
contributions and feature additions MUST comply with these principles.

### Amendment Process
- Constitution changes require clear justification and documentation
- Version increments follow semantic versioning:
  - **MAJOR**: Removal or fundamental change to a core principle
  - **MINOR**: Addition of new principles or significant expansions to existing ones
  - **PATCH**: Clarifications, wording improvements, or minor additions
- Amendments MUST update the Sync Impact Report at the top of this file

### Compliance
- Code reviews (if applicable) SHOULD verify adherence to Module-First Architecture
  and error handling requirements
- Feature complexity MUST be justified by user value, not technical interest
- When in doubt, favor simplicity and maintainability over optimization

### References
- Feature planning: Use `.specify/templates/plan-template.md`
- Feature specifications: Use `.specify/templates/spec-template.md`
- Task breakdowns: Use `.specify/templates/tasks-template.md`

**Version**: 1.0.0 | **Ratified**: 2025-10-28 | **Last Amended**: 2025-10-28
