"""
╔════════════════════════════════════════════════════════════════╗
║         CareBot AI - Telegram Health Assistant                 ║
║  Created by: Monu                                              ║
║  Date: 2026-04-26                                              ║
╚════════════════════════════════════════════════════════════════╝
"""

from flask import Flask, request
import requests
import os
import logging
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = Flask(__name__)

# 🔑 Configuration (Render Environment Variables से लेगा)
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 📩 Telegram Message भेजने का फंक्शन
def send_message(chat_id, text):
    if not text:
        return False
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": text, 
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Telegram Error: {e}")
        return False
# 🤖 Gemini AI से जवाब लेने का फंक्शन
def get_ai_reply(user_text):
    if not GEMINI_API_KEY:
        return "❌ API Key Missing in Render"

    # ✅ सही और लेटेस्ट Gemini URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": user_text}]}]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        result = response.json()
        
        if "candidates" in result and result["candidates"]:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        
        return "⚠️ AI अभी जवाब नहीं दे पा रहा है। कृपया दोबारा कोशिश करें।"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"
        
                return "⚠️ सुरक्षा कारणों से मैं इस सवाल का जवाब नहीं दे सकता।"
        
        logger.error(f"AI Empty Response: {result}")
        return "⚠️ AI अभी जवाब नहीं दे पा रहा है। कृपया दोबारा कोशिश करें।"

    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return "❌ AI सर्वर से संपर्क नहीं हो पाया।"

# 🔗 Webhook Handler
@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return "ok", 200
        
        message = data["message"]
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "").strip()

        if not chat_id or not text:
            return "ok", 200

        # Commands handling
        if text == "/start":
            reply = "👋 *CareBot AI में आपका स्वागत है!*\nमैं Monu द्वारा बनाया गया एक हेल्थ असिस्टेंट हूँ। आप मुझसे सेहत से जुड़े सवाल पूछ सकते हैं।"
        elif text == "/help":
            reply = "बस अपना सवाल टाइप करें, जैसे: 'वजन कैसे घटाएं?'"
        else:
            # Get AI response
            reply = get_ai_reply(text)
        
        send_message(chat_id, reply)
        return "ok", 200

    except Exception as e:
        logger.error(f"Webhook Error: {e}")
        return "ok", 200

@app.route("/")
def home():
    return "🚀 CareBot AI is Running Live!", 200

if __name__ == "__main__":
    # Render के लिए पोर्ट सेट करना
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
