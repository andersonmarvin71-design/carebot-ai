# *******************************************************
# 🚀 CareBot AI - THE UNSTOPPABLE EDITION
# 👑 DEVELOPER: MONU PATEL (INDORE)
# 🛠️ FEATURES: GOOGLE + GROQ DUAL-SERVER BACKUP
# *******************************************************

import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Config
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_ai_reply(user_text):
    # --- STEP 1: GOOGLE GEMINI (Primary) ---
    gemini_models = ["gemini-1.5-flash", "gemini-pro"]
    for model in gemini_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": user_text}]}]}
        try:
            res = requests.post(url, json=payload, timeout=10)
            data = res.json()
            if "candidates" in data:
                ai_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return f"{ai_text}\n\n✨ _Answered by CareBot AI (Created by Monu Patel)_"
        except:
            continue

    # --- STEP 2: GROQ LLAMA 3 (Super Backup) ---
    if GROQ_API_KEY:
        url_groq = "https://api.groq.com/openai/v1/chat/completions"
        headers_groq = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload_groq = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": user_text}]
        }
        try:
            res_groq = requests.post(url_groq, json=payload_groq, headers=headers_groq, timeout=10)
            data_groq = res_groq.json()
            if "choices" in data_groq:
                ai_text = data_groq["choices"][0]["message"]["content"]
                return f"{ai_text}\n\n🔥 _Answered by Backup Server (Created by Monu Patel)_"
        except:
            pass

    return "⏳ सारे सर्वर्स बिजी हैं। गूगल और लामा दोनों थक गए हैं पर Monu Patel हार नहीं मानेगा! फिर से ट्राई करें।"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text == "/start":
            reply = "👋 *नमस्ते! मैं CareBot AI हूँ।*\n\nमुझे *Monu Patel* ने आपकी हेल्थ और फिटनेस में मदद के लिए बनाया है। पूछिए क्या पूछना है?"
        else:
            reply = get_ai_reply(text)
            
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"})
    return "ok", 200

@app.route("/")
def home():
    return "<h1>CareBot Multi-Server is Running!</h1><h2>Designed & Developed by Monu Patel</h2>", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
            
