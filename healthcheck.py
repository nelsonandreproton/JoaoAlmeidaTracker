import os
import datetime
from notifier import send_telegram_notification

LAST_RUN_FILE = "last_run.txt"
MAX_AGE_HOURS = 6

def main():
    if not os.path.exists(LAST_RUN_FILE):
        send_telegram_notification(
            f"⚠️ João Almeida Tracker: {LAST_RUN_FILE} não existe. "
            f"O bot pode não estar a correr."
        )
        return

    with open(LAST_RUN_FILE) as f:
        last_run_str = f.read().strip()

    last_run = datetime.datetime.strptime(last_run_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.UTC)
    age = datetime.datetime.now(datetime.UTC) - last_run
    age_hours = age.total_seconds() / 3600

    print(f"Last bot run: {last_run_str} ({age_hours:.1f}h ago)")

    if age_hours > MAX_AGE_HOURS:
        send_telegram_notification(
            f"⚠️ João Almeida Tracker: o bot não corre há {age_hours:.0f}h "
            f"(última execução: {last_run_str}). Verifica o GitHub Actions."
        )
    else:
        print("Bot is healthy.")

if __name__ == "__main__":
    main()
