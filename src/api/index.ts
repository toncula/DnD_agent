import axios from 'axios';
import type { BookTreeResponse, ChatRequest, ChatResponse } from '../types';

// Create Axios instance with base URL
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

  /**
   * Fetch the current character sheet
   */
  async getCharacter(): Promise<any> {
    try {
      const response = await apiClient.get('/v1/character');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch character:', error);
      throw error;
    }
  },

  /**
   * Save or update the character sheet
   */
  async updateCharacter(data: any): Promise<any> {
    try {
      const response = await apiClient.post('/v1/character', { data });
      return response.data;
    } catch (error) {
      console.error('Failed to update character:', error);
      throw error;
    }
  }
};
