# 必要なライブラリの読み込み
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

app = Flask(__name__)

# --- ① LINE BOTの設定（ここに自分の情報をコピペ） ---
LINE_CHANNEL_ACCESS_TOKEN = 'pIjoKmI6SIVmX0PdAR/eZHGskZ5fiOuQb1o0/9r7RnPvKFYfFT20IyQfnSY5M7hJhsOxUiqnU1cmH00OF0KOS8rPAUMkA8YSIzUUboVTnMeGOW2ix2/MXCCxu2N4vxNVrW0aQXiJHt10NwkoqT25iAdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'fa12c26f5b8e571d56413e554626e470'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# --- ② Googleスプレッドシートの認証設定 ---
# スプレッドシートを操作するための認証設定
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
sheet = gspread.authorize(creds).open("調味料").sheet1  # ← スプレッドシート名に合わせて変更OK

# --- ③ LINEからのWebhookを受け取る部分 ---
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']  # LINEから送られてくる署名
    body = request.get_data(as_text=True)  # リクエスト本文
    handler.handle(body, signature)  # イベント処理に渡す
    return 'OK'

# --- ④ メッセージを受け取ったときの処理 ---
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()  # 受け取ったテキストを取得

    # 例：「6月1日 おがわ しょうゆ 300円」の形式でマッチさせる
    match = re.match(r"(\d{1,2}月\d{1,2}日)\s+(\S+)\s+(\S+)\s+(\d+)円?", text)

    if match:
        date, name, item, price = match.groups()
        # スプレッドシートに行を追加（順番は 日付｜品目｜購入者｜金額）
        sheet.append_row([date, item, name, int(price)])
        reply = "記録完了！"
    else:
        reply = "⚠️ 形式が違います。例：6月1日 おがわ しょうゆ 300円"

    # LINEに返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# --- ⑤ サーバーをローカルで起動 ---
if __name__ == "__main__":
    app.run()
