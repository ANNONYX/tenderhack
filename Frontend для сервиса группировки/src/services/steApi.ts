import { api } from './api';
import { STEListResponse, STEResponse } from '../types';

export const steApi = {
  // Search STE
  searchSTE: async (params: {
    query?: string;
    category_id?: string;
    limit?: number;
    offset?: number;
  }): Promise<STEListResponse> => {
    const response = await api.get<STEListResponse>('/ste/', { params });
    return response.data;
  },

  // Get STE by ID
  getSTEById: async (steId: number): Promise<STEResponse> => {
    const response = await api.get<STEResponse>(`/ste/${steId}`);
    return response.data;
  },
};
