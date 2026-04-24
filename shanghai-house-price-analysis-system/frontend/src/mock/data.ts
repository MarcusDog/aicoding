import type { Community, Listing, OverviewPayload, Prediction, PriceIndex } from '../types'

export const mockListings: Listing[] = [
  {
    id: 1,
    title: 'Bright two-bedroom near Century Park',
    communityName: 'Century Garden',
    district: 'Pudong',
    subdistrict: 'Huamu',
    totalPrice: 620,
    unitPrice: 78481,
    area: 79,
    layout: '2B1L',
    floorInfo: 'high floor',
    orientation: 'south-north',
    decoration: 'fine',
    buildYear: 2008,
    followCount: 32,
  },
  {
    id: 2,
    title: 'Renovated three-bedroom in Xuhui core area',
    communityName: 'Garden Lane',
    district: 'Xuhui',
    subdistrict: 'Xujiahui',
    totalPrice: 1380,
    unitPrice: 116949,
    area: 118,
    layout: '3B2L',
    floorInfo: 'middle floor',
    orientation: 'south',
    decoration: 'fine',
    buildYear: 2003,
    followCount: 45,
  },
  {
    id: 3,
    title: 'Compact starter home in Zhangjiang',
    communityName: 'Zhangjiang Park',
    district: 'Pudong',
    subdistrict: 'Zhangjiang',
    totalPrice: 520,
    unitPrice: 100000,
    area: 52,
    layout: '1B1L',
    floorInfo: 'middle floor',
    orientation: 'east',
    decoration: 'simple',
    buildYear: 2012,
    followCount: 21,
  },
]

export const mockCommunities: Community[] = [
  { id: 1, name: 'Century Garden', district: 'Pudong', subdistrict: 'Huamu', averageUnitPrice: 78000, buildYear: 2008, onSaleCount: 12 },
  { id: 2, name: 'Garden Lane', district: 'Xuhui', subdistrict: 'Xujiahui', averageUnitPrice: 115000, buildYear: 2003, onSaleCount: 7 },
  { id: 3, name: 'Zhangjiang Park', district: 'Pudong', subdistrict: 'Zhangjiang', averageUnitPrice: 98000, buildYear: 2012, onSaleCount: 5 },
]

export const mockPriceIndices: PriceIndex[] = [
  { stat_month: '2025-12', city: 'Shanghai', house_type: 'second_hand', size_segment: 'overall', mom_index: 99.4, yoy_index: 93.9 },
  { stat_month: '2026-01', city: 'Shanghai', house_type: 'second_hand', size_segment: 'overall', mom_index: 99.6, yoy_index: 93.2 },
  { stat_month: '2026-02', city: 'Shanghai', house_type: 'second_hand', size_segment: 'overall', mom_index: 100.2, yoy_index: 93.8 },
]

export const mockPredictions: Prediction[] = [
  { id: 1, target_level: 'district', target_name: 'Pudong', model_name: 'random_forest', predicted_unit_price: 81230, confidence_lower: 79000, confidence_upper: 83500 },
  { id: 2, target_level: 'district', target_name: 'Xuhui', model_name: 'random_forest', predicted_unit_price: 113400, confidence_lower: 109000, confidence_upper: 117500 },
]

export const mockOverview: OverviewPayload = {
  metrics: {
    listing_count: 30,
    community_count: 24,
    avg_unit_price: 67210,
    avg_total_price: 558,
    price_min: 33652,
    price_max: 116949,
  },
  charts: {
    district_distribution: [
      { district: 'Pudong', listing_count: 8, avg_unit_price: 75000, avg_total_price: 640, avg_area: 86 },
      { district: 'Xuhui', listing_count: 5, avg_unit_price: 108000, avg_total_price: 1250, avg_area: 108 },
      { district: 'Yangpu', listing_count: 4, avg_unit_price: 69000, avg_total_price: 530, avg_area: 78 },
      { district: 'Minhang', listing_count: 7, avg_unit_price: 62000, avg_total_price: 488, avg_area: 92 },
    ],
    latest_predictions: mockPredictions.map((item) => ({
      target_level: item.target_level,
      target_name: item.target_name,
      model_name: item.model_name,
      predicted_unit_price: item.predicted_unit_price,
    })),
  },
}
