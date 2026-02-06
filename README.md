# João Almeida Results Tracker Bot 🚴🇵🇹

A **100% free**, serverless Telegram bot that tracks **João Almeida's** race results automatically. It scrapes [ProCyclingStats](https://www.procyclingstats.com/) and sends notifications for final positions in both stage races (GC) and one-day races.

## 🚀 Features

- **Automated Tracking:** Runs every 2 hours via GitHub Actions.
- **Smart Classification:** Distinguishes between Stage Races (GC result) and One-Day Races.
- **Duplicate Prevention:** Uses a state file (`storage.json`) to ensure you only get one notification per race.
- **Zero Cost:** Uses free GitHub Actions runners and the Telegram Bot API.

## 🛠️ Architecture

1. **GitHub Actions** triggers the script on a schedule (CRON).
2. **Scraper** fetches João Almeida's race history from ProCyclingStats.
3. **Logic** checks if a race has finished (GC table exists or final results posted).
4. **Notifier** sends a formatted message to your Telegram chat.
5. **State** is committed back to the repository to prevent re-notification.

## 📋 Prerequisites

- Python 3.11+
- A Telegram Bot Token (from @BotFather)
- A Telegram Chat ID (user or group ID)

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/JoaoAlmeidaTracker.git
cd JoaoAlmeidaTracker
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
To run the bot, you must set the following environment variables:

- `TELEGRAM_BOT_TOKEN`: Your bot token.
- `TELEGRAM_CHAT_ID`: The chat ID to receive messages.

## 🏃‍♂️ Usage

### Running Locally
To test the bot manually:

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN="your_token"
$env:TELEGRAM_CHAT_ID="your_chat_id"
python bot.py
```

### Running on GitHub Actions
1. Push the code to a GitHub repository.
2. Go to **Settings** > **Secrets and variables** > **Actions**.
3. Add the following **Repository secrets**:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. The bot will run automatically every 2 hours. You can also trigger it manually under the **Actions** tab.

## 📂 Project Structure

- `bot.py`: Main entry point. Orchestrates scraping and notifications.
- `scraper.py`: Handles HTML parsing from ProCyclingStats.
- `notifier.py`: Sends HTTP requests to Telegram API.
- `storage.json`: JSON database storing notified races.
- `.github/workflows/scheduler.yml`: CRON job configuration.