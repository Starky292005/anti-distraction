from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from PIL import Image
import time
import os


class WhatsAppScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Setup Chrome driver for WhatsApp Web"""
        options = webdriver.ChromeOptions()

        # Remove user-data-dir to avoid permission issues
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")  # Start maximized to see all chats

        # Automatic chromedriver management
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        self.driver.get("https://web.whatsapp.com")

        # Wait for user to scan QR code
        print("Please scan QR code and wait for WhatsApp Web to load...")
        print("You have 60 seconds to scan the QR code...")

        try:
            # Wait for WhatsApp to fully load (check for the main panel)
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="pane-side"]'))
            )
            print("WhatsApp Web loaded successfully!")
            time.sleep(3)

        except Exception as e:
            print(f"Failed to load WhatsApp: {e}")
            print("Please make sure you scan the QR code within 60 seconds")

    def take_screenshot(self, filename="whatsapp_screenshot.png"):
        """Take screenshot of WhatsApp Web"""
        try:
            # Ensure the window is properly sized
            self.driver.set_window_size(1200, 800)
            time.sleep(2)  # Wait for resize

            self.driver.save_screenshot(filename)
            print(f"Screenshot saved as {filename}")
            return filename
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None

    def check_new_messages(self):
        """Check if there are new messages and take screenshot"""
        try:
            # Method 1: Look for green unread badges (more reliable)
            unread_indicators = self.driver.find_elements(By.XPATH,
                                                          '//div[contains(@class, "chat")]//span[contains(@class, "unread-count")] | '
                                                          '//div[contains(@class, "chat")]//span[contains(@class, "p3-")]'
                                                          )

            # Method 2: Look for any active chat with messages
            active_chats = self.driver.find_elements(By.XPATH,
                                                     '//div[contains(@class, "chat")][contains(@class, "active")] | '
                                                     '//div[contains(@class, "message-in")] | '
                                                     '//div[contains(@class, "message-out")]'
                                                     )

            print(f"Found {len(unread_indicators)} unread indicators")
            print(f"Found {len(active_chats)} active chat elements")

            # If we found any indicators OR there are active chats, take screenshot
            if unread_indicators or active_chats:
                print("Messages detected! Taking screenshot...")
                return True
            else:
                print("No messages detected in current view.")
                return False

        except Exception as e:
            print(f"Error checking for new messages: {e}")
            # Even if detection fails, take screenshot to be safe
            return True

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()