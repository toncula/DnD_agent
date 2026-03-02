<script setup lang="ts">
import { ref, computed } from 'vue';
import { Settings2, Clock, MapPin } from 'lucide-vue-next';
import SpellSlotTracker from './SpellSlotTracker.vue';
import SpellPreparationDrawer from './SpellPreparationDrawer.vue';

const props = defineProps<{
  spells: any[];
  sheet: any;
}>();

const emit = defineEmits(['update', 'hover-item', 'update:sheet']);

const showSelector = ref(false);

// 全局施法属性
const globalAbility = computed(() => props.sheet.spellcasting?.ability || 'intelligence');

// 获取已准备列表（包含戏法和恒定准备）
const preparedSpells = computed(() => {
  return (props.spells || []).filter(s => s.is_prepared || s.level === 0 || s.is_always_prepared);
});

// 计算准备限额 (不含恒定准备)
const prepLimit = computed(() => {
  const mod = props.sheet[globalAbility.value]?.modifier || 0;
  const level = props.sheet.prog?.level || 1;
  return Math.max(1, level + mod);
});

// 当前常规准备数量 (过滤掉戏法和恒定准备)
const preparedCount = computed(() => {
  return props.spells.filter(s => s.level > 0 && s.is_prepared && !s.is_always_prepared).length;
});

const handleUpdateSpells = (newList: any[]) => {
  emit('update', newList);
};

const setGlobalAbility = (ability: string) => {
  const newSpellcasting = { ...props.sheet.spellcasting, ability };
  emit('update:sheet', { spellcasting: newSpellcasting });
};

// 计算单个法术的 DC
const calculateDC = (spell: any) => {
  const pb = props.sheet.combat?.proficiency_bonus || 2;
  const abilityKey = spell.override_ability || globalAbility.value;
  const mod = props.sheet[abilityKey]?.modifier || 0;
  return 8 + pb + mod;
};

const getAbilityShort = (ability: string) => {
  const map: any = { intelligence: '智', wisdom: '感', charisma: '魅' };
  return map[ability] || '智';
};

const handleHover = (item: any, event: MouseEvent) => {
  emit('hover-item', item, event);
};
</script>

<template>
  <div class="space-y-4">
    <!-- 施法设置与限额 -->
    <div class="bg-zinc-950/50 border border-zinc-800 rounded-2xl p-4 flex flex-wrap items-center justify-between gap-6 shadow-inner">
      <div class="flex items-center gap-6">
        <div class="flex flex-col gap-1.5">
          <span class="text-[9px] font-black text-zinc-600 uppercase tracking-widest px-1">全局施法属性</span>
          <div class="flex bg-zinc-900 p-1 rounded-xl border border-zinc-800">
            <button 
              v-for="a in [{id:'intelligence', label:'智'}, {id:'wisdom', label:'感'}, {id:'charisma', label:'魅'}]" 
              :key="a.id"
              @click="setGlobalAbility(a.id)"
              class="px-3 py-1.5 rounded-lg text-[10px] font-black transition-all"
              :class="globalAbility === a.id ? 'bg-blue-600 text-white shadow-lg' : 'text-zinc-500 hover:text-zinc-300'"
            >
              {{ a.label }}
            </button>
          </div>
        </div>
        <div class="h-10 w-px bg-zinc-800 mx-2"></div>
        <div class="flex flex-col">
          <span class="text-[9px] font-black text-zinc-500 uppercase tracking-widest">常规限额</span>
          <div class="flex items-center gap-2 mt-1">
            <span class="text-xl font-black" :class="preparedCount > prepLimit ? 'text-red-500' : 'text-zinc-100'">{{ preparedCount }}</span>
            <span class="text-zinc-600 text-sm">/ {{ prepLimit }}</span>
          </div>
        </div>
      </div>

      <button @click="showSelector = true" class="flex items-center gap-2 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 px-5 py-2.5 rounded-xl border border-zinc-700 text-xs font-bold transition-all shadow-lg active:scale-95">
        <Settings2 class="w-4 h-4 text-blue-400" /> 调整准备列表
      </button>
    </div>

    <!-- 法术位 -->
    <SpellSlotTracker :sheet="sheet" @update:sheet="v => emit('update:sheet', v)" />

    <!-- 已准备列表 (按环阶显示) -->
    <div class="space-y-6">
      <div v-for="lv in 10" :key="lv-1">
        <template v-if="preparedSpells.filter(s => s.level === (lv-1)).length > 0">
          <div class="flex items-center gap-3 mb-3">
            <span class="text-[9px] font-black text-zinc-600 uppercase tracking-[0.2em]">{{ lv === 1 ? '戏法' : (lv-1) + ' 环' }}</span>
            <div class="h-px bg-zinc-800/50 flex-1"></div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div 
              v-for="(spell, i) in preparedSpells.filter(s => s.level === (lv-1))" :key="i"
              @mouseenter="e => handleHover(spell, e)"
              @mouseleave="handleHover(null, null as any)"
              class="bg-zinc-900/60 p-3 rounded-xl border border-zinc-800 hover:border-blue-500/40 transition-all cursor-help flex justify-between items-center group relative overflow-hidden"
            >
              <!-- 恒定准备标识线 -->
              <div v-if="spell.is_always_prepared" class="absolute top-0 left-0 w-1 h-full bg-amber-500/50"></div>

              <div class="flex flex-col flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-bold text-zinc-200 truncate">{{ spell.name }}</span>
                  <span v-if="spell.override_ability" class="text-[7px] bg-blue-900/30 text-blue-400 px-1 py-0.5 rounded border border-blue-500/20 font-black uppercase">
                    {{ getAbilityShort(spell.override_ability) }}
                  </span>
                </div>
                <div class="flex items-center gap-3 mt-1 text-[9px] text-zinc-500 font-medium">
                  <span class="flex items-center gap-1"><Clock class="w-2.5 h-2.5 opacity-50" /> {{ spell.casting_time }}</span>
                  <span class="italic text-zinc-600">{{ spell.duration }}</span>
                </div>
              </div>

              <!-- 独立 DC 展示 -->
              <div class="flex flex-col items-center justify-center pl-3 ml-3 border-l border-zinc-800 shrink-0 min-w-[40px]">
                <span class="text-[8px] font-black text-zinc-600 uppercase leading-none mb-1">DC</span>
                <span class="text-lg font-black leading-none" :class="spell.override_ability ? 'text-blue-400' : 'text-zinc-400'">
                  {{ calculateDC(spell) }}
                </span>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- 整备抽屉组件 -->
    <SpellPreparationDrawer 
      :show="showSelector"
      :spells="spells"
      :prepLimit="prepLimit"
      :preparedCount="preparedCount"
      @close="showSelector = false"
      @update:spells="handleUpdateSpells"
    />
  </div>
</template>