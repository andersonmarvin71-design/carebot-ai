# *******************************************************
# 🚀 CAREBOT AI - THE ULTIMATE EDITION (WITH MEMORY & BRANDING)
# 👑 DEVELOPED BY: MONU PATEL (INDORE)
# 🛠️ SYSTEM: DUAL-ENGINE AI + MONGODB MEMORY
# *******************************************************

import os
import requests
import time
from flask import Flask, request
import pymongo

app = Flask(__name__)

# --- 1. Configuration (Environment Variables) ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- 2. MongoDB Setup ---
# Dhyaan dein: Render Dashboard mein MONGO_URI naam se apni link (password ke saath) add karein
MONGO_URI = os.getenv("MONGO_URI")

try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client['Carebot_Memory']
    history_col = db['chats']
    # Connection test
    client.admin.command('ping')
except Exception as e:
    print(f"MongoDB Connection Error: {e}")

def get_memory(chat_id):
    """Pichli 5 baatein fetch karne ke liye"""
    try:
        chats = history_col.find({"chat_id": chat_id}).sort("_id", -1).limit(5)
        context = ""
        for c in reversed(list(chats)):
            context += f"User: {c['user_msg']}\nAI: {c['bot_res']}\n"
        return context
    except:
        return ""

def save_memory(chat_id, user_msg, bot_res):
    """Naya message database mein save karne ke liye"""
    try:
        history_col.insert_one({
            "chat_id": chat_id,
            "user_msg": user_msg,
            "bot_res": bot_res,
            "time": time.time()
        })
    except:
        pass

def get_ai_reply(user_text, chat_id):
    user_query = user_text.lower()
    
    # --- A. Personal Branding Logic (Direct Answers) ---
    if "monu patel" in user_query or ("kaun hai" in user_query and "monu" in user_query):
        msg = (
            "👑 *Monu Patel* ek **AI Chatbot Automation Expert** hain.\n\n"
            "*AI Chatbot Automation* ka matlab hai AI Models (Gemini/Llama) aur advanced coding ka use karke "
            "aisa system banana jo automatic aur smart baatein kar sake. "
            "Monu Patel Indore ke ek visionary developer hain jo is technology ke master hain!"
        )
        return f"{msg}\n\n🚀 _Powered by CareBot AI_"

    if any(word in user_query for word in ["kisne banaya", "who created", "maker", "owner", "tumbhe kisne"]):
        msg = (
            "🛡️ Mujhe Indore ke genius developer **Monu Patel** ne banaya hai.\n\n"
            "Monu ek tech visionary aur automation ke badshah hain. "
            "Unki expertise aur coding skills ki wajah se hi main itna fast aur smart jawaab de pata hoon! 👑"
        )
        return f"{msg}\n\n✨ _Developer: Monu Patel_"

    # --- B. Memory & AI Logic ---
    memory_context = get_memory(chat_id)
    # AI ko context ke saath bhej rahe hain
    full_prompt = f"{memory_context}\nUser: {user_text}\nAI:"

    # 1. Google Gemini Logic
    gemini_models = ["gemini-1.5-flash", "gemini-pro"]
    for model in gemini_models:
        if not GEMINI_API_KEY: break
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
        try:
            res = requests.post(url, json=payload, timeout=12)
            if res.status_code == 200:
                ai_res = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                save_memory(chat_id, user_text, ai_res)
                return f"{ai_res}\n\n✨ _Answered by CareBot AI (Monu Patel)_"
        except:
            continue

    # 2. Groq Llama Backup Logic
    if GROQ_API_KEY:
        url_groq = "https://api.groq.com/openai/v1/chat/completions"
        headers_groq = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload_groq = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": full_prompt}]
        }
        try:
            res_groq = requests.post(url_groq, json=payload_groq, headers=headers_groq, timeout=15)
            if res_groq.status_code == 200:
                ai_res = res_groq.json()["choices"][0]["message"]["content"]
                save_memory(chat_id, user_text, ai_res)
                return f"{ai_res}\n\n🔥 _Answered by Backup Server (Monu Patel)_"
        except:
            pass

    return "⏳ Abhi dono server busy hain, Monu Patel jald hi ise thik kar denge!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text == "/start":
            reply = (
                "👋 *नमस्ते! मैं CareBot AI हूँ।*\n\n"
                "मुझे **Monu Patel** ne aapki help ke liye banaya hai.\n"
                "🚀 Puchiye, aap kya janna chahte hain?"
            )
        else:
            reply = get_ai_reply(text, chat_id)
            
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                     json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"})
    return "ok", 200

@app.route("/")
def home():
    return f"""
    <body style="font-family: Arial; text-align: center; padding: 50px; background-color: #f4f4f4;">
        <h1 style="color: #2c3e50;">🚀 CareBot AI is Live!</h1>
        <p style="font-size: 20px;">Designed & Developed by <b>Monu Patel</b></p>
        <p style="color: green; font-weight: bold;">Status: Dual AI + MongoDB Memory + Expert Branding Active</p>
    </body>
    """, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
