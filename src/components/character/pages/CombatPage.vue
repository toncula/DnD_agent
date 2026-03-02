<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import CombatStats from '../CombatStats.vue';
import StatGrid from '../StatGrid.vue';
import SkillsSaves from '../SkillsSaves.vue';
import FeatureTabs from '../FeatureTabs.vue';
import EquipmentSlots from '../EquipmentSlots.vue';
import ItemTooltip from '../ItemTooltip.vue';
import ResourceTracker from '../ResourceTracker.vue';
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
  emit('update', newData);
};

// 关键功能：监听背包变化，同步到纸娃娃
watch(() => props.sheet.inventory, (newInv) => {
  if (!newInv) return;
  const newSheet = JSON.parse(JSON.stringify(props.sheet));
  let changed = false;

  // 1. 同步护甲 AC
  const equippedArmor = newInv.find((i: any) => i.category === '装备' && i.item_type === '护甲' && i.is_equipped);
  const targetAC = equippedArmor ? parseInt(equippedArmor.description?.match(/\d+/)?.[0] || '11') : 0;
  if (newSheet.equipped_armor_base_ac !== targetAC) {
    newSheet.equipped_armor_base_ac = targetAC;
    changed = true;
  }

  // 2. 同步武器数据
  const mainWeapon = newInv.find((i: any) => i.is_equipped && (i.slot_type === '主手' || i.slot_type === '双手'));
  const offWeapon = newInv.find((i: any) => i.is_equipped && i.slot_type === '副手' && i.item_type === '武器');

  const syncWeapon = (invItem: any, index: number) => {
    // 处理双手占位
    if (index === 1 && mainWeapon?.slot_type === '双手') {
      const dmg = mainWeapon.description?.match(/\d+d\d+/)?.[0] || '1d4';
      if (!newSheet.weapons[1] || !newSheet.weapons[1].is_2h_occupied || newSheet.weapons[1].name !== mainWeapon.name) {
        newSheet.weapons[1] = {
          name: mainWeapon.name,
          damage_dice: dmg,
          is_2h_occupied: true, 
          is_proficient: true
        };
        return true;
      }
      return false;
    }

    if (!invItem) {
      if (newSheet.weapons[index] && newSheet.weapons[index].name !== '空手') {
        newSheet.weapons[index] = { name: '空手', damage_dice: '1d4' };
        return true;
      }
      return false;
    }
    
    const dmg = invItem.description?.match(/\d+d\d+/)?.[0] || '1d4';
    const currentW = newSheet.weapons[index];
    
    if (!currentW || currentW.name !== invItem.name || currentW.damage_dice !== dmg) {
      newSheet.weapons[index] = {
        name: invItem.name,
        damage_dice: dmg,
        description: invItem.description,
        weight: invItem.weight,
        slot_type: invItem.slot_type,
        is_proficient: true
      };
      return true;
    }
    return false;
  };

  const c1 = syncWeapon(mainWeapon, 0);
  const c2 = syncWeapon(offWeapon, 1);
  if (c1 || c2) changed = true;

  // 3. 同步盾牌状态
  const equippedShield = newInv.find((i: any) => i.category === '装备' && i.item_type === '盾牌' && i.is_equipped);
  const hasShield = !!equippedShield && mainWeapon?.slot_type !== '双手'; 
  if (newSheet.has_shield !== hasShield) {
    newSheet.has_shield = hasShield;
    changed = true;
  }

  if (changed) {
    emit('update', newSheet);
  }
}, { deep: true });

