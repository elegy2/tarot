"""塔罗牌数据：完整 78 张（22 大阿卡那 + 56 小阿卡那）。

每张牌字段：
    id              全局唯一编号
    name_en         英文名
    name_cn         中文名
    arcana          类别：Major / Wands / Cups / Swords / Pentacles
    upright_keywords    正位关键词
    reversed_keywords   逆位关键词
    description     简短解释（用于本地兜底解读）
    image           牌面图片相对路径（只对大阿卡那提供；
                    小阿卡那未提供时为空字符串，UI 层自动兜底绘制）
"""
from __future__ import annotations

from typing import List, Dict, Any


# --- 大阿卡那牌面图片路径（22 张） ---
# 第一版只提供正位牌面图片，逆位通过显示时旋转 180 度实现。
# 所有图片放在 assets/images/cards/ 目录，命名严格按下方映射。
MAJOR_IMAGE_MAP: Dict[int, str] = {
    0: "assets/images/cards/major_00_fool.jpg",
    1: "assets/images/cards/major_01_magician.jpg",
    2: "assets/images/cards/major_02_high_priestess.jpg",
    3: "assets/images/cards/major_03_empress.jpg",
    4: "assets/images/cards/major_04_emperor.jpg",
    5: "assets/images/cards/major_05_hierophant.jpg",
    6: "assets/images/cards/major_06_lovers.jpg",
    7: "assets/images/cards/major_07_chariot.jpg",
    8: "assets/images/cards/major_08_strength.jpg",
    9: "assets/images/cards/major_09_hermit.jpg",
    10: "assets/images/cards/major_10_wheel_of_fortune.jpg",
    11: "assets/images/cards/major_11_justice.jpg",
    12: "assets/images/cards/major_12_hanged_man.jpg",
    13: "assets/images/cards/major_13_death.jpg",
    14: "assets/images/cards/major_14_temperance.jpg",
    15: "assets/images/cards/major_15_devil.jpg",
    16: "assets/images/cards/major_16_tower.jpg",
    17: "assets/images/cards/major_17_star.jpg",
    18: "assets/images/cards/major_18_moon.jpg",
    19: "assets/images/cards/major_19_sun.jpg",
    20: "assets/images/cards/major_20_judgement.jpg",
    21: "assets/images/cards/major_21_world.jpg",
}


