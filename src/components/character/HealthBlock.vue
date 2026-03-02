<script setup lang="ts">
import { computed } from 'vue';
import { Heart, CheckCircle2, XCircle, Circle, Plus, Minus } from 'lucide-vue-next';

const props = defineProps<{
  combat: any;
  sheet: any;
  level: number;
}>();

const emit = defineEmits(['update:combat']);

// 汇总生命骰：从 classes 列表中提取
const aggregatedHitDice = computed(() => {
  const totals: Record<string, number> = {};
  props.sheet?.prog?.classes?.forEach((c: any) => {
    const type = c.hit_die || 'd8';
    totals[type] = (totals[type] || 0) + c.level;
  });
  return totals;
});

const updateCombat = (field: string, value: any) => {
  emit('update:combat', { ...props.combat, [field]: value });
};

const adjustValue = (field: string, delta: number) => {
  const newVal = Math.max(0, (parseInt(props.combat[field]) || 0) + delta);
  updateCombat(field, newVal);
};

const toggleDeathSave = (type: 'successes' | 'failures', index: number) => {
  const current = props.combat.death_saves[type];
  const newVal = current === index + 1 ? index : index + 1;
  const newSaves = { ...props.combat.death_saves, [type]: newVal };
  updateCombat('death_saves', newSaves);
};

const updateHD = (type: string, delta: number) => {
  const hd = props.combat.hit_dice || {};
  const slot = hd[type] || { total: 0, expended: 0 };
  const max = aggregatedHitDice.value[type] || 0;
  const newExp = Math.max(0, Math.min(max, slot.expended + delta));
  updateCombat('hit_dice', { ...hd, [type]: { total: max, expended: newExp } });
};
</script>

<template>
  <div class="bg-zinc-800/80 border border-zinc-700/50 rounded-2xl p-4 shadow-lg relative overflow-hidden">
    <div class="absolute top-0 left-0 w-1.5 h-full bg-red-600/50"></div>
    
    <!-- 头部：HP 与 死亡豁免 -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <Heart class="w-4 h-4 text-red-500 fill-red-500/20" />
        <span class="font-black text-zinc-500 uppercase text-[10px] tracking-widest">生命状态</span>
      </div>
      
      <div class="flex gap-3 items-center bg-zinc-950/50 px-2 py-1 rounded-full border border-white/5">
        <div class="flex gap-0.5">
          <button v-for="i in 3" :key="'s'+i" @click="toggleDeathSave('successes', i-1)">
            <CheckCircle2 v-if="combat.death_saves.successes >= i" class="w-3 h-3 text-emerald-500" />
            <Circle v-else class="w-3 h-3 text-zinc-800" />
          </button>
        </div>
        <div class="w-px h-3 bg-zinc-800"></div>
        <div class="flex gap-0.5">
          <button v-for="i in 3" :key="'f'+i" @click="toggleDeathSave('failures', i-1)">
            <XCircle v-if="combat.death_saves.failures >= i" class="w-3 h-3 text-red-600" />
            <Circle v-else class="w-3 h-3 text-zinc-800" />
          </button>
        </div>
      </div>
    </div>

    <div class="flex items-start gap-6">
      <!-- HP 控制 -->
      <div class="flex items-center gap-2 font-mono">
        <div class="flex items-center bg-zinc-900 border border-zinc-700 rounded-xl px-1">
          <button @click="adjustValue('hp_current', -1)" class="p-1 text-zinc-500 hover:text-red-500"><Minus class="w-4 h-4" /></button>
          <input 
            type="number" :value="combat.hp_current"
            @input="e => updateCombat('hp_current', parseInt((e.target as HTMLInputElement).value))"
            class="w-14 bg-transparent text-3xl font-black text-white text-center outline-none"
          />
          <button @click="adjustValue('hp_current', 1)" class="p-1 text-zinc-500 hover:text-emerald-500"><Plus class="w-4 h-4" /></button>
        </div>
        <span class="text-2xl font-black text-zinc-700">/</span>
        <span class="text-4xl font-black text-zinc-400">{{ combat.hp_max }}</span>
      </div>

      <!-- 短休生命骰 (联动) -->
      <div class="flex-1 border-l border-zinc-700/50 pl-4">
        <span class="text-[8px] font-black text-zinc-600 uppercase tracking-widest block mb-2">短休生命骰 (Hit Dice)</span>
        <div class="space-y-2">
          <div v-for="(total, type) in aggregatedHitDice" :key="type" class="flex flex-col gap-1">
            <div class="flex items-center justify-between text-[9px] font-bold">
              <span class="text-zinc-500">{{ type }}</span>
              <span class="text-zinc-400">{{ total - (combat.hit_dice[type]?.expended || 0) }} / {{ total }}</span>
            </div>
            <div class="flex flex-wrap gap-1">
              <button 
                v-for="n in total" :key="n"
                @click="updateHD(type.toString(), (combat.hit_dice[type]?.expended || 0) >= (total - n + 1) ? -1 : 1)"
                class="w-2.5 h-2.5 rounded-sm border rotate-45 transition-all"
                :class="(combat.hit_dice[type]?.expended || 0) >= (total - n + 1) ? 'bg-zinc-900 border-zinc-800' : 'bg-red-500 border-red-400 shadow-[0_0_5px_rgba(239,68,68,0.3)]'"
              ></button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 临时 HP -->
    <div class="mt-4 flex items-center gap-2 bg-blue-900/10 border border-blue-900/20 rounded-lg p-1.5 w-fit">
      <span class="text-[9px] font-black text-blue-500 uppercase px-1">临时生命</span>
      <div class="flex items-center">
        <button @click="adjustValue('temp_hp', -1)" class="p-0.5 text-blue-900/50 hover:text-blue-400"><Minus class="w-3 h-3" /></button>
        <input 
          type="number" :value="combat.temp_hp"
          @input="e => updateCombat('temp_hp', parseInt((e.target as HTMLInputElement).value))"
          class="w-10 bg-transparent text-center text-sm font-black text-blue-400 outline-none"
        />
        <button @click="adjustValue('temp_hp', 1)" class="p-0.5 text-blue-900/50 hover:text-blue-400"><Plus class="w-3 h-3" /></button>
      </div>
    </div>
  </div>
</template>