<script setup lang="ts">
import { CheckSquare, Square } from 'lucide-vue-next';

const props = defineProps<{
  // 传入包含属性和豁免数据的对象
  sheet: any;
}>();

const emit = defineEmits(['update']);

const statMapping = [
  { key: 'strength', saveKey: 'str_save', label: '力量', short: '力' },
  { key: 'dexterity', saveKey: 'dex_save', label: '敏捷', short: '敏' },
  { key: 'constitution', saveKey: 'con_save', label: '体质', short: '体' },
  { key: 'intelligence', saveKey: 'int_save', label: '智力', short: '智' },
  { key: 'wisdom', saveKey: 'wis_save', label: '感知', short: '感' },
  { key: 'charisma', saveKey: 'cha_save', label: '魅力', short: '魅' }
];

const updateValue = (key: string, field: string, value: any) => {
  const newData = { ...props.sheet };
  newData[key][field] = value;
  emit('update', newData);
};

const toggleSaveProficiency = (saveKey: string) => {
  const newData = { ...props.sheet };
  newData[saveKey].is_proficient = !newData[saveKey].is_proficient;
  emit('update', newData);
};
</script>

<template>
  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-4">
    <div 
      v-for="item in statMapping" 
      :key="item.key"
      class="bg-zinc-800/80 border border-zinc-700/50 rounded-2xl p-3 flex flex-col items-center relative shadow-lg group hover:border-red-500/50 transition-all"
    >
      <!-- 豁免熟练勾选 (左上角) -->
      <button 
        @click="toggleSaveProficiency(item.saveKey)"
        class="absolute top-2 left-2 text-zinc-600 hover:text-red-500 transition-colors"
        title="豁免熟练"
      >
        <CheckSquare v-if="sheet[item.saveKey].is_proficient" class="w-3.5 h-3.5 text-red-500" />
        <Square v-else class="w-3.5 h-3.5" />
      </button>

      <!-- 属性缩写 (右上角) -->
      <span class="absolute top-2 right-2 text-sm font-black text-zinc-500 tracking-tighter bg-zinc-900/50 px-1.5 py-0.5 rounded border border-zinc-700/30 leading-none">{{ item.short }}</span>

      <!-- 核心调整值 (大字) -->
      <div class="mt-2 text-4xl font-black text-white leading-none tracking-tighter">
        {{ sheet[item.key].modifier >= 0 ? '+' : '' }}{{ sheet[item.key].modifier }}
      </div>
      
      <!-- 最终属性值 (圈) -->
      <div class="mt-2 mb-3 px-4 py-1 bg-zinc-900 border border-zinc-700 rounded-full text-sm font-black text-zinc-300 shadow-inner">
        {{ sheet[item.key].derived }}
      </div>

      <!-- 底部：豁免判定加值 -->
      <div class="w-full pt-2 border-t border-zinc-700/50 flex flex-col items-center gap-0.5">
        <span class="text-[11px] font-bold text-zinc-500 uppercase tracking-widest">豁免判定</span>
        <div class="text-sm font-black" :class="sheet[item.saveKey].is_proficient ? 'text-red-400' : 'text-zinc-300'">
          {{ sheet[item.saveKey].derived >= 0 ? '+' : '' }}{{ sheet[item.saveKey].derived }}
        </div>
      </div>

      <!-- 悬浮编辑基础值 -->
      <div class="mt-2 w-full opacity-0 group-hover:opacity-100 transition-opacity">
        <input 
          type="number" 
          :value="sheet[item.key].base_score"
          @input="e => updateValue(item.key, 'base_score', parseInt((e.target as HTMLInputElement).value))"
          class="w-full bg-zinc-950 border border-zinc-700 rounded text-center text-[10px] py-0.5 text-zinc-500 focus:text-red-400 focus:border-red-500 outline-none"
        />
      </div>
    </div>
  </div>
</template>
