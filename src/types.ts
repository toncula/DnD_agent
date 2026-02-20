export interface BookNode {
  label: string;
  value: string;
  children?: BookNode[];
}

export interface BookTreeResponse {
  nodes: BookNode[];
  valid_paths: string[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ToolLog {
  type: string;
  content: string;
}

export interface ChatResponse {
  response: string;
  logs: ToolLog[];
}

export interface ChatRequest {
  messages: ChatMessage[];
  selected_books: string[];
  thread_id?: string;
}
