# *******************************************************
# 🤖 CAREBOT AI: TEXT-ONLY FINAL (RECTIFIED)
# 👑 DEVELOPED BY: MONU PATEL (INDORE)
# 🛠️ SYSTEM: GEMINI 1.5 FLASH + FLASK
# *******************************************************

import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- 1. Configuration (Environment Variables) ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- 2. AI Logic ---

def get_ai_reply(user_text):
    # Branding logic
    user_query = user_text.lower()
    if any(word in user_query for word in ["monu patel", "maker", "owner"]):
        return "👑 *Monu Patel* ek AI Chatbot Automation Expert hain Indore se! Unhone hi mujhe ye advanced powers di hain."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": user_text}]
        }]
    }
    
    try:
        res = requests.post(url, json=payload, timeout=25)
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Error: {e}")
    
    return "⏳ Maafi, abhi main samajh nahi paa raha hoon. Monu Patel ise jald thik karenge!"

# --- 3. Webhook Logic ---

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return "ok", 200
    
    chat_id = data["message"]["chat"]["id"]
    
    # Process only Text Messages
    if "text" in data["message"]:
        text = data["message"]["text"]
        
        if text == "/start":
            reply = "👋 *Namaste! Main CareBot AI hoon.*\n\nMain sirf Text messages samajhta hoon. Mujhe **Monu Patel** ne banaya hai! 🚀"
        else:
            reply = get_ai_reply(text)

        # Send Reply
        final_text = f"{reply}\n\n✨ _By Monu Patel AI_"
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                     json={"chat_id": chat_id, "text": final_text, "parse_mode": "Markdown"})
    
    return "ok", 200

@app.route("/")
def home():
    return "🚀 CareBot Text-Only Mode is Live!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
