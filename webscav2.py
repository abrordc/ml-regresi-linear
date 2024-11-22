from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
import time

class TikTokScraper:
    def __init__(self):
        self.driver = None
    
    def initialize_driver(self):
        options = uc.ChromeOptions()
        options.add_argument('--headless')  # Optional: run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = uc.Chrome(options=options)
        
    def get_comments(self, video_url, max_comments=50):
        try:
            if not self.driver:
                self.initialize_driver()
                
            self.driver.get(video_url)
            
            # Wait for comments to load
            wait = WebDriverWait(self.driver, 20)
            comments_section = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-e2e="comment-list"]'))
            )
            
            # Scroll to load more comments
            comments = []
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while len(comments) < max_comments:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for content to load
                
                # Get comments
                comment_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-e2e="comment-level-1"]')
                
                for element in comment_elements:
                    try:
                        username = element.find_element(By.CSS_SELECTOR, '[data-e2e="comment-username-1"]').text
                        text = element.find_element(By.CSS_SELECTOR, '[data-e2e="comment-text-1"]').text
                        comments.append({
                            'username': username,
                            'text': text
                        })
                    except:
                        continue
                        
                    if len(comments) >= max_comments:
                        break
                
                # Check if we've reached the bottom
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
            return comments
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return []
            
        finally:
            self.close()
    
    def close(self):
        """Safely close the browser"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception as e:
            print(f"Error while closing browser: {str(e)}")

# Example usage
if __name__ == "__main__":
    scraper = TikTokScraper()
    video_url = "https://www.tiktok.com/@politik.pamekasan/video/7430442112254070021"  # Replace with actual video URL
    comments = scraper.get_comments(video_url, max_comments=30)
    
    for comment in comments:
        print(f"{comment['username']}: {comment['text']}")