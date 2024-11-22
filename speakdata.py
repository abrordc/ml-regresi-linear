import pyttsx3

# from pyttsx3
def read_text_from_file(file_path):
    try:
        # Membaca file teks
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Inisialisasi engine pyttsx3
        engine = pyttsx3.init()
        
        # Mengatur properti suara (opsional)
        engine.setProperty('rate', 150)  # Kecepatan bicara
        engine.setProperty('volume', 1)  # Volume (0.0 sampai 1.0)
        
        # Membaca teks
        print("Membaca teks...")
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error: {e}")

# Path ke file teks
file_path = "tiktok_comments.txt"  # Ubah dengan lokasi file Anda

# Memulai program
read_text_from_file(file_path)
