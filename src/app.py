import requests, os
from flask import Flask, request

app = Flask(__name__)
BOT_TOKEN = "8782847447:AAFaOn42abfoCErNIFNmNYMy9Et8sbZ6OWs"   # ← вставь сюда токен

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print(f"Send error: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if 'message' in data and 'text' in data['message']:
        msg = data['message']
        chat_id = msg['chat']['id']
        text = msg['text']
        username = msg['chat'].get('username', 'unknown')
        # Временно просто подтверждение клиенту
        send_message(chat_id, f"Получили ваше сообщение, @{username}. Скоро ответим.")
    return 'ok', 200

@app.route('/')
def home():
    return 'bot is alive', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
