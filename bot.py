import json
import os
from scraper import get_rider_races, get_race_result
from notifier import send_telegram_notification

RIDER_URL = "https://www.procyclingstats.com/rider/joao-almeida"
STORAGE_FILE = "storage.json"

def load_state():
    """Loads the notified races state from storage.json."""
    if not os.path.exists(STORAGE_FILE):
        return {}
    try:
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_state(state):
    """Saves the state to storage.json."""
    with open(STORAGE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def format_message(result):
    """Formats the notification message based on the race result."""
    if result['type'] == 'stage_race':
        position_label = "GC Position"
        position_value = f"{result['position']}º"
    else:  # one_day_race
        position_label = "Final Position"
        position_value = f"{result['position']}º" if result['position'].isnumeric() else result['position']

    time_gap = result['time_gap']
    if time_gap and not time_gap.startswith('+') and result['position'] != '1':
        time_gap = f"+{time_gap}"

    message = (
        f"🏁 Race finished!\n\n"
        f"🚴 João Almeida\n"
        f"📍 Race: {result['race_name']}\n"
        f"📊 {position_label}: {position_value}\n"
        f"⏱ {time_gap}\n"
        f"👕 {result['team']}"
    )
    return message

def main():
    print("Starting João Almeida results check...")
    state = load_state()
    races_to_check = get_rider_races(RIDER_URL)

    state_changed = False
    for race in races_to_check:
        race_id = race['race_id']
        
        if state.get(race_id, {}).get('notified', False):
            continue

        print(f"Checking race: {race['race_name_initial']} ({race_id})")
        result = get_race_result(race['race_url'])

        if result:
            print(f"Finished result found for {race_id}: Position {result['position']}")
            message = format_message(result)
            send_telegram_notification(message)

            state[race_id] = {"notified": True, "type": result['type']}
            state_changed = True
        else:
            print(f"Race not finished or result not available for {race_id}")

    if state_changed:
        print("State changed, saving to storage.json...")
        save_state(state)

    print("Bot run finished.")

if __name__ == "__main__":
    main()