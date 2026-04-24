type SortKey = 'default' | 'totalPrice-desc' | 'totalPrice-asc' | 'unitPrice-desc' | 'area-desc'

interface FilterOptions {
  keyword?: string
  district?: string
  sortBy?: SortKey
}

interface ListingLike {
  id: string | number
  title: string
  communityName: string
  district: string
  totalPrice: number
  unitPrice?: number
  area: number
}

export function filterListings<T extends ListingLike>(listings: T[], options: FilterOptions): T[] {
  const keyword = options.keyword?.trim().toLowerCase()
  const district = options.district?.trim()
  const sortBy = options.sortBy ?? 'default'

  const filtered = listings.filter((listing) => {
    const matchesKeyword =
      !keyword ||
      listing.title.toLowerCase().includes(keyword) ||
      listing.communityName.toLowerCase().includes(keyword)
    const matchesDistrict = !district || listing.district === district
    return matchesKeyword && matchesDistrict
  })

  const sorted = [...filtered]
  sorted.sort((left, right) => {
    switch (sortBy) {
      case 'totalPrice-desc':
        return right.totalPrice - left.totalPrice
      case 'totalPrice-asc':
        return left.totalPrice - right.totalPrice
      case 'unitPrice-desc':
        return (right.unitPrice ?? 0) - (left.unitPrice ?? 0)
      case 'area-desc':
        return right.area - left.area
      default:
        return 0
    }
  })

  return sorted
}
