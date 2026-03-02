<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import BioHeader from '../BioHeader.vue';
import ClassManager from '../ClassManager.vue';

const props = defineProps<{ sheet: any }>();
const emit = defineEmits(['update']);

const updateSheet = (key: string, val: any) => {
  emit('update', { [key]: val });
};
</script>

<template>
  <div class="space-y-8 pb-20">
    <!-- 顶部摘要块 -->
    <BioHeader 
      :bio="sheet.bio" 
      :prog="sheet.prog" 
      @update:bio="v => updateSheet('bio', v)" 
      @update:prog="v => updateSheet('prog', v)" 
    />
    
    <!-- 中部：职业管理与基础背景 (两栏) -->
    <div class="grid grid-cols-1 lg:grid-cols-[1fr_350px] gap-8">
      <!-- 职业管理块 -->
      <div class="bg-zinc-800/30 border border-zinc-700/50 rounded-2xl p-6 shadow-xl">
        <ClassManager 
          :prog="sheet.prog" 
          @update="v => updateSheet('prog', v)" 
        />
      </div>

      <!-- 身份详情块 -->
      <div class="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-6 space-y-4">
        <h3 class="text-[10px] font-black text-zinc-600 uppercase tracking-widest px-1">身份详情 (Identity)</h3>
        <div class="grid grid-cols-2 gap-4">
          <div class="flex flex-col gap-1">
            <span class="text-[8px] font-bold text-zinc-500 uppercase">种族</span>
            <input v-model="sheet.prog.race" @change="updateSheet('prog', sheet.prog)" class="bg-zinc-800 border-none rounded px-3 py-2 text-sm text-zinc-200 outline-none focus:ring-1 focus:ring-amber-500/50" />
          </div>
          <div class="flex flex-col gap-1">
            <span class="text-[8px] font-bold text-zinc-500 uppercase">背景</span>
            <input v-model="sheet.bio.background_name" @change="updateSheet('bio', sheet.bio)" class="bg-zinc-800 border-none rounded px-3 py-2 text-sm text-zinc-200 outline-none focus:ring-1 focus:ring-amber-500/50" />
          </div>
          <div class="flex flex-col gap-1">
            <span class="text-[8px] font-bold text-zinc-500 uppercase">阵营</span>
            <input v-model="sheet.bio.alignment" @change="updateSheet('bio', sheet.bio)" class="bg-zinc-800 border-none rounded px-3 py-2 text-sm text-zinc-200 outline-none focus:ring-1 focus:ring-amber-500/50" />
          </div>
          <div class="flex flex-col gap-1">
            <span class="text-[8px] font-bold text-zinc-500 uppercase">信仰</span>
            <input v-model="sheet.bio.faith" @change="updateSheet('bio', sheet.bio)" class="bg-zinc-800 border-none rounded px-3 py-2 text-sm text-zinc-200 outline-none focus:ring-1 focus:ring-amber-500/50" />
          </div>
        </div>
      </div>
    </div>

    <!-- 底部：故事与技能 (三栏或两栏) -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- 背景故事 -->
      <div class="bg-zinc-900/30 border border-zinc-800 rounded-2xl p-6">
        <h3 class="text-xs font-black text-zinc-500 uppercase tracking-widest mb-4">背景故事 (Backstory)</h3>
        <textarea 
          v-model="sheet.bio.backstory" 
          @change="updateSheet('bio', sheet.bio)"
          rows="12"
          class="w-full bg-transparent text-sm text-zinc-400 leading-relaxed resize-none outline-none focus:text-zinc-200"
          placeholder="谱写你的英雄史诗..."
        ></textarea>
      </div>

      <!-- 个性特征与熟练项 -->
      <div class="space-y-6">
        <div class="bg-zinc-800/50 border border-zinc-700/50 rounded-xl p-5 shadow-xl">
          <h3 class="text-xs font-black text-zinc-400 uppercase tracking-widest mb-4">个性特征</h3>
          <div class="space-y-3">
            <div v-for="(label, key) in {traits:'个性', ideals:'理念', bonds:'羁绊', flaws:'缺陷'}" :key="key" class="flex flex-col">
              <label class="text-[8px] font-black text-zinc-600 uppercase mb-1">{{ label }}</label>
              <textarea v-model="sheet.bio.personality[key]" @change="updateSheet('bio', sheet.bio)" class="bg-zinc-900 border border-zinc-700 rounded-lg p-2 text-xs text-zinc-300 resize-none h-16 outline-none focus:border-amber-500/50"></textarea>
            </div>
          </div>
        </div>

        <!-- 语言与工具 -->
        <div class="bg-zinc-800/50 border border-zinc-700/50 rounded-xl p-5 shadow-xl space-y-6">
          <div>
            <h3 class="text-xs font-black text-zinc-400 uppercase tracking-widest mb-4">语言与工具</h3>
            <div class="flex flex-wrap gap-2 mb-4">
              <div v-for="(lang, idx) in sheet.bio.languages" :key="idx" class="bg-zinc-900 border border-zinc-700 rounded-lg px-2 py-1 flex items-center gap-2">
                 <input v-model="sheet.bio.languages[idx]" @change="updateSheet('bio', sheet.bio)" class="bg-transparent text-[10px] text-zinc-200 outline-none w-16" />
                 <button @click="sheet.bio.languages.splice(idx, 1); updateSheet('bio', sheet.bio)" class="text-zinc-600 hover:text-red-500">×</button>
              </div>
              <button @click="sheet.bio.languages.push('新语言'); updateSheet('bio', sheet.bio)" class="bg-zinc-800 border border-dashed border-zinc-600 rounded-lg px-3 py-1 text-[10px] text-zinc-400 hover:text-zinc-200">+</button>
            </div>
            <div class="flex flex-wrap gap-2">
              <div v-for="(tool, idx) in sheet.bio.tool_proficiencies" :key="idx" class="bg-zinc-900 border border-zinc-700 rounded-lg px-2 py-1 flex items-center gap-2">
                 <input v-model="sheet.bio.tool_proficiencies[idx]" @change="updateSheet('bio', sheet.bio)" class="bg-transparent text-[10px] text-zinc-200 outline-none w-16" />
                 <button @click="sheet.bio.tool_proficiencies.splice(idx, 1); updateSheet('bio', sheet.bio)" class="text-zinc-600 hover:text-red-500">×</button>
              </div>
              <button @click="sheet.bio.tool_proficiencies.push('新工具'); updateSheet('bio', sheet.bio)" class="bg-zinc-800 border border-dashed border-zinc-600 rounded-lg px-3 py-1 text-[10px] text-zinc-400 hover:text-zinc-200">+</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>