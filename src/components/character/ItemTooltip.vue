<script setup lang="ts">
import { Sword, Shield, Package, Info, Zap, Sparkles, AlertCircle } from 'lucide-vue-next';

const props = defineProps<{
  item: any;
  x: number;
  y: number;
}>();

const getRarityColor = (rarity: string) => {
  const colors: any = {
    '普通': 'text-zinc-400',
    '精良': 'text-emerald-400',
    '稀有': 'text-blue-400',
    '极稀有': 'text-purple-400',
    '传说': 'text-orange-400',
    '神器': 'text-red-500'
  };
  return colors[rarity] || 'text-zinc-400';
};
</script>

<template>
  <div 
    class="fixed z-[100] w-72 pointer-events-none transition-opacity duration-200 shadow-[0_20px_50px_rgba(0,0,0,0.5)]"
    :style="{ left: x + 15 + 'px', top: y + 15 + 'px' }"
  >
    <div class="bg-[#1a1b1e] border-2 border-[#3e3f45] rounded-xl overflow-hidden flex flex-col shadow-2xl">
      <!-- 头部：名称与类别 -->
      <div class="bg-[#2a2b30] p-4 border-b border-[#3e3f45]">
        <div class="flex justify-between items-start mb-1">
          <h4 class="text-lg font-black text-zinc-100 leading-tight">{{ item.name }}</h4>
          <component 
            :is="item.item_type === '武器' ? Sword : (item.item_type === '护甲' || item.item_type === '盾牌' ? Shield : Package)" 
            class="w-5 h-5 text-zinc-500 shrink-0 ml-2" 
          />
        </div>
        <div class="flex items-center gap-2">
           <span class="text-[9px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded bg-black/30" :class="getRarityColor(item.rarity)">
             {{ item.rarity }}
           </span>
           <span class="text-[9px] text-zinc-500 uppercase font-bold tracking-widest">
            {{ item.category }} · {{ item.item_type || '物品' }}
          </span>
        </div>
      </div>

      <!-- 内容区 -->
      <div class="p-4 space-y-4">
        <!-- 战斗属性 -->
        <div v-if="item.category === '装备'" class="grid grid-cols-2 gap-4">
           <div v-if="item.item_type === '武器'" class="flex flex-col">
              <span class="text-[9px] text-zinc-500 font-black uppercase mb-1">攻击 / 伤害</span>
              <div class="flex items-baseline gap-1">
                <span class="text-xl font-black text-blue-400">{{ item.derived_attack_roll || '--' }}</span>
                <span class="text-xs font-bold text-amber-400">{{ item.derived_damage_roll || item.damage_dice }}</span>
              </div>
              <div v-if="item.weapon_mastery" class="mt-1 flex items-center gap-1">
                 <Zap class="w-2.5 h-2.5 text-amber-500" />
                 <span class="text-[10px] font-black text-amber-500 uppercase">{{ item.weapon_mastery }}</span>
              </div>
           </div>
           
           <div v-if="item.item_type === '护甲'" class="flex flex-col">
              <span class="text-[9px] text-zinc-500 font-black uppercase mb-1">护甲等级 (AC)</span>
              <div class="flex items-baseline gap-1">
                <span class="text-xl font-black text-emerald-400">{{ item.ac_base }}</span>
                <span v-if="item.dex_cap !== null" class="text-[9px] font-bold text-zinc-500">(敏捷上限 {{item.dex_cap}})</span>
              </div>
           </div>

           <div v-if="item.item_type === '盾牌'" class="flex flex-col">
              <span class="text-[9px] text-zinc-500 font-black uppercase mb-1">AC 加成</span>
              <span class="text-xl font-black text-emerald-400">+{{ item.ac_bonus }}</span>
           </div>

           <div v-if="item.requires_attunement" class="flex flex-col">
              <span class="text-[9px] text-zinc-500 font-black uppercase mb-1">同调</span>
              <div class="flex items-center gap-1">
                <Zap class="w-3 h-3" :class="item.is_attuned ? 'text-amber-400' : 'text-zinc-600'" />
                <span class="text-[10px] font-bold" :class="item.is_attuned ? 'text-amber-400' : 'text-zinc-500'">
                  {{ item.is_attuned ? '已同调' : '未同调' }}
                </span>
              </div>
           </div>
        </div>

        <!-- 特殊动作展示 -->
        <div v-if="item.special_actions && item.special_actions.length > 0" class="space-y-2">
           <div class="flex items-center gap-1.5 text-blue-400 border-b border-blue-900/30 pb-1">
              <Sparkles class="w-3 h-3" />
              <span class="text-[9px] font-black uppercase tracking-wider">特殊战技 / 技能</span>
           </div>
           <div v-for="action in item.special_actions" :key="action.name" class="space-y-0.5">
              <div class="flex justify-between items-center">
                 <span class="text-[10px] font-bold text-zinc-200">{{ action.name }}</span>
                 <span class="text-[8px] bg-zinc-800 text-zinc-500 px-1 rounded">{{ action.activation }}</span>
              </div>
              <p class="text-[9px] text-zinc-500 leading-tight">{{ action.description }}</p>
           </div>
        </div>

        <!-- 特性列表 -->
        <div v-if="item.properties && item.properties.length > 0" class="flex flex-wrap gap-1">
           <span v-for="p in item.properties" :key="p" class="text-[8px] font-black uppercase bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded border border-zinc-700">
             {{ p }}
           </span>
        </div>

        <!-- 详细描述 -->
        <div class="space-y-1.5">
          <div class="flex items-center gap-1.5 text-zinc-500 border-b border-zinc-800 pb-1">
            <Info class="w-3 h-3" />
            <span class="text-[9px] font-black uppercase tracking-wider">说明</span>
          </div>
          <p class="text-[11px] text-zinc-400 leading-relaxed italic">
            {{ item.description || '一件平凡的物品，似乎没有什么特别的。' }}
          </p>
        </div>

        <!-- 警告信息 (力量不足, 潜行劣势等) -->
        <div v-if="item.stealth_disadv || item.strength_req > 0" class="space-y-1">
           <div v-if="item.stealth_disadv" class="flex items-center gap-1.5 text-amber-500/60">
              <AlertCircle class="w-3 h-3" />
              <span class="text-[9px] font-bold uppercase">潜行劣势</span>
           </div>
           <div v-if="item.strength_req > 0" class="flex items-center gap-1.5 text-red-500/60">
              <AlertCircle class="w-3 h-3" />
              <span class="text-[9px] font-bold uppercase">需要力量 {{ item.strength_req }}</span>
           </div>
        </div>
      </div>

      <!-- 底部：重量与槽位 -->
      <div class="bg-black/40 p-3 px-4 border-t border-white/5 flex justify-between items-center">
        <div class="flex items-center gap-2">
           <Package class="w-3 h-3 text-zinc-600" />
           <span class="text-[10px] text-zinc-400 font-bold">{{ item.weight || 0 }} 磅</span>
        </div>
        <span class="text-[9px] text-zinc-600 font-black uppercase tracking-tighter">{{ item.slot_type || '无槽位' }}</span>
      </div>
    </div>
    
    <!-- 装饰性尖角 -->
    <div class="absolute -left-2 top-6 w-4 h-4 bg-[#1a1b1e] border-l-2 border-t-2 border-[#3e3f45] rotate-[-45deg]"></div>
  </div>
</template>