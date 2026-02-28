import json
from pathlib import Path
from typing import Union, Dict, Any
from src.engine.character_engine import CharacterSheet

class CharacterLoader:
    """
    负责从外部资源（如 JSON 文件）加载并初始化角色数据。
    """

    @staticmethod
    def load_from_json(file_path: Union[str, Path]) -> CharacterSheet:
        """
        从指定路径的 JSON 文件加载角色数据并返回 CharacterSheet 实例。
        """
        path = Path(file_path)
        if not path.exists():
            # 返回一个默认的新人物卡
            return CharacterSheet()

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return CharacterSheet.model_validate(data)
        except Exception as e:
            print(f"Error loading character: {e}")
            return CharacterSheet()

    @staticmethod
    def save_to_json(character: CharacterSheet, file_path: Union[str, Path]):
        """
        将当前角色状态保存到 JSON 文件。
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            # Pydantic v2 use model_dump
            json.dump(character.model_dump(), f, ensure_ascii=False, indent=4)
