<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';
import { RefreshCw, CheckCircle2, UserCircle, Swords, BookOpen, Lock } from 'lucide-vue-next';

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

// 1. 本地状态副本 (带结构平滑转换)
const initDataStructure = (data: any) => {
  const d = JSON.parse(JSON.stringify(data));
  if (!d.combat) d.combat = {};
  if (typeof d.combat.hp_max !== 'object' || d.combat.hp_max === null) d.combat.hp_max = { base: d.combat.hp_max || 10, bonus: 0, override: null, derived: d.combat.hp_max || 10 };
  if (typeof d.combat.armor_class !== 'object' || d.combat.armor_class === null) d.combat.armor_class = { base: d.combat.armor_class || 10, bonus: 0, override: null, derived: d.combat.armor_class || 10 };
  if (typeof d.combat.initiative !== 'object' || d.combat.initiative === null) d.combat.initiative = { base: 0, bonus: 0, override: null, derived: d.combat.initiative || 0 };
  if (!d.combat.general_dc) d.combat.general_dc = { ability: 'strength', bonus: 0, derived: 8 };
  if (!d.combat.defenses) d.combat.defenses = { resistances: [], immunities: [], vulnerabilities: [] };

  const checkFields = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma', 'str_save', 'dex_save', 'con_save', 'int_save', 'wis_save', 'cha_save', 'athletics', 'acrobatics', 'sleight_of_hand', 'stealth', 'arcana', 'history', 'investigation', 'nature', 'religion', 'animal_handling', 'insight', 'medicine', 'perception', 'survival', 'deception', 'intimidation', 'performance', 'persuasion'];
  checkFields.forEach(f => { if (d[f] && d[f].adv_state === undefined) d[f].adv_state = 0; });
  return d;
};

const localData = ref(initDataStructure(props.initialData));
const syncStatus = ref<'saved' | 'syncing' | 'error'>('saved');

let isIncomingUpdate = false;
let timeoutId: number | undefined;

const handlePageUpdate = (partialData: any) => {
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

  // 1. 基础属性计算
  const stats = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'];
  stats.forEach(s => {
    const stat = dataToSend[s];
    stat.derived = (stat.base_score || 0) + (stat.racial_bonus || 0) + (stat.asi_bonus || 0) + (stat.bonus || 0);
    stat.modifier = Math.floor((stat.derived - 10) / 2);
    const save = dataToSend[s + '_save'] || dataToSend[s.substring(0,3) + '_save'];
    if (save) save.derived = stat.modifier + (save.is_proficient ? pb : 0) + (save.bonus || 0);
  });

  // 2. 施法引擎计算 (核心判定)
  const casterConfig: Record<string, number> = { '法师': 1, '牧师': 1, '德鲁伊': 1, '吟游诗人': 1, '术士': 1, '圣武士': 0.5, '游侠': 0.5, '奥法骑士': 0.33, '诡术随从': 0.33, '人造师': 0.5 };
  let effectiveLevel = 0;
  let pactLevel = 0;
  dataToSend.prog.classes.forEach((c: any) => {
    if (casterConfig[c.name]) {
      const rate = casterConfig[c.name];
      if (rate === 1) effectiveLevel += c.level;
      else if (rate === 0.5) effectiveLevel += Math.floor(c.level / 2);
      else if (rate === 0.33) effectiveLevel += Math.floor(c.level / 3);
    } else if (c.name === '邪术师') {
      pactLevel = c.level;
    }
  });

  // 施法能力判定：有效施法等级 > 0 或邪术师等级 > 0，或者手动添加了法术
  dataToSend.can_cast = (effectiveLevel > 0 || pactLevel > 0 || (dataToSend.spells?.length > 0));

  // 3. 战斗数值计算
  const dexMod = dataToSend.dexterity.modifier;
  const ac = dataToSend.combat.armor_class;
  ac.derived = ac.override !== null ? ac.override : ((ac.base || 10) + dexMod + ac.bonus);
  const init = dataToSend.combat.initiative;
  init.derived = init.override !== null ? init.override : (dexMod + init.bonus);
  const gdc = dataToSend.combat.general_dc;
  gdc.derived = 8 + pb + (dataToSend[gdc.ability]?.modifier || 0) + gdc.bonus;

  const skillToStat: Record<string, string> = { athletics: 'strength', acrobatics: 'dexterity', sleight_of_hand: 'dexterity', stealth: 'dexterity', arcana: 'intelligence', history: 'intelligence', investigation: 'intelligence', nature: 'intelligence', religion: 'intelligence', animal_handling: 'wisdom', insight: 'wisdom', medicine: 'wisdom', perception: 'wisdom', survival: 'wisdom', deception: 'charisma', intimidation: 'charisma', performance: 'charisma', persuasion: 'charisma' };
  Object.entries(skillToStat).forEach(([sk, st]) => {
    if (dataToSend[sk]) {
      const s = dataToSend[sk];
      s.derived = (dataToSend[st]?.modifier || 0) + (s.is_proficient ? pb : 0) + (s.is_expertise ? pb : 0) + (s.bonus || 0);
    }
  });

  const conMod = dataToSend.constitution.modifier;
  const hpRolls = dataToSend.combat?.hp_rolls || [];
  const primaryClass = dataToSend.prog.classes?.find((c: any) => c.is_primary) || dataToSend.prog.classes?.[0];
  if (primaryClass) {
    const sub = primaryClass.subclass ? `${primaryClass.subclass} ` : '';
    dataToSend.prog.character_class = `${sub}${primaryClass.name}`;
  }
  const hdValue = parseInt(primaryClass?.hit_die?.replace('d', '') || '8');
  let calcHPBase = (hpRolls[0] || hdValue) + conMod;
  for (let i = 1; i < currentLevel; i++) calcHPBase += ((hpRolls[i] || Math.floor(hdValue/2)+1) + conMod);
  calcHPBase += (dataToSend.combat.bonus_hp_per_level || 0) * currentLevel;
  dataToSend.combat.hp_max.base = calcHPBase;
  dataToSend.combat.hp_max.derived = dataToSend.combat.hp_max.override !== null ? dataToSend.combat.hp_max.override : (calcHPBase + dataToSend.combat.hp_max.bonus);

  isIncomingUpdate = true;
  dataToSend.combat.proficiency_bonus = pb;
  Object.assign(localData.value, dataToSend);
  setTimeout(() => { isIncomingUpdate = false; }, 50);
  emit('update', dataToSend);
  setTimeout(() => { if (syncStatus.value === 'syncing') syncStatus.value = 'saved'; }, 1000);
};

