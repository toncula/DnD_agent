<script setup lang="ts">
import { ref } from 'vue';
import { Shield, Star, HeartCrack, Plus, X } from 'lucide-vue-next';

const props = defineProps<{ defenses: any }>();
const emit = defineEmits(['update']);

const showAddMenu = ref<string | null>(null);

const damageTypes = [
  '钝击', '穿刺', '劈砍', '酸液', '寒冷', '火焰', '力场', 
  '闪电', '毒素', '心灵', '光辉', '黯蚀', '雷鸣'
];

const addTag = (category: string, type: string) => {
  const newList = [...(props.defenses[category] || [])];
  if (!newList.includes(type)) {
    newList.push(type);
    emit('update', { ...props.defenses, [category]: newList });
  }
  showAddMenu.value = null;
};

const removeTag = (category: string, type: string) => {
  const newList = props.defenses[category].filter((t: string) => t !== type);
  emit('update', { ...props.defenses, [category]: newList });
};
</script>

<template>
  <div class="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-4 space-y-4 shadow-inner">
    <div class="flex items-center justify-between border-b border-zinc-800 pb-2">
      <span class="text-[10px] font-black text-zinc-500 uppercase tracking-widest">防御特性</span>
    </div>

    <!-- 抗性 -->
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Shield class="w-3.5 h-3.5 text-blue-400" />
          <span class="text-[10px] font-black text-blue-400/80 uppercase">抗性</span>
        </div>
        <button @click="showAddMenu = 'resistances'" class="p-1 hover:bg-zinc-800 rounded text-zinc-500"><Plus class="w-3 h-3" /></button>
      </div>
      <div class="flex flex-wrap gap-1.5 min-h-[24px]">
        <div 
          v-for="tag in defenses.resistances" :key="tag"
          class="flex items-center gap-1.5 bg-blue-900/20 border border-blue-500/30 px-2 py-0.5 rounded-full"
        >
          <span class="text-[10px] font-bold text-blue-300">{{ tag }}</span>
          <button @click="removeTag('resistances', tag)" class="text-blue-500/50 hover:text-blue-400"><X class="w-2.5 h-2.5" /></button>
        </div>
        <span v-if="!defenses.resistances?.length" class="text-[10px] text-zinc-700 italic opacity-50">无</span>
      </div>
    </div>

    <!-- 免疫 -->
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Star class="w-3.5 h-3.5 text-amber-400" />
          <span class="text-[10px] font-black text-amber-400/80 uppercase">免疫</span>
        </div>
        <button @click="showAddMenu = 'immunities'" class="p-1 hover:bg-zinc-800 rounded text-zinc-500"><Plus class="w-3 h-3" /></button>
      </div>
      <div class="flex flex-wrap gap-1.5 min-h-[24px]">
        <div 
          v-for="tag in defenses.immunities" :key="tag"
          class="flex items-center gap-1.5 bg-amber-900/20 border border-amber-500/30 px-2 py-0.5 rounded-full"
        >
          <span class="text-[10px] font-bold text-amber-300">{{ tag }}</span>
          <button @click="removeTag('immunities', tag)" class="text-amber-500/50 hover:text-amber-400"><X class="w-2.5 h-2.5" /></button>
        </div>
        <span v-if="!defenses.immunities?.length" class="text-[10px] text-zinc-700 italic opacity-50">无</span>
      </div>
    </div>

    <!-- 易伤 -->
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <HeartCrack class="w-3.5 h-3.5 text-red-500" />
          <span class="text-[10px] font-black text-red-500/80 uppercase">易伤</span>
        </div>
        <button @click="showAddMenu = 'vulnerabilities'" class="p-1 hover:bg-zinc-800 rounded text-zinc-500"><Plus class="w-3 h-3" /></button>
      </div>
      <div class="flex flex-wrap gap-1.5 min-h-[24px]">
        <div 
          v-for="tag in defenses.vulnerabilities" :key="tag"
          class="flex items-center gap-1.5 bg-red-900/20 border border-red-500/30 px-2 py-0.5 rounded-full"
        >
          <span class="text-[10px] font-bold text-red-300">{{ tag }}</span>
          <button @click="removeTag('vulnerabilities', tag)" class="text-red-500/50 hover:text-red-400"><X class="w-2.5 h-2.5" /></button>
        </div>
        <span v-if="!defenses.vulnerabilities?.length" class="text-[10px] text-zinc-700 italic opacity-50">无</span>
      </div>
    </div>

    <!-- 弹窗 -->
    <div v-if="showAddMenu" class="fixed inset-0 z-[150] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showAddMenu = null"></div>
      <div class="relative bg-zinc-900 border border-zinc-700 w-full max-w-xs rounded-3xl p-6 shadow-2xl animate-in zoom-in-95 duration-200">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-sm font-black text-white uppercase tracking-widest">添加类型</h3>
          <button @click="showAddMenu = null" class="text-zinc-500 hover:text-white"><X class="w-5 h-5" /></button>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <button 
            v-for="t in damageTypes" :key="t"
            @click="addTag(showAddMenu!, t)"
            class="px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-xl text-[10px] font-bold text-zinc-300 hover:bg-blue-600 hover:text-white transition-all text-left"
          >
            {{ t }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>