import { api } from './api';
import { GroupingRequest, GroupingResponse, AggregationResponse } from '../types';

export const aggregationApi = {
  // Perform grouping
  performGrouping: async (data: GroupingRequest): Promise<GroupingResponse> => {
    const response = await api.post<GroupingResponse>('/grouping/', data);
    return response.data;
  },

  // Get aggregations list
  getAggregations: async (params: {
    category_id?: string;
    saved_only?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<AggregationResponse[]> => {
    const response = await api.get<AggregationResponse[]>('/grouping/aggregations', { params });
    return response.data;
  },

  // Get aggregation details
  getAggregationById: async (aggregationId: number): Promise<AggregationResponse> => {
    const response = await api.get<AggregationResponse>(`/grouping/aggregations/${aggregationId}`);
    return response.data;
  },

  // Add STE to aggregation
  addSTEToAggregation: async (aggregationId: number, steId: number, order?: number): Promise<void> => {
    await api.post(`/aggregations/${aggregationId}/items/${steId}`, null, {
      params: { order },
    });
  },

  // Remove STE from aggregation
  removeSTEFromAggregation: async (aggregationId: number, itemId: number): Promise<void> => {
    await api.delete(`/aggregations/${aggregationId}/items/${itemId}`);
  },

  // Change STE order in aggregation
  changeSTEOrder: async (aggregationId: number, itemId: number, newOrder: number): Promise<void> => {
    await api.put(`/aggregations/${aggregationId}/items/${itemId}/order`, null, {
      params: { new_order: newOrder },
    });
  },

  // Save aggregation
  saveAggregation: async (aggregationId: number): Promise<void> => {
    await api.post(`/aggregations/${aggregationId}/save`);
  },

  // Delete aggregation
  deleteAggregation: async (aggregationId: number): Promise<void> => {
    await api.delete(`/aggregations/${aggregationId}`);
  },
};