watch(localData, () => { if (!isIncomingUpdate) { syncStatus.value = 'syncing'; if (timeoutId) clearTimeout(timeoutId); timeoutId = window.setTimeout(performSync, 1200); } }, { deep: true });
onUnmounted(() => { if (timeoutId) clearTimeout(timeoutId); });
</script>

<template>
  <div class="character-sheet-container pb-20 relative">
    <div class="fixed top-6 right-8 z-50 transition-all duration-500" :class="syncStatus === 'saved' ? 'opacity-0 translate-y-[-10px]' : 'opacity-100 translate-y-0'">
      <div class="flex items-center gap-2 px-4 py-2 rounded-full bg-zinc-900 border border-white/10 shadow-2xl" :class="syncStatus === 'syncing' ? 'text-amber-400' : 'text-emerald-400'">
        <RefreshCw v-if="syncStatus === 'syncing'" class="w-4 h-4 animate-spin" />
        <CheckCircle2 v-else class="w-4 h-4" />
        <span class="text-xs font-black uppercase tracking-widest">{{ syncStatus === 'syncing' ? '同步中' : '已同步' }}</span>
      </div>
    </div>

    <div class="flex gap-2 mb-6 bg-zinc-900/50 p-1.5 rounded-2xl border border-zinc-800">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="(!localData.can_cast && tab.id === 'spellbook') ? null : currentTab = tab.id"
        class="flex-1 py-3 px-4 rounded-xl flex items-center justify-center gap-2 text-sm font-bold transition-all duration-300 relative group"
        :class="[
          currentTab === tab.id ? 'bg-zinc-800 text-white shadow-lg border border-zinc-700' : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/50',
          (!localData.can_cast && tab.id === 'spellbook') ? 'opacity-40 cursor-not-allowed grayscale' : ''
        ]"
      >
        <component :is="(!localData.can_cast && tab.id === 'spellbook') ? Lock : tab.icon" class="w-5 h-5" />
        {{ tab.label }}
        <div v-if="!localData.can_cast && tab.id === 'spellbook'" class="absolute inset-0 bg-transparent" title="当前职业等级无法施法"></div>
      </button>
    </div>

    <div class="tab-content transition-all duration-300">
      <RpPage v-if="currentTab === 'rp'" :sheet="localData" @update="handlePageUpdate" />
      <CombatPage v-else-if="currentTab === 'combat'" :sheet="localData" @update="handlePageUpdate" />
      <SpellbookPage v-else-if="currentTab === 'spellbook'" :sheet="localData" @update="handlePageUpdate" />
    </div>
  </div>
</template>