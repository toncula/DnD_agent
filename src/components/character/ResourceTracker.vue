<script setup lang="ts">
import { Plus, Trash2, RotateCcw, Settings2 } from 'lucide-vue-next';
import { ref } from 'vue';

const props = defineProps<{
  resources: any[];
}>();

const emit = defineEmits(['update']);
const editingIdx = ref<number | null>(null);

const updateResource = (index: number, delta: number) => {
  const newList = JSON.parse(JSON.stringify(props.resources));
  const res = newList[index];
  res.current = Math.max(0, Math.min(res.max, res.current + delta));
  emit('update', newList);
};

const resetResource = (index: number) => {
  const newList = JSON.parse(JSON.stringify(props.resources));
  newList[index].current = newList[index].max;
  emit('update', newList);
};

const addGenericResource = () => {
  emit('update', [...props.resources, { name: '新资源', current: 3, max: 3, reset_on: '长休' }]);
};

const removeResource = (index: number) => {
  const newList = [...props.resources];
  newList.splice(index, 1);
  emit('update', newList);
};
</script>

<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between px-1">
      <span class="text-[10px] font-black text-zinc-500 uppercase tracking-widest">职业资源</span>
      <button @click="addGenericResource" class="text-[9px] font-black text-blue-500/70 hover:text-blue-400 flex items-center gap-1 uppercase tracking-tighter transition-all">
        <Plus class="w-3.5 h-3.5" /> 添加
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
      <div 
        v-for="(res, i) in resources" 
        :key="i"
        class="bg-zinc-900/60 border border-zinc-800/50 rounded-xl p-2 pr-3 flex items-center gap-3 group relative hover:border-zinc-700 transition-all"
      >
        <div class="flex flex-col min-w-[60px]">
          <input 
            v-model="res.name" 
            class="bg-transparent font-bold text-[11px] text-zinc-200 outline-none focus:text-blue-400 truncate w-20"
            @change="emit('update', resources)"
          />
          <span class="text-[7px] text-zinc-600 font-black uppercase tracking-tighter">{{ res.reset_on }}</span>
        </div>

        <div class="flex flex-wrap gap-1 flex-1">
          <button 
            v-for="n in res.max" 
            :key="n"
            @click="updateResource(i, res.current >= n ? -1 : 1)"
            class="w-3 h-3 rounded-full border transition-all"
            :class="n <= res.current 
              ? 'bg-amber-500 border-amber-400 shadow-[0_0_5px_rgba(245,158,11,0.3)]' 
              : 'bg-zinc-800 border-zinc-700 hover:border-zinc-600'"
          ></button>
        </div>

        <div class="flex items-center gap-2 shrink-0">
          <div class="text-sm font-black text-zinc-100 font-mono tracking-tighter">
            {{ res.current }}<span class="text-zinc-600 text-[10px]">/{{ res.max }}</span>
          </div>
          
          <div class="flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
            <button @click="resetResource(i)" class="p-1 text-zinc-600 hover:text-amber-500"><RotateCcw class="w-3 h-3" /></button>
            <button @click="editingIdx = editingIdx === i ? null : i" class="p-1 text-zinc-600 hover:text-blue-500"><Settings2 class="w-3 h-3" /></button>
            <button @click="removeResource(i)" class="p-1 text-zinc-600 hover:text-red-500"><Trash2 class="w-3 h-3" /></button>
          </div>
        </div>

        <div v-if="editingIdx === i" class="absolute top-full left-0 right-0 z-10 mt-1 bg-zinc-900 border border-zinc-700 rounded-lg p-2 shadow-2xl animate-in fade-in slide-in-from-top-1">
          <div class="flex items-center justify-between gap-4">
            <div class="flex items-center gap-2">
              <span class="text-[8px] text-zinc-500 font-black uppercase">上限:</span>
              <input type="number" v-model="res.max" @change="emit('update', resources)" class="w-10 bg-zinc-950 border border-zinc-800 rounded text-center text-[10px] py-0.5 text-zinc-200 outline-none" />
            </div>
            <div class="flex items-center gap-2">
              <span class="text-[8px] text-zinc-500 font-black uppercase">恢复:</span>
              <select v-model="res.reset_on" @change="emit('update', resources)" class="bg-zinc-950 border border-zinc-800 rounded text-[9px] text-zinc-300 px-1 py-0.5 outline-none">
                <option value="短休">短休</option>
                <option value="长休">长休</option>
              </select>
            </div>
            <button @click="editingIdx = null" class="text-zinc-500 hover:text-white"><Plus class="w-3 h-3 rotate-45" /></button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>