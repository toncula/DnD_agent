<script setup lang="ts">
import { User, Shield, Zap, TrendingUp } from 'lucide-vue-next';

const props = defineProps<{
  bio: any;
  prog: any;
}>();

const emit = defineEmits(['update:bio', 'update:prog']);

const updateBio = (field: string, value: string | number) => {
  const newBio = { ...props.bio, [field]: value };
  emit('update:bio', newBio);
};

const updateProg = (field: string, value: string | number) => {
  const newProg = { ...props.prog, [field]: value };
  emit('update:prog', newProg);
};
</script>

<template>
  <div class="bg-zinc-800/50 border border-zinc-700/50 rounded-xl p-5 shadow-xl mb-2">
    <div class="flex flex-wrap gap-6 items-end">
      <!-- 姓名与种族 -->
      <div class="flex-1 min-w-[250px] flex flex-col gap-4">
        <div class="flex flex-col gap-1.5">
          <label class="text-xs text-zinc-500 font-black uppercase tracking-widest px-1">英雄姓名</label>
          <div class="relative group">
            <User class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500 group-focus-within:text-red-500 transition-colors" />
            <input 
              :value="bio.character_name"
              @input="e => updateBio('character_name', (e.target as HTMLInputElement).value)"
              class="w-full bg-zinc-900/50 border border-zinc-700 rounded-xl pl-11 pr-4 py-3 text-3xl font-black focus:ring-2 focus:ring-red-500/50 outline-none transition-all tracking-tight"
              placeholder="未命名英雄"
            />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-[11px] text-zinc-500 font-bold uppercase tracking-wider px-1">种族</label>
            <input 
              :value="prog.race"
              @input="e => updateProg('race', (e.target as HTMLInputElement).value)"
              class="bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-base font-bold focus:border-red-500 outline-none"
            />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[11px] text-zinc-500 font-bold uppercase tracking-wider px-1">子种族</label>
            <input 
              :value="prog.subrace"
              @input="e => updateProg('subrace', (e.target as HTMLInputElement).value)"
              class="bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-base font-bold focus:border-red-500 outline-none"
            />
          </div>
        </div>
      </div>

      <!-- 职业与等级 -->
      <div class="flex-1 min-w-[250px] flex flex-col gap-4">
        <div class="flex flex-col gap-1.5">
          <label class="text-xs text-zinc-500 font-black uppercase tracking-widest px-1">主要职业</label>
          <div class="relative group">
            <Shield class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500 group-focus-within:text-red-500 transition-colors" />
            <input 
              :value="prog.character_class"
              @input="e => updateProg('character_class', (e.target as HTMLInputElement).value)"
              class="w-full bg-zinc-900 border border-zinc-700 rounded-xl pl-11 pr-4 py-3 text-2xl font-black focus:ring-2 focus:ring-red-500/50 outline-none transition-all"
            />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-[11px] text-zinc-500 font-bold uppercase tracking-wider px-1">等级 (1-20)</label>
            <div class="relative group">
              <TrendingUp class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 group-focus-within:text-red-500 transition-colors" />
              <input 
                type="number"
                :value="prog.level"
                @input="e => updateProg('level', parseInt((e.target as HTMLInputElement).value))"
                class="w-full bg-zinc-900 border border-zinc-700 rounded-lg pl-10 pr-4 py-2 text-lg font-black focus:ring-2 focus:ring-red-500/50 outline-none"
              />
            </div>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[11px] text-zinc-500 font-bold uppercase tracking-wider px-1">当前经验值</label>
            <div class="relative group">
              <Zap class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 group-focus-within:text-red-500 transition-colors" />
              <input 
                type="number"
                :value="prog.exp"
                @input="e => updateProg('exp', parseInt((e.target as HTMLInputElement).value))"
                class="w-full bg-zinc-900 border border-zinc-700 rounded-lg pl-10 pr-4 py-2 text-lg font-black focus:ring-2 focus:ring-red-500/50 outline-none"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
