from playwright.sync_api import sync_playwright
import time
import csv

def harvest_playlist_links_from_query(search_query, output_file="cheo_playlist_links.csv", max_scrolls=30):
    # Format the query string to replace spaces with '+'
    formatted_query = search_query.replace(' ', '+')
    
    # Inject the query and the strict "Playlist Only" filter (sp=EgIQAw%253D%253D)
    search_url = f"https://www.youtube.com/results?search_query={formatted_query}&sp=EgIQAw%253D%253D"
    
    playlist_data = {} # Using a dictionary to automatically prevent duplicates

    print(f"Launching Browser and navigating to YouTube...")
    
    with sync_playwright() as p:
        # headless=False lets you watch it work! Set to True if you want it to run invisibly in the background.
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()
        
        page.goto(search_url)
        print(f"Successfully loaded search: '{search_query}'")
        print("Beginning infinite scroll. Please wait...\n")
        
        # 1. The Infinite Scroll Loop
        # 1. The Infinite Scroll Loop
        for i in range(max_scrolls):
            page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
            time.sleep(2) 
            
            # --- UPDATED LOCATOR ---
            # Targeting the exact class from your HTML snippet
            elements = page.locator("a.yt-lockup-metadata-view-model__title").all()
            
            for el in elements:
                href = el.get_attribute("href")
                
                # --- UPDATED TITLE EXTRACTION ---
                # Since the 'title' attribute is gone, we extract the visible text directly from the nested <span>
                title = el.inner_text().strip() 
                
                if href and "list=" in href and title:
                    # --- UPDATED ID PARSING ---
                    # 1. Split at 'list=' and take the second half
                    # 2. Split at '&' and take the first half (removes extra parameters if they exist)
                    playlist_id = href.split('list=')[1].split('&')[0]
                    
                    # Reconstruct the clean, direct playlist URL
                    clean_url = f"https://www.youtube.com/playlist?list={playlist_id}"
                    
                    playlist_data[playlist_id] = {
                        "Title": title,
                        "URL": clean_url
                    }
            
            print(f"  --> Scroll {i+1}/{max_scrolls} complete. Unique playlists found so far: {len(playlist_data)}")
            
    # 3. Save the harvested links to a CSV
    print(f"\nScroll complete! Saving {len(playlist_data)} playlists to {output_file}...")
    
    with open(output_file, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Playlist_Title", "Playlist_URL"])
        
        for data in playlist_data.values():
            writer.writerow([data["Title"], data["URL"]])

    print("Success! Your top-of-funnel list is ready.")

if __name__ == "__main__":
    # You can change this query to anything: "nhạc chèo cổ", "dạy hát chèo", etc.
    TARGET_QUERY = "chèo" 
    
    # max_scrolls determines how deep it digs. 30 scrolls usually yields 100-200 playlists.
    harvest_playlist_links_from_query(TARGET_QUERY, max_scrolls=30)