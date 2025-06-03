import re
from datetime import datetime

# 固定の名前リスト
VALID_NAMES = ["おがわ", "まんぞうじ", "ゆうや", "のん"]

def parse_with_regex(text):
    today = datetime.today().strftime("%Y/%m/%d")
    text = text.replace("今日", today)

    # 日付を抽出（例：6月1日 or 6/1）
    date_match = re.search(r"(\d{1,2})[月/](\d{1,2})", text)
    if date_match:
        month, day = date_match.groups()
        year = str(datetime.today().year)
        date = f"{year}/{int(month):02d}/{int(day):02d}"
    else:
        date = today

    # 名前は厳格にリストから検索
    name = None
    for n in VALID_NAMES:
        if n in text:
            name = n
            break

    # 品目は名前の後にある語句を品目とみなす（厳格にはしない）
    item_match = re.search(rf"{name}\s+(\S+)", text) if name else None

    # 金額
    amount_match = re.search(r"(\d{2,5})円", text)

    if name and item_match and amount_match:
        return {
            "date": date,
            "name": name,
            "item": item_match.group(1),
            "amount": int(amount_match.group(1))
        }
    else:
        return None
