<script setup lang="ts">
import { ref, computed } from 'vue';
import { Plus, Search, ChevronRight, ChevronDown } from 'lucide-vue-next';
import SpellSlotTracker from '../SpellSlotTracker.vue';
import SpellItem from '../SpellItem.vue';

const props = defineProps<{ sheet: any }>();
const emit = defineEmits(['update']);

const handleSheetUpdate = (partial: any) => {
  emit('update', partial);
};

const searchQuery = ref('');
const filterLevel = ref<number | 'all'>(-1);
const expandedLevels = ref<Record<string, boolean>>({ '0': true, '1': true });
const editingIdx = ref<number | null>(null);

const filteredSpells = computed(() => {
  return (props.sheet.spells || []).filter((s: any) => {
    const nameMatch = s.name.toLowerCase().includes(searchQuery.value.toLowerCase());
    const levelMatch = filterLevel.value === -1 || s.level === filterLevel.value;
    return nameMatch && levelMatch;
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

const updateSpells = () => {
  emit('update', { spells: [...props.sheet.spells] });
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
  emit('update', { spells: newSpells });
  // 展开对应层级
  expandedLevels.value[level] = true;
};

const removeSpell = (spell: any) => {
  const idx = props.sheet.spells.indexOf(spell);
  if (idx > -1) {
    const newSpells = [...props.sheet.spells];
    newSpells.splice(idx, 1);
    emit('update', { spells: newSpells });
  }
};

const toggleLevel = (lv: number) => {
  expandedLevels.value[lv] = !expandedLevels.value[lv];
};
</script>

<template>
  <div class="flex flex-col gap-6 pb-24">
    <!-- 法术位追踪器 -->
    <SpellSlotTracker :sheet="sheet" @update:sheet="handleSheetUpdate" />

    <!-- 工具栏 -->
    <div class="flex flex-wrap items-center justify-between gap-4 bg-zinc-900/80 p-4 rounded-2xl border border-zinc-800 sticky top-0 z-10 backdrop-blur-md">
      <div class="flex items-center gap-4 flex-1 min-w-[300px]">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input 
            v-model="searchQuery" 
            placeholder="搜索法术..." 
            class="w-full bg-zinc-950 border border-zinc-700 rounded-xl pl-10 pr-4 py-2 text-sm text-zinc-200 outline-none focus:border-blue-500" 
          />
        </div>
        <select v-model="filterLevel" class="bg-zinc-950 border border-zinc-700 rounded-xl px-4 py-2 text-xs font-bold text-zinc-400 outline-none">
          <option :value="-1">全部环阶</option>
          <option :value="0">戏法</option>
          <option v-for="lv in 9" :key="lv" :value="lv">{{ lv }} 环</option>
        </select>
      </div>
      <button @click="addSpell(1)" class="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2 rounded-xl text-xs font-black flex items-center gap-2 transition-all shadow-lg shadow-blue-900/20">
        <Plus class="w-4 h-4" /> 研习新法术
      </button>
    </div>

    <!-- 法术列表 -->
    <div class="space-y-3">
      <div v-for="lv in 10" :key="lv-1" class="space-y-1">
        <template v-if="spellsByLevel[lv-1] || (filterLevel === -1 || filterLevel === (lv-1))">
          <!-- 层级标题 -->
          <div 
            @click="toggleLevel(lv-1)" 
            class="flex items-center justify-between bg-zinc-900/40 hover:bg-zinc-800/40 p-3 rounded-xl cursor-pointer transition-colors border border-transparent hover:border-zinc-700 group"
          >
            <div class="flex items-center gap-3">
              <component :is="expandedLevels[lv-1] ? ChevronDown : ChevronRight" class="w-4 h-4 text-zinc-600" />
              <span class="text-[10px] font-black text-zinc-500 uppercase tracking-widest">{{ lv === 1 ? '戏法' : (lv-1) + ' 环' }}</span>
              <span v-if="(spellsByLevel[lv-1] || []).length > 0" class="bg-zinc-800 text-[9px] font-black text-zinc-600 px-2 py-0.5 rounded-full">
                {{ (spellsByLevel[lv-1] || []).length }}
              </span>
            </div>
            <button 
              @click.stop="addSpell(lv-1)" 
              class="text-[9px] font-black text-blue-500/50 hover:text-blue-400 uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity"
            >
              + 在此添加
            </button>
          </div>

          <!-- 该层级的法术列表 -->
          <div v-show="expandedLevels[lv-1]" class="space-y-2 mt-1 pl-4 border-l border-zinc-800/50 ml-5">
            <template v-if="(spellsByLevel[lv-1] || []).length > 0">
              <SpellItem 
                v-for="spell in spellsByLevel[lv-1]" 
                :key="spell.name + lv"
                :spell="spell"
                :is-editing="editingIdx === sheet.spells.indexOf(spell)"
                @update="updateSpells"
                @remove="removeSpell(spell)"
                @toggle-edit="editingIdx = (editingIdx === sheet.spells.indexOf(spell) ? null : sheet.spells.indexOf(spell))"
              />
            </template>
            <div v-else class="py-2 text-[10px] text-zinc-700 italic pl-4">暂无此环阶法术</div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
