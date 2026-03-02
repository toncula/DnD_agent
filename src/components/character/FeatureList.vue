<script setup lang="ts">
import { ref, computed } from 'vue';
import { Plus, Trash2, ChevronRight, ChevronDown, Shield, Zap, Star, Sparkles } from 'lucide-vue-next';

const props = defineProps<{
  features: any[];
}>();

const emit = defineEmits(['update']);

const categories = [
  { id: '职业能力', icon: Shield, color: 'text-blue-400' },
  { id: '种族特性', icon: Zap, color: 'text-emerald-400' },
  { id: '专长', icon: Star, color: 'text-amber-400' },
  { id: '其他能力', icon: Sparkles, color: 'text-purple-400' }
];

const expandedCats = ref<Record<string, boolean>>({
  '职业能力': true,
  '种族特性': true,
  '专长': true,
  '其他能力': true
});

const editingIdx = ref<number | null>(null);

const featuresByCat = computed(() => {
  const groups: Record<string, any[]> = {
    '职业能力': [], '种族特性': [], '专长': [], '其他能力': []
  };
  (props.features || []).forEach(f => {
    const cat = f.source || '其他能力';
    if (groups[cat]) groups[cat].push(f);
    else groups['其他能力'].push(f);
  });
  return groups;
});

const updateFeatures = (newList: any[]) => {
  emit('update', newList);
};

const addFeature = (cat: string) => {
  const newFeatures = [...(props.features || []), { 
    name: '新特性', 
    source: cat, 
    description: '特性效果说明...' 
  }];
  updateFeatures(newFeatures);
  editingIdx.value = newFeatures.length - 1;
};

const removeFeature = (idx: number) => {
  const newList = [...props.features];
  newList.splice(idx, 1);
  updateFeatures(newList);
};
</script>

<template>
  <div class="space-y-4 pb-10">
    <div v-for="cat in categories" :key="cat.id" class="space-y-2">
      <!-- 类别标题 -->
      <div 
        @click="expandedCats[cat.id] = !expandedCats[cat.id]"
        class="flex items-center justify-between bg-zinc-900/40 hover:bg-zinc-800/40 p-3 rounded-xl cursor-pointer transition-colors border border-transparent hover:border-zinc-700 group"
      >
        <div class="flex items-center gap-3">
          <component :is="expandedCats[cat.id] ? ChevronDown : ChevronRight" class="w-4 h-4 text-zinc-600" />
          <component :is="cat.icon" class="w-4 h-4" :class="cat.color" />
          <span class="text-[10px] font-black text-zinc-400 uppercase tracking-widest">{{ cat.id }}</span>
          <span class="bg-zinc-800 text-[9px] font-black text-zinc-600 px-2 py-0.5 rounded-full">{{ featuresByCat[cat.id].length }}</span>
        </div>
        <button @click.stop="addFeature(cat.id)" class="text-[9px] font-black text-blue-500/50 hover:text-blue-400 uppercase tracking-widest opacity-0 group-hover:opacity-100">+ 添加</button>
      </div>

      <!-- 特性列表 -->
      <div v-show="expandedCats[cat.id]" class="space-y-2 pl-4 border-l border-zinc-800/50 ml-5">
        <div v-for="(feat, i) in featuresByCat[cat.id]" :key="i" class="flex flex-col bg-zinc-900/20 rounded-xl border border-zinc-800/50 overflow-hidden transition-all">
          <!-- 特性行 -->
          <div 
            @click="editingIdx = editingIdx === props.features.indexOf(feat) ? null : props.features.indexOf(feat)"
            class="flex items-center justify-between p-3 cursor-pointer hover:bg-zinc-800/30 group"
          >
            <div class="flex flex-col min-w-0">
              <span class="text-sm font-bold text-zinc-200 group-hover:text-blue-400 transition-colors">{{ feat.name }}</span>
              <span v-if="editingIdx !== props.features.indexOf(feat)" class="text-[10px] text-zinc-500 truncate mt-0.5 italic pr-8 opacity-60">{{ feat.description }}</span>
            </div>
            <button @click.stop="removeFeature(props.features.indexOf(feat))" class="p-1 text-zinc-800 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all"><Trash2 class="w-3.5 h-3.5" /></button>
          </div>

          <!-- 编辑区 -->
          <div v-if="editingIdx === props.features.indexOf(feat)" class="p-4 bg-zinc-950/30 border-t border-zinc-800 space-y-4 animate-in slide-in-from-top-1 duration-200">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="flex flex-col gap-1.5">
                <label class="text-[8px] font-black text-zinc-600 uppercase">特性名称</label>
                <input v-model="feat.name" @change="updateFeatures(props.features)" class="bg-zinc-900 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-zinc-200 outline-none focus:border-blue-500" />
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="text-[8px] font-black text-zinc-600 uppercase">来源类别</label>
                <select v-model="feat.source" @change="updateFeatures(props.features)" class="bg-zinc-900 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-zinc-200 outline-none">
                  <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.id }}</option>
                </select>
              </div>
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-[8px] font-black text-zinc-600 uppercase">效果说明</label>
              <textarea v-model="feat.description" @change="updateFeatures(props.features)" rows="4" class="bg-zinc-900 border border-zinc-800 rounded-xl p-3 text-xs text-zinc-400 outline-none focus:border-blue-500 leading-relaxed resize-none"></textarea>
            </div>
          </div>
        </div>
        
        <div v-if="featuresByCat[cat.id].length === 0" class="py-2 text-[9px] text-zinc-800 italic uppercase">暂无特性</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
select { appearance: none; -webkit-appearance: none; }
</style>