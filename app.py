from flask import Flask, request, abort
import os
import re
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# LINEの環境変数を読み込む
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

# Flaskアプリ作成
app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Googleスプレッドシート設定：credentials.jsonの代わりに環境変数から読み込む
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
credentials_dict = json.loads(credentials_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
sheet = gspread.authorize(creds).open("調味料").sheet1  # スプレッドシート名に合わせて修正OK

# LINEのWebhook受信エンドポイント
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# LINEでメッセージを受け取ったときの処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()

    match = re.match(r"(\d{1,2})月(\d{1,2})日\s+(\S+)\s+(\S+)\s+(\d+)円", text)
    if match:
        month, day, name, item, amount = match.groups()
        date = f"2025/{int(month):02d}/{int(day):02d}"
        sheet.append_row([date, name, item, int(amount)])
        reply = "記録完了！"
    else:
        reply = "⚠️ 形式が違います。例：6月1日 おがわ しょうゆ 300円"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# Flaskアプリ終了処理（Renderでは使わない）
# if __name__ == "__main__": は不要（gunicorn app:app を使うため）

# ユーザーに返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# ← ここから追加！
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

