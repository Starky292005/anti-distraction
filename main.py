from whatsapp_scraper import WhatsAppScraper
from message_analyzer import MessageAnalyzer
from config import SCREENSHOT_INTERVAL
import time
import os


def main():
    print("Starting Anti-Distraction WhatsApp Filter...")
    print("This app will check for new WhatsApp messages and filter important ones.")
    print("Make sure to keep the Chrome window open and don't close it.\n")

    scraper = None
    try:
        scraper = WhatsAppScraper()
        analyzer = MessageAnalyzer()

        check_count = 0

        while True:
            check_count += 1
            print(f"\n--- Check #{check_count} at {time.strftime('%H:%M:%S')} ---")

            # For testing: ALWAYS take screenshot regardless of detection
            print("Taking screenshot for analysis...")
            screenshot_path = scraper.take_screenshot()

            if screenshot_path and os.path.exists(screenshot_path):
                # Analyze for important messages
                print("Analyzing messages with Gemini...")
                result = analyzer.analyze_screenshot(screenshot_path)

                # Display important messages
                important_messages = result.get("important_messages", [])

                if important_messages:
                    print(f"\n🚨 IMPORTANT MESSAGES FOUND: {len(important_messages)}")
                    for i, msg in enumerate(important_messages, 1):
                        print(f"\n{i}. From: {msg.get('sender', 'Unknown')}")
                        print(f"   Message: {msg.get('message', 'No content')}")
                        print(f"   Reason: {msg.get('reason', 'Not specified')}")
                    print("-" * 50)
                else:
                    print("No important messages found. You can focus! ✅")

                # Clean up screenshot
                try:
                    os.remove(screenshot_path)
                    print("Cleaned up screenshot")
                except:
                    pass
            else:
                print("Failed to take screenshot")

            print(f"Waiting {SCREENSHOT_INTERVAL} seconds for next check...")
            time.sleep(SCREENSHOT_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping application...")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your Gemini API key is correct in .env file")
    finally:
        if scraper:
            scraper.close()
            print("Browser closed.")


if __name__ == "__main__":
    main()