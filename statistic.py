import os
import librosa
import pandas as pd
from tqdm import tqdm
from pathlib import Path

def get_audio_statistics(root_dir):
    data = []
    root_path = Path(root_dir)
    
    audio_files = list(root_path.glob("**/*.wav"))
    
    print(f"Bắt đầu quét {len(audio_files)} file audio...")
    
    for file_path in tqdm(audio_files, desc="Processing Audio"):
        try:
            # 1. Trích xuất thông tin từ đường dẫn và tên file
            folder_name = file_path.parent.name  
            file_name = file_path.stem          
            
            # Tách play_id và segment_id từ tên file
            parts = file_name.split('_')
            if len(parts) >= 3:
                play_id = parts[1]
                segment_id = parts[2]
            else:
                continue

            # 2. Tính thời lượng của file (giây)
            duration = librosa.get_duration(path=str(file_path))
            
            # 3. Lưu thông tin vào danh sách
            data.append({
                'folder': folder_name,
                'play_id': play_id,
                'segment_id': segment_id,
                'file_name': file_path.name,
                'duration': duration
            })
            
        except Exception as e:
            print(f"❌ Lỗi xử lý file {file_path}: {e}")

    df = pd.DataFrame(data)
    
    if df.empty:
        print("⚠️ Không có dữ liệu để thống kê.")
        return

    # 1. Thống kê tổng thời lượng theo từng Folder con
    folder_stats = df.groupby('folder')['duration'].sum().reset_index()
    folder_stats['duration_min'] = folder_stats['duration'] / 60
    folder_stats['duration_hour'] = folder_stats['duration'] / 3600

    # 2. Thống kê tổng thời lượng theo từng Play (Trích đoạn) trong mỗi Folder
    play_stats = df.groupby(['folder', 'play_id'])['duration'].sum().reset_index()
    play_stats['duration_min'] = play_stats['duration'] / 60

    # 3. Tổng thời lượng toàn bộ dataset
    total_sec = df['duration'].sum()
    
    print("\n" + "="*50)
    print("THỐNG KÊ DATASET AUDIO")
    print("="*50)
    
    print(f"\n🔹 Tổng số file: {len(df)}")
    print(f"🔹 Tổng thời lượng dataset: {total_sec/3600:.2f} giờ ({total_sec/60:.2f} phút)")
    
    print("\n🔹 Thống kê theo loại hình nghệ thuật (Folder):")
    print(folder_stats[['folder', 'duration_min', 'duration_hour']].to_string(index=False))
    
    print("\n🔹 Thống kê top 10 trích đoạn (Play) có thời lượng dài nhất:")
    print(play_stats.sort_values(by='duration', ascending=False).head(10).to_string(index=False))

    df.to_csv("chi_tiet_thoi_luong_file.csv", index=False, encoding='utf-8-sig')
    play_stats.to_csv("tong_thoi_luong_theo_play.csv", index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    dataset_path = "audios" 
    get_audio_statistics(dataset_path)