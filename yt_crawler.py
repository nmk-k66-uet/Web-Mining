import yt_dlp
import os
import csv
import time

def extract_metadata_humanized(playlist_url, output_dir="Cheo_Metadata"):
    os.makedirs(output_dir, exist_ok=True)
    metadata_path = os.path.join(output_dir, "cheo_metadata_channel1.csv")

    # 1. Initialize the CSV
    file_exists = os.path.isfile(metadata_path)
    with open(metadata_path, mode='a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                'YouTube_ID', 'Expected_Filename', 'Raw_Title_Label', 
                'Uploader_Channel', 'Duration_Seconds', 
                'Upload_Date', 'View_Count', 'Like_Count', 'Full_Description'
            ])

    print(f"Fetching playlist structure...\n")

    # 2. FAST PASS: Get the flat list of video URLs first
    flat_opts = {'extract_flat': True, 'quiet': True}
    with yt_dlp.YoutubeDL(flat_opts) as ydl_flat:
        playlist_info = ydl_flat.extract_info(playlist_url, download=False)
        videos = playlist_info.get('entries', [playlist_info])

    total_videos = len(videos)
    print(f"Found {total_videos} videos. Starting humanized extraction...\n")

    # 3. DEEP PASS: Configure the metadata extractor with Anti-Bot delays
    meta_opts = {
        'quiet': True,
        'ignoreerrors': True,
        
        # --- THE RATE LIMIT FIXES ---
        # Random sleep between 3 and 8 seconds per request
        'sleep_interval': 3,
        'max_sleep_interval': 8,
        
        # Force IPv4 routing (sometimes bypasses IPv6 blanket bans)
        'source_address': '0.0.0.0', 
    }

    # 4. Loop through and extract
    with yt_dlp.YoutubeDL(meta_opts) as ydl_meta:
        for i, video in enumerate(videos):
            if video is None:
                continue

            v_id = video.get('id')
            video_url = video.get('url') or f"https://www.youtube.com/watch?v={v_id}"
            expected_filename = f"{v_id}.wav"
            
            print(f"[{i+1}/{total_videos}] Extracting: {video.get('title', v_id)}")

            try:
                info = ydl_meta.extract_info(video_url, download=False)
                
                if not info:
                    print(f"  --> [WARNING] Could not fetch data for {v_id}. Skipping.\n")
                    continue

                # Extract everything safely
                v_title = info.get('title', 'Unknown Title')
                uploader = info.get('uploader', 'Unknown')
                duration = info.get('duration', 0)
                upload_date = info.get('upload_date', 'Unknown')
                view_count = info.get('view_count', 0)
                like_count = info.get('like_count', 0)
                
                # Clean the description
                description = info.get('description', '')
                if description:
                    description = description.replace('\n', ' ').replace('\r', '')

                # Save directly to CSV
                with open(metadata_path, mode='a', encoding='utf-8', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        v_id, expected_filename, v_title, 
                        uploader, duration, upload_date, 
                        view_count, like_count, description
                    ])
                
                print("  --> Success. Sleeping to mimic human behavior...\n")
                
            except Exception as e:
                print(f"  --> Failed to extract metadata for {v_id}. Error: {e}\n")

    print(f"\nExtraction complete! All data securely logged in {metadata_path}")

if __name__ == "__main__":
    # Point this to the output file from your cleaning script
    input_csv = "mai_van_lang_playlists_cleaned.csv"
    
    # Safety check to ensure the file exists
    if not os.path.exists(input_csv):
        print(f"Error: Could not find '{input_csv}'. Please ensure it is in the same folder.")
    else:
        print(f"Loading verified playlists from {input_csv}...\n")
        
        # Open and read the CSV
        with open(input_csv, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            # Skip the header row ("Playlist_Title", "Playlist_URL")
            next(reader, None)
            
            # Loop through every row in the file
            for row_num, row in enumerate(reader, start=1):
                # Guard against accidental blank rows in the CSV
                if not row or len(row) < 2:
                    continue
                
                playlist_title = row[0]
                playlist_url = row[1]
                
                print("\n" + "=" * 60)
                print(f"🎬 PROCESSING PLAYLIST #{row_num}: {playlist_title}")
                print("=" * 60)
                
                try:
                    # Feed the URL directly into your extraction function
                    extract_metadata_humanized(playlist_url)
                except Exception as e:
                    print(f"CRITICAL ERROR on playlist {playlist_title}: {e}")
                    print("Skipping to the next playlist...\n")
                    
        print("\n PIPELINE COMPLETE! All playlists have been processed.")