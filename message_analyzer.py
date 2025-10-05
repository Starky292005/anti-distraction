import google.generativeai as genai
import base64
from config import GEMINI_API_KEY
import json
import time
import PIL.Image


class MessageAnalyzer:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        # Use the working model from your available list
        self.model = genai.GenerativeModel('models/gemini-2.0-flash')
        print("✅ Using model: gemini-2.0-flash")

    def analyze_screenshot(self, screenshot_path):
        """Analyze WhatsApp screenshot using Gemini"""
        try:
            print(f"Analyzing screenshot: {screenshot_path}")

            # Load image using PIL
            image = PIL.Image.open(screenshot_path)

            prompt = """
            Analyze this WhatsApp screenshot and extract ONLY formal/important messages. 

            IMPORTANT: Focus on messages that contain:
            - Work, job, or professional content
            - Meetings, appointments, schedules
            - Deadlines, urgent matters, time-sensitive info
            - Important announcements or official communications
            - Project-related discussions
            - Business or formal invitations

            IGNORE:
            - Casual chats like "hello", "hey", "wassup", "what's up"
            - Personal conversations about hanging out
            - Informal greetings without important content
            - Random casual messages

            Return ONLY a JSON response with this exact format:
            {
                "important_messages": [
                    {
                        "sender": "sender name or number",
                        "message": "exact message content", 
                        "reason": "brief explanation why this is important"
                    }
                ]
            }

            If no important messages found, return: {"important_messages": []}
            """

            # Generate content with image
            response = self.model.generate_content([prompt, image])

            print("Gemini Response received:")
            print(response.text)

            return self._parse_response(response.text)

        except Exception as e:
            print(f"Error analyzing screenshot: {e}")
            return {"important_messages": []}

    def _parse_response(self, response_text):
        """Parse Gemini response to extract JSON"""
        try:
            print("Parsing Gemini response...")

            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                print(f"Extracted JSON: {json_str}")
                return json.loads(json_str)
            else:
                print("No JSON found in response, returning empty")
                return {"important_messages": []}

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Raw response: {response_text}")
            return {"important_messages": []}