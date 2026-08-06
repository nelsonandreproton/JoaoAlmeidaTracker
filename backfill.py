import json
from scraper import get_race_result
from notifier import send_telegram_notification
from bot import format_message, load_state, save_state

RACE_IDS = [
    "tour-de-pologne/2026/stage-1",
    "tour-de-pologne/2026/stage-2",
    "tour-de-pologne/2026/stage-3",
]

def main():
    state = load_state()
    state_changed = False

    for race_id in RACE_IDS:
        if state.get(race_id, {}).get('notified', False):
            print(f"Skipping {race_id} (already notified)")
            continue

        race_url = f"https://www.procyclingstats.com/race/{race_id}"
        print(f"Fetching result for {race_id}...")
        result = get_race_result(race_url)

        if result:
            message = format_message(result)
            print(message)
            send_telegram_notification(message)
            state[race_id] = {"notified": True, "type": result['type']}
            state_changed = True
        else:
            print(f"No result found for {race_id}")

    if state_changed:
        save_state(state)
        print("storage.json updated")

if __name__ == "__main__":
    main()
