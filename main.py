from openai import OpenAI
import os

app = Flask(__name__)

TOKEN = "8618597269:AAGuVOwLmesBYZ2OazaQId0SNm_gwowGs6I"
import os

OPENAI_API_KEY = 
os.environ.get("OPENAI_API_KEY")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def get_ai_reply(user_text):
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful health assistant."},
            {"role": "user", "content": user_text}
        ]
    }

    res = requests.post(url, headers=headers, json=data)

    try:
        return res.json()["choices"][0]["message"]["content"]
    except:
        return "Error in AI"

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram():
    data = request.get_json()

    if not data or "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    message = data["message"].get("text", "")

    if message == "/start":
        reply = "👋 Welcome to CareBot AI"
    else:
        reply = get_ai_reply(message)

    send_message(chat_id, reply)
    return "ok"

@app.route("/")
def home():
    return "Bot running 🚀"

app.run(host="0.0.0.0", port=8080)
