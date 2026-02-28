<script setup lang="ts">
import { ref } from 'vue';
import { Heart, ShieldCheck, Wind, Timer, Crosshair, Lock, ChevronDown, ChevronUp, Dice5, CheckCircle2, XCircle, Circle, Plus, Minus } from 'lucide-vue-next';

const props = defineProps<{
  combat: any;
  level: number; 
}>();

const emit = defineEmits(['update:combat']);

const isRollsVisible = ref(false);

const updateCombat = (field: string, value: any) => {
  const newCombat = { ...props.combat, [field]: value };
  emit('update:combat', newCombat);
};

const adjustValue = (field: string, delta: number) => {
  const currentValue = parseInt(props.combat[field]) || 0;
  const newValue = Math.max(0, currentValue + delta);
  updateCombat(field, newValue);
};

const updateHPRoll = (index: number, value: any) => {
  if (index >= props.level) return;
  const safeValue = isNaN(parseInt(value)) ? 0 : parseInt(value);
  const newRolls = [...props.combat.hp_rolls];
  while (newRolls.length <= index) newRolls.push(0);
  newRolls[index] = safeValue;
  updateCombat('hp_rolls', newRolls);
};

const toggleDeathSave = (type: 'successes' | 'failures', index: number) => {
  const currentCount = props.combat.death_saves[type];
  const newCount = currentCount === index + 1 ? index : index + 1;
  const newSaves = { ...props.combat.death_saves, [type]: newCount };
  updateCombat('death_saves', newSaves);
};
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-4 gap-3 mb-2">
    <!-- HP Block -->
    <div class="md:col-span-2 bg-zinc-800/80 border border-zinc-700/50 rounded-2xl p-4 flex flex-col justify-center shadow-lg relative group overflow-hidden">
      <div class="absolute top-0 left-0 w-1.5 h-full bg-red-600/50"></div>
      
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <Heart class="w-4 h-4 text-red-500 fill-red-500/20" />
          <span class="font-black text-zinc-500 uppercase text-[10px] tracking-widest">角色生命状态</span>
        </div>
        
        <!-- 死亡豁免 -->
        <div class="flex gap-4 items-center bg-zinc-900/50 px-3 py-1 rounded-full border border-white/5">
          <div class="flex items-center gap-1.5">
            <span class="text-[9px] font-black text-zinc-500 uppercase tracking-tighter">成功</span>
            <div class="flex gap-1">
              <button v-for="i in 3" :key="'s'+i" @click="toggleDeathSave('successes', i-1)">
                <CheckCircle2 v-if="combat.death_saves.successes >= i" class="w-3.5 h-3.5 text-emerald-500 fill-emerald-500/20" />
                <Circle v-else class="w-3.5 h-3.5 text-zinc-700" />
              </button>
            </div>
          </div>
          <div class="w-px h-3 bg-zinc-800"></div>
          <div class="flex items-center gap-1.5">
            <span class="text-[9px] font-black text-zinc-500 uppercase tracking-tighter">失败</span>
            <div class="flex gap-1">
              <button v-for="i in 3" :key="'f'+i" @click="toggleDeathSave('failures', i-1)">
                <XCircle v-if="combat.death_saves.failures >= i" class="w-3.5 h-3.5 text-red-600 fill-red-600/20" />
                <Circle v-else class="w-3.5 h-3.5 text-zinc-700" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-3 font-mono">
        <!-- 当前 HP 控制 -->
        <div class="flex items-center bg-zinc-900/80 border border-zinc-700 rounded-xl px-1">
          <button @click="adjustValue('hp_current', -1)" class="p-1.5 text-zinc-500 hover:text-red-500 transition-colors"><Minus class="w-4 h-4" /></button>
          <input 
            type="number" 
            :value="combat.hp_current"
            @input="e => updateCombat('hp_current', parseInt((e.target as HTMLInputElement).value))"
            class="w-16 bg-transparent py-1 text-center text-4xl font-black text-white outline-none transition-all no-spinner"
          />
          <button @click="adjustValue('hp_current', 1)" class="p-1.5 text-zinc-500 hover:text-emerald-500 transition-colors"><Plus class="w-4 h-4" /></button>
        </div>
        
        <span class="text-4xl font-black text-zinc-600">/</span>
        
        <!-- 上限 HP -->
        <div class="text-5xl font-black text-zinc-400 min-w-[60px] text-center">
          {{ combat.hp_max }}
        </div>

        <!-- 临时 HP 控制 -->
        <div class="flex items-center bg-blue-900/10 border border-blue-900/20 rounded-xl px-1 ml-2">
          <button @click="adjustValue('temp_hp', -1)" class="p-1 text-blue-900/50 hover:text-blue-400"><Minus class="w-3.5 h-3.5" /></button>
          <div class="flex items-center gap-1">
            <span class="text-2xl font-black text-blue-500/50 ml-1">+</span>
            <input 
              type="number" 
              :value="combat.temp_hp"
              @input="e => updateCombat('temp_hp', parseInt((e.target as HTMLInputElement).value))"
              class="w-14 bg-transparent py-1 text-center text-3xl font-black text-blue-400 outline-none transition-all no-spinner"
            />
          </div>
          <button @click="adjustValue('temp_hp', 1)" class="p-1 text-blue-900/50 hover:text-blue-400"><Plus class="w-3.5 h-3.5" /></button>
        </div>
      </div>

      <!-- 生命骰区域保持不变 -->
      <div class="mt-4 pt-2 border-t border-zinc-700/30">
        <button 
          @click="isRollsVisible = !isRollsVisible"
          class="flex items-center gap-2 text-[10px] font-black text-zinc-500 uppercase hover:text-zinc-200 transition-colors"
        >
          <Dice5 class="w-3 h-3" />
          升级生命骰记录
          <component :is="isRollsVisible ? ChevronUp : ChevronDown" class="w-3 h-3" />
        </button>

        <div v-show="isRollsVisible" class="mt-3 flex flex-wrap gap-1.5 justify-start animate-in fade-in slide-in-from-top-1 duration-200">
          <div v-for="i in 20" :key="i" class="flex flex-col items-center">
            <div class="relative group">
              <input 
                type="number"
                :value="combat.hp_rolls[i-1] || 0"
                :readonly="i > level"
                @input="e => updateHPRoll(i-1, (e.target as HTMLInputElement).value)"
                class="w-8 border rounded text-center text-[10px] py-1 transition-all font-black text-red-500 no-spinner"
                :class="[
                  i <= level 
                    ? 'bg-zinc-900 border-zinc-700 focus:border-red-400' 
                    : 'bg-zinc-950/50 border-zinc-800 cursor-not-allowed opacity-30 pointer-events-none'
                ]"
              />
              <div v-if="i > level" class="absolute -top-1 -right-1 bg-zinc-900 rounded-full p-0.5 border border-zinc-800">
                <Lock class="w-1.5 h-1.5 text-zinc-600" />
              </div>
            </div>
            <span class="text-[8px] font-black mt-1" :class="i <= level ? 'text-zinc-200' : 'text-zinc-700'">L{{ i }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- AC / Init / Speed / PB 保持不变 -->
    <div class="grid grid-cols-2 gap-3 md:col-span-2">
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
            type="number" 
            :value="combat.speed"
            @input="e => updateCombat('speed', parseInt((e.target as HTMLInputElement).value))"
            class="w-16 bg-transparent text-4xl font-black text-white text-center outline-none focus:text-red-500 no-spinner"
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
  </div>
</template>

<style scoped>
.no-spinner::-webkit-outer-spin-button,
.no-spinner::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.no-spinner {
  -moz-appearance: textfield;
}
</style>
