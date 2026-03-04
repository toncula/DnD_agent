<script setup lang="ts">
import { ref, watch, onUnmounted, computed } from 'vue';
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

// 施法能力判定：转为计算属性以实现瞬时响应
const canCast = computed(() => {
  const casterConfig: Record<string, number> = { '法师': 1, '牧师': 1, '德鲁伊': 1, '吟游诗人': 1, '术士': 1, '圣武士': 0.5, '游侠': 0.5, '奥法骑士': 0.33, '诡术随从': 0.33, '人造师': 0.5 };
  let effectiveLevel = 0;
  let pactLevel = 0;
  
  const classes = localData.value.prog?.classes || [];
  classes.forEach((c: any) => {
    const name = (c.name || '').trim();
    if (casterConfig[name]) {
      const rate = casterConfig[name];
      if (rate === 1) effectiveLevel += c.level;
      else if (rate === 0.5) effectiveLevel += Math.floor(c.level / 2);
      else if (rate === 0.33) effectiveLevel += Math.floor(c.level / 3);
    } else if (name === '邪术师') {
      pactLevel = c.level;
    }
  });

  return (effectiveLevel > 0 || pactLevel > 0 || (localData.value.spells?.length > 0));
});

// 1. 本地状态副本 (带结构平滑转换)
const initDataStructure = (data: any) => {
  const d = JSON.parse(JSON.stringify(data));
  if (!d.combat) d.combat = {};
  
  // 核心修复：确保 hp_max 为数字，且 hp_current 存在
  if (typeof d.combat.hp_max === 'object' && d.combat.hp_max !== null) {
    d.combat.hp_max = d.combat.hp_max.derived || 10;
  }
  if (d.combat.hp_current === undefined) d.combat.hp_current = d.combat.hp_max || 10;
  if (d.combat.temp_hp === undefined) d.combat.temp_hp = 0;
  if (d.combat.bonus_hp_per_level === undefined) d.combat.bonus_hp_per_level = 0;
  if (!d.combat.hp_rolls) d.combat.hp_rolls = [];

  if (typeof d.combat.armor_class !== 'object' || d.combat.armor_class === null) d.combat.armor_class = { base: d.combat.armor_class || 10, bonus: 0, override: null, derived: d.combat.armor_class || 10 };
  if (typeof d.combat.initiative !== 'object' || d.combat.initiative === null) d.combat.initiative = { base: 0, bonus: 0, override: null, derived: d.combat.initiative || 0 };
  if (!d.combat.general_dc) d.combat.general_dc = { ability: 'strength', bonus: 0, derived: 8 };
  if (!d.combat.defenses) d.combat.defenses = { resistances: [], immunities: [], vulnerabilities: [] };

  const checkFields = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma', 'str_save', 'dex_save', 'con_save', 'int_save', 'wis_save', 'cha_save', 'athletics', 'acrobatics', 'sleight_of_hand', 'stealth', 'arcana', 'history', 'investigation', 'nature', 'religion', 'animal_handling', 'insight', 'medicine', 'perception', 'survival', 'deception', 'intimidation', 'performance', 'persuasion'];
  checkFields.forEach(f => { if (d[f] && d[f].adv_state === undefined) d[f].adv_state = 0; });
  return d;
};

const localData = ref(initDataStructure(props.initialData));

// 关键修复：当 props 变化时（比如刷新后读取或保存后返回），同步更新本地数据
watch(() => props.initialData, (newVal) => {
  if (newVal) {
    isIncomingUpdate = true;
    localData.value = initDataStructure(newVal);
    setTimeout(() => { isIncomingUpdate = false; }, 50);
  }
}, { deep: true });

const syncStatus = ref<'saved' | 'syncing' | 'error'>('saved');

let isIncomingUpdate = false;
let timeoutId: number | undefined;

const handlePageUpdate = (partialData: any) => {
  // 1. 深拷贝 localData 以触发 Vue 的响应式
  const updatedData = JSON.parse(JSON.stringify(localData.value));
  for (const key in partialData) {
    updatedData[key] = partialData[key];
  }
  // 2. 将更新后的数据赋值给 localData，这会确保所有引用它的子组件都刷新
  localData.value = updatedData;
  // 3. 立即触发同步
  performSync();
};

const performSync = () => {
  if (isIncomingUpdate) return;
  syncStatus.value = 'syncing';
  
  const dataToSend = JSON.parse(JSON.stringify(localData.value));
  
  // 后端负责所有核心计算，这里只发送数据并同步状态
  emit('update', dataToSend);
  
  setTimeout(() => { 
    if (syncStatus.value === 'syncing') syncStatus.value = 'saved'; 
  }, 800);
};

// 移除原有的 watch 自动同步逻辑，改为由 PageUpdate 主动触发或手动保存感官
// watch(localData, ...) -> 已移除
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
        @click="currentTab = tab.id"
        class="flex-1 py-3 px-4 rounded-xl flex items-center justify-center gap-2 text-sm font-bold transition-all duration-300 relative group"
        :class="[
          currentTab === tab.id ? 'bg-zinc-800 text-white shadow-lg border border-zinc-700' : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/50',
          (!canCast && tab.id === 'spellbook') ? 'opacity-60 grayscale-[0.5]' : ''
        ]"
      >
        <component :is="(!canCast && tab.id === 'spellbook') ? Lock : tab.icon" class="w-5 h-5" />
        {{ tab.label }}
        <div v-if="!canCast && tab.id === 'spellbook'" class="absolute -top-1 -right-1 bg-zinc-800 rounded-full p-1 border border-zinc-700 shadow-xl" title="暂无施法职业，但仍可手动管理法术">
          <Lock class="w-2.5 h-2.5 text-amber-500" />
        </div>
      </button>
    </div>

    <div class="tab-content transition-all duration-300">
      <RpPage v-if="currentTab === 'rp'" :sheet="localData" @update="handlePageUpdate" />
      <CombatPage v-else-if="currentTab === 'combat'" :sheet="localData" @update="handlePageUpdate" />
      <SpellbookPage v-else-if="currentTab === 'spellbook'" :sheet="localData" @update="handlePageUpdate" />
    </div>
  </div>
</template>