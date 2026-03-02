<script setup lang="ts">
import { ref } from 'vue';
import { Shield, Zap, Target, X, Footprints } from 'lucide-vue-next';

const props = defineProps<{ sheet: any }>();
const emit = defineEmits(['update']);

const showAdjuster = ref<string | null>(null);

const updateVal = (key: 'armor_class' | 'initiative', field: string, val: number) => {
  const combat = { ...props.sheet.combat };
  combat[key] = { ...combat[key], [field]: val };
  emit('update', { combat });
};

const updateSimple = (field: string, val: any) => {
  const combat = { ...props.sheet.combat, [field]: val };
  emit('update', { combat });
};

const updateDC = (updates: any) => {
  const combat = { ...props.sheet.combat };
  combat.general_dc = { ...combat.general_dc, ...updates };
  emit('update', { combat });
};

const getAbilityLabel = (key: string) => {
  const map: any = { strength: '力量', dexterity: '敏捷', constitution: '体质', intelligence: '智力', wisdom: '感知', charisma: '魅力' };
  return map[key] || key;
};
</script>

<template>
  <div class="grid grid-cols-2 gap-2 h-full">
    <!-- AC -->
    <div 
      @click="showAdjuster = 'ac'"
      class="bg-zinc-950/40 border border-zinc-800/50 rounded-2xl p-3 flex flex-col items-center justify-center hover:bg-zinc-800/40 transition-all cursor-pointer group shadow-inner"
    >
      <div class="flex items-center gap-2 mb-1">
        <Shield class="w-4 h-4 text-blue-500 opacity-60 group-hover:opacity-100" />
        <span class="text-[9px] font-black text-zinc-500 uppercase tracking-widest leading-none">护甲等级</span>
      </div>
      <div class="flex items-baseline gap-1">
        <span class="text-2xl font-black text-zinc-100 leading-none">{{ sheet.combat.armor_class.derived }}</span>
        <span v-if="sheet.combat.armor_class.bonus !== 0" class="text-xs font-bold text-blue-400">
          {{ sheet.combat.armor_class.bonus > 0 ? '+' : '' }}{{ sheet.combat.armor_class.bonus }}
        </span>
      </div>
    </div>

    <!-- Initiative -->
    <div 
      @click="showAdjuster = 'init'"
      class="bg-zinc-950/40 border border-zinc-800/50 rounded-2xl p-3 flex flex-col items-center justify-center hover:bg-zinc-800/40 transition-all cursor-pointer group shadow-inner"
    >
      <div class="flex items-center gap-2 mb-1">
        <Zap class="w-4 h-4 text-amber-500 opacity-60 group-hover:opacity-100" />
        <span class="text-[9px] font-black text-zinc-500 uppercase tracking-widest leading-none">先攻加值</span>
      </div>
      <div class="flex items-baseline gap-1">
        <span class="text-2xl font-black text-zinc-100 leading-none">
          {{ sheet.combat.initiative.derived >= 0 ? '+' : '' }}{{ sheet.combat.initiative.derived }}
        </span>
      </div>
    </div>

    <!-- Speed -->
    <div 
      @click="showAdjuster = 'speed'"
      class="bg-zinc-950/40 border border-zinc-800/50 rounded-2xl p-3 flex flex-col items-center justify-center hover:bg-zinc-800/40 transition-all cursor-pointer group shadow-inner"
    >
      <div class="flex items-center gap-2 mb-1">
        <Footprints class="w-4 h-4 text-zinc-500 opacity-60 group-hover:opacity-100" />
        <span class="text-[9px] font-black text-zinc-500 uppercase tracking-widest leading-none">移动速度</span>
      </div>
      <div class="flex items-baseline gap-1">
        <span class="text-2xl font-black text-zinc-100 leading-none">{{ sheet.combat.speed }}</span>
        <span class="text-[9px] font-black text-zinc-600 uppercase tracking-tighter">尺</span>
      </div>
    </div>

    <!-- DC -->
    <div 
      @click="showAdjuster = 'dc'"
      class="bg-zinc-950/40 border border-zinc-800/50 rounded-2xl p-3 flex flex-col items-center justify-center hover:bg-zinc-800/40 transition-all cursor-pointer group shadow-inner"
    >
      <div class="flex items-center gap-2 mb-1">
        <Target class="w-4 h-4 text-emerald-500 opacity-60 group-hover:opacity-100" />
        <span class="text-[8px] font-black text-zinc-500 uppercase tracking-widest leading-none">通用 DC</span>
      </div>
      <div class="flex items-baseline gap-1">
        <span class="text-2xl font-black text-zinc-100 leading-none">{{ sheet.combat.general_dc.derived }}</span>
        <span class="text-[8px] font-black text-zinc-600 uppercase tracking-tighter ml-1">{{ getAbilityLabel(sheet.combat.general_dc.ability).substring(0,2) }}</span>
      </div>
    </div>

    <!-- 调整抽屉 -->
    <div v-if="showAdjuster" class="fixed inset-0 z-[110] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showAdjuster = null"></div>
      <div class="relative bg-zinc-900 border border-zinc-700 w-full max-w-xs rounded-3xl p-6 shadow-2xl animate-in zoom-in-95 duration-200">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-black text-white uppercase tracking-tighter">
            {{ showAdjuster === 'ac' ? '调整护甲等级' : showAdjuster === 'init' ? '调整先攻' : showAdjuster === 'speed' ? '调整移动速度' : '调整通用 DC' }}
          </h3>
          <button @click="showAdjuster = null" class="text-zinc-500 hover:text-white"><X class="w-5 h-5" /></button>
        </div>

        <div v-if="showAdjuster === 'ac' || showAdjuster === 'init'" class="space-y-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-[9px] font-black text-zinc-500 uppercase">临时加值</label>
            <input 
              type="number" 
              :value="sheet.combat[showAdjuster === 'ac' ? 'armor_class' : 'initiative'].bonus"
              @input="e => updateVal(showAdjuster === 'ac' ? 'armor_class' : 'initiative', 'bonus', parseInt((e.target as HTMLInputElement).value) || 0)"
              class="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2 text-xl font-black text-blue-400 outline-none"
            />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[9px] font-black text-zinc-500 uppercase">强制覆盖值</label>
            <input 
              type="number" 
              placeholder="留空则不覆盖"
              :value="sheet.combat[showAdjuster === 'ac' ? 'armor_class' : 'initiative'].override || ''"
              @input="e => updateVal(showAdjuster === 'ac' ? 'armor_class' : 'initiative', 'override', parseInt((e.target as HTMLInputElement).value) || 0)"
              class="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2 text-xl font-black text-zinc-400 outline-none"
            />
          </div>
        </div>

        <div v-if="showAdjuster === 'speed'" class="space-y-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-[9px] font-black text-zinc-500 uppercase">基础移动速度</label>
            <input 
              type="number" 
              :value="sheet.combat.speed"
              @input="e => updateSimple('speed', parseInt((e.target as HTMLInputElement).value) || 0)"
              class="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2 text-3xl font-black text-zinc-100 outline-none"
            />
          </div>
        </div>

        <div v-if="showAdjuster === 'dc'" class="space-y-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-[9px] font-black text-zinc-500 uppercase">关联属性</label>
            <select 
              :value="sheet.combat.general_dc.ability"
              @change="e => updateDC({ ability: (e.target as HTMLSelectElement).value })"
              class="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2 text-sm font-bold text-zinc-300 outline-none"
            >
              <option v-for="a in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']" :key="a" :value="a">
                {{ getAbilityLabel(a) }}
              </option>
            </select>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[9px] font-black text-zinc-500 uppercase">临时加值</label>
            <input 
              type="number" 
              :value="sheet.combat.general_dc.bonus"
              @input="e => updateDC({ bonus: parseInt((e.target as HTMLInputElement).value) || 0 })"
              class="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2 text-xl font-black text-emerald-400 outline-none"
            />
          </div>
        </div>

        <button @click="showAdjuster = null" class="w-full mt-6 bg-zinc-100 text-zinc-900 py-3 rounded-xl font-black text-sm hover:bg-white transition-all shadow-xl">完成修改</button>
      </div>
    </div>
  </div>
</template>