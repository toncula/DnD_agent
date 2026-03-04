<script setup lang="ts">
import { Shield, Sword, Shirt, HardHat, Footprints, Hand, Sparkle, Scale, Anchor, Wind } from 'lucide-vue-next';
import { computed } from 'vue';
import EquipmentSlotItem from './EquipmentSlotItem.vue';
import CharacterSilhouette from './CharacterSilhouette.vue';
import WeaponStatsBar from './WeaponStatsBar.vue';

const props = defineProps<{
  sheet: any;
}>();

const emit = defineEmits(['update', 'hover-item']);

const getEquippedItemBySlot = (slotType: string) => {
  if (!props.sheet.inventory) return null;
  return props.sheet.inventory.find((i: any) => i.is_equipped && i.slot_type === slotType);
};

// 核心槽位计算
const equippedArmor = computed(() => props.sheet.inventory?.find((i: any) => i.is_equipped && (i.item_type === '护甲' || i.slot_type === '躯干')));
const equippedLegs = computed(() => props.sheet.inventory?.find((i: any) => i.is_equipped && i.slot_type === '腿部'));
const equippedMainhand = computed(() => props.sheet.inventory?.find((i: any) => i.is_equipped && (i.slot_type === '主手' || i.slot_type === '双手')));

// 副手逻辑：如果是双手武器，则副手显示为主手武器
const equippedOffhand = computed(() => {
  if (equippedMainhand.value?.slot_type === '双手') {
    return equippedMainhand.value;
  }
  return props.sheet.inventory?.find((i: any) => i.is_equipped && (i.item_type === '盾牌' || i.slot_type === '副手'));
});

const isAttuned = computed(() => props.sheet.inventory?.some((i: any) => i.is_equipped && i.is_attuned));

const handleMouseEnter = (item: any, event: MouseEvent) => {
  if (item) emit('hover-item', item, event);
};

const handleMouseLeave = () => {
  emit('hover-item', null);
};

const unequip = (item: any) => {
  if (!item) return;
  const itemToUnequip = item.value || item;
  if (!itemToUnequip || !itemToUnequip.name) return;

  const newInventory = JSON.parse(JSON.stringify(props.sheet.inventory));
  const target = newInventory.find((i: any) => i.name === itemToUnequip.name);
  if (target) {
    target.is_equipped = false;
    emit('update', { inventory: newInventory });
  }
};
</script>

