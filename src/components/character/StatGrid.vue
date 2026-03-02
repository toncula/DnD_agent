<script setup lang="ts">
import { CheckSquare, Square, Edit2, TrendingUp, ChevronUp, ChevronDown } from 'lucide-vue-next';
import { ref } from 'vue';

const props = defineProps<{
  sheet: any;
}>();

const emit = defineEmits(['update']);

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
  newData[key][field] = parseInt(value) || 0;
  emit('update', newData);
};

const toggleAdv = (key: string) => {
  const newData = { ...props.sheet };
  const current = newData[key].adv_state || 0;
  newData[key].adv_state = current === 0 ? 1 : current === 1 ? -1 : 0;
  emit('update', newData);
};

const updateCombat = (field: string, val: any) => {
  const combat = { ...props.sheet.combat, [field]: val };
  emit('update', { combat });
};

const toggleSaveProficiency = (saveKey: string) => {
  const newData = { ...props.sheet };
  newData[saveKey].is_proficient = !newData[saveKey].is_proficient;
  emit('update', newData);
};
</script>

<template>
  <div class="flex flex-col gap-3 w-full min-w-0">
    <!-- 熟练加值 -->
    <div class="bg-zinc-950/60 border border-zinc-800/50 p-3 rounded-2xl flex items-center justify-between shadow-inner">
      <div class="flex items-center gap-3">
        <div class="bg-zinc-900 p-1.5 rounded-lg border border-zinc-800"><TrendingUp class="w-4 h-4 text-zinc-500" /></div>
        <span class="text-[9px] font-black text-zinc-600 uppercase tracking-widest">熟练加值</span>
      </div>
      <input type="number" :value="sheet.combat.proficiency_bonus" @input="e => updateCombat('proficiency_bonus', parseInt((e.target as HTMLInputElement).value) || 0)" class="w-10 bg-zinc-900 border border-zinc-800 rounded-lg py-1 text-center text-lg font-black text-zinc-100 outline-none" />
    </div>

    <div v-for="item in statMapping" :key="item.key" class="bg-zinc-900/50 border border-zinc-800 rounded-xl p-3 flex flex-col relative shadow-lg hover:border-zinc-600 transition-all group">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <!-- 豁免项 -->
          <button @click.stop="toggleSaveProficiency(item.saveKey)" class="p-1 -ml-1 text-zinc-700 hover:text-red-500">
            <CheckSquare v-if="sheet[item.saveKey].is_proficient" class="w-4 h-4 text-red-500" />
            <Square v-else class="w-4 h-4" />
          </button>
          <div class="flex flex-col">
            <span class="text-[10px] font-black text-zinc-500 uppercase tracking-widest mb-1">{{ item.label }}</span>
            <div class="flex items-center gap-1.5">
              <span class="text-[9px] font-black" :class="sheet[item.saveKey].is_proficient ? 'text-red-400' : 'text-zinc-600'">豁免 {{ sheet[item.saveKey].derived >= 0 ? '+' : '' }}{{ sheet[item.saveKey].derived }}</span>
              <!-- 豁免优劣势按钮 (改进) -->
              <button 
                @click.stop="toggleAdv(item.saveKey)" 
                class="w-4 h-4 rounded border flex items-center justify-center transition-all hover:scale-110 active:scale-95"
                :class="sheet[item.saveKey].adv_state === 1 ? 'bg-emerald-500/20 border-emerald-500/50' : sheet[item.saveKey].adv_state === -1 ? 'bg-red-500/20 border-red-500/50' : 'bg-zinc-950 border-zinc-800/50 hover:bg-zinc-800'"
                :title="sheet[item.saveKey].adv_state === 1 ? '优势' : sheet[item.saveKey].adv_state === -1 ? '劣势' : '正常 (点击切换优势/劣势)'"
              >
                <ChevronUp v-if="sheet[item.saveKey].adv_state === 1" class="w-2.5 h-2.5 text-emerald-500" />
                <ChevronDown v-else-if="sheet[item.saveKey].adv_state === -1" class="w-2.5 h-2.5 text-red-500" />
                <div v-else class="w-1 h-1 rounded-full bg-zinc-800 group-hover:bg-zinc-600"></div>
              </button>
            </div>
          </div>
        </div>

        <!-- 属性值项 -->
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <!-- 属性优劣势按钮 (改进) -->
            <button 
              @click.stop="toggleAdv(item.key)" 
              class="w-5 h-5 rounded-lg border flex items-center justify-center transition-all hover:bg-zinc-800 hover:scale-110"
              :class="sheet[item.key].adv_state === 1 ? 'bg-emerald-500/20 border-emerald-500/50' : sheet[item.key].adv_state === -1 ? 'bg-red-500/20 border-red-500/50' : 'bg-zinc-950 border-zinc-800 border-dashed'"
              :title="sheet[item.key].adv_state === 1 ? '优势' : sheet[item.key].adv_state === -1 ? '劣势' : '正常 (点击切换属性检定优势/劣势)'"
            >
              <ChevronUp v-if="sheet[item.key].adv_state === 1" class="w-3.5 h-3.5 text-emerald-500" />
              <ChevronDown v-else-if="sheet[item.key].adv_state === -1" class="w-3.5 h-3.5 text-red-500" />
              <div v-else class="w-1.5 h-1.5 rounded-full bg-zinc-800 group-hover:bg-zinc-600"></div>
            </button>
            
            <div class="flex flex-col items-end cursor-pointer" @click="editingKey = editingKey === item.key ? null : item.key">
              <span class="text-2xl font-black text-white leading-none">{{ sheet[item.key].modifier >= 0 ? '+' : '' }}{{ sheet[item.key].modifier }}</span>
              <span class="text-[10px] font-bold text-zinc-600 mt-0.5">{{ sheet[item.key].derived }}</span>
            </div>
          </div>
          <Edit2 class="w-3 h-3 text-zinc-700 cursor-pointer" @click="editingKey = editingKey === item.key ? null : item.key" />
        </div>
      </div>

      <div v-if="editingKey === item.key" class="mt-3 pt-3 border-t border-zinc-800 flex gap-2 animate-in fade-in slide-in-from-top-1">
         <div class="flex-1 flex flex-col gap-1">
           <span class="text-[8px] text-zinc-600 font-black">基础</span>
           <input type="number" :value="sheet[item.key].base_score" @input="e => updateValue(item.key, 'base_score', (e.target as HTMLInputElement).value)" class="w-full bg-zinc-950 border border-zinc-700 rounded text-center text-xs py-1 text-white outline-none" />
         </div>
         <div class="flex-1 flex flex-col gap-1">
           <span class="text-[8px] text-blue-500 font-black">加值</span>
           <input type="number" :value="sheet[item.key].bonus" @input="e => updateValue(item.key, 'bonus', (e.target as HTMLInputElement).value)" class="w-full bg-zinc-950 border border-blue-900/50 rounded text-center text-xs py-1 text-blue-400 outline-none" />
         </div>
         <div class="flex-1 flex flex-col gap-1">
           <span class="text-[8px] text-emerald-500 font-black">豁免</span>
           <input type="number" :value="sheet[item.saveKey].bonus" @input="e => updateValue(item.saveKey, 'bonus', (e.target as HTMLInputElement).value)" class="w-full bg-zinc-950 border border-emerald-900/50 rounded text-center text-xs py-1 text-emerald-400 outline-none" />
         </div>
      </div>
    </div>
  </div>
</template>