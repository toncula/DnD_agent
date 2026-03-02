<script setup lang="ts">
import { computed, ref } from 'vue';
import { Heart, CheckCircle2, XCircle, Circle, Plus, Minus, X } from 'lucide-vue-next';

const props = defineProps<{
  combat: any;
  sheet: any;
  level: number;
}>();

const emit = defineEmits(['update:combat']);

const showHpAdjuster = ref(false);

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

const updateHpField = (field: string, val: number) => {
  const hp_max = { ...props.combat.hp_max, [field]: val };
  updateCombat('hp_max', hp_max);
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
        <div class="flex flex-col items-start cursor-pointer group" @click="showHpAdjuster = true">
          <span class="text-4xl font-black text-zinc-400 leading-none group-hover:text-white transition-colors">{{ combat.hp_max.derived }}</span>
          <span v-if="combat.hp_max.bonus !== 0" class="text-[10px] font-black text-blue-400 mt-1">
            {{ combat.hp_max.bonus > 0 ? '+' : '' }}{{ combat.hp_max.bonus }} 修正
          </span>
        </div>
      </div>

      <div class="flex-1 border-l border-zinc-700/50 pl-4">
        <span class="text-[8px] font-black text-zinc-600 uppercase tracking-widest block mb-2">短休生命骰</span>
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

    <div v-if="showHpAdjuster" class="fixed inset-0 z-[120] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showHpAdjuster = false"></div>
      <div class="relative bg-zinc-900 border border-zinc-700 w-full max-w-xs rounded-3xl p-6 shadow-2xl animate-in zoom-in-95 duration-200">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-black text-white uppercase tracking-tighter">调整生命上限</h3>
          <button @click="showHpAdjuster = false" class="text-zinc-500 hover:text-white"><X class="w-5 h-5" /></button>
        </div>
        <div class="space-y-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-[9px] font-black text-zinc-500 uppercase tracking-widest">基础计算值</label>
            <div class="bg-zinc-950 p-2 rounded-xl text-zinc-400 font-mono text-center text-xl border border-zinc-800">{{ combat.hp_max.base }}</div>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[9px] font-black text-blue-500 uppercase tracking-widest">临时修正</label>
            <input 
              type="number" 
              :value="combat.hp_max.bonus"
              @input="e => updateHpField('bonus', parseInt((e.target as HTMLInputElement).value) || 0)"
              class="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2 text-xl font-black text-blue-400 outline-none"
            />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[9px] font-black text-amber-500 uppercase tracking-widest">强制覆盖值</label>
            <input 
              type="number" 
              placeholder="留空则不覆盖"
              :value="combat.hp_max.override || ''"
              @input="e => updateHpField('override', parseInt((e.target as HTMLInputElement).value) || 0)"
              class="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2 text-xl font-black text-zinc-100 outline-none"
            />
          </div>
        </div>
        <button @click="showHpAdjuster = false" class="w-full mt-6 bg-zinc-100 text-zinc-900 py-3 rounded-xl font-black text-sm hover:bg-white transition-all shadow-xl">确认修改</button>
      </div>
    </div>
  </div>
</template>