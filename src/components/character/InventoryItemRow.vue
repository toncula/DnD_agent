<script setup lang="ts">
import { ref } from 'vue';
import { Trash2, Shield, Sword, Package, Settings2, ChevronDown, ChevronUp } from 'lucide-vue-next';
import type { InventoryItem } from '../../types';

const props = defineProps<{
  item: InventoryItem;
}>();

const emit = defineEmits(['update', 'remove', 'equip', 'hover-item']);

const isExpanded = ref(false);

const categories = ['装备', '消耗品', '杂物'];
const itemTypes = ['武器', '护甲', '盾牌', '饰品', '奇物'];
const slotTypes = ['头部', '躯干', '腿部', '足部', '主手', '副手', '双手', '手套', '披风', '腰带', '戒指 I', '戒指 II', '项链', '乐器'];
const rarities = ['普通', '精良', '稀有', '极稀有', '传说', '神器'];

const updateItem = () => {
  emit('update');
};

const toggleEquip = () => {
  emit('equip', props.item);
};

const addAction = () => {
  if (!props.item.special_actions) props.item.special_actions = [];
  props.item.special_actions.push({ name: '新技能', activation: '1动作', description: '' });
  updateItem();
};

const removeAction = (idx: number) => {
  props.item.special_actions?.splice(idx, 1);
  updateItem();
};
</script>

