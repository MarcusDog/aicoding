import { mockCommunities, mockListings, mockOverview, mockPredictions, mockPriceIndices } from '../mock/data'
import type { Community, Listing, OverviewPayload, Prediction, PriceIndex } from '../types'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000/api'

async function request<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${path}`)
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`)
    }
    return (await response.json()) as T
  } catch {
    return fallback
  }
}

function mapListing(item: Record<string, unknown>): Listing {
  return {
    id: item.id as string | number,
    title: String(item.title ?? ''),
    communityName: String(item.community_name ?? item.communityName ?? ''),
    district: String(item.district ?? ''),
    subdistrict: String(item.subdistrict ?? ''),
    totalPrice: Number(item.total_price ?? item.totalPrice ?? 0),
    unitPrice: Number(item.unit_price ?? item.unitPrice ?? 0),
    area: Number(item.area ?? 0),
    layout: String(item.layout ?? ''),
    floorInfo: String(item.floor_info ?? item.floorInfo ?? ''),
    orientation: String(item.orientation ?? ''),
    decoration: String(item.decoration ?? ''),
    buildYear: item.build_year as number | string | undefined,
    followCount: Number(item.follow_count ?? item.followCount ?? 0),
    listingUrl: String(item.listing_url ?? item.listingUrl ?? ''),
  }
}

function mapCommunity(item: Record<string, unknown>): Community {
  return {
    id: item.id as string | number,
    name: String(item.name ?? ''),
    district: String(item.district ?? ''),
    subdistrict: String(item.subdistrict ?? ''),
    averageUnitPrice: Number(item.average_unit_price ?? item.averageUnitPrice ?? 0),
    buildYear: item.build_year as number | string | undefined,
    onSaleCount: Number(item.on_sale_count ?? item.onSaleCount ?? 0),
  }
}

function mapPriceIndex(item: Record<string, unknown>): PriceIndex {
  return {
    id: item.id as string | number | undefined,
    stat_month: String(item.stat_month ?? ''),
    city: String(item.city ?? ''),
    house_type: String(item.house_type ?? ''),
    size_segment: String(item.size_segment ?? ''),
    mom_index: Number(item.mom_index ?? 0),
    yoy_index: Number(item.yoy_index ?? 0),
  }
}

function mapPrediction(item: Record<string, unknown>): Prediction {
  return {
    id: item.id as string | number | undefined,
    target_level: String(item.target_level ?? ''),
    target_name: String(item.target_name ?? ''),
    model_name: String(item.model_name ?? ''),
    predicted_unit_price: Number(item.predicted_unit_price ?? 0),
    confidence_lower: Number(item.confidence_lower ?? 0),
    confidence_upper: Number(item.confidence_upper ?? 0),
  }
}

export async function fetchOverview(): Promise<OverviewPayload> {
  return request('/overview/', mockOverview)
}

export async function fetchListings(): Promise<Listing[]> {
  const payload = await request<{ count: number; results: Listing[] }>('/listings/', {
    count: mockListings.length,
    results: mockListings,
  })
  return payload.results.map((item) => mapListing(item as unknown as Record<string, unknown>))
}

export async function fetchCommunities(): Promise<Community[]> {
  const payload = await request<{ count: number; results: Community[] }>('/communities/', {
    count: mockCommunities.length,
    results: mockCommunities,
  })
  return payload.results.map((item) => mapCommunity(item as unknown as Record<string, unknown>))
}

export async function fetchDistrictStats(): Promise<OverviewPayload['charts']['district_distribution']> {
  const payload = await request<{ results: OverviewPayload['charts']['district_distribution'] }>('/district-stats/', {
    results: mockOverview.charts.district_distribution,
  })
  return payload.results
}

export async function fetchPriceIndices(): Promise<PriceIndex[]> {
  const payload = await request<{ count: number; results: PriceIndex[] }>('/price-indices/', {
    count: mockPriceIndices.length,
    results: mockPriceIndices,
  })
  return payload.results.map((item) => mapPriceIndex(item as unknown as Record<string, unknown>))
}

export async function fetchPredictions(): Promise<Prediction[]> {
  const payload = await request<{ count: number; results: Prediction[] }>('/predictions/', {
    count: mockPredictions.length,
    results: mockPredictions,
  })
  return payload.results.map((item) => mapPrediction(item as unknown as Record<string, unknown>))
}
