<script setup lang="ts">
import { ShieldCheck, Timer, Wind, Crosshair } from 'lucide-vue-next';

const props = defineProps<{
  combat: any;
}>();

const emit = defineEmits(['update:combat']);

const updateCombat = (field: string, value: any) => {
  emit('update:combat', { ...props.combat, [field]: value });
};
</script>

<template>
  <div class="grid grid-cols-2 gap-3">
    <div class="bg-zinc-800/80 border border-zinc-700/50 rounded-2xl p-3 flex flex-col items-center justify-center shadow-lg group">
      <ShieldCheck class="w-4 h-4 text-blue-500 mb-1 opacity-50" />
      <span class="text-5xl font-black text-white leading-none tracking-tighter">{{ combat.armor_class }}</span>
      <span class="text-xs font-black text-zinc-500 uppercase tracking-widest mt-2">护甲等级</span>
    </div>

    <div class="bg-zinc-800/80 border border-zinc-700/50 rounded-2xl p-3 flex flex-col items-center justify-center shadow-lg group">
      <Timer class="w-4 h-4 text-amber-500 mb-1 opacity-50" />
      <span class="text-5xl font-black text-white leading-none tracking-tighter">{{ combat.initiative >= 0 ? '+' : '' }}{{ combat.initiative }}</span>
      <span class="text-xs font-black text-zinc-500 uppercase tracking-widest mt-2">先攻加值</span>
    </div>

    <div class="bg-zinc-800/80 border border-zinc-700/50 rounded-2xl p-3 flex flex-col items-center justify-center shadow-lg group">
      <Wind class="w-4 h-4 text-emerald-500 mb-1 opacity-50" />
      <div class="flex items-baseline gap-0.5">
        <input 
          type="number" :value="combat.speed"
          @input="e => updateCombat('speed', parseInt((e.target as HTMLInputElement).value))"
          class="w-16 bg-transparent text-4xl font-black text-white text-center outline-none no-spinner"
        />
      </div>
      <span class="text-xs font-black text-zinc-500 uppercase tracking-widest mt-1">速度 (尺)</span>
    </div>

    <div class="bg-zinc-800/80 border border-zinc-700/50 rounded-2xl p-3 flex flex-col items-center justify-center shadow-lg group">
      <Crosshair class="w-4 h-4 text-purple-500 mb-1 opacity-50" />
      <span class="text-4xl font-black text-white leading-none tracking-tighter">+{{ combat.proficiency_bonus }}</span>
      <span class="text-xs font-black text-zinc-500 uppercase tracking-widest mt-2">熟练加值</span>
    </div>
  </div>
</template>

<style scoped>
.no-spinner::-webkit-outer-spin-button,
.no-spinner::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
.no-spinner { -moz-appearance: textfield; }
</style>