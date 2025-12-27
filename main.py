from whatsapp_scraper import WhatsAppScraper
from message_analyzer import MessageAnalyzer
from message_tracker import MessageTracker
from config import SCREENSHOT_INTERVAL
import time
import os


def main():
    print("🚀 ENHANCED WhatsApp Filter")
    print("📱 Now enters chats to capture FULL message content!")
    print("💡 Will detect ALL important messages, not just previews!\n")

    scraper = None
    try:
        scraper = WhatsAppScraper()
        analyzer = MessageAnalyzer()
        tracker = MessageTracker()

        print("🔍 Scanning for unread chats...")

        # NEW: Enter each unread chat and capture screenshots
        screenshot_paths = scraper.capture_all_unread_chats()

        if not screenshot_paths:
            print("🎉 No unread chats found! You're all caught up.")
            return

        all_important_messages = []

        # Analyze each chat screenshot
        for screenshot_path in screenshot_paths:
            if os.path.exists(screenshot_path):
                print(f"🤖 Analyzing chat: {screenshot_path}")
                result = analyzer.analyze_screenshot(screenshot_path)

                important_messages = result.get("important_messages", [])
                new_messages = tracker.filter_new_messages(important_messages)
                all_important_messages.extend(new_messages)

                # Clean up screenshot
                try:
                    os.remove(screenshot_path)
                    print(f"🗑️ Cleaned up: {screenshot_path}")
                except:
                    pass

        # Show all results
        if all_important_messages:
            print(f"\n🚨 IMPORTANT MESSAGES FOUND: {len(all_important_messages)}")
            print("=" * 60)
            for i, msg in enumerate(all_important_messages, 1):
                print(f"\n{i}. 📨 From: {msg.get('sender', 'Unknown')}")
                print(f"   💬 Message: {msg.get('message', 'No content')}")
                print(f"   📋 Reason: {msg.get('reason', 'Not specified')}")
            print("=" * 60)
            print("✅ Scan complete! Found ALL important messages from full chat history.")
        else:
            print("✅ No important messages found in any unread chats.")

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