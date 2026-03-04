<script setup lang="ts">
import { UserCircle } from 'lucide-vue-next';

defineProps<{
  isAttuned: boolean;
}>();
</script>

<template>
  <div class="relative z-0">
    <!-- 装饰性旋转光圈 -->
    <div class="absolute inset-0 -m-12 border border-zinc-800/50 rounded-full animate-[spin_20s_linear_infinite] pointer-events-none"></div>
    <div class="absolute inset-0 -m-20 border border-zinc-800/20 rounded-full animate-[spin_30s_linear_infinite_reverse] pointer-events-none"></div>
    
    <!-- 中心剪影容器 -->
    <div class="w-48 h-72 border-2 border-zinc-800/50 rounded-[4rem] flex items-center justify-center bg-zinc-950/30 backdrop-blur-sm relative overflow-hidden shadow-inner">
      <UserCircle class="w-32 h-32 text-zinc-900/50" />
      
      <!-- 同调状态脉冲特效 -->
      <div v-if="isAttuned" class="absolute inset-0 animate-pulse bg-blue-500/5 shadow-[inset_0_0_40px_rgba(59,130,246,0.1)]"></div>
      
      <!-- 底部渐变遮罩 -->
      <div class="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-blue-900/10 to-transparent"></div>
    </div>
  </div>
</template>