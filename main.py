# ******************************************
# 🚀 CareBot AI - Telegram Health Assistant
# 👨‍डिंग: Monu Patel
# 📅 Date: 2026-04-26
# ******************************************

import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Config - Render Environment Variables
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_reply(user_text):
    # ✅ आपके cURL के हिसाब से एकदम सही URL और मॉडल नाम
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': GEMINI_API_KEY
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": f"You are a health assistant created by Monu Patel. User says: {user_text}"}]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        if "candidates" in result:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        
        return f"❌ AI Error: {result.get('error', {}).get('message', 'Check API Key')}"
    except Exception as e:
        return f"⚠️ Connection Error: {str(e)}"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text == "/start":
            reply = "👋 *नमस्ते! मैं CareBot AI हूँ।*\n\nमुझे *Monu Patel* ने आपकी सेहत का ख्याल रखने के लिए बनाया है। आप मुझसे कोई भी हेल्थ सवाल पूछ सकते हैं।"
        else:
            reply = get_ai_reply(text)
            
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={
                          "chat_id": chat_id, 
                          "text": reply,
                          "parse_mode": "Markdown"
                      })
    return "ok", 200

@app.route("/")
def home():
    return f"<h1>CareBot AI is Live!</h1><p>Created by: Monu Patel</p>", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    
