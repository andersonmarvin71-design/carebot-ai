"""
╔════════════════════════════════════════════════════════════════╗
║         CareBot AI - Telegram Health Assistant                 ║
║                                                                ║
║  Created by: Monu                                              ║
║  Date: 2026-04-26                                              ║
║  Description: A Telegram chatbot powered by Google Gemini AI   ║
╚════════════════════════════════════════════════════════════════╝
"""

from flask import Flask, request
import requests
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# 🔑 Configuration - Fixed to look up key names, not values
TOKEN = os.getenv("8618597269:AAGuVOwLmesBYZ2OazaQId0SNm_gwowGs6I")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ⚙️ Validation
if not TOKEN or not GEMINI_API_KEY:
    print("❌ ERROR: TELEGRAM_TOKEN or GEMINI_API_KEY is missing in .env")
    exit(1)

# 📊 Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 📩 Send Telegram Message
def send_message(chat_id, text):
    if not text:
        return False
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    # Telegram has a 4096 character limit. This crops it just in case.
    if len(text) > 4000:
        text = text[:4000] + "..."

    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"❌ Telegram Send Error: {e}")
        # Fallback without Markdown if parsing fails
        requests.post(url, json={"chat_id": chat_id, "text": text})
        return False

# 🤖 Get AI Reply from Gemini
def get_ai_reply(user_text):
    if not user_text.strip():
        return "📝 Please send a health-related question."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # System Instruction to keep it safe and concise
    prompt = (
        "You are CareBot, a helpful health assistant. Provide safe, concise health info. "
        "Disclaimer: You are not a doctor. User asked: " + user_text
    )
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        
        # Robust parsing for Gemini response structure
        if "candidates" in result and result["candidates"]:
            candidate = result["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                return candidate["content"]["parts"][0]["text"]
            elif candidate.get("finishReason") == "SAFETY":
                return "⚠️ This query was flagged by safety filters. I can only provide general health information."
        
        return "⚠️ I'm having trouble thinking right now. Please try again."

    except Exception as e:
        logger.error(f"❌ Gemini API Error: {e}")
        return "❌ Sorry, I'm currently unable to connect to my AI brain."

# 🔗 Telegram Webhook Handler
@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return "ok", 200
    
    message = data["message"]
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if not chat_id or not text:
        return "ok", 200

    logger.info(f"📨 Msg from {chat_id}: {text}")

    # Commands
    if text.startswith("/start"):
        reply = "👋 *Welcome to CareBot AI!*\n\nAsk me about fitness, nutrition, or wellness.\n\n_Note: I am an AI, not a doctor._"
    elif text.startswith("/help"):
        reply = "Ask me things like: 'How to improve sleep?' or 'Healthy breakfast ideas'."
    else:
        reply = get_ai_reply(text)

    send_message(chat_id, reply)
    return "ok", 200

@app.route("/", methods=["GET"])
def index():
    return f"CareBot AI is Active. Webhook: /{TOKEN[:10]}...", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
