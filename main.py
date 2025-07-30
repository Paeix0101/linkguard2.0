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

        chat_type = msg['chat']['type']

        # ✅ Handle private chat /start command
        if chat_type == 'private' and text.strip() == '/start':
            welcome_text = (
                "🤖 *Advance HYPERLINK Remove Bot*\n\n"
                "🛡️ Give *admin* rights to this bot in your group\n\n"
                "✨ *Features:*\n"
                "1️⃣ Deletes links sent by members in groups 🔗❌\n"
                "2️⃣ Does *not* delete links sent by *admins* 👮✅\n"
            )
            telegram_api("sendMessage", {
                "chat_id": chat_id,
                "text": welcome_text,
                "parse_mode": "Markdown"
            })

        # ✅ Handle link deletion in group
        elif chat_type in ['group', 'supergroup']:
            if any(link in text for link in ['http://', 'https://', 't.me/', 'telegram.me/']):
                if not is_admin(chat_id, user_id):
                    telegram_api("deleteMessage", {
                        "chat_id": chat_id,
                        "message_id": msg['message_id']
                    })
                    telegram_api("sendMessage", {
                        "chat_id": chat_id,
                        "text": "⚠️ *Warning*\nLinks are not allowed in this group.",
                        "parse_mode": "Markdown"
                    })

    return "OK"

@app.route('/', methods=['GET'])
def set_webhook():
    return telegram_api("setWebhook", {"url": WEBHOOK_URL})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

    
