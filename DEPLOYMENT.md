# BeanBot Server Deployment Guide

This guide explains how to deploy BeanBot on a remote server.

## Prerequisites

- A server with Python 3.12+ installed
- Access to Discord Developer Portal to obtain bot token

## Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/lazhannya/BeanBot.git
   cd BeanBot
   ```

2. **Set up a virtual environment** (optional but recommended)
   ```bash
   python3 -m venv .
   source bin/activate  # On Windows: .\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file with your Discord bot token:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

## Running the Bot

### Manual Execution

To start the bot manually:
```bash
python main.py
```

### Running as a Background Service

To keep the bot running after you log out:

#### Using tmux (recommended)
```bash
# Install tmux if not already installed
sudo apt-get install tmux  # For Debian/Ubuntu

# Create a new tmux session
tmux new -s beanbot

# Inside the tmux session, activate the environment and run the bot
source bin/activate
python main.py

# Detach from the session with Ctrl+B followed by D
```

To reattach to the session later:
```bash
tmux attach -t beanbot
```

#### Using systemd (for more permanent setup)
Create a systemd service file:

```bash
sudo nano /etc/systemd/system/beanbot.service
```

Add the following content (adjust paths as needed):
```ini
[Unit]
Description=BeanBot Discord Bot
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/BeanBot
ExecStart=/path/to/BeanBot/bin/python main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable beanbot
sudo systemctl start beanbot
```

Check status:
```bash
sudo systemctl status beanbot
```

## Monitoring and Maintenance

- View logs with `tail -f discord.log`
- To update the bot: stop the service, pull latest code, and restart

## Troubleshooting

1. **Bot doesn't start**
   - Check that your token is valid and properly set in the `.env` file
   - Verify Python version (`python --version`) is 3.12 or higher
   - Check discord.log for errors

2. **Bot starts but doesn't respond**
   - Ensure bot has proper permissions in Discord
   - Verify intents are enabled in Discord Developer Portal

3. **Permissions issues**
   - Ensure file permissions are correct: `chmod +x main.py`