MAJOR_ARCANA: List[Dict[str, Any]] = [
    {
        "id": 0, "name_en": "The Fool", "name_cn": "愚者", "arcana": "Major",
        "upright_keywords": ["新开始", "自由", "冒险", "天真"],
        "reversed_keywords": ["鲁莽", "逃避", "不成熟", "风险"],
        "description": "愚者象征新的旅程、未知的可能性与对直觉的信任。",
    },
    {
        "id": 1, "name_en": "The Magician", "name_cn": "魔术师", "arcana": "Major",
        "upright_keywords": ["创造", "意志", "技能", "显化"],
        "reversed_keywords": ["操纵", "拖延", "自我怀疑", "误用才能"],
        "description": "魔术师代表把想法转化为现实的能力,资源已就绪。",
    },
    {
        "id": 2, "name_en": "The High Priestess", "name_cn": "女祭司", "arcana": "Major",
        "upright_keywords": ["直觉", "潜意识", "神秘", "内省"],
        "reversed_keywords": ["压抑直觉", "秘密", "迷茫", "脱离内心"],
        "description": "女祭司提醒你倾听内在声音,真相在沉默中显现。",
    },
    {
        "id": 3, "name_en": "The Empress", "name_cn": "女皇", "arcana": "Major",
        "upright_keywords": ["丰饶", "母性", "创造力", "滋养"],
        "reversed_keywords": ["依赖", "停滞", "缺乏自爱", "创意阻塞"],
        "description": "女皇象征丰盈与温柔的力量,是孕育的能量。",
    },
    {
        "id": 4, "name_en": "The Emperor", "name_cn": "皇帝", "arcana": "Major",
        "upright_keywords": ["秩序", "权威", "稳定", "结构"],
        "reversed_keywords": ["专制", "僵化", "失控", "缺乏纪律"],
        "description": "皇帝代表理性与制度,以稳定的力量构筑根基。",
    },
    {
        "id": 5, "name_en": "The Hierophant", "name_cn": "教皇", "arcana": "Major",
        "upright_keywords": ["传统", "信仰", "教导", "传承"],
        "reversed_keywords": ["反叛", "教条", "脱离群体", "墨守成规"],
        "description": "教皇象征制度与精神传承,提示遵循已有路径或寻师。",
    },
    {
        "id": 6, "name_en": "The Lovers", "name_cn": "恋人", "arcana": "Major",
        "upright_keywords": ["爱", "选择", "和谐", "结合"],
        "reversed_keywords": ["分歧", "犹豫", "失衡", "诱惑"],
        "description": "恋人牌不仅指爱情,也代表重大选择与价值观对齐。",
    },
    {
        "id": 7, "name_en": "The Chariot", "name_cn": "战车", "arcana": "Major",
        "upright_keywords": ["决心", "胜利", "意志", "前进"],
        "reversed_keywords": ["失控", "冲突", "方向迷失", "停滞"],
        "description": "战车代表凭借自律与意志驾驭对立力量,赢得胜利。",
    },
    {
        "id": 8, "name_en": "Strength", "name_cn": "力量", "arcana": "Major",
        "upright_keywords": ["勇气", "耐心", "温柔", "内在力"],
        "reversed_keywords": ["自我怀疑", "脆弱", "暴躁", "缺乏耐心"],
        "description": "力量牌是以柔克刚,以爱与耐心驯服内在野性。",
    },
    {
        "id": 9, "name_en": "The Hermit", "name_cn": "隐士", "arcana": "Major",
        "upright_keywords": ["内省", "独处", "智慧", "寻找"],
        "reversed_keywords": ["孤立", "迷失", "拒绝建议", "封闭"],
        "description": "隐士提着灯独行,提示你向内观照、寻找自己的真相。",
    },
    {
        "id": 10, "name_en": "Wheel of Fortune", "name_cn": "命运之轮", "arcana": "Major",
        "upright_keywords": ["转机", "循环", "命运", "因果"],
        "reversed_keywords": ["低谷", "反复", "抗拒变化", "厄运"],
        "description": "命运之轮象征循环与转机,提醒在变化中保持中心。",
    },
    {
        "id": 11, "name_en": "Justice", "name_cn": "正义", "arcana": "Major",
        "upright_keywords": ["公正", "真相", "因果", "理性"],
        "reversed_keywords": ["偏见", "不公", "推卸责任", "失衡"],
        "description": "正义代表清晰的判断与因果回响,该承担的必须承担。",
    },
    {
        "id": 12, "name_en": "The Hanged Man", "name_cn": "倒吊人", "arcana": "Major",
        "upright_keywords": ["臣服", "新视角", "等待", "牺牲"],
        "reversed_keywords": ["抗拒", "拖延", "无意义牺牲", "停滞"],
        "description": "倒吊人邀请你换个角度看问题,暂停反而带来洞察。",
    },
    {
        "id": 13, "name_en": "Death", "name_cn": "死神", "arcana": "Major",
        "upright_keywords": ["结束", "蜕变", "释放", "重生"],
        "reversed_keywords": ["抗拒结束", "停滞", "执着", "缓慢转化"],
        "description": "死神并非字面终结,而是必要的转化与告别。",
    },
    {
        "id": 14, "name_en": "Temperance", "name_cn": "节制", "arcana": "Major",
        "upright_keywords": ["平衡", "调和", "耐心", "中道"],
        "reversed_keywords": ["失衡", "极端", "冲动", "不耐烦"],
        "description": "节制是缓慢调和、找到属于你节奏的艺术。",
    },
    {
        "id": 15, "name_en": "The Devil", "name_cn": "恶魔", "arcana": "Major",
        "upright_keywords": ["束缚", "欲望", "执念", "依赖"],
        "reversed_keywords": ["挣脱束缚", "觉醒", "释放", "戒除"],
        "description": "恶魔指向你自缚的牢笼,真正的钥匙一直在你手中。",
    },
    {
        "id": 16, "name_en": "The Tower", "name_cn": "塔", "arcana": "Major",
        "upright_keywords": ["崩塌", "突变", "觉醒", "解构"],
        "reversed_keywords": ["拖延崩塌", "勉强维系", "渐变", "恐惧改变"],
        "description": "塔的倒塌粗暴却必要,虚假的根基终须重建。",
    },
    {
        "id": 17, "name_en": "The Star", "name_cn": "星星", "arcana": "Major",
        "upright_keywords": ["希望", "疗愈", "灵感", "信念"],
        "reversed_keywords": ["失望", "怀疑", "失去信心", "枯竭"],
        "description": "星星是黑夜中的微光,提醒希望与温柔的力量。",
    },
    {
        "id": 18, "name_en": "The Moon", "name_cn": "月亮", "arcana": "Major",
        "upright_keywords": ["幻觉", "潜意识", "迷雾", "直觉"],
        "reversed_keywords": ["真相浮现", "释放恐惧", "清醒", "走出迷雾"],
        "description": "月亮提示模糊与梦境,容许情绪流动而不急于判断。",
    },
    {
        "id": 19, "name_en": "The Sun", "name_cn": "太阳", "arcana": "Major",
        "upright_keywords": ["喜悦", "光明", "成功", "活力"],
        "reversed_keywords": ["乌云", "低落", "短暂阴霾", "缺乏自信"],
        "description": "太阳带来温暖与确定,是简单而真实的快乐。",
    },
    {
        "id": 20, "name_en": "Judgement", "name_cn": "审判", "arcana": "Major",
        "upright_keywords": ["觉醒", "复活", "召唤", "宽恕"],
        "reversed_keywords": ["自我怀疑", "拒绝召唤", "悔恨", "犹豫"],
        "description": "审判像号角声,邀你回应那个内心一直在听到的呼唤。",
    },
    {
        "id": 21, "name_en": "The World", "name_cn": "世界", "arcana": "Major",
        "upright_keywords": ["完成", "圆满", "成就", "整合"],
        "reversed_keywords": ["未完成", "拖延", "缺一角", "停滞"],
        "description": "世界象征旅程圆满,你已整合内外,准备进入新的循环。",
    },
]


