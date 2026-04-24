<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { fetchListings } from '../api/client'
import type { Listing } from '../types'
import { filterListings } from '../utils/filters'

const listings = ref<Listing[]>([])
const keyword = ref('')
const district = ref('')
const sortBy = ref<'default' | 'totalPrice-desc' | 'totalPrice-asc' | 'unitPrice-desc' | 'area-desc'>('default')

const filteredListings = computed(() =>
  filterListings(listings.value, {
    keyword: keyword.value,
    district: district.value,
    sortBy: sortBy.value,
  }),
)

const districts = computed(() => Array.from(new Set(listings.value.map((item) => item.district))).sort())

onMounted(async () => {
  listings.value = await fetchListings()
})
</script>

<template>
  <section class="page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Listings</p>
        <h2>房源列表</h2>
      </div>
      <p class="page-copy">支持关键字筛选、区域筛选和按总价/单价排序。</p>
    </header>

    <div class="toolbar">
      <input v-model="keyword" class="input" placeholder="输入标题或小区名" />
      <select v-model="district" class="input">
        <option value="">全部区域</option>
        <option v-for="item in districts" :key="item" :value="item">{{ item }}</option>
      </select>
      <select v-model="sortBy" class="input">
        <option value="default">默认排序</option>
        <option value="totalPrice-desc">总价从高到低</option>
        <option value="totalPrice-asc">总价从低到高</option>
        <option value="unitPrice-desc">单价从高到低</option>
        <option value="area-desc">面积从大到小</option>
      </select>
    </div>

    <div class="table-shell">
      <table class="data-table">
        <thead>
          <tr>
            <th>标题</th>
            <th>区域</th>
            <th>小区</th>
            <th>总价(万)</th>
            <th>单价(元/平)</th>
            <th>面积(平)</th>
            <th>户型</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredListings" :key="item.id">
            <td>{{ item.title }}</td>
            <td>{{ item.district }}</td>
            <td>{{ item.communityName }}</td>
            <td>{{ item.totalPrice }}</td>
            <td>{{ item.unitPrice }}</td>
            <td>{{ item.area }}</td>
            <td>{{ item.layout }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
