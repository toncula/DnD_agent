<script setup lang="ts">
import { computed } from 'vue';
import { Plus, GraduationCap } from 'lucide-vue-next';
import ClassRow from './ClassRow.vue';

const props = defineProps<{
  prog: any;
}>();

const emit = defineEmits(['update']);

const totalLevel = computed(() => {
  return props.prog.classes.reduce((sum: number, c: any) => sum + c.level, 0);
});

// 标准 5E 职业列表
const standardClasses = [
  { name: '战士', hit_die: 'd10' },
  { name: '法师', hit_die: 'd6' },
  { name: '牧师', hit_die: 'd8' },
  { name: '游荡者', hit_die: 'd8' },
  { name: '蛮人', hit_die: 'd12' },
  { name: '德鲁伊', hit_die: 'd8' },
  { name: '吟游诗人', hit_die: 'd8' },
  { name: '术士', hit_die: 'd6' },
  { name: '邪术师', hit_die: 'd8' },
  { name: '圣武士', hit_die: 'd10' },
  { name: '游侠', hit_die: 'd10' },
  { name: '武僧', hit_die: 'd8' }
];

const updateClass = (index: number, updatedCls: any) => {
  const newList = [...props.prog.classes];
  newList[index] = updatedCls;
  
  // 同步更新总等级和显示名
  const total = newList.reduce((sum: number, c: any) => sum + c.level, 0);
  const mainClass = newList.find(c => c.is_primary)?.name || newList[0].name;
  
  emit('update', { 
    ...props.prog, 
    classes: newList, 
    level: total,
    character_class: mainClass
  });
};

const addMulticlass = (className: string) => {
  if (props.prog.classes.some((c: any) => c.name === className)) return;
  const classData = standardClasses.find(c => c.name === className);
  
  const newList = [...props.prog.classes, {
    name: className,
    level: 1,
    subclass: '',
    is_primary: false,
    hit_die: classData?.hit_die || 'd8'
  }];
  
  const total = newList.reduce((sum: number, c: any) => sum + c.level, 0);
  emit('update', { ...props.prog, classes: newList, level: total });
};

const removeClass = (index: number) => {
  const newList = [...props.prog.classes];
  newList.splice(index, 1);
  const total = newList.reduce((sum: number, c: any) => sum + c.level, 0);
  emit('update', { ...props.prog, classes: newList, level: total });
};
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between px-1">
      <div class="flex items-center gap-2">
        <GraduationCap class="w-5 h-5 text-zinc-500" />
        <h3 class="text-xs font-black text-zinc-500 uppercase tracking-widest">职业等级 (Classes)</h3>
      </div>
      <div class="bg-amber-500/10 text-amber-500 px-3 py-1 rounded-full border border-amber-500/20 text-[10px] font-black uppercase">
        总等级 {{ totalLevel }}
      </div>
    </div>

    <!-- 职业列表 -->
    <div class="space-y-2">
      <ClassRow 
        v-for="(cls, i) in prog.classes" 
        :key="cls.name"
        :cls="cls"
        :isFirst="i === 0"
        @update="v => updateClass(i, v)"
        @remove="removeClass(i)"
      />
    </div>

    <!-- 添加兼职 -->
    <div class="mt-6">
      <span class="text-[8px] font-black text-zinc-600 uppercase ml-1">添加兼职</span>
      <div class="flex flex-wrap gap-2 mt-2">
        <button 
          v-for="c in standardClasses" 
          :key="c.name"
          @click="addMulticlass(c.name)"
          :disabled="prog.classes.some((existing: any) => existing.name === c.name)"
          class="px-2 py-1.5 bg-zinc-900 border border-zinc-800 rounded text-[10px] text-zinc-400 hover:border-amber-500/50 hover:text-amber-500 disabled:opacity-20 disabled:hover:border-zinc-800 disabled:hover:text-zinc-400 transition-all flex items-center gap-1"
        >
          <Plus class="w-2.5 h-2.5" /> {{ c.name }}
        </button>
      </div>
    </div>
  </div>
</template>