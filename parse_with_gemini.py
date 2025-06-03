import os
import google.generativeai as genai

# 環境変数から Gemini API キーを設定
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def parse_with_gemini(text):
    """
    Gemini に自然文を送って、名前・品目・金額を抽出する。
    JSON形式で返ってくることを期待。
    """
    prompt = f"""
以下の文章から、次の3項目を抽出し、Pythonの辞書形式（JSON）で返してください。

- name（名前）→ 必ず「おがわ」「まんぞうじ」「のん」「ゆうや」のいずれかに変換してください。
- item（品目）→ 買ったものの名前
- amount（金額）→ 数字で。漢数字でも構いません。

例：
「今日 オガワが みかんを 五百円で買いました」→
{{"name": "おがわ", "item": "みかん", "amount": "五百円"}}

入力文：
{text}
"""

    try:
        model = genai.GenerativeModel("models/gemini-pro")
        response = model.generate_content(prompt)
        result_text = response.text.strip()

        print("🔍 Gemini出力：", result_text)

        # 安全にJSONに変換（evalより安全）
        import json
        result = json.loads(result_text)

        # 結果に必要なキーが全てあるか確認
        if all(k in result for k in ["name", "item", "amount"]):
            return result
        else:
            return None

    except Exception as e:
        print("❌ Geminiエラー：", e)
        return None
