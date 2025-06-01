from flask import Flask, request, abort
import os
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 環境変数からLINEのチャネル情報を読み込む
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]


# Flaskアプリケーション作成
app = Flask(__name__)

# LINE Bot API と Webhook ハンドラ
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Google Sheets APIの設定
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# スプレッドシート名（自分のファイル名に合わせて）
sheet = client.open("調味料").sheet1

# Webhookのエンドポイント
@app.route("/callback", methods=['POST'])
def callback():
    # LINEから送られた署名
    signature = request.headers['X-Line-Signature']

    # 送られてきた本文
    body = request.get_data(as_text=True)

    # 署名が正しいか確認
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# メッセージ受信時の処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    # 入力形式：6月1日 おがわ しょうゆ 300円
    pattern = r'(\d{1,2})月(\d{1,2})日\s+(\S+)\s+(\S+)\s+(\d+)円'
    match = re.match(pattern, text)

    if match:
        month, day, name, item, amount = match.groups()
        date = f"2025/{int(month):02d}/{int(day):02d}"
        sheet.append_row([date, name, item, int(amount)])
        reply = "記録完了！"
    else:
        reply = "形式が正しくありません。例：6月1日 おがわ しょうゆ 300円"

    # ユーザーに返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# 注意：Renderでは app.run() は不要！
# gunicorn app:app で起動するのでこの行は書かない
