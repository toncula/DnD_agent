<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';
import { RefreshCw, CheckCircle2, UserCircle, Swords, BookOpen } from 'lucide-vue-next';

import RpPage from './character/pages/RpPage.vue';
import CombatPage from './character/pages/CombatPage.vue';
import SpellbookPage from './character/pages/SpellbookPage.vue';

const props = defineProps<{
  initialData: any; 
}>();

const emit = defineEmits(['update']);

const tabs = [
  { id: 'rp', label: 'RP 背景', icon: UserCircle },
  { id: 'combat', label: '战斗核心', icon: Swords },
  { id: 'spellbook', label: '法术书', icon: BookOpen }
];
const currentTab = ref('rp');

// 1. 本地状态副本
const localData = ref(JSON.parse(JSON.stringify(props.initialData)));
const syncStatus = ref<'saved' | 'syncing' | 'error'>('saved');

// 2. 标志位，防止同步循环
let isIncomingUpdate = false;
let timeoutId: number | undefined;

const handlePageUpdate = (partialData: any) => {
  // Merge partial updates into localData
  for (const key in partialData) {
    localData.value[key] = partialData[key];
  }
};

const performSync = () => {
  if (isIncomingUpdate) return;
  syncStatus.value = 'syncing';
  
  const dataToSend = JSON.parse(JSON.stringify(localData.value));
  const currentLevel = dataToSend.prog.level || 1;
  const pb = Math.floor((currentLevel - 1) / 4) + 2;

  // 1. 前端自动计算属性与调整值
  const stats = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'];
  const saveMapping: Record<string, string> = {
    strength: 'str_save', dexterity: 'dex_save', constitution: 'con_save',
    intelligence: 'int_save', wisdom: 'wis_save', charisma: 'cha_save'
  };

  stats.forEach(s => {
    const stat = dataToSend[s];
    stat.derived = (stat.base_score || 0) + (stat.racial_bonus || 0) + (stat.asi_bonus || 0) + (stat.bonus || 0);
    stat.modifier = Math.floor((stat.derived - 10) / 2);
    
    const saveKey = saveMapping[s];
    if (dataToSend[saveKey]) {
      const save = dataToSend[saveKey];
      save.derived = stat.modifier + (save.is_proficient ? pb : 0) + (save.bonus || 0);
    }
  });

  // 1.5 新增：计算技能检定值
  const skillToStat: Record<string, string> = {
    athletics: 'strength',
    acrobatics: 'dexterity', sleight_of_hand: 'dexterity', stealth: 'dexterity',
    arcana: 'intelligence', history: 'intelligence', investigation: 'intelligence', nature: 'intelligence', religion: 'intelligence',
    animal_handling: 'wisdom', insight: 'wisdom', medicine: 'wisdom', perception: 'wisdom', survival: 'wisdom',
    deception: 'charisma', intimidation: 'charisma', performance: 'charisma', persuasion: 'charisma'
  };

  // 1.7 新增：5E 兼职施法计算引擎
  const fullCasters = ['法师', '牧师', '德鲁伊', '吟游诗人', '术士'];
  const halfCasters = ['圣武士', '游侠'];
  const thirdCasters = ['奥法骑士', '诡术随从'];
  
  let effectiveLevel = 0;
  let pactLevel = 0;
  let primaryCasterAbility = dataToSend.spellcasting?.ability || 'wisdom';

  // 核心修复：锁定主职业显示名
  const primaryClassObj = dataToSend.prog.classes.find((c: any) => c.is_primary) || dataToSend.prog.classes[0];
  if (primaryClassObj) {
    dataToSend.prog.character_class = primaryClassObj.name;
  }

  dataToSend.prog.classes.forEach((c: any) => {
    if (fullCasters.includes(c.name)) effectiveLevel += c.level;
    else if (halfCasters.includes(c.name)) effectiveLevel += Math.floor(c.level / 2);
    else if (thirdCasters.includes(c.name)) effectiveLevel += Math.floor(c.level / 3);
    else if (c.name === '人造师') effectiveLevel += Math.ceil(c.level / 2);
    else if (c.name === '邪术师') pactLevel = c.level;
    
    // 如果是首选职业且有施法能力，更新施法属性
    if (c.is_primary && (fullCasters.includes(c.name) || c.name === '邪术师' || halfCasters.includes(c.name))) {
       const abilityMap: Record<string, string> = { '法师': 'intelligence', '牧师': 'wisdom', '德鲁伊': 'wisdom', '术士': 'charisma', '吟游诗人': 'charisma', '圣武士': 'charisma', '邪术师': 'charisma' };
       primaryCasterAbility = abilityMap[c.name] || 'wisdom';
    }
  });

  // 标准施法位查找表 (1-20级)
  const slotTable: Record<number, number[]> = {
    1: [2], 2: [3], 3: [4, 2], 4: [4, 3], 5: [4, 3, 2], 6: [4, 3, 3], 7: [4, 3, 3, 1], 8: [4, 3, 3, 2], 
    9: [4, 3, 3, 3, 1], 10: [4, 3, 3, 3, 2], 11: [4, 3, 3, 3, 2, 1], 12: [4, 3, 3, 3, 2, 1],
    13: [4, 3, 3, 3, 2, 1, 1], 14: [4, 3, 3, 3, 2, 1, 1], 15: [4, 3, 3, 3, 2, 1, 1, 1], 16: [4, 3, 3, 3, 2, 1, 1, 1],
    17: [4, 3, 3, 3, 2, 1, 1, 1, 1], 18: [4, 3, 3, 3, 3, 1, 1, 1, 1], 19: [4, 3, 3, 3, 3, 2, 1, 1, 1], 20: [4, 3, 3, 3, 3, 2, 2, 1, 1]
  };

  const counts = effectiveLevel > 0 ? (slotTable[Math.min(20, effectiveLevel)] || []) : [];
  
  // 核心修复：遍历 1-9 环，确保所有位都被更新或重置为 0
  for (let i = 1; i <= 9; i++) {
    const lv = i.toString();
    if (dataToSend.spellcasting.slots[lv]) {
      dataToSend.spellcasting.slots[lv].max_slots = i <= counts.length ? counts[i - 1] : 0;
      // 如果上限被重置为 0，消耗量也应当归零
      if (dataToSend.spellcasting.slots[lv].max_slots === 0) {
        dataToSend.spellcasting.slots[lv].expended = 0;
      }
    }
  }

  // 计算施法 DC 和 攻击加值
  const castMod = dataToSend[primaryCasterAbility]?.modifier || 0;
  dataToSend.spellcasting.ability = primaryCasterAbility;
  dataToSend.spellcasting.spell_save_dc = 8 + pb + castMod;
  dataToSend.spellcasting.spell_attack_bonus = pb + castMod;

  // 2. 计算 HP Max
  const conMod = dataToSend.constitution.modifier;
  const hpRolls = dataToSend.combat?.hp_rolls || [];
  const primaryClass = dataToSend.prog.classes?.find((c: any) => c.is_primary) || dataToSend.prog.classes?.[0];
  const hdValue = parseInt(primaryClass?.hit_die?.replace('d', '') || '8');
  
  let calculatedHP = (hpRolls[0] || hdValue) + conMod;
  for (let i = 1; i < currentLevel; i++) {
    const roll = hpRolls[i] || Math.floor(hdValue / 2) + 1;
    calculatedHP += (roll + conMod);
  }
  calculatedHP += (dataToSend.combat.bonus_hp_per_level || 0) * currentLevel;
  
  // 更新本地展示 (wrap with flag to prevent loop)
  isIncomingUpdate = true;
  dataToSend.combat.hp_max = calculatedHP;
  dataToSend.combat.proficiency_bonus = pb;
  Object.assign(localData.value, dataToSend);
  // 使用 nextTick 或确保在下一轮事件循环前恢复
  setTimeout(() => { isIncomingUpdate = false; }, 50);

  // 3. 截断 hp_rolls 发送给后端
  if (dataToSend.combat?.hp_rolls) {
    let rolls = dataToSend.combat.hp_rolls.map((v: any) => parseInt(v) || 0);
    if (rolls.length > currentLevel) rolls = rolls.slice(0, currentLevel);
    else while (rolls.length < currentLevel) rolls.push(0);
    dataToSend.combat.hp_rolls = rolls;
  }
  
  emit('update', dataToSend);
  
  setTimeout(() => {
    if (syncStatus.value === 'syncing') syncStatus.value = 'saved';
  }, 1000);
};

