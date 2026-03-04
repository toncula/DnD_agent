<script setup lang="ts">
import { Target, Flame, Sword, Shield } from 'lucide-vue-next';

defineProps<{
  mainhand?: any;
  offhand?: any;
}>();
</script>

<template>
  <div class="mt-8 pt-6 border-t border-zinc-800/50 flex flex-col items-center gap-4">
    <!-- 武器数值面板 -->
    <div class="flex gap-4 flex-wrap justify-center w-full">
      <!-- 主手数值 -->
      <div v-if="mainhand?.item_type === '武器'" 
           class="flex items-center gap-3 bg-zinc-950/50 border border-zinc-800 px-4 py-2 rounded-2xl shadow-xl transition-all hover:border-blue-500/30 group">
        <div class="p-1.5 bg-blue-600/10 rounded-lg group-hover:bg-blue-600/20 transition-colors">
          <Sword class="w-3.5 h-3.5 text-blue-400" />
        </div>
        <div class="flex flex-col">
          <span class="text-[8px] font-black text-zinc-600 uppercase tracking-widest leading-none mb-1">主手: {{ mainhand.name }}</span>
          <div class="flex items-center gap-3">
            <div class="flex items-center gap-1.5">
              <Target class="w-3 h-3 text-blue-400 opacity-70" />
              <span class="text-sm font-black text-blue-400 leading-none">{{ mainhand.derived_attack_roll }}</span>
            </div>
            <div class="w-px h-2.5 bg-zinc-800"></div>
            <div class="flex items-center gap-1.5">
              <Flame class="w-3 h-3 text-amber-400 opacity-70" />
              <span class="text-sm font-black text-amber-400 leading-none">{{ mainhand.derived_damage_roll }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 副手数值 (仅当是武器且不是主手的双手武器时显示) -->
      <div v-if="offhand?.item_type === '武器' && offhand?.name !== mainhand?.name" 
           class="flex items-center gap-3 bg-zinc-950/50 border border-zinc-800 px-4 py-2 rounded-2xl shadow-xl transition-all hover:border-emerald-500/30 group">
        <div class="p-1.5 bg-emerald-600/10 rounded-lg group-hover:bg-emerald-600/20 transition-colors">
          <Sword class="w-3.5 h-3.5 text-emerald-400" />
        </div>
        <div class="flex flex-col">
          <span class="text-[8px] font-black text-zinc-600 uppercase tracking-widest leading-none mb-1">副手: {{ offhand.name }}</span>
          <div class="flex items-center gap-3">
            <div class="flex items-center gap-1.5">
              <Target class="w-3 h-3 text-blue-400 opacity-70" />
              <span class="text-sm font-black text-blue-400 leading-none">{{ offhand.derived_attack_roll }}</span>
            </div>
            <div class="w-px h-2.5 bg-zinc-800"></div>
            <div class="flex items-center gap-1.5">
              <Flame class="w-3 h-3 text-amber-400 opacity-70" />
              <span class="text-sm font-black text-amber-400 leading-none">{{ offhand.derived_damage_roll }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>