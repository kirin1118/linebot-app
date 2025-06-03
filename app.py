from flask import Flask, request, abort
import os, json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from datetime import datetime

# 外部モジュールの読み込み
from parse_with_gemini import parse_with_gemini
from helpers import resolve_name, resolve_amount

# 環境変数の読み込み
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

# Flaskアプリのセットアップ
app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Googleスプレッドシートの認証
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials_dict = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
sheet = gspread.authorize(creds).open("調味料").sheet1  # スプレッドシート名に合わせて変更可

# LINEのWebhookエンドポイント
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# LINEでのメッセージ受信時の処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    print("📩 受信テキスト：", text)

    # Geminiで解析
    result = parse_with_gemini(text)
    print("🧠 Gemini解析結果：", result)

    if result:
        # 名前・金額の補正処理（helpers.py）
        result["name"] = resolve_name(result["name"])
        result["amount"] = resolve_amount(result["amount"])

        # 日付は今日の日付で記録
        today = datetime.today().strftime("%Y/%m/%d")
        sheet.append_row([
            today,
            result["name"],
            result["item"],
            result["amount"]
        ])

        reply = f"✅ 記録完了！\n{today} に {result['name']} が {result['item']} を {result['amount']}円で購入しました。"
    else:
        reply = "⚠️ 内容を理解できませんでした。\n例：6月3日 おがわ バナナ 300円"

    # LINEに返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# Render用（PORT環境変数対応）
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
