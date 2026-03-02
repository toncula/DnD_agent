<script setup lang="ts">
import { computed } from 'vue';
import { Sparkles } from 'lucide-vue-next';

const props = defineProps<{
  sheet: any;
}>();

const emit = defineEmits(['update:sheet']);

const hasAnySlots = computed(() => {
  if (!props.sheet?.spellcasting?.slots) return false;
  return Object.values(props.sheet.spellcasting.slots).some((s: any) => s.max_slots > 0);
});

const updateSlotExpended = (level: string, delta: number) => {
  const slots = JSON.parse(JSON.stringify(props.sheet.spellcasting.slots));
  slots[level].expended = Math.max(0, Math.min(slots[level].max_slots, slots[level].expended + delta));
  emit('update:sheet', { spellcasting: { ...props.sheet.spellcasting, slots } });
};
</script>

<template>
  <div v-if="hasAnySlots" class="mb-4 bg-blue-950/20 border border-blue-500/20 rounded-2xl p-4 flex flex-wrap gap-6 items-center shadow-inner">
    <div class="flex items-center gap-2 pr-4 border-r border-blue-500/20">
      <Sparkles class="w-4 h-4 text-blue-400" />
      <span class="text-[10px] font-black text-blue-500 uppercase tracking-widest">法术位追踪</span>
    </div>
    <div v-for="(slot, level) in sheet.spellcasting.slots" :key="level">
      <div v-if="slot.max_slots > 0" class="flex flex-col items-center gap-1.5">
        <span class="text-[9px] font-black text-zinc-500">{{ level }} 环</span>
        <div class="flex gap-1">
          <button 
            v-for="i in slot.max_slots" :key="i"
            @click="updateSlotExpended(level.toString(), slot.expended >= i ? -1 : 1)"
            class="w-3 h-3 rounded-sm border transition-all"
            :class="slot.expended >= i ? 'bg-zinc-800 border-zinc-700' : 'bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)] border-blue-400'"
          ></button>
        </div>
      </div>
    </div>
  </div>
</template>