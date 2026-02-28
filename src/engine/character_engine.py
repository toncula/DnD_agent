import sys
from pathlib import Path

# --- 关键修复：将项目根目录添加到系统路径中 ---
# character_engine.py 在 src/engine/ 目录下，向上两级即为项目根目录
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

import math
from typing import Dict, List
from pydantic import BaseModel, Field, model_validator

# 引入拆分后的数据模型组件
from src.engine.models import (
    Biography,
    Personality,
    Progression,
    Feature,
    StatField,
    SkillField,
    SaveField,
    CombatStats,
    WeaponItem,
    InventoryItem,
    Spell,
    SpellcastingStats,
    HitDiceSlot,
    DeathSaves,
    Defenses,
)


def calculate_max_spell_slots(class_levels: dict) -> dict:
    """
    核心算法：根据 D&D 5E 规则计算兼职施法者的法术位。
    包含单职业向上取整、兼职向下取整、奇械师特殊向上取整、以及独立的邪术师契约魔法逻辑。
    """
    FULL_CASTERS = {"诗人", "吟游诗人", "牧师", "德鲁伊", "术士", "法师"}
    HALF_CASTERS = {"圣武士", "游侠"}
    ARTIFICER = {"奇械师"}
    THIRD_CASTERS = {"奥法骑士", "战士(奥法骑士)", "诡术师", "游荡者(诡术师)"}
    WARLOCK = {"邪术师", "契约者"}

    # 1-20级的标准施法者法术位表
    STANDARD_SLOTS = [
        [0] * 9,  # 0级 (兜底)
        [2, 0, 0, 0, 0, 0, 0, 0, 0],
        [3, 0, 0, 0, 0, 0, 0, 0, 0],
        [4, 2, 0, 0, 0, 0, 0, 0, 0],
        [4, 3, 0, 0, 0, 0, 0, 0, 0],
        [4, 3, 2, 0, 0, 0, 0, 0, 0],
        [4, 3, 3, 0, 0, 0, 0, 0, 0],
        [4, 3, 3, 1, 0, 0, 0, 0, 0],
        [4, 3, 3, 2, 0, 0, 0, 0, 0],
        [4, 3, 3, 3, 1, 0, 0, 0, 0],
        [4, 3, 3, 3, 2, 0, 0, 0, 0],
        [4, 3, 3, 3, 2, 1, 0, 0, 0],
        [4, 3, 3, 3, 2, 1, 0, 0, 0],
        [4, 3, 3, 3, 2, 1, 1, 0, 0],
        [4, 3, 3, 3, 2, 1, 1, 0, 0],
        [4, 3, 3, 3, 2, 1, 1, 1, 0],
        [4, 3, 3, 3, 2, 1, 1, 1, 0],
        [4, 3, 3, 3, 2, 1, 1, 1, 1],
        [4, 3, 3, 3, 3, 1, 1, 1, 1],
        [4, 3, 3, 3, 3, 2, 1, 1, 1],
        [4, 3, 3, 3, 3, 2, 2, 1, 1],
    ]

    # 邪术师契约魔法表 (数量, 环阶)
    PACT_MAGIC_SLOTS = {
        1: (1, 1),
        2: (2, 1),
        3: (2, 2),
        4: (2, 2),
        5: (2, 3),
        6: (2, 3),
        7: (2, 4),
        8: (2, 4),
        9: (2, 5),
        10: (2, 5),
        11: (3, 5),
        12: (3, 5),
        13: (3, 5),
        14: (3, 5),
        15: (3, 5),
        16: (3, 5),
        17: (4, 5),
        18: (4, 5),
        19: (4, 5),
        20: (4, 5),
    }

    standard_caster_classes = {}
    pact_magic_level = 0

    # 职业分组与分类
    for cls_name, lvl in class_levels.items():
        if any(w in cls_name for w in WARLOCK):
            pact_magic_level += lvl
        else:
            is_caster = any(
                any(c in cls_name for c in group)
                for group in [FULL_CASTERS, HALF_CASTERS, ARTIFICER, THIRD_CASTERS]
            )
            if is_caster:
                standard_caster_classes[cls_name] = lvl

    standard_slots = [0] * 9
    if len(standard_caster_classes) == 1:
        # 单一施法职业，采用独立的向上取整逻辑
        cls_name, lvl = list(standard_caster_classes.items())[0]
        ecl = 0
        if any(c in cls_name for c in FULL_CASTERS):
            ecl = lvl
        elif any(c in cls_name for c in ARTIFICER):
            ecl = math.ceil(lvl / 2)
        elif any(c in cls_name for c in HALF_CASTERS):
            ecl = math.ceil(lvl / 2) if lvl >= 2 else 0
        elif any(c in cls_name for c in THIRD_CASTERS):
            ecl = math.ceil(lvl / 3) if lvl >= 3 else 0
        standard_slots = STANDARD_SLOTS[min(ecl, 20)]

    elif len(standard_caster_classes) > 1:
        # 兼职施法职业，采用向下取整累计公式
        ecl = 0
        for cls_name, lvl in standard_caster_classes.items():
            if any(c in cls_name for c in FULL_CASTERS):
                ecl += lvl
            elif any(c in cls_name for c in ARTIFICER):
                ecl += math.ceil(lvl / 2)  # 奇械师特殊：永远向上取整
            elif any(c in cls_name for c in HALF_CASTERS):
                ecl += math.floor(lvl / 2)
            elif any(c in cls_name for c in THIRD_CASTERS):
                ecl += math.floor(lvl / 3)
        standard_slots = STANDARD_SLOTS[min(ecl, 20)]

    pact_slots = None
    if pact_magic_level > 0:
        count, level = PACT_MAGIC_SLOTS.get(pact_magic_level, (0, 0))
        pact_slots = {"count": count, "level": level}

    return {"standard_slots": standard_slots, "pact_magic": pact_slots}


