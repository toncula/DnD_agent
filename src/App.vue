<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ChevronLeft, ChevronRight, MessageSquare, PanelsTopLeft, RefreshCw } from 'lucide-vue-next';
import Sidebar from './components/Sidebar.vue';
import ChatWindow from './components/ChatWindow.vue';
import CharacterSheet from './components/CharacterSheet.vue';
import api from './api';
import type { BookNode, ChatMessage, ToolLog } from './types';

const bookNodes = ref<BookNode[]>([]);
const selectedBooks = ref<string[]>([]);
const messages = ref<(ChatMessage & { logs?: ToolLog[] })[]>([]);
const isLoading = ref(false);
const characterData = ref<any>(null);
const isChatOpen = ref(true);
const isSidebarOpen = ref(true);

onMounted(async () => {
  try {
    const books = await api.getBooks();
    bookNodes.value = books.nodes;
    
    // 自动勾选核心规则，战役设定和规则扩展
    const targetCategories = ['核心规则', '战役设定', '规则扩展'];
    const autoSelected = new Set<string>();
    
    const collectValues = (nodes: BookNode[]) => {
      nodes.forEach(node => {
        autoSelected.add(node.value);
        if (node.children) {
          collectValues(node.children);
        }
      });
    };
    
    books.nodes.forEach(node => {
      if (targetCategories.includes(node.label)) {
        autoSelected.add(node.value);
        if (node.children) {
          collectValues(node.children);
        }
      }
    });
    selectedBooks.value = Array.from(autoSelected);

    const char = await api.getCharacter();
    characterData.value = char;
  } catch (error) {
    console.error('Initial load failed:', error);
  }
});

const saveCharacter = async (newData: any) => {
  try {
    const updated = await api.updateCharacter(newData);
    // 直接赋值触发全量更新，虽然会有轻微刷新感，但绝对不会崩
    characterData.value = updated;
  } catch (error) {
    console.error('Save failed:', error);
  }
};

async function handleSendMessage(content: string) {
  if (selectedBooks.value.length === 0) {
    messages.value.push({ role: 'assistant', content: '发送失败：请先在左侧选择至少一本规则书。', logs: [] });
    return;
  }

  messages.value.push({ role: 'user', content });
  isLoading.value = true;
  try {
    const response = await api.sendChat({
      messages: messages.value.map(({ role, content }) => ({ role, content })),
      selected_books: selectedBooks.value,
      character_data: characterData.value
    });
    messages.value.push({ role: 'assistant', content: response.response, logs: response.logs });
  } catch (error) {
    messages.value.push({ role: 'assistant', content: '连接助手失败。', logs: [] });
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="flex h-screen w-full bg-[#121212] text-zinc-100 overflow-hidden font-sans">
    <aside 
      class="flex-shrink-0 flex flex-col border-r border-white/5 bg-[#18181b] transition-all duration-300 relative z-30"
      :style="{ width: isSidebarOpen ? '260px' : '0px' }"
    >
      <div v-if="isSidebarOpen" class="w-[260px] h-full flex flex-col">
        <Sidebar :nodes="bookNodes" v-model:selected-paths="selectedBooks" />
      </div>
      <button @click="isSidebarOpen = !isSidebarOpen" class="absolute -right-4 top-1/2 -translate-y-1/2 w-8 h-8 bg-[#18181b] border border-white/10 rounded-full flex items-center justify-center text-zinc-400 hover:text-white z-40 shadow-xl">
        <ChevronLeft v-if="isSidebarOpen" class="w-4 h-4" />
        <ChevronRight v-else class="w-4 h-4" />
      </button>
    </aside>

    <main class="flex-1 flex flex-col relative overflow-y-auto bg-[#121212]">
      <div class="p-6 max-w-4xl mx-auto w-full">
        <header class="mb-6 flex justify-between items-start">
          <div class="flex flex-col gap-1">
            <h1 class="text-4xl font-black text-white tracking-tighter flex items-center gap-3">
              <span class="text-red-600">D&D</span> 5E 角色面板
            </h1>
            <p class="text-xs text-zinc-500 font-bold uppercase tracking-[0.3em]">Adventure Engine</p>
          </div>
          <div class="flex gap-3">
             <button @click="isSidebarOpen = !isSidebarOpen" class="p-2.5 rounded-xl border border-white/10 text-zinc-400 hover:bg-zinc-800">
              <PanelsTopLeft class="w-5 h-5" />
            </button>
            <button @click="isChatOpen = !isChatOpen" class="flex items-center gap-2 px-5 py-2.5 rounded-xl border border-white/10 font-bold text-sm bg-zinc-800 hover:bg-zinc-700">
              <MessageSquare class="w-4 h-4" />
              {{ isChatOpen ? '隐藏助手' : '召唤助手' }}
            </button>
          </div>
        </header>
        
        <CharacterSheet 
          v-if="characterData" 
          :key="characterData.character_name"
          :initial-data="characterData" 
          @update="saveCharacter"
        />
        <div v-else class="flex flex-col justify-center items-center h-96 gap-4">
          <RefreshCw class="w-10 h-10 text-red-600 animate-spin opacity-20" />
          <p class="text-zinc-600 italic">正在读取角色卷轴...</p>
        </div>
      </div>
    </main>

    <aside v-show="isChatOpen" class="w-[420px] flex-shrink-0 flex flex-col border-l border-white/5 bg-[#18181b] z-20 shadow-2xl">
      <div class="p-5 border-b border-white/5 flex justify-between items-center bg-zinc-900/50">
        <span class="font-black text-sm uppercase tracking-widest">DM 规则顾问</span>
        <button @click="isChatOpen = false" class="text-zinc-500 hover:text-white">✕</button>
      </div>
      <ChatWindow :messages="messages" :is-loading="isLoading" @send-message="handleSendMessage" />
    </aside>
  </div>
</template>
