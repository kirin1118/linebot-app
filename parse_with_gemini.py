import os
import json
import google.generativeai as genai

# Gemini APIキーの設定（環境変数から取得）
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def parse_with_gemini(text):
    """
    Geminiに自然文を渡して、「name」「item」「amount」を抽出してJSONで返す。
    失敗時は None を返す。
    """

    prompt = f"""
以下の文章から、次の3つの情報を抽出してください。

【抽出対象】
- name：購入者の名前（必ず「おがわ」「まんぞうじ」「のん」「ゆうや」のいずれかに変換）
- item：購入した品目（例：しょうゆ、バナナ）
- amount：金額（数字または漢数字で指定された金額）

【出力フォーマット】
次の形式で Pythonの辞書（JSON）として **そのまま** 出力してください。
例：
{{"name": "おがわ", "item": "バナナ", "amount": "五百円"}}

【制約】
- 出力はJSONの形式のみ。余計なコメントや文章はつけないこと。
- 金額は「円」を必ず付けること。
- 入力が短文でも正確に判断すること。

【入力文】
{text}
"""

    try:
        model = genai.GenerativeModel("models/gemini-pro")
        response = model.generate_content(prompt)
        result_text = response.text.strip()

        print("🔍 Gemini出力：", result_text)

        result = json.loads(result_text)

        # name, item, amount がそろっているか確認
        if all(k in result for k in ["name", "item", "amount"]):
            return result
        else:
            print("⚠️ 必要なキーが足りません")
            return None

    except Exception as e:
        print("❌ Gemini解析エラー：", e)
        return None
