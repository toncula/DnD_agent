<script setup lang="ts">
import { ChevronUp, ChevronDown, Trash2, Award } from 'lucide-vue-next';

const props = defineProps<{
  cls: any;
  isFirst: boolean;
}>();

const emit = defineEmits(['update', 'remove']);

const updateLevel = (delta: number) => {
  const newLevel = Math.max(1, props.cls.level + delta);
  emit('update', { ...props.cls, level: newLevel });
};
</script>

<template>
  <div class="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 flex items-center justify-between group transition-all hover:border-zinc-700">
    <div class="flex items-center gap-4 flex-1">
      <!-- 职业图标/首字母 -->
      <div class="w-10 h-10 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center font-black text-zinc-400 group-hover:text-amber-500 transition-colors">
        {{ cls.name[0] }}
      </div>

      <div class="flex flex-col flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <span class="font-bold text-zinc-100">{{ cls.name }}</span>
          <Award v-if="cls.is_primary" class="w-3 h-3 text-amber-500" />
          <span v-if="cls.is_primary" class="text-[8px] font-black text-amber-600 uppercase tracking-widest">起始职业</span>
        </div>
        <!-- 子职业输入 -->
        <input 
          v-model="cls.subclass" 
          placeholder="点击输入子职业..."
          @change="emit('update', { ...cls })"
          class="bg-transparent text-[10px] text-zinc-500 outline-none focus:text-zinc-300 w-full"
        />
      </div>
    </div>

    <!-- 等级控制 -->
    <div class="flex items-center gap-4 ml-4">
      <div class="flex flex-col items-center">
        <span class="text-[8px] font-black text-zinc-600 uppercase mb-1">等级</span>
        <div class="flex items-center bg-zinc-950 border border-zinc-800 rounded-lg px-2 py-1">
          <button @click="updateLevel(-1)" class="p-1 text-zinc-600 hover:text-red-500"><ChevronDown class="w-3 h-3" /></button>
          <span class="w-6 text-center font-mono font-bold text-zinc-200">{{ cls.level }}</span>
          <button @click="updateLevel(1)" class="p-1 text-zinc-600 hover:text-emerald-500"><ChevronUp class="w-3 h-3" /></button>
        </div>
      </div>

      <!-- 删除按钮 (非起始职业可见) -->
      <button 
        v-if="!cls.is_primary"
        @click="emit('remove')"
        class="p-2 text-zinc-700 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
      >
        <Trash2 class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>