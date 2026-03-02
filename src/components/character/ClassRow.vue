<script setup lang="ts">
import { Trash2, ShieldCheck } from 'lucide-vue-next';

const props = defineProps<{
  classInfo: any;
}>();

const emit = defineEmits(['update', 'remove']);

// 5E 标准职业配置表
const classPresets: Record<string, { hd: string }> = {
  '战士': { hd: 'd10' },
  '圣武士': { hd: 'd10' },
  '游侠': { hd: 'd10' },
  '野蛮人': { hd: 'd12' },
  '牧师': { hd: 'd8' },
  '德鲁伊': { hd: 'd8' },
  '吟游诗人': { hd: 'd8' },
  '武僧': { hd: 'd8' },
  '游荡者': { hd: 'd8' },
  '邪术师': { hd: 'd8' },
  '人工技师': { hd: 'd8' },
  '术士': { hd: 'd6' },
  '法师': { hd: 'd6' }
};

const updateField = (field: string, value: any) => {
  const updates: any = { [field]: value };
  
  // 自动化逻辑：如果修改了职业名称，自动同步生命骰
  if (field === 'name' && classPresets[value]) {
    updates.hit_die = classPresets[value].hd;
  }
  
  emit('update', { ...props.classInfo, ...updates });
};
</script>

<template>
  <div class="flex items-center gap-4 bg-zinc-950/50 border border-zinc-800 rounded-2xl p-3 group transition-all hover:border-zinc-700">
    <!-- 主职业标记 -->
    <div class="flex flex-col items-center justify-center gap-1 min-w-[40px]">
      <button 
        @click="updateField('is_primary', !classInfo.is_primary)"
        class="transition-all"
      >
        <div v-if="classInfo.is_primary" class="bg-emerald-500/20 p-1.5 rounded-lg border border-emerald-500/50">
          <ShieldCheck class="w-4 h-4 text-emerald-400" />
        </div>
        <div v-else class="bg-zinc-900 p-1.5 rounded-lg border border-zinc-800 text-zinc-700 hover:text-zinc-500">
          <ShieldCheck class="w-4 h-4" />
        </div>
      </button>
      <span class="text-[7px] font-black uppercase tracking-tighter" :class="classInfo.is_primary ? 'text-emerald-500' : 'text-zinc-700'">
        {{ classInfo.is_primary ? '首选' : '兼职' }}
      </span>
    </div>

    <!-- 职业字段选择区 -->
    <div class="flex-1 grid grid-cols-1 md:grid-cols-4 gap-4">
      <!-- 职业名称 (下拉框) -->
      <div class="flex flex-col gap-1">
        <label class="text-[8px] font-black text-zinc-600 uppercase tracking-widest px-1">职业</label>
        <select 
          :value="classInfo.name"
          @change="e => updateField('name', (e.target as HTMLSelectElement).value)"
          class="bg-zinc-900 border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-zinc-200 outline-none focus:border-blue-500 appearance-none cursor-pointer"
        >
          <option v-for="(cfg, name) in classPresets" :key="name" :value="name">{{ name }}</option>
          <option value="自定义">自定义/其他</option>
        </select>
      </div>

      <!-- 等级 -->
      <div class="flex flex-col gap-1">
        <label class="text-[8px] font-black text-zinc-600 uppercase tracking-widest px-1">等级</label>
        <input 
          type="number"
          :value="classInfo.level"
          @input="e => updateField('level', parseInt((e.target as HTMLInputElement).value) || 1)"
          class="bg-zinc-900 border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-zinc-200 outline-none focus:border-blue-500"
        />
      </div>

      <!-- 子职业 (保留手动输入，增强自由度) -->
      <div class="flex flex-col gap-1">
        <label class="text-[8px] font-black text-zinc-600 uppercase tracking-widest px-1">子职业</label>
        <input 
          :value="classInfo.subclass"
          @input="e => updateField('subclass', (e.target as HTMLInputElement).value)"
          class="bg-zinc-900 border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-zinc-200 outline-none focus:border-blue-500"
          placeholder="如: 冠军"
        />
      </div>

      <!-- 生命骰 (只读/自动关联) -->
      <div class="flex flex-col gap-1">
        <label class="text-[8px] font-black text-zinc-600 uppercase tracking-widest px-1">生命骰</label>
        <div class="bg-zinc-950 border border-zinc-800/50 rounded-xl px-3 py-1.5 text-[10px] font-black text-zinc-500 flex items-center h-full">
          {{ classInfo.hit_die }}
        </div>
      </div>
    </div>

    <!-- 移除按钮 -->
    <div class="flex flex-col items-end gap-2">
      <button @click="emit('remove')" class="p-2 text-zinc-800 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all">
        <Trash2 class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>

<style scoped>
select {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%233f3f46'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 1rem;
}
</style>