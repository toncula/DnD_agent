<script setup lang="ts">
import { ref } from 'vue';
import { Star, Package, Sparkles } from 'lucide-vue-next';
import FeatureList from './FeatureList.vue';
import InventoryList from './InventoryList.vue';
import SpellManager from './SpellManager.vue';

const props = defineProps<{
  features: any[];
  inventory: any[];
  spells: any[];
  sheet: any;
}>();

const emit = defineEmits(['update:features', 'update:inventory', 'update:spells', 'equip', 'hover-item', 'update:sheet']);

const activeTab = ref('features');

const handleHover = (item: any, event: MouseEvent) => {
  emit('hover-item', item, event);
};
</script>

<template>
  <div class="mt-8 bg-zinc-800 border border-zinc-700 rounded-xl overflow-hidden shadow-2xl">
    <!-- Tab Headers -->
    <div class="flex border-b border-zinc-700 bg-zinc-900/50">
      <button 
        v-for="tab in [{id:'features', label:'特性', icon:Star, color:'text-red-500'}, {id:'inventory', label:'背包', icon:Package, color:'text-emerald-500'}, {id:'spells', label:'法术', icon:Sparkles, color:'text-blue-500'}]"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="flex-1 py-4 px-6 flex items-center justify-center gap-2 text-sm font-bold uppercase tracking-wider transition-all"
        :class="activeTab === tab.id ? `${tab.color} border-b-2 border-current bg-zinc-800` : 'text-zinc-500 hover:text-zinc-300'"
      >
        <component :is="tab.icon" class="w-4 h-4" /> {{ tab.label }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="p-6 min-h-[400px]">
      <FeatureList 
        v-if="activeTab === 'features'" 
        :features="features" 
        @update="v => emit('update:features', v)" 
      />
      
      <InventoryList 
        v-else-if="activeTab === 'inventory'" 
        :inventory="inventory" 
        @update="v => emit('update:inventory', v)"
        @equip="v => emit('equip', v)"
        @hover-item="handleHover"
      />
      
      <SpellManager 
        v-else-if="activeTab === 'spells'" 
        :spells="spells" 
        :sheet="sheet"
        @update="v => emit('update:spells', v)"
        @update:sheet="v => emit('update:sheet', v)"
        @hover-item="handleHover"
      />
    </div>
  </div>
</template>