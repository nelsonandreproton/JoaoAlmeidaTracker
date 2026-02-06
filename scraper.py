import requests
import cloudscraper
from bs4 import BeautifulSoup
import datetime

BASE_URL = "https://www.procyclingstats.com/"

def get_page_content(url):
    """Fetches and parses a URL, returning a BeautifulSoup object."""
    try:
        # Use a specific browser profile to better mimic a real user
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
        response = scraper.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'lxml')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_rider_races(rider_url):
    """Gets the list of races for a rider for the current year."""
    today = datetime.date.today()
    current_year = str(today.year)
    
    # Construct the URL for the specific season to ensure correct table format
    # Example: https://www.procyclingstats.com/rider/joao-almeida/2025
    season_url = f"{rider_url.rstrip('/')}/{current_year}"
    
    print(f"DEBUG: Fetching rider races for year {current_year} from: {season_url}")
    soup = get_page_content(season_url)
    if not soup:
        return []

    # Debug: Print page title to ensure we aren't stuck on a Cloudflare challenge page
    page_title = soup.title.string.strip() if soup.title else "No Title"
    print(f"DEBUG: Page Title: '{page_title}'")

    races = []
    
    # Try primary selector
    results_table = soup.select_one('table.results')
    
    # Fallback selector (sometimes used by PCS)
    if not results_table:
        results_table = soup.select_one('table.rdrResults')

    if not results_table:
        print("DEBUG: No results table found.")
        # Debug: list all tables found to help diagnose
        tables = soup.find_all('table')
        if tables:
            print(f"DEBUG: Found {len(tables)} tables. Classes: {[t.get('class') for t in tables]}")
        else:
            print("DEBUG: No tables found in HTML. Possible Cloudflare block or layout change.")
        return []

    for row in results_table.select('tbody tr'):
        # 1. Parse the Date Column to check if race finishes TODAY
        date_col = row.select_one('td:nth-child(1)')
        if not date_col:
            continue
            
        date_text = date_col.get_text(strip=True)
        # Format can be "26.01" (One Day) or "19.02 » 23.02" (Stage Race)
        if '»' in date_text:
            end_date_str = date_text.split('»')[-1].strip()
        else:
            end_date_str = date_text.strip()
            
        try:
            day, month = map(int, end_date_str.split('.'))
            race_date = datetime.date(today.year, month, day)
        except ValueError:
            continue # Skip rows with invalid dates
            
        if race_date != today:
            # print(f"DEBUG: Skipping {date_text} (Not today)") # Optional: uncomment for verbose logs
            continue

        # 2. Extract Race Info
        # Find the race link (usually contains 'race/' in the href)
        race_link_element = row.select_one('a[href*="race/"]')
        
        if race_link_element and 'href' in race_link_element.attrs:
            race_path = race_link_element['href']
            race_name = race_link_element.get_text(strip=True)
            
            # Handle relative URLs correctly
            if race_path.startswith('/'):
                race_url = "https://www.procyclingstats.com" + race_path
            else:
                race_url = BASE_URL + race_path
                
            race_id = race_path.split('?')[0].replace('race/', '')
            races.append({'race_id': race_id, 'race_url': race_url, 'race_name_initial': race_name})
            print(f"DEBUG: Found race finishing TODAY ({race_date}): {race_name}")
            
    if not races:
        print(f"DEBUG: No races found for year {current_year} in the table.")
        
    return races

def get_race_result(race_url):
    """Scrapes a race page to find João Almeida's result."""
    print(f"DEBUG: Checking race URL: {race_url}")
    soup = get_page_content(race_url)
    if not soup:
        return None

    # Debug: Print page title
    page_title = soup.title.string.strip() if soup.title else "No Title"
    print(f"DEBUG: Race Page Title: '{page_title}'")

    h1 = soup.select_one('h1')
    if h1:
        # Clean up race name (handle different separators like » or ›)
        race_name = h1.get_text(strip=True).replace('»', '›').split('›')[-1].strip()
    else:
        race_name = "Unknown Race"
    
    # Find all occurrences of the rider to capture both Stage and GC results
    # Remove leading slash to match both absolute and relative URLs (e.g. "rider/joao-almeida")
    rider_links = soup.select('a[href*="rider/joao-almeida"]')
    
    if not rider_links:
        print("DEBUG: João Almeida not found in results.")
        return None

    # Initialize result container
    data = {
        "type": "one_day_race", # Default
        "race_name": race_name,
        "stage_pos": None,
        "gc_pos": None,
        "time_gap": "",
        "team": ""
    }

    # Check if URL implies stage race
    is_stage_race_url = "stage" in race_url or "prologue" in race_url

    for link in rider_links:
        row = link.find_parent('tr')
        if not row: continue
        
        table = row.find_parent('table')
        if not table: continue
        
        table_classes = table.get('class', [])
        
        # Try to find a header for the table to identify it
        header_text = ""
        prev_node = table.find_previous(['h3', 'h4'])
        if prev_node:
            header_text = prev_node.get_text(strip=True).lower()

        # Helper to safely get text
        def get_col_text(selector):
            el = row.select_one(selector)
            return el.get_text(strip=True).replace(',', '').strip() if el else ""

        # Get Position (try .pos class, fallback to first column)
        pos_el = row.select_one('td.pos')
        if not pos_el:
            pos_el = row.select_one('td:nth-child(1)')
        pos = pos_el.get_text(strip=True) if pos_el else ""

        # Identification Logic
        is_gc_table = 'gc' in table_classes or 'general' in header_text or 'standing' in header_text
        is_aux_table = any(x in header_text for x in ['points', 'mountain', 'youth', 'team']) or \
                       any(cls in table_classes for cls in ['points', 'climber', 'sprint', 'youth', 'teams'])

        if is_aux_table:
            print(f"DEBUG: Skipping auxiliary table: {header_text} / {table_classes}")
            continue

        if is_gc_table:
            print(f"DEBUG: Found GC position: {pos}")
            data['gc_pos'] = pos
            data['type'] = "stage_race"
            # If team is missing from stage result, try getting it here
            if not data['team']:
                data['team'] = get_col_text('td.team')
        else:
            # Assume Stage/One-Day result
            # Only set stage_pos if it's not set yet (prevents overwriting by subsequent tables)
            if not data['stage_pos']:
                print(f"DEBUG: Found Stage/Result position: {pos}")
                data['stage_pos'] = pos
                data['time_gap'] = get_col_text('td.time')
                data['team'] = get_col_text('td.team')
            elif is_stage_race_url and not data['gc_pos']:
                # If we already have stage_pos, and this is a stage race, and we don't have GC yet...
                # This second table is likely GC even if we missed the header/class.
                print(f"DEBUG: Inferring GC position from second table: {pos}")
                data['gc_pos'] = pos
                data['type'] = "stage_race"

    # Construct final result object
    # If we have a GC position, it's definitely a stage race
    if data['gc_pos']:
        data['type'] = "stage_race"

    # Primary position is stage position, unless it's missing, then GC (fallback)
    primary_pos = data['stage_pos'] if data['stage_pos'] else data['gc_pos']
    
    if not primary_pos:
        return None

    return {
        "type": data['type'],
        "race_name": race_name,
        "position": primary_pos,
        "stage_position": data['stage_pos'],
        "gc_position": data['gc_pos'],
        "time_gap": data['time_gap'],
        "team": data['team']
    }