def _minor_set(arcana_en: str, arcana_cn: str, base_id: int,
               suit_words: List[str], suit_intro: str) -> List[Dict[str, Any]]:
    """生成同一花色的 14 张小阿卡那(Ace ~ 10 + 侍从、骑士、王后、国王)。"""
    ranks = [
        ("Ace", "一"), ("Two", "二"), ("Three", "三"), ("Four", "四"),
        ("Five", "五"), ("Six", "六"), ("Seven", "七"), ("Eight", "八"),
        ("Nine", "九"), ("Ten", "十"),
        ("Page", "侍从"), ("Knight", "骑士"),
        ("Queen", "王后"), ("King", "国王"),
    ]
    upright_pool = {
        "Wands": [
            ["灵感", "起步", "热情", "潜能"],
            ["规划", "选择", "远见", "伙伴"],
            ["扩张", "等待", "远方", "合作"],
            ["庆祝", "归属", "稳定", "里程碑"],
            ["争执", "竞争", "意见分歧", "磨合"],
            ["胜利", "认可", "凯旋", "自信"],
            ["坚守", "防御", "立场", "勇气"],
            ["快速进展", "信息", "行动", "转机"],
            ["坚持", "戒备", "韧性", "蓄力"],
            ["重担", "责任", "近终点", "压力"],
            ["探索", "学习", "好奇", "信使"],
            ["冲劲", "冒险", "热血", "莽撞"],
            ["热情", "魅力", "自信", "领导"],
            ["远见", "魄力", "掌控", "格局"],
        ],
        "Cups": [
            ["新感情", "心动", "情感涌现", "灵感"],
            ["共鸣", "结盟", "恋爱", "互相吸引"],
            ["庆祝", "友谊", "团聚", "喜悦"],
            ["倦怠", "重新评估", "冷淡", "内省"],
            ["失落", "悲伤", "未走出"],
            ["怀旧", "童年", "纯真", "再相遇"],
            ["幻想", "选择困难", "白日梦"],
            ["离开", "寻找意义", "放下"],
            ["心愿成就", "满足", "感激"],
            ["家庭和谐", "圆满", "情感丰盛"],
            ["敏感", "信使", "艺术", "情书"],
            ["浪漫", "提议", "理想主义"],
            ["温柔", "共情", "包容", "情感成熟"],
            ["情感掌控", "深沉", "稳定的爱"],
        ],
        "Swords": [
            ["突破", "清晰", "真相", "决心"],
            ["僵局", "选择", "回避决定"],
            ["心碎", "伤痛", "释放泪水"],
            ["休整", "退避", "冥想"],
            ["冲突", "胜负", "代价"],
            ["过渡", "离开", "前行"],
            ["谋略", "回避", "不诚实", "策略"],
            ["受困", "自我设限", "盲点"],
            ["焦虑", "梦魇", "担忧", "失眠"],
            ["谷底", "结束", "重生前的黑夜"],
            ["机敏", "好奇", "信息", "求知"],
            ["果断", "冲动", "正面突破"],
            ["独立", "理性", "清晰", "界限"],
            ["权威", "公正", "严谨", "战略"],
        ],
        "Pentacles": [
            ["机会", "现实", "种子", "礼物"],
            ["平衡", "节奏", "兼顾"],
            ["合作", "技艺", "认可"],
            ["守财", "保守", "稳定"],
            ["匮乏", "孤立", "财务忧虑"],
            ["施与受", "援助", "慷慨"],
            ["评估", "耐心", "回顾"],
            ["精进", "勤勉", "学徒"],
            ["独立丰盛", "享受", "成熟"],
            ["传承", "家业", "长期富足"],
            ["学习", "实干", "踏实"],
            ["稳健", "可靠", "进度慢"],
            ["丰盛", "踏实", "滋养", "现实关怀"],
            ["事业有成", "稳健", "守护者"],
        ],
    }
    reversed_pool = {
        "Wands": ["延误", "失焦", "动力消退", "鲁莽", "抗拒前行"],
        "Cups": ["情感压抑", "失望", "拖延", "幻灭", "逃避"],
        "Swords": ["混乱", "自我攻击", "执念", "拖延决定", "信息失真"],
        "Pentacles": ["不稳定", "短视", "拖延", "贪婪", "失衡"],
    }
    desc_intro = suit_intro
    cards: List[Dict[str, Any]] = []
    for i, (rank_en, rank_cn) in enumerate(ranks):
        upright = upright_pool[arcana_en][i]
        reversed_kw = reversed_pool[arcana_en] + ["与正位相反"]
        cards.append({
            "id": base_id + i,
            "name_en": f"{rank_en} of {arcana_en}",
            "name_cn": f"{arcana_cn}{rank_cn}",
            "arcana": arcana_en,
            "upright_keywords": upright,
            "reversed_keywords": reversed_kw[:4],
            "description": f"{desc_intro}{rank_cn}阶段,关键词:{ '、'.join(upright) }。",
        })
    return cards


