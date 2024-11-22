from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
import time
import logging
import atexit
import signal
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TikTokScraper:
    def __init__(self):
        self.driver = None
        # Register cleanup functions
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def initialize_driver(self):
        try:
            options = uc.ChromeOptions()
            options.add_argument('--start-maximized')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Initialize the driver with explicit executable path
            self.driver = uc.Chrome(options=options)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize driver: {str(e)}")
            return False

    def cleanup(self):
        """Safe cleanup of browser resources"""
        try:
            if hasattr(self, 'driver') and self.driver is not None:
                logger.info("Cleaning up browser resources...")
                try:
                    self.driver.close()
                except:
                    pass
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        logger.info("Received interrupt signal. Cleaning up...")
        self.cleanup()
        sys.exit(1)

    def scrape_comments(self, video_url, max_scroll_attempts=10):
        if not self.initialize_driver():
            return []

        try:
            logger.info(f"Accessing URL: {video_url}")
            self.driver.get(video_url)
            time.sleep(5)  # Initial page load wait

            # Wait for comments section with multiple selector attempts
            selectors = [
                '[class*="DivCommentListContainer"]',
                '[data-e2e="comment-list"]',
                '[class*="CommentList"]'
            ]
            
            comments_found = False
            for selector in selectors:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    comments_found = True
                    logger.info(f"Comments section found with selector: {selector}")
                    break
                except:
                    continue

            if not comments_found:
                logger.error("Comments section not found with any selector")
                return []

            # Collect comments
            comments_set = set()
            scroll_attempts = 0
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            while scroll_attempts < max_scroll_attempts:
                # Scroll and wait
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

                # Try different comment selectors
                selectors = [
                    'div[class*="DivCommentItemContainer"]',
                    'div[data-e2e="comment-item"]',
                    'div[class*="CommentItem"]'
                ]
                
                for selector in selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        for element in elements:
                            try:
                                comment_text = element.text.strip()
                                if comment_text:
                                    comments_set.add(comment_text)
                            except:
                                continue

                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1
                logger.info(f"Scroll attempt {scroll_attempts}/{max_scroll_attempts}")

            # Save comments
            if comments_set:
                logger.info(f"Found {len(comments_set)} comments")
                with open("tiktok_comments.txt", "w", encoding="utf-8") as file:
                    for comment in comments_set:
                        file.write(comment + "\n")
                logger.info("Comments saved to tiktok_comments.txt")
            else:
                logger.warning("No comments found")

            return list(comments_set)

        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            return []
        finally:
            self.cleanup()

def main():
    video_url = "https://www.tiktok.com/@politik.pamekasan/video/7430442112254070021"
    scraper = TikTokScraper()
    
    try:
        comments = scraper.scrape_comments(video_url)
        if comments:
            print(f"\nSuccessfully scraped {len(comments)} comments!")
            print("\nFirst few comments:")
            for comment in comments[:5]:
                print(comment)
        else:
            print("No comments were scraped. Check the logs for details.")
    except Exception as e:
        logger.error(f"Main execution error: {str(e)}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()