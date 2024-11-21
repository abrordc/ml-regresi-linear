from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time

try: 
# Inisialisasi Selenium
    driver = webdriver.Chrome()

    # URL video TikTok
    video_url = "https://www.tiktok.com/@politik.pamekasan/video/7430442112254070021"
    driver = uc.Chrome()
    driver.get(video_url)

    # Tunggu elemen komentar muncul
    try:
        # Tunggu hingga komentar termuat
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.css-7whb78-DivCommentListContainer'))
        )
        print("Komentar ditemukan!")
    except Exception as e:
        print("Komentar tidak ditemukan:", e)
        driver.quit()
        exit()

    # Scrolling untuk memuat lebih banyak komentar
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Tunggu untuk memuat komentar baru
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Ambil elemen komentar
    comments = driver.find_elements(By.CSS_SELECTOR, 'div[data-e2e="comment-item"]')

    with open("comments.txt", "w", encoding="utf-8") as file:
        for comment in comments:
            text = comment.text.strip()  # Hapus spasi atau karakter kosong di awal/akhir
            file.write(text + "\n")  # Tulis komentar ke file dan tambahkan baris baru
            print(text)  # Tampilkan komentar di terminal (opsional)

    driver.save_screenshot("final_debug.png")

finally:
    driver.quit()

