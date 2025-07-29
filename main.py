import os
import requests
from flask import Flask, request

# === CONFIGURATION ===
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
WEBHOOK_URL = "https://your-render-url.onrender.com/webhook"

app = Flask(__name__)

# === Helper function to get chat member status ===
def get_user_status(chat_id, user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
    params = {
        "chat_id": chat_id,
        "user_id": user_id
    }
    response = requests.get(url, params=params).json()
    if response.get("ok"):
        return response["result"]["status"]  # 'administrator', 'creator', or 'member'
    return None

# === Webhook endpoint ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'message' in data:
        message = data['message']
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        text = message.get('text', '')

        # Only act in group or supergroup
        if message['chat']['type'] in ['group', 'supergroup']:
            # If message contains a link
            if 'http://' in text or 'https://' in text or 't.me/' in text or 'telegram.me/' in text:
                user_status = get_user_status(chat_id, user_id)
                
                # If user is not admin or owner, delete message
                if user_status not in ['administrator', 'creator']:
                    message_id = message['message_id']
                    
                    # Delete message
                    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage", params={
                        "chat_id": chat_id,
                        "message_id": message_id
                    })

                    # Send warning
                    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params={
                        "chat_id": chat_id,
                        "text": "Warning⚠️ \nLinks is not allowed in this group"
                    })

    return 'OK'

# === Set webhook route ===
@app.route('/', methods=['GET'])
def set_webhook():
    set_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}"
    r = requests.get(set_url)
    return r.text

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
