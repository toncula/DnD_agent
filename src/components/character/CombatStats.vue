<script setup lang="ts">
import { ref } from 'vue';
import { ChevronDown, ChevronUp, Dice5, Lock } from 'lucide-vue-next';
import SpellSlotTracker from './SpellSlotTracker.vue';
import HealthBlock from './HealthBlock.vue';
import MiscCombatStats from './MiscCombatStats.vue';

const props = defineProps<{
  combat: any;
  level: number;
  sheet: any;
}>();

const emit = defineEmits(['update:combat', 'update:sheet']);

const isRollsVisible = ref(false);

const updateCombat = (newCombat: any) => {
  emit('update:combat', newCombat);
};

const updateSheet = (partial: any) => {
  emit('update:sheet', partial);
};

const updateHPRoll = (index: number, value: any) => {
  if (index >= props.level) return;
  const safeValue = isNaN(parseInt(value)) ? 0 : parseInt(value);
  const newRolls = [...props.combat.hp_rolls];
  while (newRolls.length <= index) newRolls.push(0);
  newRolls[index] = safeValue;
  emit('update:combat', { ...props.combat, hp_rolls: newRolls });
};
</script>

<template>
  <div class="space-y-4">
    <!-- 1. 法术位追踪 (子组件) -->
    <SpellSlotTracker :sheet="sheet" @update:sheet="updateSheet" />

    <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
      <!-- 2. 生命与生命骰追踪 (子组件) -->
      <div class="md:col-span-2">
        <HealthBlock 
          :combat="combat" 
          :sheet="sheet" 
          :level="level"
          @update:combat="updateCombat" 
        />
      </div>

      <!-- 3. 基础战斗属性 (子组件) -->
      <div class="md:col-span-2">
        <MiscCombatStats 
          :combat="combat" 
          @update:combat="updateCombat" 
        />
      </div>
    </div>

    <!-- 4. 生命骰历史记录 (抽屉) -->
    <div class="bg-zinc-900/30 border border-zinc-800 rounded-2xl p-4 mt-2">
      <button 
        @click="isRollsVisible = !isRollsVisible"
        class="flex items-center gap-2 text-[10px] font-black text-zinc-500 uppercase hover:text-zinc-200 transition-colors"
      >
        <Dice5 class="w-3 h-3" />
        每级生命骰明细 (HP History)
        <component :is="isRollsVisible ? ChevronUp : ChevronDown" class="w-3 h-3" />
      </button>

      <div v-show="isRollsVisible" class="mt-4 flex flex-wrap gap-2 animate-in fade-in slide-in-from-top-1 duration-200">
        <div v-for="i in 20" :key="i" class="flex flex-col items-center">
          <div class="relative group">
            <input 
              type="number" :value="combat.hp_rolls[i-1] || 0" :readonly="i > level"
              @input="e => updateHPRoll(i-1, (e.target as HTMLInputElement).value)"
              class="w-9 border rounded text-center text-[10px] py-1 transition-all font-black text-red-500"
              :class="i <= level ? 'bg-zinc-950 border-zinc-700' : 'bg-zinc-950/20 border-zinc-800 opacity-20 pointer-events-none'"
            />
            <div v-if="i > level" class="absolute -top-1 -right-1 bg-zinc-900 rounded-full p-0.5 border border-zinc-800"><Lock class="w-1.5 h-1.5 text-zinc-600" /></div>
          </div>
          <span class="text-[8px] font-black mt-1" :class="i <= level ? 'text-zinc-400' : 'text-zinc-800'">L{{ i }}</span>
        </div>
      </div>
    </div>
  </div>
</template>