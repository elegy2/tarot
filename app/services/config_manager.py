"""配置管理:把用户设置保存为 JSON 文件,放在 user_data_dir。"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional


DEFAULT_CONFIG: Dict[str, Any] = {
    "deepseek_api_key": "",
    "deepseek_base_url": "https://api.deepseek.com",
    "deepseek_model": "deepseek-chat",
    "temperature": 0.8,
    "max_tokens": 1500,
    "save_history": True,
    "theme": "dark_mystic",
    "language": "zh-CN",
}

CONFIG_FILE_NAME = "config.json"
HISTORY_FILE_NAME = "history.json"


class ConfigManager:
    """读写本地 JSON 配置。所有路径基于传入的 base_dir。"""

    def __init__(self, base_dir: str):
        self._base_dir = base_dir
        os.makedirs(self._base_dir, exist_ok=True)
        self._config_path = os.path.join(self._base_dir, CONFIG_FILE_NAME)
        self._history_path = os.path.join(self._base_dir, HISTORY_FILE_NAME)
        self._config: Dict[str, Any] = self._load()

    # ---------- 基础读写 ----------
    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self._config_path):
            self._save_dict(DEFAULT_CONFIG)
            return dict(DEFAULT_CONFIG)
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = dict(DEFAULT_CONFIG)
            merged.update(data)
            return merged
        except (OSError, json.JSONDecodeError):
            # 文件损坏时回到默认值,但不要覆盖,避免丢失用户数据
            return dict(DEFAULT_CONFIG)

    def _save_dict(self, data: Dict[str, Any]) -> None:
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def reload(self) -> None:
        self._config = self._load()

    def save(self) -> None:
        self._save_dict(self._config)

    # ---------- 通用接口 ----------
    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._config[key] = value
        self.save()

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._config)

    # ---------- API Key 便捷方法 ----------
    def get_api_key(self) -> str:
        # 优先从环境变量读取,方便桌面调试,不会落盘
        env_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        if env_key:
            return env_key
        return (self._config.get("deepseek_api_key") or "").strip()

    def has_api_key(self) -> bool:
        return bool(self.get_api_key())

    def set_api_key(self, api_key: str) -> None:
        self.set("deepseek_api_key", api_key.strip())

    def clear_api_key(self) -> None:
        self.set("deepseek_api_key", "")

    @staticmethod
    def mask_api_key(api_key: str) -> str:
        """脱敏展示:sk-****abcd。"""
        api_key = (api_key or "").strip()
        if not api_key:
            return "未配置"
        if len(api_key) <= 8:
            return "****" + api_key[-2:]
        return api_key[:3] + "****" + api_key[-4:]

    # ---------- 历史记录 ----------
    def load_history(self) -> list:
        if not os.path.exists(self._history_path):
            return []
        try:
            with open(self._history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def save_history(self, history: list) -> None:
        with open(self._history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def append_history(self, record: Dict[str, Any]) -> None:
        if not self.get("save_history", True):
            return
        history = self.load_history()
        history.insert(0, record)
        history = history[:200]  # 上限,避免文件膨胀
        self.save_history(history)

    def delete_history_at(self, index: int) -> None:
        history = self.load_history()
        if 0 <= index < len(history):
            history.pop(index)
            self.save_history(history)

    def clear_history(self) -> None:
        self.save_history([])
