<script setup lang="ts">
import { Shield, Sword, Shirt, HardHat, Footprints, Hand, Sparkle, UserCircle } from 'lucide-vue-next';
import EquipmentSlotItem from './EquipmentSlotItem.vue';

const props = defineProps<{
  sheet: any;
}>();

const emit = defineEmits(['update', 'hover-item']);

const handleMouseEnter = (slotId: string, event: MouseEvent) => {
  let item = null;
  if (slotId === 'body' && props.sheet.combat.armor_class.base > 0) {
    item = { 
      name: '当前护甲', 
      category: '装备', 
      slot_type: '躯干', 
      description: `基础 AC: ${props.sheet.combat.armor_class.base}`,
      weight: 10
    };
  } else if (slotId === 'mainHand' && props.sheet.weapons[0] && props.sheet.weapons[0].name !== '空手') {
    item = props.sheet.weapons[0];
  } else if (slotId === 'offHand') {
    if (props.sheet.has_shield) {
      item = { name: '盾牌', category: '装备', slot_type: '副手', description: '提供 +2 AC', weight: 6 };
    } else if (props.sheet.weapons[1] && props.sheet.weapons[1].name !== '空手') {
      item = props.sheet.weapons[1];
    }
  }
  
  if (item) {
    emit('hover-item', item, event);
  }
};

const handleMouseLeave = () => {
  emit('hover-item', null);
};

const unequip = (slotId: string) => {
  const newSheet = JSON.parse(JSON.stringify(props.sheet));
  const clearInventoryFlag = (slot: string) => {
    newSheet.inventory.forEach((i: any) => {
      if (i.slot_type === slot && i.is_equipped) {
        i.is_equipped = false;
      }
    });
  };

  if (slotId === 'body') {
    newSheet.combat.armor_class.base = 10;
    clearInventoryFlag('躯干');
  } else if (slotId === 'offHand') {
    if (props.sheet.weapons[1]?.is_2h_occupied) {
      clearInventoryFlag('双手');
      newSheet.weapons[0] = { name: '空手', damage_dice: '1d4' };
      newSheet.weapons[1] = { name: '空手', damage_dice: '1d4' };
    } else {
      newSheet.has_shield = false;
      clearInventoryFlag('副手');
      if (newSheet.weapons.length > 1) {
        newSheet.weapons[1] = { name: '空手', damage_dice: '1d4' };
      }
    }
  } else if (slotId === 'mainHand') {
    if (props.sheet.weapons[0]?.slot_type === '双手') {
      clearInventoryFlag('双手');
      newSheet.weapons[1] = { name: '空手', damage_dice: '1d4' };
    } else {
      clearInventoryFlag('主手');
    }
    if (newSheet.weapons.length > 0) {
      newSheet.weapons[0] = { name: '空手', damage_dice: '1d4' };
    }
  }
  emit('update', newSheet);
};
</script>

<template>
  <div class="bg-zinc-900/80 border border-zinc-700/50 rounded-2xl p-6 shadow-2xl relative overflow-hidden group">
    <div class="absolute inset-0 opacity-5 pointer-events-none flex items-center justify-center">
      <UserCircle class="w-64 h-64 text-white" />
    </div>

    <h3 class="text-xs font-black text-zinc-500 uppercase tracking-widest mb-8 text-center">装备槽位</h3>

    <div class="relative flex justify-center items-center min-h-[420px]">
      <div class="flex gap-10 items-center z-10">
        <div class="flex flex-col gap-6">
          <EquipmentSlotItem label="头部" :icon="HardHat" />
          <EquipmentSlotItem label="披风" :icon="Sparkle" />
          <EquipmentSlotItem label="项链" :icon="Sparkle" />
          <EquipmentSlotItem label="足部" :icon="Footprints" />
        </div>

        <div class="flex flex-col items-center gap-6">
          <EquipmentSlotItem 
            label="躯干护甲" 
            :icon="Shirt" 
            :active="sheet.combat.armor_class.base > 10"
            :value="sheet.combat.armor_class.base > 10 ? 'AC ' + sheet.combat.armor_class.base : ''"
            class="scale-125 mb-4"
            @click="unequip('body')"
            @mouseenter="e => handleMouseEnter('body', e)"
            @mouseleave="handleMouseLeave"
          />
          <div class="w-32 h-56 border-2 border-zinc-800 rounded-[3rem] flex items-center justify-center bg-zinc-950/50 relative overflow-hidden">
             <UserCircle class="w-24 h-24 text-zinc-900" />
             <div class="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-blue-900/10 to-transparent"></div>
          </div>
          
          <div class="flex gap-6 mt-2">
             <EquipmentSlotItem 
                label="主手" 
                :icon="Sword" 
                :active="sheet.weapons[0] && sheet.weapons[0].name !== '空手'"
                :value="sheet.weapons[0]?.name"
                @click="unequip('mainHand')"
                @mouseenter="e => handleMouseEnter('mainHand', e)"
                @mouseleave="handleMouseLeave"
             />
             <EquipmentSlotItem 
                label="副手" 
                :icon="Shield" 
                :active="sheet.has_shield || (sheet.weapons[1] && sheet.weapons[1].name !== '空手')"
                :value="sheet.has_shield ? '盾牌' : (sheet.weapons[1]?.name || '')"
                @click="unequip('offHand')"
                @mouseenter="e => handleMouseEnter('offHand', e)"
                @mouseleave="handleMouseLeave"
             />
          </div>
        </div>

        <div class="flex flex-col gap-6">
          <EquipmentSlotItem label="手套" :icon="Hand" />
          <EquipmentSlotItem label="戒指 I" :icon="Sparkle" />
          <EquipmentSlotItem label="戒指 II" :icon="Sparkle" />
          <EquipmentSlotItem label="乐器" :icon="Sparkle" />
        </div>
      </div>
    </div>
  </div>
</template>