WANDS = _minor_set("Wands", "权杖", 22, [], "权杖代表火元素与行动、热情,")
CUPS = _minor_set("Cups", "圣杯", 36, [], "圣杯代表水元素与情感、关系,")
SWORDS = _minor_set("Swords", "宝剑", 50, [], "宝剑代表风元素与思想、沟通,")
PENTACLES = _minor_set("Pentacles", "星币", 64, [], "星币代表土元素与现实、物质,")


ALL_CARDS: List[Dict[str, Any]] = MAJOR_ARCANA + WANDS + CUPS + SWORDS + PENTACLES


# 为所有牌注入 image 字段:大阿卡那用 MAJOR_IMAGE_MAP,小阿卡那暂留空。
for _card in ALL_CARDS:
    if _card["arcana"] == "Major":
        _card["image"] = MAJOR_IMAGE_MAP.get(_card["id"], "")
    else:
        _card["image"] = ""


def get_all_cards() -> List[Dict[str, Any]]:
    """返回完整 78 张牌的副本。"""
    return [dict(card) for card in ALL_CARDS]


def get_major_arcana() -> List[Dict[str, Any]]:
    """只返回 22 张大阿卡那(第一版推荐只用大阿卡那抽牌)。"""
    return [dict(c) for c in ALL_CARDS if c["arcana"] == "Major"]
