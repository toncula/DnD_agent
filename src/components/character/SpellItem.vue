<script setup lang="ts">
import { ref } from 'vue';
import { Trash2, Clock, MapPin, ChevronDown, ChevronRight } from 'lucide-vue-next';

const props = defineProps<{
  spell: any;
  isEditing: boolean;
}>();

const emit = defineEmits(['update', 'remove', 'toggleEdit']);

const updateField = () => {
  emit('update');
};
</script>

<template>
  <div class="flex flex-col bg-zinc-900/20 rounded-xl border border-zinc-800/50 overflow-hidden">
    <!-- 概览栏 -->
    <div @click="emit('toggleEdit')" class="flex items-center gap-4 p-2 pr-4 cursor-pointer hover:bg-zinc-800/30 group">
      <input 
        v-model="spell.name" 
        @click.stop 
        @change="updateField" 
        class="bg-transparent text-sm font-bold text-zinc-200 outline-none focus:text-blue-400 min-w-[180px]" 
      />
      <span class="text-[9px] font-black text-zinc-600 uppercase px-2 py-0.5 bg-zinc-950 rounded border border-zinc-800">{{ spell.school }}</span>
      <div class="flex-1 flex items-center gap-4 text-[10px] text-zinc-500 overflow-hidden">
        <span class="flex items-center gap-1 shrink-0"><Clock class="w-3 h-3" /> {{ spell.casting_time }}</span>
        <span class="flex items-center gap-1 shrink-0"><MapPin class="w-3 h-3" /> {{ spell.range }}</span>
        <span class="truncate italic opacity-60">{{ spell.description }}</span>
      </div>
      <button @click.stop="emit('remove')" class="p-1 text-zinc-800 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity">
        <Trash2 class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- 编辑面板 -->
    <div v-if="isEditing" class="p-4 bg-zinc-950/30 border-t border-zinc-800 grid grid-cols-1 md:grid-cols-3 gap-4 animate-in slide-in-from-top-1">
      <div class="flex flex-col gap-1">
        <label class="text-[8px] font-black text-zinc-600 uppercase">法术环阶</label>
        <select v-model="spell.level" @change="updateField" class="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 outline-none">
          <option :value="0">戏法 (Cantrip)</option>
          <option v-for="lv in 9" :key="lv" :value="lv">{{ lv }} 环</option>
        </select>
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-[8px] font-black text-zinc-600 uppercase">法术系别</label>
        <select v-model="spell.school" @change="updateField" class="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 outline-none">
          <option v-for="s in ['防护系', '咒法系', '预言系', '惑控系', '塑能系', '幻术系', '死灵系', '变化系']" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-[8px] font-black text-zinc-600 uppercase">施法时间</label>
        <input v-model="spell.casting_time" @change="updateField" class="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 outline-none" />
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-[8px] font-black text-zinc-600 uppercase">施法距离</label>
        <input v-model="spell.range" @change="updateField" class="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 outline-none" />
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-[8px] font-black text-zinc-600 uppercase">法术成分</label>
        <input v-model="spell.components" @change="updateField" class="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 outline-none" />
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-[8px] font-black text-zinc-600 uppercase">持续时间</label>
        <input v-model="spell.duration" @change="updateField" class="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 outline-none" />
      </div>
      <div class="flex flex-col gap-1 md:col-span-3">
        <label class="text-[8px] font-black text-zinc-600 uppercase">材料描述</label>
        <input v-model="spell.materials" @change="updateField" class="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 outline-none" />
      </div>
      <div class="flex flex-col gap-1 md:col-span-3">
        <label class="text-[8px] font-black text-zinc-600 uppercase">法术说明</label>
        <textarea v-model="spell.description" @change="updateField" rows="4" class="bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-xs text-zinc-400 outline-none leading-relaxed resize-none"></textarea>
      </div>
    </div>
  </div>
</template>