// 监听本地所有修改
watch(localData, () => {
  if (isIncomingUpdate) return;
  syncStatus.value = 'syncing';
  if (timeoutId) clearTimeout(timeoutId);
  timeoutId = window.setTimeout(performSync, 1200);
}, { deep: true });

// 关键修复 2：监听外部 props 变化，回填后端算好的 hp_max 等字段
watch(() => props.initialData, (newData) => {
  if (!newData) return;
  isIncomingUpdate = true;
  
  // 只同步后端计算出的派生数值，不覆盖用户正在输入的字段
  if (localData.value.combat && newData.combat) {
    localData.value.combat.hp_max = newData.combat.hp_max;
    localData.value.combat.armor_class = newData.combat.armor_class;
    localData.value.combat.initiative = newData.combat.initiative;
    localData.value.combat.proficiency_bonus = newData.combat.proficiency_bonus;
  }
  
  // 同步属性调整值
  const stats = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'];
  stats.forEach(s => {
    if (localData.value[s] && newData[s]) {
      localData.value[s].modifier = newData[s].modifier;
      localData.value[s].derived = newData[s].derived;
    }
  });

  isIncomingUpdate = false;
}, { deep: true });

onUnmounted(() => {
  if (timeoutId) clearTimeout(timeoutId);
});
</script>

