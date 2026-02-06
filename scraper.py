import requests
from bs4 import BeautifulSoup
import datetime

BASE_URL = "https://www.procyclingstats.com/"

def get_page_content(url):
    """Fetches and parses a URL, returning a BeautifulSoup object."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'lxml')
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_rider_races(rider_url):
    """Gets the list of races for a rider for the current year."""
    soup = get_page_content(rider_url)
    if not soup:
        return []

    races = []
    current_year = str(datetime.date.today().year)
    results_table = soup.select_one('table.results')
    if not results_table:
        return []

    for row in results_table.select('tbody tr'):
        year_td = row.select_one('td:nth-child(1)')
        if not year_td or year_td.get_text(strip=True) != current_year:
            continue

        race_link_element = row.select_one('td:nth-child(3) a')
        if race_link_element and 'href' in race_link_element.attrs:
            race_path = race_link_element['href']
            race_name = race_link_element.get_text(strip=True)
            race_url = BASE_URL + race_path
            race_id = race_path.split('?')[0].replace('race/', '')
            races.append({'race_id': race_id, 'race_url': race_url, 'race_name_initial': race_name})
    return races

def get_race_result(race_url):
    """Scrapes a race page to find João Almeida's result."""
    soup = get_page_content(race_url)
    if not soup:
        return None

    race_name = soup.select_one('h1').get_text(strip=True).split('›')[-1].strip()
    almeida_selector = 'tr:has(a[href*="/rider/joao-almeida"])'

    # Check for Stage Race (GC table)
    gc_table = soup.select_one('table.results.gc')
    if gc_table:
        almeida_row = gc_table.select_one(almeida_selector)
        if almeida_row and almeida_row.select_one('td.pos').get_text(strip=True).isnumeric():
            return {
                "type": "stage_race", "race_name": race_name,
                "position": almeida_row.select_one('td.pos').get_text(strip=True),
                "time_gap": almeida_row.select_one('td.time').get_text(strip=True),
                "team": almeida_row.select_one('td.team a').get_text(strip=True)
            }

    # Check for One-Day Race (final results table)
    results_table = soup.select_one('table.results')
    if results_table and not gc_table:
        almeida_row = results_table.select_one(almeida_selector)
        if almeida_row:
            pos = almeida_row.select_one('td.pos').get_text(strip=True)
            if pos.isnumeric() or pos in ["DNF", "DNS", "OTL", "DSQ"]:
                return {
                    "type": "one_day_race", "race_name": race_name, "position": pos,
                    "time_gap": almeida_row.select_one('td.time').get_text(strip=True),
                    "team": almeida_row.select_one('td.team a').get_text(strip=True)
                }
    return None