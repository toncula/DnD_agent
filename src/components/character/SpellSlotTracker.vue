<script setup lang="ts">
import { computed, ref } from 'vue';
import { Sparkles, Settings2, X } from 'lucide-vue-next';

const props = defineProps<{
  sheet: any;
}>();

const emit = defineEmits(['update:sheet']);

const showSettings = ref<string | null>(null);

const hasAnySlots = computed(() => {
  if (!props.sheet?.spellcasting?.slots) return false;
  return Object.values(props.sheet.spellcasting.slots).some((s: any) => s.max_slots > 0);
});

const updateSlotExpended = (level: string, delta: number) => {
  const slots = JSON.parse(JSON.stringify(props.sheet.spellcasting.slots));
  slots[level].expended = Math.max(0, Math.min(slots[level].max_slots, slots[level].expended + delta));
  emit('update:sheet', { spellcasting: { ...props.sheet.spellcasting, slots } });
};

const updateOverride = (level: string, val: string) => {
  const slots = JSON.parse(JSON.stringify(props.sheet.spellcasting.slots));
  slots[level].override = val === '' ? null : parseInt(val);
  emit('update:sheet', { spellcasting: { ...props.sheet.spellcasting, slots } });
};
</script>

<template>
  <div v-if="hasAnySlots" class="mb-4 bg-blue-950/20 border border-blue-500/20 rounded-3xl p-5 flex flex-wrap gap-8 items-start shadow-inner relative">
    <!-- 移除 overflow-hidden 以允许弹窗溢出显示 -->
    
    <!-- 装饰背景 (改为不使用容器裁剪) -->
    <div class="absolute top-0 right-4 p-4 opacity-5 pointer-events-none">
       <Sparkles class="w-12 h-12 text-blue-400" />
    </div>

    <div class="flex flex-col gap-1 pr-6 border-r border-blue-500/20 shrink-0">
      <div class="flex items-center gap-2">
        <Sparkles class="w-4 h-4 text-blue-400" />
        <span class="text-[11px] font-black text-blue-400 uppercase tracking-widest">法术位追踪</span>
      </div>
      <span class="text-[9px] text-zinc-600 font-bold uppercase">Spell Slot Management</span>
    </div>

    <!-- 标准法术位 -->
    <div class="flex flex-wrap gap-6 items-start">
      <div v-for="(slot, level) in sheet.spellcasting.slots" :key="level" class="group/slot relative">
        <div v-if="slot.max_slots > 0 || slot.override" class="flex flex-col items-center gap-2">
          <div class="flex items-center gap-1">
            <span class="text-[9px] font-black text-zinc-500">{{ level }} 环</span>
            <button @click="showSettings = level.toString()" class="opacity-0 group-hover/slot:opacity-100 transition-opacity p-0.5 text-zinc-600 hover:text-blue-400">
              <Settings2 class="w-2.5 h-2.5" />
            </button>
          </div>
          <div class="flex gap-1">
            <button 
              v-for="i in slot.max_slots" :key="i"
              @click="updateSlotExpended(level.toString(), slot.expended >= i ? -1 : 1)"
              class="w-3.5 h-3.5 rounded-sm border transition-all"
              :class="slot.expended >= i ? 'bg-zinc-800 border-zinc-700' : 'bg-blue-600 shadow-[0_0_8px_rgba(37,99,235,0.4)] border-blue-400'"
            ></button>
            <span v-if="slot.max_slots === 0" class="text-[10px] text-zinc-700 italic">未习得</span>
          </div>
        </div>

        <!-- 快捷调整弹窗 (增加 z-index 和背景模糊) -->
        <div v-if="showSettings === level.toString()" class="absolute top-full left-1/2 -translate-x-1/2 mt-2 z-[100] bg-zinc-900 border border-zinc-700 rounded-xl p-3 shadow-2xl min-w-[120px] animate-in zoom-in-95 duration-200 backdrop-blur-md">
          <div class="flex justify-between items-center mb-2">
            <span class="text-[8px] font-black text-zinc-500 uppercase">修改 {{ level }} 环上限</span>
            <button @click="showSettings = null"><X class="w-3 h-3 text-zinc-600 hover:text-white" /></button>
          </div>
          <div class="flex flex-col gap-2">
            <input 
              type="number" 
              placeholder="自动计算"
              :value="slot.override ?? ''"
              @input="e => updateOverride(level.toString(), (e.target as HTMLInputElement).value)"
              class="w-full bg-zinc-950 border border-zinc-800 rounded px-2 py-1.5 text-xs text-blue-400 font-bold outline-none focus:border-blue-500 shadow-inner"
            />
            <p class="text-[7px] text-zinc-600 italic">留空恢复默认计算</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>