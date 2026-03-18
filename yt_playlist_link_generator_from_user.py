from playwright.sync_api import sync_playwright
import time
import csv

def harvest_channel_playlists(channel_url, output_file="mai_van_lang_playlists.csv", max_scrolls=20):
    # Safety check: Ensure the URL actually lands on the playlists tab
    if not channel_url.endswith("/playlists"):
        channel_url = channel_url.rstrip("/") + "/playlists"
        
    playlist_data = {} 

    print(f"Launching Browser and navigating to Channel...")
    print(f"Target: {channel_url}")
    
    with sync_playwright() as p:
        # Set headless=True if you want it to run invisibly
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()
        
        page.goto(channel_url)
        print("Successfully loaded the channel's playlists tab.")
        print("Beginning infinite scroll. Please wait...\n")
        
        # 1. The Infinite Scroll Loop
        for i in range(max_scrolls):
            # Scroll to the bottom to trigger YouTube's lazy loading
            page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
            time.sleep(2) 
            
            # --- THE UPDATED LOCATOR ---
            # Grab EVERY anchor tag that contains 'list=' in its URL
            elements = page.locator("a[href*='list=']").all()
            
            for el in elements:
                href = el.get_attribute("href")
                # Extract the visible text. Thumbnails will return empty strings.
                title = el.inner_text().strip() 
                
                # Only process if we have a valid link AND actual text
                if href and "list=" in href and title:
                    
                    # Ignore YouTube's generic UI text buttons
                    if title.lower() in ["play all", "phát tất cả", "xem toàn bộ danh sách phát", "view full playlist"]:
                        continue
                        
                    try:
                        # Extract the pure Playlist ID
                        playlist_id = href.split('list=')[1].split('&')[0]
                        
                        # QUALITY CONTROL: 
                        # Standard playlists start with 'PL'. Album releases start with 'OL'.
                        # YouTube's auto-generated infinite mixes start with 'RD'. We drop the mixes.
                        if playlist_id.startswith('PL') or playlist_id.startswith('OL'):
                            clean_url = f"https://www.youtube.com/playlist?list={playlist_id}"
                            
                            # Dictionary automatically overwrites/prevents duplicates
                            playlist_data[playlist_id] = {
                                "Title": title,
                                "URL": clean_url
                            }
                    except IndexError:
                        pass
            
            print(f"  --> Scroll {i+1}/{max_scrolls} complete. Unique playlists found: {len(playlist_data)}")

        browser.close()

    # 2. Save the harvested links to a CSV
    print(f"\nScroll complete! Saving {len(playlist_data)} pristine playlists to {output_file}...")
    
    with open(output_file, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Playlist_Title", "Playlist_URL"])
        
        for data in playlist_data.values():
            writer.writerow([data["Title"], data["URL"]])

    print("Success! Your channel-specific top-of-funnel dataset is ready.")

if __name__ == "__main__":
    # The target channel's playlist tab
    TARGET_CHANNEL = "https://www.youtube.com/@SoanGiaMaiVanLangNew/playlists" 
    
    # 20 scrolls should be more than enough to hit the bottom of almost any channel's playlist tab
    harvest_channel_playlists(TARGET_CHANNEL, max_scrolls=20)