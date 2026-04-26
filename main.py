"""
╔════════════════════════════════════════════════════════════════╗
║         CareBot AI - Telegram Health Assistant                 ║
║  Created by: Monu | Hosted on GitHub                           ║
╚════════════════════════════════════════════════════════════════╝
"""

from flask import Flask, request
import requests
import os
import logging
from dotenv import load_dotenv

# Local development के लिए .env लोड करेगा, Server पर environment variables लेगा
load_dotenv()

app = Flask(__name__)

# Config
TOKEN = os.getenv("8618597269:AAGuVOwLmesBYZ2OazaQId0SNm_gwowGs6I")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Error sending message: {e}")

def get_ai_reply(user_text):
    # Gemini 1.5 Flash is recommended for fast chatbot responses
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"You are CareBot, a friendly health assistant created by Monu. Provide safe, concise info. User: {user_text}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        result = response.json()
        if "candidates" in result and result["candidates"]:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        return "⚠️ I'm busy right now, please try again later."
    except Exception as e:
        return "❌ Connection error with AI."

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        msg = data["message"]
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "")

        if text == "/start":
            reply = "👋 *CareBot AI is Active!*\nCreated by Monu. How can I help you today?"
        else:
            reply = get_ai_reply(text)
        
        send_message(chat_id, reply)
    return "ok", 200

@app.route("/")
def home():
    return "CareBot is Online", 200

if __name__ == "__main__":
    # GitHub/Cloud Deployment के लिए Port dynamic होना चाहिए
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
