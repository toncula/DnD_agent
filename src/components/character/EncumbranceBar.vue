<script setup lang="ts">
import { computed } from 'vue';
import { Scale, Settings2 } from 'lucide-vue-next';
import { ref } from 'vue';

const props = defineProps<{
  totalWeight: number;
  strength: number;
  settings: {
    base_mult: number;
  };
}>();

const emit = defineEmits(['update:settings']);

const isSettingsOpen = ref(false);

// 5e 规则：力量 * base (5) = 轻， * base*2 (10) = 中， * base*3 (15) = 重
const baseMult = computed(() => props.settings?.base_mult ?? 5.0);
const lightThreshold = computed(() => props.strength * baseMult.value);
const mediumThreshold = computed(() => props.strength * baseMult.value * 2);
const heavyThreshold = computed(() => props.strength * baseMult.value * 3);

const percentage = computed(() => Math.min((props.totalWeight / (heavyThreshold.value || 1)) * 100, 100));

const status = computed(() => {
  if (props.totalWeight <= lightThreshold.value) return { label: '轻载', color: 'bg-emerald-500', text: 'text-emerald-400' };
  if (props.totalWeight <= mediumThreshold.value) return { label: '中载', color: 'bg-amber-500', text: 'text-amber-400' };
  return { label: '重载', color: 'bg-red-500', text: 'text-red-400' };
});

const updateSettings = () => {
  emit('update:settings', { ...props.settings });
};
</script>

<template>
  <div class="bg-zinc-900/80 border border-zinc-800 rounded-2xl p-4 mb-6 shadow-xl">
    <div class="flex justify-between items-center mb-3">
      <div class="flex items-center gap-2">
        <div class="p-2 bg-blue-600/20 rounded-lg">
          <Scale class="w-4 h-4 text-blue-400" />
        </div>
        <div>
          <h3 class="text-[10px] font-black text-zinc-500 uppercase tracking-widest leading-none mb-1">负重状态</h3>
          <div class="flex items-baseline gap-1">
            <span class="text-lg font-black text-zinc-100">{{ totalWeight.toFixed(1) }}</span>
            <span class="text-[10px] font-bold text-zinc-500">/ {{ heavyThreshold.toFixed(0) }} 磅</span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-4">
        <div class="text-right">
          <span class="text-[9px] font-black uppercase tracking-tighter block mb-0.5" :class="status.text">{{ status.label }}</span>
          <span class="text-[10px] font-bold text-zinc-600 uppercase">{{ percentage.toFixed(0) }}%</span>
        </div>
        <button @click="isSettingsOpen = !isSettingsOpen" class="p-2 hover:bg-zinc-800 rounded-xl transition-colors">
          <Settings2 class="w-4 h-4 text-zinc-500" />
        </button>
      </div>
    </div>

    <!-- 进度条 -->
    <div class="relative h-2 bg-zinc-800 rounded-full overflow-hidden mb-1 flex">
      <div :style="{ width: percentage + '%' }" class="h-full transition-all duration-500" :class="status.color"></div>
      
      <!-- 刻度线 (33% 和 66% 处) -->
      <div class="absolute inset-0 flex pointer-events-none">
        <div class="absolute top-0 bottom-0 left-[33.3%] w-0.5 bg-black/20"></div>
        <div class="absolute top-0 bottom-0 left-[66.6%] w-0.5 bg-black/20"></div>
      </div>
    </div>

    <!-- 阈值数值显示 -->
    <div class="flex justify-between text-[8px] font-black text-zinc-600 uppercase px-1">
      <span>0</span>
      <span>轻: {{ lightThreshold.toFixed(0) }}</span>
      <span>中: {{ mediumThreshold.toFixed(0) }}</span>
      <span>重: {{ heavyThreshold.toFixed(0) }}</span>
    </div>

    <!-- 设置面板 -->
    <div v-if="isSettingsOpen" class="mt-4 pt-4 border-t border-zinc-800 animate-in slide-in-from-top-2">
      <div class="flex flex-col gap-1 max-w-[120px]">
        <label class="text-[8px] font-black text-zinc-500 uppercase">基础负重倍率</label>
        <div class="flex items-center gap-2">
          <span class="text-[10px] font-bold text-zinc-600">力量 ×</span>
          <input type="number" step="0.5" v-model="settings.base_mult" @change="updateSettings" class="w-full bg-zinc-950 border border-zinc-800 rounded px-2 py-1 text-xs text-zinc-300 outline-none" />
        </div>
        <p class="text-[7px] text-zinc-600 mt-1 italic">默认规则为 5.0 (轻/中/重为 5/10/15)</p>
      </div>
    </div>
  </div>
</template>