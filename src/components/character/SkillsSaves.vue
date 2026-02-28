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
</script>

<template>
  <div class="bg-zinc-800/30 p-3 rounded-2xl border border-zinc-700/50 shadow-inner">
    <h3 class="text-[10px] font-black text-zinc-500 uppercase tracking-widest mb-3 flex items-center gap-2 px-1">
      <span class="w-1 h-1 rounded-full bg-emerald-500"></span>
      技能 (Skills)
    </h3>
    
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-1">
      <div 
        v-for="(info, key) in skillNames" 
        :key="key"
        class="flex items-center justify-between p-2.5 rounded-xl hover:bg-zinc-700/40 transition-all group"
      >
        <div class="flex items-center gap-3">
          <button @click="toggleProficiency(key)" class="text-zinc-600 hover:text-emerald-500 transition-colors">
            <CheckCircle2 v-if="sheet[key].is_proficient" class="w-5 h-5 text-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.3)]" />
            <Circle v-else class="w-5 h-5" />
          </button>
          <span class="text-base font-bold text-zinc-200 group-hover:text-white">{{ info.label }}</span>
          <span class="text-xs text-zinc-500 font-black bg-zinc-950 px-1.5 py-0.5 rounded border border-zinc-800">{{ info.stat }}</span>
        </div>
        <span class="text-lg font-black font-mono" :class="sheet[key].derived >= 0 ? 'text-zinc-300' : 'text-zinc-500'">
          {{ sheet[key].derived >= 0 ? '+' : '' }}{{ sheet[key].derived }}
        </span>
      </div>
    </div>
  </div>
</template>
