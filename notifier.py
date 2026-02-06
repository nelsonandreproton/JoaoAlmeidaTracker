import os
import requests

def send_telegram_notification(message):
    """Sends a message to a Telegram chat."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars must be set.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message}

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print(f"Notification sent successfully to chat ID {chat_id}.")
    except requests.RequestException as e:
        print(f"Error sending Telegram notification: {e}")
        print(f"Response: {getattr(e.response, 'text', 'No response text')}")