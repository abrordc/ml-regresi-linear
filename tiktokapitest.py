
from TikTokApi import TikTokApi

# Inisialisasi TikTokApi
api = TikTokApi(logging_level="DEBUG")

# URL video TikTok
video_url = "https://www.tiktok.com/@politik.pamekasan/video/7430442112254070021"

# Ambil data video
video = api.video(url=video_url)

# Ambil komentar
comments = video.comments(count=20)  # Batasi jumlah komentar

# Tampilkan komentar
for comment in comments:
    print(comment.text)
