import { describe, expect, it } from 'vitest'

import { filterListings } from '@/utils/filters'

const listings = [
  { id: '1', district: 'Pudong', communityName: 'Century Garden', title: 'Bright two-bedroom', totalPrice: 820, area: 86 },
  { id: '2', district: 'Xuhui', communityName: 'Garden Lane', title: 'Renovated three-bedroom', totalPrice: 1380, area: 118 },
  { id: '3', district: 'Pudong', communityName: 'Zhangjiang Park', title: 'Compact starter home', totalPrice: 520, area: 52 },
]

describe('filterListings', () => {
  it('filters by keyword and district', () => {
    const result = filterListings(listings, {
      keyword: 'starter',
      district: 'Pudong',
    })

    expect(result).toHaveLength(1)
    expect(result[0]?.id).toBe('3')
  })

  it('sorts by total price descending', () => {
    const result = filterListings(listings, {
      sortBy: 'totalPrice-desc',
    })

    expect(result.map((item) => item.id)).toEqual(['2', '1', '3'])
  })
})
