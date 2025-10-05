import json
import os
import hashlib


class MessageTracker:
    def __init__(self, history_file="message_history.json"):
        self.history_file = history_file
        self.processed_messages = self.load_history()
        print(f"📚 Loaded {len(self.processed_messages)} previously seen messages")

    def load_history(self):
        """Load previously seen messages"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return set(data)
                    else:
                        return set()
            except Exception as e:
                print(f"❌ Error loading message history: {e}")
                return set()
        else:
            print("📝 No message history found. Starting fresh.")
            return set()

    def save_history(self):
        """Save seen messages to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(list(self.processed_messages), f, indent=2)
            print(f"💾 Saved {len(self.processed_messages)} messages to history")
        except Exception as e:
            print(f"❌ Error saving message history: {e}")

    def is_new_message(self, sender, message):
        """Check if this is a new message"""
        if not message or not sender:
            return False

        # Clean the message content
        clean_message = message.strip()
        if len(clean_message) < 5:  # Too short to be meaningful
            return False

        # Create a unique ID for the message (use first 50 chars to handle long messages)
        message_preview = clean_message[:50]
        message_id = f"{sender}:{message_preview}"
        message_hash = hashlib.md5(message_id.encode()).hexdigest()

        if message_hash in self.processed_messages:
            print(f"📭 Already seen: {sender}: {message_preview}...")
            return False

        # Add to processed messages
        self.processed_messages.add(message_hash)
        print(f"📬 New message: {sender}: {message_preview}...")
        return True

    def filter_new_messages(self, important_messages):
        """Filter out already seen messages"""
        if not important_messages:
            return []

        new_messages = []
        for msg in important_messages:
            sender = msg.get('sender', 'Unknown').strip()
            message_content = msg.get('message', '').strip()

            if self.is_new_message(sender, message_content):
                new_messages.append(msg)

        # Save after processing all messages
        if new_messages:
            self.save_history()

        return new_messages