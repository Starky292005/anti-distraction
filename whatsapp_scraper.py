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
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        self.driver.get("https://web.whatsapp.com")

        print("Please scan QR code and wait for WhatsApp Web to load...")
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="pane-side"]'))
            )
            print("WhatsApp Web loaded successfully!")
            time.sleep(3)
        except Exception as e:
            print(f"Failed to load WhatsApp: {e}")

    def get_unread_chats(self):
        """Get list of chats with unread messages using multiple detection methods"""
        try:
            unread_chats = []

            # Method 1: Look for unread count badges (most reliable)
            unread_selectors = [
                '//div[@role="listitem"]//span[contains(@aria-label, "unread")]',
                '//div[contains(@class, "chat")]//span[contains(@data-testid, "icon-unread")]',
                '//div[@role="listitem"][.//*[contains(text(), "unread")]]',
            ]

            for selector in unread_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        # Get the chat name from parent
                        chat_element = element.find_element(By.XPATH, './ancestor::div[@role="listitem"]')
                        chat_name_element = chat_element.find_elements(By.XPATH,
                                                                       './/span[@dir="auto"] | .//div[contains(@class, "chat-title")]')
                        if chat_name_element:
                            chat_name = chat_name_element[0].text.strip()
                            if chat_name and chat_name not in unread_chats:
                                unread_chats.append(chat_name)
                                print(f"🔔 Found unread chat: {chat_name}")
                except Exception as e:
                    continue

            # Method 2: Look for visual indicators (green background, bold text)
            if not unread_chats:
                print("🔄 Trying visual detection...")
                all_chats = self.driver.find_elements(By.XPATH, '//div[@role="listitem"]')
                for chat in all_chats:
                    try:
                        # Check if chat looks "unread" (different background, bold, etc.)
                        chat_style = chat.get_attribute("style") or ""
                        chat_class = chat.get_attribute("class") or ""

                        # Look for visual cues of unread messages
                        if "unread" in chat_class.lower() or "active" in chat_class.lower():
                            chat_name_element = chat.find_elements(By.XPATH,
                                                                   './/span[@dir="auto"] | .//div[contains(@class, "chat-title")]')
                            if chat_name_element:
                                chat_name = chat_name_element[0].text.strip()
                                if chat_name and chat_name not in unread_chats:
                                    unread_chats.append(chat_name)
                                    print(f"👀 Visually detected unread chat: {chat_name}")
                    except:
                        continue

            return unread_chats

        except Exception as e:
            print(f"Error finding unread chats: {e}")
            return []

    def enter_chat_and_capture(self, chat_name):
        """Enter a specific chat and capture all messages"""
        try:
            print(f"🚀 Entering chat: {chat_name}")

            # Find and click on the chat (multiple selector strategies)
            selectors = [
                f'//span[@dir="auto"][contains(text(), "{chat_name}")]',
                f'//div[contains(@class, "chat-title")][contains(text(), "{chat_name}")]',
                f'//span[contains(text(), "{chat_name}")]'
            ]

            chat_element = None
            for selector in selectors:
                try:
                    chat_element = self.driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue

            if not chat_element:
                print(f"❌ Could not find chat: {chat_name}")
                return None

            chat_element.click()
            print(f"✅ Clicked on chat: {chat_name}")

            # Wait for chat to load
            time.sleep(3)

            # Scroll to load more messages
            self.scroll_chat_for_messages()

            # Take screenshot of the full chat
            safe_chat_name = "".join(c for c in chat_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            screenshot_path = f"chat_{safe_chat_name}.png"
            return self.take_screenshot(screenshot_path)

        except Exception as e:
            print(f"❌ Failed to enter chat {chat_name}: {e}")
            return None

    def scroll_chat_for_messages(self):
        """Scroll up in chat to load more message history"""
        try:
            # Find the main message area
            message_selectors = [
                '//div[@role="application"]',
                '//div[contains(@class, "message-list")]',
                '//div[contains(@class, "copyable-area")]',
                '//div[@id="main"]'
            ]

            message_container = None
            for selector in message_selectors:
                try:
                    message_container = self.driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue

            if message_container:
                # Scroll up to load more messages
                for i in range(3):
                    self.driver.execute_script("arguments[0].scrollTop = 0", message_container)
                    print(f"📜 Scrolling to load more messages... ({i + 1}/3)")
                    time.sleep(2)
            else:
                print("ℹ️  Could not find message container for scrolling")

        except Exception as e:
            print(f"Note: Could not scroll chat: {e}")

    def capture_all_unread_chats(self):
        """Enter each unread chat and capture screenshots"""
        unread_chats = self.get_unread_chats()
        screenshot_paths = []

        if not unread_chats:
            print("📭 No unread chats found")
            # Fallback: Take screenshot of main view anyway
            print("🔄 Taking screenshot of main view as fallback...")
            screenshot_path = self.take_screenshot("whatsapp_main_view.png")
            if screenshot_path:
                screenshot_paths.append(screenshot_path)
            return screenshot_paths

        print(f"🔍 Found {len(unread_chats)} unread chats: {unread_chats}")

        for chat in unread_chats:
            screenshot_path = self.enter_chat_and_capture(chat)
            if screenshot_path:
                screenshot_paths.append(screenshot_path)
            # Small delay between chats
            time.sleep(2)

        return screenshot_paths

    def take_screenshot(self, filename="whatsapp_screenshot.png"):
        """Take screenshot of current view"""
        try:
            self.driver.set_window_size(1200, 800)
            time.sleep(2)
            self.driver.save_screenshot(filename)
            print(f"📸 Screenshot saved: {filename}")
            return filename
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()