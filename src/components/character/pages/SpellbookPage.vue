<script setup lang="ts">
import { ref, computed } from 'vue';
import { Plus, Trash2, Search, ChevronRight, ChevronDown, BookOpen, Clock, Zap, MapPin } from 'lucide-vue-next';

const props = defineProps<{ sheet: any }>();
const emit = defineEmits(['update']);

const searchQuery = ref('');
const filterLevel = ref<number | 'all'>(-1);
const expandedLevels = ref<Record<string, boolean>>({ '0': true, '1': true });
const editingIdx = ref<number | null>(null); // 当前正在展开编辑的法术索引

const filteredSpells = computed(() => {
  return (props.sheet.spells || []).filter((s: any) => {
    const matchesSearch = s.name.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesLevel = filterLevel.value === -1 || s.level === filterLevel.value;
    return matchesSearch && matchesLevel;
  });
});

const spellsByLevel = computed(() => {
  const groups: Record<number, any[]> = {};
  filteredSpells.value.forEach(s => {
    if (!groups[s.level]) groups[s.level] = [];
    groups[s.level].push(s);
  });
  return groups;
});

const updateSpells = (newSpells: any[]) => {
  emit('update', { spells: newSpells });
};

const addSpell = (level: number = 1) => {
  const newSpells = [...(props.sheet.spells || []), { 
    name: '新法术', 
    level: level, 
    school: '塑能系',
    casting_time: '1动作', 
    range: '60尺',
    components: 'V, S',
    materials: '',
    duration: '即时',
    description: '法术说明...', 
    is_prepared: false 
  }];
  updateSpells(newSpells);
};

const removeSpell = (idx: number) => {
  const newSpells = [...props.sheet.spells];
  newSpells.splice(idx, 1);
  updateSpells(newSpells);
};

const toggleLevel = (lv: number) => {
  expandedLevels.value[lv] = !expandedLevels.value[lv];
};
</script>

