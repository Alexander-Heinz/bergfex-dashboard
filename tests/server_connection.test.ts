// @vitest-environment node
import { describe, it, expect } from 'vitest';

describe('Backend Server Connection', () => {
  const API_URL = 'http://localhost:8000';

  it('should be reachable', async () => {
    try {
      // We check the docs endpoint or root to see if server is up
      const response = await fetch(`${API_URL}/docs`);
      expect(response.status).toBe(200);
    } catch (error) {
      console.error('Server connection failed. Is the backend running?');
      throw error;
    }
  });

  it('should return resorts data', async () => {
    try {
      const response = await fetch(`${API_URL}/api/resorts`);
      expect(response.status).toBe(200);
      
      const data = await response.json();
      expect(Array.isArray(data)).toBe(true);
      if (data.length > 0) {
        expect(data[0]).toHaveProperty('name');
        expect(data[0]).toHaveProperty('id');
      }
    } catch (error) {
       console.error('Failed to fetch resorts data');
       throw error;
    }
  });
});
