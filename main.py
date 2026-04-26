# *******************************************************
# 🚀 CAREBOT AI - THE ULTIMATE EDITION
# 👑 DEVELOPED BY: MONU PATEL (INDORE)
# 🛠️ SYSTEM: DUAL-ENGINE AI (GOOGLE GEMINI + GROQ LLAMA)
# *******************************************************

import os
import requests
import time
from flask import Flask, request

app = Flask(__name__)

# --- Configuration (Environment Variables से डेटा लेगा) ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_ai_reply(user_text):
    # 1. पहले Google Gemini मॉडल्स को ट्राई करेंगे
    gemini_models = ["gemini-1.5-flash", "gemini-pro"]
    
    for model in gemini_models:
        if not GEMINI_API_KEY: break
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": user_text}]}]}
        
        try:
            res = requests.post(url, json=payload, timeout=12)
            if res.status_code == 200:
                data = res.json()
                ai_response = data["candidates"][0]["content"]["parts"][0]["text"]
                return f"{ai_response}\n\n✨ _Answered by CareBot AI (Monu Patel)_"
        except:
            continue # अगर एक मॉडल फेल हुआ, तो अगले पर जाओ

    # 2. अगर Google के दोनों मॉडल फेल हुए, तो Groq Llama 3 ट्राई करेंगे
    if GROQ_API_KEY:
        url_groq = "https://api.groq.com/openai/v1/chat/completions"
        headers_groq = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload_groq = {
            "model": "llama-3.3-70b-versatile", # लेटेस्ट स्टेबल मॉडल
            "messages": [{"role": "user", "content": user_text}]
        }
        
        try:
            # Groq बहुत तेज़ है, इसे 15 सेकंड का समय देते हैं
            res_groq = requests.post(url_groq, json=payload_groq, headers=headers_groq, timeout=15)
            if res_groq.status_code == 200:
                data_groq = res_groq.json()
                ai_response = data_groq["choices"][0]["message"]["content"]
                return f"{ai_response}\n\n🔥 _Answered by Backup Server (Monu Patel)_"
        except:
            pass

    # 3. अगर सब कुछ फेल हो गया
    return "⏳ माफ़ी चाहता हूँ, गूगल और लामा दोनों अभी बिजी हैं। पर Monu Patel हार नहीं मानेगा! कृपया कुछ देर बाद फिर से ट्राई करें।"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        # /start कमांड के लिए स्पेशल वेलकम मैसेज
        if text == "/start":
            reply = (
                "👋 *नमस्ते! मैं CareBot AI हूँ।*\n\n"
                "मुझे *Monu Patel* ने आपकी सेहत और फिटनेस से जुड़े सवालों "
                "के जवाब देने के लिए बनाया है।\n\n"
                "🚀 आप मुझसे कोई भी सवाल पूछ सकते हैं!"
            )
        else:
            reply = get_ai_reply(text)
            
        # Telegram को मैसेज भेजना
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
            json={
                "chat_id": chat_id, 
                "text": reply, 
                "parse_mode": "Markdown"
            }
        )
    return "ok", 200

@app.route("/")
def home():
    # Render के होमपेज पर आपकी शान बढ़ेगी
    return """
    <body style="font-family: Arial; text-align: center; padding: 50px; background-color: #f4f4f4;">
        <h1 style="color: #2c3e50;">🚀 CareBot AI is Running Live!</h1>
        <p style="font-size: 20px;">Designed & Developed by <b>Monu Patel</b></p>
        <p style="color: green;">Status: Google + Groq Dual Support Enabled</p>
    </body>
    """, 200

if __name__ == "__main__":
    # Render के लिए पोर्ट सेटिंग
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
        
