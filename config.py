import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API Config
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# WhatsApp Config
WHATSAPP_WEB_URL = "https://web.whatsapp.com"
SCREENSHOT_INTERVAL = 15  # seconds

# Make sure your .env file has:
# GEMINI_API_KEY=your_actual_gemini_api_key_here