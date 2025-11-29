// STE Types
export interface STECharacteristics {
  [key: string]: string | null;
}

export interface STEResponse {
  id: number;
  ste_id: string;
  name: string;
  image_url: string | null;
  model: string | null;
  country: string | null;
  manufacturer: string | null;
  category_id: string;
  category_name: string;
  characteristics: STECharacteristics;
  created_at: string;
  updated_at: string | null;
}

export interface STEListResponse {
  items: STEResponse[];
  total: number;
}

// Aggregation Types
export interface AggregationItem {
  id: number;
  ste: STEResponse;
  order: number;
  created_at: string;
}

export interface AggregationResponse {
  id: number;
  name: string;
  category_id: string;
  category_name: string;
  grouping_characteristics: STECharacteristics;
  status: 'auto' | 'manual';
  rating: number | null;
  is_saved: boolean;
  created_at: string;
  updated_at: string | null;
  items: AggregationItem[];
  items_count: number;
}

export interface GroupingRequest {
  ste_ids?: number[] | null;
  category_id?: string | null;
  characteristics?: STECharacteristics | null;
  force_regenerate?: boolean;
}

export interface GroupingResponse {
  aggregations: AggregationResponse[];
  total_groups: number;
  total_items: number;
}

// Rating Types
export interface RatingRequest {
  rating: number;
  comment?: string | null;
}

export interface RatingResponse {
  id: number;
  rating: number;
  comment: string | null;
  created_at: string;
}

export interface AggregationRatingsResponse {
  aggregation_id: number;
  average_rating: number;
  ratings_count: number;
  ratings: RatingResponse[];
}
