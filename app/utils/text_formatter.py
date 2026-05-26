"""AI 解读文本清理工具。

DeepSeek 即使被要求纯文本也偶尔会输出 Markdown 标记,
本模块负责"展示层"的清理,不改变中文语义。

只做最小必要清理:
- 代码块 ```...```
- 行首 # 标题
- 加粗/斜体 ** __ * _
- 项目符号 - * • 在行首
- 表格分隔 | 替换为空格
- 多余空行收缩为最多两行
- HTML 标签去掉
"""
from __future__ import annotations

import re

from typing import List


_CODE_BLOCK_RE = re.compile(r"```.*?```", flags=re.S)
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s*", flags=re.M)
_BULLET_RE = re.compile(r"^\s*[-•*]\s+", flags=re.M)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_TABLE_SEP_RE = re.compile(r"^[\s\-|:]+$", flags=re.M)
_MULTI_BLANK_RE = re.compile(r"\n{3,}")
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")


def sanitize_ai_text(text: str) -> str:
    """清理 AI 输出中不适合 App 展示的 Markdown 符号。

    不改变主要语义,只做展示层清理。空字符串安全返回。
    """
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 删除三反引号代码块及孤立反引号
    text = _CODE_BLOCK_RE.sub("", text)
    text = text.replace("```", "")
    # 行内代码 `xxx` -> xxx
    text = _INLINE_CODE_RE.sub(r"\1", text)

    # 行首井号标题
    text = _HEADING_RE.sub("", text)

    # 加粗 / 斜体
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("*", "")
    text = text.replace("_", "")

    # 项目符号(行首) -> 直接去掉,中文阅读不需要项目符号
    text = _BULLET_RE.sub("", text)

    # Markdown 表格分隔行(纯 |、-、:、空格组成)整行删
    text = _TABLE_SEP_RE.sub("", text)
    # 单元格分隔竖线替换为两个空格
    text = text.replace("|", "  ")

    # HTML 标签
    text = _HTML_TAG_RE.sub("", text)

    # 收缩多余空行
    text = _MULTI_BLANK_RE.sub("\n\n", text)

    return text.strip()


def split_paragraphs(text: str) -> List[str]:
    """按空行拆段,便于前端用多个 Label 渲染长文本。

    空字符串返回空列表;尾随空白被 strip。
    """
    if not text:
        return []
    parts = re.split(r"\n\s*\n", text.strip())
    return [p.strip() for p in parts if p.strip()]
