# *******************************************************
# 🤖 CAREBOT AI: MULTIMODAL FINAL (RECTIFIED)
# 👑 DEVELOPED BY: MONU PATEL (INDORE)
# 🛠️ SYSTEM: GEMINI 1.5 FLASH + GROQ WHISPER + MONGODB
# *******************************************************

import os
import requests
import time
import base64
from flask import Flask, request
import pymongo

app = Flask(__name__)

# --- 1. Configuration (Environment Variables) ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# --- 2. MongoDB Setup ---
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client['Carebot_Memory']
    history_col = db['chats']
except:
    pass

# --- 3. Helper Functions ---

def download_telegram_file(file_id):
    file_info = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}").json()
    file_path = file_info['result']['file_path']
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    local_filename = file_path.split('/')[-1]
    
    response = requests.get(file_url)
    with open(local_filename, "wb") as f:
        f.write(response.content)
    return local_filename

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def get_ai_reply(user_text, chat_id, image_path=None):
    # Branding logic
    user_query = user_text.lower() if user_text else ""
    if "monu patel" in user_query or "maker" in user_query:
        return "👑 *Monu Patel* ek AI Chatbot Automation Expert hain Indore se! Unhone hi mujhe ye advanced powers di hain."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt_text = user_text if user_text else "Is image ko detail mein samjhao."
    
    # Correct Multi-modal Payload
    parts = [{"text": prompt_text}]
    if image_path:
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": encode_image_to_base64(image_path)
            }
        })

    payload = {"contents": [{"parts": parts}]}
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        pass
    return "⏳ Maafi, abhi main samajh nahi paa raha hoon. Monu Patel ise jald thik karenge!"

def transcribe_voice(voice_path):
    # RECTIFIED URL: Removed extra 'api.'
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    
    try:
        with open(voice_path, "rb") as f:
            files = {
                "file": (voice_path, f),
                "model": (None, "whisper-large-v3"),
                "language": (None, "hi")
            }
            res = requests.post(url, headers=headers, files=files, timeout=25)
            if res.status_code == 200:
                return res.json().get("text")
    except:
        pass
    return None

# --- 4. Webhook Logic ---

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return "ok", 200
    
    chat_id = data["message"]["chat"]["id"]
    reply = ""

    # PHOTO
    if "photo" in data["message"]:
        file_id = data["message"]["photo"][-1]["file_id"]
        img_name = download_telegram_file(file_id)
        caption = data["message"].get("caption", "")
        reply = get_ai_reply(caption, chat_id, image_path=img_name)
        os.remove(img_name)

    # VOICE
    elif "voice" in data["message"]:
        file_id = data["message"]["voice"]["file_id"]
        voice_name = download_telegram_file(file_id)
        transcript = transcribe_voice(voice_name)
        
        if transcript:
            reply = f"🎤 *Aapne kaha:* \"{transcript}\"\n\n" + get_ai_reply(transcript, chat_id)
        else:
            reply = "🔊 Maafi, awaaz samajhne mein dikkat hui."
        os.remove(voice_name)

    # TEXT
    elif "text" in data["message"]:
        text = data["message"]["text"]
        if text == "/start":
            reply = "👋 *Namaste! Main CareBot AI hoon.*\n\nMain Text, Photos aur Voice sab samajh sakta hoon. Mujhe **Monu Patel** ne banaya hai! 🚀"
        else:
            reply = get_ai_reply(text, chat_id)

    if reply:
        final_text = f"{reply}\n\n✨ _By Monu Patel AI_"
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                     json={"chat_id": chat_id, "text": final_text, "parse_mode": "Markdown"})
    
    return "ok", 200

@app.route("/")
def home():
    return "🚀 CareBot Multimodal (Rectified) is Live!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
        
