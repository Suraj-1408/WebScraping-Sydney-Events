from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from db import get_db_connection

 
BASE_URL = "https://www.sydney.com"
EVENTS_URL = urljoin(BASE_URL, "/events")
 

def scrape_events():
    # Setup headless Chrome driver
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)

    print("EVENTS_URL:", EVENTS_URL)

    driver.get(EVENTS_URL)
    driver.implicitly_wait(10)  # wait for JS to load

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")

    event_tiles = soup.find_all("div", class_="grid-item product-list-widget tile__product-list")

    events = []

    for tile in event_tiles:
        try:
            # Event URL
            a_tag = tile.find("a", class_="tile__product-list-link")
            url = a_tag['href'] if a_tag and 'href' in a_tag.attrs else ""

            # Title
            title_tag = tile.find("div", class_="tile__product-list-tile-heading")
            title = title_tag.find("h3").get_text(strip=True) if title_tag else ""

            # Location
            location_tag = tile.find("div", class_="tile__product-list-area")
            location = location_tag.find("span", class_="tile__area-name").get_text(strip=True) if location_tag else ""

            # Description
            desc_tag = tile.find("div", class_="prod-desc")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            # Dates
            start_date_tag = tile.find("time", class_="start-date")
            start_date = start_date_tag.get_text(strip=True) if start_date_tag else ""

            end_date_tag = tile.find("time", class_="end-date")
            end_date = end_date_tag.get_text(strip=True) if end_date_tag else ""

            # Image URL
            image_div = tile.find("div", class_="tile__product-list-image")
            img_tag = image_div.find("img") if image_div else None
            img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else ""

            events.append((title, location, description, start_date, end_date, url, img_url))

        except Exception as e:
            print(f"Error while parsing event tile: {e}")
            continue

    return events


def save_events_to_db(events):
    conn = get_db_connection()       
    cur = conn.cursor()

    for event in events:
        cur.execute("""
            INSERT IGNORE INTO events (title, location, description, start_date, end_date, url, img_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, event)
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(events)} events into the database.")
