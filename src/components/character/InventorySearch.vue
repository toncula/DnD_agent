<script setup lang="ts">
import { Search, X, Filter } from 'lucide-vue-next';
import { ref, watch } from 'vue';

const props = defineProps<{
  modelValue: string;
  categories: string[];
  activeCategory: string;
}>();

const emit = defineEmits(['update:modelValue', 'update:activeCategory']);

const internalQuery = ref(props.modelValue);

watch(internalQuery, (newVal) => {
  emit('update:modelValue', newVal);
});

watch(() => props.modelValue, (newVal) => {
  internalQuery.value = newVal;
});
</script>

<template>
  <div class="flex flex-col gap-4 mb-6">
    <!-- 搜索框 -->
    <div class="relative group">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 group-focus-within:text-blue-400 transition-colors" />
      <input 
        v-model="internalQuery"
        type="text" 
        placeholder="搜索物品名称或描述..."
        class="w-full bg-zinc-900/50 border border-zinc-800 rounded-xl py-2.5 pl-10 pr-10 text-sm text-zinc-200 outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all font-medium"
      />
      <button 
        v-if="internalQuery"
        @click="internalQuery = ''"
        class="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-zinc-800 rounded-lg transition-colors"
      >
        <X class="w-3.5 h-3.5 text-zinc-500" />
      </button>
    </div>

    <!-- 分类标签 -->
    <div class="flex flex-wrap gap-2">
      <button 
        @click="emit('update:activeCategory', '全部')"
        class="px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all border"
        :class="activeCategory === '全部' 
          ? 'bg-blue-600/20 border-blue-500/50 text-blue-400 shadow-lg shadow-blue-900/20' 
          : 'bg-zinc-900/50 border-zinc-800 text-zinc-500 hover:border-zinc-700 hover:text-zinc-300'"
      >
        全部
      </button>
      <button 
        v-for="cat in categories" 
        :key="cat"
        @click="emit('update:activeCategory', cat)"
        class="px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all border"
        :class="activeCategory === cat
          ? 'bg-amber-600/20 border-amber-500/50 text-amber-400 shadow-lg shadow-amber-900/20' 
          : 'bg-zinc-900/50 border-zinc-800 text-zinc-500 hover:border-zinc-700 hover:text-zinc-300'"
      >
        {{ cat }}
      </button>
    </div>
  </div>
</template>