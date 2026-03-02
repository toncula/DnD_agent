<script setup lang="ts">
import { CheckCircle2, Circle } from 'lucide-vue-next';

const props = defineProps<{
  sheet: any;
}>();

const emit = defineEmits(['update']);

const skillNames: Record<string, { label: string, stat: string }> = {
  athletics: { label: '运动', stat: '力' },
  acrobatics: { label: '体操', stat: '敏' },
  sleight_of_hand: { label: '巧手', stat: '敏' },
  stealth: { label: '隐匿', stat: '敏' },
  arcana: { label: '奥秘', stat: '智' },
  history: { label: '历史', stat: '智' },
  investigation: { label: '调查', stat: '智' },
  nature: { label: '自然', stat: '智' },
  religion: { label: '宗教', stat: '智' },
  animal_handling: { label: '驯养', stat: '感' },
  insight: { label: '洞悉', stat: '感' },
  medicine: { label: '医药', stat: '感' },
  perception: { label: '察觉', stat: '感' },
  survival: { label: '生存', stat: '感' },
  deception: { label: '欺瞒', stat: '魅' },
  intimidation: { label: '威吓', stat: '魅' },
  performance: { label: '表演', stat: '魅' },
  persuasion: { label: '说服', stat: '魅' }
};

const toggleProficiency = (key: string) => {
  const newData = { ...props.sheet };
  newData[key].is_proficient = !newData[key].is_proficient;
  emit('update', newData);
};

const updateBonus = (key: string, value: number) => {
  const newData = { ...props.sheet };
  newData[key].bonus = value || 0;
  emit('update', newData);
};
</script>

<template>
  <div class="bg-zinc-950/40 p-3 rounded-2xl border border-zinc-800 shadow-inner w-full min-w-0">
    <h3 class="text-[10px] font-black text-zinc-600 uppercase tracking-[0.2em] mb-3 flex items-center gap-2 px-1">
      <span class="w-1 h-1 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
      技能熟练 (Skills)
    </h3>
    
    <div class="flex flex-col gap-0.5">
      <div 
        v-for="(info, key) in skillNames" 
        :key="key"
        class="flex items-center justify-between py-1 px-2 rounded-lg hover:bg-zinc-800/40 transition-all group"
      >
        <div class="flex items-center gap-2 min-w-0">
          <button @click="toggleProficiency(key)" class="text-zinc-800 hover:text-emerald-500 transition-colors shrink-0">
            <CheckCircle2 v-if="sheet[key].is_proficient" class="w-3.5 h-3.5 text-emerald-600" />
            <Circle v-else class="w-3.5 h-3.5" />
          </button>
          <span class="text-xs font-bold text-zinc-400 group-hover:text-zinc-200 truncate">{{ info.label }}</span>
          <span class="text-[9px] text-zinc-700 font-black uppercase shrink-0">{{ info.stat }}</span>
        </div>
        <div class="flex items-center gap-2">
          <!-- 临时加值输入 (核心变更) -->
          <input 
            type="number" 
            :value="sheet[key].bonus"
            @input="e => updateBonus(key, parseInt((e.target as HTMLInputElement).value))"
            class="w-8 bg-blue-500/10 border border-blue-500/20 rounded text-[9px] text-center text-blue-400 opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity outline-none"
            placeholder="0"
          />
          <span class="text-xs font-black font-mono shrink-0" :class="sheet[key].derived >= 0 ? 'text-zinc-200' : 'text-zinc-600'">
            {{ sheet[key].derived >= 0 ? '+' : '' }}{{ sheet[key].derived }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
