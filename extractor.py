from google import genai
from google.genai import types
import pandas as pd
import json
import time
import os
from tqdm import tqdm
import argparse

# --- CẤU HÌNH ---
# Read API_KEY from file
API_KEY_FILE = "api_key.txt"
if os.path.exists(API_KEY_FILE):
    with open(API_KEY_FILE, 'r') as f:
        API_KEY = f.read().strip()
else:
    raise FileNotFoundError(f"API key file '{API_KEY_FILE}' not found. Please create it with your API key.")

INPUT_FILE = "Statistic/Dataset.xlsx"
SHEET_NAME = "Text Dataset"     
COLUMN_NAME = "Description" 
OUTPUT_FILE = "ket_qua_cheo.xlsx"
BATCH_SIZE = 10 

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

def process_data(start_idx=None):
    try:
        df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)
    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return

    # Resume logic
    if start_idx is None:
        if os.path.exists(OUTPUT_FILE):
            df_result = pd.read_excel(OUTPUT_FILE)
            start_idx = len(df_result)
            print(f"Tiếp tục từ dòng {start_idx}...")
        else:
            start_idx = 0
            df_result = pd.DataFrame()
    else:
        if os.path.exists(OUTPUT_FILE):
            df_result = pd.read_excel(OUTPUT_FILE)
        else:
            df_result = pd.DataFrame()
        print(f"Bắt đầu từ dòng chỉ định: {start_idx}...")

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
            # Ensure results is a list
            if isinstance(results, dict) and len(results) == 1:
                results = list(results.values())[0]
                
            batch_extracted = pd.DataFrame(results)
            # Use index-based join to handle cases where AI returns fewer/more items than BATCH_SIZE
            combined_batch = batch_slice.reset_index(drop=True).join(batch_extracted, rsuffix='_extracted')
            
            df_result = pd.concat([df_result, combined_batch], ignore_index=True)
            df_result.to_excel(OUTPUT_FILE, index=False)
            
            time.sleep(2) # Avoid rate limits
        except Exception as e:
            print(f"Lỗi tại {i}: {e}")
            time.sleep(5)

    print("Hoàn tất!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract data from Excel using Gemini API")
    parser.add_argument('--start-row', type=int, default=None, help="Starting row index (0-based) to begin extraction. If not provided, resumes from output file.")
    args = parser.parse_args()
    
    process_data(start_idx=args.start_row)