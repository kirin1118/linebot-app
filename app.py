from flask import Flask, request, abort
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from datetime import datetime

# Gemini/GSheet補助関数
from parse_with_gemini import parse_with_gemini
from helpers import resolve_name, resolve_amount

# LINEの環境変数
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

# Flaskアプリ作成
app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Googleスプレッドシート設定
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
credentials_dict = json.loads(credentials_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
sheet = gspread.authorize(creds).open("調味料").sheet1  # スプレッドシート名に合わせて変更可

# Webhookエンドポイント
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("❌ LINE署名が無効です")
        abort(400)

    return 'OK'

# LINEからのメッセージ処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    print("📨 ユーザー入力：", text)

    # Geminiで解析
    result = parse_with_gemini(text)
    print("🔮 Geminiの解析結果：", result)

    if result:
        # 日付は今日の日付を使う
        today = datetime.today().strftime("%Y/%m/%d")

        # 名前と金額を補正（別ファイルの関数）
        name = resolve_name(result["name"])
        item = result["item"]
        amount = resolve_amount(result["amount"])

        print("✅ 補正後の値:", today, name, item, amount)

        # スプレッドシートに記録
        sheet.append_row([today, name, item, amount])
        reply = f"✅ 記録完了！\n{today} に {name} が {item} を {amount}円で購入しました。"
    else:
        reply = "⚠️ 内容を理解できませんでした。\n例：のん 納豆 五百円"

    # ユーザーに返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# Render用（ポート指定）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
