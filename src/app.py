import requests, os, json
from flask import Flask, request

app = Flask(__name__)

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "СЮДА_ТОКЕН_НОВОГО_БОТА"  # ← ВСТАВЬ СВОЙ ТОКЕН БОТА
DEEPSEEK_API_KEY = "sk-225628b2abe34ac9af08fdca94d81c0c"             # ← ВСТАВЬ СВОЙ API-КЛЮЧ DEEPSEEK
GROUP_CHAT_ID = -5260784715             # ID нашей группы «Штаб Призрак»
SYSTEM_PROMPT = "Ты — полезный AI-ассистент. Отвечай вежливо и по делу."
# =============================================

clients = {}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)

def ask_deepseek(question):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        "stream": False
    }
    try:
        r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data, timeout=30)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "⚠️ Ошибка связи с AI. Попробуйте позже."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if "message" not in data or "text" not in data["message"]:
        return "ok", 200

    msg = data["message"]
    chat_id = msg["chat"]["id"]
    text = msg["text"].strip()
    username = msg["chat"].get("username", "unknown")

    if chat_id > 0:  # Личное сообщение боту
        clients[username] = chat_id
        answer = ask_deepseek(text)  # ← Здесь я отвечаю через API
        send_message(chat_id, answer)
        send_message(GROUP_CHAT_ID, f"📩 @{username}: {text}\n🤖 Бот: {answer}")

    return "ok", 200

@app.route("/")
def home():
    return "bot is alive", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
