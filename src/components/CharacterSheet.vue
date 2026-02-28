<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';
import { RefreshCw, CheckCircle2, AlertCircle } from 'lucide-vue-next';
import BioHeader from './character/BioHeader.vue';
import StatGrid from './character/StatGrid.vue';
import CombatStats from './character/CombatStats.vue';
import SkillsSaves from './character/SkillsSaves.vue';
import FeatureTabs from './character/FeatureTabs.vue';

const props = defineProps<{
  initialData: any; 
}>();

const emit = defineEmits(['update']);

// 1. 本地状态副本
const localData = ref(JSON.parse(JSON.stringify(props.initialData)));
const syncStatus = ref<'saved' | 'syncing' | 'error'>('saved');

// 2. 标志位，防止同步循环
let isIncomingUpdate = false;
let timeoutId: number | undefined;

const performSync = () => {
  if (isIncomingUpdate) return;
  syncStatus.value = 'syncing';
  
  const dataToSend = JSON.parse(JSON.stringify(localData.value));
  const currentLevel = dataToSend.prog.level || 1;
  
  // 关键修复 1：严格按等级截断 hp_rolls，确保后端计算 hp_max 准确
  if (dataToSend.combat?.hp_rolls) {
    let rolls = dataToSend.combat.hp_rolls.map((v: any) => {
      const p = parseInt(v);
      return isNaN(p) ? 0 : p;
    });
    // 强制截断/补齐到当前等级长度
    if (rolls.length > currentLevel) {
      rolls = rolls.slice(0, currentLevel);
    } else {
      while (rolls.length < currentLevel) rolls.push(0);
    }
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

    <div class="space-y-4">
      <BioHeader v-model:bio="localData.bio" v-model:prog="localData.prog" />
      <CombatStats v-model:combat="localData.combat" :level="localData.prog.level" />
      <StatGrid :sheet="localData" @update="(newData) => Object.assign(localData.value, newData)" />
      <SkillsSaves :sheet="localData" @update="(newData) => Object.assign(localData.value, newData)" />
      <FeatureTabs v-model:features="localData.features" v-model:inventory="localData.inventory" v-model:spells="localData.spells" />
    </div>
  </div>
</template>

<style scoped>
input, textarea { transition: none !important; }
</style>
