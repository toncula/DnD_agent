<script setup lang="ts">
import { Plus, Trash2, ShieldCheck } from 'lucide-vue-next';
import ClassRow from './ClassRow.vue';

const props = defineProps<{
  prog: any;
}>();

const emit = defineEmits(['update:prog']);

const addClass = () => {
  const newClasses = [...props.prog.classes, { name: '战士', level: 1, subclass: '', is_primary: false, hit_die: 'd10' }];
  emit('update:prog', { ...props.prog, classes: newClasses });
};

const updateClass = (index: number, updates: any) => {
  const newClasses = [...props.prog.classes];
  newClasses[index] = { ...newClasses[index], ...updates };
  
  if (updates.is_primary) {
    newClasses.forEach((c, i) => { if (i !== index) c.is_primary = false; });
  }
  
  emit('update:prog', { ...props.prog, classes: newClasses });
};

const removeClass = (index: number) => {
  const newClasses = [...props.prog.classes];
  newClasses.splice(index, 1);
  emit('update:prog', { ...props.prog, classes: newClasses });
};
</script>

<template>
  <div class="bg-zinc-900/50 border border-zinc-800 rounded-3xl p-6">
    <div class="flex items-center justify-between mb-6 px-2">
      <div class="flex items-center gap-3">
        <div class="bg-zinc-800 p-2 rounded-xl"><ShieldCheck class="w-5 h-5 text-emerald-400" /></div>
        <h3 class="text-lg font-black text-white uppercase tracking-tighter">职业等级</h3>
      </div>
      <button @click="addClass" class="text-[10px] font-black text-blue-500 hover:text-blue-400 transition-colors uppercase tracking-widest">+ 兼职</button>
    </div>

    <div class="space-y-3">
      <ClassRow 
        v-for="(c, i) in prog.classes" 
        :key="i"
        :class-info="c"
        @update="v => updateClass(i, v)"
        @remove="removeClass(i)"
      />
    </div>
  </div>
</template>