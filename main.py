from whatsapp_scraper import WhatsAppScraper
from message_analyzer import MessageAnalyzer
from message_tracker import MessageTracker
from config import SCREENSHOT_INTERVAL
import time
import os


def main():
    print("🚀 Anti-Distraction WhatsApp Filter")
    print("📱 Monitoring for NEW important messages only")
    print("💡 Make sure to keep the Chrome window open!\n")

    scraper = None
    try:
        scraper = WhatsAppScraper()
        analyzer = MessageAnalyzer()
        tracker = MessageTracker()  # This should now persist between runs

        check_count = 0
        max_checks = 8

        while check_count < max_checks:
            check_count += 1
            print(f"\n--- Check #{check_count} at {time.strftime('%H:%M:%S')} ---")

            print("📸 Taking screenshot...")
            screenshot_path = scraper.take_screenshot()

            if screenshot_path and os.path.exists(screenshot_path):
                print("🤖 Analyzing with Gemini AI...")
                result = analyzer.analyze_screenshot(screenshot_path)

                important_messages = result.get("important_messages", [])
                new_messages = tracker.filter_new_messages(important_messages)

                if new_messages:
                    print(f"\n🚨 NEW IMPORTANT MESSAGES FOUND: {len(new_messages)}")
                    print("=" * 60)
                    for i, msg in enumerate(new_messages, 1):
                        print(f"\n{i}. 📨 From: {msg.get('sender', 'Unknown')}")
                        print(f"   💬 Message: {msg.get('message', 'No content')}")
                        print(f"   📋 Reason: {msg.get('reason', 'Not specified')}")
                    print("=" * 60)

                    print("✅ New important messages found! Stopping...")

                    # Clean up
                    try:
                        os.remove(screenshot_path)
                    except:
                        pass

                    break
                else:
                    if important_messages:
                        print("📝 All important messages were already seen previously.")
                    else:
                        print("✅ No important messages found. You can focus!")

                # Clean up screenshot
                try:
                    os.remove(screenshot_path)
                    print("🗑️ Cleaned up screenshot")
                except:
                    pass
            else:
                print("❌ Failed to take screenshot")

            if check_count < max_checks:
                print(f"⏰ Waiting {SCREENSHOT_INTERVAL} seconds...")
                time.sleep(SCREENSHOT_INTERVAL)
            else:
                print("📊 Reached check limit. Stopping...")
                break

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if scraper:
            scraper.close()
            print("🔒 Browser closed.")


if __name__ == "__main__":
    main()