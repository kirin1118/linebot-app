from flask import Flask, request, abort
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 🔽 正規表現＆Geminiモジュールをインポート
from parse_with_regex import parse_with_regex
from parse_with_gemini import parse_with_gemini

# LINEの環境変数
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

# Flaskアプリ作成
app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Googleスプレッドシートの認証と接続
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
credentials_dict = json.loads(credentials_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
sheet = gspread.authorize(creds).open("調味料").sheet1  # スプレッドシート名に合わせて変更OK

# Webhookエンドポイント
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# メッセージ受信処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()

    # 🔽 ログ追加：受け取ったメッセージを表示
    print("🟡 受け取ったテキスト：", text)

    # 正規表現で解析してみる
    result = parse_with_regex(text)
    print("🟢 正規表現の結果：", result)

    if not result:
        result = parse_with_gemini(text)
        print("🔵 Geminiの結果：", result)

    if result:
        sheet.append_row([
            result["date"],
            result["name"],
            result["item"],
            result["amount"]
        ])
        reply = "記録完了！"
    else:
        reply = "⚠️ 内容を理解できませんでした"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

    text = event.message.text.strip()

    # まずは正規表現で解析
    result = parse_with_regex(text)

    # ダメだったらGeminiに渡す
    if not result:
        result = parse_with_gemini(text)

    if result:
        # スプレッドシートに書き込み
        sheet.append_row([
            result["date"],
            result["name"],
            result["item"],
            result["amount"]
        ])
        reply = "記録完了！（正規表現 or Gemini）"
    else:
        reply = "⚠️ 内容を理解できませんでした\n例：6月1日 おがわ しょうゆ 300円"

    # LINEで返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# Render向けポート指定
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
