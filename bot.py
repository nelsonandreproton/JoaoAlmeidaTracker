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
    
    def fmt_gap(gap):
        if gap and not gap.startswith('+') and gap != ',,':
            return f"+{gap}"
        return gap or ""

    message = (
        f"🏁 Race finished!\n\n"
        f"🚴 João Almeida\n"
        f"📍 Race: {result['race_name']}\n"
    )

    if result['type'] == 'stage_race':
        if result.get('stage_position'):
            message += f"📊 Stage Position: {result['stage_position']}º\n"
        if result.get('gc_position'):
            message += f"🌍 GC Position: {result['gc_position']}º"
        message += f"\n⏱ {fmt_gap(result['time_gap'])}"
        gc_gap = fmt_gap(result.get('gc_time_gap', ''))
        if gc_gap:
            message += f"\n👕 {gc_gap}"
    else:
        pos = result['position']
        if pos.isnumeric():
             pos = f"{pos}º"
        message += f"📊 Final Position: {pos}"
        message += f"\n⏱ {fmt_gap(result['time_gap'])}"

    return message

def main():
    print("Starting João Almeida results check...")
    state = load_state()
    races_to_check = get_rider_races(RIDER_URL)

    state_changed = False
    for race in races_to_check:
        race_id = race['race_id']
        
        if state.get(race_id, {}).get('notified', False):
            print(f"DEBUG: Skipping {race_id} (Already notified).")
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