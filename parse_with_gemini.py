import os
import google.generativeai as genai
import json
import re

# 環境変数からAPIキーを読み込む
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Geminiへのプロンプト
PROMPT = """
以下の日本語の文章を読み取り、次の情報を抽出してください：
- name（誰が）
- item（何を）
- amount（金額）

条件：
- name, item, amount がすべて文章に含まれていると仮定してよい
- 金額は「五百円」「500円」「500」など様々な表記がある
- 「昨日」「今日」などの日付表現は無視してよい
- nameやitemはひらがな・カタカナ・漢字の区別があるが、意味を優先
- nameは以下のいずれかに必ず変換してください：
  「おがわ」「まんぞうじ」「のん」「ゆうや」
  ※たとえば「小川」は「おがわ」に、「まんぞうじさん」は「まんぞうじ」にする

出力は以下の形式のJSONで：
{"name": "〇〇", "item": "〇〇", "amount": "〇〇"}

では、以下の文章を解析してください：
"""

def parse_with_gemini(text):
    # Gemini 1.5 Flash モデルを使用
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

    # ユーザーのメッセージをプロンプトに結合して送信
    response = model.generate_content(PROMPT + text)

    # レスポンスからJSON部分だけ取り出す
    match = re.search(r'\{.*?\}', response.text, re.DOTALL)
    if match:
        return json.loads(match.group())
    else:
        raise ValueError("Geminiの返答からJSONが見つかりませんでした")
