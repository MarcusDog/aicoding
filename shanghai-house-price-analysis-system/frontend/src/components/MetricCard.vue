<script setup lang="ts">
defineProps<{
  label: string
  value: string
  hint: string
}>()
</script>

<template>
  <section class="metric-card">
    <p class="metric-label">{{ label }}</p>
    <h3 class="metric-value">{{ value }}</h3>
    <p class="metric-hint">{{ hint }}</p>
  </section>
</template>
