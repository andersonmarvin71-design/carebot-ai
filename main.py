# ******************************************
# CareBot AI - Telegram Health Assistant
# Created by: Monu Patel
# ******************************************

import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Config - Render Environment Variables
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_reply(user_text):
    # ✅ यह URL का सबसे लेटेस्ट वर्जन है
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": user_text}]}]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        result = response.json()
        
        # अगर जवाब मिल गया
        if "candidates" in result and result["candidates"]:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        
        # अगर कोई एरर आये तो असली वजह बताएगा
        error_info = result.get('error', {}).get('message', 'Unknown Error')
        return f"⚠️ AI Error: {error_info}"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text == "/start":
            reply = "👋 CareBot AI Live! मैं Monu द्वारा बनाया गया आपका हेल्थ दोस्त हूँ।"
        else:
            reply = get_ai_reply(text)
            
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": chat_id, "text": reply})
    return "ok", 200

@app.route("/")
def home():
    return "CareBot is Running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
