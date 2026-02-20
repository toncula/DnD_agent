import axios from 'axios';
import type { BookTreeResponse, ChatRequest, ChatResponse } from '../types';

// Create Axios instance with base URL
// In a real app, this might come from import.meta.env.VITE_API_BASE_URL
// For this demo, we default to localhost:8000 as per requirements
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  /**
   * Fetch the book directory tree
   */
  async getBooks(): Promise<BookTreeResponse> {
    try {
      const response = await apiClient.get<BookTreeResponse>('/v1/books');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch books:', error);
      throw error;
    }
  },

  /**
   * Send a chat message
   */
  async sendChat(payload: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await apiClient.post<ChatResponse>('/v1/chat', payload);
      return response.data;
    } catch (error) {
      console.error('Failed to send chat message:', error);
      throw error;
    }
  },
};