<template>
  <div class="flex flex-col gap-6 pb-24">
    <!-- 工具栏 -->
    <div class="flex flex-wrap items-center justify-between gap-4 bg-zinc-900/80 p-4 rounded-2xl border border-zinc-800 sticky top-0 z-10 backdrop-blur-md">
      <div class="flex items-center gap-4 flex-1 min-w-[300px]">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input v-model="searchQuery" placeholder="搜索法术知识库..." class="w-full bg-zinc-950 border border-zinc-700 rounded-xl pl-10 pr-4 py-2 text-sm text-zinc-200 outline-none focus:border-blue-500 transition-all" />
        </div>
        <select v-model="filterLevel" class="bg-zinc-950 border border-zinc-700 rounded-xl px-4 py-2 text-xs font-bold text-zinc-400 outline-none focus:border-blue-500">
          <option :value="-1">全部环阶</option>
          <option :value="0">戏法</option>
          <option v-for="lv in 9" :key="lv" :value="lv">{{ lv }} 环</option>
        </select>
      </div>
      <button @click="addSpell(1)" class="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2 rounded-xl text-xs font-black flex items-center gap-2 transition-all">+ 研习新法术</button>
    </div>

    <!-- 分组列表 -->
    <div class="space-y-3">
      <div v-for="lv in 10" :key="lv-1" class="space-y-1">
        <template v-if="spellsByLevel[lv-1] || filterLevel === (lv-1)">
          <div @click="toggleLevel(lv-1)" class="flex items-center justify-between bg-zinc-900/40 hover:bg-zinc-800/40 p-3 rounded-xl cursor-pointer transition-colors border border-transparent hover:border-zinc-700 group">
            <div class="flex items-center gap-3">
              <component :is="expandedLevels[lv-1] ? ChevronDown : ChevronRight" class="w-4 h-4 text-zinc-600" />
              <span class="text-[10px] font-black text-zinc-500 uppercase tracking-widest">{{ lv === 1 ? '戏法 (Cantrips)' : (lv-1) + ' 环 (Level ' + (lv-1) + ')' }}</span>
              <span class="bg-zinc-800 text-[9px] font-black text-zinc-600 px-2 py-0.5 rounded-full">{{ (spellsByLevel[lv-1] || []).length }}</span>
            </div>
            <button @click.stop="addSpell(lv-1)" class="text-[9px] font-black text-blue-500/50 hover:text-blue-400 uppercase tracking-widest opacity-0 group-hover:opacity-100">+ 在此环阶添加</button>
          </div>

          <div v-show="expandedLevels[lv-1]" class="space-y-2 mt-1 pl-4 border-l border-zinc-800/50 ml-5">
            <div v-for="(spell, i) in (spellsByLevel[lv-1] || [])" :key="i" class="flex flex-col bg-zinc-900/20 rounded-xl border border-zinc-800/50 overflow-hidden">
              <!-- 精简行 -->
              <div @click="editingIdx = editingIdx === i ? null : i" class="flex items-center gap-4 p-2 pr-4 cursor-pointer hover:bg-zinc-800/30 transition-colors group">
                <input v-model="spell.name" @click.stop @change="updateSpells(sheet.spells)" class="bg-transparent text-sm font-bold text-zinc-200 outline-none focus:text-blue-400 min-w-[180px]" />
                <span class="text-[9px] font-black text-zinc-600 uppercase px-2 py-0.5 bg-zinc-950 rounded border border-zinc-800">{{ spell.school }}</span>
                <div class="flex-1 flex items-center gap-4 text-[10px] text-zinc-500 overflow-hidden">
                  <span class="flex items-center gap-1 shrink-0"><Clock class="w-3 h-3" /> {{ spell.casting_time }}</span>
                  <span class="flex items-center gap-1 shrink-0"><MapPin class="w-3 h-3" /> {{ spell.range }}</span>
                  <span class="truncate italic opacity-60">{{ spell.description }}</span>
                </div>
                <button @click.stop="removeSpell(sheet.spells.indexOf(spell))" class="p-1 text-zinc-800 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all"><Trash2 class="w-3.5 h-3.5" /></button>
              </div>

              <!-- 展开编辑区 (标准化字段) -->
              <div v-if="editingIdx === i" class="p-4 bg-zinc-950/30 border-t border-zinc-800 grid grid-cols-1 md:grid-cols-3 gap-4 animate-in slide-in-from-top-1 duration-200">
                <div class="flex flex-col gap-1">
                  <label class="text-[8px] font-black text-zinc-600 uppercase">法术系别 (School)</label>
                  <select v-model="spell.school" @change="updateSpells(sheet.spells)" class="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 outline-none">
                    <option v-for="s in ['防护系', '咒法系', '预言系', '惑控系', '塑能系', '幻术系', '死灵系', '变化系']" :key="s" :value="s">{{ s }}</option>
                  </select>
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-[8px] font-black text-zinc-600 uppercase">施法时间 (Casting Time)</label>
                  <input v-model="spell.casting_time" @change="updateSpells(sheet.spells)" class="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 outline-none" />
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-[8px] font-black text-zinc-600 uppercase">施法距离 (Range)</label>
                  <input v-model="spell.range" @change="updateSpells(sheet.spells)" class="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 outline-none" />
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-[8px] font-black text-zinc-600 uppercase">法术成分 (Components)</label>
                  <input v-model="spell.components" @change="updateSpells(sheet.spells)" class="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 outline-none" placeholder="V, S, M" />
                </div>
                <div class="flex flex-col gap-1 md:col-span-2">
                  <label class="text-[8px] font-black text-zinc-600 uppercase">法术材料 (Materials)</label>
                  <input v-model="spell.materials" @change="updateSpells(sheet.spells)" class="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 outline-none" placeholder="如果法术需要消耗材料，请在此注明..." />
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-[8px] font-black text-zinc-600 uppercase">持续时间 (Duration)</label>
                  <input v-model="spell.duration" @change="updateSpells(sheet.spells)" class="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 outline-none" />
                </div>
                <div class="flex flex-col gap-1 md:col-span-3">
                  <label class="text-[8px] font-black text-zinc-600 uppercase">详细说明 (Description)</label>
                  <textarea v-model="spell.description" @change="updateSpells(sheet.spells)" rows="4" class="bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-xs text-zinc-400 outline-none leading-relaxed resize-none"></textarea>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
select { appearance: none; -webkit-appearance: none; }
</style>