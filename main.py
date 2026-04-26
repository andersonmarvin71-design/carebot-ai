import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Config
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_reply(user_text):
    # ✅ यह URL का सबसे सटीक तरीका है (Google Standard)
    base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    full_url = f"{base_url}?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": user_text}]}]
    }
    
    try:
        response = requests.post(full_url, json=payload, timeout=15)
        result = response.json()
        
        # अगर मॉडल मिल गया
        if "candidates" in result:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        
        # अगर अभी भी 404 आ रहा है, तो error message दिखाओ
        return f"⚠️ AI Error: {result.get('error', {}).get('message', 'Unknown Error')}"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

@app.route(f"/{TOKEN}" if TOKEN else "/bot", methods=["POST"])
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
    return "Bot is Running", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
            
