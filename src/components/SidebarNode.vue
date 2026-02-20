<script setup lang="ts">
import { computed } from 'vue';
import { ChevronRight, ChevronDown, Folder, FileText } from 'lucide-vue-next';
import type { BookNode } from '../types';

const props = defineProps<{
  node: BookNode;
  selectedPaths: string[];
  level?: number;
}>();

const emit = defineEmits<{
  (e: 'toggle-select', node: BookNode): void;
}>();

const isExpanded = defineModel('expanded', { default: false });

const isSelected = computed(() => props.selectedPaths.includes(props.node.value));
const hasChildren = computed(() => props.node.children && props.node.children.length > 0);
const paddingLeft = computed(() => `${(props.level || 0) * 12 + 12}px`);

function toggleExpand() {
  if (hasChildren.value) {
    isExpanded.value = !isExpanded.value;
  }
}

function toggleSelection() {
  emit('toggle-select', props.node);
}
</script>

<template>
  <div class="select-none">
    <div 
      class="flex items-center py-1.5 pr-2 hover:bg-zinc-800 cursor-pointer transition-colors group"
      :style="{ paddingLeft }"
    >
      <!-- Expand/Collapse Icon -->
      <div 
        class="mr-1 w-4 h-4 flex items-center justify-center text-zinc-500 hover:text-zinc-300"
        @click.stop="toggleExpand"
      >
        <component 
          :is="isExpanded ? ChevronDown : ChevronRight" 
          v-if="hasChildren" 
          class="w-3.5 h-3.5"
        />
      </div>

      <!-- Checkbox -->
      <div 
        class="mr-2 flex items-center"
        @click.stop="toggleSelection"
      >
        <div 
          class="w-4 h-4 border rounded flex items-center justify-center transition-colors"
          :class="[
            isSelected 
              ? 'bg-emerald-600 border-emerald-600' 
              : 'border-zinc-600 group-hover:border-zinc-500 bg-zinc-900'
          ]"
        >
          <svg 
            v-if="isSelected" 
            class="w-3 h-3 text-white" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
          </svg>
        </div>
      </div>

      <!-- Label -->
      <div class="flex-1 flex items-center text-sm text-zinc-300 group-hover:text-zinc-100" @click="toggleExpand">
        <component 
          :is="hasChildren ? Folder : FileText" 
          class="w-4 h-4 mr-2 text-zinc-500"
        />
        <span class="truncate">{{ node.label }}</span>
      </div>
    </div>

    <!-- Children -->
    <div v-if="hasChildren && isExpanded">
      <SidebarNode
        v-for="child in node.children"
        :key="child.value"
        :node="child"
        :selected-paths="selectedPaths"
        :level="(level || 0) + 1"
        @toggle-select="(node) => emit('toggle-select', node)"
      />
    </div>
  </div>
</template>

<script lang="ts">
export default {
  name: 'SidebarNode'
}
</script>
