<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Sidebar from './components/Sidebar.vue';
import ChatWindow from './components/ChatWindow.vue';
import api from './api';
import type { BookNode, ChatMessage, ToolLog } from './types';

// State
const bookNodes = ref<BookNode[]>([]);
const selectedBooks = ref<string[]>([]);
const messages = ref<(ChatMessage & { logs?: ToolLog[] })[]>([]);
const isLoading = ref(false);
const threadId = ref('default_thread'); // In a real app, generate UUID

// Fetch books on mount
onMounted(async () => {
  try {
    const data = await api.getBooks();
    bookNodes.value = data.nodes;
    // Optionally pre-select some books if needed
    // selectedBooks.value = data.valid_paths;
  } catch (error) {
    console.error('Failed to load books:', error);
    // Could show a toast notification here
  }
});

// Handle sending messages
async function handleSendMessage(content: string) {
  // Add user message immediately
  messages.value.push({ role: 'user', content });
  isLoading.value = true;

  try {
    // Call API
    const response = await api.sendChat({
      messages: messages.value.map(({ role, content }) => ({ role, content })), // Send clean messages
      selected_books: selectedBooks.value,
      thread_id: threadId.value
    });

    // Add assistant response
    messages.value.push({
      role: 'assistant',
      content: response.response,
      logs: response.logs
    });
  } catch (error) {
    console.error('Chat error:', error);
    messages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error processing your request. Please check your connection and try again.',
      logs: []
    });
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="flex h-screen w-full bg-[#343541] text-zinc-100 overflow-hidden font-sans">
    <!-- Sidebar -->
    <aside class="w-[260px] flex-shrink-0 hidden md:flex flex-col z-20">
      <Sidebar 
        :nodes="bookNodes" 
        v-model:selected-paths="selectedBooks" 
      />
    </aside>

    <!-- Main Chat Area -->
    <main class="flex-1 flex flex-col relative min-w-0">
      <ChatWindow 
        :messages="messages" 
        :is-loading="isLoading"
        @send-message="handleSendMessage"
      />
    </main>
  </div>
</template>
