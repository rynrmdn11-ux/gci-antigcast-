# GCI AntiGcast Bot (Deploy-ready)

Project: **gci-antigcast**

This repository contains a ready-to-deploy Telegram Anti-Gcast bot (Mode A: Kill Everything).
It deletes detected broadcast/spam messages and bans the sender immediately.

## Included files
- `main.py` — bot implementation using python-telegram-bot (async)
- `requirements.txt` — Python dependencies
- `Procfile` — for Railway deployment
- `.env.example` — example environment variables

## Features (Mode A)
- Delete forwarded messages and ban sender
- Delete messages containing STOPWORDS and ban sender
- Delete messages with too many links and ban sender
- Basic checks for suspicious new members (auto-ban bots / suspicious usernames)

## Deploy on Railway (recommended)
1. Create an account at https://railway.app and log in.
2. Create a new project → Deploy from GitHub (or use "Deploy from repo" and upload this project).
3. In Railway, set the Environment Variable:
   - `TELEGRAM_TOKEN` = your bot token (get it from @BotFather)
4. Set the Railway service's Region to **Singapore** for best latency in Indonesia.
5. Start the project. Railway will run `worker: python main.py` from Procfile.
6. Add your bot to the Telegram group and make it **Admin** with permissions:
   - Delete messages
   - Ban users
   - Read messages

## Running locally
1. Copy `.env.example` to `.env` and fill TELEGRAM_TOKEN
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run:
   ```
   python main.py
   ```

## Important Security Notes
- **Never share your TELEGRAM_TOKEN** publicly. If you ever do, immediately revoke it via @BotFather and create a new one.
- This bot operates in "kill everything" mode — it will ban users automatically. Consider testing in a small private group first.
- Telegram Bot API does not reliably expose user account creation date; some heuristics are included but may not be perfect.

## Customization
- Edit `STOPWORDS` and `MAX_LINKS` via environment variables.
- If you want a warning-first mode, modify `handle_message` to send warning messages instead of immediate bans.

