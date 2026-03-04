<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import CombatStats from '../CombatStats.vue';
import StatGrid from '../StatGrid.vue';
import SkillsSaves from '../SkillsSaves.vue';
import FeatureTabs from '../FeatureTabs.vue';
import EquipmentSlots from '../EquipmentSlots.vue';
import ItemTooltip from '../ItemTooltip.vue';
import ResourceTracker from '../ResourceTracker.vue';
import DefensesBlock from '../DefensesBlock.vue';
import { ref, watch } from 'vue';

const props = defineProps<{ sheet: any }>();
const emit = defineEmits(['update']);

// Tooltip 状态
const hoveredItem = ref<any>(null);
const mouseX = ref(0);
const mouseY = ref(0);

const handleHover = (item: any, event?: MouseEvent) => {
  if (item && event) {
    hoveredItem.value = item;
    mouseX.value = event.clientX;
    mouseY.value = event.clientY;
  } else {
    hoveredItem.value = null;
  }
};

const updateSheet = (key: string, val: any) => {
  emit('update', { [key]: val });
};

const assignMultiple = (newData: any) => {
  // 确保 newData 是一个新的对象引用，触发 CharacterSheet 的 handlePageUpdate
  emit('update', { ...newData });
};

// 后端负责所有 AC 和攻击派生计算，前端仅负责 UI 交互和简单的互斥逻辑
const handleEquip = (item: any) => {
  const newInventory = [...props.sheet.inventory];
  const targetItem = newInventory.find(i => i.name === item.name);
  if (!targetItem) return;

  const isNowEquipped = !targetItem.is_equipped;
  
  if (isNowEquipped) {
    // 互斥逻辑
    if (targetItem.item_type === '护甲' || targetItem.slot_type === '躯干') {
      // 卸下其他护甲
      newInventory.forEach(i => {
        if ((i.item_type === '护甲' || i.slot_type === '躯干') && i.is_equipped) i.is_equipped = false;
      });
    }
    
    if (targetItem.slot_type === '双手') {
      // 卸下副手物品（盾牌或副手武器）
      newInventory.forEach(i => {
        if (i.slot_type === '副手' && i.is_equipped) i.is_equipped = false;
        if (i.item_type === '盾牌' && i.is_equipped) i.is_equipped = false;
        if (i.slot_type === '双手' && i.is_equipped) i.is_equipped = false;
        if (i.slot_type === '主手' && i.is_equipped) i.is_equipped = false;
      });
    }

    if (targetItem.slot_type === '主手') {
      newInventory.forEach(i => {
        if ((i.slot_type === '主手' || i.slot_type === '双手') && i.is_equipped) i.is_equipped = false;
      });
    }

    if (targetItem.slot_type === '副手' || targetItem.item_type === '盾牌') {
      newInventory.forEach(i => {
        if ((i.slot_type === '副手' || i.item_type === '盾牌' || i.slot_type === '双手') && i.is_equipped) i.is_equipped = false;
      });
    }
    
    // 槽位互斥
    if (targetItem.slot_type && targetItem.slot_type !== '') {
       newInventory.forEach(i => {
         if (i.slot_type === targetItem.slot_type && i.is_equipped) i.is_equipped = false;
       });
    }
  }

  targetItem.is_equipped = isNowEquipped;
  emit('update', { ...props.sheet, inventory: newInventory });
};
</script>

<template>
  <div class="space-y-6 relative">
    <!-- 悬浮 Tooltip -->
    <ItemTooltip v-if="hoveredItem" :item="hoveredItem" :x="mouseX" :y="mouseY" />

    <!-- 核心战斗顶部状态栏 -->
    <CombatStats :combat="sheet.combat" :level="sheet.prog.level" :sheet="sheet" @update:combat="v => updateSheet('combat', v)" @update:sheet="assignMultiple" />

    <!-- 战术信息区：职业资源与防御特性 (并排布局) -->
    <div class="grid grid-cols-1 lg:grid-cols-[1fr_1fr] gap-6 items-stretch">
      <div class="h-full">
        <ResourceTracker 
          v-if="sheet.combat.class_resources"
          :resources="sheet.combat.class_resources" 
          @update="v => updateSheet('combat', { ...sheet.combat, class_resources: v })"
        />
      </div>
      <div class="h-full">
        <DefensesBlock 
          :defenses="sheet.combat.defenses" 
          @update="v => updateSheet('combat', { ...sheet.combat, defenses: v })"
        />
      </div>
    </div>

    <!-- 中间三栏布局 -->
    <div class="grid grid-cols-1 lg:grid-cols-[200px_1fr_240px] gap-8 items-start">
      <div class="w-[200px] shrink-0"><StatGrid :sheet="sheet" @update="assignMultiple" /></div>
      <div class="min-w-0"><EquipmentSlots :sheet="sheet" @update="assignMultiple" @hover-item="handleHover" /></div>
      <div class="w-[240px] shrink-0"><SkillsSaves :sheet="sheet" @update="assignMultiple" /></div>
    </div>
    
    <FeatureTabs :sheet="sheet" :features="sheet.features" :inventory="sheet.inventory" :spells="sheet.spells" @update:features="v => updateSheet('features', v)" @update:inventory="v => updateSheet('inventory', v)" @update:spells="v => updateSheet('spells', v)" @update:sheet="assignMultiple" @equip="handleEquip" @hover-item="handleHover" />
  </div>
</template>