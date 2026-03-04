<script setup lang="ts">
import { ref } from 'vue';
import { User, ScrollText, Heart, Languages, Wrench } from 'lucide-vue-next';
import BioHeader from '../BioHeader.vue';
import ClassManager from '../ClassManager.vue';

const props = defineProps<{
  sheet: any;
}>();

const emit = defineEmits(['update']);

const updateVal = (key: string, val: any) => {
  emit('update', { [key]: val });
};

const updateBio = (newBio: any) => {
  updateVal('bio', newBio);
};

const updatePersonality = (field: string, val: any) => {
  const p = { ...props.sheet.bio.personality, [field]: val };
  const bio = { ...props.sheet.bio, personality: p };
  updateBio(bio);
};

// 处理列表字段的同步 (如语言和工具)
const updateBioList = (field: string, val: string) => {
  const list = val.split(/[,，]/).map(s => s.trim()).filter(s => s !== '');
  const bio = { ...props.sheet.bio, [field]: list };
  updateBio(bio);
};
</script>

<template>
  <div class="space-y-8 pb-20">
    <BioHeader 
      :bio="sheet.bio" 
      :prog="sheet.prog" 
      @update:bio="updateBio" 
      @update:prog="v => updateVal('prog', v)"
    />

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div class="lg:col-span-2 space-y-8">
        <!-- 身份详情 -->
        <div class="bg-zinc-900/50 border border-zinc-800 rounded-3xl p-6">
          <div class="flex items-center gap-3 mb-6 px-2">
            <div class="bg-zinc-800 p-2 rounded-xl"><User class="w-5 h-5 text-blue-400" /></div>
            <h3 class="text-lg font-black text-white uppercase tracking-tighter">身份详情</h3>
          </div>
          
          <!-- 基础属性网格 -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
            <div v-for="f in [
              {k:'age', l:'年龄', p:'20', t:'number'}, {k:'gender', l:'性别', p:'男/女', t:'text'},
              {k:'height', l:'身高', p:'180cm', t:'text'}, {k:'weight', l:'体重', p:'70kg', t:'text'},
              {k:'alignment', l:'阵营', p:'中立善', t:'text'}, {k:'faith', l:'信仰', p:'无', t:'text'},
              {k:'hometown', l:'故乡', p:'无', t:'text'}, {k:'background_name', l:'背景', p:'英雄', t:'text'}
            ]" :key="f.k" class="flex flex-col gap-1.5 px-2">
              <label class="text-[9px] font-black text-zinc-500 uppercase tracking-widest">{{ f.l }}</label>
              <input 
                :type="f.t"
                :value="sheet.bio[f.k]"
                @input="e => {
                  const val = f.t === 'number' ? (parseInt((e.target as HTMLInputElement).value) || 0) : (e.target as HTMLInputElement).value;
                  updateBio({ ...sheet.bio, [f.k]: val });
                }"
                class="bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-sm text-zinc-200 outline-none focus:border-blue-500 transition-all"
                :placeholder="f.p"
              />
            </div>
          </div>

          <!-- 语言与工具熟练项 (恢复项) -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 border-t border-zinc-800/50 pt-6">
            <div class="flex flex-col gap-2 px-2">
              <div class="flex items-center gap-2 mb-1">
                <Languages class="w-3 h-3 text-zinc-500" />
                <label class="text-[9px] font-black text-zinc-500 uppercase tracking-widest">掌握语言</label>
              </div>
              <input 
                :value="sheet.bio.languages?.join('，')"
                @change="e => updateBioList('languages', (e.target as HTMLInputElement).value)"
                class="bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-zinc-300 outline-none focus:border-blue-500 transition-all"
                placeholder="通用语，精灵语..."
              />
            </div>
            <div class="flex flex-col gap-2 px-2">
              <div class="flex items-center gap-2 mb-1">
                <Wrench class="w-3 h-3 text-zinc-500" />
                <label class="text-[9px] font-black text-zinc-500 uppercase tracking-widest">工具熟练</label>
              </div>
              <input 
                :value="sheet.bio.tool_proficiencies?.join('，')"
                @change="e => updateBioList('tool_proficiencies', (e.target as HTMLInputElement).value)"
                class="bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-zinc-300 outline-none focus:border-blue-500 transition-all"
                placeholder="盗贼工具，笛子..."
              />
            </div>
          </div>
        </div>

        <!-- 职业等级 -->
        <ClassManager :prog="sheet.prog" @update:prog="v => updateVal('prog', v)" />

        <!-- 背景故事 -->
        <div class="bg-zinc-900/50 border border-zinc-800 rounded-3xl p-6">
          <div class="flex items-center gap-3 mb-6 px-2">
            <div class="bg-zinc-800 p-2 rounded-xl"><ScrollText class="w-5 h-5 text-amber-400" /></div>
            <h3 class="text-lg font-black text-white uppercase tracking-tighter">背景故事</h3>
          </div>
          <textarea 
            :value="sheet.bio.backstory"
            @input="e => updateBio({ ...sheet.bio, backstory: (e.target as HTMLTextAreaElement).value })"
            rows="12"
            class="w-full bg-zinc-950 border border-zinc-800 rounded-2xl p-6 text-sm text-zinc-400 outline-none focus:border-amber-500 leading-relaxed transition-all resize-none"
            placeholder="在此书写角色的过往经历..."
          ></textarea>
        </div>
      </div>

      <!-- 右侧：性格 -->
      <div class="space-y-6">
        <div class="bg-zinc-900/50 border border-zinc-800 rounded-3xl p-6">
          <div class="flex items-center gap-3 mb-6 px-2">
            <div class="bg-zinc-800 p-2 rounded-xl"><Heart class="w-5 h-5 text-red-400" /></div>
            <h3 class="text-lg font-black text-white uppercase tracking-tighter">性格特征</h3>
          </div>
          <div class="space-y-6">
            <div v-for="f in [
              {k:'traits', l:'个性特点'}, {k:'ideals', l:'理想信念'},
              {k:'bonds', l:'核心羁绊'}, {k:'flaws', l:'缺点瑕疵'}
            ]" :key="f.k" class="flex flex-col gap-2">
              <label class="text-[9px] font-black text-zinc-500 uppercase tracking-widest px-1">{{ f.l }}</label>
              <textarea 
                :value="sheet.bio.personality[f.k]"
                @input="e => updatePersonality(f.k, (e.target as HTMLTextAreaElement).value)"
                rows="3"
                class="w-full bg-zinc-950 border border-zinc-800 rounded-xl p-3 text-xs text-zinc-400 outline-none focus:border-red-500/50 transition-all resize-none"
              ></textarea>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>