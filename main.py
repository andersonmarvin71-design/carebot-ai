# *******************************************************
# 🤖 CAREBOT AI: TEXT + MEMORY (STABILIZED)
# 👑 DEVELOPED BY: MONU PATEL (INDORE)
# 🛠️ SYSTEM: GEMINI 1.5 FLASH + MONGODB
# *******************************************************

import os
import requests
import pymongo
from flask import Flask, request

app = Flask(__name__)

# --- 1. Configuration ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# --- 2. MongoDB Setup ---
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client['Carebot_Memory']
    history_col = db['chats']
except Exception as e:
    print(f"MongoDB Connection Error: {e}")

# --- 3. AI Logic with Memory ---

def get_ai_reply(user_text, chat_id):
    # Branding Logic
    user_query = user_text.lower()
    if any(word in user_query for word in ["monu patel", "maker", "owner"]):
        return "👑 *Monu Patel* ek AI Chatbot Automation Expert hain Indore se! Unhone hi mujhe ye advanced powers di hain."

    # Fetch History from MongoDB (Last 10 messages for context)
    chat_history = []
    try:
        user_data = history_col.find_one({"chat_id": chat_id})
        if user_data:
            chat_history = user_data.get("messages", [])[-10:] # Keep context lean
    except:
        pass

    # Build Gemini Payload with History
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    contents = []
    # Add historical context to the prompt
    for msg in chat_history:
        contents.append({"role": msg["role"], "parts": [{"text": msg["text"]}]})
    
    # Add current user message
    contents.append({"role": "user", "parts": [{"text": user_text}]})

    payload = {"contents": contents}
    
    try:
        res = requests.post(url, json=payload, timeout=25)
        if res.status_code == 200:
            bot_response = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            
            # Save new exchange to MongoDB
            history_col.update_one(
                {"chat_id": chat_id},
                {"$push": {"messages": {"$each": [
                    {"role": "user", "text": user_text},
                    {"role": "model", "text": bot_response}
                ]}}},
                upsert=True
            )
            return bot_response
    except Exception as e:
        print(f"Gemini Error: {e}")
    
    return "⏳ Maafi, abhi main samajh nahi paa raha hoon. Monu Patel ise jald thik karenge!"

# --- 4. Webhook Logic ---

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return "ok", 200
    
    chat_id = data["message"]["chat"]["id"]
    
    if "text" in data["message"]:
        text = data["message"]["text"]
        
        if text == "/start":
            # Clear history on /start to reset conversation
            history_col.delete_one({"chat_id": chat_id})
            reply = "👋 *Namaste! Main CareBot AI hoon.*\n\nMain aapki purani baatein yaad rakh sakta hoon! Mujhe **Monu Patel** ne banaya hai. 🚀"
        else:
            reply = get_ai_reply(text, chat_id)

        # Send Reply
        final_text = f"{reply}\n\n✨ _By Monu Patel AI_"
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                     json={"chat_id": chat_id, "text": final_text, "parse_mode": "Markdown"})
    
    return "ok", 200

@app.route("/")
def home():
    return "🚀 CareBot Memory Mode is Live!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
        
