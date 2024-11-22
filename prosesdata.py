import re
from datetime import datetime, timedelta
import pandas as pd

def parse_comments(file_path):
    # Baca isi file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()

    # Pisahkan berdasarkan pola tertentu (nama, komentar, tanggal, interaksi)
    comments = []
    pattern = r"(.*?)\n(.*?)\n([\w-]+)\n(\d+)"
    matches = re.findall(pattern, data, re.DOTALL)
    
    for match in matches:
        username = match[0].strip()
        comment = match[1].strip()
        date_raw = match[2].strip()
        interaction_count = int(match[3].strip())
        
        # Konversi tanggal jika memungkinkan
        if "yang lalu" in date_raw or "j" in date_raw:
            hours_ago = int(re.search(r'\d+', date_raw).group())
            date = (datetime.now() - timedelta(hours=hours_ago)).strftime('%Y-%m-%d')
        else:
            # Format MM-DD ke format YYYY-MM-DD
            try:
                month, day = map(int, date_raw.split('-'))
                year = datetime.now().year
                date = f"{year}-{month:02d}-{day:02d}"
            except:
                date = date_raw  # Simpan mentah jika gagal
        
        # Tambahkan ke daftar
        comments.append({
            'username': username,
            'comment': comment,
            'date': date,
            'interaction_count': interaction_count
        })
    
    return comments

def save_to_excel(parsed_data, output_file):
    df = pd.DataFrame(parsed_data)
    df.to_excel(output_file, index=False)
    print(f"Comments saved to {output_file}")

# Lokasi file teks
file_path = "comments.txt"
output_file = "comments.xlsx"

# Parsing data
parsed_comments = parse_comments("tiktok_comments.txt")

# Simpan hasil ke Excel
save_to_excel(parsed_comments, output_file)
