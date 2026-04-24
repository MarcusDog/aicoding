<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand__eyebrow">Spark News Monitor</div>
        <h1>新闻热度监测系统</h1>
        <p>面向毕业设计演示的全链路新闻采集、分析、预警与数据服务平台。</p>
      </div>

      <nav class="nav">
        <RouterLink to="/dashboard" class="nav__link">可视化大屏</RouterLink>
        <RouterLink to="/news" class="nav__link">新闻查询</RouterLink>
        <RouterLink to="/events" class="nav__link">事件分析</RouterLink>
        <RouterLink to="/influence" class="nav__link">传播评估</RouterLink>
        <RouterLink to="/services" class="nav__link">服务中心</RouterLink>
      </nav>
    </aside>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from "vue-router";
</script>
