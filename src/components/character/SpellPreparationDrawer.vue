<script setup lang="ts">
import { ref, computed } from 'vue';
import { BookOpen, Check, X, Search, Star } from 'lucide-vue-next';

const props = defineProps<{
  spells: any[];
  prepLimit: number;
  preparedCount: number;
  show: boolean;
}>();

const emit = defineEmits(['close', 'update:spells']);

const searchQuery = ref('');

const filteredAllSpells = computed(() => {
  return props.spells.filter(s => 
    s.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  ).sort((a, b) => a.level - b.level);
});

const updateSpell = (spellName: string, updates: any) => {
  const newList = props.spells.map(s => s.name === spellName ? { ...s, ...updates } : s);
  emit('update:spells', newList);
};

const toggleSpellPrepared = (spell: any) => {
  if (spell.is_always_prepared) return; // 恒定法术无法取消常规准备
  if (!spell.is_prepared && props.preparedCount >= props.prepLimit && spell.level > 0) return;
  updateSpell(spell.name, { is_prepared: !spell.is_prepared });
};

const toggleAlwaysPrepared = (spell: any) => {
  const isAlways = !spell.is_always_prepared;
  // 如果设为恒定准备，则自动视为已准备；如果取消，则保留普通准备状态
  updateSpell(spell.name, { is_always_prepared: isAlways, is_prepared: isAlways ? true : spell.is_prepared });
};

const setOverrideAbility = (spell: any, ability: string | null) => {
  updateSpell(spell.name, { override_ability: ability });
};
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/80 backdrop-blur-md" @click="emit('close')"></div>
    <div class="relative w-full max-w-5xl h-full max-h-[85vh] bg-zinc-900 border border-zinc-700 rounded-3xl shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
      
      <!-- Drawer Header -->
      <div class="p-6 border-b border-zinc-800 flex flex-wrap items-center justify-between bg-zinc-900/50 gap-4">
        <div class="flex items-center gap-4">
          <div class="bg-blue-600 p-2 rounded-lg"><BookOpen class="w-5 h-5 text-white" /></div>
          <div>
            <h3 class="text-xl font-black text-white">今日法术整备</h3>
            <p class="text-xs text-zinc-500 font-bold uppercase">常规准备额度: <span :class="preparedCount > prepLimit ? 'text-red-500' : 'text-blue-400'">{{ preparedCount }}</span> / {{ prepLimit }}</p>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <div class="relative w-64">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <input v-model="searchQuery" placeholder="快速搜索法术..." class="w-full bg-zinc-950 border border-zinc-800 rounded-xl pl-10 pr-4 py-2 text-xs text-zinc-200 outline-none" />
          </div>
          <button @click="emit('close')" class="p-2 hover:bg-zinc-800 rounded-full transition-colors"><X class="w-6 h-6 text-zinc-500" /></button>
        </div>
      </div>

      <!-- Drawer Body -->
      <div class="flex-1 overflow-y-auto p-6 bg-zinc-950/20 custom-scrollbar">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
          <div 
            v-for="(spell, i) in filteredAllSpells" :key="i"
            class="flex items-center gap-3 p-3 rounded-xl border transition-all group relative"
            :class="[(spell.is_prepared || spell.level === 0 || spell.is_always_prepared) ? 'bg-blue-600/10 border-blue-500/40' : 'bg-zinc-900/40 border-zinc-800 grayscale opacity-60 hover:opacity-100 hover:grayscale-0']"
          >
            <!-- Preparation Checkbox -->
            <button 
              @click="spell.level > 0 ? toggleSpellPrepared(spell) : null"
              class="w-8 h-8 rounded-lg flex items-center justify-center border shrink-0 transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="spell.is_always_prepared && spell.level > 0"
              :class="(spell.is_prepared || spell.level === 0) ? 'bg-blue-500 border-blue-400 text-white' : 'bg-zinc-950 border-zinc-800 text-zinc-700'"
            >
              <span v-if="spell.level === 0" class="text-[10px] font-black">C</span>
              <Check v-else-if="spell.is_prepared" class="w-4 h-4" />
              <span v-else class="text-[10px] font-black">{{ spell.level }}</span>
            </button>
            
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <div class="text-sm font-bold truncate" :class="(spell.is_prepared || spell.level === 0) ? 'text-white' : 'text-zinc-500'">{{ spell.name }}</div>
                <div v-if="spell.is_always_prepared" class="text-[8px] bg-amber-500/20 border border-amber-500/50 text-amber-400 px-1.5 py-0.5 rounded uppercase font-black shrink-0">恒定</div>
              </div>
              <div class="text-[8px] text-zinc-500 font-bold uppercase tracking-tighter mt-0.5">{{ spell.level === 0 ? '戏法 (无需准备)' : spell.level + ' 环法术' }}</div>
            </div>

            <!-- Individual Ability & Always Prepared -->
            <div class="flex items-center gap-2">
              <div class="flex flex-col gap-0.5">
                <select 
                  :value="spell.override_ability || ''"
                  @change="e => setOverrideAbility(spell, (e.target as HTMLSelectElement).value || null)"
                  class="bg-zinc-950 border border-zinc-800 rounded px-1.5 py-1 text-[9px] outline-none"
                  :class="spell.override_ability ? 'text-blue-400 border-blue-900/50' : 'text-zinc-500'"
                >
                  <option value="">跟随全局属性</option>
                  <option value="intelligence">智力 (INT)</option>
                  <option value="wisdom">感知 (WIS)</option>
                  <option value="charisma">魅力 (CHA)</option>
                </select>
              </div>

              <button 
                v-if="spell.level > 0"
                @click="toggleAlwaysPrepared(spell)"
                class="p-2 rounded-lg border transition-all"
                :class="spell.is_always_prepared ? 'bg-amber-500/20 border-amber-500/50 text-amber-400' : 'bg-zinc-900 border-zinc-700 text-zinc-600 hover:text-amber-500 hover:border-amber-500/30'"
                title="设为恒定准备(不占用准备限额)"
              >
                <Star class="w-4 h-4" :class="{'fill-current': spell.is_always_prepared}" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Drawer Footer -->
      <div class="p-4 border-t border-zinc-800 bg-zinc-900/50 flex justify-end">
        <button @click="emit('close')" class="bg-zinc-100 text-zinc-900 px-8 py-2.5 rounded-xl font-black text-sm hover:bg-white transition-all shadow-xl">完成</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #27272a; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #3f3f46; }
select { appearance: none; -webkit-appearance: none; }
</style>