<template>
  <div 
    class="bg-zinc-900/50 rounded-xl border border-zinc-800 transition-all overflow-hidden"
    :class="{ 'border-zinc-600 ring-1 ring-zinc-700': isExpanded }"
    @mouseenter="e => emit('hover-item', item, e)"
    @mouseleave="emit('hover-item', null)"
  >
    <!-- 主行 -->
    <div class="flex items-center gap-3 p-3">
      <input 
        type="number" 
        v-model="item.quantity" 
        @change="updateItem" 
        class="w-10 bg-zinc-800 rounded px-1 py-1 text-center text-xs font-bold text-zinc-300 outline-none" 
      />
      
      <div class="flex-1 min-w-0 flex items-center gap-2">
        <div v-if="item.is_equipped" class="bg-blue-600 text-[8px] font-black px-1 rounded text-white shrink-0">E</div>
        <input 
          v-model="item.name" 
          @change="updateItem" 
          class="bg-transparent font-medium text-zinc-100 outline-none flex-1 truncate text-sm" 
          placeholder="物品名称"
        />
      </div>

      <!-- 重量快速编辑 -->
      <div class="flex items-center gap-1 shrink-0 bg-black/20 px-2 py-1 rounded-lg border border-white/5">
        <input 
          type="number" 
          step="0.1"
          v-model="item.weight" 
          @change="updateItem" 
          class="w-10 bg-transparent text-right text-[10px] font-bold text-zinc-400 outline-none" 
        />
        <span class="text-[8px] font-black text-zinc-600 uppercase">磅</span>
      </div>

      <!-- 派生数值展示 -->
      <div v-if="item.is_equipped && item.item_type === '武器'" class="flex gap-2 text-[10px] font-black">
        <span class="text-blue-400">{{ item.derived_attack_roll }}</span>
        <span class="text-amber-400">{{ item.derived_damage_roll }}</span>
      </div>

      <div class="flex items-center gap-2 shrink-0">
        <button 
          v-if="item.category === '装备'"
          @click="toggleEquip"
          class="px-2 py-1 text-[10px] font-black rounded border transition-all"
          :class="item.is_equipped ? 'bg-amber-600/20 text-amber-400 border-amber-500/50' : 'bg-blue-600/20 text-blue-400 border-blue-500/50'"
        >
          {{ item.is_equipped ? '卸下' : '装备' }}
        </button>

        <button 
          @click="isExpanded = !isExpanded" 
          class="p-1.5 text-zinc-500 hover:text-zinc-200 transition-colors"
        >
          <component :is="isExpanded ? ChevronUp : Settings2" class="w-4 h-4" />
        </button>

        <button @click="emit('remove')" class="p-1.5 text-zinc-600 hover:text-red-500 transition-colors">
          <Trash2 class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- 展开详情编辑区 -->
    <div v-if="isExpanded" class="px-4 pb-4 pt-2 border-t border-zinc-800 bg-black/20 space-y-4 animate-in slide-in-from-top-2 duration-200">
      <div class="grid grid-cols-3 gap-3">
        <div class="flex flex-col gap-1">
          <label class="text-[9px] font-black text-zinc-500 uppercase">类别</label>
          <select v-model="item.category" @change="updateItem" class="bg-zinc-800 text-xs text-zinc-300 rounded px-2 py-1.5 outline-none border border-zinc-700">
            <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>

        <div v-if="item.category === '装备'" class="flex flex-col gap-1">
          <label class="text-[9px] font-black text-zinc-500 uppercase">子类</label>
          <select v-model="item.item_type" @change="updateItem" class="bg-zinc-800 text-xs text-amber-500 rounded px-2 py-1.5 outline-none border border-zinc-700">
            <option v-for="t in itemTypes" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>

        <div v-if="item.category === '装备'" class="flex flex-col gap-1">
          <label class="text-[9px] font-black text-zinc-500 uppercase">槽位</label>
          <select v-model="item.slot_type" @change="updateItem" class="bg-zinc-800 text-xs text-blue-400 rounded px-2 py-1.5 outline-none border border-zinc-700">
            <option v-for="s in slotTypes" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
      </div>

      <div class="grid grid-cols-4 gap-3">
         <div class="flex flex-col gap-1">
          <label class="text-[9px] font-black text-zinc-500 uppercase">重量</label>
          <input type="number" step="0.1" v-model="item.weight" @change="updateItem" class="bg-zinc-800 text-xs rounded px-2 py-1.5 outline-none border border-zinc-700" />
        </div>
        <div v-if="item.category === '装备'" class="flex flex-col gap-1">
          <label class="text-[9px] font-black text-zinc-500 uppercase">稀有度</label>
          <select v-model="item.rarity" @change="updateItem" class="bg-zinc-800 text-xs rounded px-2 py-1.5 outline-none border border-zinc-700">
            <option v-for="r in rarities" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
        <div v-if="item.category === '装备'" class="flex items-center gap-2 h-full pt-4">
           <input type="checkbox" v-model="item.is_proficient" @change="updateItem" class="rounded border-zinc-700 bg-zinc-800 text-blue-600" />
           <label class="text-[9px] font-black text-zinc-400 uppercase">熟练</label>
        </div>
        <div v-if="item.category === '装备'" class="flex items-center gap-2 h-full pt-4">
           <input type="checkbox" v-model="item.requires_attunement" @change="updateItem" class="rounded border-zinc-700 bg-zinc-800 text-blue-600" />
           <label class="text-[9px] font-black text-zinc-400 uppercase">同调</label>
        </div>
      </div>

      <!-- 武器/护甲特定字段 -->
      <div v-if="item.item_type === '武器'" class="p-3 bg-blue-900/10 rounded-lg border border-blue-500/20 space-y-3">
         <div class="grid grid-cols-4 gap-3">
            <div class="flex flex-col gap-1">
               <label class="text-[9px] font-black text-blue-400 uppercase">伤害骰</label>
               <input v-model="item.damage_dice" @change="updateItem" placeholder="1d8" class="bg-zinc-950 text-xs rounded px-2 py-1 border border-zinc-800" />
            </div>
            <div class="flex flex-col gap-1">
               <label class="text-[9px] font-black text-blue-400 uppercase">类型</label>
               <input v-model="item.damage_type" @change="updateItem" placeholder="挥砍" class="bg-zinc-950 text-xs rounded px-2 py-1 border border-zinc-800" />
            </div>
            <div class="flex flex-col gap-1">
               <label class="text-[9px] font-black text-blue-400 uppercase">武器专精</label>
               <input v-model="item.weapon_mastery" @change="updateItem" placeholder="Topple" class="bg-zinc-950 text-xs rounded px-2 py-1 border border-zinc-800" />
            </div>
            <div class="flex flex-col gap-1 text-[9px] font-black text-blue-400">
               <label class="uppercase">加值(攻/伤)</label>
               <div class="flex gap-1">
                  <input type="number" v-model="item.attack_bonus" @change="updateItem" class="w-full bg-zinc-950 text-xs rounded px-1 py-1 border border-zinc-800 text-center" />
                  <input type="number" v-model="item.damage_bonus" @change="updateItem" class="w-full bg-zinc-950 text-xs rounded px-1 py-1 border border-zinc-800 text-center" />
               </div>
            </div>
         </div>

         <!-- 特殊动作编辑 -->
         <div class="space-y-2">
            <div class="flex justify-between items-center">
               <label class="text-[9px] font-black text-blue-400 uppercase">特殊动作/技能</label>
               <button @click="addAction" class="text-[8px] bg-blue-600/20 text-blue-400 px-1.5 py-0.5 rounded border border-blue-500/30 hover:bg-blue-600/40 transition-all">+ 添加</button>
            </div>
            <div v-for="(action, idx) in item.special_actions" :key="idx" class="bg-black/30 p-2 rounded border border-zinc-800 space-y-2 relative group/action">
               <button @click="removeAction(idx)" class="absolute top-1 right-1 opacity-0 group-hover/action:opacity-100 text-zinc-600 hover:text-red-500 transition-all">
                  <Trash2 class="w-3 h-3" />
               </button>
               <div class="flex gap-2">
                  <input v-model="action.name" @change="updateItem" placeholder="技能名" class="bg-zinc-900 text-[10px] font-bold rounded px-1.5 py-1 border border-zinc-800 w-1/3" />
                  <input v-model="action.activation" @change="updateItem" placeholder="消耗" class="bg-zinc-900 text-[10px] rounded px-1.5 py-1 border border-zinc-800 w-1/4 text-zinc-500" />
               </div>
               <textarea v-model="action.description" @change="updateItem" rows="1" placeholder="效果描述..." class="w-full bg-zinc-900 text-[10px] rounded px-1.5 py-1 border border-zinc-800 text-zinc-400"></textarea>
            </div>
         </div>
      </div>

      <div v-if="item.item_type === '护甲'" class="p-3 bg-emerald-900/10 rounded-lg border border-emerald-500/20 grid grid-cols-4 gap-3">
         <div class="flex flex-col gap-1">
            <label class="text-[9px] font-black text-emerald-400 uppercase">基础 AC</label>
            <input type="number" v-model="item.ac_base" @change="updateItem" placeholder="11" class="bg-zinc-950 text-xs rounded px-2 py-1 border border-zinc-800" />
         </div>
         <div class="flex flex-col gap-1">
            <label class="text-[9px] font-black text-emerald-400 uppercase">敏捷上限</label>
            <input type="number" v-model="item.dex_cap" @change="updateItem" placeholder="无" class="bg-zinc-950 text-xs rounded px-2 py-1 border border-zinc-800" />
         </div>
         <div class="flex flex-col gap-1">
            <label class="text-[9px] font-black text-emerald-400 uppercase">力量要求</label>
            <input type="number" v-model="item.strength_req" @change="updateItem" class="bg-zinc-950 text-xs rounded px-2 py-1 border border-zinc-800" />
         </div>
         <div class="flex items-center gap-2 pt-4">
            <input type="checkbox" v-model="item.stealth_disadv" @change="updateItem" class="rounded border-zinc-700 bg-zinc-800 text-emerald-600" />
            <label class="text-[9px] font-black text-emerald-400 uppercase">潜行劣势</label>
         </div>
      </div>

      <div v-if="item.item_type === '盾牌'" class="p-3 bg-emerald-900/10 rounded-lg border border-emerald-500/20">
         <div class="flex flex-col gap-1 w-24">
            <label class="text-[9px] font-black text-emerald-400 uppercase">AC 加成</label>
            <input type="number" v-model="item.ac_bonus" @change="updateItem" placeholder="2" class="bg-zinc-950 text-xs rounded px-2 py-1 border border-zinc-800" />
         </div>
      </div>

      <div class="flex flex-col gap-1">
        <label class="text-[9px] font-black text-zinc-500 uppercase">物品描述</label>
        <textarea v-model="item.description" @change="updateItem" rows="3" class="bg-zinc-800 text-xs text-zinc-400 rounded p-2 outline-none border border-zinc-700 italic"></textarea>
      </div>
    </div>
  </div>
</template>