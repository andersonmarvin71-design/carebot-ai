# ******************************************
# 🚀 CareBot AI - Standard Edition
# 👨‍💻 Created by: Monu Patel
# 🛠️ Status: High Stability Mode
# ******************************************

import os
import requests
import time
from flask import Flask, request

app = Flask(__name__)

# Config
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_reply(user_text):
    # ✅ बैकअप मॉडल्स की लिस्ट
    models = ["gemini-1.5-flash", "gemini-pro", "gemini-flash-latest"]
    
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": f"You are a health assistant created by Monu Patel. Answer this: {user_text}"}]}]
        }
        
        try:
            # Timeout को 60 सेकंड किया ताकि 'High Demand' के समय भी मौका मिले
            response = requests.post(url, json=payload, timeout=60)
            result = response.json()
            
            if "candidates" in result and result["candidates"]:
                return result["candidates"][0]["content"]["parts"][0]["text"]
            
            # अगर एरर 'High Demand' वाला है, तो 1 सेकंड रुक कर अगला मॉडल ट्राई करो
            print(f"Model {model} busy, trying next...")
            time.sleep(1)
            
        except Exception as e:
            print(f"Connection failed for {model}: {e}")
            continue
            
    return "⏳ माफ़ी चाहता हूँ, Google के सभी सर्वर अभी बहुत बिजी हैं। कृपया कुछ मिनट बाद दोबारा कोशिश करें। मेहनत जारी है! - Monu"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text == "/start":
            reply = "👋 *नमस्ते! मैं CareBot AI हूँ।*\n\nमुझे *Monu Patel* ने आपकी मदद के लिए बनाया है। पूछिए अपना सवाल!"
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
    return "<h1>CareBot AI is Running!</h1><p>Designed by Monu Patel</p>", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
                
