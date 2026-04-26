import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_reply(user_text):
    # ✅ यह URL सीधा 'gemini-1.5-flash' पर निशाना साधेगा, सबसे लेटेस्ट तरीके से
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": user_text}]}]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        result = response.json()
        
        if "candidates" in result:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        
        # अगर फिर भी एरर आये, तो साफ़ बताएगा क्या दिक्कत है
        return f"❌ Google Says: {result.get('error', {}).get('message', 'Unknown Error')}"
    except Exception as e:
        return f"⚠️ Connection Problem: {str(e)}"

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
    return "Bot is Running", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
            
