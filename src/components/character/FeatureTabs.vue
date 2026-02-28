<script setup lang="ts">
import { ref } from 'vue';
import { Star, Package, Sparkles, Plus, Trash2 } from 'lucide-vue-next';

const props = defineProps<{
  features: any[];
  inventory: any[];
  spells: any[];
}>();

const emit = defineEmits(['update:features', 'update:inventory', 'update:spells']);

const activeTab = ref('features');

const addItem = (type: string) => {
  if (type === 'features') {
    emit('update:features', [...props.features, { name: '新特性', source: '职业', description: '' }]);
  } else if (type === 'inventory') {
    emit('update:inventory', [...props.inventory, { name: '新物品', quantity: 1, weight: 0, description: '' }]);
  } else if (type === 'spells') {
    emit('update:spells', [...props.spells, { name: '新法术', level: 0, casting_time: '1动作', description: '' }]);
  }
};

const removeItem = (type: string, index: number) => {
  if (type === 'features') {
    const list = [...props.features];
    list.splice(index, 1);
    emit('update:features', list);
  } else if (type === 'inventory') {
    const list = [...props.inventory];
    list.splice(index, 1);
    emit('update:inventory', list);
  } else if (type === 'spells') {
    const list = [...props.spells];
    list.splice(index, 1);
    emit('update:spells', list);
  }
};
</script>

<template>
  <div class="mt-8 bg-zinc-800 border border-zinc-700 rounded-xl overflow-hidden shadow-2xl">
    <!-- Tab Headers -->
    <div class="flex border-b border-zinc-700 bg-zinc-900/50">
      <button 
        @click="activeTab = 'features'"
        class="flex-1 py-4 px-6 flex items-center justify-center gap-2 text-sm font-bold uppercase tracking-wider transition-all"
        :class="activeTab === 'features' ? 'text-red-500 border-b-2 border-red-500 bg-zinc-800' : 'text-zinc-500 hover:text-zinc-300'"
      >
        <Star class="w-4 h-4" /> 特性
      </button>
      <button 
        @click="activeTab = 'inventory'"
        class="flex-1 py-4 px-6 flex items-center justify-center gap-2 text-sm font-bold uppercase tracking-wider transition-all"
        :class="activeTab === 'inventory' ? 'text-emerald-500 border-b-2 border-emerald-500 bg-zinc-800' : 'text-zinc-500 hover:text-zinc-300'"
      >
        <Package class="w-4 h-4" /> 背包
      </button>
      <button 
        @click="activeTab = 'spells'"
        class="flex-1 py-4 px-6 flex items-center justify-center gap-2 text-sm font-bold uppercase tracking-wider transition-all"
        :class="activeTab === 'spells' ? 'text-blue-500 border-b-2 border-blue-500 bg-zinc-800' : 'text-zinc-500 hover:text-zinc-300'"
      >
        <Sparkles class="w-4 h-4" /> 法术
      </button>
    </div>

    <!-- Tab Content -->
    <div class="p-6 min-h-[400px]">
      <!-- Features -->
      <div v-if="activeTab === 'features'" class="space-y-4">
        <div v-for="(feat, i) in features" :key="i" class="bg-zinc-900/50 p-4 rounded-lg border border-zinc-700 group">
          <div class="flex justify-between items-start mb-2">
            <input v-model="feat.name" class="bg-transparent font-bold text-zinc-100 outline-none focus:text-red-400" />
            <div class="flex items-center gap-3">
              <span class="text-[10px] bg-zinc-700 px-2 py-0.5 rounded text-zinc-400">{{ feat.source }}</span>
              <button @click="removeItem('features', i)" class="text-zinc-600 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all">
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
          <textarea v-model="feat.description" class="w-full bg-transparent text-sm text-zinc-400 resize-none outline-none" rows="2" placeholder="描述特性效果..."></textarea>
        </div>
        <button @click="addItem('features')" class="w-full py-3 border-2 border-dashed border-zinc-700 rounded-lg text-zinc-500 hover:border-red-500/50 hover:text-red-500 transition-all flex items-center justify-center gap-2 text-sm">
          <Plus class="w-4 h-4" /> 添加新特性
        </button>
      </div>

      <!-- Inventory -->
      <div v-if="activeTab === 'inventory'" class="space-y-2">
        <div v-for="(item, i) in inventory" :key="i" class="flex items-center gap-4 bg-zinc-900/50 p-3 rounded-lg border border-zinc-700">
          <input v-model="item.quantity" type="number" class="w-12 bg-zinc-800 rounded px-2 py-1 text-center text-sm" />
          <input v-model="item.name" class="flex-1 bg-transparent font-medium text-zinc-200 outline-none" />
          <div class="flex items-center gap-2">
            <input v-model="item.weight" type="number" step="0.1" class="w-16 bg-zinc-800 rounded px-2 py-1 text-center text-xs" />
            <span class="text-[10px] text-zinc-500">磅</span>
          </div>
          <button @click="removeItem('inventory', i)" class="text-zinc-600 hover:text-red-500">
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
        <button @click="addItem('inventory')" class="w-full py-3 border-2 border-dashed border-zinc-700 rounded-lg text-zinc-500 hover:text-emerald-500 transition-all flex items-center justify-center gap-2 text-sm mt-4">
          <Plus class="w-4 h-4" /> 添加物品
        </button>
      </div>

      <!-- Spells -->
      <div v-if="activeTab === 'spells'" class="space-y-4">
        <div v-for="(spell, i) in spells" :key="i" class="bg-zinc-900/50 p-4 rounded-lg border border-zinc-700">
          <div class="flex justify-between items-center mb-2">
            <div class="flex items-center gap-3">
              <span class="w-6 h-6 rounded bg-blue-900/50 flex items-center justify-center text-xs font-bold text-blue-400">{{ spell.level }}</span>
              <input v-model="spell.name" class="bg-transparent font-bold text-zinc-100 outline-none" />
            </div>
            <button @click="removeItem('spells', i)" class="text-zinc-600 hover:text-red-500">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
          <div class="text-[10px] text-zinc-500 uppercase tracking-widest mb-2">{{ spell.casting_time }}</div>
          <textarea v-model="spell.description" class="w-full bg-transparent text-xs text-zinc-500 resize-none outline-none" rows="2"></textarea>
        </div>
        <button @click="addItem('spells')" class="w-full py-3 border-2 border-dashed border-zinc-700 rounded-lg text-zinc-500 hover:text-blue-500 transition-all flex items-center justify-center gap-2 text-sm">
          <Plus class="w-4 h-4" /> 添加新法术
        </button>
      </div>
    </div>
  </div>
</template>
