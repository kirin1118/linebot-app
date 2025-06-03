# 名前の補正辞書
NAME_MAP = {
    "小川": "おがわ", "オガワ": "おがわ", "OGAWA": "おがわ", "おがわ": "おがわ",
    "マンゾウジ": "まんぞうじ", "万蔵寺": "まんぞうじ", "まんぞうじ": "まんぞうじ",
    "ゆうや": "ゆうや", "ユウヤ": "ゆうや", "YUYA": "ゆうや",
    "のん": "のん", "ノン": "のん"
}

def resolve_name(name_raw: str) -> str:
    """名前を定義された表記に統一"""
    return NAME_MAP.get(name_raw.strip(), name_raw.strip())


# 漢数字の変換用辞書
KANJI_NUM_MAP = {
    '〇': 0, '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
    '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
    '十': 10, '百': 100, '千': 1000, '万': 10000
}

def kanji_to_number(kanji: str) -> int:
    """漢数字をアラビア数字に変換（例：五百一→501）"""
    num, tmp, unit = 0, 0, 1
    for char in reversed(kanji):
        if char not in KANJI_NUM_MAP:
            continue
        val = KANJI_NUM_MAP[char]
        if val >= 10:
            if tmp == 0:
                tmp = 1
            unit = val
        else:
            tmp = val
        if unit > 1:
            num += tmp * unit
            tmp = 0
            unit = 1
    num += tmp
    return num


def resolve_amount(raw: str) -> int:
    """
    金額を整数で返す（例：'五百円' → 500, '500円' → 500）
    """
    raw = raw.replace("円", "").replace(",", "").strip()

    # 数字そのままならintにして返す
    if raw.isdigit():
        return int(raw)

    # 漢数字が含まれている場合は変換
    if any(k in raw for k in KANJI_NUM_MAP):
        return kanji_to_number(raw)

    # その他 → エラー扱いで 0 を返す
    return 0
