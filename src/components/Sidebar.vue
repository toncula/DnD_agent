<script setup lang="ts">
import { BookOpen } from 'lucide-vue-next';
import type { BookNode } from '../types';
import SidebarNode from './SidebarNode.vue';

defineProps<{
  nodes: BookNode[];
  selectedPaths: string[];
}>();

const emit = defineEmits<{
  (e: 'update:selectedPaths', paths: string[]): void;
}>();

function getAllDescendantValues(node: BookNode): string[] {
  let values = [node.value];
  if (node.children) {
    for (const child of node.children) {
      values = values.concat(getAllDescendantValues(child));
    }
  }
  return values;
}

function handleToggleSelect(node: BookNode, currentSelected: string[]) {
  const newSelected = new Set(currentSelected);
  const descendantValues = getAllDescendantValues(node);
  
  // Check if the node itself is currently selected
  const isSelected = currentSelected.includes(node.value);

  if (isSelected) {
    // Deselect node and all descendants
    descendantValues.forEach(val => newSelected.delete(val));
  } else {
    // Select node and all descendants
    descendantValues.forEach(val => newSelected.add(val));
  }
  
  emit('update:selectedPaths', Array.from(newSelected));
}
</script>

<template>
  <div class="flex flex-col h-full bg-zinc-900 border-r border-zinc-800">
    <!-- Header -->
    <div class="p-4 border-b border-zinc-800 flex items-center space-x-2">
      <div class="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center">
        <BookOpen class="w-5 h-5 text-white" />
      </div>
      <h1 class="font-bold text-zinc-100 text-lg tracking-tight">D&D Rule Agent</h1>
    </div>

    <!-- Scrollable Tree Area -->
    <div class="flex-1 overflow-y-auto py-2">
      <div v-if="nodes.length === 0" class="p-4 text-zinc-500 text-sm text-center">
        Loading rules...
      </div>
      
      <SidebarNode
        v-for="node in nodes"
        :key="node.value"
        :node="node"
        :selected-paths="selectedPaths"
        @toggle-select="(node) => handleToggleSelect(node, selectedPaths)"
      />
    </div>

    <!-- Footer / Stats -->
    <div class="p-4 border-t border-zinc-800 bg-zinc-900/50">
      <div class="text-xs text-zinc-500 flex justify-between">
        <span>Selected:</span>
        <span class="text-zinc-300 font-medium">{{ selectedPaths.length }} books</span>
      </div>
    </div>
  </div>
</template>
