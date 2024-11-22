from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
import time
import logging
import pandas as pd
import re
from datetime import datetime, timedelta
import atexit
import signal

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TikTokExcelScraper:
    def __init__(self):
        self.driver = None
        # Register cleanup
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        self.cleanup()
        
    def cleanup(self):
        """Safe cleanup of browser resources"""
        try:
            if self.driver:
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
        
    def initialize_driver(self):
        try:
            options = uc.ChromeOptions()
            options.add_argument('--start-maximized')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            self.driver = uc.Chrome(options=options)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize driver: {str(e)}")
            return False
            
    def save_to_excel(self, comments_data, output_file):
        """Safely save data to Excel"""
        try:
            df = pd.DataFrame(comments_data)
            df = df.drop_duplicates()  # Remove duplicates
            
            # Try saving with openpyxl first
            try:
                df.to_excel(output_file, index=False, engine='openpyxl')
            except:
                # Fallback to CSV if Excel fails
                csv_file = output_file.replace('.xlsx', '.csv')
                df.to_csv(csv_file, index=False, encoding='utf-8-sig')
                logger.info(f"Saved as CSV instead: {csv_file}")
            
            return True
        except Exception as e:
            logger.error(f"Error saving to file: {str(e)}")
            return False

    def parse_comment(self, comment_text):
        """Extract username and comment from the text"""
        try:
            # Split into lines
            lines = comment_text.strip().split('\n')
            if not lines:
                return None
                
            # First line is username
            username = lines[0].strip()
            
            # Find the date
            date = None
            comment_lines = []
            
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if line is a date
                if re.search(r'\d{1,2}-\d{1,2}|[0-9]+[hj] yang lalu', line):
                    date = line
                # Skip "Jawab" line
                elif line != "Jawab":
                    comment_lines.append(line)
            
            # Join remaining lines as comment
            comment = ' '.join(comment_lines).strip()
            
            # Convert date format
            if date:
                if 'j yang lalu' in date or 'h yang lalu' in date:
                    hours = int(re.search(r'\d+', date).group())
                    date = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d')
                else:
                    # Assuming MM-DD format
                    try:
                        month, day = map(int, date.split('-'))
                        year = datetime.now().year
                        date = f"{year}-{month:02d}-{day:02d}"
                    except:
                        date = date  # Keep original if parsing fails

            return {
                'username': username,
                'comment': comment,
                'date': date if date else ''
            }
            
        except Exception as e:
            logger.error(f"Error parsing comment: {str(e)}")
            return None

    def scrape_comments(self, video_url, output_file="tiktok_comments.xlsx", max_scroll_attempts=10):
        if not self.initialize_driver():
            return False

        try:
            logger.info(f"Accessing URL: {video_url}")
            self.driver.get(video_url)
            time.sleep(5)  # Initial load wait

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
                    break
                except:
                    continue

            if not comments_found:
                logger.error("Comments section not found")
                return False

            comments_data = []
            scroll_attempts = 0
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            while scroll_attempts < max_scroll_attempts:
                # Get comments
                comment_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    'div[class*="DivCommentItemContainer"], div[data-e2e="comment-item"]')
                logger.info(f"Found {len(comment_elements)} comment elements.")
                
                for element in comment_elements:
                    try:
                        comment_text = element.text.strip()
                        if comment_text:
                            parsed_comment = self.parse_comment(comment_text)
                            if parsed_comment:
                                comments_data.append(parsed_comment)
                    except Exception as e:
                        continue

                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1
                logger.info(f"Scroll attempt {scroll_attempts}/{max_scroll_attempts}")

            if comments_data:
                if self.save_to_excel(comments_data, output_file):
                    logger.info(f"Successfully saved {len(comments_data)} comments")
                    return True
            else:
                logger.warning("No comments found")
                
            return False

        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            return False
        finally:
            self.cleanup()

def main():
    video_url = "https://www.tiktok.com/@politik.pamekasan/video/7430442112254070021"
    scraper = TikTokExcelScraper()
    
    try:
        if scraper.scrape_comments(video_url):
            print("Comments successfully scraped and saved!")
        else:
            print("Failed to scrape comments. Check the logs for details.")
    except Exception as e:
        logger.error(f"Main execution error: {str(e)}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()