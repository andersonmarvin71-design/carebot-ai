from flask import Flask, request
import requests

app = Flask(__name__)

# 🔑 Telegram Bot Token (BotFather से)
TOKEN = "8618597269:AAGuVOwLmesBYZ2OazaQId0SNm_gwowGs6I"

# 🔑 Gemini API Key (Google AI Studio से)
GEMINI_API_KEY = "YAHAN_GEMINI_KEY"

# 📩 Telegram message भेजना
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

# 🤖 Gemini AI reply
def get_ai_reply(user_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

    data = {
        "contents": [
            {
                "parts": [{"text": f"You are a helpful health assistant. {user_text}"}]
            }
        ]
    }

    res = requests.post(url, json=data)

    try:
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "⚠️ AI error"

# 🔗 Telegram webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def telegram():
    data = request.get_json()

    if not data or "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    message = data["message"].get("text", "")

    if message == "/start":
        reply = "👋 Welcome to CareBot AI (FREE VERSION)"
    else:
        reply = get_ai_reply(message)
reply += "\n\n— Developed by Monu Patel 🚀"

    send_message(chat_id, reply)
    return "ok"

# 🧪 Test route
@app.route("/")
def home():
    return "Bot running 🚀"

app.run(host="0.0.0.0", port=8080)
