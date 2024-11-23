from gtts import gTTS
import os
import pygame

def read_text_from_file(file_path):
    try:
        # Membaca teks dari file
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Konversi teks menjadi suara
        tts = gTTS(text, lang='id')  # Bahasa Indonesia, ubah 'id' ke 'en' jika perlu
        audio_file = "output_audio1.mp3"
        tts.save(audio_file)
        
        # Memulai pygame untuk memutar audio
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        # Menunggu sampai audio selesai diputar
        while pygame.mixer.music.get_busy():  # Memeriksa apakah audio masih diputar
            pygame.time.Clock().tick(10)
        
        # Menghapus file audio setelah selesai
        os.remove(audio_file)
    
    except Exception as e:
        print(f"Error: {e}")

# Path ke file teks
file_path = "tiktok_comments.txt"  # Ganti dengan path file kamu

# Memulai program
read_text_from_file(file_path)