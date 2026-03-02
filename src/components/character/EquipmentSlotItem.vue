<script setup lang="ts">
const props = defineProps<{
  label: string;
  icon: any;
  active?: boolean;
  value?: string;
}>();

defineEmits(['click']);
</script>

<template>
  <div 
    @click="$emit('click')"
    :class="[
      'w-14 h-14 rounded-xl border-2 flex flex-col items-center justify-center cursor-pointer transition-all duration-300 relative group/slot',
      active 
        ? 'bg-blue-600/20 border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.3)]' 
        : 'bg-zinc-950/80 border-zinc-800 hover:border-zinc-600'
    ]"
  >
    <component :is="icon" :class="['w-6 h-6', active ? 'text-blue-400' : 'text-zinc-600 group-hover/slot:text-zinc-400']" />
    <div v-if="value && value !== '空手'" class="absolute -bottom-1 left-1/2 -translate-x-1/2 bg-blue-600 text-[8px] font-black px-1.5 rounded-full text-white whitespace-nowrap border border-zinc-900">
      {{ value }}
    </div>
    <span class="absolute -top-6 text-[10px] font-bold text-zinc-600 opacity-0 group-hover/slot:opacity-100 transition-opacity whitespace-nowrap">
      {{ label }}
    </span>
  </div>
</template>