"""DeepSeek API 客户端封装。

设计目标:
1. 不在代码中硬编码 API Key。
2. 兼容用户安装的不同版本 openai SDK,在不支持 reasoning_effort/extra_body/timeout 时降级。
3. 出错时返回带分类的异常,UI 层据此显示友好提示。
4. 支持模拟测试(test_connection)。
5. system prompt 明确要求纯文本输出,适合移动端展示。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class DeepSeekError(Exception):
    """所有 DeepSeek 调用相关错误的基类。"""

    def __init__(self, message: str, kind: str = "unknown"):
        super().__init__(message)
        self.kind = kind  # network / auth / timeout / empty / sdk / unknown


@dataclass
class DeepSeekConfig:
    api_key: str
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    temperature: float = 0.8
    max_tokens: int = 1500
    timeout: float = 60.0


SYSTEM_PROMPT = (
    "你是一位专业、温和、富有洞察力的塔罗牌解读师。\n"
    "你的解读风格神秘、优雅、克制,像一位心理咨询式的塔罗师。\n"
    "请使用简体中文回答。\n"
    "请不要使用任何 Markdown 格式。\n"
    "请不要使用井号 # 作为标题。\n"
    "请不要使用星号 * 或下划线 _ 表示加粗或斜体。\n"
    "请不要使用项目符号(- * •)。\n"
    "请不要使用表格、代码块、反引号、分隔线、HTML 标签。\n"
    "请使用自然段和用户提供的中文序号组织内容。\n"
    "每段不要太长,适合手机屏幕阅读,段与段之间空一行。\n"
    "请严格遵守用户消息中给出的输出结构、风格要求与字数要求。\n"
    "不要恐吓用户,不要做绝对化预言,不要使用「必然」「一定会」「无法改变」等说法。\n"
    "请结合用户问题、牌阵位置、牌名、正逆位和关键词进行解读;"
    "牌阵中每张牌的位置含义不同,务必按照「牌位」字段所示语境进行解读,而不是孤立讲牌义。\n"
    "结尾请温和地提醒:塔罗解读仅供参考,重要决定仍需结合现实情况理性判断。\n"
    "若问题涉及医疗、法律、投资或严重心理危机,请提醒寻求相关专业人士的帮助。"
)


def build_user_prompt(question: str, spread: Dict[str, Any],
                      cards: List[Dict[str, Any]]) -> str:
    """根据牌阵元信息(focus / sections / style_hints / length_hint)
    动态拼装用户 prompt。

    spread 至少需要包含 name 字段;若缺少 prompt 相关字段,会回退到通用结构。
    """
    if not (question or "").strip():
        question = "今日指引:请给我一段属于今天的能量提示。"

    spread_name = spread.get("name", "塔罗牌阵")
    focus = (spread.get("focus") or "").strip()
    sections = spread.get("sections") or []
    style_hints = (spread.get("style_hints") or "").strip()
    length_hint = (
        spread.get("length_hint")
        or "总长度控制在 900 到 1400 个中文字符之间。"
    )

    lines: List[str] = []
    lines.append("用户问题:")
    lines.append(question.strip())
    lines.append("")
    lines.append(f"牌阵名称:{spread_name}")
    if focus:
        lines.append(f"本牌阵的解读重点:{focus}")
    lines.append("")
    lines.append("抽牌结果:")
    for idx, card in enumerate(cards, start=1):
        kw = "、".join(card.get("keywords", []))
        lines.append(f"{idx}. 牌位:{card['position']}")
        lines.append(f"   牌名:{card['card_name_cn']} {card['card_name_en']}")
        lines.append(f"   状态:{card['orientation']}")
        lines.append(f"   关键词:{kw}")
        lines.append(f"   基础牌义:{card['description']}")
    lines.append("")

    if sections:
        lines.append("请按照以下结构输出纯文本解读,使用中文序号,段落之间用空行分隔:")
        for idx_cn, title, hint in sections:
            if hint:
                lines.append(f"{idx_cn}、{title}({hint})")
            else:
                lines.append(f"{idx_cn}、{title}")
    else:
        lines.append("请按照以下结构输出纯文本解读,使用中文序号,段落之间用空行分隔:")
        lines.append("一、整体能量")
        lines.append("二、每张牌的提示")
        lines.append("三、牌与牌之间的关系")
        lines.append("四、针对问题的回答")
        lines.append("五、行动建议")
        lines.append("六、温和提醒")

    lines.append("")
    if style_hints:
        lines.append(f"风格要求:{style_hints}")
    lines.append("")
    lines.append("请注意:")
    lines.append("不要使用 Markdown。")
    lines.append("不要使用项目符号。")
    lines.append("不要使用表格。")
    lines.append("不要使用代码块。")
    lines.append(length_hint)
    return "\n".join(lines)


class DeepSeekClient:
    def __init__(self, config: DeepSeekConfig):
        if not config.api_key:
            raise DeepSeekError("未配置 API Key", kind="auth")
        self._config = config
        self._client = self._build_client()

    def _build_client(self):
        try:
            from openai import OpenAI
        except ImportError as e:
            raise DeepSeekError(
                "未安装 openai 库,请先执行 pip install openai", kind="sdk"
            ) from e

        try:
            return OpenAI(
                api_key=self._config.api_key,
                base_url=self._config.base_url,
                timeout=self._config.timeout,
            )
        except TypeError:
            return OpenAI(
                api_key=self._config.api_key,
                base_url=self._config.base_url,
            )

    # ---------- 公开方法 ----------
    def test_connection(self) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "ping"},
        ]
        text = self._chat(messages, max_tokens=16)
        return text or "ok"

    def interpret_tarot(self, question: str,
                        spread: Dict[str, Any] | str,
                        cards: List[Dict[str, Any]]) -> str:
        """生成解读。spread 可以是完整 dict(推荐)或仅 name 字符串(向后兼容)。

        若 spread 是 dict 且声明了 recommended_max_tokens,会自动把
        max_tokens 上抬到该下限,避免凯尔特十字这种长牌阵被截断。
        """
        if isinstance(spread, str):
            spread = {"name": spread}

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": build_user_prompt(question, spread, cards)},
        ]
        max_tokens = self._config.max_tokens
        rec = spread.get("recommended_max_tokens")
        if isinstance(rec, int) and rec > max_tokens:
            max_tokens = rec
        return self._chat(messages, max_tokens=max_tokens)

    # ---------- 内部 ----------
    def _chat(self, messages: List[Dict[str, str]],
              max_tokens: Optional[int] = None) -> str:
        kwargs: Dict[str, Any] = {
            "model": self._config.model,
            "messages": messages,
            "stream": False,
            "temperature": self._config.temperature,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        response = None
        # 1) 尝试带 reasoning_effort + extra_body + timeout
        try:
            response = self._client.chat.completions.create(
                **kwargs,
                reasoning_effort="high",
                extra_body={"thinking": {"type": "enabled"}},
                timeout=self._config.timeout,
            )
        except TypeError:
            response = None
        except Exception as e:  # noqa: BLE001
            # 不是参数不兼容,而是真实调用错误,直接分类
            raise self._classify(e) from e

        # 2) 去掉 timeout 试一次
        if response is None:
            try:
                response = self._client.chat.completions.create(
                    **kwargs,
                    reasoning_effort="high",
                    extra_body={"thinking": {"type": "enabled"}},
                )
            except TypeError:
                response = None
            except Exception as e:  # noqa: BLE001
                raise self._classify(e) from e

        # 3) 去掉 thinking 相关参数,最朴素的调用
        if response is None:
            try:
                response = self._client.chat.completions.create(**kwargs)
            except Exception as e:  # noqa: BLE001
                raise self._classify(e) from e

        try:
            content = response.choices[0].message.content or ""
        except (AttributeError, IndexError) as e:
            raise DeepSeekError("API 返回内容无法解析", kind="empty") from e

        content = content.strip()
        if not content:
            raise DeepSeekError("API 返回了空内容,请稍后重试", kind="empty")
        return content

    @staticmethod
    def _classify(err: Exception) -> DeepSeekError:
        msg = str(err)
        lower = msg.lower()
        if ("apikey" in lower or "api key" in lower
                or "unauthorized" in lower or "401" in lower):
            return DeepSeekError("API Key 无效或未授权,请检查后重试。", kind="auth")
        if "timeout" in lower or "timed out" in lower:
            return DeepSeekError("请求超时,请检查网络后重试。", kind="timeout")
        if ("connection" in lower or "network" in lower
                or "name or service" in lower):
            return DeepSeekError("网络异常,无法连接到 DeepSeek 服务。",
                                 kind="network")
        if ("balance" in lower or "quota" in lower
                or "insufficient" in lower):
            return DeepSeekError("账户额度不足,请前往 DeepSeek 充值后再试。",
                                 kind="auth")
        return DeepSeekError(f"调用失败:{msg}", kind="unknown")
