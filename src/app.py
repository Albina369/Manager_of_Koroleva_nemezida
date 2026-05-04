import requests, os, time, threading
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "8782847447:AAFaOn42abfoCErNIFNmNYMy9Et8sbZ6OWs"   # ← замени на токен
GROUP_CHAT_ID = -5260784715  # ID твоей группы

# Словарь: username клиента → его chat_id (чтобы позже отвечать)
clients = {}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except:
        pass

def listen():
    offset = 0
    while True:
        try:
            r = requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                params={"offset": offset, "timeout": 30}
            ).json()
            for upd in r.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message")
                if not msg or "text" not in msg:
                    continue

                chat_id = msg["chat"]["id"]
                text = msg["text"].strip()
                username = msg["from"].get("username", "unknown")

                # Если клиент пишет боту в ЛС — сразу пересылаем в группу
                if chat_id > 0:
                    clients[username] = chat_id  # запоминаем для ответа
                    send_message(GROUP_CHAT_ID, f"📩 От @{username}:\n{text}")
        except:
            pass
        time.sleep(1)

threading.Thread(target=listen, daemon=True).start()

@app.route("/webhook", methods=["POST"])
def webhook():
    return "ok", 200

@app.route("/")
def home():
    return "bot is alive", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