const handleEquip = (item: any) => {
  const newSheet = JSON.parse(JSON.stringify(props.sheet));
  
  // 1. 在背包中寻找该物品并切换状态
  const invItem = newSheet.inventory.find((i: any) => i.name === item.name);
  if (!invItem) return;

  // 如果已经装备，则卸下
  if (invItem.is_equipped) {
    invItem.is_equipped = false;
    // 重置相关数值
    if (invItem.item_type === '护甲' || invItem.slot_type === '躯干') newSheet.equipped_armor_base_ac = 0;
    else if (invItem.item_type === '盾牌') newSheet.has_shield = false;
    else if (invItem.slot_type === '主手' || invItem.slot_type === '双手') {
       newSheet.weapons[0] = { name: '空手', damage_dice: '1d4' };
       if (invItem.slot_type === '双手') newSheet.weapons[1] = { name: '空手', damage_dice: '1d4' };
    }
    else if (invItem.slot_type === '副手') {
       if (newSheet.weapons[1]) newSheet.weapons[1] = { name: '空手', damage_dice: '1d4' };
    }
    emit('update', newSheet);
    return;
  }

  // 2. 正常装备逻辑
  const slot = item.slot_type;
  const itemType = item.item_type;
  const itemName = item.name.toLowerCase();
  
  // 同类排他逻辑
  newSheet.inventory.forEach((i: any) => {
    if (i.slot_type === slot && slot !== '' && i.is_equipped) i.is_equipped = false;
    if (i.item_type === itemType && itemType === '盾牌' && i.is_equipped) i.is_equipped = false;
    if (slot === '双手' && i.slot_type === '副手' && i.is_equipped) i.is_equipped = false;
  });
  invItem.is_equipped = true;

  // 护甲逻辑
  if (itemType === '护甲' || slot === '躯干') {
    const match = item.description?.match(/\d+/);
    newSheet.equipped_armor_base_ac = match ? parseInt(match[0]) : 11;
  } 
  // 盾牌逻辑
  else if (itemType === '盾牌') {
    newSheet.has_shield = true;
    if (newSheet.weapons.length > 1) {
      newSheet.weapons[1] = { name: '空手', damage_dice: '1d4' };
      newSheet.inventory.forEach((i: any) => {
        if (i.slot_type === '副手' && i.item_type === '武器' && i.is_equipped) i.is_equipped = false;
      });
    }
  } 
  // 武器逻辑
  else if (itemType === '武器' || slot === '主手' || slot === '副手' || slot === '双手') {
    const damageMatch = item.description?.match(/\d+d\d+/);
    const newWeapon = {
      name: item.name,
      damage_dice: damageMatch ? damageMatch[0] : '1d4',
      is_finesse: item.description?.includes('灵巧') || itemName.includes('匕首') || itemName.includes('弓'),
      is_proficient: true,
      category: '装备',
      item_type: '武器',
      slot_type: slot,
      description: item.description,
      weight: item.weight
    };
    
    if (slot === '双手') {
      newSheet.has_shield = false;
      newSheet.weapons[0] = newWeapon;
      newSheet.weapons[1] = { ...newWeapon, is_2h_occupied: true }; 
    } 
    else if (slot === '主手') {
      if (newSheet.weapons.length === 0) newSheet.weapons.push(newWeapon);
      else newSheet.weapons[0] = newWeapon;
    } 
    else if (slot === '副手') {
      newSheet.has_shield = false; 
      if (newSheet.weapons.length < 2) {
        newSheet.weapons = [newSheet.weapons[0] || { name: '空手', damage_dice: '1d4' }, newWeapon];
      } else {
        newSheet.weapons[1] = newWeapon;
      }
    }
  }
  
  emit('update', newSheet);
};
</script>

<template>
  <div class="space-y-6 relative">
    <!-- 悬浮 Tooltip -->
    <ItemTooltip 
      v-if="hoveredItem" 
      :item="hoveredItem" 
      :x="mouseX" 
      :y="mouseY" 
    />

    <!-- 核心战斗顶部状态栏 -->
    <CombatStats 
      :combat="sheet.combat" 
      :level="sheet.prog.level"
      :sheet="sheet"
      @update:combat="v => updateSheet('combat', v)" 
      @update:sheet="assignMultiple"
    />

    <!-- 职业特殊资源追踪 (核心新块) -->
    <ResourceTracker 
      v-if="sheet.combat.class_resources"
      :resources="sheet.combat.class_resources" 
      @update="v => updateSheet('combat', { ...sheet.combat, class_resources: v })"
    />

    <!-- 中间三栏布局 -->
    <div class="grid grid-cols-1 lg:grid-cols-[200px_1fr_240px] gap-8 items-start">
      <!-- 左：属性 (固定宽度) -->
      <div class="w-[200px] shrink-0">
        <StatGrid 
          :sheet="sheet" 
          @update="assignMultiple" 
        />
      </div>
      
      <!-- 中：装备纸娃娃 (自适应) -->
      <div class="min-w-0">
        <EquipmentSlots 
          :sheet="sheet" 
          @update="assignMultiple" 
          @hover-item="handleHover"
        />
      </div>

      <!-- 右：技能与豁免 (固定宽度) -->
      <div class="w-[240px] shrink-0">
        <SkillsSaves 
          :sheet="sheet" 
          @update="assignMultiple" 
        />
      </div>
    </div>
    
    <!-- 底部：背包与特性 -->
    <FeatureTabs 
      :sheet="sheet"
      :features="sheet.features" 
      :inventory="sheet.inventory" 
      :spells="sheet.spells"
      @update:features="v => updateSheet('features', v)"
      @update:inventory="v => updateSheet('inventory', v)"
      @update:spells="v => updateSheet('spells', v)" 
      @update:sheet="assignMultiple"
      @equip="handleEquip"
      @hover-item="handleHover"
    />
  </div>
</template>