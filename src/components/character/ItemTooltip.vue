<script setup lang="ts">
import { Sword, Shield, Package, Info } from 'lucide-vue-next';

const props = defineProps<{
  item: any;
  x: number;
  y: number;
}>();
</script>

<template>
  <div 
    class="fixed z-[100] w-72 pointer-events-none transition-opacity duration-200 shadow-[0_20px_50px_rgba(0,0,0,0.5)]"
    :style="{ left: x + 15 + 'px', top: y + 15 + 'px' }"
  >
    <div class="bg-[#1a1b1e] border-2 border-[#3e3f45] rounded-lg overflow-hidden flex flex-col">
      <!-- 头部：名称与类别 -->
      <div class="bg-[#2a2b30] p-3 border-b border-[#3e3f45] flex justify-between items-start">
        <div class="flex flex-col">
          <h4 class="text-lg font-black text-zinc-100 leading-tight">{{ item.name }}</h4>
          <span class="text-[10px] text-zinc-500 uppercase font-bold tracking-widest mt-1">
            {{ item.category }} · {{ item.slot_type || '通用' }}
          </span>
        </div>
        <component 
          :is="item.category === '装备' ? (item.slot_type === '躯干' ? Shield : Sword) : Package" 
          class="w-5 h-5 text-zinc-600" 
        />
      </div>

      <!-- 内容区 -->
      <div class="p-4 space-y-3">
        <!-- 核心属性展示 (如果是装备) -->
        <div v-if="item.category === '装备'" class="flex gap-4">
           <!-- 仅武器显示伤害 -->
           <div v-if="item.item_type === '武器'" class="flex flex-col">
              <span class="text-[10px] text-zinc-500 font-bold uppercase">伤害</span>
              <span class="text-xl font-black text-blue-400">{{ item.description?.match(/\d+d\d+/)?.[0] || '1d4' }}</span>
           </div>
           <!-- 护甲或盾牌显示 AC -->
           <div v-if="item.item_type === '护甲' || item.item_type === '盾牌'" class="flex flex-col">
              <span class="text-[10px] text-zinc-500 font-bold uppercase">
                {{ item.item_type === '盾牌' ? '加成' : '护甲等级 (AC)' }}
              </span>
              <span class="text-xl font-black text-emerald-400">
                {{ item.item_type === '盾牌' ? '+2 AC' : (item.description?.match(/\d+/)?.[0] || '10') }}
              </span>
           </div>
        </div>

        <!-- 详细描述 -->
        <div class="flex flex-col gap-1">
          <div class="flex items-center gap-1.5 text-zinc-400">
            <Info class="w-3 h-3" />
            <span class="text-[10px] font-bold uppercase tracking-wider">详细说明</span>
          </div>
          <p class="text-xs text-zinc-400 leading-relaxed italic">
            {{ item.description || '一件平凡的物品，似乎没有什么特别的。' }}
          </p>
        </div>
      </div>

      <!-- 底部：重量 -->
      <div class="bg-black/20 p-2 px-4 border-t border-white/5 flex justify-between items-center">
        <span class="text-[10px] text-zinc-600 font-bold uppercase">重量</span>
        <span class="text-[10px] text-zinc-400">{{ item.weight || 0 }} 磅</span>
      </div>
    </div>
    
    <!-- 装饰性尖角 -->
    <div class="absolute -left-2 top-4 w-4 h-4 bg-[#1a1b1e] border-l-2 border-t-2 border-[#3e3f45] rotate-[-45deg]"></div>
  </div>
</template>