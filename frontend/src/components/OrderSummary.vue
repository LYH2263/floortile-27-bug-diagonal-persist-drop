<script setup>
defineProps({
  result: { type: Object, default: null },
})
</script>
<template>
  <div v-if="result" class="order-summary">
    <div class="hero">
      <span :class="{ muted: result.diagonal }">正铺 {{ result.order_count }} 片</span>
      <span v-if="result.diagonal" class="diag">斜铺 {{ result.diag_order_count }} 片</span>
    </div>
    <ul>
      <li>正铺净用量 {{ result.raw_count }} 片，损耗 {{ result.waste_pct }}%</li>
      <li v-if="result.diagonal">
        斜铺净用量 {{ result.diag_raw_count }} 片（系数 ×{{ result.diag_factor }}），套同档损耗后
        <strong>{{ result.diag_order_count }} 片</strong>
      </li>
      <li>地面 {{ result.area_m2 }} m²，单砖 {{ result.piece_m2 }} m²</li>
    </ul>
  </div>
</template>
