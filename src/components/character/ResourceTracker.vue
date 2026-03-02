<script setup lang="ts">
import { Zap, Plus, Trash2, RotateCcw } from 'lucide-vue-next';

const props = defineProps<{
  resources: any[];
}>();

const emit = defineEmits(['update']);

const updateResource = (index: number, delta: number) => {
  const newList = [...props.resources];
  const res = { ...newList[index] };
  res.current = Math.max(0, Math.min(res.max, res.current + delta));
  newList[index] = res;
  emit('update', newList);
};

const resetResource = (index: number) => {
  const newList = [...props.resources];
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
  <div class="flex flex-wrap gap-4">
    <div 
      v-for="(res, i) in resources" 
      :key="i"
      class="bg-zinc-900/80 border border-zinc-700/50 rounded-2xl p-4 flex flex-col min-w-[180px] shadow-lg group relative overflow-hidden"
    >
      <div class="flex justify-between items-start mb-3">
        <div class="flex flex-col">
          <input 
            v-model="res.name" 
            class="bg-transparent font-black text-xs text-zinc-100 uppercase tracking-widest outline-none focus:text-amber-400"
            @change="emit('update', resources)"
          />
          <span class="text-[8px] text-zinc-500 font-bold uppercase mt-0.5">{{ res.reset_on }}恢复</span>
        </div>
        <button @click="removeResource(i)" class="text-zinc-700 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all">
          <Trash2 class="w-3 h-3" />
        </button>
      </div>

      <div class="flex items-center gap-3">
        <!-- 资源气泡 -->
        <div class="flex flex-wrap gap-1.5 flex-1">
          <button 
            v-for="n in res.max" 
            :key="n"
            @click="updateResource(i, res.current >= n ? -1 : 1)"
            class="w-4 h-4 rounded-full border transition-all"
            :class="n <= res.current 
              ? 'bg-amber-500 border-amber-400 shadow-[0_0_8px_rgba(245,158,11,0.4)]' 
              : 'bg-zinc-800 border-zinc-700 hover:border-zinc-500'"
          ></button>
        </div>

        <div class="flex items-center gap-2">
           <div class="text-xl font-black text-zinc-100 font-mono">{{ res.current }}<span class="text-zinc-600 text-xs ml-0.5">/{{ res.max }}</span></div>
           <button @click="resetResource(i)" class="p-1.5 text-zinc-600 hover:text-amber-500 transition-colors">
             <RotateCcw class="w-3.5 h-3.5" />
           </button>
        </div>
      </div>

      <!-- 快速调整最大值 (悬浮可见) -->
      <div class="mt-3 pt-3 border-t border-zinc-800 flex items-center justify-between opacity-0 group-hover:opacity-100 transition-all">
        <span class="text-[8px] text-zinc-600 font-black uppercase">上限调整</span>
        <div class="flex items-center gap-2">
          <input 
            type="number" 
            v-model="res.max" 
            @change="emit('update', resources)"
            class="w-10 bg-zinc-950 border border-zinc-800 rounded text-center text-[10px] py-0.5 text-zinc-400 outline-none"
          />
          <select v-model="res.reset_on" @change="emit('update', resources)" class="bg-zinc-950 border border-zinc-800 rounded text-[8px] text-zinc-500 outline-none">
            <option value="短休">短休</option>
            <option value="长休">长休</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 添加按钮 -->
    <button 
      @click="addGenericResource"
      class="border-2 border-dashed border-zinc-800 rounded-2xl p-4 flex flex-col items-center justify-center min-w-[120px] text-zinc-700 hover:border-zinc-600 hover:text-zinc-500 transition-all gap-2"
    >
      <Plus class="w-6 h-6" />
      <span class="text-[10px] font-black uppercase tracking-widest">添加资源</span>
    </button>
  </div>
</template>