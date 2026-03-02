<script setup lang="ts">
import { Plus, Trash2 } from 'lucide-vue-next';

const props = defineProps<{
  inventory: any[];
}>();

const emit = defineEmits(['update', 'equip', 'hover-item']);

const addItem = () => {
  emit('update', [...props.inventory, { name: '新物品', quantity: 1, weight: 0, description: '', category: '杂物' }]);
};

const removeItem = (index: number) => {
  const list = [...props.inventory];
  list.splice(index, 1);
  emit('update', list);
};

const handleHover = (item: any, event: MouseEvent) => {
  emit('hover-item', item, event);
};
</script>

<template>
  <div class="space-y-2">
    <div 
      v-for="(item, i) in inventory" 
      :key="i" 
      class="flex items-center gap-4 bg-zinc-900/50 p-3 rounded-lg border border-zinc-700 group cursor-help"
      @mouseenter="e => handleHover(item, e)"
      @mouseleave="handleHover(null, null as any)"
    >
      <input type="number" v-model="item.quantity" @change="emit('update', inventory)" class="w-12 bg-zinc-800 rounded px-2 py-1 text-center text-sm" />
      
      <div class="flex-1 flex flex-col gap-1 min-w-0">
        <div class="flex items-center gap-2">
          <div v-if="item.is_equipped" class="bg-blue-600 text-white text-[8px] font-black px-1 rounded shrink-0">E</div>
          <input v-model="item.name" @change="emit('update', inventory)" class="bg-transparent font-medium text-zinc-200 outline-none flex-1 truncate" />
          
          <select v-model="item.category" @change="emit('update', inventory)" class="bg-zinc-800 text-[10px] text-zinc-400 border-none rounded px-1.5 py-0.5 outline-none">
            <option value="装备">装备</option>
            <option value="消耗品">消耗品</option>
            <option value="杂物">杂物</option>
          </select>

          <select v-if="item.category === '装备'" v-model="item.item_type" @change="emit('update', inventory)" class="bg-zinc-800 text-[10px] text-amber-500 border-none rounded px-1.5 py-0.5 outline-none">
            <option value="武器">武器</option>
            <option value="护甲">护甲</option>
            <option value="盾牌">盾牌</option>
            <option value="饰品">饰品</option>
          </select>

          <select v-if="item.category === '装备'" v-model="item.slot_type" @change="emit('update', inventory)" class="bg-zinc-800 text-[10px] text-blue-400 border-none rounded px-1.5 py-0.5 outline-none">
            <option value="头部">头部</option>
            <option value="躯干">躯干</option>
            <option value="主手">主手</option>
            <option value="副手">副手</option>
            <option value="双手">双手</option>
            <option value="足部">足部</option>
            <option value="戒指">戒指</option>
            <option value="项链">项链</option>
          </select>
        </div>
      </div>
      
      <button 
        v-if="item.category === '装备' || item.item_type === '盾牌'"
        @click="emit('equip', item)"
        class="px-3 py-1 text-[10px] font-bold rounded border transition-all shrink-0"
        :class="item.is_equipped ? 'bg-amber-600/20 text-amber-400 border-amber-500/50 hover:bg-amber-600' : 'bg-blue-600/20 text-blue-400 border-blue-500/50 hover:bg-blue-600'"
      >
        {{ item.is_equipped ? '卸下' : '装备' }}
      </button>

      <div class="flex items-center gap-2">
        <input type="number" v-model="item.weight" @change="emit('update', inventory)" step="0.1" class="w-14 bg-zinc-800 rounded px-2 py-1 text-center text-xs" />
        <span class="text-[10px] text-zinc-500">磅</span>
      </div>

      <button @click="removeItem(i)" class="text-zinc-600 hover:text-red-500">
        <Trash2 class="w-4 h-4" />
      </button>
    </div>

    <button @click="addItem" class="w-full py-3 border-2 border-dashed border-zinc-700 rounded-lg text-zinc-500 hover:text-emerald-500 transition-all flex items-center justify-center gap-2 text-sm mt-4">
      <Plus class="w-4 h-4" /> 添加物品
    </button>
  </div>
</template>