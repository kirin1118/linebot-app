import google.generativeai as genai
import os
from datetime import datetime

# 環境変数から Gemini APIキーを読み込む
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# Gemini APIの初期設定
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Geminiに渡す命令（プロンプト）
SYSTEM_PROMPT = """
あなたは家計簿記録アシスタントです。
以下の文を読み取り、「日付」「名前」「品目」「金額」を抽出し、次のJSON形式で返してください：

{
  "date": "2025/06/01",
  "name": "おがわ",
  "item": "しょうゆ",
  "amount": 300
}
"""

# Geminiを使ってメッセージを解析する関数
def parse_with_gemini(text):
    # "今日" という単語があれば、今日の日付に変換する
    today = datetime.today().strftime("%Y/%m/%d")
    text = text.replace("今日", today)

    # Geminiに渡す完全なプロンプトを作る
    prompt = f"{SYSTEM_PROMPT}\n\n文：{text}"
    print("🟠 Geminiに渡すプロンプト：", prompt)

    try:
        # Geminiに問い合わせて応答を受け取る
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        print("🟢 Geminiの返答：", response_text)

        # 応答が文字列なので、Pythonの辞書に変換する
        parsed = eval(response_text)

        # 必須の項目がすべて揃っているか確認
        if all(key in parsed for key in ["date", "name", "item", "amount"]):
            return parsed
        else:
            print("🔴 Gemini返答に必要な項目が足りません")
            return None

    except Exception as e:
        print("🔴 Geminiでエラー発生:", e)
        return None
