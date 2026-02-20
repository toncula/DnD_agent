<script setup lang="ts">
import { ref, nextTick, watch, onMounted } from 'vue';
import MarkdownIt from 'markdown-it';
import { Send, Bot, User, Loader2, ChevronDown, ChevronRight, Terminal } from 'lucide-vue-next';
import type { ChatMessage, ToolLog } from '../types';

const props = defineProps<{
  messages: (ChatMessage & { logs?: ToolLog[] })[];
  isLoading: boolean;
}>();

const emit = defineEmits<{
  (e: 'send-message', content: string): void;
}>();

const userInput = ref('');
const messagesContainer = ref<HTMLElement | null>(null);
const textareaRef = ref<HTMLTextAreaElement | null>(null);

// Initialize Markdown parser
const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
});

// Auto-scroll to bottom when messages change
watch(() => props.messages.length, () => {
  scrollToBottom();
});

// Also scroll when loading state changes (e.g. when thinking starts)
watch(() => props.isLoading, () => {
  scrollToBottom();
});

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
}

function handleSend() {
  const content = userInput.value.trim();
  if (!content || props.isLoading) return;
  
  emit('send-message', content);
  userInput.value = '';
  
  // Reset textarea height
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
}

// Auto-resize textarea
function adjustHeight() {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
    textareaRef.value.style.height = `${Math.min(textareaRef.value.scrollHeight, 200)}px`;
  }
}

// Log collapse state
const logsExpanded = ref<Record<number, boolean>>({});

function toggleLogs(index: number) {
  logsExpanded.value[index] = !logsExpanded.value[index];
}
</script>

<template>
  <div class="flex flex-col h-full bg-[#343541] relative">
    <!-- Messages Area -->
    <div 
      ref="messagesContainer"
      class="flex-1 overflow-y-auto custom-scrollbar scroll-smooth"
    >
      <div v-if="messages.length === 0" class="h-full flex flex-col items-center justify-center text-zinc-500 space-y-4">
        <div class="w-16 h-16 bg-zinc-700 rounded-2xl flex items-center justify-center">
          <Bot class="w-8 h-8 text-zinc-400" />
        </div>
        <p class="text-lg font-medium">Ask me anything about D&D 5E rules</p>
      </div>

      <div 
        v-for="(msg, index) in messages" 
        :key="index"
        class="w-full border-b border-black/10 dark:border-gray-900/50"
        :class="[
          msg.role === 'assistant' ? 'bg-[#444654]' : 'bg-[#343541]'
        ]"
      >
        <div class="max-w-3xl mx-auto p-4 md:p-6 flex gap-4 md:gap-6">
          <!-- Avatar -->
          <div class="flex-shrink-0 flex flex-col relative items-end">
            <div 
              class="w-8 h-8 rounded-sm flex items-center justify-center"
              :class="msg.role === 'assistant' ? 'bg-emerald-600' : 'bg-indigo-600'"
            >
              <Bot v-if="msg.role === 'assistant'" class="w-5 h-5 text-white" />
              <User v-else class="w-5 h-5 text-white" />
            </div>
          </div>

          <!-- Content -->
          <div class="relative flex-1 overflow-hidden">
            <div class="font-bold text-zinc-300 mb-1 text-sm">
              {{ msg.role === 'assistant' ? 'D&D Agent' : 'You' }}
            </div>

            <!-- Tool Logs (Thought Process) - Moved to top -->
            <div v-if="msg.logs && msg.logs.length > 0" class="mb-4">
              <div class="bg-black/10 dark:bg-black/20 rounded-lg overflow-hidden border border-black/5 dark:border-white/5">
                <button 
                  @click="toggleLogs(index)"
                  class="w-full flex items-center justify-between px-3 py-2 text-xs text-zinc-400 hover:text-zinc-200 hover:bg-black/5 transition-colors"
                >
                  <div class="flex items-center font-medium">
                    <component :is="logsExpanded[index] ? ChevronDown : ChevronRight" class="w-3.5 h-3.5 mr-1.5" />
                    <span>Thinking Process</span>
                  </div>
                  <span class="text-[10px] bg-black/20 px-1.5 py-0.5 rounded-full">{{ msg.logs.length }} steps</span>
                </button>
                
                <div v-if="logsExpanded[index]" class="px-3 py-2 border-t border-black/5 dark:border-white/5 bg-black/5">
                  <div class="space-y-3">
                    <div 
                      v-for="(log, logIndex) in msg.logs" 
                      :key="logIndex"
                      class="text-xs font-mono"
                    >
                      <div class="flex items-start gap-2">
                        <Terminal class="w-3 h-3 mt-0.5 text-zinc-500 flex-shrink-0" />
                        <div class="min-w-0 flex-1">
                          <span class="text-emerald-500 font-semibold uppercase tracking-wider text-[10px] block mb-0.5">{{ log.type }}</span>
                          <div class="text-zinc-400 whitespace-pre-wrap break-words">{{ log.content }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Markdown Content -->
            <div 
              class="prose prose-invert prose-sm max-w-none leading-7"
              v-html="md.render(msg.content)"
            ></div>
          </div>
        </div>
      </div>

      <!-- Loading Indicator -->
      <div v-if="isLoading" class="w-full bg-[#444654] border-b border-black/10 dark:border-gray-900/50">
        <div class="max-w-3xl mx-auto p-4 md:p-6 flex gap-4 md:gap-6">
          <div class="w-8 h-8 bg-emerald-600 rounded-sm flex items-center justify-center">
            <Loader2 class="w-5 h-5 text-white animate-spin" />
          </div>
          <div class="flex items-center">
            <span class="text-zinc-400 text-sm animate-pulse">Thinking...</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="absolute bottom-0 left-0 w-full bg-gradient-to-t from-[#343541] via-[#343541] to-transparent pt-10 pb-6 px-4">
      <div class="max-w-3xl mx-auto relative">
        <div class="relative flex items-end w-full p-3 bg-[#40414F] rounded-xl border border-black/10 dark:border-gray-900/50 shadow-md overflow-hidden ring-offset-2 focus-within:ring-2 ring-emerald-600/50">
          <textarea
            ref="textareaRef"
            v-model="userInput"
            rows="1"
            class="w-full max-h-[200px] py-2 pr-10 pl-2 bg-transparent border-0 focus:ring-0 resize-none text-zinc-100 placeholder-zinc-400 scrollbar-hide"
            placeholder="Ask a question about D&D rules..."
            @keydown="handleKeydown"
            @input="adjustHeight"
            :disabled="isLoading"
          ></textarea>
          <button
            @click="handleSend"
            :disabled="isLoading || !userInput.trim()"
            class="absolute right-3 bottom-3 p-1.5 rounded-md transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            :class="userInput.trim() ? 'bg-emerald-600 text-white hover:bg-emerald-700' : 'text-zinc-400 hover:bg-zinc-700'"
          >
            <Send class="w-4 h-4" />
          </button>
        </div>
        <div class="text-center text-xs text-zinc-500 mt-2">
          D&D Rule Agent may produce inaccurate information about game rules.
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.2);
}
</style>
