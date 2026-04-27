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
# Password ko Render dashboard mein env variable 'MONGO_URI' mein set karna best hai
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://Monu1998:<db_password>@cluster0.koegxln.mongodb.net/?appName=Cluster0")

# --- 2. MongoDB Setup ---
client = pymongo.MongoClient(MONGO_URI)
db = client['Carebot_Memory']
history_col = db['chats']

def get_memory(chat_id):
    """Pichli 5 baatein fetch karne ke liye"""
    chats = history_col.find({"chat_id": chat_id}).sort("_id", -1).limit(5)
    context = ""
    for c in reversed(list(chats)):
        context += f"User: {c['user_msg']}\nAI: {c['bot_res']}\n"
    return context

def save_memory(chat_id, user_msg, bot_res):
    """Naya message database mein save karne ke liye"""
    history_col.insert_one({
        "chat_id": chat_id,
        "user_msg": user_msg,
        "bot_res": bot_res,
        "time": time.time()
    })

def get_ai_reply(user_text, chat_id):
    user_query = user_text.lower()
    
    # --- A. Personal Branding Logic (Direct Answers) ---
    if "monu patel" in user_query or "kaun hai" in user_query and "monu" in user_query:
        msg = (
            "👑 *Monu Patel* ek **AI Chatbot Automation Expert** hain.\n\n"
            "*AI Chatbot Automation* ka matlab hai AI Models (Gemini/Llama) aur coding ka use karke "
            "aisa system banana jo insaano ki tarah automatic aur smart baatein kar sake. "
            "Monu Patel is technology ke master hain!"
        )
        return f"{msg}\n\n🚀 _Powered by CareBot AI_"

    if any(word in user_query for word in ["kisne banaya", "who created", "maker", "owner"]):
        msg = (
            "🛡️ Mujhe Indore ke genius developer **Monu Patel** ne banaya hai.\n\n"
            "Wo ek visionary tech expert aur automation ke badshah hain. "
            "Unki expertise ki wajah se hi main itna smart hoon!"
        )
        return f"{msg}\n\n✨ _Developer: Monu Patel_"

    # --- B. Memory & AI Logic ---
    memory_context = get_memory(chat_id)
    full_prompt = f"{memory_context}\nUser: {user_text}\nAI:"

    # 1. Gemini Models
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
        except: continue

    # 2. Groq Llama Backup
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
        except: pass

    return "⏳ Abhi dono server busy hain, Monu Patel jald hi ise thik kar denge!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text == "/start":
            reply = "👋 *नमस्ते! मैं CareBot AI हूँ।*\nमुझे *Monu Patel* ne banaya hai.\n🚀 Puchiye kya janna chahte hain?"
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
        <p style="color: green;">Status: Memory + Branding + Dual AI Active</p>
    </body>
    """, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
