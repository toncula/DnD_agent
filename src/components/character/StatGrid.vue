<script setup lang="ts">
import { CheckSquare, Square, Edit2 } from 'lucide-vue-next';
import { ref } from 'vue';

const props = defineProps<{
  sheet: any;
}>();

const emit = defineEmits(['update']);

// 记录当前正在编辑哪一项的基础值
const editingKey = ref<string | null>(null);

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
  const numVal = parseInt(value) || 0;
  newData[key][field] = numVal;
  emit('update', newData);
};

const toggleSaveProficiency = (saveKey: string) => {
  const newData = { ...props.sheet };
  newData[saveKey].is_proficient = !newData[saveKey].is_proficient;
  emit('update', newData);
};
</script>

<template>
  <div class="flex flex-col gap-2 w-full min-w-0">
    <div 
      v-for="item in statMapping" 
      :key="item.key"
      class="bg-zinc-900/50 border border-zinc-800 rounded-xl p-3 flex flex-col relative shadow-lg hover:border-zinc-600 transition-all"
    >
      <div class="flex items-center justify-between">
        <!-- 左侧：熟练勾选与名称 -->
        <div class="flex items-center gap-3">
          <button 
            @click.stop="toggleSaveProficiency(item.saveKey)"
            class="z-10 p-1 -ml-1 text-zinc-700 hover:text-red-500 transition-colors"
            title="切换豁免熟练度"
          >
            <CheckSquare v-if="sheet[item.saveKey].is_proficient" class="w-4 h-4 text-red-500" />
            <Square v-else class="w-4 h-4" />
          </button>
          <div class="flex flex-col">
            <span class="text-[10px] font-black text-zinc-500 uppercase tracking-widest leading-none mb-1">{{ item.label }}</span>
            <span class="text-[9px] font-black" :class="sheet[item.saveKey].is_proficient ? 'text-red-400' : 'text-zinc-600'">
              豁免 {{ sheet[item.saveKey].derived >= 0 ? '+' : '' }}{{ sheet[item.saveKey].derived }}
            </span>
          </div>
        </div>

        <!-- 右侧：数值展示 -->
        <div class="flex items-center gap-3 cursor-pointer" @click="editingKey = editingKey === item.key ? null : item.key">
          <div class="flex flex-col items-end">
            <span class="text-2xl font-black text-white leading-none tracking-tighter">
              {{ sheet[item.key].modifier >= 0 ? '+' : '' }}{{ sheet[item.key].modifier }}
            </span>
            <span class="text-[10px] font-bold text-zinc-600 mt-0.5">{{ sheet[item.key].derived }}</span>
          </div>
          <Edit2 class="w-3 h-3 text-zinc-700" />
        </div>
      </div>

      <!-- 下拉编辑区 (点击数值后展开，不再使用悬浮遮挡) -->
      <div v-if="editingKey === item.key" class="mt-3 pt-3 border-t border-zinc-800 flex gap-2 animate-in fade-in slide-in-from-top-1 duration-200">
         <div class="flex-1 flex flex-col gap-1">
           <span class="text-[8px] text-zinc-600 uppercase font-black">基础值</span>
           <input 
            type="number" 
            :value="sheet[item.key].base_score"
            @input="e => updateValue(item.key, 'base_score', (e.target as HTMLInputElement).value)"
            class="w-full bg-zinc-950 border border-zinc-700 rounded text-center text-xs py-1 text-white focus:border-amber-500 outline-none"
          />
         </div>
         <div class="flex-1 flex flex-col gap-1">
           <span class="text-[8px] text-blue-500 uppercase font-black">临时加值</span>
           <input 
            type="number" 
            :value="sheet[item.key].bonus"
            @input="e => updateValue(item.key, 'bonus', (e.target as HTMLInputElement).value)"
            class="w-full bg-zinc-950 border border-blue-900/50 rounded text-center text-xs py-1 text-blue-400 focus:border-blue-500 outline-none"
          />
         </div>
         <div class="flex-1 flex flex-col gap-1">
           <span class="text-[8px] text-emerald-500 uppercase font-black">豁免修正</span>
           <input 
            type="number" 
            :value="sheet[item.saveKey].bonus"
            @input="e => updateValue(item.saveKey, 'bonus', (e.target as HTMLInputElement).value)"
            class="w-full bg-zinc-950 border border-emerald-900/50 rounded text-center text-xs py-1 text-emerald-400 focus:border-emerald-500 outline-none"
          />
         </div>
      </div>
    </div>
  </div>
</template>
