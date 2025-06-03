import google.generativeai as genai
import os
from datetime import datetime

# 環境変数からAPIキーを取得（事前に設定済みであること）
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# Geminiの初期設定
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# プロンプトに渡す命令文（Geminiに「この形式で答えて」とお願い）
SYSTEM_PROMPT = """
あなたは家計簿記録用のアシスタントです。
以下のような文を読み取り、「日付」「名前」「品目」「金額」をJSON形式で返してください。
出力形式は以下のようにしてください（文字列として返してね）：

{
  "date": "2025/06/01",
  "name": "おがわ",
  "item": "しょうゆ",
  "amount": 300
}
"""

# Geminiで解析して辞書形式で返す関数
def parse_with_gemini(text):
    today = datetime.today().strftime("%Y/%m/%d")
    text = text.replace("今日", today)

    prompt = f"{SYSTEM_PROMPT}\n\n文：{text}"

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Geminiは文字列で返すため、明示的に辞書化
        parsed = eval(response_text)
        
        # 最低限の構造確認
        if all(key in parsed for key in ["date", "name", "item", "amount"]):
            return parsed
        else:
            return None
    except Exception as e:
        print("Gemini解析エラー:", e)
        return None
