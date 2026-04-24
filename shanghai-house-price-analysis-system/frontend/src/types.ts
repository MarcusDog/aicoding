export interface Listing {
  id: string | number
  title: string
  communityName: string
  district: string
  subdistrict?: string
  totalPrice: number
  unitPrice: number
  area: number
  layout?: string
  floorInfo?: string
  orientation?: string
  decoration?: string
  buildYear?: number | string
  followCount?: number
  listingUrl?: string
}

export interface Community {
  id: string | number
  name: string
  district: string
  subdistrict?: string
  averageUnitPrice: number
  buildYear?: number | string
  onSaleCount: number
}

export interface OverviewPayload {
  metrics: {
    listing_count: number
    community_count: number
    avg_unit_price: number
    avg_total_price: number
    price_min: number
    price_max: number
  }
  charts: {
    district_distribution: Array<{
      district: string
      listing_count: number
      avg_unit_price: number
      avg_total_price: number
      avg_area: number
    }>
    latest_predictions: Array<{
      target_level: string
      target_name: string
      model_name: string
      predicted_unit_price: number
    }>
  }
}

export interface PriceIndex {
  id?: string | number
  stat_month: string
  city: string
  house_type: string
  size_segment: string
  mom_index: number
  yoy_index: number
}

export interface Prediction {
  id?: string | number
  target_level: string
  target_name: string
  model_name: string
  predicted_unit_price: number
  confidence_lower?: number
  confidence_upper?: number
}
