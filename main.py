from flask import Flask, request
import requests
import os

BOT_TOKEN = "7947263495:AAFxvHiG31WLuusHbcnAS7hHqz1WvGtMLWU"
WEBHOOK_URL = "https://linkguard2-0.onrender.com/webhook"

app = Flask(__name__)

def telegram_api(method, params=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    return requests.get(url, params=params).json()

def is_admin(chat_id, user_id):
    resp = telegram_api("getChatMember", {"chat_id": chat_id, "user_id": user_id})
    return resp.get("ok") and resp["result"]["status"] in ["administrator", "creator"]

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    print(update)

    if 'message' in update:
        msg = update['message']
        chat_id = msg['chat']['id']
        user_id = msg['from']['id']
        text = msg.get('text', '')

        if msg['chat']['type'] in ['group', 'supergroup']:
            if any(link in text for link in ['http://', 'https://', 't.me/', 'telegram.me/']):
                if not is_admin(chat_id, user_id):
                    telegram_api("deleteMessage", {
                        "chat_id": chat_id,
                        "message_id": msg['message_id']
                    })
                    telegram_api("sendMessage", {
                        "chat_id": chat_id,
                        "text": "Warning⚠️ \nLinks is not allowed in this group"
                    })
    return "OK"

@app.route('/', methods=['GET'])
def set_webhook():
    return telegram_api("setWebhook", {"url": WEBHOOK_URL})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

    
