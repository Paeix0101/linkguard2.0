from flask import Flask, request
import requests
import os

BOT_TOKEN = "7947263495:AAFxvHiG31WLuusHbcnAS7hHqz1WvGtMLWU"
WEBHOOK_URL = "https://linkguard2-0.onrender.com/webhook"
OWNER_ID = 8141547148  # Replace with your Telegram user ID

app = Flask(__name__)

def telegram_api(method, params=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    return requests.get(url, params=params).json()

def is_admin(chat_id, user_id):
    resp = telegram_api("getChatMember", {"chat_id": chat_id, "user_id": user_id})
    return resp.get("ok") and resp["result"]["status"] in ["administrator", "creator"]

def save_group_id(chat_id):
    file_path = "group.txt"
    sent_file = "sent_groups.txt"

    # Create files if not exist
    if not os.path.exists(file_path):
        open(file_path, 'w').close()
    if not os.path.exists(sent_file):
        open(sent_file, 'w').close()

    # Save group ID if not already in group.txt
    with open(file_path, 'r') as f:
        groups = f.read().splitlines()

    if str(chat_id) not in groups:
        with open(file_path, 'a') as f:
            f.write(f"{chat_id}\n")

        # Notify owner only once
        with open(sent_file, 'r') as f:
            sent_ids = f.read().splitlines()
        if str(chat_id) not in sent_ids:
            telegram_api("sendMessage", {
                "chat_id": OWNER_ID,
                "text": f"📢 Bot added to new group:\n`{chat_id}`",
                "parse_mode": "Markdown"
            })
            with open(sent_file, 'a') as f:
                f.write(f"{chat_id}\n")

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

        # ✅ Group/supergroup logic
        if chat_type in ['group', 'supergroup']:
            save_group_id(chat_id)

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

        # ✅ Private chat logic
        elif chat_type == 'private':
            # /start command
            if text.strip() == '/start':
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
            # ✅ If owner sends a group ID to check status
            elif str(user_id) == str(OWNER_ID) and text.strip().lstrip('-').isdigit():
                target_group_id = int(text.strip())
                resp = telegram_api("getChatMember", {
                    "chat_id": target_group_id,
                    "user_id": BOT_TOKEN.split(":")[0]
                })

                if resp.get("ok") and resp["result"]["status"] in ["administrator", "creator"]:
                    telegram_api("sendMessage", {
                        "chat_id": chat_id,
                        "text": "✅ Bot is *active* and has admin rights in the group.",
                        "parse_mode": "Markdown"
                    })
                else:
                    telegram_api("sendMessage", {
                        "chat_id": chat_id,
                        "text": "⚠️ Bot is *not active* or doesn't have admin rights in that group.",
                        "parse_mode": "Markdown"
                    })

    return "OK"

@app.route('/', methods=['GET'])
def set_webhook():
    return telegram_api("setWebhook", {"url": WEBHOOK_URL})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

    
