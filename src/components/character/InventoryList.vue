<script setup lang="ts">
import { ref, computed } from 'vue';
import { Plus, LayoutGrid } from 'lucide-vue-next';
import InventoryItemRow from './InventoryItemRow.vue';
import EncumbranceBar from './EncumbranceBar.vue';
import InventorySearch from './InventorySearch.vue';
import type { InventoryItem } from '../../types';

const props = defineProps<{
  inventory: InventoryItem[];
  sheet: any; // 需要 sheet 里的 strength 和 encumbrance_settings
}>();

const emit = defineEmits(['update', 'equip', 'hover-item', 'update:sheet']);

// 状态
const searchQuery = ref('');
const activeCategory = ref('全部');
const categories = ['装备', '消耗品', '杂物'];

// 过滤逻辑
const filteredInventory = computed(() => {
  let list = props.inventory;
  
  // 1. 类别过滤
  if (activeCategory.value !== '全部') {
    list = list.filter(i => i.category === activeCategory.value);
  }
  
  // 2. 搜索过滤
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase();
    list = list.filter(i => 
      i.name.toLowerCase().includes(q) || 
      i.description.toLowerCase().includes(q) ||
      i.item_type.toLowerCase().includes(q)
    );
  }
  
  return list;
});

// 分组逻辑
const groupedInventory = computed(() => {
  if (activeCategory.value !== '全部') {
    return [{ name: activeCategory.value, items: filteredInventory.value }];
  }
  
  // 如果是全部，则按照类别分组显示
  return categories.map(cat => ({
    name: cat,
    items: filteredInventory.value.filter(i => i.category === cat)
  })).filter(group => group.items.length > 0);
});

const addItem = () => {
  const newItem: InventoryItem = {
    name: '新物品',
    quantity: 1,
    weight: 0,
    category: (activeCategory.value === '全部' ? '杂物' : activeCategory.value) as any,
    item_type: '',
    slot_type: '',
    is_equipped: false,
    is_proficient: true,
    description: '',
    rarity: '普通',
    requires_attunement: false,
    is_attuned: false,
    properties: [],
    damage_dice: '',
    damage_type: '',
    attack_bonus: 0,
    damage_bonus: 0,
    ac_bonus: 0,
    strength_req: 0,
    stealth_disadv: false,
    derived_attack_roll: '',
    derived_damage_roll: ''
  };
  emit('update', [...props.inventory, newItem]);
};

const updateItem = () => {
  emit('update', props.inventory);
};

const removeItem = (item: InventoryItem) => {
  const idx = props.inventory.indexOf(item);
  if (idx > -1) {
    const list = [...props.inventory];
    list.splice(idx, 1);
    emit('update', list);
  }
};

const handleSettingsUpdate = (newSettings: any) => {
  emit('update:sheet', { ...props.sheet, encumbrance_settings: newSettings });
};
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- 1. 负重系统 (最上面) -->
    <EncumbranceBar 
      :total-weight="sheet.total_weight"
      :strength="sheet.strength.derived"
      :settings="sheet.encumbrance_settings || { base_mult: 5.0 }"
      @update:settings="handleSettingsUpdate"
    />

    <!-- 2. 搜索与分类 (中间) -->
    <InventorySearch 
      v-model="searchQuery"
      :categories="categories"
      v-model:active-category="activeCategory"
    />

    <!-- 3. 物品列表 (带分组) -->
    <div class="space-y-8 pb-20">
      <div v-for="group in groupedInventory" :key="group.name" class="space-y-3">
        <div class="flex items-center gap-2 px-1">
          <div class="w-1 h-4 bg-amber-500 rounded-full"></div>
          <h3 class="text-[10px] font-black text-zinc-400 uppercase tracking-[0.2em]">{{ group.name }}</h3>
          <span class="text-[9px] font-bold text-zinc-600 bg-zinc-800/50 px-1.5 rounded-full">{{ group.items.length }}</span>
          <div class="flex-1 h-[1px] bg-zinc-800/50 ml-2"></div>
        </div>

        <div class="space-y-2">
          <InventoryItemRow 
            v-for="(item, i) in group.items" 
            :key="item.name + i"
            :item="item"
            @update="updateItem"
            @remove="removeItem(item)"
            @equip="i => emit('equip', i)"
            @hover-item="(i, e) => emit('hover-item', i, e)"
          />
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="filteredInventory.length === 0" class="py-12 flex flex-col items-center justify-center text-zinc-600 bg-zinc-900/20 rounded-2xl border border-dashed border-zinc-800">
        <LayoutGrid class="w-8 h-8 mb-3 opacity-20" />
        <p class="text-xs font-bold uppercase tracking-widest">没有找到相关物品</p>
      </div>

      <button @click="addItem" class="w-full py-4 border-2 border-dashed border-zinc-800 rounded-xl text-zinc-600 hover:text-emerald-500 hover:border-emerald-500/50 hover:bg-emerald-500/5 transition-all flex items-center justify-center gap-2 text-xs font-black uppercase tracking-widest mt-4">
        <Plus class="w-4 h-4" /> 添加{{ activeCategory === '全部' ? '' : activeCategory }}物品
      </button>
    </div>
  </div>
</template>