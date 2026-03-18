import pandas as pd
import os
from pathlib import Path
from moviepy import VideoFileClip
from tqdm import tqdm

def time_to_seconds(time_str):
    try:
        parts = time_str.split(':')
        if len(parts) == 2: # mm:ss
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3: # hh:mm:ss
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0
    except:
        return 0

def process_audio_segments(excel_path, source_dir, target_dir):
    df = pd.read_excel(excel_path) 
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)

    for index, row in tqdm(df.iterrows(), total=len(df), desc="Đang cắt âm thanh"):
        try:
            title = str(row['Title']).strip()
            title_id = row['Title_ID']
            segment_id = row['Segment_ID']
            start_sec = time_to_seconds(str(row['Start_time']))
            end_sec = time_to_seconds(str(row['End_time']))

            video_file = source_path / f"{title}.mp4"

            if not video_file.exists():
                tqdm.write(f"⚠️ Không tìm thấy: {video_file}")
                continue

            with VideoFileClip(str(video_file)) as video:
                actual_end = min(end_sec, video.duration)
                
                # Format: ID_001.wav
                output_filename = f"{title_id}_{int(segment_id):03d}.wav"
                output_path = target_path / output_filename

                # Trích xuất và lưu
                audio_segment = video.subclipped(start_sec, actual_end).audio
                audio_segment.write_audiofile(
                    str(output_path), 
                    fps=44100,
                    codec='pcm_s16le', 
                    logger=None
                )
        except Exception as e:
            tqdm.write(f"❌ Lỗi dòng {index} ({row.get('Title', 'N/A')}): {e}")

if __name__ == "__main__":
    EXCEL_FILE = "Audio.xlsx" 
    SOURCE_VIDEOS = r"videos"
    TARGET_AUDIOS = r"audios/cheo"

    process_audio_segments(EXCEL_FILE, SOURCE_VIDEOS, TARGET_AUDIOS)
    print("\n✅ Hoàn thành xử lý toàn bộ danh sách!")