import requests, os, threading, time
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "8782847447:AAFaOn42abfoCErNIFNmNYMy9Et8sbZ6OWs"  # ← замени
GROUP_CHAT_ID = -5260784715  # ID группы (минус для супергрупп)
OWNER_USERNAME = "твой_username_без_@"  # ← вставь свой Telegram username (без @), чтобы бот знал, что сообщения от тебя — это я

# Связка username → chat_id клиента
clients = {}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except:
        pass

def process_updates():
    offset = 0
    while True:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
        try:
            r = requests.get(url, timeout=35).json()
            for upd in r.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message")
                if not msg or "text" not in msg:
                    continue

                chat_id = msg["chat"]["id"]
                text = msg["text"].strip()
                from_user = msg.get("from", {})
                sender_username = from_user.get("username", "")

                # 1. Клиент пишет боту в личку → пересылаем в группу
                if chat_id > 0 and sender_username != OWNER_USERNAME:
                    clients[sender_username] = chat_id  # запоминаем
                    if GROUP_CHAT_ID:
                        send_message(GROUP_CHAT_ID, f"📩 От @{sender_username}:\n{text}")

                # 2. В группе пишет "я" (под твоим username) → пересылаем клиенту
                if chat_id == GROUP_CHAT_ID and sender_username == OWNER_USERNAME:
                    # Формат ответа: @username_клиента текст ответа
                    if text.startswith("@"):
                        parts = text.split(maxsplit=1)
                        if len(parts) == 2:
                            target = parts[0][1:]  # убираем @
                            answer = parts[1]
                            client_chat = clients.get(target)
                            if client_chat:
                                send_message(client_chat, f"Ответ от менеджера:\n{answer}")
                            else:
                                send_message(GROUP_CHAT_ID, f"⚠️ Не найден chat_id для @{target}")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)

# Запускаем поток для прослушивания сообщений
threading.Thread(target=process_updates, daemon=True).start()

@app.route("/webhook", methods=["POST"])
def webhook():
    # Вебхук уже не обязателен, но оставим для совместимости
    return "ok", 200

@app.route("/")
def home():
    return "bot is alive", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
