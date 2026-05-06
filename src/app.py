import requests, os, json
from flask import Flask, request

app = Flask(__name__)

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8782847447:AAFaOn42abfoCErNIFNmNYMy9Et8sbZ6OWs
"  # ← вставь токен бота
DEEPSEEK_API_KEY = "sk-780958c4d0ed46bf9c7c44ba52705a0b"             # ← вставь свой API-ключ DeepSeek
GROUP_CHAT_ID = -5260784715             # ID нашей группы «Штаб Призрак»
SYSTEM_PROMPT = "Ты — полезный AI-ассистент. Отвечай вежливо и по делу."
# =============================================

clients = {}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print(f"Send error: {e}")

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
        r = requests.post("https://api.deepseek.com/v1/chat/completions",
                         headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        else:
            return f"Ошибка API (код {r.status_code}): {r.text[:100]}"
    except Exception as e:
        return f"Сетевая ошибка: {str(e)}"

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
