from typing import Optional
from pydantic import BaseModel, Field

# ==========================================
# 1. 身份与背景相关模块
# ==========================================


class Personality(BaseModel):
    traits: str = Field(default="", description="个性特征")
    ideals: str = Field(default="", description="理念")
    bonds: str = Field(default="", description="羁绊")
    flaws: str = Field(default="", description="缺陷")


class Biography(BaseModel):
    character_name: str = Field(default="未命名英雄")
    player_name: str = Field(default="")
    gender: str = Field(default="")
    age: int = Field(default=20)
    height: str = Field(default="")
    weight: str = Field(default="")
    alignment: str = Field(default="绝对中立")
    faith: str = Field(default="", description="信仰")
    hometown: str = Field(default="", description="故乡")
    background_name: str = Field(default="", description="背景来源(如:农民)")
    backstory: str = Field(default="", description="完整的背景故事")
    personality: Personality = Field(default_factory=Personality)
    languages: list[str] = Field(default_factory=list, description="语言熟练项")
    tool_proficiencies: list[str] = Field(default_factory=list, description="工具熟练项")


# ==========================================
# 2. 职业、种族与特性模块
# ==========================================


class ClassInfo(BaseModel):
    """单个职业的信息"""
    name: str = Field(..., description="职业名称")
    level: int = Field(default=1, ge=1, le=20)
    subclass: str = Field(default="", description="子职业/范型")
    is_primary: bool = Field(default=False, description="是否为起始职业(影响豁免熟练)")
    hit_die: str = Field(default="d8", description="生命骰类型")

class Progression(BaseModel):
    character_class: str = Field(default="战士", description="主职业显示名")
    level: int = Field(default=1, ge=1, le=20, description="总等级")
    classes: list[ClassInfo] = Field(
        default_factory=list,
        description="职业列表，例如 [{'name': '战士', 'level': 2, 'is_primary': True}]",
    )
    race: str = Field(default="人类")
    subrace: str = Field(default="")
    exp: int = Field(default=0, description="当前经验值")


class Feature(BaseModel):
    """特性模块 (涵盖种族特性、职业能力、专长)"""

    name: str = Field(..., description="特性名称")
    source: str = Field(default="职业", description="来源(如: 种族, 德鲁伊Lv2, 专长)")
    description: str = Field(default="", description="特性效果描述")


# ==========================================
# 3. 核心数值相关模块 (属性/技能/豁免/战斗)
# ==========================================


class StatField(BaseModel):
    base_score: int = Field(default=10, description="初始值")
    racial_bonus: int = Field(default=0, description="种族加值")
    asi_bonus: int = Field(default=0, description="成长值 (能力值提升或专长)")
    override: Optional[int] = Field(default=None, description="修正值 (强制锁定值)")
    derived: int = Field(default=10, description="最终计算结果")
    modifier: int = Field(default=0, description="属性调整值")


class SkillField(BaseModel):
    is_proficient: bool = Field(default=False)
    is_expertise: bool = Field(default=False)
    bonus: int = Field(default=0, description="临时修正值")
    override: Optional[int] = Field(default=None)
    derived: int = Field(default=0)


class SaveField(BaseModel):
    is_proficient: bool = Field(default=False)
    bonus: int = Field(default=0, description="临时修正值")
    override: Optional[int] = Field(default=None)
    derived: int = Field(default=0)


class DeathSaves(BaseModel):
    """死亡豁免状态"""

    successes: int = Field(default=0, ge=0, le=3, description="成功次数 (0-3)")
    failures: int = Field(default=0, ge=0, le=3, description="失败次数 (0-3)")


class HitDiceSlot(BaseModel):
    """单种生命骰的消耗状态"""

    total: int = Field(default=0, description="该类型生命骰的最大数量")
    expended: int = Field(default=0, description="已消耗的该类生命骰数量")


class ClassResource(BaseModel):
    """职业特殊资源 (如诗人激励, 气点, 荒野变形)"""
    name: str = Field(..., description="资源名称")
    current: int = Field(default=0)
    max: int = Field(default=0)
    reset_on: str = Field(default="长休", description="恢复周期: 短休, 长休")

