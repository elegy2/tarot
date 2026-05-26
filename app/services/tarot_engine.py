"""塔罗引擎:负责抽牌与构造结构化结果。

抽牌使用 `random.SystemRandom()`,比默认 `random.Random()` 更接近真随机,
适合作为占卜场景的洗牌源。

返回的结果字段包含真实牌名、正逆位、图片路径等完整信息,
但 UI 层在用户真正"翻牌"前不得展示这些信息(见 TarotCardWidget)。
"""
from __future__ import annotations

import random
from typing import List, Dict, Any, Optional

from app.data.tarot_cards import get_all_cards, get_major_arcana
from app.data.spreads import get_spread


class TarotEngine:
    """单次占卜的核心抽牌器。"""

    def __init__(self, rng: Optional[random.Random] = None,
                 use_major_only: bool = False):
        # 默认使用系统级 CSPRNG,更接近真随机
        self._rng = rng or random.SystemRandom()
        self._use_major_only = use_major_only
        self._refresh_deck()

    def _refresh_deck(self) -> None:
        self._all_cards = (
            get_major_arcana() if self._use_major_only else get_all_cards()
        )

    def draw(self, spread_key: str) -> List[Dict[str, Any]]:
        """根据牌阵 key 随机抽牌,返回结构化结果。

        每张牌包含位置、正逆位、关键词、本地基础解释与图片路径。

        **重要**:该方法只负责产出数据,调用方(UI 层)必须在用户"翻牌"之前,
        只显示牌背,不能泄露牌名、正逆位、关键词。
        """
        spread = get_spread(spread_key)
        positions: List[str] = spread["positions"]

        # 每次抽牌都重新取一份完整牌组的深拷贝,避免上一次的剩余状态影响
        deck = list(self._all_cards)
        if len(positions) > len(deck):
            raise ValueError("牌阵需要的牌数超过可用牌数")

        self._rng.shuffle(deck)
        chosen = deck[:len(positions)]

        results: List[Dict[str, Any]] = []
        for position, card in zip(positions, chosen):
            is_upright = self._rng.random() >= 0.5
            orientation = "正位" if is_upright else "逆位"
            keywords = card["upright_keywords"] if is_upright else card["reversed_keywords"]
            results.append({
                "position": position,
                "card_id": card["id"],
                "card_name_cn": card["name_cn"],
                "card_name_en": card["name_en"],
                "arcana": card["arcana"],
                "image": card.get("image", ""),
                "orientation": orientation,
                "is_upright": is_upright,
                "keywords": list(keywords),
                "description": card["description"],
            })
        return results

    @staticmethod
    def render_local_summary(cards: List[Dict[str, Any]]) -> str:
        """没有 API Key 时,用本地数据拼一段兜底解读。"""
        lines: List[str] = []
        for c in cards:
            lines.append(
                f"【{c['position']}】{c['card_name_cn']} · {c['orientation']}\n"
                f"关键词:{ '、'.join(c['keywords']) }\n"
                f"{c['description']}"
            )
        lines.append("\n提示:这是基于本地牌义生成的简版解读。配置 DeepSeek API 可获得更深入的 AI 解牌。")
        return "\n\n".join(lines)