<template>
  <div class="character-sheet-container pb-20 relative">
    <!-- 同步指示灯 -->
    <div class="fixed top-6 right-8 z-50 transition-all duration-500" :class="syncStatus === 'saved' ? 'opacity-0 translate-y-[-10px]' : 'opacity-100 translate-y-0'">
      <div 
        class="flex items-center gap-2 px-4 py-2 rounded-full bg-zinc-900 border border-white/10 shadow-2xl"
        :class="syncStatus === 'syncing' ? 'text-amber-400' : 'text-emerald-400'"
      >
        <RefreshCw v-if="syncStatus === 'syncing'" class="w-4 h-4 animate-spin" />
        <CheckCircle2 v-else class="w-4 h-4" />
        <span class="text-xs font-black uppercase tracking-widest">
          {{ syncStatus === 'syncing' ? '同步中...' : '已同步' }}
        </span>
      </div>
    </div>

    <!-- 顶部标签导航 -->
    <div class="flex gap-2 mb-6 bg-zinc-900/50 p-1.5 rounded-2xl border border-zinc-800">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="currentTab = tab.id"
        class="flex-1 py-3 px-4 rounded-xl flex items-center justify-center gap-2 text-sm font-bold transition-all duration-300"
        :class="currentTab === tab.id 
          ? 'bg-zinc-800 text-white shadow-lg border border-zinc-700' 
          : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/50'"
      >
        <component :is="tab.icon" class="w-5 h-5" />
        {{ tab.label }}
      </button>
    </div>

    <div class="tab-content transition-all duration-300">
      <RpPage 
        v-if="currentTab === 'rp'" 
        :sheet="localData" 
        @update="handlePageUpdate" 
      />
      <CombatPage 
        v-else-if="currentTab === 'combat'" 
        :sheet="localData" 
        @update="handlePageUpdate" 
      />
      <SpellbookPage 
        v-else-if="currentTab === 'spellbook'" 
        :sheet="localData" 
        @update="handlePageUpdate" 
      />
    </div>
  </div>
</template>

<style scoped>
input, textarea { transition: none !important; }
</style>
