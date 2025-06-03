# helpers.py

# 名前補正辞書
NAME_MAP = {
    "小川": "おがわ", "オガワ": "おがわ", "OGAWA": "おがわ", "おがわ": "おがわ",
    "マンゾウジ": "まんぞうじ", "まんぞうじ": "まんぞうじ",
    "のん": "のん", "ゆうや": "ゆうや", "ユウヤ": "ゆうや"
}

def resolve_name(name_raw):
    return NAME_MAP.get(name_raw, name_raw)

# 漢数字変換
KANJI_NUM_MAP = {
    '〇': 0, '一': 1, '二': 2, '三': 3, '四': 4,
    '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
    '十': 10, '百': 100, '千': 1000, '万': 10000
}

def kanji_to_number(kanji):
    num, tmp, unit = 0, 0, 1
    for char in reversed(kanji):
        val = KANJI_NUM_MAP.get(char)
        if val is None:
            continue
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

def resolve_amount(raw):
    raw = raw.replace("円", "").replace(",", "").strip()
    if raw.isdigit():
        return int(raw)
    if any(k in raw for k in KANJI_NUM_MAP):
        return kanji_to_number(raw)
    return 0