class CombatStats(BaseModel):
    # --- 生命值系统 ---
    hp_rolls: list[int] = Field(
        default_factory=list, description="用户填写的每级生命骰掷骰结果，如 [10, 6, 8]"
    )
    bonus_hp_per_level: int = Field(
        default=0, description="每级额外生命加值"
    )
    hp_max: int = Field(default=0)
    hp_current: int = Field(default=0)
    temp_hp: int = Field(default=0)

    # --- 职业资源 ---
    class_resources: list[ClassResource] = Field(
        default_factory=list,
        description="特殊资源列表"
    )

    # --- 短休与濒死 ---
    hit_dice: dict[str, HitDiceSlot] = Field(
        default_factory=dict,
        description="拥有的生命骰池，例如 {'d10': HitDiceSlot(), 'd6': HitDiceSlot()}",
    )
    death_saves: DeathSaves = Field(
        default_factory=DeathSaves, description="死亡豁免记录"
    )

    # --- 其他战斗属性 ---
    armor_class: int = Field(default=10)
    initiative: int = Field(default=0)
    speed: int = Field(default=30)
    proficiency_bonus: int = Field(default=2)


class WeaponItem(BaseModel):
    name: str
    damage_dice: str
    is_finesse: bool = Field(default=False)
    is_proficient: bool = Field(default=True)
    derived_attack_bonus: int = Field(default=0)
    derived_damage_bonus: int = Field(default=0)


class Defenses(BaseModel):
    """防御特性 (抗性、免疫、易伤)"""
    resistances: list[str] = Field(default_factory=list)
    immunities: list[str] = Field(default_factory=list)
    vulnerabilities: list[str] = Field(default_factory=list)
    damage_reduction: int = Field(default=0)


# ==========================================
# 4. 背包与物品模块 (对应"背包.csv")
# ==========================================


class InventoryItem(BaseModel):
    """背包里的单件物品"""

    name: str = Field(..., description="物品名称")
    quantity: int = Field(default=1, description="数量")
    weight: float = Field(default=0.0, description="单件重量(磅)")
    category: str = Field(default="杂物", description="顶级类别: 装备, 消耗品, 杂物")
    item_type: str = Field(default="", description="子类别: 武器, 护甲, 盾牌, 饰品")
    slot_type: str = Field(default="", description="装备槽位: 头部, 躯干, 主手, 副手, 双手, 足部, 戒指, 项链")
    is_equipped: bool = Field(default=False, description="是否已装备")
    description: str = Field(default="", description="描述")


# ==========================================
# 5. 施法与法术书模块 (对应"法术书I/II.csv")
# ==========================================


class Spell(BaseModel):
    """标准化法术属性 (5E 规则)"""

    name: str = Field(..., description="法术名称")
    level: int = Field(default=0, description="法术环阶，0为戏法")
    school: str = Field(default="塑能系", description="法术系别: 防护, 咒法, 预言, 惑控, 塑能, 幻术, 死灵, 变化")
    is_prepared: bool = Field(default=False, description="是否已准备")
    is_always_prepared: bool = Field(default=False, description="是否为恒定准备(不计入限额)")
    override_ability: Optional[str] = Field(default=None, description="覆盖施法属性(如物品赋予)")
    casting_time: str = Field(default="1动作", description="施法时间")
    range: str = Field(default="自身", description="施法距离")
    components: str = Field(default="V, S", description="法术成分 (言语, 姿态, 材料)")
    materials: str = Field(default="", description="法术材料描述")
    duration: str = Field(default="即时", description="持续时间")
    description: str = Field(default="", description="完整的法术说明")


class SpellSlot(BaseModel):
    max_slots: int = Field(default=0, description="最大法术位数量 (自动计算或覆盖)")
    expended: int = Field(default=0, description="已消耗的法术位数 (用于记录当前状态)")
    override: Optional[int] = Field(
        default=None, description="强制覆盖最大法术位数 (如家规或特殊物品)"
    )


class PactMagicSlot(BaseModel):
    """邪术师特有的契约魔法位"""

    level: int = Field(default=0, description="契约魔法的固定环阶")
    max_slots: int = Field(default=0, description="最大法术位数量")
    expended: int = Field(default=0, description="已消耗数量")


class SpellcastingStats(BaseModel):
    ability: str = Field(
        default="wisdom",
        description="施法关键属性 (德鲁伊/牧师为wisdom, 法师为intelligence)",
    )
    spell_save_dc: int = Field(default=8, description="法术豁免DC (8+PB+属性调整值)")
    spell_attack_bonus: int = Field(
        default=0, description="法术攻击加值 (PB+属性调整值)"
    )
    slots: dict[str, SpellSlot] = Field(
        default_factory=lambda: {str(i): SpellSlot() for i in range(1, 10)},
        description="各环阶法术位，键为 '1' 到 '9'",
    )
    pact_magic: PactMagicSlot = Field(
        default_factory=PactMagicSlot, description="契约魔法位状态"
    )
