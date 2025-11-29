import { api } from './api';
import { RatingRequest, AggregationRatingsResponse } from '../types';

export const ratingApi = {
  // Submit rating for aggregation
  submitRating: async (aggregationId: number, data: RatingRequest): Promise<void> => {
    await api.post(`/ratings/aggregations/${aggregationId}`, data);
  },

  // Get ratings for aggregation
  getRatings: async (aggregationId: number): Promise<AggregationRatingsResponse> => {
    const response = await api.get<AggregationRatingsResponse>(`/ratings/aggregations/${aggregationId}`);
    return response.data;
  },
};