# ==========================================
# 完整人物卡结构 (Character Sheet Schema)
# ==========================================
class CharacterSheet(BaseModel):
    """D&D 5E 完整人物卡聚合根"""

    bio: Biography = Field(default_factory=Biography)
    prog: Progression = Field(default_factory=Progression)

    # --- 核心属性 ---
    strength: StatField = Field(default_factory=StatField)
    dexterity: StatField = Field(default_factory=StatField)
    constitution: StatField = Field(default_factory=StatField)
    intelligence: StatField = Field(default_factory=StatField)
    wisdom: StatField = Field(default_factory=StatField)
    charisma: StatField = Field(default_factory=StatField)

    # --- 豁免判定 (Saving Throws) ---
    str_save: SaveField = Field(default_factory=SaveField)
    dex_save: SaveField = Field(default_factory=SaveField)
    con_save: SaveField = Field(default_factory=SaveField)
    int_save: SaveField = Field(default_factory=SaveField)
    wis_save: SaveField = Field(default_factory=SaveField)
    cha_save: SaveField = Field(default_factory=SaveField)

    # --- 技能 (Skills) ---
    athletics: SkillField = Field(default_factory=SkillField)
    acrobatics: SkillField = Field(default_factory=SkillField)
    sleight_of_hand: SkillField = Field(default_factory=SkillField)
    stealth: SkillField = Field(default_factory=SkillField)
    arcana: SkillField = Field(default_factory=SkillField)
    history: SkillField = Field(default_factory=SkillField)
    investigation: SkillField = Field(default_factory=SkillField)
    nature: SkillField = Field(default_factory=SkillField)
    religion: SkillField = Field(default_factory=SkillField)
    animal_handling: SkillField = Field(default_factory=SkillField)
    insight: SkillField = Field(default_factory=SkillField)
    medicine: SkillField = Field(default_factory=SkillField)
    perception: SkillField = Field(default_factory=SkillField)
    survival: SkillField = Field(default_factory=SkillField)
    deception: SkillField = Field(default_factory=SkillField)
    intimidation: SkillField = Field(default_factory=SkillField)
    performance: SkillField = Field(default_factory=SkillField)
    persuasion: SkillField = Field(default_factory=SkillField)

    # --- 战斗与装备 ---
    combat: CombatStats = Field(default_factory=CombatStats)
    equipped_armor_base_ac: int = Field(default=0)
    has_shield: bool = Field(default=False)
    weapons: List[WeaponItem] = Field(default_factory=list)

    # --- [新增] 特性、背包与施法系统 ---
    features: List[Feature] = Field(
        default_factory=list, description="职业能力/种族特性/专长"
    )

    inventory: List[InventoryItem] = Field(default_factory=list, description="背包物品")
    total_weight: float = Field(default=0.0, description="当前背包总重量 (自动计算)")
    carrying_capacity: float = Field(default=0.0, description="最大负重能力 (自动计算)")

    spells: List[Spell] = Field(default_factory=list, description="法术书/已知法术")
    spellcasting: SpellcastingStats = Field(
        default_factory=SpellcastingStats, description="施法面板"
    )

    # ==========================================
    # 核心计算引擎 (The Reactive Engine)
    # ==========================================

    @model_validator(mode="after")
    def calculate_derived_stats(self) -> "CharacterSheet":
        # 1. 计算熟练加值 (PB)
        self.combat.proficiency_bonus = math.ceil(self.prog.level / 4) + 1
        pb = self.combat.proficiency_bonus

        # 2. 计算六维属性
        ability_map = {
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
        }
        for name, stat in ability_map.items():
            calculated_base = stat.base_score + stat.racial_bonus + stat.asi_bonus
            if stat.override is not None:
                stat.derived = stat.override
            else:
                stat.derived = calculated_base
            stat.modifier = math.floor((stat.derived - 10) / 2)

        # 3. 计算豁免判定
        self._calc_save(self.str_save, self.strength.modifier, pb)
        self._calc_save(self.dex_save, self.dexterity.modifier, pb)
        self._calc_save(self.con_save, self.constitution.modifier, pb)
        self._calc_save(self.int_save, self.intelligence.modifier, pb)
        self._calc_save(self.wis_save, self.wisdom.modifier, pb)
        self._calc_save(self.cha_save, self.charisma.modifier, pb)

        # 4. 计算 AC 和 先攻
        self.combat.initiative = self.dexterity.modifier
        base_ac = self.equipped_armor_base_ac if self.equipped_armor_base_ac > 0 else 10
        shield_bonus = 2 if self.has_shield else 0
        dex_bonus = (
            self.dexterity.modifier
            if self.equipped_armor_base_ac == 0
            else min(2, self.dexterity.modifier)
        )
        if self.equipped_armor_base_ac >= 15:
            dex_bonus = 0
        self.combat.armor_class = base_ac + dex_bonus + shield_bonus

        # 5. 计算完整的 18 项技能
        self._calc_skill(self.athletics, self.strength.modifier, pb)
        self._calc_skill(self.acrobatics, self.dexterity.modifier, pb)
        self._calc_skill(self.sleight_of_hand, self.dexterity.modifier, pb)
        self._calc_skill(self.stealth, self.dexterity.modifier, pb)
        self._calc_skill(self.arcana, self.intelligence.modifier, pb)
        self._calc_skill(self.history, self.intelligence.modifier, pb)
        self._calc_skill(self.investigation, self.intelligence.modifier, pb)
        self._calc_skill(self.nature, self.intelligence.modifier, pb)
        self._calc_skill(self.religion, self.intelligence.modifier, pb)
        self._calc_skill(self.animal_handling, self.wisdom.modifier, pb)
        self._calc_skill(self.insight, self.wisdom.modifier, pb)
        self._calc_skill(self.medicine, self.wisdom.modifier, pb)
        self._calc_skill(self.perception, self.wisdom.modifier, pb)
        self._calc_skill(self.survival, self.wisdom.modifier, pb)
        self._calc_skill(self.deception, self.charisma.modifier, pb)
        self._calc_skill(self.intimidation, self.charisma.modifier, pb)
        self._calc_skill(self.performance, self.charisma.modifier, pb)
        self._calc_skill(self.persuasion, self.charisma.modifier, pb)

        # 6. 计算武器攻击加值
        for weapon in self.weapons:
            use_modifier = self.strength.modifier
            if weapon.is_finesse and self.dexterity.modifier > self.strength.modifier:
                use_modifier = self.dexterity.modifier

            atk_bonus = use_modifier
            if weapon.is_proficient:
                atk_bonus += pb
            weapon.derived_attack_bonus = atk_bonus
            weapon.derived_damage_bonus = use_modifier

        # --- [新增] 7. 负重计算逻辑 ---
        # 遍历背包，总重量 = 单件重量 * 数量
        self.total_weight = sum(item.weight * item.quantity for item in self.inventory)
        # 5e 标准规则：最大负重(磅) = 力量最终值 * 15
        self.carrying_capacity = self.strength.derived * 15

        # --- [新增] 8. 施法面板计算逻辑 ---
        # 自动提取施法关键属性的调整值 (德鲁伊是感知 Wisdom)
        caster_stat = ability_map.get(self.spellcasting.ability)
        if caster_stat:
            # 豁免DC = 8 + 熟练加值 + 关键属性调整值
            self.spellcasting.spell_save_dc = 8 + pb + caster_stat.modifier
            # 攻击加值 = 熟练加值 + 关键属性调整值
            self.spellcasting.spell_attack_bonus = pb + caster_stat.modifier

        # --- [修改] 9. 支持兼职的全系法术位自动推算 ---
        # 如果没有显式配置兼职字典，使用主职业构建字典
        current_classes = self.prog.classes
        if not current_classes:
            current_classes = {self.prog.character_class: self.prog.level}

        slots_data = calculate_max_spell_slots(current_classes)

        # 填充标准法术位
        standard_array = slots_data["standard_slots"]
        for i in range(9):
            lvl_str = str(i + 1)
            slot_obj = self.spellcasting.slots[lvl_str]
            if slot_obj.override is not None:
                slot_obj.max_slots = slot_obj.override
            else:
                slot_obj.max_slots = standard_array[i]

        # 填充契约魔法位
        pact_data = slots_data["pact_magic"]
        if pact_data:
            self.spellcasting.pact_magic.level = pact_data["level"]
            self.spellcasting.pact_magic.max_slots = pact_data["count"]

        # --- [新增] 10. 生命上限与生命骰池计算 ---
        total_level = self.prog.level
        con_mod = self.constitution.modifier

        # 计算生命上限 = 掷骰总和 + (体质调整值 * 总等级) + (每级额外生命 * 总等级)
        calculated_hp_max = (
            sum(self.combat.hp_rolls)
            + (con_mod * total_level)
            + (self.combat.bonus_hp_per_level * total_level)
        )
        self.combat.hp_max = max(1, calculated_hp_max)  # 最少为1

        # 自动推演生命骰池 (根据兼职字典)
        HD_MAP = {
            "法师": "d6",
            "术士": "d6",
            "诗人": "d8",
            "吟游诗人": "d8",
            "牧师": "d8",
            "德鲁伊": "d8",
            "武僧": "d8",
            "游荡者": "d8",
            "邪术师": "d8",
            "契约者": "d8",
            "奇械师": "d8",
            "战士": "d10",
            "圣武士": "d10",
            "游侠": "d10",
            "野蛮人": "d12",
        }

        new_hd_totals = {}
        for cls_name, lvl in current_classes.items():
            hd_type = "d8"  # 默认兜底
            for key, val in HD_MAP.items():
                if key in cls_name:
                    hd_type = val
                    break
            new_hd_totals[hd_type] = new_hd_totals.get(hd_type, 0) + lvl

        # 更新到模型中，同时保护已经记录的 expended 消耗值不被重置
        for hd_type, total in new_hd_totals.items():
            if hd_type not in self.combat.hit_dice:
                self.combat.hit_dice[hd_type] = HitDiceSlot(total=total, expended=0)
            else:
                self.combat.hit_dice[hd_type].total = total

        # 清除已被遗忘/洗点的职业生命骰
        keys_to_remove = [
            k for k in self.combat.hit_dice.keys() if k not in new_hd_totals
        ]
        for k in keys_to_remove:
            del self.combat.hit_dice[k]

        return self

    def _calc_skill(self, skill: SkillField, ability_mod: int, pb: int):
        if skill.override is not None:
            skill.derived = skill.override
            return
        total_bonus = ability_mod + skill.bonus
        if skill.is_proficient:
            total_bonus += pb
        if skill.is_expertise:
            total_bonus += pb
        skill.derived = total_bonus

    def _calc_save(self, save: SaveField, ability_mod: int, pb: int):
        if save.override is not None:
            save.derived = save.override
            return
        total_bonus = ability_mod + save.bonus
        if save.is_proficient:
            total_bonus += pb
        save.derived = total_bonus