<template>
  <div class="bg-zinc-900/80 border border-zinc-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden group min-h-[650px]">
    <!-- 背景光效 -->
    <div class="absolute inset-0 bg-gradient-to-b from-blue-500/5 to-transparent pointer-events-none"></div>
    
    <!-- 1. 顶部栏 (标题与负重) -->
    <div class="flex justify-between items-start mb-4 relative z-10">
      <div>
        <h3 class="text-sm font-black text-zinc-400 uppercase tracking-[0.3em] mb-1">纸娃娃系统</h3>
        <p class="text-[10px] text-zinc-600 font-bold uppercase">Combat Readiness</p>
      </div>
      <div class="flex items-center gap-2 bg-black/40 px-3 py-1.5 rounded-full border border-white/5 shadow-inner">
        <Scale class="w-3.5 h-3.5 text-zinc-500" />
        <span class="text-[11px] font-black" :class="sheet.total_weight > sheet.carrying_capacity ? 'text-red-500' : 'text-zinc-400'">
          {{ sheet.total_weight.toFixed(1) }} <span class="text-zinc-600">/</span> {{ sheet.carrying_capacity }}
        </span>
      </div>
    </div>

    <!-- 2. 环绕式装备布局 -->
    <div class="relative flex justify-center items-center h-[480px]">
      
      <!-- 中心组件: 人物剪影与旋转特效 -->
      <CharacterSilhouette :is-attuned="isAttuned" />

      <!-- 中轴位组件 -->
      <div class="absolute inset-0 flex flex-col items-center justify-between py-2 pointer-events-none">
        <div class="pointer-events-auto">
          <EquipmentSlotItem 
            label="躯干护甲" :icon="Shirt" 
            :active="!!equippedArmor" :value="equippedArmor?.name" 
            class="scale-110 shadow-lg"
            @click="unequip(equippedArmor)"
            @mouseenter="e => handleMouseEnter(equippedArmor, e)"
            @mouseleave="handleMouseLeave"
          />
        </div>
        <div class="pointer-events-auto">
          <EquipmentSlotItem 
            label="腿部" :icon="Anchor" 
            :active="!!equippedLegs" :value="equippedLegs?.name" 
            @click="unequip(equippedLegs)"
            @mouseenter="e => handleMouseEnter(equippedLegs, e)"
            @mouseleave="handleMouseLeave"
          />
        </div>
      </div>

      <!-- 左侧位 (Head, Neck, Mainhand, Belt, Feet) -->
      <div class="absolute left-4 top-0 bottom-0 flex flex-col justify-between py-4">
        <EquipmentSlotItem 
          label="头部" :icon="HardHat" 
          :active="!!getEquippedItemBySlot('头部')" :value="getEquippedItemBySlot('头部')?.name" 
          @click="unequip(getEquippedItemBySlot('头部'))"
          @mouseenter="e => handleMouseEnter(getEquippedItemBySlot('头部'), e)"
          @mouseleave="handleMouseLeave"
        />
        <EquipmentSlotItem 
          label="项链" :icon="Sparkle" 
          :active="!!getEquippedItemBySlot('项链')" :value="getEquippedItemBySlot('项链')?.name" 
          @click="unequip(getEquippedItemBySlot('项链'))"
          @mouseenter="e => handleMouseEnter(getEquippedItemBySlot('项链'), e)"
          @mouseleave="handleMouseLeave"
        />
        <EquipmentSlotItem 
          label="主手" :icon="Sword" 
          :active="!!equippedMainhand" :value="equippedMainhand?.name" 
          class="scale-125 border-blue-500/20 bg-blue-500/5 shadow-[0_0_20px_rgba(59,130,246,0.1)]"
          @click="unequip(equippedMainhand)"
          @mouseenter="e => handleMouseEnter(equippedMainhand, e)"
          @mouseleave="handleMouseLeave"
        />
        <EquipmentSlotItem 
          label="腰带" :icon="Sparkle" 
          :active="!!getEquippedItemBySlot('腰带')" :value="getEquippedItemBySlot('腰带')?.name" 
          @click="unequip(getEquippedItemBySlot('腰带'))"
          @mouseenter="e => handleMouseEnter(getEquippedItemBySlot('腰带'), e)"
          @mouseleave="handleMouseLeave"
        />
        <EquipmentSlotItem 
          label="足部" :icon="Footprints" 
          :active="!!getEquippedItemBySlot('足部')" :value="getEquippedItemBySlot('足部')?.name" 
          @click="unequip(getEquippedItemBySlot('足部'))"
          @mouseenter="e => handleMouseEnter(getEquippedItemBySlot('足部'), e)"
          @mouseleave="handleMouseLeave"
        />
      </div>

      <!-- 右侧位 (Cape, Gloves, Offhand, Ring I, Ring II) -->
      <div class="absolute right-4 top-0 bottom-0 flex flex-col justify-between py-4 items-end">
        <EquipmentSlotItem 
          label="披风" :icon="Wind" 
          :active="!!getEquippedItemBySlot('披风')" :value="getEquippedItemBySlot('披风')?.name" 
          @click="unequip(getEquippedItemBySlot('披风'))"
          @mouseenter="e => handleMouseEnter(getEquippedItemBySlot('披风'), e)"
          @mouseleave="handleMouseLeave"
        />
        <EquipmentSlotItem 
          label="手套" :icon="Hand" 
          :active="!!getEquippedItemBySlot('手套')" :value="getEquippedItemBySlot('手套')?.name" 
          @click="unequip(getEquippedItemBySlot('手套'))"
          @mouseenter="e => handleMouseEnter(getEquippedItemBySlot('手套'), e)"
          @mouseleave="handleMouseLeave"
        />
        <EquipmentSlotItem 
          label="副手" :icon="Shield" 
          :active="!!equippedOffhand" :value="equippedOffhand?.name" 
          class="scale-125 border-emerald-500/20 bg-emerald-500/5 shadow-[0_0_20px_rgba(16,185,129,0.1)]"
          @click="unequip(equippedOffhand)"
          @mouseenter="e => handleMouseEnter(equippedOffhand, e)"
          @mouseleave="handleMouseLeave"
        />
        <EquipmentSlotItem 
          label="戒指 I" :icon="Sparkle" 
          :active="!!getEquippedItemBySlot('戒指 I')" :value="getEquippedItemBySlot('戒指 I')?.name" 
          @click="unequip(getEquippedItemBySlot('戒指 I'))"
          @mouseenter="e => handleMouseEnter(getEquippedItemBySlot('戒指 I'), e)"
          @mouseleave="handleMouseLeave"
        />
        <EquipmentSlotItem 
          label="戒指 II" :icon="Sparkle" 
          :active="!!getEquippedItemBySlot('戒指 II')" :value="getEquippedItemBySlot('戒指 II')?.name" 
          @click="unequip(getEquippedItemBySlot('戒指 II'))"
          @mouseenter="e => handleMouseEnter(getEquippedItemBySlot('戒指 II'), e)"
          @mouseleave="handleMouseLeave"
        />
      </div>
    </div>

    <!-- 3. 底部数值栏 (独立武器信息面板) -->
    <WeaponStatsBar :mainhand="equippedMainhand" :offhand="equippedOffhand" />
  </div>
</template>