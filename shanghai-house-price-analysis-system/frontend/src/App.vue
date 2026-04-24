<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand-block">
        <p class="eyebrow">Shanghai Resale Housing</p>
        <h1>二手房价数据分析系统</h1>
        <p class="brand-copy">采集、分析、预测与答辩演示一体化单机系统</p>
      </div>
      <nav class="nav-list">
        <RouterLink to="/overview">总览</RouterLink>
        <RouterLink to="/listings">房源列表</RouterLink>
        <RouterLink to="/communities">小区分析</RouterLink>
        <RouterLink to="/trends">趋势分析</RouterLink>
        <RouterLink to="/predictions">预测结果</RouterLink>
      </nav>
    </aside>
    <main class="page-shell">
      <RouterView />
    </main>
  </div>
</template>
