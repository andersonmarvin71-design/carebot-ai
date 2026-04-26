# ******************************************
# CareBot AI - Telegram Health Assistant
# Created by: Monu Patel
# Date: 2026-04-26
# ******************************************

from flask import Flask, request
import requests
import os
import logging

# Flask setup
app = Flask(__name__)

# Logging setup (Errors dekhne ke liye)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔑 Render Environment Variables se keys lega
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_reply(user_text):
    """Gemini AI se response lene ka function"""
    if not GEMINI_API_KEY:
        return "❌ Gemini API Key is missing in Render settings."

    # ✅ Latest Gemini 1.5 Flash URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"You are CareBot, a helpful health assistant created by Monu Patel. Provide safe information. User query: {user_text}"}]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        result = response.json()
        
        # JSON se response nikalna
        if "candidates" in result and result["candidates"]:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            logger.error(f"AI Error: {result}")
            return "⚠️ AI अभी जवाब नहीं दे पा रहा है। कृपया दोबारा कोशिश करें।"
    except Exception as e:
        logger.error(f"Connection Error: {e}")
        return "❌ Connection Error. Please check logs."

@app.route("/", methods=["GET"])
def home():
    return "CareBot AI is Running Live!", 200

# ✅ Webhook Route - Isse 404 Error nahi aayega
@app.route(f"/{TOKEN}" if TOKEN else "/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            reply = "👋 *CareBot AI में आपका स्वागत है!*\n\nमैं Monu द्वारा बनाया गया एक हेल्थ असिस्टेंट हूँ। आप मुझसे सेहत से जुड़े सवाल पूछ सकते हैं।"
        else:
            reply = get_ai_reply(text)
        
        # Telegram ko message bhejna
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(telegram_url, json={
            "chat_id": chat_id, 
            "text": reply,
            "parse_mode": "Markdown"
        })
    
    return "ok", 200

if __name__ == "__main__":
    # Render automatically PORT assign karta hai
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
