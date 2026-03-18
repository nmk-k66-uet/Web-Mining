from google import genai
from google.genai import types
import pandas as pd
import json
import time
import os
from tqdm import tqdm

# --- CẤU HÌNH ---
API_KEY = "AIzaSyB5TS2vQmxq_It55-wh68wQSTk0vzVhDbE"
INPUT_FILE = "Audio.xlsx"
SHEET_NAME = "Sheet3"     
COLUMN_NAME = "Description" 
OUTPUT_FILE = "ket_qua_cheo.xlsx"
BATCH_SIZE = 15 

client = genai.Client(api_key=API_KEY)

CONFIG = types.GenerateContentConfig(
    response_mime_type="application/json",
    thinking_config=types.ThinkingConfig(include_thoughts=False, thinking_level="medium"),
    temperature=1.0
)

PROMPT_TEMPLATE = """
Trích xuất thông tin Chèo từ danh sách sau thành JSON list:
- tac_gia, doan_dien, soan_loi, vo_dien, ngay_bieu_dien (DD/MM/YYYY)
- nguoi_hat: [mảng nghệ sĩ]
- lan_dieu: [mảng làn điệu Chèo]

Dữ liệu:
{}
"""

def process_data():
    try:
        df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)
    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return

    # Resume logic
    if os.path.exists(OUTPUT_FILE):
        df_result = pd.read_excel(OUTPUT_FILE)
        start_idx = len(df_result)
        print(f"Tiếp tục từ dòng {start_idx}...")
    else:
        start_idx = 0
        df_result = pd.DataFrame()

    for i in tqdm(range(start_idx, len(df), BATCH_SIZE)):
        batch_slice = df.iloc[i:i+BATCH_SIZE]
        batch_texts = batch_slice[COLUMN_NAME].astype(str).tolist()
        formatted_list = "\n---\n".join([f"[{j}]: {txt}" for j, txt in enumerate(batch_texts)])
        
        try:
            # Gọi API theo cú pháp mới của Gemini 3
            response = client.models.generate_content(
                model='gemini-3-flash-preview', 
                contents=PROMPT_TEMPLATE.format(formatted_list),
                config=CONFIG
            )
            
            results = json.loads(response.text)
            batch_extracted = pd.DataFrame(results)
            combined_batch = pd.concat([batch_slice.reset_index(drop=True), batch_extracted], axis=1)
            
            df_result = pd.concat([df_result, combined_batch], ignore_index=True)
            df_result.to_excel(OUTPUT_FILE, index=False)
            
            time.sleep(1) # Gemini 3 Flash xử lý rất nhanh
        except Exception as e:
            print(f"Lỗi tại {i}: {e}")
            time.sleep(5)

    print("Hoàn tất!")

if __name__ == "__main__":
    process_data()