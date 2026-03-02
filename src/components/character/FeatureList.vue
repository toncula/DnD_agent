<script setup lang="ts">
import { Plus, Trash2 } from 'lucide-vue-next';

const props = defineProps<{ features: any[] }>();
const emit = defineEmits(['update']);

const addItem = () => {
  emit('update', [...props.features, { name: '新特性', source: '职业', description: '' }]);
};

const removeItem = (index: number) => {
  const list = [...props.features];
  list.splice(index, 1);
  emit('update', list);
};
</script>

<template>
  <div class="space-y-4">
    <div v-for="(feat, i) in features" :key="i" class="bg-zinc-900/50 p-4 rounded-lg border border-zinc-700 group">
      <div class="flex justify-between items-start mb-2">
        <input v-model="feat.name" @change="emit('update', features)" class="bg-transparent font-bold text-zinc-100 outline-none focus:text-red-400" />
        <div class="flex items-center gap-3">
          <span class="text-[10px] bg-zinc-700 px-2 py-0.5 rounded text-zinc-400">{{ feat.source }}</span>
          <button @click="removeItem(i)" class="text-zinc-600 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all">
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
      <textarea v-model="feat.description" @change="emit('update', features)" class="w-full bg-transparent text-sm text-zinc-400 resize-none outline-none" rows="2" placeholder="描述特性效果..."></textarea>
    </div>
    <button @click="addItem" class="w-full py-3 border-2 border-dashed border-zinc-700 rounded-lg text-zinc-500 hover:border-red-500/50 hover:text-red-500 transition-all flex items-center justify-center gap-2 text-sm">
      <Plus class="w-4 h-4" /> 添加新特性
    </button>
  </div>
</template>