import os
import hmac
import hashlib
import base64
import requests
from flask import Flask, request, abort

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "")

CARD_IMAGES = [
    "https://card-type-message.line-scdn.net/card-type-message-image-2025/463byvhe/1775552684624-di4nUgiaEBz6uL6eSROCvDFapWv05emHFuHkUSJoGh64HG6f5w",
    "https://card-type-message.line-scdn.net/card-type-message-image-2025/463byvhe/1775552846966-7Kl6cOzylceEKZVsJLm2vRhdnfc28cMmltZuzYnBI6Z1ysUu33",
    "https://card-type-message.line-scdn.net/card-type-message-image-2025/463byvhe/1775552897065-gGOYL0SdSZhx0fs1xp0Fn1wcbFxn2NuPzQZKQqvtsYT5VgZ3Yd",
    "https://card-type-message.line-scdn.net/card-type-message-image-2025/463byvhe/1775552948424-JjLrzWpDwnpwrtl7tIJuqfFWCYgjMjWLsePOZNX6UzgBK2CGvb",
    "https://card-type-message.line-scdn.net/card-type-message-image-2025/463byvhe/1775553006169-3nSAlN4zwYqBwuzu4u0PLgtlkJ0sZS8dIIquY6AwTzE73IQWBB",
]

CARD_LABELS = [
    "ご予約について",
    "お支払い方法について",
    "施設内設備について",
    "施設内のアメニティについて",
    "その他",
]


def verify_signature(body, signature):
    h = hmac.new(CHANNEL_SECRET.encode("utf-8"), body, hashlib.sha256).digest()
    return hmac.compare_digest(base64.b64encode(h).decode("utf-8"), signature)


def build_carousel():
    bubbles = []
    for img, label in zip(CARD_IMAGES, CARD_LABELS):
        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": img,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "よくあるご質問", "weight": "bold",
                     "size": "sm", "color": "#888888"},
                    {"type": "text", "text": label, "weight": "bold",
                     "size": "md", "wrap": True},
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": label, "text": label},
                        "style": "primary",
                        "color": "#B8860B",
                    }
                ],
            },
        }
        bubbles.append(bubble)
    return {
        "type": "flex",
        "altText": "よくあるご質問",
        "contents": {"type": "carousel", "contents": bubbles},
    }


def reply_message(reply_token, messages):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    requests.post(url, headers=headers, json={"replyToken": reply_token, "messages": messages})


@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data()
    if not verify_signature(body, signature):
        abort(400)
    events = request.json.get("events", [])
    for event in events:
        if event.get("type") == "postback":
            data = event.get("postback", {}).get("data", "")
            if data == "action=show_faq":
                reply_message(event.get("replyToken"), [build_carousel()])
    return "OK"


@app.route("/", methods=["GET"])
def health():
    return "OK"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
